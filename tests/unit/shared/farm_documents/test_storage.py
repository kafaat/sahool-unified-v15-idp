"""
Tests for farm_documents storage module
اختبارات وحدة تخزين وثائق المزرعة
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from shared.farm_documents.models import DocumentStatus, DocumentType, FileFormat
from shared.farm_documents.storage import (
    DocumentStorageService,
    LocalStorageProvider,
    StorageConfig,
    StorageError,
    get_mime_type_for_format,
    is_document_format,
    is_image_format,
)


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def storage_config(tmp_dir):
    return StorageConfig(base_path=tmp_dir)


@pytest.fixture
def local_provider(tmp_dir):
    return LocalStorageProvider(tmp_dir)


@pytest.fixture
def storage_service(storage_config):
    return DocumentStorageService(config=storage_config)


# ─────────────────────────────────────────────────────────────────────────────
# LocalStorageProvider Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestLocalStorageProvider:
    @pytest.mark.asyncio
    async def test_store_and_retrieve(self, local_provider):
        content = b"Hello, World!"
        await local_provider.store(content, "test/file.txt")
        retrieved = await local_provider.retrieve("test/file.txt")
        assert retrieved == content

    @pytest.mark.asyncio
    async def test_exists(self, local_provider):
        await local_provider.store(b"data", "test/exists.txt")
        assert await local_provider.exists("test/exists.txt") is True
        assert await local_provider.exists("test/nope.txt") is False

    @pytest.mark.asyncio
    async def test_delete(self, local_provider):
        await local_provider.store(b"data", "test/delete.txt")
        result = await local_provider.delete("test/delete.txt")
        assert result is True
        assert await local_provider.exists("test/delete.txt") is False

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, local_provider):
        result = await local_provider.delete("nonexistent.txt")
        assert result is False

    @pytest.mark.asyncio
    async def test_retrieve_nonexistent(self, local_provider):
        with pytest.raises(FileNotFoundError):
            await local_provider.retrieve("nonexistent.txt")

    @pytest.mark.asyncio
    async def test_get_url(self, local_provider):
        await local_provider.store(b"data", "test/url.txt")
        url = await local_provider.get_url("test/url.txt")
        assert url.startswith("file://")

    def test_path_traversal_prevention(self, local_provider):
        with pytest.raises(ValueError, match="Path traversal"):
            local_provider._safe_path("../../etc/passwd")

    def test_safe_path_normal(self, local_provider):
        path = local_provider._safe_path("tenant/farm/doc.pdf")
        assert path.is_relative_to(local_provider.base_path)


# ─────────────────────────────────────────────────────────────────────────────
# StorageConfig Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestStorageConfig:
    def test_default_config(self):
        config = StorageConfig()
        assert config.max_file_size == 50 * 1024 * 1024
        assert len(config.allowed_formats) == 10
        assert config.compute_checksums is True

    def test_custom_config(self):
        config = StorageConfig(max_file_size=10 * 1024 * 1024, allowed_formats=[FileFormat.PDF])
        assert config.max_file_size == 10 * 1024 * 1024
        assert config.allowed_formats == [FileFormat.PDF]


# ─────────────────────────────────────────────────────────────────────────────
# DocumentStorageService Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestDocumentStorageService:
    @pytest.mark.asyncio
    async def test_upload_document(self, storage_service):
        doc = await storage_service.upload_document(
            file_content=b"PDF content here",
            filename="report.pdf",
            tenant_id="t1",
            farm_id="f1",
            document_type=DocumentType.SOIL_TEST,
            title_en="Soil Test Report",
            title_ar="تقرير اختبار التربة",
            uploaded_by="user1",
        )
        assert doc.id is not None
        assert doc.document_type == DocumentType.SOIL_TEST
        assert doc.metadata.file_size == len(b"PDF content here")
        assert doc.metadata.file_format == FileFormat.PDF
        assert doc.metadata.sha256_hash is not None

    @pytest.mark.asyncio
    async def test_upload_too_large(self, tmp_dir):
        config = StorageConfig(base_path=tmp_dir, max_file_size=10)
        service = DocumentStorageService(config=config)
        with pytest.raises(StorageError, match="File too large"):
            await service.upload_document(
                file_content=b"x" * 20,
                filename="big.pdf",
                tenant_id="t1",
                farm_id="f1",
                document_type=DocumentType.REPORT,
                title_en="Big",
                title_ar="كبير",
                uploaded_by="u1",
            )

    @pytest.mark.asyncio
    async def test_upload_unsupported_format(self, storage_service):
        with pytest.raises(StorageError, match="Unsupported file format"):
            await storage_service.upload_document(
                file_content=b"data",
                filename="file.exe",
                tenant_id="t1",
                farm_id="f1",
                document_type=DocumentType.OTHER,
                title_en="T",
                title_ar="ت",
                uploaded_by="u1",
            )

    @pytest.mark.asyncio
    async def test_get_document(self, storage_service):
        doc = await storage_service.upload_document(
            file_content=b"data",
            filename="test.pdf",
            tenant_id="t1",
            farm_id="f1",
            document_type=DocumentType.REPORT,
            title_en="T",
            title_ar="ت",
            uploaded_by="u1",
        )
        retrieved = await storage_service.get_document(doc.id)
        assert retrieved is not None
        assert retrieved.id == doc.id

    @pytest.mark.asyncio
    async def test_get_document_not_found(self, storage_service):
        result = await storage_service.get_document("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_document_soft(self, storage_service):
        doc = await storage_service.upload_document(
            file_content=b"data",
            filename="test.pdf",
            tenant_id="t1",
            farm_id="f1",
            document_type=DocumentType.REPORT,
            title_en="T",
            title_ar="ت",
            uploaded_by="u1",
        )
        result = await storage_service.delete_document(doc.id, "admin")
        assert result is True
        # Document still exists but archived
        retrieved = await storage_service.get_document(doc.id)
        assert retrieved.status == DocumentStatus.ARCHIVED

    @pytest.mark.asyncio
    async def test_delete_document_hard(self, storage_service):
        doc = await storage_service.upload_document(
            file_content=b"data",
            filename="test.pdf",
            tenant_id="t1",
            farm_id="f1",
            document_type=DocumentType.REPORT,
            title_en="T",
            title_ar="ت",
            uploaded_by="u1",
        )
        result = await storage_service.delete_document(doc.id, "admin", hard_delete=True)
        assert result is True
        assert await storage_service.get_document(doc.id) is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, storage_service):
        assert await storage_service.delete_document("fake", "admin") is False

    @pytest.mark.asyncio
    async def test_list_documents(self, storage_service):
        for i in range(3):
            await storage_service.upload_document(
                file_content=b"data",
                filename=f"test{i}.pdf",
                tenant_id="t1",
                farm_id="f1",
                document_type=DocumentType.REPORT,
                title_en=f"T{i}",
                title_ar=f"ت{i}",
                uploaded_by="u1",
            )
        docs = await storage_service.list_documents("t1", farm_id="f1")
        assert len(docs) == 3

    @pytest.mark.asyncio
    async def test_list_documents_pagination(self, storage_service):
        for i in range(5):
            await storage_service.upload_document(
                file_content=b"data",
                filename=f"test{i}.pdf",
                tenant_id="t1",
                farm_id="f1",
                document_type=DocumentType.REPORT,
                title_en=f"T{i}",
                title_ar=f"ت{i}",
                uploaded_by="u1",
            )
        docs = await storage_service.list_documents("t1", limit=2, offset=0)
        assert len(docs) == 2

    @pytest.mark.asyncio
    async def test_search_documents(self, storage_service):
        await storage_service.upload_document(
            file_content=b"data",
            filename="soil.pdf",
            tenant_id="t1",
            farm_id="f1",
            document_type=DocumentType.SOIL_TEST,
            title_en="Soil Analysis Report",
            title_ar="تقرير تحليل التربة",
            uploaded_by="u1",
        )
        await storage_service.upload_document(
            file_content=b"data",
            filename="water.pdf",
            tenant_id="t1",
            farm_id="f1",
            document_type=DocumentType.WATER_TEST,
            title_en="Water Quality",
            title_ar="جودة المياه",
            uploaded_by="u1",
        )
        results = await storage_service.search_documents("t1", "soil")
        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_update_document(self, storage_service):
        doc = await storage_service.upload_document(
            file_content=b"data",
            filename="test.pdf",
            tenant_id="t1",
            farm_id="f1",
            document_type=DocumentType.REPORT,
            title_en="Old Title",
            title_ar="ت",
            uploaded_by="u1",
        )
        updated = await storage_service.update_document(
            doc.id,
            "admin",
            title_en="New Title",
        )
        assert updated.title_en == "New Title"

    @pytest.mark.asyncio
    async def test_update_document_not_found(self, storage_service):
        result = await storage_service.update_document("fake", "admin", title_en="X")
        assert result is None

    @pytest.mark.asyncio
    async def test_create_new_version(self, storage_service):
        doc = await storage_service.upload_document(
            file_content=b"v1",
            filename="test.pdf",
            tenant_id="t1",
            farm_id="f1",
            document_type=DocumentType.REPORT,
            title_en="T",
            title_ar="ت",
            uploaded_by="u1",
        )
        new_doc = await storage_service.create_new_version(
            doc.id,
            b"v2",
            "test_v2.pdf",
            "u1",
        )
        assert new_doc.version == 2
        assert new_doc.previous_version_id == doc.id
        # Old doc should be archived
        old = await storage_service.get_document(doc.id)
        assert old.status == DocumentStatus.ARCHIVED

    @pytest.mark.asyncio
    async def test_create_new_version_not_found(self, storage_service):
        with pytest.raises(StorageError, match="not found"):
            await storage_service.create_new_version("fake", b"data", "f.pdf", "u1")

    @pytest.mark.asyncio
    async def test_get_categories(self, storage_service):
        cats = await storage_service.get_categories()
        assert len(cats) >= 7
        # Should be sorted by order
        assert cats[0].order <= cats[1].order

    @pytest.mark.asyncio
    async def test_get_storage_stats(self, storage_service):
        await storage_service.upload_document(
            file_content=b"x" * 100,
            filename="test.pdf",
            tenant_id="t1",
            farm_id="f1",
            document_type=DocumentType.REPORT,
            title_en="T",
            title_ar="ت",
            uploaded_by="u1",
        )
        stats = await storage_service.get_storage_stats("t1")
        assert stats["total_documents"] == 1
        assert stats["total_size_bytes"] == 100


# ─────────────────────────────────────────────────────────────────────────────
# Helper Function Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestHelperFunctions:
    def test_get_mime_type_for_format(self):
        assert get_mime_type_for_format(FileFormat.PDF) == "application/pdf"
        assert get_mime_type_for_format(FileFormat.PNG) == "image/png"
        assert (
            get_mime_type_for_format(FileFormat.XLSX)
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    def test_is_image_format(self):
        assert is_image_format(FileFormat.PNG) is True
        assert is_image_format(FileFormat.JPG) is True
        assert is_image_format(FileFormat.PDF) is False
        assert is_image_format(FileFormat.DOCX) is False

    def test_is_document_format(self):
        assert is_document_format(FileFormat.PDF) is True
        assert is_document_format(FileFormat.DOCX) is True
        assert is_document_format(FileFormat.PNG) is False


class TestSanitizeFilename:
    def test_normal_filename(self):
        service = DocumentStorageService()
        assert service._sanitize_filename("report.pdf") == "report.pdf"

    def test_dangerous_characters(self):
        service = DocumentStorageService()
        result = service._sanitize_filename("file name (1).pdf")
        assert " " not in result
        assert "(" not in result

    def test_path_traversal(self):
        service = DocumentStorageService()
        result = service._sanitize_filename("../../etc/passwd")
        assert "/" not in result
        assert ".." not in result

    def test_leading_dots(self):
        service = DocumentStorageService()
        result = service._sanitize_filename(".hidden")
        assert not result.startswith(".")

    def test_long_filename(self):
        service = DocumentStorageService()
        long_name = "a" * 250 + ".pdf"
        result = service._sanitize_filename(long_name)
        assert len(result) <= 200
