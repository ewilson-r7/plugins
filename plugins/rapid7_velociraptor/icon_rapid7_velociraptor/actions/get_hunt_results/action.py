import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.helper import clean

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import GetHuntResultsInput, GetHuntResultsOutput, Input, Output, Component


class GetHuntResults(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super().__init__(
            name="get_hunt_results",
            description=Component.DESCRIPTION,
            input=GetHuntResultsInput(),
            output=GetHuntResultsOutput(),
        )

    @auto_instrument
    def run(self, params={}):  # pylint: disable=dangerous-default-value
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        hunt_id = params.get(Input.HUNT_ID)
        limit = params.get(Input.LIMIT, 100)
        # END INPUT BINDING - DO NOT REMOVE

        response = self.connection.client.get_hunt_results(hunt_id, limit=limit)

        results = response.get("data", []) if isinstance(response, dict) else response

        return clean(
            {
                Output.RESULTS: results if results else [],
                Output.COUNT: len(results) if results else 0,
            }
        )
