"""
SAHOOL Pivot Management Module - وحدة إدارة المحور المركزي

Backend support for center pivot and linear move irrigation systems:
- Circular field geometry generation | هندسة الحقول الدائرية
- Pivot zone creation and management | إنشاء وإدارة مناطق المحور
- VRA to VRI prescription conversion | تحويل وصفات VRA إلى VRI
- Span/tower configuration | تكوين الأبراج

Bridges the mobile SpanZone models with backend infrastructure.

Version: 1.0.0
Author: SAHOOL Platform
"""

from .geometry import (
    create_circular_field_boundary,
    create_pivot_sector,
    create_pivot_zone_grid,
    create_span_annulus,
    PivotGeometry,
    PivotSector,
    PivotZoneGrid,
    SpanAnnulus,
)

from .vri_converter import (
    ndvi_to_vri_prescription,
    vra_to_vri_prescription,
    VRIConverterConfig,
    VRIPrescription,
    VRIZone,
)

__all__ = [
    # Geometry
    "create_circular_field_boundary",
    "create_pivot_sector",
    "create_pivot_zone_grid",
    "create_span_annulus",
    "PivotGeometry",
    "PivotSector",
    "PivotZoneGrid",
    "SpanAnnulus",
    # VRI Converter
    "ndvi_to_vri_prescription",
    "vra_to_vri_prescription",
    "VRIConverterConfig",
    "VRIPrescription",
    "VRIZone",
]
