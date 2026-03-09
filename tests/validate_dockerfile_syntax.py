#!/usr/bin/env python3
"""
Validate Dockerfile syntax for all modified Dockerfiles.

Checks:
1. Every RUN pip install command is syntactically valid (balanced quotes, proper flags)
2. Fallback chains with || are properly structured
3. No dangling backslash continuations
4. --trusted-host is present alongside -i flag
"""

import os
import re
import sys


def find_dockerfiles(root: str) -> list[str]:
    """Find all Dockerfiles in the project."""
    dockerfiles = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", "archive", "__pycache__", ".venv")]
        for f in filenames:
            if f == "Dockerfile" or f.startswith("Dockerfile."):
                full = os.path.join(dirpath, f)
                dockerfiles.append(full)
    return sorted(dockerfiles)


def check_balanced_quotes(content: str) -> list[str]:
    """Check that quotes are balanced in Dockerfile."""
    issues = []
    for i, line in enumerate(content.split("\n"), 1):
        single = line.count("'") - line.count("\\'")
        double = line.count('"') - line.count('\\"')
        if single % 2 != 0:
            issues.append(f"  Line {i}: Unbalanced single quotes")
        if double % 2 != 0:
            issues.append(f"  Line {i}: Unbalanced double quotes")
    return issues


def check_continuation_lines(content: str) -> list[str]:
    """Check backslash continuations are properly formed."""
    issues = []
    lines = content.split("\n")
    for i, line in enumerate(lines):
        stripped = line.rstrip()
        if stripped.endswith("\\"):
            # Next line should exist and not be empty (unless it's a comment)
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line == "" and i + 2 < len(lines):
                    issues.append(f"  Line {i + 1}: Backslash continuation followed by empty line")
    return issues


def check_trusted_host_with_mirror(content: str) -> list[str]:
    """Check that -i flag is paired with --trusted-host for non-pypi mirrors."""
    issues = []
    # Join continuation lines
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

    for line in logical_lines:
        if "pip install" not in line:
            continue
        # Check each || segment
        segments = line.split("||")
        for seg in segments:
            seg = seg.strip()
            if "pip install" not in seg:
                continue
            if "-i https://mirrors.aliyun.com" in seg or "--index-url https://mirrors.aliyun.com" in seg:
                if "--trusted-host mirrors.aliyun.com" not in seg and "--trusted-host=mirrors.aliyun.com" not in seg:
                    short = seg[:100] + "..." if len(seg) > 100 else seg
                    issues.append(f"  Missing --trusted-host for Aliyun mirror: {short}")
    return issues


def check_pip_conf_heredoc(content: str) -> list[str]:
    """Check pip.conf heredoc is properly closed."""
    issues = []
    in_heredoc = False
    heredoc_marker = None
    heredoc_start = 0

    for i, line in enumerate(content.split("\n"), 1):
        if "<<" in line and "EOF" in line and not in_heredoc:
            in_heredoc = True
            heredoc_marker = "EOF"
            heredoc_start = i
        elif in_heredoc and line.strip() == heredoc_marker:
            in_heredoc = False

    if in_heredoc:
        issues.append(f"  Unclosed heredoc starting at line {heredoc_start}")

    return issues


def validate_dockerfile(filepath: str) -> list[str]:
    """Run all syntax validations on a Dockerfile."""
    with open(filepath) as f:
        content = f.read()

    if "pip install" not in content:
        return []

    issues = []
    issues.extend(check_balanced_quotes(content))
    issues.extend(check_continuation_lines(content))
    issues.extend(check_trusted_host_with_mirror(content))
    issues.extend(check_pip_conf_heredoc(content))

    return issues


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dockerfiles = find_dockerfiles(root)

    print("Dockerfile Syntax Validation")
    print(f"Found {len(dockerfiles)} Dockerfiles")
    print("=" * 80)

    total_issues = 0
    files_with_issues = 0
    files_checked = 0

    for df in dockerfiles:
        with open(df) as f:
            content = f.read()

        if "pip install" not in content:
            continue

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
    print(f"Files checked: {files_checked}")
    print(f"Files with issues: {files_with_issues}")
    print(f"Total issues: {total_issues}")

    if total_issues > 0:
        print("\nRESULT: FAIL")
        return 1
    else:
        print("\nRESULT: PASS - All Dockerfiles have valid syntax")
        return 0


if __name__ == "__main__":
    sys.exit(main())
