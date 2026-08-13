import os
import sys

sys.path.append(os.path.abspath("../"))

import json
from unittest import TestCase
from unittest.mock import patch

import requests
from icon_zscaler.actions.custom_api_request import CustomApiRequest
from icon_zscaler.actions.custom_api_request.schema import Input, Output
from insightconnect_plugin_runtime.exceptions import PluginException
from parameterized import parameterized
from util import Util


class MockResponse:
    """Minimal response stub exposing the attributes the action reads."""

    def __init__(self, status_code: int, url: str = "", text: str = ""):
        self.status_code = status_code
        self.url = url
        self.text = text


def make_response(status_code: int = 200, text: str = "[]"):
    def _request(method=None, url=None, **kwargs):
        _request.calls.append({"method": method, "url": url, **kwargs})
        return MockResponse(status_code, url, text)

    _request.calls = []
    return _request


class TestCustomApiRequest(TestCase):
    def setUp(self) -> None:
        self.action = Util.default_connector(CustomApiRequest())

    @parameterized.expand(
        [
            ("zia", "ZIA", "urlLookup", "https://api.zsapi.net/zia/api/v1/urlLookup"),
            ("zpa", "ZPA", "serverGroup", "https://api.zsapi.net/zpa/api/v1/serverGroup"),
            (
                "zcc",
                "ZCC",
                "web/policy/listByCompany",
                "https://api.zsapi.net/zcc/papi/public/v1/web/policy/listByCompany",
            ),
        ]
    )
    def test_builds_url_from_service_prefix(self, _name, service, path, expected_url) -> None:
        fake = make_response(200, "[]")
        with patch.object(requests, "request", side_effect=fake):
            result = self.action.run({Input.SERVICE: service, Input.METHOD: "GET", Input.PATH: path})

        self.assertEqual(fake.calls[0]["url"], expected_url)
        self.assertEqual(result[Output.URL], expected_url)
        self.assertEqual(result[Output.STATUS_CODE], 200)

    def test_reproduces_known_working_zcc_request(self) -> None:
        fake = make_response(200, '[{"profileName": "Default"}]')
        with patch.object(requests, "request", side_effect=fake):
            result = self.action.run(
                {Input.SERVICE: "ZCC", Input.METHOD: "GET", Input.PATH: "web/policy/listByCompany"}
            )

        self.assertEqual(
            result[Output.URL],
            "https://api.zsapi.net/zcc/papi/public/v1/web/policy/listByCompany",
        )
        self.assertEqual(result[Output.STATUS_CODE], 200)
        self.assertEqual(result[Output.RESPONSE], '[{"profileName": "Default"}]')
        self.assertEqual(fake.calls[0]["headers"]["Authorization"], "Bearer mock-access-token-12345")

    def test_returns_error_status_instead_of_raising(self) -> None:
        """The action must surface non-2xx responses so they can be compared, not raise."""
        fake = make_response(401, '{"detail": "unauthorized"}')
        with patch.object(requests, "request", side_effect=fake):
            result = self.action.run({Input.SERVICE: "ZIA", Input.METHOD: "GET", Input.PATH: "status"})

        self.assertEqual(result[Output.STATUS_CODE], 401)
        self.assertEqual(result[Output.RESPONSE], '{"detail": "unauthorized"}')
        # Only one call, meaning no 401 re-authentication retry muddied the result
        self.assertEqual(len(fake.calls), 1)

    def test_sends_json_body_on_post(self) -> None:
        fake = make_response(200, "[]")
        with patch.object(requests, "request", side_effect=fake):
            self.action.run(
                {
                    Input.SERVICE: "ZIA",
                    Input.METHOD: "POST",
                    Input.PATH: "urlLookup",
                    Input.BODY: {"urls": ["facebook.com"]},
                }
            )

        call = fake.calls[0]
        self.assertEqual(json.loads(call["data"]), {"urls": ["facebook.com"]})
        self.assertEqual(call["headers"]["Content-Type"], "application/json")

    def test_ignores_body_on_get(self) -> None:
        fake = make_response(200, "[]")
        with patch.object(requests, "request", side_effect=fake):
            self.action.run(
                {
                    Input.SERVICE: "ZIA",
                    Input.METHOD: "GET",
                    Input.PATH: "status",
                    Input.BODY: {"urls": ["facebook.com"]},
                }
            )

        self.assertNotIn("data", fake.calls[0])

    def test_strips_leading_slash_from_path(self) -> None:
        fake = make_response(200, "[]")
        with patch.object(requests, "request", side_effect=fake):
            self.action.run({Input.SERVICE: "ZIA", Input.METHOD: "GET", Input.PATH: "/status"})

        self.assertEqual(fake.calls[0]["url"], "https://api.zsapi.net/zia/api/v1/status")

    def test_raises_on_unsupported_service(self) -> None:
        with self.assertRaises(PluginException):
            self.action.run({Input.SERVICE: "ZDX", Input.METHOD: "GET", Input.PATH: "status"})

    @parameterized.expand(
        [("timeout", requests.exceptions.Timeout), ("connection", requests.exceptions.ConnectionError)]
    )
    def test_raises_on_transport_error(self, _name, error) -> None:
        with patch.object(requests, "request", side_effect=error):
            with self.assertRaises(PluginException):
                self.action.run({Input.SERVICE: "ZIA", Input.METHOD: "GET", Input.PATH: "status"})
