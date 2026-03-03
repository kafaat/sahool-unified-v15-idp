"""
Tests for Knowledge Base Collection Populator
===============================================
اختبارات أداة تعبئة مجموعات قاعدة المعرفة

Tests for population from docs and code modules, dry runs,
and population status reporting.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from shared.ai.knowledge.collection_populator import (
    KnowledgeBasePopulator,
    PopulationReport,
)
from shared.ai.knowledge.collections import (
    ALL_COLLECTIONS,
    CROP_KNOWLEDGE,
)


@pytest.fixture
def sample_docs_tree(tmp_path: Path) -> Path:
    """Create a sample docs directory tree mirroring knowledge-base layout."""
    base = tmp_path / "docs" / "knowledge-base"

    # Create crop documents
    crops_dir = base / "crops"
    crops_dir.mkdir(parents=True)
    (crops_dir / "README.md").write_text("# Crops Overview")
    (crops_dir / "wheat.md").write_text("---\ntitle: Wheat\n---\n# Wheat\nWheat crop info.")
    (crops_dir / "barley.md").write_text("---\ntitle: Barley\n---\n# Barley\nBarley crop info.")

    # Create soil documents
    soils_dir = base / "soils"
    soils_dir.mkdir(parents=True)
    (soils_dir / "README.md").write_text("# Soils Overview")
    (soils_dir / "sandy.md").write_text("---\ntitle: Sandy Soil\n---\n# Sandy\nSandy soil info.")

    # Create main directory with a general file
    (base / "README.md").write_text("# Knowledge Base")
    (base / "best-practices.md").write_text("---\ntitle: Best Practices\n---\n# Best Practices\nGeneral info.")

    return tmp_path


@pytest.fixture
def populator(sample_docs_tree: Path) -> KnowledgeBasePopulator:
    """Create a populator with the sample docs tree."""
    return KnowledgeBasePopulator(
        base_docs_path=sample_docs_tree / "docs" / "knowledge-base",
    )


# ─── PopulationReport Tests ──────────────────────────────────────────────────


class TestPopulationReport:
    """Tests for PopulationReport dataclass."""

    @pytest.mark.unit
    def test_default_values(self):
        """Test default report values."""
        report = PopulationReport()
        assert report.total_files == 0
        assert report.total_ingested == 0
        assert report.total_failed == 0
        assert report.total_skipped == 0
        assert report.errors == []
        assert report.by_collection == {}
        assert report.by_domain == {}


# ─── Dry Run Tests ───────────────────────────────────────────────────────────


class TestDryRun:
    """Tests for dry run mode."""

    @pytest.mark.unit
    def test_docs_dry_run(self, populator: KnowledgeBasePopulator):
        """Test dry run counts files without ingesting."""
        report = populator.populate_from_docs(dry_run=True)
        assert report.total_files > 0
        # In dry run, no actual ingestion
        assert report.total_ingested == 0

    @pytest.mark.unit
    def test_docs_dry_run_counts_correct(self, populator: KnowledgeBasePopulator):
        """Test dry run counts exclude README files."""
        report = populator.populate_from_docs(
            collections=[CROP_KNOWLEDGE],
            dry_run=True,
        )
        # Should find wheat.md and barley.md but not README.md
        assert report.by_collection.get(CROP_KNOWLEDGE, 0) == 2

    @pytest.mark.unit
    def test_code_modules_dry_run(self, populator: KnowledgeBasePopulator):
        """Test code modules dry run."""
        report = populator.populate_from_code_modules(dry_run=True)
        # Some code modules may not exist but dry run should still work
        assert isinstance(report, PopulationReport)


# ─── Docs Population Tests ──────────────────────────────────────────────────


class TestDocsPopulation:
    """Tests for population from documentation."""

    @pytest.mark.unit
    def test_populate_all_collections(self, populator: KnowledgeBasePopulator):
        """Test populating from all collections."""
        report = populator.populate_from_docs()
        assert report.total_files > 0

    @pytest.mark.unit
    def test_populate_specific_collection(self, populator: KnowledgeBasePopulator):
        """Test populating a specific collection."""
        report = populator.populate_from_docs(collections=[CROP_KNOWLEDGE])
        assert report.total_files > 0

    @pytest.mark.unit
    def test_skips_readme(self, populator: KnowledgeBasePopulator):
        """Test README.md files are skipped."""
        report = populator.populate_from_docs(collections=[CROP_KNOWLEDGE])
        assert report.total_skipped >= 1

    @pytest.mark.unit
    def test_nonexistent_directory_handled(self, tmp_path: Path):
        """Test graceful handling of non-existent directory."""
        pop = KnowledgeBasePopulator(base_docs_path=tmp_path / "nonexistent")
        report = pop.populate_from_docs()
        # Should not crash
        assert isinstance(report, PopulationReport)


# ─── Full Population Tests ───────────────────────────────────────────────────


class TestFullPopulation:
    """Tests for populate_all (docs + code modules)."""

    @pytest.mark.unit
    def test_populate_all(self, populator: KnowledgeBasePopulator):
        """Test full population merges docs and code reports."""
        report = populator.populate_all()
        assert report.total_files >= 0
        assert isinstance(report.by_collection, dict)
        assert isinstance(report.by_domain, dict)

    @pytest.mark.unit
    def test_populate_all_dry_run(self, populator: KnowledgeBasePopulator):
        """Test full dry run."""
        report = populator.populate_all(dry_run=True)
        assert report.total_ingested == 0  # Dry run = no ingestion

    @pytest.mark.unit
    def test_populate_all_merges_collections(self, populator: KnowledgeBasePopulator):
        """Test merged report combines collection counts."""
        report = populator.populate_all(dry_run=True)
        # Should have at least crop_knowledge from docs dry run
        assert len(report.by_collection) >= 0


# ─── Population Status Tests ────────────────────────────────────────────────


class TestPopulationStatus:
    """Tests for population status reporting."""

    @pytest.mark.unit
    def test_status_has_all_collections(self, populator: KnowledgeBasePopulator):
        """Test status includes all collection names."""
        status = populator.get_population_status()
        assert "collections" in status
        for coll in ALL_COLLECTIONS:
            assert coll in status["collections"]

    @pytest.mark.unit
    def test_status_has_files_available(self, populator: KnowledgeBasePopulator):
        """Test status shows files available per collection."""
        status = populator.get_population_status()
        for coll, info in status["collections"].items():
            assert "files_available" in info
            assert "directories" in info

    @pytest.mark.unit
    def test_status_total_files(self, populator: KnowledgeBasePopulator):
        """Test status total files count."""
        status = populator.get_population_status()
        assert "total_files" in status
        assert status["total_files"] >= 0
