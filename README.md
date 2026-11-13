# github-human-reply-skill

An agent skill that files GitHub issues and writes replies in issues, pull requests and review threads that you can post under your own name.

Before writing, it reads the whole thread and checks the code, the history and existing issues, so the message does not repeat or contradict what is already there. Then it writes a short, plain message instead of a report, shows you the exact text, and posts only after you approve it.

## Install

With the [skills CLI](https://github.com/vercel-labs/skills), which works with Claude Code, Codex, Cursor and other agents:

```bash
# from GitHub
npx skills add kacperpaczos/github-human-reply-skill

# globally, for a specific agent
npx skills add kacperpaczos/github-human-reply-skill --skill github-human-reply -g -a claude-code

# from a local clone
npx skills add ./github-human-reply-skill
```

Or copy `skills/github-human-reply/` into `~/.claude/skills/` (personal) or `.claude/skills/` (per project).

## Layout

```
skills/
└── github-human-reply/
    ├── SKILL.md              # the workflow: gather, close gaps, draft, show, post after approval
    ├── scripts/ghr.py        # one command gathers the thread, rules, project style, duplicates; guarded poster
    └── references/
        ├── writing.md        # how to write the draft, including the humanize pass
        └── filing.md         # routing and writing for a new issue
research/                     # how 17 projects write issues and replies, and the evidence behind the rules
benchmark/                    # reply benchmark against real maintainer replies
```

## Requirements

The [gh CLI](https://cli.github.com/), authenticated, and Python 3.8 or newer.

## License

MIT
