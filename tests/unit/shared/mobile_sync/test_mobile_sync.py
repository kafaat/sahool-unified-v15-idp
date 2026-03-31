"""
Tests for Mobile Sync Module - اختبارات وحدة المزامنة

Covers:
- Sync data models and enums
- Delta computation (compute_delta, apply_delta)
- Checksum computation
- Delta configuration
- Conflict detection and resolution
- Conflict resolution strategies
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from shared.mobile_sync.delta import (
    DeltaSyncConfig,
    apply_delta,
    compute_checksum,
    compute_delta,
)
from shared.mobile_sync.models import (
    BilingualMessage,
    ConflictResolutionStrategy,
    ConflictType,
    DeltaChange,
    EntityType,
    SyncConflict,
    SyncDirection,
    SyncItem,
    SyncOperationType,
    SyncPriority,
    SyncStatus,
)
from shared.mobile_sync.resolver import (
    ClientWinsResolver,
    LastWriteWinsResolver,
    ResolutionConfig,
    ServerWinsResolver,
    detect_conflict,
    find_conflicting_fields,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Enum Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestSyncEnums:
    """Test sync-related enums."""

    def test_sync_status_values(self):
        assert SyncStatus.PENDING == "pending"
        assert SyncStatus.SYNCED == "synced"
        assert SyncStatus.CONFLICT == "conflict"
        assert SyncStatus.FAILED == "failed"
        assert len(SyncStatus) == 8

    def test_sync_priority_values(self):
        assert SyncPriority.CRITICAL == "critical"
        assert SyncPriority.BACKGROUND == "background"
        assert len(SyncPriority) == 5

    def test_sync_direction_values(self):
        assert SyncDirection.UPLOAD == "upload"
        assert SyncDirection.DOWNLOAD == "download"
        assert SyncDirection.BIDIRECTIONAL == "bidirectional"

    def test_sync_operation_type(self):
        assert SyncOperationType.CREATE == "create"
        assert SyncOperationType.UPDATE == "update"
        assert SyncOperationType.DELETE == "delete"
        assert SyncOperationType.PARTIAL_UPDATE == "partial_update"

    def test_conflict_type_values(self):
        assert ConflictType.UPDATE_UPDATE == "update_update"
        assert ConflictType.UPDATE_DELETE == "update_delete"
        assert ConflictType.SCHEMA_MISMATCH == "schema_mismatch"

    def test_conflict_resolution_strategies(self):
        assert ConflictResolutionStrategy.LAST_WRITE_WINS == "last_write_wins"
        assert ConflictResolutionStrategy.SERVER_WINS == "server_wins"
        assert ConflictResolutionStrategy.FIELD_LEVEL_MERGE == "field_level_merge"

    def test_entity_type_values(self):
        assert EntityType.FIELD == "field"
        assert EntityType.IRRIGATION == "irrigation"
        assert EntityType.SENSOR_READING == "sensor_reading"


# ═══════════════════════════════════════════════════════════════════════════════
# Model Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestSyncItem:
    """Test SyncItem dataclass."""

    def test_basic_creation(self):
        item = SyncItem(
            entity_id="field-123",
            entity_type=EntityType.FIELD,
            operation=SyncOperationType.UPDATE,
            priority=SyncPriority.HIGH,
            direction=SyncDirection.UPLOAD,
            local_data={"name": "North Field", "area_hectares": 5.5},
            user_id="user-001",
            tenant_id="tenant-001",
        )
        assert item.entity_id == "field-123"
        assert item.entity_type == EntityType.FIELD
        assert item.id != ""  # Auto-generated

    def test_defaults(self):
        item = SyncItem(
            entity_id="f-001",
            entity_type=EntityType.FIELD,
            operation=SyncOperationType.CREATE,
        )
        assert item.status == SyncStatus.PENDING
        assert item.priority == SyncPriority.MEDIUM
        assert item.retry_count == 0


class TestSyncConflict:
    """Test SyncConflict dataclass."""

    def test_basic_creation(self):
        conflict = SyncConflict(
            sync_item_id="item-001",
            entity_id="field-123",
            entity_type=EntityType.FIELD,
            conflict_type=ConflictType.UPDATE_UPDATE,
            local_data={"name": "Local Field"},
            server_data={"name": "Server Field"},
            conflicting_fields=["name"],
            local_modified_at=datetime.now(UTC),
            server_modified_at=datetime.now(UTC),
            tenant_id="t-001",
        )
        assert conflict.conflict_type == ConflictType.UPDATE_UPDATE
        assert len(conflict.conflicting_fields) == 1


class TestBilingualMessage:
    """Test BilingualMessage dataclass."""

    def test_basic_creation(self):
        msg = BilingualMessage(en="Sync completed", ar="تمت المزامنة")
        assert msg.en == "Sync completed"
        assert msg.ar == "تمت المزامنة"


# ═══════════════════════════════════════════════════════════════════════════════
# Delta Computation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestComputeChecksum:
    """Test checksum computation."""

    def test_deterministic(self):
        data = {"name": "Field A", "area": 5.5}
        checksum1 = compute_checksum(data)
        checksum2 = compute_checksum(data)
        assert checksum1 == checksum2

    def test_different_data_different_checksum(self):
        data1 = {"name": "Field A"}
        data2 = {"name": "Field B"}
        assert compute_checksum(data1) != compute_checksum(data2)

    def test_order_independent(self):
        """Keys should be sorted for deterministic output."""
        data1 = {"a": 1, "b": 2}
        data2 = {"b": 2, "a": 1}
        assert compute_checksum(data1) == compute_checksum(data2)

    def test_returns_string(self):
        checksum = compute_checksum({"key": "value"})
        assert isinstance(checksum, str)
        assert len(checksum) == 16  # SHA256 truncated to 16 chars


class TestComputeDelta:
    """Test delta computation between data versions."""

    def test_no_changes(self):
        old = {"name": "Field", "area": 5.0}
        new = {"name": "Field", "area": 5.0}
        changes = compute_delta(old, new)
        assert len(changes) == 0

    def test_value_changed(self):
        old = {"name": "Field A", "area": 5.0}
        new = {"name": "Field B", "area": 5.0}
        changes = compute_delta(old, new)
        assert len(changes) == 1
        assert changes[0].field_path == "name"
        assert changes[0].new_value == "Field B"
        assert changes[0].operation == "set"

    def test_field_added(self):
        old = {"name": "Field"}
        new = {"name": "Field", "crop": "wheat"}
        changes = compute_delta(old, new)
        assert len(changes) == 1
        assert changes[0].field_path == "crop"
        assert changes[0].operation == "set"
        assert changes[0].old_value is None

    def test_field_removed(self):
        old = {"name": "Field", "crop": "wheat"}
        new = {"name": "Field"}
        changes = compute_delta(old, new)
        assert len(changes) == 1
        assert changes[0].field_path == "crop"
        assert changes[0].operation == "unset"

    def test_numeric_increment(self):
        old = {"count": 10}
        new = {"count": 15}
        changes = compute_delta(old, new)
        assert len(changes) == 1
        assert changes[0].operation == "increment"

    def test_excluded_fields_skipped(self):
        config = DeltaSyncConfig()
        old = {"name": "Field", "_version": 1, "updated_at": "2025-01-01"}
        new = {"name": "Field", "_version": 2, "updated_at": "2025-01-02"}
        changes = compute_delta(old, new, config)
        # _version and updated_at should be excluded
        assert len(changes) == 0

    def test_nested_object_delta(self):
        old = {"name": "Field", "location": {"lat": 24.7, "lon": 46.6}}
        new = {"name": "Field", "location": {"lat": 24.7, "lon": 46.7}}
        changes = compute_delta(old, new)
        assert len(changes) >= 1

    def test_full_sync_fields_sent_entirely(self):
        """Fields like 'geometry' should be sent in full, not as delta."""
        config = DeltaSyncConfig()
        old = {"geometry": {"type": "Point", "coordinates": [1, 2]}}
        new = {"geometry": {"type": "Point", "coordinates": [3, 4]}}
        changes = compute_delta(old, new, config)
        assert len(changes) == 1
        assert changes[0].operation == "set"
        assert changes[0].new_value == new["geometry"]

    def test_multiple_changes(self):
        old = {"name": "A", "area": 5.0, "crop": "wheat"}
        new = {"name": "B", "area": 10.0, "crop": "wheat"}
        changes = compute_delta(old, new)
        assert len(changes) == 2


class TestApplyDelta:
    """Test applying delta changes to data."""

    def test_apply_set(self):
        data = {"name": "Old", "area": 5.0}
        changes = [
            DeltaChange(field_path="name", old_value="Old", new_value="New", operation="set"),
        ]
        result = apply_delta(data, changes)
        assert result["name"] == "New"
        assert result["area"] == 5.0

    def test_apply_unset(self):
        data = {"name": "Field", "obsolete": True}
        changes = [
            DeltaChange(field_path="obsolete", old_value=True, new_value=None, operation="unset"),
        ]
        result = apply_delta(data, changes)
        assert "obsolete" not in result

    def test_apply_add_new_field(self):
        data = {"name": "Field"}
        changes = [
            DeltaChange(field_path="crop", old_value=None, new_value="wheat", operation="set"),
        ]
        result = apply_delta(data, changes)
        assert result["crop"] == "wheat"


class TestDeltaSyncConfig:
    """Test DeltaSyncConfig."""

    def test_defaults(self):
        config = DeltaSyncConfig()
        assert config.min_savings_percent == 20.0
        assert config.enable_compression is True
        assert "geometry" in config.full_sync_fields
        assert "updated_at" in config.excluded_fields

    def test_to_dict(self):
        config = DeltaSyncConfig()
        d = config.to_dict()
        assert "min_savings_percent" in d
        assert "enable_compression" in d


# ═══════════════════════════════════════════════════════════════════════════════
# Conflict Detection Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestConflictDetection:
    """Test conflict detection logic."""

    @pytest.fixture
    def local_item(self):
        return SyncItem(
            entity_id="field-001",
            entity_type=EntityType.FIELD,
            operation=SyncOperationType.UPDATE,
            local_data={"name": "Local Field", "area": 5.0, "crop": "wheat"},
            local_modified_at=datetime(2025, 1, 15, 10, 0, tzinfo=UTC),
            user_id="user-001",
            tenant_id="t-001",
        )

    def test_no_conflict_when_server_older(self, local_item):
        """No conflict if server was modified before local."""
        conflict = detect_conflict(
            local_item=local_item,
            server_data={"name": "Server Field", "area": 5.0, "crop": "wheat"},
            server_modified_at=datetime(2025, 1, 14, 10, 0, tzinfo=UTC),  # Before local
        )
        assert conflict is None

    def test_update_update_conflict(self, local_item):
        """Conflict when both sides updated the same entity."""
        conflict = detect_conflict(
            local_item=local_item,
            server_data={"name": "Server Field", "area": 5.0, "crop": "wheat"},
            server_modified_at=datetime(2025, 1, 16, 10, 0, tzinfo=UTC),  # After local
        )
        assert conflict is not None
        assert conflict.conflict_type == ConflictType.UPDATE_UPDATE

    def test_delete_update_conflict(self):
        """Conflict when local deletes but server updates."""
        local_item = SyncItem(
            entity_id="field-001",
            entity_type=EntityType.FIELD,
            operation=SyncOperationType.DELETE,
            local_data={"name": "Deleted Field", "area": 5.0, "crop": "wheat"},
            local_modified_at=datetime(2025, 1, 15, 10, 0, tzinfo=UTC),
            user_id="user-001",
            tenant_id="t-001",
        )
        conflict = detect_conflict(
            local_item=local_item,
            server_data={"name": "Updated Field", "area": 10.0, "crop": "wheat"},
            server_modified_at=datetime(2025, 1, 16, 10, 0, tzinfo=UTC),
        )
        assert conflict is not None
        assert conflict.conflict_type == ConflictType.DELETE_UPDATE

    def test_no_conflict_when_no_fields_differ(self, local_item):
        """No conflict if data is identical despite newer server timestamp."""
        conflict = detect_conflict(
            local_item=local_item,
            server_data=local_item.local_data.copy(),
            server_modified_at=datetime(2025, 1, 16, 10, 0, tzinfo=UTC),
        )
        assert conflict is None


class TestFindConflictingFields:
    """Test conflicting field detection."""

    def test_finds_changed_fields(self):
        fields = find_conflicting_fields(
            local_data={"name": "A", "area": 5.0},
            server_data={"name": "B", "area": 5.0},
        )
        assert "name" in fields

    def test_no_conflicts_identical_data(self):
        fields = find_conflicting_fields(
            local_data={"name": "A", "area": 5.0},
            server_data={"name": "A", "area": 5.0},
        )
        assert len(fields) == 0

    def test_with_base_data(self):
        """Using base data to detect true conflicts (both changed from base)."""
        fields = find_conflicting_fields(
            local_data={"name": "Local", "area": 5.0},
            server_data={"name": "Server", "area": 5.0},
            base_data={"name": "Original", "area": 5.0},
        )
        assert "name" in fields


# ═══════════════════════════════════════════════════════════════════════════════
# Conflict Resolution Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestLastWriteWinsResolver:
    """Test last-write-wins conflict resolution."""

    def test_server_is_newer(self):
        resolver = LastWriteWinsResolver()
        conflict = SyncConflict(
            sync_item_id="item-001",
            entity_id="field-001",
            entity_type=EntityType.FIELD,
            conflict_type=ConflictType.UPDATE_UPDATE,
            local_data={"name": "Local"},
            server_data={"name": "Server"},
            conflicting_fields=["name"],
            local_modified_at=datetime(2025, 1, 15, tzinfo=UTC),
            server_modified_at=datetime(2025, 1, 16, tzinfo=UTC),  # Newer
            tenant_id="t-001",
        )
        result = resolver.resolve(conflict)
        assert result is not None
        assert result["name"] == "Server"

    def test_local_is_newer(self):
        resolver = LastWriteWinsResolver()
        conflict = SyncConflict(
            sync_item_id="item-001",
            entity_id="field-001",
            entity_type=EntityType.FIELD,
            conflict_type=ConflictType.UPDATE_UPDATE,
            local_data={"name": "Local"},
            server_data={"name": "Server"},
            conflicting_fields=["name"],
            local_modified_at=datetime(2025, 1, 17, tzinfo=UTC),  # Newer
            server_modified_at=datetime(2025, 1, 16, tzinfo=UTC),
            tenant_id="t-001",
        )
        result = resolver.resolve(conflict)
        assert result is not None
        assert result["name"] == "Local"


class TestServerWinsResolver:
    """Test server-wins conflict resolution."""

    def test_server_always_wins(self):
        resolver = ServerWinsResolver()
        conflict = SyncConflict(
            sync_item_id="item-001",
            entity_id="field-001",
            entity_type=EntityType.FIELD,
            conflict_type=ConflictType.UPDATE_UPDATE,
            local_data={"name": "Local", "area": 10},
            server_data={"name": "Server", "area": 20},
            conflicting_fields=["name", "area"],
            local_modified_at=datetime(2025, 1, 17, tzinfo=UTC),
            server_modified_at=datetime(2025, 1, 15, tzinfo=UTC),
            tenant_id="t-001",
        )
        result = resolver.resolve(conflict)
        assert result is not None
        assert result["name"] == "Server"


class TestClientWinsResolver:
    """Test client-wins conflict resolution."""

    def test_client_always_wins(self):
        resolver = ClientWinsResolver()
        conflict = SyncConflict(
            sync_item_id="item-001",
            entity_id="field-001",
            entity_type=EntityType.FIELD,
            conflict_type=ConflictType.UPDATE_UPDATE,
            local_data={"name": "Local", "area": 10},
            server_data={"name": "Server", "area": 20},
            conflicting_fields=["name", "area"],
            local_modified_at=datetime(2025, 1, 15, tzinfo=UTC),
            server_modified_at=datetime(2025, 1, 17, tzinfo=UTC),
            tenant_id="t-001",
        )
        result = resolver.resolve(conflict)
        assert result is not None
        assert result["name"] == "Local"


class TestResolutionConfig:
    """Test resolution configuration."""

    def test_defaults(self):
        config = ResolutionConfig()
        assert config.default_strategy == ConflictResolutionStrategy.LAST_WRITE_WINS

    def test_custom_strategy(self):
        config = ResolutionConfig(
            default_strategy=ConflictResolutionStrategy.SERVER_WINS,
            auto_resolve_simple=True,
        )
        assert config.default_strategy == ConflictResolutionStrategy.SERVER_WINS
