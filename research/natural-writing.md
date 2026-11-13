# How people write on GitHub, and candidate rules

Status: findings and candidate rules, written for independent review. This is not the skill. Nothing here has been tested as an instruction to a model.

## 0. Decisions already made by the operator

- The tool drafts text even when a project forbids AI-written comments. The operator carries that responsibility. (Open: whether a draft should carry a one-line note when the project's rules require disclosure. Not decided.)
- Posting happens only after the operator approves the exact text.

## 1. What was measured, and how far to trust it

- **Corpus:** the 150 most recently created closed issues per repository (up to 40 comments each) from 17 projects: ruff, vite, ripgrep, alacritty, helix, neovim, mpv, curl, systemd, podman, flatpak, sway, PrismLauncher, godot, cinnamon, nemo, siyuan. Text measures exclude siyuan (Chinese; word counts are meaningless), so 16 projects and 6,064 human comments. Bots are excluded.
- **Roles:** "maintainer" means an owner/member/collaborator badge, or someone who closes or labels other people's issues. "Reporter" is the issue author. "Other" is everyone else.
- **Limits:** only closed issues, newest first, so long and unanswered threads are missing. PR review threads and PR conversations were not collected. Everything is English except siyuan. The "move" labels (section 2.4) come from regular expressions; on 66 hand-checked first replies about 75% were right, and the patterns were tightened afterwards without a second full check. Section 4 is correlation, not effect.
- **Role mix:** maintainers wrote 40% of the 6,064 comments, other participants 26%, reporters 34%. The operator is often an outsider (filing, answering another user, or answering a maintainer's request as the reporter). Section 2.1 and the move table in 2.4 therefore show all three roles, and rules 4, 5 and 19 depend on role.

## 2. How a reply naturally looks

### 2.1 Size and shape

Share of comments, %, unless noted.

| | maintainer | maintainer, first reply to the reporter | other participant | reporter |
|---|---|---|---|---|
| comments | 2423 | 1149 | 1562 | 2079 |
| words, median (p25 to p75) | 27 (12 to 54) | 23 (11 to 44) | 37 (16 to 77) | 37 (16 to 82) |
| sentences / paragraphs, median | 2 / 1 | 2 / 1 | 2 / 1 | 2 / 2 |
| one paragraph | 57 | 61 | 53 | 48 |
| 15 words or fewer | 32 | 37 | 24 | 24 |
| over 100 words | 10 | 7 | 18 | 20 |
| greeting | 0 | 1 | 3 | 2 |
| "thanks" as the opening | 5 | 8 | 2 | 8 |
| header / bold label / list | 0 / 1 / 3 | 0 / 1 / 2 | 1 / 6 / 5 | 1 / 5 / 5 |
| emoji | 1 | 1 | 2 | 3 |
| closing offer ("let me know", "hope this helps") | 1 | 1 | 1 | 1 |
| em dash | 0 | 0 | 3 | 4 |
| inline code / code block | 26 / 7 | 24 / 6 | 32 / 15 | 27 / 13 |
| contains a link | 29 | 32 | 27 | 25 |
| quotes the earlier comment with `>` | 17 | 10 | 14 | 19 |
| contains a question mark | 23 | 22 | 25 | 26 |
| contains a hedge word | 28 | 26 | 28 | 28 |
| uses "I" / "we" | 38 / 21 | 32 / 18 | 49 / 8 | 59 / 8 |

A typical maintainer comment is two sentences in one paragraph. The first sentence is about 10 words and carries the point. Outsiders and reporters write somewhat more, with more code blocks and more "I".

### 2.2 The length that counts is the project's

Median maintainer comment length by project: cinnamon 13, helix 16, PrismLauncher 17, sway 18, vite 20.5, nemo 21, curl 25, alacritty 27, godot 27, systemd 27, mpv 29, neovim 29, ripgrep 35, flatpak 37, podman 37, ruff 39.5.

Surface habits also differ sharply by project:

| habit | where it is common |
|---|---|
| "thanks" as the opening | ruff 36%, godot 21%, curl 8%, every other project 4% or less |
| lowercase first letter | PrismLauncher 37%, systemd 25%, podman 22%, mpv 11%, neovim 11%, vite 10%; 1 to 6% elsewhere |
| no final period | PrismLauncher 75%, helix 54%, godot 50%, podman 42%, nemo 41%; 3 to 12% in alacritty, ripgrep |
| comments of 15 words or fewer | cinnamon 58%, PrismLauncher 49%, helix 48%, sway 44%; ruff 17% |

### 2.3 What is almost never there

Greeting, header, bold label, bullet list, emoji, closing offer, em dash: each at most 3% of maintainer comments. A comment that restates the thread or summarises itself does not appear in the samples read.

### 2.4 What a comment does (move) and how long it takes

Only 5% of maintainer comments match patterns for two or more moves, 40% for exactly one, and 55% for none (they explain or opine in plain prose). Comments make one move.

| primary move | share of maintainer comments | median words | has a link or #ref | has a code block |
|---|---|---|---|---|
| explain (cause, instruction, opinion, own test result) | 58% | 27 | 28% | 6% |
| ask for information or confirmation | 20% | 29.5 | 30% | 10% |
| decline ("not planned", "intended", "won't") | 7% | 37 | 34% | 8% |
| announce a fix or "already exists" | 7% | 10.5 | 64% | 2% |
| redirect to another place or project | 5% | 39 | 53% | 4% |
| duplicate | 3% | 12 | 95% | 1% |
| invite a patch | 1% | 24 | 24% | 4% |

First maintainer reply, by kind of issue (guessed from labels, type, title and headings): bugs get "explain" 53%, "ask" 21%, decline 8%, fix announcement 7%. Feature requests: explain 59%, ask 14%, decline 8%, invite 3%. Questions: explain 57%, ask 17%, decline 14%. Declining is the exception, not the norm.

The same patterns on the other roles (share of that role's comments, median words):

| primary move | maintainer | other participant | reporter |
|---|---|---|---|
| explain | 58% (27) | 67% (33) | 72% (30) |
| ask | 20% (29.5) | 21% (41) | 19% (54.5) |
| decline | 7% (37) | 3% (64) | 4% (77) |
| announce a fix | 7% (10.5) | 4% (49) | 3% (31) |
| redirect | 5% (39) | 3% (65) | 2% (59) |
| duplicate | 3% (12) | 2% (13) | 1% (34) |

Outsiders and reporters mostly explain and ask; they rarely decline, redirect, announce fixes or call duplicates, and when they do the comment is longer. A reporter who answers a maintainer's request (282 cases) writes a median of 50 words (p75 120; 29% over 100).

Inside "explain", a rough keyword count (lower bounds): states a cause 9%, gives an opinion or proposal 12%, gives an instruction 7%, reports its own test 4%.

Real examples, one project each (first replies unless noted):

| move | text |
|---|---|
| duplicate | "Likely a (subtle) duplicate of #3140." (ripgrep #3183) |
| duplicate | "Thanks, this is a duplicate of https://github.com/astral-sh/ruff/issues/19576." (ruff #27314) |
| fix | "Thanks! Proposed fix in #23793. Would be nice if you could verify it." (curl #23788) |
| fix | "Should be fixed by, if you want to try: https://github.com/mpv-player/mpv/pull/18193" (mpv #18192) |
| ask | "Please provide the content of the service by `systemctl cat`." (systemd #43401) |
| ask | "Does it help to revert this wlroots commit?" followed by the commit link (sway #8829) |
| decline | "ChromeOS is not supported" (PrismLauncher #6105) |
| decline | "I'm unwilling to do this at this time. The `ignore` crate needs to be re-designed, and opening up more of its internals is really not something I am willing to support." (ripgrep #3014) |
| redirect | "Please report this to inkscape. Flatpak takes no part in rendering." (flatpak #6552) |
| redirect | "File your request at https://github.com/orgs/linuxmint/discussions instead." (cinnamon #14112) |
| explain | "Thanks for the suggestion and for finding the related issues. I think this would fit better as a change to the formatting style. https://github.com/astral-sh/ruff/issues/25808 also seems closely related and was folded into #12856. That seems to fit here too." (ruff #29767) |
| invite | "Feel free to submit a patch, but I recommend just not doing that (also just for the record, this does not reproduce for me)." (alacritty #8983) |

### 2.5 The conversation around it

Median first reply arrives 3.1 hours after the report (0.6 h in siyuan, 14.6 h in vite). The median issue has 1 to 3 human comments. Between 1% (siyuan) and 40% (vite) of closed issues have no human comment at all. Reporters close their own issue in a median 17% of cases. Details per project: `research/README.md` and `research/notes/`.

## 3. How generated drafts differ from the real reply

On the same 19 threads: the real reply, a draft written with the current skill, and a draft written without it. These are the 26 test threads (the skill was never tuned on them), minus 5 where the skill declined to write and minus 2 siyuan threads.

| | real reply | with skill | without skill |
|---|---|---|---|
| words, median | 32 | 66 | 90 |
| sentences, median | 2 | 4 | 5 |
| one paragraph | 63% | 11% | 0% |
| inline code | 21% | 95% | 84% |
| contains a question | 26% | 68% | 47% |
| main move is "ask" / "explain" | 21% / 58% | 58% / 21% | 32% / 21% |
| quotes the reporter | 21% | 0% | 0% |
| has a link | 32% | 11% | 26% |
| has a hedge word | 26% | 11% | 11% |
| first sentence, words | 10 | 12 | 12 |

Not in this table: the 5 test threads where the skill declined to write (4 because the project's rules forbid AI-written comments, 1 because there was nothing to add), and the 2 siyuan threads (Chinese). The blind test below covers 21 threads, which are these 19 plus the 2 siyuan threads. Drafts ask more than the real reply (58% against 21% as the main move) partly because the drafter knows less than the real author did, and partly because of style; this table cannot separate the two.

The first sentence is the right size in all three. The difference is what follows it: drafts add a second and third sentence, more code formatting, more questions, and fewer links.

In the blind test (three judges, 21 test threads, 63 judgements) the real reply was picked as the human one 59 times, the skill draft 4 times, the no-skill draft never. When judges explained what gave the drafts away (126 explanations, counted by keywords, so approximate): polished, tidy, structured or "complete" 63%; too confident or too evenly balanced 20%; extra nobody asked for (a workaround, a proposal, a setup snippet) 18%; generic or unlike this person or project 17%; a thanks or polite closing 12%; an invented-looking link, anchor or output 4%.

## 4. How a report naturally looks, and what goes with it being fixed

Reporter-written issues by non-maintainers: 2,250. Typical contents: a version number 76%, a filled template (two or more headings) 76%, a mention of reproduction 64%, a code block 54%, log or error text 38%, a screenshot or video 22%. Median length in words: bug 254, feature 109, question 116, other 94.

Shares closed as "completed" with and without each feature, and the mean within-project difference in percentage points (projects with at least 10 issues on each side). Pooled figures can mislead: filled templates look worse pooled (71% vs 75%) and better within projects (+7).

| feature | closed as completed, within-project difference | closed as not planned or duplicate | answered by a human, within-project |
|---|---|---|---|
| mentions a version number | +9 | -9 | +5 |
| mentions reproduction | +10 | -10 | 0 |
| filled the template | +7 | -7 | +2 |
| has a screenshot or video | +8 | -8 | +4 |
| has a code block | +6 | -6 | +2 |
| has log or error text | +2 | -2 | +6 |
| body 60 words or fewer | -4 | +4 | -6 |
| body 60 to 250 words | +1 | -1 | +3 |
| body over 250 words | +2 | -2 | 0 |
| title 6 words or fewer | -3 | +3 | +2 |
| title over 12 words | +2 | -2 | -3 |

Reading: whether someone answers depends on the project far more than on the report (differences stay within about 6 points). What the report changes is whether it ends as fixed or as rejected, and the features that move that are specifics (version, reproduction, a template filled in, evidence), not length or title. This also reflects the kind of request, since bugs end "completed" more often than feature requests.

## 5. Candidate rules

Each rule says how strong the evidence is: **H** consistent across projects, **M** supported but project-dependent, **L** weak or inferred. "Varies" means the value must come from the project, not from this list.

### Replying

1. **Length comes from the project, the role and the move, as a soft target.** A maintainer comment has a median of 13 to 40 words by project; a first reply 23; an outsider's comment 37; a reporter answering a maintainer's request 50 (p75 120). The soft ceiling is the 75th percentile for that role and move (maintainer: explain 51, ask 64, decline 83, redirect 80 words), not a multiple of the median. Never cut a command, output or reproduction that the operator supplied or the thread contains. Drafts run two to three times the human median (66 and 90 words against 32). H for the direction, M for the numbers.
2. **One main point per comment.** Answer, ask, decline, point, or announce a fix, and say which in the first sentence (about 10 words). A short supporting follow-on is normal (a request to verify next to a fix announcement, the evidence behind an answer). Only 4 to 5% of comments in every role match patterns for two moves, but the patterns miss 55% of comments and were about 75% accurate, so this is a tendency, not a measured law. L to M.
3. **Asking is concrete.** Name the exact thing wanted, and the command or flag when it is not obvious. Typical maintainer ask: about 30 words; only 10% contain a code block, so a command is sometimes needed, not usually. H.
4. **Pointing is a link and a clause.** Duplicate and "already fixed in" replies: median 10.5 to 12 words, link or #ref in 64 to 95%. A redirect to another project is longer (median 39). For maintainers; an outsider offers the same as a suspicion (rule 19). H.
5. **Declining gives one reason and no apology,** roughly 37 words for maintainers (64 to 77 for the few outsiders who do it). Declining is only 7 to 8% of maintainers' first replies, so it needs a reason the thread supports. Maintainers only (rule 19). M.
6. **Explaining names the cause or the step in concrete terms** (the option, the file, the behaviour), then stops. L to M: the share of explanations that state a cause is only measured loosely.
7. **Absent by default:** greeting, header, bold label, bullet list, emoji, closing offer, em dash, summary of the thread. Each is 3% or less of maintainer comments. H for maintainers; outsiders use bold, lists and code blocks a little more (5 to 6%, 15%).
8. **Thanks only where the project does it.** Opening with thanks is 36% in ruff, 21% in godot and 4% or less in most others, so decide from the sampled comments. H, varies.
9. **Link rather than paste, and code-format identifiers.** 29% of maintainer comments link, 26% use inline code for identifiers and commands, 7% use a code block for commands and output. Drafts use inline code in 95% and link in 11%. Link only to URLs opened in this session, because an invented link is a stated tell. M.
10. **Quote only the sentence you answer** (`>`), in 17% of maintainer comments, and only when the thread has several points. M.
11. **Match surface habits only from evidence.** Lowercase openings and a missing final period are common in some projects (up to 37% and 75%). Copy them only when the operator's own comments show them; never invent them. M, varies.
12. **(Removed after review.)** Hedge words (28% of human comments) say nothing useful on their own: drafts hedge less (11%) and are still judged overconfident. The useful part is rule 14.
13. **No unrequested extras.** No design proposal, setup snippet or second topic nobody asked for. A workaround is allowed when it is the answer. This is named in about 18% of the judges' explanations, and "polished, complete" (63%) is the larger family. M.
14. **State only what was checked, as what it is.** A result may be written as run only if it was run; reading code is "as far as I can tell from X". Own test results appear in a small share of human replies (4% by keyword, a lower bound), and invented-looking evidence is the tell maintainers call out most sharply (`research/README.md`, section 6). M.

### Filing

15. **Route first.** Which kind of report this project takes as an issue, and where the rest goes, comes before any drafting (`research/README.md`, sections 3 and 4). H.
16. **Specifics, not length.** Version, exact reproduction, evidence and a filled template go with "completed" (+6 to +10 points within project); length and title do not (within 4). Exploratory: closed issues only, issue type not controlled, no intervals, 11 features by 3 outcomes. M for the direction; the numbers are not effect sizes. Never fill a specific the operator did not supply: write "unknown" instead of inventing a version or environment (see rule 14).
17. **Follow the project's template headings, and add a section when a crucial field is missing.** Filled templates go with "completed" within projects. Exploratory, M.
18. **Title states the symptom for a bug, the need for a feature request,** in the project's style (some prefix the area). Title length has no measurable relation to outcome and titles were not studied further. L.

### Added after review (apply to both)

19. **The operator's role decides which moves are allowed.** Declining, closing as duplicate, redirecting and announcing fixes are maintainer acts (outsiders do them in 2 to 4% of their comments, at 49 to 65 words). An outsider writes the same content as a suspicion with a pointer ("this looks like #3140"; "this may belong to upstream"). Role comes from the operator's permissions on the repository, and the operator's statement wins. M.
20. **Ask only what the thread cannot proceed without.** Drafts ask in 58 to 68% of cases against 26% for real replies, the largest distortion measured. Part of it is that a drafter knows less than the author of the real reply; either way, a question needs a reason. M.
21. **A reporter answering a maintainer's request answers exactly that, with the output asked for.** 282 such answers: median 50 words, p75 120, 29% over 100. These are longer than maintainers' comments and rightly so. M.
22. **Never invent a link, issue number, path, version or quote.** Evidence the operator or the thread supplied, or that was opened in this session, may be cited; nothing else. H as an integrity rule; it is not a frequency finding.
23. **Defaults when a project is unseen:** pooled medians (maintainer 27 words, outsider 37), no greeting, no thanks opener, no copied surface habits. M.
24. **Say nothing when there is nothing to add.** No "same here", no second copy of an answer already given. Report that no comment is needed. L (prior experience of maintainers, not measured here).
25. **Precedence:** correctness and completeness first (a needed command, output or reproduction stays); then the operator's own habits; then the project's habits; then these pooled defaults. M.

## 5b. Review round 1 (three independent reviewers, no context)

All three reviewers (Fable 5.2, Codex, MiniMax) agreed on these points:

- **The evidence measures resemblance, not the stated goal.** Success is "the operator posts after one or two small edits"; nothing here measures operator edits. A real reply also carries authority and knowledge the drafter lacks, so matching its shape can produce confident emptiness. Not fixed: needs the operator's real threads.
- **Rules 4 and 5 are maintainer acts** and rules 1 and 8 target the maintainer median for an operator who is often an outsider. Fixed: role section, rule 19, outsider and reporter move table.
- **"One move" and the H ratings are not supported** by regular expressions of about 75% accuracy that were changed without a new check. Fixed: rules 2, 16 and 17 downgraded and reworded. Not fixed: no hand-labelled sample yet.
- **Rule 1's ceiling cuts real content** (maintainer p75 is twice the median) and its exception was not operable. Fixed: soft ceiling by role and move, exception defined as supplied or in-thread commands and output.
- **Conflicts:** inline code (rules 3, 6) against rule 9; links (rule 9) against invented links (rule 14); workarounds (rule 13) against the outsider's actual value. Fixed in rules 9, 13 and the precedence rule 25.
- **Rule 16 can pay for fabrication** (an invented version string). Fixed in rules 16 and 22.
- **Missing:** the reporter answering a maintainer, asking too much, never inventing links, defaults for unseen projects, staying silent. Added as rules 20 to 24. Filing basics (expected against actual behaviour, minimal reproduction, one problem per issue, duplicate search) are in the skill's reference file but not in this evidence.
- **Corrections to the first version:** "most measured text is by maintainers" was wrong (they wrote 40%); rule 3's "often with a command" was wrong (10%); rule 4 grouped redirects with short replies; the 19 against 21 thread counts and the 5 dropped threads are now explained; rule 12 removed.

Still open, and not resolvable from this corpus: whether a draft should carry a note when a project requires disclosure of AI use (the operator has chosen to draft regardless); PR review threads and conversations were not collected; the operator's own comment history has not been looked at; closed issues only.

## 6. What the reviewers should challenge

- Which rules are not supported by the numbers above, or are supported only for maintainers and not for an outsider filing or commenting?
- Where could following a rule literally make the text worse, for example a length ceiling that cuts a command the reader needs?
- Which measurements are too crude to base a rule on (the move labels, keyword counts, correlations)?
- What is missing from "how people write" that matters for filing issues or for replying, given that PR review threads and PR conversations were not collected?
- Are any two rules in conflict?
- Is the structure of the evidence (measure humans, compare with drafts, list rules) sound, or does it hide an error?
