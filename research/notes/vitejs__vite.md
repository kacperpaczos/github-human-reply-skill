# vitejs/vite

## Opening an issue
Blank issues are disabled. Bugs and feature proposals are wanted; questions go to Discussions or Discord.

(a) Bugs. The form requires a description and a reproduction link, plus steps, System Info, logs and a checklist. Without a reproduction the issue is labelled "needs reproduction" and auto-closed after 3 days: #22971 ("I'll make one later") and #22937 were closed by github-actions. Fixed reports have a runnable repository (#22942, #23975). Free-form issues are closed silently (#23475) or declined (#23102).

(b) Features. Description and Suggested solution are required. Answers are often an existing API (#23215) or PR (#24005).

(c) Fix proposals. Every form says: "If you intend to submit a PR for this issue, tell us in the description." #23975 did so and #23976 was merged.

Titles: a full sentence, often with the version ("Upgrade to v8 breaks ?inline").

## Issues and pull requests
62% of issues closed via a PR; 63% of PR bodies carry a closing keyword, often repeated in the title: "fix(build): ... (fix #23975)". All PR titles are conventional commits. The PR template says, for AI use: "Keep the PR description and discussion concise. Use your own words". 24% of outsider PRs are merged. Quick PRs on untriaged issues go unmerged (#23348, #23523, #23383 had two each).

## How the conversation goes
40% of issues close with no human comment. Median first response is 14.6 hours, from sapphi-red or bluwy, in a median of 19 words: no greeting, a fact and a link. A no is one reason in one sentence (#23102, #23266). Duplicates and upstream bugs get "Let's track this in <link>" and are closed (#23523, #23287). Wrong claims are corrected flatly: "This isn't true." (#23348). Reporters confirm and thank. All English.

## Maintainer voice
- "This was fixed in v8.2.0." (#22943)
- "We no longer support Vite 5. I'd suggest upgrading and see if this is fixed" (#23312)
- "Let's track this at https://github.com/oxc-project/oxc/issues/24743" (#22982)
- "less v5 is still alpha and is not ready for Vite. Let's wait for them." (#23266)
- "Please don't use agents to get it done quickly." (#23383)

## If you are an outsider here
1. Attach a reproduction that runs; never promise one for later.
2. Test on the current major and say which version works and which breaks (#22942, #22982).
3. Verify every claim (#23348).
4. Do not post "can I work on this" (#23215, #22982) or rush a PR; state the intent in the issue, then open a PR with "fix #N".
5. Check whether the fault is upstream (Rolldown, oxc).

## What this sample cannot tell
Closed issues only, so the unanswered backlog and how long "pending triage" lasts are unknown.
