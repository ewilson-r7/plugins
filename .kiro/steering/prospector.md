---
inclusion: manual
---
# Prospector & Code Quality Rules

Prospector runs in CI on every PR. All issues must be resolved before merge.

## Tools Enabled
- **pylint** — static analysis
- **mccabe** — cyclomatic complexity (max 10)
- **bandit** — security linting
- **pycodestyle** — PEP8 style
- **dodgy** — checks for accidental secrets/debug code

## Common Issues & How to Avoid Them

### mccabe: MC0001 — Function too complex
**Threshold:** 10

**Prevention:** Break complex methods into smaller helpers:
- Extract validation logic into `_validate_*()` methods
- Extract response handling into `_handle_*_response()` methods
- Extract URL/endpoint construction into `_build_*_endpoint()` methods
- Extract pagination into `_paginate_results()`
- Extract filtering into `_filter_*()` methods

**Pattern:**
```python
# BAD — one method doing everything (complexity 13)
def get_teams(self, name, explicit):
    # compile regex, build URL, make request, paginate, filter, raise...

# GOOD — decomposed (each method complexity < 5)
def get_teams(self, name, explicit):
    endpoint = self._build_teams_endpoint(name, explicit)
    result = self._make_request("GET", endpoint)
    teams = self._paginate_results(result.get("value", []), result.get("@odata.nextLink"))
    if name:
        return self._filter_teams_by_name(teams, name, explicit)
    return teams
```

### bandit: B105 — Possible hardcoded password
**Trigger:** Any string assigned to a variable with "password", "token", or "secret" in the name, or URLs containing auth-related paths.

**Prevention:**
- Don't store token endpoint URLs in constants named with "TOKEN" — use a descriptive name like `AUTH_ENDPOINT_PATH` or build them dynamically
- Never hardcode actual credentials (obvious)
- If a constant legitimately contains "token" or "password" in its name and isn't a secret, suppress with `# nosec B105`
- Error message strings in `Cause` classes (e.g., `TOKEN_EXPIRED = "OAuth 2.0 bearer token has expired..."`) are false positives — suppress with `# noqa: B105` on the line

### pylint: import-outside-toplevel
**Prevention:** Always put imports at the top of the file. Never use `from x import y` inside a function body.

```python
# BAD
def enable_teams(self):
    from time import sleep  # pylint will flag this
    sleep(10)

# GOOD
from time import sleep  # at top of file

def enable_teams(self):
    sleep(10)
```

### pylint: too-many-arguments
**Threshold:** 5 arguments (including self)

**Options:**
1. Suppress if the method signature is a legitimate API interface:
   ```python
   def create_group(  # pylint: disable=too-many-arguments,too-many-positional-arguments
       self, name, description, nickname, mail_enabled, owners=None, members=None
   ):
   ```
2. Use a dataclass or dict for grouped parameters if the method isn't a public API boundary

### pylint: too-many-branches
**Threshold:** 15 branches per method

**Prevention:** Same decomposition approach as mccabe complexity. Common offenders:
- Methods that handle multiple HTTP status codes inline (200, 201, 202, 403, 404...)
- Methods with nested if/for/try blocks for polling or retry logic
- Methods that validate inputs, make a request, and process the response all in one

**Fix:** Extract each concern into a helper:
```python
# BAD — polling + response handling + error mapping all in one method
def _handle_async(self, response):
    # 40 lines with if/elif/for/try... (19 branches)

# GOOD — each helper has 3-5 branches
def _handle_async(self, response):
    result = self._try_direct_fetch(chat_id)
    if result:
        return result
    return self._poll_operation(location, chat_id)

def _try_direct_fetch(self, chat_id): ...
def _poll_operation(self, location, chat_id): ...
def _process_poll_response(self, response, chat_id): ...
```

### pylint: protected-access
**Prevention:** Don't call `_private_method()` from outside the class. If you need to call it from connection.py or tests, expose a public wrapper:

```python
# In base_client.py
def authenticate(self):
    """Public method for connection test."""
    self._authenticate()

def get_auth_headers(self, force_refresh=False):
    """Public method for external header access."""
    return self._get_auth_headers(force_refresh)
```

### pylint: possibly-used-before-assignment
**Prevention:** Always initialize variables before conditional branches:

```python
# BAD
if not explicit:
    compiled = re.compile(name)
# ... later ...
if compiled.search(x):  # possibly unassigned if explicit=True

# GOOD
compiled = None
if not explicit:
    compiled = re.compile(name)
```

### pylint: signature-differs
**Context:** The SDK's `connect()` method has a different base signature. This is expected in all plugins.

**Fix:** Suppress on the method:
```python
def connect(self, params):  # pylint: disable=signature-differs
```

### pylint: bad-super-call
**Prevention:** Use modern `super()` syntax:
```python
# BAD
super(self.__class__, self).__init__(input=ConnectionSchema())

# GOOD
super().__init__(input=ConnectionSchema())
```

## Running Prospector Locally

```bash
# Check specific files
prospector icon_plugin_name/util/api.py icon_plugin_name/connection/connection.py

# Check entire plugin (slower)
prospector icon_plugin_name/

# Exclude test files and generated files
prospector icon_plugin_name/ --without-tool pyflakes --ignore-paths unit_test
```

## Pre-commit Checklist
Before pushing, verify:
- [ ] No mccabe complexity > 10 (break up large methods)
- [ ] No bandit findings (no hardcoded secrets, no `# nosec` without justification)
- [ ] No unused imports
- [ ] No imports inside functions
- [ ] All variables initialized before use in conditional branches
- [ ] `too-many-arguments` either suppressed with comment or refactored
