"""Update Ticket action for TeamDynamix InsightConnect plugin."""
import insightconnect_plugin_runtime
from .schema import UpdateTicketInput, UpdateTicketOutput, Input, Output, Component


class UpdateTicket(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="update_ticket",
            description=Component.DESCRIPTION,
            input=UpdateTicketInput(),
            output=UpdateTicketOutput(),
        )

    def run(self, params={}):
        app_id = self.connection.client.app_id
        ticket_id = params.get(Input.TICKET_ID)

        # First fetch the current ticket so we can PATCH only changed fields
        current = self.connection.client.make_request(
            method="get",
            endpoint=f"/TDWebApi/api/{app_id}/tickets/{ticket_id}",
        )

        payload = dict(current)  # Start from current state

        if params.get(Input.TITLE):
            payload["Title"] = params.get(Input.TITLE)
        if params.get(Input.DESCRIPTION):
            payload["Description"] = params.get(Input.DESCRIPTION)
        if params.get(Input.STATUS_ID):
            payload["StatusID"] = params.get(Input.STATUS_ID)
        if params.get(Input.PRIORITY_ID):
            payload["PriorityID"] = params.get(Input.PRIORITY_ID)

        payload.update(params.get(Input.ADDITIONAL_FIELDS, {}))

        self.connection.client.make_request(
            method="post",
            endpoint=f"/TDWebApi/api/{app_id}/tickets/{ticket_id}",
            payload=payload,
        )

        return {Output.SUCCESS: True}
