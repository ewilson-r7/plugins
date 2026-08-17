import insightconnect_plugin_runtime
from .schema import GetEnrolledDevicesInput, GetEnrolledDevicesOutput, Input, Output, Component

# Custom imports below
from insightconnect_plugin_runtime.helper import clean


OS_TYPE_MAP = {
    "Windows": "1",
    "macOS": "2",
    "iOS": "3",
    "Android": "4",
    "Linux": "5",
}


class GetEnrolledDevices(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super().__init__(
            name="get_enrolled_devices",
            description=Component.DESCRIPTION,
            input=GetEnrolledDevicesInput(),
            output=GetEnrolledDevicesOutput(),
        )

    def run(self, params={}):
        username = params.get(Input.USERNAME, "")
        os_type = params.get(Input.OS_TYPE, "")

        os_type_value = OS_TYPE_MAP.get(os_type, "") if os_type else ""

        devices = self.connection.zcc_client.get_enrolled_devices(
            username=username,
            os_type=os_type_value,
        )

        return clean({Output.DEVICES: devices})
