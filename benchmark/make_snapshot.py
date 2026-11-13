#!/usr/bin/env python3
"""Freeze one benchmark case as a ghr.py snapshot (offline, no leakage of the hidden reply).

Usage: python3 benchmark/make_snapshot.py <case-id> > snapshot.json
The snapshot has the thread up to the cut, recent maintainer comments from before the cut,
and duplicate candidates from older issues of the same repository.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "research"))
sys.path.insert(0, str(ROOT / "skills" / "github-human-reply" / "scripts"))
from analyze import DATA, is_bot, maintainers, MAINT  # noqa: E402
import ghr  # noqa: E402

WORK = ROOT / "benchmark" / "work"


def build(cid):
    h = json.loads((WORK / "hidden" / f"{cid}.json").read_text())
    rec = json.loads((DATA / (h["repo"].replace("/", "__") + ".json")).read_text())
    issue = next(i for i in rec["issues"] if i["number"] == h["number"])
    cut = h["cutoff"]
    before = [c for c in issue["comments"]["nodes"] if c["createdAt"] < cut]
    maint = maintainers(rec)
    room = []
    for i in rec["issues"]:
        if i["number"] == h["number"]:
            continue
        for c in i["comments"]["nodes"]:
            a = c["author"] or {}
            if c["createdAt"] < cut and not is_bot(a) and (a.get("login") in maint or c["authorAssociation"] in MAINT):
                room.append((c["createdAt"], c["body"]))
    room.sort(reverse=True)
    kws = ghr.title_keywords(issue["title"], 3)
    dups = []
    if kws:
        for i in rec["issues"]:
            if i["number"] == h["number"] or i["createdAt"] >= issue["createdAt"]:
                continue
            hits = sum(1 for k in kws if k.lower() in i["title"].lower())
            if hits >= 2 or (hits == 1 and len(kws) == 1):
                dups.append({"number": i["number"], "title": i["title"], "state": "?", "reason": None, "pr": False,
                             "url": f"https://github.com/{h['repo']}/issues/{i['number']}"})
    author = (issue["author"] or {}).get("login", "ghost")
    return {
        "repo": h["repo"], "number": h["number"], "kind": "issue", "anchor": None,
        "issue": {"title": issue["title"], "body": issue["body"] or "", "state": "open", "state_reason": None, "locked": False,
                  "user": author, "assoc": issue["authorAssociation"], "created_at": issue["createdAt"],
                  "updated_at": (before[-1]["createdAt"] if before else issue["createdAt"]),
                  "url": f"https://github.com/{h['repo']}/issues/{h['number']}",
                  "labels": [l["name"] for l in issue["labels"]["nodes"]], "comments": len(before)},
        "comments": [{"id": k + 1, "user": (c["author"] or {}).get("login", "ghost"), "type": (c["author"] or {}).get("__typename"),
                      "assoc": c["authorAssociation"], "created_at": c["createdAt"], "body": c["body"] or "", "url": c["url"]}
                     for k, c in enumerate(before)],
        "reviews": [], "review_comments": [], "pr": None,
        "viewer": {"login": "operator", "permission": "write" if h["role"] == "maintainer" else "read", "is_author": False},
        "room": {"bodies": [b for _, b in room[:100]], "who": "recent comments by owners, members and collaborators"},
        "release": None, "links": [], "duplicates": dups[:5],
    }


if __name__ == "__main__":
    json.dump(build(sys.argv[1]), sys.stdout)
