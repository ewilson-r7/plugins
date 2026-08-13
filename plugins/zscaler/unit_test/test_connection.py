import os
import sys

sys.path.append(os.path.abspath("../"))

import logging
from unittest import TestCase
from unittest.mock import Mock, patch

from icon_zscaler.connection import Connection
from icon_zscaler.util.token_provider import TokenProvider
from insightconnect_plugin_runtime.exceptions import ConnectionTestException, PluginException
from parameterized import parameterized
from util import STUB_CONNECTION, Util

UNAUTHORIZED = PluginException(
    cause="OAuth 2.0 bearer token has expired or is invalid.",
    assistance="Verify that the API client has the required permissions.",
    data='{"detail": "unauthorized"}',
)


def grant_token(provider: TokenProvider) -> None:
    """Stand in for a successful token exchange without real JWT signing."""
    provider.token = "mock-access-token-12345"
    provider.expiry = 9999999999


class TestConnection(TestCase):
    @patch("requests.request", side_effect=Util.mock_request)
    def setUp(self, _mock_request: Mock) -> None:
        self.connection = Connection()
        self.connection.logger = logging.getLogger("connection logger")
        self.connection.connect(STUB_CONNECTION)
        grant_token(self.connection.token_provider)

    # ------------------------------------------------------------------
    # Shared token
    # ------------------------------------------------------------------

    def test_clients_share_one_token_provider(self) -> None:
        provider = self.connection.token_provider
        self.assertIs(self.connection.zia_client.token_provider, provider)
        self.assertIs(self.connection.zpa_client.token_provider, provider)
        self.assertIs(self.connection.zcc_client.token_provider, provider)

    def test_token_set_once_is_visible_to_every_client(self) -> None:
        self.connection.token_provider.token = "rotated-token"
        self.assertEqual(self.connection.zia_client._token, "rotated-token")
        self.assertEqual(self.connection.zpa_client._token, "rotated-token")
        self.assertEqual(self.connection.zcc_client._token, "rotated-token")

    @patch("requests.request", side_effect=Util.mock_request)
    def test_token_is_fetched_once_across_all_services(self, _mock_request: Mock) -> None:
        """Without a shared provider each service client would authenticate separately."""
        with patch.object(TokenProvider, "authenticate", autospec=True) as mock_auth:
            mock_auth.side_effect = grant_token
            self.connection.token_provider.token = None
            self.connection.token_provider.expiry = 0
            self.connection.test()

        self.assertEqual(mock_auth.call_count, 1)

    # ------------------------------------------------------------------
    # Tier 1: authentication is fatal
    # ------------------------------------------------------------------

    @patch("requests.request", side_effect=Util.mock_request)
    def test_authentication_failure_fails_the_test(self, _mock_request: Mock) -> None:
        auth_error = PluginException(
            cause="Failed to obtain OAuth 2.0 access token.",
            assistance="Verify that client_id, private_key, vanity_domain, and cloud are correct.",
            data="Authentication failed",
        )
        self.connection.token_provider.authenticate = Mock(side_effect=auth_error)

        with self.assertRaises(ConnectionTestException) as context:
            self.connection.test()

        self.assertEqual(context.exception.cause, "Failed to obtain OAuth 2.0 access token.")
        self.assertEqual(context.exception.data, "Authentication failed")

    @patch("requests.request", side_effect=Util.mock_request)
    def test_services_are_not_probed_when_authentication_fails(self, _mock_request: Mock) -> None:
        self.connection.token_provider.authenticate = Mock(side_effect=UNAUTHORIZED)
        self.connection.zia_client.test = Mock()

        with self.assertRaises(ConnectionTestException):
            self.connection.test()

        self.connection.zia_client.test.assert_not_called()

    # ------------------------------------------------------------------
    # Tier 2: per-service authorization is informational
    # ------------------------------------------------------------------

    @patch("requests.request", side_effect=Util.mock_request)
    def test_succeeds_when_all_services_authorized(self, _mock_request: Mock) -> None:
        self.connection.token_provider.authenticate = Mock(
            side_effect=lambda: grant_token(self.connection.token_provider)
        )

        self.assertEqual(self.connection.test(), {"success": True})

    @parameterized.expand(
        [
            ("only_zia_unauthorized", ["zia_client"]),
            ("only_zcc_authorized", ["zia_client", "zpa_client"]),
            ("only_zia_authorized", ["zpa_client", "zcc_client"]),
        ]
    )
    @patch("requests.request", side_effect=Util.mock_request)
    def test_succeeds_when_at_least_one_service_authorized(
        self, _name: str, unauthorized: list, _mock_request: Mock
    ) -> None:
        """A customer may license and scope only the products they use."""
        self.connection.token_provider.authenticate = Mock(
            side_effect=lambda: grant_token(self.connection.token_provider)
        )
        for client_name in unauthorized:
            getattr(self.connection, client_name).test = Mock(side_effect=UNAUTHORIZED)

        self.assertEqual(self.connection.test(), {"success": True})

    @patch("requests.request", side_effect=Util.mock_request)
    def test_probes_every_service_rather_than_aborting_on_first_failure(self, _mock_request: Mock) -> None:
        """The first failure previously masked the state of the remaining services."""
        self.connection.token_provider.authenticate = Mock(
            side_effect=lambda: grant_token(self.connection.token_provider)
        )
        self.connection.zia_client.test = Mock(side_effect=UNAUTHORIZED)
        self.connection.zpa_client.test = Mock(side_effect=UNAUTHORIZED)
        self.connection.zcc_client.test = Mock(return_value={"success": True})

        self.connection.test()

        self.connection.zia_client.test.assert_called_once()
        self.connection.zpa_client.test.assert_called_once()
        self.connection.zcc_client.test.assert_called_once()

    @patch("requests.request", side_effect=Util.mock_request)
    def test_fails_when_no_service_is_authorized(self, _mock_request: Mock) -> None:
        self.connection.token_provider.authenticate = Mock(
            side_effect=lambda: grant_token(self.connection.token_provider)
        )
        for client in (self.connection.zia_client, self.connection.zpa_client, self.connection.zcc_client):
            client.test = Mock(side_effect=UNAUTHORIZED)

        with self.assertRaises(ConnectionTestException) as context:
            self.connection.test()

        self.assertIn("no Zscaler service is authorized", context.exception.cause)
        self.assertIn("Resources tab", context.exception.assistance)
