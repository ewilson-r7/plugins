import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.helper import clean

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import CreateHuntInput, CreateHuntOutput, Input, Output, Component


class CreateHunt(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super().__init__(
            name="create_hunt", description=Component.DESCRIPTION, input=CreateHuntInput(), output=CreateHuntOutput()
        )

    @auto_instrument
    def run(self, params={}):  # pylint: disable=dangerous-default-value
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        hunt_description = params.get(Input.HUNT_DESCRIPTION)
        artifacts = params.get(Input.ARTIFACTS)
        os_condition = params.get(Input.OS_CONDITION, "ALL")
        include_labels = params.get(Input.INCLUDE_LABELS)
        exclude_labels = params.get(Input.EXCLUDE_LABELS)
        client_limit = params.get(Input.CLIENT_LIMIT)
        expires = params.get(Input.EXPIRES)
        # END INPUT BINDING - DO NOT REMOVE

        payload = {
            "hunt_description": hunt_description,
            "start_request": {
                "artifacts": artifacts,
            },
        }

        condition = {}
        if os_condition and os_condition != "ALL":
            condition["os"] = {"os": os_condition}
        if include_labels:
            condition["labels"] = {"label": include_labels}
        if exclude_labels:
            condition["excluded_labels"] = {"label": exclude_labels}
        if condition:
            payload["condition"] = condition

        if client_limit:
            payload["client_limit"] = client_limit
        if expires:
            payload["expires"] = expires

        hunt_id = self.connection.client.create_hunt(payload)

        return clean(
            {
                Output.HUNT_ID: hunt_id,
            }
        )
