import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.exceptions import PluginException
from insightconnect_plugin_runtime.telemetry import auto_instrument

from .schema import InstallPolicyPackageInput, InstallPolicyPackageOutput, Input, Output, Component

# Custom imports below


class InstallPolicyPackage(insightconnect_plugin_runtime.Action):

    def __init__(self):
        super(self.__class__, self).__init__(
            name="install_policy_package",
            description=Component.DESCRIPTION,
            input=InstallPolicyPackageInput(),
            output=InstallPolicyPackageOutput(),
        )

    @auto_instrument
    def run(self, params={}):
        # START INPUT BINDING - DO NOT REMOVE - ANY INPUTS BELOW WILL UPDATE WITH YOUR PLUGIN SPEC AFTER REGENERATION
        adom = params.get(Input.ADOM)
        policy_package = params.get(Input.POLICY_PACKAGE)
        target_device_groups = params.get(Input.TARGET_DEVICE_GROUPS)
        target_devices = params.get(Input.TARGET_DEVICES)
        # END INPUT BINDING - DO NOT REMOVE

        # Resolve ADOM: use input override or fall back to connection default
        adom = adom or self.connection.default_adom

        # Normalize optional lists
        target_devices = target_devices or []
        target_device_groups = target_device_groups or []

        # Validate at least one target is provided
        if not target_devices and not target_device_groups:
            raise PluginException(
                cause="No target devices or device groups provided.",
                assistance="Provide at least one target device or target device group for the policy installation.",
            )

        # Build target scope list
        targets = []
        for device in target_devices:
            targets.append({"name": device, "vdom": "root"})
        for group in target_device_groups:
            targets.append({"name": group, "vdom": "root"})

        # Install policy package (API raises PluginException if package/ADOM/device not found)
        task_id = self.connection.api.install_policy_package(adom, policy_package, targets)

        return {Output.TASK_ID: task_id}
