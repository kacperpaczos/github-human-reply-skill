# swaywm/sway

## Opening an issue

(a) Bugs: `bug_report.md` requests version, full debug log, default/minimal configuration, reproduction steps, and symbolized crash backtrace. A reproducible crash with attachments received diagnostic help (#8939). #8707 lacked a log and received no maintainer reply; the sample cannot establish why.

(b) Features: `enhancement.md` asks for plain-English functionality and use case; new window-management features must already exist in i3. `i3_compat.md` requests behavioral differences and an i3 PR for new functionality, excluding listed unsupported features. Concrete protocol support received engagement (#8812); colord integration was rejected (#8760), and existing cursor functionality prompted closure (#8840).

(c) Fix proposals: no separate patch template appears. Issues can propose changes (#8696); contributors also submit unlinked PRs (#9244). No issue-first requirement is demonstrated.

Titles usually state the symptom without a mandatory prefix (#8939, #9177). Questions belong on IRC; #9107 was redirected and closed.

## Issues and pull requests

PR bodies use `Fixes` (#9166), `Closes` (#9083), or `Resolves` (#9025). The digest also records closure through commits (#8999, #8845) and by hand after reporter confirmation (#9005).

Contributors follow both issue-first (#8909 → PR #8910) and direct-PR routes (#9244). Descriptions explain cause and change (#9188), sometimes adding testing (#9025). Component-prefixed PR titles recur (#9175). Review counts appear, but substantive reviewer requests are absent.

## How the conversation goes

Emersion supplies most sampled maintainer replies. Digest medians are 12.4 hours to first response and 18 words per maintainer comment; #8926 shows same-day troubleshooting.

English replies are concise and technical. Requests specify debug symbols or ASan commands (#8939); refusals explain scope (#8760); duplicates receive a link (#9177). Reporters return traces (#8939), acknowledge fixes, and close their own reports (#9005, #9177). Longer design discussion occurs in #8885.

## Maintainer voice

- “Indeed, Sway already supports this.” (#8840)
- “ASan print stack traces to stdout/stderr.” (#8939)
- “Please ask questions on IRC, not on the issue tracker.” (#9107)
- “Sorry, but colord support is not planned/desirable.” (#8760)
- “Thanks for testing!” (#8885)

## If you are an outsider here

1. Supply symbolized traces; return ASan output when requested (#8939).
2. Retest newer Sway/wlroots before extending an old-version report (#9005, #8926).
3. Verify shell quoting before alleging an i3 incompatibility (#8696).
4. Ground protocol requests in specifications and executable reproducers (#8845).
5. Confirm linked upstream fixes and close duplicates yourself (#9177).

## What this sample cannot tell

Closed issues cannot establish how unresolved reports fare. Truncated bodies and missing PR review text limit conclusions about review requirements.
