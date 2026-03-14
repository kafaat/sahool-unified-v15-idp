"""
Conflict Resolution Strategies
==============================
استراتيجيات حل التعارضات

Conflict resolution strategies for offline sync including last-write-wins,
server-wins, client-wins, field-level merge, and manual merge.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Callable

from .models import (
    SYNC_ERRORS,
    SYNC_MESSAGES,
    BilingualMessage,
    ConflictResolutionStrategy,
    ConflictType,
    EntityType,
    SyncConflict,
    SyncItem,
)

# ─────────────────────────────────────────────────────────────────────────────
# Conflict Detection
# ─────────────────────────────────────────────────────────────────────────────


def detect_conflict(
    local_item: SyncItem,
    server_data: dict[str, Any],
    server_modified_at: datetime,
    server_modified_by: str | None = None,
    base_data: dict[str, Any] | None = None,
) -> SyncConflict | None:
    """
    Detect if there's a conflict between local and server data.

    كشف ما إذا كان هناك تعارض بين البيانات المحلية والخادم.

    Returns:
        SyncConflict if conflict detected, None otherwise
    """
    # No conflict if server wasn't modified after local
    if server_modified_at <= local_item.local_modified_at:
        return None

    # Determine conflict type
    local_deleted = local_item.operation.value == "delete"
    server_deleted = server_data.get("_deleted", False)

    if local_deleted and server_deleted:
        # Both deleted - no conflict
        return None
    elif local_deleted and not server_deleted:
        conflict_type = ConflictType.DELETE_UPDATE
    elif not local_deleted and server_deleted:
        conflict_type = ConflictType.UPDATE_DELETE
    else:
        # Detect schema mismatch - significant structural differences indicate schema version change
        # Exclude common metadata keys to reduce false positives from generic field overlap
        _metadata_keys = {
            "id", "updated_at", "created_at", "_deleted",
            "name", "type", "status", "tenant_id", "version", "schema_version",
        }
        local_keys = set(local_item.local_data.keys()) - _metadata_keys
        server_keys = set(server_data.keys()) - _metadata_keys
        all_keys = local_keys | server_keys
        overlap = local_keys & server_keys
        # Only trigger when both sides have enough domain-specific keys to compare
        if len(all_keys) >= 3 and len(overlap) / len(all_keys) < 0.5:
            return SyncConflict(
                sync_item_id=local_item.id,
                entity_id=local_item.entity_id,
                entity_type=local_item.entity_type,
                conflict_type=ConflictType.SCHEMA_MISMATCH,
                local_data=local_item.local_data,
                server_data=server_data,
                base_data=base_data,
                conflicting_fields=sorted(local_keys.symmetric_difference(server_keys)),
                local_modified_at=local_item.local_modified_at,
                server_modified_at=server_modified_at,
                local_modified_by=local_item.user_id,
                server_modified_by=server_modified_by,
                tenant_id=local_item.tenant_id,
                auto_resolvable=False,
            )
        conflict_type = ConflictType.UPDATE_UPDATE

    # Find conflicting fields
    conflicting_fields = find_conflicting_fields(
        local_data=local_item.local_data,
        server_data=server_data,
        base_data=base_data,
    )

    # No conflict if no fields differ
    if not conflicting_fields and conflict_type == ConflictType.UPDATE_UPDATE:
        return None

    # Check if auto-resolvable
    auto_resolvable = is_auto_resolvable(
        conflict_type=conflict_type,
        conflicting_fields=conflicting_fields,
        local_item=local_item,
        server_data=server_data,
    )

    return SyncConflict(
        sync_item_id=local_item.id,
        entity_id=local_item.entity_id,
        entity_type=local_item.entity_type,
        conflict_type=conflict_type,
        local_data=local_item.local_data,
        server_data=server_data,
        base_data=base_data,
        conflicting_fields=conflicting_fields,
        local_modified_at=local_item.local_modified_at,
        server_modified_at=server_modified_at,
        local_modified_by=local_item.user_id,
        server_modified_by=server_modified_by,
        tenant_id=local_item.tenant_id,
        auto_resolvable=auto_resolvable,
    )


def find_conflicting_fields(
    local_data: dict[str, Any],
    server_data: dict[str, Any],
    base_data: dict[str, Any] | None = None,
) -> list[str]:
    """
    Find fields that have conflicting values.

    البحث عن الحقول التي لها قيم متعارضة.
    """
    conflicting = []

    # Get all unique keys
    all_keys = set(local_data.keys()) | set(server_data.keys())
    if base_data:
        all_keys |= set(base_data.keys())

    # Skip metadata fields
    skip_fields = {"_id", "_deleted", "_version", "_modified_at", "_modified_by"}

    for key in all_keys:
        if key in skip_fields:
            continue

        local_value = local_data.get(key)
        server_value = server_data.get(key)
        base_value = base_data.get(key) if base_data else None

        # Both changed from base differently
        if base_data:
            local_changed = local_value != base_value
            server_changed = server_value != base_value
            if local_changed and server_changed and local_value != server_value:
                conflicting.append(key)
        else:
            # No base - conflict if values differ
            if local_value != server_value:
                conflicting.append(key)

    return conflicting


def is_auto_resolvable(
    conflict_type: ConflictType,
    conflicting_fields: list[str],
    local_item: SyncItem,
    server_data: dict[str, Any],
) -> bool:
    """
    Determine if a conflict can be automatically resolved.

    تحديد ما إذا كان يمكن حل التعارض تلقائياً.
    """
    # Delete conflicts usually need manual intervention
    if conflict_type in [ConflictType.UPDATE_DELETE, ConflictType.DELETE_UPDATE]:
        return False

    # Schema mismatches need manual intervention
    if conflict_type == ConflictType.SCHEMA_MISMATCH:
        return False

    # Check if all conflicting fields have clear winners
    for field_name in conflicting_fields:
        # Fields that require manual merge
        manual_fields = {"notes", "description", "comments", "name"}
        if field_name.lower() in manual_fields:
            return False

        # Complex nested objects need manual review
        local_val = local_item.local_data.get(field_name)
        server_val = server_data.get(field_name)
        if isinstance(local_val, dict) or isinstance(server_val, dict):
            return False
        if isinstance(local_val, list) or isinstance(server_val, list):
            return False

    return True


# ─────────────────────────────────────────────────────────────────────────────
# Base Resolver
# ─────────────────────────────────────────────────────────────────────────────


class ConflictResolver(ABC):
    """
    Base class for conflict resolvers.

    الفئة الأساسية لحل التعارضات.
    """

    strategy: ConflictResolutionStrategy

    @abstractmethod
    def resolve(self, conflict: SyncConflict) -> dict[str, Any]:
        """
        Resolve a conflict and return the merged data.

        حل التعارض وإرجاع البيانات المدمجة.
        """
        pass

    def apply_resolution(
        self,
        conflict: SyncConflict,
        resolved_by: str | None = None,
        note: str | None = None,
        note_ar: str | None = None,
    ) -> SyncConflict:
        """
        Apply resolution to a conflict.

        تطبيق الحل على التعارض.
        """
        resolved_data = self.resolve(conflict)

        conflict.resolution_strategy = self.strategy
        conflict.resolved_data = resolved_data
        conflict.resolved_at = datetime.now(UTC)
        conflict.resolved_by = resolved_by
        conflict.resolution_note = note
        conflict.resolution_note_ar = note_ar

        return conflict


# ─────────────────────────────────────────────────────────────────────────────
# Last Write Wins Resolver
# ─────────────────────────────────────────────────────────────────────────────


class LastWriteWinsResolver(ConflictResolver):
    """
    Resolver that uses the most recently modified version.

    محلل يستخدم النسخة المعدلة الأحدث.

    الكتابة الأخيرة تفوز - The last write wins.
    """

    strategy = ConflictResolutionStrategy.LAST_WRITE_WINS

    def resolve(self, conflict: SyncConflict) -> dict[str, Any]:
        """Use the most recently modified data."""
        if conflict.local_modified_at > conflict.server_modified_at:
            return conflict.local_data.copy()
        else:
            return conflict.server_data.copy()


# ─────────────────────────────────────────────────────────────────────────────
# Server Wins Resolver
# ─────────────────────────────────────────────────────────────────────────────


class ServerWinsResolver(ConflictResolver):
    """
    Resolver that always uses server data.

    محلل يستخدم دائماً بيانات الخادم.

    الخادم يفوز - Server always wins.
    """

    strategy = ConflictResolutionStrategy.SERVER_WINS

    def resolve(self, conflict: SyncConflict) -> dict[str, Any]:
        """Always use server data."""
        return conflict.server_data.copy()


# ─────────────────────────────────────────────────────────────────────────────
# Client Wins Resolver
# ─────────────────────────────────────────────────────────────────────────────


class ClientWinsResolver(ConflictResolver):
    """
    Resolver that always uses client/local data.

    محلل يستخدم دائماً البيانات المحلية.

    العميل يفوز - Client always wins.
    """

    strategy = ConflictResolutionStrategy.CLIENT_WINS

    def resolve(self, conflict: SyncConflict) -> dict[str, Any]:
        """Always use local data."""
        return conflict.local_data.copy()


# ─────────────────────────────────────────────────────────────────────────────
# Field-Level Merge Resolver
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class FieldMergeRule:
    """Rule for merging a specific field."""

    field_name: str
    strategy: str = "last_write"  # last_write, server, client, max, min, combine
    combine_separator: str = "; "

    def apply(
        self,
        local_value: Any,
        server_value: Any,
        local_modified_at: datetime,
        server_modified_at: datetime,
    ) -> Any:
        """Apply the merge rule."""
        if self.strategy == "last_write":
            return local_value if local_modified_at > server_modified_at else server_value
        elif self.strategy == "server":
            return server_value
        elif self.strategy == "client":
            return local_value
        elif self.strategy == "max":
            try:
                return max(local_value, server_value)
            except (TypeError, ValueError):
                return server_value
        elif self.strategy == "min":
            try:
                return min(local_value, server_value)
            except (TypeError, ValueError):
                return server_value
        elif self.strategy == "combine":
            if isinstance(local_value, str) and isinstance(server_value, str):
                if local_value == server_value:
                    return local_value
                return f"{local_value}{self.combine_separator}{server_value}"
            elif isinstance(local_value, list) and isinstance(server_value, list):
                combined = list(local_value)
                for item in server_value:
                    if item not in combined:
                        combined.append(item)
                return combined
            return server_value
        else:
            return server_value


class FieldLevelMergeResolver(ConflictResolver):
    """
    Resolver that merges at the field level.

    محلل يدمج على مستوى الحقل.

    دمج على مستوى الحقل - Field-level merge.
    """

    strategy = ConflictResolutionStrategy.FIELD_LEVEL_MERGE

    def __init__(
        self,
        field_rules: dict[str, FieldMergeRule] | None = None,
        default_strategy: str = "last_write",
    ):
        """
        Initialize with field-specific merge rules.

        Args:
            field_rules: Map of field name to merge rule
            default_strategy: Strategy for fields without specific rules
        """
        self.field_rules = field_rules or {}
        self.default_strategy = default_strategy
        self._default_rule = FieldMergeRule(
            field_name="*",
            strategy=default_strategy,
        )

    def resolve(self, conflict: SyncConflict) -> dict[str, Any]:
        """Merge data at the field level."""
        # Start with base data if available, otherwise server data
        merged = (conflict.base_data or conflict.server_data).copy()

        # Process each field
        all_keys = set(conflict.local_data.keys()) | set(conflict.server_data.keys())

        for key in all_keys:
            local_value = conflict.local_data.get(key)
            server_value = conflict.server_data.get(key)
            base_value = conflict.base_data.get(key) if conflict.base_data else None

            # If only one side has the value, use it
            if key not in conflict.local_data:
                merged[key] = server_value
                continue
            if key not in conflict.server_data:
                merged[key] = local_value
                continue

            # If values are the same, no conflict
            if local_value == server_value:
                merged[key] = local_value
                continue

            # If this field wasn't in conflicting_fields, use server (unchanged locally)
            if key not in conflict.conflicting_fields:
                # Check if local changed from base
                if conflict.base_data and local_value != base_value:
                    merged[key] = local_value
                else:
                    merged[key] = server_value
                continue

            # Apply merge rule
            rule = self.field_rules.get(key, self._default_rule)
            merged[key] = rule.apply(
                local_value=local_value,
                server_value=server_value,
                local_modified_at=conflict.local_modified_at,
                server_modified_at=conflict.server_modified_at,
            )

        return merged


# ─────────────────────────────────────────────────────────────────────────────
# Manual Merge Resolver
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class ManualMergeChoice:
    """A user's choice for resolving a field conflict."""

    field_name: str
    chosen_value: Any
    source: str  # "local", "server", "custom"
    custom_value: Any | None = None


class ManualMergeResolver(ConflictResolver):
    """
    Resolver that requires manual user input for each field.

    محلل يتطلب إدخال يدوي من المستخدم لكل حقل.

    دمج يدوي - Manual merge.
    """

    strategy = ConflictResolutionStrategy.MANUAL_MERGE

    def __init__(self, choices: list[ManualMergeChoice] | None = None):
        """Initialize with user choices."""
        self.choices = {c.field_name: c for c in (choices or [])}

    def set_choice(self, choice: ManualMergeChoice) -> None:
        """Set a user's choice for a field."""
        self.choices[choice.field_name] = choice

    def set_choices(self, choices: list[ManualMergeChoice]) -> None:
        """Set multiple user choices."""
        for choice in choices:
            self.choices[choice.field_name] = choice

    def is_complete(self, conflict: SyncConflict) -> bool:
        """Check if all conflicting fields have choices."""
        return all(field_name in self.choices for field_name in conflict.conflicting_fields)

    def get_pending_fields(self, conflict: SyncConflict) -> list[str]:
        """Get fields that still need user choices."""
        return [f for f in conflict.conflicting_fields if f not in self.choices]

    def resolve(self, conflict: SyncConflict) -> dict[str, Any]:
        """
        Merge data based on user choices.

        Note: Will raise ValueError if choices are incomplete.
        """
        if not self.is_complete(conflict):
            pending = self.get_pending_fields(conflict)
            raise ValueError(
                f"Manual merge incomplete. Pending fields: {pending} | "
                f"الدمج اليدوي غير مكتمل. الحقول المعلقة: {pending}"
            )

        # Start with server data as base
        merged = conflict.server_data.copy()

        # Apply non-conflicting local changes
        if conflict.base_data:
            for key, value in conflict.local_data.items():
                if key not in conflict.conflicting_fields:
                    base_value = conflict.base_data.get(key)
                    if value != base_value:
                        merged[key] = value

        # Apply user choices for conflicting fields
        for field_name in conflict.conflicting_fields:
            choice = self.choices.get(field_name)
            if choice:
                if choice.source == "local":
                    merged[field_name] = conflict.local_data.get(field_name)
                elif choice.source == "server":
                    merged[field_name] = conflict.server_data.get(field_name)
                elif choice.source == "custom" and choice.custom_value is not None:
                    merged[field_name] = choice.custom_value
                else:
                    merged[field_name] = choice.chosen_value

        return merged


# ─────────────────────────────────────────────────────────────────────────────
# Custom Resolver
# ─────────────────────────────────────────────────────────────────────────────


CustomResolverFunc = Callable[[SyncConflict], dict[str, Any]]


class CustomResolver(ConflictResolver):
    """
    Resolver with a custom resolution function.

    محلل بوظيفة حل مخصصة.
    """

    strategy = ConflictResolutionStrategy.CUSTOM

    def __init__(self, resolver_func: CustomResolverFunc):
        """Initialize with a custom resolver function."""
        self.resolver_func = resolver_func

    def resolve(self, conflict: SyncConflict) -> dict[str, Any]:
        """Apply the custom resolver function."""
        return self.resolver_func(conflict)


# ─────────────────────────────────────────────────────────────────────────────
# Resolver Factory
# ─────────────────────────────────────────────────────────────────────────────


class ConflictResolverFactory:
    """
    Factory for creating conflict resolvers.

    مصنع لإنشاء محللات التعارضات.
    """

    # Default field rules for common entity types
    DEFAULT_FIELD_RULES: dict[EntityType, dict[str, FieldMergeRule]] = {
        EntityType.FIELD: {
            "name": FieldMergeRule("name", "last_write"),
            "area_hectares": FieldMergeRule("area_hectares", "last_write"),
            "notes": FieldMergeRule("notes", "combine"),
            "status": FieldMergeRule("status", "last_write"),
        },
        EntityType.IRRIGATION: {
            "water_amount_mm": FieldMergeRule("water_amount_mm", "max"),
            "duration_minutes": FieldMergeRule("duration_minutes", "max"),
            "notes": FieldMergeRule("notes", "combine"),
        },
        EntityType.OBSERVATION: {
            "value": FieldMergeRule("value", "last_write"),
            "notes": FieldMergeRule("notes", "combine"),
            "severity": FieldMergeRule("severity", "max"),
        },
        EntityType.TASK: {
            "status": FieldMergeRule("status", "last_write"),
            "priority": FieldMergeRule("priority", "max"),
            "notes": FieldMergeRule("notes", "combine"),
            "assigned_to": FieldMergeRule("assigned_to", "last_write"),
        },
    }

    @classmethod
    def create(
        cls,
        strategy: ConflictResolutionStrategy,
        entity_type: EntityType | None = None,
        field_rules: dict[str, FieldMergeRule] | None = None,
        custom_func: CustomResolverFunc | None = None,
    ) -> ConflictResolver:
        """
        Create a resolver based on strategy.

        إنشاء محلل بناءً على الاستراتيجية.
        """
        if strategy == ConflictResolutionStrategy.LAST_WRITE_WINS:
            return LastWriteWinsResolver()

        elif strategy == ConflictResolutionStrategy.SERVER_WINS:
            return ServerWinsResolver()

        elif strategy == ConflictResolutionStrategy.CLIENT_WINS:
            return ClientWinsResolver()

        elif strategy == ConflictResolutionStrategy.FIELD_LEVEL_MERGE:
            rules = field_rules
            if not rules and entity_type:
                rules = cls.DEFAULT_FIELD_RULES.get(entity_type, {})
            return FieldLevelMergeResolver(field_rules=rules)

        elif strategy == ConflictResolutionStrategy.MANUAL_MERGE:
            return ManualMergeResolver()

        elif strategy == ConflictResolutionStrategy.CUSTOM:
            if not custom_func:
                raise ValueError("Custom resolver requires a resolver function | المحلل المخصص يتطلب وظيفة حل")
            return CustomResolver(custom_func)

        else:
            # Default to last write wins
            return LastWriteWinsResolver()


# ─────────────────────────────────────────────────────────────────────────────
# Conflict Resolution Manager
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class ResolutionConfig:
    """Configuration for conflict resolution."""

    default_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.LAST_WRITE_WINS
    auto_resolve_simple: bool = True  # تلقائي للبسيط
    auto_resolve_non_critical: bool = True  # تلقائي لغير الحرج
    notify_on_conflict: bool = True  # إشعار عند التعارض
    log_resolutions: bool = True  # تسجيل الحلول

    # Entity-specific strategies
    entity_strategies: dict[EntityType, ConflictResolutionStrategy] = field(default_factory=dict)

    # Field criticality (fields that always require manual merge)
    critical_fields: set[str] = field(
        default_factory=lambda: {"boundary", "geometry", "financial_data", "legal_status"}
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "default_strategy": self.default_strategy.value,
            "auto_resolve_simple": self.auto_resolve_simple,
            "auto_resolve_non_critical": self.auto_resolve_non_critical,
            "notify_on_conflict": self.notify_on_conflict,
            "log_resolutions": self.log_resolutions,
            "entity_strategies": {k.value: v.value for k, v in self.entity_strategies.items()},
            "critical_fields": list(self.critical_fields),
        }


class ConflictResolutionManager:
    """
    Manager for detecting and resolving conflicts.

    مدير لكشف وحل التعارضات.
    """

    def __init__(self, config: ResolutionConfig | None = None):
        """Initialize the manager."""
        self.config = config or ResolutionConfig()

        # Pending conflicts requiring manual resolution
        self._pending_conflicts: dict[str, SyncConflict] = {}

        # Resolution history
        self._resolution_history: list[dict[str, Any]] = []

    def detect_conflict(
        self,
        local_item: SyncItem,
        server_data: dict[str, Any],
        server_modified_at: datetime,
        server_modified_by: str | None = None,
        base_data: dict[str, Any] | None = None,
    ) -> SyncConflict | None:
        """
        Detect if there's a conflict.

        كشف ما إذا كان هناك تعارض.
        """
        return detect_conflict(
            local_item=local_item,
            server_data=server_data,
            server_modified_at=server_modified_at,
            server_modified_by=server_modified_by,
            base_data=base_data,
        )

    def resolve(
        self,
        conflict: SyncConflict,
        strategy: ConflictResolutionStrategy | None = None,
        user_id: str | None = None,
        note: str | None = None,
        note_ar: str | None = None,
    ) -> tuple[SyncConflict, bool]:
        """
        Resolve a conflict.

        حل تعارض.

        Returns:
            Tuple of (resolved conflict, success)
        """
        # Determine strategy
        if strategy is None:
            strategy = self._get_strategy_for_conflict(conflict)

        # Check for critical fields requiring manual merge
        if self._has_critical_fields(conflict):
            if strategy != ConflictResolutionStrategy.MANUAL_MERGE:
                # Store for manual resolution
                self._pending_conflicts[conflict.id] = conflict
                return conflict, False

        # Create resolver
        resolver = ConflictResolverFactory.create(
            strategy=strategy,
            entity_type=conflict.entity_type,
        )

        try:
            # Apply resolution
            resolved_conflict = resolver.apply_resolution(
                conflict=conflict,
                resolved_by=user_id,
                note=note,
                note_ar=note_ar,
            )

            # Log resolution
            if self.config.log_resolutions:
                self._log_resolution(resolved_conflict)

            # Remove from pending
            self._pending_conflicts.pop(conflict.id, None)

            return resolved_conflict, True

        except ValueError:
            # Manual merge incomplete
            self._pending_conflicts[conflict.id] = conflict
            return conflict, False

    def auto_resolve(
        self,
        conflict: SyncConflict,
    ) -> tuple[SyncConflict, bool]:
        """
        Attempt to automatically resolve a conflict.

        محاولة حل تعارض تلقائياً.
        """
        # Check if auto-resolvable
        if not conflict.auto_resolvable:
            self._pending_conflicts[conflict.id] = conflict
            return conflict, False

        # Check if simple enough for auto-resolution
        if not self.config.auto_resolve_simple:
            self._pending_conflicts[conflict.id] = conflict
            return conflict, False

        # Check for critical fields
        if self._has_critical_fields(conflict):
            self._pending_conflicts[conflict.id] = conflict
            return conflict, False

        # Use default strategy
        return self.resolve(
            conflict=conflict,
            strategy=self.config.default_strategy,
            user_id="system",
            note="Auto-resolved",
            note_ar="تم الحل تلقائياً",
        )

    def manual_resolve(
        self,
        conflict_id: str,
        choices: list[ManualMergeChoice],
        user_id: str,
        note: str | None = None,
        note_ar: str | None = None,
    ) -> tuple[SyncConflict | None, bool, BilingualMessage]:
        """
        Manually resolve a pending conflict.

        حل تعارض معلق يدوياً.
        """
        conflict = self._pending_conflicts.get(conflict_id)
        if not conflict:
            return None, False, SYNC_ERRORS["conflict_unresolved"]

        # Create manual resolver with choices
        resolver = ManualMergeResolver(choices=choices)

        # Check if complete
        if not resolver.is_complete(conflict):
            pending = resolver.get_pending_fields(conflict)
            return (
                conflict,
                False,
                BilingualMessage(
                    en=f"Missing choices for fields: {pending}",
                    ar=f"خيارات مفقودة للحقول: {pending}",
                ),
            )

        try:
            resolved_conflict = resolver.apply_resolution(
                conflict=conflict,
                resolved_by=user_id,
                note=note,
                note_ar=note_ar,
            )

            # Log resolution
            if self.config.log_resolutions:
                self._log_resolution(resolved_conflict)

            # Remove from pending
            del self._pending_conflicts[conflict_id]

            return resolved_conflict, True, SYNC_MESSAGES["conflict_resolved"]

        except ValueError as e:
            return (
                conflict,
                False,
                BilingualMessage(
                    en=str(e),
                    ar=str(e),
                ),
            )

    def get_pending_conflicts(self) -> list[SyncConflict]:
        """Get all pending conflicts."""
        return list(self._pending_conflicts.values())

    def get_pending_conflict(self, conflict_id: str) -> SyncConflict | None:
        """Get a specific pending conflict."""
        return self._pending_conflicts.get(conflict_id)

    def get_pending_count(self) -> int:
        """Get count of pending conflicts."""
        return len(self._pending_conflicts)

    def get_resolution_history(
        self,
        limit: int = 100,
        entity_type: EntityType | None = None,
    ) -> list[dict[str, Any]]:
        """Get resolution history."""
        history = self._resolution_history
        if entity_type:
            history = [h for h in history if h.get("entity_type") == entity_type.value]
        return history[-limit:]

    def _get_strategy_for_conflict(
        self,
        conflict: SyncConflict,
    ) -> ConflictResolutionStrategy:
        """Get the appropriate strategy for a conflict."""
        # Check entity-specific strategy
        entity_strategy = self.config.entity_strategies.get(conflict.entity_type)
        if entity_strategy:
            return entity_strategy

        return self.config.default_strategy

    def _has_critical_fields(self, conflict: SyncConflict) -> bool:
        """Check if conflict involves critical fields."""
        return any(field in self.config.critical_fields for field in conflict.conflicting_fields)

    def _log_resolution(self, conflict: SyncConflict) -> None:
        """Log a resolution."""
        self._resolution_history.append(
            {
                "conflict_id": conflict.id,
                "entity_id": conflict.entity_id,
                "entity_type": conflict.entity_type.value,
                "conflict_type": conflict.conflict_type.value,
                "strategy": conflict.resolution_strategy.value if conflict.resolution_strategy else None,
                "conflicting_fields": conflict.conflicting_fields,
                "resolved_by": conflict.resolved_by,
                "resolved_at": conflict.resolved_at.isoformat() if conflict.resolved_at else None,
                "note": conflict.resolution_note,
            }
        )
