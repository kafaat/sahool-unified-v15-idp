"""Read open PRs, retrying only bounded transient GitHub failures."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time

COMMAND = [
    "gh",
    "pr",
    "list",
    "--state",
    "open",
    "--json",
    "number,title,headRefName,baseRefName,mergeable,statusCheckRollup,updatedAt,createdAt",
]
TRANSIENT_HTTP = re.compile(r"\bHTTP (?:408|429|500|502|503|504)\b")
MAX_ATTEMPTS = 3


def fetch_pr_status() -> list[dict]:
    """Return successful JSON only; never convert an API failure to an empty list."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            result = subprocess.run(COMMAND, capture_output=True, text=True, timeout=60, check=False)
        except subprocess.TimeoutExpired:
            if attempt == MAX_ATTEMPTS:
                raise RuntimeError("GitHub PR query timed out after 3 attempts") from None
        else:
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if not isinstance(data, list) or any(not isinstance(pr, dict) for pr in data):
                    raise ValueError("GitHub PR query did not return an array of objects")
                return data
            if not TRANSIENT_HTTP.search(result.stderr) or attempt == MAX_ATTEMPTS:
                raise RuntimeError(f"GitHub PR query failed (exit {result.returncode}): {result.stderr.strip()}")
        print(f"Transient GitHub PR query failure; retry {attempt + 1}/{MAX_ATTEMPTS}", file=sys.stderr)
        time.sleep(2**attempt)
    raise AssertionError("unreachable")


def main() -> int:
    try:
        data = fetch_pr_status()
    except (OSError, ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
