"""
SAHOOL Code Fix Agent - Git Integration Tools
أدوات التكامل مع Git

Provides Git operations for the code fix agent:
- Repository management
- Branch operations
- Commit and diff analysis
- PR creation and management
"""

import os
import re
import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class GitOperationType(Enum):
    """أنواع عمليات Git"""

    CLONE = "clone"
    CHECKOUT = "checkout"
    COMMIT = "commit"
    PUSH = "push"
    PULL = "pull"
    DIFF = "diff"
    BRANCH = "branch"
    MERGE = "merge"
    STASH = "stash"
    STATUS = "status"
    LOG = "log"


class FileChangeType(Enum):
    """أنواع تغييرات الملفات"""

    ADDED = "A"
    MODIFIED = "M"
    DELETED = "D"
    RENAMED = "R"
    COPIED = "C"
    UNTRACKED = "?"


@dataclass
class FileChange:
    """تغيير في ملف"""

    path: str
    change_type: FileChangeType
    old_path: str | None = None  # For renames
    additions: int = 0
    deletions: int = 0
    diff_content: str = ""


@dataclass
class CommitInfo:
    """معلومات الالتزام"""

    sha: str
    short_sha: str
    author: str
    author_email: str
    date: datetime
    message: str
    files_changed: list[FileChange] = field(default_factory=list)


@dataclass
class BranchInfo:
    """معلومات الفرع"""

    name: str
    is_current: bool
    tracking: str | None = None
    ahead: int = 0
    behind: int = 0
    last_commit: CommitInfo | None = None


@dataclass
class DiffHunk:
    """قطعة من الفرق"""

    old_start: int
    old_count: int
    new_start: int
    new_count: int
    header: str
    lines: list[str]


@dataclass
class FileDiff:
    """فرق ملف"""

    file_path: str
    old_path: str | None
    change_type: FileChangeType
    hunks: list[DiffHunk]
    is_binary: bool = False
    additions: int = 0
    deletions: int = 0


@dataclass
class GitOperationResult:
    """نتيجة عملية Git"""

    success: bool
    operation: GitOperationType
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    duration_ms: float = 0.0


class GitTools:
    """
    أدوات Git للوكيل
    Git Tools for Code Fix Agent

    Provides safe Git operations with:
    - Repository validation
    - Error handling
    - Audit logging
    - Rollback support
    """

    # Safe commands that can be run without confirmation
    SAFE_COMMANDS = {
        "status",
        "log",
        "diff",
        "show",
        "branch",
        "remote",
        "fetch",
        "ls-files",
        "rev-parse",
        "describe",
        "tag",
    }

    # Commands that modify state and need caution
    MODIFYING_COMMANDS = {
        "add",
        "commit",
        "push",
        "pull",
        "merge",
        "rebase",
        "checkout",
        "reset",
        "stash",
        "cherry-pick",
    }

    # Dangerous commands that should be blocked or require confirmation
    DANGEROUS_COMMANDS = {"push --force", "reset --hard", "clean -fd", "rebase -i", "filter-branch"}

    def __init__(
        self,
        repo_path: str | Path | None = None,
        safe_mode: bool = True,
        max_diff_size: int = 1_000_000,  # 1MB
    ):
        """
        تهيئة أدوات Git

        Args:
            repo_path: مسار المستودع (اختياري)
            safe_mode: وضع آمن يمنع العمليات الخطرة
            max_diff_size: الحد الأقصى لحجم الفرق
        """
        self.repo_path = Path(repo_path) if repo_path else None
        self.safe_mode = safe_mode
        self.max_diff_size = max_diff_size
        self._validate_git_available()

    def _validate_git_available(self) -> None:
        """التحقق من توفر Git"""
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                raise RuntimeError("Git is not available")
            logger.debug("git_available", version=result.stdout.strip())
        except FileNotFoundError:
            raise RuntimeError("Git executable not found")

    def _run_git_command(
        self,
        args: list[str],
        cwd: Path | None = None,
        timeout: int = 60,
        check_dangerous: bool = True,
    ) -> subprocess.CompletedProcess:
        """
        تنفيذ أمر Git

        Args:
            args: معطيات الأمر
            cwd: مسار العمل
            timeout: المهلة الزمنية
            check_dangerous: التحقق من الأوامر الخطرة
        """
        command = " ".join(args)

        # Check for dangerous commands in safe mode
        if self.safe_mode and check_dangerous:
            for dangerous in self.DANGEROUS_COMMANDS:
                if dangerous in command:
                    raise ValueError(f"Dangerous command blocked: {dangerous}")

        work_dir = cwd or self.repo_path

        logger.debug("git_command", args=args, cwd=str(work_dir))

        # nosemgrep: dangerous-subprocess-use-audit -- internal tooling (Auto-Fix/diagnostics); args are hardcoded program names + validated paths, not user-controlled shell strings
        result = subprocess.run(
            ["git"] + args,
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode != 0:
            logger.warning(
                "git_command_failed",
                args=args,
                stderr=result.stderr,
                returncode=result.returncode,
            )

        return result

    def is_git_repository(self, path: Path | None = None) -> bool:
        """التحقق من كون المسار مستودع Git"""
        check_path = path or self.repo_path
        if not check_path:
            return False

        try:
            result = self._run_git_command(
                ["rev-parse", "--git-dir"],
                cwd=check_path,
                check_dangerous=False,
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_status(self, path: Path | None = None) -> GitOperationResult:
        """
        الحصول على حالة المستودع
        Get repository status
        """
        start = datetime.now()
        work_path = path or self.repo_path

        try:
            result = self._run_git_command(
                ["status", "--porcelain", "-b"],
                cwd=work_path,
                check_dangerous=False,
            )

            if result.returncode != 0:
                return GitOperationResult(
                    success=False,
                    operation=GitOperationType.STATUS,
                    message="Failed to get status",
                    error=result.stderr,
                )

            # Parse status output
            lines = result.stdout.strip().split("\n")
            branch_info = lines[0] if lines else ""
            file_changes = []

            for line in lines[1:]:
                if not line:
                    continue
                status = line[:2]
                file_path = line[3:]

                change_type = FileChangeType.MODIFIED
                if "A" in status:
                    change_type = FileChangeType.ADDED
                elif "D" in status:
                    change_type = FileChangeType.DELETED
                elif "R" in status:
                    change_type = FileChangeType.RENAMED
                elif "?" in status:
                    change_type = FileChangeType.UNTRACKED

                file_changes.append(
                    FileChange(
                        path=file_path,
                        change_type=change_type,
                    )
                )

            duration = (datetime.now() - start).total_seconds() * 1000

            return GitOperationResult(
                success=True,
                operation=GitOperationType.STATUS,
                message="Status retrieved successfully",
                data={
                    "branch": branch_info,
                    "changes": [{"path": f.path, "type": f.change_type.value} for f in file_changes],
                    "clean": len(file_changes) == 0,
                },
                duration_ms=duration,
            )

        except Exception as e:
            logger.error("git_status_error", error=str(e))
            return GitOperationResult(
                success=False,
                operation=GitOperationType.STATUS,
                message="Error getting status",
                error=str(e),
            )

    def get_diff(
        self,
        target: str = "HEAD",
        path: Path | None = None,
        staged: bool = False,
        context_lines: int = 3,
    ) -> GitOperationResult:
        """
        الحصول على فرق الكود
        Get code diff
        """
        start = datetime.now()
        work_path = path or self.repo_path

        try:
            args = ["diff"]
            if staged:
                args.append("--staged")
            args.extend([f"-U{context_lines}", target])

            result = self._run_git_command(
                args,
                cwd=work_path,
                check_dangerous=False,
            )

            # Check diff size
            if len(result.stdout) > self.max_diff_size:
                return GitOperationResult(
                    success=False,
                    operation=GitOperationType.DIFF,
                    message="Diff too large",
                    error=f"Diff size {len(result.stdout)} exceeds limit {self.max_diff_size}",
                )

            # Parse diff
            diffs = self._parse_diff(result.stdout)
            duration = (datetime.now() - start).total_seconds() * 1000

            return GitOperationResult(
                success=True,
                operation=GitOperationType.DIFF,
                message="Diff retrieved successfully",
                data={
                    "raw_diff": result.stdout,
                    "files": [
                        {
                            "path": d.file_path,
                            "old_path": d.old_path,
                            "type": d.change_type.value,
                            "additions": d.additions,
                            "deletions": d.deletions,
                            "is_binary": d.is_binary,
                            "hunks_count": len(d.hunks),
                        }
                        for d in diffs
                    ],
                    "total_additions": sum(d.additions for d in diffs),
                    "total_deletions": sum(d.deletions for d in diffs),
                },
                duration_ms=duration,
            )

        except Exception as e:
            logger.error("git_diff_error", error=str(e))
            return GitOperationResult(
                success=False,
                operation=GitOperationType.DIFF,
                message="Error getting diff",
                error=str(e),
            )

    def _parse_diff(self, diff_output: str) -> list[FileDiff]:
        """تحليل مخرجات الفرق"""
        diffs: list[FileDiff] = []
        current_file: FileDiff | None = None
        current_hunk: DiffHunk | None = None

        # Regex patterns
        file_pattern = re.compile(r"^diff --git a/(.*) b/(.*)$")
        hunk_pattern = re.compile(r"^@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@(.*)$")
        binary_pattern = re.compile(r"^Binary files .* differ$")

        for line in diff_output.split("\n"):
            # New file
            file_match = file_pattern.match(line)
            if file_match:
                if current_file:
                    if current_hunk:
                        current_file.hunks.append(current_hunk)
                    diffs.append(current_file)

                old_path, new_path = file_match.groups()
                current_file = FileDiff(
                    file_path=new_path,
                    old_path=old_path if old_path != new_path else None,
                    change_type=FileChangeType.MODIFIED,
                    hunks=[],
                )
                current_hunk = None
                continue

            # Binary file
            if current_file and binary_pattern.match(line):
                current_file.is_binary = True
                continue

            # New hunk
            hunk_match = hunk_pattern.match(line)
            if hunk_match and current_file:
                if current_hunk:
                    current_file.hunks.append(current_hunk)

                groups = hunk_match.groups()
                current_hunk = DiffHunk(
                    old_start=int(groups[0]),
                    old_count=int(groups[1]) if groups[1] else 1,
                    new_start=int(groups[2]),
                    new_count=int(groups[3]) if groups[3] else 1,
                    header=groups[4],
                    lines=[],
                )
                continue

            # Diff line
            if current_hunk and current_file:
                current_hunk.lines.append(line)
                if line.startswith("+") and not line.startswith("+++"):
                    current_file.additions += 1
                elif line.startswith("-") and not line.startswith("---"):
                    current_file.deletions += 1

        # Add last file
        if current_file:
            if current_hunk:
                current_file.hunks.append(current_hunk)
            diffs.append(current_file)

        return diffs

    def get_log(
        self,
        limit: int = 10,
        path: Path | None = None,
        since: datetime | None = None,
        author: str | None = None,
    ) -> GitOperationResult:
        """
        الحصول على سجل الالتزامات
        Get commit log
        """
        start = datetime.now()
        work_path = path or self.repo_path

        try:
            args = [
                "log",
                f"-n{limit}",
                "--format=%H|%h|%an|%ae|%aI|%s",
            ]

            if since:
                args.append(f"--since={since.isoformat()}")
            if author:
                args.append(f"--author={author}")

            result = self._run_git_command(
                args,
                cwd=work_path,
                check_dangerous=False,
            )

            if result.returncode != 0:
                return GitOperationResult(
                    success=False,
                    operation=GitOperationType.LOG,
                    message="Failed to get log",
                    error=result.stderr,
                )

            commits = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("|")
                if len(parts) >= 6:
                    commits.append(
                        CommitInfo(
                            sha=parts[0],
                            short_sha=parts[1],
                            author=parts[2],
                            author_email=parts[3],
                            date=datetime.fromisoformat(parts[4]),
                            message="|".join(parts[5:]),  # Message might contain |
                        )
                    )

            duration = (datetime.now() - start).total_seconds() * 1000

            return GitOperationResult(
                success=True,
                operation=GitOperationType.LOG,
                message=f"Retrieved {len(commits)} commits",
                data={
                    "commits": [
                        {
                            "sha": c.sha,
                            "short_sha": c.short_sha,
                            "author": c.author,
                            "author_email": c.author_email,
                            "date": c.date.isoformat(),
                            "message": c.message,
                        }
                        for c in commits
                    ],
                },
                duration_ms=duration,
            )

        except Exception as e:
            logger.error("git_log_error", error=str(e))
            return GitOperationResult(
                success=False,
                operation=GitOperationType.LOG,
                message="Error getting log",
                error=str(e),
            )

    def get_branches(self, path: Path | None = None) -> GitOperationResult:
        """
        الحصول على قائمة الفروع
        Get branch list
        """
        start = datetime.now()
        work_path = path or self.repo_path

        try:
            result = self._run_git_command(
                [
                    "branch",
                    "-vv",
                    "--format=%(refname:short)|%(upstream:short)|%(HEAD)|%(upstream:track)",
                ],
                cwd=work_path,
                check_dangerous=False,
            )

            if result.returncode != 0:
                return GitOperationResult(
                    success=False,
                    operation=GitOperationType.BRANCH,
                    message="Failed to get branches",
                    error=result.stderr,
                )

            branches = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("|")
                if len(parts) >= 3:
                    name = parts[0]
                    tracking = parts[1] if parts[1] else None
                    is_current = parts[2] == "*"
                    track_info = parts[3] if len(parts) > 3 else ""

                    # Parse ahead/behind
                    ahead = behind = 0
                    if "ahead" in track_info:
                        match = re.search(r"ahead (\d+)", track_info)
                        if match:
                            ahead = int(match.group(1))
                    if "behind" in track_info:
                        match = re.search(r"behind (\d+)", track_info)
                        if match:
                            behind = int(match.group(1))

                    branches.append(
                        BranchInfo(
                            name=name,
                            is_current=is_current,
                            tracking=tracking,
                            ahead=ahead,
                            behind=behind,
                        )
                    )

            duration = (datetime.now() - start).total_seconds() * 1000

            return GitOperationResult(
                success=True,
                operation=GitOperationType.BRANCH,
                message=f"Found {len(branches)} branches",
                data={
                    "branches": [
                        {
                            "name": b.name,
                            "is_current": b.is_current,
                            "tracking": b.tracking,
                            "ahead": b.ahead,
                            "behind": b.behind,
                        }
                        for b in branches
                    ],
                    "current": next((b.name for b in branches if b.is_current), None),
                },
                duration_ms=duration,
            )

        except Exception as e:
            logger.error("git_branches_error", error=str(e))
            return GitOperationResult(
                success=False,
                operation=GitOperationType.BRANCH,
                message="Error getting branches",
                error=str(e),
            )

    def create_branch(
        self,
        branch_name: str,
        base: str = "HEAD",
        checkout: bool = True,
        path: Path | None = None,
    ) -> GitOperationResult:
        """
        إنشاء فرع جديد
        Create new branch
        """
        start = datetime.now()
        work_path = path or self.repo_path

        # Validate branch name
        if not self._is_valid_branch_name(branch_name):
            return GitOperationResult(
                success=False,
                operation=GitOperationType.BRANCH,
                message="Invalid branch name",
                error=f"Branch name '{branch_name}' is not valid",
            )

        try:
            if checkout:
                result = self._run_git_command(
                    ["checkout", "-b", branch_name, base],
                    cwd=work_path,
                )
            else:
                result = self._run_git_command(
                    ["branch", branch_name, base],
                    cwd=work_path,
                )

            duration = (datetime.now() - start).total_seconds() * 1000

            if result.returncode != 0:
                return GitOperationResult(
                    success=False,
                    operation=GitOperationType.BRANCH,
                    message="Failed to create branch",
                    error=result.stderr,
                    duration_ms=duration,
                )

            return GitOperationResult(
                success=True,
                operation=GitOperationType.BRANCH,
                message=f"Branch '{branch_name}' created successfully",
                data={
                    "branch": branch_name,
                    "base": base,
                    "checked_out": checkout,
                },
                duration_ms=duration,
            )

        except Exception as e:
            logger.error("git_create_branch_error", error=str(e))
            return GitOperationResult(
                success=False,
                operation=GitOperationType.BRANCH,
                message="Error creating branch",
                error=str(e),
            )

    def _is_valid_branch_name(self, name: str) -> bool:
        """التحقق من صحة اسم الفرع"""
        # Git branch naming rules
        invalid_patterns = [
            r"^\.",  # Cannot start with .
            r"\.\.",  # Cannot contain ..
            r"~",  # Cannot contain ~
            r"\^",  # Cannot contain ^
            r":",  # Cannot contain :
            r"\s",  # Cannot contain whitespace
            r"@\{",  # Cannot contain @{
            r"\\",  # Cannot contain \
            r"^\-",  # Cannot start with -
            r"\.lock$",  # Cannot end with .lock
            r"/$",  # Cannot end with /
        ]

        for pattern in invalid_patterns:
            if re.search(pattern, name):
                return False

        return len(name) > 0 and len(name) < 255

    def stage_files(
        self,
        files: list[str] | None = None,
        all_files: bool = False,
        path: Path | None = None,
    ) -> GitOperationResult:
        """
        إضافة الملفات للتجهيز
        Stage files for commit
        """
        start = datetime.now()
        work_path = path or self.repo_path

        try:
            if all_files:
                args = ["add", "-A"]
            elif files:
                args = ["add"] + files
            else:
                return GitOperationResult(
                    success=False,
                    operation=GitOperationType.COMMIT,
                    message="No files specified",
                    error="Either files or all_files must be provided",
                )

            result = self._run_git_command(args, cwd=work_path)

            duration = (datetime.now() - start).total_seconds() * 1000

            if result.returncode != 0:
                return GitOperationResult(
                    success=False,
                    operation=GitOperationType.COMMIT,
                    message="Failed to stage files",
                    error=result.stderr,
                    duration_ms=duration,
                )

            return GitOperationResult(
                success=True,
                operation=GitOperationType.COMMIT,
                message="Files staged successfully",
                data={
                    "files": files,
                    "all": all_files,
                },
                duration_ms=duration,
            )

        except Exception as e:
            logger.error("git_stage_error", error=str(e))
            return GitOperationResult(
                success=False,
                operation=GitOperationType.COMMIT,
                message="Error staging files",
                error=str(e),
            )

    def commit(
        self,
        message: str,
        author: str | None = None,
        path: Path | None = None,
        no_gpg_sign: bool = False,
    ) -> GitOperationResult:
        """
        إنشاء التزام
        Create commit

        Args:
            message: Commit message
            author: Optional author override
            path: Optional path override
            no_gpg_sign: Skip GPG signing (useful for tests)
        """
        start = datetime.now()
        work_path = path or self.repo_path

        if not message or len(message.strip()) == 0:
            return GitOperationResult(
                success=False,
                operation=GitOperationType.COMMIT,
                message="Commit message required",
                error="Commit message cannot be empty",
            )

        try:
            args = ["commit", "-m", message]
            if author:
                args.extend(["--author", author])
            if no_gpg_sign:
                args.append("--no-gpg-sign")

            result = self._run_git_command(args, cwd=work_path)

            duration = (datetime.now() - start).total_seconds() * 1000

            if result.returncode != 0:
                return GitOperationResult(
                    success=False,
                    operation=GitOperationType.COMMIT,
                    message="Failed to create commit",
                    error=result.stderr,
                    duration_ms=duration,
                )

            # Get commit SHA
            sha_result = self._run_git_command(
                ["rev-parse", "HEAD"],
                cwd=work_path,
                check_dangerous=False,
            )

            return GitOperationResult(
                success=True,
                operation=GitOperationType.COMMIT,
                message="Commit created successfully",
                data={
                    "sha": sha_result.stdout.strip() if sha_result.returncode == 0 else None,
                    "message": message,
                },
                duration_ms=duration,
            )

        except Exception as e:
            logger.error("git_commit_error", error=str(e))
            return GitOperationResult(
                success=False,
                operation=GitOperationType.COMMIT,
                message="Error creating commit",
                error=str(e),
            )

    def clone_repository(
        self,
        url: str,
        target_path: Path,
        branch: str | None = None,
        depth: int | None = None,
    ) -> GitOperationResult:
        """
        استنساخ مستودع
        Clone repository
        """
        start = datetime.now()

        # Validate URL
        if not self._is_valid_git_url(url):
            return GitOperationResult(
                success=False,
                operation=GitOperationType.CLONE,
                message="Invalid Git URL",
                error=f"URL '{url}' is not a valid Git URL",
            )

        try:
            args = ["clone"]
            if branch:
                args.extend(["--branch", branch])
            if depth:
                args.extend(["--depth", str(depth)])
            args.extend([url, str(target_path)])

            # nosemgrep: dangerous-subprocess-use-audit -- internal tooling (Auto-Fix/diagnostics); args are hardcoded program names + validated paths, not user-controlled shell strings
            result = subprocess.run(
                ["git"] + args,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes for clone
            )

            duration = (datetime.now() - start).total_seconds() * 1000

            if result.returncode != 0:
                return GitOperationResult(
                    success=False,
                    operation=GitOperationType.CLONE,
                    message="Failed to clone repository",
                    error=result.stderr,
                    duration_ms=duration,
                )

            return GitOperationResult(
                success=True,
                operation=GitOperationType.CLONE,
                message="Repository cloned successfully",
                data={
                    "url": url,
                    "path": str(target_path),
                    "branch": branch,
                },
                duration_ms=duration,
            )

        except subprocess.TimeoutExpired:
            return GitOperationResult(
                success=False,
                operation=GitOperationType.CLONE,
                message="Clone timed out",
                error="Clone operation exceeded 5 minute timeout",
            )
        except Exception as e:
            logger.error("git_clone_error", error=str(e))
            return GitOperationResult(
                success=False,
                operation=GitOperationType.CLONE,
                message="Error cloning repository",
                error=str(e),
            )

    def _is_valid_git_url(self, url: str) -> bool:
        """التحقق من صحة رابط Git"""
        git_url_patterns = [
            r"^https?://.*\.git$",
            r"^https?://github\.com/",
            r"^https?://gitlab\.com/",
            r"^https?://bitbucket\.org/",
            r"^git@.*:.*\.git$",
            r"^ssh://git@.*",
        ]

        return any(re.match(pattern, url) for pattern in git_url_patterns)

    def get_file_history(
        self,
        file_path: str,
        limit: int = 10,
        repo_path: Path | None = None,
    ) -> GitOperationResult:
        """
        الحصول على تاريخ ملف
        Get file history
        """
        start = datetime.now()
        work_path = repo_path or self.repo_path

        try:
            result = self._run_git_command(
                ["log", f"-n{limit}", "--format=%H|%h|%an|%aI|%s", "--", file_path],
                cwd=work_path,
                check_dangerous=False,
            )

            if result.returncode != 0:
                return GitOperationResult(
                    success=False,
                    operation=GitOperationType.LOG,
                    message="Failed to get file history",
                    error=result.stderr,
                )

            commits = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("|")
                if len(parts) >= 5:
                    commits.append(
                        {
                            "sha": parts[0],
                            "short_sha": parts[1],
                            "author": parts[2],
                            "date": parts[3],
                            "message": "|".join(parts[4:]),
                        }
                    )

            duration = (datetime.now() - start).total_seconds() * 1000

            return GitOperationResult(
                success=True,
                operation=GitOperationType.LOG,
                message=f"Found {len(commits)} commits for {file_path}",
                data={
                    "file": file_path,
                    "commits": commits,
                },
                duration_ms=duration,
            )

        except Exception as e:
            logger.error("git_file_history_error", error=str(e))
            return GitOperationResult(
                success=False,
                operation=GitOperationType.LOG,
                message="Error getting file history",
                error=str(e),
            )

    def get_blame(
        self,
        file_path: str,
        repo_path: Path | None = None,
    ) -> GitOperationResult:
        """
        الحصول على معلومات التأليف
        Get blame information
        """
        start = datetime.now()
        work_path = repo_path or self.repo_path

        try:
            result = self._run_git_command(
                ["blame", "--porcelain", file_path],
                cwd=work_path,
                check_dangerous=False,
            )

            if result.returncode != 0:
                return GitOperationResult(
                    success=False,
                    operation=GitOperationType.LOG,
                    message="Failed to get blame",
                    error=result.stderr,
                )

            # Parse blame output (simplified)
            duration = (datetime.now() - start).total_seconds() * 1000

            return GitOperationResult(
                success=True,
                operation=GitOperationType.LOG,
                message=f"Blame retrieved for {file_path}",
                data={
                    "file": file_path,
                    "raw_blame": result.stdout[:10000],  # Limit output
                },
                duration_ms=duration,
            )

        except Exception as e:
            logger.error("git_blame_error", error=str(e))
            return GitOperationResult(
                success=False,
                operation=GitOperationType.LOG,
                message="Error getting blame",
                error=str(e),
            )
