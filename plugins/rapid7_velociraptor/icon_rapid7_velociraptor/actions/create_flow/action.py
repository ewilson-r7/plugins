import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.helper import clean

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import CreateFlowInput, CreateFlowOutput, Input, Output, Component


class CreateFlow(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super().__init__(
            name="create_flow", description=Component.DESCRIPTION, input=CreateFlowInput(), output=CreateFlowOutput()
        )

    @auto_instrument
    def run(self, params={}):  # pylint: disable=dangerous-default-value
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        client_id = params.get(Input.CLIENT_ID)
        artifacts = params.get(Input.ARTIFACTS)
        urgent = params.get(Input.URGENT, False)
        timeout = params.get(Input.TIMEOUT, 600)
        max_rows = params.get(Input.MAX_ROWS)
        # END INPUT BINDING - DO NOT REMOVE

        payload = {
            "artifacts": artifacts,
            "urgent": urgent,
            "timeout": timeout,
        }
        if max_rows:
            payload["max_rows"] = max_rows

        flow_id = self.connection.client.create_flow(client_id, payload)

        return clean(
            {
                Output.FLOW_ID: flow_id,
            }
        )
