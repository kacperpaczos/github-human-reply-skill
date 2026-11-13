# linuxmint/cinnamon

## Opening an issue
(a) Bugs are what the tracker wants (78% of the sample). The form opens with "STOP!": search first, send Wayland bugs to linuxmint/wayland, disable third-party xlets, check `~/.xsession-errors`. Fields: distribution, package version, graphics hardware, frequency, description, steps, expected behavior. Reports that got real work were short, on a current version, with a traceback or exact steps (#13690, #13717, #13823). Old versions are closed at once (#13796, #13689). Titles are plain sentences.
(b) Feature requests are not accepted; the template is marked OBSOLETE and points to org discussions. Filing one anyway gets a redirect or a rebuke (#13920, #14122, #13888).
(c) A compact fix proposal inside a bug report can work (#14024, fixed by a maintainer commit); long LLM-written analyses meet hostility (#13925, #13629). A direct PR is the normal route.

## Issues and pull requests
12% of issues close via PR, 10% via maintainer commit, the rest by hand. 93% of PRs come from outsiders, about half merge, and only 19% carry a closing keyword: a bare "Fixes #N" or "closes <url>" (#14045, #13830, #13896). Titles use a `component: change` prefix (66%). Good bodies are one or two paragraphs of cause and fix, sometimes with the tested version (#13896).

## How the conversation goes
First reply in a median 2.7 hours, mostly from leigh123linux or mtwebster, median 13 words, no greeting or sign-off. They ask for one thing at a time, often a command in a code block (#13690, #13696), and repeat it bluntly if skipped (#13696). Duplicates get one line with a link (#13989). Refusals are flat statements of design or support scope (#13833, #13796). Packaging problems are pushed to the distro (#13812, #13710). English only (#14122). 20% of issues get no human comment.

## Maintainer voice
- "Duplicate of https://github.com/linuxmint/cinnamon-settings-daemon/issues/435" (#13989)
- "cinnamon-6.0.4 isn't a support version, reopen if you can reproduce with cinnamon-6.6.x" (#13796)
- "Not animating to open is a deliberate performance decision for this applet." (#13833)
- "For all screenshot types or just windowed?" (#14024)
- "You will need to address this in your distro packaging" (#13710)
- "You still haven't provided any information about hardware." (#13696)

## If you are an outsider here
1. Reproduce on the current 6.6.x or master before filing.
2. Never file a feature request; use linuxmint discussions.
3. Fill the hardware field and paste terminal output; they will ask otherwise.
4. Keep it short and unformatted: no tables, no root-cause essays (#13629, #13925).
5. Answer the exact question asked, with the command output, in one comment.

## What this sample cannot tell
It does not cover the linuxmint discussions where features go, nor how long open issues wait.
