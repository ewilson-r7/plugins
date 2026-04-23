import insightconnect_plugin_runtime.action


class Component:
    DESCRIPTION = "Search for tickets in TeamDynamix"


class Input:
    SEARCH_TEXT = "search_text"
    STATUS_ID = "status_id"
    MAX_RESULTS = "max_results"


class Output:
    TICKETS = "tickets"
    COUNT = "count"


class SearchTicketsInput(insightconnect_plugin_runtime.action.Input):
    schema = {
        "type": "object",
        "title": "Variables",
        "properties": {
            "search_text": {"type": "string", "title": "Search Text", "order": 1},
            "status_id": {"type": "integer", "title": "Status ID", "order": 2},
            "max_results": {"type": "integer", "title": "Max Results", "default": 25, "order": 3},
        },
        "required": [],
    }


class SearchTicketsOutput(insightconnect_plugin_runtime.action.Output):
    schema = {
        "type": "object",
        "title": "Variables",
        "properties": {
            "tickets": {
                "type": "array",
                "items": {"type": "object"},
                "title": "Tickets",
                "order": 1,
            },
            "count": {"type": "integer", "title": "Count", "order": 2},
        },
        "required": ["tickets", "count"],
    }
