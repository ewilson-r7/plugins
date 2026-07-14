import unittest
from unittest.mock import patch
from parameterized import parameterized

from insightconnect_plugin_runtime.exceptions import PluginException

from icon_ip_api.actions.geolocate_bulk.action import GeolocateBulk
from icon_ip_api.actions.geolocate_bulk.schema import Input, Output
from unit_test.util import MockResponse, default_connector, load_response


class TestGeolocateBulk(unittest.TestCase):
    """Unit tests for the geolocate_bulk action."""

    def setUp(self):
        self.action = default_connector(GeolocateBulk())

    # ------------------------------------------------------------------
    # Parameterized happy-path tests
    # ------------------------------------------------------------------

    @parameterized.expand(
        [
            (
                "two_ips",
                ["8.8.8.8", "1.1.1.1"],
                "en",
                "geolocate_bulk_success.json",
                2,
            ),
            (
                "single_ip_list",
                ["8.8.8.8"],
                "en",
                "geolocate_bulk_success.json",
                # Still returns as many entries as the mock provides; we check >= 1
                None,
            ),
        ]
    )
    @patch("requests.Session.request")
    def test_success(self, name, queries, lang, fixture, expected_count, mock_request):
        """Successful bulk lookups should return a list of geolocation results."""
        response_data = load_response(fixture)
        mock_request.return_value = MockResponse(response_data, status_code=200)

        result = self.action.run({Input.QUERIES: queries, Input.LANG: lang})

        self.assertIn(Output.RESULTS, result)
        results = result[Output.RESULTS]
        self.assertIsInstance(results, list)
        if expected_count is not None:
            self.assertEqual(len(results), expected_count)
        else:
            self.assertGreaterEqual(len(results), 1)

        # Verify each result has the as_number remapping and no raw 'as' key
        for geo in results:
            if geo.get("status") == "success":
                self.assertNotIn("as", geo)
                self.assertIn("as_number", geo)

    @parameterized.expand(
        [
            ("english", "en"),
            ("german", "de"),
            ("japanese", "ja"),
        ]
    )
    @patch("requests.Session.request")
    def test_lang_parameter_forwarded(self, name, lang, mock_request):
        """The lang parameter must be forwarded as a query param to the API."""
        response_data = load_response("geolocate_bulk_success.json")
        mock_request.return_value = MockResponse(response_data, status_code=200)

        self.action.run({Input.QUERIES: ["8.8.8.8"], Input.LANG: lang})

        call_kwargs = mock_request.call_args.kwargs
        params = call_kwargs.get("params", {})
        self.assertEqual(params.get("lang"), lang)

    # ------------------------------------------------------------------
    # Validation tests
    # ------------------------------------------------------------------

    def test_too_many_queries_raises_plugin_exception(self):
        """Submitting more than 100 queries must raise a PluginException before any HTTP call."""
        too_many = [f"10.0.{i // 256}.{i % 256}" for i in range(101)]

        with self.assertRaises(PluginException) as context:
            self.action.run({Input.QUERIES: too_many, Input.LANG: "en"})

        exc = context.exception
        self.assertIn("101", str(exc.cause))
        self.assertIn("100", str(exc.assistance))

    def test_exactly_100_queries_does_not_raise_before_http(self):
        """Exactly 100 queries should pass validation (no pre-HTTP exception)."""
        exactly_100 = [f"10.0.{i // 256}.{i % 256}" for i in range(100)]

        # We expect an HTTP error (no mock set up) or success — just confirm no
        # PluginException from our own validation code.  We patch the session so
        # no real network call is made.
        with patch("requests.Session.request") as mock_request:
            response_data = load_response("geolocate_bulk_success.json")
            mock_request.return_value = MockResponse(response_data, status_code=200)
            # Should not raise
            result = self.action.run({Input.QUERIES: exactly_100, Input.LANG: "en"})
            self.assertIn(Output.RESULTS, result)

    # ------------------------------------------------------------------
    # HTTP error tests
    # ------------------------------------------------------------------

    @patch("requests.Session.request")
    def test_http_429_raises_rate_limit_exception(self, mock_request):
        """HTTP 429 on the batch endpoint must raise a rate-limited PluginException."""
        mock_request.return_value = MockResponse(
            {"error": "Too Many Requests"},
            status_code=429,
            headers={"X-Rl": "5", "X-Ttl": "60"},
        )

        with self.assertRaises(PluginException) as context:
            self.action.run({Input.QUERIES: ["8.8.8.8", "1.1.1.1"], Input.LANG: "en"})

        self.assertEqual(context.exception.preset, PluginException.Preset.RATE_LIMIT)

    @patch("requests.Session.request")
    def test_http_422_raises_bad_request_exception(self, mock_request):
        """HTTP 422 on the batch endpoint must raise a bad-request PluginException."""
        mock_request.return_value = MockResponse(
            {"error": "Unprocessable Entity"},
            status_code=422,
            headers={"X-Rl": "5", "X-Ttl": "60"},
        )

        with self.assertRaises(PluginException) as context:
            self.action.run({Input.QUERIES: ["8.8.8.8", "1.1.1.1"], Input.LANG: "en"})

        self.assertEqual(context.exception.preset, PluginException.Preset.BAD_REQUEST)

    @patch("requests.Session.request")
    def test_x_rl_zero_header_raises_rate_limit_exception(self, mock_request):
        """X-Rl: 0 header on a successful response must still raise a PluginException."""
        response_data = load_response("geolocate_bulk_success.json")
        mock_request.return_value = MockResponse(
            response_data,
            status_code=200,
            headers={"X-Rl": "0", "X-Ttl": "30"},
        )

        with self.assertRaises(PluginException) as context:
            self.action.run({Input.QUERIES: ["8.8.8.8", "1.1.1.1"], Input.LANG: "en"})

        self.assertIn("X-Rl", str(context.exception.cause))
        self.assertIn("30", str(context.exception.assistance))

    @patch("requests.Session.request")
    def test_http_500_raises_server_error_exception(self, mock_request):
        """HTTP 5xx on the batch endpoint must raise a server-error PluginException."""
        mock_request.return_value = MockResponse(
            {"error": "Internal Server Error"},
            status_code=500,
            headers={"X-Rl": "14", "X-Ttl": "60"},
        )

        with self.assertRaises(PluginException) as context:
            self.action.run({Input.QUERIES: ["8.8.8.8", "1.1.1.1"], Input.LANG: "en"})

        self.assertEqual(context.exception.preset, PluginException.Preset.SERVER_ERROR)

    @patch("requests.Session.request")
    def test_partial_fail_entries_included_in_results(self, mock_request):
        """Individual fail entries in a batch response should appear in results, not raise."""
        mixed_response = [
            {
                "status": "success",
                "country": "United States",
                "countryCode": "US",
                "as": "AS15169 Google LLC",
                "query": "8.8.8.8",
            },
            {
                "status": "fail",
                "message": "private range",
                "query": "192.168.1.1",
            },
        ]
        mock_request.return_value = MockResponse(mixed_response, status_code=200)

        result = self.action.run({Input.QUERIES: ["8.8.8.8", "192.168.1.1"], Input.LANG: "en"})

        results = result[Output.RESULTS]
        self.assertEqual(len(results), 2)
        statuses = [r["status"] for r in results]
        self.assertIn("success", statuses)
        self.assertIn("fail", statuses)

    @patch("requests.Session.request")
    def test_timeout_raises_timeout_exception(self, mock_request):
        """A requests.Timeout on the batch endpoint must raise a TIMEOUT PluginException."""
        import requests as req_lib

        mock_request.side_effect = req_lib.exceptions.Timeout("Connection timed out")

        with self.assertRaises(PluginException) as context:
            self.action.run({Input.QUERIES: ["8.8.8.8"], Input.LANG: "en"})

        self.assertEqual(context.exception.preset, PluginException.Preset.TIMEOUT)


if __name__ == "__main__":
    unittest.main()
