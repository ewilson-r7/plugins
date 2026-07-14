import os
import sys

from insightconnect_plugin_runtime.exceptions import PluginException

sys.path.append(os.path.abspath("../"))

import logging
from unittest import TestCase
from unittest.mock import Mock

from icon_microsoft_office365_email_security.actions.message_trace import MessageTrace
from icon_microsoft_office365_email_security.actions.message_trace.schema import Input, Output
from icon_microsoft_office365_email_security.connection.connection import Connection
from jsonschema import validate


class TestMessageTrace(TestCase):
    def setUp(self) -> None:
        log = logging.getLogger("Test")
        test_conn = Connection()
        test_action = MessageTrace()
        test_conn.client = Mock()
        test_conn.logger = log
        test_action.logger = log
        test_action.connection = test_conn
        self.action = test_action
        return super().setUp()

    def test_success_mass_purge(self):
        COMPLETION_MESSAGE = """Success - trace follows: 
        [
          {
            "PSComputerName":"outlook.office365.com",
            "RunspaceId":"1111",
            "PSShowComputerName":false,
            "Organization":"example.com",
            "MessageId":"1111",
            "Received":"2022-07-25T15:48:38.5260938",
            "SenderAddress":"example@example.com",
            "RecipientAddress":"1221",
            "Subject":"screenshot",
            "Status":"Delivered",
            "ToIP":"12",
            "FromIP":"2342",
            "Size":19539,
            "MessageTraceId":"111",
            "Index":41
          }
        ]
        """
        self.action.connection.client.configure_mock(**{"message_trace.return_value": (COMPLETION_MESSAGE, None)})
        result = self.action.run(
            params={
                Input.START_DATE: "2022-12-01",
                Input.END_DATE: "2022-12-02",
                Input.SENDER_ADDRESS: "js@mi.c",
            }
        )
        validate(result, self.action.output.schema)
        expected_output = {
            Output.MESSAGE_TRACES: [
                {
                    "PSComputerName": "outlook.office365.com",
                    "RunspaceId": "1111",
                    "PSShowComputerName": False,
                    "Organization": "example.com",
                    "MessageId": "1111",
                    "Received": "2022-07-25T15:48:38.5260938",
                    "SenderAddress": "example@example.com",
                    "RecipientAddress": "1221",
                    "Subject": "screenshot",
                    "Status": "Delivered",
                    "ToIP": "12",
                    "FromIP": "2342",
                    "Size": 19539,
                    "MessageTraceId": "111",
                    "Index": 41,
                }
            ]
        }
        self.assertEqual(result, expected_output)

    def test_exception_mass_purge(self):
        COMPLETION_MESSAGE = "Script not complete"
        self.action.connection.client.configure_mock(
            **{
                "message_trace.return_value": (
                    COMPLETION_MESSAGE,
                    "Nique toi, you got an error!",
                )
            }
        )
        with self.assertRaises(PluginException) as cm:
            self.action.run(
                params={
                    "start_date": "2022-12-01",
                    "end_date": "2022-12-02",
                    "Sender_address": "user@example.com",
                }
            )
            self.assertEqual(cm.exception.cause, "Powershell returned an error.")
