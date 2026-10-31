#!/usr/bin/env python3
"""Fetch a complete, validated PR snapshot without masking GitHub API failures.

The monitor's downstream jobs may update branches or post notifications. A
failed or malformed API response must never become a successful empty snapshot.
Only the read-only ``gh pr list`` request is retried.

Validation covers unique PR numbers, names, timestamp strings with timezones,
mergeability, and nullable check-run/status-context lists. An explicit 1000-PR
cap replaces gh's default 30-item limit; reaching the cap fails closed because
the snapshot might be incomplete. This is not a merge-readiness assessment.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

MAX_ATTEMPTS = 3
REQUEST_TIMEOUT_SECONDS = 60
RETRY_DELAYS_SECONDS = (2, 4)
PR_LIMIT = 1000
PR_FIELDS = "number,title,headRefName,baseRefName,mergeable,statusCheckRollup,updatedAt,createdAt"


class FetchError(RuntimeError):
    """No trustworthy snapshot could be obtained within the retry budget."""


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"Nonstandard JSON constant: {value}")


def validate_pr_data(raw: str) -> list[dict[str, Any]]:
    """Reject malformed/truncated JSON and shapes that would yield false counts."""
    data = json.loads(raw, parse_constant=_reject_json_constant)
    if not isinstance(data, list):
        raise ValueError("GitHub PR response must be a JSON list")
    if len(data) >= PR_LIMIT:
        raise ValueError(f"PR response reached the {PR_LIMIT}-item limit; completeness is unproven")

    seen_numbers: set[int] = set()
    for row in data:
        if not isinstance(row, dict):
            raise ValueError("Each PR response entry must be an object")
        number = row.get("number")
        if type(number) is not int or number <= 0 or number in seen_numbers:
            raise ValueError("PR numbers must be positive, unique integers")
        seen_numbers.add(number)

        for field in ("title", "headRefName", "baseRefName", "updatedAt", "createdAt"):
            if not isinstance(row.get(field), str) or not row[field]:
                raise ValueError(f"PR #{number} requires a nonempty {field} string")
        for field in ("updatedAt", "createdAt"):
            timestamp = datetime.fromisoformat(row[field])
            if timestamp.tzinfo is None:
                raise ValueError(f"PR #{number} requires a timezone-aware {field}")
        if row.get("mergeable") not in ("MERGEABLE", "CONFLICTING", "UNKNOWN"):
            raise ValueError(f"PR #{number} has an invalid mergeable state")
        if "statusCheckRollup" not in row:
            raise ValueError(f"PR #{number} is missing statusCheckRollup")
        checks = row["statusCheckRollup"]
        if checks is not None:
            if not isinstance(checks, list):
                raise ValueError(f"PR #{number} statusCheckRollup must be a list or null")
            for check in checks:
                if not isinstance(check, dict) or not ("conclusion" in check or "state" in check):
                    raise ValueError(f"PR #{number} contains an invalid status check")
                for field in ("conclusion", "state"):
                    if check.get(field) is not None and not isinstance(check[field], str):
                        raise ValueError(f"PR #{number} contains an invalid status check {field}")
    return data


def fetch_pr_status(
    repository: str,
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
    sleeper: Callable[[float], None] | None = None,
) -> list[dict[str, Any]]:
    """Retry read failures with a bounded timeout; fail after the last attempt."""
    run = runner or subprocess.run
    sleep = sleeper or time.sleep
    command = [
        "gh",
        "pr",
        "list",
        "--repo",
        repository,
        "--state",
        "open",
        "--limit",
        str(PR_LIMIT),
        "--json",
        PR_FIELDS,
    ]
    last_error = "No response received"
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            result = run(
                command,
                capture_output=True,
                encoding="utf-8",
                timeout=REQUEST_TIMEOUT_SECONDS,
                check=False,
            )
            if result.returncode:
                diagnostic = result.stderr.strip().splitlines()
                detail = diagnostic[-1][:400] if diagnostic else "no diagnostic returned"
                last_error = f"GitHub CLI exited {result.returncode}: {detail}"
            else:
                return validate_pr_data(result.stdout)
        except subprocess.TimeoutExpired:
            last_error = f"GitHub CLI timed out after {REQUEST_TIMEOUT_SECONDS} seconds"
        except ValueError as exc:
            last_error = f"Invalid GitHub PR response: {exc}"
        except OSError as exc:
            # Missing gh or an invalid local executable is not a transient API failure.
            raise FetchError(f"Cannot execute GitHub CLI: {exc}") from exc

        print(f"PR status attempt {attempt}/{MAX_ATTEMPTS} failed: {last_error}", file=sys.stderr)
        if attempt < MAX_ATTEMPTS:
            sleep(RETRY_DELAYS_SECONDS[attempt - 1])
    raise FetchError(f"Failed to obtain a valid PR snapshot after {MAX_ATTEMPTS} attempts: {last_error}")


def write_snapshot(path: Path, data: list[dict[str, Any]]) -> None:
    """Publish only a fully validated snapshot, preserving the old file on error."""
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as handle:
            temporary_path = Path(handle.name)
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True, help="GitHub repository in owner/name form")
    parser.add_argument("--output", type=Path, default=Path("pr-data.json"))
    args = parser.parse_args(argv)
    try:
        data = fetch_pr_status(args.repository)
        write_snapshot(args.output, data)
    except (FetchError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Fetched {len(data)} open PRs into {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
