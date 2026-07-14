import os
import sys

sys.path.append(os.path.abspath("../"))

import logging
from unittest import TestCase
from unittest.mock import Mock

from icon_microsoft_office365_email_security.actions.block_sender_transport_rule import BlockSenderTransportRule
from icon_microsoft_office365_email_security.actions.block_sender_transport_rule.action import (
    Input,
    Output,
)
from icon_microsoft_office365_email_security.connection.connection import Connection
from insightconnect_plugin_runtime.exceptions import PluginException
from jsonschema import validate


class TestBlockSenderTransportRule(TestCase):
    def setUp(self) -> None:
        self.TESTED_METHOD = "block_sender_transport_rule"
        log = logging.getLogger("Test")
        test_conn = Connection()
        test_action = BlockSenderTransportRule()
        test_conn.client = Mock()
        test_conn.logger = log
        test_action.logger = log
        test_action.connection = test_conn
        self.action = test_action
        return super().setUp()

    def test_success_block_sender_transport_rule(self):
        COMPLETION_MESSAGE = b"Blocking Finished"
        self.action.connection.client.configure_mock(
            **{f"{self.TESTED_METHOD}.return_value": (COMPLETION_MESSAGE, None)}
        )
        result = self.action.run()
        validate(result, self.action.output.schema)
        self.assertEqual(result, {Output.RESULT: "Success"})

    def test_exception_block_sender_transport_rule(self):
        COMPLETION_MESSAGE = b"Script not complete"
        self.action.connection.client.configure_mock(
            **{
                f"{self.TESTED_METHOD}.return_value": (
                    COMPLETION_MESSAGE,
                    b"Nique toi, you got an error!",
                )
            }
        )
        with self.assertRaises(PluginException) as context_manager:
            self.action.run()
        self.assertEqual(context_manager.exception.cause, "Powershell returned an error.")

    def test_success_block_different_senders_for_same_transport_rule(self):
        COMPLETION_MESSAGE = b"Blocking Finished"
        self.action.connection.client.configure_mock(
            **{f"{self.TESTED_METHOD}.return_value": (COMPLETION_MESSAGE, None)}
        )
        result = self.action.run(
            {
                Input.DOMAIN_OR_EMAIL_TO_BLOCK: "test1@rapid7.com",
                Input.TRANSPORT_RULE_NAME: "test",
            }
        )
        second_result = self.action.run(
            {
                Input.DOMAIN_OR_EMAIL_TO_BLOCK: "test2@rapid7.com",
                Input.TRANSPORT_RULE_NAME: "test",
            }
        )
        validate(result, self.action.output.schema)
        validate(second_result, self.action.output.schema)
        self.assertEqual(result, {Output.RESULT: "Success"})
        self.assertEqual(second_result, {Output.RESULT: "Success"})
