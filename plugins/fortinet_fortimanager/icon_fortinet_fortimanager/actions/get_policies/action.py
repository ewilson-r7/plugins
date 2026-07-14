import insightconnect_plugin_runtime

from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import GetPoliciesInput, GetPoliciesOutput, Input, Output, Component

# Custom imports below
from icon_fortinet_fortimanager.util.helpers import Helpers


class GetPolicies(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
            name="get_policies", description=Component.DESCRIPTION, input=GetPoliciesInput(), output=GetPoliciesOutput()
        )

    @auto_instrument
    def run(self, params={}):
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        adom = params.get(Input.ADOM)
        name_filter = params.get(Input.NAME_FILTER)
        policy_package = params.get(Input.POLICY_PACKAGE)
        # END INPUT BINDING - DO NOT REMOVE

        # Resolve ADOM: input override or connection default
        adom = adom or self.connection.default_adom

        # Fetch policies from the specified package (API raises PluginException if package/ADOM not found)
        policies = self.connection.api.get_policies(adom, policy_package)

        # Apply optional name filter (case-insensitive exact match)
        filters = {"name": name_filter or ""}
        policies = Helpers.filter_objects(policies, filters)

        return {Output.POLICIES: policies}
