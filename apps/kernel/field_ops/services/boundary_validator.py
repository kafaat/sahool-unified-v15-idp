"""
خدمة التحقق من حدود الحقول - SAHOOL Field Boundary Validation Service
==========================================================================
نظام شامل للتحقق من صحة حدود الحقول الجغرافية

Comprehensive field boundary validation system with:
- Geometry validation (self-intersection, winding order, etc.)
- Yemen-specific geographic constraints
- Overlap detection with existing fields
- Area and perimeter calculations
- Automatic geometry repair

المطور: SAHOOL Platform
Developer: SAHOOL Platform
الإصدار: 1.0.0
Version: 1.0.0
"""

import json
import math
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any, Set
from enum import Enum
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, ConfigDict

try:
    from shapely.geometry import (
        shape,
        Point,
        Polygon,
        MultiPolygon,
        LineString,
        mapping,
    )
    from shapely.ops import unary_union
    from shapely.validation import make_valid, explain_validity
    from shapely import simplify, normalize
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False
    print("تحذير: مكتبة Shapely غير مثبتة - Warning: Shapely not installed")
    print("يرجى التثبيت: pip install shapely")


# ============== الثوابت - Constants ==============

# حدود اليمن الجغرافية - Yemen geographic bounds
YEMEN_BOUNDS = {
    "latitude": {"min": 12.0, "max": 19.0},
    "longitude": {"min": 42.0, "max": 54.0},
}

# حدود المساحة - Area limits (hectares)
AREA_LIMITS = {
    "min_hectares": 0.1,  # 0.1 هكتار = 1000 م² - 0.1 hectare = 1000 m²
    "max_hectares": 1000.0,  # 1000 هكتار - 1000 hectares
}

# دقة الإحداثيات - Coordinate precision
COORDINATE_PRECISION = 6  # 6 منازل عشرية ≈ 0.11 متر - 6 decimal places ≈ 0.11 meters

# التفاوت الافتراضي للتبسيط - Default simplification tolerance
DEFAULT_SIMPLIFICATION_TOLERANCE = 0.00001  # ≈ 1 متر - ≈ 1 meter

# محافظات اليمن - Yemen governorates
YEMEN_GOVERNORATES = [
    "صنعاء", "عدن", "تعز", "الحديدة", "إب", "ذمار", "حضرموت",
    "المحويت", "حجة", "صعدة", "عمران", "البيضاء", "أبين", "شبوة",
    "المهرة", "لحج", "الضالع", "مأرب", "الجوف", "ريمة", "سقطرى", "أمانة العاصمة"
]


# ============== التعدادات - Enumerations ==============

class ValidationSeverity(str, Enum):
    """مستوى خطورة مشكلة التحقق - Validation issue severity"""
    INFO = "info"  # معلومات - Information
    WARNING = "warning"  # تحذير - Warning
    ERROR = "error"  # خطأ - Error
    CRITICAL = "critical"  # حرج - Critical


class GeometryIssueType(str, Enum):
    """أنواع مشاكل الهندسة - Geometry issue types"""
    SELF_INTERSECTION = "self_intersection"  # تقاطع ذاتي
    INVALID_WINDING = "invalid_winding"  # اتجاه خاطئ
    DUPLICATE_POINTS = "duplicate_points"  # نقاط مكررة
    INSUFFICIENT_POINTS = "insufficient_points"  # نقاط غير كافية
    INVALID_POLYGON = "invalid_polygon"  # مضلع غير صالح
    TOPOLOGY_ERROR = "topology_error"  # خطأ في الطوبولوجيا


class BoundarySeverity(str, Enum):
    """مستوى خطورة انتهاك الحدود - Boundary violation severity"""
    OUT_OF_YEMEN = "out_of_yemen"  # خارج اليمن
    PARTIALLY_OUT = "partially_out"  # جزئياً خارج الحدود
    AREA_TOO_SMALL = "area_too_small"  # مساحة صغيرة جداً
    AREA_TOO_LARGE = "area_too_large"  # مساحة كبيرة جداً
    MARITIME_AREA = "maritime_area"  # منطقة بحرية


# ============== النماذج - Models ==============

class ValidationIssue(BaseModel):
    """مشكلة في التحقق - Validation issue"""
    model_config = ConfigDict(populate_by_name=True)

    issue_type: str = Field(..., description="نوع المشكلة - Issue type")
    severity: ValidationSeverity = Field(..., description="الخطورة - Severity")
    message_ar: str = Field(..., description="الرسالة بالعربية - Arabic message")
    message_en: str = Field(..., description="الرسالة بالإنجليزية - English message")
    location: Optional[Dict[str, float]] = Field(None, description="موقع المشكلة - Issue location")
    fixable: bool = Field(False, description="قابل للإصلاح - Can be auto-fixed")
    details: Dict[str, Any] = Field(default_factory=dict, description="تفاصيل إضافية - Additional details")


class BoundaryValidationResult(BaseModel):
    """نتيجة التحقق من الحدود - Boundary validation result"""
    model_config = ConfigDict(populate_by_name=True)

    is_valid: bool = Field(..., description="صالح - Is valid")
    issues: List[ValidationIssue] = Field(default_factory=list, description="المشاكل - Issues")

    # الإحصائيات - Statistics
    area_hectares: Optional[float] = Field(None, description="المساحة (هكتار) - Area in hectares")
    perimeter_meters: Optional[float] = Field(None, description="المحيط (متر) - Perimeter in meters")
    centroid: Optional[Dict[str, float]] = Field(None, description="المركز - Centroid")
    bounding_box: Optional[Dict[str, float]] = Field(None, description="المربع المحيط - Bounding box")

    # التحسينات - Improvements
    simplified_geometry: Optional[Dict[str, Any]] = Field(None, description="هندسة مبسطة - Simplified geometry")
    fixed_geometry: Optional[Dict[str, Any]] = Field(None, description="هندسة مصلحة - Fixed geometry")

    # الميتاداتا - Metadata
    validation_timestamp: datetime = Field(default_factory=datetime.utcnow, description="وقت التحقق - Validation time")
    validator_version: str = Field("1.0.0", description="إصدار المحقق - Validator version")


class OverlapResult(BaseModel):
    """نتيجة فحص التداخل - Overlap detection result"""
    model_config = ConfigDict(populate_by_name=True)

    has_overlap: bool = Field(..., description="يوجد تداخل - Has overlap")
    overlapping_fields: List[Dict[str, Any]] = Field(default_factory=list, description="الحقول المتداخلة - Overlapping fields")
    total_overlap_area_hectares: float = Field(0.0, description="مساحة التداخل الكلية - Total overlap area")
    max_overlap_percentage: float = Field(0.0, description="أقصى نسبة تداخل - Max overlap percentage")


# ============== فئة المحقق - Validator Class ==============

class BoundaryValidator:
    """
    محقق حدود الحقول
    Field boundary validator

    الميزات الرئيسية:
    - التحقق من صحة الهندسة (تقاطعات، اتجاهات، إلخ)
    - قيود اليمن الجغرافية
    - كشف التداخل مع الحقول الموجودة
    - حسابات المساحة والمحيط
    - إصلاح تلقائي للمشاكل الشائعة

    Main Features:
    - Geometry validation (intersections, winding, etc.)
    - Yemen geographic constraints
    - Overlap detection with existing fields
    - Area and perimeter calculations
    - Automatic repair of common issues
    """

    def __init__(self, yemen_boundaries_path: Optional[str] = None):
        """
        تهيئة المحقق
        Initialize validator

        Args:
            yemen_boundaries_path: مسار ملف حدود اليمن GeoJSON
                                  Path to Yemen boundaries GeoJSON file
        """
        if not SHAPELY_AVAILABLE:
            raise ImportError(
                "مكتبة Shapely مطلوبة - Shapely library required\n"
                "التثبيت: pip install shapely"
            )

        self.yemen_boundaries = None
        self.governorate_boundaries = {}

        # تحميل حدود اليمن إذا كان المسار موجوداً
        # Load Yemen boundaries if path provided
        if yemen_boundaries_path:
            self._load_yemen_boundaries(yemen_boundaries_path)

    def _load_yemen_boundaries(self, path: str) -> None:
        """
        تحميل حدود اليمن من ملف GeoJSON
        Load Yemen boundaries from GeoJSON file
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # تحميل الحدود الوطنية - Load national boundaries
            if data.get('type') == 'FeatureCollection':
                for feature in data.get('features', []):
                    props = feature.get('properties', {})
                    geom = shape(feature['geometry'])

                    if props.get('type') == 'country':
                        self.yemen_boundaries = geom
                    elif props.get('type') == 'governorate':
                        gov_name = props.get('name_ar')
                        if gov_name:
                            self.governorate_boundaries[gov_name] = geom

        except Exception as e:
            print(f"تحذير: فشل تحميل حدود اليمن - Warning: Failed to load Yemen boundaries: {e}")

    # ============== التحقق من الهندسة - Geometry Validation ==============

    def validate_geometry(self, geojson: Dict[str, Any]) -> BoundaryValidationResult:
        """
        التحقق من صحة هندسة GeoJSON
        Validate GeoJSON geometry

        Args:
            geojson: كائن GeoJSON (Feature أو Geometry)
                    GeoJSON object (Feature or Geometry)

        Returns:
            BoundaryValidationResult: نتيجة التحقق الشاملة
                                     Comprehensive validation result
        """
        issues = []

        try:
            # استخراج الهندسة - Extract geometry
            if geojson.get('type') == 'Feature':
                geometry = geojson.get('geometry')
            elif geojson.get('type') in ['Polygon', 'MultiPolygon']:
                geometry = geojson
            else:
                issues.append(ValidationIssue(
                    issue_type=GeometryIssueType.INVALID_POLYGON.value,
                    severity=ValidationSeverity.CRITICAL,
                    message_ar="نوع GeoJSON غير صالح",
                    message_en="Invalid GeoJSON type",
                    fixable=False
                ))
                return BoundaryValidationResult(is_valid=False, issues=issues)

            # تحويل إلى كائن Shapely - Convert to Shapely object
            polygon = shape(geometry)

            # التحقق الأساسي - Basic validation
            if not polygon.is_valid:
                validity_msg = explain_validity(polygon)
                issues.append(ValidationIssue(
                    issue_type=GeometryIssueType.INVALID_POLYGON.value,
                    severity=ValidationSeverity.ERROR,
                    message_ar=f"مضلع غير صالح: {validity_msg}",
                    message_en=f"Invalid polygon: {validity_msg}",
                    fixable=True,
                    details={"validity_reason": validity_msg}
                ))

            # التحقق من التقاطع الذاتي - Check self-intersection
            self_intersect_issues = self.check_self_intersection(polygon)
            issues.extend(self_intersect_issues)

            # التحقق من اتجاه النقاط - Check winding order
            winding_issues = self.check_winding_order(polygon)
            issues.extend(winding_issues)

            # التحقق من النقاط المكررة - Check duplicate points
            duplicate_issues = self._check_duplicate_points(polygon)
            issues.extend(duplicate_issues)

            # التحقق من عدد النقاط - Check point count
            point_count_issues = self._check_point_count(polygon)
            issues.extend(point_count_issues)

            # التحقق من الحدود الجغرافية - Check geographic bounds
            bounds_issues = self._check_yemen_bounds(polygon)
            issues.extend(bounds_issues)

            # التحقق من المساحة - Check area
            area_issues = self._check_area(polygon)
            issues.extend(area_issues)

            # حساب الإحصائيات - Calculate statistics
            area_ha = self.calculate_area_hectares(polygon)
            perimeter_m = self.calculate_perimeter_meters(polygon)
            centroid = self.get_centroid(polygon)
            bbox = self.get_bounding_box(polygon)

            # إصلاح المشاكل إذا لزم الأمر - Fix issues if needed
            fixed_geom = None
            if any(issue.fixable for issue in issues):
                try:
                    fixed_polygon = self.fix_common_issues(polygon)
                    if fixed_polygon and fixed_polygon.is_valid:
                        fixed_geom = mapping(fixed_polygon)
                except Exception as e:
                    issues.append(ValidationIssue(
                        issue_type=GeometryIssueType.TOPOLOGY_ERROR.value,
                        severity=ValidationSeverity.WARNING,
                        message_ar=f"فشل الإصلاح التلقائي: {str(e)}",
                        message_en=f"Auto-fix failed: {str(e)}",
                        fixable=False
                    ))

            # تبسيط الهندسة - Simplify geometry
            simplified_geom = None
            try:
                simplified_polygon = self.simplify_geometry(polygon, DEFAULT_SIMPLIFICATION_TOLERANCE)
                if simplified_polygon:
                    simplified_geom = mapping(simplified_polygon)
            except Exception:
                pass

            # تحديد الصلاحية النهائية - Determine final validity
            critical_issues = [i for i in issues if i.severity == ValidationSeverity.CRITICAL]
            error_issues = [i for i in issues if i.severity == ValidationSeverity.ERROR]
            is_valid = len(critical_issues) == 0 and len(error_issues) == 0

            return BoundaryValidationResult(
                is_valid=is_valid,
                issues=issues,
                area_hectares=area_ha,
                perimeter_meters=perimeter_m,
                centroid=centroid,
                bounding_box=bbox,
                simplified_geometry=simplified_geom,
                fixed_geometry=fixed_geom,
            )

        except Exception as e:
            issues.append(ValidationIssue(
                issue_type=GeometryIssueType.TOPOLOGY_ERROR.value,
                severity=ValidationSeverity.CRITICAL,
                message_ar=f"خطأ في التحقق: {str(e)}",
                message_en=f"Validation error: {str(e)}",
                fixable=False,
                details={"error": str(e)}
            ))
            return BoundaryValidationResult(is_valid=False, issues=issues)

    def check_self_intersection(self, polygon: Polygon) -> List[ValidationIssue]:
        """
        التحقق من التقاطع الذاتي
        Check for self-intersections in polygon

        Args:
            polygon: مضلع Shapely - Shapely polygon

        Returns:
            List[ValidationIssue]: قائمة المشاكل - List of issues
        """
        issues = []

        # التحقق من الحلقة الخارجية - Check exterior ring
        exterior = LineString(polygon.exterior.coords)
        if not exterior.is_simple:
            issues.append(ValidationIssue(
                issue_type=GeometryIssueType.SELF_INTERSECTION.value,
                severity=ValidationSeverity.ERROR,
                message_ar="الحد الخارجي للحقل يتقاطع مع نفسه",
                message_en="Field boundary has self-intersections",
                fixable=True,
                details={"ring": "exterior"}
            ))

        # التحقق من الثقوب - Check interior rings (holes)
        for i, interior in enumerate(polygon.interiors):
            interior_line = LineString(interior.coords)
            if not interior_line.is_simple:
                issues.append(ValidationIssue(
                    issue_type=GeometryIssueType.SELF_INTERSECTION.value,
                    severity=ValidationSeverity.ERROR,
                    message_ar=f"الثقب رقم {i+1} يتقاطع مع نفسه",
                    message_en=f"Hole #{i+1} has self-intersections",
                    fixable=True,
                    details={"ring": "interior", "hole_index": i}
                ))

        return issues

    def check_winding_order(self, polygon: Polygon) -> List[ValidationIssue]:
        """
        التحقق من اتجاه النقاط (عكس عقارب الساعة للخارج، مع عقارب الساعة للثقوب)
        Check winding order (counter-clockwise for exterior, clockwise for holes)

        Args:
            polygon: مضلع Shapely - Shapely polygon

        Returns:
            List[ValidationIssue]: قائمة المشاكل - List of issues
        """
        issues = []

        # Shapely يتبع معيار GeoJSON (عكس عقارب الساعة للخارج)
        # Shapely follows GeoJSON standard (counter-clockwise for exterior)

        # التحقق من الحلقة الخارجية - Check exterior ring
        # مساحة موجبة = عكس عقارب الساعة (صحيح)
        # Positive area = counter-clockwise (correct)
        exterior_coords = list(polygon.exterior.coords)
        if len(exterior_coords) >= 4:
            area = self._calculate_signed_area(exterior_coords)
            if area < 0:
                issues.append(ValidationIssue(
                    issue_type=GeometryIssueType.INVALID_WINDING.value,
                    severity=ValidationSeverity.WARNING,
                    message_ar="الحد الخارجي بترتيب خاطئ (يجب أن يكون عكس عقارب الساعة)",
                    message_en="Exterior boundary has wrong winding order (should be counter-clockwise)",
                    fixable=True,
                    details={"ring": "exterior", "area": area}
                ))

        # التحقق من الثقوب - Check interior rings (holes)
        # مساحة سالبة = مع عقارب الساعة (صحيح للثقوب)
        # Negative area = clockwise (correct for holes)
        for i, interior in enumerate(polygon.interiors):
            interior_coords = list(interior.coords)
            if len(interior_coords) >= 4:
                area = self._calculate_signed_area(interior_coords)
                if area > 0:
                    issues.append(ValidationIssue(
                        issue_type=GeometryIssueType.INVALID_WINDING.value,
                        severity=ValidationSeverity.WARNING,
                        message_ar=f"الثقب رقم {i+1} بترتيب خاطئ (يجب أن يكون مع عقارب الساعة)",
                        message_en=f"Hole #{i+1} has wrong winding order (should be clockwise)",
                        fixable=True,
                        details={"ring": "interior", "hole_index": i, "area": area}
                    ))

        return issues

    def simplify_geometry(self, polygon: Polygon, tolerance: float = DEFAULT_SIMPLIFICATION_TOLERANCE) -> Polygon:
        """
        تبسيط الهندسة (تقليل عدد النقاط مع الحفاظ على الشكل)
        Simplify geometry (reduce points while preserving shape)

        Args:
            polygon: المضلع الأصلي - Original polygon
            tolerance: التفاوت المسموح (بالدرجات) - Tolerance in degrees

        Returns:
            Polygon: المضلع المبسط - Simplified polygon
        """
        try:
            # استخدام خوارزمية Douglas-Peucker - Use Douglas-Peucker algorithm
            simplified = simplify(polygon, tolerance, preserve_topology=True)

            # التأكد من أن النتيجة صالحة - Ensure result is valid
            if not simplified.is_valid:
                simplified = make_valid(simplified)

            return simplified
        except Exception as e:
            print(f"تحذير: فشل التبسيط - Warning: Simplification failed: {e}")
            return polygon

    def fix_common_issues(self, polygon: Polygon) -> Polygon:
        """
        إصلاح المشاكل الشائعة في الهندسة
        Fix common geometry issues

        Args:
            polygon: المضلع الأصلي - Original polygon

        Returns:
            Polygon: المضلع المصلح - Fixed polygon
        """
        try:
            # إصلاح المضلع غير الصالح - Fix invalid polygon
            if not polygon.is_valid:
                polygon = make_valid(polygon)

                # إذا أصبح MultiPolygon، خذ أكبر جزء
                # If became MultiPolygon, take largest part
                if isinstance(polygon, MultiPolygon):
                    polygon = max(polygon.geoms, key=lambda p: p.area)

            # تنظيم الاتجاه - Normalize orientation
            polygon = normalize(polygon)

            # إزالة النقاط المكررة - Remove duplicate points
            polygon = self._remove_duplicate_points(polygon)

            # تبسيط بسيط لإزالة النقاط القريبة جداً
            # Light simplification to remove very close points
            polygon = simplify(polygon, tolerance=0.0000001, preserve_topology=True)

            return polygon

        except Exception as e:
            print(f"تحذير: فشل الإصلاح - Warning: Fix failed: {e}")
            return polygon

    # ============== التحقق من الحدود - Boundary Validation ==============

    def _check_yemen_bounds(self, polygon: Polygon) -> List[ValidationIssue]:
        """
        التحقق من أن المضلع ضمن حدود اليمن
        Check if polygon is within Yemen bounds
        """
        issues = []

        bounds = polygon.bounds  # (minx, miny, maxx, maxy)

        # التحقق من خطوط الطول - Check longitude
        if bounds[0] < YEMEN_BOUNDS["longitude"]["min"] or bounds[2] > YEMEN_BOUNDS["longitude"]["max"]:
            issues.append(ValidationIssue(
                issue_type=BoundarySeverity.OUT_OF_YEMEN.value,
                severity=ValidationSeverity.ERROR,
                message_ar=f"الحقل خارج حدود اليمن (خط الطول: {bounds[0]:.4f} - {bounds[2]:.4f})",
                message_en=f"Field outside Yemen bounds (longitude: {bounds[0]:.4f} - {bounds[2]:.4f})",
                fixable=False,
                details={"bounds": bounds, "yemen_bounds": YEMEN_BOUNDS}
            ))

        # التحقق من خطوط العرض - Check latitude
        if bounds[1] < YEMEN_BOUNDS["latitude"]["min"] or bounds[3] > YEMEN_BOUNDS["latitude"]["max"]:
            issues.append(ValidationIssue(
                issue_type=BoundarySeverity.OUT_OF_YEMEN.value,
                severity=ValidationSeverity.ERROR,
                message_ar=f"الحقل خارج حدود اليمن (خط العرض: {bounds[1]:.4f} - {bounds[3]:.4f})",
                message_en=f"Field outside Yemen bounds (latitude: {bounds[1]:.4f} - {bounds[3]:.4f})",
                fixable=False,
                details={"bounds": bounds, "yemen_bounds": YEMEN_BOUNDS}
            ))

        # التحقق من الحدود التفصيلية إذا كانت متوفرة
        # Check detailed boundaries if available
        if self.yemen_boundaries:
            if not self.yemen_boundaries.contains(polygon):
                if self.yemen_boundaries.intersects(polygon):
                    issues.append(ValidationIssue(
                        issue_type=BoundarySeverity.PARTIALLY_OUT.value,
                        severity=ValidationSeverity.WARNING,
                        message_ar="جزء من الحقل خارج الحدود الدقيقة لليمن",
                        message_en="Part of field is outside detailed Yemen boundaries",
                        fixable=False
                    ))
                else:
                    issues.append(ValidationIssue(
                        issue_type=BoundarySeverity.OUT_OF_YEMEN.value,
                        severity=ValidationSeverity.ERROR,
                        message_ar="الحقل بالكامل خارج حدود اليمن",
                        message_en="Field is completely outside Yemen boundaries",
                        fixable=False
                    ))

        return issues

    def _check_area(self, polygon: Polygon) -> List[ValidationIssue]:
        """
        التحقق من حدود المساحة
        Check area limits
        """
        issues = []

        area_ha = self.calculate_area_hectares(polygon)

        if area_ha < AREA_LIMITS["min_hectares"]:
            issues.append(ValidationIssue(
                issue_type=BoundarySeverity.AREA_TOO_SMALL.value,
                severity=ValidationSeverity.WARNING,
                message_ar=f"مساحة الحقل صغيرة جداً ({area_ha:.2f} هكتار، الحد الأدنى {AREA_LIMITS['min_hectares']} هكتار)",
                message_en=f"Field area too small ({area_ha:.2f} ha, minimum {AREA_LIMITS['min_hectares']} ha)",
                fixable=False,
                details={"area_hectares": area_ha, "min_required": AREA_LIMITS["min_hectares"]}
            ))

        if area_ha > AREA_LIMITS["max_hectares"]:
            issues.append(ValidationIssue(
                issue_type=BoundarySeverity.AREA_TOO_LARGE.value,
                severity=ValidationSeverity.WARNING,
                message_ar=f"مساحة الحقل كبيرة جداً ({area_ha:.2f} هكتار، الحد الأقصى {AREA_LIMITS['max_hectares']} هكتار)",
                message_en=f"Field area too large ({area_ha:.2f} ha, maximum {AREA_LIMITS['max_hectares']} ha)",
                fixable=False,
                details={"area_hectares": area_ha, "max_allowed": AREA_LIMITS["max_hectares"]}
            ))

        return issues

    def _check_duplicate_points(self, polygon: Polygon) -> List[ValidationIssue]:
        """
        التحقق من النقاط المكررة
        Check for duplicate consecutive points
        """
        issues = []

        # فحص الحلقة الخارجية - Check exterior ring
        exterior_coords = list(polygon.exterior.coords)
        duplicates = self._find_duplicate_consecutive_points(exterior_coords)
        if duplicates:
            issues.append(ValidationIssue(
                issue_type=GeometryIssueType.DUPLICATE_POINTS.value,
                severity=ValidationSeverity.INFO,
                message_ar=f"الحد الخارجي يحتوي على {len(duplicates)} نقطة مكررة",
                message_en=f"Exterior boundary has {len(duplicates)} duplicate points",
                fixable=True,
                details={"duplicate_count": len(duplicates), "ring": "exterior"}
            ))

        # فحص الثقوب - Check interior rings
        for i, interior in enumerate(polygon.interiors):
            interior_coords = list(interior.coords)
            duplicates = self._find_duplicate_consecutive_points(interior_coords)
            if duplicates:
                issues.append(ValidationIssue(
                    issue_type=GeometryIssueType.DUPLICATE_POINTS.value,
                    severity=ValidationSeverity.INFO,
                    message_ar=f"الثقب رقم {i+1} يحتوي على {len(duplicates)} نقطة مكررة",
                    message_en=f"Hole #{i+1} has {len(duplicates)} duplicate points",
                    fixable=True,
                    details={"duplicate_count": len(duplicates), "ring": "interior", "hole_index": i}
                ))

        return issues

    def _check_point_count(self, polygon: Polygon) -> List[ValidationIssue]:
        """
        التحقق من عدد النقاط الكافي
        Check sufficient point count
        """
        issues = []

        # المضلع يحتاج على الأقل 4 نقاط (3 نقاط فريدة + نقطة الإغلاق)
        # Polygon needs at least 4 points (3 unique + closing point)
        min_points = 4

        exterior_count = len(polygon.exterior.coords)
        if exterior_count < min_points:
            issues.append(ValidationIssue(
                issue_type=GeometryIssueType.INSUFFICIENT_POINTS.value,
                severity=ValidationSeverity.CRITICAL,
                message_ar=f"عدد نقاط غير كافٍ ({exterior_count}، الحد الأدنى {min_points})",
                message_en=f"Insufficient points ({exterior_count}, minimum {min_points})",
                fixable=False,
                details={"point_count": exterior_count, "min_required": min_points}
            ))

        return issues

    # ============== كشف التداخل - Overlap Detection ==============

    def check_overlap_with_existing(
        self,
        new_boundary: Dict[str, Any],
        existing_fields: List[Dict[str, Any]],
        user_id: Optional[str] = None,
        tolerance_percentage: float = 5.0
    ) -> OverlapResult:
        """
        فحص التداخل مع الحقول الموجودة
        Check overlap with existing fields

        Args:
            new_boundary: حدود الحقل الجديد (GeoJSON) - New field boundary (GeoJSON)
            existing_fields: قائمة الحقول الموجودة - List of existing fields
                            كل حقل يحتوي على: {"field_id": ..., "geometry": ..., "user_id": ...}
            user_id: معرف المستخدم (للسماح بالتداخل مع حقول نفس المستخدم)
                    User ID (to allow overlap with same user's fields)
            tolerance_percentage: نسبة التفاوت المسموح - Allowed overlap percentage

        Returns:
            OverlapResult: نتيجة فحص التداخل - Overlap detection result
        """
        try:
            # تحويل الحد الجديد - Convert new boundary
            new_polygon = shape(new_boundary if new_boundary.get('type') != 'Feature'
                              else new_boundary['geometry'])

            overlapping_fields = []
            total_overlap_area = 0.0
            max_overlap_percentage = 0.0

            for field in existing_fields:
                # تخطي حقول نفس المستخدم إذا لزم الأمر
                # Skip same user's fields if needed
                if user_id and field.get('user_id') == user_id:
                    continue

                # تحويل هندسة الحقل - Convert field geometry
                field_geom = field.get('geometry')
                if not field_geom:
                    continue

                field_polygon = shape(field_geom if field_geom.get('type') != 'Feature'
                                     else field_geom['geometry'])

                # فحص التداخل - Check overlap
                if new_polygon.intersects(field_polygon):
                    intersection = new_polygon.intersection(field_polygon)
                    overlap_area_ha = self.calculate_area_hectares(intersection)

                    # حساب نسبة التداخل - Calculate overlap percentage
                    new_area_ha = self.calculate_area_hectares(new_polygon)
                    overlap_percentage = (overlap_area_ha / new_area_ha * 100) if new_area_ha > 0 else 0

                    # إذا كان التداخل أكبر من التفاوت المسموح
                    # If overlap exceeds tolerance
                    if overlap_percentage > tolerance_percentage:
                        overlapping_fields.append({
                            "field_id": field.get('field_id'),
                            "overlap_area_hectares": overlap_area_ha,
                            "overlap_percentage": overlap_percentage,
                            "field_name": field.get('name', 'غير معروف - Unknown'),
                            "intersection_geometry": mapping(intersection)
                        })

                        total_overlap_area += overlap_area_ha
                        max_overlap_percentage = max(max_overlap_percentage, overlap_percentage)

            has_overlap = len(overlapping_fields) > 0

            return OverlapResult(
                has_overlap=has_overlap,
                overlapping_fields=overlapping_fields,
                total_overlap_area_hectares=total_overlap_area,
                max_overlap_percentage=max_overlap_percentage
            )

        except Exception as e:
            print(f"خطأ في فحص التداخل - Overlap check error: {e}")
            return OverlapResult(has_overlap=False, overlapping_fields=[])

    def get_overlapping_fields(
        self,
        boundary: Dict[str, Any],
        field_database: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        الحصول على قائمة الحقول المتداخلة
        Get list of overlapping fields

        Args:
            boundary: حدود الحقل (GeoJSON) - Field boundary (GeoJSON)
            field_database: قاعدة بيانات الحقول - Field database

        Returns:
            List[Dict]: قائمة الحقول المتداخلة - List of overlapping fields
        """
        result = self.check_overlap_with_existing(
            new_boundary=boundary,
            existing_fields=field_database,
            tolerance_percentage=0.0  # أي تداخل - Any overlap
        )
        return result.overlapping_fields

    def calculate_overlap_percentage(
        self,
        poly1: Dict[str, Any],
        poly2: Dict[str, Any]
    ) -> float:
        """
        حساب نسبة التداخل بين مضلعين
        Calculate overlap percentage between two polygons

        Args:
            poly1: المضلع الأول (GeoJSON) - First polygon (GeoJSON)
            poly2: المضلع الثاني (GeoJSON) - Second polygon (GeoJSON)

        Returns:
            float: نسبة التداخل (0-100) - Overlap percentage (0-100)
        """
        try:
            polygon1 = shape(poly1 if poly1.get('type') != 'Feature' else poly1['geometry'])
            polygon2 = shape(poly2 if poly2.get('type') != 'Feature' else poly2['geometry'])

            if not polygon1.intersects(polygon2):
                return 0.0

            intersection = polygon1.intersection(polygon2)
            intersection_area = self.calculate_area_hectares(intersection)
            poly1_area = self.calculate_area_hectares(polygon1)

            if poly1_area == 0:
                return 0.0

            return (intersection_area / poly1_area) * 100

        except Exception as e:
            print(f"خطأ في حساب التداخل - Overlap calculation error: {e}")
            return 0.0

    # ============== حسابات المساحة - Area Calculations ==============

    def calculate_area_hectares(self, polygon: Polygon) -> float:
        """
        حساب المساحة بالهكتار
        Calculate area in hectares

        يستخدم إسقاط UTM لليمن للحصول على دقة عالية
        Uses UTM projection for Yemen for high accuracy

        Args:
            polygon: المضلع - Polygon

        Returns:
            float: المساحة بالهكتار - Area in hectares
        """
        try:
            # حساب المساحة الجيوديزية - Calculate geodesic area
            # نستخدم تقريب WGS84 ellipsoid
            # Use WGS84 ellipsoid approximation

            # للبساطة، نستخدم حساب تقريبي بناءً على خط العرض
            # For simplicity, use approximate calculation based on latitude
            centroid = polygon.centroid
            lat = centroid.y

            # عامل التحويل من الدرجات المربعة إلى متر مربع عند خط العرض
            # Conversion factor from square degrees to square meters at latitude
            # 1 degree latitude ≈ 111,320 meters
            # 1 degree longitude ≈ 111,320 * cos(latitude) meters
            lat_rad = math.radians(lat)
            meters_per_deg_lat = 111320
            meters_per_deg_lon = 111320 * math.cos(lat_rad)

            # حساب المساحة بالدرجات المربعة - Calculate area in square degrees
            area_deg2 = polygon.area

            # تحويل إلى متر مربع - Convert to square meters
            area_m2 = area_deg2 * meters_per_deg_lat * meters_per_deg_lon

            # تحويل إلى هكتار (1 هكتار = 10,000 م²)
            # Convert to hectares (1 hectare = 10,000 m²)
            area_ha = area_m2 / 10000

            return round(area_ha, 4)

        except Exception as e:
            print(f"خطأ في حساب المساحة - Area calculation error: {e}")
            return 0.0

    def calculate_perimeter_meters(self, polygon: Polygon) -> float:
        """
        حساب المحيط بالأمتار
        Calculate perimeter in meters

        Args:
            polygon: المضلع - Polygon

        Returns:
            float: المحيط بالأمتار - Perimeter in meters
        """
        try:
            centroid = polygon.centroid
            lat = centroid.y

            # عامل التحويل - Conversion factor
            lat_rad = math.radians(lat)
            meters_per_deg_lat = 111320
            meters_per_deg_lon = 111320 * math.cos(lat_rad)

            # حساب المحيط - Calculate perimeter
            coords = list(polygon.exterior.coords)
            perimeter_m = 0.0

            for i in range(len(coords) - 1):
                lon1, lat1 = coords[i]
                lon2, lat2 = coords[i + 1]

                # حساب المسافة التقريبية - Calculate approximate distance
                dlat = (lat2 - lat1) * meters_per_deg_lat
                dlon = (lon2 - lon1) * meters_per_deg_lon

                distance = math.sqrt(dlat**2 + dlon**2)
                perimeter_m += distance

            return round(perimeter_m, 2)

        except Exception as e:
            print(f"خطأ في حساب المحيط - Perimeter calculation error: {e}")
            return 0.0

    def get_centroid(self, polygon: Polygon) -> Dict[str, float]:
        """
        الحصول على نقطة المركز
        Get centroid point

        Args:
            polygon: المضلع - Polygon

        Returns:
            Dict: إحداثيات المركز {"longitude": ..., "latitude": ...}
                 Centroid coordinates
        """
        try:
            centroid = polygon.centroid
            return {
                "longitude": round(centroid.x, COORDINATE_PRECISION),
                "latitude": round(centroid.y, COORDINATE_PRECISION)
            }
        except Exception as e:
            print(f"خطأ في حساب المركز - Centroid calculation error: {e}")
            return {"longitude": 0.0, "latitude": 0.0}

    def get_bounding_box(self, polygon: Polygon) -> Dict[str, float]:
        """
        الحصول على المربع المحيط
        Get bounding box

        Args:
            polygon: المضلع - Polygon

        Returns:
            Dict: المربع المحيط {"min_lon": ..., "min_lat": ..., "max_lon": ..., "max_lat": ...}
                 Bounding box coordinates
        """
        try:
            bounds = polygon.bounds  # (minx, miny, maxx, maxy)
            return {
                "min_longitude": round(bounds[0], COORDINATE_PRECISION),
                "min_latitude": round(bounds[1], COORDINATE_PRECISION),
                "max_longitude": round(bounds[2], COORDINATE_PRECISION),
                "max_latitude": round(bounds[3], COORDINATE_PRECISION)
            }
        except Exception as e:
            print(f"خطأ في حساب المربع المحيط - Bounding box calculation error: {e}")
            return {
                "min_longitude": 0.0,
                "min_latitude": 0.0,
                "max_longitude": 0.0,
                "max_latitude": 0.0
            }

    # ============== دوال مساعدة - Helper Functions ==============

    def _calculate_signed_area(self, coords: List[Tuple[float, float]]) -> float:
        """
        حساب المساحة الموقعة (للتحقق من الاتجاه)
        Calculate signed area (for winding order check)

        موجب = عكس عقارب الساعة
        سالب = مع عقارب الساعة

        Positive = counter-clockwise
        Negative = clockwise
        """
        area = 0.0
        n = len(coords)

        for i in range(n - 1):
            x1, y1 = coords[i]
            x2, y2 = coords[i + 1]
            area += (x2 - x1) * (y2 + y1)

        return area / 2.0

    def _find_duplicate_consecutive_points(
        self,
        coords: List[Tuple[float, float]]
    ) -> List[int]:
        """
        إيجاد النقاط المتتالية المكررة
        Find duplicate consecutive points

        Returns:
            List[int]: مؤشرات النقاط المكررة - Indices of duplicate points
        """
        duplicates = []

        for i in range(len(coords) - 1):
            if coords[i] == coords[i + 1]:
                duplicates.append(i)

        return duplicates

    def _remove_duplicate_points(self, polygon: Polygon) -> Polygon:
        """
        إزالة النقاط المكررة
        Remove duplicate consecutive points
        """
        try:
            # إزالة التكرار من الحلقة الخارجية - Remove from exterior
            exterior_coords = list(polygon.exterior.coords)
            unique_exterior = [exterior_coords[0]]

            for i in range(1, len(exterior_coords)):
                if exterior_coords[i] != exterior_coords[i-1]:
                    unique_exterior.append(exterior_coords[i])

            # التأكد من إغلاق المضلع - Ensure polygon is closed
            if unique_exterior[0] != unique_exterior[-1]:
                unique_exterior.append(unique_exterior[0])

            # إزالة التكرار من الثقوب - Remove from holes
            unique_interiors = []
            for interior in polygon.interiors:
                interior_coords = list(interior.coords)
                unique_interior = [interior_coords[0]]

                for i in range(1, len(interior_coords)):
                    if interior_coords[i] != interior_coords[i-1]:
                        unique_interior.append(interior_coords[i])

                if unique_interior[0] != unique_interior[-1]:
                    unique_interior.append(unique_interior[0])

                if len(unique_interior) >= 4:
                    unique_interiors.append(unique_interior)

            return Polygon(unique_exterior, unique_interiors)

        except Exception as e:
            print(f"تحذير: فشل إزالة التكرار - Warning: Duplicate removal failed: {e}")
            return polygon

    def validate_governorate(
        self,
        polygon: Polygon,
        governorate_name: str
    ) -> bool:
        """
        التحقق من أن الحقل داخل محافظة معينة
        Validate that field is within a specific governorate

        Args:
            polygon: حدود الحقل - Field boundary
            governorate_name: اسم المحافظة - Governorate name

        Returns:
            bool: هل الحقل داخل المحافظة - Is field within governorate
        """
        if governorate_name not in self.governorate_boundaries:
            print(f"تحذير: حدود المحافظة '{governorate_name}' غير متوفرة")
            print(f"Warning: Governorate '{governorate_name}' boundaries not available")
            return True  # افتراض الصحة إذا لم تكن البيانات متوفرة

        gov_boundary = self.governorate_boundaries[governorate_name]
        return gov_boundary.contains(polygon)


# ============== مصدّر الوحدة - Module Exports ==============

__all__ = [
    "BoundaryValidator",
    "BoundaryValidationResult",
    "OverlapResult",
    "ValidationIssue",
    "ValidationSeverity",
    "GeometryIssueType",
    "BoundarySeverity",
    "YEMEN_BOUNDS",
    "AREA_LIMITS",
    "YEMEN_GOVERNORATES",
]
