import os
import sys

from insightconnect_plugin_runtime.exceptions import PluginException

sys.path.append(os.path.abspath("../"))

import logging
from unittest import TestCase
from unittest.mock import Mock

from icon_microsoft_office365_email_security.actions.mass_search_and_purge import MassSearchAndPurge
from icon_microsoft_office365_email_security.actions.mass_search_and_purge.schema import Output
from icon_microsoft_office365_email_security.connection.connection import Connection
from jsonschema import validate


class TestMassSearchAndPurge(TestCase):
    def setUp(self) -> None:
        log = logging.getLogger("Test")
        test_conn = Connection()
        test_action = MassSearchAndPurge()
        test_conn.client = Mock()
        test_conn.logger = log
        test_action.logger = log
        test_action.connection = test_conn
        self.action = test_action
        return super().setUp()

    def test_success_mass_purge(self):
        COMPLETION_MESSAGE = "Success!"
        self.action.connection.client.configure_mock(
            **{"mass_search_and_purge.return_value": (COMPLETION_MESSAGE, None)}
        )
        result = self.action.run()
        validate(result, self.action.output.schema)
        self.assertEqual(result, {Output.SUCCESS: True})

    def test_exception_mass_purge(self):
        COMPLETION_MESSAGE = "Script not complete"
        self.action.connection.client.configure_mock(
            **{
                "mass_search_and_purge.return_value": (
                    COMPLETION_MESSAGE,
                    "Nique toi, you got an error!",
                )
            }
        )
        with self.assertRaises(PluginException) as cm:
            self.action.run()
            self.assertEqual(cm.exception.cause, "Powershell returned an error.")
