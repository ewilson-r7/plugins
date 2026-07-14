import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from unittest.mock import patch

from icon_fortinet_fortimanager.actions.get_policies import GetPolicies
from icon_fortinet_fortimanager.actions.get_policies.schema import Input, Output
from insightconnect_plugin_runtime.exceptions import PluginException
from unit_test.util import create_mock_connection, load_payload, MockResponse


class TestGetPolicies(TestCase):
    def setUp(self):
        self.action = GetPolicies()
        self.action.connection = create_mock_connection()
        self.action.logger = self.action.connection.logger

        # Load payload for mocking
        self.mock_response_data = load_payload("get_policies.json.resp")

    @patch("requests.Session.post")
    def test_get_all_policies(self, mock_post):
        """Test retrieving all policies without filters."""
        mock_post.return_value = MockResponse(self.mock_response_data)

        result = self.action.run({Input.POLICY_PACKAGE: "default"})

        self.assertIsInstance(result[Output.POLICIES], list)
        self.assertEqual(len(result[Output.POLICIES]), 3)

    @patch("requests.Session.post")
    def test_get_policies_with_name_filter(self, mock_post):
        """Test retrieving policies filtered by name."""
        mock_post.return_value = MockResponse(self.mock_response_data)

        result = self.action.run(
            {
                Input.POLICY_PACKAGE: "default",
                Input.NAME_FILTER: "Allow-Internal",
            }
        )

        self.assertEqual(len(result[Output.POLICIES]), 1)
        self.assertEqual(result[Output.POLICIES][0]["name"], "Allow-Internal")
        self.assertEqual(result[Output.POLICIES][0]["policyid"], 1)

    @patch("requests.Session.post")
    def test_get_policies_name_filter_case_insensitive(self, mock_post):
        """Test that name filter is case-insensitive."""
        mock_post.return_value = MockResponse(self.mock_response_data)

        result = self.action.run(
            {
                Input.POLICY_PACKAGE: "default",
                Input.NAME_FILTER: "allow-internal",
            }
        )

        self.assertEqual(len(result[Output.POLICIES]), 1)
        self.assertEqual(result[Output.POLICIES][0]["name"], "Allow-Internal")

    @patch("requests.Session.post")
    def test_get_policies_no_matches_returns_empty(self, mock_post):
        """Test that non-matching filter returns empty list without exception."""
        mock_post.return_value = MockResponse(self.mock_response_data)

        result = self.action.run(
            {
                Input.POLICY_PACKAGE: "default",
                Input.NAME_FILTER: "nonexistent-policy",
            }
        )

        self.assertEqual(result[Output.POLICIES], [])

    @patch("requests.Session.post")
    def test_get_policies_with_adom_override(self, mock_post):
        """Test that ADOM input overrides connection default."""
        mock_post.return_value = MockResponse(self.mock_response_data)

        result = self.action.run(
            {
                Input.POLICY_PACKAGE: "default",
                Input.ADOM: "custom-adom",
            }
        )

        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        payload = call_kwargs[1]["json"] if "json" in call_kwargs[1] else call_kwargs[0][0]
        request_url = payload["params"][0]["url"]
        self.assertIn("custom-adom", request_url)

    @patch("requests.Session.post")
    def test_get_policies_uses_default_adom(self, mock_post):
        """Test that connection default ADOM is used when no override provided."""
        mock_post.return_value = MockResponse(self.mock_response_data)

        result = self.action.run({Input.POLICY_PACKAGE: "default"})

        mock_post.assert_called_once()
        call_kwargs = mock_post.call_args
        payload = call_kwargs[1]["json"] if "json" in call_kwargs[1] else call_kwargs[0][0]
        request_url = payload["params"][0]["url"]
        self.assertIn("root", request_url)

    @patch("requests.Session.post")
    def test_get_policies_adom_not_found(self, mock_post):
        """Test that PluginException is raised when ADOM does not exist."""
        error_response = {"id": 1, "result": [{"status": {"code": -3, "message": "Object does not exist"}}]}
        mock_post.return_value = MockResponse(error_response)

        with self.assertRaises(PluginException) as context:
            self.action.run(
                {
                    Input.POLICY_PACKAGE: "default",
                    Input.ADOM: "nonexistent-adom",
                }
            )

        self.assertIn("-3", context.exception.cause)

    @patch("requests.Session.post")
    def test_get_policies_package_not_found(self, mock_post):
        """Test that PluginException is raised when policy package does not exist."""
        error_response = {"id": 1, "result": [{"status": {"code": -3, "message": "Object does not exist"}}]}
        mock_post.return_value = MockResponse(error_response)

        with self.assertRaises(PluginException) as context:
            self.action.run(
                {
                    Input.POLICY_PACKAGE: "nonexistent-package",
                }
            )

        self.assertIn("-3", context.exception.cause)

    @patch("requests.Session.post")
    def test_get_policies_empty_name_filter_returns_all(self, mock_post):
        """Test that empty string name filter returns all policies."""
        mock_post.return_value = MockResponse(self.mock_response_data)

        result = self.action.run(
            {
                Input.POLICY_PACKAGE: "default",
                Input.NAME_FILTER: "",
            }
        )

        self.assertEqual(len(result[Output.POLICIES]), 3)
