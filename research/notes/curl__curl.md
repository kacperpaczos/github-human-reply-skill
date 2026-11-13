# curl/curl

Percentages: share of 150 closed issues / 94 non-bot PRs.

## Opening an issue
Blank issues are disabled. Only bugs are wanted: feature requests go to the mailing lists, questions to Discussions or the lists, security problems of severity HIGH or above to HackerOne.

(a) Bugs: the form has four fields: "I did this", "I expected the following", "curl/libcurl version" (`curl -V`), "operating system" (`uname -a`). It warns: "Do not paste massive AI generated explanations." Reports that got real work show the command line, verbose output and full `curl -V` (#22923, #22609). Closed quickly as `not-a-curl-bug`: behaviour that follows the RFC or has always been so (#23636, #22999).

(b) Features (1%): an enhancement filed as a bug is closed as "a discussion topic" (#23070).

(c) Fix proposals: a diff pasted in the issue is tested back and forth (#22609); otherwise the maintainer asks for a PR (#23025).

Titles: lowercase area, colon, symptom: "ws: split incoming PING leaks payload..." (37% prefixed).

## Issues and pull requests
PRs are not merged through GitHub (1% show as merged): a maintainer lands the commit and the PR is closed. Issues close via PR (49%) or directly via commit (17%). The PR body is the commit message: a few plain sentences, then "Fixes #N" and "Reported-by: Name" (#23879, #23765). Titles are `area: lowercase summary` (93%). Outsiders wrote 20% of PRs.

## How the conversation goes
First reply after a median 3.1 h; only 10% of issues get no human comment. bagder, icing and jay answer, median 26 words. Tone is direct, sometimes sharp; RFC text is quoted as the argument (#23284, #23070). Maintainers ask reporters to test a PR (#22923). Authors close 25% of issues. English only.

## Maintainer voice
- "This is how curl has treated FTP URLs since the beginning. It is not a bug." (#22999)
- "@qwaz you up to providing a PR to fix this?" (#23025)
- "Could you try https://github.com/curl/curl/pull/22946 and report if this fixes the problem? Thanks!" (#22923)
- "unclear issue, bad title" (#23742)

## If you are an outsider here
1. File only bugs; take feature ideas to the mailing list.
2. Start with the exact command and paste the whole `curl -V`.
3. Keep it short and in your own words; the form warns against long generated analyses.
4. Check the RFC before claiming a protocol bug: maintainers will quote it.
5. Write the PR body as a commit message ending in "Fixes #N"; expect no "merged" badge.

## What this sample cannot tell
How the mailing lists treat feature requests, and how reviewers reacted to long, sectioned PR bodies such as #23775.
