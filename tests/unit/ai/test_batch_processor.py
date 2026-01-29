"""
Tests for BatchProcessor - Auto-fix batch processing module.

Tests the batch processing functionality for large-scale code analysis.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

# Import the modules to test
from shared.ai.auto_fix.batch_processor import (
    BatchConfig,
    BatchProgress,
    BatchResult,
    FileResult,
    Checkpoint,
    BatchProcessor,
    SARIFExporter,
)
from shared.ai.auto_fix.models import (
    Diagnostic,
    DiagnosticSeverity,
    DiagnosticCategory,
    ToolType,
)


class TestBatchConfig:
    """Tests for BatchConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = BatchConfig()
        assert config.max_workers == 4
        assert config.batch_size == 50
        assert config.timeout_per_file == 30.0
        assert config.checkpoint_interval == 100
        assert config.enable_checkpoints is True

    def test_custom_config(self):
        """Test custom configuration values."""
        config = BatchConfig(
            max_workers=8,
            batch_size=100,
            timeout_per_file=60.0,
            checkpoint_interval=50,
            enable_checkpoints=False,
        )
        assert config.max_workers == 8
        assert config.batch_size == 100
        assert config.timeout_per_file == 60.0
        assert config.checkpoint_interval == 50
        assert config.enable_checkpoints is False


class TestBatchProgress:
    """Tests for BatchProgress dataclass."""

    def test_progress_percentage(self):
        """Test progress percentage calculation."""
        progress = BatchProgress(
            total_files=100,
            processed_files=50,
            failed_files=5,
            total_diagnostics=200,
            fixable_diagnostics=150,
        )
        assert progress.processed_files == 50
        assert progress.failed_files == 5
        assert progress.total_diagnostics == 200


class TestFileResult:
    """Tests for FileResult dataclass."""

    def test_file_result_creation(self):
        """Test FileResult creation."""
        result = FileResult(
            file_path="/path/to/file.py",
            diagnostics=[],
            processing_time=1.5,
            success=True,
        )
        assert result.file_path == "/path/to/file.py"
        assert result.diagnostics == []
        assert result.processing_time == 1.5
        assert result.success is True


class TestDiagnosticModel:
    """Tests for Diagnostic model used in batch processing."""

    def test_diagnostic_creation(self):
        """Test Diagnostic model creation."""
        diagnostic = Diagnostic(
            id=str(uuid4()),
            file_path="/path/to/file.py",
            line=10,
            column=5,
            message="Test error",
            severity=DiagnosticSeverity.ERROR,
            category=DiagnosticCategory.STYLE,
            tool=ToolType.RUFF,
            rule_id="E501",
        )
        assert diagnostic.line == 10
        assert diagnostic.severity == DiagnosticSeverity.ERROR
        assert diagnostic.tool == ToolType.RUFF


class TestBatchResult:
    """Tests for BatchResult dataclass."""

    def test_batch_result_creation(self):
        """Test BatchResult creation."""
        result = BatchResult(
            batch_id="test-batch-123",
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            total_files=10,
            processed_files=10,
            failed_files=1,
            total_diagnostics=50,
            fixable_diagnostics=30,
            file_results=[],
        )
        assert result.batch_id == "test-batch-123"
        assert result.total_files == 10
        assert result.failed_files == 1


class TestCheckpoint:
    """Tests for Checkpoint dataclass."""

    def test_checkpoint_creation(self):
        """Test Checkpoint creation."""
        checkpoint = Checkpoint(
            batch_id="test-batch-123",
            created_at=datetime.now(timezone.utc),
            processed_files=["file1.py", "file2.py"],
            pending_files=["file3.py"],
            file_results=[],
        )
        assert checkpoint.batch_id == "test-batch-123"
        assert len(checkpoint.processed_files) == 2
        assert len(checkpoint.pending_files) == 1


class TestSARIFExporter:
    """Tests for SARIF export functionality."""

    def test_sarif_structure(self):
        """Test SARIF export creates valid structure."""
        exporter = SARIFExporter()

        # Create test diagnostics
        diagnostics = [
            Diagnostic(
                id=str(uuid4()),
                file_path="/path/to/file.py",
                line=10,
                column=5,
                message="Test error",
                severity=DiagnosticSeverity.ERROR,
                category=DiagnosticCategory.STYLE,
                tool=ToolType.RUFF,
                rule_id="E501",
            )
        ]

        sarif = exporter.export(diagnostics, tool_name="ruff")

        assert sarif["version"] == "2.1.0"
        assert "$schema" in sarif
        assert "runs" in sarif
        assert len(sarif["runs"]) == 1


class TestBatchProcessor:
    """Tests for BatchProcessor class."""

    def test_processor_initialization(self):
        """Test BatchProcessor initialization."""
        config = BatchConfig(max_workers=2)
        processor = BatchProcessor(config=config)

        assert processor.config.max_workers == 2

    @pytest.mark.asyncio
    async def test_process_empty_files(self):
        """Test processing with empty file list."""
        processor = BatchProcessor()

        result = await processor.process_files(
            files=[],
            tools=["ruff"],
        )

        assert result.total_files == 0
        assert result.processed_files == 0

    def test_config_validation(self):
        """Test configuration validation."""
        # Should not raise with valid config
        config = BatchConfig(
            max_workers=1,
            batch_size=10,
        )
        processor = BatchProcessor(config=config)
        assert processor.config.max_workers == 1
