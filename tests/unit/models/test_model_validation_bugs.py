"""
Bug-hunting tests for SAHOOL Model Validation.

Tests target:
- shared/auth/models.py: User, TokenPayload, Permission, AuthErrors, AuthException
- shared/events/models.py: FieldCreatedEvent, TaskCreatedEvent, etc.
- Pydantic model strict mode violations
- Enum values that don't exist
- Fields with None when not Optional

Run:
    ENVIRONMENT=test PYTHONPATH=. pytest tests/unit/models/test_model_validation_bugs.py -v --timeout=30
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")

from shared.auth.models import (  # noqa: E402
    AuthErrorMessage,
    AuthErrors,
    AuthException,
    Permission,
    TokenPayload,
    User,
)
from shared.events.models import (  # noqa: E402
    AdvisorRecommendationEvent,
    AlertCreatedEvent,
    CropPlantedEvent,
    EventMetadata,
    EventMetadataDTO,
    EventPriority,
    EventStatus,
    FieldCreatedEvent,
    FieldUpdatedEvent,
    FarmCreatedEvent,
    TaskCompletedEvent,
    TaskCreatedEvent,
)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Auth Models - User with Missing Fields
# ─────────────────────────────────────────────────────────────────────────────


class TestUserModelValidation:
    """BUG HUNT: User model field validation and edge cases."""

    def test_user_with_all_required_fields(self):
        """User with all required fields should be valid."""
        user = User(
            id="user-123",
            email="test@example.com",
            roles=["farmer"],
        )
        assert user.id == "user-123"
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.is_verified is True

    def test_user_default_values(self):
        """Default values for optional fields should be set correctly."""
        user = User(id="u1", email="t@t.com", roles=[])
        assert user.farm_ids == []
        assert user.tenant_id is None
        assert user.permissions == []
        assert user.is_active is True
        assert user.is_verified is True

    def test_user_has_role(self):
        """has_role should correctly detect roles."""
        user = User(id="u1", email="t@t.com", roles=["admin", "farmer"])
        assert user.has_role("admin") is True
        assert user.has_role("farmer") is True
        assert user.has_role("superadmin") is False

    def test_user_has_any_role(self):
        """has_any_role should return True if user has at least one of the given roles."""
        user = User(id="u1", email="t@t.com", roles=["farmer"])
        assert user.has_any_role("admin", "farmer") is True
        assert user.has_any_role("admin", "superadmin") is False

    def test_user_has_all_roles(self):
        """has_all_roles should return True only if user has ALL given roles."""
        user = User(id="u1", email="t@t.com", roles=["admin", "farmer"])
        assert user.has_all_roles("admin", "farmer") is True
        assert user.has_all_roles("admin", "superadmin") is False

    def test_user_has_farm_access(self):
        """has_farm_access should check farm_ids list."""
        user = User(id="u1", email="t@t.com", roles=[], farm_ids=["farm-1", "farm-2"])
        assert user.has_farm_access("farm-1") is True
        assert user.has_farm_access("farm-3") is False

    def test_user_has_permission(self):
        """has_permission should check permissions list."""
        user = User(id="u1", email="t@t.com", roles=[], permissions=["farm:read"])
        assert user.has_permission("farm:read") is True
        assert user.has_permission("farm:write") is False

    def test_user_empty_roles_methods_dont_crash(self):
        """BUG HUNT: Methods with empty roles/permissions should not crash."""
        user = User(id="u1", email="t@t.com", roles=[])
        assert user.has_role("admin") is False
        assert user.has_any_role("admin") is False
        assert user.has_all_roles() is True  # vacuously true
        assert user.has_farm_access("farm-1") is False
        assert user.has_permission("anything") is False

    def test_user_with_none_email(self):
        """BUG HUNT: User model uses str for email, not Optional[str]. None should fail."""
        # User is a dataclass with email: str, not Optional[str]
        # However, Python dataclasses don't enforce types at runtime
        user = User(id="u1", email=None, roles=[])  # type: ignore
        # This documents a potential bug: dataclass doesn't validate types
        # In a strict system, this should raise an error
        assert user.email is None  # Dataclass allows this


# ─────────────────────────────────────────────────────────────────────────────
# 2. TokenPayload Model Validation
# ─────────────────────────────────────────────────────────────────────────────


class TestTokenPayloadValidation:
    """BUG HUNT: TokenPayload model edge cases."""

    def test_token_payload_all_fields(self):
        """TokenPayload with all fields should work."""
        now = datetime.now(UTC)
        payload = TokenPayload(
            user_id="u1",
            roles=["farmer"],
            exp=now,
            iat=now,
            tenant_id="t1",
            jti="jti-123",
            token_type="access",
            permissions=["farm:read"],
        )
        assert payload.user_id == "u1"
        assert payload.token_type == "access"
        assert payload.permissions == ["farm:read"]

    def test_token_payload_defaults(self):
        """TokenPayload with only required fields should have correct defaults."""
        now = datetime.now(UTC)
        payload = TokenPayload(
            user_id="u1",
            roles=["farmer"],
            exp=now,
            iat=now,
        )
        assert payload.tenant_id is None
        assert payload.jti is None
        assert payload.token_type == "access"
        assert payload.permissions == []

    def test_token_payload_has_role(self):
        """has_role should work correctly."""
        now = datetime.now(UTC)
        payload = TokenPayload(
            user_id="u1",
            roles=["admin", "farmer"],
            exp=now,
            iat=now,
        )
        assert payload.has_role("admin") is True
        assert payload.has_role("superadmin") is False

    def test_token_payload_has_permission(self):
        """has_permission should check permissions list."""
        now = datetime.now(UTC)
        payload = TokenPayload(
            user_id="u1",
            roles=[],
            exp=now,
            iat=now,
            permissions=["farm:read", "farm:write"],
        )
        assert payload.has_permission("farm:read") is True
        assert payload.has_permission("farm:delete") is False

    def test_token_payload_empty_roles_safe(self):
        """BUG HUNT: Empty roles list should not crash any method."""
        now = datetime.now(UTC)
        payload = TokenPayload(user_id="u1", roles=[], exp=now, iat=now)
        assert payload.has_role("anything") is False
        assert payload.has_any_role("a", "b") is False
        assert payload.has_all_roles() is True  # vacuously true

    def test_token_payload_with_none_user_id(self):
        """BUG HUNT: None user_id -- dataclass doesn't enforce types at runtime."""
        now = datetime.now(UTC)
        # This documents a weakness: dataclass allows None for str fields
        payload = TokenPayload(user_id=None, roles=[], exp=now, iat=now)  # type: ignore
        assert payload.user_id is None


# ─────────────────────────────────────────────────────────────────────────────
# 3. Permission Enum Validation
# ─────────────────────────────────────────────────────────────────────────────


class TestPermissionEnum:
    """BUG HUNT: Permission StrEnum edge cases."""

    def test_all_permissions_are_strings(self):
        """All Permission enum values should be strings."""
        for perm in Permission:
            assert isinstance(perm, str), f"Permission {perm.name} is not a string"
            assert isinstance(perm.value, str)

    def test_permission_format_is_resource_colon_action(self):
        """All permissions should follow 'resource:action' format."""
        for perm in Permission:
            assert ":" in perm.value, (
                f"Permission {perm.name} = {perm.value!r} doesn't follow 'resource:action' format"
            )

    def test_invalid_permission_string_not_in_enum(self):
        """A string not in the enum should not match any Permission."""
        assert "nonexistent:permission" not in [p.value for p in Permission]

    def test_permission_lookup_by_value(self):
        """Should be able to look up Permission by its string value."""
        perm = Permission("farm:read")
        assert perm == Permission.FARM_READ

    def test_invalid_permission_lookup_raises(self):
        """Looking up a non-existent permission value should raise ValueError."""
        with pytest.raises(ValueError):
            Permission("invalid:perm")

    def test_permissions_are_unique(self):
        """No two Permission members should have the same value."""
        values = [p.value for p in Permission]
        assert len(values) == len(set(values)), "Duplicate permission values found"


# ─────────────────────────────────────────────────────────────────────────────
# 4. AuthErrors and AuthException
# ─────────────────────────────────────────────────────────────────────────────


class TestAuthErrorsAndException:
    """BUG HUNT: AuthErrors constants and AuthException behavior."""

    def test_all_error_messages_have_bilingual_text(self):
        """Every AuthErrorMessage must have non-empty en, ar, and code."""
        error_attrs = [
            AuthErrors.INVALID_TOKEN,
            AuthErrors.EXPIRED_TOKEN,
            AuthErrors.MISSING_TOKEN,
            AuthErrors.INVALID_CREDENTIALS,
            AuthErrors.INSUFFICIENT_PERMISSIONS,
            AuthErrors.ACCOUNT_DISABLED,
            AuthErrors.ACCOUNT_NOT_VERIFIED,
            AuthErrors.TOKEN_REVOKED,
            AuthErrors.RATE_LIMIT_EXCEEDED,
            AuthErrors.INVALID_ISSUER,
            AuthErrors.INVALID_AUDIENCE,
        ]
        for err in error_attrs:
            assert isinstance(err, AuthErrorMessage), f"{err} is not an AuthErrorMessage"
            assert err.en, f"Missing English message for code={err.code}"
            assert err.ar, f"Missing Arabic message for code={err.code}"
            assert err.code, f"Missing error code"

    def test_auth_exception_to_dict_english(self):
        """AuthException.to_dict should return English by default."""
        exc = AuthException(AuthErrors.INVALID_TOKEN)
        d = exc.to_dict("en")
        assert d["error"] == "invalid_token"
        assert "message" in d
        assert d["status_code"] == 401

    def test_auth_exception_to_dict_arabic(self):
        """AuthException.to_dict with lang='ar' should return Arabic message."""
        exc = AuthException(AuthErrors.INVALID_TOKEN)
        d = exc.to_dict("ar")
        assert d["error"] == "invalid_token"
        # Arabic message should differ from English
        d_en = exc.to_dict("en")
        assert d["message"] != d_en["message"]

    def test_auth_exception_custom_status_code(self):
        """AuthException should accept custom status codes."""
        exc = AuthException(AuthErrors.INSUFFICIENT_PERMISSIONS, status_code=403)
        assert exc.status_code == 403

    def test_error_codes_are_unique(self):
        """All AuthErrors error codes must be unique."""
        codes = []
        for attr_name in dir(AuthErrors):
            attr = getattr(AuthErrors, attr_name)
            if isinstance(attr, AuthErrorMessage):
                codes.append(attr.code)
        assert len(codes) == len(set(codes)), f"Duplicate error codes found: {codes}"


# ─────────────────────────────────────────────────────────────────────────────
# 5. Events Models (shared/events/models.py) Validation
# ─────────────────────────────────────────────────────────────────────────────


class TestEventsModelValidation:
    """BUG HUNT: Test event models from shared/events/models.py with invalid data."""

    def test_field_created_event_missing_required_fields(self):
        """FieldCreatedEvent without required fields must raise ValidationError."""
        with pytest.raises(ValidationError):
            FieldCreatedEvent()  # Missing all required fields

    def test_field_created_event_valid(self):
        """FieldCreatedEvent with all required fields should succeed."""
        event = FieldCreatedEvent(
            field_id=uuid4(),
            farm_id=uuid4(),
            name="Test Field",
            geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
            created_at=datetime.now(UTC),
        )
        assert event.name == "Test Field"

    def test_task_created_invalid_priority(self):
        """TaskCreatedEvent with invalid priority pattern must be rejected."""
        with pytest.raises(ValidationError):
            TaskCreatedEvent(
                task_id=uuid4(),
                tenant_id=uuid4(),
                title="Test Task",
                priority="super_urgent",  # Not in pattern
                created_at=datetime.now(UTC),
            )

    def test_task_created_valid_priorities(self):
        """TaskCreatedEvent should accept valid priority values."""
        for priority in ["low", "medium", "high", "urgent"]:
            event = TaskCreatedEvent(
                task_id=uuid4(),
                tenant_id=uuid4(),
                title="Test",
                priority=priority,
                created_at=datetime.now(UTC),
            )
            assert event.priority == priority

    def test_advisor_recommendation_invalid_type(self):
        """AdvisorRecommendationEvent with invalid recommendation_type must fail."""
        with pytest.raises(ValidationError):
            AdvisorRecommendationEvent(
                recommendation_id=uuid4(),
                field_id=uuid4(),
                tenant_id=uuid4(),
                recommendation_type="weather",  # Not in pattern
                title="Test",
                description="Test",
                priority="low",
                confidence_score=0.5,
                created_at=datetime.now(UTC),
            )

    def test_advisor_recommendation_valid_types(self):
        """AdvisorRecommendationEvent should accept valid recommendation_type values."""
        for rec_type in ["irrigation", "fertilizer", "pest", "harvest"]:
            event = AdvisorRecommendationEvent(
                recommendation_id=uuid4(),
                field_id=uuid4(),
                tenant_id=uuid4(),
                recommendation_type=rec_type,
                title="Test",
                description="Test",
                priority="low",
                confidence_score=0.5,
                created_at=datetime.now(UTC),
            )
            assert event.recommendation_type == rec_type

    def test_alert_invalid_severity(self):
        """AlertCreatedEvent with invalid severity must be rejected."""
        with pytest.raises(ValidationError):
            AlertCreatedEvent(
                alert_id=uuid4(),
                tenant_id=uuid4(),
                alert_type="weather",
                severity="extreme",  # Not in pattern (info|warning|critical)
                title="Test",
                message="Test",
                created_at=datetime.now(UTC),
            )

    def test_alert_invalid_type(self):
        """AlertCreatedEvent with invalid alert_type must be rejected."""
        with pytest.raises(ValidationError):
            AlertCreatedEvent(
                alert_id=uuid4(),
                tenant_id=uuid4(),
                alert_type="earthquake",  # Not in pattern
                severity="warning",
                title="Test",
                message="Test",
                created_at=datetime.now(UTC),
            )

    def test_confidence_score_out_of_range(self):
        """confidence_score must be 0-1."""
        with pytest.raises(ValidationError):
            AdvisorRecommendationEvent(
                recommendation_id=uuid4(),
                field_id=uuid4(),
                tenant_id=uuid4(),
                recommendation_type="irrigation",
                title="Test",
                description="Test",
                priority="low",
                confidence_score=2.0,  # > 1
                created_at=datetime.now(UTC),
            )

    def test_farm_created_invalid_coordinates(self):
        """FarmCreatedEvent with out-of-range lat/lon must be rejected."""
        with pytest.raises(ValidationError):
            FarmCreatedEvent(
                farm_id=uuid4(),
                tenant_id=uuid4(),
                name="Test Farm",
                location_lat=200.0,  # Invalid
                location_lon=46.0,
                created_at=datetime.now(UTC),
            )

    def test_field_name_too_long(self):
        """Field name exceeding max_length=120 must be rejected."""
        with pytest.raises(ValidationError):
            FieldCreatedEvent(
                field_id=uuid4(),
                farm_id=uuid4(),
                name="A" * 121,  # Over 120 chars
                geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
                created_at=datetime.now(UTC),
            )

    def test_ndvi_value_boundary(self):
        """NDVI at exact boundaries (-1 and 1) should be accepted."""
        event_low = FieldUpdatedEvent(
            field_id=uuid4(),
            ndvi_value=-1.0,
            updated_at=datetime.now(UTC),
        )
        assert event_low.ndvi_value == -1.0

        event_high = FieldUpdatedEvent(
            field_id=uuid4(),
            ndvi_value=1.0,
            updated_at=datetime.now(UTC),
        )
        assert event_high.ndvi_value == 1.0


# ─────────────────────────────────────────────────────────────────────────────
# 6. Event Enum Validation
# ─────────────────────────────────────────────────────────────────────────────


class TestEventEnums:
    """BUG HUNT: Event enum edge cases."""

    def test_event_priority_values(self):
        """EventPriority must contain expected values."""
        assert EventPriority.LOW == "low"
        assert EventPriority.MEDIUM == "medium"
        assert EventPriority.HIGH == "high"
        assert EventPriority.CRITICAL == "critical"

    def test_event_status_values(self):
        """EventStatus must contain expected values."""
        assert EventStatus.PENDING == "pending"
        assert EventStatus.PROCESSING == "processing"
        assert EventStatus.COMPLETED == "completed"
        assert EventStatus.FAILED == "failed"

    def test_invalid_priority_raises(self):
        """Non-existent EventPriority should raise ValueError."""
        with pytest.raises(ValueError):
            EventPriority("extreme")

    def test_invalid_status_raises(self):
        """Non-existent EventStatus should raise ValueError."""
        with pytest.raises(ValueError):
            EventStatus("cancelled")

    def test_event_priority_is_string(self):
        """EventPriority values should be usable as plain strings."""
        assert isinstance(EventPriority.HIGH, str)
        assert EventPriority.HIGH == "high"

    def test_event_status_is_string(self):
        """EventStatus values should be usable as plain strings."""
        assert isinstance(EventStatus.COMPLETED, str)
        assert EventStatus.COMPLETED == "completed"


# ─────────────────────────────────────────────────────────────────────────────
# 7. EventMetadata Model
# ─────────────────────────────────────────────────────────────────────────────


class TestEventMetadataModel:
    """BUG HUNT: EventMetadataDTO / EventMetadata model."""

    def test_all_fields_optional(self):
        """EventMetadataDTO should allow empty construction (all optional)."""
        meta = EventMetadataDTO()
        assert meta.correlation_id is None
        assert meta.causation_id is None
        assert meta.user_id is None
        assert meta.trace_id is None
        assert meta.span_id is None

    def test_backward_compatible_alias(self):
        """EventMetadata should be an alias for EventMetadataDTO."""
        assert EventMetadata is EventMetadataDTO

    def test_with_all_fields(self):
        """EventMetadataDTO with all fields should work."""
        meta = EventMetadataDTO(
            correlation_id="corr-1",
            causation_id="cause-1",
            user_id="user-1",
            trace_id="trace-1",
            span_id="span-1",
        )
        assert meta.correlation_id == "corr-1"
        assert meta.user_id == "user-1"

    def test_serialization_roundtrip(self):
        """EventMetadataDTO should survive JSON roundtrip."""
        meta = EventMetadataDTO(correlation_id="corr-1", user_id="user-1")
        json_str = meta.model_dump_json()
        restored = EventMetadataDTO.model_validate_json(json_str)
        assert restored.correlation_id == "corr-1"
        assert restored.user_id == "user-1"
        assert restored.trace_id is None


# ─────────────────────────────────────────────────────────────────────────────
# 8. Cross-Module Consistency
# ─────────────────────────────────────────────────────────────────────────────


class TestCrossModuleConsistency:
    """BUG HUNT: Test consistency between shared/events/models.py and shared/events/contracts.py."""

    def test_field_created_event_exists_in_both_modules(self):
        """FieldCreatedEvent should exist in both models.py and contracts.py."""
        from shared.events import contracts, models

        assert hasattr(contracts, "FieldCreatedEvent")
        assert hasattr(models, "FieldCreatedEvent")

    def test_base_event_import_from_contracts(self):
        """models.py should import BaseEvent from contracts.py (or define a fallback)."""
        from shared.events.models import BaseEvent

        assert BaseEvent is not None

    def test_field_created_event_both_modules_have_same_fields(self):
        """BUG HUNT: Both FieldCreatedEvent definitions should have compatible fields."""
        from shared.events.contracts import FieldCreatedEvent as ContractEvent
        from shared.events.models import FieldCreatedEvent as ModelEvent

        contract_fields = set(ContractEvent.model_fields.keys())
        model_fields = set(ModelEvent.model_fields.keys())

        # Core fields that must be in both
        common_required = {"field_id", "farm_id", "name", "geometry_wkt"}
        for field in common_required:
            assert field in contract_fields, (
                f"contracts.FieldCreatedEvent missing {field}"
            )
            assert field in model_fields, (
                f"models.FieldCreatedEvent missing {field}"
            )
