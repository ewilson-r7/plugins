# Plugin Release Workflow

> **Scope:** This is the **prod** release process for `insightconnect-plugins` (origin `rapid7`). Dev builds on the `plugins` fork just push a feature branch to your fork (see `repos.md`) — no release branch.

Step-by-step workflow for releasing a plugin change through the GitHub process.

## Prerequisites
- All code changes are complete and tested
- `insight-plugin validate` passes
- Prospector is clean
- Unit tests pass with ≥80% coverage

## Steps

### 1. Sync Dev Branch with Master
```bash
git checkout master && git pull origin master
git checkout feature/<your-branch>
git rebase master
git push --force-with-lease
```

### 2. Create Release Branch
```bash
git checkout master
git checkout -b <plugin-name>-<version>-release
git push -u origin <plugin-name>-<version>-release
```

Example: `microsoft-teams-8.0.0-release`

### 3. Open PR
- Source: `feature/<your-branch>`
- Target: `<plugin-name>-<version>-release`
- Fill in PR template (Type, Background, What Changed, Testing)

### 4. Wait for CI
- All checks must pass (unit tests, prospector, black, snyk)
- Address any review comments

### 5. If Master Moves During Review
Sync the release branch:
```bash
git checkout <plugin-name>-<version>-release
git merge master
git push
```

### 6. If PR Diff Shows Wrong Files
Toggle the base branch in GitHub UI (change to master, then back to release) to force diff recalculation.

### 7. After Approval
- Merge PR into release branch
- Open final PR from release branch → master
- After merge to master, delete the release and feature branches

## Commit Message Format
```
plugin_name: Short description of change

Longer explanation if needed. Bullet points for multiple changes:
- Change 1
- Change 2
```

## PR Description Template
```markdown
## 🎫 Ticket
N/A (or link)

## 🧩 Type of Change
- [x] Feature / Bug fix / Other

## 🧠 Background & Motivation
Why this change is needed.

## ✨ What Changed
Key changes summarized.

## 🧪 Testing
How it was verified.
```
