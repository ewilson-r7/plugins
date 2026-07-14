import os
import sys

sys.path.append(os.path.abspath("../"))

import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch

from icon_microsoft_office365_email_security.connection.connection import Connection
from icon_microsoft_office365_email_security.connection.schema import Input
from insightconnect_plugin_runtime.exceptions import ConnectionTestException

STUB_CONNECTION = {Input.CREDENTIALS: {"username": "ExampleUsername", "password": "ExamplePassword"}}


class TestConnectionTest(TestCase):
    def setUp(self) -> None:
        self.connection = Connection()
        self.connection.logger = logging.getLogger("Connection Logger")
        self.connection.connect(STUB_CONNECTION)

    @patch(
        "icon_microsoft_office365_email_security.util.api.MicrosoftCommunicationAPI.test_connection",
        return_value=(b"Test", None),
    )
    def test_connection_test(self, mock_test: MagicMock) -> None:
        response = self.connection.test()
        self.assertEqual(response, {"result": True})

    @patch(
        "icon_microsoft_office365_email_security.util.api.MicrosoftCommunicationAPI.test_connection",
        return_value=(b"Test", b"Error"),
    )
    def test_connection_test_error(self, mock_test: MagicMock) -> None:
        with self.assertRaises(ConnectionTestException) as context:
            self.connection.test()
        self.assertEqual(
            context.exception.cause, ConnectionTestException.causes[ConnectionTestException.Preset.UNAUTHORIZED]
        )
        self.assertEqual(
            context.exception.assistance,
            ConnectionTestException.assistances[ConnectionTestException.Preset.UNAUTHORIZED],
        )
