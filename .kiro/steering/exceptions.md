---
inclusion: fileMatch
fileMatchPattern: "plugins/**/*.py"
---
# PluginException & Error Handling

## Available Presets (verify against the installed SDK)
<!-- The latest SDK version is the top entry of komand-plugin-sdk-python/README.md `## Changelog`. Do not hardcode. -->
`NOT_FOUND`, `UNAUTHORIZED`, `INVALID_CREDENTIALS`, `RATE_LIMIT`, `SERVER_ERROR`,
`SERVICE_UNAVAILABLE`, `TIMEOUT`, `INVALID_JSON`, `BAD_REQUEST`, `CONNECTION_ERROR`,
`API_KEY`, `USERNAME_PASSWORD`, `CONFLICT`, `METHOD_NOT_ALLOWED`, `REDIRECT_ERROR`, `UNKNOWN`

## Usage
```python
# Preset (recommended for standard HTTP errors):
raise PluginException(preset=PluginException.Preset.NOT_FOUND)

# Custom (when preset isn't specific enough):
raise PluginException(cause="Device not found.", assistance="Verify the device ID.", data=response.text)

# IMPORTANT: preset + custom cause/assistance = custom is SILENTLY IGNORED
# Omit preset entirely if you need a custom message
```

## ConnectionTestException
Used exclusively in `Connection.test()` and `test_task()`:
```python
except PluginException as error:
    raise ConnectionTestException(cause=error.cause, assistance=error.assistance, data=error.data)
```

Keep connection test logic minimal — push error handling into client `test()` methods so
`Connection.test()` is a single try-except:
```python
def test(self):
    try:
        self.client.test()
        self.bot.test()
    except PluginException as error:
        raise ConnectionTestException(
            cause=error.cause, assistance=error.assistance, data=error.data
        ) from error
    return {"success": True}
```

## Rules
- Never raise raw `Exception`
- Provide actionable `assistance` messages
- Include `data` for debugging — pass the error object directly (`data=error`), not `data=str(error)`.
  The SDK handles `str()` conversion internally via `insightconnect_plugin_runtime.exceptions`
- For response-based errors, use `data=response.text` (already a string)
- Use presets for standard HTTP errors; custom for domain-specific errors
- Note: `RATE_LIMIT` not `RATE_LIMITED`
- Do not chain `from error` when re-raising the same PluginException — only use it when wrapping a different exception type
