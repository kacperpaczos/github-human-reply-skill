# godotengine/godot

## Opening an issue
One template (bug_report.yml); blank issues disabled; contact links to godot-proposals, godot-docs, community chat.

(a) Bugs — the only kind wanted. Five required fields: Tested versions (version + commit hash, plus versions tested), System information (OS/CPU/GPU/renderer; missing data may be closed at maintainers' discretion), Issue description, Steps to reproduce, Minimal reproduction project (MRP zip, no .godot). Titles are descriptive sentences, no type prefix, often area/version prefixed (#124658, #125260). Answered reports carried version+hash and an MRP; AI-written ones were closed unprocessed (#125073, #124842), as were duplicates (#124780).

(b) Feature requests — refused: "That's a missing feature and belongs in a proposal, please open one over there" (AThousandShips, #125165). Features go to godot-proposals; doc bugs to godot-docs; support to community channels.

(c) Fix proposals — a PR, after a bug issue; the PR template wants "What problem(s) does this PR solve?" and "Closes #N".

## Issues and pull requests
54/150 issues closed by a merged PR, 0 by a maintainer commit. PRs link with closing keywords in the body (33/100; #125319 closed #123359, #124780). 58/100 PRs came from non-members; small fixes ship without an issue (#125267). Maintainers want one topic per PR (AThousandShips, #125404) and reject undisclosed AI PRs (bruvzg, #125382).

## How the conversation goes
Median first reply 4.4 h, one comment per issue; 27/150 issues drew no human reply. AThousandShips and the bug squad triage; Calinou, KoBeWi, YeldhamDev and syntaxerror247 answer in their areas. Replies are short (median 27 words) and imperative. Missing MRP or written steps gets asked for again; duplicates get a link (#124621). Threads end "CLOSED by ... via hand". Reporters reply briefly (#125315). English only.

## Maintainer voice
#124582, Calinou: "This is not a bug. Game embedding intentionally preserves the aspect ratio by default."
#124582, AThousandShips: "Please add clear steps for reproducing this, a video is not very easy to use as a reference"
#124712, AThousandShips: "Please upload a complete MRP rather than individual files:"
#125165, AThousandShips: "That's a missing feature and belongs in a proposal, please open one over there"
#124842, AThousandShips: "Closing as this is too verbose and AI authored, if you clean it up it can be reopened"

## If you are an outsider here
One bug per issue; all five fields filled; MRP zip attached.
Exact version + commit hash, plus versions tested.
Repro steps as text, not a video link.
Feature ideas to godot-proposals; doc bugs to godot-docs.
Disclose AI authorship (🤖 in title) or the report is closed unprocessed (#125073).

## What this sample cannot tell
No proposals-repo data, so how a feature request is accepted is invisible; the 150 issues are all closed, over-representing fixed or rejected reports, not the live backlog.
