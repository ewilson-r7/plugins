import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.exceptions import PluginException

from .schema import MessageTraceInput, MessageTraceOutput, Input, Output, Component
from icon_microsoft_office365_email_security.util.utils import Utils


class MessageTrace(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="message_trace",
            description=Component.DESCRIPTION,
            input=MessageTraceInput(),
            output=MessageTraceOutput(),
        )

    def run(self, params={}):
        out, error = self.connection.client.message_trace(
            params.get(Input.START_DATE).strip(),
            params.get(Input.END_DATE).strip(),
            params.get(Input.SENDER_ADDRESS).strip(),
        )
        if isinstance(error, bytes):
            error = error.decode("utf-8")
        if isinstance(out, bytes):
            out = out.decode("utf-8")
        if error and "Success" not in str(out):
            self.logger.error(f"Error output received: \n{error}")
            if out:
                self.logger.error(f"Standard output received: \n{out}")
            raise PluginException(
                cause="Powershell returned an error.",
                assistance="Please see the plugin logs for more information.",
                data=error,
            )
        out = Utils.extract_data(str(out))
        if not out:
            return {Output.MESSAGE_TRACES: []}
        else:
            return {Output.MESSAGE_TRACES: Utils.load_json(out, self.logger)}
