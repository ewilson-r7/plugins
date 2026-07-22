import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.helper import clean

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import ListArtifactsInput, ListArtifactsOutput, Input, Output, Component


class ListArtifacts(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super().__init__(
            name="list_artifacts",
            description=Component.DESCRIPTION,
            input=ListArtifactsInput(),
            output=ListArtifactsOutput(),
        )

    @auto_instrument
    def run(self, params={}):  # pylint: disable=dangerous-default-value
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        artifact_type = params.get(Input.ARTIFACT_TYPE, "ALL")
        os_filter = params.get(Input.OS, "ALL")
        include_built_in = params.get(Input.INCLUDE_BUILT_IN, True)
        include_custom = params.get(Input.INCLUDE_CUSTOM, True)
        # END INPUT BINDING - DO NOT REMOVE

        artifacts = self.connection.client.list_artifacts(
            artifact_type=artifact_type,
            os_filter=os_filter,
            include_built_in=include_built_in,
            include_custom=include_custom,
        )

        return clean(
            {
                Output.ARTIFACTS: artifacts if artifacts else [],
                Output.COUNT: len(artifacts) if artifacts else 0,
            }
        )
