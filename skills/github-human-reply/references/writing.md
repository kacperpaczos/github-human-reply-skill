# Writing the draft

The case file's "How people write here" section gives the numbers for this project. Use them. Everything below was measured on real maintainer, contributor and reporter comments from 17 open-source projects.

## What goes in

1. **The first sentence carries the point:** the answer, the finding or the question. No greeting, no sign-off, and no "thanks" as the opening unless thanks-openers are common here (the case file shows the share).
2. **One main point.** A short supporting follow-on is normal (what to check, the evidence behind the answer). Make the move completely: an answer says what is true and why in a clause; a request says exactly what to provide and how to get it (the command, the flag); a pointer is a link and a clause; a "no" gives one reason and no apology.
3. **Then stop.** No workaround, design proposal, setup snippet or second topic nobody asked for, unless that is the answer. Do not restate the thread or summarise your own message.
4. **Be concrete.** Name the file, option, version or commit. Format identifiers as code. Link code as a permalink at a commit instead of pasting it; paste only what the reader lacks (a command, trimmed output).
5. **Ask only what the thread cannot move without.** Real replies contain a question in about a quarter of cases; drafts drift to more than half. One question, and say how to answer it.
6. **Integrity.** Say only what is in the case file or what you checked. "I ran it" only if it was run; something read in code is "as far as I can tell from `file`". Unknown stays unknown. No invented links, numbers, versions or quotes. No promises or dates on the operator's behalf. No talk about process ("after analysing the codebase"), tools or how the text was made.

## Role

Contributor: observations, pointers and suspicions. Maintainer (only when the operator says so): may decline, point elsewhere or announce a fix, with one reason.

## Length and form

Aim near the median in the case file and stay under the 75th percentile, unless a command, output or reproduction needs the room; never cut those to hit a number. A typical human reply is two sentences in one paragraph; a one-line paragraph is fine. A reporter answering a maintainer's request writes more (median about 50 words, up to 120) and should answer exactly what was asked, with the output requested.

Plain prose. No headings, bold labels, bullets or emoji in a reply; numbered steps only for reproduction; a code block only for a command or output.

## Language and register

Write in the language the maintainers use in this thread (the case file says which). Professional, plain, direct. Match their formality and how they cite code and issues. No forced slang and no imitation of typos.

## Humanize pass (before showing the draft)

Read the draft as the maintainer who receives it. In this order:

1. Cut every sentence that restates the thread, announces what you are about to say, or sums up.
2. Cut extras: a workaround, a proposal, a snippet, a second question beyond the one needed.
3. Cut filler: greetings, "thanks for reporting" (unless thanks-openers are common here), "hope this helps", "let me know", "feel free to".
4. Replace evenly balanced hedging with one clear statement of what is verified and one clause flagging the single thing that is not.
5. Break the symmetry. If paragraphs or sentences have the same size and build, merge or cut: people stop when they are done, and a fragment is fine when it is clear ("Fixed in 4e1c9aa.").
6. Remove em dashes, "not X but Y", lists of three, and stock words (crucial, robust, seamless, delve, comprehensive, ensure, leverage, additionally, furthermore).
7. Check that every link, number and identifier is in the case file or was opened in this session.

Then compare the length with the numbers in the case file once more.

## Contrasts

Too thin to act on, then what the maintainer actually wrote:

> Can you grab a stack trace?

> Please provide a stack trace. You can do so by compiling from source, reproducing the crash and then running `coredumpctl gdb` and then `bt full`.

Generated-looking, then enough:

> Thanks for the suggestion! This already exists, it's just hidden from the help output, so it's easy to miss. [code block] For bash, you can enable it with: [second code block] The other supported shells are covered in the docs.

> There is a `generate-shell-completion` subcommand for bash, fish, zsh and a few others. It's missing from `--help` but documented here: (link)

Something read in code but not run:

> as far as i can tell from the code, helix only replaces the current split if `takeFocus` is true ([here](permalink)). not sure that's what the spec intends, but it might explain what you're seeing.

After a fix was pushed in a review thread:

> Fixed in 4e1c9aa.
