---
inclusion: auto
---
# Product Overview & Core Rules

This is the **Rapid7 InsightConnect Plugins** monorepo — 250+ open-source plugins for the InsightConnect SOAR platform. Each plugin is a self-contained Python package exposing **actions**, **triggers**, and **tasks** for automated playbooks.

## Repo Routing (read `repos.md` for full details)
- **Build/update/enhance** → ask **prod or dev** (never infer from the working directory).
  - prod → `insightconnect-plugins/plugins/<name>` (full release flow)
  - dev → `plugins/plugins/<name>` fork (lightweight feature-branch flow)
- **Review/question** → read-only from a master repo (`insightconnect-plugins`, or `komand-plugins` for legacy).
- Before any build, run the `plugin-build-prep` skill (tooling check + latest SDK version from `komand-plugin-sdk-python/README.md`).

## Plugin Concepts
- **Actions**: One-shot operations (e.g., "Get Agent Details", "Quarantine Device")
- **Triggers**: Event-driven polling loops that emit events via `self.send()`
- **Tasks**: Polling/scheduled background operations
- **Connection**: Auth and API client setup — shared across all actions/triggers/tasks

## Core Rules (always apply)
- Python 3.13, SDK `insightconnect-plugin-runtime` latest available
- Formatter: Black (v21.5b1), Linter: Prospector (max complexity 10)
- Always use `self.logger` — never `print()`
- Always raise `PluginException` or `ConnectionTestException` — never raw `Exception`
- Use `Output.FIELD_NAME` constants — never bare string keys
- Use descriptive variable names — no single-character identifiers (e.g., `k`, `v`, `x`) even in comprehensions or lambdas
- `plugin.spec.yaml` is the source of truth — write/update it first, then run `insight-plugin refresh` to generate action/trigger/task scaffolding before writing implementation code
- Never edit generated files: `schema.py`, `setup.py`, `bin/icon_*`, `__init__.py`, `.CHECKSUM`, `.dockerignore`, `Makefile`, `help.md`
- `requirements.txt` deps must be version-pinned (e.g., `requests==2.31.0`)
- `connect()` only stores state — never makes API calls; `test()` validates credentials
- Always `.strip()` string credentials
- Minimum 80% code coverage on all new/modified code
- Always run `insight-plugin validate` before declaring work done

## Versioning (semver)
| Change | Bump |
|--------|------|
| Remove/rename field, change type, add required input | **Major** |
| New action/trigger/task, add optional field | **Minor** |
| Bug fix, SDK update, dependency update | **Patch** |

Every version bump requires a `version_history` entry in `plugin.spec.yaml`.

## Key Commands
```bash
insight-plugin create    # scaffold new plugin (run from parent dir)
insight-plugin refresh   # regenerate schemas after spec changes
insight-plugin validate  # lint and validate plugin
python -m pytest unit_test/ --cov=icon_<name> --cov-report=term-missing
```

## Resources
- Style guide: https://docs.rapid7.com/insightconnect/style-guide/
- Source: https://github.com/rapid7/insightconnect-plugins
