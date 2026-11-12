# gh commands

`O/R` is `owner/repo`, `N` an issue or PR number. Add `--repo O/R` (or use the full path in `gh api`) whenever the target is not the current checkout. Issues and PRs share one number space, and a PR's conversation tab is served by the issues endpoints.

## Contents

- Account, repository, role
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
gh api repos/O/R --jq '.permissions'            # push: true means maintainer voice
```

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

The thread `id` is what a GraphQL reply needs. The first comment's `databaseId` is the top-level comment ID a REST reply needs.

## How people here write

Recent comments by maintainers of the repository, newest first:

```bash
gh api "repos/O/R/issues/comments?sort=created&direction=desc&per_page=100" --jq '
  .[] | select(.author_association=="OWNER" or .author_association=="MEMBER" or .author_association=="COLLABORATOR")
      | select(.user.type=="User") | {user: .user.login, body}'
```

The user's own recent comments, first in this repository, then anywhere:

```bash
me=$(gh api user --jq .login)
gh api "repos/O/R/issues/comments?sort=created&direction=desc&per_page=100" \
  --jq ".[] | select(.user.login==\"$me\") | .body"
gh api graphql -f query='{ viewer { issueComments(last: 20) { nodes { url body } } } }' \
  --jq '.data.viewer.issueComments.nodes[] | {url, body}'
```

Ten to twenty comments are enough. Skip ones that are mostly pasted logs or look generated.

## Checking facts

```bash
gh search issues "<keywords>" --repo O/R --include-prs          # open and closed
gh search issues "<keywords>" --repo O/R --state closed --match title
gh pr list --repo O/R --state all --search "<keywords>"
gh release list --repo O/R --limit 10
git log --oneline -S'<string>' -- <path>       # when a string appeared or vanished
git blame -L <start>,<end> <path>
git tag --contains <sha>                        # which releases include a commit
git show <tag>:<path>                           # the file as the reporter has it
```

Try at least two wordings in the search: the error text, and the symptom in plain words.

## Before filing an issue

```bash
gh api repos/O/R/contents/.github/ISSUE_TEMPLATE --jq '.[].name'
gh api repos/O/R/contents/.github/ISSUE_TEMPLATE/config.yml -H "Accept: application/vnd.github.raw"
gh api repos/O/.github/contents/.github/ISSUE_TEMPLATE --jq '.[].name'   # owner-wide fallback
gh api repos/O/R/community/profile --jq '.files'                         # CONTRIBUTING, SECURITY, templates
gh label list --repo O/R --limit 100
```

A 404 means the file is absent, which is normal. For a YAML issue form, render each field's `attributes.label` as a `###` heading with the answer under it, which is what the web form produces. If `config.yml` has `blank_issues_enabled: false`, use one of the templates.

## Posting

Write the approved text to a temporary file outside the repository, then post from the file.

```bash
body=$(mktemp --suffix=.md)    # write the approved text into "$body"

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
- Add `--label`, `--assignee`, `--type` or `--milestone` to `gh issue create` only when the user asked, or the template declares them. Use labels that already exist.
- Each command prints or returns the URL of the new comment or issue. Pass it on to the user.
- To fix a typo in something already posted, with the user's approval:
  `gh api -X PATCH repos/O/R/issues/comments/COMMENT_ID -F body=@"$body"`. An edit does not recall the notification email.
- Posting many comments in quick succession trips GitHub's secondary rate limit. Post one at a time.
- After a failure or timeout, list the thread's latest comments before retrying.
