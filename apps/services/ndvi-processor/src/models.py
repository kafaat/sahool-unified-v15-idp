"""
SAHOOL NDVI Processor - Data Models
نماذج بيانات معالج NDVI
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


# ============== Enums ==============


class SatelliteSource(str, Enum):
    """مصادر الأقمار الصناعية"""

    SENTINEL_2 = "sentinel-2"
    LANDSAT_8 = "landsat-8"
    LANDSAT_9 = "landsat-9"
    MODIS = "modis"


class JobStatus(str, Enum):
    """حالة المهمة"""

    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CompositeMethod(str, Enum):
    """طريقة التركيب"""

    MAX_NDVI = "max_ndvi"
    MEAN_NDVI = "mean_ndvi"
    MEDIAN_NDVI = "median_ndvi"
    MIN_CLOUD = "min_cloud"


class ExportFormat(str, Enum):
    """صيغة التصدير"""

    GEOTIFF = "geotiff"
    PNG = "png"
    CSV = "csv"
    JSON = "json"


class TrendDirection(str, Enum):
    """اتجاه التغير"""

    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"


# ============== Processing Options ==============


class ProcessingOptions(BaseModel):
    """خيارات المعالجة"""

    cloud_threshold_percent: int = Field(default=20, ge=0, le=100)
    atmospheric_correction: bool = Field(default=True)
    cloud_masking: bool = Field(default=True)
    output_format: ExportFormat = Field(default=ExportFormat.GEOTIFF)
    include_thumbnail: bool = Field(default=True)


class DateRange(BaseModel):
    """نطاق التاريخ"""

    start: str = Field(..., description="تاريخ البداية YYYY-MM-DD")
    end: str = Field(..., description="تاريخ النهاية YYYY-MM-DD")


# ============== Request Models ==============


class ProcessRequest(BaseModel):
    """طلب معالجة صورة"""

    tenant_id: str
    field_id: str
    source: SatelliteSource = Field(default=SatelliteSource.SENTINEL_2)
    date_range: DateRange
    options: Optional[ProcessingOptions] = None
    priority: int = Field(default=5, ge=1, le=10)
    callback_url: Optional[str] = None


class CompositeRequest(BaseModel):
    """طلب إنشاء مركب"""

    tenant_id: str
    field_id: str
    year: int = Field(..., ge=2000, le=2100)
    month: int = Field(..., ge=1, le=12)
    method: CompositeMethod = Field(default=CompositeMethod.MAX_NDVI)
    source: SatelliteSource = Field(default=SatelliteSource.SENTINEL_2)


class ChangeAnalysisRequest(BaseModel):
    """طلب تحليل التغير"""

    tenant_id: str
    field_id: str
    date1: str
    date2: str
    include_zones: bool = Field(default=True)


class SeasonalAnalysisRequest(BaseModel):
    """طلب تحليل موسمي"""

    tenant_id: str
    field_id: str
    year: int = Field(..., ge=2000, le=2100)


# ============== Response Models ==============


class NDVIStatistics(BaseModel):
    """إحصائيات NDVI"""

    mean: float = Field(..., ge=-1, le=1)
    median: Optional[float] = Field(None, ge=-1, le=1)
    std: float = Field(..., ge=0)
    min: float = Field(..., ge=-1, le=1)
    max: float = Field(..., ge=-1, le=1)
    percentiles: Optional[Dict[str, float]] = None


class QualityMetrics(BaseModel):
    """مقاييس الجودة"""

    cloud_cover_percent: float = Field(..., ge=0, le=100)
    shadow_percent: Optional[float] = Field(None, ge=0, le=100)
    valid_pixels_percent: float = Field(..., ge=0, le=100)


class SourceInfo(BaseModel):
    """معلومات المصدر"""

    satellite: str
    scene_id: str
    acquisition_time: str
    resolution_meters: int


class ProcessingInfo(BaseModel):
    """معلومات المعالجة"""

    atmospheric_correction: Optional[str]
    cloud_mask: Optional[str]
    processed_at: str


class FileUrls(BaseModel):
    """روابط الملفات"""

    geotiff: Optional[str] = None
    png: Optional[str] = None
    thumbnail: Optional[str] = None


class NDVIResult(BaseModel):
    """نتيجة NDVI"""

    id: str
    field_id: str
    date: str
    source: SourceInfo
    processing: ProcessingInfo
    statistics: NDVIStatistics
    quality: QualityMetrics
    files: FileUrls


class TimeseriesPoint(BaseModel):
    """نقطة في السلسلة الزمنية"""

    date: str
    ndvi_mean: float
    ndvi_min: float
    ndvi_max: float
    cloud_cover_percent: float
    source: str


class TimeseriesResponse(BaseModel):
    """استجابة السلسلة الزمنية"""

    field_id: str
    start_date: str
    end_date: str
    data: List[TimeseriesPoint]
    total_points: int
    sources: List[str]


class ZoneChange(BaseModel):
    """تغير منطقة"""

    zone: str
    zone_name_ar: Optional[str]
    ndvi_date1: float
    ndvi_date2: float
    change: float
    change_percent: float
    trend: TrendDirection


class ChangeAnalysisResponse(BaseModel):
    """استجابة تحليل التغير"""

    field_id: str
    date1: str
    date2: str
    days_between: int
    change: Dict[str, Any]
    zones: Optional[List[ZoneChange]]


class SeasonalStats(BaseModel):
    """إحصائيات موسمية"""

    season: str
    season_ar: str
    months: List[int]
    ndvi_mean: float
    ndvi_max: float
    ndvi_min: float
    observations_count: int


class SeasonalAnalysisResponse(BaseModel):
    """استجابة التحليل الموسمي"""

    field_id: str
    year: int
    seasons: List[SeasonalStats]
    peak_month: int
    trough_month: int
    annual_mean: float


class AnomalyResponse(BaseModel):
    """استجابة الشذوذ"""

    field_id: str
    date: str
    current_ndvi: float
    historical_mean: float
    historical_std: float
    z_score: float
    is_anomaly: bool
    anomaly_type: Optional[str]
    severity: Optional[str]


# ============== Job Models ==============


class JobResponse(BaseModel):
    """استجابة المهمة"""

    job_id: str
    field_id: str
    tenant_id: str
    type: str
    status: JobStatus
    progress_percent: int = Field(..., ge=0, le=100)
    parameters: Dict[str, Any]
    started_at: Optional[str]
    completed_at: Optional[str]
    estimated_completion: Optional[str]
    result: Optional[Dict[str, Any]]
    error: Optional[str]


class JobListResponse(BaseModel):
    """قائمة المهام"""

    jobs: List[JobResponse]
    total: int
    active_count: int


# ============== Composite Models ==============


class CompositeResponse(BaseModel):
    """استجابة المركب"""

    composite_id: str
    field_id: str
    year: int
    month: int
    method: str
    source: str
    statistics: NDVIStatistics
    images_used: int
    files: FileUrls
    created_at: str


class CompositeListResponse(BaseModel):
    """قائمة المركبات"""

    field_id: str
    composites: List[CompositeResponse]
    total: int
