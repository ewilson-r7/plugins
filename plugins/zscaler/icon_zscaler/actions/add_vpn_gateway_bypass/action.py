import insightconnect_plugin_runtime
from .schema import AddVpnGatewayBypassInput, AddVpnGatewayBypassOutput, Input, Output, Component

# Custom imports below
from icon_zscaler.util.helpers import clean_dict


class AddVpnGatewayBypass(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super().__init__(
            name="add_vpn_gateway_bypass",
            description=Component.DESCRIPTION,
            input=AddVpnGatewayBypassInput(),
            output=AddVpnGatewayBypassOutput(),
        )

    def run(self, params={}):
        profile_id = params.get(Input.PROFILE_ID)
        entry = params.get(Input.ENTRY)

        result = self.connection.zcc_client.add_vpn_gateway_bypass(profile_id, entry)
        return clean_dict(
            {
                Output.SUCCESS: result.get("success"),
                Output.VPN_GATEWAYS: result.get("vpn_gateways", []),
            }
        )
