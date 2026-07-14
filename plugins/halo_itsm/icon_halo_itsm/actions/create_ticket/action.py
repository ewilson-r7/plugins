import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.telemetry import auto_instrument
from .schema import CreateTicketInput, CreateTicketOutput, Input, Output, Component
from icon_halo_itsm.util.helpers import clean_ticket


class CreateTicket(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
            name="create_ticket",
            description=Component.DESCRIPTION,
            input=CreateTicketInput(),
            output=CreateTicketOutput(),
        )

    @auto_instrument
    def run(self, params={}):
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        agent_id = params.get(Input.AGENT_ID)
        category_1 = params.get(Input.CATEGORY_1)
        category_2 = params.get(Input.CATEGORY_2)
        client_id = params.get(Input.CLIENT_ID)
        details = params.get(Input.DETAILS)
        impact = params.get(Input.IMPACT)
        priority_id = params.get(Input.PRIORITY_ID)
        site_id = params.get(Input.SITE_ID)
        status_id = params.get(Input.STATUS_ID)
        summary = params.get(Input.SUMMARY)
        tickettype_id = params.get(Input.TICKETTYPE_ID)
        urgency = params.get(Input.URGENCY)
        user_id = params.get(Input.USER_ID)
        # END INPUT BINDING - DO NOT REMOVE

        ticket_data = {"summary": summary, "tickettype_id": tickettype_id}

        if details:
            ticket_data["details"] = details
        if agent_id:
            ticket_data["agent_id"] = agent_id
        if category_1:
            ticket_data["category_1"] = category_1
        if category_2:
            ticket_data["category_2"] = category_2
        if client_id:
            ticket_data["client_id"] = client_id
        if impact:
            ticket_data["impact"] = impact
        if priority_id:
            ticket_data["priority_id"] = priority_id
        if site_id:
            ticket_data["site_id"] = site_id
        if status_id:
            ticket_data["status_id"] = status_id
        if urgency:
            ticket_data["urgency"] = urgency
        if user_id:
            ticket_data["user_id"] = user_id

        self.logger.info(f"Creating ticket with summary: {summary}")
        result = self.connection.client.create_ticket(ticket_data)

        return {Output.TICKET: clean_ticket(result)}
