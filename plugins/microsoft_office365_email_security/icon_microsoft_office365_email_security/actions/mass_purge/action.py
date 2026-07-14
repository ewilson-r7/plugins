import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.exceptions import PluginException
from .schema import MassPurgeInput, MassPurgeOutput, Input, Output, Component


class MassPurge(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="mass_purge",
            description=Component.DESCRIPTION,
            input=MassPurgeInput(),
            output=MassPurgeOutput(),
        )

    def run(self, params={}):
        out, error = self.connection.client.mass_purge(
            params.get(Input.COMPLIANCE_SEARCH_NAME),
            params.get(Input.QUERY_TIMEOUT, 60),
        )
        if isinstance(error, bytes):
            error = error.decode("utf-8")
        if isinstance(out, bytes):
            out = out.decode("utf-8")
        if error and "Script Complete" not in str(out):
            self.logger.error(error)
            if out:
                self.logger.error(out)

            # This is a generic error message as there's a lot that can go wrong here.
            # Hopefully the above logs give us enough information to diagnose the problem
            raise PluginException(
                cause="Powershell returned an error.",
                assistance="Please see the plugin logs for more information.",
                data=error,
            )

        return {Output.SUCCESS: True}
