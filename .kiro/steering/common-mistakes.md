---
inclusion: auto
---
# Common Mistakes & Checklist

## Mistakes to Avoid
1. **Editing auto-generated files** — changes will be overwritten by `insight-plugin`
2. **Bare string output keys** — use `Output.FIELD_NAME` from schema imports
3. **API calls in `connect()`** — only `test()` makes API calls
4. **Raising raw `Exception`** — use `PluginException` or `ConnectionTestException`
5. **Using `print()`** — use `self.logger`
6. **Unpinned requirements** — exact versions only (e.g., `requests==2.31.0`)
7. **Skipping `insight-plugin validate`**
8. **Wrong semver bump** — Major: breaking, Minor: additive, Patch: fixes
9. **Coverage below 80%**
10. **Missing `version_history`** — validate crashes without it
11. **Mixing preset and custom cause/assistance** — preset wins silently
12. **Manually creating schema.py** — let tooling generate them
13. **Forgetting `.strip()` on credentials**
14. **Hard-coding sleep in triggers** — use configurable `poll_interval`
15. **Shadowing Python builtins** — never use `filter`, `input`, `type`, `id`, `list`, `format`, `hash` as variable names (Prospector will flag `redefined-builtin`)
16. **Quoting version_history entries** — entries must NOT have quotes around them (e.g. `- 1.0.0 - Initial plugin release`, not `- '1.0.0 - Initial plugin release'`)
17. **Accessing `[0]` without guards** — always check `if not results:` before indexing into API response lists
18. **Auth logic in connection.py** — authentication belongs in the API client class; connection just passes credentials
19. **Using legacy `super(self.__class__, self).__init__()`** — use modern `super().__init__()`
20. **Using `/beta` Graph API endpoints** — always use `/v1.0` (GA) unless the feature is genuinely beta-only
21. **Including `{tenant_id}` in Graph API resource paths** — the tenant is determined by the auth token, not the URL path
22. **Hardcoding token endpoint tenants** — single-tenant bots use the app's own tenant ID, not `botframework.com`
23. **Importing inside functions** — move all imports to the top of the file (pylint: import-outside-toplevel)
24. **Mocking at the wrong level in tests** — action tests should mock client methods, not `requests.get`/`requests.post`
25. **Using `requests.Session` in class state** — use plain `requests.request()`/`requests.post()` calls; stored sessions cause issues with long-lived plugin processes
26. **Using `data=str(error)` in PluginException** — pass the error object directly (`data=error`); the SDK handles `str()` conversion internally
27. **Separate try-except blocks in connection test** — use a single `try-except` that catches `PluginException` and passes `error.cause`, `error.assistance`, `error.data` to `ConnectionTestException`
28. **Em dashes (`—`) in spec YAML fields** — the EncodingValidator rejects them. Use hyphens (`-`) instead in `requirements`, `description`, `version_history`, etc.
29. **Long-running pagination loops in actions** — plugins run in ICON Cloud with short runtime caps. Never loop through all pages internally. Instead, accept `next_link` as an optional input and return it as an output so pagination can be driven by a loop step in the workflow builder.
30. **Applying `clean()` to individual output fields** — prefer wrapping `clean()` around the entire return dict so empty/None optional outputs (like pagination links) are stripped entirely rather than returned as empty strings
31. **Passing one service client into another** — never inject ClientA into ClientB for cross-cutting concerns. Actions orchestrate between clients; clients stay independent. If an action needs to call Graph API and then Bot Framework, the action coordinates both via `self.connection.client` and `self.connection.bot`.
32. **Putting retry/remediation logic in service clients** — catch-install-retry flows belong at the action level. Service clients should raise on failure and let the action decide what to do next.
33. **Nested double quotes in spec descriptions** — `description: 'Supports (e.g., "News")'` generates a schema.py with a syntax error. Rephrase to avoid nested quotes entirely.
34. **Large enums for vendor-managed lists** — URL categories, rule types, and similar lists change over time and include customer-defined values. Use a free-text string input and resolve names via the API at runtime instead of a hardcoded enum that goes stale.
35. **Using `...` (ellipsis) in abstract methods** — `@abstractmethod` is sufficient; the ellipsis body triggers pylint `unnecessary-ellipsis`. Leave the method body empty (just the docstring).
36. **f-strings without interpolation** — `f"some static text"` triggers pylint `f-string-without-interpolation`. Use a plain string literal instead.
37. **Using `conftest.py` for sys.path manipulation** — this repo's convention is `sys.path.append(os.path.abspath("../"))` at the top of each test file with tests run from the `unit_test/` directory. Don't add a `conftest.py`.
38. **Using `object` or `[]object` as output types** — define proper shared types in `plugin.spec.yaml` for structured API responses. Reuse types across actions that return the same entities (e.g., a `firewallRule` type shared by list/get/create/update actions).

## Updating Existing Plugins Checklist
- [ ] Read current `plugin.spec.yaml` first
- [ ] Determine correct semver bump
- [ ] Edit `plugin.spec.yaml` for schema changes
- [ ] Run `insight-plugin refresh`
- [ ] Update hand-written implementation files only
- [ ] Update/add unit tests (≥80% coverage)
- [ ] Update `version_history` in `plugin.spec.yaml`
- [ ] Run `prospector` on modified files (fix all issues before pushing)
- [ ] Run `insight-plugin validate`
- [ ] Verify no `[0]` access without empty-list guards
