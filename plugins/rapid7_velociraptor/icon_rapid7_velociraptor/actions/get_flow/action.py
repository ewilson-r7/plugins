import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.helper import clean

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import GetFlowInput, GetFlowOutput, Input, Output, Component


class GetFlow(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super().__init__(
            name="get_flow", description=Component.DESCRIPTION, input=GetFlowInput(), output=GetFlowOutput()
        )

    @auto_instrument
    def run(self, params={}):  # pylint: disable=dangerous-default-value
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        client_id = params.get(Input.CLIENT_ID)
        flow_id = params.get(Input.FLOW_ID)
        # END INPUT BINDING - DO NOT REMOVE

        flow = self.connection.client.get_flow(client_id, flow_id)

        return clean(
            {
                Output.FLOW: flow,
            }
        )
