import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from unittest.mock import patch

from util import Util
from icon_zscaler.actions.get_one_time_password import GetOneTimePassword


@patch("requests.request", side_effect=Util.mock_request)
class TestGetOneTimePassword(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.action = Util.default_connector(GetOneTimePassword())

    def test_get_otp_success(self, mock_request):
        result = self.action.run({"udid": "abc123-def456-ghi789"})
        self.assertIn("otp", result)
        otp_bundle = result["otp"]
        self.assertEqual(otp_bundle["logout_otp"], "482916")
        self.assertEqual(otp_bundle["exit_otp"], "739205")
        self.assertEqual(otp_bundle["uninstall_otp"], "158473")

    def test_get_otp_contains_all_fields(self, mock_request):
        result = self.action.run({"udid": "abc123-def456-ghi789"})
        otp_bundle = result["otp"]
        expected_fields = [
            "logout_otp",
            "exit_otp",
            "uninstall_otp",
            "revert_otp",
            "zia_disable_otp",
            "zpa_disable_otp",
            "zdx_disable_otp",
            "zdp_disable_otp",
            "anti_tempering_disable_otp",
            "otp",
        ]
        for field in expected_fields:
            self.assertIn(field, otp_bundle)
