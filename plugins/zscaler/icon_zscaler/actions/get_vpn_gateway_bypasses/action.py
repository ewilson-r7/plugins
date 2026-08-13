import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import GetVpnGatewayBypassesInput, GetVpnGatewayBypassesOutput, Input, Output, Component

# Custom imports below
from icon_zscaler.util.helpers import clean_dict


class GetVpnGatewayBypasses(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super().__init__(
            name="get_vpn_gateway_bypasses",
            description=Component.DESCRIPTION,
            input=GetVpnGatewayBypassesInput(),
            output=GetVpnGatewayBypassesOutput(),
        )

    @auto_instrument
    def run(self, params={}):
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        profile_id = params.get(Input.PROFILE_ID)
        search = params.get(Input.SEARCH)
        # END INPUT BINDING - DO NOT REMOVE

        profiles = self.connection.zcc_client.get_vpn_gateway_bypasses(profile_id=profile_id or None)

        # Client-side name filter — the API does not support server-side search by name
        if search and not profile_id:
            profiles = [profile for profile in profiles if search.lower() in profile.get("profile_name", "").lower()]

        return clean_dict({Output.PROFILES: profiles})
