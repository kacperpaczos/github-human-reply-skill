#!/usr/bin/env python3
"""Judge benchmark runs with three different models.

Two questions per case and judge, asked in separate calls:
  blind   - three unlabelled replies (the real one, skill, baseline): which was
            posted by the real person?
  content - knowing the real reply and how the thread ended: is each draft
            right, and usable?

Usage: python3 benchmark/judge.py [--judges fable,codex,minimax] [--jobs N] [case-id ...]
Output: benchmark/work/judgements/<case-id>/<judge>.<part>.json
"""
import argparse, concurrent.futures as cf, hashlib, json, pathlib, random, re, subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORK = ROOT / "benchmark" / "work"

BLIND = """Below is a GitHub issue thread from {repo}, cut at a point where @{login} ({role}) posted the next comment. After it are a few of @{login}'s earlier comments, and then three candidate texts X, Y and Z for that next comment.

Exactly one candidate is the comment @{login} really posted. The other two were drafted by an AI assistant. Decide which is which. Judge by how people actually write in this thread and how @{login} writes, not by which text is the most complete or polished.

Answer with one JSON object and nothing else:
{{"human": "X|Y|Z", "ranking_most_to_least_humanlike": ["?", "?", "?"], "tells": {{"X": "<what gave it away or made it convincing, max 20 words>", "Y": "...", "Z": "..."}}}}

<thread>
{thread}
</thread>

<earlier_comments_by_{login}>
{voice}
</earlier_comments_by_{login}>

<candidate id="X">
{X}
</candidate>
<candidate id="Y">
{Y}
</candidate>
<candidate id="Z">
{Z}
</candidate>"""

CONTENT = """Below is a GitHub issue thread from {repo}, cut at a point where @{login} ({role}) posted the next comment. You are given the comment that was really posted, what happened in the thread afterwards, and two drafts P and Q written by AI assistants for that same slot, without seeing the real comment.

The real comment is one good answer, not the only one. Judge each draft on its own merits against what turned out to be true. Do not reward length, structure or polish.

For each draft decide:
- act: does it make the same kind of move as the real comment (answer, ask for information, decline, point to a duplicate, promise a fix ...)? "same", "partly" or "different".
- wrong: factual statements that the real comment or the later thread contradicts. A list of short quotes, empty if none.
- unsupported: statements presented as fact that nothing in the thread backs and that @{login} would have to check before posting. A list of short quotes.
- commitments: promises or decisions made on @{login}'s behalf that the real comment did not make. A list of short quotes.
- usable: could @{login} post it? "as is", "after small edits" or "no".
- embarrassing: would posting it make @{login} look bad (wrong, clueless, obviously machine-written)? true or false.
Then say which draft @{login} would rather post: "P", "Q" or "tie".

Answer with one JSON object and nothing else:
{{"P": {{"act": "", "wrong": [], "unsupported": [], "commitments": [], "usable": "", "embarrassing": false, "note": "<max 25 words>"}}, "Q": {{...same keys...}}, "preferred": "P|Q|tie"}}

<thread>
{thread}
</thread>

<real_comment>
{real}
</real_comment>

<what_happened_next>
{later}
</what_happened_next>

<draft id="P">
{P}
</draft>
<draft id="Q">
{Q}
</draft>"""


def call(judge, prompt):
    if judge == "fable":
        cmd = ["claude", "-p", prompt, "--model", "claude-fable-5-2", "--tools", "", "--strict-mcp-config",
               "--disable-slash-commands", "--setting-sources", "local", "--no-session-persistence"]
    elif judge == "codex":
        cmd = ["codex", "exec", "--skip-git-repo-check", "-s", "read-only", "-C", "/tmp", prompt]
    elif judge == "minimax":
        cmd = ["omp", "-p", "--model", "minimax-code/MiniMax-M3", "--thinking", "medium", "--no-tools", "--no-session",
               "--no-skills", "--no-rules", "--no-context-files", "--cwd", "/tmp", prompt]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=900, stdin=subprocess.DEVNULL)
    if "hit your" in r.stdout and "limit" in r.stdout:
        raise SystemExit("rate limited: " + r.stdout.strip()[:120])
    return r.stdout


def parse(text):
    for m in reversed(list(re.finditer(r"\{", text))):
        pass
    best = None
    depth, start = 0, None
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}" and depth:
            depth -= 1
            if depth == 0:
                try:
                    obj = json.loads(text[start:i + 1])
                    if isinstance(obj, dict) and (("human" in obj) or ("preferred" in obj)):
                        best = obj
                except Exception:
                    pass
    return best


def clip(s, n):
    return s if len(s) <= n else s[:n] + "\n[truncated]"


def judge_case(cid, judge):
    h = json.loads((WORK / "hidden" / f"{cid}.json").read_text())
    runs = {arm: json.loads((WORK / "runs" / cid / f"{arm}.json").read_text()) for arm in ("skill", "baseline")}
    out = WORK / "judgements" / cid
    out.mkdir(parents=True, exist_ok=True)
    inp = WORK / "cases" / cid / "input"
    thread = clip((inp / "thread.md").read_text(), 14000)
    voice = clip((inp / "voice.md").read_text(), 3500)
    role = "maintainer" if h["role"] == "maintainer" else "regular contributor"
    texts = {"human": h["reply"].replace("\r", "").strip(), "skill": runs["skill"]["reply"] or "", "baseline": runs["baseline"]["reply"] or ""}
    status = []
    # blind part: only when both drafts are real replies
    f = out / f"{judge}.blind.json"
    if not f.exists() and all(t and t != "NO_REPLY" for t in texts.values()):
        rnd = random.Random(int(hashlib.sha1(f"{cid}{judge}b".encode()).hexdigest(), 16))
        order = ["human", "skill", "baseline"]; rnd.shuffle(order)
        m = dict(zip("XYZ", order))
        res = parse(call(judge, BLIND.format(repo=h["repo"], login=h["login"], role=role, thread=thread, voice=voice,
                                             **{k: texts[v] for k, v in m.items()})))
        if res:
            res["mapping"] = m
            f.write_text(json.dumps(res, indent=1))
        status.append("blind:" + ("ok" if res else "FAIL"))
    f = out / f"{judge}.content.json"
    if not f.exists():
        rnd = random.Random(int(hashlib.sha1(f"{cid}{judge}c".encode()).hexdigest(), 16))
        order = ["skill", "baseline"]; rnd.shuffle(order)
        m = dict(zip("PQ", order))
        later = "\n\n".join(f"@{c['login']}: {clip(c['body'] or '', 900)}" for c in h["later_comments"][:6]) or "(no further comments)"
        later += f"\n\nIssue closed as {h['state_reason']}." + (f" Closed by {'; '.join(h['closed_by'])}." if h["closed_by"] else "")
        res = parse(call(judge, CONTENT.format(repo=h["repo"], login=h["login"], role=role, thread=thread, real=texts["human"], later=later,
                                               **{k: texts[v] or "NO_REPLY" for k, v in m.items()})))
        if res:
            res["mapping"] = m
            f.write_text(json.dumps(res, indent=1))
        status.append("content:" + ("ok" if res else "FAIL"))
    return cid, judge, " ".join(status) or "cached"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judges", default="fable,codex,minimax")
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("cases", nargs="*")
    a = ap.parse_args()
    cases = a.cases or sorted(p.name for p in (WORK / "runs").iterdir() if (p / "skill.json").exists() and (p / "baseline.json").exists())
    jobs = [(c, j) for c in cases for j in a.judges.split(",")]
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        for cid, judge, st in ex.map(lambda x: judge_case(*x), jobs):
            print(f"{judge:8} {cid}: {st}", flush=True)


if __name__ == "__main__":
    main()
