# mpv-player/mpv

## Opening an issue

(a) Bugs: platform forms request version/build source, system details, reproduction, expected/actual behavior, logs and crash backtraces; build reports request Meson details/logs. A minimal file and `--no-config` command enabled diagnosis (#18332); a standalone reproducer led to a fix (#18405). Empty template answers attracted sarcasm and same-day closure (#18509). Titles describe symptoms, sometimes with platform/component prefixes (#18332, #18527).

(b) Features: the form requires expected behavior, asks about alternatives and supporting material, and directs uncertain requests to Discussions/IRC after checking existing support. Missing-information requests received engagement, but MediaInfo integration was refused (#18146). Already-supported functionality ended requests quickly (#18168, #18466). Titles name the capability (#18308).

(c) Fix proposals: no separate patch-issue form appears. A source-level question with revisions, API evidence and explicit testing limits received a fix (#18527). Direct PRs occur without linked issues (#18797); no issue-first requirement is established.

## Issues and pull requests

Bodies use `Fixes #18749` (PR #18752) or `Closes #17241` (PR #18681). Other issues close through a commit (#18527) or manually after an existing fix is identified (#18217). Outsiders submit linked and unlinked PRs (#18681, #18705).

Descriptions range from one sentence (#18681) to reproduction, alternatives and upstream links (#18705); component-prefixed titles recur (#18797). Review counts appear, but reviewer requests are absent from these extracts.

## How the conversation goes

Kasper93, sfan5, Dudemanguy and philipl answer alongside others (#18217, #18240, #18332). Digest medians are 1.4 hours to first response and 29 words per maintainer comment; same-day exchanges occur (#18332), while #18405 waited longer.

Replies give direct technical instructions, sometimes bluntly or sarcastically (#18116, #18509). Maintainers request exact builds/dumps and link related issues (#18332), explain scope limits (#18240), and invite retesting when closing (#18217). Reporters return test results or correct build assumptions (#18332, #18298). English predominates; #18157 includes Chinese and Swiss German.

## Maintainer voice

- “Can't reproduce.” (#18217)
- “What information are you looking for?” (#18146)
- “Works for me. Consult your build configuration for enabling VP6 in ffmpeg.” (#18466)
- “Yes, it would be, as per issue template. Because I cannot reproduce your issue.” (#18678)

## If you are an outsider here

1. Attach the complete reproduction log immediately (#18678).
2. Compare official development builds with third-party builds (#18332).
3. Identify specific missing information when requesting features (#18146).
4. State what source/API tests demonstrate and their limits (#18527).
5. Return concrete retest results and correct mistaken build provenance (#18298).

## What this sample cannot tell

Closed issues cannot establish the fate of unanswered open reports. Truncated templates and missing review text limit conclusions about requirements and review practice.
