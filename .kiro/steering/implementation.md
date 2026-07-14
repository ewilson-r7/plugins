---
inclusion: fileMatch
fileMatchPattern: "plugins/**/*.py"
---
# Implementation Patterns

## Connection Rules
- `connect()` stores state and initializes client — **never** makes API calls
- `test()` validates credentials, converts `PluginException` → `ConnectionTestException`
- `credential_secret_key`: `params.get(Input.FIELD, {}).get("secretKey", "").strip()`
- `credential_username_password`: `.get("username", "").strip()` / `.get("password", "").strip()`
- Some plugins implement `test_task()` for task-specific validation
- Prefer `super().__init__()` over `super(self.__class__, self).__init__()` (modern Python)
- Authentication logic belongs in the API client class, not in connection.py
- Connection.py should only instantiate clients and pass credentials

## Action Rules
- Output keys **must** use `Output.FIELD_NAME` constants — never bare strings
- Use `self.logger` for logging — never `print()`
- Raise `PluginException` with `cause`, `assistance`, optionally `data`
- Access API via `self.connection.client`
- Use `insightconnect_plugin_runtime.helper.clean()` to strip None/empty from output — wrap the entire return dict, not individual fields
- Default values for optional inputs belong in `action.py` via `params.get(Input.FIELD, default)` — not in the API client method signature
- Never shadow Python builtins with variable names — avoid `filter`, `input`, `type`, `id`, `list`, `format`, `hash`, `map`, `range`, `set`
- Always use descriptive variable names — never single-letter variables (e.g. `key` not `k`, `item` not `i`, `value` not `v`)
- **Retry and orchestration logic belongs at the action level** — if an action needs to catch an error, perform a remediation step (e.g., install an app), and retry, that logic goes in the action's `run()` or a helper method on the action class. Service clients should raise on failure, not silently retry with side effects.

## Pagination Pattern (Cloud-Compatible)
Actions that call paginated APIs must NOT loop internally. Instead:
- Accept an optional `next_link` string input
- If `next_link` is provided, use it as the URL instead of constructing the initial endpoint
- Return `next_link` in the output (the `@odata.nextLink` or equivalent from the API)
- Wrap the return in `clean()` so `next_link` is omitted when there are no more pages
- Users drive pagination via a loop step in the ICON workflow builder

```python
if next_link:
    self.logger.info(f"Using provided next_link for pagination: {next_link}")
    url = next_link
else:
    url = Endpoint.SOME_ENDPOINT.format(self.connection.tenant, id=some_id)

# Single request — no loop
response = requests.request(method="GET", url=url, headers=headers)
result = response.json()

memberships = result.get("value")
if output_next_link := result.get("@odata.nextLink"):
    self.logger.info("Additional pages available via next_link.")

return clean({
    Output.ITEMS: memberships,
    Output.COUNT: len(memberships) if memberships else 0,
    Output.NEXT_LINK: output_next_link,
})
```

## Trigger Rules
- Infinite loop calling `self.send(output_dict)` for each event
- Track seen IDs to avoid duplicates
- Use `time.sleep(poll_interval)` — never hard-code sleep
- `run()` returns `None`

## API Client Pattern (util/api.py)
- Use plain `requests.request()` / `requests.post()` calls — do NOT store `requests.Session` objects in the class (causes issues with long-lived connections in the plugin runtime)
- Central `_make_request(method, endpoint, **kwargs)` method
- Central `_call_api(method, url, **kwargs)` for raw HTTP with timeout/connection error handling
- Handle `Timeout` → `PluginException(preset=TIMEOUT)`
- Handle `ConnectionError` → custom cause/assistance
- `_handle_status()` or `_raise_for_status()` maps HTTP codes via `HTTP_ERROR_MAP` dict
- Parse JSON with fallback to `INVALID_JSON` preset
- Combine `_call_api()` + JSON parsing + error handling in `_make_request()` for most endpoints
- Keep `_authenticate()` separate from `_make_request()` to avoid circular auth dependencies

## Base Client Pattern (for plugins with multiple API targets)
When a plugin talks to multiple services (e.g., Graph API + Bot Framework), use a shared base class:
```python
# util/base_client.py
class BaseClient:
    def __init__(self, app_id, app_secret, tenant_id, auth_url, scope, logger):
        # Shared OAuth2 client_credentials auth
        # Shared _call_api(), _get_auth_headers(), _raise_for_status()

# util/graph_api_client.py
class GraphApiClient(BaseClient):
    # Domain-specific methods, inherits auth + request handling
    def test(self):
        """Each client owns its own test logic and error handling."""
        try:
            self._authenticate()
            self._make_request("GET", "/v1.0/organization")
        except PluginException:
            raise
        except Exception as error:
            raise PluginException(cause="...", assistance="...", data=error) from error

# util/bot_service.py
class BotService(BaseClient):
    # Different scope/service URL, same auth pattern
    def test(self):
        try:
            self._authenticate()
        except PluginException:
            raise
        except Exception as error:
            raise PluginException(cause="...", assistance="...", data=error) from error
```
- Each client handles its own authentication (different scopes, different token endpoints)
- Each client implements a `test()` method with its own error handling — connection.py just catches PluginException
- Connection.py just instantiates clients and passes credentials — no auth logic in connection
- Expose public `authenticate()` and `get_auth_headers()` methods for connection test
- Use `_call_api()` for all HTTP calls (unified timeout/connection error handling)
- Use plain `requests.request()` — never store `requests.Session` in the class
- **Keep service clients independent** — never pass one client into another. If an action needs to coordinate between clients (e.g., install an app via Graph then send via Bot), the action orchestrates both. Clients should not hold references to each other.
- **Configuration belongs on the client that uses it** — if a config value (e.g., an app catalog ID) is only used by one client's API calls, store it on that client. Don't put it on the connection or pass it to unrelated clients.

## Guards for List Access
Always guard before accessing `[0]` on API results that return lists:
```python
teams = self.connection.client.get_teams(team_name)
if not teams:
    raise PluginException(
        cause="Team not found.",
        assistance=f"Please verify '{team_name}' is a valid team name.",
    )
team_id = teams[0].get("id")
```
Never assume a list result contains elements — the API may return an empty list.

## Client-Side Filtering
When an API endpoint doesn't support server-side search/filter parameters (common with list-all endpoints), implement client-side filtering in the action:
```python
result = self.connection.zia_client.list_firewall_rules(next_link or None)
rules = result.get("rules", [])

# Client-side filtering — API doesn't support server-side search
if search:
    rules = [r for r in rules if search.lower() in r.get("name", "").lower()]

return clean({
    Output.RULES: rules,
    Output.NEXT_LINK: result.get("next_link", ""),
})
```
Add the `search` input as optional in the spec. Document that it's a client-side filter in the description so users understand all results are fetched first.

## Constants Pattern (util/constants.py)
- `TIMEOUT = 60`
- `HTTP_ERROR_MAP` dict mapping status codes to `{cause, assistance}` pairs
- Cover at minimum: 400, 401, 403, 404, 429, 500, 503

## Microsoft Graph API Notes
- Some properties (e.g., `signInActivity`) require the user to be referenced by GUID, not UPN. When these properties are requested via `$select`, resolve the UPN to a GUID first with a `?$select=id` call.
- When using `$select`, the API only returns the explicitly listed properties — it drops the defaults (displayName, mail, id, etc.). Always merge user-requested properties with the default set to avoid losing standard fields.
- The `manager` navigation property cannot go in `$select` — it must use `$expand=manager`. Filter it out of any user-supplied select list.
