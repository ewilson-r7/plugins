import time
import uuid

import jwt
import requests
from insightconnect_plugin_runtime.exceptions import PluginException

from icon_zscaler.util.constants import TIMEOUT


class TokenProvider:
    """Issues and caches the OneAPI OAuth 2.0 access token.

    The token is not service specific. It is minted from a single client_id against a
    single audience, and authorization is enforced per endpoint by the API resource
    roles assigned to the client. One provider is therefore shared by every service
    client on a connection so a token is fetched once rather than once per service.
    """

    # OAuth audience identifier for OneAPI. This is an identifier, not a callable endpoint.
    AUDIENCE = "https://api.zscaler.com"
    ASSERTION_TYPE = "urn:ietf:params:oauth:client-assertion-type:jwt-bearer"
    ASSERTION_LIFETIME = 300  # seconds
    EXPIRY_BUFFER = 30  # seconds before expiry to trigger a refresh

    def __init__(self, client_id: str, private_key: str, vanity_domain: str, cloud: str, logger: object):
        self.client_id = client_id
        self.private_key = private_key
        self.vanity_domain = vanity_domain
        self.cloud = cloud
        self.logger = logger
        self.token = None
        self.expiry = 0

    @property
    def token_endpoint(self) -> str:
        return f"https://{self.vanity_domain}.{self.cloud}/oauth2/v1/token"

    def build_assertion(self) -> str:
        """Build the RS256 signed JWT client assertion."""
        now = int(time.time())
        claims = {
            "iss": self.client_id,
            "sub": self.client_id,
            "aud": self.token_endpoint,
            "iat": now,
            "exp": now + self.ASSERTION_LIFETIME,
            "jti": str(uuid.uuid4()),  # Unique ID per assertion for replay protection
        }

        self.logger.info("Building JWT assertion for OAuth 2.0 authentication...")
        return jwt.encode(claims, self.private_key, algorithm="RS256", headers={"typ": "JWT"})

    def authenticate(self) -> None:
        """Exchange a signed JWT assertion for an access token and cache it.

        Raises:
            PluginException: If the token endpoint is unreachable or rejects the request.
        """
        # Sent as a dict so requests form-encodes each value correctly (the audience
        # URI must be percent-encoded, otherwise the token is issued without it).
        body = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_assertion_type": self.ASSERTION_TYPE,
            "client_assertion": self.build_assertion(),
            "audience": self.AUDIENCE,
        }

        self.logger.info(f"Requesting OAuth token from {self.token_endpoint}")
        try:
            response = requests.request(
                method="POST",
                url=self.token_endpoint,
                data=body,
                timeout=TIMEOUT,
            )
        except requests.exceptions.Timeout:
            raise PluginException(
                cause="Timeout while requesting OAuth token.",
                assistance="Verify network connectivity and that the Zscaler identity provider is reachable.",
            )
        except requests.exceptions.ConnectionError:
            raise PluginException(
                cause="Connection error while requesting OAuth token.",
                assistance=(
                    "Verify the vanity domain and cloud settings are correct and the identity provider is "
                    "reachable. The cloud must match the domain of your ZIdentity login URL, for example "
                    "zslogin.net when you sign in at https://mycompany.zslogin.net."
                ),
            )

        if response.status_code != 200:
            raise PluginException(
                cause="Failed to obtain OAuth 2.0 access token.",
                assistance=(
                    f"Token endpoint returned HTTP {response.status_code}. "
                    "Verify that client_id, private_key, vanity_domain, and cloud are correct."
                ),
                data=response.text,
            )

        token_data = response.json()
        self.token = token_data.get("access_token")
        self.expiry = int(time.time()) + token_data.get("expires_in", 3600)
        self.logger.info("OAuth 2.0 token obtained successfully.")

    def get_token(self) -> str:
        """Return the cached token, refreshing it if missing or near expiry."""
        if self.token is None or time.time() >= (self.expiry - self.EXPIRY_BUFFER):
            self.logger.info("Token missing or near expiry, refreshing...")
            self.authenticate()
        return self.token
