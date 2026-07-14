import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.exceptions import PluginException
from .schema import (
    BlockSenderTransportRuleInput,
    BlockSenderTransportRuleOutput,
    Input,
    Output,
    Component,
)


class BlockSenderTransportRule(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super(self.__class__, self).__init__(
            name="block_sender_transport_rule",
            description=Component.DESCRIPTION,
            input=BlockSenderTransportRuleInput(),
            output=BlockSenderTransportRuleOutput(),
        )

    def run(self, params={}):
        out, error = self.connection.client.block_sender_transport_rule(
            params.get(Input.DOMAIN_OR_EMAIL_TO_BLOCK),
            params.get(Input.TRANSPORT_RULE_NAME),
        )
        if isinstance(error, bytes):
            error = error.decode("utf-8")
        if isinstance(out, bytes):
            out = out.decode("utf-8")
        if error and "Blocking finished" not in out:
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

        return {Output.RESULT: "Success"}
