import time
from abc import ABC, abstractmethod

import requests
from insightconnect_plugin_runtime.exceptions import PluginException

from icon_zscaler.util.constants import (
    HTTP_ERROR_MAP,
    TIMEOUT,
    Assistance,
    Cause,
)
from icon_zscaler.util.token_provider import TokenProvider


class BaseClient(ABC):
    """Base client for Zscaler OneAPI with OAuth 2.0 Client Credentials (Private Key) authentication."""

    BASE_URL = "https://api.zsapi.net"

    def __init__(
        self,
        client_id: str,
        private_key: str,
        vanity_domain: str,
        cloud: str,
        logger: object,
        token_provider: TokenProvider = None,
    ):
        self.logger = logger
        self.base_url = self.BASE_URL
        self.service_prefix = ""  # Set by subclasses (e.g., "/zia/api/v1", "/zpa/api/v1")
        # A provider is shared across service clients so the token is fetched once per
        # connection. One is created here when a client is used standalone.
        self.token_provider = token_provider or TokenProvider(client_id, private_key, vanity_domain, cloud, logger)

    # Credentials live on the token provider so the shared instance is the single
    # source of truth. These delegate rather than holding a second copy.
    @property
    def client_id(self):
        return self.token_provider.client_id

    @client_id.setter
    def client_id(self, value) -> None:
        self.token_provider.client_id = value

    @property
    def private_key(self):
        return self.token_provider.private_key

    @private_key.setter
    def private_key(self, value) -> None:
        self.token_provider.private_key = value

    @property
    def vanity_domain(self):
        return self.token_provider.vanity_domain

    @vanity_domain.setter
    def vanity_domain(self, value) -> None:
        self.token_provider.vanity_domain = value

    @property
    def cloud(self):
        return self.token_provider.cloud

    @cloud.setter
    def cloud(self, value) -> None:
        self.token_provider.cloud = value

    @property
    def token_endpoint(self) -> str:
        return self.token_provider.token_endpoint

    @property
    def _token(self):
        return self.token_provider.token

    @_token.setter
    def _token(self, value) -> None:
        self.token_provider.token = value

    @property
    def _token_expiry(self):
        return self.token_provider.expiry

    @_token_expiry.setter
    def _token_expiry(self, value) -> None:
        self.token_provider.expiry = value

    def authenticate(self) -> None:
        """Obtain an access token, proving the credentials are valid.

        Exposed for the connection test, which validates authentication separately
        from per-service authorization.
        """
        self.token_provider.authenticate()

    def _authenticate(self) -> None:
        self.token_provider.authenticate()

    def _get_token(self) -> str:
        return self.token_provider.get_token()

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Build full URL with service prefix and make an authenticated API request."""
        url = f"{self.base_url}{self.service_prefix}/{endpoint}"
        token = self._get_token()
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        return self._call_api(method, url, headers=headers, **kwargs)

    def raw_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Send an authenticated request and return the response without status handling.

        Unlike _make_request, this does not raise on non-2xx responses and does not
        retry on 401. Callers observe the exact status code and body returned by the
        API, which is what makes it useful for reproducing a request for comparison.

        Args:
            method: HTTP method to use.
            endpoint: Endpoint path relative to the service prefix.

        Returns:
            The raw requests.Response, whatever its status code.
        """
        url = f"{self.base_url}{self.service_prefix}/{endpoint.lstrip('/')}"
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self._get_token()}"
        kwargs.setdefault("timeout", TIMEOUT)

        self.logger.info(f"Sending {method} request to {url}")
        try:
            return requests.request(method=method, url=url, headers=headers, **kwargs)
        except requests.exceptions.Timeout:
            raise PluginException(
                cause="Request timed out.",
                assistance="The Zscaler API did not respond in time. Retry the request or check network connectivity.",
            )
        except requests.exceptions.ConnectionError:
            raise PluginException(
                cause="Connection error occurred.",
                assistance="Unable to reach the Zscaler API. Verify network connectivity and API availability.",
            )

    def _call_api(self, method: str, url: str, **kwargs) -> requests.Response:
        """Execute HTTP request using requests.request() (no Session). Handle transport errors."""
        kwargs.setdefault("timeout", TIMEOUT)
        try:
            response = requests.request(method=method, url=url, **kwargs)
        except requests.exceptions.Timeout:
            raise PluginException(
                cause="Request timed out.",
                assistance="The Zscaler API did not respond in time. Retry the request or check network connectivity.",
            )
        except requests.exceptions.ConnectionError:
            raise PluginException(
                cause="Connection error occurred.",
                assistance="Unable to reach the Zscaler API. Verify network connectivity and API availability.",
            )

        return self._handle_status(response, method, url, **kwargs)

    def _handle_status(self, response: requests.Response, method: str, url: str, **kwargs) -> requests.Response:
        """Map HTTP status codes to PluginException using HTTP_ERROR_MAP. Handle 401 with one retry."""
        status_code = response.status_code

        if 200 <= status_code < 300:
            return response

        # Handle 401 with one re-authentication retry
        if status_code == 401:
            self.logger.info("Received 401 Unauthorized. Re-authenticating and retrying...")
            self._authenticate()
            # Update the Authorization header with the new token
            headers = kwargs.get("headers", {})
            headers["Authorization"] = f"Bearer {self._token}"
            kwargs["headers"] = headers

            try:
                retry_response = requests.request(method=method, url=url, **kwargs)
            except requests.exceptions.Timeout:
                raise PluginException(
                    cause="Request timed out on retry.",
                    assistance="The Zscaler API did not respond in time after re-authentication.",
                )
            except requests.exceptions.ConnectionError:
                raise PluginException(
                    cause="Connection error on retry.",
                    assistance="Unable to reach the Zscaler API after re-authentication.",
                )

            if 200 <= retry_response.status_code < 300:
                return retry_response

            # Still 401 after retry — raise auth error
            if retry_response.status_code == 401:
                error_info = HTTP_ERROR_MAP.get(401, {})
                raise PluginException(
                    cause=error_info.get("cause", Cause.TOKEN_EXPIRED),
                    assistance=error_info.get("assistance", Assistance.REAUTHENTICATE),
                    data=retry_response.text,
                )

            # Different error after retry — handle normally
            return self._raise_for_status(retry_response)

        return self._raise_for_status(response)

    def _raise_for_status(self, response: requests.Response) -> requests.Response:
        """Raise PluginException for non-2xx responses using HTTP_ERROR_MAP."""
        status_code = response.status_code

        if 200 <= status_code < 300:
            return response

        error_info = HTTP_ERROR_MAP.get(status_code)

        if error_info:
            if status_code == 429:
                retry_after = response.headers.get("Retry-After", "unknown")
                self.logger.info(f"Rate limited. Retry-After: {retry_after}")
            raise PluginException(
                cause=error_info["cause"],
                assistance=error_info["assistance"],
                data=response.text,
            )

        # Fallback for unmapped status codes
        raise PluginException(
            cause=f"Unexpected HTTP status code: {status_code}",
            assistance="An unexpected error occurred. Please contact support if the issue persists.",
            data=response.text,
        )

    @abstractmethod
    def test(self) -> dict:
        """Test connectivity to the Zscaler API. Implemented by subclasses."""
