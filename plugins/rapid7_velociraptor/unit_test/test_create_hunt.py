import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase
from icon_rapid7_velociraptor.connection.connection import Connection
from icon_rapid7_velociraptor.actions.create_hunt import CreateHunt
import json
import logging


class TestCreateHunt(TestCase):
    def test_create_hunt(self):
        """
        DO NOT USE PRODUCTION/SENSITIVE DATA FOR UNIT TESTS

        TODO: Implement test cases here
        """

        self.fail("Unimplemented Test Case")
