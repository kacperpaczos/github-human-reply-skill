#!/usr/bin/env python3
"""Reply benchmark with MiniMax through omp: the installed skill versus no skill.

The skill arm loads only github-human-reply (installed from the GitHub repository into
~/.agents/skills) and reads a frozen snapshot of the thread. The baseline arm loads no skill and
gets the same thread and maintainer comments as plain files. Network is off for both; every tool
call is recorded and runs that reached for the live thread are flagged as leaks.

Usage: python3 benchmark/run_omp.py [--tag omp] [--arms skill,baseline] [--jobs N] [--set test|dev|all] [case-id ...]
Output: benchmark/work/runs_<tag>/<case-id>/<arm>.json
"""
import argparse, concurrent.futures as cf, json, os, pathlib, re, subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORK = ROOT / "benchmark" / "work"
SKILL_DIR = pathlib.Path.home() / ".agents" / "skills" / "github-human-reply"
SANDBOX = pathlib.Path.home() / ".cache" / "ghr-bench"
MODEL = "minimax-code/MiniMax-M3"
TIMEOUT = 900  # seconds; a run that is still going is recorded as a timeout, not dropped
sys.path.insert(0, str(ROOT / "benchmark"))
import make_snapshot  # noqa: E402

FORMAT = """Final answer format, exactly:
<<<REPLY
(the comment exactly as it would be posted)
REPLY>>>
Checked: (one line)
Not checked: (one line)
If you decide nothing should be posted, put the single word NO_REPLY between the markers and say why on the line after them.
Do not ask the operator anything: where you would ask, take the most reasonable assumption and state it in the Not checked line. Nothing is posted.
Work economically: use at most 10 tool calls in total, then write the answer."""

SKILL_PROMPT = """Use the github-human-reply skill. The operator wants a draft of the next comment on https://github.com/{repo}/issues/{n}.
{role}
This is an offline test and the network is off. Where the skill says to run `python3 scripts/ghr.py thread <URL>`, run
python3 {skill}/scripts/ghr.py thread https://github.com/{repo}/issues/{n} --snapshot {snap}
instead. Searches fail; `file` reads the checkout of the repository in the current directory.
""" + FORMAT

BASE_PROMPT = """You are drafting a GitHub comment for the operator to post under their own name: the next comment on https://github.com/{repo}/issues/{n}.
{role}
The network is off. Files: {thread} is the thread as it stands; {room} has recent comments by other maintainers of this project. The repository is checked out in the current directory (git log, git show and grep work).
""" + FORMAT

LEAK = re.compile(r"(?:^|[;&|(]\s*|\bsudo\s+)(curl|wget|nc|ncat)\s|api\.github\.com|\bgh\s+(api|issue|pr|search|repo)\b|urllib|requests\.|http\.client|socket|hidden/|benchmark/work|git\s+(fetch|pull|ls-remote|clone|remote)")


def role_sentence(h):
    if h["role"] == "maintainer":
        return f"The operator maintains {h['repo']}."
    return f"The operator is an outside contributor to {h['repo']}."


def ensure_case(cid):
    d = SANDBOX / cid
    if not (d / "repo" / ".git").exists():
        sys.exit(f"{cid}: run benchmark/isolate_repos.py first")
    return d, d / "snapshot.json"


def parse_events(text):
    ev = []
    for line in text.splitlines():
        try:
            ev.append(json.loads(line))
        except Exception:
            pass
    return ev


def run(cid, arm, tag, key=None):
    out = WORK / f"runs_{tag}" / cid / f"{arm}.json"
    if out.exists():
        return cid, arm, "cached"
    out.parent.mkdir(parents=True, exist_ok=True)
    h = json.loads((WORK / "hidden" / f"{cid}.json").read_text())
    d, snap = ensure_case(cid)
    if arm == "skill":
        prompt = SKILL_PROMPT.format(repo=h["repo"], n=h["number"], role=role_sentence(h), skill=SKILL_DIR, snap=snap)
        skills = ["--skills", "github-human-reply"]
    else:
        prompt = BASE_PROMPT.format(repo=h["repo"], n=h["number"], role=role_sentence(h), thread=d / "thread.md", room=d / "room.md")
        skills = ["--no-skills"]
    cmd = ["omp", "-p", "--mode", "json", "--model", MODEL, "--thinking", "low", "--no-session", "--no-extensions",
           "--no-context-files", "--no-rules", *skills, *(["--api-key", key] if key else []), "--cwd", str(d / "repo"), prompt]
    env = dict(os.environ, GHR_OFFLINE="1", GH_HOST="offline.invalid", GH_TOKEN="offline", GH_PROMPT_DISABLED="1")
    t0 = time.time()
    timed_out = False
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT, stdin=subprocess.DEVNULL, env=env)
        stdout, stderr = r.stdout, r.stderr
    except subprocess.TimeoutExpired as e:
        timed_out = True
        dec = lambda b: b.decode("utf-8", "replace") if isinstance(b, bytes) else (b or "")
        stdout, stderr = dec(e.stdout), dec(e.stderr)
    ev = parse_events(stdout)
    final, calls, turns, usage = "", [], 0, {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0}
    for e in ev:
        if e.get("type") == "tool_execution_start":
            a = e.get("args") or {}
            calls.append({"tool": e.get("toolName"), "cmd": str(a.get("command") or a.get("path") or a.get("pattern") or a)[:300]})
        elif e.get("type") == "turn_end":
            turns += 1
            u = (e.get("message") or {}).get("usage") or {}
            for k in usage:
                usage[k] += u.get(k, 0) or 0
        elif e.get("type") == "agent_end":
            for m in reversed(e.get("messages") or []):
                if m.get("role") == "assistant":
                    final = "".join(b.get("text", "") for b in m.get("content", []) if b.get("type") == "text")
                    if final.strip():
                        break
    m = re.search(r"<<<REPLY\s*\n(.*?)\n?REPLY>>>(.*)", final, re.S)
    leaks = [c["cmd"] for c in calls if c["tool"] == "bash" and "ghr.py" not in c["cmd"] and LEAK.search(c["cmd"])]
    rec = {"case": cid, "arm": arm, "model": MODEL, "reply": m.group(1).strip() if m else None, "after": m.group(2).strip() if m else None,
           "raw": final, "turns": turns, "seconds": round(time.time() - t0), "usage": usage,
           "tokens": sum(usage.values()), "tool_calls": calls, "used_script": any("ghr.py" in c["cmd"] for c in calls),
           "leaks": leaks, "cost_usd": None, "timeout": timed_out}
    out.write_text(json.dumps(rec, indent=1))
    if not m:
        (out.with_suffix(".err")).write_text(final[-2000:] + "\n---\n" + stderr[-1500:])
    return cid, arm, ("LEAK " if leaks else "") + ("TIMEOUT" if timed_out else ("ok" if m else "NO_MARKERS"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="omp")
    ap.add_argument("--arms", default="skill,baseline")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--set", default="test", choices=["test", "dev", "all"])
    ap.add_argument("--key-file", help="file whose first line is an API key; passed with --api-key, never stored or printed")
    ap.add_argument("cases", nargs="*")
    a = ap.parse_args()
    if not SKILL_DIR.exists():
        sys.exit(f"skill not installed at {SKILL_DIR}")
    test = set((WORK / "test_cases.txt").read_text().split())
    allc = sorted(p.stem for p in (WORK / "hidden").glob("*.json"))
    cases = a.cases or [c for c in allc if a.set == "all" or (a.set == "test") == (c in test)]
    key = None
    if a.key_file:
        key = next(l.strip() for l in open(os.path.expanduser(a.key_file)) if l.strip())
    jobs = [(c, arm) for c in cases for arm in a.arms.split(",")]
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for cid, arm, st in ex.map(lambda x: run(x[0], x[1], a.tag, key), jobs):
            print(f"{st:14} {arm:9} {cid}", flush=True)


if __name__ == "__main__":
    main()
