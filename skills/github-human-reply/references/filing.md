# Filing an issue

The case file from `ghr.py new` lists the templates and their fields, the project's own rules about issues, labels and duplicate candidates. Also read `references/writing.md`: the same rules apply to the text. Observations here come from 17 open-source projects; each project differs, so the case file wins.

## 1. Route first

| Kind | Where it usually goes |
|---|---|
| Bug | An issue, in every project studied. Bugs in a packaged app, a distribution's build or a dependency belong to that project. |
| Question or support | Often not the tracker: discussions, chat, a forum. |
| Feature request | An issue in most projects. Some refuse it in the tracker (their contact links or CONTRIBUTING name discussions, a proposals repository or a mailing list). |
| A fix you have | Differs: an issue first, a note inside the bug report, or a pull request with no issue. |

If this project does not take this kind of report as an issue, do not draft one: say where it goes. A suspected vulnerability never goes into a public issue; use the channel the SECURITY file names.

## 2. Before writing

- Search open and closed issues with two or three wordings, including ideas that were already declined. If the same problem exists, show it to the operator; usually the right move is a short comment there with the new information, or nothing.
- Reproduce on a supported version (the latest release or the default branch) and say which one.
- One problem per issue.

## 3. The body

- **Bug:** the exact version, the exact steps or commands, what happened, what was expected, and trimmed real output. Follow the template field by field with its own headings, leave no placeholder, and add a section only if a crucial field is missing. Attach the log the form asks for instead of interpreting it. Offer a cause only if it was verified.
- **Feature request:** the concrete problem, why the existing options do not solve it, and the smallest change that would. Check for an earlier declined idea. Do not invent bug sections.
- **Offering a fix:** state the intent in the issue and wait for a go-ahead, unless the project is plainly PR-first. A fast pull request on an untriaged bug often loses to the maintainer's own fix. Link the PR the way recent merged PRs here do (`Fixes #N` in the body, a commit trailer, or in the title).

Never fill a specific the operator did not supply: write "unknown" instead of inventing a version or environment. Strip tokens, keys, internal hostnames and home-directory paths from logs.

## 4. Title and length

The title states the symptom for a bug and the need for a feature request, in the project's style (some prefix the area, most use a plain sentence). No "[Bug]" unless the form sets it. Keep the body no longer than this project's usual report; typical bug reports are 120 to 550 words, and long sectioned reports with unverified analysis are the ones maintainers call out.

## 5. Posting

After the operator approves the exact title and body, use `ghr.py post issue`. Add no labels, assignees, types or milestones unless asked.
