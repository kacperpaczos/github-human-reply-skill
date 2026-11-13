# helix-editor/helix

## Opening an issue
Bugs and narrow enhancements are wanted as issues. The enhancement template says: "If this is an idea for a feature, please open an "Idea" Discussion instead." Grammar and theme changes arrive as direct PRs (#16049, #16068).

(a) Bugs. The form asks for Summary, Reproduction Steps in a fixed shape ("I tried this: 1. `hx` / I expected this to happen / Instead, this happened"), log, platform, terminal, install method and version. Reports that got traction give a key sequence, an asciinema recording or the breaking commit (#15525, #16322). Many turn out local or upstream: a key remapper (#15916), clangd (#15601), stale grammars (#15877). 39% of issues are closed by their author.

(b) Enhancements. The template is only a comment. Small ones get implemented (#15386, #15998). Large ones are closed as duplicates of old issues (#15241, #15395) or declined (#16092).

(c) Fix proposals. #15318 gave the root cause and "Would you like me to submit a Pull Request?"; #15320 was merged.

Titles: short (median 7 words), no prefix: "Can't open file picker".

## Issues and pull requests
32% of issues closed via a PR; only 12% of PR bodies carry a closing keyword, written "Closes #15998" (#16024). PR bodies have a median of 34 words and are often empty; titles are "area: description" ("languages: uxntal: don't auto-pairs quotes") or a plain sentence.

## How the conversation goes
Median first response is 7 hours. Maintainers archseer and the-mikedavis reply in a median of 16 words; much first-line help comes from other users, m4rch3n1ng in all lowercase (#15941). A duplicate is one bare line and a close, even over objection (#15241). A refusal is explained only when pushed, as maintenance burden (#16092). Reporters confirm and close themselves. All English.

## Maintainer voice
- "This must be an issue in the steel branch, I can't reproduce on master." (#15103)
- "It's not broken, I recently updated the grammar. You just need to rebuild via hx --grammar build" (#15877)
- "Should already be fixed on latest master" (#16322)
- "Duplicate of https://github.com/helix-editor/helix/issues/6747" (#15395)
- "Sometimes that sadly means saying no to feature requests." (#16092)

## If you are an outsider here
1. Test on current master and give the commit hash (#16322).
2. First rule out the terminal, key remappers, the language server (`:lsp-stop`, #15601) and stale grammars (`hx -g build`).
3. Keep the "I tried / I expected / Instead" form.
4. Put feature ideas in Discussions; an issue is for a small, concrete change.
5. Come back, confirm in one line and close the issue yourself.

## What this sample cannot tell
Closed issues only, so unanswered reports are invisible; the PR sample shows no review discussion.
