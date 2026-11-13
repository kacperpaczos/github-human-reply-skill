# alacritty/alacritty

## Opening an issue

The digest captures no issue template, so it establishes no required fields.

(a) Bugs receive diagnostic replies when they include versions, reproduction and logs (#8905, #8964). Video without a clear textual symptom prompts clarification (#8920). Detailed reports can close without replies (#9064, #9090); missing follow-up brought closure within six days (#8964).

(b) Feature issues get considered: reproducible macOS automation failure led to an accepted patch (#8937). Requests conflicting with intentional behavior (#8837), platform ownership (#8850), or a previous rejection (#8929) close with explanations.

(c) Fix proposals can start as issues (#9055) or direct PRs (#9036). No sampled reply redirects these categories to discussions or a mailing list.

Titles describe symptoms and platforms (#8853, #8905); feature prefixes vary between “[Feature Request]” (#8837), “Feature request:” (#8929), and none (#9087). No uniform sampled convention emerges.

## Issues and pull requests

Both routes occur: #9055 became contributor PR #9056; contributor PR #9036 has no linked issue. Bodies include `Fixes #9055`, `Fixed #8937`, and maintainer PR #9013’s `Closes: #9012`. Other issues close manually (#8964).

Descriptions range from one-line references (PR #8999) to causal explanations, patch sequencing and benchmarks (#9036). Maintainers welcome small fixes (#8937, #9055). PR #8878 adds a no-LLM contribution policy; sampled PRs include a corresponding checkbox (#8966, #9036). Substantive review comments are omitted.

## How the conversation goes

Chrisduerr usually answers, with kchibisov also participating (#8964, #8968). Digest medians are 2.5 hours to first response and 27 words per maintainer comment; #8905 and #8920 show same-day exchanges.

English replies are often one or two direct sentences: diagnostic questions (#8920), blunt refusals with alternatives (#8850), and reminders to search existing issues (#9058). Duplicate handling references existing conclusions (#8849). Reporters provide logs and thanks after resolving configuration problems (#8920), but sometimes contest diagnoses (#8968). Closure can be silent (#9090).

## Maintainer voice

- “Are you using alt to switch workspaces?” (#8920)
- “If you believe it's a regression, you can also bisect.” (#8964)
- “Seems like this isn't going to see any update.” (#8964)
- “Happy to accept a patch.” (#8937)
- “Nothing has changed about the relevance of this feature.” (#8929)

## If you are an outsider here

1. Describe precise keystrokes and wrong output alongside videos (#8920).
2. Supply requested `--print-events` logs (#8920).
3. Test stable dependencies and bisect claimed regressions (#8964).
4. Check previous feature decisions before reopening them (#8849, #8929).
5. Account for the no-LLM patch policy and declaration before submitting code (PR #8878, #9089).

## What this sample cannot tell

Closed issues cannot establish how unanswered open requests fare. Missing review text and truncated bodies limit explanations of PR rejection and silent closures.
