"""
Tests for Knowledge Base CLI
==============================
اختبارات واجهة سطر الأوامر
"""

from __future__ import annotations

import pytest

from shared.ai.knowledge.cli import KnowledgeCLI


@pytest.fixture
def cli() -> KnowledgeCLI:
    return KnowledgeCLI()


class TestKnowledgeCLI:
    """Tests for CLI commands."""

    @pytest.mark.unit
    def test_no_command_shows_help(self, cli: KnowledgeCLI):
        """No command returns exit code 1."""
        assert cli.run([]) == 1

    @pytest.mark.unit
    def test_collections_command(self, cli: KnowledgeCLI):
        """Collections command succeeds."""
        assert cli.run(["collections"]) == 0

    @pytest.mark.unit
    def test_stats_command(self, cli: KnowledgeCLI):
        """Stats command succeeds."""
        assert cli.run(["stats"]) == 0

    @pytest.mark.unit
    def test_status_command(self, cli: KnowledgeCLI):
        """Status command succeeds."""
        assert cli.run(["status"]) == 0

    @pytest.mark.unit
    def test_freshness_command(self, cli: KnowledgeCLI):
        """Freshness command succeeds."""
        assert cli.run(["freshness"]) == 0

    @pytest.mark.unit
    def test_freshness_custom_days(self, cli: KnowledgeCLI):
        """Freshness command with custom warning days."""
        assert cli.run(["freshness", "--warning-days", "60"]) == 0

    @pytest.mark.unit
    def test_ingest_nonexistent_path(self, cli: KnowledgeCLI):
        """Ingest with nonexistent path returns error."""
        assert cli.run(["ingest", "/nonexistent/path"]) == 1

    @pytest.mark.unit
    def test_validate_nonexistent_path(self, cli: KnowledgeCLI):
        """Validate with nonexistent path returns error."""
        assert cli.run(["validate", "/nonexistent/path"]) == 1

    @pytest.mark.unit
    def test_ingest_real_directory(self, cli: KnowledgeCLI):
        """Ingest from real knowledge base directory."""
        from pathlib import Path
        crops_dir = Path("docs/knowledge-base/crops")
        if not crops_dir.exists():
            pytest.skip("Knowledge base docs not available")
        result = cli.run(["ingest", str(crops_dir)])
        assert result == 0
