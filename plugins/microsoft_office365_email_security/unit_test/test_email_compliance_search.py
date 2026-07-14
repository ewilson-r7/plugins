import os
import sys

sys.path.append(os.path.abspath("../"))

import logging
from unittest import TestCase
from unittest.mock import Mock

from icon_microsoft_office365_email_security.actions.email_compliance_search import EmailComplianceSearch
from icon_microsoft_office365_email_security.actions.email_compliance_search.schema import Output
from icon_microsoft_office365_email_security.connection.connection import Connection
from insightconnect_plugin_runtime.exceptions import PluginException
from jsonschema import validate


class TestEmailCompilanceSearch(TestCase):
    def setUp(self) -> None:
        self.TESTED_METHOD = "email_compliance_search"
        log = logging.getLogger("Test")
        test_conn = Connection()
        test_action = EmailComplianceSearch()
        test_conn.client = Mock()
        test_conn.logger = log
        test_action.logger = log
        test_action.connection = test_conn
        self.action = test_action
        return super().setUp()

    def test_success_block_email_compliance_search(self):
        COMPLETION_MESSAGE = b"""
            @{SearchStatistics={"ExchangeBinding":{"Search":{"Name":null,"Sources":"2","SourcesRaw":2,"ContentItems":59,"ContentSize":"4.43 MB","ContentSizeRaw":4646094,"HasFaults":false},"Queries":[{"Name":"_PrimaryQuery","Sources":"2","SourcesRaw":2,"ContentItems":59,"ContentSize":"4.43 MB","ContentSizeRaw":4646094,"Type":"Primary"},{"Name":"_UnindexedQuery","Sources":"2","SourcesRaw":2,"ContentItems":42,"ContentSize":"79.74 MB","ContentSizeRaw":4646094,"Query":"((IndexingErrorCode\u003c0) OR (IndexingErrorCode\u003e0) OR (IsPartiallyIndexed=True))","Type":"Unindexed"}],"Sources":[{"Name":"user2@example.com","ContentItems":32,"ContentSize":"1.55 MB"},{"Name":"user1@example.com","ContentItems":27,"ContentSize":"2.88 MB"},{"Name":"nickname_goes_here@example.com","ContentItems":0,"ContentSize":"0 B"},{"Name":"Integrations@example.com","ContentItems":0,"ContentSize":"0 B"},{"Name":"eventsources@example.com","ContentItems":0,"ContentSize":"0 B"},{"Name":"change_me@example.com","ContentItems":0,"ContentSize":"0 B"},{"Name":"Testforcustomer@example.com","ContentItems":0,"ContentSize":"0 B"},{"Name":"demo@example.com","ContentItems":0,"ContentSize":"0 B"},{"Name":"Komand-Test-Everyone@example.com","ContentItems":0,"ContentSize":"0 B"},{"Name":"R7-Security@example.com","ContentItems":0,"ContentSize":"0 B"},{"Name":"user1@example.com","ContentItems":0,"ContentSize":"0 B"},{"Name":"pm_user1@example.com","ContentItems":0,"ContentSize":"0 B"},{"Name":"AzureADTestGroup@example.com","ContentItems":0,"ContentSize":"0 B"},{"Name":"AllCompany.10249927.ncpgxunu@example.com","ContentItems":0,"ContentSize":"0 B"},{"Name":"DreamTeam@example.com","ContentItems":0,"ContentSize":"0 B"},{"Name":"change_me887@example.com","ContentItems":0,"ContentSize":"0 B"}]}}}
        """
        self.action.connection.client.configure_mock(
            **{
                f"{self.TESTED_METHOD}.return_value": (
                    COMPLETION_MESSAGE.decode("utf-8"),
                    None,
                )
            }
        )
        result = self.action.run()
        validate(result, self.action.output.schema)
        self.assertEqual(
            result,
            {
                Output.AFFECTED_USERS: 2,
                Output.EMAILS_FOUND: 59,
                Output.USERS: ["user2@example.com", "user1@example.com"],
            },
        )

    def test_exception_email_compliance_search(self):
        COMPLETION_MESSAGE = "Script not complete"
        self.action.connection.client.configure_mock(
            **{
                f"{self.TESTED_METHOD}.return_value": (
                    COMPLETION_MESSAGE,
                    "Nique toi, you got an error!",
                )
            }
        )
        with self.assertRaises(PluginException) as context_manager:
            self.action.run()
        self.assertEqual(
            context_manager.exception.cause,
            "PowerShell returned an unexpected response.",
        )
