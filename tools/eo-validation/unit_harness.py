"""Structured unittest execution; the caller validates an independent static contract."""

import argparse
import hashlib
import json
import sys
import unittest
from pathlib import Path

from run_checks import ROOT, expected_test_ids, validate_unit, verify_manifest


class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.executed_ids = []

    def startTest(self, test):
        self.executed_ids.append(test.id())
        super().startTest(test)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    inputs = verify_manifest()
    manifest_hash = hashlib.sha256((ROOT / "manifest.json").read_bytes()).hexdigest()
    expected = expected_test_ids()
    sys.path.insert(0, str(ROOT / "encoding_guard"))
    suite = unittest.defaultTestLoader.loadTestsFromNames(["test_guard", "test_runner"])
    result = unittest.TextTestRunner(verbosity=2, resultclass=RecordedResult).run(suite)
    receipt = {
        "schema": "eo-unit-v1",
        "run_id": args.run_id,
        "tests_run": result.testsRun,
        "successful": result.wasSuccessful(),
        "executed_ids": result.executed_ids,
        "failures": [t.id() for t, _ in result.failures],
        "errors": [t.id() for t, _ in result.errors],
        "skipped": [t.id() for t, _ in result.skipped],
        "expected_failures": [t.id() for t, _ in result.expectedFailures],
        "unexpected_successes": [t.id() for t in result.unexpectedSuccesses],
        "input_sha256": inputs,
        "manifest_sha256": manifest_hash,
        "inputs_unchanged": inputs == verify_manifest(),
    }
    accepted = True
    try:
        validate_unit(receipt, expected, inputs, manifest_hash, args.run_id)
    except ValueError as exc:
        accepted = False
        receipt["contract_error"] = str(exc)
    args.output.write_text(json.dumps(receipt, indent=2, allow_nan=False))
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
