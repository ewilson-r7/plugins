import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.exceptions import PluginException

from .schema import (
    UpdateListOfBlockedDomainsInput,
    UpdateListOfBlockedDomainsOutput,
    Input,
    Output,
    Component,
)

# Custom imports below
from ...util.utils import Utils


class UpdateListOfBlockedDomains(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="update_list_of_blocked_domains",
            description=Component.DESCRIPTION,
            input=UpdateListOfBlockedDomainsInput(),
            output=UpdateListOfBlockedDomainsOutput(),
        )

    def run(self, params={}):
        Utils.validate_domains(params.get(Input.DOMAINS))
        out, error = self.connection.client.update_blocked_list(
            params.get(Input.OPERATION),
            params.get(Input.IDENTITY),
            params.get(Input.DOMAINS),
        )
        success = False
        if isinstance(error, bytes):
            error = error.decode("utf-8")
        if isinstance(out, bytes):
            out = out.decode("utf-8")
        if "Success" in out and not error:
            success = True
        else:
            if "Timeout was exceeded." in str(error):
                raise PluginException(
                    cause="Timeout Error.",
                    assistance="The Update List of Blocked Domains action may have succeeded, however, the timeout was reached.",
                    data=f"\n\nstderr:\n{error}\n\nstdout:\n{out}\n\n",
                )
            elif error:
                self.logger.error(f"stderr:\n\n{error}\n\n")
                self.logger.error(f"stdout:\n\n{out}\n\n")
                raise PluginException(
                    cause="PowerShell returned an error.",
                    assistance="Please see the plugin logs for more information.",
                    data=f"\n\nstderr:\n{error}\n\nstdout:\n{out}\n\n",
                )
        return {Output.SUCCESS: success}
