"""
Batch Processor for Code Fixes
==============================
معالج الدُفعات لإصلاحات الكود

Provides batch processing capabilities for large-scale code analysis
and automated fixing across multiple files and repositories.

Features:
- Parallel file processing with configurable concurrency
- Progress tracking and reporting
- Incremental processing (resume from checkpoint)
- Memory-efficient streaming
- Integration with CI/CD pipelines

Author: SAHOOL Platform Team
Created: January 2026
"""

import asyncio
import json
import os
import time
import uuid
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

import structlog

from .diagnostics import CodeDiagnostics, DiagnosticError
from .engine import AutoFixEngine
from .models import (
    FixStrategy,
)

logger = structlog.get_logger()


# ============================================================================
# DATA MODELS
# ============================================================================


class BatchStatus(StrEnum):
    """Batch processing status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class BatchConfig:
    """
    Configuration for batch processing.
    تكوين معالجة الدُفعات
    """

    # Concurrency settings
    max_concurrent_files: int = 10
    max_concurrent_fixes: int = 5

    # File selection
    include_patterns: list[str] = field(default_factory=lambda: ["*.py", "*.ts", "*.tsx", "*.js"])
    exclude_patterns: list[str] = field(
        default_factory=lambda: [
            "**/node_modules/**",
            "**/.venv/**",
            "**/__pycache__/**",
            "**/dist/**",
            "**/build/**",
            "**/.git/**",
        ]
    )
    max_file_size_kb: int = 500

    # Processing settings
    fix_strategy: FixStrategy = FixStrategy.SAFE
    dry_run: bool = False
    stop_on_error: bool = False

    # Checkpoint settings
    enable_checkpoints: bool = True
    checkpoint_interval: int = 50  # Save checkpoint every N files

    # Output settings
    output_format: str = "json"  # json, markdown, sarif
    generate_report: bool = True


@dataclass
class FileResult:
    """Result for a single file in batch processing."""

    file_path: str
    status: str  # success, skipped, error
    diagnostics_count: int = 0
    fixes_applied: int = 0
    duration_ms: float = 0
    error: str | None = None


@dataclass
class BatchProgress:
    """Progress tracking for batch processing."""

    total_files: int = 0
    processed_files: int = 0
    successful_files: int = 0
    failed_files: int = 0
    skipped_files: int = 0
    total_diagnostics: int = 0
    total_fixes: int = 0
    current_file: str | None = None
    start_time: datetime | None = None
    estimated_remaining_seconds: float | None = None


@dataclass
class BatchResult:
    """
    Result of batch processing.
    نتيجة معالجة الدُفعات
    """

    batch_id: str
    status: BatchStatus
    config: BatchConfig
    progress: BatchProgress
    file_results: list[FileResult] = field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    errors: list[str] = field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return 0

    @property
    def success_rate(self) -> float:
        if self.progress.processed_files == 0:
            return 0
        return self.progress.successful_files / self.progress.processed_files * 100

    def to_dict(self) -> dict[str, Any]:
        return {
            "batch_id": self.batch_id,
            "status": self.status.value,
            "duration_seconds": self.duration_seconds,
            "success_rate": self.success_rate,
            "progress": {
                "total_files": self.progress.total_files,
                "processed_files": self.progress.processed_files,
                "successful_files": self.progress.successful_files,
                "failed_files": self.progress.failed_files,
                "skipped_files": self.progress.skipped_files,
                "total_diagnostics": self.progress.total_diagnostics,
                "total_fixes": self.progress.total_fixes,
            },
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "errors": self.errors[:10],  # Limit errors in output
        }


@dataclass
class Checkpoint:
    """Checkpoint for resumable processing."""

    batch_id: str
    processed_files: list[str]
    last_file: str | None
    progress: BatchProgress
    timestamp: datetime


# ============================================================================
# BATCH PROCESSOR
# ============================================================================


class BatchProcessor:
    """
    Batch processor for large-scale code analysis and fixing.
    معالج الدُفعات لتحليل وإصلاح الكود على نطاق واسع

    Provides:
    - Parallel processing of multiple files
    - Progress tracking with callbacks
    - Checkpoint/resume capability
    - Memory-efficient streaming
    - CI/CD integration

    Example:
        processor = BatchProcessor()

        # Process directory with progress tracking
        async for progress in processor.process_directory_stream(
            "/path/to/repo",
            config=BatchConfig(max_concurrent_files=20)
        ):
            print(f"Progress: {progress.processed_files}/{progress.total_files}")

        # Get final result
        result = await processor.get_result()
        print(f"Fixed {result.progress.total_fixes} issues")
    """

    def __init__(
        self,
        diagnostics: CodeDiagnostics | None = None,
        fix_engine: AutoFixEngine | None = None,
        checkpoint_dir: str | None = None,
    ):
        """
        Initialize batch processor.

        Args:
            diagnostics: Code diagnostics engine
            fix_engine: Auto-fix engine
            checkpoint_dir: Directory for storing checkpoints
        """
        self._diagnostics = diagnostics or CodeDiagnostics()
        self._fix_engine = fix_engine
        self._checkpoint_dir = checkpoint_dir or ".sahool/checkpoints"

        self._current_batch: BatchResult | None = None
        self._is_running = False
        self._cancel_requested = False
        self._semaphore: asyncio.Semaphore | None = None

        # Callbacks
        self._progress_callbacks: list[Callable[[BatchProgress], None]] = []
        self._file_callbacks: list[Callable[[FileResult], None]] = []

    def on_progress(self, callback: Callable[[BatchProgress], None]) -> None:
        """Register progress callback."""
        self._progress_callbacks.append(callback)

    def on_file_complete(self, callback: Callable[[FileResult], None]) -> None:
        """Register file completion callback."""
        self._file_callbacks.append(callback)

    def _notify_progress(self, progress: BatchProgress) -> None:
        """Notify progress callbacks."""
        for callback in self._progress_callbacks:
            try:
                callback(progress)
            except Exception as e:
                logger.warning("Progress callback failed", error=str(e))

    def _notify_file_complete(self, result: FileResult) -> None:
        """Notify file completion callbacks."""
        for callback in self._file_callbacks:
            try:
                callback(result)
            except Exception as e:
                logger.warning("File callback failed", error=str(e))

    async def process_directory(
        self,
        directory: str,
        config: BatchConfig | None = None,
        resume_batch_id: str | None = None,
    ) -> BatchResult:
        """
        Process all files in a directory.
        معالجة جميع الملفات في مجلد

        Args:
            directory: Directory path to process
            config: Batch configuration
            resume_batch_id: ID of batch to resume (if any)

        Returns:
            BatchResult with processing summary
        """
        async for _ in self.process_directory_stream(directory, config, resume_batch_id):
            pass

        return self._current_batch

    async def process_directory_stream(
        self,
        directory: str,
        config: BatchConfig | None = None,
        resume_batch_id: str | None = None,
    ) -> AsyncIterator[BatchProgress]:
        """
        Process directory with streaming progress updates.
        معالجة المجلد مع تحديثات التقدم المتدفقة

        Yields progress updates as files are processed.
        """
        config = config or BatchConfig()

        # Initialize or resume batch
        if resume_batch_id:
            checkpoint = self._load_checkpoint(resume_batch_id)
            if checkpoint:
                self._current_batch = BatchResult(
                    batch_id=checkpoint.batch_id,
                    status=BatchStatus.RUNNING,
                    config=config,
                    progress=checkpoint.progress,
                )
                processed_files = set(checkpoint.processed_files)
            else:
                raise ValueError(f"Checkpoint not found: {resume_batch_id}")
        else:
            self._current_batch = BatchResult(
                batch_id=str(uuid.uuid4()),
                status=BatchStatus.RUNNING,
                config=config,
                progress=BatchProgress(),
            )
            processed_files = set()

        self._current_batch.started_at = datetime.now(UTC)
        self._current_batch.progress.start_time = self._current_batch.started_at
        self._is_running = True
        self._cancel_requested = False

        # Initialize semaphore for concurrency control
        self._semaphore = asyncio.Semaphore(config.max_concurrent_files)

        # Discover files
        files = self._discover_files(directory, config, processed_files)
        self._current_batch.progress.total_files = len(files) + len(processed_files)

        logger.info(
            "batch_processing_started",
            batch_id=self._current_batch.batch_id,
            total_files=self._current_batch.progress.total_files,
            new_files=len(files),
        )

        yield self._current_batch.progress

        # Process files concurrently
        tasks = []
        for i, file_path in enumerate(files):
            if self._cancel_requested:
                break

            task = asyncio.create_task(self._process_file_with_semaphore(file_path, config))
            tasks.append(task)

            # Yield progress periodically
            if len(tasks) >= config.max_concurrent_files:
                done, pending = await asyncio.wait(
                    tasks,
                    return_when=asyncio.FIRST_COMPLETED,
                )

                for completed_task in done:
                    result = await completed_task
                    self._update_progress(result)
                    yield self._current_batch.progress

                tasks = list(pending)

            # Save checkpoint periodically
            if config.enable_checkpoints and i > 0 and i % config.checkpoint_interval == 0:
                self._save_checkpoint()

        # Wait for remaining tasks
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, FileResult):
                    self._update_progress(result)
                    yield self._current_batch.progress
                elif isinstance(result, Exception):
                    self._current_batch.errors.append(str(result))

        # Finalize
        self._current_batch.completed_at = datetime.now(UTC)
        self._current_batch.status = BatchStatus.CANCELLED if self._cancel_requested else BatchStatus.COMPLETED
        self._is_running = False

        # Final checkpoint
        if config.enable_checkpoints:
            self._save_checkpoint()

        logger.info(
            "batch_processing_completed",
            batch_id=self._current_batch.batch_id,
            status=self._current_batch.status.value,
            duration=self._current_batch.duration_seconds,
            success_rate=self._current_batch.success_rate,
        )

        yield self._current_batch.progress

    async def _process_file_with_semaphore(
        self,
        file_path: str,
        config: BatchConfig,
    ) -> FileResult:
        """Process a file with semaphore for concurrency control."""
        async with self._semaphore:
            return await self._process_single_file(file_path, config)

    async def _process_single_file(
        self,
        file_path: str,
        config: BatchConfig,
    ) -> FileResult:
        """Process a single file."""
        start_time = time.time()

        try:
            # Check file size
            file_size = os.path.getsize(file_path) / 1024  # KB
            if file_size > config.max_file_size_kb:
                return FileResult(
                    file_path=file_path,
                    status="skipped",
                    error=f"File too large: {file_size:.1f}KB",
                )

            # Run diagnostics
            report = await self._diagnostics.diagnose_file(file_path)

            diagnostics_count = len(report.diagnostics)
            fixes_applied = 0

            # Apply fixes if not dry run and engine available
            if not config.dry_run and self._fix_engine and report.diagnostics:
                try:
                    fix_results = await self._fix_engine.auto_fix(
                        report,
                        strategy=config.fix_strategy,
                        dry_run=False,
                    )
                    fixes_applied = sum(1 for r in fix_results if r.success)
                except Exception as e:
                    logger.warning("Fix failed", file=file_path, error=str(e))

            duration = (time.time() - start_time) * 1000

            return FileResult(
                file_path=file_path,
                status="success",
                diagnostics_count=diagnostics_count,
                fixes_applied=fixes_applied,
                duration_ms=duration,
            )

        except DiagnosticError as e:
            return FileResult(
                file_path=file_path,
                status="error",
                error=str(e),
                duration_ms=(time.time() - start_time) * 1000,
            )
        except Exception as e:
            logger.error("File processing failed", file=file_path, error=str(e))
            return FileResult(
                file_path=file_path,
                status="error",
                error=str(e),
                duration_ms=(time.time() - start_time) * 1000,
            )

    def _update_progress(self, result: FileResult) -> None:
        """Update progress with file result."""
        if not self._current_batch:
            return

        self._current_batch.file_results.append(result)
        self._current_batch.progress.processed_files += 1
        self._current_batch.progress.current_file = result.file_path

        if result.status == "success":
            self._current_batch.progress.successful_files += 1
            self._current_batch.progress.total_diagnostics += result.diagnostics_count
            self._current_batch.progress.total_fixes += result.fixes_applied
        elif result.status == "skipped":
            self._current_batch.progress.skipped_files += 1
        else:
            self._current_batch.progress.failed_files += 1

        # Calculate estimated remaining time
        if self._current_batch.progress.start_time:
            elapsed = (datetime.now(UTC) - self._current_batch.progress.start_time).total_seconds()
            if self._current_batch.progress.processed_files > 0:
                rate = elapsed / self._current_batch.progress.processed_files
                remaining = self._current_batch.progress.total_files - self._current_batch.progress.processed_files
                self._current_batch.progress.estimated_remaining_seconds = rate * remaining

        # Notify callbacks
        self._notify_progress(self._current_batch.progress)
        self._notify_file_complete(result)

    def _discover_files(
        self,
        directory: str,
        config: BatchConfig,
        already_processed: set[str],
    ) -> list[str]:
        """Discover files to process."""
        files = []
        dir_path = Path(directory)

        for pattern in config.include_patterns:
            for file_path in dir_path.rglob(pattern):
                str_path = str(file_path)

                # Skip already processed
                if str_path in already_processed:
                    continue

                # Check exclusions
                excluded = any(file_path.match(excl) for excl in config.exclude_patterns)
                if excluded:
                    continue

                if file_path.is_file():
                    files.append(str_path)

        return files

    def _save_checkpoint(self) -> None:
        """Save processing checkpoint."""
        if not self._current_batch:
            return

        checkpoint = Checkpoint(
            batch_id=self._current_batch.batch_id,
            processed_files=[r.file_path for r in self._current_batch.file_results],
            last_file=self._current_batch.progress.current_file,
            progress=self._current_batch.progress,
            timestamp=datetime.now(UTC),
        )

        # Ensure checkpoint directory exists
        os.makedirs(self._checkpoint_dir, exist_ok=True)

        checkpoint_path = os.path.join(
            self._checkpoint_dir,
            f"{self._current_batch.batch_id}.json",
        )

        with open(checkpoint_path, "w") as f:
            json.dump(
                {
                    "batch_id": checkpoint.batch_id,
                    "processed_files": checkpoint.processed_files,
                    "last_file": checkpoint.last_file,
                    "progress": {
                        "total_files": checkpoint.progress.total_files,
                        "processed_files": checkpoint.progress.processed_files,
                        "successful_files": checkpoint.progress.successful_files,
                        "failed_files": checkpoint.progress.failed_files,
                        "skipped_files": checkpoint.progress.skipped_files,
                        "total_diagnostics": checkpoint.progress.total_diagnostics,
                        "total_fixes": checkpoint.progress.total_fixes,
                    },
                    "timestamp": checkpoint.timestamp.isoformat(),
                },
                f,
                indent=2,
            )

        logger.debug("checkpoint_saved", batch_id=checkpoint.batch_id)

    def _load_checkpoint(self, batch_id: str) -> Checkpoint | None:
        """Load processing checkpoint."""
        checkpoint_path = os.path.join(self._checkpoint_dir, f"{batch_id}.json")

        if not os.path.exists(checkpoint_path):
            return None

        try:
            with open(checkpoint_path) as f:
                data = json.load(f)

            progress = BatchProgress(
                total_files=data["progress"]["total_files"],
                processed_files=data["progress"]["processed_files"],
                successful_files=data["progress"]["successful_files"],
                failed_files=data["progress"]["failed_files"],
                skipped_files=data["progress"]["skipped_files"],
                total_diagnostics=data["progress"]["total_diagnostics"],
                total_fixes=data["progress"]["total_fixes"],
            )

            return Checkpoint(
                batch_id=data["batch_id"],
                processed_files=data["processed_files"],
                last_file=data.get("last_file"),
                progress=progress,
                timestamp=datetime.fromisoformat(data["timestamp"]),
            )

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("Failed to load checkpoint", error=str(e))
            return None

    def cancel(self) -> None:
        """Request cancellation of batch processing."""
        self._cancel_requested = True
        logger.info("batch_cancellation_requested")

    def pause(self) -> None:
        """Pause batch processing (saves checkpoint)."""
        if self._current_batch:
            self._save_checkpoint()
            self._current_batch.status = BatchStatus.PAUSED
        self._cancel_requested = True

    def get_result(self) -> BatchResult | None:
        """Get current batch result."""
        return self._current_batch

    def get_progress(self) -> BatchProgress | None:
        """Get current progress."""
        return self._current_batch.progress if self._current_batch else None

    def list_checkpoints(self) -> list[str]:
        """List available checkpoints."""
        if not os.path.exists(self._checkpoint_dir):
            return []

        return [f.replace(".json", "") for f in os.listdir(self._checkpoint_dir) if f.endswith(".json")]

    def delete_checkpoint(self, batch_id: str) -> bool:
        """Delete a checkpoint."""
        checkpoint_path = os.path.join(self._checkpoint_dir, f"{batch_id}.json")
        if os.path.exists(checkpoint_path):
            os.remove(checkpoint_path)
            return True
        return False

    def export_report(
        self,
        output_path: str,
        format: str = "json",
    ) -> None:
        """
        Export batch result to file.
        تصدير نتيجة الدُفعة إلى ملف

        Args:
            output_path: Path to output file
            format: Output format (json, markdown, sarif)
        """
        if not self._current_batch:
            raise ValueError("No batch result available")

        if format == "json":
            self._export_json(output_path)
        elif format == "markdown":
            self._export_markdown(output_path)
        elif format == "sarif":
            self._export_sarif(output_path)
        else:
            raise ValueError(f"Unknown format: {format}")

    def _export_json(self, output_path: str) -> None:
        """Export as JSON."""
        with open(output_path, "w") as f:
            json.dump(self._current_batch.to_dict(), f, indent=2)

    def _export_markdown(self, output_path: str) -> None:
        """Export as Markdown report."""
        batch = self._current_batch
        lines = [
            "# Batch Processing Report | تقرير معالجة الدُفعات",
            "",
            f"**Batch ID**: `{batch.batch_id}`",
            f"**Status**: {batch.status.value}",
            f"**Duration**: {batch.duration_seconds:.1f} seconds",
            "",
            "## Summary | ملخص",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total Files | {batch.progress.total_files} |",
            f"| Processed | {batch.progress.processed_files} |",
            f"| Successful | {batch.progress.successful_files} |",
            f"| Failed | {batch.progress.failed_files} |",
            f"| Skipped | {batch.progress.skipped_files} |",
            f"| Success Rate | {batch.success_rate:.1f}% |",
            f"| Diagnostics Found | {batch.progress.total_diagnostics} |",
            f"| Fixes Applied | {batch.progress.total_fixes} |",
            "",
        ]

        if batch.errors:
            lines.append("## Errors | الأخطاء")
            lines.append("")
            for error in batch.errors[:10]:
                lines.append(f"- {error}")
            lines.append("")

        with open(output_path, "w") as f:
            f.write("\n".join(lines))

    def _export_sarif(self, output_path: str) -> None:
        """Export as SARIF format (for CI/CD integration)."""
        # SARIF 2.1.0 format
        sarif = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "SAHOOL AutoFix Batch Processor",
                            "version": "16.0.0",
                            "informationUri": "https://sahool.app/docs/auto-fix",
                        }
                    },
                    "results": [],
                    "invocations": [
                        {
                            "executionSuccessful": self._current_batch.status == BatchStatus.COMPLETED,
                            "startTimeUtc": self._current_batch.started_at.isoformat()
                            if self._current_batch.started_at
                            else None,
                            "endTimeUtc": self._current_batch.completed_at.isoformat()
                            if self._current_batch.completed_at
                            else None,
                        }
                    ],
                }
            ],
        }

        with open(output_path, "w") as f:
            json.dump(sarif, f, indent=2)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def create_batch_processor(
    checkpoint_dir: str | None = None,
) -> BatchProcessor:
    """
    Factory function to create a batch processor.
    دالة لإنشاء معالج الدُفعات
    """
    return BatchProcessor(checkpoint_dir=checkpoint_dir)


async def process_repository(
    repo_path: str,
    config: BatchConfig | None = None,
    progress_callback: Callable[[BatchProgress], None] | None = None,
) -> BatchResult:
    """
    Convenience function to process an entire repository.
    دالة مساعدة لمعالجة مستودع كامل

    Args:
        repo_path: Path to repository
        config: Batch configuration
        progress_callback: Optional progress callback

    Returns:
        BatchResult with processing summary
    """
    processor = BatchProcessor()

    if progress_callback:
        processor.on_progress(progress_callback)

    return await processor.process_directory(repo_path, config)
