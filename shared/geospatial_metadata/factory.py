"""
ISO 19115 Metadata Factory Functions | دوال إنشاء البيانات الوصفية

Convenience factory functions to create ISO 19115-compliant metadata
records for common SAHOOL geospatial data types: fields, NDVI,
terrain, satellite imagery, and IoT sensors.

Author: SAHOOL Platform
Version: 16.0.0
"""

from __future__ import annotations

from datetime import UTC, datetime

from .iso19115 import (
    CI_Citation,
    DataQualityReport,
    DQ_Scope,
    EX_Extent,
    EX_GeographicBoundingBox,
    EX_TemporalExtent,
    GeospatialMetadataRecord,
    LI_Lineage,
    LI_ProcessStep,
    LI_Source,
    MD_DataIdentification,
    MD_Keywords,
    MD_LegalConstraints,
    MD_MaintenanceFrequencyCode,
    MD_MaintenanceInformation,
    MD_Metadata,
    MD_ReferenceSystem,
    MD_Resolution,
    MD_ScopeCode,
    MD_SpatialRepresentationType,
    MD_TopicCategory,
)


def _validate_bbox(bbox: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    """
    Validate bounding box coordinates.

    IMPORTANT: bbox order is (west_lon, south_lat, east_lon, north_lat)
    following OGC/GeoJSON convention (longitude first, then latitude).
    This matches PostGIS ST_MakeEnvelope(xmin, ymin, xmax, ymax) order.

    NOT the (lat, lng) order used by some mapping libraries.

    Args:
        bbox: (west_longitude, south_latitude, east_longitude, north_latitude)

    Returns:
        Validated bbox tuple

    Raises:
        ValueError: If coordinates are out of range or inverted
    """
    west, south, east, north = bbox
    if not (-180 <= west <= 180):
        raise ValueError(f"west_longitude {west} out of range [-180, 180]")
    if not (-180 <= east <= 180):
        raise ValueError(f"east_longitude {east} out of range [-180, 180]")
    if not (-90 <= south <= 90):
        raise ValueError(f"south_latitude {south} out of range [-90, 90]")
    if not (-90 <= north <= 90):
        raise ValueError(f"north_latitude {north} out of range [-90, 90]")
    if east < west:
        raise ValueError(f"east_longitude ({east}) must be >= west_longitude ({west})")
    if north < south:
        raise ValueError(f"north_latitude ({north}) must be >= south_latitude ({south})")
    return bbox


def create_field_metadata(
    *,
    field_id: str,
    tenant_id: str,
    title: str,
    title_ar: str | None = None,
    abstract: str,
    abstract_ar: str | None = None,
    bbox: tuple[float, float, float, float],
    crs: str = "EPSG:4326",
    area_hectares: float | None = None,
    accuracy_m: float | None = None,
    capture_method: str = "GPS survey",
    created_by: str | None = None,
) -> GeospatialMetadataRecord:
    """
    Create ISO 19115 metadata for a field boundary.
    إنشاء بيانات وصفية لحدود الحقل

    Args:
        field_id: Field identifier
        tenant_id: Tenant identifier
        title: Field name/title
        title_ar: Arabic title
        abstract: Brief description
        abstract_ar: Arabic description
        bbox: (west_lon, south_lat, east_lon, north_lat)
        crs: Coordinate reference system code
        area_hectares: Field area
        accuracy_m: GPS accuracy in meters
        capture_method: How boundary was captured
        created_by: User who created
    """
    _validate_bbox(bbox)
    west, south, east, north = bbox

    quality = DataQualityReport(scope=DQ_Scope(level=MD_ScopeCode.FEATURE))
    if accuracy_m is not None:
        quality.add_positional_accuracy(accuracy_m, method=capture_method)
    quality.add_conformance("GeoJSON RFC 7946", is_conformant=True)
    quality.add_conformance(
        "ISO 19115-1:2014",
        is_conformant=True,
        explanation="SAHOOL platform geospatial metadata compliance",
    )

    lineage = LI_Lineage(
        statement=f"Field boundary captured via {capture_method}",
        statement_ar=f"تم التقاط حدود الحقل عبر {capture_method}",
        source=[
            LI_Source(
                description=f"GPS survey data for field {field_id}",
                description_ar=f"بيانات مسح GPS للحقل {field_id}",
                source_reference_system=MD_ReferenceSystem(code=crs),
            )
        ],
        process_step=[
            LI_ProcessStep(
                description="Field boundary coordinates captured and validated",
                description_ar="تم التقاط إحداثيات حدود الحقل والتحقق منها",
                software_reference="SAHOOL Field App v16.0.0",
                algorithm="Polygon simplification with Douglas-Peucker",
            )
        ],
    )

    keywords = [
        MD_Keywords(
            keyword=["field boundary", "agriculture", "geospatial"],
            keyword_ar=["حدود الحقل", "زراعة", "جغرافي مكاني"],
            type="theme",
            thesaurus_name="SAHOOL Agricultural Vocabulary",
        ),
        MD_Keywords(
            keyword=["Middle East", "Arabian Peninsula"],
            keyword_ar=["الشرق الأوسط", "شبه الجزيرة العربية"],
            type="place",
        ),
    ]

    level_detail = f"{area_hectares:.1f} hectares" if area_hectares else "field-level"

    metadata = MD_Metadata(
        hierarchy_level=MD_ScopeCode.FEATURE,
        identification_info=MD_DataIdentification(
            citation=CI_Citation(
                title=title,
                title_ar=title_ar,
                date_type="creation",
                presentation_form="mapDigital",
            ),
            abstract=abstract,
            abstract_ar=abstract_ar,
            purpose="Agricultural field boundary definition for precision farming",
            purpose_ar="تحديد حدود الحقل الزراعي للزراعة الدقيقة",
            topic_category=[MD_TopicCategory.FARMING, MD_TopicCategory.BOUNDARIES],
            descriptive_keywords=keywords,
            spatial_representation_type=[MD_SpatialRepresentationType.VECTOR],
            spatial_resolution=[
                MD_Resolution(
                    distance_m=accuracy_m or 5.0,
                    level_of_detail=level_detail,
                    level_of_detail_ar=f"{area_hectares:.1f} هكتار" if area_hectares else "مستوى الحقل",
                )
            ],
            extent=[
                EX_Extent(
                    description=f"Field {field_id} boundary extent",
                    description_ar=f"نطاق حدود الحقل {field_id}",
                    geographic_element=EX_GeographicBoundingBox(
                        west_bound_longitude=west,
                        east_bound_longitude=east,
                        south_bound_latitude=south,
                        north_bound_latitude=north,
                    ),
                )
            ],
            resource_constraints=[MD_LegalConstraints()],
            resource_maintenance=MD_MaintenanceInformation(
                maintenance_frequency=MD_MaintenanceFrequencyCode.AS_NEEDED,
                maintenance_note="Updated when field boundary is re-surveyed",
                maintenance_note_ar="يُحدَّث عند إعادة مسح حدود الحقل",
            ),
            tenant_id=tenant_id,
            domain="field",
        ),
        reference_system_info=[MD_ReferenceSystem(code=crs)],
        data_quality_info=quality,
        lineage=lineage,
    )

    return GeospatialMetadataRecord(
        tenant_id=tenant_id,
        domain="field",
        resource_id=field_id,
        resource_type="field_boundary",
        metadata=metadata,
        created_by=created_by,
        tags=["field", "boundary", "geospatial"],
    )


def create_ndvi_metadata(
    *,
    field_id: str,
    tenant_id: str,
    bbox: tuple[float, float, float, float],
    acquisition_date: datetime,
    cloud_coverage_pct: float = 0.0,
    mean_ndvi: float | None = None,
    data_source: str = "Sentinel-2",
    resolution_m: float = 10.0,
    created_by: str | None = None,
) -> GeospatialMetadataRecord:
    """
    Create ISO 19115 metadata for NDVI analysis results.
    إنشاء بيانات وصفية لنتائج تحليل NDVI
    """
    _validate_bbox(bbox)
    west, south, east, north = bbox

    quality = DataQualityReport(scope=DQ_Scope(level=MD_ScopeCode.DATASET))
    quality.add_completeness(100.0 - cloud_coverage_pct, name="Cloud-free pixel coverage")
    quality.add_thematic_accuracy(
        85.0,
        name="NDVI classification accuracy",
    )
    quality.add_conformance(
        "Copernicus Sentinel-2 L2A",
        is_conformant=True,
        explanation="Atmospherically corrected surface reflectance",
    )

    lineage = LI_Lineage(
        statement=f"NDVI computed from {data_source} imagery for field {field_id}",
        statement_ar=f"تم حساب NDVI من صور {data_source} للحقل {field_id}",
        source=[
            LI_Source(
                description=f"{data_source} Level-2A surface reflectance imagery",
                description_ar=f"صور انعكاس سطحي من {data_source} المستوى 2A",
                source_citation=CI_Citation(
                    title=f"{data_source} Satellite Imagery",
                    date=acquisition_date,
                    date_type="creation",
                ),
                source_spatial_resolution=MD_Resolution(distance_m=resolution_m),
            )
        ],
        process_step=[
            LI_ProcessStep(
                description="Atmospheric correction (Sen2Cor L2A)",
                description_ar="تصحيح جوي (Sen2Cor L2A)",
                software_reference="Sen2Cor 2.11",
                algorithm="Scene Classification + Atmospheric Correction",
            ),
            LI_ProcessStep(
                description="NDVI calculation: (NIR - Red) / (NIR + Red) using B8 and B4",
                description_ar="حساب NDVI: (قريب تحت أحمر - أحمر) / (قريب تحت أحمر + أحمر)",
                software_reference="SAHOOL Vegetation Analysis Service v16.0.0",
                algorithm="Normalized Difference Vegetation Index",
                parameters={"nir_band": "B8", "red_band": "B4"},
            ),
            LI_ProcessStep(
                description="Field boundary clipping and zonal statistics",
                description_ar="قص حدود الحقل والإحصائيات المنطقية",
                software_reference="PostGIS 3.4 / rasterio",
            ),
        ],
    )

    abstract = (
        f"NDVI vegetation analysis from {data_source} imagery. "
        f"Resolution: {resolution_m}m. Cloud coverage: {cloud_coverage_pct:.1f}%."
    )
    if mean_ndvi is not None:
        abstract += f" Mean NDVI: {mean_ndvi:.3f}."

    metadata = MD_Metadata(
        hierarchy_level=MD_ScopeCode.DATASET,
        identification_info=MD_DataIdentification(
            citation=CI_Citation(
                title=f"NDVI Analysis - Field {field_id}",
                title_ar=f"تحليل NDVI - الحقل {field_id}",
                date=acquisition_date,
                date_type="creation",
                presentation_form="imageDigital",
            ),
            abstract=abstract,
            abstract_ar=f"تحليل مؤشر الغطاء النباتي من صور {data_source}. الدقة: {resolution_m} متر",
            topic_category=[
                MD_TopicCategory.FARMING,
                MD_TopicCategory.IMAGERY_BASE_MAPS,
            ],
            descriptive_keywords=[
                MD_Keywords(
                    keyword=["NDVI", "vegetation index", "remote sensing", "crop health"],
                    keyword_ar=["NDVI", "مؤشر الغطاء النباتي", "استشعار عن بعد", "صحة المحصول"],
                    type="theme",
                ),
            ],
            spatial_representation_type=[MD_SpatialRepresentationType.GRID],
            spatial_resolution=[
                MD_Resolution(
                    distance_m=resolution_m,
                    level_of_detail=f"{resolution_m}m ground resolution",
                    level_of_detail_ar=f"دقة أرضية {resolution_m} متر",
                )
            ],
            extent=[
                EX_Extent(
                    geographic_element=EX_GeographicBoundingBox(
                        west_bound_longitude=west,
                        east_bound_longitude=east,
                        south_bound_latitude=south,
                        north_bound_latitude=north,
                    ),
                    temporal_element=EX_TemporalExtent(
                        begin_position=acquisition_date,
                        end_position=acquisition_date,
                    ),
                )
            ],
            resource_constraints=[MD_LegalConstraints()],
            resource_maintenance=MD_MaintenanceInformation(
                maintenance_frequency=MD_MaintenanceFrequencyCode.FORTNIGHTLY,
                maintenance_note="Updated with each Sentinel-2 revisit cycle (5-day)",
                maintenance_note_ar="يُحدَّث مع كل دورة مراجعة Sentinel-2 (5 أيام)",
            ),
            tenant_id=tenant_id,
            domain="satellite",
        ),
        reference_system_info=[MD_ReferenceSystem.wgs84()],
        data_quality_info=quality,
        lineage=lineage,
    )

    return GeospatialMetadataRecord(
        tenant_id=tenant_id,
        domain="ndvi",
        resource_id=field_id,
        resource_type="ndvi_reading",
        metadata=metadata,
        created_by=created_by,
        tags=["ndvi", "satellite", "vegetation", "crop-health"],
    )


def create_terrain_metadata(
    *,
    field_id: str,
    tenant_id: str,
    bbox: tuple[float, float, float, float],
    dem_source: str = "SRTM",
    resolution_m: float = 30.0,
    elevation_min_m: float | None = None,
    elevation_max_m: float | None = None,
    analysis_types: list[str] | None = None,
    created_by: str | None = None,
) -> GeospatialMetadataRecord:
    """
    Create ISO 19115 metadata for terrain/DEM analysis.
    إنشاء بيانات وصفية لتحليل التضاريس/نموذج الارتفاعات الرقمي
    """
    _validate_bbox(bbox)
    west, south, east, north = bbox
    analysis = analysis_types or ["slope", "aspect", "curvature"]

    quality = DataQualityReport(scope=DQ_Scope(level=MD_ScopeCode.DATASET))
    quality.add_positional_accuracy(resolution_m, method="DEM grid resolution")
    if elevation_min_m is not None and elevation_max_m is not None:
        quality.add_completeness(100.0, name="DEM coverage completeness")

    source_desc = {
        "SRTM": "NASA Shuttle Radar Topography Mission",
        "ASTER": "ASTER Global DEM v3",
        "ALOS": "ALOS PALSAR DEM",
        "LiDAR": "Airborne LiDAR survey",
    }

    lineage = LI_Lineage(
        statement=f"Terrain analysis derived from {dem_source} DEM at {resolution_m}m resolution",
        statement_ar=f"تحليل تضاريس مشتق من {dem_source} بدقة {resolution_m} متر",
        source=[
            LI_Source(
                description=source_desc.get(dem_source, dem_source),
                source_spatial_resolution=MD_Resolution(distance_m=resolution_m),
            )
        ],
        process_step=[
            LI_ProcessStep(
                description=f"DEM acquisition from {dem_source}",
                description_ar=f"الحصول على نموذج الارتفاعات من {dem_source}",
            ),
            LI_ProcessStep(
                description=f"Terrain analysis: {', '.join(analysis)}",
                description_ar=f"تحليل التضاريس: {', '.join(analysis)}",
                software_reference="SAHOOL Terrain Core Service v16.0.0",
                algorithm="GDAL DEM processing + Horn's method for slope",
            ),
        ],
    )

    metadata = MD_Metadata(
        hierarchy_level=MD_ScopeCode.DATASET,
        identification_info=MD_DataIdentification(
            citation=CI_Citation(
                title=f"Terrain Analysis - Field {field_id}",
                title_ar=f"تحليل التضاريس - الحقل {field_id}",
                presentation_form="mapDigital",
            ),
            abstract=f"Terrain analysis from {dem_source} DEM at {resolution_m}m. Includes: {', '.join(analysis)}.",
            abstract_ar=f"تحليل تضاريس من {dem_source} بدقة {resolution_m}م",
            topic_category=[
                MD_TopicCategory.ELEVATION,
                MD_TopicCategory.GEOSCIENTIFIC_INFORMATION,
            ],
            descriptive_keywords=[
                MD_Keywords(
                    keyword=["terrain", "DEM", "slope", "elevation", "topography"],
                    keyword_ar=["تضاريس", "نموذج ارتفاعات", "ميل", "ارتفاع", "طبوغرافيا"],
                    type="theme",
                ),
            ],
            spatial_representation_type=[MD_SpatialRepresentationType.GRID],
            spatial_resolution=[MD_Resolution(distance_m=resolution_m)],
            extent=[
                EX_Extent(
                    geographic_element=EX_GeographicBoundingBox(
                        west_bound_longitude=west,
                        east_bound_longitude=east,
                        south_bound_latitude=south,
                        north_bound_latitude=north,
                    ),
                    vertical_min_m=elevation_min_m,
                    vertical_max_m=elevation_max_m,
                )
            ],
            resource_constraints=[MD_LegalConstraints()],
            tenant_id=tenant_id,
            domain="terrain",
        ),
        reference_system_info=[
            MD_ReferenceSystem.wgs84(),
            MD_ReferenceSystem.utm_zone_38n(),
        ],
        data_quality_info=quality,
        lineage=lineage,
    )

    return GeospatialMetadataRecord(
        tenant_id=tenant_id,
        domain="terrain",
        resource_id=field_id,
        resource_type="dem_analysis",
        metadata=metadata,
        created_by=created_by,
        tags=["terrain", "dem", "elevation", "slope"],
    )


def create_satellite_metadata(
    *,
    scene_id: str,
    tenant_id: str,
    bbox: tuple[float, float, float, float],
    satellite: str = "Sentinel-2",
    acquisition_date: datetime,
    cloud_coverage_pct: float = 0.0,
    bands: list[str] | None = None,
    resolution_m: float = 10.0,
    processing_level: str = "L2A",
    created_by: str | None = None,
) -> GeospatialMetadataRecord:
    """
    Create ISO 19115 metadata for satellite imagery.
    إنشاء بيانات وصفية لصور الأقمار الصناعية
    """
    _validate_bbox(bbox)
    west, south, east, north = bbox
    bands = bands or ["B2", "B3", "B4", "B8"]

    quality = DataQualityReport(scope=DQ_Scope(level=MD_ScopeCode.DATASET))
    quality.add_completeness(100.0 - cloud_coverage_pct, name="Cloud-free area coverage")
    quality.add_positional_accuracy(resolution_m, method="Satellite GSD")

    lineage = LI_Lineage(
        statement=f"{satellite} {processing_level} imagery acquired {acquisition_date.strftime('%Y-%m-%d')}",
        statement_ar=f"صور {satellite} مستوى {processing_level} بتاريخ {acquisition_date.strftime('%Y-%m-%d')}",
        source=[
            LI_Source(
                description=f"{satellite} multispectral imagery",
                description_ar=f"صور متعددة الأطياف من {satellite}",
                source_citation=CI_Citation(
                    title=f"{satellite} Scene {scene_id}",
                    date=acquisition_date,
                    date_type="creation",
                ),
            )
        ],
    )

    metadata = MD_Metadata(
        hierarchy_level=MD_ScopeCode.DATASET,
        identification_info=MD_DataIdentification(
            citation=CI_Citation(
                title=f"{satellite} Imagery - {scene_id}",
                title_ar=f"صورة {satellite} - {scene_id}",
                date=acquisition_date,
                date_type="creation",
                presentation_form="imageDigital",
            ),
            abstract=(
                f"{satellite} {processing_level} multispectral imagery. "
                f"Bands: {', '.join(bands)}. Resolution: {resolution_m}m. "
                f"Cloud coverage: {cloud_coverage_pct:.1f}%."
            ),
            abstract_ar=f"صور {satellite} متعددة الأطياف. الدقة: {resolution_m} متر",
            topic_category=[MD_TopicCategory.IMAGERY_BASE_MAPS],
            descriptive_keywords=[
                MD_Keywords(
                    keyword=["satellite imagery", satellite, "remote sensing", "multispectral"],
                    keyword_ar=["صور أقمار صناعية", satellite, "استشعار عن بعد"],
                    type="theme",
                ),
            ],
            spatial_representation_type=[MD_SpatialRepresentationType.GRID],
            spatial_resolution=[MD_Resolution(distance_m=resolution_m)],
            extent=[
                EX_Extent(
                    geographic_element=EX_GeographicBoundingBox(
                        west_bound_longitude=west,
                        east_bound_longitude=east,
                        south_bound_latitude=south,
                        north_bound_latitude=north,
                    ),
                    temporal_element=EX_TemporalExtent(
                        begin_position=acquisition_date,
                        end_position=acquisition_date,
                    ),
                )
            ],
            resource_constraints=[MD_LegalConstraints()],
            tenant_id=tenant_id,
            domain="satellite",
        ),
        data_quality_info=quality,
        lineage=lineage,
    )

    return GeospatialMetadataRecord(
        tenant_id=tenant_id,
        domain="satellite",
        resource_id=scene_id,
        resource_type="satellite_image",
        metadata=metadata,
        created_by=created_by,
        tags=["satellite", satellite.lower(), "imagery"],
    )


def create_iot_sensor_metadata(
    *,
    device_id: str,
    sensor_id: str,
    tenant_id: str,
    location: tuple[float, float],
    sensor_type: str = "soil_moisture",
    accuracy_pct: float | None = None,
    measurement_unit: str = "%",
    installation_date: datetime | None = None,
    created_by: str | None = None,
) -> GeospatialMetadataRecord:
    """
    Create ISO 19115 metadata for IoT sensor location/data.
    إنشاء بيانات وصفية لموقع/بيانات أجهزة الاستشعار
    """
    lon, lat = location
    buffer = 0.001  # ~100m buffer around sensor

    quality = DataQualityReport(scope=DQ_Scope(level=MD_ScopeCode.FEATURE))
    quality.add_positional_accuracy(5.0, method="GPS sensor placement")
    if accuracy_pct is not None:
        quality.add_thematic_accuracy(accuracy_pct, name="Sensor measurement accuracy")

    sensor_types_ar = {
        "soil_moisture": "رطوبة التربة",
        "temperature": "درجة الحرارة",
        "humidity": "الرطوبة",
        "rainfall": "هطول الأمطار",
        "wind_speed": "سرعة الرياح",
        "soil_ec": "الموصلية الكهربائية للتربة",
        "soil_ph": "حموضة التربة",
    }

    metadata = MD_Metadata(
        hierarchy_level=MD_ScopeCode.FEATURE,
        identification_info=MD_DataIdentification(
            citation=CI_Citation(
                title=f"IoT Sensor {sensor_id} ({sensor_type})",
                title_ar=f"مستشعر {sensor_id} ({sensor_types_ar.get(sensor_type, sensor_type)})",
                presentation_form="tableDigital",
            ),
            abstract=f"IoT {sensor_type} sensor on device {device_id}. Unit: {measurement_unit}.",
            abstract_ar=f"مستشعر {sensor_types_ar.get(sensor_type, sensor_type)} على جهاز {device_id}",
            topic_category=[MD_TopicCategory.FARMING, MD_TopicCategory.GEOSCIENTIFIC_INFORMATION],
            descriptive_keywords=[
                MD_Keywords(
                    keyword=["IoT", "sensor", sensor_type, "precision agriculture"],
                    keyword_ar=["إنترنت الأشياء", "مستشعر", sensor_types_ar.get(sensor_type, sensor_type)],
                    type="theme",
                ),
            ],
            spatial_representation_type=[MD_SpatialRepresentationType.TEXT_TABLE],
            extent=[
                EX_Extent(
                    geographic_element=EX_GeographicBoundingBox(
                        west_bound_longitude=lon - buffer,
                        east_bound_longitude=lon + buffer,
                        south_bound_latitude=lat - buffer,
                        north_bound_latitude=lat + buffer,
                    ),
                    temporal_element=EX_TemporalExtent(
                        begin_position=installation_date or datetime.now(UTC),
                    ),
                )
            ],
            resource_constraints=[MD_LegalConstraints()],
            resource_maintenance=MD_MaintenanceInformation(
                maintenance_frequency=MD_MaintenanceFrequencyCode.CONTINUAL,
                maintenance_note="Real-time sensor data stream",
                maintenance_note_ar="تدفق بيانات المستشعر في الوقت الفعلي",
            ),
            tenant_id=tenant_id,
            domain="iot",
        ),
        data_quality_info=quality,
    )

    return GeospatialMetadataRecord(
        tenant_id=tenant_id,
        domain="iot",
        resource_id=sensor_id,
        resource_type="sensor_data",
        metadata=metadata,
        created_by=created_by,
        tags=["iot", "sensor", sensor_type],
    )
