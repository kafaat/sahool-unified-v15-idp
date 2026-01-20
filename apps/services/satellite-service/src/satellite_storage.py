"""
SAHOOL Satellite Image Storage Service
خدمة تخزين صور الأقمار الصناعية

Stores satellite imagery in MinIO S3-compatible object storage:
- Raw satellite images (GeoTIFF)
- Processed NDVI/health maps (PNG, GeoTIFF)
- Thumbnails for quick preview
- Cached analysis results

Bucket Structure:
- sahool-satellite-raw/       Raw satellite imagery
- sahool-satellite-processed/ Processed maps and indices
- sahool-satellite-cache/     Cached analysis results (with TTL)
"""

import io
import hashlib
import logging
import os
from datetime import datetime, timedelta, UTC
from enum import Enum
from typing import BinaryIO, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# MinIO configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", os.getenv("MINIO_ROOT_USER", ""))
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", os.getenv("MINIO_ROOT_PASSWORD", ""))
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"
MINIO_REGION = os.getenv("MINIO_REGION", "us-east-1")

# Bucket names
BUCKET_RAW = os.getenv("SATELLITE_BUCKET_RAW", "sahool-satellite-raw")
BUCKET_PROCESSED = os.getenv("SATELLITE_BUCKET_PROCESSED", "sahool-satellite-processed")
BUCKET_CACHE = os.getenv("SATELLITE_BUCKET_CACHE", "sahool-satellite-cache")

# Cache TTL in days
CACHE_TTL_DAYS = int(os.getenv("SATELLITE_CACHE_TTL_DAYS", "30"))

# Try to import MinIO client
try:
    from minio import Minio
    from minio.error import S3Error
    MINIO_AVAILABLE = True
except ImportError:
    logger.warning("MinIO client not installed. Run: pip install minio")
    MINIO_AVAILABLE = False
    Minio = None
    S3Error = Exception


class ImageType(Enum):
    """أنواع الصور"""
    RAW_GEOTIFF = "raw_geotiff"
    PROCESSED_NDVI = "processed_ndvi"
    PROCESSED_HEALTH = "processed_health"
    PROCESSED_LAI = "processed_lai"
    THUMBNAIL = "thumbnail"
    COLORMAP = "colormap"


class SatelliteSource(Enum):
    """مصادر الأقمار الصناعية"""
    SENTINEL_2 = "sentinel2"
    LANDSAT_8 = "landsat8"
    LANDSAT_9 = "landsat9"
    MODIS = "modis"
    SIMULATED = "simulated"


@dataclass
class StoredImage:
    """معلومات الصورة المخزنة"""
    bucket: str
    object_name: str
    url: str
    size_bytes: int
    content_type: str
    etag: str
    created_at: datetime
    metadata: dict


@dataclass
class ImageMetadata:
    """بيانات وصفية للصورة"""
    field_id: str
    tenant_id: str
    capture_date: str
    satellite_source: str
    image_type: str
    bands: Optional[str] = None
    cloud_coverage: Optional[float] = None
    resolution_meters: Optional[float] = None
    bbox: Optional[str] = None  # "minx,miny,maxx,maxy"
    crs: Optional[str] = "EPSG:4326"


class SatelliteStorageService:
    """
    Service for storing and retrieving satellite imagery from MinIO.
    خدمة تخزين واسترجاع صور الأقمار الصناعية من MinIO
    """

    def __init__(self):
        self._client: Optional[Minio] = None
        self._initialized = False
        self._buckets_created = False

    @property
    def client(self) -> Optional[Minio]:
        """Get or create MinIO client (lazy initialization)"""
        if not MINIO_AVAILABLE:
            logger.warning("MinIO client not available")
            return None

        if self._client is None and MINIO_ACCESS_KEY and MINIO_SECRET_KEY:
            try:
                self._client = Minio(
                    MINIO_ENDPOINT,
                    access_key=MINIO_ACCESS_KEY,
                    secret_key=MINIO_SECRET_KEY,
                    secure=MINIO_SECURE,
                    region=MINIO_REGION,
                )
                logger.info(f"MinIO client initialized: {MINIO_ENDPOINT}")
            except Exception as e:
                logger.error(f"Failed to initialize MinIO client: {e}")
                self._client = None

        return self._client

    @property
    def is_available(self) -> bool:
        """Check if storage service is available"""
        return self.client is not None

    async def initialize(self) -> bool:
        """
        Initialize storage service and create buckets if needed.
        تهيئة خدمة التخزين وإنشاء الـ buckets
        """
        if self._initialized:
            return True

        if not self.is_available:
            logger.warning("MinIO not available - satellite images will not be stored")
            return False

        try:
            # Create buckets if they don't exist
            await self._ensure_buckets()
            self._initialized = True
            logger.info("Satellite storage service initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize satellite storage: {e}")
            return False

    async def _ensure_buckets(self):
        """Create required buckets if they don't exist"""
        if self._buckets_created:
            return

        buckets = [BUCKET_RAW, BUCKET_PROCESSED, BUCKET_CACHE]

        for bucket_name in buckets:
            try:
                if not self.client.bucket_exists(bucket_name):
                    self.client.make_bucket(bucket_name, location=MINIO_REGION)
                    logger.info(f"Created bucket: {bucket_name}")

                    # Set lifecycle policy for cache bucket
                    if bucket_name == BUCKET_CACHE:
                        self._set_cache_lifecycle(bucket_name)
                else:
                    logger.debug(f"Bucket already exists: {bucket_name}")
            except S3Error as e:
                logger.error(f"Error creating bucket {bucket_name}: {e}")
                raise

        self._buckets_created = True

    def _set_cache_lifecycle(self, bucket_name: str):
        """Set lifecycle policy for cache bucket to auto-delete old files"""
        try:
            from minio.lifecycleconfig import LifecycleConfig, Rule, Expiration

            config = LifecycleConfig(
                [
                    Rule(
                        rule_id="expire-cache",
                        status="Enabled",
                        expiration=Expiration(days=CACHE_TTL_DAYS),
                    )
                ]
            )
            self.client.set_bucket_lifecycle(bucket_name, config)
            logger.info(f"Set {CACHE_TTL_DAYS}-day lifecycle policy on {bucket_name}")
        except ImportError:
            logger.warning("Lifecycle config not available in this MinIO version")
        except Exception as e:
            logger.warning(f"Could not set lifecycle policy: {e}")

    def _generate_object_name(
        self,
        metadata: ImageMetadata,
        image_type: ImageType,
        extension: str = "tiff"
    ) -> str:
        """
        Generate a structured object name for the image.
        إنشاء اسم منظم للصورة

        Format: tenant_id/field_id/YYYY/MM/DD/satellite_type_capture_date.ext
        """
        capture_date = datetime.fromisoformat(metadata.capture_date.replace("Z", "+00:00"))

        path_parts = [
            metadata.tenant_id,
            metadata.field_id,
            capture_date.strftime("%Y"),
            capture_date.strftime("%m"),
            capture_date.strftime("%d"),
        ]

        filename = f"{metadata.satellite_source}_{image_type.value}_{capture_date.strftime('%Y%m%d_%H%M%S')}.{extension}"

        return "/".join(path_parts) + "/" + filename

    def _get_content_type(self, extension: str) -> str:
        """Get MIME type for file extension"""
        content_types = {
            "tiff": "image/tiff",
            "tif": "image/tiff",
            "geotiff": "image/tiff",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "json": "application/json",
        }
        return content_types.get(extension.lower(), "application/octet-stream")

    async def store_raw_image(
        self,
        image_data: bytes | BinaryIO,
        metadata: ImageMetadata,
        extension: str = "tiff"
    ) -> Optional[StoredImage]:
        """
        Store raw satellite image.
        تخزين الصورة الأصلية للقمر الصناعي

        Args:
            image_data: Raw image data (GeoTIFF)
            metadata: Image metadata
            extension: File extension

        Returns:
            StoredImage with URL and details
        """
        return await self._store_image(
            bucket=BUCKET_RAW,
            image_data=image_data,
            metadata=metadata,
            image_type=ImageType.RAW_GEOTIFF,
            extension=extension,
        )

    async def store_processed_image(
        self,
        image_data: bytes | BinaryIO,
        metadata: ImageMetadata,
        image_type: ImageType = ImageType.PROCESSED_NDVI,
        extension: str = "png"
    ) -> Optional[StoredImage]:
        """
        Store processed satellite image (NDVI, health map, etc.).
        تخزين الصورة المعالجة (NDVI، خريطة الصحة، إلخ)

        Args:
            image_data: Processed image data
            metadata: Image metadata
            image_type: Type of processed image
            extension: File extension

        Returns:
            StoredImage with URL and details
        """
        return await self._store_image(
            bucket=BUCKET_PROCESSED,
            image_data=image_data,
            metadata=metadata,
            image_type=image_type,
            extension=extension,
        )

    async def store_thumbnail(
        self,
        image_data: bytes | BinaryIO,
        metadata: ImageMetadata,
        extension: str = "png"
    ) -> Optional[StoredImage]:
        """
        Store thumbnail image.
        تخزين الصورة المصغرة
        """
        return await self._store_image(
            bucket=BUCKET_PROCESSED,
            image_data=image_data,
            metadata=metadata,
            image_type=ImageType.THUMBNAIL,
            extension=extension,
        )

    async def store_cached_analysis(
        self,
        data: bytes,
        cache_key: str,
        content_type: str = "application/json"
    ) -> Optional[StoredImage]:
        """
        Store cached analysis results.
        تخزين نتائج التحليل المؤقتة
        """
        if not self.is_available:
            return None

        try:
            object_name = f"cache/{cache_key}"

            # Convert to BytesIO if needed
            if isinstance(data, bytes):
                data_stream = io.BytesIO(data)
                data_length = len(data)
            else:
                data_stream = data
                data_length = -1

            result = self.client.put_object(
                bucket_name=BUCKET_CACHE,
                object_name=object_name,
                data=data_stream,
                length=data_length,
                content_type=content_type,
            )

            url = self._generate_url(BUCKET_CACHE, object_name)

            return StoredImage(
                bucket=BUCKET_CACHE,
                object_name=object_name,
                url=url,
                size_bytes=data_length if data_length > 0 else 0,
                content_type=content_type,
                etag=result.etag,
                created_at=datetime.now(UTC),
                metadata={"cache_key": cache_key},
            )
        except Exception as e:
            logger.error(f"Failed to store cached analysis: {e}")
            return None

    async def _store_image(
        self,
        bucket: str,
        image_data: bytes | BinaryIO,
        metadata: ImageMetadata,
        image_type: ImageType,
        extension: str,
    ) -> Optional[StoredImage]:
        """Internal method to store image in MinIO"""
        if not self.is_available:
            logger.warning("MinIO not available - cannot store image")
            return None

        try:
            object_name = self._generate_object_name(metadata, image_type, extension)
            content_type = self._get_content_type(extension)

            # Prepare metadata for MinIO
            minio_metadata = {
                "x-amz-meta-field-id": metadata.field_id,
                "x-amz-meta-tenant-id": metadata.tenant_id,
                "x-amz-meta-capture-date": metadata.capture_date,
                "x-amz-meta-satellite": metadata.satellite_source,
                "x-amz-meta-image-type": image_type.value,
            }

            if metadata.cloud_coverage is not None:
                minio_metadata["x-amz-meta-cloud-coverage"] = str(metadata.cloud_coverage)
            if metadata.resolution_meters is not None:
                minio_metadata["x-amz-meta-resolution"] = str(metadata.resolution_meters)
            if metadata.bbox:
                minio_metadata["x-amz-meta-bbox"] = metadata.bbox
            if metadata.bands:
                minio_metadata["x-amz-meta-bands"] = metadata.bands

            # Convert to BytesIO if needed
            if isinstance(image_data, bytes):
                data_stream = io.BytesIO(image_data)
                data_length = len(image_data)
            else:
                # Seek to end to get size, then back to start
                image_data.seek(0, 2)
                data_length = image_data.tell()
                image_data.seek(0)
                data_stream = image_data

            # Upload to MinIO
            result = self.client.put_object(
                bucket_name=bucket,
                object_name=object_name,
                data=data_stream,
                length=data_length,
                content_type=content_type,
                metadata=minio_metadata,
            )

            url = self._generate_url(bucket, object_name)

            logger.info(f"Stored satellite image: {bucket}/{object_name} ({data_length} bytes)")

            return StoredImage(
                bucket=bucket,
                object_name=object_name,
                url=url,
                size_bytes=data_length,
                content_type=content_type,
                etag=result.etag,
                created_at=datetime.now(UTC),
                metadata={
                    "field_id": metadata.field_id,
                    "tenant_id": metadata.tenant_id,
                    "capture_date": metadata.capture_date,
                    "satellite_source": metadata.satellite_source,
                    "image_type": image_type.value,
                },
            )

        except S3Error as e:
            logger.error(f"S3 error storing image: {e}")
            return None
        except Exception as e:
            logger.error(f"Error storing image: {e}")
            return None

    def _generate_url(self, bucket: str, object_name: str) -> str:
        """Generate URL for stored object"""
        protocol = "https" if MINIO_SECURE else "http"
        return f"{protocol}://{MINIO_ENDPOINT}/{bucket}/{object_name}"

    async def get_image(self, bucket: str, object_name: str) -> Optional[bytes]:
        """
        Retrieve image from storage.
        استرجاع الصورة من التخزين
        """
        if not self.is_available:
            return None

        try:
            response = self.client.get_object(bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            if e.code == "NoSuchKey":
                logger.debug(f"Object not found: {bucket}/{object_name}")
            else:
                logger.error(f"Error retrieving image: {e}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving image: {e}")
            return None

    async def get_presigned_url(
        self,
        bucket: str,
        object_name: str,
        expires: timedelta = timedelta(hours=1)
    ) -> Optional[str]:
        """
        Generate presigned URL for direct download.
        إنشاء رابط مؤقت للتحميل المباشر
        """
        if not self.is_available:
            return None

        try:
            url = self.client.presigned_get_object(
                bucket_name=bucket,
                object_name=object_name,
                expires=expires,
            )
            return url
        except Exception as e:
            logger.error(f"Error generating presigned URL: {e}")
            return None

    async def delete_image(self, bucket: str, object_name: str) -> bool:
        """
        Delete image from storage.
        حذف الصورة من التخزين
        """
        if not self.is_available:
            return False

        try:
            self.client.remove_object(bucket, object_name)
            logger.info(f"Deleted image: {bucket}/{object_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting image: {e}")
            return False

    async def list_field_images(
        self,
        tenant_id: str,
        field_id: str,
        bucket: str = BUCKET_PROCESSED,
        prefix_filter: Optional[str] = None,
    ) -> list[dict]:
        """
        List all images for a field.
        قائمة جميع صور الحقل
        """
        if not self.is_available:
            return []

        try:
            prefix = f"{tenant_id}/{field_id}/"
            if prefix_filter:
                prefix += prefix_filter

            objects = self.client.list_objects(bucket, prefix=prefix, recursive=True)

            images = []
            for obj in objects:
                images.append({
                    "object_name": obj.object_name,
                    "size_bytes": obj.size,
                    "last_modified": obj.last_modified.isoformat() if obj.last_modified else None,
                    "etag": obj.etag,
                    "url": self._generate_url(bucket, obj.object_name),
                })

            return images
        except Exception as e:
            logger.error(f"Error listing field images: {e}")
            return []

    async def get_storage_stats(self) -> dict:
        """
        Get storage statistics.
        إحصائيات التخزين
        """
        if not self.is_available:
            return {"available": False, "error": "MinIO not available"}

        stats = {
            "available": True,
            "endpoint": MINIO_ENDPOINT,
            "buckets": {},
        }

        for bucket_name in [BUCKET_RAW, BUCKET_PROCESSED, BUCKET_CACHE]:
            try:
                if self.client.bucket_exists(bucket_name):
                    objects = list(self.client.list_objects(bucket_name, recursive=True))
                    total_size = sum(obj.size for obj in objects)
                    stats["buckets"][bucket_name] = {
                        "exists": True,
                        "object_count": len(objects),
                        "total_size_bytes": total_size,
                        "total_size_mb": round(total_size / (1024 * 1024), 2),
                    }
                else:
                    stats["buckets"][bucket_name] = {"exists": False}
            except Exception as e:
                stats["buckets"][bucket_name] = {"error": str(e)}

        return stats

    async def health_check(self) -> dict:
        """
        Health check for storage service.
        فحص صحة خدمة التخزين
        """
        if not self.is_available:
            return {
                "status": "unavailable",
                "error": "MinIO client not configured",
            }

        try:
            # Check if we can list buckets
            buckets = list(self.client.list_buckets())
            return {
                "status": "healthy",
                "endpoint": MINIO_ENDPOINT,
                "bucket_count": len(buckets),
                "satellite_buckets_ready": all(
                    self.client.bucket_exists(b)
                    for b in [BUCKET_RAW, BUCKET_PROCESSED, BUCKET_CACHE]
                ),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }


# Global instance
_storage_service: Optional[SatelliteStorageService] = None


def get_satellite_storage() -> SatelliteStorageService:
    """Get or create the global satellite storage service instance"""
    global _storage_service
    if _storage_service is None:
        _storage_service = SatelliteStorageService()
    return _storage_service


async def init_satellite_storage() -> bool:
    """Initialize satellite storage service"""
    storage = get_satellite_storage()
    return await storage.initialize()
