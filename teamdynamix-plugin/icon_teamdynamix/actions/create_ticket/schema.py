"""Schema for Create Ticket action."""
import insightconnect_plugin_runtime.action


class Component:
    DESCRIPTION = "Create a new ticket in TeamDynamix"


class Input:
    TITLE = "title"
    DESCRIPTION = "description"
    TYPE_ID = "type_id"
    FORM_ID = "form_id"
    ACCOUNT_ID = "account_id"
    PRIORITY_ID = "priority_id"
    REQUESTOR_UID = "requestor_uid"
    RESPONSIBLE_GROUP_ID = "responsible_group_id"
    ADDITIONAL_FIELDS = "additional_fields"


class Output:
    TICKET_ID = "ticket_id"
    TICKET_URL = "ticket_url"
    SUCCESS = "success"


class CreateTicketInput(insightconnect_plugin_runtime.action.Input):
    schema = {
        "type": "object",
        "title": "Variables",
        "properties": {
            "title": {"type": "string", "title": "Title", "order": 1},
            "description": {"type": "string", "title": "Description", "order": 2},
            "type_id": {"type": "integer", "title": "Type ID", "order": 3},
            "form_id": {"type": "integer", "title": "Form ID", "order": 4},
            "account_id": {"type": "integer", "title": "Account/Department ID", "order": 5},
            "priority_id": {"type": "integer", "title": "Priority ID", "order": 6},
            "requestor_uid": {"type": "string", "title": "Requestor UID", "order": 7},
            "responsible_group_id": {"type": "integer", "title": "Responsible Group ID", "order": 8},
            "additional_fields": {"type": "object", "title": "Additional Fields", "order": 9},
        },
        "required": ["title", "type_id"],
    }


class CreateTicketOutput(insightconnect_plugin_runtime.action.Output):
    schema = {
        "type": "object",
        "title": "Variables",
        "properties": {
            "ticket_id": {"type": "integer", "title": "Ticket ID", "order": 1},
            "ticket_url": {"type": "string", "title": "Ticket URL", "order": 2},
            "success": {"type": "boolean", "title": "Success", "order": 3},
        },
        "required": ["ticket_id", "ticket_url", "success"],
    }
