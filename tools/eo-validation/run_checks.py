"""Run pinned offline research checks with explicit receipt contracts."""

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SAMPLES = ("yemen", "yemen_march_selected", "yemen_december_fixed_window")
INDEPENDENT_CASES = frozenset(
    [
        "scl_asset_transform_mismatch",
        "scl_source_window_mismatch",
        "nonfinite_raw",
        "zero_denominator",
        "product_mismatch",
        "grid_mismatch",
        "missing_offset",
        "shape_mismatch",
        "unknown_flag",
        "all_invalid",
        "nodata_zero_without_mask",
        "scl_shift",
        "scl_url_mismatch",
        "quality_flags_no_clamp",
        "real_yemen",
        "real_yemen_march_selected",
        "real_yemen_december_fixed_window",
        "source_and_inputs_unchanged",
    ]
)


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def verify_manifest():
    expected = json.loads((ROOT / "manifest.json").read_text())["files"]
    require(isinstance(expected, dict) and bool(expected), "Empty or invalid manifest")
    required = {
        "run_checks.py",
        "unit_harness.py",
        "expected_tests.json",
        "test_runner.py",
        "encoding_guard/guard.py",
        "encoding_guard/test_guard.py",
        "encoding_guard_review/review.py",
    }
    require(required <= expected.keys(), "Manifest omits required executable or contract")
    actual = {}
    for name, digest in expected.items():
        relative = Path(name)
        require(not relative.is_absolute() and ".." not in relative.parts, "Invalid manifest path: " + name)
        path = ROOT / relative
        require(not path.is_symlink() and path.is_file(), "Missing or symlinked input: " + name)
        actual[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        require(actual[name] == digest, "Input hash mismatch: " + name)
    return actual


def expected_test_ids():
    value = json.loads((ROOT / "expected_tests.json").read_text())
    require(isinstance(value, list) and bool(value), "Empty unit test contract")
    require(all(isinstance(v, str) and v for v in value), "Invalid test identity")
    require(len(value) == len(set(value)), "Duplicate expected test identity")
    return value


def validate_unit(receipt, expected, inputs, manifest_hash, run_id):
    require(isinstance(receipt, dict), "Invalid unit receipt")
    require(receipt.get("schema") == "eo-unit-v1", "Wrong unit receipt schema")
    require(receipt.get("run_id") == run_id and isinstance(run_id, str) and bool(run_id), "Unit run identity mismatch")
    require(receipt.get("successful") is True, "Unit receipt not successful")
    require(type(receipt.get("tests_run")) is int and receipt["tests_run"] == len(expected), "Unit count mismatch")
    ids = receipt.get("executed_ids")
    require(isinstance(ids, list) and all(isinstance(v, str) for v in ids), "Missing executed unit identities")
    require(
        len(ids) == len(set(ids)) == len(expected) and set(ids) == set(expected), "Executed unit identities mismatch"
    )
    for key in ("failures", "errors", "skipped", "expected_failures", "unexpected_successes"):
        require(receipt.get(key) == [], "Unaccepted unit outcome: " + key)
    require(receipt.get("input_sha256") == inputs, "Unit input/code hashes mismatch")
    require(receipt.get("manifest_sha256") == manifest_hash, "Unit manifest mismatch")
    require(receipt.get("inputs_unchanged") is True, "Unit inputs changed")


def validate_independent(receipt, inputs, run_id):
    require(isinstance(receipt, dict), "Invalid independent receipt")
    require(receipt.get("schema") == "eo-independent-v1", "Wrong independent schema")
    require(
        receipt.get("run_id") == run_id and isinstance(run_id, str) and bool(run_id),
        "Independent run identity mismatch",
    )
    require(receipt.get("all_passed") is True, "Independent summary not successful")
    cases = receipt.get("cases")
    require(isinstance(cases, list) and len(cases) == len(INDEPENDENT_CASES), "Independent count mismatch")
    require(
        all(isinstance(c, dict) and isinstance(c.get("case"), str) and c.get("passed") is True for c in cases),
        "Independent case not explicitly passed",
    )
    ids = [c["case"] for c in cases]
    require(len(set(ids)) == len(ids) and set(ids) == INDEPENDENT_CASES, "Independent identities mismatch")
    require(receipt.get("guard_sha256") == inputs["encoding_guard/guard.py"], "Independent guard hash mismatch")
    expected_inputs = {k: v for k, v in inputs.items() if k.split("/")[0] in SAMPLES}
    require(receipt.get("input_sha256") == expected_inputs, "Independent input hashes mismatch")
    require(receipt.get("source_inputs_unchanged") is True, "Independent source or inputs changed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True, help="New output directory outside this package")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output == ROOT or ROOT in output.parents:
        parser.error("Output directory must be outside the package")
    try:
        before = verify_manifest()
        expected = expected_test_ids()
        manifest_hash = hashlib.sha256((ROOT / "manifest.json").read_bytes()).hexdigest()
        import numpy

        require(numpy.__version__ == "2.5.4", "Use the tested dependency numpy==2.5.4")
        output.mkdir(parents=True, exist_ok=False)
    except (OSError, ValueError, ImportError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}))
        return 2
    run_id = uuid.uuid4().hex
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    stages = [
        (
            "unit",
            [sys.executable, str(ROOT / "unit_harness.py"), "--output", str(output / "unit.json"), "--run-id", run_id],
        ),
        (
            "independent",
            [
                sys.executable,
                str(ROOT / "encoding_guard_review/review.py"),
                "--evidence-root",
                str(ROOT),
                "--output",
                str(output / "independent.json"),
                "--run-id",
                run_id,
            ],
        ),
    ]
    completed = []
    for name, command in stages:
        stage = {"stage": name, "exit_code": None, "receipt_valid": False}
        try:
            result = subprocess.run(
                command, cwd=ROOT, env=environment, capture_output=True, text=True, timeout=120, check=False
            )
            (output / (name + ".log")).write_text(result.stdout + result.stderr)
            stage["exit_code"] = result.returncode
            require(result.returncode == 0, "Subprocess failed")
            data = json.loads((output / (name + ".json")).read_text())
            if name == "unit":
                validate_unit(data, expected, before, manifest_hash, run_id)
            else:
                validate_independent(data, before, run_id)
            stage["receipt_valid"] = True
        except subprocess.TimeoutExpired:
            stage["reason"] = "timeout"
        except (OSError, ValueError, KeyError, TypeError) as exc:
            stage["reason"] = str(exc)
        completed.append(stage)
        if not stage["receipt_valid"]:
            break
    passed = len(completed) == 2 and all(x["receipt_valid"] for x in completed)
    final_integrity_reason = None
    try:
        require(before == verify_manifest(), "Inputs changed during run")
        require(
            manifest_hash == hashlib.sha256((ROOT / "manifest.json").read_bytes()).hexdigest(),
            "Manifest changed during run",
        )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        passed = False
        final_integrity_reason = str(exc)
    receipt = {
        "status": "PASSED_OFFLINE_RESEARCH_ONLY" if passed else "FAILED",
        "production_approved": False,
        "run_id": run_id,
        "stages": completed,
        "python": platform.python_version(),
        "numpy": numpy.__version__,
        "input_sha256": before,
        "manifest_sha256": manifest_hash,
        "expected_unit_tests": len(expected),
        "expected_independent_checks": len(INDEPENDENT_CASES),
        "final_integrity_error": final_integrity_reason,
        "scope": "Offline research checks; three windows, two dates; no network/API/PostGIS benchmark",
    }
    (output / "result.json").write_text(json.dumps(receipt, indent=2, allow_nan=False))
    print(json.dumps({"status": receipt["status"], "output_dir": str(output)}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
