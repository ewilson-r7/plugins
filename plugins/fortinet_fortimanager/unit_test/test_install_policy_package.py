import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from unittest.mock import patch

from insightconnect_plugin_runtime.exceptions import PluginException

from icon_fortinet_fortimanager.actions.install_policy_package import InstallPolicyPackage
from icon_fortinet_fortimanager.actions.install_policy_package.schema import Input, Output
from unit_test.util import create_mock_connection, load_payload, MockResponse


class TestInstallPolicyPackage(TestCase):
    def setUp(self):
        self.action = InstallPolicyPackage()
        self.action.connection = create_mock_connection()
        self.action.logger = self.action.connection.logger

    @patch("requests.Session.post")
    def test_install_policy_package_with_devices(self, mock_post):
        """Test successfully installing a policy package to target devices."""
        install_response = load_payload("install_policy_package.json.resp")
        mock_post.return_value = MockResponse(install_response)

        params = {
            Input.POLICY_PACKAGE: "default",
            Input.TARGET_DEVICES: ["firewall-01", "firewall-02"],
            Input.TARGET_DEVICE_GROUPS: [],
        }

        result = self.action.run(params)

        self.assertEqual(result[Output.TASK_ID], 247)

    @patch("requests.Session.post")
    def test_install_policy_package_with_device_groups(self, mock_post):
        """Test successfully installing a policy package to target device groups."""
        install_response = load_payload("install_policy_package.json.resp")
        mock_post.return_value = MockResponse(install_response)

        params = {
            Input.POLICY_PACKAGE: "default",
            Input.TARGET_DEVICES: [],
            Input.TARGET_DEVICE_GROUPS: ["branch-offices"],
        }

        result = self.action.run(params)

        self.assertEqual(result[Output.TASK_ID], 247)

    @patch("requests.Session.post")
    def test_install_policy_package_with_both_targets(self, mock_post):
        """Test installing a policy package to both devices and device groups."""
        install_response = load_payload("install_policy_package.json.resp")
        mock_post.return_value = MockResponse(install_response)

        params = {
            Input.POLICY_PACKAGE: "default",
            Input.TARGET_DEVICES: ["firewall-01"],
            Input.TARGET_DEVICE_GROUPS: ["branch-offices"],
        }

        result = self.action.run(params)

        self.assertEqual(result[Output.TASK_ID], 247)

    def test_install_policy_package_no_targets(self):
        """Test that PluginException is raised when no targets provided."""
        params = {
            Input.POLICY_PACKAGE: "default",
            Input.TARGET_DEVICES: [],
            Input.TARGET_DEVICE_GROUPS: [],
        }

        with self.assertRaises(PluginException) as context:
            self.action.run(params)

        self.assertIn("No target devices or device groups provided", context.exception.cause)

    def test_install_policy_package_none_targets(self):
        """Test that PluginException is raised when targets are None."""
        params = {
            Input.POLICY_PACKAGE: "default",
        }

        with self.assertRaises(PluginException) as context:
            self.action.run(params)

        self.assertIn("No target devices or device groups provided", context.exception.cause)

    @patch("requests.Session.post")
    def test_install_policy_package_with_adom_override(self, mock_post):
        """Test ADOM override from action input."""
        install_response = load_payload("install_policy_package.json.resp")
        mock_post.return_value = MockResponse(install_response)

        params = {
            Input.POLICY_PACKAGE: "default",
            Input.TARGET_DEVICES: ["firewall-01"],
            Input.TARGET_DEVICE_GROUPS: [],
            Input.ADOM: "custom-adom",
        }

        result = self.action.run(params)

        self.assertEqual(result[Output.TASK_ID], 247)

        # Verify the API call used the custom ADOM in the data payload
        call_payload = mock_post.call_args[1].get("json") or mock_post.call_args[0][0]
        if isinstance(call_payload, dict):
            data = call_payload.get("params", [{}])[0].get("data", {})
            self.assertEqual(data.get("adom"), "custom-adom")

    @patch("requests.Session.post")
    def test_install_policy_package_api_error(self, mock_post):
        """Test PluginException raised when API returns an error (e.g., package not found)."""
        error_response = load_payload("error_object_not_exist.json.resp")
        mock_post.return_value = MockResponse(error_response)

        params = {
            Input.POLICY_PACKAGE: "nonexistent-package",
            Input.TARGET_DEVICES: ["firewall-01"],
            Input.TARGET_DEVICE_GROUPS: [],
        }

        with self.assertRaises(PluginException) as context:
            self.action.run(params)

        self.assertIn("-3", context.exception.cause)

    @patch("requests.Session.post")
    def test_install_policy_package_builds_correct_scope(self, mock_post):
        """Test that targets are built with correct scope format."""
        install_response = load_payload("install_policy_package.json.resp")
        mock_post.return_value = MockResponse(install_response)

        params = {
            Input.POLICY_PACKAGE: "my-policy",
            Input.TARGET_DEVICES: ["device-a"],
            Input.TARGET_DEVICE_GROUPS: ["group-b"],
        }

        self.action.run(params)

        # Verify the scope in the request payload
        call_payload = mock_post.call_args[1].get("json") or mock_post.call_args[0][0]
        if isinstance(call_payload, dict):
            data = call_payload.get("params", [{}])[0].get("data", {})
            scope = data.get("scope", [])
            self.assertEqual(len(scope), 2)
            self.assertEqual(scope[0], {"name": "device-a", "vdom": "root"})
            self.assertEqual(scope[1], {"name": "group-b", "vdom": "root"})
