import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from icon_teamdynamix.connection.connection import Connection
from icon_teamdynamix.actions.search_tickets import SearchTickets
import json
import logging


class TestSearchTickets(TestCase):
    def test_search_tickets(self):
        """
        DO NOT USE PRODUCTION/SENSITIVE DATA FOR UNIT TESTS

        TODO: Implement test cases here
        """

        self.fail("Unimplemented Test Case")
