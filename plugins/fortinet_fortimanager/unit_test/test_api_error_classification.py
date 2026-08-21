"""Unit coverage for FortiManagerPluginException condition classification.

FortiManager reports the same logical condition under different status codes
depending on version and endpoint. 3.0.0 matched on the status code alone, which
missed the duplicate-object case the customer hit: the API returns -2 with the
message "Object already exists" rather than the documented -6. These tests pin both
halves of the classification so neither a re-coded nor a re-worded error slips past.
"""

import sys
import os

sys.path.append(os.path.abspath("../"))

from unittest import TestCase

from icon_fortinet_fortimanager.util.api import FortiManagerPluginException


def _error(code: int, message: str = "") -> FortiManagerPluginException:
    return FortiManagerPluginException(
        code=code,
        api_message=message,
        cause=f"FortiManager API error (code {code}): {message}",
        assistance="Verify the input parameters and ADOM configuration.",
    )


class TestObjectAlreadyExists(TestCase):
    def test_documented_code_matches(self):
        self.assertTrue(_error(-6, "Object already exists (naming conflict)").object_already_exists)

    def test_code_matches_even_without_a_message(self):
        self.assertTrue(_error(-6).object_already_exists)

    def test_message_matches_under_generic_code(self):
        """The real customer response: code -2 with 'Object already exists'."""
        self.assertTrue(_error(-2, "Object already exists").object_already_exists)

    def test_message_match_is_case_insensitive(self):
        self.assertTrue(_error(-2, "OBJECT ALREADY EXISTS").object_already_exists)

    def test_duplicate_wording_matches(self):
        self.assertTrue(_error(-2, "duplicate entry").object_already_exists)

    def test_genuine_invalid_params_does_not_match(self):
        """-2 is the generic invalid-params code and must not be swallowed."""
        self.assertFalse(_error(-2, "Invalid value for attribute subnet").object_already_exists)

    def test_empty_message_under_generic_code_does_not_match(self):
        self.assertFalse(_error(-2).object_already_exists)


class TestObjectNotExist(TestCase):
    def test_documented_code_matches(self):
        self.assertTrue(_error(-3, "Object does not exist").object_not_exist)

    def test_message_matches_under_other_code(self):
        self.assertTrue(_error(-2, "no such object").object_not_exist)

    def test_already_exists_is_not_read_as_absent(self):
        """'Object already exists' must not satisfy the absent condition."""
        self.assertFalse(_error(-2, "Object already exists").object_not_exist)

    def test_unrelated_error_does_not_match(self):
        self.assertFalse(_error(-1, "No permission for the resource").object_not_exist)


class TestObjectInUse(TestCase):
    def test_documented_code_matches(self):
        self.assertTrue(_error(-10015, "used").object_in_use)

    def test_bare_used_message_matches_exactly(self):
        self.assertTrue(_error(-2, "used").object_in_use)

    def test_unused_does_not_false_positive(self):
        """'used' is matched against the whole message because it occurs inside 'unused'."""
        self.assertFalse(_error(-2, "attribute is unused").object_in_use)

    def test_phrase_variants_match(self):
        self.assertTrue(_error(-2, "object is in use by addrgrp").object_in_use)
        self.assertTrue(_error(-2, "still referenced by a policy").object_in_use)
        self.assertTrue(_error(-2, "used by other objects").object_in_use)

    def test_unrelated_error_does_not_match(self):
        self.assertFalse(_error(-1, "No permission for the resource").object_in_use)


class TestExceptionRemainsAPluginException(TestCase):
    def test_carries_code_and_message(self):
        error = _error(-2, "Object already exists")

        self.assertEqual(error.code, -2)
        self.assertEqual(error.api_message, "Object already exists")

    def test_missing_message_defaults_to_empty_string(self):
        """api_message must be a string so the predicates can normalize it."""
        self.assertEqual(FortiManagerPluginException(code=-2, cause="x", assistance="y").api_message, "")
