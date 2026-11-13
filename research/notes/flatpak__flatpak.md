# flatpak/flatpak

## Opening an issue
(a) Bugs (65%): the form presets the title "[Bug]: " and label "needs triage", requires four checkboxes (code of conduct, searched, tried the app's own tracker, not a security report), then Flatpak version, distribution (dropdown), distribution version, architecture, how to reproduce, expected, actual, additional information. Reports that got engagement had exact commands with output (#6539, #6508), a VM reproduction (#6449) or `-vv` and strace logs (#6618). Reports about one app, Steam or drivers are closed as not Flatpak's (#6465, #6792, #6641, #6430).
(b) Feature requests (18%) are accepted as issues: "[Feature request]: " title, two checkboxes, one "Suggestion" field. Most are declined or duplicates (#6497, #6624, #6471, #6530); 42% of all issues close as not planned, 14% as duplicate.
(c) Fix proposals: a maintainer names the fix and the reporter sends the PR (#6508 -> #6519), or a test case is requested first (#6449).

## Issues and pull requests
25% of issues close via PR, none via bare commit. PRs link with trailer-style keywords: "Closes: #N", "Fixes: <full URL>", "Updates: #N", "Resolves:" (#6908, #6888, #6878, #6834). 60% of PRs come from outsiders; 86% merge. Titles follow `area: Imperative summary` (86%): "dir:", "cli:". Bodies are short (median 38 words) and read like commit messages: what was wrong, what changes, which test was added (#6971).

## How the conversation goes
First reply in a median 7.4 hours; replies are the longest of the four projects (median 37 words). bbhtt triages tersely; smcv writes multi-paragraph explanations (#6471, #6641, #6697); swick is blunt and opinionated (#6668, #6497, #6624). Duplicates get a one-line link (#6530). English only.

## Maintainer voice
- "I don't see anything in the logs that points to an issue in Flatpak itself." (#6465)
- "How does the system clock predate the key creation time?" (#6449)
- "A GUI app is out-of-scope for this particular project." (#6826)
- "This is not a Flatpak bug." (#6641)
- "The issue is completely devoid of useful information." (#6668)
- "Not going to happen. I was involved in the protocol and it was a mistake." (#6624)

## If you are an outsider here
1. Rule out the app, runtime, driver and distro package before filing.
2. Include `flatpak info --show-permissions` output and overrides for sandbox behaviour (#6668).
3. Put exact commands and output in "How to reproduce"; never leave it empty (#6792).
4. For a feature, give the use case and expect "no" to low-level control (#6497).
5. In a PR, use `area: summary`, a "Closes: #N" or "Fixes: URL" trailer, and a test.

## What this sample cannot tell
It does not show how security reports or larger design discussions are handled; both happen outside the issue tracker.
