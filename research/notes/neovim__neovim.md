# neovim/neovim

Percentages: share of 150 closed issues / 99 PRs.

## Opening an issue
Blank issues are disabled; questions go to Discussions.

(a) Bugs (80%): the form asks Problem, Steps to reproduce (on nightly, with `nvim --clean` or a `minimal.lua`), Expected behavior, version, "Vim behaves the same?", OS, terminal. Reports with a real answer have a pasteable repro (#41995, #42239) and a Vim comparison (#42309). Closed at once: an unfilled template (#42304), a usage question (#41989), bugs in deprecated code (#42208) or in third-party parsers (#42513).

(b) Features (15%): Problem and Expected behavior only. Accepted when small and backed by a use case (#41960); otherwise closed not-planned with the existing way to do it (#41983, #42603).

(c) Fix proposals go inside the bug report as "Possible cause" / "Suggested fix" (#42309, #42521); the answer is "PR welcome." (#41709).

Titles: lowercase area, colon, symptom, commands in backticks: "multicursor: `gQ` does not restore all cursor positions" (49% prefixed).

## Issues and pull requests
69% of issues were closed by a PR whose body says "Fix #N" or "Fixes #N" (#42790, #42632). PR titles are `fix(scope): summary` (74%); bodies are a short "Problem: / Solution:" pair (#42660). Some outsider PRs end with "AI-assisted" (#42648, #42693). Quick outsider PRs on a fresh bug were often left unmerged while a maintainer landed his own (#42026 vs #42027, #41809 vs #41958, #42240 vs #42244, #42523 vs #42615); #42001 was merged.

## How the conversation goes
First reply after a median 4.7 h, mostly justinmk; 27% of issues get no human comment, only the fix. Maintainer comments: median 29 words, never a greeting, usually one quoted sentence and a line or two under it. Refusals are flat, with a reason. Reporters quote back, then argue with a concrete case (#41960) or concede (#42603). English only.

## Maintainer voice
- "PR welcome." (#41709)
- "Yes, this is a bug." (#41939)
- "we aren't going to add new `--foo` args for random features." (#41983)
- "If there's a minimal way to fix, that's acceptable, but otherwise I don't care. `vim.opt` is on the way out." (#41953)
- "This isn't a support forum." (#42304)

## If you are an outsider here
1. Start the repro with `nvim --clean` and say whether Vim behaves the same.
2. Title it `area: symptom`.
3. Verify your root-cause claim first: wrong ones are caught in a line ("Really?", #42387).
4. Reply by quoting the sentence you answer, then one or two lines.
5. For a feature, say why existing commands or a few lines of Lua do not suffice.

## What this sample cannot tell
Why the unmerged outsider PRs were passed over; review comments are not in the digest.
