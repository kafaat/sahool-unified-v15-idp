"""
ISO 19115:2014 Geospatial Metadata Models | نماذج البيانات الوصفية الجغرافية

Complete implementation of ISO 19115:2014 Geographic Information - Metadata
for the SAHOOL agricultural platform. Covers all mandatory and conditional
metadata elements per the standard.

تنفيذ كامل لمعيار ISO 19115:2014 للمعلومات الجغرافية - البيانات الوصفية
لمنصة سهول الزراعية.

References:
- ISO 19115-1:2014 Geographic information — Metadata — Part 1: Fundamentals
- ISO 19115-2:2019 Extensions for imagery and gridded data
- ISO 19157:2013 Geographic information — Data quality

Note: Class names follow ISO 19115 naming conventions (e.g., CI_Citation,
MD_Metadata, DQ_Element) per the standard's UML class diagram.
These intentionally use underscores in class names (ruff N801 suppressed).

Author: SAHOOL Platform
Version: 16.0.0
"""
# ruff: noqa: N801

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

# =============================================================================
# ISO 19115 Code Lists (Enumerations)
# =============================================================================


class CI_RoleCode(StrEnum):
    """
    ISO 19115 CI_RoleCode - Role of the responsible party.
    دور الجهة المسؤولة
    """

    RESOURCE_PROVIDER = "resourceProvider"
    CUSTODIAN = "custodian"
    OWNER = "owner"
    USER = "user"
    DISTRIBUTOR = "distributor"
    ORIGINATOR = "originator"
    POINT_OF_CONTACT = "pointOfContact"
    PRINCIPAL_INVESTIGATOR = "principalInvestigator"
    PROCESSOR = "processor"
    PUBLISHER = "publisher"
    AUTHOR = "author"


class MD_ScopeCode(StrEnum):
    """
    ISO 19115 MD_ScopeCode - Scope of the metadata.
    نطاق البيانات الوصفية
    """

    DATASET = "dataset"
    SERIES = "series"
    SERVICE = "service"
    FEATURE = "feature"
    FEATURE_TYPE = "featureType"
    FIELD_SESSION = "fieldSession"
    SOFTWARE = "software"
    MODEL = "model"
    TILE = "tile"
    COLLECTION_HARDWARE = "collectionHardware"


class MD_TopicCategory(StrEnum):
    """
    ISO 19115 MD_TopicCategory - High-level theme classification.
    تصنيف الموضوع عالي المستوى
    """

    FARMING = "farming"
    BIOTA = "biota"
    BOUNDARIES = "boundaries"
    CLIMATOLOGY_METEOROLOGY = "climatologyMeteorologyAtmosphere"
    ENVIRONMENT = "environment"
    GEOSCIENTIFIC_INFORMATION = "geoscientificInformation"
    IMAGERY_BASE_MAPS = "imageryBaseMapsEarthCover"
    INLAND_WATERS = "inlandWaters"
    INTELLIGENCE_MILITARY = "intelligenceMilitary"
    LOCATION = "location"
    PLANNING_CADASTRE = "planningCadastre"
    ELEVATION = "elevation"
    HEALTH = "health"
    STRUCTURE = "structure"


class MD_SpatialRepresentationType(StrEnum):
    """
    ISO 19115 MD_SpatialRepresentationTypeCode
    نوع التمثيل المكاني
    """

    VECTOR = "vector"
    GRID = "grid"
    TEXT_TABLE = "textTable"
    TIN = "tin"
    STEREO_MODEL = "stereoModel"
    VIDEO = "video"


class MD_RestrictionCode(StrEnum):
    """
    ISO 19115 MD_RestrictionCode - Access/use constraints.
    قيود الوصول والاستخدام
    """

    COPYRIGHT = "copyright"
    PATENT = "patent"
    PATENT_PENDING = "patentPending"
    TRADEMARK = "trademark"
    LICENSE = "license"
    INTELLECTUAL_PROPERTY_RIGHTS = "intellectualPropertyRights"
    RESTRICTED = "restricted"
    OTHER_RESTRICTIONS = "otherRestrictions"


class MD_MaintenanceFrequencyCode(StrEnum):
    """
    ISO 19115 MD_MaintenanceFrequencyCode
    تردد الصيانة
    """

    CONTINUAL = "continual"
    DAILY = "daily"
    WEEKLY = "weekly"
    FORTNIGHTLY = "fortnightly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    BIANNUALLY = "biannually"
    ANNUALLY = "annually"
    AS_NEEDED = "asNeeded"
    IRREGULAR = "irregular"
    NOT_PLANNED = "notPlanned"
    UNKNOWN = "unknown"


class MD_ProgressCode(StrEnum):
    """
    ISO 19115 MD_ProgressCode - Status of the dataset.
    حالة مجموعة البيانات
    """

    COMPLETED = "completed"
    HISTORICAL_ARCHIVE = "historicalArchive"
    OBSOLETE = "obsolete"
    ON_GOING = "onGoing"
    PLANNED = "planned"
    REQUIRED = "required"
    UNDER_DEVELOPMENT = "underDevelopment"


# =============================================================================
# ISO 19115 Citation & Responsible Party
# =============================================================================


class CI_OnlineResource(BaseModel):
    """
    ISO 19115 CI_OnlineResource - Online reference for the resource.
    مورد عبر الإنترنت
    """

    linkage: str = Field(..., description="URL of the online resource")
    protocol: str | None = Field(default=None, description="Protocol (HTTP, FTP, OGC:WMS)")
    name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    function: str | None = Field(default=None, description="download | information | search")


class CI_ResponsibleParty(BaseModel):
    """
    ISO 19115 CI_ResponsibleParty - Identification and contact info.
    بيانات الجهة المسؤولة

    Mandatory when creating metadata per ISO 19115 Section 6.2.
    """

    individual_name: str | None = Field(
        default=None, description="Name of the responsible individual | اسم الشخص المسؤول"
    )
    organisation_name: str = Field(
        default="KAFAAT - SAHOOL Platform",
        description="Name of the organization | اسم المنظمة",
    )
    organisation_name_ar: str = Field(
        default="كفاءات - منصة سهول",
        description="Arabic organization name | اسم المنظمة بالعربية",
    )
    position_name: str | None = Field(default=None, description="Role/position | المنصب")
    role: CI_RoleCode = Field(
        default=CI_RoleCode.POINT_OF_CONTACT,
        description="Role of the responsible party | دور الجهة",
    )
    email: str | None = Field(default=None)
    phone: str | None = Field(default=None)
    online_resource: CI_OnlineResource | None = Field(default=None)


class CI_Citation(BaseModel):
    """
    ISO 19115 CI_Citation - Standard citation information.
    معلومات الاستشهاد القياسية

    Section 6.2 of ISO 19115:2014.
    """

    title: str = Field(..., description="Dataset title | عنوان مجموعة البيانات")
    title_ar: str | None = Field(default=None, description="Arabic title | العنوان بالعربية")
    date: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Reference date | التاريخ المرجعي",
    )
    date_type: str = Field(default="creation", description="creation | publication | revision")
    edition: str | None = Field(default=None, description="Version of the resource")
    identifier: str = Field(
        default_factory=lambda: f"SAHOOL-{uuid.uuid4().hex[:12].upper()}",
        description="Unique resource identifier | المعرف الفريد",
    )
    cited_responsible_party: list[CI_ResponsibleParty] = Field(default_factory=list)
    presentation_form: str | None = Field(default=None, description="mapDigital | tableDigital | imageDigital")


# =============================================================================
# ISO 19115 Extent Information
# =============================================================================


class EX_GeographicBoundingBox(BaseModel):
    """
    ISO 19115 EX_GeographicBoundingBox - Geographic extent.
    الحدود الجغرافية

    All coordinates are in decimal degrees (WGS84 / EPSG:4326).
    """

    west_bound_longitude: float = Field(..., ge=-180, le=180, description="Western-most longitude | خط الطول الغربي")
    east_bound_longitude: float = Field(..., ge=-180, le=180, description="Eastern-most longitude | خط الطول الشرقي")
    south_bound_latitude: float = Field(..., ge=-90, le=90, description="Southern-most latitude | خط العرض الجنوبي")
    north_bound_latitude: float = Field(..., ge=-90, le=90, description="Northern-most latitude | خط العرض الشمالي")

    @field_validator("east_bound_longitude")
    @classmethod
    def east_gt_west(cls, v: float, info: Any) -> float:
        # Guard `info.data is None` — Pydantic v2 passes None when the
        # validator fires before sibling fields are populated (notably
        # on `model_validate_json()` round-trips). Without this guard
        # `test_field_metadata_json_roundtrip` crashes with
        # `AttributeError: 'NoneType' object has no attribute 'get'`.
        if info.data is None:
            return v
        west = info.data.get("west_bound_longitude")
        if west is not None and v < west:
            raise ValueError("East longitude must be >= west longitude | خط الطول الشرقي يجب أن يكون >= الغربي")
        return v

    @field_validator("north_bound_latitude")
    @classmethod
    def north_gt_south(cls, v: float, info: Any) -> float:
        if info.data is None:
            return v
        south = info.data.get("south_bound_latitude")
        if south is not None and v < south:
            raise ValueError("North latitude must be >= south latitude | خط العرض الشمالي يجب أن يكون >= الجنوبي")
        return v


class EX_TemporalExtent(BaseModel):
    """
    ISO 19115 EX_TemporalExtent - Temporal period of data.
    النطاق الزمني للبيانات
    """

    begin_position: datetime = Field(..., description="Start of temporal extent | بداية النطاق الزمني")
    end_position: datetime | None = Field(
        default=None, description="End of temporal extent (None=ongoing) | نهاية النطاق"
    )

    @field_validator("end_position")
    @classmethod
    def end_after_begin(cls, v: datetime | None, info: Any) -> datetime | None:
        if info.data is None:
            return v
        begin = info.data.get("begin_position")
        if v is not None and begin is not None and v < begin:
            raise ValueError("End position must be after begin position")
        return v


class EX_Extent(BaseModel):
    """
    ISO 19115 EX_Extent - Combined spatial and temporal extent.
    النطاق المكاني والزمني
    """

    description: str | None = Field(default=None, description="Extent description | وصف النطاق")
    description_ar: str | None = Field(default=None)
    geographic_element: EX_GeographicBoundingBox | None = Field(default=None)
    temporal_element: EX_TemporalExtent | None = Field(default=None)
    vertical_min_m: float | None = Field(
        default=None, description="Minimum elevation in meters | الارتفاع الأدنى بالمتر"
    )
    vertical_max_m: float | None = Field(
        default=None, description="Maximum elevation in meters | الارتفاع الأقصى بالمتر"
    )

    @field_validator("vertical_max_m")
    @classmethod
    def vertical_max_gte_min(cls, v: float | None, info: Any) -> float | None:
        if info.data is None:
            return v
        vmin = info.data.get("vertical_min_m")
        if v is not None and vmin is not None and v < vmin:
            raise ValueError(
                f"vertical_max_m ({v}) must be >= vertical_min_m ({vmin}) | الارتفاع الأقصى يجب أن يكون >= الأدنى"
            )
        return v


# =============================================================================
# ISO 19115 Keywords & Constraints
# =============================================================================


class MD_Keywords(BaseModel):
    """
    ISO 19115 MD_Keywords - Keywords describing the dataset.
    الكلمات المفتاحية
    """

    keyword: list[str] = Field(..., min_length=1, description="Keywords | الكلمات المفتاحية")
    keyword_ar: list[str] = Field(default_factory=list, description="Arabic keywords | الكلمات المفتاحية بالعربية")
    type: str = Field(default="theme", description="discipline | place | stratum | temporal | theme")
    thesaurus_name: str | None = Field(
        default=None,
        description="Name of the keyword thesaurus | اسم القاموس المرجعي",
    )


class MD_Constraints(BaseModel):
    """
    ISO 19115 MD_Constraints - General metadata constraints.
    القيود العامة
    """

    use_limitation: list[str] = Field(default_factory=list, description="Use limitations | حدود الاستخدام")
    use_limitation_ar: list[str] = Field(default_factory=list)


class MD_LegalConstraints(MD_Constraints):
    """
    ISO 19115 MD_LegalConstraints - Legal restrictions.
    القيود القانونية
    """

    access_constraints: list[MD_RestrictionCode] = Field(
        default_factory=lambda: [MD_RestrictionCode.RESTRICTED],
        description="Access restrictions | قيود الوصول",
    )
    use_constraints: list[MD_RestrictionCode] = Field(
        default_factory=lambda: [MD_RestrictionCode.INTELLECTUAL_PROPERTY_RIGHTS],
        description="Use restrictions | قيود الاستخدام",
    )
    other_constraints: list[str] = Field(
        default_factory=lambda: [
            "Data is proprietary to KAFAAT/SAHOOL platform and tenant organizations",
            "البيانات ملكية خاصة لمنصة كفاءات/سهول والمنظمات المستأجرة",
        ]
    )


# =============================================================================
# ISO 19115 Distribution Information
# =============================================================================


class MD_DistributionFormat(BaseModel):
    """
    ISO 19115 MD_Format - Distribution format.
    تنسيق التوزيع
    """

    name: str = Field(..., description="Format name | اسم التنسيق")
    version: str | None = Field(default=None, description="Format version | إصدار التنسيق")
    specification: str | None = Field(default=None)


class MD_DigitalTransferOptions(BaseModel):
    """
    ISO 19115 MD_DigitalTransferOptions
    خيارات النقل الرقمي
    """

    units_of_distribution: str | None = Field(default=None)
    transfer_size_mb: float | None = Field(default=None, ge=0)
    online_resource: list[CI_OnlineResource] = Field(default_factory=list)


# Alias for backward compat
MD_TransferOptions = MD_DigitalTransferOptions


class MD_Distribution(BaseModel):
    """
    ISO 19115 MD_Distribution - Distribution information.
    معلومات التوزيع
    """

    distribution_format: list[MD_DistributionFormat] = Field(default_factory=list)
    transfer_options: list[MD_DigitalTransferOptions] = Field(default_factory=list)
    distributor: list[CI_ResponsibleParty] = Field(default_factory=list)


# =============================================================================
# ISO 19115 Reference System
# =============================================================================


class MD_ReferenceSystem(BaseModel):
    """
    ISO 19115 MD_ReferenceSystem - CRS information.
    نظام الإسناد الإحداثي

    Default is WGS 84 (EPSG:4326) - the standard for GPS and web mapping.
    """

    code: str = Field(default="EPSG:4326", description="CRS code (e.g., EPSG:4326) | رمز النظام الإحداثي")
    code_space: str = Field(default="EPSG", description="Authority (EPSG, OGC) | الجهة المرجعية")
    version: str | None = Field(default=None)
    description: str = Field(
        default="WGS 84 - World Geodetic System 1984",
        description="CRS description | وصف النظام الإحداثي",
    )
    description_ar: str = Field(
        default="النظام الجيوديسي العالمي 1984",
    )

    # Common CRS presets
    @classmethod
    def wgs84(cls) -> MD_ReferenceSystem:
        """WGS 84 (EPSG:4326) - GPS coordinates."""
        return cls(
            code="EPSG:4326",
            description="WGS 84 - World Geodetic System 1984",
            description_ar="النظام الجيوديسي العالمي 1984",
        )

    @classmethod
    def utm_zone_38n(cls) -> MD_ReferenceSystem:
        """UTM Zone 38N (EPSG:32638) - Middle East / Arabian Peninsula."""
        return cls(
            code="EPSG:32638",
            code_space="EPSG",
            description="WGS 84 / UTM zone 38N - Arabian Peninsula",
            description_ar="UTM المنطقة 38 شمال - شبه الجزيرة العربية",
        )

    @classmethod
    def utm_zone_39n(cls) -> MD_ReferenceSystem:
        """UTM Zone 39N (EPSG:32639) - Eastern Arabia / Yemen."""
        return cls(
            code="EPSG:32639",
            code_space="EPSG",
            description="WGS 84 / UTM zone 39N - Eastern Arabia",
            description_ar="UTM المنطقة 39 شمال - شرق الجزيرة العربية",
        )


# =============================================================================
# ISO 19115 Spatial Resolution
# =============================================================================


class MD_Resolution(BaseModel):
    """
    ISO 19115 MD_Resolution - Spatial resolution of the data.
    الدقة المكانية للبيانات
    """

    equivalent_scale: int | None = Field(
        default=None,
        description="Scale denominator (e.g., 50000 means 1:50000) | مقام المقياس",
    )
    distance_m: float | None = Field(
        default=None,
        ge=0,
        description="Ground sample distance in meters | دقة العينة الأرضية بالمتر",
    )
    level_of_detail: str | None = Field(
        default=None,
        description="Description of spatial resolution | وصف الدقة المكانية",
    )
    level_of_detail_ar: str | None = Field(default=None)


# =============================================================================
# ISO 19115 Maintenance Information
# =============================================================================


class MD_MaintenanceInformation(BaseModel):
    """
    ISO 19115 MD_MaintenanceInformation - Update frequency.
    معلومات الصيانة والتحديث
    """

    maintenance_frequency: MD_MaintenanceFrequencyCode = Field(
        default=MD_MaintenanceFrequencyCode.AS_NEEDED,
        description="Update frequency | تردد التحديث",
    )
    date_of_next_update: datetime | None = Field(default=None)
    update_scope: MD_ScopeCode | None = Field(default=None)
    maintenance_note: str | None = Field(default=None)
    maintenance_note_ar: str | None = Field(default=None)


# =============================================================================
# ISO 19115 Browse Graphic & Aggregation
# =============================================================================


class MD_BrowseGraphic(BaseModel):
    """
    ISO 19115 MD_BrowseGraphic - Thumbnail/preview reference.
    صورة مصغرة / معاينة
    """

    file_name: str = Field(..., description="Path or URL to graphic")
    file_description: str | None = Field(default=None)
    file_type: str = Field(default="image/png", description="MIME type")


class MD_AggregateInformation(BaseModel):
    """
    ISO 19115 MD_AggregateInformation - Related datasets.
    معلومات التجميع - مجموعات البيانات ذات الصلة
    """

    aggregate_dataset_name: str = Field(...)
    aggregate_dataset_identifier: str | None = Field(default=None)
    association_type: str = Field(
        default="crossReference",
        description="crossReference | largerWorkCitation | partOfSeamlessDatabase | source | stereoMate",
    )
    initiative_type: str | None = Field(default=None)


# =============================================================================
# ISO 19115 Data Identification (Section 6.5)
# =============================================================================


class MD_DataIdentification(BaseModel):
    """
    ISO 19115 MD_DataIdentification - Core identification info.
    بيانات تعريف مجموعة البيانات الأساسية

    This is the main identification section (Section 6.5) containing
    abstract, purpose, keywords, extent, and constraints.
    """

    citation: CI_Citation = Field(...)
    abstract: str = Field(..., description="Brief description of the dataset | وصف موجز لمجموعة البيانات")
    abstract_ar: str | None = Field(default=None, description="Arabic abstract | الملخص بالعربية")
    purpose: str | None = Field(default=None, description="Purpose of the dataset | الغرض من مجموعة البيانات")
    purpose_ar: str | None = Field(default=None)
    status: MD_ProgressCode = Field(
        default=MD_ProgressCode.ON_GOING,
        description="Current status | الحالة الحالية",
    )
    point_of_contact: list[CI_ResponsibleParty] = Field(default_factory=list)

    # Topic & keywords
    topic_category: list[MD_TopicCategory] = Field(
        default_factory=lambda: [MD_TopicCategory.FARMING],
        description="ISO 19115 topic categories | تصنيفات الموضوع",
    )
    descriptive_keywords: list[MD_Keywords] = Field(default_factory=list)

    # Spatial
    spatial_representation_type: list[MD_SpatialRepresentationType] = Field(
        default_factory=lambda: [MD_SpatialRepresentationType.VECTOR],
    )
    spatial_resolution: list[MD_Resolution] = Field(default_factory=list)
    language: str = Field(default="eng", description="ISO 639-2/B language code")
    supplemental_languages: list[str] = Field(
        default_factory=lambda: ["ara"],
        description="Additional languages (Arabic) | اللغات الإضافية",
    )
    character_set: str = Field(default="utf8")

    # Extent & constraints
    extent: list[EX_Extent] = Field(default_factory=list)
    resource_constraints: list[MD_LegalConstraints] = Field(default_factory=list)
    resource_maintenance: MD_MaintenanceInformation | None = Field(default=None)

    # Browse graphic
    graphic_overview: list[MD_BrowseGraphic] = Field(default_factory=list)

    # Aggregation
    aggregation_info: list[MD_AggregateInformation] = Field(default_factory=list)

    # SAHOOL-specific
    tenant_id: str | None = Field(default=None, description="SAHOOL tenant ID | معرف المستأجر")
    domain: str | None = Field(
        default=None,
        description="SAHOOL domain (field, satellite, terrain, iot) | المجال",
    )


# =============================================================================
# ISO 19157 Data Quality (linked from ISO 19115)
# =============================================================================


class DQ_Scope(BaseModel):
    """
    ISO 19157 DQ_Scope - Scope of quality evaluation.
    نطاق تقييم الجودة
    """

    level: MD_ScopeCode = Field(
        default=MD_ScopeCode.DATASET,
        description="Quality scope level | مستوى نطاق الجودة",
    )
    level_description: str | None = Field(default=None)


class DQ_QuantitativeResult(BaseModel):
    """
    ISO 19157 DQ_QuantitativeResult - Numeric quality result.
    نتيجة الجودة الكمية
    """

    value: float = Field(..., description="Quality measurement value | قيمة القياس")
    value_unit: str = Field(..., description="Unit of measure (m, %, px) | وحدة القياس")
    value_type: str = Field(default="measure", description="measure | percentage | count")


class DQ_ConformanceResult(BaseModel):
    """
    ISO 19157 DQ_ConformanceResult - Standard conformance.
    نتيجة المطابقة مع المعيار
    """

    specification: str = Field(..., description="Standard/specification name | اسم المعيار")
    explanation: str | None = Field(default=None)
    is_conformant: bool = Field(..., description="Does data conform to spec? | هل البيانات مطابقة؟")


class DQ_Element(BaseModel):
    """
    ISO 19157 DQ_Element - Individual quality element.
    عنصر جودة فردي

    Quality types per ISO 19157:
    - completeness (omission/commission)
    - logicalConsistency (conceptual/domain/format/topological)
    - positionalAccuracy (absolute/relative/gridded)
    - temporalQuality (accuracy/consistency/validity)
    - thematicAccuracy (classification/quantitative/non-quantitative)
    """

    quality_type: str = Field(
        ...,
        description="ISO 19157 quality type | نوع الجودة",
    )
    quality_type_ar: str | None = Field(default=None)
    name: str = Field(..., description="Element name | اسم العنصر")
    name_ar: str | None = Field(default=None)
    measure_description: str | None = Field(default=None)
    measure_description_ar: str | None = Field(default=None)
    evaluation_method: str | None = Field(default=None, description="How quality was assessed | طريقة التقييم")
    date_time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When quality was evaluated | تاريخ التقييم",
    )
    quantitative_result: DQ_QuantitativeResult | None = Field(default=None)
    conformance_result: DQ_ConformanceResult | None = Field(default=None)


class DataQualityReport(BaseModel):
    """
    ISO 19157 Data Quality Report - Complete quality assessment.
    تقرير جودة البيانات الكامل

    Aggregates all quality elements for a dataset, providing
    completeness, accuracy, and consistency metrics.
    """

    scope: DQ_Scope = Field(default_factory=DQ_Scope)
    report: list[DQ_Element] = Field(default_factory=list, description="Quality elements | عناصر الجودة")

    def add_positional_accuracy(
        self,
        accuracy_m: float,
        method: str = "GPS measurement",
        name: str = "Absolute positional accuracy",
    ) -> None:
        """Add positional accuracy quality element."""
        self.report.append(
            DQ_Element(
                quality_type="positionalAccuracy",
                quality_type_ar="الدقة المكانية",
                name=name,
                name_ar="الدقة المكانية المطلقة",
                evaluation_method=method,
                quantitative_result=DQ_QuantitativeResult(value=accuracy_m, value_unit="m", value_type="measure"),
            )
        )

    def add_completeness(
        self,
        completeness_pct: float,
        name: str = "Data completeness",
    ) -> None:
        """Add completeness quality element."""
        self.report.append(
            DQ_Element(
                quality_type="completeness",
                quality_type_ar="الاكتمال",
                name=name,
                name_ar="اكتمال البيانات",
                quantitative_result=DQ_QuantitativeResult(
                    value=completeness_pct, value_unit="%", value_type="percentage"
                ),
            )
        )

    def add_temporal_accuracy(
        self,
        accuracy_hours: float,
        name: str = "Temporal accuracy",
    ) -> None:
        """Add temporal accuracy quality element."""
        self.report.append(
            DQ_Element(
                quality_type="temporalQuality",
                quality_type_ar="الدقة الزمنية",
                name=name,
                name_ar="الدقة الزمنية",
                quantitative_result=DQ_QuantitativeResult(
                    value=accuracy_hours, value_unit="hours", value_type="measure"
                ),
            )
        )

    def add_thematic_accuracy(
        self,
        accuracy_pct: float,
        name: str = "Classification accuracy",
    ) -> None:
        """Add thematic accuracy quality element."""
        self.report.append(
            DQ_Element(
                quality_type="thematicAccuracy",
                quality_type_ar="الدقة الموضوعية",
                name=name,
                name_ar="دقة التصنيف",
                quantitative_result=DQ_QuantitativeResult(value=accuracy_pct, value_unit="%", value_type="percentage"),
            )
        )

    def add_logical_consistency(
        self,
        consistency_pct: float,
        name: str = "Topological consistency",
        method: str = "Automated validation",
    ) -> None:
        """Add logical consistency quality element (topology, domain, format)."""
        self.report.append(
            DQ_Element(
                quality_type="logicalConsistency",
                quality_type_ar="الاتساق المنطقي",
                name=name,
                name_ar="الاتساق الطوبولوجي",
                evaluation_method=method,
                quantitative_result=DQ_QuantitativeResult(
                    value=consistency_pct, value_unit="%", value_type="percentage"
                ),
            )
        )

    def add_conformance(
        self,
        specification: str,
        is_conformant: bool,
        explanation: str | None = None,
    ) -> None:
        """Add conformance quality element."""
        self.report.append(
            DQ_Element(
                quality_type="logicalConsistency",
                quality_type_ar="الاتساق المنطقي",
                name=f"Conformance to {specification}",
                name_ar=f"المطابقة مع {specification}",
                conformance_result=DQ_ConformanceResult(
                    specification=specification,
                    is_conformant=is_conformant,
                    explanation=explanation,
                ),
            )
        )

    def overall_quality_score(self) -> float | None:
        """
        Calculate overall quality score as weighted average of quantitative results.
        حساب درجة الجودة الكلية كمتوسط مرجح للنتائج الكمية

        Weights: positionalAccuracy=0.3, completeness=0.25, thematicAccuracy=0.25,
                 logicalConsistency=0.1, temporalQuality=0.1

        Returns:
            Score between 0-100, or None if no quantitative elements exist.
        """
        weights = {
            "positionalAccuracy": 0.30,
            "completeness": 0.25,
            "thematicAccuracy": 0.25,
            "logicalConsistency": 0.10,
            "temporalQuality": 0.10,
        }
        total_weight = 0.0
        weighted_sum = 0.0

        for element in self.report:
            if element.quantitative_result is None:
                continue
            w = weights.get(element.quality_type, 0.10)
            val = element.quantitative_result.value
            # Normalize: positionalAccuracy is in meters (lower=better), cap at 100m
            if element.quality_type == "positionalAccuracy":
                val = max(0.0, 100.0 - val)  # Invert: 0m error = 100 score
            # Clamp to 0-100 range
            val = max(0.0, min(100.0, val))
            weighted_sum += val * w
            total_weight += w

        if total_weight == 0:
            return None
        return round(weighted_sum / total_weight, 2)


# =============================================================================
# ISO 19115 Lineage (Section 6.6)
# =============================================================================


class LI_Source(BaseModel):
    """
    ISO 19115 LI_Source - Data source description.
    وصف مصدر البيانات

    Documents the origin of the data used in processing.
    """

    description: str = Field(..., description="Source description | وصف المصدر")
    description_ar: str | None = Field(default=None)
    source_citation: CI_Citation | None = Field(default=None)
    source_extent: EX_Extent | None = Field(default=None)
    source_reference_system: MD_ReferenceSystem | None = Field(default=None)
    source_spatial_resolution: MD_Resolution | None = Field(default=None)


class LI_ProcessStep(BaseModel):
    """
    ISO 19115 LI_ProcessStep - Processing step in the data lineage.
    خطوة معالجة في سلسلة نسب البيانات

    Documents each transformation applied to the source data.
    """

    description: str = Field(..., description="Step description | وصف الخطوة")
    description_ar: str | None = Field(default=None)
    rationale: str | None = Field(default=None, description="Why this step was done | سبب الخطوة")
    date_time: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When this step was performed | تاريخ التنفيذ",
    )
    processor: CI_ResponsibleParty | None = Field(default=None, description="Who/what processed this step | المعالج")
    source: list[LI_Source] = Field(default_factory=list, description="Input sources for this step | مصادر الإدخال")
    software_reference: str | None = Field(default=None, description="Software used (e.g., GDAL 3.8, PostGIS 3.4)")
    algorithm: str | None = Field(default=None, description="Algorithm used | الخوارزمية المستخدمة")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Processing parameters | معلمات المعالجة")


class LI_Lineage(BaseModel):
    """
    ISO 19115 LI_Lineage - Complete data lineage.
    سلسلة نسب البيانات الكاملة

    Documents the full provenance chain from source data through
    all processing steps to the final product.
    """

    statement: str = Field(
        ...,
        description="General lineage statement | بيان النسب العام",
    )
    statement_ar: str | None = Field(default=None)
    source: list[LI_Source] = Field(default_factory=list, description="Source datasets | مجموعات البيانات المصدر")
    process_step: list[LI_ProcessStep] = Field(default_factory=list, description="Processing steps | خطوات المعالجة")

    def add_step(
        self,
        description: str,
        description_ar: str | None = None,
        software: str | None = None,
        algorithm: str | None = None,
        parameters: dict[str, Any] | None = None,
    ) -> LI_ProcessStep:
        """Add a processing step to the lineage."""
        step = LI_ProcessStep(
            description=description,
            description_ar=description_ar,
            software_reference=software,
            algorithm=algorithm,
            parameters=parameters or {},
        )
        self.process_step.append(step)
        return step


# =============================================================================
# ISO 19115 MD_Metadata - Root Element (Section 6.2)
# =============================================================================


class MD_Metadata(BaseModel):
    """
    ISO 19115 MD_Metadata - Root metadata entity.
    الكيان الجذري للبيانات الوصفية

    This is the top-level container per ISO 19115:2014 Section 6.2.
    All mandatory elements are included:
    - fileIdentifier (metadata_identifier)
    - language
    - characterSet
    - hierarchyLevel
    - contact (metadata_contact)
    - dateStamp (metadata_date)
    - metadataStandardName
    - referenceSystemInfo
    - identificationInfo
    """

    model_config = ConfigDict(use_enum_values=False)

    # Metadata about metadata
    metadata_identifier: str = Field(
        default_factory=lambda: f"MD-{uuid.uuid4().hex[:16].upper()}",
        description="Unique metadata identifier | المعرف الفريد للبيانات الوصفية",
    )
    metadata_language: str = Field(default="eng", description="ISO 639-2/B code")
    metadata_character_set: str = Field(default="utf8")
    metadata_date: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Metadata creation/update date | تاريخ إنشاء/تحديث البيانات الوصفية",
    )
    metadata_standard_name: str = Field(
        default="ISO 19115-1:2014",
        description="Metadata standard name | اسم معيار البيانات الوصفية",
    )
    metadata_standard_version: str = Field(default="2014", description="Standard version | إصدار المعيار")
    metadata_contact: list[CI_ResponsibleParty] = Field(
        default_factory=lambda: [CI_ResponsibleParty()],
        description="Metadata point of contact | جهة الاتصال للبيانات الوصفية",
    )
    hierarchy_level: MD_ScopeCode = Field(
        default=MD_ScopeCode.DATASET,
        description="Scope of the metadata | نطاق البيانات الوصفية",
    )

    # Core identification
    identification_info: MD_DataIdentification = Field(...)

    # Reference system
    reference_system_info: list[MD_ReferenceSystem] = Field(
        default_factory=lambda: [MD_ReferenceSystem.wgs84()],
    )

    # Distribution
    distribution_info: MD_Distribution | None = Field(default=None)

    # Data quality & lineage
    data_quality_info: DataQualityReport | None = Field(default=None)
    lineage: LI_Lineage | None = Field(default=None)

    def to_iso_dict(self) -> dict[str, Any]:
        """
        Export metadata as ISO 19115-compliant dictionary.
        تصدير البيانات الوصفية كقاموس متوافق مع ISO 19115
        """
        return {
            "MD_Metadata": {
                "fileIdentifier": self.metadata_identifier,
                "language": self.metadata_language,
                "characterSet": self.metadata_character_set,
                "hierarchyLevel": self.hierarchy_level.value
                if isinstance(self.hierarchy_level, StrEnum)
                else self.hierarchy_level,
                "contact": [
                    {
                        "CI_ResponsibleParty": {
                            "organisationName": c.organisation_name,
                            "role": c.role.value if isinstance(c.role, StrEnum) else c.role,
                        }
                    }
                    for c in self.metadata_contact
                ],
                "dateStamp": self.metadata_date.isoformat(),
                "metadataStandardName": self.metadata_standard_name,
                "metadataStandardVersion": self.metadata_standard_version,
                "identificationInfo": {
                    "MD_DataIdentification": {
                        "citation": {
                            "CI_Citation": {
                                "title": self.identification_info.citation.title,
                                "date": self.identification_info.citation.date.isoformat(),
                                "dateType": self.identification_info.citation.date_type,
                                "identifier": self.identification_info.citation.identifier,
                            }
                        },
                        "abstract": self.identification_info.abstract,
                        "purpose": self.identification_info.purpose,
                        "status": self.identification_info.status.value
                        if isinstance(self.identification_info.status, StrEnum)
                        else self.identification_info.status,
                        "topicCategory": [
                            tc.value if isinstance(tc, StrEnum) else tc
                            for tc in self.identification_info.topic_category
                        ],
                        "extent": [
                            {
                                "EX_Extent": {
                                    "geographicElement": {
                                        "EX_GeographicBoundingBox": {
                                            "westBoundLongitude": ext.geographic_element.west_bound_longitude,
                                            "eastBoundLongitude": ext.geographic_element.east_bound_longitude,
                                            "southBoundLatitude": ext.geographic_element.south_bound_latitude,
                                            "northBoundLatitude": ext.geographic_element.north_bound_latitude,
                                        }
                                    }
                                    if ext.geographic_element
                                    else None,
                                }
                            }
                            for ext in self.identification_info.extent
                        ],
                    }
                },
                "referenceSystemInfo": [
                    {
                        "MD_ReferenceSystem": {
                            "referenceSystemIdentifier": {
                                "code": rs.code,
                                "codeSpace": rs.code_space,
                            }
                        }
                    }
                    for rs in self.reference_system_info
                ],
            }
        }


# =============================================================================
# GeospatialMetadataRecord - SAHOOL convenience wrapper
# =============================================================================


class GeospatialMetadataRecord(BaseModel):
    """
    SAHOOL Geospatial Metadata Record - High-level wrapper.
    سجل البيانات الوصفية الجغرافية لسهول

    Convenience class that wraps MD_Metadata with SAHOOL-specific
    fields for tenant isolation and domain classification.
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Record ID | معرف السجل",
    )
    tenant_id: str = Field(..., description="SAHOOL tenant ID | معرف المستأجر")
    domain: str = Field(
        ...,
        description="Data domain: field | satellite | terrain | iot | weather | ndvi",
    )
    resource_id: str = Field(
        ...,
        description="ID of the resource this metadata describes | معرف المورد",
    )
    resource_type: str = Field(
        ...,
        description="Type of resource (field_boundary, ndvi_reading, dem, sensor_data)",
    )

    # ISO 19115 metadata
    metadata: MD_Metadata = Field(...)

    # SAHOOL timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    created_by: str | None = Field(default=None)

    # Indexing
    is_published: bool = Field(default=False)
    tags: list[str] = Field(default_factory=list)

    def to_geojson_metadata(self) -> dict[str, Any]:
        """Export as GeoJSON-compatible metadata properties."""
        return {
            "metadata_id": self.id,
            "metadata_standard": "ISO 19115-1:2014",
            "domain": self.domain,
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "title": self.metadata.identification_info.citation.title,
            "abstract": self.metadata.identification_info.abstract,
            "crs": self.metadata.reference_system_info[0].code if self.metadata.reference_system_info else "EPSG:4326",
            "created_at": self.created_at.isoformat(),
        }
