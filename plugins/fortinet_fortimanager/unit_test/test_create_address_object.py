import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from unittest.mock import patch, MagicMock

from icon_fortinet_fortimanager.actions.create_address_object import CreateAddressObject
from icon_fortinet_fortimanager.actions.create_address_object.schema import Input, Output
from insightconnect_plugin_runtime.exceptions import PluginException
from unit_test.util import create_mock_connection, load_payload, MockResponse


class TestCreateAddressObject(TestCase):
    def setUp(self):
        self.action = CreateAddressObject()
        self.action.connection = create_mock_connection()
        self.action.logger = self.action.connection.logger

        # Load payloads for mocking
        self.mock_success_response = load_payload("create_address_object.json.resp")
        self.mock_error_conflict = load_payload("error_conflict.json.resp")

    @patch("requests.Session.post")
    def test_create_ipmask_from_bare_ip(self, mock_post):
        """Test creating ipmask object from a bare IP (should become /32)."""
        mock_post.return_value = MockResponse(self.mock_success_response)

        result = self.action.run(
            {
                Input.ADDRESS: "10.20.30.40",
                Input.SKIP_RFC1918: False,
            }
        )

        self.assertTrue(result[Output.SUCCESS])
        self.assertEqual(result[Output.ADDRESS_OBJECT]["name"], "10.20.30.40")
        self.assertEqual(result[Output.ADDRESS_OBJECT]["type"], "ipmask")
        self.assertEqual(result[Output.ADDRESS_OBJECT]["subnet"], "10.20.30.40/32")

    @patch("requests.Session.post")
    def test_create_ipmask_from_cidr(self, mock_post):
        """Test creating ipmask object from CIDR notation."""
        mock_post.return_value = MockResponse(self.mock_success_response)

        result = self.action.run(
            {
                Input.ADDRESS: "192.168.10.0/24",
                Input.SKIP_RFC1918: False,
            }
        )

        self.assertTrue(result[Output.SUCCESS])
        self.assertEqual(result[Output.ADDRESS_OBJECT]["name"], "192.168.10.0/24")
        self.assertEqual(result[Output.ADDRESS_OBJECT]["type"], "ipmask")
        self.assertEqual(result[Output.ADDRESS_OBJECT]["subnet"], "192.168.10.0/24")

    @patch("requests.Session.post")
    def test_create_fqdn_object(self, mock_post):
        """Test creating fqdn object from a domain name."""
        mock_post.return_value = MockResponse(self.mock_success_response)

        result = self.action.run(
            {
                Input.ADDRESS: "malicious.example.com",
                Input.SKIP_RFC1918: False,
            }
        )

        self.assertTrue(result[Output.SUCCESS])
        self.assertEqual(result[Output.ADDRESS_OBJECT]["name"], "malicious.example.com")
        self.assertEqual(result[Output.ADDRESS_OBJECT]["type"], "fqdn")
        self.assertEqual(result[Output.ADDRESS_OBJECT]["fqdn"], "malicious.example.com")

    def test_invalid_address_raises_plugin_exception(self):
        """Test that an invalid address raises PluginException."""
        with self.assertRaises(PluginException) as context:
            self.action.run(
                {
                    Input.ADDRESS: "not_a_valid_address!!!",
                    Input.SKIP_RFC1918: False,
                }
            )

        self.assertIn("Invalid address format", context.exception.cause)

    @patch("requests.Session.post")
    def test_whitelist_skip_returns_success_false(self, mock_post):
        """Test that whitelisted address skips creation and returns success=false."""
        result = self.action.run(
            {
                Input.ADDRESS: "8.8.8.8",
                Input.SKIP_RFC1918: False,
                Input.WHITELIST: ["8.8.8.0/24"],
            }
        )

        self.assertFalse(result[Output.SUCCESS])
        self.assertEqual(result[Output.ADDRESS_OBJECT], {})
        # Verify no API call was made
        mock_post.assert_not_called()

    @patch("requests.Session.post")
    def test_rfc1918_skip_returns_success_false(self, mock_post):
        """Test that RFC 1918 address skips creation and returns success=false when skip_rfc1918 is enabled."""
        result = self.action.run(
            {
                Input.ADDRESS: "192.168.1.100",
                Input.SKIP_RFC1918: True,
            }
        )

        self.assertFalse(result[Output.SUCCESS])
        self.assertEqual(result[Output.ADDRESS_OBJECT], {})
        # Verify no API call was made
        mock_post.assert_not_called()

    @patch("requests.Session.post")
    def test_naming_conflict_raises_plugin_exception(self, mock_post):
        """Test that a naming conflict (error -6) raises PluginException."""
        mock_post.return_value = MockResponse(self.mock_error_conflict)

        with self.assertRaises(PluginException) as context:
            self.action.run(
                {
                    Input.ADDRESS: "8.8.8.8",
                    Input.SKIP_RFC1918: False,
                }
            )

        self.assertIn("-6", context.exception.cause)

    @patch("requests.Session.post")
    def test_custom_name_input(self, mock_post):
        """Test that a custom address object name is used when provided."""
        mock_post.return_value = MockResponse(self.mock_success_response)

        result = self.action.run(
            {
                Input.ADDRESS: "1.2.3.4",
                Input.ADDRESS_OBJECT_NAME: "my-custom-name",
                Input.SKIP_RFC1918: False,
            }
        )

        self.assertTrue(result[Output.SUCCESS])
        self.assertEqual(result[Output.ADDRESS_OBJECT]["name"], "my-custom-name")
        self.assertEqual(result[Output.ADDRESS_OBJECT]["type"], "ipmask")
        self.assertEqual(result[Output.ADDRESS_OBJECT]["subnet"], "1.2.3.4/32")
