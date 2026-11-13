# PrismLauncher/PrismLauncher

## Opening an issue
(a) Bugs (63%): the form sends support questions to Discord first and asks you to read the wiki, rule out Minecraft and mods, and search. Fields: operating system, Prism Launcher version, Qt version, description, steps to reproduce, suspected cause or other information, an "issue is unique" checkbox. Reports that got fixed had numbered steps plus a log file, video or stack trace (#6392, #6047, #5969). Network trouble, upstream outages and reports without logs are closed (#6029, #6177, #6207). Titles are descriptive sentences.
(b) Suggestions (28%) are welcome as issues: one-line "Suggestion" and "Benefit" fields, a uniqueness checkbox that mentions rejected ideas, free text. Many are closed as already existing or duplicate (#6311, #5983); 25% of all issues close as duplicate.
(c) Larger proposals use the RFC form (Goal, Motivation, Specification, Drawbacks). Re-proposing a rejected idea is closed as duplicate however detailed (#5999, #6439), and AI-written text is labelled or refused.

## Issues and pull requests
22% of issues close via PR, none via bare commit, the rest by hand. Only 30% of PRs come from outsiders; 76% merge. Bodies link with "Fixes #N" or "Closes #N" (#6416, #6394, #6331, #6223). Titles are mixed: 41% conventional ("fix(ui): ...", "feat: ..."), others plain. The PR template demands signed-off commits and points to the AI policy. Bodies are short and informal, often with before/after screenshots (#6302, #6283). Most PRs get several reviews.

## How the conversation goes
First reply in a median 1.3 hours, median 18 words. Trial97 answers most, lowercase and unpunctuated; TheKodeToad and Octol1ttle explain decisions more fully (#5983, #6360). 32% of issues get no human comment. Requests for information are specific (a gdb backtrace with a wiki link, #6304). Refusals are short; abuse gets one formal reply and a close (#6339). English is required.

## Maintainer voice
- "No logs, no bug." (#6207)
- "check filter options you can already do that" (#6311)
- "also no AI" (#6439)
- "This is intentional behavior. Resource packs are backwards compatible in relation to the Minecraft version" (#6353)
- "Closed this because it still suggests the same thing as the other issue" (#5999)

## If you are an outsider here
1. Attach the launcher log to every bug report.
2. Search closed and rejected suggestions first; Discord Rich Presence is settled (#232).
3. Do not submit AI-generated issue text or code; read the AI policy in CONTRIBUTING.
4. Write in English, briefly and casually.
5. Sign off commits and put "Fixes #N" in the PR body.

## What this sample cannot tell
Most support happens on Discord, so the tracker shows only what was escalated.
