# podman-container-tools/podman

Percentages: share of 149 closed issues / 71 non-bot PRs.

## Opening an issue
Blank issues are allowed; questions go to Discussions.

(a) Bugs (69%, labels `kind/bug`, `triage-needed`): the form asks Issue Description, Steps to reproduce, results received, results expected, `podman info` output, in a container?, rootless?, latest release? Answered reports show commands with output for the failing and the control case (#29600, #30094) or measurements (#29981). A free-form bug (#29979) and a placeholder instead of `podman info` (#30062) were rebuked.

(b) Features (13%, `kind/feature`): description, potential solution, alternatives. Maintainers debate naming and compatibility in the thread (#29946) or refuse because config already covers it (#29962).

(c) Fix proposals: issue first, then a claim by commenting `/assign` (#29600, #29562, #30208). Maintainers file small `Contribfest` / `Good First Issue` tasks for outsiders (#30208). All three kinds are wanted as issues.

Titles: plain sentence, sometimes prefixed: "events: ...", "[RFE]", "[kube]" (24% prefixed).

## Issues and pull requests
72% of PRs carry "Fixes: #N" or "Fixes: <issue URL>", required in the commit message too. Outsiders wrote 68% of PRs. Every PR keeps the template: a checklist (at most two open PRs for new contributors; "PR description, commit message, and GitHub comments are human-written, per LLM Policy"; DCO `Signed-off-by`) and a `release-note` block, `None` if nothing user-facing. Claimed issues still drew competing PRs: three each for #29600 and #29579.

## How the conversation goes
First reply after a median 5.7 h, mostly Luap99; 18% get no human comment. Maintainer comments: median 38 words, informal, typos left in. Routing is "cc @name". Refusals explain the mechanism and link docs or a blog post (#29970). Duplicates (8%) are closed by hand with a link. Reporters answer briefly (#29979) or with the data asked for (#29891). English only.

## Maintainer voice
- "Please follow our proper bug template when reporting issues in the future." (#29979)
- "That provides zero information to us." (#30062)
- "AS such I do not see anything for us to add here" (#29962)
- "This is already merged: https://github.com/podman-container-tools/podman/pull/29677" (#29829)

## If you are an outsider here
1. Use the bug form, paste real `podman info`, say whether the latest release fails.
2. Before fixing, check nobody claimed the issue, then comment `/assign`.
3. Skip the long plan: one was posted in #29478 and the reporter closed the issue anyway.
4. Keep the PR checklist and `release-note` block, sign off commits, put `Fixes: #N` in the commit message.
5. Write PR text and comments yourself; the checklist makes you certify it.

## What this sample cannot tell
Whether the LLM policy is applied to issue text (the openly AI-prepared #29891 was handled normally).
