"""
Boundary Sharing Module | وحدة مشاركة الحدود

This module provides functionality for sharing field boundaries between
users/neighbors, including permission management, approval workflows,
and conflict detection.

Author: SAHOOL Platform
Version: 16.0.0
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

from .geometry import (
    calculate_overlap_area,
    haversine_distance,
    polygons_overlap,
)
from .models import (
    BoundaryConflict,
    BoundaryShareRequest,
    ConflictType,
    FieldBoundary,
    Polygon,
)


class PermissionLevel(StrEnum):
    """
    Boundary permission levels | مستويات صلاحيات الحدود

    Attributes:
        VIEW: Can view boundary | يمكن عرض الحدود
        COMMENT: Can view and comment | يمكن العرض والتعليق
        EDIT: Can suggest edits | يمكن اقتراح تعديلات
        APPROVE: Can approve changes | يمكن الموافقة على التغييرات
        ADMIN: Full control | تحكم كامل
    """

    VIEW = "view"
    COMMENT = "comment"
    EDIT = "edit"
    APPROVE = "approve"
    ADMIN = "admin"


class ShareStatus(StrEnum):
    """
    Share request status | حالة طلب المشاركة
    """

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"
    REVOKED = "revoked"


class ApprovalStatus(StrEnum):
    """
    Boundary approval status | حالة الموافقة على الحدود
    """

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_CHANGES = "requires_changes"


@dataclass
class SharePermission:
    """
    Permission record for boundary sharing.
    سجل صلاحيات مشاركة الحدود.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    boundary_id: str = ""
    user_id: str = ""
    granted_by: str = ""
    permission_level: PermissionLevel = PermissionLevel.VIEW

    # Validity | الصلاحية
    granted_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    is_active: bool = True

    # Restrictions | القيود
    can_reshare: bool = False
    max_reshare_level: PermissionLevel | None = None


@dataclass
class ApprovalRequest:
    """
    Request for boundary approval from neighbor.
    طلب الموافقة على الحدود من الجار.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    boundary_id: str = ""
    requester_id: str = ""
    approver_id: str = ""

    # Request details | تفاصيل الطلب
    message: str | None = None
    message_ar: str | None = None

    # Status | الحالة
    status: ApprovalStatus = ApprovalStatus.PENDING
    response_message: str | None = None
    response_message_ar: str | None = None

    # Requested changes | التغييرات المطلوبة
    requested_changes: dict[str, Any] | None = None

    # Timestamps | الطوابع الزمنية
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    responded_at: datetime | None = None
    expires_at: datetime | None = None


@dataclass
class ConflictResolution:
    """
    Resolution record for boundary conflict.
    سجل حل تعارض الحدود.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conflict_id: str = ""

    # Resolution details | تفاصيل الحل
    resolution_type: str = ""  # mediated, agreed, surveyed, legal
    resolution_description: str | None = None
    resolution_description_ar: str | None = None

    # New boundary (if applicable) | الحد الجديد
    agreed_boundary: Polygon | None = None

    # Parties | الأطراف
    party_a_approved: bool = False
    party_b_approved: bool = False
    mediator_id: str | None = None

    # Evidence | الأدلة
    evidence_urls: list[str] = field(default_factory=list)
    survey_reference: str | None = None

    # Timestamps | الطوابع الزمنية
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    finalized_at: datetime | None = None


class BoundarySharingManager:
    """
    Manager for boundary sharing operations.
    مدير عمليات مشاركة الحدود.

    Handles sharing, permissions, approvals, and conflict detection
    between field boundaries and their neighbors.
    """

    def __init__(self, tenant_id: str):
        """Initialize the sharing manager.

        Args:
            tenant_id: Tenant ID for isolation (required). All operations are scoped to this tenant.
        """
        if not tenant_id:
            raise ValueError("tenant_id is required for BoundarySharingManager")
        self.tenant_id = tenant_id
        # In-memory storage for demo; replace with database in production
        self._permissions: dict[str, list[SharePermission]] = {}
        self._share_requests: dict[str, BoundaryShareRequest] = {}
        self._approval_requests: dict[str, ApprovalRequest] = {}
        self._conflicts: dict[str, BoundaryConflict] = {}
        self._resolutions: dict[str, ConflictResolution] = {}

    # -------------------------------------------------------------------------
    # Sharing Operations | عمليات المشاركة
    # -------------------------------------------------------------------------

    def create_share_request(
        self,
        boundary: FieldBoundary,
        recipient_id: str,
        permission_level: PermissionLevel = PermissionLevel.VIEW,
        message: str | None = None,
        message_ar: str | None = None,
        expires_in_days: int = 30,
    ) -> BoundaryShareRequest:
        """
        Create a boundary share request.
        إنشاء طلب مشاركة حدود.

        Args:
            boundary: Boundary to share
            recipient_id: User ID to share with
            permission_level: Permission level to grant
            message: Optional message (English)
            message_ar: Optional message (Arabic)
            expires_in_days: Days until request expires

        Returns:
            Created share request
        """
        # Strict tenant isolation: fail closed if tenant_id is missing or mismatched
        if not isinstance(boundary, FieldBoundary):
            raise TypeError("boundary must be a FieldBoundary instance")
        if not getattr(boundary, "tenant_id", None):
            raise ValueError("Boundary is missing tenant_id — cannot verify isolation")
        if boundary.tenant_id != self.tenant_id:
            raise ValueError("Boundary does not belong to this tenant")

        request = BoundaryShareRequest(
            boundary_id=boundary.id,
            requester_id=boundary.owner_id,
            recipient_id=recipient_id,
            message=message,
            message_ar=message_ar,
            permission_level=permission_level.value,
            status=ShareStatus.PENDING.value,
            expires_at=datetime.now(UTC) + timedelta(days=expires_in_days),
        )

        self._share_requests[request.id] = request
        return request

    def accept_share_request(
        self,
        request_id: str,
        user_id: str,
        response_message: str | None = None,
        response_message_ar: str | None = None,
    ) -> tuple[bool, str, SharePermission | None]:
        """
        Accept a share request.
        قبول طلب مشاركة.

        Args:
            request_id: Share request ID
            user_id: User accepting (must be recipient)
            response_message: Optional response (English)
            response_message_ar: Optional response (Arabic)

        Returns:
            Tuple of (success, message, permission if granted)
        """
        request = self._share_requests.get(request_id)
        if not request:
            return (False, "Request not found | الطلب غير موجود", None)

        if request.recipient_id != user_id:
            return (False, "Not authorized | غير مصرح", None)

        if request.status != ShareStatus.PENDING.value:
            return (False, f"Request is {request.status} | الطلب {request.status}", None)

        if request.expires_at and datetime.now(UTC) > request.expires_at:
            request.status = ShareStatus.EXPIRED.value
            return (False, "Request expired | انتهت صلاحية الطلب", None)

        # Update request
        request.status = ShareStatus.ACCEPTED.value
        request.responded_at = datetime.now(UTC)
        request.response_message = response_message
        request.response_message_ar = response_message_ar

        # Grant permission
        permission = self._grant_permission(
            boundary_id=request.boundary_id,
            user_id=user_id,
            granted_by=request.requester_id,
            level=PermissionLevel(request.permission_level),
        )

        return (True, "Share accepted | تم قبول المشاركة", permission)

    def reject_share_request(
        self,
        request_id: str,
        user_id: str,
        response_message: str | None = None,
        response_message_ar: str | None = None,
    ) -> tuple[bool, str]:
        """
        Reject a share request.
        رفض طلب مشاركة.
        """
        request = self._share_requests.get(request_id)
        if not request:
            return (False, "Request not found | الطلب غير موجود")

        if request.recipient_id != user_id:
            return (False, "Not authorized | غير مصرح")

        request.status = ShareStatus.REJECTED.value
        request.responded_at = datetime.now(UTC)
        request.response_message = response_message
        request.response_message_ar = response_message_ar

        return (True, "Share rejected | تم رفض المشاركة")

    def revoke_share(self, boundary_id: str, user_id: str, revoker_id: str) -> tuple[bool, str]:
        """
        Revoke a user's access to a boundary.
        إلغاء وصول مستخدم إلى حدود.

        Args:
            boundary_id: Boundary ID
            user_id: User whose access to revoke
            revoker_id: User performing revocation (must be owner or admin)

        Returns:
            Tuple of (success, message)
        """
        permissions = self._permissions.get(boundary_id, [])

        for perm in permissions:
            if perm.user_id == user_id and perm.is_active:
                # Verify revoker has permission
                if revoker_id != perm.granted_by:
                    revoker_perm = self.get_permission(boundary_id, revoker_id)
                    if not revoker_perm or revoker_perm.permission_level != PermissionLevel.ADMIN:
                        return (False, "Not authorized to revoke | غير مصرح بالإلغاء")

                perm.is_active = False
                return (True, "Access revoked | تم إلغاء الوصول")

        return (False, "Permission not found | الصلاحية غير موجودة")

    def _grant_permission(
        self,
        boundary_id: str,
        user_id: str,
        granted_by: str,
        level: PermissionLevel,
        expires_at: datetime | None = None,
    ) -> SharePermission:
        """Grant permission to user."""
        permission = SharePermission(
            boundary_id=boundary_id,
            user_id=user_id,
            granted_by=granted_by,
            permission_level=level,
            expires_at=expires_at,
            can_reshare=level in [PermissionLevel.ADMIN, PermissionLevel.APPROVE],
        )

        if boundary_id not in self._permissions:
            self._permissions[boundary_id] = []

        self._permissions[boundary_id].append(permission)
        return permission

    def get_permission(self, boundary_id: str, user_id: str) -> SharePermission | None:
        """Get user's permission for a boundary."""
        permissions = self._permissions.get(boundary_id, [])

        for perm in permissions:
            if perm.user_id == user_id and perm.is_active:
                # Check expiry
                if perm.expires_at and datetime.now(UTC) > perm.expires_at:
                    perm.is_active = False
                    continue
                return perm

        return None

    def has_permission(self, boundary_id: str, user_id: str, required_level: PermissionLevel) -> bool:
        """Check if user has required permission level."""
        permission = self.get_permission(boundary_id, user_id)

        if not permission:
            return False

        # Permission hierarchy
        hierarchy = [
            PermissionLevel.VIEW,
            PermissionLevel.COMMENT,
            PermissionLevel.EDIT,
            PermissionLevel.APPROVE,
            PermissionLevel.ADMIN,
        ]

        user_level_idx = hierarchy.index(permission.permission_level)
        required_level_idx = hierarchy.index(required_level)

        return user_level_idx >= required_level_idx

    def list_shared_with(self, boundary_id: str) -> list[SharePermission]:
        """List all users the boundary is shared with."""
        permissions = self._permissions.get(boundary_id, [])
        return [p for p in permissions if p.is_active]

    def list_accessible_boundaries(self, user_id: str) -> list[tuple[str, SharePermission]]:
        """List all boundaries accessible to a user."""
        result = []

        for boundary_id, permissions in self._permissions.items():
            for perm in permissions:
                if perm.user_id == user_id and perm.is_active:
                    if perm.expires_at and datetime.now(UTC) > perm.expires_at:
                        perm.is_active = False
                        continue
                    result.append((boundary_id, perm))

        return result

    # -------------------------------------------------------------------------
    # Approval Workflow | سير عمل الموافقة
    # -------------------------------------------------------------------------

    def request_approval(
        self,
        boundary: FieldBoundary,
        neighbor_id: str,
        message: str | None = None,
        message_ar: str | None = None,
        expires_in_days: int = 14,
    ) -> ApprovalRequest:
        """
        Request approval from a neighbor for boundary.
        طلب موافقة الجار على الحدود.

        Args:
            boundary: Boundary requiring approval
            neighbor_id: Neighbor user ID
            message: Optional message (English)
            message_ar: Optional message (Arabic)
            expires_in_days: Days until request expires

        Returns:
            Created approval request
        """
        request = ApprovalRequest(
            boundary_id=boundary.id,
            requester_id=boundary.owner_id,
            approver_id=neighbor_id,
            message=message,
            message_ar=message_ar,
            expires_at=datetime.now(UTC) + timedelta(days=expires_in_days),
        )

        self._approval_requests[request.id] = request
        return request

    def approve_boundary(
        self,
        request_id: str,
        user_id: str,
        response_message: str | None = None,
        response_message_ar: str | None = None,
    ) -> tuple[bool, str]:
        """
        Approve a boundary.
        الموافقة على الحدود.
        """
        request = self._approval_requests.get(request_id)
        if not request:
            return (False, "Request not found | الطلب غير موجود")

        if request.approver_id != user_id:
            return (False, "Not authorized | غير مصرح")

        if request.status != ApprovalStatus.PENDING.value:
            return (False, f"Request already {request.status}")

        request.status = ApprovalStatus.APPROVED.value
        request.responded_at = datetime.now(UTC)
        request.response_message = response_message
        request.response_message_ar = response_message_ar

        return (True, "Boundary approved | تم الموافقة على الحدود")

    def reject_boundary(
        self,
        request_id: str,
        user_id: str,
        response_message: str | None = None,
        response_message_ar: str | None = None,
        requested_changes: dict[str, Any] | None = None,
    ) -> tuple[bool, str]:
        """
        Reject a boundary with optional change requests.
        رفض الحدود مع طلبات تغيير اختيارية.
        """
        request = self._approval_requests.get(request_id)
        if not request:
            return (False, "Request not found | الطلب غير موجود")

        if request.approver_id != user_id:
            return (False, "Not authorized | غير مصرح")

        if requested_changes:
            request.status = ApprovalStatus.REQUIRES_CHANGES.value
            request.requested_changes = requested_changes
        else:
            request.status = ApprovalStatus.REJECTED.value

        request.responded_at = datetime.now(UTC)
        request.response_message = response_message
        request.response_message_ar = response_message_ar

        status_msg = "Changes requested" if requested_changes else "Rejected"
        return (True, f"Boundary {status_msg} | الحدود {status_msg}")

    def get_pending_approvals(self, user_id: str) -> list[ApprovalRequest]:
        """Get all pending approval requests for a user."""
        return [
            req
            for req in self._approval_requests.values()
            if req.approver_id == user_id and req.status == ApprovalStatus.PENDING.value
        ]

    # -------------------------------------------------------------------------
    # Conflict Detection | اكتشاف التعارضات
    # -------------------------------------------------------------------------

    def detect_conflicts(
        self,
        boundary: FieldBoundary,
        neighbor_boundaries: list[FieldBoundary],
        overlap_threshold_sqm: float = 10.0,
        gap_threshold_m: float = 1.0,
    ) -> list[BoundaryConflict]:
        """
        Detect conflicts between a boundary and its neighbors.
        اكتشاف التعارضات بين الحدود وجيرانها.

        Args:
            boundary: Boundary to check
            neighbor_boundaries: List of neighboring boundaries
            overlap_threshold_sqm: Minimum overlap to report (m2)
            gap_threshold_m: Gap distance to report (m)

        Returns:
            List of detected conflicts
        """
        conflicts = []

        if not isinstance(boundary.geometry, Polygon):
            return conflicts

        boundary_coords = boundary.geometry.exterior_ring

        for neighbor in neighbor_boundaries:
            if boundary.id == neighbor.id:
                continue

            if not isinstance(neighbor.geometry, Polygon):
                continue

            neighbor_coords = neighbor.geometry.exterior_ring

            # Check for overlap
            if polygons_overlap(boundary_coords, neighbor_coords):
                overlap_area = calculate_overlap_area(boundary_coords, neighbor_coords)

                if overlap_area >= overlap_threshold_sqm:
                    conflict = BoundaryConflict(
                        boundary_id_a=boundary.id,
                        boundary_id_b=neighbor.id,
                        field_id_a=boundary.field_id,
                        field_id_b=neighbor.field_id,
                        owner_id_a=boundary.owner_id,
                        owner_id_b=neighbor.owner_id,
                        conflict_type=ConflictType.OVERLAP,
                        overlap_area_sqm=overlap_area,
                        severity=self._classify_conflict_severity(overlap_area),
                    )
                    conflicts.append(conflict)
                    self._conflicts[conflict.id] = conflict
            else:
                # Check for gaps (near but not touching)
                min_distance = self._calculate_min_boundary_distance(boundary_coords, neighbor_coords)

                if min_distance <= gap_threshold_m:
                    conflict = BoundaryConflict(
                        boundary_id_a=boundary.id,
                        boundary_id_b=neighbor.id,
                        field_id_a=boundary.field_id,
                        field_id_b=neighbor.field_id,
                        owner_id_a=boundary.owner_id,
                        owner_id_b=neighbor.owner_id,
                        conflict_type=ConflictType.GAP,
                        gap_distance_m=min_distance,
                        severity="low",
                    )
                    conflicts.append(conflict)
                    self._conflicts[conflict.id] = conflict

        return conflicts

    def _calculate_min_boundary_distance(
        self, coords1: list[tuple[float, float]], coords2: list[tuple[float, float]]
    ) -> float:
        """Calculate minimum distance between two boundaries."""
        min_dist = float("inf")

        for p1 in coords1:
            for p2 in coords2:
                dist = haversine_distance(p1[0], p1[1], p2[0], p2[1])
                min_dist = min(min_dist, dist)

        return min_dist

    def _classify_conflict_severity(self, overlap_area_sqm: float) -> str:
        """Classify conflict severity based on overlap area."""
        if overlap_area_sqm > 1000:  # > 0.1 hectare
            return "high"
        elif overlap_area_sqm > 100:  # > 0.01 hectare
            return "medium"
        else:
            return "low"

    def get_conflicts(
        self,
        boundary_id: str | None = None,
        user_id: str | None = None,
        include_resolved: bool = False,
    ) -> list[BoundaryConflict]:
        """
        Get conflicts filtered by criteria.
        الحصول على التعارضات مفلترة حسب المعايير.
        """
        conflicts = list(self._conflicts.values())

        if boundary_id:
            conflicts = [c for c in conflicts if c.boundary_id_a == boundary_id or c.boundary_id_b == boundary_id]

        if user_id:
            conflicts = [c for c in conflicts if c.owner_id_a == user_id or c.owner_id_b == user_id]

        if not include_resolved:
            conflicts = [c for c in conflicts if not c.is_resolved]

        return conflicts

    # -------------------------------------------------------------------------
    # Conflict Resolution | حل التعارضات
    # -------------------------------------------------------------------------

    def create_resolution(
        self,
        conflict_id: str,
        resolution_type: str,
        description: str | None = None,
        description_ar: str | None = None,
        agreed_boundary: Polygon | None = None,
        mediator_id: str | None = None,
    ) -> ConflictResolution:
        """
        Create a conflict resolution record.
        إنشاء سجل حل التعارض.

        Args:
            conflict_id: Conflict to resolve
            resolution_type: Type of resolution (mediated, agreed, surveyed, legal)
            description: Resolution description (English)
            description_ar: Resolution description (Arabic)
            agreed_boundary: New agreed boundary if applicable
            mediator_id: Mediator user ID if applicable

        Returns:
            Created resolution record
        """
        resolution = ConflictResolution(
            conflict_id=conflict_id,
            resolution_type=resolution_type,
            resolution_description=description,
            resolution_description_ar=description_ar,
            agreed_boundary=agreed_boundary,
            mediator_id=mediator_id,
        )

        self._resolutions[resolution.id] = resolution
        return resolution

    def approve_resolution(self, resolution_id: str, user_id: str, is_party_a: bool) -> tuple[bool, str]:
        """
        Approve a resolution by one of the parties.
        الموافقة على الحل من قبل أحد الأطراف.
        """
        resolution = self._resolutions.get(resolution_id)
        if not resolution:
            return (False, "Resolution not found | الحل غير موجود")

        conflict = self._conflicts.get(resolution.conflict_id)
        if not conflict:
            return (False, "Conflict not found | التعارض غير موجود")

        # Verify user is a party
        if is_party_a:
            if user_id != conflict.owner_id_a:
                return (False, "Not authorized | غير مصرح")
            resolution.party_a_approved = True
        else:
            if user_id != conflict.owner_id_b:
                return (False, "Not authorized | غير مصرح")
            resolution.party_b_approved = True

        # Check if fully resolved
        if resolution.party_a_approved and resolution.party_b_approved:
            resolution.finalized_at = datetime.now(UTC)
            conflict.is_resolved = True
            conflict.resolved_at = datetime.now(UTC)
            conflict.resolved_by = resolution.mediator_id or "parties"

            return (True, "Conflict resolved | تم حل التعارض")

        return (True, "Approval recorded | تم تسجيل الموافقة")

    def get_resolution(self, conflict_id: str) -> ConflictResolution | None:
        """Get resolution for a conflict."""
        for resolution in self._resolutions.values():
            if resolution.conflict_id == conflict_id:
                return resolution
        return None


# -------------------------------------------------------------------------
# PostGIS Integration Helpers | وظائف مساعدة للتكامل مع PostGIS
# -------------------------------------------------------------------------


def generate_postgis_conflict_detection_query(
    table: str,
    boundary_id: str,
    tenant_id: str,
    overlap_threshold_sqm: float = 10.0,
    geometry_column: str = "geometry",
) -> str:
    """
    Generate PostGIS query to detect boundary conflicts.
    إنشاء استعلام PostGIS لاكتشاف تعارضات الحدود.

    Args:
        table: Table name
        boundary_id: Boundary to check
        tenant_id: Tenant ID for scoping
        overlap_threshold_sqm: Minimum overlap area to report
        geometry_column: Geometry column name

    Returns:
        SQL query string
    """
    g = geometry_column
    threshold = overlap_threshold_sqm
    # SECURITY: Use parameterized placeholders ($1, $2) for user-provided values
    # Table/column names are application constants, not user input
    sql = f"""
    WITH target AS (
        SELECT id, field_id, owner_id, {g}
        FROM {table}
        WHERE id = $1 AND tenant_id = $2
    ),
    neighbors AS (
        SELECT
            b.id,
            b.field_id,
            b.owner_id,
            b.{g},
            ST_Intersects(t.{g}, b.{g}) AS overlaps,
            ST_Area(ST_Intersection(t.{g}, b.{g})::geography) AS overlap_area_sqm,
            ST_Distance(t.{g}::geography, b.{g}::geography) AS distance_m
        FROM {table} b
        CROSS JOIN target t
        WHERE b.id != t.id
            AND b.tenant_id = $2
            AND (
                ST_Intersects(t.{g}, b.{g})
                OR ST_DWithin(t.{g}::geography, b.{g}::geography, 10)
            )
    )
    SELECT
        $1 AS boundary_id_a,
        n.id AS boundary_id_b,
        n.field_id AS field_id_b,
        n.owner_id AS owner_id_b,
        CASE
            WHEN n.overlaps AND n.overlap_area_sqm > {threshold} THEN 'overlap'
            WHEN NOT n.overlaps AND n.distance_m < 1.0 THEN 'gap'
            ELSE 'none'
        END AS conflict_type,
        n.overlap_area_sqm,
        n.distance_m AS gap_distance_m,
        ST_AsGeoJSON(ST_Intersection(
            (SELECT {g} FROM target),
            n.{g}
        )) AS conflict_geometry
    FROM neighbors n
    WHERE (n.overlaps AND n.overlap_area_sqm > {threshold})
        OR (NOT n.overlaps AND n.distance_m < 1.0)
    ORDER BY n.overlap_area_sqm DESC NULLS LAST;
    """  # nosec B608 - table/column names are application constants; user values use $1/$2 params
    return sql


def generate_postgis_shared_boundaries_query(
    permissions_table: str, boundaries_table: str, user_id: str, geometry_column: str = "geometry"
) -> str:
    """
    Generate PostGIS query to get all boundaries shared with a user.
    إنشاء استعلام PostGIS للحصول على جميع الحدود المشتركة مع مستخدم.
    """
    # SECURITY: Use parameterized placeholder ($1) for user_id to prevent SQL injection
    sql = f"""
    SELECT
        b.id,
        b.field_id,
        b.name,
        b.name_ar,
        b.boundary_type,
        b.status,
        b.area_hectares,
        b.perimeter_meters,
        ST_AsGeoJSON(b.{geometry_column}) AS geometry,
        p.permission_level,
        p.granted_at,
        p.expires_at
    FROM {permissions_table} p
    JOIN {boundaries_table} b ON p.boundary_id = b.id
    WHERE p.user_id = $1
        AND p.is_active = true
        AND (p.expires_at IS NULL OR p.expires_at > NOW())
    ORDER BY p.granted_at DESC;
    """  # nosec B608 - table/column names are application constants; user_id uses $1 param
    return sql


def generate_postgis_neighbor_notification_query(
    boundaries_table: str,
    boundary_id: str,
    buffer_m: float = 50.0,
    geometry_column: str = "geometry",
) -> str:
    """
    Generate PostGIS query to find neighbors to notify about boundary changes.
    إنشاء استعلام PostGIS للعثور على الجيران لإبلاغهم بتغييرات الحدود.

    Security Note: boundary_id must be a validated UUID from the database,
    not raw user input. Table and column names are application constants.
    """
    import re

    # Validate boundary_id is a UUID format to prevent SQL injection
    uuid_pattern = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
    if not uuid_pattern.match(boundary_id):
        raise ValueError("Invalid boundary_id format: must be UUID")

    g = geometry_column
    tbl = boundaries_table
    bid = boundary_id
    # SECURITY: Use parameterized placeholder ($1) for boundary_id
    sql = f"""
    SELECT DISTINCT
        b.owner_id,
        b.field_id,
        b.name,
        ST_Distance(
            (SELECT {g} FROM {tbl} WHERE id = $1)::geography,
            b.{g}::geography
        ) AS distance_m
    FROM {tbl} b
    WHERE b.id != $1
        AND ST_DWithin(
            (SELECT {g} FROM {tbl} WHERE id = $1)::geography,
            b.{g}::geography,
            {buffer_m}
        )
    ORDER BY distance_m ASC;
    """  # nosec B608 - table/column names are application constants; boundary_id uses $1 param
    return sql
