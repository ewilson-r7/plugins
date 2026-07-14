"""Search Tickets action for TeamDynamix InsightConnect plugin."""

import insightconnect_plugin_runtime
from .schema import SearchTicketsInput, SearchTicketsOutput, Input, Output, Component


class SearchTickets(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="search_tickets",
            description=Component.DESCRIPTION,
            input=SearchTicketsInput(),
            output=SearchTicketsOutput(),
        )

    def run(self, params={}):
        app_id = self.connection.client.app_id

        search_payload = {
            "MaxResults": params.get(Input.MAX_RESULTS, 25),
        }

        if params.get(Input.SEARCH_TEXT):
            search_payload["SearchText"] = params.get(Input.SEARCH_TEXT)
        if params.get(Input.STATUS_ID):
            search_payload["StatusIDs"] = [params.get(Input.STATUS_ID)]

        response = self.connection.client.make_request(
            method="post",
            endpoint=f"/TDWebApi/api/{app_id}/tickets/search",
            payload=search_payload,
        )

        tickets = response if isinstance(response, list) else []

        return {
            Output.TICKETS: tickets,
            Output.COUNT: len(tickets),
        }
