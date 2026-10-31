"""Exercise the repository worktree guard against real Git indexes."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPOSITORY = Path(__file__).resolve().parents[2]
GUARD = REPOSITORY / "scripts/ci/check_repository_worktrees.py"


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )


def run_guard(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GUARD), "--repo", str(repo)],
        check=False,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def git_repository(tmp_path: Path) -> Path:
    git(tmp_path, "init", "-q")
    (tmp_path / ".gitignore").write_text((REPOSITORY / ".gitignore").read_text())
    (tmp_path / "README.md").write_text("Repository metadata test fixture.\n")
    git(tmp_path, "add", ".gitignore", "README.md")
    git(
        tmp_path,
        "-c",
        "user.name=Repository Hygiene Test",
        "-c",
        "user.email=repository-hygiene@example.invalid",
        "-c",
        "commit.gpgsign=false",
        "-c",
        f"core.hooksPath={tmp_path / '.git' / 'disabled-hooks'}",
        "commit",
        "-qm",
        "Initialize metadata fixture",
    )
    return tmp_path


def test_current_repository_has_no_tracked_agent_worktrees() -> None:
    result = run_guard(REPOSITORY)
    assert result.returncode == 0, result.stderr


def test_ignore_rule_preserves_worktrees_and_shared_claude_configuration(git_repository: Path) -> None:
    worktree_file = git_repository / ".claude/worktrees/agent-test/local-work.txt"
    worktree_file.parent.mkdir(parents=True)
    worktree_file.write_text("Uncommitted local work must remain on disk.\n")
    configuration = [
        ".claude/agents/example.md",
        ".claude/skills/example/SKILL.md",
        ".claude/settings.json",
    ]
    for path in configuration:
        target = git_repository / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("{}\n")

    ignored = git(git_repository, "check-ignore", "-v", "--", str(worktree_file.relative_to(git_repository)))
    assert ignored.stdout.startswith(".gitignore:")
    git(git_repository, "add", "--all")
    tracked = git(git_repository, "ls-files", "-z").stdout.split("\0")
    assert not any(path.startswith(".claude/worktrees/") for path in tracked)
    assert all(path in tracked for path in configuration)
    assert worktree_file.read_text() == "Uncommitted local work must remain on disk.\n"
    assert run_guard(git_repository).returncode == 0


@pytest.mark.parametrize("entry_kind", ["file", "gitlink"])
def test_guard_rejects_forced_worktree_entries(git_repository: Path, entry_kind: str) -> None:
    path = ".claude/worktrees/agent-regression"
    worktree = git_repository / path
    worktree.mkdir(parents=True)
    if entry_kind == "file":
        path += "/local-work.txt"
        (git_repository / path).write_text("This must not enter the repository.\n")
        git(git_repository, "add", "--force", "--", path)
    else:
        commit = git(git_repository, "rev-parse", "HEAD").stdout.strip()
        git(git_repository, "update-index", "--add", "--cacheinfo", f"160000,{commit},{path}")

    result = run_guard(git_repository)
    assert result.returncode == 1
    assert path in result.stderr
    assert "must not be tracked" in result.stderr


def test_guard_allows_declared_submodule_outside_local_worktrees(git_repository: Path) -> None:
    path = "vendor/example"
    (git_repository / path).mkdir(parents=True)
    (git_repository / ".gitmodules").write_text(
        f'[submodule "example"]\n\tpath = {path}\n\turl = https://example.invalid/vendor/example.git\n'
    )
    git(git_repository, "add", ".gitmodules")
    commit = git(git_repository, "rev-parse", "HEAD").stdout.strip()
    git(git_repository, "update-index", "--add", "--cacheinfo", f"160000,{commit},{path}")

    result = run_guard(git_repository)
    assert result.returncode == 0, result.stderr
    git(git_repository, "submodule", "foreach", "--recursive", "true")
