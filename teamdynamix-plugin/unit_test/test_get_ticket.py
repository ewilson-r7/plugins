import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from icon_teamdynamix.connection.connection import Connection
from icon_teamdynamix.actions.get_ticket import GetTicket
import json
import logging


class TestGetTicket(TestCase):
    def test_get_ticket(self):
        """
        DO NOT USE PRODUCTION/SENSITIVE DATA FOR UNIT TESTS

        TODO: Implement test cases here
        """

        self.fail("Unimplemented Test Case")
