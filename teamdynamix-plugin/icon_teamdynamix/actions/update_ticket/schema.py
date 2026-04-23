import insightconnect_plugin_runtime.action


class Component:
    DESCRIPTION = "Update an existing TeamDynamix ticket"


class Input:
    TICKET_ID = "ticket_id"
    TITLE = "title"
    DESCRIPTION = "description"
    STATUS_ID = "status_id"
    PRIORITY_ID = "priority_id"
    ADDITIONAL_FIELDS = "additional_fields"


class Output:
    SUCCESS = "success"


class UpdateTicketInput(insightconnect_plugin_runtime.action.Input):
    schema = {
        "type": "object",
        "title": "Variables",
        "properties": {
            "ticket_id": {"type": "integer", "title": "Ticket ID", "order": 1},
            "title": {"type": "string", "title": "Title", "order": 2},
            "description": {"type": "string", "title": "Description", "order": 3},
            "status_id": {"type": "integer", "title": "Status ID", "order": 4},
            "priority_id": {"type": "integer", "title": "Priority ID", "order": 5},
            "additional_fields": {"type": "object", "title": "Additional Fields", "order": 6},
        },
        "required": ["ticket_id"],
    }


class UpdateTicketOutput(insightconnect_plugin_runtime.action.Output):
    schema = {
        "type": "object",
        "title": "Variables",
        "properties": {
            "success": {"type": "boolean", "title": "Success", "order": 1},
        },
        "required": ["success"],
    }
