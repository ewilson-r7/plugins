import insightconnect_plugin_runtime
from .schema import GetOneTimePasswordInput, GetOneTimePasswordOutput, Input, Output, Component

# Custom imports below


class GetOneTimePassword(insightconnect_plugin_runtime.Action):
    def __init__(self):
        super().__init__(
            name="get_one_time_password",
            description=Component.DESCRIPTION,
            input=GetOneTimePasswordInput(),
            output=GetOneTimePasswordOutput(),
        )

    def run(self, params={}):
        udid = params.get(Input.UDID)

        otp_bundle = self.connection.zcc_client.get_device_otp(udid=udid)

        return {Output.OTP: otp_bundle}
