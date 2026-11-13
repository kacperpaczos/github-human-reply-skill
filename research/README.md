# How 17 open-source projects handle GitHub issues

Maintainers in all 17 projects answer in a median of 13 to 40 words, without greetings or headings, and most of them want one thing from a reporter: the exact command, its real output, and the version, in the project's own form. Where a report belongs depends on its kind: every project takes bugs as issues, but four refuse feature requests in the tracker, and the route for a fix ranges from "issue first, then `/assign`" (podman) to "just send the PR" (systemd). Long, sectioned, unverified text is the most punished style in the sample: godot refused 24 of 150 sampled issues as AI-authored, and maintainers or regular contributors in 11 other projects reacted to suspected LLM text with a rebuke or a close.

## Method and limits

`collect.py` fetched, per repository, the 150 most recently created closed issues (with up to 40 comments each), the 100 most recently created closed or merged PRs (bodies only), and the issue templates. `analyze.py` computed `data/stats.json`. `digest.py` rendered about 21 threads and 10 PRs per repository, and one reader per repository wrote a note from that digest. Quotes used below were checked against the raw JSON. Section 6 adds examples found by searching the raw comments, marked "raw data".

What the numbers cannot support:

- Only closed issues, newest first. Open and long-running threads are absent, so reply times and thread lengths are biased low, and nothing is known about reports that never get an answer.
- Issue kind is guessed from labels, type, title and headings. alacritty has 47% "other" and ruff 2% "feature", so the bug/feature shares are rough.
- "Maintainer" is anyone with an owner, member or collaborator badge or who closes or labels other people's issues. "First reply" is the first comment by anyone other than the author.
- `closed_not_planned` and `closed_duplicate` depend on maintainers setting a reason. alacritty shows 100% "completed", so its 0% duplicates means nothing.
- The closing-keyword regex misses `Fixes: <URL>` (flatpak, podman) and commit trailers. curl merges outside GitHub, so its merged% (1) is meaningless.
- siyuan is mostly Chinese; its word counts are not comparable.
- PR comments and reviews were not collected. Nothing here describes review conversations.

## Opening an issue

### Bug reports

Every project takes bugs as issues, and 16 of 17 have a bug template (alacritty has none captured; sway's is plain Markdown, the rest are forms). The common demand is version, steps, expected and actual result. Projects differ in what they add: a mandatory reproduction artifact (vite, godot), a clean-configuration run (neovim, mpv, siyuan), a comparison with a reference tool (neovim, ripgrep, nemo), or a supported-version gate (systemd, cinnamon, vite). Median bug body is 124 to 556 words (median of repositories 213); 5% to 85% of bodies contain a code block.

| Repository | Where | Key requirement | Example |
|---|---|---|---|
| alacritty | issue | version, textual symptom, `--print-events` log | #8920 |
| ruff | issue | snippet, `ruff check --isolated` command, output, version | #27333 |
| ripgrep | issue | `rg --version`, shell commands that create the files, real output | #3180 |
| curl | issue | "I did this / I expected", full `curl -V`, `uname -a` | #22923 |
| flatpak | issue | version, distro, exact commands with output; app bugs go to the app | #6539 |
| godot | issue | version and commit hash, steps as text, MRP zip | #124712 |
| helix | issue | "I tried / I expected / Instead", tested on master | #16322 |
| cinnamon | issue | current 6.6.x, hardware field, steps | #13690 |
| nemo | issue | latest version, terminal run, backtrace or shell steps | #3730 |
| mpv | issue | per-platform form, full log, `--no-config` repro | #18332 |
| neovim | issue | `nvim --clean` repro on nightly, "Vim behaves the same?" | #41995 |
| podman | issue | real `podman info`, failing and control commands | #29600 |
| PrismLauncher | issue (support: Discord) | launcher log, numbered steps | #6392 |
| siyuan | issue | four confirmations, default theme, no plugins | #21298 |
| sway | issue (questions: IRC) | debug log, minimal config, symbolized backtrace | #8939 |
| systemd | issue | one of the two newest releases, journal output | #43700 |
| vite | issue | runnable reproduction link, or auto-close after 3 days | #22971 |

### Feature requests

Four projects do not want them in the tracker. The rest accept them but decline often: 45% of ripgrep's and 42% of flatpak's sampled issues closed as not planned, and 25% of PrismLauncher's closed as duplicates. Median feature body is 37 to 244 words, shorter than the median bug report in every project except curl, where a 1% feature share makes the figure unusable.

| Repository | Where | Key requirement | Example |
|---|---|---|---|
| alacritty | issue | check earlier decisions first | #8929 |
| ruff | issue (rule request) | one "Summary" with motivation | #27310 |
| ripgrep | issue | behaviour, motivation, examples; new flags are declined | #3215 |
| curl | mailing list | not wanted; closed as "a discussion topic" | #23070 |
| flatpak | issue | use case; low-level control is declined | #6497 |
| godot | godot-proposals repository | not wanted in this tracker | #125165 |
| helix | "Idea" Discussion; issue only for a small concrete change | large requests are declined or closed as duplicates | #16092 |
| cinnamon | org discussions | not wanted; template marked OBSOLETE | #13920 |
| nemo | org discussions | not wanted | #3879 |
| mpv | issue | check it is not already supported | #18466 |
| neovim | issue | say why existing commands or Lua do not suffice | #41983 |
| podman | issue | description, potential solution, alternatives | #29946 |
| PrismLauncher | issue (suggestion or RFC form) | not a previously rejected idea | #5999 |
| siyuan | issue | one request per issue, broadly applicable, not graph-related | #21396 |
| sway | issue | window-management features must exist in i3 | #8760 |
| systemd | issue (RFE) | problem, solution, alternatives | #43807 |
| vite | issue | description and suggested solution | #23215 |

### Proposals of a fix

Projects split three ways: propose inside the issue and wait for a go-ahead, issue first by rule, or PR directly. The sway and mpv notes found no stated requirement.

| Repository | Where | Key requirement | Example |
|---|---|---|---|
| alacritty | issue or direct PR | no-LLM checkbox in the PR | #9055 to PR #9056 |
| ruff | inside the issue ("Likely cause") | wait for a maintainer's direction | #27245 |
| ripgrep | offer in the issue | wait for "go for it", send tests | #3127 |
| curl | diff in the issue, or PR on request | none stated | #23025 |
| flatpak | maintainer names the fix, reporter sends the PR | test case | #6508 to PR #6519 |
| godot | PR after a bug issue; small fixes direct | one topic per PR | PR #125267 |
| helix | issue with root cause and an offer | none stated | #15318 to PR #15320 |
| cinnamon | direct PR | keep any in-issue proposal compact | #14024 |
| nemo | direct PR | cause, then fix | PR #3731 |
| mpv | either | state what was tested and what was not | #18527 |
| neovim | "Suggested fix" in the bug | verified cause | #42309 |
| podman | issue first | claim with `/assign` | #29600 |
| PrismLauncher | PR; RFC form for larger changes | signed-off commits | PR #6416 |
| siyuan | issue first (text changes excepted) | fill the PR template | PR #20851 |
| sway | either | none stated | #8909 to PR #8910 |
| systemd | direct PR | a fix pasted in an issue gets `please-submit-as-pr` | #43547 |
| vite | state the intent in the issue, then PR | repro in the issue | #23975 to PR #23976 |

## Issues and pull requests

The share of issues closed through a PR runs from 0% (siyuan) to 69% (neovim). A low share does not mean fixes are unlinked: in siyuan, cinnamon and nemo the maintainer commits and closes by hand, and ripgrep's owner lands outsider work in his own rollup commits (#3290, #3127). systemd is the opposite case: 61% of issues closed by a PR, but only 7% of PRs name an issue, because most PRs have none.

| Repository | Closed via PR / commit % | PRs with closing keyword / linked issue % | Convention | Outsider route |
|---|---|---|---|---|
| alacritty | 6 / 0 | 30 / 30 | `Fixes #N` in body; many closed by hand | both |
| ruff | 45 / 0 | 14 / 19 | `Closes #N` under `## Summary`; also by hand | issue first |
| ripgrep | 18 / 6 | 37 / 36 | `Fixes #N`; owner rollup commits | issue first |
| curl | 49 / 17 | 33 / 33 | `Fixes #N` and `Reported-by:` as commit message | issue first, PR on request |
| flatpak | 25 / 0 | 18 / 24 | trailer `Closes: #N` or `Fixes: <URL>` | both |
| godot | 54 / 0 | 33 / 45 | `Closes #N` in body | issue first; small fixes direct |
| helix | 32 / 3 | 12 / 16 | `Closes #N`; bodies often empty | both |
| cinnamon | 12 / 10 | 19 / 18 | bare `Fixes #N`; mostly by hand | PR first |
| nemo | 10 / 16 | 20 / 20 | bare `Fixes #N`; maintainer commit | PR first |
| mpv | 27 / 14 | 16 / 18 | `Fixes #N` or `Closes #N` | both |
| neovim | 69 / 1 | 33 / 28 | `Fix #N` in a "Problem: / Solution:" body | issue first |
| podman | 56 / 5 | 72 / 45 | `Fixes: #N` in body and commit message | issue first, `/assign` |
| PrismLauncher | 22 / 0 | 18 / 19 | `Fixes #N` in body | both |
| siyuan | 0 / 0 | 10 / 0 | maintainer commit link, closed by hand | issue first |
| sway | 25 / 0 | 30 / 38 | `Fixes`, `Closes` or `Resolves` | both |
| systemd | 61 / 1 | 7 / 7 | `Fixes #N` as last line | PR first |
| vite | 62 / 0 | 63 / 40 | `fix #N`, repeated in the title | issue first |

A fast outsider PR on a fresh bug often loses. Maintainers landed their own fix beside it in ruff (#28721) and neovim (PR #42026 vs #42027, #42240 vs #42244); vite left two PRs each unmerged on #23348, #23523 and #23383; podman's claimed #29600 still drew three competing PRs. Outsider merge rates are 24% (vite), 26% (ruff) and 20% (alacritty), against 85% (podman) and 94% (systemd). The notes cannot say why PRs were passed over, since review text was not collected.

## How conversations go

**Speed.** Median first reply is 0.6 h (siyuan) to 14.6 h (vite), 3.1 h across repositories. Between 1% (siyuan) and 40% (vite) of issues close with no human comment at all.

**Length.** The median issue has 1 to 3 human comments. Maintainer comments have a median of 13 (cinnamon) to 39.5 (ruff) words; 18% to 57% are 15 words or fewer. Outsiders write more than maintainers in 14 of the 16 comparable projects (median 27 to 61 words; ruff and flatpak are the exceptions, siyuan is excluded).

**Form.** A greeting opens 0% to 5% of comments. Headings or bold labels appear in 0% to 6%. A "thanks" opener is 1% to 12%, except ruff at 24%.

**Tone.** Mostly flat and technical. ruff is the one consistently warm project ("Thanks for the report!", #27333). Sarcasm appears in mpv ("I hope there is world peace.", #18509) and bluntness in flatpak ("The issue is completely devoid of useful information.", #6668).

The standard moves:

- **Ask for information**, one thing at a time. "Please provide an MRE. Without instructions to reproduce, this won't be actionable." (ripgrep #3223). "You still haven't provided any information about hardware." (cinnamon #13696). "That provides zero information to us." (podman #30062, a placeholder instead of `podman info`).
- **Decline**, one reason, sometimes an alternative. "No. `ignore` is tightly coupled with file system APIs and I don't want to change that. Sorry." (ripgrep #3093). "we aren't going to add new `--foo` args for random features." (neovim #41983). "This is how curl has treated FTP URLs since the beginning. It is not a bug." (curl #22999).
- **Duplicate**, one line and a link. "Duplicate of https://github.com/helix-editor/helix/issues/6747" (helix #15395). "Let's track this at ..." (vite #22982). ruff says "fold this into" (#29550).
- **Redirect.** "That's a missing feature and belongs in a proposal, please open one over there" (godot #125165). "Please ask questions on IRC, not on the issue tracker." (sway #9107). "Please submit the suggested change as a PR. Thank you." (systemd #43547).
- **Close on version or silence.** "cinnamon-6.0.4 isn't a support version, reopen if you can reproduce with cinnamon-6.6.x" (cinnamon #13796). "Seems like this isn't going to see any update." (alacritty #8964, after six days).
- **Invite a patch.** "PR welcome." (neovim #41709). "A patch with tests is welcome." (ripgrep #3158).

Reporters answer briefly, with the data asked for, and often close the issue themselves: 44% in sway, 39% in helix, 25% in curl and mpv, median 17%.

## Policies on AI-written text

Seven projects state a policy in material the sample captured. The others have none visible, but maintainers still react.

| Repository | Stated policy | Observed |
|---|---|---|
| godot | Contribution rules: no AI-authored issue reports; "Do not use AI-generated text in human-to-human communication" (quoted in #124837) | 24 of 150 sampled issues refused as AI-authored (raw data), 23 closed not planned. "Closing as this is too verbose and AI authored, if you clean it up it can be reopened" (#124842). Repeat offenders are warned of a ban (#124929). |
| curl | Bug form: "Do not paste massive AI generated explanations. We accept the use of AI as long as it is digestible." | "This has all the smell of a silly LLM finding." (#23696, raw data), on a report with no reachable trigger. |
| podman | LLM policy; PR checklist certifies "PR description, commit message, and GitHub comments are human-written" | "stop using AI tools to interact with users here." (#29986, raw data). The note reports AI-prepared #29891 was handled normally. |
| PrismLauncher | AI policy in CONTRIBUTING; an `AI` label | "also no AI" (#6439); "Do not use AI to write issues." (#6346, raw data). Label on #5999 and #6117. |
| alacritty | No-LLM policy for patches (PR #8878), checkbox in the PR template | PR #9089 disclosed LLM use and closed unmerged; the reason is not in the data. |
| vite | PR template: "Keep the PR description and discussion concise. Use your own words" | "Please don't use agents to get it done quickly." (#23383) |
| mpv | Contribution docs require full understanding of AI-assisted code (cited in #18384, raw data) | "Attach full log file, not LLM speculation" (#18365, raw data) |

Without a stated policy: cinnamon ("What AI provided you with that bullshit?", #13629), neovim ("I didn't read the rest of this.", #41959, raw data), systemd (#43675, raw data), flatpak ("You should stop spamming these meaningless LLM generated issues", #6672, raw data), helix (#16002, raw data), ripgrep ("Your tables are bunk.", #3052, raw data).

Three things stand out:

1. **What triggers the reaction is verbosity plus an unverified claim**, not disclosure. The flagged reports were long, sectioned, and asserted things nobody had run: an unreachable overflow (curl #23696), a repro that bypassed the mapping under test (neovim #41959), unfilled placeholders (cinnamon #14040).
2. **Disclosure helps in some projects and not in godot.** Disclosed AI use was merged in nemo (PR #3593) and neovim (PR #42648). In godot, six of the seven sampled issues titled with a 🤖 marker closed as not planned and the seventh was a misfile (raw data); #124758 got "We don't allow issues to be posted by AI agents". This contradicts the godot note, which reads the marker as protective.
3. **godot allows translation.** "You can write the issue manually in Chinese and use AI to translate it, that's alright." (#124817, raw data); that issue was reopened and confirmed.

Nothing AI-related appears in the sway or siyuan samples. flatpak accepts AI-assisted code; a maintainer says almost all recent contributions were assisted (#6509, raw data).

## What this means for the skill

### For filing an issue

1. **Route by kind before drafting.** Read the templates, `config.yml` contact links and CONTRIBUTING. Do not file a feature request in curl, godot, cinnamon or nemo; name the right venue instead (#23070, #125165, #13920, #3879).
2. **Check the AI policy first.** In godot and PrismLauncher, do not produce the issue text: the user writes it, and the skill may translate (godot #124817) or check completeness. In podman, comments must be human-written (#29986).
3. **Fill the project's form field by field, with no placeholder left.** Empty or unfilled templates were closed in mpv #18509, neovim #42304, podman #30062 and cinnamon #14040.
4. **Lead with commands, real output and the exact version.** Never include output that was not actually produced. Fixed reports had this in ripgrep #3180, ruff #27333, nemo #3730 and podman #29600.
5. **Confirm on a supported version first**, and say which was tested (cinnamon #13796, vite #23312, helix #16322).
6. **Stay at or under the repository's median bug length** (`body_words_bug`, 124 to 556 words) and use only the form's own headings.
7. **Offer a cause only where the project does so, and only if verified.** ruff and neovim take "Likely cause" sections (#27245, #42309); wrong ones are caught in a line ("Really?", neovim #42387).
8. **Search open and closed issues, including rejected ideas.** Duplicates are 25% of PrismLauncher's and 22% of ruff's sample (#5999, #29767).
9. **Match the title style.** `area: symptom` in neovim (49% prefixed) and curl (37%); a plain sentence elsewhere. No "[Bug]" tag unless the form presets it (flatpak).
10. **State the intent to fix in the issue and wait for direction.** Do not open a PR on an untriaged bug (vite #23383, ruff #28721, ripgrep #3127, podman `/assign`).
11. **Link a PR with the repository's own form** from the table above: `Fixes: #N` in the commit for podman, `fix #N` in the title for vite, commit-message body for curl.

### For replying

1. **Keep a reply under the repository's median outsider comment** (`outsider_comment_words`, 27 to 61 words) unless it carries requested output.
2. **No greeting, no headings, no bold labels, no sign-off.** These appear in at most 5% and 6% of human comments.
3. **Open with thanks only where maintainers do** (ruff 24%; median 4% elsewhere).
4. **Answer the exact question asked, in one comment, with the command output in a code block** (cinnamon #13696, mpv #18365).
5. **Retest when asked and report the result plainly** (curl #22923, mpv #18217).
6. **On "duplicate" or "not a bug", concede in one line and close**, or push back once with a concrete case (neovim #41960). Authors close a median 17% of issues.
7. **Never post "can I work on this" or "same issue".** Both go unanswered or are rebuked (vite #23215, podman #29986, nemo #3697).
8. **Assert only what was run, and say what was not tested** (mpv #18527). Wrong claims get "This isn't true." (vite #23348).
9. **Write in English**; Chinese is also accepted in siyuan (#21386).
