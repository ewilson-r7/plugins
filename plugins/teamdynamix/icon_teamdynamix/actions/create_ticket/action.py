"""Create Ticket action for TeamDynamix InsightConnect plugin."""

import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.exceptions import PluginException

from .schema import CreateTicketInput, CreateTicketOutput, Input, Output, Component


class CreateTicket(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="create_ticket",
            description=Component.DESCRIPTION,
            input=CreateTicketInput(),
            output=CreateTicketOutput(),
        )

    def run(self, params={}):
        app_id = self.connection.client.app_id
        base_url = self.connection.client.base_url

        payload = {
            "TypeID": params.get(Input.TYPE_ID),
            "Title": params.get(Input.TITLE),
            "Description": params.get(Input.DESCRIPTION, ""),
        }

        # Optional fields — only include if provided
        if params.get(Input.FORM_ID):
            payload["FormID"] = params.get(Input.FORM_ID)
        if params.get(Input.ACCOUNT_ID):
            payload["AccountID"] = params.get(Input.ACCOUNT_ID)
        if params.get(Input.PRIORITY_ID):
            payload["PriorityID"] = params.get(Input.PRIORITY_ID)
        if params.get(Input.REQUESTOR_UID):
            payload["RequestorUID"] = params.get(Input.REQUESTOR_UID)
        if params.get(Input.RESPONSIBLE_GROUP_ID):
            payload["ResponsibleGroupID"] = params.get(Input.RESPONSIBLE_GROUP_ID)

        # Merge any additional custom fields
        payload.update(params.get(Input.ADDITIONAL_FIELDS, {}))

        response = self.connection.client.make_request(
            method="post",
            endpoint=f"/TDWebApi/api/{app_id}/tickets",
            payload=payload,
        )

        ticket_id = response.get("ID")
        if not ticket_id:
            raise PluginException(
                cause="TeamDynamix did not return a ticket ID.",
                assistance=f"Response: {response}",
            )

        ticket_url = f"{base_url}/TDClient/{app_id}/Requests/TicketDet?TicketID={ticket_id}"

        return {
            Output.TICKET_ID: ticket_id,
            Output.TICKET_URL: ticket_url,
            Output.SUCCESS: True,
        }
