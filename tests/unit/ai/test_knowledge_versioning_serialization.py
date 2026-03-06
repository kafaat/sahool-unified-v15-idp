"""
Tests for Knowledge Versioning and Serialization
==================================================
اختبارات الإصدارات والتسلسل
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from shared.ai.knowledge.models import BaseKnowledgeDocument, KnowledgeDomain
from shared.ai.knowledge.serialization import (
    ExportManifest,
    ImportResult,
    KnowledgeSerializer,
)
from shared.ai.knowledge.versioning import (
    DocumentVersion,
    DocumentVersionManager,
    VersionDiff,
)


def _make_doc(title: str = "Test", content: str = "Content") -> BaseKnowledgeDocument:
    return BaseKnowledgeDocument(
        title=title,
        domain=KnowledgeDomain.CROPS,
        content=content,
    )


# ─── Versioning Tests ────────────────────────────────────────────────────────


class TestDocumentVersionManager:
    """Tests for document version tracking."""

    @pytest.fixture
    def manager(self) -> DocumentVersionManager:
        return DocumentVersionManager()

    @pytest.mark.unit
    def test_track_first_version(self, manager: DocumentVersionManager):
        doc = _make_doc("Wheat Guide")
        version = manager.track(doc, author="admin", change_summary="Initial version")
        assert version is not None

    @pytest.mark.unit
    def test_track_increments_version(self, manager: DocumentVersionManager):
        doc = _make_doc("Wheat Guide")
        v1 = manager.track(doc)
        doc.content = "Updated content"
        v2 = manager.track(doc)
        assert v1 != v2

    @pytest.mark.unit
    def test_get_history(self, manager: DocumentVersionManager):
        doc = _make_doc("Guide")
        manager.track(doc)
        doc.content = "V2"
        manager.track(doc)

        history = manager.get_history(doc.id)
        assert len(history) == 2

    @pytest.mark.unit
    def test_get_history_empty(self, manager: DocumentVersionManager):
        assert manager.get_history("nonexistent") == []

    @pytest.mark.unit
    def test_get_latest(self, manager: DocumentVersionManager):
        doc = _make_doc("Guide")
        manager.track(doc, change_summary="v1")
        doc.content = "Updated"
        manager.track(doc, change_summary="v2")

        latest = manager.get_latest(doc.id)
        assert latest is not None
        assert latest.change_summary == "v2"

    @pytest.mark.unit
    def test_get_latest_empty(self, manager: DocumentVersionManager):
        assert manager.get_latest("nonexistent") is None

    @pytest.mark.unit
    def test_get_specific_version(self, manager: DocumentVersionManager):
        doc = _make_doc("Guide")
        v1 = manager.track(doc)
        retrieved = manager.get_version(doc.id, v1)
        assert retrieved is not None

    @pytest.mark.unit
    def test_diff_between_versions(self, manager: DocumentVersionManager):
        doc = _make_doc("Guide", content="Original")
        v1 = manager.track(doc)
        doc.content = "Modified"
        doc.tags = ["new_tag"]
        v2 = manager.track(doc)

        diff = manager.diff(doc.id, v1, v2)
        assert diff is not None
        assert isinstance(diff, VersionDiff)
        assert diff.content_changed is True

    @pytest.mark.unit
    def test_rollback(self, manager: DocumentVersionManager):
        doc = _make_doc("Guide", content="Original")
        v1 = manager.track(doc)
        doc.content = "Changed"
        manager.track(doc)

        data = manager.rollback(doc.id, v1)
        assert data is not None
        assert data.get("content") == "Original"

    @pytest.mark.unit
    def test_increment_version(self, manager: DocumentVersionManager):
        assert manager._increment_version("1.0.0") == "1.0.1"
        assert manager._increment_version("1.0.9") == "1.0.10"
        assert manager._increment_version("2.3.4") == "2.3.5"


# ─── Serialization Tests ─────────────────────────────────────────────────────


class TestKnowledgeSerializer:
    """Tests for knowledge export/import."""

    @pytest.fixture
    def serializer(self) -> KnowledgeSerializer:
        return KnowledgeSerializer()

    @pytest.mark.unit
    def test_export_to_dict(self, serializer: KnowledgeSerializer):
        docs = [_make_doc(f"Doc {i}") for i in range(3)]
        result = serializer.export_to_dict(docs)
        assert "manifest" in result
        assert "documents" in result
        assert result["manifest"]["total_documents"] == 3

    @pytest.mark.unit
    def test_export_and_import_roundtrip(self, serializer: KnowledgeSerializer):
        docs = [
            _make_doc("Wheat", content="Wheat cultivation guide"),
            _make_doc("Barley", content="Barley growing guide"),
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            manifest = serializer.export_documents(docs, f.name)
            assert manifest.total_documents == 2

            imported_docs, result = serializer.import_documents(f.name)
            assert result.imported >= 1
            assert len(imported_docs) >= 1

            Path(f.name).unlink()

    @pytest.mark.unit
    def test_import_from_dict(self, serializer: KnowledgeSerializer):
        docs = [_make_doc("Test")]
        exported = serializer.export_to_dict(docs)
        imported_docs, result = serializer.import_from_dict(exported)
        assert result.imported >= 1

    @pytest.mark.unit
    def test_export_manifest(self, serializer: KnowledgeSerializer):
        docs = [
            BaseKnowledgeDocument(title="A", domain=KnowledgeDomain.CROPS, content="a"),
            BaseKnowledgeDocument(title="B", domain=KnowledgeDomain.SOIL, content="b"),
        ]
        result = serializer.export_to_dict(docs)
        manifest = result["manifest"]
        assert manifest["total_documents"] == 2
        assert len(manifest["domains"]) >= 2

    @pytest.mark.unit
    def test_import_invalid_data(self, serializer: KnowledgeSerializer):
        data = {"manifest": {}, "documents": [{"invalid": "data"}]}
        docs, result = serializer.import_from_dict(data)
        assert result.errors or result.skipped > 0 or result.imported == 0
