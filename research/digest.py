#!/usr/bin/env python3
"""Render a readable sample of threads per repository for qualitative reading.

Usage: python3 research/digest.py
Output: research/data/digests/<owner>__<repo>.md
"""
import json, pathlib, random, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from analyze import DATA, is_bot, kind, maintainers, words

OUT = DATA / "digests"
random.seed(7)


def clip(s, n):
    s = (s or "").replace("\r", "").strip()
    return s if len(s) <= n else s[:n] + f"\n[... {len(s) - n} more characters]"


def role(login, assoc, author, maint):
    if login == author:
        return "reporter"
    return "maintainer" if (login in maint or assoc in ("OWNER", "MEMBER", "COLLABORATOR")) else "other"


def render_issue(repo, i, maint, prs):
    author = (i["author"] or {}).get("login")
    L = [f"### #{i['number']} {i['title']}",
         f"https://github.com/{repo}/issues/{i['number']}",
         f"kind: {kind(i)} | by {author} ({i['authorAssociation']}) | labels: {', '.join(l['name'] for l in i['labels']['nodes']) or '-'}"
         f" | type: {(i.get('issueType') or {}).get('name') or '-'} | closed as {i['stateReason']} | {i['comments']['totalCount']} comments", ""]
    L += ["BODY:", clip(i["body"], 2500), ""]
    for c in [c for c in i["comments"]["nodes"] if not is_bot(c["author"])][:10]:
        lg = c["author"]["login"]
        L += [f"[{role(lg, c['authorAssociation'], author, maint)} {lg}, {c['createdAt'][:10]}]", clip(c["body"], 1200), ""]
    for e in i["timelineItems"]["nodes"]:
        if e["__typename"] == "ClosedEvent":
            c = e.get("closer") or {}
            how = f"PR #{c['number']}" if c.get("__typename") == "PullRequest" else ("a commit" if c.get("__typename") == "Commit" else "hand")
            L.append(f"CLOSED by {(e.get('actor') or {}).get('login')} via {how}")
    for p in i["closedByPullRequestsReferences"]["nodes"]:
        full = prs.get(p["number"])
        L.append(f"LINKED PR #{p['number']} \"{p['title']}\" by {(p['author'] or {}).get('login')} ({p['authorAssociation']}), merged {p['mergedAt'] or 'no'}")
        if full:
            L += ["PR BODY:", clip(full["body"], 800)]
    return "\n".join(L) + "\n"


def render_pr(repo, p):
    return "\n".join([
        f"### PR #{p['number']} {p['title']}", f"https://github.com/{repo}/pull/{p['number']}",
        f"by {(p['author'] or {}).get('login')} ({p['authorAssociation']}) | {p['state']} | +{p['additions']}/-{p['deletions']} in {p['changedFiles']} files"
        f" | closes: {', '.join('#' + str(x['number']) for x in p['closingIssuesReferences']['nodes']) or '-'}"
        f" | {p['comments']['totalCount']} comments, {p['reviews']['totalCount']} reviews, {p['reviewThreads']['totalCount']} review threads",
        "", clip(p["body"], 1200), ""])


def pick(xs, n):
    xs = list(xs)
    random.shuffle(xs)
    return xs[:n]


def main():
    OUT.mkdir(exist_ok=True)
    stats = {s["repo"]: s for s in json.loads((DATA / "stats.json").read_text())}
    for path in sorted(DATA.glob("*__*.json")):
        rec = json.loads(path.read_text())
        repo, maint = rec["repo"], maintainers(rec)
        prs = {p["number"]: p for p in rec["prs"]}
        iss = [i for i in rec["issues"] if not is_bot(i["author"])]
        talk = [i for i in iss if sum(1 for c in i["comments"]["nodes"] if not is_bot(c["author"])) >= 2]
        chosen, seen = [], set()

        def add(cands, n):
            for i in pick([c for c in cands if c["number"] not in seen], n):
                seen.add(i["number"]); chosen.append(i)

        add([i for i in talk if kind(i) == "bug" and i["stateReason"] == "COMPLETED"], 6)
        add([i for i in talk if kind(i) == "feature"], 5)
        add([i for i in iss if i["closedByPullRequestsReferences"]["nodes"]], 4)
        add([i for i in talk if i["stateReason"] in ("NOT_PLANNED", "DUPLICATE")], 4)
        add([i for i in iss if kind(i) in ("question", "other")], 2)
        hp = [p for p in rec["prs"] if not is_bot(p["author"])]
        out_prs = [p for p in hp if p["authorAssociation"] not in ("OWNER", "MEMBER", "COLLABORATOR")]
        pr_sel = pick([p for p in out_prs if p["state"] == "MERGED"], 4) + pick([p for p in out_prs if p["state"] != "MERGED"], 3) \
            + pick([p for p in hp if p not in out_prs], 3)
        L = [f"# {repo}", "", "## Numbers (150 recent closed issues, 100 recent PRs)", "",
             "```json", json.dumps({k: v for k, v in stats[repo].items() if k not in ("repo", "community")}, indent=0), "```", "",
             f"Community files: {', '.join(rec['community_files'])}", "", "## Issue templates", ""]
        for name, body in rec["templates"]["files"].items():
            L += [f"### {name}", "```", clip(body, 1800), "```", ""]
        L += ["## Issue threads", ""] + [render_issue(repo, i, maint, prs) for i in chosen]
        L += ["## Pull requests", ""] + [render_pr(repo, p) for p in pr_sel]
        text = "\n".join(L)
        (OUT / path.name.replace(".json", ".md")).write_text(text)
        print(f"{repo}: {len(chosen)} threads, {len(pr_sel)} prs, {words(text)} words")


if __name__ == "__main__":
    main()
