---
name: deslop
description: Remove AI-generated code slop from Python plugin code. Use when asked to "clean up AI code", "deslop", "remove slop", or after a large AI-generated changeset to tighten it up before committing.
---

# Remove AI Code Slop

Check the diff against main and remove AI-generated slop introduced in the current working changes.

## Focus Areas (Python / InsightConnect Plugins)

- **Unnecessary comments** — comments restating what the code does (`# increment counter` above `counter += 1`), or comments inconsistent with local style
- **Defensive overkill** — try/except blocks that can never fire, None checks on values that are always populated, redundant `if not x: return` guards for impossible states
- **Over-abstraction** — helper functions called from exactly one place, base classes with a single subclass, strategy patterns for code that does one thing
- **Unnecessary complexity** — builder patterns, factory functions, or config objects for things constructed in one place
- **Stuttering names** — `class ZscalerZscalerClient`, `def get_get_users()`, redundant prefixes that repeat the module name
- **Error message noise** — `PluginException` chains that produce `Failed to get users: Failed to make request: Failed to connect: actual error`. One wrap is enough.
- **Dead code** — unused helper functions, unreachable branches, commented-out code blocks, imports used nowhere
- **Import bloat** — imported modules used for a single trivial call that could be inlined
- **Overly verbose error handling** — multi-line try/except/raise blocks where a simple `raise PluginException(...)` suffices
- **Speculative flexibility** — configurable timeouts nobody changes, optional parameters with no use case, generic type hints on concrete implementations
- **Redundant logging** — `self.logger.info("Starting get_users")` followed by `self.logger.info("Finished get_users")` on a 3-line method
- **Over-documentation** — docstrings that restate the function signature, or `"""Get user."""` on a method called `get_user()`

## Process

1. Identify changed files:
   ```bash
   git -C ~/Documents/GitHub/plugins diff --name-only main -- plugins/
   ```
2. For each changed `.py` file, read the diff and surrounding code
3. Identify slop patterns from the focus areas above
4. Apply minimal, focused edits — one concern at a time
5. Run `prospector` on modified files to verify no new issues introduced
6. Run `insight-plugin validate` if spec or structural files were touched

## Guardrails

- Keep behavior unchanged unless fixing a clear bug
- Prefer minimal, focused edits over broad rewrites
- Match the existing codebase style, not an idealized style
- Don't remove pre-existing slop unless asked — only clean up what the branch introduced
- Don't touch generated files (`schema.py`, `__init__.py`, `setup.py`, `help.md`)
- Don't reformat code that wasn't part of the change (let Black handle formatting)
- Keep the final summary concise (1-3 sentences per file touched)

## Common Python Plugin Slop Patterns

### Before (sloppy)
```python
def get_users(self, params={}):
    """Get users from the API."""
    # Get the search parameter from params
    search = params.get(Input.SEARCH, "")
    # Log that we are starting
    self.logger.info(f"Starting get_users with search={search}")
    # Call the API client to get users
    try:
        result = self.connection.client.get_users(search=search)
    except Exception as error:
        # Handle the error
        raise PluginException(
            cause="Failed to get users",
            assistance="An error occurred while getting users",
            data=error,
        ) from error
    # Log that we finished
    self.logger.info(f"Finished get_users, got {len(result)} users")
    # Return the cleaned result
    return {Output.USERS: clean(result)}
```

### After (clean)
```python
def get_users(self, params={}):
    search = params.get(Input.SEARCH, "")
    result = self.connection.client.get_users(search=search)
    return {Output.USERS: clean(result)}
```

The API client already handles errors with `PluginException`. The action doesn't need to re-wrap them. The logging adds no diagnostic value on a simple pass-through action.
