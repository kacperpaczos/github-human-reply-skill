#!/usr/bin/env python3
"""Collect recent closed issues, recent PRs and issue-template metadata for the
repositories in repos.txt. Read-only: uses `gh api` GET/GraphQL queries only.

Usage: python3 research/collect.py [owner/repo ...]
Output: research/data/<owner>__<repo>.json
"""
import json, pathlib, subprocess, sys, base64

HERE = pathlib.Path(__file__).parent
DATA = HERE / "data"
N_ISSUES, N_PRS, PAGE = 150, 100, 25

ISSUES_Q = """
query($owner:String!,$repo:String!,$n:Int!,$after:String){
  repository(owner:$owner,name:$repo){
    issues(first:$n,after:$after,states:CLOSED,orderBy:{field:CREATED_AT,direction:DESC}){
      pageInfo{hasNextPage endCursor}
      nodes{
        number title body createdAt closedAt stateReason locked
        author{login __typename} authorAssociation
        issueType{name}
        labels(first:15){nodes{name}}
        comments(first:40){totalCount nodes{
          author{login __typename} authorAssociation createdAt body url}}
        closedByPullRequestsReferences(first:5,includeClosedPrs:true){nodes{
          number title createdAt mergedAt author{login} authorAssociation}}
        timelineItems(itemTypes:[CLOSED_EVENT,CROSS_REFERENCED_EVENT,LABELED_EVENT,MARKED_AS_DUPLICATE_EVENT],first:40){nodes{
          __typename
          ... on ClosedEvent{createdAt actor{login} closer{__typename ... on PullRequest{number} ... on Commit{oid}}}
          ... on CrossReferencedEvent{createdAt actor{login} source{__typename ... on PullRequest{number} ... on Issue{number}}}
          ... on LabeledEvent{createdAt actor{login} label{name}}
          ... on MarkedAsDuplicateEvent{createdAt actor{login}}
        }}
      }
    }
  }
}"""

PRS_Q = """
query($owner:String!,$repo:String!,$n:Int!,$after:String){
  repository(owner:$owner,name:$repo){
    pullRequests(first:$n,after:$after,states:[MERGED,CLOSED],orderBy:{field:CREATED_AT,direction:DESC}){
      pageInfo{hasNextPage endCursor}
      nodes{
        number title body createdAt mergedAt closedAt state
        author{login __typename} authorAssociation
        changedFiles additions deletions
        labels(first:15){nodes{name}}
        closingIssuesReferences(first:5){nodes{number}}
        comments{totalCount} reviews{totalCount} reviewThreads{totalCount}
        commits{totalCount}
      }
    }
  }
}"""


def gh(args, check=True):
    r = subprocess.run(["gh", "api", *args], capture_output=True, text=True)
    if r.returncode != 0:
        if check:
            raise RuntimeError(r.stderr.strip()[:300])
        return None
    return r.stdout


def paged(query, key, owner, repo, total):
    out, after = [], None
    while len(out) < total:
        args = ["graphql", "-f", f"query={query}", "-f", f"owner={owner}", "-f", f"repo={repo}",
                "-F", f"n={min(PAGE, total - len(out))}"]
        if after:
            args += ["-f", f"after={after}"]
        conn = json.loads(gh(args))["data"]["repository"][key]
        out += conn["nodes"]
        if not conn["pageInfo"]["hasNextPage"]:
            break
        after = conn["pageInfo"]["endCursor"]
    return out


def templates(owner, repo):
    """Issue templates from the repo, falling back to the owner's .github repo."""
    for src in (f"{owner}/{repo}", f"{owner}/.github"):
        raw = gh([f"repos/{src}/contents/.github/ISSUE_TEMPLATE"], check=False)
        if not raw:
            continue
        files = {}
        for f in json.loads(raw):
            if f.get("type") != "file":
                continue
            body = gh([f"repos/{src}/contents/{f['path']}"], check=False)
            if body:
                files[f["name"]] = base64.b64decode(json.loads(body)["content"]).decode("utf-8", "replace")
        return {"source": src, "files": files}
    return {"source": None, "files": {}}


def main():
    repos = sys.argv[1:] or (HERE / "repos.txt").read_text().split()
    DATA.mkdir(exist_ok=True)
    for full in repos:
        owner, repo = full.split("/")
        dest = DATA / f"{owner}__{repo}.json"
        if dest.exists():
            print(f"skip {full} (exists)")
            continue
        try:
            meta = json.loads(gh([f"repos/{full}"]))
            profile = json.loads(gh([f"repos/{full}/community/profile"], check=False) or "{}")
            rec = {
                "repo": full,
                "meta": {k: meta.get(k) for k in ("stargazers_count", "language", "open_issues_count", "has_discussions", "default_branch")},
                "community_files": sorted(k for k, v in (profile.get("files") or {}).items() if v),
                "templates": templates(owner, repo),
                "issues": paged(ISSUES_Q, "issues", owner, repo, N_ISSUES),
                "prs": paged(PRS_Q, "pullRequests", owner, repo, N_PRS),
            }
        except Exception as e:  # keep going; report at the end
            print(f"FAIL {full}: {e}")
            continue
        dest.write_text(json.dumps(rec))
        print(f"ok {full}: {len(rec['issues'])} issues, {len(rec['prs'])} prs, {len(rec['templates']['files'])} templates")


if __name__ == "__main__":
    main()
