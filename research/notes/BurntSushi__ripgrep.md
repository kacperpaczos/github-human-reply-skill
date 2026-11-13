# BurntSushi/ripgrep

## Opening an issue
Bugs and feature requests are taken as issues; questions go to Discussions; file-type additions go straight to a PR.

(a) Bugs. The form lists common non-bugs, makes you tick "I have a different issue", then asks for `rg --version` output, install method, OS, steps, actual and expected behaviour. Reports that got a fix build the test files with shell commands and paste the output (#3180, #3184, #3131). Without a reproduction the answer is a request for an MRE (#3223).

(b) Features. The template asks for behaviour, motivation and examples. 45% of the sample closed as not planned: new flags (#3034, #3097, #3215) and exposing crate internals (#3093, #3014) are declined. Small library additions (#3158) and opt-in modes (#3127) are accepted.

(c) Fix proposals are offered inside the issue ("Happy to put up the PR if this seems reasonable", #3014).

Titles: a plain statement, sometimes with a crate prefix ("ignore: publicize ignore::dir").

## Issues and pull requests
18% of issues closed via a PR and 6% via a commit: the owner often lands outsider work in his own "rollup" PRs, so #3290, #2943 and #3127 closed "via a commit" while the outsider PRs show as unmerged. 31% of outsider PRs are merged. Titles are "area: lowercase description" ("printer: fix panic in replacements in look-around corner case"). Bodies are short prose (median 72 words) with "Fixes #N".

## How the conversation goes
BurntSushi answers alone: median first response 1.9 hours, 35 words. A real behaviour question gets a long answer with source links and GNU grep comparisons (#3131, #3184); a feature request gets two sentences and a wontfix label. Refusals are plain, sometimes with "sorry", often with an alternative: a fork, your own crate, `.rgignore` (#3215, #3093, #3121). Reporters reply briefly, often conceding (#2952). All English.

## Maintainer voice
- "Please provide an MRE. Without instructions to reproduce, this won't be actionable." (#3223)
- "A patch with tests is welcome." (#3158)
- "No. `ignore` is tightly coupled with file system APIs and I don't want to change that. Sorry." (#3093)
- "Sure, go for it. Remember that this should be an _opt-in_ behavior though." (#3127)

## If you are an outsider here
1. Reproduce in an empty directory with commands that create the files; paste `rg --version` and the real output.
2. Read the FAQ, GUIDE and docs.rs first (#2952, #3121).
3. Do not request a flag for a niche case; expect a no.
4. Compare with GNU grep, as he does (#3131).
5. Offer the patch in the issue, wait for "go for it", send tests.

## What this sample cannot tell
One person is the whole maintainer voice and only closed issues were sampled.
