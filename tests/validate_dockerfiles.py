#!/usr/bin/env python3
"""
Validate that all Dockerfiles use Aliyun mirror as primary pip install source.

This script parses multi-line RUN commands in Dockerfiles and checks that
every `pip install` invocation includes `-i https://mirrors.aliyun.com/pypi/simple/`
or `--index-url https://mirrors.aliyun.com/pypi/simple/`.

Exceptions:
- PyTorch installs with PIP_CONFIG_FILE=/dev/null (intentional)
- Lines that are fallback attempts (second/third in || chains)
"""

import os
import re
import sys
from pathlib import Path
import shlex
from urllib.parse import urlparse


def find_dockerfiles(root: str) -> list[str]:
    """Find all Dockerfiles in the project."""
    dockerfiles = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip archive, node_modules, .git
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "archive", "__pycache__", ".venv")]
        for f in filenames:
            if f == "Dockerfile" or f.startswith("Dockerfile."):
                full = os.path.join(dirpath, f)
                dockerfiles.append(full)
    return sorted(dockerfiles)


def join_continuation_lines(content: str) -> list[str]:
    """Join lines ending with backslash into single logical lines."""
    lines = content.split("\n")
    logical_lines = []
    current = ""
    for line in lines:
        stripped = line.rstrip()
        if stripped.endswith("\\"):
            current += stripped[:-1] + " "
        else:
            current += stripped
            logical_lines.append(current)
            current = ""
    if current:
        logical_lines.append(current)
    return logical_lines


def extract_run_commands(content: str) -> list[str]:
    """Extract all RUN commands as joined single-line strings."""
    logical_lines = join_continuation_lines(content)
    run_commands = []
    for line in logical_lines:
        stripped = line.strip()
        if stripped.startswith("RUN "):
            run_commands.append(stripped)
    return run_commands


def extract_pip_install_commands(run_cmd: str) -> list[str]:
    """Extract individual pip install commands from a RUN command.

    Handles || chains and && chains.
    """
    # Remove the RUN prefix
    cmd_body = run_cmd[4:].strip()

    # Split by || and && to get individual commands
    # We need to handle the pip install commands specifically
    pip_cmds = []

    # Split by || first (fallback chains)
    parts = re.split(r"\|\|", cmd_body)

    for part in parts:
        # Split by && for chained commands
        subparts = re.split(r"&&", part)
        for sub in subparts:
            sub = sub.strip()
            if "pip install" in sub or "pip3 install" in sub:
                pip_cmds.append(sub)

    return pip_cmds


def has_aliyun_mirror(pip_cmd: str) -> bool:
    """Check if a pip install command uses Aliyun as primary mirror.

    We look specifically for primary index flags (-i/--index-url) that point to
    mirrors.aliyun.com, rather than doing a simple substring check.
    """
    try:
        args = shlex.split(pip_cmd)
    except ValueError:
        # Fallback to conservative behavior if the command cannot be parsed
        return False

    aliyun_host = "mirrors.aliyun.com"

    i = 0
    while i < len(args):
        arg = args[i]
        # Handle '--index-url=https://...'
        if arg.startswith("--index-url="):
            url = arg.split("=", 1)[1]
        # Handle '--index-url https://...'
        elif arg == "--index-url" and i + 1 < len(args):
            url = args[i + 1]
            i += 1
        # Handle '-ihttps://...'
        elif arg.startswith("-i") and arg != "-i":
            url = arg[2:]
        # Handle '-i https://...'
        elif arg == "-i" and i + 1 < len(args):
            url = args[i + 1]
            i += 1
        else:
            i += 1
            continue

        parsed = urlparse(url)
        host = parsed.hostname
        if host and host.lower() == aliyun_host:
            return True

        i += 1

    return False


def is_pytorch_exception(pip_cmd: str, run_cmd: str) -> bool:
    """Check if this is a PyTorch install that intentionally skips pip.conf."""
    return "PIP_CONFIG_FILE=/dev/null" in run_cmd and "download.pytorch.org" in pip_cmd


def is_fallback_command(pip_cmd: str, full_run: str) -> bool:
    """Check if this pip install is a fallback (2nd or 3rd in || chain)."""
    parts = re.split(r"\|\|", full_run)
    if len(parts) <= 1:
        return False
    # The first part is the primary, others are fallbacks
    first_part = parts[0]
    return pip_cmd.strip() not in first_part


def has_pip_conf_before(content: str, run_line_approx: str) -> bool:
    """Check if pip.conf is configured before this RUN command."""
    # Look for pip.conf creation pattern
    pip_conf_pattern = r"cat\s*>\s*/root/\.pip/pip\.conf"
    content_before_run = content.split(run_line_approx[:50])[0] if run_line_approx[:50] in content else content
    return bool(re.search(pip_conf_pattern, content_before_run))


def validate_dockerfile(filepath: str) -> list[str]:
    """Validate a single Dockerfile. Returns list of issues."""
    issues = []

    with open(filepath) as f:
        content = f.read()

    # Skip Node.js Dockerfiles (npm, not pip)
    if "npm install" in content and "pip install" not in content:
        return []

    run_commands = extract_run_commands(content)

    for run_cmd in run_commands:
        pip_commands = extract_pip_install_commands(run_cmd)

        for pip_cmd in pip_commands:
            # Skip if it's a fallback command (not the primary attempt)
            if is_fallback_command(pip_cmd, run_cmd):
                continue

            # Skip PyTorch exceptions
            if is_pytorch_exception(pip_cmd, run_cmd):
                continue

            # Check if Aliyun mirror is used
            if not has_aliyun_mirror(pip_cmd):
                # Truncate for readability
                short_cmd = pip_cmd[:120] + "..." if len(pip_cmd) > 120 else pip_cmd
                issues.append(f"  Missing Aliyun mirror: {short_cmd}")

    return issues


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dockerfiles = find_dockerfiles(root)

    print(f"Found {len(dockerfiles)} Dockerfiles")
    print("=" * 80)

    total_issues = 0
    files_with_issues = 0
    files_checked = 0
    files_with_pip = 0

    for df in dockerfiles:
        with open(df) as f:
            content = f.read()

        if "pip install" not in content and "pip3 install" not in content:
            continue

        files_with_pip += 1
        files_checked += 1
        rel_path = os.path.relpath(df, root)

        issues = validate_dockerfile(df)
        if issues:
            files_with_issues += 1
            total_issues += len(issues)
            print(f"\nFAIL: {rel_path}")
            for issue in issues:
                print(issue)
        else:
            print(f"  OK: {rel_path}")

    print("\n" + "=" * 80)
    print(f"Files with pip install: {files_with_pip}")
    print(f"Files checked: {files_checked}")
    print(f"Files with issues: {files_with_issues}")
    print(f"Total issues: {total_issues}")

    if total_issues > 0:
        print("\nRESULT: FAIL")
        return 1
    else:
        print("\nRESULT: PASS - All Dockerfiles use Aliyun mirror as primary")
        return 0


if __name__ == "__main__":
    sys.exit(main())
