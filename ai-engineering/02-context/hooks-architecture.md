# Hook Architecture — galactus

How the Claude Code hook suite works in this project.

## Overview

Hooks are shell scripts invoked by the Claude Code harness at lifecycle events. They enforce standards automatically — no reminders needed mid-task. All hooks live in `.claude/hooks/`. They source `.claude/hooks/lib.sh` for shared utilities.

## Lifecycle events

| Event | When it fires | Used for |
|---|---|---|
| `PreToolUse` | Before a tool call | Block risky git commands, branch naming guard, secrets scan, pre-commit test gate |
| `PostToolUse` | After a tool call | Code quality lint, memory duplication check |
| `Stop` | When the agent finishes a turn | macOS notification |
| `PreCompact` | Before context compaction | Session checkpoint capture |

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Pass — proceed |
| `2` | Block — Claude sees stderr as an error and must fix before proceeding |
| Other | Advisory — logged but not blocking |

## Current hooks

| Hook | Event | Matcher | What it does |
|---|---|---|---|
| `risky-git-guard.sh` | PreToolUse | Bash | Blocks force push, reset --hard, rebase -i, branch -D main |
| `branch-guard.sh` | PreToolUse | Bash | Blocks `git commit` when branch lacks `vir-[0-9]+` Linear ID |
| `bash-antipattern.sh` | PreToolUse | Bash | Advisory check for common bash antipatterns |
| `dor-guard.sh` | PreToolUse | Bash | Advisory check before executing plans without DoR context |
| `dod-guard.sh` | PreToolUse | Bash | Blocks PR/push paths with unfinished stubs or missing DoD checks |
| `structure-guard.sh` | PreToolUse | Write/Edit/MultiEdit/Bash | Blocks new top-level `evals/` dirs outside `graders`, `metrics`, `pipelines`, `reports` |
| `secrets-scan.sh` | PreToolUse | Write/Edit/MultiEdit | Blocks writes that appear to contain secrets |
| `memory-duplication-guard.sh` | PreToolUse | Write/Edit/MultiEdit | Advisory warning when memory files repeat bullets already in CLAUDE.md |
| _(inline in settings.json)_ | PostToolUse | Bash | macOS notification when pytest finishes |
| _(inline in settings.json)_ | Stop | — | macOS notification when Claude finishes a turn |
| _(inline in settings.json)_ | PreCompact | — | Runs `~/.claude/hooks/pre-compact.sh` for session snapshots |

Pre-commit test gate is inline in `settings.json`: runs `uv run pytest tests/` before every `git commit`.

## `lib.sh` utilities

```bash
source "$(dirname "$0")/lib.sh"   # script-relative — works regardless of CWD

claude_path()     # file_path from CLAUDE_TOOL_INPUT
claude_command()  # command from CLAUDE_TOOL_INPUT
claude_content()  # new_string / content from CLAUDE_TOOL_INPUT
warn "msg"        # print to stderr, exit 1 (advisory)
block "msg"       # print to stderr, exit 2 (blocking)
```

## Adding a new hook

1. Write the script in `.claude/hooks/<name>.sh` — source `lib.sh`, exit 0 or exit 2
2. `chmod +x .claude/hooks/<name>.sh`
3. Add an entry to `.claude/settings.json` under the relevant matcher

Pattern for a file-type-scoped PostToolUse hook:
```bash
#!/usr/bin/env bash
source "$(dirname "$0")/lib.sh"
path=$(claude_path)
[ -z "$path" ] && exit 0
echo "$path" | grep -qE '\.py$' || exit 0   # scope to Python files

# ... checks ...
[ -n "$issues" ] && block "$issues"
exit 0
```

Pattern for a Bash PreToolUse guard:
```bash
#!/usr/bin/env bash
source "$(dirname "$0")/lib.sh"
cmd=$(claude_command)
echo "$cmd" | grep -qE 'some-pattern' || exit 0
block "Guard: reason why this is blocked."
```

## Settings layers

| File | Purpose | Committed? |
|---|---|---|
| `~/.claude/settings.json` | Global defaults for all projects | Yes (global) |
| `.claude/settings.json` | Team settings for this repo | Yes |
| `.claude/settings.local.json` | Personal overrides (gitignored) | No |

`settings.local.json` is gitignored — use it for personal Bash permissions (broader `allow` list), faster pre-commit (skips slow targets), personal API keys.
