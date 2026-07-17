---
inclusion: auto
---
# Commit Guidelines

## Format

Use conventional commit format for the plugin repos:

```
plugin_name: Short description of change
```

For non-plugin commits (docs, .kiro, repo config):

```
type(scope): description
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

## Focus on WHY, not WHAT

The diff shows what changed. The commit message explains why.

**Bad** (restates the diff):
```
zscaler: Update timeout from 30 to 60
```

**Good** (explains motivation):
```
zscaler: Increase timeout to prevent failures on large tenant queries

Customers with 10k+ users were hitting timeouts during full user list
retrieval. 60s matches the ZIA API's own gateway timeout.
```

## Logical Commits

- One logical change per commit — don't mix unrelated changes
- Each commit should leave the codebase in a working state
- Separate refactoring from features (refactor first, then add)

## AI Agent Attribution

Do not add `Co-authored-by` trailers for AI agents. Commits represent human intent and ownership — the agent is a tool, not an author.
