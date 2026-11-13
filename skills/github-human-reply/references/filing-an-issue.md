# Filing an issue

Read this before drafting a new issue. It covers where a report belongs, what it has to contain, and how a fix gets tied to it. The observations come from a study of 17 projects (ruff, vite, curl, neovim, systemd, podman, flatpak, the Linux Mint repositories and others); each project differs, so read the target project's own files and treat the patterns below as what to look for.

## Contents

- Route it first
- Before writing
- Bug reports
- Feature requests
- Proposing a fix
- Linking a pull request
- Title and body

## Route it first

Decide what kind of report this is, then find out where this project wants that kind. Read the issue templates, `.github/ISSUE_TEMPLATE/config.yml` (its `contact_links` name the other venues), and `CONTRIBUTING`.

| Kind | Where projects send it |
|---|---|
| Bug | An issue, in every project studied. Bugs in a packaged app, a distribution's build or a dependency belong to that project instead. |
| Question, support | Often not the tracker: discussions, IRC, Discord, a forum. |
| Feature request | An issue in most projects. Several refuse them in the tracker and use discussions, a proposals repository or a mailing list. |
| A fix you have | Depends on the project: an issue first, a note inside the bug report, or a pull request with no issue at all. |

If this project does not take this kind of report as an issue, do not draft one. Tell the user where it goes and help with that instead.

A suspected vulnerability never goes into a public issue. Stop and point the user to the private channel in `SECURITY`.

## Before writing

- Search open and closed issues with two or three wordings, including the error text. For a feature, look for the same idea already declined. In some projects a quarter of new issues are closed as duplicates.
- If the search finds the same problem, show it to the user. The right move is usually a short comment there with the new information, or nothing.
- Reproduce on a version the project still supports, normally the latest release or the default branch, and record exactly which one. Maintainers close reports against old versions with one line.
- One problem per issue.

## Bug reports

What every project wants, in its own form: the exact version, the commands or steps, what happened, what was expected. What projects add on top, which you find in the template:

- a reproduction that runs as given: a repository link, a zip, shell commands that create the files
- a run with a clean configuration (`--clean`, `--no-config`, default theme, no plugins)
- a full log or backtrace, attached rather than described
- a comparison with a reference tool

Rules that held across projects:

- Fill the form field by field. A placeholder left in, or a required section left empty, gets the issue closed.
- Lead with the commands and their real output. Only include output that was actually produced. A plausible-looking transcript that nobody ran is the fastest way to lose a maintainer's trust.
- Attach the log the form asks for instead of interpreting it.
- Offer a cause only if it was verified, and only where the project's reports do that. A wrong guess costs more than no guess.

## Feature requests

Shorter than bug reports in almost every project. What gets a real answer: the concrete problem, why the existing options do not solve it, and the smallest change that would. Requests are declined often, sometimes for half of them, usually with one reason. Check for earlier decisions on the same idea before filing, and say so if the request differs from one that was declined.

Do not invent bug-report sections for a feature request.

## Proposing a fix

Projects split three ways, so find out which applies here:

- **Issue first.** Describe the bug, say you intend to fix it, wait for a maintainer's go-ahead. Some projects have a claim mechanism such as `/assign`.
- **Inside the bug report.** A short "likely cause" or "suggested fix" in the issue, verified, then a PR when a maintainer agrees.
- **Pull request directly.** Some projects answer a fix pasted into an issue with "please submit this as a PR".

A fast pull request on a bug nobody has triaged often loses: maintainers land their own fix beside it, or several competing PRs sit unmerged. State the intent and wait, unless the project is plainly PR-first.

Check whether the project has rules for the PR itself: a signed-off commit, a checkbox about AI-written text, a template to fill.

## Linking a pull request

Use the form this project uses, which you can see in its recent merged PRs:

- `Fixes #N` or `Closes #N` in the PR body is the most common.
- Some want it in the commit message as a trailer (`Fixes: #N`, `Closes: #N`, or a full URL).
- Some repeat it in the title (`fix: ... (fix #N)`).
- In projects where maintainers commit the change themselves and close by hand, there is nothing to add.

## Title and body

The title states the symptom as observed ("`build` exits 0 when a plugin throws"), not a proposed fix and not a category. Follow the project's style: some prefix the area (`lsp: ...`, `docs: ...`), most use a plain sentence. Do not add "[Bug]" unless the form sets it.

The body follows the project's template and uses only its headings. Without a template, plain paragraphs:

- what happens, and what you expected instead, a sentence each
- the smallest steps that reproduce it, numbered, with the exact command
- version and environment, as far as they matter
- the error trimmed to the relevant lines, with tokens, keys, internal hostnames and home-directory paths removed

Keep it no longer than this project's usual report. Median bug reports in the projects studied run from about 120 to 550 words; long, sectioned reports with unverified analysis are the ones maintainers call out as generated.
