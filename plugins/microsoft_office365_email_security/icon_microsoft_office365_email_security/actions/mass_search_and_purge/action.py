import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.exceptions import PluginException
from .schema import (
    MassSearchAndPurgeInput,
    MassSearchAndPurgeOutput,
    Input,
    Output,
    Component,
)


class MassSearchAndPurge(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="mass_search_and_purge",
            description=Component.DESCRIPTION,
            input=MassSearchAndPurgeInput(),
            output=MassSearchAndPurgeOutput(),
        )

    def run(self, params={}):
        compliance_search_name = params.get(Input.COMPLIANCE_SEARCH_NAME)
        out, error = self.connection.client.mass_search_and_purge(
            compliance_search_name,
            params.get(Input.CONTENT_MATCH_QUERY),
            params.get(Input.QUERY_TIMEOUT, 60),
            params.get(Input.DELETE_ITEMS, False),
        )
        success = False
        if isinstance(error, bytes):
            error = error.decode("utf-8")
        if isinstance(out, bytes):
            out = out.decode("utf-8")
        if "Success!" in out:
            success = True
        else:
            if "Timeout was exceeded." in str(error):
                raise PluginException(
                    cause="Timeout Error.",
                    assistance=f"The Mass Search and Purge action may have succeeded, however, the timeout was reached. "
                    f"Check compliance center to see if '{compliance_search_name}' is still running or has results.",
                    data=f"\n\nstderr:\n{error}\n\nstdout:\n{out}\n\n",
                )

            raise PluginException(
                cause="PowerShell returned an error.",
                assistance="Please see the plugin logs for more information.",
                data=f"\n\nstderr:\n{error}\n\nstdout:\n{out}\n\n",
            )

        if error:
            self.logger.error(f"\n\n{error}\n\n")
            if out:
                self.logger.error(f"\n\n{out}\n\n")

        return {Output.SUCCESS: success}
