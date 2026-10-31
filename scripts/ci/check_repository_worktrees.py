#!/usr/bin/env python3
"""Keep local Claude worktrees out of the repository's tracked contents."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()

    result = subprocess.run(
        ["git", "-C", str(args.repo), "ls-files", "-z", "--", ".claude/worktrees"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        print(f"Cannot inspect tracked repository files: {result.stderr.strip()}", file=sys.stderr)
        return result.returncode

    paths = [path for path in result.stdout.split("\0") if path]
    if paths:
        print("Local agent worktrees must not be tracked in Git:", file=sys.stderr)
        for path in paths:
            print(f"  {path}", file=sys.stderr)
        print("Untrack these entries while preserving local worktree contents.", file=sys.stderr)
        return 1

    print("No local agent worktrees are tracked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
