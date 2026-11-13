# gh commands

`O/R` is `owner/repo`, `N` an issue or PR number. Add `--repo O/R` (or use the full path in `gh api`) whenever the target is not the current checkout. Issues and PRs share one number space, and a PR's conversation tab is served by the issues endpoints.

## Contents

- Account, repository, role
- Project rules
- Reading an issue
- Reading a PR
- How people here write
- Checking facts
- Before filing an issue
- Posting

## Account, repository, role

```bash
gh auth status                                  # which account will post
gh repo view O/R --json nameWithOwner,isFork,parent,defaultBranchRef
gh api repos/O/R --jq '.permissions'            # evidence of the user's role, not proof
```

`push`, `maintain` or `triage` set to true suggests the user helps run the project. What the user says about their role wins.

## Project rules

```bash
gh api repos/O/R/community/profile --jq '.files | to_entries[] | select(.value) | .key'   # which files exist
gh api repos/O/R/contents/CONTRIBUTING.md -H "Accept: application/vnd.github.raw"
gh api repos/O/R/contents/SECURITY.md -H "Accept: application/vnd.github.raw"
gh api repos/O/R/contents/.github/PULL_REQUEST_TEMPLATE.md -H "Accept: application/vnd.github.raw"
```

The community profile lists which files exist but not their text, and it does not report `SECURITY`. File names and locations vary (`docs/`, `.github/`, the owner's `.github` repository), so look at the profile's `html_url` values or the repository root when a path returns 404. Search what you fetched for "AI", "LLM", "generated", "agent" and "human-written" to find the project's policy on AI-written text.

A 404 means "not found at this path with this account". On a private or restricted repository it does not prove the file is absent.

## Reading an issue

`gh issue view N --comments` is fine for a quick look but can be long and loses IDs. For the full thread:

```bash
gh issue view N --repo O/R --json title,body,state,stateReason,author,labels,createdAt,closedAt
gh api repos/O/R/issues/N/comments --paginate \
  --jq '.[] | {id, user: .user.login, created_at, body}'
gh api repos/O/R/issues/N/timeline --paginate \
  --jq '.[] | select(.event=="cross-referenced" or .event=="referenced" or .event=="closed")'
```

The timeline shows PRs and issues that mention this one and the commit or PR that closed it.

## Reading a PR

Three separate sources. The conversation view does not include inline review threads.

```bash
gh pr view N --repo O/R --json title,body,state,author,baseRefName,headRefName,mergedAt,closingIssuesReferences
gh api repos/O/R/issues/N/comments --paginate   # conversation tab
gh api repos/O/R/pulls/N/reviews --paginate     # review summaries
```

Inline review threads, with resolution state and the IDs needed to reply:

```bash
gh api graphql --paginate -f query='
query($owner: String!, $repo: String!, $pr: Int!, $endCursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      reviewThreads(first: 50, after: $endCursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id isResolved isOutdated path line
          comments(first: 100) {
            nodes { databaseId author { login } body createdAt }
          }
        }
      }
    }
  }
}' -f owner=O -f repo=R -F pr=N
```

`--paginate` walks the threads, not the comments inside one thread. If a thread reaches 100 comments, fetch the rest of that thread separately before calling the read complete.

The thread `id` is what a GraphQL reply needs. The first comment's `databaseId` is the top-level comment ID a REST reply needs.

## How people here write

On a busy repository the newest comments are mostly bots and reporters, so go through search instead of the comment feed.

The people who run the project are whoever closes, labels and merges, whatever badge they show:

```bash
gh api "repos/O/R/issues?state=closed&per_page=30" --jq '.[] | select(.pull_request|not) | .closed_by.login' | sort | uniq -c | sort -rn
gh search issues --repo O/R --commenter LOGIN --sort updated --limit 5 --json number,title
gh api repos/O/R/issues/N/comments --paginate --jq '.[] | select(.user.login=="LOGIN") | .body[0:800]'
```

The user's own recent comments, in this repository and then anywhere:

```bash
gh search issues --repo O/R --commenter @me --include-prs --sort updated --limit 5 --json number,title
gh api graphql -f query='{ viewer { issueComments(last: 20) { nodes { url body } } } }' \
  --jq '.data.viewer.issueComments.nodes[] | {url, body: .body[0:800]}'
```

About a dozen comments from each side are enough. Skip ones that are mostly pasted logs.

## Checking facts

```bash
gh search issues "<2-3 keywords>" --repo O/R --include-prs      # open and closed
gh search issues "<2-3 keywords>" --repo O/R --state closed --match title
gh pr list --repo O/R --state all --search "<keywords>"
gh release list --repo O/R --limit 10
git log --oneline -S'<string>' -- <path>       # when a string appeared or vanished
git blame -L <start>,<end> <path>
git tag --contains <sha>                        # which releases include a commit
git show <tag>:<path>                           # the file as the reporter has it
```

Search terms are ANDed, so four words often return nothing where two return the duplicate. Try at least two wordings: the error text, and the symptom in plain words.

Without a local clone, the same checks work through the API:

```bash
gh api "repos/O/R/contents/<path>?ref=<tag-or-sha>" -H "Accept: application/vnd.github.raw"   # a file at a version
gh api "repos/O/R/commits?path=<path>&per_page=10" --jq '.[] | "\(.sha[0:8]) \(.commit.message | split("\n")[0])"'
gh api repos/O/R/compare/<tag>...<sha> --jq '.status'    # "behind" or "identical": the tag contains the commit
gh search code "<symbol>" --repo O/R
```

## Before filing an issue

```bash
gh api repos/O/R/contents/.github/ISSUE_TEMPLATE --jq '.[].name'
gh api repos/O/R/contents/.github/ISSUE_TEMPLATE/config.yml -H "Accept: application/vnd.github.raw"
gh api repos/O/.github/contents/.github/ISSUE_TEMPLATE --jq '.[].name'   # owner-wide fallback
gh label list --repo O/R --limit 100
```

A 404 here usually means the folder does not exist, which is normal. For a YAML issue form, render each field's `attributes.label` as a `###` heading with the answer under it, which is what the web form produces. If `config.yml` has `blank_issues_enabled: false`, use one of the templates.

## Posting

Write the approved text to a temporary file outside the repository, then post from the file.

```bash
body=$(mktemp)    # write the approved text into "$body"

# new issue
gh issue create --repo O/R --title "<title>" --body-file "$body"

# comment on an issue, or on a PR's conversation tab
gh issue comment N --repo O/R --body-file "$body"

# reply in a review thread (REST): COMMENT_ID is the thread's top-level comment
gh api -X POST repos/O/R/pulls/N/comments/COMMENT_ID/replies -F body=@"$body"

# reply in a review thread (GraphQL): THREAD_ID from the reviewThreads query
gh api graphql -f query='
mutation($threadId: ID!, $body: String!) {
  addPullRequestReviewThreadReply(input: {pullRequestReviewThreadId: $threadId, body: $body}) {
    comment { url }
  }
}' -f threadId=THREAD_ID -F body=@"$body"
```

Notes:

- The REST reply endpoint takes only `body`. Its `COMMENT_ID` must be the top-level comment of the thread; to answer a later comment, reply to the same thread and it lands at the bottom.
- Add `--label`, `--assignee`, `--type` or `--milestone` to `gh issue create` only when the user asked. Use labels that already exist. If the chosen template would set labels or a type, say so in the draft summary and let the user decide.
- Each command prints or returns the URL of the new comment or issue. Pass it on to the user.
- To fix a typo in something already posted, with the user's approval:
  `gh api -X PATCH repos/O/R/issues/comments/COMMENT_ID -F body=@"$body"`. An edit does not recall the notification email.
- Posting many comments in quick succession trips GitHub's secondary rate limit. Post one at a time.
- After a failure or timeout, list the thread's latest comments before retrying.
