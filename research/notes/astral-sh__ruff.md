# astral-sh/ruff

## Opening an issue
All three kinds are wanted as issues; ty reports go to astral-sh/ty.

(a) Bugs. One required "Summary" (minimal example, command, ideally `--isolated`, playground link) and an optional version. Reports fixed within a day are a snippet, the command, the output and the version (#27333, #28989, #27245). Long structured reports are judged on merit: #28493 ended as a docs change, #29849 as "working as intended". 22% closed as duplicates.

(b) Rule requests. A single "Summary". A short motivated idea can land (#27310); style requests are folded into older issues (#29767, #29550).

(c) Fix proposals sit inside the issue as "Likely cause" or "Suggested resolution" (#27245, #28493).

Titles: rule code plus the misbehaviour: "SLF001 false positives in __new__".

## Issues and pull requests
45% of issues closed through a PR, though only 14% of PR bodies carry a closing keyword; maintainers also close by hand ("fixed in #28722"). Outsider PRs put "Closes #N" under `## Summary`, then `## Test Plan` (#30333, #30256). Titles: "[`flake8-bugbear`] Mark `range` as immutable (`B008`)". 26% of outsider PRs are merged. Maintainers often fix a fresh bug themselves, leaving parallel outsider PRs unmerged (#28721). PRs following a maintainer's stated direction get merged (#28509, #28542, #29001).

## How the conversation goes
Median first response is 2 hours, mostly from ntBre. Replies run about 40 words, open with thanks, hedge ("I think", "Sorry if I'm misunderstanding") and carry occasional emoji. A no is "working as intended" plus the flags to use instead (#29849, #27334). Duplicates are "folded into" the older issue and closed by hand (#29672). Reporters reply with short thanks. All English.

## Maintainer voice
- "Thanks for the report! Seems like the rule should not apply to `singledispatch` functions." (#27333)
- "Thanks for the suggestion! I think we can fold this into https://github.com/astral-sh/ruff/issues/22394." (#29550)
- "The issue is that our default Regex only matches ASCII identifiers" (#28721)
- "So I believe this is working as intended." (#27334)
- "Is this the kind of code that caused the diagnostic in a real project?" (#27324)

## If you are an outsider here
1. Name the rule code in the title; give a snippet, the `ruff check --isolated --select X` command, its output and `ruff version`.
2. Search first and link related issues yourself (#29767).
3. With many similar findings, file one consolidated issue (#29400).
4. Argue fix safety on runtime behaviour or lost comments, the criteria stated in #28493.
5. Do not race a PR onto a fresh bug; wait for a maintainer's direction.

## What this sample cannot tell
Only closed issues were sampled and nearly all replies come from one maintainer; the PR sample is mostly ty work.
