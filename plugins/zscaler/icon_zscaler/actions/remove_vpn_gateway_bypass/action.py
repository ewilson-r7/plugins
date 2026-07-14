import insightconnect_plugin_runtime

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import RemoveVpnGatewayBypassInput, RemoveVpnGatewayBypassOutput, Input, Output, Component

# Custom imports below
from icon_zscaler.util.helpers import clean_dict


class RemoveVpnGatewayBypass(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
            name="remove_vpn_gateway_bypass",
            description=Component.DESCRIPTION,
            input=RemoveVpnGatewayBypassInput(),
            output=RemoveVpnGatewayBypassOutput(),
        )

    @auto_instrument
    def run(self, params={}):
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        entry = params.get(Input.ENTRY)
        profile_id = params.get(Input.PROFILE_ID)
        # END INPUT BINDING - DO NOT REMOVE

        result = self.connection.zcc_client.remove_vpn_gateway_bypass(profile_id, entry)
        return clean_dict(
            {
                Output.SUCCESS: result.get("success"),
                Output.VPN_GATEWAYS: result.get("vpn_gateways", []),
            }
        )
