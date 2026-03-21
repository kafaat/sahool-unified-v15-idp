"""
Geofencing Engine - محرك السياج الجغرافي
Core geofencing logic with point-in-polygon and distance calculations
"""

from __future__ import annotations

import math
import uuid
from datetime import UTC, datetime

from .models import (
    AlertSeverity,
    AlertType,
    EquipmentZoneStatus,
    Geofence,
    GeofenceAlert,
    GeofenceType,
    LatLng,
    PositionUpdate,
    ZoneStatus,
)

# Earth radius in meters
EARTH_RADIUS_M = 6371000


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate distance between two points using Haversine formula
    حساب المسافة بين نقطتين باستخدام صيغة Haversine

    Returns distance in meters
    """
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)

    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_M * c


def point_in_polygon(lat: float, lng: float, boundary: list[LatLng]) -> bool:
    """
    Check if a point is inside a polygon using ray casting algorithm
    فحص ما إذا كانت النقطة داخل المضلع

    Returns True if point is inside
    """
    if len(boundary) < 3:
        return False

    n = len(boundary)
    inside = False

    p1_lat = boundary[0].lat
    p1_lng = boundary[0].lng

    for i in range(1, n + 1):
        p2_lat = boundary[i % n].lat
        p2_lng = boundary[i % n].lng

        if lng > min(p1_lng, p2_lng):
            if lng <= max(p1_lng, p2_lng):
                if lat <= max(p1_lat, p2_lat):
                    lat_intersect = p1_lat  # Default for vertical edges
                    if abs(p2_lng - p1_lng) > 1e-10:
                        lat_intersect = (lng - p1_lng) * (p2_lat - p1_lat) / (p2_lng - p1_lng) + p1_lat

                    if p1_lat == p2_lat or lat <= lat_intersect:
                        inside = not inside

        p1_lat, p1_lng = p2_lat, p2_lng

    return inside


def distance_to_polygon_boundary(lat: float, lng: float, boundary: list[LatLng]) -> float:
    """
    Calculate minimum distance from a point to polygon boundary
    حساب أقل مسافة من نقطة إلى حدود المضلع

    Returns distance in meters
    """
    if len(boundary) < 2:
        return float("inf")

    min_distance = float("inf")

    for i in range(len(boundary)):
        p1 = boundary[i]
        p2 = boundary[(i + 1) % len(boundary)]

        # Distance to line segment
        distance = point_to_line_distance(lat, lng, p1.lat, p1.lng, p2.lat, p2.lng)
        min_distance = min(min_distance, distance)

    return min_distance


def point_to_line_distance(px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calculate distance from point to line segment
    حساب المسافة من نقطة إلى قطعة مستقيمة
    """
    # Vector from p1 to p2
    dx = x2 - x1
    dy = y2 - y1

    # If line segment has zero length
    if dx == 0 and dy == 0:
        return haversine_distance(px, py, x1, y1)

    # Parameter t for closest point on line
    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))

    # Closest point on line segment
    closest_x = x1 + t * dx
    closest_y = y1 + t * dy

    return haversine_distance(px, py, closest_x, closest_y)


def check_position_in_geofence(lat: float, lng: float, geofence: Geofence) -> tuple[bool, float]:
    """
    Check if position is inside a geofence
    فحص ما إذا كان الموقع داخل السياج الجغرافي

    Returns (is_inside, distance_to_boundary_m)
    """
    if geofence.center and geofence.radius_m:
        # Circular geofence
        distance = haversine_distance(lat, lng, geofence.center.lat, geofence.center.lng)
        is_inside = distance <= geofence.radius_m
        distance_to_boundary = abs(geofence.radius_m - distance)
        return is_inside, distance_to_boundary

    elif geofence.boundary:
        # Polygon geofence
        is_inside = point_in_polygon(lat, lng, geofence.boundary)
        distance_to_boundary = distance_to_polygon_boundary(lat, lng, geofence.boundary)
        return is_inside, distance_to_boundary

    return False, float("inf")


def calculate_distance_to_boundary(lat: float, lng: float, geofence: Geofence) -> float:
    """
    Calculate distance from position to geofence boundary
    حساب المسافة من الموقع إلى حدود السياج
    """
    _, distance = check_position_in_geofence(lat, lng, geofence)
    return distance


def create_circular_geofence(
    tenant_id: str,
    name: str,
    name_ar: str,
    center_lat: float,
    center_lng: float,
    radius_m: float,
    geofence_type: GeofenceType = GeofenceType.ALLOWED,
    **kwargs,
) -> Geofence:
    """
    Create a circular geofence
    إنشاء سياج جغرافي دائري
    """
    return Geofence(
        id=f"geo_{uuid.uuid4().hex[:8]}",
        tenant_id=tenant_id,
        name=name,
        name_ar=name_ar,
        geofence_type=geofence_type,
        center=LatLng(lat=center_lat, lng=center_lng),
        radius_m=radius_m,
        **kwargs,
    )


def create_polygon_geofence(
    tenant_id: str,
    name: str,
    name_ar: str,
    boundary: list[tuple[float, float]],
    geofence_type: GeofenceType = GeofenceType.ALLOWED,
    **kwargs,
) -> Geofence:
    """
    Create a polygon geofence
    إنشاء سياج جغرافي مضلع

    boundary: list of (lat, lng) tuples
    """
    return Geofence(
        id=f"geo_{uuid.uuid4().hex[:8]}",
        tenant_id=tenant_id,
        name=name,
        name_ar=name_ar,
        geofence_type=geofence_type,
        boundary=[LatLng(lat=lat, lng=lng) for lat, lng in boundary],
        **kwargs,
    )


class GeofenceEngine:
    """
    Main geofencing engine - محرك السياج الجغرافي الرئيسي

    Manages geofences and monitors equipment positions
    """

    def __init__(self):
        self.geofences: dict[str, Geofence] = {}
        self.equipment_positions: dict[str, PositionUpdate] = {}
        self.alerts: list[GeofenceAlert] = []

    def add_geofence(self, geofence: Geofence) -> str:
        """Add a geofence - إضافة سياج جغرافي"""
        self.geofences[geofence.id] = geofence
        return geofence.id

    def remove_geofence(self, geofence_id: str) -> bool:
        """Remove a geofence - إزالة سياج جغرافي"""
        if geofence_id in self.geofences:
            del self.geofences[geofence_id]
            return True
        return False

    def get_geofence(self, geofence_id: str, tenant_id: str | None = None) -> Geofence | None:
        """Get a geofence by ID, optionally validating tenant ownership."""
        geofence = self.geofences.get(geofence_id)
        if geofence and tenant_id and geofence.tenant_id != tenant_id:
            return None
        return geofence

    def get_geofences_for_equipment(self, equipment_id: str) -> list[Geofence]:
        """Get all geofences associated with an equipment"""
        return [
            gf
            for gf in self.geofences.values()
            if equipment_id in gf.equipment_ids or not gf.equipment_ids  # Include tenant-wide geofences
        ]

    def update_position(self, update: PositionUpdate) -> list[GeofenceAlert]:
        """
        Process position update and check against geofences
        معالجة تحديث الموقع وفحصه مقابل السياجات الجغرافية

        Returns list of generated alerts
        """
        equipment_id = update.equipment_id
        tenant_id = update.tenant_id

        # Get previous position
        prev_update = self.equipment_positions.get(equipment_id)

        # Store current position
        self.equipment_positions[equipment_id] = update

        # Get applicable geofences
        geofences = [
            gf
            for gf in self.geofences.values()
            if gf.tenant_id == tenant_id and gf.is_active and (equipment_id in gf.equipment_ids or not gf.equipment_ids)
        ]

        generated_alerts = []

        for geofence in geofences:
            # Check current position
            is_inside, distance_to_boundary = check_position_in_geofence(update.lat, update.lng, geofence)

            # Check previous position if available
            was_inside = None
            if prev_update:
                was_inside, _ = check_position_in_geofence(prev_update.lat, prev_update.lng, geofence)

            # Generate alerts based on transitions
            alert = self._check_for_alert(update, geofence, is_inside, was_inside, distance_to_boundary)
            if alert:
                self.alerts.append(alert)
                generated_alerts.append(alert)

            # Check speed limit
            if geofence.max_speed_kmh and update.speed_kmh:
                if update.speed_kmh > geofence.max_speed_kmh and is_inside:
                    speed_alert = self._generate_speed_alert(update, geofence)
                    self.alerts.append(speed_alert)
                    generated_alerts.append(speed_alert)

        # Check for potential theft (movement outside operating hours or outside all allowed zones)
        theft_alert = self._check_for_theft(update, prev_update, geofences)
        if theft_alert:
            self.alerts.append(theft_alert)
            generated_alerts.append(theft_alert)

        return generated_alerts

    def _check_for_alert(
        self,
        update: PositionUpdate,
        geofence: Geofence,
        is_inside: bool,
        was_inside: bool | None,
        distance_to_boundary: float,
    ) -> GeofenceAlert | None:
        """Check if an alert should be generated"""

        # Exit alert
        if geofence.alert_on_exit and was_inside is True and not is_inside:
            return self._generate_exit_alert(update, geofence, distance_to_boundary)

        # Entry alert
        if geofence.alert_on_entry and was_inside is False and is_inside:
            return self._generate_entry_alert(update, geofence)

        # Approaching boundary (within buffer zone and heading out)
        if is_inside and distance_to_boundary < geofence.buffer_distance_m and geofence.alert_on_exit:
            # Could add approaching alert here
            pass

        return None

    def _generate_exit_alert(
        self,
        update: PositionUpdate,
        geofence: Geofence,
        distance_to_boundary: float,
    ) -> GeofenceAlert:
        """Generate exit alert"""
        severity = AlertSeverity.HIGH
        if geofence.geofence_type == GeofenceType.FARM_BOUNDARY:
            severity = AlertSeverity.CRITICAL

        return GeofenceAlert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            tenant_id=update.tenant_id,
            equipment_id=update.equipment_id,
            equipment_name="",  # Will be filled by service
            equipment_name_ar="",
            alert_type=AlertType.EXIT,
            severity=severity,
            timestamp=update.timestamp,
            geofence_id=geofence.id,
            geofence_name=geofence.name,
            geofence_name_ar=geofence.name_ar,
            lat=update.lat,
            lng=update.lng,
            speed_kmh=update.speed_kmh,
            distance_to_boundary_m=distance_to_boundary,
            title_en=f"🚨 Equipment Left Zone: {geofence.name}",
            title_ar=f"🚨 المعدة غادرت المنطقة: {geofence.name_ar}",
            message_en=f"Equipment has exited the allowed zone '{geofence.name}'. "
            f"Current distance from boundary: {distance_to_boundary:.0f}m",
            message_ar=f"المعدة غادرت المنطقة المسموح بها '{geofence.name_ar}'. "
            f"المسافة الحالية من الحدود: {distance_to_boundary:.0f}م",
            channels=geofence.alert_channels,
        )

    def _generate_entry_alert(
        self,
        update: PositionUpdate,
        geofence: Geofence,
    ) -> GeofenceAlert:
        """Generate entry alert"""
        severity = AlertSeverity.MEDIUM
        if geofence.geofence_type == GeofenceType.RESTRICTED:
            severity = AlertSeverity.HIGH
        elif geofence.geofence_type == GeofenceType.SENSITIVE:
            severity = AlertSeverity.CRITICAL

        return GeofenceAlert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            tenant_id=update.tenant_id,
            equipment_id=update.equipment_id,
            equipment_name="",
            equipment_name_ar="",
            alert_type=AlertType.ENTRY,
            severity=severity,
            timestamp=update.timestamp,
            geofence_id=geofence.id,
            geofence_name=geofence.name,
            geofence_name_ar=geofence.name_ar,
            lat=update.lat,
            lng=update.lng,
            speed_kmh=update.speed_kmh,
            title_en=f"⚠️ Equipment Entered Zone: {geofence.name}",
            title_ar=f"⚠️ المعدة دخلت المنطقة: {geofence.name_ar}",
            message_en=f"Equipment has entered the '{geofence.name}' zone.",
            message_ar=f"المعدة دخلت منطقة '{geofence.name_ar}'.",
            channels=geofence.alert_channels,
        )

    def _generate_speed_alert(
        self,
        update: PositionUpdate,
        geofence: Geofence,
    ) -> GeofenceAlert:
        """Generate speed limit violation alert"""
        return GeofenceAlert(
            alert_id=f"alert_{uuid.uuid4().hex[:8]}",
            tenant_id=update.tenant_id,
            equipment_id=update.equipment_id,
            equipment_name="",
            equipment_name_ar="",
            alert_type=AlertType.SPEEDING,
            severity=AlertSeverity.MEDIUM,
            timestamp=update.timestamp,
            geofence_id=geofence.id,
            geofence_name=geofence.name,
            geofence_name_ar=geofence.name_ar,
            lat=update.lat,
            lng=update.lng,
            speed_kmh=update.speed_kmh,
            title_en=f"⚡ Speed Limit Exceeded in {geofence.name}",
            title_ar=f"⚡ تجاوز حد السرعة في {geofence.name_ar}",
            message_en=f"Equipment traveling at {update.speed_kmh:.1f} km/h. Limit: {geofence.max_speed_kmh} km/h",
            message_ar=f"المعدة تسير بسرعة {update.speed_kmh:.1f} كم/س. الحد: {geofence.max_speed_kmh} كم/س",
            channels=["push"],  # Speed alerts usually less urgent
        )

    def _check_for_theft(
        self,
        update: PositionUpdate,
        prev_update: PositionUpdate | None,
        geofences: list[Geofence],
    ) -> GeofenceAlert | None:
        """
        Check for potential theft indicators
        فحص مؤشرات السرقة المحتملة

        Theft indicators:
        - Movement outside all allowed zones
        - Movement during non-operating hours
        - Rapid movement away from farm
        """
        if not prev_update:
            return None

        # Check if currently outside ALL allowed zones
        allowed_zones = [gf for gf in geofences if gf.geofence_type == GeofenceType.ALLOWED]
        farm_boundaries = [gf for gf in geofences if gf.geofence_type == GeofenceType.FARM_BOUNDARY]

        in_any_allowed = any(check_position_in_geofence(update.lat, update.lng, gf)[0] for gf in allowed_zones)

        in_farm = any(check_position_in_geofence(update.lat, update.lng, gf)[0] for gf in farm_boundaries)

        # Check movement
        distance_moved = haversine_distance(prev_update.lat, prev_update.lng, update.lat, update.lng)
        time_diff = (update.timestamp - prev_update.timestamp).total_seconds() / 3600  # hours
        if time_diff > 0:
            speed_kmh = (distance_moved / 1000) / time_diff
        else:
            speed_kmh = 0

        # Theft conditions
        is_suspicious = False
        reasons = []

        # Outside farm boundary with significant movement
        if farm_boundaries and not in_farm and distance_moved > 100:
            is_suspicious = True
            reasons.append("Outside farm boundary")

        # Moving at high speed outside operating hours
        # (simplified - in production, check operating hours from geofence settings)
        hour = update.timestamp.hour
        if (hour < 6 or hour > 22) and speed_kmh > 30 and not in_any_allowed:
            is_suspicious = True
            reasons.append("High-speed movement outside operating hours")

        # Rapid movement away from all zones
        if not in_any_allowed and speed_kmh > 50:
            is_suspicious = True
            reasons.append("Rapid movement outside allowed zones")

        if is_suspicious:
            return GeofenceAlert(
                alert_id=f"alert_{uuid.uuid4().hex[:8]}",
                tenant_id=update.tenant_id,
                equipment_id=update.equipment_id,
                equipment_name="",
                equipment_name_ar="",
                alert_type=AlertType.THEFT,
                severity=AlertSeverity.CRITICAL,
                timestamp=update.timestamp,
                geofence_id="theft_detection",
                geofence_name="Theft Detection",
                geofence_name_ar="كشف السرقة",
                lat=update.lat,
                lng=update.lng,
                speed_kmh=update.speed_kmh or speed_kmh,
                title_en="🚨 THEFT ALERT - Unauthorized Movement Detected",
                title_ar="🚨 تنبيه سرقة - تم كشف حركة غير مصرح بها",
                message_en=f"Suspicious equipment movement detected! "
                f"Reasons: {', '.join(reasons)}. "
                f"Current speed: {speed_kmh:.1f} km/h. "
                f"Location: ({update.lat:.6f}, {update.lng:.6f})",
                message_ar=f"تم كشف حركة مشبوهة للمعدة! "
                f"الأسباب: {', '.join(reasons)}. "
                f"السرعة الحالية: {speed_kmh:.1f} كم/س. "
                f"الموقع: ({update.lat:.6f}, {update.lng:.6f})",
                channels=["push", "sms", "whatsapp", "call"],  # Use all channels for theft
            )

        return None

    def get_equipment_status(
        self,
        equipment_id: str,
        equipment_name: str,
    ) -> EquipmentZoneStatus | None:
        """
        Get current status of equipment relative to all geofences
        الحصول على حالة المعدة بالنسبة لجميع السياجات
        """
        update = self.equipment_positions.get(equipment_id)
        if not update:
            return None

        zones = []
        is_within_allowed = False
        is_in_restricted = False
        nearest_distance = float("inf")

        for geofence in self.geofences.values():
            is_inside, distance = check_position_in_geofence(update.lat, update.lng, geofence)

            status = ZoneStatus.INSIDE if is_inside else ZoneStatus.OUTSIDE

            zones.append(
                {
                    "geofence_id": geofence.id,
                    "geofence_name": geofence.name,
                    "geofence_name_ar": geofence.name_ar,
                    "geofence_type": geofence.geofence_type.value,
                    "status": status.value,
                    "distance_m": round(distance, 1),
                }
            )

            if is_inside and geofence.geofence_type == GeofenceType.ALLOWED:
                is_within_allowed = True
            if is_inside and geofence.geofence_type == GeofenceType.RESTRICTED:
                is_in_restricted = True
            if distance < nearest_distance:
                nearest_distance = distance

        # Get active alerts for this equipment
        active_alerts = [
            alert.alert_id for alert in self.alerts if alert.equipment_id == equipment_id and not alert.acknowledged
        ]

        return EquipmentZoneStatus(
            equipment_id=equipment_id,
            equipment_name=equipment_name,
            timestamp=update.timestamp,
            lat=update.lat,
            lng=update.lng,
            zones=zones,
            is_within_allowed_zones=is_within_allowed,
            is_in_restricted_zone=is_in_restricted,
            nearest_boundary_distance_m=round(nearest_distance, 1) if nearest_distance != float("inf") else None,
            active_alerts=active_alerts,
        )

    def acknowledge_alert(
        self,
        alert_id: str,
        acknowledged_by: str,
        tenant_id: str | None = None,
    ) -> bool:
        """Acknowledge an alert, optionally validating tenant ownership."""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                if tenant_id and alert.tenant_id != tenant_id:
                    return False
                alert.acknowledged = True
                alert.acknowledged_by = acknowledged_by
                alert.acknowledged_at = datetime.now(UTC)
                return True
        return False

    def get_unacknowledged_alerts(
        self,
        tenant_id: str,
        equipment_id: str | None = None,
    ) -> list[GeofenceAlert]:
        """Get all unacknowledged alerts"""
        alerts = [alert for alert in self.alerts if alert.tenant_id == tenant_id and not alert.acknowledged]
        if equipment_id:
            alerts = [a for a in alerts if a.equipment_id == equipment_id]
        return alerts
