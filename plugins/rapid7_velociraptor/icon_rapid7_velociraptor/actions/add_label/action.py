import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.helper import clean

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import AddLabelInput, AddLabelOutput, Input, Output, Component


class AddLabel(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super().__init__(
            name="add_label", description=Component.DESCRIPTION, input=AddLabelInput(), output=AddLabelOutput()
        )

    @auto_instrument
    def run(self, params={}):  # pylint: disable=dangerous-default-value
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        client_id = params.get(Input.CLIENT_ID)
        label = params.get(Input.LABEL)
        # END INPUT BINDING - DO NOT REMOVE

        response = self.connection.client.add_label(client_id, label)

        return clean(
            {
                Output.LABEL_RESPONSE: response,
            }
        )
