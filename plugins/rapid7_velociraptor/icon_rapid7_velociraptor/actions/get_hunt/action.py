import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.helper import clean

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import GetHuntInput, GetHuntOutput, Input, Output, Component


class GetHunt(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super().__init__(
            name="get_hunt", description=Component.DESCRIPTION, input=GetHuntInput(), output=GetHuntOutput()
        )

    @auto_instrument
    def run(self, params={}):  # pylint: disable=dangerous-default-value
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        hunt_id = params.get(Input.HUNT_ID)
        # END INPUT BINDING - DO NOT REMOVE

        hunt_details = self.connection.client.get_hunt(hunt_id)

        return clean(
            {
                Output.HUNT_DETAILS: hunt_details,
            }
        )
