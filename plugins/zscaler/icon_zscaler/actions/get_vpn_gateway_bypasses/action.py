import insightconnect_plugin_runtime

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import GetVpnGatewayBypassesInput, GetVpnGatewayBypassesOutput, Output, Component

# Custom imports below
from icon_zscaler.util.helpers import clean_dict


class GetVpnGatewayBypasses(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
            name="get_vpn_gateway_bypasses",
            description=Component.DESCRIPTION,
            input=GetVpnGatewayBypassesInput(),
            output=GetVpnGatewayBypassesOutput(),
        )

    @auto_instrument
    def run(self, params={}):
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        # END INPUT BINDING - DO NOT REMOVE

        profiles = self.connection.zcc_client.get_vpn_gateway_bypasses()
        return clean_dict(
            {
                Output.PROFILES: profiles,
            }
        )
