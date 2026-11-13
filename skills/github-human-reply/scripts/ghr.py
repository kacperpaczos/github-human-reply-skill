#!/usr/bin/env python3
"""ghr: read-only GitHub context for the github-human-reply skill, plus a guarded poster.

One call gathers what a draft needs, so the model does not spend turns fetching it.

  ghr.py thread <issue|pr|comment URL | owner/repo#N>   case file for replying
  ghr.py new <owner/repo> [--keywords "two or three words"]   case file for filing an issue
  ghr.py file <owner/repo> <path> [--ref REF] [--lines A-B]   a file (or part of it) with line numbers
  ghr.py search <owner/repo> <keywords...> [--code]           issues and PRs (open and closed), or code
  ghr.py post comment <ref> --body-file F [--expect SIG] --yes      comment on an issue or PR conversation
  ghr.py post review-reply <owner/repo> <pr> <comment_id> --body-file F --yes
  ghr.py post issue <owner/repo> --title T --body-file F --yes

Everything except `post` only reads. `post` does nothing without --yes, which is passed only after the
operator approved the exact text. Needs the gh CLI, authenticated, and Python 3.8+.
Environment: GHR_OFFLINE=1 disables the network (used for benchmarks on frozen snapshots).
"""
import argparse
import base64
import json
import os
import re
import statistics
import subprocess
import sys
import tempfile

OFFLINE = os.environ.get("GHR_OFFLINE") == "1"
MAINT = {"OWNER", "MEMBER", "COLLABORATOR"}
BOT = re.compile(r"(\[bot\]$|-bot$|bot$|^github-actions|^dependabot|^renovate|^codecov|^copilot)", re.I)
CAP_TOTAL = 15000


class Fail(Exception):
    pass


# ----------------------------------------------------------------------------- gh access

def _decode_many(text):
    dec, i, out = json.JSONDecoder(), 0, []
    text = text.strip()
    while i < len(text):
        obj, i = dec.raw_decode(text, i)
        out.append(obj)
        while i < len(text) and text[i].isspace():
            i += 1
    return out


def gh(path, method="GET", fields=None, accept=None, raw=False, check=True, body_file=None):
    if OFFLINE:
        raise Fail("offline mode: this command needs the network; use the snapshot or local files")
    cmd = ["gh", "api", path]
    if method != "GET" or fields or body_file:
        cmd += ["-X", method]
    if accept:
        cmd += ["-H", f"Accept: {accept}"]
    for k, v in (fields or {}).items():
        cmd += ["-f", f"{k}={v}"]
    if body_file:
        cmd += ["-F", f"body=@{body_file}"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True)
    except FileNotFoundError:
        raise Fail("the gh CLI is not installed or not on PATH")
    if p.returncode != 0:
        if check:
            msg = (p.stderr or p.stdout).strip().splitlines()
            raise Fail(f"gh api {path}: {msg[0] if msg else 'failed'}")
        return None
    if raw:
        return p.stdout
    parsed = _decode_many(p.stdout) if p.stdout.strip() else []
    return parsed[0] if len(parsed) == 1 else parsed


def paged(path, limit_pages=3, total=None):
    """Fetch a list endpoint, at most `limit_pages` pages from the start (plus the last page when long)."""
    sep = "&" if "?" in path else "?"
    first = gh(f"{path}{sep}per_page=100&page=1")
    out = list(first)
    pages = 1 if total is None else -(-total // 100)
    for pg in range(2, min(pages, limit_pages) + 1):
        out += gh(f"{path}{sep}per_page=100&page={pg}")
    if pages > limit_pages:
        out += gh(f"{path}{sep}per_page=100&page={pages}")
    return out


def parse_ref(ref):
    m = re.match(r"https?://github\.com/([^/]+)/([^/]+)/(issues|pull|discussions)/(\d+)(?:.*?#(issuecomment-|discussion_r|r)(\d+))?", ref)
    if m:
        return {"owner": m[1], "repo": m[2], "kind": m[3], "number": int(m[4]), "anchor": m[5], "anchor_id": int(m[6]) if m[6] else None}
    m = re.match(r"([\w.-]+)/([\w.-]+)#(\d+)$", ref)
    if m:
        return {"owner": m[1], "repo": m[2], "kind": "issues", "number": int(m[3]), "anchor": None, "anchor_id": None}
    raise Fail(f"cannot read this reference: {ref} (use an issue, PR or comment URL, or owner/repo#N)")


# ----------------------------------------------------------------------------- text helpers

def words(s):
    return len(re.findall(r"\S+", s or ""))


def strip_noise(s):
    s = re.sub(r"```.*?```", " ", s or "", flags=re.S)
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)|<img[^>]*>|<[^>]+>", " ", s)
    return "\n".join(l for l in s.splitlines() if not l.lstrip().startswith(">")).strip()


def clip(s, n):
    s = (s or "").replace("\r", "").strip()
    return s if len(s) <= n else s[:n].rstrip() + f" [... {len(s) - n} more characters]"


def is_bot(user, utype=None):
    return utype == "Bot" or bool(BOT.search(user or "")) or not user


def detect_language(texts):
    sample = " ".join(texts)[:20000]
    letters = [c for c in sample if c.isalpha()]
    if not letters:
        return "unknown"
    ascii_share = sum(1 for c in letters if c < "\u0080") / len(letters)
    if ascii_share < 0.7:
        for name, lo, hi in (("Chinese/Japanese", 0x3040, 0x9FFF), ("Korean", 0xAC00, 0xD7AF), ("Cyrillic", 0x0400, 0x04FF)):
            if sum(1 for c in letters if lo <= ord(c) <= hi) / len(letters) > 0.3:
                return name + " (read the samples and answer in that language)"
        return "not English (read the samples and answer in that language)"
    toks = re.findall(r"[a-z']+", sample.lower())
    en = {"the", "is", "to", "of", "and", "a", "in", "it", "that", "this", "for", "with", "not", "you", "be", "are", "on", "as", "can", "if", "i"}
    share = sum(1 for t in toks if t in en) / max(1, len(toks))
    return "English" if share > 0.15 else "probably not English (read the samples and answer in that language)"


def room_profile(bodies):
    cleaned = [strip_noise(b) for b in bodies]
    cleaned = [c for c in cleaned if 6 <= words(c) <= 400]
    if len(cleaned) < 8:
        return {"n": len(cleaned)}
    w = [words(c) for c in cleaned]
    q = statistics.quantiles(w, n=4)
    pct = lambda f: round(100 * sum(1 for c in cleaned if f(c)) / len(cleaned))
    first_alpha = lambda c: next((ch for ch in c if ch.isalpha()), "A")
    p = {
        "n": len(cleaned), "median": round(statistics.median(w)), "p75": round(q[2]),
        "short": pct(lambda c: words(c) <= 15),
        "thanks": pct(lambda c: re.match(r"\s*(thanks|thank you|thx)", c, re.I)),
        "greeting": pct(lambda c: re.match(r"\s*(hi|hello|hey|dear)\b", c, re.I)),
        "lower": pct(lambda c: first_alpha(c).islower()),
        "nodot": pct(lambda c: not c.rstrip().endswith((".", "?", "!", ":"))),
        "lang": detect_language(cleaned),
    }
    med = statistics.median(w)
    pool = [c for c in cleaned if 6 <= words(c) <= max(12, med * 1.6)]
    seen, samples = set(), []
    for c in pool:
        key = c.split()[0].lower()
        if key in seen:
            continue
        seen.add(key)
        samples.append(c)
        if len(samples) == 3:
            break
    p["samples"] = samples
    return p


def render_room(p, who):
    if p.get("n", 0) < 8 or "median" not in p:
        return (f"## How people write here\nToo few recent comments to measure (n={p.get('n', 0)}). Use defaults: about 25 words, "
                "one paragraph, no greeting, no thanks as an opener, English unless the thread is in another language.\n")
    L = [f"## How people write here ({who}, n={p['n']})",
         f"Language: {p['lang']}",
         f"Length: median {p['median']} words, 75th percentile {p['p75']}; {p['short']}% are 15 words or fewer. Aim at the median ({p['median']} words); more than {round(p['median'] * 1.5)} needs a reason: a command, output or reproduction the reader needs.",
         f"Habits: thanks as the opening {p['thanks']}%, greeting {p['greeting']}%, lowercase first letter {p['lower']}%, no final period {p['nodot']}%."]
    if p["samples"]:
        L.append("Typical short comments (for register only, never copy their wording):")
        L += [f"- {clip(re.sub(chr(10) + '+', ' / ', s), 260)}" for s in p["samples"]]
    return "\n".join(L) + "\n"


# ----------------------------------------------------------------------------- live collection

def permission_of(perms):
    if not perms:
        return "unknown"
    for key, name in (("admin", "admin"), ("maintain", "maintain"), ("push", "write"), ("triage", "triage"), ("pull", "read")):
        if perms.get(key):
            return name
    return "none"


def collect_viewer(owner, repo):
    me = gh("user")
    r = gh(f"repos/{owner}/{repo}")
    return {"login": me.get("login"), "permission": permission_of(r.get("permissions")), "repo": r}


def collect_room(owner, repo, exclude_login=None):
    pages = gh(f"repos/{owner}/{repo}/issues/comments?sort=created&direction=desc&per_page=100&page=1")
    pages += gh(f"repos/{owner}/{repo}/issues/comments?sort=created&direction=desc&per_page=100&page=2", check=False) or []
    humans = [c for c in pages if not is_bot(c["user"]["login"], c["user"].get("type"))]
    maint = [c["body"] for c in humans if c.get("author_association") in MAINT]
    if len(maint) >= 8:
        return maint, "recent comments by owners, members and collaborators"
    counts = {}
    for c in humans:
        counts[c["user"]["login"]] = counts.get(c["user"]["login"], 0) + 1
    regulars = [c["body"] for c in humans if counts[c["user"]["login"]] >= 3 and c["user"]["login"] != exclude_login]
    if len(regulars) >= 8:
        return regulars, "recent comments by the most active commenters (no maintainer badges found)"
    return [c["body"] for c in humans if c["user"]["login"] != exclude_login], "recent comments by everyone (few regulars found)"


def title_keywords(title, n=3):
    stop = {"the", "a", "an", "is", "are", "to", "of", "in", "on", "for", "and", "or", "with", "when", "not", "no", "does", "doesnt", "how", "why", "add", "support", "fix", "bug", "issue", "error", "can", "cannot", "cant", "it", "this", "that", "from", "after", "before", "using", "use"}
    toks = [t for t in re.findall(r"[A-Za-z][A-Za-z0-9_.-]{2,}", title) if t.lower() not in stop]
    toks.sort(key=lambda t: (-len(t)))
    return toks[:n]


def collect_duplicates(owner, repo, keywords, exclude_number=None, limit=6):
    if not keywords:
        return []
    q = f"repo:{owner}/{repo} " + " ".join(keywords)
    res = gh("search/issues", method="GET", fields={"q": q, "per_page": str(limit + 1), "sort": "relevance"}, check=False)
    items = (res or {}).get("items", []) if isinstance(res, dict) else []
    out = []
    for it in items:
        if it["number"] == exclude_number:
            continue
        out.append({"number": it["number"], "title": it["title"], "state": it["state"], "reason": it.get("state_reason"),
                    "pr": "pull_request" in it, "url": it["html_url"]})
    return out[:limit]


def collect_latest_release(owner, repo):
    r = gh(f"repos/{owner}/{repo}/releases/latest", check=False)
    return {"tag": r.get("tag_name"), "date": (r.get("published_at") or "")[:10]} if isinstance(r, dict) and r.get("tag_name") else None


def collect_links(owner, repo, number):
    same = f"/{owner}/{repo}".lower()
    ev = gh(f"repos/{owner}/{repo}/issues/{number}/timeline?per_page=100", check=False) or []
    out = []
    for e in ev if isinstance(ev, list) else []:
        kind = e.get("event")
        if kind == "cross-referenced":
            src = (e.get("source") or {}).get("issue") or {}
            if src and not (src.get("repository_url") or "").lower().endswith(same):
                continue
            if src:
                what = "PR" if src.get("pull_request") else "issue"
                merged = " merged" if (src.get("pull_request") or {}).get("merged_at") else ""
                out.append(f"referenced by {what} #{src['number']} \"{clip(src['title'], 70)}\" ({src['state']}{merged})")
        elif kind == "closed":
            how = f"commit {e['commit_id'][:7]}" if e.get("commit_id") else "hand"
            out.append(f"closed by {(e.get('actor') or {}).get('login')} via {how}" + (f" ({e['state_reason']})" if e.get("state_reason") else ""))
        elif kind == "marked_as_duplicate":
            out.append("marked as duplicate")
    return out[:10]


def collect_thread(ref):
    t = parse_ref(ref)
    o, r, n = t["owner"], t["repo"], t["number"]
    issue = gh(f"repos/{o}/{r}/issues/{n}")
    is_pr = "pull_request" in issue
    comments = paged(f"repos/{o}/{r}/issues/{n}/comments", total=issue.get("comments", 0)) if issue.get("comments") else []
    snap = {
        "repo": f"{o}/{r}", "number": n, "kind": "pr" if is_pr else "issue", "anchor": t,
        "issue": {"title": issue["title"], "body": issue.get("body") or "", "state": issue["state"], "state_reason": issue.get("state_reason"),
                  "locked": issue.get("locked"), "user": issue["user"]["login"], "assoc": issue.get("author_association"),
                  "created_at": issue["created_at"], "updated_at": issue["updated_at"], "url": issue["html_url"],
                  "labels": [l["name"] for l in issue.get("labels", [])], "comments": issue.get("comments", 0)},
        "comments": [{"id": c["id"], "user": c["user"]["login"], "type": c["user"].get("type"), "assoc": c.get("author_association"),
                      "created_at": c["created_at"], "body": c.get("body") or "", "url": c["html_url"]} for c in comments],
        "reviews": [], "review_comments": [], "pr": None,
    }
    if is_pr:
        pr = gh(f"repos/{o}/{r}/pulls/{n}")
        snap["pr"] = {"merged": bool(pr.get("merged")), "draft": pr.get("draft"), "base": pr["base"]["ref"], "head": pr["head"]["ref"],
                      "files": pr.get("changed_files"), "additions": pr.get("additions"), "deletions": pr.get("deletions")}
        rev = gh(f"repos/{o}/{r}/pulls/{n}/reviews?per_page=100", check=False) or []
        snap["reviews"] = [{"user": x["user"]["login"], "state": x["state"], "body": x.get("body") or "", "assoc": x.get("author_association")} for x in rev if (x.get("body") or "").strip()]
        rc = gh(f"repos/{o}/{r}/pulls/{n}/comments?per_page=100", check=False) or []
        snap["review_comments"] = [{"id": c["id"], "user": c["user"]["login"], "assoc": c.get("author_association"), "path": c["path"], "line": c.get("line") or c.get("original_line"),
                                    "body": c.get("body") or "", "created_at": c["created_at"], "in_reply_to": c.get("in_reply_to_id")} for c in rc]
    v = collect_viewer(o, r)
    snap["viewer"] = {"login": v["login"], "permission": v["permission"], "is_author": (v["login"] or "").lower() == issue["user"]["login"].lower()}
    bodies, who = collect_room(o, r, exclude_login=issue["user"]["login"])
    snap["room"] = {"bodies": bodies, "who": who}
    snap["release"] = collect_latest_release(o, r)
    snap["links"] = collect_links(o, r, n)
    snap["duplicates"] = collect_duplicates(o, r, title_keywords(issue["title"]), exclude_number=n)
    return snap


# ----------------------------------------------------------------------------- rendering

def signature(snap):
    last = snap["comments"][-1]["id"] if snap["comments"] else 0
    return f"{snap['issue']['comments']}:{snap['issue']['updated_at']}:{last}"


def select_comments(snap, viewer_login):
    cs = snap["comments"]
    if len(cs) <= 12:
        return list(range(len(cs))), 0
    keep = set(range(3)) | set(range(len(cs) - 5, len(cs)))
    maint = [i for i, c in enumerate(cs) if c["assoc"] in MAINT and not is_bot(c["user"], c.get("type"))]
    keep |= set(maint[:8]) | {i for i, c in enumerate(cs) if c["user"] == viewer_login}
    idx = sorted(keep)
    return idx, len(cs) - len(idx)


def detect_gaps(snap):
    iss, gaps = snap["issue"], []
    body = iss["body"]
    first_human_comments = [c for c in snap["comments"] if not is_bot(c["user"], c.get("type"))]
    if snap["kind"] == "issue" and re.search(r"bug|crash|error|fail|broken|regress|exception|doesn'?t work|not working", iss["title"] + " " + body[:600], re.I):
        if not re.search(r"\bv?\d+\.\d+(\.\d+)?\b|\b[0-9a-f]{7,40}\b", body):
            gaps.append("the report gives no version number")
        if not re.search(r"reproduc|steps|minimal|\bmre\b|\bmrp\b|repro", body, re.I):
            gaps.append("the report has no reproduction steps")
        if "```" not in body and not re.search(r"traceback|stack trace|backtrace|error:|panic|segfault|journalctl", body, re.I):
            gaps.append("the report has no command output or log")
    if iss["state"] == "closed":
        gaps.append(f"the thread is closed ({iss.get('state_reason') or 'no reason given'})")
    if iss.get("locked"):
        gaps.append("the thread is locked")
    if first_human_comments:
        last = first_human_comments[-1]
        if last["user"] != snap["viewer"]["login"] and "?" in strip_noise(last["body"]):
            gaps.append(f"the last comment (by @{last['user']}) asks a question: \"{clip(strip_noise(last['body']).replace(chr(10), ' '), 140)}\"")
    for l in snap.get("links", []):
        if "merged" in l and l.startswith("referenced by PR"):
            gaps.append(f"a merged PR is linked ({l}); check whether the fix is in the reporter's version")
            break
    if snap["duplicates"]:
        gaps.append("possible duplicates are listed above; confirm before claiming one")
    return gaps


def role_lines(snap):
    v = snap["viewer"]
    perm = v["permission"]
    lines = [f"You are @{v['login']}; permission on this repository: {perm}."]
    if v.get("is_author"):
        lines.append("The operator opened this thread (they are the reporter).")
    if perm in ("admin", "maintain", "write"):
        lines.append("Role: write access, so possibly a maintainer. Treat them as an outside contributor unless the operator says otherwise; ask one short question only if the answer changes what you may say.")
    else:
        lines.append("Role: outside contributor. Do not decide for the project: no closing, declining or calling something intended; offer observations, pointers and suspicions instead.")
    return lines


def render_thread(snap):
    iss = snap["issue"]
    out = []
    kind = "PR" if snap["kind"] == "pr" else "issue"
    out.append(f"# Case file: {snap['repo']}#{snap['number']} ({kind}) [{iss['state']}]")
    out.append(f"{iss['url']}")
    out.append(f"signature: {signature(snap)}   (pass to `post --expect` so a changed thread stops the post)")
    out.append("")
    out += role_lines(snap)
    meta = f"Opened {iss['created_at'][:10]} by @{iss['user']} ({(iss['assoc'] or '').lower()}). Labels: {', '.join(iss['labels']) or 'none'}. Comments: {iss['comments']}."
    out.append(meta)
    if snap.get("pr"):
        p = snap["pr"]
        out.append(f"PR: {p['head']} -> {p['base']}, {'merged' if p['merged'] else 'not merged'}{', draft' if p['draft'] else ''}, +{p['additions']}/-{p['deletions']} in {p['files']} files.")
    if snap.get("release"):
        out.append(f"Latest release: {snap['release']['tag']} ({snap['release']['date']}).")
    for l in snap.get("links", []):
        out.append(f"- {l}")
    out.append("")
    prof = room_profile(snap["room"]["bodies"]) if snap.get("room") else {"n": 0}
    out.append(render_room(prof, snap["room"]["who"] if snap.get("room") else "n/a"))
    out.append(f"## {iss['title']}")
    out.append(clip(iss["body"], 2200) or "(no description)")
    out.append("")
    idx, omitted = select_comments(snap, snap["viewer"]["login"])
    out.append(f"## Comments ({len(snap['comments'])} total{f', {omitted} in the middle omitted' if omitted else ''})")
    if not snap["comments"]:
        out.append("(none)")
    anchor = (snap.get("anchor") or {}).get("anchor_id") if (snap.get("anchor") or {}).get("anchor") == "issuecomment-" else None
    prev = -1
    for i in idx:
        c = snap["comments"][i]
        if i != prev + 1 and prev != -1:
            out.append("[... comments omitted ...]")
        prev = i
        who = "maintainer" if c["assoc"] in MAINT else ("reporter" if c["user"] == iss["user"] else "participant")
        if is_bot(c["user"], c.get("type")):
            who = "bot"
        mark = "  <== the comment being answered" if anchor and c["id"] == anchor else ""
        out.append(f"### @{c['user']} ({who}) {c['created_at'][:16]}{mark}")
        out.append(clip(c["body"], 700 if c["assoc"] in MAINT else 600))
        out.append("")
    if snap.get("reviews"):
        out.append("## Review summaries")
        for r in snap["reviews"][:6]:
            out.append(f"- @{r['user']} {r['state'].lower()}: {clip(r['body'], 300)}")
        out.append("")
    if snap.get("review_comments"):
        rc = snap["review_comments"]
        target = (snap.get("anchor") or {}).get("anchor_id") if (snap.get("anchor") or {}).get("anchor") in ("discussion_r", "r") else None
        out.append(f"## Inline review comments ({len(rc)} total; the thread being answered is shown in full when a comment URL was given)")
        roots = {c["id"]: c for c in rc if not c["in_reply_to"]}
        shown = 0
        for c in rc:
            root_id = c["in_reply_to"] or c["id"]
            in_target = target is not None and (c["id"] == target or root_id == target or (target in roots and False))
            if (target is not None and not in_target) or (target is None and shown >= 8):
                continue
            shown += 1
            out.append(f"- {c['path']}:{c['line']} @{c['user']} (id {c['id']}): {clip(c['body'], 400)}")
        out.append("")
    if snap["duplicates"]:
        out.append("## Possible duplicates (search by title keywords, open and closed)")
        for d in snap["duplicates"]:
            out.append(f"- #{d['number']} [{d['state']}{'/' + d['reason'] if d.get('reason') else ''}] {clip(d['title'], 90)} {d['url']}")
        out.append("")
    gaps = detect_gaps(snap)
    out.append("## Gaps to close before writing")
    out += [f"- {g}" for g in gaps] if gaps else ["- none detected automatically; still check every claim the draft will make"]
    text = "\n".join(out)
    if len(text) > CAP_TOTAL:
        text = text[:CAP_TOTAL] + "\n[case file truncated]"
    return text


# ----------------------------------------------------------------------------- filing context

def parse_form_fields(yaml_text):
    fields, cur = [], None
    for line in yaml_text.splitlines():
        if re.match(r"\s*-\s*type:", line):
            cur = {"label": None, "required": False}
            fields.append(cur)
        elif cur is not None:
            m = re.match(r"\s*label:\s*['\"]?(.+?)['\"]?\s*$", line)
            if m and not cur["label"]:
                cur["label"] = m[1]
            if re.match(r"\s*required:\s*true", line):
                cur["required"] = True
    return [f for f in fields if f["label"]]


def collect_filing(owner, repo, keywords):
    v = collect_viewer(owner, repo)
    r = v["repo"]
    ctx = {"repo": f"{owner}/{repo}", "viewer": {"login": v["login"], "permission": v["permission"]}, "meta": {
        "archived": r.get("archived"), "has_issues": r.get("has_issues"), "default_branch": r.get("default_branch"), "language": r.get("language"),
        "has_discussions": r.get("has_discussions"), "fork": r.get("fork"), "parent": (r.get("parent") or {}).get("full_name")}}
    templates = {}
    for src in (f"{owner}/{repo}", f"{owner}/.github"):
        listing = gh(f"repos/{src}/contents/.github/ISSUE_TEMPLATE", check=False)
        if isinstance(listing, list):
            for f in listing:
                if f.get("type") == "file":
                    raw = gh(f"repos/{src}/contents/{f['path']}", accept="application/vnd.github.raw", raw=True, check=False)
                    if raw:
                        templates[f["name"]] = raw
            ctx["template_source"] = src
            break
    ctx["templates"] = templates
    docs = {}
    for name in ("CONTRIBUTING.md", ".github/CONTRIBUTING.md", "docs/CONTRIBUTING.md", "SECURITY.md", ".github/SECURITY.md"):
        raw = gh(f"repos/{owner}/{repo}/contents/{name}", accept="application/vnd.github.raw", raw=True, check=False)
        if raw:
            docs[name] = raw
    ctx["docs"] = docs
    labels = gh(f"repos/{owner}/{repo}/labels?per_page=100", check=False)
    ctx["labels"] = [l["name"] for l in labels] if isinstance(labels, list) else []
    bodies, who = collect_room(owner, repo)
    ctx["room"] = {"bodies": bodies, "who": who}
    ctx["release"] = collect_latest_release(owner, repo)
    ctx["duplicates"] = collect_duplicates(owner, repo, keywords)
    ctx["keywords"] = keywords
    return ctx


def render_filing(ctx):
    L = [f"# Filing context: {ctx['repo']}", ""]
    m = ctx["meta"]
    L.append(f"You are @{ctx['viewer']['login']}; permission here: {ctx['viewer']['permission']}. Treat the operator as an outside contributor unless they say otherwise.")
    if m.get("archived"):
        L.append("WARNING: the repository is archived; issues cannot be opened.")
    if m.get("has_issues") is False:
        L.append("WARNING: issues are disabled on this repository; look for discussions or another venue below.")
    if m.get("fork"):
        L.append(f"This is a fork of {m.get('parent')}; bugs in the upstream code usually belong upstream.")
    L.append(f"Language: {m.get('language')}. Discussions enabled: {m.get('has_discussions')}. Default branch: {m.get('default_branch')}.")
    if ctx.get("release"):
        L.append(f"Latest release: {ctx['release']['tag']} ({ctx['release']['date']}). Reproduce on this or the default branch and state which.")
    L.append("")
    L.append(f"## Issue templates ({ctx.get('template_source', 'none found')})")
    cfg = ctx["templates"].get("config.yml", "")
    if cfg:
        if re.search(r"blank_issues_enabled:\s*false", cfg):
            L.append("Blank issues are disabled: pick one of the templates.")
        for name, url in re.findall(r"-\s*name:\s*(.+?)\s*\n\s*url:\s*(\S+)", cfg):
            L.append(f"- contact link: {name.strip(chr(34))} -> {url} (this is where that kind of request belongs)")
    for name, text in ctx["templates"].items():
        if name == "config.yml":
            continue
        title = re.search(r"^name:\s*['\"]?(.+?)['\"]?\s*$", text, re.M)
        if title:
            title = [re.sub(r"\\U([0-9A-Fa-f]{8})", lambda m: chr(int(m[1], 16)), title[1])]
            title = type("T", (), {"__getitem__": lambda self, i: title[0]})()
        L.append(f"### {name}" + (f" ({title[1]})" if title else ""))
        if name.endswith((".yml", ".yaml")):
            fl = parse_form_fields(text)
            L.append("Fields: " + "; ".join(f"{f['label']}{' (required)' if f['required'] else ''}" for f in fl))
        else:
            heads = re.findall(r"^#{1,4}\s*(.+)$", text, re.M)
            L.append("Headings: " + "; ".join(heads) if heads else clip(text, 300))
    if not ctx["templates"]:
        L.append("No templates found; plain paragraphs are fine (see references/filing.md).")
    L.append("")
    L.append("## Project rules that matter for an issue")
    kw = re.compile(r"issue|bug report|feature request|discussion|question|duplicate|reproduc|security|template|support|mailing list|forum|chat|irc|discord", re.I)
    shown = False
    for name, text in ctx["docs"].items():
        lines = [l.strip() for l in text.splitlines() if kw.search(l) and len(l.strip()) > 20 and not l.lstrip().startswith("|")]
        if lines:
            shown = True
            L.append(f"### {name}")
            L += [f"- {clip(l, 220)}" for l in lines[:14]]
    if not shown:
        L.append("(no CONTRIBUTING or SECURITY text found)")
    if any("SECURITY" in n for n in ctx["docs"]):
        L.append("A SECURITY file exists: a suspected vulnerability goes to the channel it names, never into a public issue.")
    L.append("")
    if ctx["labels"]:
        L.append("Existing labels (do not add any unless the operator asks): " + ", ".join(ctx["labels"][:40]))
        L.append("")
    prof = room_profile(ctx["room"]["bodies"])
    L.append(render_room(prof, ctx["room"]["who"]))
    L.append(f"## Duplicate candidates for \"{' '.join(ctx['keywords'])}\"" if ctx["keywords"] else "## Duplicate candidates")
    if ctx["duplicates"]:
        for d in ctx["duplicates"]:
            L.append(f"- #{d['number']} [{d['state']}{'/' + d['reason'] if d.get('reason') else ''}]{' PR' if d['pr'] else ''} {clip(d['title'], 90)} {d['url']}")
    elif ctx["keywords"]:
        L.append("(none found; try another wording with `search`)")
    else:
        L.append("(no keywords given; run `search` with two or three words of the symptom)")
    text = "\n".join(L)
    return text[:CAP_TOTAL] + ("\n[truncated]" if len(text) > CAP_TOTAL else "")


# ----------------------------------------------------------------------------- file / search / post

def cmd_file(a):
    if OFFLINE or a.local:
        p = subprocess.run(["git", "show", f"{a.ref or 'HEAD'}:{a.path}"], capture_output=True, text=True)
        if p.returncode != 0:
            raise Fail(f"git show {a.ref or 'HEAD'}:{a.path} failed (run from a clone, or drop --local)")
        text, ref_label = p.stdout, a.ref or "HEAD (local checkout)"
        sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    else:
        ref = a.ref
        q = f"?ref={ref}" if ref else ""
        text = gh(f"repos/{a.repo}/contents/{a.path}{q}", accept="application/vnd.github.raw", raw=True)
        c = gh(f"repos/{a.repo}/commits/{ref or gh(f'repos/{a.repo}')['default_branch']}", check=False)
        sha = c.get("sha", "") if isinstance(c, dict) else ""
        ref_label = ref or "default branch"
    lines = text.splitlines()
    lo, hi = 1, min(len(lines), 150)
    if a.lines:
        m = re.match(r"(\d+)-(\d+)$", a.lines)
        if not m:
            raise Fail("--lines must look like 120-160")
        lo, hi = int(m[1]), min(int(m[2]), len(lines), int(m[1]) + 199)
    print(f"{a.repo}:{a.path} @ {ref_label}  lines {lo}-{hi} of {len(lines)}")
    for i in range(lo, hi + 1):
        print(f"{i:5d}  {lines[i - 1]}")
    if sha:
        print(f"permalink: https://github.com/{a.repo}/blob/{sha}/{a.path}#L{lo}-L{hi}")


def cmd_search(a):
    q = " ".join(a.keywords)
    if a.code:
        res = gh("search/code", fields={"q": f"repo:{a.repo} {q}", "per_page": "8"})
        for it in res.get("items", []):
            print(f"{it['path']}  {it['html_url']}")
        return
    res = gh("search/issues", fields={"q": f"repo:{a.repo} {q}", "per_page": "10"})
    for it in res.get("items", []):
        kind = "PR" if "pull_request" in it else "issue"
        reason = f"/{it['state_reason']}" if it.get("state_reason") else ""
        print(f"#{it['number']} {kind} [{it['state']}{reason}] {it['title']}  {it['html_url']}")
    if not res.get("items"):
        print("(no results; search terms are ANDed, try fewer or different words)")


def require_yes(a):
    if not a.yes:
        raise Fail("not posted: this command needs --yes, which is passed only after the operator approved the exact text")


def read_body(path):
    text = open(path, encoding="utf-8").read()
    if not text.strip():
        raise Fail("the body file is empty")
    return text


def cmd_post(a):
    body = read_body(a.body_file)
    if a.what == "comment":
        t = parse_ref(a.args[0])
        o, r, n = t["owner"], t["repo"], t["number"]
        if a.expect:
            cur = gh(f"repos/{o}/{r}/issues/{n}")
            last = gh(f"repos/{o}/{r}/issues/{n}/comments?per_page=1&page={max(1, cur.get('comments', 1))}", check=False) if cur.get("comments") else []
            now = f"{cur.get('comments', 0)}:{cur['updated_at']}:{last[-1]['id'] if last else 0}"
            if now != a.expect:
                raise Fail(f"not posted: the thread changed since the case file (was {a.expect}, now {now}); re-read it and redraft if needed")
        path, fields = f"repos/{o}/{r}/issues/{n}/comments", None
        target = f"{o}/{r}#{n}"
    elif a.what == "review-reply":
        repo, pr, cid = a.args
        path, target = f"repos/{repo}/pulls/{pr}/comments/{cid}/replies", f"{repo}#{pr} review comment {cid}"
    elif a.what == "issue":
        repo = a.args[0]
        if not a.title:
            raise Fail("--title is required")
        path, target = f"repos/{repo}/issues", f"new issue in {repo}"
    else:
        raise Fail("post what? comment | review-reply | issue")
    print(f"target: {target}\nbody: {len(body)} characters, {words(body)} words")
    if a.dry_run:
        print("dry run: nothing sent")
        return
    require_yes(a)
    if a.what == "issue":
        out = gh(path, method="POST", fields={"title": a.title}, body_file=a.body_file)
    else:
        out = gh(path, method="POST", body_file=a.body_file)
    print(f"posted: {out.get('html_url')}")


# ----------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(prog="ghr.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("thread"); t.add_argument("ref"); t.add_argument("--snapshot"); t.add_argument("--save-snapshot")
    n = sub.add_parser("new"); n.add_argument("repo"); n.add_argument("--keywords", default="")
    f = sub.add_parser("file"); f.add_argument("repo"); f.add_argument("path"); f.add_argument("--ref"); f.add_argument("--lines"); f.add_argument("--local", action="store_true")
    s = sub.add_parser("search"); s.add_argument("repo"); s.add_argument("keywords", nargs="+"); s.add_argument("--code", action="store_true")
    p = sub.add_parser("post"); p.add_argument("what"); p.add_argument("args", nargs="+"); p.add_argument("--body-file", required=True)
    p.add_argument("--title"); p.add_argument("--expect"); p.add_argument("--yes", action="store_true"); p.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    try:
        if a.cmd == "thread":
            if a.snapshot:
                snap = json.load(open(a.snapshot, encoding="utf-8"))
            else:
                snap = collect_thread(a.ref)
                if a.save_snapshot:
                    json.dump(snap, open(a.save_snapshot, "w", encoding="utf-8"))
            print(render_thread(snap))
        elif a.cmd == "new":
            o, r = a.repo.split("/")
            print(render_filing(collect_filing(o, r, a.keywords.split())))
        elif a.cmd == "file":
            cmd_file(a)
        elif a.cmd == "search":
            cmd_search(a)
        elif a.cmd == "post":
            cmd_post(a)
    except Fail as e:
        print(f"ghr: {e}", file=sys.stderr)
        sys.exit(3 if "thread changed" in str(e) else 2)


if __name__ == "__main__":
    main()
