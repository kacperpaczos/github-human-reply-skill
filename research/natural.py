#!/usr/bin/env python3
"""How people naturally write on GitHub, measured on the collected corpus.

Reads research/data/*.json (collect.py) and, when present, the benchmark replies
(benchmark/work), and prints markdown tables. Also writes research/data/natural.json.
Heuristics are crude on purpose; they are validated by `--examples MOVE`, which
prints random comments carrying a label so they can be read.

Usage:
  python3 research/natural.py                  # all tables
  python3 research/natural.py --examples ask   # sample comments labelled `ask`
"""
import glob, json, pathlib, random, re, statistics as st, sys
from datetime import datetime

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from analyze import DATA, is_bot, kind, maintainers, MAINT  # noqa: E402

SKIP_TEXT = {"siyuan-note/siyuan"}  # Chinese: whitespace word counts are meaningless

MOVES = {
    "fixed": r"(\bfixed (in|by|with|on)\b|\bshould be fixed\b|\b(fix|fixes) (is )?(in|merged|landed|pushed)\b|\bresolved (in|by)\b|\b(merged|landed|implemented) (in|on|already)\b|\balready (implemented|merged|fixed|landed|supported|possible)\b|\bcloses? #\d+|\bfixed by #?\d+|\b(i|we)('ve| have)? (opened|sent|pushed|submitted|created) (a |the )?(pr|pull request|patch|fix)\b|\b(pr|patch|fix) (is )?(up|here|ready)\b|\bi'll (send|open|push|submit) (a |the )?(pr|fix|patch))",
    "duplicate": r"(\bduplicate of\b|\bdup of\b|\bdupe\b|\bsame as #\d+|\balready (reported|tracked|filed)\b|\btracked (at|in|by)\b|\bfold this into\b|\bcovered by #|\bsee #\d+)",
    "redirect": r"(\bbelongs (in|to|on)\b|\bwrong (repo|place|tracker|project)\b|\bshould be (filed|reported|opened|asked)\b|\bplease (open|file|report|ask|use)\b|\bhave you (reported|filed|asked|opened)\b|\byou need to (report|file|ask)\b|\b(report|file) (it|this|the issue) (to|with|upstream)\b|\bask (on|in) |\bdiscussions?\b|\bmailing list\b|\bupstream\b|\b(report|file|open) (it|this|an issue) (to|at|in|on|over)\b|\bissue tracker is for\b)",
    "decline": r"(\bnot planned\b|\bwon'?t (fix|add|support|implement|change|do|accept)\b|\bwill not\b|\b(we|i)('m| am| are|'re) (not )?going to\b|\bnot going to\b|\bout of scope\b|\bnot a goal\b|\bno plans\b|\bnot interested\b|\bby design\b|\bworking as (intended|designed)\b|\b(is|it'?s|this is|as) (intended|intentional|expected|normal)\b|\bintentional (change|behaviou?r)\b|\b(do not|don'?t|won'?t) (accept|allow)\b|\bnot allowed\b|\bbefore considering\b|\bexpected behaviou?r\b|\bnot a bug\b|\bwontfix\b|\b(is|are|isn'?t|aren'?t) (not )?supported\b|\bnot something (we|i)\b)",
    "ask": r"(\?|\bplease (provide|share|attach|post|paste|show|try|run|check|test|confirm|send|include|upload|retest|give)\b|\b(can|could|would) you\b|\bdo you\b|\bdid you\b|\bwhich version\b|\bwhat version\b|\bmre\b|\bsteps to reproduce\b|\bneed more (info|information|details)\b)",
    "invite": r"(\bpr welcome\b|\bpatch(es)? (is |are )?welcome\b|\bpull requests? (is |are )?welcome\b|\bwould you like to (send|submit|make|try)\b|\bfeel free to (send|submit|open|make)\b|\bhappy to review\b|\bare you (up to|willing)\b|\bwould you be willing\b|\bwilling to (submit|send|make)\b|\bplease submit\b[^.]{0,40}\b(pr|pull request|patch)\b|\bwant to (send|submit|make) a (pr|patch)\b)",
}
MOVE_RE = {k: re.compile(v, re.I) for k, v in MOVES.items()}
HEDGE = re.compile(r"\b(i think|i guess|maybe|perhaps|probably|possibly|might|iirc|afaik|afaict|not sure|i believe|i suspect|seems|looks like|appears)\b", re.I)
TICS = re.compile(r"\b(additionally|furthermore|moreover|it('| i)s worth noting|in summary|to summarize|comprehensive|robust|seamless|crucial|delve|leverage|ensure that|great question|good catch|great catch)\b", re.I)
OFFER = re.compile(r"(let me know|hope (this|that) helps|feel free to|happy to help|don'?t hesitate|any questions)[^\n]*\s*$", re.I)


def words(s):
    return len(re.findall(r"\S+", s or ""))


def feats(body):
    t = (body or "").replace("\r", "").strip()
    prose = re.sub(r"```.*?```", " ", t, flags=re.S)
    sents = [s for s in re.split(r"(?<=[.!?])\s+", prose.strip()) if s.strip()]
    paras = [p for p in re.split(r"\n\s*\n", prose) if p.strip()]
    first = sents[0] if sents else ""
    return {
        "words": words(t), "sentences": len(sents), "paragraphs": len(paras), "first_sentence_words": words(first),
        "code_block": "```" in t, "inline_code": bool(re.search(r"`[^`\n]+`", prose)),
        "link": bool(re.search(r"https?://", t)), "issue_ref": bool(re.search(r"(?<![\w/])#\d+", t)),
        "quote": bool(re.search(r"^\s*>", t, re.M)), "list": bool(re.search(r"^\s*([-*]|\d+\.)\s", prose, re.M)),
        "header": bool(re.search(r"^#{1,5}\s", prose, re.M)), "bold": "**" in prose,
        "emoji": bool(re.search("[\U0001F300-\U0001FAFF☀-➿]", t)), "question": "?" in prose,
        "exclaim": "!" in prose, "lower_start": t[:1].islower(), "no_final_period": not prose.strip().endswith((".", "?", "!", ":")),
        "greeting": bool(re.match(r"\s*(hi|hello|hey|dear|good (morning|day))\b", t, re.I)),
        "thanks_open": bool(re.match(r"\s*(thanks|thank you|thx)", t, re.I)),
        "thanks_any": bool(re.search(r"\b(thanks|thank you|thx)\b", t, re.I)),
        "hedge": bool(HEDGE.search(prose)), "first_person": bool(re.search(r"\b(I|I'm|I've|I'd|I'll)\b", prose)),
        "we": bool(re.search(r"\b(we|our)\b", prose, re.I)), "offer": bool(OFFER.search(t)),
        "em_dash": "—" in prose, "tics": bool(TICS.search(prose)), "mention": bool(re.search(r"(?<![\w`])@\w", prose)),
        "only_link": bool(re.fullmatch(r"\s*(<?https?://\S+>?\s*)+", t)),
    }


def moves(body):
    t = (body or "")
    prose = re.sub(r"```.*?```", " ", t, flags=re.S)
    prose = "\n".join(l for l in prose.splitlines() if not l.lstrip().startswith(">"))
    found = [m for m, rx in MOVE_RE.items() if rx.search(prose)]
    return found or ["explain"]


def primary(ms):
    for m in ("duplicate", "redirect", "fixed", "decline", "invite", "ask"):
        if m in ms:
            return m
    return "explain"


def load():
    return [json.loads(open(p).read()) for p in sorted(glob.glob(str(DATA / "*__*.json")))]


def roles(rec):
    maint = maintainers(rec)
    out = []
    for i in rec["issues"]:
        if is_bot(i["author"]):
            continue
        rep = (i["author"] or {}).get("login")
        k = kind(i)
        for pos, c in enumerate([c for c in i["comments"]["nodes"] if not is_bot(c["author"])]):
            lg = c["author"]["login"]
            role = "reporter" if lg == rep else ("maintainer" if (lg in maint or c["authorAssociation"] in MAINT) else "other")
            out.append({"repo": rec["repo"], "issue": i, "kind": k, "pos": pos, "role": role, "login": lg, "c": c})
    return out


def pct(n, d):
    return round(100 * n / d) if d else 0


def med(xs):
    xs = list(xs)
    return round(st.median(xs), 1) if xs else None


def table(head, rows):
    print("| " + " | ".join(head) + " |\n|" + "|".join("---" for _ in head) + "|")
    for r in rows:
        print("| " + " | ".join(str(x) for x in r) + " |")
    print()


BOOL = ["greeting", "thanks_open", "thanks_any", "header", "bold", "list", "emoji", "exclaim", "quote", "code_block", "inline_code", "link", "issue_ref",
        "question", "hedge", "first_person", "we", "lower_start", "no_final_period", "offer", "tics", "em_dash", "only_link"]


def profile(rows):
    f = [feats(r["c"]["body"]) for r in rows]
    n = len(f)
    d = {"n": n, "words_med": med(x["words"] for x in f), "words_p25": round(st.quantiles([x["words"] for x in f], n=4)[0]) if n > 3 else None,
         "words_p75": round(st.quantiles([x["words"] for x in f], n=4)[2]) if n > 3 else None,
         "sentences_med": med(x["sentences"] for x in f), "paragraphs_med": med(x["paragraphs"] for x in f),
         "first_sentence_words_med": med(x["first_sentence_words"] for x in f),
         "one_paragraph": pct(sum(1 for x in f if x["paragraphs"] <= 1), n), "le15": pct(sum(1 for x in f if x["words"] <= 15), n),
         "gt100": pct(sum(1 for x in f if x["words"] > 100), n)}
    for k in BOOL:
        d[k] = pct(sum(1 for x in f if x[k]), n)
    return d


def main():
    recs = [r for r in load() if r["repo"] not in SKIP_TEXT]
    allc = [c for r in recs for c in roles(r)]
    if "--examples" in sys.argv:
        want = sys.argv[sys.argv.index("--examples") + 1]
        pool = [c for c in allc if c["role"] == "maintainer" and primary(moves(c["c"]["body"])) == want and 8 <= words(c["c"]["body"]) <= 120]
        random.seed(3)
        for c in random.sample(pool, min(12, len(pool))):
            print(f"--- {c['repo']}#{c['issue']['number']} @{c['login']}: {c['c']['body'][:320]!r}")
        return
    out = {}
    M = [c for c in allc if c["role"] == "maintainer"]
    R = [c for c in allc if c["role"] == "reporter"]
    O = [c for c in allc if c["role"] == "other"]
    F = [c for c in M if c["pos"] == 0 or all(x["role"] == "reporter" for x in allc if x["issue"] is c["issue"] and x["pos"] < c["pos"])]

    print(f"# Measured on {len(recs)} repositories (siyuan excluded from text measures), {len(allc)} human comments\n")
    print("## 1. Comment profile by role (share of comments, %, unless noted)\n")
    groups = {"maintainer": M, "maintainer, first reply to reporter": F, "other participant": O, "reporter": R}
    profs = {k: profile(v) for k, v in groups.items()}
    out["profile"] = profs
    keys = ["n", "words_med", "words_p25", "words_p75", "sentences_med", "paragraphs_med", "first_sentence_words_med", "one_paragraph", "le15", "gt100"] + BOOL
    table(["measure"] + list(groups), [[k] + [profs[g][k] for g in groups] for k in keys])

    print("## 2. What a maintainer comment does (move), and how long it is\n")
    lab = [(c, moves(c["c"]["body"])) for c in M]
    rows = []
    for m in ["explain", "ask", "decline", "duplicate", "redirect", "fixed", "invite"]:
        sel = [c for c, ms in lab if primary(ms) == m]
        anyc = [c for c, ms in lab if m in ms]
        w = [words(c["c"]["body"]) for c in sel]
        rows.append([m, pct(len(sel), len(lab)), pct(len(anyc), len(lab)), med(w), round(st.quantiles(w, n=4)[0]) if len(w) > 3 else "", round(st.quantiles(w, n=4)[2]) if len(w) > 3 else "",
                     pct(sum(1 for c in sel if "```" in c["c"]["body"]), len(sel)), pct(sum(1 for c in sel if re.search(r"https?://|#\d+", c["c"]["body"])), len(sel))])
    table(["primary move", "% of comments (one label)", "% containing it (multi-label)", "median words", "p25", "p75", "% with code block", "% with link or #ref"], rows)
    out["moves"] = rows
    print("First maintainer reply, by kind of issue and move (% of first replies)\n")
    FL = [(c, primary(moves(c["c"]["body"]))) for c in F]
    mv = ["explain", "ask", "decline", "duplicate", "redirect", "fixed", "invite"]
    rows = []
    for k in ["bug", "feature", "question", "other"]:
        sel = [m for c, m in FL if c["kind"] == k]
        rows.append([k, len(sel)] + [pct(sel.count(m), len(sel)) for m in mv] + [med(words(c["c"]["body"]) for c, _ in FL if c["kind"] == k)])
    table(["issue kind", "n"] + mv + ["median words"], rows)
    out["first_by_kind"] = rows

    print("## 3. Per project: maintainer comment length and shape\n")
    rows = []
    for r in recs:
        mc = [c for c in M if c["repo"] == r["repo"]]
        if len(mc) < 20:
            continue
        p = profile(mc)
        rows.append([r["repo"].split("/")[1], p["n"], p["words_med"], p["le15"], p["one_paragraph"], p["code_block"], p["link"], p["thanks_open"], p["greeting"], p["hedge"], p["lower_start"], p["no_final_period"]])
    table(["project", "n", "median words", "<=15 words %", "one paragraph %", "code block %", "link %", "thanks opener %", "greeting %", "hedge %", "lowercase start %", "no final period %"], rows)
    out["per_project"] = rows

    print("## 4. Human replies vs drafts on the same threads (benchmark)\n")
    W = ROOT = HERE.parent / "benchmark" / "work"
    pairs = []
    test_file = W / "test_cases.txt"
    test_ids = set(test_file.read_text().split()) if test_file.exists() else None  # only threads the skill was never tuned on
    for hp in sorted((W / "hidden").glob("*.json")) if (W / "hidden").exists() else []:
        h = json.loads(hp.read_text())
        if test_ids is not None and h["id"] not in test_ids:
            continue
        d = W / "runs" / h["id"]
        if not (d / "skill.json").exists() or not (d / "baseline.json").exists() or h["repo"] in SKIP_TEXT:
            continue
        s, b = (json.loads((d / a).read_text())["reply"] for a in ("skill.json", "baseline.json"))
        if s and s != "NO_REPLY" and b:
            pairs.append({"human": h["reply"], "skill": s, "baseline": b})
    arms = ["human", "skill", "baseline"]
    ps = {a: [feats(p[a]) for p in pairs] for a in arms}
    rows = [["n"] + [len(pairs)] * 3]
    for k in ["words", "sentences", "paragraphs", "first_sentence_words"]:
        rows.append([k + " (median)"] + [med(x[k] for x in ps[a]) for a in arms])
    for k in ["one_paragraph"]:
        rows.append(["one paragraph %"] + [pct(sum(1 for x in ps[a] if x["paragraphs"] <= 1), len(pairs)) for a in arms])
    for k in ["code_block", "inline_code", "link", "issue_ref", "list", "quote", "question", "hedge", "first_person", "we", "lower_start", "no_final_period", "thanks_any", "offer", "tics", "exclaim"]:
        rows.append([k + " %"] + [pct(sum(1 for x in ps[a] if x[k]), len(pairs)) for a in arms])
    for m in ["explain", "ask", "decline", "duplicate", "redirect", "fixed", "invite"]:
        rows.append([f"primary move = {m} %"] + [pct(sum(1 for p in pairs if primary(moves(p[a])) == m), len(pairs)) for a in arms])
    table(["measure"] + arms, rows)
    out["human_vs_draft"] = rows
    ratio = [len(p["skill"].split()) / max(1, len(p["human"].split())) for p in pairs]
    print(f"Skill draft length / human length: median {st.median(ratio):.1f}, share of drafts at most 1.5x the human: {pct(sum(1 for r in ratio if r <= 1.5), len(ratio))}%\n")

    print("## 5. What a reporter's issue looks like, and what goes with getting it answered or fixed\n")
    rows_i = []
    for r in recs:
        maint = maintainers(r)
        for i in r["issues"]:
            rep = (i["author"] or {}).get("login")
            if is_bot(i["author"]) or rep in maint or i["authorAssociation"] in MAINT:
                continue
            hum = [c for c in i["comments"]["nodes"] if not is_bot(c["author"]) and c["author"]["login"] != rep]
            sub = [c for c in hum if words(c["body"]) >= 8]
            first = hum[0] if hum else None
            b = i["body"] or ""
            rows_i.append({"repo": r["repo"], "k": kind(i), "w": words(b), "tw": words(i["title"]),
                           "code": "```" in b, "version": bool(re.search(r"\bv?\d+\.\d+(\.\d+)?\b", b)),
                           "repro": bool(re.search(r"steps to reproduce|reproduc|minimal|\bmre\b|\bmrp\b|repro", b, re.I)),
                           "templ": len(re.findall(r"^#{2,4}\s", b, re.M)) >= 2,
                           "shot": bool(re.search(r"user-attachments|<img|!\[|\.png|\.jpg|\.gif|\.mp4", b)),
                           "log": bool(re.search(r"(traceback|stack trace|backtrace|error:|panic|segfault|coredump|journalctl|\blog\b)", b, re.I)),
                           "answered": bool(sub), "completed": i["stateReason"] == "COMPLETED",
                           "rejected": i["stateReason"] in ("NOT_PLANNED", "DUPLICATE"),
                           "hours": (datetime.fromisoformat(first["createdAt"].replace("Z", "+00:00")) - datetime.fromisoformat(i["createdAt"].replace("Z", "+00:00"))).total_seconds() / 3600 if first else None})
    print(f"{len(rows_i)} issues by non-maintainers. Differences are correlations, not effects; the table shows the pooled share and the mean within-project difference (projects with 10+ issues on each side).\n")

    def contrast(name, f):
        res = []
        for outc in ("answered", "completed", "rejected"):
            a = [x for x in rows_i if f(x)]
            b = [x for x in rows_i if not f(x)]
            diffs = []
            for repo in {x["repo"] for x in rows_i}:
                aa = [x[outc] for x in a if x["repo"] == repo]
                bb = [x[outc] for x in b if x["repo"] == repo]
                if len(aa) >= 10 and len(bb) >= 10:
                    diffs.append(100 * (sum(aa) / len(aa) - sum(bb) / len(bb)))
            res.append(f"{pct(sum(x[outc] for x in a), len(a))} vs {pct(sum(x[outc] for x in b), len(b))} ({'+' if st.mean(diffs) >= 0 else ''}{round(st.mean(diffs))})" if diffs else "n/a")
        return [name, len(a), len(b)] + res
    feats_i = [("body <= 60 words", lambda x: x["w"] <= 60), ("body 60-250 words", lambda x: 60 < x["w"] <= 250), ("body > 250 words", lambda x: x["w"] > 250),
               ("has code block", lambda x: x["code"]), ("mentions a version number", lambda x: x["version"]), ("mentions reproduction", lambda x: x["repro"]),
               ("filled a template (2+ headings)", lambda x: x["templ"]), ("has screenshot or video", lambda x: x["shot"]), ("has log or error text", lambda x: x["log"]),
               ("title <= 6 words", lambda x: x["tw"] <= 6), ("title > 12 words", lambda x: x["tw"] > 12)]
    table(["feature present", "n with", "n without", "answered by a human (with vs without, within-project diff)", "closed as completed", "closed as not planned / duplicate"],
          [contrast(n, f) for n, f in feats_i])
    out["reports"] = [contrast(n, f) for n, f in feats_i]
    print("Report length in words by issue kind (median, non-maintainer reporters):", {k: med(x["w"] for x in rows_i if x["k"] == k) for k in ("bug", "feature", "question", "other")}, "\n")
    (DATA / "natural.json").write_text(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
