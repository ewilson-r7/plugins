import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.helper import clean

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import ListHuntsInput, ListHuntsOutput, Input, Output, Component


class ListHunts(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super().__init__(
            name="list_hunts", description=Component.DESCRIPTION, input=ListHuntsInput(), output=ListHuntsOutput()
        )

    @auto_instrument
    def run(self, params={}):  # pylint: disable=dangerous-default-value
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        state = params.get(Input.STATE)
        limit = params.get(Input.LIMIT, 50)
        # END INPUT BINDING - DO NOT REMOVE

        response = self.connection.client.list_hunts(state=state, limit=limit)

        hunts = response.get("data", []) if isinstance(response, dict) else response

        return clean(
            {
                Output.HUNTS: hunts,
                Output.COUNT: len(hunts) if hunts else 0,
            }
        )
