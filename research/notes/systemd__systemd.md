# systemd/systemd

Percentages: share of 150 closed issues / 100 PRs.

## Opening an issue
Blank issues are allowed; questions go to the systemd-devel mailing list.

(a) Bugs (79%, label "bug 🐛"): the form asks systemd version (required; only the two newest major releases, older goes to the distribution), distribution, kernel, architecture, component, expected and unexpected behaviour, steps, log output. Answered reports carry journal excerpts and a deterministic repro (#43700) or links to exact source lines (#43104). Closed fast: unsupported kernel, label `version-too-ancient` (#43575); matters of another project, label `misfiled` (#43889).

(b) Features (12%, label "RFE 🎁"): component, problem, solution, alternatives. Maintainers question the use case or propose another design (#43676, #43807).

(c) Fix proposals: a ready hwdb or udev line in an issue gets the label `please-submit-as-pr` and one sentence (#43547, #43256); both times someone else sent the PR. Patches are wanted as PRs.

Titles: plain sentence, often led by the component: "systemd-resolved: DNSSEC=yes still downgrades server to no DNSSEC" (26% prefixed).

## Issues and pull requests
61% of issues were closed by a PR with "Fixes #N" as the last line of its body (#44726). Yet only 7% of PRs have a closing keyword: most PRs, outsiders' included (33% of PRs), have no issue. PR titles are `component: lowercase summary` (80%); bodies are a few sentences like a commit message (median 36 words).

## How the conversation goes
First reply after a median 9.4 h; 31% of issues get no human comment, only the fix (#44289). Maintainer comments: median 27 words. poettering writes lowercase, opens with "hmm," and asks why; bluca refuses bluntly; yuwata is terse and polite. Routing is "/cc @name" plus labels. Duplicates are named by number, often by the reporter (#43556, #43168); authors close 17% of issues, also after a design is refused (#43807). English only.

## Maintainer voice
- "hmm, yeah, this looks like a bug" (#43700)
- "what does it get you to avoid that?" (#43807)
- "Please submit the suggested change as a PR. Thank you." (#43547)
- "Just use an ESP?" (#43889)

## If you are an outsider here
1. Give the exact systemd version; old releases and kernels below the README minimum are closed.
2. Paste journal output and a command sequence.
3. If you know the one-line fix (hwdb, rules, man page), open a PR, not an issue.
4. For an RFE, expect "why not X instead?" and answer with your constraints (#43807).
5. If your issue is a duplicate or settled elsewhere, close it yourself with the number.

## What this sample cannot tell
How review inside PRs goes (only bodies are sampled) and how long-open RFEs are treated.
