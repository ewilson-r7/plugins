import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from icon_teamdynamix.connection.connection import Connection
from icon_teamdynamix.actions.update_ticket import UpdateTicket
import json
import logging


class TestUpdateTicket(TestCase):
    def test_update_ticket(self):
        """
        DO NOT USE PRODUCTION/SENSITIVE DATA FOR UNIT TESTS

        TODO: Implement test cases here
        """

        self.fail("Unimplemented Test Case")
