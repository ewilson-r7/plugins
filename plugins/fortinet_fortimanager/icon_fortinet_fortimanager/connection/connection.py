import insightconnect_plugin_runtime
from .schema import ConnectionSchema, Input

# Custom imports below
from icon_fortinet_fortimanager.util.api import FortiManagerAPI
from icon_fortinet_fortimanager.util.constants import METHOD_GET, URL_SYSTEM_STATUS
from icon_fortinet_fortimanager.util.helpers import Helpers
from insightconnect_plugin_runtime.exceptions import ConnectionTestException, PluginException


class Connection(insightconnect_plugin_runtime.Connection):
    def __init__(self):
        super(self.__class__, self).__init__(input=ConnectionSchema())
        self.api = None
        self.default_adom = None

    def connect(self, params):
        # Strip whitespace from string credential inputs
        params = Helpers.strip_credentials(params)

        # Extract connection parameters
        hostname = params.get(Input.HOSTNAME, "")
        auth_type = params.get(Input.AUTHENTICATION_TYPE, "API Token")
        ssl_verify = params.get(Input.SSL_VERIFY, False)
        self.default_adom = params.get(Input.ADOM, "root")

        # Extract auth credentials based on type
        api_key = None
        username = None
        password = None

        if auth_type == "API Token":
            api_key_param = params.get(Input.API_KEY, {})
            if isinstance(api_key_param, dict):
                api_key = api_key_param.get("secretKey", "")
            else:
                api_key = ""
        else:
            username = params.get(Input.USERNAME, "")
            password_param = params.get(Input.PASSWORD, {})
            if isinstance(password_param, dict):
                password = password_param.get("secretKey", "")
            else:
                password = ""

        # Instantiate API client — no API calls here
        self.api = FortiManagerAPI(
            host=hostname,
            logger=self.logger,
            ssl_verify=ssl_verify,
            auth_type=auth_type,
            api_key=api_key,
            username=username,
            password=password,
        )

    def test(self):
        try:
            if self.api.auth_type == "API Token":
                # For API Token: call /sys/status with Bearer header, verify response
                self.api.execute(METHOD_GET, URL_SYSTEM_STATUS)
            else:
                # For Session-Based: login, verify session, logout
                session = self.api.login()
                if not session:
                    raise ConnectionTestException(
                        cause="FortiManager login failed: no session token returned.",
                        assistance="Verify your username and password credentials are correct.",
                    )
                self.api.logout()
        except ConnectionTestException:
            raise
        except PluginException as error:
            raise ConnectionTestException(
                cause=error.cause,
                assistance=error.assistance,
                data=error.data,
            )

        return {"success": True}
