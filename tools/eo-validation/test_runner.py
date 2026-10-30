"""Adversarial receipt contracts: successful exit is insufficient."""

import copy
import unittest

from run_checks import INDEPENDENT_CASES, validate_independent, validate_unit


class RunnerGateTests(unittest.TestCase):
    def setUp(self):
        self.inputs = {"encoding_guard/guard.py": "guard-hash", "yemen/a": "input-hash"}
        self.expected = ["module.Case.test_a", "module.Case.test_b"]
        self.run_id = "current-run"
        self.unit = {
            "schema": "eo-unit-v1",
            "run_id": self.run_id,
            "tests_run": 2,
            "successful": True,
            "executed_ids": self.expected.copy(),
            "failures": [],
            "errors": [],
            "skipped": [],
            "expected_failures": [],
            "unexpected_successes": [],
            "input_sha256": self.inputs.copy(),
            "manifest_sha256": "manifest-hash",
            "inputs_unchanged": True,
        }
        self.review = {
            "schema": "eo-independent-v1",
            "run_id": self.run_id,
            "all_passed": True,
            "guard_sha256": "guard-hash",
            "input_sha256": {"yemen/a": "input-hash"},
            "source_inputs_unchanged": True,
            "cases": [{"case": name, "passed": True} for name in sorted(INDEPENDENT_CASES)],
        }

    def unit_check(self, receipt):
        return validate_unit(receipt, self.expected, self.inputs, "manifest-hash", self.run_id)

    def review_check(self, receipt):
        return validate_independent(receipt, self.inputs, self.run_id)

    def test_valid_receipts(self):
        self.unit_check(self.unit)
        self.review_check(self.review)

    def test_zero_unit_tests_not_success(self):
        self.unit.update(tests_run=0, executed_ids=[])
        with self.assertRaises(ValueError):
            self.unit_check(self.unit)

    def test_unit_count_or_identity_forgery(self):
        for change in [
            {"tests_run": True},
            {"tests_run": 1},
            {"executed_ids": ["module.Case.test_a"] * 2},
            {"executed_ids": ["module.Case.test_a", "module.Case.unknown"]},
        ]:
            with self.subTest(change=change):
                value = copy.deepcopy(self.unit)
                value.update(change)
                with self.assertRaises(ValueError):
                    self.unit_check(value)

    def test_unit_nonpass_outcomes_rejected(self):
        for key in ["failures", "errors", "skipped", "expected_failures", "unexpected_successes"]:
            with self.subTest(key=key):
                value = copy.deepcopy(self.unit)
                value[key] = ["module.Case.test_a"]
                with self.assertRaises(ValueError):
                    self.unit_check(value)

    def test_unit_missing_outcome_fields_rejected(self):
        del self.unit["skipped"]
        with self.assertRaises(ValueError):
            self.unit_check(self.unit)

    def test_unit_hashes_and_run_identity(self):
        for key, value in [
            ("input_sha256", {}),
            ("manifest_sha256", "wrong"),
            ("run_id", "stale-run"),
            ("inputs_unchanged", False),
            ("successful", 1),
        ]:
            with self.subTest(key=key):
                receipt = copy.deepcopy(self.unit)
                receipt[key] = value
                with self.assertRaises(ValueError):
                    self.unit_check(receipt)

    def test_independent_duplicates_and_wrong_case(self):
        for name in [self.review["cases"][0]["case"], "unknown_case"]:
            value = copy.deepcopy(self.review)
            value["cases"][1]["case"] = name
            with self.assertRaises(ValueError):
                self.review_check(value)

    def test_independent_hidden_false_and_nonboolean(self):
        for passed in [False, 1, "true", None]:
            value = copy.deepcopy(self.review)
            value["cases"][0]["passed"] = passed
            with self.assertRaises(ValueError):
                self.review_check(value)

    def test_independent_count_mismatch(self):
        self.review["cases"].pop()
        with self.assertRaises(ValueError):
            self.review_check(self.review)

    def test_independent_hashes_and_run_identity(self):
        for key, value in [
            ("guard_sha256", "wrong"),
            ("input_sha256", {}),
            ("source_inputs_unchanged", False),
            ("run_id", "stale-run"),
            ("all_passed", 1),
        ]:
            with self.subTest(key=key):
                receipt = copy.deepcopy(self.review)
                receipt[key] = value
                with self.assertRaises(ValueError):
                    self.review_check(receipt)

    def test_malformed_receipts_fail_closed(self):
        for value in [None, [], {}, {"cases": None}, {"cases": [None] * 18}]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.review_check(value)
                with self.assertRaises(ValueError):
                    self.unit_check(value)


if __name__ == "__main__":
    unittest.main(verbosity=2)
