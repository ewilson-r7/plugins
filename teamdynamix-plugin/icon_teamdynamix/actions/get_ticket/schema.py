import insightconnect_plugin_runtime.action


class Component:
    DESCRIPTION = "Retrieve a TeamDynamix ticket by its ID"


class Input:
    TICKET_ID = "ticket_id"


class Output:
    TICKET = "ticket"
    TITLE = "title"
    STATUS = "status"
    TICKET_ID = "ticket_id"


class GetTicketInput(insightconnect_plugin_runtime.action.Input):
    schema = {
        "type": "object",
        "title": "Variables",
        "properties": {
            "ticket_id": {"type": "integer", "title": "Ticket ID", "order": 1},
        },
        "required": ["ticket_id"],
    }


class GetTicketOutput(insightconnect_plugin_runtime.action.Output):
    schema = {
        "type": "object",
        "title": "Variables",
        "properties": {
            "ticket": {"type": "object", "title": "Ticket", "order": 1},
            "title": {"type": "string", "title": "Title", "order": 2},
            "status": {"type": "string", "title": "Status", "order": 3},
            "ticket_id": {"type": "integer", "title": "Ticket ID", "order": 4},
        },
        "required": ["ticket"],
    }
