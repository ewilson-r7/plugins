---
inclusion: fileMatch
fileMatchPattern: "plugins/**"
---
# Project Structure

## Repository Layout
```
plugins/<plugin_name>/
├── plugin.spec.yaml        # SOURCE OF TRUTH
├── Dockerfile              # [GENERATED]
├── Makefile                # [GENERATED]
├── setup.py                # [GENERATED]
├── requirements.txt        # Pinned deps (hand-written)
├── help.md                 # [GENERATED]
├── .CHECKSUM / .dockerignore  # [GENERATED]
├── bin/icon_<plugin_name>  # [GENERATED]
├── icon_<plugin_name>/     # Main package (or komand_<name> for legacy)
│   ├── actions/<name>/action.py   # HAND-WRITTEN
│   ├── connection/connection.py   # HAND-WRITTEN
│   ├── triggers/<name>/trigger.py # HAND-WRITTEN
│   ├── tasks/<name>/task.py       # HAND-WRITTEN
│   └── util/                      # HAND-WRITTEN (api.py, constants.py)
└── unit_test/
    ├── util.py             # Test helpers
    ├── test_<action>.py    # One per action/trigger/task
    ├── responses/          # Mock JSON fixtures
    └── payloads/           # Test input payloads
```

## Conventions
- Plugin directories: **snake_case**
- Package prefix: `icon_` (current) or `komand_` (legacy)
- Each action/trigger/task in its own subdirectory with `schema.py` (generated)
- One plugin per PR; PRs target `master`
- Unit tests mock HTTP calls; no live API calls

## Workflow: New Plugin
1. Write `plugin.spec.yaml` → 2. `insight-plugin create` (from parent dir) → 3. Implement hand-written files → 4. Write tests → 5. `insight-plugin validate`

## Workflow: Add New Action/Trigger/Task
1. Edit `plugin.spec.yaml` — add the action definition, bump version (semver), bump SDK version to latest, add `version_history` entry
2. Run `insight-plugin refresh` — this **generates** the new action folder with `schema.py` and `__init__.py`; never create these by hand
3. Implement `action.py` (or `trigger.py`/`task.py`) in the generated folder
4. Add any new API methods to `util/api.py`
5. Write unit tests in `unit_test/`
6. Run `insight-plugin validate`

## Workflow: Update Existing Plugin
1. Read spec → 2. Edit spec → 3. `insight-plugin refresh` → 4. Update implementation → 5. Update tests → 6. Update `version_history` → 7. `insight-plugin validate`
