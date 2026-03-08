"""
SAHOOL Code Fix Agent - Unit Tests for Git Tools
اختبارات الوحدة لأدوات Git

Tests for Git integration tools.
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tools.git_tools import (
    FileChangeType,
    GitOperationResult,
    GitOperationType,
    GitTools,
)


class TestGitToolsInit:
    """اختبارات تهيئة أدوات Git"""

    def test_init_without_repo(self):
        """Test initialization without repository"""
        tools = GitTools()

        assert tools.repo_path is None
        assert tools.safe_mode is True

    def test_init_with_path(self, tmp_path):
        """Test initialization with path"""
        tools = GitTools(repo_path=tmp_path)

        assert tools.repo_path == tmp_path

    def test_init_safe_mode(self):
        """Test safe mode is enabled by default"""
        tools = GitTools()

        assert tools.safe_mode is True

    def test_init_unsafe_mode(self):
        """Test disabling safe mode"""
        tools = GitTools(safe_mode=False)

        assert tools.safe_mode is False


class TestGitToolsValidation:
    """اختبارات التحقق"""

    def test_is_valid_branch_name(self):
        """Test valid branch names"""
        tools = GitTools()

        valid_names = [
            "main",
            "feature/new-feature",
            "bugfix/issue-123",
            "release-1.0.0",
            "claude/implement-task",
        ]

        for name in valid_names:
            assert tools._is_valid_branch_name(name) is True

    def test_is_invalid_branch_name(self):
        """Test invalid branch names"""
        tools = GitTools()

        invalid_names = [
            ".hidden",  # Starts with .
            "branch..name",  # Contains ..
            "branch~name",  # Contains ~
            "branch^name",  # Contains ^
            "branch:name",  # Contains :
            "branch name",  # Contains space
            "-starting-dash",  # Starts with -
            "ending.lock",  # Ends with .lock
        ]

        for name in invalid_names:
            assert tools._is_valid_branch_name(name) is False, f"{name} should be invalid"

    def test_is_valid_git_url(self):
        """Test valid Git URLs"""
        tools = GitTools()

        valid_urls = [
            "https://github.com/user/repo.git",
            "https://github.com/user/repo",
            "https://gitlab.com/user/repo.git",
            "git@github.com:user/repo.git",
        ]

        for url in valid_urls:
            assert tools._is_valid_git_url(url) is True, f"{url} should be valid"

    def test_is_invalid_git_url(self):
        """Test invalid Git URLs"""
        tools = GitTools()

        invalid_urls = [
            "not-a-url",
            "ftp://example.com/repo",
            "/local/path",
        ]

        for url in invalid_urls:
            assert tools._is_valid_git_url(url) is False, f"{url} should be invalid"


class TestGitToolsRepository:
    """اختبارات المستودع"""

    @pytest.fixture
    def git_repo(self, tmp_path):
        """Create a temporary git repository"""
        import subprocess

        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()

        # Initialize git repo
        subprocess.run(["git", "init"], cwd=repo_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=repo_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, capture_output=True)
        # Disable GPG signing for test commits
        subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=repo_path, capture_output=True)

        # Create initial commit
        (repo_path / "README.md").write_text("# Test")
        subprocess.run(["git", "add", "."], cwd=repo_path, capture_output=True)
        result = subprocess.run(
            ["git", "commit", "--no-gpg-sign", "-m", "Initial commit"],
            cwd=repo_path,
            capture_output=True,
        )

        return repo_path

    def test_is_git_repository(self, git_repo):
        """Test checking if path is a git repository"""
        tools = GitTools(repo_path=git_repo)

        assert tools.is_git_repository() is True

    def test_is_not_git_repository(self, tmp_path):
        """Test checking non-git directory"""
        tools = GitTools(repo_path=tmp_path)

        assert tools.is_git_repository() is False

    def test_get_status(self, git_repo):
        """Test getting repository status"""
        tools = GitTools(repo_path=git_repo)

        result = tools.get_status()

        assert result.success is True
        assert result.operation == GitOperationType.STATUS
        assert "clean" in result.data

    def test_get_status_with_changes(self, git_repo):
        """Test getting status with uncommitted changes"""
        tools = GitTools(repo_path=git_repo)

        # Create a new file
        (git_repo / "new_file.txt").write_text("content")

        result = tools.get_status()

        assert result.success is True
        assert len(result.data["changes"]) > 0

    def test_get_diff(self, git_repo):
        """Test getting diff"""
        tools = GitTools(repo_path=git_repo)

        # Modify a file
        (git_repo / "README.md").write_text("# Modified")

        result = tools.get_diff()

        assert result.success is True
        assert result.operation == GitOperationType.DIFF

    def test_get_log(self, git_repo):
        """Test getting commit log"""
        tools = GitTools(repo_path=git_repo)

        result = tools.get_log(limit=5)

        assert result.success is True
        assert result.operation == GitOperationType.LOG
        assert "commits" in result.data
        assert len(result.data["commits"]) >= 1

    def test_get_branches(self, git_repo):
        """Test getting branch list"""
        tools = GitTools(repo_path=git_repo)

        result = tools.get_branches()

        assert result.success is True
        assert result.operation == GitOperationType.BRANCH
        assert "branches" in result.data
        # Should have at least main/master branch

    def test_create_branch(self, git_repo):
        """Test creating a new branch"""
        tools = GitTools(repo_path=git_repo)

        result = tools.create_branch("feature/test-branch", checkout=False)

        assert result.success is True
        assert result.data["branch"] == "feature/test-branch"

    def test_create_branch_invalid_name(self, git_repo):
        """Test creating branch with invalid name"""
        tools = GitTools(repo_path=git_repo)

        result = tools.create_branch(".invalid-name")

        assert result.success is False
        assert "invalid" in result.message.lower()

    def test_stage_files(self, git_repo):
        """Test staging files"""
        tools = GitTools(repo_path=git_repo)

        # Create a new file
        (git_repo / "test.txt").write_text("test")

        result = tools.stage_files(files=["test.txt"])

        assert result.success is True

    def test_stage_all_files(self, git_repo):
        """Test staging all files"""
        tools = GitTools(repo_path=git_repo)

        # Create new files
        (git_repo / "file1.txt").write_text("1")
        (git_repo / "file2.txt").write_text("2")

        result = tools.stage_files(all_files=True)

        assert result.success is True

    def test_commit(self, git_repo):
        """Test creating a commit"""
        tools = GitTools(repo_path=git_repo)

        # Create and stage a file
        (git_repo / "commit_test.txt").write_text("commit test")
        tools.stage_files(files=["commit_test.txt"])

        result = tools.commit("Test commit message", no_gpg_sign=True)

        assert result.success is True
        assert "sha" in result.data

    def test_commit_empty_message(self, git_repo):
        """Test commit with empty message fails"""
        tools = GitTools(repo_path=git_repo)

        result = tools.commit("")

        assert result.success is False
        assert "message" in result.error.lower()

    def test_get_file_history(self, git_repo):
        """Test getting file history"""
        tools = GitTools(repo_path=git_repo)

        result = tools.get_file_history("README.md")

        assert result.success is True
        assert "commits" in result.data


class TestGitToolsSafety:
    """اختبارات الأمان"""

    def test_safe_commands_allowed(self):
        """Test that safe commands are allowed"""
        tools = GitTools(safe_mode=True)

        # These should be in safe commands
        assert "status" in tools.SAFE_COMMANDS
        assert "log" in tools.SAFE_COMMANDS
        assert "diff" in tools.SAFE_COMMANDS

    def test_dangerous_commands_blocked(self):
        """Test that dangerous commands are blocked"""
        tools = GitTools(safe_mode=True)

        # These should be in dangerous commands
        assert "push --force" in tools.DANGEROUS_COMMANDS
        assert "reset --hard" in tools.DANGEROUS_COMMANDS


class TestDiffParsing:
    """اختبارات تحليل الفروق"""

    def test_parse_simple_diff(self):
        """Test parsing a simple diff"""
        tools = GitTools()

        diff_output = """diff --git a/file.py b/file.py
--- a/file.py
+++ b/file.py
@@ -1,3 +1,4 @@
 line 1
-old line
+new line
+added line
 line 3
"""
        diffs = tools._parse_diff(diff_output)

        assert len(diffs) == 1
        assert diffs[0].file_path == "file.py"
        assert diffs[0].additions >= 1
        assert diffs[0].deletions >= 1

    def test_parse_multiple_files_diff(self):
        """Test parsing diff with multiple files"""
        tools = GitTools()

        diff_output = """diff --git a/file1.py b/file1.py
--- a/file1.py
+++ b/file1.py
@@ -1 +1 @@
-old
+new
diff --git a/file2.py b/file2.py
--- a/file2.py
+++ b/file2.py
@@ -1 +1 @@
-old2
+new2
"""
        diffs = tools._parse_diff(diff_output)

        assert len(diffs) == 2


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
