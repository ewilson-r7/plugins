import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from icon_rapid7_velociraptor.connection.connection import Connection
from icon_rapid7_velociraptor.actions.get_client import GetClient
import json
import logging


class TestGetClient(TestCase):
    def test_get_client(self):
        """
        DO NOT USE PRODUCTION/SENSITIVE DATA FOR UNIT TESTS

        TODO: Implement test cases here
        """

        self.fail("Unimplemented Test Case")
