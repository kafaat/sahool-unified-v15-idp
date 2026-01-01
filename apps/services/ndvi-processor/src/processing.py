"""
SAHOOL NDVI Processor - Processing Logic
منطق معالجة NDVI
"""

import os
import random
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Tuple
from uuid import uuid4

from .models import (
    JobStatus,
    SatelliteSource,
    CompositeMethod,
    TrendDirection,
    NDVIStatistics,
    QualityMetrics,
    SourceInfo,
    ProcessingInfo,
    FileUrls,
    NDVIResult,
    TimeseriesPoint,
    ZoneChange,
    SeasonalStats,
)


# ============== Mock Data Store ==============

_jobs: Dict[str, dict] = {}
_results: Dict[str, List[dict]] = {}  # field_id -> [NDVIResult]
_composites: Dict[str, dict] = {}


# ============== Job Management ==============


def create_job(
    tenant_id: str, field_id: str, job_type: str, parameters: dict, priority: int = 5
) -> str:
    """إنشاء مهمة معالجة"""
    job_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()

    # تقدير وقت الإنجاز
    estimated_minutes = random.randint(2, 10)
    estimated = (
        datetime.now(timezone.utc) + timedelta(minutes=estimated_minutes)
    ).isoformat()

    job = {
        "job_id": job_id,
        "tenant_id": tenant_id,
        "field_id": field_id,
        "type": job_type,
        "status": JobStatus.QUEUED.value,
        "progress_percent": 0,
        "parameters": parameters,
        "priority": priority,
        "started_at": None,
        "completed_at": None,
        "estimated_completion": estimated,
        "result": None,
        "error": None,
        "created_at": now,
    }

    _jobs[job_id] = job
    return job_id


def get_job(job_id: str) -> Optional[dict]:
    """جلب مهمة"""
    return _jobs.get(job_id)


def update_job_status(
    job_id: str,
    status: JobStatus,
    progress: int = None,
    result: dict = None,
    error: str = None,
) -> Optional[dict]:
    """تحديث حالة المهمة"""
    if job_id not in _jobs:
        return None

    job = _jobs[job_id]
    job["status"] = status.value

    if progress is not None:
        job["progress_percent"] = progress

    if status == JobStatus.PROCESSING and not job["started_at"]:
        job["started_at"] = datetime.now(timezone.utc).isoformat()

    if status in [JobStatus.COMPLETED, JobStatus.FAILED]:
        job["completed_at"] = datetime.now(timezone.utc).isoformat()
        job["progress_percent"] = (
            100 if status == JobStatus.COMPLETED else job["progress_percent"]
        )

    if result:
        job["result"] = result

    if error:
        job["error"] = error

    _jobs[job_id] = job
    return job


def cancel_job(job_id: str) -> bool:
    """إلغاء مهمة"""
    if job_id not in _jobs:
        return False

    job = _jobs[job_id]
    if job["status"] in [JobStatus.COMPLETED.value, JobStatus.FAILED.value]:
        return False

    job["status"] = JobStatus.CANCELLED.value
    job["completed_at"] = datetime.now(timezone.utc).isoformat()
    _jobs[job_id] = job
    return True


def list_jobs(
    tenant_id: str = None, field_id: str = None, status: str = None
) -> List[dict]:
    """قائمة المهام"""
    jobs = list(_jobs.values())

    if tenant_id:
        jobs = [j for j in jobs if j["tenant_id"] == tenant_id]
    if field_id:
        jobs = [j for j in jobs if j["field_id"] == field_id]
    if status:
        jobs = [j for j in jobs if j["status"] == status]

    return sorted(jobs, key=lambda x: x["created_at"], reverse=True)


# ============== NDVI Processing ==============


def process_ndvi_mock(
    field_id: str,
    source: SatelliteSource,
    date_range: Tuple[str, str],
    options: dict = None,
) -> NDVIResult:
    """معالجة NDVI (محاكاة)"""
    options = options or {}
    result_id = str(uuid4())
    now = datetime.now(timezone.utc)

    # محاكاة قيم NDVI
    base_ndvi = random.uniform(0.4, 0.8)
    variation = random.uniform(0.1, 0.2)

    ndvi_mean = round(base_ndvi, 3)
    ndvi_min = round(base_ndvi - variation, 3)
    ndvi_max = round(base_ndvi + variation, 3)
    ndvi_std = round(variation / 3, 3)

    # معلومات المصدر
    resolution_map = {
        SatelliteSource.SENTINEL_2: 10,
        SatelliteSource.LANDSAT_8: 30,
        SatelliteSource.LANDSAT_9: 30,
        SatelliteSource.MODIS: 250,
    }

    source_info = SourceInfo(
        satellite=source.value,
        scene_id=f"{source.value.upper()}_{now.strftime('%Y%m%d')}_{field_id[:8]}",
        acquisition_time=now.isoformat(),
        resolution_meters=resolution_map.get(source, 10),
    )

    # معلومات المعالجة
    processing_info = ProcessingInfo(
        atmospheric_correction=(
            "sen2cor" if options.get("atmospheric_correction", True) else None
        ),
        cloud_mask="s2cloudless" if options.get("cloud_masking", True) else None,
        processed_at=now.isoformat(),
    )

    # مقاييس الجودة
    cloud_cover = random.uniform(0, options.get("cloud_threshold_percent", 20))
    quality = QualityMetrics(
        cloud_cover_percent=round(cloud_cover, 1),
        shadow_percent=round(random.uniform(0, 5), 1),
        valid_pixels_percent=round(100 - cloud_cover - random.uniform(0, 5), 1),
    )

    # الإحصائيات
    statistics = NDVIStatistics(
        mean=ndvi_mean,
        median=round(ndvi_mean + random.uniform(-0.02, 0.02), 3),
        std=ndvi_std,
        min=ndvi_min,
        max=ndvi_max,
        percentiles={
            "p10": round(ndvi_min + 0.05, 3),
            "p25": round(ndvi_min + 0.1, 3),
            "p75": round(ndvi_max - 0.1, 3),
            "p90": round(ndvi_max - 0.05, 3),
        },
    )

    # روابط الملفات (محاكاة)
    bucket = os.getenv("S3_BUCKET", "sahool-ndvi-data")
    date_str = date_range[0]
    files = FileUrls(
        geotiff=f"s3://{bucket}/{field_id}/{date_str}.tif",
        png=f"s3://{bucket}/{field_id}/{date_str}.png",
        thumbnail=f"s3://{bucket}/{field_id}/{date_str}_thumb.png",
    )

    result = NDVIResult(
        id=result_id,
        field_id=field_id,
        date=date_range[0],
        source=source_info,
        processing=processing_info,
        statistics=statistics,
        quality=quality,
        files=files,
    )

    # تخزين النتيجة
    if field_id not in _results:
        _results[field_id] = []
    _results[field_id].append(result.model_dump())

    return result


def get_field_ndvi(field_id: str, date: str = None) -> Optional[dict]:
    """جلب NDVI لحقل"""
    if field_id not in _results:
        return None

    results = _results[field_id]
    if not results:
        return None

    if date:
        for r in results:
            if r["date"] == date:
                return r
        return None

    # أحدث نتيجة
    return sorted(results, key=lambda x: x["date"], reverse=True)[0]


def get_ndvi_timeseries(
    field_id: str, start_date: str, end_date: str
) -> List[TimeseriesPoint]:
    """جلب السلسلة الزمنية"""
    if field_id not in _results:
        # توليد بيانات محاكاة
        return _generate_mock_timeseries(field_id, start_date, end_date)

    results = _results[field_id]
    filtered = [r for r in results if start_date <= r["date"] <= end_date]

    points = []
    for r in sorted(filtered, key=lambda x: x["date"]):
        points.append(
            TimeseriesPoint(
                date=r["date"],
                ndvi_mean=r["statistics"]["mean"],
                ndvi_min=r["statistics"]["min"],
                ndvi_max=r["statistics"]["max"],
                cloud_cover_percent=r["quality"]["cloud_cover_percent"],
                source=r["source"]["satellite"],
            )
        )

    return points


def _generate_mock_timeseries(
    field_id: str, start_date: str, end_date: str
) -> List[TimeseriesPoint]:
    """توليد سلسلة زمنية محاكاة"""
    from datetime import datetime

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    points = []
    current = start
    base_ndvi = random.uniform(0.5, 0.7)

    while current <= end:
        # تغير موسمي
        day_of_year = current.timetuple().tm_yday
        seasonal = 0.1 * (1 + (day_of_year - 180) / 180)  # ذروة في الصيف

        ndvi = base_ndvi + seasonal + random.uniform(-0.05, 0.05)
        ndvi = max(-1, min(1, ndvi))

        points.append(
            TimeseriesPoint(
                date=current.strftime("%Y-%m-%d"),
                ndvi_mean=round(ndvi, 3),
                ndvi_min=round(ndvi - 0.1, 3),
                ndvi_max=round(ndvi + 0.1, 3),
                cloud_cover_percent=round(random.uniform(0, 30), 1),
                source="sentinel-2",
            )
        )

        current += timedelta(days=5)  # تردد Sentinel-2

    return points


# ============== Change Analysis ==============


def analyze_change(
    field_id: str, date1: str, date2: str, include_zones: bool = True
) -> dict:
    """تحليل التغير بين تاريخين"""
    from datetime import datetime

    d1 = datetime.strptime(date1, "%Y-%m-%d")
    d2 = datetime.strptime(date2, "%Y-%m-%d")
    days_between = abs((d2 - d1).days)

    # محاكاة NDVI للتاريخين
    ndvi1 = random.uniform(0.4, 0.7)
    ndvi2 = ndvi1 + random.uniform(-0.15, 0.15)

    mean_change = round(ndvi2 - ndvi1, 3)
    percent_change = round((mean_change / ndvi1) * 100, 1) if ndvi1 != 0 else 0

    # تحديد الاتجاه
    if mean_change > 0.05:
        pct_increased, pct_decreased, pct_stable = 65, 20, 15
    elif mean_change < -0.05:
        pct_increased, pct_decreased, pct_stable = 20, 65, 15
    else:
        pct_increased, pct_decreased, pct_stable = 30, 30, 40

    change_data = {
        "mean_change": mean_change,
        "percent_change": percent_change,
        "percent_increased": pct_increased,
        "percent_decreased": pct_decreased,
        "percent_stable": pct_stable,
        "ndvi_date1": round(ndvi1, 3),
        "ndvi_date2": round(ndvi2, 3),
    }

    zones = None
    if include_zones:
        zones = [
            ZoneChange(
                zone="north",
                zone_name_ar="الشمال",
                ndvi_date1=round(ndvi1 + random.uniform(-0.05, 0.05), 3),
                ndvi_date2=round(ndvi2 + random.uniform(-0.05, 0.1), 3),
                change=round(random.uniform(-0.05, 0.15), 3),
                change_percent=round(random.uniform(-10, 20), 1),
                trend=TrendDirection.IMPROVING,
            ),
            ZoneChange(
                zone="south",
                zone_name_ar="الجنوب",
                ndvi_date1=round(ndvi1 + random.uniform(-0.05, 0.05), 3),
                ndvi_date2=round(ndvi2 + random.uniform(-0.1, 0.05), 3),
                change=round(random.uniform(-0.15, 0.05), 3),
                change_percent=round(random.uniform(-20, 10), 1),
                trend=(
                    TrendDirection.DECLINING
                    if random.random() > 0.5
                    else TrendDirection.STABLE
                ),
            ),
            ZoneChange(
                zone="center",
                zone_name_ar="الوسط",
                ndvi_date1=round(ndvi1, 3),
                ndvi_date2=round(ndvi2, 3),
                change=mean_change,
                change_percent=percent_change,
                trend=TrendDirection.STABLE,
            ),
        ]

    return {
        "field_id": field_id,
        "date1": date1,
        "date2": date2,
        "days_between": days_between,
        "change": change_data,
        "zones": [z.model_dump() for z in zones] if zones else None,
    }


# ============== Seasonal Analysis ==============


def analyze_seasonal(field_id: str, year: int) -> dict:
    """تحليل موسمي"""
    seasons = [
        SeasonalStats(
            season="winter",
            season_ar="الشتاء",
            months=[12, 1, 2],
            ndvi_mean=round(random.uniform(0.3, 0.5), 3),
            ndvi_max=round(random.uniform(0.5, 0.6), 3),
            ndvi_min=round(random.uniform(0.2, 0.3), 3),
            observations_count=random.randint(15, 25),
        ),
        SeasonalStats(
            season="spring",
            season_ar="الربيع",
            months=[3, 4, 5],
            ndvi_mean=round(random.uniform(0.5, 0.7), 3),
            ndvi_max=round(random.uniform(0.7, 0.85), 3),
            ndvi_min=round(random.uniform(0.4, 0.5), 3),
            observations_count=random.randint(15, 25),
        ),
        SeasonalStats(
            season="summer",
            season_ar="الصيف",
            months=[6, 7, 8],
            ndvi_mean=round(random.uniform(0.6, 0.8), 3),
            ndvi_max=round(random.uniform(0.8, 0.9), 3),
            ndvi_min=round(random.uniform(0.5, 0.6), 3),
            observations_count=random.randint(18, 28),
        ),
        SeasonalStats(
            season="fall",
            season_ar="الخريف",
            months=[9, 10, 11],
            ndvi_mean=round(random.uniform(0.4, 0.6), 3),
            ndvi_max=round(random.uniform(0.6, 0.75), 3),
            ndvi_min=round(random.uniform(0.3, 0.4), 3),
            observations_count=random.randint(15, 25),
        ),
    ]

    # حساب المتوسط السنوي
    annual_mean = sum(s.ndvi_mean for s in seasons) / len(seasons)

    # الذروة والقاع
    peak_season = max(seasons, key=lambda s: s.ndvi_mean)
    trough_season = min(seasons, key=lambda s: s.ndvi_mean)

    return {
        "field_id": field_id,
        "year": year,
        "seasons": [s.model_dump() for s in seasons],
        "peak_month": peak_season.months[1],  # منتصف الموسم
        "trough_month": trough_season.months[1],
        "annual_mean": round(annual_mean, 3),
    }


# ============== Anomaly Detection ==============


def detect_anomaly(field_id: str, date: str, current_ndvi: float = None) -> dict:
    """كشف الشذوذ"""
    if current_ndvi is None:
        current_ndvi = random.uniform(0.3, 0.8)

    # محاكاة القيم التاريخية
    historical_mean = random.uniform(0.5, 0.7)
    historical_std = random.uniform(0.05, 0.1)

    z_score = (
        (current_ndvi - historical_mean) / historical_std if historical_std > 0 else 0
    )
    is_anomaly = abs(z_score) > 2.0

    anomaly_type = None
    severity = None

    if is_anomaly:
        if z_score < 0:
            anomaly_type = "negative"
            severity = "high" if abs(z_score) > 3 else "medium"
        else:
            anomaly_type = "positive"
            severity = "high" if abs(z_score) > 3 else "medium"

    return {
        "field_id": field_id,
        "date": date,
        "current_ndvi": round(current_ndvi, 3),
        "historical_mean": round(historical_mean, 3),
        "historical_std": round(historical_std, 3),
        "z_score": round(z_score, 2),
        "is_anomaly": is_anomaly,
        "anomaly_type": anomaly_type,
        "severity": severity,
    }


# ============== Compositing ==============


def create_composite(
    field_id: str,
    year: int,
    month: int,
    method: CompositeMethod,
    source: SatelliteSource,
) -> dict:
    """إنشاء مركب شهري"""
    composite_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()

    # محاكاة الإحصائيات
    base_ndvi = random.uniform(0.5, 0.75)
    variation = random.uniform(0.1, 0.15)

    statistics = NDVIStatistics(
        mean=round(base_ndvi, 3),
        median=round(base_ndvi + random.uniform(-0.02, 0.02), 3),
        std=round(variation / 3, 3),
        min=round(base_ndvi - variation, 3),
        max=round(base_ndvi + variation, 3),
    )

    bucket = os.getenv("S3_BUCKET", "sahool-ndvi-data")
    date_str = f"{year}-{month:02d}"

    files = FileUrls(
        geotiff=f"s3://{bucket}/composites/{field_id}/{date_str}_{method.value}.tif",
        png=f"s3://{bucket}/composites/{field_id}/{date_str}_{method.value}.png",
        thumbnail=f"s3://{bucket}/composites/{field_id}/{date_str}_{method.value}_thumb.png",
    )

    composite = {
        "composite_id": composite_id,
        "field_id": field_id,
        "year": year,
        "month": month,
        "method": method.value,
        "source": source.value,
        "statistics": statistics.model_dump(),
        "images_used": random.randint(4, 8),
        "files": files.model_dump(),
        "created_at": now,
    }

    _composites[composite_id] = composite
    return composite


def get_composites(field_id: str, year: int = None) -> List[dict]:
    """جلب المركبات"""
    composites = [c for c in _composites.values() if c["field_id"] == field_id]

    if year:
        composites = [c for c in composites if c["year"] == year]

    return sorted(composites, key=lambda x: (x["year"], x["month"]), reverse=True)
