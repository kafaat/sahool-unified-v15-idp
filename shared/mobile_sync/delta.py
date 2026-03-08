"""
Delta Sync Module
=================
وحدة المزامنة التزايدية

Delta/incremental sync logic for bandwidth-efficient synchronization.
Computes and applies changes between versions.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from .models import (
    SYNC_MESSAGES,
    BilingualMessage,
    DeltaChange,
    DeltaPacket,
    EntityType,
    SyncItem,
    SyncOperationType,
)

# ─────────────────────────────────────────────────────────────────────────────
# Delta Configuration
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class DeltaSyncConfig:
    """Configuration for delta sync operations."""

    # Delta thresholds
    min_savings_percent: float = 20.0  # الحد الأدنى للتوفير - Skip delta if savings < 20%
    max_delta_size_bytes: int = 1024 * 100  # الحد الأقصى لحجم الدلتا - 100KB max delta
    max_changes_per_packet: int = 1000  # الحد الأقصى للتغييرات لكل حزمة

    # Compression
    enable_compression: bool = True  # تفعيل الضغط
    compression_level: int = 6  # مستوى الضغط (1-9)

    # Versioning
    track_versions: bool = True  # تتبع الإصدارات
    max_version_history: int = 10  # الحد الأقصى لتاريخ الإصدارات

    # Fields to exclude from delta
    excluded_fields: set[str] = field(
        default_factory=lambda: {
            "_id",
            "_version",
            "_modified_at",
            "_modified_by",
            "created_at",
            "updated_at",
            "sync_status",
        }
    )

    # Fields that should always be sent in full (not delta)
    full_sync_fields: set[str] = field(
        default_factory=lambda: {
            "geometry",
            "boundary",
            "coordinates",
        }
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "min_savings_percent": self.min_savings_percent,
            "max_delta_size_bytes": self.max_delta_size_bytes,
            "max_changes_per_packet": self.max_changes_per_packet,
            "enable_compression": self.enable_compression,
            "compression_level": self.compression_level,
            "track_versions": self.track_versions,
            "max_version_history": self.max_version_history,
            "excluded_fields": list(self.excluded_fields),
            "full_sync_fields": list(self.full_sync_fields),
        }


# ─────────────────────────────────────────────────────────────────────────────
# Delta Operations
# ─────────────────────────────────────────────────────────────────────────────


def compute_checksum(data: dict[str, Any]) -> str:
    """
    Compute a checksum for data integrity verification.

    حساب مجموع التحقق للتحقق من سلامة البيانات.
    """
    # Sort keys for deterministic hashing
    serialized = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode()).hexdigest()[:16]


def compute_delta(
    old_data: dict[str, Any],
    new_data: dict[str, Any],
    config: DeltaSyncConfig | None = None,
) -> list[DeltaChange]:
    """
    Compute the delta between two versions of data.

    حساب الفرق بين نسختين من البيانات.

    Args:
        old_data: Previous version of the data
        new_data: New version of the data
        config: Delta sync configuration

    Returns:
        List of DeltaChange representing differences
    """
    config = config or DeltaSyncConfig()
    changes: list[DeltaChange] = []

    # Get all unique keys
    all_keys = set(old_data.keys()) | set(new_data.keys())

    for key in all_keys:
        # Skip excluded fields
        if key in config.excluded_fields:
            continue

        old_value = old_data.get(key)
        new_value = new_data.get(key)

        # Key removed
        if key not in new_data:
            changes.append(
                DeltaChange(
                    field_path=key,
                    old_value=old_value,
                    new_value=None,
                    operation="unset",
                )
            )
            continue

        # Key added
        if key not in old_data:
            changes.append(
                DeltaChange(
                    field_path=key,
                    old_value=None,
                    new_value=new_value,
                    operation="set",
                )
            )
            continue

        # Value unchanged
        if old_value == new_value:
            continue

        # Handle nested objects
        if isinstance(old_value, dict) and isinstance(new_value, dict):
            # Fields that require full sync
            if key in config.full_sync_fields:
                changes.append(
                    DeltaChange(
                        field_path=key,
                        old_value=old_value,
                        new_value=new_value,
                        operation="set",
                    )
                )
            else:
                # Recursively compute nested delta
                nested_changes = _compute_nested_delta(old_value, new_value, key, config)
                changes.extend(nested_changes)
            continue

        # Handle lists
        if isinstance(old_value, list) and isinstance(new_value, list):
            list_changes = _compute_list_delta(old_value, new_value, key, config)
            changes.extend(list_changes)
            continue

        # Handle numeric increment/decrement
        if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
            diff = new_value - old_value
            if diff != 0:
                changes.append(
                    DeltaChange(
                        field_path=key,
                        old_value=old_value,
                        new_value=new_value,
                        operation="increment" if diff > 0 else "set",
                    )
                )
            continue

        # General value change
        changes.append(
            DeltaChange(
                field_path=key,
                old_value=old_value,
                new_value=new_value,
                operation="set",
            )
        )

    return changes


def _compute_nested_delta(
    old_data: dict[str, Any],
    new_data: dict[str, Any],
    prefix: str,
    config: DeltaSyncConfig,
) -> list[DeltaChange]:
    """Compute delta for nested objects."""
    changes: list[DeltaChange] = []
    all_keys = set(old_data.keys()) | set(new_data.keys())

    for key in all_keys:
        field_path = f"{prefix}.{key}"
        old_value = old_data.get(key)
        new_value = new_data.get(key)

        if key not in new_data:
            changes.append(
                DeltaChange(
                    field_path=field_path,
                    old_value=old_value,
                    new_value=None,
                    operation="unset",
                )
            )
        elif key not in old_data:
            changes.append(
                DeltaChange(
                    field_path=field_path,
                    old_value=None,
                    new_value=new_value,
                    operation="set",
                )
            )
        elif old_value != new_value:
            if isinstance(old_value, dict) and isinstance(new_value, dict):
                nested = _compute_nested_delta(old_value, new_value, field_path, config)
                changes.extend(nested)
            else:
                changes.append(
                    DeltaChange(
                        field_path=field_path,
                        old_value=old_value,
                        new_value=new_value,
                        operation="set",
                    )
                )

    return changes


def _compute_list_delta(
    old_list: list[Any],
    new_list: list[Any],
    field_path: str,
    config: DeltaSyncConfig,
) -> list[DeltaChange]:
    """Compute delta for list changes."""
    changes: list[DeltaChange] = []

    # Determine if we should use full replacement or incremental
    if len(old_list) > 100 or len(new_list) > 100:
        # Large lists - use full replacement
        changes.append(
            DeltaChange(
                field_path=field_path,
                old_value=old_list,
                new_value=new_list,
                operation="set",
            )
        )
        return changes

    # Check for objects with IDs
    old_by_id = {}
    new_by_id = {}

    for item in old_list:
        if isinstance(item, dict) and "id" in item:
            old_by_id[item["id"]] = item

    for item in new_list:
        if isinstance(item, dict) and "id" in item:
            new_by_id[item["id"]] = item

    # If items have IDs, track by ID
    if old_by_id or new_by_id:
        # Added items
        for item_id, item in new_by_id.items():
            if item_id not in old_by_id:
                changes.append(
                    DeltaChange(
                        field_path=f"{field_path}[{item_id}]",
                        old_value=None,
                        new_value=item,
                        operation="append",
                    )
                )
            elif item != old_by_id[item_id]:
                # Item modified
                changes.append(
                    DeltaChange(
                        field_path=f"{field_path}[{item_id}]",
                        old_value=old_by_id[item_id],
                        new_value=item,
                        operation="set",
                    )
                )

        # Removed items
        for item_id in old_by_id:
            if item_id not in new_by_id:
                changes.append(
                    DeltaChange(
                        field_path=f"{field_path}[{item_id}]",
                        old_value=old_by_id[item_id],
                        new_value=None,
                        operation="remove",
                    )
                )

        return changes

    # Simple list - full replacement if different
    if old_list != new_list:
        changes.append(
            DeltaChange(
                field_path=field_path,
                old_value=old_list,
                new_value=new_list,
                operation="set",
            )
        )

    return changes


def apply_delta(
    base_data: dict[str, Any],
    changes: list[DeltaChange],
) -> dict[str, Any]:
    """
    Apply delta changes to base data.

    تطبيق تغييرات الدلتا على البيانات الأساسية.

    Args:
        base_data: The base version of data
        changes: List of delta changes to apply

    Returns:
        New data with all changes applied
    """
    result = base_data.copy()

    for change in changes:
        _apply_single_change(result, change)

    return result


def _apply_single_change(data: dict[str, Any], change: DeltaChange) -> None:
    """Apply a single delta change."""
    path_parts = change.field_path.split(".")

    # Navigate to the parent of the target field
    current = data
    for i, part in enumerate(path_parts[:-1]):
        # Handle array notation
        if "[" in part:
            field_name, item_id = part.split("[")
            item_id = item_id.rstrip("]")

            if field_name not in current:
                current[field_name] = []

            # Find or create the item
            found = False
            for item in current[field_name]:
                if isinstance(item, dict) and str(item.get("id")) == item_id:
                    current = item
                    found = True
                    break

            if not found:
                new_item = {"id": item_id}
                current[field_name].append(new_item)
                current = new_item
        else:
            if part not in current:
                current[part] = {}
            current = current[part]

    # Apply the change to the target field
    target_field = path_parts[-1]

    # Handle array notation in target
    if "[" in target_field:
        field_name, item_id = target_field.split("[")
        item_id = item_id.rstrip("]")

        if field_name not in current:
            current[field_name] = []

        if change.operation == "unset" or change.operation == "remove":
            # Remove item
            current[field_name] = [
                item for item in current[field_name] if not (isinstance(item, dict) and str(item.get("id")) == item_id)
            ]
        elif change.operation == "append":
            current[field_name].append(change.new_value)
        else:
            # Update or add item
            found = False
            for i, item in enumerate(current[field_name]):
                if isinstance(item, dict) and str(item.get("id")) == item_id:
                    current[field_name][i] = change.new_value
                    found = True
                    break
            if not found:
                current[field_name].append(change.new_value)
    else:
        if change.operation == "unset":
            current.pop(target_field, None)
        elif change.operation == "increment":
            old_val = current.get(target_field, 0)
            current[target_field] = old_val + (change.new_value - change.old_value)
        else:
            current[target_field] = change.new_value


# ─────────────────────────────────────────────────────────────────────────────
# Delta Packet Builder
# ─────────────────────────────────────────────────────────────────────────────


class DeltaPacketBuilder:
    """
    Builder for creating delta packets.

    منشئ لإنشاء حزم الدلتا.
    """

    def __init__(self, config: DeltaSyncConfig | None = None):
        """Initialize the builder."""
        self.config = config or DeltaSyncConfig()

    def build(
        self,
        entity_id: str,
        entity_type: EntityType,
        old_data: dict[str, Any],
        new_data: dict[str, Any],
        base_version: int = 0,
        target_version: int = 1,
    ) -> DeltaPacket | None:
        """
        Build a delta packet from old and new data.

        بناء حزمة دلتا من البيانات القديمة والجديدة.

        Returns:
            DeltaPacket if delta is efficient, None if full sync is better
        """
        # Compute changes
        changes = compute_delta(old_data, new_data, self.config)

        if not changes:
            return None  # No changes

        # Calculate sizes
        full_size = len(json.dumps(new_data, default=str).encode())
        delta_size = len(json.dumps([c.to_dict() for c in changes], default=str).encode())

        # Check if delta is worth it
        savings_percent = ((full_size - delta_size) / full_size) * 100 if full_size > 0 else 0

        if savings_percent < self.config.min_savings_percent:
            return None  # Full sync is more efficient

        if delta_size > self.config.max_delta_size_bytes:
            return None  # Delta is too large

        if len(changes) > self.config.max_changes_per_packet:
            return None  # Too many changes

        # Build packet
        packet = DeltaPacket(
            entity_id=entity_id,
            entity_type=entity_type,
            base_version=base_version,
            target_version=target_version,
            changes=changes,
            full_size_bytes=full_size,
            delta_size_bytes=delta_size,
            compression_ratio=delta_size / full_size if full_size > 0 else 1.0,
            checksum=compute_checksum(new_data),
        )

        return packet

    def build_from_sync_item(
        self,
        item: SyncItem,
        base_version: int = 0,
    ) -> DeltaPacket | None:
        """
        Build a delta packet from a sync item.

        بناء حزمة دلتا من عنصر مزامنة.
        """
        if not item.server_data:
            return None

        return self.build(
            entity_id=item.entity_id,
            entity_type=item.entity_type,
            old_data=item.server_data,
            new_data=item.local_data,
            base_version=base_version,
            target_version=base_version + 1,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Delta Sync Manager
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class DeltaSyncStats:
    """Statistics for delta sync operations."""

    total_syncs: int = 0
    delta_syncs: int = 0
    full_syncs: int = 0
    total_bytes_saved: int = 0
    total_bytes_transferred: int = 0
    average_savings_percent: float = 0.0

    def record_delta_sync(self, full_size: int, delta_size: int) -> None:
        """Record a delta sync operation."""
        self.total_syncs += 1
        self.delta_syncs += 1
        self.total_bytes_saved += full_size - delta_size
        self.total_bytes_transferred += delta_size
        self._update_average_savings()

    def record_full_sync(self, size: int) -> None:
        """Record a full sync operation."""
        self.total_syncs += 1
        self.full_syncs += 1
        self.total_bytes_transferred += size
        self._update_average_savings()

    def _update_average_savings(self) -> None:
        """Update average savings percentage."""
        if self.total_bytes_transferred + self.total_bytes_saved > 0:
            self.average_savings_percent = (
                self.total_bytes_saved / (self.total_bytes_transferred + self.total_bytes_saved)
            ) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_syncs": self.total_syncs,
            "delta_syncs": self.delta_syncs,
            "full_syncs": self.full_syncs,
            "delta_rate": round((self.delta_syncs / self.total_syncs * 100) if self.total_syncs > 0 else 0, 2),
            "total_bytes_saved": self.total_bytes_saved,
            "total_bytes_transferred": self.total_bytes_transferred,
            "average_savings_percent": round(self.average_savings_percent, 2),
        }


class DeltaSyncManager:
    """
    Manager for delta/incremental sync operations.

    مدير لعمليات المزامنة التزايدية.
    """

    def __init__(self, config: DeltaSyncConfig | None = None):
        """Initialize the manager."""
        self.config = config or DeltaSyncConfig()
        self.builder = DeltaPacketBuilder(config)
        self.stats = DeltaSyncStats()

        # Version tracking (entity_key -> version history)
        self._version_history: dict[str, list[dict[str, Any]]] = {}

        # Sync tokens (device_id -> last sync state)
        self._sync_tokens: dict[str, dict[str, Any]] = {}

    def prepare_upload(
        self,
        item: SyncItem,
    ) -> tuple[SyncItem, bool]:
        """
        Prepare an item for upload, using delta if efficient.

        تحضير عنصر للرفع، باستخدام الدلتا إذا كانت فعالة.

        Returns:
            Tuple of (prepared item, is_delta)
        """
        # Check if we have base data for delta
        if not item.server_data:
            # No base data - must use full sync
            self.stats.record_full_sync(len(json.dumps(item.local_data, default=str).encode()))
            return item, False

        # Try to build delta
        base_version = item.metadata.server_version or 0
        delta_packet = self.builder.build(
            entity_id=item.entity_id,
            entity_type=item.entity_type,
            old_data=item.server_data,
            new_data=item.local_data,
            base_version=base_version,
            target_version=base_version + 1,
        )

        if delta_packet:
            # Use delta sync
            item.delta_data = {
                "packet_id": delta_packet.id,
                "base_version": delta_packet.base_version,
                "target_version": delta_packet.target_version,
                "changes": [c.to_dict() for c in delta_packet.changes],
                "checksum": delta_packet.checksum,
            }
            item.operation = SyncOperationType.PARTIAL_UPDATE

            self.stats.record_delta_sync(
                delta_packet.full_size_bytes,
                delta_packet.delta_size_bytes,
            )

            # Track version
            if self.config.track_versions:
                self._track_version(item, delta_packet)

            return item, True
        else:
            # Full sync
            item.delta_data = None
            self.stats.record_full_sync(len(json.dumps(item.local_data, default=str).encode()))
            return item, False

    def apply_download(
        self,
        entity_id: str,
        entity_type: EntityType,
        current_data: dict[str, Any] | None,
        delta_packet: DeltaPacket,
    ) -> tuple[dict[str, Any], bool, BilingualMessage]:
        """
        Apply a downloaded delta packet to local data.

        تطبيق حزمة دلتا منزلة على البيانات المحلية.

        Returns:
            Tuple of (result data, success, message)
        """
        if current_data is None:
            return (
                {},
                False,
                BilingualMessage(
                    en="Cannot apply delta without base data",
                    ar="لا يمكن تطبيق الدلتا بدون بيانات أساسية",
                ),
            )

        # Verify checksum of base
        compute_checksum(current_data)

        try:
            # Apply delta
            result = apply_delta(current_data, delta_packet.changes)

            # Verify result checksum
            if delta_packet.checksum:
                result_checksum = compute_checksum(result)
                if result_checksum != delta_packet.checksum:
                    return (
                        current_data,
                        False,
                        BilingualMessage(
                            en="Checksum mismatch after applying delta",
                            ar="عدم تطابق مجموع التحقق بعد تطبيق الدلتا",
                        ),
                    )

            return result, True, SYNC_MESSAGES["download_completed"]

        except Exception as e:
            return (
                current_data,
                False,
                BilingualMessage(
                    en=f"Failed to apply delta: {str(e)}",
                    ar=f"فشل تطبيق الدلتا: {str(e)}",
                ),
            )

    def get_sync_token(self, device_id: str) -> str | None:
        """Get the current sync token for a device."""
        state = self._sync_tokens.get(device_id)
        return state.get("token") if state else None

    def update_sync_token(
        self,
        device_id: str,
        token: str,
        server_timestamp: datetime,
    ) -> None:
        """Update the sync token for a device."""
        self._sync_tokens[device_id] = {
            "token": token,
            "timestamp": server_timestamp.isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
        }

    def get_changes_since_token(
        self,
        device_id: str,
        entity_type: EntityType | None = None,
    ) -> list[dict[str, Any]]:
        """Get all changes since the device's last sync token."""
        state = self._sync_tokens.get(device_id)
        if not state:
            return []

        # This would typically query a changelog or event store
        # For now, return empty (implementation depends on backend)
        return []

    def should_use_delta(
        self,
        item: SyncItem,
    ) -> bool:
        """
        Determine if delta sync should be used for an item.

        تحديد ما إذا كان يجب استخدام مزامنة الدلتا لعنصر.
        """
        # No delta for creates or deletes
        if item.operation in [SyncOperationType.CREATE, SyncOperationType.DELETE]:
            return False

        # No delta without base data
        if not item.server_data:
            return False

        # Check if changes are small enough
        changes = compute_delta(
            item.server_data,
            item.local_data,
            self.config,
        )

        if not changes:
            return False

        if len(changes) > self.config.max_changes_per_packet:
            return False

        # Estimate savings
        full_size = len(json.dumps(item.local_data, default=str).encode())
        delta_size = len(json.dumps([c.to_dict() for c in changes], default=str).encode())

        savings = ((full_size - delta_size) / full_size) * 100 if full_size > 0 else 0

        return savings >= self.config.min_savings_percent

    def get_stats(self) -> dict[str, Any]:
        """Get delta sync statistics."""
        return self.stats.to_dict()

    def reset_stats(self) -> None:
        """Reset statistics."""
        self.stats = DeltaSyncStats()

    def _track_version(self, item: SyncItem, packet: DeltaPacket) -> None:
        """Track version history for an entity."""
        entity_key = f"{item.entity_type.value}:{item.entity_id}"

        if entity_key not in self._version_history:
            self._version_history[entity_key] = []

        self._version_history[entity_key].append(
            {
                "version": packet.target_version,
                "timestamp": datetime.now(UTC).isoformat(),
                "checksum": packet.checksum,
                "change_count": len(packet.changes),
            }
        )

        # Trim history
        max_history = self.config.max_version_history
        if len(self._version_history[entity_key]) > max_history:
            self._version_history[entity_key] = self._version_history[entity_key][-max_history:]

    def get_version_history(
        self,
        entity_id: str,
        entity_type: EntityType,
    ) -> list[dict[str, Any]]:
        """Get version history for an entity."""
        entity_key = f"{entity_type.value}:{entity_id}"
        return self._version_history.get(entity_key, [])


# ─────────────────────────────────────────────────────────────────────────────
# Batch Delta Operations
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class BatchDeltaResult:
    """Result of a batch delta operation."""

    total_items: int = 0
    delta_items: int = 0
    full_sync_items: int = 0
    total_bytes_original: int = 0
    total_bytes_transferred: int = 0
    savings_bytes: int = 0
    savings_percent: float = 0.0
    items: list[tuple[SyncItem, bool]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_items": self.total_items,
            "delta_items": self.delta_items,
            "full_sync_items": self.full_sync_items,
            "delta_rate": round((self.delta_items / self.total_items * 100) if self.total_items > 0 else 0, 2),
            "total_bytes_original": self.total_bytes_original,
            "total_bytes_transferred": self.total_bytes_transferred,
            "savings_bytes": self.savings_bytes,
            "savings_percent": round(self.savings_percent, 2),
        }


def prepare_batch_upload(
    items: list[SyncItem],
    manager: DeltaSyncManager,
) -> BatchDeltaResult:
    """
    Prepare a batch of items for upload with delta optimization.

    تحضير دفعة من العناصر للرفع مع تحسين الدلتا.
    """
    result = BatchDeltaResult()

    for item in items:
        original_size = len(json.dumps(item.local_data, default=str).encode())
        result.total_bytes_original += original_size

        prepared_item, is_delta = manager.prepare_upload(item)
        result.items.append((prepared_item, is_delta))
        result.total_items += 1

        if is_delta and prepared_item.delta_data:
            result.delta_items += 1
            delta_size = len(json.dumps(prepared_item.delta_data, default=str).encode())
            result.total_bytes_transferred += delta_size
        else:
            result.full_sync_items += 1
            result.total_bytes_transferred += original_size

    result.savings_bytes = result.total_bytes_original - result.total_bytes_transferred
    if result.total_bytes_original > 0:
        result.savings_percent = (result.savings_bytes / result.total_bytes_original) * 100

    return result
