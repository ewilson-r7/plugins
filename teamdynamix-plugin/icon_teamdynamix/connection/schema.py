"""Auto-generated schema stubs for TeamDynamix connection."""
import insightconnect_plugin_runtime.action


class Input:
    BASE_URL = "base_url"
    BEID = "beid"
    WEB_SERVICES_KEY = "web_services_key"
    APP_ID = "app_id"


class ConnectionSchema(insightconnect_plugin_runtime.action.Input):
    schema = {
        "type": "object",
        "title": "Variables",
        "properties": {
            "base_url": {"type": "string", "title": "Base URL", "order": 1},
            "beid": {"type": "string", "title": "BEID", "order": 2},
            "web_services_key": {
                "$ref": "#/definitions/credential_secret_key",
                "title": "Web Services Key",
                "order": 3,
            },
            "app_id": {"type": "integer", "title": "Application ID", "order": 4},
        },
        "required": ["base_url", "beid", "web_services_key", "app_id"],
        "definitions": {
            "credential_secret_key": {
                "id": "credential_secret_key",
                "type": "object",
                "title": "Credential: Secret Key",
                "properties": {"secretKey": {"type": "string", "title": "Secret Key"}},
                "required": ["secretKey"],
            }
        },
    }
