#!/usr/bin/env python3
"""Give every benchmark case a standalone repository whose history ends at the cut.

The shared partial clones contain every later commit and branch, so `git log origin/master` would show
the future fix. Here each case gets its own repo built by fetching only the cut commit and its
ancestors (blobs on demand), with no branches and no tags.

Usage: python3 benchmark/isolate_repos.py [case-id ...]   (default: all built cases)
"""
import json, pathlib, shutil, subprocess, sys

WORK = pathlib.Path(__file__).resolve().parent / "work"
SANDBOX = pathlib.Path.home() / ".cache" / "ghr-bench"   # outside the project, so a model cannot wander into hidden/
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))


def sh(*a, cwd=None, check=True):
    p = subprocess.run(a, cwd=cwd, capture_output=True, text=True)
    if check and p.returncode:
        raise RuntimeError(f"{' '.join(a)}: {p.stderr.strip()[-300:]}")
    return p.stdout.strip()


def isolate(cid):
    case = WORK / "cases" / cid
    dest = case / "repo_iso"
    if (dest / ".git").exists():
        return "have"
    wt = case / "repo"
    sha = sh("git", "rev-parse", "HEAD", cwd=wt)
    repo = sh("git", "rev-parse", "--git-common-dir", cwd=wt)
    clone = pathlib.Path(repo).resolve()
    sh("git", "config", "uploadpack.allowFilter", "true", cwd=clone)
    sh("git", "config", "uploadpack.allowAnySHA1InWant", "true", cwd=clone)
    dest.mkdir(parents=True, exist_ok=True)
    sh("git", "init", "-q", cwd=dest)
    sh("git", "remote", "add", "origin", str(clone), cwd=dest)
    sh("git", "fetch", "-q", "--no-tags", "--filter=blob:none", "origin", sha, cwd=dest)
    sh("git", "checkout", "-q", "--detach", "FETCH_HEAD", cwd=dest)
    n = sh("git", "rev-list", "--count", "HEAD", cwd=dest)
    refs = sh("git", "for-each-ref", cwd=dest)
    head_date = sh("git", "log", "-1", "--format=%cI", cwd=dest)
    return f"ok {sha[:8]} {head_date} commits={n} refs={'none' if not refs else 'PRESENT'}"


def sandbox(cid):
    """Move the isolated repo out of the project, cut its link to the full clone, and put the inputs beside it."""
    import make_snapshot
    sb = SANDBOX / cid
    if (sb / "repo" / ".git").exists():
        return "have"
    iso = WORK / "cases" / cid / "repo_iso"
    if not (iso / ".git").exists():
        isolate(cid)
    sb.mkdir(parents=True, exist_ok=True)
    shutil.move(str(iso), str(sb / "repo"))
    sh("git", "remote", "remove", "origin", cwd=sb / "repo", check=False)
    (sb / "snapshot.json").write_text(json.dumps(make_snapshot.build(cid)))
    for f in ("thread.md", "room.md"):
        shutil.copy(WORK / "cases" / cid / "input" / f, sb / f)
    left = sh("git", "remote", cwd=sb / "repo")
    refs = sh("git", "for-each-ref", cwd=sb / "repo")
    return f"sandboxed remotes={'none' if not left else left} refs={'none' if not refs else 'PRESENT'}"


if __name__ == "__main__":
    cases = sys.argv[1:] or sorted(p.name for p in (WORK / "cases").iterdir() if (p / "repo").exists())
    for c in cases:
        try:
            print(c, isolate(c), sandbox(c), flush=True)
        except Exception as e:
            print(c, "FAIL", e, flush=True)
