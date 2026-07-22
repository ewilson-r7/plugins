import insightconnect_plugin_runtime

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import RemoveLabelInput, RemoveLabelOutput, Input, Output, Component


class RemoveLabel(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super().__init__(
            name="remove_label", description=Component.DESCRIPTION, input=RemoveLabelInput(), output=RemoveLabelOutput()
        )

    @auto_instrument
    def run(self, params={}):  # pylint: disable=dangerous-default-value
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        client_id = params.get(Input.CLIENT_ID)
        label = params.get(Input.LABEL)
        # END INPUT BINDING - DO NOT REMOVE

        self.connection.client.remove_label(client_id, label)

        return {
            Output.SUCCESS: True,
        }
