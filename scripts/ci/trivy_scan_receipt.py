#!/usr/bin/env python3
"""Retain a real Trivy filesystem scan and gate its validated result.

The scan flags and CRITICAL scope match the existing dependency workflow.
Structural validation requires SARIF 2.1.0, nonempty Trivy runs, explicit result
arrays, rule IDs/messages and levels. Exit 0 requires no findings; exit 1 requires
findings. Tool errors, missing reports and unknown/partial structure never mean
clean. Completeness failures block every event. Findings are advisory on PRs
and block other events. No synthetic SARIF is created.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from audit_python_requirements import run_command, write_json


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_sarif(report: Path) -> dict:
    data = json.loads(report.read_text())
    if not isinstance(data, dict) or data.get("version") != "2.1.0":
        raise ValueError("Expected a SARIF 2.1.0 object")
    runs = data.get("runs")
    if not isinstance(runs, list) or not runs:
        raise ValueError("SARIF must contain at least one run")
    count = 0
    versions = set()
    for run in runs:
        if not isinstance(run, dict):
            raise ValueError("Invalid SARIF run")
        driver = run.get("tool", {}).get("driver", {})
        if driver.get("name") != "Trivy" or not isinstance(driver.get("version"), str) or not driver["version"]:
            raise ValueError("SARIF run must identify Trivy and its actual version")
        versions.add(driver["version"])
        results = run.get("results")
        if not isinstance(results, list):
            raise ValueError("SARIF run is missing its results array")
        for invocation in run.get("invocations", []):
            if invocation.get("executionSuccessful") is False:
                raise ValueError("SARIF reports an unsuccessful scanner invocation")
        for result in results:
            if not isinstance(result, dict) or not isinstance(result.get("ruleId"), str) or not result["ruleId"]:
                raise ValueError("SARIF result has no rule identifier")
            if result.get("level") != "error":
                raise ValueError("Unexpected severity in the CRITICAL-only Trivy scan")
            message = result.get("message")
            if not isinstance(message, dict) or not isinstance(message.get("text"), str):
                raise ValueError("SARIF result has no text message")
            count += 1
    return {"runs": len(runs), "critical_count": count, "trivy_versions": sorted(versions)}


def validate_scan(exit_code: int | None, report: Path, log: str, execution_error: str | None = None) -> dict:
    result = {"status": "incomplete", "structural_validation": False, "critical_count": None, "error": execution_error}
    if execution_error:
        return result
    try:
        parsed = inspect_sarif(report)
        if re.search(r"(?m)(?:^|\s)(?:FATAL|ERROR)\s", log):
            raise ValueError("Trivy emitted an execution error; its report may be partial")
        expected_exit = 1 if parsed["critical_count"] else 0
        if exit_code != expected_exit:
            raise ValueError(f"Trivy exit code {exit_code} disagrees with report (expected {expected_exit})")
        result.update(parsed, structural_validation=True, status="findings" if expected_exit else "clean")
    except (OSError, ValueError, TypeError, AttributeError) as error:
        result["error"] = str(error)
    return result


def capture_database(cache: Path) -> dict:
    metadata = cache / "db/metadata.json"
    database = cache / "db/trivy.db"
    result = {"cache_directory": str(cache), "metadata": None, "database_sha256": None}
    if metadata.is_file():
        try:
            result["metadata"] = json.loads(metadata.read_text())
        except (OSError, ValueError) as error:
            result["metadata_error"] = str(error)
    if database.is_file():
        result["database_sha256"] = file_digest(database)
    return result


def scan(repository: Path, output: Path, binary: str, cache: Path) -> int:
    repository, output, cache = repository.resolve(), output.resolve(), cache.resolve()
    output.mkdir(parents=True, exist_ok=True)
    report = output / "trivy-results.sarif"
    report.unlink(missing_ok=True)
    command = [
        binary,
        "fs",
        "--cache-dir",
        str(cache),
        "--skip-check-update",
        "--scanners",
        "vuln",
        "--severity",
        "CRITICAL",
        "--exit-code",
        "1",
        "--format",
        "sarif",
        "--output",
        str(report),
        ".",
    ]
    execution = run_command(command, output / "stdout.log", output / "stderr.log", 1200, repository)
    log = "\n".join(path.read_text() for path in [output / "stdout.log", output / "stderr.log"] if path.exists())
    validation = validate_scan(execution["exit_code"], report, log, execution["execution_error"])
    receipt = {
        **execution,
        **validation,
        "report": str(report) if report.is_file() else None,
        "report_sha256": file_digest(report) if report.is_file() else None,
        "database": capture_database(cache),
        "schema_validation": "strict structural contract for Trivy CRITICAL SARIF 2.1.0 (not a complete JSON Schema validator)",
    }
    write_json(output / "receipt.json", receipt)
    if os.environ.get("GITHUB_OUTPUT"):
        with Path(os.environ["GITHUB_OUTPUT"]).open("a") as handle:
            handle.write(f"valid_report={str(validation['structural_validation']).lower()}\n")
    print(json.dumps(receipt))
    return 2 if validation["status"] == "incomplete" else 0


def gate(receipt_path: Path, event: str) -> int:
    try:
        receipt = json.loads(receipt_path.read_text())
        if receipt.get("status") not in {"clean", "findings"} or receipt.get("structural_validation") is not True:
            raise ValueError(receipt.get("error") or "Scanner receipt is incomplete")
        report = Path(receipt["report"])
        if file_digest(report) != receipt["report_sha256"]:
            raise ValueError("SARIF changed after scan validation")
        parsed = inspect_sarif(report)
        count = parsed["critical_count"]
        if count != receipt["critical_count"] or receipt.get("exit_code") != (1 if count else 0):
            raise ValueError("Receipt and SARIF result counts or exit code disagree")
        if count:
            informational = event == "pull_request"
            message = f"Trivy found {count} CRITICAL findings; " + (
                "informational on pull requests" if informational else "gate failed"
            )
            exit_code = 0 if informational else 1
        else:
            message = "Trivy completed successfully with zero CRITICAL findings in the configured scan scope"
            exit_code = 0
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        message = f"Trivy scan incomplete: {error}"
        exit_code = 2
    print(f"::{'error' if exit_code else 'notice'}::{message}")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a") as handle:
            handle.write(f"\n## Trivy dependency scan\n\n{message}.\n")
    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="action", required=True)
    run = subcommands.add_parser("scan")
    run.add_argument("--repository", type=Path, default=Path.cwd())
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--binary", default="trivy")
    run.add_argument(
        "--cache", type=Path, default=Path(os.environ.get("TRIVY_CACHE_DIR", Path.home() / ".cache/trivy"))
    )
    check = subcommands.add_parser("gate")
    check.add_argument("--receipt", type=Path, required=True)
    check.add_argument("--event", required=True)
    arguments = parser.parse_args()
    if arguments.action == "scan":
        return scan(arguments.repository.resolve(), arguments.output.resolve(), arguments.binary, arguments.cache)
    return gate(arguments.receipt, arguments.event)


if __name__ == "__main__":
    sys.exit(main())
