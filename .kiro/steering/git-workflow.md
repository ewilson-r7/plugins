---
inclusion: manual
---
# Git & Release Workflow

> **Scope:** This is the **prod** release flow for `insightconnect-plugins` (origin `rapid7`). For **dev** builds on the `plugins` fork (`ewilson-r7/plugins`), use the lightweight feature-branch flow in `repos.md` — no release branch needed.

## Branch Strategy

```
master (protected)
  └── feature/<plugin-name>-<description>     (dev work)
        └── PR → <plugin-name>-<version>-release  (staging/test)
              └── PR → master                      (production)
```

## Development Flow

1. **Create dev branch from master:**
   ```bash
   git checkout master && git pull
   git checkout -b feature/microsoft-teams-app-only-auth
   ```

2. **Do work, commit, push:**
   ```bash
   git add <specific files>
   git commit -m "plugin_name: Short description"
   git push -u origin feature/microsoft-teams-app-only-auth
   ```

3. **Before creating release PR, sync with master:**
   ```bash
   git checkout master && git pull
   git checkout feature/microsoft-teams-app-only-auth
   git rebase master
   git push --force-with-lease
   ```

4. **Create release branch from master:**
   ```bash
   git checkout master
   git checkout -b microsoft-teams-8.0.0-release
   git push -u origin microsoft-teams-8.0.0-release
   ```

5. **Open PR:** dev branch → release branch

6. **If master moves while testing on release branch:**
   ```bash
   git checkout microsoft-teams-8.0.0-release
   git merge master
   git push
   ```

## Key Rules

- **Rebase private dev branches** (keeps history linear)
- **Merge into shared branches** (don't rewrite shared history)
- **`--force-with-lease`** not `--force` (protects against overwriting others' work)
- **Stage specific files** — avoid `git add .` to prevent committing secrets or unrelated changes
- **Never push directly to master**
- **Commit message format:** `plugin_name: Short description of change`

## PR Diff Shows Wrong Files

If the PR shows file differences that don't exist (stale merge base):
- **Quick fix:** Toggle the PR base branch in GitHub UI (change to master, then back to release) — forces diff recalculation
- **Alternative:** Close and reopen the PR
- **Root cause:** Dev branch was rebased but release branch wasn't synced with master

## Amending Commits

- Only amend your own unpushed commits
- After amending a pushed commit, use `--force-with-lease` to push
- Never amend commits on shared branches

## Release Branch Naming

Format: `<plugin-name>-<version>-release`

Examples:
- `microsoft-teams-8.0.0-release`
- `defender-atp-2.0.0-release`
- `abnormal-security-1.5.0-release`
