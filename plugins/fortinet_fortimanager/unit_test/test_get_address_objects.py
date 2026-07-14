import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from unittest.mock import patch, MagicMock

from icon_fortinet_fortimanager.actions.get_address_objects import GetAddressObjects
from icon_fortinet_fortimanager.actions.get_address_objects.schema import Input, Output
from insightconnect_plugin_runtime.exceptions import PluginException
from unit_test.util import create_mock_connection, load_payload, MockResponse


class TestGetAddressObjects(TestCase):
    def setUp(self):
        self.action = GetAddressObjects()
        self.action.connection = create_mock_connection()
        self.action.logger = self.action.connection.logger

        # Load payload for mocking
        self.mock_response_data = load_payload("get_address_objects.json.resp")

    @patch("requests.Session.post")
    def test_get_all_address_objects(self, mock_post):
        """Test retrieving all address objects without filters."""
        mock_post.return_value = MockResponse(self.mock_response_data)

        result = self.action.run({})

        self.assertIsInstance(result[Output.ADDRESS_OBJECTS], list)
        self.assertEqual(len(result[Output.ADDRESS_OBJECTS]), 4)

    @patch("requests.Session.post")
    def test_get_address_objects_with_name_filter(self, mock_post):
        """Test retrieving address objects filtered by name."""
        mock_post.return_value = MockResponse(self.mock_response_data)

        result = self.action.run({Input.NAME_FILTER: "google-dns"})

        self.assertEqual(len(result[Output.ADDRESS_OBJECTS]), 1)
        self.assertEqual(result[Output.ADDRESS_OBJECTS][0]["name"], "google-dns")

    @patch("requests.Session.post")
    def test_get_address_objects_with_name_filter_case_insensitive(self, mock_post):
        """Test that name filter is case-insensitive."""
        mock_post.return_value = MockResponse(self.mock_response_data)

        result = self.action.run({Input.NAME_FILTER: "GOOGLE-DNS"})

        self.assertEqual(len(result[Output.ADDRESS_OBJECTS]), 1)
        self.assertEqual(result[Output.ADDRESS_OBJECTS][0]["name"], "google-dns")

    @patch("requests.Session.post")
    def test_get_address_objects_with_subnet_filter(self, mock_post):
        """Test retrieving address objects filtered by subnet."""
        mock_post.return_value = MockResponse(self.mock_response_data)

        result = self.action.run({Input.SUBNET_FILTER: "192.168.1.0/24"})

        self.assertEqual(len(result[Output.ADDRESS_OBJECTS]), 1)
        self.assertEqual(result[Output.ADDRESS_OBJECTS][0]["name"], "internal-net")

    @patch("requests.Session.post")
    def test_get_address_objects_with_fqdn_filter(self, mock_post):
        """Test retrieving address objects filtered by FQDN."""
        mock_post.return_value = MockResponse(self.mock_response_data)

        result = self.action.run({Input.FQDN_FILTER: "example.com"})

        self.assertEqual(len(result[Output.ADDRESS_OBJECTS]), 1)
        self.assertEqual(result[Output.ADDRESS_OBJECTS][0]["name"], "example-fqdn")

    @patch("requests.Session.post")
    def test_get_address_objects_with_multiple_filters_and_logic(self, mock_post):
        """Test that multiple filters use AND logic."""
        mock_post.return_value = MockResponse(self.mock_response_data)

        # Name + subnet filter that matches one object
        result = self.action.run(
            {
                Input.NAME_FILTER: "internal-net",
                Input.SUBNET_FILTER: "192.168.1.0/24",
            }
        )

        self.assertEqual(len(result[Output.ADDRESS_OBJECTS]), 1)
        self.assertEqual(result[Output.ADDRESS_OBJECTS][0]["name"], "internal-net")

    @patch("requests.Session.post")
    def test_get_address_objects_with_conflicting_filters_returns_empty(self, mock_post):
        """Test that conflicting filters return empty list."""
        mock_post.return_value = MockResponse(self.mock_response_data)

        # Name matches one object but subnet does not match that object
        result = self.action.run(
            {
                Input.NAME_FILTER: "google-dns",
                Input.FQDN_FILTER: "example.com",
            }
        )

        self.assertEqual(len(result[Output.ADDRESS_OBJECTS]), 0)

    @patch("requests.Session.post")
    def test_get_address_objects_no_matches_returns_empty(self, mock_post):
        """Test that non-matching filter returns empty list without exception."""
        mock_post.return_value = MockResponse(self.mock_response_data)

        result = self.action.run({Input.NAME_FILTER: "nonexistent-object"})

        self.assertEqual(result[Output.ADDRESS_OBJECTS], [])

    @patch("requests.Session.post")
    def test_get_address_objects_with_adom_override(self, mock_post):
        """Test that ADOM input overrides connection default."""
        mock_post.return_value = MockResponse(self.mock_response_data)

        result = self.action.run({Input.ADOM: "custom-adom"})

        # Verify the API was called (mock was used)
        mock_post.assert_called_once()
        # Check the request payload contains the custom ADOM in the URL
        call_kwargs = mock_post.call_args
        payload = call_kwargs[1]["json"] if "json" in call_kwargs[1] else call_kwargs[0][0]
        request_url = payload["params"][0]["url"]
        self.assertIn("custom-adom", request_url)

    @patch("requests.Session.post")
    def test_get_address_objects_uses_default_adom(self, mock_post):
        """Test that connection default ADOM is used when no override provided."""
        mock_post.return_value = MockResponse(self.mock_response_data)

        result = self.action.run({})

        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        payload = call_kwargs[1]["json"] if "json" in call_kwargs[1] else call_kwargs[0][0]
        request_url = payload["params"][0]["url"]
        self.assertIn("root", request_url)

    @patch("requests.Session.post")
    def test_get_address_objects_adom_not_found(self, mock_post):
        """Test that PluginException is raised when ADOM does not exist."""
        error_response = {"id": 1, "result": [{"status": {"code": -3, "message": "Object does not exist"}}]}
        mock_post.return_value = MockResponse(error_response)

        with self.assertRaises(PluginException) as context:
            self.action.run({Input.ADOM: "nonexistent-adom"})

        self.assertIn("-3", context.exception.cause)
