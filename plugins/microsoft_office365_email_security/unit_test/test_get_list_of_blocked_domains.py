import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from icon_microsoft_office365_email_security.connection.connection import Connection
from icon_microsoft_office365_email_security.actions.get_list_of_blocked_domains import GetListOfBlockedDomains
import json
import logging


class TestGetListOfBlockedDomains(TestCase):
    def test_get_list_of_blocked_domains(self):
        """
        DO NOT USE PRODUCTION/SENSITIVE DATA FOR UNIT TESTS

        TODO: Implement test cases here
        """

        self.fail("Unimplemented Test Case")
