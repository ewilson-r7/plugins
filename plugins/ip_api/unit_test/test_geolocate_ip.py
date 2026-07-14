import unittest
from unittest.mock import patch, MagicMock

from insightconnect_plugin_runtime.exceptions import PluginException

from icon_ip_api.actions.geolocate_ip.action import GeolocateIp
from icon_ip_api.actions.geolocate_ip.schema import Input, Output
from unit_test.util import MockResponse, default_connector, load_response


class TestGeolocateIp(unittest.TestCase):
    """Unit tests for the geolocate_ip action."""

    def setUp(self):
        self.action = default_connector(GeolocateIp())

    # ------------------------------------------------------------------
    # Happy-path tests
    # ------------------------------------------------------------------

    @patch("requests.Session.request")
    def test_success_with_ipv4(self, mock_request):
        """A successful lookup for 8.8.8.8 should return a populated result dict."""
        response_data = load_response("geolocate_ip_success.json")
        mock_request.return_value = MockResponse(response_data, status_code=200)

        result = self.action.run({Input.QUERY: "8.8.8.8", Input.LANG: "en"})

        self.assertIn(Output.RESULT, result)
        geo = result[Output.RESULT]
        self.assertEqual(geo["status"], "success")
        self.assertEqual(geo["query"], "8.8.8.8")
        self.assertEqual(geo["country"], "United States")
        self.assertEqual(geo["countryCode"], "US")
        # 'as' field must be remapped to 'as_number'
        self.assertNotIn("as", geo)
        self.assertEqual(geo["as_number"], "AS15169 Google LLC")
        # boolean fields
        self.assertFalse(geo["mobile"])
        self.assertFalse(geo["proxy"])
        self.assertTrue(geo["hosting"])

    @patch("requests.Session.request")
    def test_success_with_domain(self, mock_request):
        """A successful lookup for a domain should work identically to an IP lookup."""
        response_data = load_response("geolocate_ip_success.json")
        # Simulate a domain lookup — the API returns the same shape
        response_data = dict(response_data)
        response_data["query"] = "google-public-dns-a.google.com"
        mock_request.return_value = MockResponse(response_data, status_code=200)

        result = self.action.run({Input.QUERY: "google-public-dns-a.google.com", Input.LANG: "en"})

        self.assertIn(Output.RESULT, result)
        geo = result[Output.RESULT]
        self.assertEqual(geo["status"], "success")
        self.assertEqual(geo["query"], "google-public-dns-a.google.com")

    @patch("requests.Session.request")
    def test_success_with_non_default_lang(self, mock_request):
        """The lang parameter should be forwarded to the API."""
        response_data = load_response("geolocate_ip_success.json")
        mock_request.return_value = MockResponse(response_data, status_code=200)

        result = self.action.run({Input.QUERY: "8.8.8.8", Input.LANG: "de"})

        self.assertIn(Output.RESULT, result)
        # Verify the lang query param was sent
        call_kwargs = mock_request.call_args
        params = call_kwargs[1].get("params") or call_kwargs[0][2] if len(call_kwargs[0]) > 2 else {}
        # Extract params from kwargs dict
        params = mock_request.call_args.kwargs.get(
            "params", mock_request.call_args.args[2] if len(mock_request.call_args.args) > 2 else {}
        )
        self.assertEqual(params.get("lang"), "de")

    # ------------------------------------------------------------------
    # Failure / error-path tests
    # ------------------------------------------------------------------

    @patch("requests.Session.request")
    def test_fail_status_raises_plugin_exception(self, mock_request):
        """When the API returns status=fail the action must raise PluginException."""
        response_data = load_response("geolocate_ip_fail.json")
        mock_request.return_value = MockResponse(response_data, status_code=200)

        with self.assertRaises(PluginException) as context:
            self.action.run({Input.QUERY: "notanip", Input.LANG: "en"})

        self.assertIn("invalid query", str(context.exception.cause))
        self.assertIn("publicly routable", str(context.exception.assistance))

    @patch("requests.Session.request")
    def test_http_429_raises_rate_limit_exception(self, mock_request):
        """HTTP 429 responses must raise a rate-limited PluginException."""
        mock_request.return_value = MockResponse(
            {"error": "Too Many Requests"},
            status_code=429,
            headers={"X-Rl": "5", "X-Ttl": "30"},
        )

        with self.assertRaises(PluginException) as context:
            self.action.run({Input.QUERY: "8.8.8.8", Input.LANG: "en"})

        self.assertEqual(context.exception.preset, PluginException.Preset.RATE_LIMIT)

    @patch("requests.Session.request")
    def test_http_422_raises_bad_request_exception(self, mock_request):
        """HTTP 422 responses must raise a bad-request PluginException."""
        mock_request.return_value = MockResponse(
            {"error": "Unprocessable Entity"},
            status_code=422,
            headers={"X-Rl": "5", "X-Ttl": "30"},
        )

        with self.assertRaises(PluginException) as context:
            self.action.run({Input.QUERY: "8.8.8.8", Input.LANG: "en"})

        self.assertEqual(context.exception.preset, PluginException.Preset.BAD_REQUEST)

    @patch("requests.Session.request")
    def test_x_rl_zero_header_raises_rate_limit_exception(self, mock_request):
        """When X-Rl header is '0' a rate-limited PluginException must be raised."""
        response_data = load_response("geolocate_ip_success.json")
        mock_request.return_value = MockResponse(
            response_data,
            status_code=200,
            headers={"X-Rl": "0", "X-Ttl": "45"},
        )

        with self.assertRaises(PluginException) as context:
            self.action.run({Input.QUERY: "8.8.8.8", Input.LANG: "en"})

        self.assertIn("X-Rl", str(context.exception.cause))
        self.assertIn("45", str(context.exception.assistance))

    @patch("requests.Session.request")
    def test_http_500_raises_server_error_exception(self, mock_request):
        """HTTP 5xx responses must raise a server-error PluginException."""
        mock_request.return_value = MockResponse(
            {"error": "Internal Server Error"},
            status_code=500,
            headers={"X-Rl": "44", "X-Ttl": "60"},
        )

        with self.assertRaises(PluginException) as context:
            self.action.run({Input.QUERY: "8.8.8.8", Input.LANG: "en"})

        self.assertEqual(context.exception.preset, PluginException.Preset.SERVER_ERROR)

    @patch("requests.Session.request")
    def test_timeout_raises_timeout_exception(self, mock_request):
        """A requests.Timeout must be converted to a TIMEOUT PluginException."""
        import requests as req_lib

        mock_request.side_effect = req_lib.exceptions.Timeout("Connection timed out")

        with self.assertRaises(PluginException) as context:
            self.action.run({Input.QUERY: "8.8.8.8", Input.LANG: "en"})

        self.assertEqual(context.exception.preset, PluginException.Preset.TIMEOUT)

    @patch("requests.Session.request")
    def test_connection_error_raises_plugin_exception(self, mock_request):
        """A requests.ConnectionError must be converted to a PluginException."""
        import requests as req_lib

        mock_request.side_effect = req_lib.exceptions.ConnectionError("Network unreachable")

        with self.assertRaises(PluginException):
            self.action.run({Input.QUERY: "8.8.8.8", Input.LANG: "en"})

    @patch("requests.Session.request")
    def test_none_values_stripped_from_result(self, mock_request):
        """None values in the API response must not appear in the output dict."""
        response_data = load_response("geolocate_ip_success.json")
        response_data = dict(response_data)
        response_data["district"] = None
        mock_request.return_value = MockResponse(response_data, status_code=200)

        result = self.action.run({Input.QUERY: "8.8.8.8", Input.LANG: "en"})
        geo = result[Output.RESULT]
        self.assertNotIn("district", geo)


if __name__ == "__main__":
    unittest.main()
