# Git — Workflow Reference

Branch management, PR review, and stash patterns. Most gotchas arise when switching
context between a large in-progress working tree and reviewing a teammate's PR.

---

## Branch health check before switching

```bash
# See how two branches diverge
git log --oneline origin/their-branch ^main        # commits they have, main doesn't
git log --oneline main ^origin/their-branch        # commits main has, they don't

# If the second list is empty → their branch already contains main (no rebase needed)
# If both lists are non-empty → branches have diverged (rebase before merge)
```

---

## Reviewing a teammate's PR with a dirty working tree

Prefer a named branch over stash when the working tree is large — stashes are anonymous
and two large stashes with overlapping files cause messy conflicts on pop.

**Option A — Create a WIP branch (recommended for large working trees):**
```bash
git checkout -b my-wip-branch
git add -A && git commit -m "wip: <description>"

git fetch origin their-branch
git checkout their-branch   # or: git checkout -b review/their-branch origin/their-branch

# review, approve, merge on GitHub

git checkout my-wip-branch
git rebase main             # pick up the merged changes
```

**Option B — Stash (fine for small/focused changes):**
```bash
git stash list              # check for existing stashes first
git stash drop stash@{0}    # drop stale stashes before adding a new one
git stash push -m "my wip description"

git checkout -               # detach or checkout their branch
# review and approve

git checkout main && git pull
git stash pop               # resolve any conflicts in the named files
```

---

## Reading a stash diff

`git stash show -p | grep "^+++"` shows only destination filenames:

| Pattern | Meaning |
|---|---|
| `+++ b/path/to/file` | file modified or added in stash |
| `+++ /dev/null` | file **deleted** in stash |

All `+++` — no merge conflict markers. Conflict risk only materialises on `git stash pop`
if the merged branch touched the same named files.

---

## After merging a teammate's PR

```bash
git checkout main && git pull   # pull the merge commit

# If you used a WIP branch:
git checkout my-wip-branch
git rebase main                 # likely conflicts only in shared config files

# If you used stash:
git stash pop                   # git will flag conflicts inline
```

**Files most likely to conflict** (touched by multiple branches):
`CLAUDE.md`, `Makefile`, `.env.example`, `pyproject.toml`, `uv.lock`

---

## When does a PR need a rebase before merge?

| Situation | Action |
|---|---|
| `main ^their-branch` is empty | No rebase needed — their branch already contains `main` |
| Both sides have unique commits | Rebase their branch on `main` (or merge `main` into theirs) |
| Their branch has a `Merge branch 'origin/main'` commit | They already merged `main` in — check the divergence count, not just commit messages |

---

## Commit style (project convention)

- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`, `wip:`
- Title ≤ 60 chars, imperative mood
- Body: why, not what
- Branch names include Linear ID: `LIN-123-short-description`
