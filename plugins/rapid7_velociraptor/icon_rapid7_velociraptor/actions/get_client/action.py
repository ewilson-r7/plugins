import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.helper import clean

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import GetClientInput, GetClientOutput, Input, Output, Component


class GetClient(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super().__init__(
            name="get_client", description=Component.DESCRIPTION, input=GetClientInput(), output=GetClientOutput()
        )

    @auto_instrument
    def run(self, params={}):  # pylint: disable=dangerous-default-value
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        client_id = params.get(Input.CLIENT_ID)
        # END INPUT BINDING - DO NOT REMOVE

        client = self.connection.client.get_client(client_id)

        return clean(
            {
                Output.CLIENT: client,
            }
        )
