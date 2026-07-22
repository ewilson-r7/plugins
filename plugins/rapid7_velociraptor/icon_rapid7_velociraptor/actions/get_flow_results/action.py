import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.helper import clean

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import GetFlowResultsInput, GetFlowResultsOutput, Input, Output, Component


class GetFlowResults(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super().__init__(
            name="get_flow_results",
            description=Component.DESCRIPTION,
            input=GetFlowResultsInput(),
            output=GetFlowResultsOutput(),
        )

    @auto_instrument
    def run(self, params={}):  # pylint: disable=dangerous-default-value
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        client_id = params.get(Input.CLIENT_ID)
        flow_id = params.get(Input.FLOW_ID)
        artifact = params.get(Input.ARTIFACT)
        # END INPUT BINDING - DO NOT REMOVE

        response = self.connection.client.get_flow_results(client_id, flow_id, artifact)

        results = response.get("data", []) if isinstance(response, dict) else response

        return clean(
            {
                Output.RESULTS: results if results else [],
                Output.COUNT: len(results) if results else 0,
            }
        )
