import insightconnect_plugin_runtime
from insightconnect_plugin_runtime.exceptions import ConnectionTestException, PluginException

from .schema import ConnectionSchema, Input

# Custom imports below
from icon_zscaler.util.token_provider import TokenProvider
from icon_zscaler.util.zcc_client import ZCCClient
from icon_zscaler.util.zia_client import ZIAClient
from icon_zscaler.util.zpa_client import ZPAClient

DEFAULT_CLOUD = "zsapi.net"


class Connection(insightconnect_plugin_runtime.Connection):
    def __init__(self):
        super().__init__(input=ConnectionSchema())
        self.token_provider = None
        self.zia_client = None
        self.zpa_client = None
        self.zcc_client = None

    def connect(self, params={}):
        self.logger.info("Connect: Connecting...")

        client_id = params.get(Input.CLIENT_ID)
        private_key = params.get(Input.PRIVATE_KEY, {}).get("privateKey")
        vanity_domain = params.get(Input.VANITY_DOMAIN)
        cloud = params.get(Input.CLOUD) or DEFAULT_CLOUD

        # One provider shared by every service client. The token is not service
        # specific, so this fetches it once instead of once per service.
        self.token_provider = TokenProvider(client_id, private_key, vanity_domain, cloud, self.logger)

        self.zia_client = ZIAClient(
            client_id, private_key, vanity_domain, cloud, self.logger, token_provider=self.token_provider
        )
        self.zpa_client = ZPAClient(
            client_id, private_key, vanity_domain, cloud, self.logger, token_provider=self.token_provider
        )
        self.zcc_client = ZCCClient(
            client_id, private_key, vanity_domain, cloud, self.logger, token_provider=self.token_provider
        )

    @property
    def service_clients(self) -> dict:
        """Service name to client mapping, in the order they are probed."""
        return {"ZIA": self.zia_client, "ZPA": self.zpa_client, "ZCC": self.zcc_client}

    def test(self):
        """Validate the connection in two tiers.

        Authentication is fatal: if a token cannot be obtained then the credentials,
        vanity domain or cloud are wrong and nothing else can succeed.

        Per-service authorization is informational. A Zscaler API client is scoped by
        the API Resource roles assigned to it, and customers legitimately license and
        scope only the products they use. Every service is therefore probed and
        reported, and the test only fails when none of them are authorized.
        """
        try:
            self.token_provider.authenticate()
        except PluginException as error:
            raise ConnectionTestException(cause=error.cause, assistance=error.assistance, data=error.data) from error

        authorized, unauthorized = [], []
        for name, client in self.service_clients.items():
            try:
                client.test()
                authorized.append(name)
                self.logger.info(f"{name}: authorized")
            except PluginException as error:
                unauthorized.append(name)
                self.logger.info(f"{name}: not authorized ({error.cause})")

        if not authorized:
            raise ConnectionTestException(
                cause="The credentials are valid but no Zscaler service is authorized for this API client.",
                assistance=(
                    "Authentication succeeded, so the client ID, private key, vanity domain and cloud are "
                    "correct. In ZIdentity, open the API client and use the Resources tab to assign an API "
                    "Resource role for each service you intend to use. At least one of ZIA, ZPA or ZCC must "
                    "be assigned."
                ),
            )

        self.logger.info(f"Connection test succeeded. Authorized services: {', '.join(authorized)}.")
        if unauthorized:
            self.logger.info(
                f"The following services are not authorized for this API client and their actions will "
                f"fail until a role is assigned in ZIdentity: {', '.join(unauthorized)}."
            )

        return {"success": True}
