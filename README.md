# github-human-reply-skill

An agent skill that files GitHub issues and writes replies in issues, pull requests and review threads that you can post under your own name.

Before writing, it reads the whole thread and checks the code, the history and existing issues, so the message does not repeat or contradict what is already there. Then it writes a short, plain message instead of a report, shows you the exact text, and posts only after you approve it.

## Install

With the [skills CLI](https://github.com/vercel-labs/skills), which works with Claude Code, Codex, Cursor and other agents:

```bash
# from GitHub
npx skills add <owner>/github-human-reply-skill

# globally, for a specific agent
npx skills add <owner>/github-human-reply-skill --skill github-human-reply -g -a claude-code

# from a local clone
npx skills add ./github-human-reply-skill
```

Or copy `skills/github-human-reply/` into `~/.claude/skills/` (personal) or `.claude/skills/` (per project).

## Layout

```
skills/
└── github-human-reply/
    ├── SKILL.md                  # workflow, checks, writing rules
    └── references/
        └── gh-commands.md        # gh / API commands for reading and posting
```

## Requirements

The [gh CLI](https://cli.github.com/), authenticated.

## License

MIT
