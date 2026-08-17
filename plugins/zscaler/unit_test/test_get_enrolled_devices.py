import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from unittest.mock import patch

from util import Util
from icon_zscaler.actions.get_enrolled_devices import GetEnrolledDevices


@patch("requests.request", side_effect=Util.mock_request)
class TestGetEnrolledDevices(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.action = Util.default_connector(GetEnrolledDevices())

    def test_get_enrolled_devices_with_username(self, mock_request):
        result = self.action.run({"username": "jdoe@example.com"})
        self.assertIn("devices", result)
        self.assertEqual(len(result["devices"]), 2)
        self.assertEqual(result["devices"][0]["udid"], "abc123-def456-ghi789")
        self.assertEqual(result["devices"][0]["user"], "jdoe@example.com")

    def test_get_enrolled_devices_with_os_type(self, mock_request):
        result = self.action.run({"username": "jdoe@example.com", "os_type": "Windows"})
        self.assertIn("devices", result)
        self.assertEqual(len(result["devices"]), 2)

    def test_get_enrolled_devices_no_filter(self, mock_request):
        result = self.action.run({})
        self.assertIn("devices", result)
        self.assertIsInstance(result["devices"], list)
