import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.helper import clean

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import GetClientLabelsInput, GetClientLabelsOutput, Input, Output, Component


class GetClientLabels(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super().__init__(
            name="get_client_labels",
            description=Component.DESCRIPTION,
            input=GetClientLabelsInput(),
            output=GetClientLabelsOutput(),
        )

    @auto_instrument
    def run(self, params={}):  # pylint: disable=dangerous-default-value
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        client_id = params.get(Input.CLIENT_ID)
        # END INPUT BINDING - DO NOT REMOVE

        labels = self.connection.client.get_client_labels(client_id)

        return clean(
            {
                Output.LABELS: labels if labels else [],
            }
        )
