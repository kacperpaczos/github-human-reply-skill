# linuxmint/nemo

## Opening an issue
(a) Bugs are 83% of the sample and the only kind wanted. The form says "STOP!", search first, run `nemo --quit && nemo` from a terminal, attach crash info. Fields: distribution, package version, frequency, description, steps, expected behavior, additional information. Reports that got a fix had exact reproduction commands (#3730, #3442), a backtrace (#3712) or tool output compared against Caja (#3870). Titles are plain descriptions without prefixes ("Seg fault on file rename").
(b) Feature requests: the template is OBSOLETE and its body is only the discussions link; people submit it unchanged and are closed (#3879, #3778, #3835).
(c) Fix proposals arrive as PRs, not issues.

## Issues and pull requests
16% of issues close by maintainer commit, 10% via PR, the rest by hand or by the stale bot (#3436, #3418, #3456). 82% of PRs are from outsiders but only 38% merge. 20% use a closing keyword, always a bare "Fixes #N" (#3731, #3724, #3828). Titles follow `file-or-area.c: Sentence.` (#3731, #3858, #3853). Bodies give cause then fix in a short paragraph; stronger ones add "How to reproduce" with Before/After (#3853) or the build tested (#3828). Disclosed AI use did not block a merge (#3593).

## How the conversation goes
First reply in a median 1.6 hours, median 21 words, from mtwebster or leigh123linux. They answer with a question or a screenshot of the setting that explains the behaviour (#3535, #3676, #3656). Old-version reports are closed in one line (#3535). Design decisions are explained once, firmly, with a warning about tone (#3676). "Same issue" comments get no reply (#3697). Regular users such as Jeremy7701 often answer first (#3815, #3778, #3418). English throughout.

## Maintainer voice
- "Works in current release" (#3535)
- "Hi can you attach additional crash info please?" (#3712)
- "Thanks, it was just to confirm the latest is still broken." (#3870)
- "That isn't going to happen." (#3580)
- "Np, you're not the first and won't be the last." (#3676)
- "Are you sure you're even using nemo? Tracker support is a compile-time option, and not supported by default." (#3815)

## If you are an outsider here
1. Test on the latest nemo; state distribution and exact `nemo --version`.
2. Check Preferences and Mouse/Keyboard settings before calling a behaviour change a bug (#3676, #3535).
3. Do not submit the feature template; go to linuxmint discussions.
4. Give copy-pasteable shell steps and the observed output, as in #3730.
5. When asked to run a command or test a package, report the result plainly.

## What this sample cannot tell
It does not show why 62% of PRs go unmerged; the rejected PRs in the digest carry little visible discussion.
