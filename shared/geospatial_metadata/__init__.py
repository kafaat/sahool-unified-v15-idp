"""
ISO 19115 Geospatial Metadata Module | وحدة البيانات الوصفية الجغرافية ISO 19115

Provides comprehensive ISO 19115:2014 compliant metadata models for all
geospatial datasets in the SAHOOL platform including fields, satellite imagery,
terrain analysis, and NDVI data.

يوفر نماذج بيانات وصفية متوافقة مع ISO 19115:2014 لجميع مجموعات
البيانات الجغرافية في منصة سهول.

Author: SAHOOL Platform
Version: 16.0.0
License: Proprietary - KAFAAT

Example Usage:
    ```python
    from shared.geospatial_metadata import (
        GeospatialMetadataRecord,
        DataQualityReport,
        LineageInfo,
        create_field_metadata,
        create_ndvi_metadata,
    )

    # Create metadata for a field boundary
    metadata = create_field_metadata(
        field_id="FIELD-001",
        title="North Wheat Field Boundary",
        abstract="Boundary survey of 8.5 ha wheat field",
        bbox=(46.7, 24.7, 46.8, 24.8),
        crs="EPSG:4326",
    )
    ```
"""

from .factory import (
    create_field_metadata,
    create_iot_sensor_metadata,
    create_ndvi_metadata,
    create_satellite_metadata,
    create_terrain_metadata,
)
from .iso19115 import (
    CI_Citation,
    CI_OnlineResource,
    CI_ResponsibleParty,
    CI_RoleCode,
    DataQualityReport,
    DQ_ConformanceResult,
    DQ_Element,
    DQ_QuantitativeResult,
    DQ_Scope,
    EX_Extent,
    EX_GeographicBoundingBox,
    EX_TemporalExtent,
    GeospatialMetadataRecord,
    LI_Lineage,
    LI_ProcessStep,
    LI_Source,
    MD_AggregateInformation,
    MD_BrowseGraphic,
    MD_Constraints,
    MD_DataIdentification,
    MD_DigitalTransferOptions,
    MD_Distribution,
    MD_DistributionFormat,
    MD_Keywords,
    MD_LegalConstraints,
    MD_MaintenanceInformation,
    MD_Metadata,
    MD_ReferenceSystem,
    MD_Resolution,
    MD_RestrictionCode,
    MD_ScopeCode,
    MD_SpatialRepresentationType,
    MD_TopicCategory,
    MD_TransferOptions,
)

__all__ = [
    # Core metadata record
    "GeospatialMetadataRecord",
    "MD_Metadata",
    "MD_DataIdentification",
    "MD_Distribution",
    "MD_ReferenceSystem",
    "MD_Resolution",
    "MD_MaintenanceInformation",
    # Citation
    "CI_Citation",
    "CI_ResponsibleParty",
    "CI_RoleCode",
    "CI_OnlineResource",
    # Extent
    "EX_Extent",
    "EX_GeographicBoundingBox",
    "EX_TemporalExtent",
    # Keywords & constraints
    "MD_Keywords",
    "MD_Constraints",
    "MD_LegalConstraints",
    "MD_RestrictionCode",
    # Distribution
    "MD_DistributionFormat",
    "MD_DigitalTransferOptions",
    "MD_TransferOptions",
    # Browse graphic & aggregation
    "MD_BrowseGraphic",
    "MD_AggregateInformation",
    # Data quality (ISO 19157)
    "DataQualityReport",
    "DQ_Scope",
    "DQ_Element",
    "DQ_QuantitativeResult",
    "DQ_ConformanceResult",
    # Lineage
    "LI_Lineage",
    "LI_ProcessStep",
    "LI_Source",
    # Enums
    "MD_ScopeCode",
    "MD_TopicCategory",
    "MD_SpatialRepresentationType",
    # Factory functions
    "create_field_metadata",
    "create_ndvi_metadata",
    "create_terrain_metadata",
    "create_satellite_metadata",
    "create_iot_sensor_metadata",
]

__version__ = "16.0.0"
__author__ = "SAHOOL Platform"
