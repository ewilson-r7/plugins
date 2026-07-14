import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from icon_microsoft_office365_email_security.connection.connection import Connection
from icon_microsoft_office365_email_security.actions.update_list_of_blocked_domains import UpdateListOfBlockedDomains
import json
import logging


class TestUpdateListOfBlockedDomains(TestCase):
    def test_update_list_of_blocked_domains(self):
        """
        DO NOT USE PRODUCTION/SENSITIVE DATA FOR UNIT TESTS

        TODO: Implement test cases here
        """

        self.fail("Unimplemented Test Case")
