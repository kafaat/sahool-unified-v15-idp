#!/usr/bin/env python3
"""Run Safety once against a project directory only when its API key is set.

No credentials are invented or printed. The optional-provider status is kept
separate from the mandatory, complete pip-audit inventory. Safety 3.8.1 uses 64
for findings and 65+ for authentication/service/input failures; the latter fail
the configured scanner check. A missing key is explicitly skipped, never clean.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from audit_python_requirements import run_command, write_json


def run(directory: Path, output: Path, binary: str = "safety") -> int:
    output.mkdir(parents=True, exist_ok=True)
    if not os.environ.get("SAFETY_API_KEY", "").strip():
        receipt = {"status": "not_configured", "reason": "SAFETY_API_KEY is not set; Safety was not invoked"}
        code = 0
    else:
        directory = directory.resolve()
        report = output / "safety.json"
        report.unlink(missing_ok=True)
        if not directory.is_dir():
            receipt = {"status": "execution_error", "error": "Safety --target must be a project directory"}
            code = 2
        else:
            execution = run_command(
                [binary, "scan", "--target", str(directory), "--output", "json"],
                report,
                output / "stderr.log",
                600,
                directory,
            )
            receipt = {**execution, "status": "execution_error"}
            try:
                data = json.loads(report.read_text())
                if not isinstance(data, dict) or not isinstance(data.get("meta"), dict):
                    raise ValueError("Safety did not return report metadata")
                results = data.get("scan_results")
                if not isinstance(results, dict) or any(
                    not isinstance(results.get(field), list) for field in ("files", "projects")
                ):
                    raise ValueError("Safety did not return the expected scan-result arrays")
                if execution["execution_error"] or execution["exit_code"] not in (0, 64):
                    raise ValueError(f"Safety did not complete; exit={execution['exit_code']}")
                receipt["status"] = "completed_with_findings" if execution["exit_code"] == 64 else "completed"
                code = 0
            except (OSError, ValueError) as error:
                receipt["error"] = str(error)
                code = 2
    write_json(output / "receipt.json", receipt)
    message = f"Safety status: {receipt['status']}. See the separate provider receipt; pip-audit remains mandatory."
    print(message)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with Path(os.environ["GITHUB_STEP_SUMMARY"]).open("a") as handle:
            handle.write(f"\n## Optional Safety scan\n\n{message}\n")
    return code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    return run(arguments.directory, arguments.output)


if __name__ == "__main__":
    raise SystemExit(main())
