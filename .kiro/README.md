# .kiro/ — AI Development Configuration

This directory contains configuration files for [Kiro](https://kiro.dev), an AI-powered development environment. These files guide the AI agent's behavior when working on plugins in this repository.

## Directory Structure

```
.kiro/
├── steering/       # Context rules loaded automatically or on demand
├── skills/         # Reusable multi-step workflows the agent can execute
├── hooks/          # Event-driven automation triggered by IDE/agent actions
└── settings/       # MCP servers and permission configuration
```

## Steering Files

Steering files provide context and constraints that shape how the agent works. They can be loaded automatically (on every interaction), conditionally (when specific files are open), or manually (when explicitly referenced).

| File | Inclusion | Purpose |
|------|-----------|---------|
| `repos.md` | auto | Repository routing table — which repo to use for builds vs reviews |
| `plugin-dev.md` | auto | Product overview, core rules, versioning, key commands |
| `common-mistakes.md` | auto | 38 common anti-patterns to avoid when writing plugin code |
| `structure.md` | fileMatch (`plugins/**`) | Project layout and file conventions |
| `implementation.md` | fileMatch (`plugins/**/*.py`) | Connection, action, trigger, and API client patterns |
| `exceptions.md` | fileMatch (`plugins/**/*.py`) | PluginException usage, presets, and error handling rules |
| `plugin-spec.md` | fileMatch (`**/plugin.spec.yaml`) | plugin.spec.yaml field reference and validation rules |
| `testing.md` | fileMatch (`**/unit_test/**`) | Unit testing patterns, mock strategies, coverage requirements |
| `prospector.md` | manual | Prospector/linter issue resolution guide |
| `git-workflow.md` | manual | Production release branch strategy (for upstream PRs) |
| `quick-actions-create.md` | manual | Creating InsightConnect analyst quick actions |
| `quick-actions-update.md` | manual | Updating existing quick actions after plugin version bumps |

## Skills

Skills are detailed step-by-step workflows the agent follows for specific tasks. They're activated when the user requests a matching action.

| Skill | Purpose |
|-------|---------|
| `plugin-dev.md` | Master routing skill — classifies intent, picks repo, delegates to sub-skills |
| `plugin-build-prep.md` | Pre-build readiness check (tooling, SDK version, Python version) |
| `create-new-plugin.md` | Full workflow for building a new plugin from scratch |
| `create-plugin-action.md` | Adding a new action to an existing plugin |
| `plugin-release.md` | Production release workflow (branch strategy, PR process) |
| `plugin-review.md` | Read-only plugin review and analysis |
| `refactor-plugin-auth.md` | Migrating plugins from user-delegated to app-only auth |
| `generate-plugin-html-docs.md` | Generate self-contained HTML documentation pages |
| `workflow-builder.md` | Build importable InsightConnect .icon workflow files |
| `workflow-submission.md` | Submit workflows to the rapid7/insightconnect-workflows repo |

## Hooks

Hooks run automatically when specific events occur in the IDE or agent session.

| Hook | Trigger | What it Does |
|------|---------|--------------|
| `update-steering-on-fix.json` | User-triggered | Reviews session learnings and updates steering files to prevent repeat mistakes |
| `regenerate-docs.json` | PostTaskExec | After a dev plugin build task completes, regenerates HTML docs and updates the docs site index |

## Settings

| File | Purpose |
|------|---------|
| `settings/mcp.json` | Model Context Protocol server configuration (e.g., web fetch) |
| `settings/permissions.yaml` | Shell command allowlists for the agent |

## How It Works Together

1. **Steering** loads automatically based on what files you're working with — if you open a `.py` file in a plugin, the implementation patterns and exception rules load silently
2. **Skills** activate when you ask the agent to do something specific — "build a new plugin" activates `create-new-plugin.md`
3. **Hooks** fire on events — after a build task completes, the doc generation hook updates the site
4. The `plugin-dev.md` skill acts as a router: it classifies your request (build vs review, prod vs dev) and delegates to the appropriate sub-skill

## For External Contributors

If you're looking at this repo to understand the plugin development process:
- Start with `steering/structure.md` for the project layout
- Read `steering/common-mistakes.md` for coding standards
- See `skills/create-new-plugin.md` for the full build workflow
- Check `skills/generate-plugin-html-docs.md` for how the documentation site is generated
