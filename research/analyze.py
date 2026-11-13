#!/usr/bin/env python3
"""Descriptive statistics over research/data/*.json. Prints a markdown table set
and writes research/data/stats.json.

Usage: python3 research/analyze.py
"""
import json, pathlib, re, statistics as st
from datetime import datetime

DATA = pathlib.Path(__file__).parent / "data"
BOT = re.compile(r"(\[bot\]$|-bot$|bot$|^github-actions|^dependabot|^renovate|^codecov|^stale|^netlify|^vercel|^pkg-pr-new|^graphite|^copilot|^claude|^codex)", re.I)
MAINT = {"OWNER", "MEMBER", "COLLABORATOR"}
BUG = re.compile(r"bug|crash|regress|defect|broken|incorrect|panic|error", re.I)
FEAT = re.compile(r"feature|enhanc|request|proposal|idea|rfe|wish|improvement", re.I)
QUES = re.compile(r"question|support|help|usage|discussion", re.I)
CLOSE_KW = re.compile(r"\b(fix(?:e[sd])?|close[sd]?|resolve[sd]?)\b[:\s]+(?:[\w.-]+/[\w.-]+)?#\d+", re.I)
ANYREF = re.compile(r"(?<![\w/])#\d+")


def t(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def is_bot(a):
    return (not a) or a.get("__typename") == "Bot" or bool(BOT.search(a.get("login") or ""))


def words(s):
    return len(re.findall(r"\S+", s or ""))


def med(xs):
    xs = [x for x in xs if x is not None]
    return round(st.median(xs), 1) if xs else None


def pct(n, d):
    return round(100 * n / d) if d else 0


def kind(issue):
    """bug / feature / question / other, from issue type, labels, title prefix and template headings."""
    typ = (issue.get("issueType") or {}).get("name") or ""
    labels = " ".join(l["name"] for l in issue["labels"]["nodes"])
    title, body = issue["title"], issue["body"] or ""
    heads = " ".join(re.findall(r"^#{2,4}\s*(.+)$", body, re.M))
    for src in (typ, labels, title[:40], heads):
        if not src:
            continue
        if FEAT.search(src) and not BUG.search(src):
            return "feature"
        if BUG.search(src):
            return "bug"
        if QUES.search(src):
            return "question"
    if re.search(r"steps to reproduce|expected behavio|actual behavio|reproduc", body, re.I):
        return "bug"
    return "other"


def maintainers(rec):
    """People who act like maintainers: badge, or they close/label issues they did not open."""
    m = set()
    for i in rec["issues"]:
        for c in i["comments"]["nodes"]:
            if c["authorAssociation"] in MAINT and not is_bot(c["author"]):
                m.add(c["author"]["login"])
        for e in i["timelineItems"]["nodes"]:
            a = e.get("actor")
            if e["__typename"] in ("ClosedEvent", "LabeledEvent") and a and not is_bot(a):
                if a["login"] != (i["author"] or {}).get("login"):
                    m.add(a["login"])
    return m


def repo_stats(rec):
    iss, prs = rec["issues"], rec["prs"]
    iss = [i for i in iss if not is_bot(i["author"])]
    maint = maintainers(rec)
    n = len(iss)
    s = {"repo": rec["repo"], "issues": n}
    tfiles = rec["templates"]["files"]
    s["templates"] = sorted(k for k in tfiles if k != "config.yml")
    s["forms"] = sum(1 for k in tfiles if k.endswith((".yml", ".yaml")) and k != "config.yml")
    cfg = tfiles.get("config.yml", "")
    s["blank_disabled"] = bool(re.search(r"blank_issues_enabled:\s*false", cfg))
    s["contact_links"] = len(re.findall(r"^\s*-\s*name:", cfg, re.M))
    s["community"] = rec["community_files"]

    kinds = [kind(i) for i in iss]
    for k in ("bug", "feature", "question", "other"):
        s[f"k_{k}"] = pct(kinds.count(k), n)
    s["typed"] = pct(sum(1 for i in iss if i.get("issueType")), n)
    s["labelled"] = pct(sum(1 for i in iss if i["labels"]["nodes"]), n)
    s["templated"] = pct(sum(1 for i in iss if len(re.findall(r"^#{2,4}\s", i["body"] or "", re.M)) >= 2), n)
    s["by_outsiders"] = pct(sum(1 for i in iss if i["authorAssociation"] not in MAINT and (i["author"] or {}).get("login") not in maint), n)
    s["title_words"] = med([words(i["title"]) for i in iss])
    s["title_prefix"] = pct(sum(1 for i in iss if re.match(r"^(\[[^\]]+\]|[\w./-]+(\([^)]*\))?:)\s", i["title"])), n)
    s["body_words"] = med([words(i["body"]) for i in iss])
    for k in ("bug", "feature"):
        s[f"body_words_{k}"] = med([words(i["body"]) for i, kk in zip(iss, kinds) if kk == k])
    s["has_code_block"] = pct(sum(1 for i in iss if "```" in (i["body"] or "")), n)
    s["has_version"] = pct(sum(1 for i in iss if re.search(r"\bv?\d+\.\d+(\.\d+)?\b", i["body"] or "")), n)

    reasons = [i["stateReason"] for i in iss]
    for r in ("COMPLETED", "NOT_PLANNED", "DUPLICATE"):
        s[f"closed_{r.lower()}"] = pct(reasons.count(r), n)

    by_pr = by_commit = cross_pr = closed_by_maint = closed_by_author = 0
    first_resp, first_resp_words, n_comments, no_comment = [], [], [], 0
    human_cw, maint_cw, out_cw = [], [], []
    greet = thanks = 0
    ncom = 0
    for i in iss:
        author = (i["author"] or {}).get("login")
        closer = None
        for e in i["timelineItems"]["nodes"]:
            if e["__typename"] == "ClosedEvent":
                closer = e
        linked = bool(i["closedByPullRequestsReferences"]["nodes"])
        c = (closer or {}).get("closer") or {}
        if linked or c.get("__typename") == "PullRequest":
            by_pr += 1
        elif c.get("__typename") == "Commit":
            by_commit += 1
        if any(e["__typename"] == "CrossReferencedEvent" and (e.get("source") or {}).get("__typename") == "PullRequest"
               for e in i["timelineItems"]["nodes"]):
            cross_pr += 1
        ca = ((closer or {}).get("actor") or {}).get("login")
        if ca and ca == author:
            closed_by_author += 1
        elif ca and ca in maint:
            closed_by_maint += 1
        humans = [c for c in i["comments"]["nodes"] if not is_bot(c["author"])]
        n_comments.append(len(humans))
        if not humans:
            no_comment += 1
        others = [c for c in humans if c["author"]["login"] != author]
        if others:
            first_resp.append((t(others[0]["createdAt"]) - t(i["createdAt"])).total_seconds() / 3600)
            first_resp_words.append(words(others[0]["body"]))
        for cm in humans:
            w = words(cm["body"])
            human_cw.append(w)
            (maint_cw if cm["author"]["login"] in maint else out_cw).append(w)
            ncom += 1
            head = (cm["body"] or "")[:60].lower()
            if re.match(r"\s*(hi|hello|hey|dear)\b", head):
                greet += 1
            if re.match(r"\s*(thanks|thank you|thx)", head):
                thanks += 1
    s["closed_via_pr"] = pct(by_pr, n)
    s["closed_via_commit"] = pct(by_commit, n)
    s["pr_mentions_issue"] = pct(cross_pr, n)
    s["closed_by_maint"] = pct(closed_by_maint, n)
    s["closed_by_author"] = pct(closed_by_author, n)
    s["no_human_comment"] = pct(no_comment, n)
    s["comments_med"] = med(n_comments)
    s["first_resp_h"] = med(first_resp)
    s["first_resp_words"] = med(first_resp_words)
    s["maint_comment_words"] = med(maint_cw)
    s["outsider_comment_words"] = med(out_cw)
    s["maint_short"] = pct(sum(1 for w in maint_cw if w <= 15), len(maint_cw))
    s["comment_md_struct"] = pct(sum(1 for i in iss for c in i["comments"]["nodes"]
                                     if not is_bot(c["author"]) and re.search(r"^(#{1,4}\s|\*\*[^*]+:\*\*)", c["body"] or "", re.M)), ncom)
    s["comment_greeting"] = pct(greet, ncom)
    s["comment_thanks_open"] = pct(thanks, ncom)

    hp = [p for p in prs if not is_bot(p["author"])]
    m = len(hp)
    s["prs"] = m
    s["pr_bots"] = pct(len(prs) - m, len(prs))
    s["pr_merged"] = pct(sum(1 for p in hp if p["state"] == "MERGED"), m)
    s["pr_linked_issue"] = pct(sum(1 for p in hp if p["closingIssuesReferences"]["nodes"]), m)
    s["pr_closing_kw"] = pct(sum(1 for p in hp if CLOSE_KW.search(p["body"] or "")), m)
    s["pr_any_ref"] = pct(sum(1 for p in hp if ANYREF.search((p["body"] or "") + " " + p["title"])), m)
    outs = [p for p in hp if p["authorAssociation"] not in MAINT and p["author"]["login"] not in maint]
    s["pr_by_outsiders"] = pct(len(outs), m)
    s["pr_out_linked"] = pct(sum(1 for p in outs if p["closingIssuesReferences"]["nodes"] or ANYREF.search(p["body"] or "")), len(outs))
    s["pr_out_merged"] = pct(sum(1 for p in outs if p["state"] == "MERGED"), len(outs))
    s["pr_body_words"] = med([words(p["body"]) for p in hp])
    s["pr_title_conv"] = pct(sum(1 for p in hp if re.match(r"^(\[[^\]]+\]|[\w./ -]+(\([^)]*\))?!?:)\s", p["title"])), m)
    s["pr_review_threads"] = med([p["reviewThreads"]["totalCount"] for p in hp])
    s["pr_size"] = med([p["additions"] + p["deletions"] for p in hp])
    return s


def table(rows, cols):
    print("| " + " | ".join(c for c, _ in cols) + " |")
    print("|" + "|".join("---" for _ in cols) + "|")
    for r in rows:
        print("| " + " | ".join(str(r.get(k, "")) if not callable(k) else str(k(r)) for _, k in cols) + " |")
    print()


def main():
    rows = [repo_stats(json.loads(p.read_text())) for p in sorted(DATA.glob("*__*.json"))]
    (DATA / "stats.json").write_text(json.dumps(rows, indent=1))
    short = lambda r: r["repo"].split("/")[1]
    print("## How issues are opened\n")
    table(rows, [("repo", short), ("templates", lambda r: len(r["templates"])), ("forms", "forms"), ("blank off", lambda r: "yes" if r["blank_disabled"] else ""),
                 ("bug%", "k_bug"), ("feature%", "k_feature"), ("question%", "k_question"), ("other%", "k_other"),
                 ("typed%", "typed"), ("templated%", "templated"), ("outsider%", "by_outsiders")])
    print("## What an issue looks like\n")
    table(rows, [("repo", short), ("title words", "title_words"), ("title prefix%", "title_prefix"), ("body words", "body_words"),
                 ("bug body", "body_words_bug"), ("feature body", "body_words_feature"), ("code block%", "has_code_block"), ("version%", "has_version")])
    print("## How issues end and link to PRs\n")
    table(rows, [("repo", short), ("completed%", "closed_completed"), ("not planned%", "closed_not_planned"), ("duplicate%", "closed_duplicate"),
                 ("closed via PR%", "closed_via_pr"), ("via commit%", "closed_via_commit"), ("PR mentions%", "pr_mentions_issue"),
                 ("closed by maint%", "closed_by_maint"), ("by author%", "closed_by_author")])
    print("## How the conversation goes\n")
    table(rows, [("repo", short), ("comments", "comments_med"), ("no comment%", "no_human_comment"), ("first reply h", "first_resp_h"),
                 ("first reply words", "first_resp_words"), ("maint words", "maint_comment_words"), ("outsider words", "outsider_comment_words"),
                 ("maint <=15w%", "maint_short"), ("headers/bold%", "comment_md_struct"), ("greeting%", "comment_greeting"), ("thanks opener%", "comment_thanks_open")])
    print("## Pull requests\n")
    table(rows, [("repo", short), ("bot PR%", "pr_bots"), ("merged%", "pr_merged"), ("linked issue%", "pr_linked_issue"), ("closing kw%", "pr_closing_kw"),
                 ("any #ref%", "pr_any_ref"), ("outsider PR%", "pr_by_outsiders"), ("outsider linked%", "pr_out_linked"), ("outsider merged%", "pr_out_merged"),
                 ("body words", "pr_body_words"), ("title conv%", "pr_title_conv"), ("review threads", "pr_review_threads"), ("lines", "pr_size")])


if __name__ == "__main__":
    main()
