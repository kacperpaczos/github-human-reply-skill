#!/usr/bin/env python3
"""Pick reply-benchmark cases from research/data and freeze their inputs.

A case is an issue thread cut just before a reply that a real person posted.
The agent sees everything before the cut; the reply itself is stored apart
under benchmark/work/hidden/.

Usage:
  python3 benchmark/select_cases.py list  [--per-repo N]        # print candidates
  python3 benchmark/select_cases.py build owner/repo#123 ...    # freeze cases
"""
import json, pathlib, random, re, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "research"))
from analyze import DATA, is_bot, kind, maintainers, words

WORK = ROOT / "benchmark" / "work"
BOILER = re.compile(
    r"^\s*(duplicate of|dup of|closing\b|closed\b|thanks?[.!]?\s*$|\+1|same here|bump|ping\b)", re.I)
MEDIA = re.compile(r"<img|!\[|\.png|\.jpg|\.mp4|user-attachments", re.I)


def load(repo):
    return json.loads((DATA / (repo.replace("/", "__") + ".json")).read_text())


def comment_counts(rec):
    n = {}
    for i in rec["issues"]:
        for c in i["comments"]["nodes"]:
            if not is_bot(c["author"]):
                n[c["author"]["login"]] = n.get(c["author"]["login"], 0) + 1
    return n


def target_of(issue, maint, counts):
    """Index and role of the reply to hide: the first substantive comment by a
    maintainer, or by a regular who is neither maintainer nor the reporter."""
    reporter = (issue["author"] or {}).get("login")
    cs = issue["comments"]["nodes"]
    for idx, c in enumerate(cs):
        if is_bot(c["author"]):
            continue
        login = c["author"]["login"]
        if login == reporter:
            continue
        role = "maintainer" if login in maint else ("regular" if counts.get(login, 0) >= 4 else None)
        if not role:
            continue
        w = words(c["body"])
        if not (8 <= w <= 220) or BOILER.search(c["body"] or "") or MEDIA.search(c["body"] or ""):
            return None
        return idx, role
    return None


def candidates(repo):
    rec = load(repo)
    maint, counts = maintainers(rec), comment_counts(rec)
    out = []
    for i in rec["issues"]:
        if is_bot(i["author"]) or words(i["body"]) < 25 or i["comments"]["totalCount"] > 40:
            continue
        t = target_of(i, maint, counts)
        if t:
            out.append((i, *t))
    return rec, maint, out


def clip(s, n):
    s = (s or "").replace("\r", "").strip()
    return s if len(s) <= n else s[:n] + "\n[truncated]"


def thread_md(repo, issue, upto, maint):
    reporter = (issue["author"] or {}).get("login")
    L = [f"# {repo} issue #{issue['number']}: {issue['title']}", "",
         f"Opened {issue['createdAt']} by @{reporter} ({issue['authorAssociation'].lower()})",
         f"Labels: {', '.join(l['name'] for l in issue['labels']['nodes']) or 'none'}",
         f"State: open", "", "## Issue body", "", (issue["body"] or "").replace("\r", ""), "", "## Comments so far", ""]
    cs = issue["comments"]["nodes"][:upto]
    if not cs:
        L.append("(none)")
    for c in cs:
        a = c["author"] or {}
        tag = "bot" if is_bot(a) else ("reporter" if a.get("login") == reporter else ("maintainer" if a.get("login") in maint else "participant"))
        L += [f"### @{a.get('login')} ({tag}) on {c['createdAt']}", "", (c["body"] or "").replace("\r", ""), ""]
    return "\n".join(L)


def samples(rec, pick, before, exclude_issue, limit, cap):
    out = []
    for i in rec["issues"]:
        if i["number"] == exclude_issue:
            continue
        for c in i["comments"]["nodes"]:
            if not is_bot(c["author"]) and pick(c["author"]["login"]) and c["createdAt"] < before and 4 <= words(c["body"]) <= 250:
                out.append((c["createdAt"], i, c))
    out.sort(key=lambda x: x[0], reverse=True)
    L = []
    for _, i, c in out[:limit]:
        L += [f"--- on #{i['number']} \"{i['title']}\", {c['createdAt'][:10]}, by @{c['author']['login']}", clip(c["body"], cap), ""]
    return "\n".join(L) or "(no earlier comments found)\n", len(out[:limit])


def build(spec):
    repo, num = spec.split("#")
    rec, maint, cands = candidates(repo)
    hit = [x for x in cands if x[0]["number"] == int(num)]
    if not hit:
        sys.exit(f"{spec}: not an eligible case")
    issue, idx, role = hit[0]
    tgt = issue["comments"]["nodes"][idx]
    login, cut = tgt["author"]["login"], tgt["createdAt"]
    cid = f"{repo.replace('/', '__')}__{num}"
    d = WORK / "cases" / cid / "input"
    d.mkdir(parents=True, exist_ok=True)
    (d / "thread.md").write_text(thread_md(repo, issue, idx, maint))
    voice, nv = samples(rec, lambda l: l == login, cut, issue["number"], 12, 700)
    room, nr = samples(rec, lambda l: l in maint and l != login, cut, issue["number"], 12, 500)
    (d / "voice.md").write_text(f"# Earlier comments by @{login} in {repo}\n\n" + voice)
    (d / "room.md").write_text(f"# Recent comments by other maintainers of {repo}\n\n" + room)
    hidden = WORK / "hidden"
    hidden.mkdir(parents=True, exist_ok=True)
    later = [{"login": (c["author"] or {}).get("login"), "at": c["createdAt"], "body": c["body"]}
             for c in issue["comments"]["nodes"][idx + 1:] if not is_bot(c["author"])]
    closed_by = [f"PR #{p['number']} {p['title']}" for p in issue["closedByPullRequestsReferences"]["nodes"]]
    (hidden / f"{cid}.json").write_text(json.dumps({
        "id": cid, "repo": repo, "number": int(num), "url": tgt["url"], "login": login, "role": role, "cutoff": cut,
        "kind": kind(issue), "reply": tgt["body"], "later_comments": later, "state_reason": issue["stateReason"],
        "closed_by": closed_by, "voice_samples": nv, "room_samples": nr}, indent=1))
    print(f"built {cid}: reply by {login} ({role}), {words(tgt['body'])} words, cut {cut}, voice {nv}, room {nr}")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("list", "build"):
        sys.exit(__doc__)
    if sys.argv[1] == "build":
        for spec in sys.argv[2:]:
            build(spec)
        return
    per = int(sys.argv[sys.argv.index("--per-repo") + 1]) if "--per-repo" in sys.argv else 5
    random.seed(11)
    for path in sorted(DATA.glob("*__*.json")):
        repo = path.stem.replace("__", "/")
        _, _, cands = candidates(repo)
        print(f"\n{repo}: {len(cands)} eligible")
        for issue, idx, role in random.sample(cands, min(per, len(cands))):
            t = issue["comments"]["nodes"][idx]
            print(f"  #{issue['number']} [{kind(issue)}/{issue['stateReason']}] pos {idx} {role} {t['author']['login']} {words(t['body'])}w: "
                  + re.sub(r"\s+", " ", t["body"])[:150])


if __name__ == "__main__":
    main()
