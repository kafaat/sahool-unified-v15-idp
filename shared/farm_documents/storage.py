"""
Farm Document Storage Module
وحدة تخزين وثائق المزرعة

Provides document storage, retrieval, and management functionality.
توفر وظائف تخزين واسترجاع وإدارة الوثائق.
"""

from __future__ import annotations

import hashlib
import mimetypes
import os
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import structlog

from .models import (
    DocumentCategory,
    DocumentMetadata,
    DocumentStatus,
    DocumentType,
    FarmDocument,
    FileFormat,
)

logger = structlog.get_logger()


# ─────────────────────────────────────────────────────────────────────────────
# Storage Configuration - إعدادات التخزين
# ─────────────────────────────────────────────────────────────────────────────


class StorageConfig:
    """
    Storage configuration
    إعدادات التخزين
    """

    def __init__(
        self,
        base_path: str = "/var/sahool/documents",
        max_file_size: int = 50 * 1024 * 1024,  # 50MB
        allowed_formats: list[FileFormat] | None = None,
        generate_thumbnails: bool = True,
        thumbnail_size: tuple[int, int] = (200, 200),
        compute_checksums: bool = True,
    ):
        self.base_path = base_path
        self.max_file_size = max_file_size
        self.allowed_formats = allowed_formats or [
            FileFormat.PDF,
            FileFormat.PNG,
            FileFormat.JPG,
            FileFormat.JPEG,
            FileFormat.WEBP,
            FileFormat.TIFF,
            FileFormat.DOC,
            FileFormat.DOCX,
            FileFormat.XLS,
            FileFormat.XLSX,
        ]
        self.generate_thumbnails = generate_thumbnails
        self.thumbnail_size = thumbnail_size
        self.compute_checksums = compute_checksums


# ─────────────────────────────────────────────────────────────────────────────
# Storage Provider Interface - واجهة مزود التخزين
# ─────────────────────────────────────────────────────────────────────────────


class StorageProvider(ABC):
    """
    Abstract storage provider interface
    واجهة مزود التخزين المجردة
    """

    @abstractmethod
    async def store(
        self,
        file_content: bytes,
        storage_path: str,
    ) -> str:
        """Store file and return storage path"""
        pass

    @abstractmethod
    async def retrieve(self, storage_path: str) -> bytes:
        """Retrieve file content"""
        pass

    @abstractmethod
    async def delete(self, storage_path: str) -> bool:
        """Delete file"""
        pass

    @abstractmethod
    async def exists(self, storage_path: str) -> bool:
        """Check if file exists"""
        pass

    @abstractmethod
    async def get_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """Get access URL (optionally signed/expiring)"""
        pass


class LocalStorageProvider(StorageProvider):
    """
    Local filesystem storage provider
    مزود التخزين على نظام الملفات المحلي
    """

    def __init__(self, base_path: str):
        self.base_path = Path(base_path).resolve()
        # Directory is created lazily on first store() to avoid PermissionError
        # when the path requires elevated privileges (e.g. /var/sahool in tests).

    def _safe_path(self, storage_path: str) -> Path:
        """Resolve path and prevent path traversal outside base_path."""
        full_path = (self.base_path / storage_path).resolve()
        if not full_path.is_relative_to(self.base_path):
            raise ValueError(f"Path traversal detected: {storage_path}")
        return full_path

    async def store(
        self,
        file_content: bytes,
        storage_path: str,
    ) -> str:
        """Store file on local filesystem"""
        full_path = self._safe_path(storage_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "wb") as f:
            f.write(file_content)

        logger.info(
            "document_stored",
            storage_path=storage_path,
            size=len(file_content),
        )

        return storage_path

    async def retrieve(self, storage_path: str) -> bytes:
        """Retrieve file from local filesystem"""
        full_path = self._safe_path(storage_path)

        if not full_path.exists():
            raise FileNotFoundError(f"Document not found: {storage_path}")

        with open(full_path, "rb") as f:
            return f.read()

    async def delete(self, storage_path: str) -> bool:
        """Delete file from local filesystem"""
        full_path = self._safe_path(storage_path)

        if full_path.exists():
            full_path.unlink()
            logger.info("document_deleted", storage_path=storage_path)
            return True

        return False

    async def exists(self, storage_path: str) -> bool:
        """Check if file exists on local filesystem"""
        full_path = self._safe_path(storage_path)
        return full_path.exists()

    async def get_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """Get local file path as URL"""
        full_path = self._safe_path(storage_path)
        return f"file://{full_path}"


class S3StorageProvider(StorageProvider):
    """
    AWS S3 storage provider (placeholder for production)
    مزود تخزين AWS S3 (للإنتاج)
    """

    def __init__(
        self,
        bucket_name: str,
        region: str = "me-south-1",
        access_key: str | None = None,
        secret_key: str | None = None,
    ):
        self.bucket_name = bucket_name
        self.region = region
        self.access_key = access_key
        self.secret_key = secret_key
        # In production, initialize boto3 client here

    async def store(
        self,
        file_content: bytes,
        storage_path: str,
    ) -> str:
        """Store file on S3"""
        # Placeholder - implement with boto3
        logger.info(
            "s3_store_placeholder",
            bucket=self.bucket_name,
            path=storage_path,
        )
        return f"s3://{self.bucket_name}/{storage_path}"

    async def retrieve(self, storage_path: str) -> bytes:
        """Retrieve file from S3"""
        logger.error(
            "s3_retrieve_not_implemented",
            bucket=self.bucket_name,
            path=storage_path,
        )
        raise NotImplementedError(
            f"S3 retrieval not yet implemented for bucket={self.bucket_name}, path={storage_path}"
        )

    async def delete(self, storage_path: str) -> bool:
        """Delete file from S3"""
        logger.warning(
            "s3_delete_not_implemented",
            bucket=self.bucket_name,
            path=storage_path,
        )
        return False

    async def exists(self, storage_path: str) -> bool:
        """Check if file exists on S3"""
        logger.warning(
            "s3_exists_not_implemented",
            bucket=self.bucket_name,
            path=storage_path,
        )
        return False

    async def get_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """Get presigned S3 URL"""
        # Placeholder - implement with boto3 presigned URLs
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{storage_path}"


# ─────────────────────────────────────────────────────────────────────────────
# Document Storage Service - خدمة تخزين الوثائق
# ─────────────────────────────────────────────────────────────────────────────


class StorageError(Exception):
    """
    Storage operation error
    خطأ عملية التخزين
    """

    def __init__(self, message: str, error_code: str = "STORAGE_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class DocumentStorageService:
    """
    Document storage service
    خدمة تخزين الوثائق

    Handles document upload, retrieval, and management.
    تتعامل مع تحميل واسترجاع وإدارة الوثائق.
    """

    def __init__(
        self,
        config: StorageConfig | None = None,
        provider: StorageProvider | None = None,
    ):
        self.config = config or StorageConfig()
        self.provider = provider or LocalStorageProvider(self.config.base_path)

        # In-memory storage for demo/testing
        self._documents: dict[str, FarmDocument] = {}
        self._categories: dict[str, DocumentCategory] = {}

        # Initialize default categories
        self._init_default_categories()

    def _init_default_categories(self) -> None:
        """Initialize default document categories"""
        default_categories = [
            DocumentCategory(
                id="cat_cert",
                code="CERT",
                name_en="Certifications",
                name_ar="الشهادات",
                description_en="Certification documents and licenses",
                description_ar="وثائق الشهادات والتراخيص",
                document_types=[
                    DocumentType.CERTIFICATE,
                    DocumentType.LICENSE,
                    DocumentType.PERMIT,
                ],
                requires_expiry=True,
                icon="certificate",
                color="#10B981",
                order=1,
            ),
            DocumentCategory(
                id="cat_comp",
                code="COMP",
                name_en="Compliance",
                name_ar="الامتثال",
                description_en="Compliance and audit documents",
                description_ar="وثائق الامتثال والتدقيق",
                document_types=[
                    DocumentType.AUDIT_REPORT,
                    DocumentType.INSPECTION_REPORT,
                    DocumentType.COMPLIANCE_CHECKLIST,
                ],
                requires_expiry=True,
                icon="clipboard-check",
                color="#3B82F6",
                order=2,
            ),
            DocumentCategory(
                id="cat_farm",
                code="FARM",
                name_en="Farm Records",
                name_ar="سجلات المزرعة",
                description_en="Farm operation records",
                description_ar="سجلات تشغيل المزرعة",
                document_types=[
                    DocumentType.SOIL_TEST,
                    DocumentType.WATER_TEST,
                    DocumentType.PESTICIDE_RECORD,
                    DocumentType.FERTILIZER_RECORD,
                    DocumentType.HARVEST_RECORD,
                ],
                retention_days=365 * 5,  # 5 years
                icon="leaf",
                color="#22C55E",
                order=3,
            ),
            DocumentCategory(
                id="cat_legal",
                code="LEGAL",
                name_en="Legal Documents",
                name_ar="الوثائق القانونية",
                description_en="Legal and contractual documents",
                description_ar="الوثائق القانونية والتعاقدية",
                document_types=[
                    DocumentType.LAND_DEED,
                    DocumentType.LEASE_AGREEMENT,
                    DocumentType.INSURANCE_POLICY,
                    DocumentType.CONTRACT,
                ],
                requires_expiry=True,
                icon="scale",
                color="#8B5CF6",
                order=4,
            ),
            DocumentCategory(
                id="cat_fin",
                code="FIN",
                name_en="Financial",
                name_ar="المالية",
                description_en="Financial documents",
                description_ar="الوثائق المالية",
                document_types=[
                    DocumentType.INVOICE,
                    DocumentType.RECEIPT,
                    DocumentType.PAYMENT_PROOF,
                ],
                retention_days=365 * 7,  # 7 years
                icon="currency-dollar",
                color="#F59E0B",
                order=5,
            ),
            DocumentCategory(
                id="cat_train",
                code="TRAIN",
                name_en="Training",
                name_ar="التدريب",
                description_en="Training and safety certificates",
                description_ar="شهادات التدريب والسلامة",
                document_types=[
                    DocumentType.TRAINING_CERTIFICATE,
                    DocumentType.SAFETY_CERTIFICATE,
                ],
                requires_expiry=True,
                icon="academic-cap",
                color="#EC4899",
                order=6,
            ),
            DocumentCategory(
                id="cat_other",
                code="OTHER",
                name_en="Other",
                name_ar="أخرى",
                description_en="Other documents",
                description_ar="وثائق أخرى",
                document_types=[
                    DocumentType.PHOTO,
                    DocumentType.MAP,
                    DocumentType.PLAN,
                    DocumentType.REPORT,
                    DocumentType.OTHER,
                ],
                icon="folder",
                color="#6B7280",
                order=99,
            ),
        ]

        for category in default_categories:
            self._categories[category.id] = category

    # ─────────────────────────────────────────────────────────────────────────
    # Document Operations - عمليات الوثائق
    # ─────────────────────────────────────────────────────────────────────────

    async def upload_document(
        self,
        file_content: bytes,
        filename: str,
        tenant_id: str,
        farm_id: str,
        document_type: DocumentType,
        title_en: str,
        title_ar: str,
        uploaded_by: str,
        field_id: str | None = None,
        description_en: str | None = None,
        description_ar: str | None = None,
        category_id: str | None = None,
        expiry_date: datetime | None = None,
        tags: list[str] | None = None,
        tags_ar: list[str] | None = None,
    ) -> FarmDocument:
        """
        Upload a new document
        تحميل وثيقة جديدة

        Args:
            file_content: File binary content
            filename: Original filename
            tenant_id: Tenant ID
            farm_id: Farm ID
            document_type: Type of document
            title_en: Title in English
            title_ar: Title in Arabic
            uploaded_by: User ID who uploaded
            field_id: Optional field ID
            description_en: Description in English
            description_ar: Description in Arabic
            category_id: Category ID
            expiry_date: Document expiry date
            tags: Tags in English
            tags_ar: Tags in Arabic

        Returns:
            Created FarmDocument

        Raises:
            StorageError: If upload fails
        """
        # Validate file size
        if len(file_content) > self.config.max_file_size:
            max_mb = self.config.max_file_size / (1024 * 1024)
            raise StorageError(
                f"File too large. Maximum size is {max_mb}MB / الملف كبير جداً. الحد الأقصى {max_mb}MB",
                error_code="FILE_TOO_LARGE",
            )

        # Detect file format
        file_ext = Path(filename).suffix.lower().lstrip(".")
        try:
            file_format = FileFormat(file_ext)
        except ValueError:
            raise StorageError(
                f"Unsupported file format: {file_ext} / تنسيق ملف غير مدعوم: {file_ext}",
                error_code="UNSUPPORTED_FORMAT",
            )

        # Check if format is allowed
        if file_format not in self.config.allowed_formats:
            raise StorageError(
                f"File format not allowed: {file_ext} / تنسيق الملف غير مسموح: {file_ext}",
                error_code="FORMAT_NOT_ALLOWED",
            )

        # Detect MIME type
        mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

        # Compute checksums
        md5_hash = None
        sha256_hash = None
        if self.config.compute_checksums:
            # MD5 used for backward compatibility, not security
            md5_hash = hashlib.md5(
                file_content, usedforsecurity=False
            ).hexdigest()  # nosemgrep: python.lang.security.audit.insecure-hash-algorithm-md5 -- backward compatibility checksum, not for security
            sha256_hash = hashlib.sha256(file_content).hexdigest()

        # Generate document ID and storage path
        doc_id = str(uuid4())
        timestamp = datetime.now(UTC).strftime("%Y/%m/%d")
        safe_filename = self._sanitize_filename(filename)
        storage_path = f"{tenant_id}/{farm_id}/{timestamp}/{doc_id}_{safe_filename}"

        # Store file
        await self.provider.store(file_content, storage_path)

        # Create metadata
        metadata = DocumentMetadata(
            file_name=filename,
            file_size=len(file_content),
            file_format=file_format,
            mime_type=mime_type,
            md5_hash=md5_hash,
            sha256_hash=sha256_hash,
            storage_path=storage_path,
            storage_provider="local",
        )

        # Create document
        document = FarmDocument(
            id=doc_id,
            tenant_id=tenant_id,
            farm_id=farm_id,
            field_id=field_id,
            document_type=document_type,
            category_id=category_id or self._get_category_for_type(document_type),
            title_en=title_en,
            title_ar=title_ar,
            description_en=description_en,
            description_ar=description_ar,
            metadata=metadata,
            status=DocumentStatus.APPROVED,
            expiry_date=expiry_date.date() if expiry_date else None,
            tags=tags or [],
            tags_ar=tags_ar or [],
            uploaded_by=uploaded_by,
        )

        # Store document record
        self._documents[doc_id] = document

        logger.info(
            "document_uploaded",
            document_id=doc_id,
            farm_id=farm_id,
            document_type=document_type.value,
            file_size=len(file_content),
        )

        return document

    async def get_document(self, document_id: str) -> FarmDocument | None:
        """
        Get document by ID
        الحصول على وثيقة بالمعرف
        """
        return self._documents.get(document_id)

    async def get_document_content(self, document_id: str) -> bytes:
        """
        Get document file content
        الحصول على محتوى ملف الوثيقة
        """
        document = self._documents.get(document_id)
        if not document:
            raise StorageError(
                f"Document not found: {document_id} / لم يتم العثور على الوثيقة",
                error_code="NOT_FOUND",
            )

        return await self.provider.retrieve(document.metadata.storage_path)

    async def delete_document(
        self,
        document_id: str,
        deleted_by: str,
        hard_delete: bool = False,
    ) -> bool:
        """
        Delete document
        حذف وثيقة

        Args:
            document_id: Document ID
            deleted_by: User ID who deleted
            hard_delete: If True, permanently delete file

        Returns:
            True if deleted successfully
        """
        document = self._documents.get(document_id)
        if not document:
            return False

        if hard_delete:
            # Delete actual file
            await self.provider.delete(document.metadata.storage_path)
            del self._documents[document_id]
        else:
            # Soft delete - just mark as archived
            document.status = DocumentStatus.ARCHIVED
            document.updated_at = datetime.now(UTC)

        logger.info(
            "document_deleted",
            document_id=document_id,
            deleted_by=deleted_by,
            hard_delete=hard_delete,
        )

        return True

    async def list_documents(
        self,
        tenant_id: str,
        farm_id: str | None = None,
        field_id: str | None = None,
        document_type: DocumentType | None = None,
        category_id: str | None = None,
        status: DocumentStatus | None = None,
        tags: list[str] | None = None,
        include_expired: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> list[FarmDocument]:
        """
        List documents with filters
        قائمة الوثائق مع الفلاتر
        """
        results = []

        for doc in self._documents.values():
            # Apply filters
            if doc.tenant_id != tenant_id:
                continue
            if farm_id and doc.farm_id != farm_id:
                continue
            if field_id and doc.field_id != field_id:
                continue
            if document_type and doc.document_type != document_type:
                continue
            if category_id and doc.category_id != category_id:
                continue
            if status and doc.status != status:
                continue
            if not include_expired and doc.is_expired:
                continue
            if tags and not any(tag in doc.tags for tag in tags):
                continue

            results.append(doc)

        # Sort by created_at descending
        results.sort(key=lambda d: d.created_at, reverse=True)

        # Apply pagination
        return results[offset : offset + limit]

    async def search_documents(
        self,
        tenant_id: str,
        query: str,
        farm_id: str | None = None,
        limit: int = 50,
    ) -> list[FarmDocument]:
        """
        Search documents by title, description, or tags
        البحث في الوثائق بالعنوان أو الوصف أو العلامات
        """
        query_lower = query.lower()
        results = []

        for doc in self._documents.values():
            if doc.tenant_id != tenant_id:
                continue
            if farm_id and doc.farm_id != farm_id:
                continue

            # Search in title, description, and tags
            searchable = " ".join(
                [
                    doc.title_en.lower(),
                    doc.title_ar,
                    doc.description_en or "",
                    doc.description_ar or "",
                    " ".join(doc.tags),
                    " ".join(doc.tags_ar),
                ]
            )

            if query_lower in searchable:
                results.append(doc)

        return results[:limit]

    async def update_document(
        self,
        document_id: str,
        updated_by: str,
        title_en: str | None = None,
        title_ar: str | None = None,
        description_en: str | None = None,
        description_ar: str | None = None,
        expiry_date: datetime | None = None,
        tags: list[str] | None = None,
        tags_ar: list[str] | None = None,
        status: DocumentStatus | None = None,
    ) -> FarmDocument | None:
        """
        Update document metadata
        تحديث البيانات الوصفية للوثيقة
        """
        document = self._documents.get(document_id)
        if not document:
            return None

        if title_en is not None:
            document.title_en = title_en
        if title_ar is not None:
            document.title_ar = title_ar
        if description_en is not None:
            document.description_en = description_en
        if description_ar is not None:
            document.description_ar = description_ar
        if expiry_date is not None:
            document.expiry_date = expiry_date.date()
        if tags is not None:
            document.tags = tags
        if tags_ar is not None:
            document.tags_ar = tags_ar
        if status is not None:
            document.status = status

        document.updated_at = datetime.now(UTC)

        logger.info(
            "document_updated",
            document_id=document_id,
            updated_by=updated_by,
        )

        return document

    async def create_new_version(
        self,
        document_id: str,
        file_content: bytes,
        filename: str,
        uploaded_by: str,
    ) -> FarmDocument:
        """
        Create a new version of an existing document
        إنشاء نسخة جديدة من وثيقة موجودة
        """
        old_document = self._documents.get(document_id)
        if not old_document:
            raise StorageError(
                f"Original document not found: {document_id}",
                error_code="NOT_FOUND",
            )

        # Create new document with same metadata
        new_document = await self.upload_document(
            file_content=file_content,
            filename=filename,
            tenant_id=old_document.tenant_id,
            farm_id=old_document.farm_id,
            document_type=old_document.document_type,
            title_en=old_document.title_en,
            title_ar=old_document.title_ar,
            uploaded_by=uploaded_by,
            field_id=old_document.field_id,
            description_en=old_document.description_en,
            description_ar=old_document.description_ar,
            category_id=old_document.category_id,
            expiry_date=(
                datetime.combine(old_document.expiry_date, datetime.min.time()) if old_document.expiry_date else None
            ),
            tags=old_document.tags,
            tags_ar=old_document.tags_ar,
        )

        # Update version info
        new_document.version = old_document.version + 1
        new_document.previous_version_id = document_id

        # Archive old version
        old_document.status = DocumentStatus.ARCHIVED
        old_document.updated_at = datetime.now(UTC)

        logger.info(
            "document_version_created",
            old_document_id=document_id,
            new_document_id=new_document.id,
            version=new_document.version,
        )

        return new_document

    # ─────────────────────────────────────────────────────────────────────────
    # Category Operations - عمليات الفئات
    # ─────────────────────────────────────────────────────────────────────────

    async def get_categories(self) -> list[DocumentCategory]:
        """Get all document categories"""
        categories = list(self._categories.values())
        categories.sort(key=lambda c: c.order)
        return categories

    async def get_category(self, category_id: str) -> DocumentCategory | None:
        """Get category by ID"""
        return self._categories.get(category_id)

    async def create_category(self, category: DocumentCategory) -> DocumentCategory:
        """Create a new document category"""
        self._categories[category.id] = category
        return category

    async def update_category(
        self,
        category_id: str,
        **updates,
    ) -> DocumentCategory | None:
        """Update document category"""
        category = self._categories.get(category_id)
        if not category:
            return None

        for key, value in updates.items():
            if hasattr(category, key) and value is not None:
                setattr(category, key, value)

        category.updated_at = datetime.now(UTC)
        return category

    # ─────────────────────────────────────────────────────────────────────────
    # Utility Methods - الدوال المساعدة
    # ─────────────────────────────────────────────────────────────────────────

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for safe storage
        تنظيف اسم الملف للتخزين الآمن
        """
        # Get base name
        filename = os.path.basename(filename)

        # Remove dangerous characters
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
        sanitized = "".join(c if c in safe_chars else "_" for c in filename)

        # Remove leading dots
        sanitized = sanitized.lstrip(".")

        # Limit length
        if len(sanitized) > 200:
            name, ext = os.path.splitext(sanitized)
            sanitized = name[: 200 - len(ext)] + ext

        return sanitized or f"document_{uuid4().hex[:8]}"

    def _get_category_for_type(self, document_type: DocumentType) -> str | None:
        """Get default category ID for document type"""
        for category in self._categories.values():
            if document_type in category.document_types:
                return category.id
        return "cat_other"

    async def get_storage_stats(
        self,
        tenant_id: str,
        farm_id: str | None = None,
    ) -> dict:
        """
        Get storage statistics
        الحصول على إحصائيات التخزين
        """
        total_size = 0
        total_docs = 0
        by_type: dict[str, int] = {}
        by_format: dict[str, int] = {}

        for doc in self._documents.values():
            if doc.tenant_id != tenant_id:
                continue
            if farm_id and doc.farm_id != farm_id:
                continue

            total_docs += 1
            total_size += doc.metadata.file_size

            doc_type = doc.document_type.value
            by_type[doc_type] = by_type.get(doc_type, 0) + 1

            file_format = doc.metadata.file_format.value
            by_format[file_format] = by_format.get(file_format, 0) + 1

        return {
            "total_documents": total_docs,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "by_document_type": by_type,
            "by_file_format": by_format,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions - الدوال المساعدة
# ─────────────────────────────────────────────────────────────────────────────


def get_mime_type_for_format(file_format: FileFormat) -> str:
    """Get MIME type for file format"""
    mime_map = {
        FileFormat.PDF: "application/pdf",
        FileFormat.PNG: "image/png",
        FileFormat.JPG: "image/jpeg",
        FileFormat.JPEG: "image/jpeg",
        FileFormat.WEBP: "image/webp",
        FileFormat.TIFF: "image/tiff",
        FileFormat.DOC: "application/msword",
        FileFormat.DOCX: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        FileFormat.XLS: "application/vnd.ms-excel",
        FileFormat.XLSX: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }
    return mime_map.get(file_format, "application/octet-stream")


def is_image_format(file_format: FileFormat) -> bool:
    """Check if format is an image"""
    return file_format in [
        FileFormat.PNG,
        FileFormat.JPG,
        FileFormat.JPEG,
        FileFormat.WEBP,
        FileFormat.TIFF,
    ]


def is_document_format(file_format: FileFormat) -> bool:
    """Check if format is a document"""
    return file_format in [
        FileFormat.PDF,
        FileFormat.DOC,
        FileFormat.DOCX,
        FileFormat.XLS,
        FileFormat.XLSX,
    ]
