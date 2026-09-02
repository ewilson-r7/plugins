# Refactor Plugin Authentication

Guide for migrating a plugin from user-delegated auth (ROPC/password grant) to app-only auth (client_credentials) with optional Bot Framework for messaging.

## When to Use
- Plugin currently requires username/password credentials
- Customer wants to eliminate service accounts (MFA, licensing, security concerns)
- Vendor API supports application permissions

## Investigation Steps

### 1. Assess Current Auth Model
- Read `connection.py` — identify the OAuth grant type
- Check if it uses `grant_type: password` (ROPC) or `client_credentials`
- Identify which API endpoints require delegated vs application permissions

### 2. Check Vendor API Permission Model
- For Microsoft Graph: check each endpoint's permission table at learn.microsoft.com
- Identify which operations support Application permissions
- Identify which operations ONLY support Delegated permissions (these need alternatives)

### 3. Determine Alternatives for Delegated-Only Operations
- **Microsoft Teams messaging**: Use Bot Framework REST API
- **Other vendors**: Check for webhook, service account, or API key alternatives
- Document any operations that cannot be migrated

## Implementation Pattern

### Base Client (util/base_client.py)
```python
class BaseClient:
    def __init__(self, app_id, app_secret, tenant_id, auth_url, scope, logger):
        # OAuth2 client_credentials flow
        # Shared: _authenticate(), _get_auth_headers(), _call_api(), _raise_for_status()
```

### Service-Specific Clients
```python
class GraphApiClient(BaseClient):
    # scope: https://graph.microsoft.com/.default
    # Domain methods: get_teams(), get_channels(), get_user_info(), etc.

class BotService(BaseClient):
    # scope: https://api.botframework.com/.default
    # Methods: send_channel_message(), send_chat_message()
```

### Connection (simplified)
```python
class Connection:
    def connect(self, params):
        # Just instantiate clients — no auth logic here
        self.client = GraphApiClient(app_id, app_secret, tenant_id, ...)
        self.bot = BotService(app_id, app_secret, tenant_id, ...)

    def test(self):
        self.client.authenticate()
        self.client._make_request("GET", "/v1.0/organization")
```

## Key Decisions

### Token Endpoint
- **Multi-tenant apps**: `https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token`
- **Single-tenant bots**: Same — use the app's own tenant ID, NOT `botframework.com`
- **Scope for Graph**: `https://graph.microsoft.com/.default`
- **Scope for Bot Framework**: `https://api.botframework.com/.default`

### Breaking Changes (Major version bump)
- Removing `username_password` from connection = breaking change
- Removing inputs from actions (e.g., `username` from get_message_in_chat) = breaking change
- Changing auth flow = connection_version bump

### Bot Framework Setup Requirements
- Azure Bot resource linked to the same App Registration
- Bot must be installed in target teams (via Teams app manifest)
- Messages appear as bot identity, not a user

## Checklist
- [ ] Remove username_password from connection spec
- [ ] Bump connection_version
- [ ] Major version bump (breaking change)
- [ ] Migrate all endpoints from /beta to /v1.0
- [ ] Remove tenant_id from Graph API resource paths
- [ ] Add guards for empty list access
- [ ] Update unit tests to mock at client level
- [ ] Create setup documentation for customers
- [ ] Test with `insight-plugin run` against live environment
