import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.exceptions import PluginException

from .schema import (
    GetListOfBlockedDomainsInput,
    GetListOfBlockedDomainsOutput,
    Output,
    Component,
)

# Custom imports below
from ...util.utils import Utils


class GetListOfBlockedDomains(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="get_list_of_blocked_domains",
            description=Component.DESCRIPTION,
            input=GetListOfBlockedDomainsInput(),
            output=GetListOfBlockedDomainsOutput(),
        )

    def run(self, params={}):
        # pylint: disable=unused-argument
        out, error = self.connection.client.get_list_blocked_domains()
        if error and "Success" not in str(out):
            self.logger.error(f'Error output received: \n{error.decode("utf-8")}')
            if out:
                self.logger.error(f'Standard output received: \n{out.decode("utf-8")}')
            if isinstance(error, bytes):
                error = error.decode("utf-8")
            if isinstance(out, bytes):
                out = out.decode("utf-8")
            raise PluginException(
                cause="Powershell returned an error.",
                assistance="Please see the plugin logs for more information.",
                data=error,
            )
        return {Output.SPAM_POLICY: Utils.load_json(Utils.extract_data(out.decode("utf-8")), self.logger)}
