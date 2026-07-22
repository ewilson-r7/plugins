import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.helper import clean

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import ListFlowsInput, ListFlowsOutput, Input, Output, Component


class ListFlows(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super().__init__(
            name="list_flows", description=Component.DESCRIPTION, input=ListFlowsInput(), output=ListFlowsOutput()
        )

    @auto_instrument
    def run(self, params={}):  # pylint: disable=dangerous-default-value
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        client_id = params.get(Input.CLIENT_ID)
        creator = params.get(Input.CREATOR)
        limit = params.get(Input.LIMIT, 50)
        # END INPUT BINDING - DO NOT REMOVE

        response = self.connection.client.list_flows(
            client_id=client_id,
            creator=creator,
            limit=limit,
        )

        flows = response.get("data", []) if isinstance(response, dict) else response

        return clean(
            {
                Output.FLOWS: flows,
                Output.COUNT: len(flows) if flows else 0,
            }
        )
