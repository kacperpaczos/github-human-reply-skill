#!/usr/bin/env python3
"""Summarise benchmark runs: text metrics, blind identification, content verdicts.

Usage: python3 benchmark/report.py [--full] [--set test|dev] [--v1]
  --full  also print every reply side by side
  --set   test = cases the skill was never tuned on, dev = the six pilot cases
  --v1    score the first version of the skill (dev cases only)
"""
import json, pathlib, re, statistics as st, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORK = ROOT / "benchmark" / "work"
ARMS = ("human", "skill", "baseline")


def metrics(t):
    t = (t or "").replace("\r", "").strip()
    prose = re.sub(r"```.*?```", " ", t, flags=re.S)
    sents = [s for s in re.split(r"(?<=[.!?])\s+", prose) if s.strip()]
    sl = [len(s.split()) for s in sents]
    return {
        "words": len(t.split()), "paragraphs": len([p for p in re.split(r"\n\s*\n", t) if p.strip()]),
        "sentences": len(sents), "sent_len_sd": round(st.pstdev(sl), 1) if len(sl) > 1 else 0,
        "headers": bool(re.search(r"^#{1,5}\s", prose, re.M)), "bullets": bool(re.search(r"^\s*([-*]|\d+\.)\s", prose, re.M)),
        "bold": "**" in prose, "code_block": "```" in t, "em_dash": "—" in prose,
        "greeting": bool(re.match(r"\s*(hi|hello|hey)\b", t, re.I)), "thanks_open": bool(re.match(r"\s*(thanks|thank you)", t, re.I)),
        "signoff": bool(re.search(r"(let me know|hope this helps|feel free)[^\n]*$", t.strip(), re.I)),
        "links": len(re.findall(r"https?://|#\d+", t)),
    }


FAILED = []  # cases excluded because a run produced no draft


def arg(name):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else None


def load():
    rows = []
    v1 = "--v1" in sys.argv
    tag = arg("--tag")
    skill_file, jdir = ("skill_v1.json", "judgements_v1") if v1 else ("skill.json", "judgements")
    rdir = "runs_" + tag if tag else "runs"
    if tag:
        jdir = "judgements_" + tag
    test = set((WORK / "test_cases.txt").read_text().split()) if (WORK / "test_cases.txt").exists() else set()
    which = arg("--set")
    for h in sorted((WORK / "hidden").glob("*.json")):
        h = json.loads(h.read_text())
        if (which == "test" and h["id"] not in test) or (which == "dev" and h["id"] in test):
            continue
        d = WORK / rdir / h["id"]
        if not (d / skill_file).exists() or not (d / "baseline.json").exists():
            continue
        runs = {"skill": json.loads((d / skill_file).read_text()), "baseline": json.loads((d / "baseline.json").read_text())}
        if runs["skill"]["reply"] is None or runs["baseline"]["reply"] is None:
            FAILED.append((h["id"], [a for a in ("skill", "baseline") if runs[a]["reply"] is None]))
            continue
        texts = {"human": h["reply"], "skill": runs["skill"]["reply"], "baseline": runs["baseline"]["reply"]}
        js = {}
        for f in sorted((WORK / jdir / h["id"]).glob("*.json")) if (WORK / jdir / h["id"]).exists() else []:
            judge, part, _ = f.name.split(".")
            js.setdefault(part, {})[judge] = json.loads(f.read_text())
        rows.append({"h": h, "runs": runs, "texts": texts, "m": {a: metrics(texts[a]) for a in ARMS}, "j": js})
    return rows


def main():
    rows = load()
    n = len(rows)
    print(f"# Reply benchmark: {n} cases\n")
    if FAILED:
        print("Excluded, no draft from: " + "; ".join(f"{c} ({'+'.join(a)})" for c, a in FAILED) + "\n")
    print("## Text shape (median unless noted)\n")
    print("| | human | skill | baseline |\n|---|---|---|---|")
    med = lambda a, k: st.median([r["m"][a][k] for r in rows if r["texts"][a] and r["texts"][a] != "NO_REPLY"])
    share = lambda a, k: f"{sum(1 for r in rows if r['m'][a][k])}/{n}"
    for k in ("words", "paragraphs", "sentences", "sent_len_sd", "links"):
        print(f"| {k} | " + " | ".join(str(med(a, k)) for a in ARMS) + " |")
    for k in ("headers", "bullets", "bold", "code_block", "em_dash", "greeting", "thanks_open", "signoff"):
        print(f"| {k} (cases) | " + " | ".join(share(a, k) for a in ARMS) + " |")
    ratio = lambda a: st.median([r["m"][a]["words"] / max(1, r["m"]["human"]["words"]) for r in rows if r["texts"][a] and r["texts"][a] != "NO_REPLY"])
    print(f"| length / human length | 1.0 | {ratio('skill'):.1f} | {ratio('baseline'):.1f} |")
    print(f"| NO_REPLY | - | {sum(1 for r in rows if r['texts']['skill'] == 'NO_REPLY')} | {sum(1 for r in rows if r['texts']['baseline'] == 'NO_REPLY')} |")
    for a in ("skill", "baseline"):
        toks = [r["runs"][a].get("tokens") for r in rows if r["runs"][a].get("tokens")]
        print(f"\n{a}: median {st.median([r['runs'][a]['seconds'] for r in rows])}s, {st.median([r['runs'][a]['turns'] or 0 for r in rows])} turns"
              + (f", median {round(st.median(toks)/1000)}k tokens (total {round(sum(toks)/1000)}k)" if toks else "")
              + (f", ${sum(r['runs'][a]['cost_usd'] or 0 for r in rows):.2f} total" if any(r['runs'][a].get('cost_usd') for r in rows) else "")
              + (f", used the script in {sum(1 for r in rows if r['runs'][a].get('used_script'))}/{len(rows)}" if a == "skill" else "")
              + (f", flagged for network use in {sum(1 for r in rows if r['runs'][a].get('leaks'))}" ))

    print("\n## Blind test: which reply did the judge take for the real one?\n")
    judges = sorted({j for r in rows for j in r["j"].get("blind", {})})
    print("| judge | picked human | picked skill | picked baseline | skill ranked above baseline |\n|---|---|---|---|---|")
    tot = {a: 0 for a in ARMS}; tn = 0
    for j in judges:
        c = {a: 0 for a in ARMS}; above = k = 0
        for r in rows:
            b = r["j"].get("blind", {}).get(j)
            if not b or b.get("human") not in b["mapping"]:
                continue
            k += 1; c[b["mapping"][b["human"]]] += 1
            rk = [b["mapping"].get(x) for x in b.get("ranking_most_to_least_humanlike", [])]
            if "skill" in rk and "baseline" in rk and rk.index("skill") < rk.index("baseline"):
                above += 1
        for a in ARMS:
            tot[a] += c[a]
        tn += k
        print(f"| {j} | {c['human']}/{k} | {c['skill']}/{k} | {c['baseline']}/{k} | {above}/{k} |")
    print(f"| all | {tot['human']}/{tn} | {tot['skill']}/{tn} | {tot['baseline']}/{tn} | |")

    print("\n## Content, judged against the real reply and the thread's outcome\n")
    print("| | skill | baseline |\n|---|---|---|")
    agg = {a: {"same": 0, "partly": 0, "different": 0, "wrong": 0, "unsupported": 0, "commitments": 0, "as is": 0, "after small edits": 0, "no": 0, "embarrassing": 0, "n": 0}
           for a in ("skill", "baseline")}
    pref = {"skill": 0, "baseline": 0, "tie": 0}
    for r in rows:
        for j, c in r["j"].get("content", {}).items():
            for lab, arm in c["mapping"].items():
                v = c.get(lab) or {}
                g = agg[arm]; g["n"] += 1
                for key in (v.get("act"), v.get("usable")):
                    if key in g:
                        g[key] += 1
                g["wrong"] += len(v.get("wrong") or []); g["unsupported"] += len(v.get("unsupported") or [])
                g["commitments"] += len(v.get("commitments") or []); g["embarrassing"] += bool(v.get("embarrassing"))
            p = c.get("preferred")
            pref[c["mapping"].get(p, "tie")] += 1
    for k, label in (("same", "same move as the real reply"), ("partly", "partly the same move"), ("different", "different move"),
                     ("wrong", "contradicted statements (total)"), ("unsupported", "unsupported statements (total)"),
                     ("commitments", "commitments not in the real reply (total)"), ("as is", "usable as is"),
                     ("after small edits", "usable after small edits"), ("no", "not usable"), ("embarrassing", "embarrassing")):
        print(f"| {label} | {agg['skill'][k]}/{agg['skill']['n']} | {agg['baseline'][k]}/{agg['baseline']['n']} |" if k not in ("wrong", "unsupported", "commitments")
              else f"| {label} | {agg['skill'][k]} | {agg['baseline'][k]} |")
    print(f"\nPreferred draft (judge verdicts): skill {pref['skill']}, baseline {pref['baseline']}, tie {pref['tie']}")

    if "--full" in sys.argv:
        for r in rows:
            h = r["h"]
            print(f"\n---\n### {h['repo']}#{h['number']} ({h['kind']}, @{h['login']}, {h['role']})\n{h['url']}\n")
            for a in ARMS:
                print(f"**{a}** ({r['m'][a]['words']} words)\n\n{(r['texts'][a] or '(none)').strip()}\n")
            for j, b in r["j"].get("blind", {}).items():
                print(f"- blind {j}: took **{b['mapping'].get(b.get('human'))}** for the human; " + "; ".join(f"{b['mapping'][k]}: {v}" for k, v in (b.get("tells") or {}).items() if k in b["mapping"]))
            for j, c in r["j"].get("content", {}).items():
                print(f"- content {j}: prefers **{c['mapping'].get(c.get('preferred'), 'tie')}**; " + "; ".join(
                    f"{arm}: {c[l].get('act')}/{c[l].get('usable')}, wrong={c[l].get('wrong')}, unsupported={len(c[l].get('unsupported') or [])} ({c[l].get('note')})" for l, arm in c["mapping"].items() if l in c))


if __name__ == "__main__":
    main()
