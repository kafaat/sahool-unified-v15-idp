"""
SAHOOL Alert Service - Comprehensive Model Tests
Tests for all Pydantic models, enums, validation logic, and edge cases.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

try:
    import pydantic  # noqa: F401
except ImportError:
    pytest.skip("pydantic not installed", allow_module_level=True)

from datetime import UTC, datetime
from uuid import uuid4


# ═══════════════════════════════════════════════════════════════════════════════
# Enum Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestAlertTypeEnum:
    """Exhaustive tests for AlertType enum."""

    def test_all_alert_types_exist(self):
        from src.models import AlertType

        expected = [
            "weather", "pest", "disease", "irrigation", "fertilizer",
            "harvest", "ndvi_low", "ndvi_anomaly", "soil_moisture",
            "equipment", "general",
        ]
        for val in expected:
            assert AlertType(val) == val

    def test_alert_type_is_str_enum(self):
        from src.models import AlertType

        assert isinstance(AlertType.WEATHER, str)
        assert AlertType.WEATHER == "weather"

    def test_alert_type_invalid_value(self):
        from src.models import AlertType

        with pytest.raises(ValueError):
            AlertType("nonexistent_type")

    def test_alert_type_values_count(self):
        from src.models import AlertType

        assert len(AlertType) == 11


class TestAlertSeverityEnum:
    """Exhaustive tests for AlertSeverity enum."""

    def test_all_severities(self):
        from src.models import AlertSeverity

        assert AlertSeverity.CRITICAL == "critical"
        assert AlertSeverity.HIGH == "high"
        assert AlertSeverity.MEDIUM == "medium"
        assert AlertSeverity.LOW == "low"
        assert AlertSeverity.INFO == "info"

    def test_severity_count(self):
        from src.models import AlertSeverity

        assert len(AlertSeverity) == 5

    def test_severity_invalid(self):
        from src.models import AlertSeverity

        with pytest.raises(ValueError):
            AlertSeverity("ultra_critical")


class TestAlertStatusEnum:
    """Exhaustive tests for AlertStatus enum."""

    def test_all_statuses(self):
        from src.models import AlertStatus

        assert AlertStatus.ACTIVE == "active"
        assert AlertStatus.ACKNOWLEDGED == "acknowledged"
        assert AlertStatus.DISMISSED == "dismissed"
        assert AlertStatus.RESOLVED == "resolved"
        assert AlertStatus.EXPIRED == "expired"

    def test_status_count(self):
        from src.models import AlertStatus

        assert len(AlertStatus) == 5


class TestConditionOperatorEnum:
    """Tests for ConditionOperator enum."""

    def test_all_operators(self):
        from src.models import ConditionOperator

        assert ConditionOperator.EQ == "eq"
        assert ConditionOperator.NE == "ne"
        assert ConditionOperator.GT == "gt"
        assert ConditionOperator.GTE == "gte"
        assert ConditionOperator.LT == "lt"
        assert ConditionOperator.LTE == "lte"

    def test_operator_count(self):
        from src.models import ConditionOperator

        assert len(ConditionOperator) == 6


# ═══════════════════════════════════════════════════════════════════════════════
# AlertCreate Model Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestAlertCreateModel:
    """Tests for AlertCreate Pydantic model."""

    def test_minimal_creation(self):
        from src.models import AlertCreate, AlertSeverity, AlertType

        alert = AlertCreate(
            field_id="f1",
            type=AlertType.WEATHER,
            severity=AlertSeverity.LOW,
            title="Test",
            message="Test message",
        )
        assert alert.field_id == "f1"
        assert alert.tenant_id is None
        assert alert.recommendations is None
        assert alert.metadata is None
        assert alert.expires_at is None
        assert alert.source_service is None
        assert alert.correlation_id is None

    def test_full_creation(self):
        from src.models import AlertCreate, AlertSeverity, AlertType

        now = datetime.now(UTC)
        alert = AlertCreate(
            field_id="field-999",
            tenant_id="11111111-1111-1111-1111-111111111111",
            type=AlertType.PEST,
            severity=AlertSeverity.CRITICAL,
            title="Pest detected",
            title_en="Pest detected EN",
            message="High pest count",
            message_en="High pest count EN",
            recommendations=["Spray insecticide"],
            recommendations_en=["Spray insecticide EN"],
            metadata={"pest_type": "aphid", "count": 150},
            expires_at=now,
            source_service="pest-detection-service",
            correlation_id="corr-abc",
        )
        assert alert.tenant_id == "11111111-1111-1111-1111-111111111111"
        assert alert.recommendations == ["Spray insecticide"]
        assert alert.metadata["pest_type"] == "aphid"
        assert alert.expires_at == now

    def test_title_min_length_validation(self):
        from pydantic import ValidationError

        from src.models import AlertCreate, AlertSeverity, AlertType

        with pytest.raises(ValidationError):
            AlertCreate(
                field_id="f1",
                type=AlertType.WEATHER,
                severity=AlertSeverity.LOW,
                title="",  # min_length=1
                message="msg",
            )

    def test_title_max_length_validation(self):
        from pydantic import ValidationError

        from src.models import AlertCreate, AlertSeverity, AlertType

        with pytest.raises(ValidationError):
            AlertCreate(
                field_id="f1",
                type=AlertType.WEATHER,
                severity=AlertSeverity.LOW,
                title="x" * 201,  # max_length=200
                message="msg",
            )

    def test_message_min_length_validation(self):
        from pydantic import ValidationError

        from src.models import AlertCreate, AlertSeverity, AlertType

        with pytest.raises(ValidationError):
            AlertCreate(
                field_id="f1",
                type=AlertType.WEATHER,
                severity=AlertSeverity.LOW,
                title="title",
                message="",  # min_length=1
            )

    def test_message_max_length_validation(self):
        from pydantic import ValidationError

        from src.models import AlertCreate, AlertSeverity, AlertType

        with pytest.raises(ValidationError):
            AlertCreate(
                field_id="f1",
                type=AlertType.WEATHER,
                severity=AlertSeverity.LOW,
                title="title",
                message="x" * 2001,  # max_length=2000
            )

    def test_missing_required_field_id(self):
        from pydantic import ValidationError

        from src.models import AlertCreate, AlertSeverity, AlertType

        with pytest.raises(ValidationError):
            AlertCreate(
                type=AlertType.WEATHER,
                severity=AlertSeverity.LOW,
                title="title",
                message="msg",
            )

    def test_missing_required_type(self):
        from pydantic import ValidationError

        from src.models import AlertCreate

        with pytest.raises(ValidationError):
            AlertCreate(
                field_id="f1",
                severity="low",
                title="title",
                message="msg",
            )

    def test_invalid_type_value(self):
        from pydantic import ValidationError

        from src.models import AlertCreate

        with pytest.raises(ValidationError):
            AlertCreate(
                field_id="f1",
                type="fake_type",
                severity="low",
                title="title",
                message="msg",
            )


# ═══════════════════════════════════════════════════════════════════════════════
# AlertUpdate Model Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestAlertUpdateModel:
    """Tests for AlertUpdate Pydantic model."""

    def test_empty_update(self):
        from src.models import AlertUpdate

        update = AlertUpdate()
        assert update.status is None
        assert update.acknowledged_by is None
        assert update.dismissed_by is None
        assert update.resolved_by is None
        assert update.resolution_note is None

    def test_status_update(self):
        from src.models import AlertStatus, AlertUpdate

        update = AlertUpdate(status=AlertStatus.ACKNOWLEDGED, acknowledged_by="user-1")
        assert update.status == AlertStatus.ACKNOWLEDGED

    def test_resolution_note_max_length(self):
        from pydantic import ValidationError

        from src.models import AlertUpdate

        with pytest.raises(ValidationError):
            AlertUpdate(resolution_note="x" * 1001)  # max_length=1000

    def test_resolution_note_within_limit(self):
        from src.models import AlertUpdate

        update = AlertUpdate(resolution_note="x" * 1000)
        assert len(update.resolution_note) == 1000


# ═══════════════════════════════════════════════════════════════════════════════
# RuleCondition Model Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestRuleConditionModel:
    """Tests for RuleCondition Pydantic model."""

    def test_basic_condition(self):
        from src.models import ConditionOperator, RuleCondition

        cond = RuleCondition(metric="soil_moisture", operator=ConditionOperator.LT, value=20.0)
        assert cond.metric == "soil_moisture"
        assert cond.operator == ConditionOperator.LT
        assert cond.value == 20.0
        assert cond.duration_minutes == 0

    def test_condition_with_duration(self):
        from src.models import ConditionOperator, RuleCondition

        cond = RuleCondition(
            metric="ndvi",
            operator=ConditionOperator.LTE,
            value=0.2,
            duration_minutes=30,
        )
        assert cond.duration_minutes == 30

    def test_condition_negative_duration_rejected(self):
        from pydantic import ValidationError

        from src.models import ConditionOperator, RuleCondition

        with pytest.raises(ValidationError):
            RuleCondition(
                metric="ndvi",
                operator=ConditionOperator.LT,
                value=0.2,
                duration_minutes=-1,  # ge=0
            )


# ═══════════════════════════════════════════════════════════════════════════════
# AlertRuleConfig Model Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestAlertRuleConfigModel:
    """Tests for AlertRuleConfig Pydantic model."""

    def test_basic_config(self):
        from src.models import AlertRuleConfig, AlertSeverity, AlertType

        cfg = AlertRuleConfig(
            type=AlertType.IRRIGATION,
            severity=AlertSeverity.HIGH,
            title="Low Moisture",
        )
        assert cfg.type == AlertType.IRRIGATION
        assert cfg.title_en is None
        assert cfg.message_template is None

    def test_config_with_all_fields(self):
        from src.models import AlertRuleConfig, AlertSeverity, AlertType

        cfg = AlertRuleConfig(
            type=AlertType.SOIL_MOISTURE,
            severity=AlertSeverity.MEDIUM,
            title="Soil Moisture Alert",
            title_en="Soil Moisture Alert EN",
            message_template="Moisture at {value}%",
        )
        assert cfg.title_en == "Soil Moisture Alert EN"
        assert cfg.message_template == "Moisture at {value}%"

    def test_config_title_max_length(self):
        from pydantic import ValidationError

        from src.models import AlertRuleConfig, AlertSeverity, AlertType

        with pytest.raises(ValidationError):
            AlertRuleConfig(
                type=AlertType.WEATHER,
                severity=AlertSeverity.LOW,
                title="x" * 201,
            )


# ═══════════════════════════════════════════════════════════════════════════════
# AlertRuleCreate Model Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestAlertRuleCreateModel:
    """Tests for AlertRuleCreate Pydantic model."""

    def test_basic_rule_create(self):
        from src.models import (
            AlertRuleConfig,
            AlertRuleCreate,
            AlertSeverity,
            AlertType,
            ConditionOperator,
            RuleCondition,
        )

        rule = AlertRuleCreate(
            field_id="field-1",
            name="Test Rule",
            condition=RuleCondition(metric="ndvi", operator=ConditionOperator.LT, value=0.3),
            alert_config=AlertRuleConfig(type=AlertType.NDVI_LOW, severity=AlertSeverity.HIGH, title="NDVI Low"),
        )
        assert rule.enabled is True
        assert rule.cooldown_hours == 24
        assert rule.tenant_id is None

    def test_rule_name_min_length(self):
        from pydantic import ValidationError

        from src.models import (
            AlertRuleConfig,
            AlertRuleCreate,
            AlertSeverity,
            AlertType,
            ConditionOperator,
            RuleCondition,
        )

        with pytest.raises(ValidationError):
            AlertRuleCreate(
                field_id="f1",
                name="",  # min_length=1
                condition=RuleCondition(metric="x", operator=ConditionOperator.LT, value=1),
                alert_config=AlertRuleConfig(type=AlertType.GENERAL, severity=AlertSeverity.LOW, title="T"),
            )

    def test_rule_name_max_length(self):
        from pydantic import ValidationError

        from src.models import (
            AlertRuleConfig,
            AlertRuleCreate,
            AlertSeverity,
            AlertType,
            ConditionOperator,
            RuleCondition,
        )

        with pytest.raises(ValidationError):
            AlertRuleCreate(
                field_id="f1",
                name="x" * 101,  # max_length=100
                condition=RuleCondition(metric="x", operator=ConditionOperator.LT, value=1),
                alert_config=AlertRuleConfig(type=AlertType.GENERAL, severity=AlertSeverity.LOW, title="T"),
            )

    def test_cooldown_hours_bounds(self):
        from pydantic import ValidationError

        from src.models import (
            AlertRuleConfig,
            AlertRuleCreate,
            AlertSeverity,
            AlertType,
            ConditionOperator,
            RuleCondition,
        )

        # Too high
        with pytest.raises(ValidationError):
            AlertRuleCreate(
                field_id="f1",
                name="Rule",
                condition=RuleCondition(metric="x", operator=ConditionOperator.LT, value=1),
                alert_config=AlertRuleConfig(type=AlertType.GENERAL, severity=AlertSeverity.LOW, title="T"),
                cooldown_hours=169,  # le=168
            )

        # Negative
        with pytest.raises(ValidationError):
            AlertRuleCreate(
                field_id="f1",
                name="Rule",
                condition=RuleCondition(metric="x", operator=ConditionOperator.LT, value=1),
                alert_config=AlertRuleConfig(type=AlertType.GENERAL, severity=AlertSeverity.LOW, title="T"),
                cooldown_hours=-1,  # ge=0
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Response Model Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestAlertResponseModel:
    """Tests for AlertResponse Pydantic model."""

    def test_response_from_dict(self):
        from src.models import AlertResponse

        now = datetime.now(UTC)
        data = {
            "id": str(uuid4()),
            "field_id": "field-1",
            "tenant_id": None,
            "type": "weather",
            "severity": "low",
            "status": "active",
            "title": "Title",
            "title_en": None,
            "message": "Msg",
            "message_en": None,
            "recommendations": [],
            "recommendations_en": [],
            "metadata": {},
            "source_service": None,
            "correlation_id": None,
            "created_at": now,
            "expires_at": None,
            "acknowledged_at": None,
            "acknowledged_by": None,
            "dismissed_at": None,
            "dismissed_by": None,
            "resolved_at": None,
            "resolved_by": None,
            "resolution_note": None,
        }
        resp = AlertResponse(**data)
        assert resp.field_id == "field-1"
        assert resp.type == "weather"


class TestAlertStatsModel:
    """Tests for AlertStats Pydantic model."""

    def test_stats_model(self):
        from src.models import AlertStats

        stats = AlertStats(
            total_alerts=100,
            active_alerts=25,
            by_type={"weather": 50, "pest": 50},
            by_severity={"high": 30, "low": 70},
            by_status={"active": 25, "resolved": 75},
            acknowledged_rate=50.0,
            resolved_rate=75.0,
            average_resolution_hours=4.5,
        )
        assert stats.total_alerts == 100
        assert stats.acknowledged_rate == 50.0

    def test_stats_model_none_resolution(self):
        from src.models import AlertStats

        stats = AlertStats(
            total_alerts=0,
            active_alerts=0,
            by_type={},
            by_severity={},
            by_status={},
            acknowledged_rate=0,
            resolved_rate=0,
            average_resolution_hours=None,
        )
        assert stats.average_resolution_hours is None


class TestPaginatedResponseModel:
    """Tests for PaginatedResponse Pydantic model."""

    def test_paginated_response(self):
        from src.models import PaginatedResponse

        resp = PaginatedResponse(
            items=[],
            total=0,
            skip=0,
            limit=50,
            has_more=False,
        )
        assert resp.total == 0
        assert resp.has_more is False

    def test_paginated_has_more_true(self):
        from src.models import PaginatedResponse

        resp = PaginatedResponse(
            items=[],
            total=100,
            skip=0,
            limit=50,
            has_more=True,
        )
        assert resp.has_more is True


class TestAlertRuleResponseModel:
    """Tests for AlertRuleResponse Pydantic model."""

    def test_rule_response(self):
        from src.models import AlertRuleResponse

        now = datetime.now(UTC)
        resp = AlertRuleResponse(
            id=str(uuid4()),
            field_id="f1",
            tenant_id=None,
            name="Rule",
            name_en=None,
            enabled=True,
            condition={"metric": "ndvi", "operator": "lt", "value": 0.3},
            alert_config={"type": "ndvi_low", "severity": "high", "title": "T"},
            cooldown_hours=24,
            last_triggered_at=None,
            created_at=now,
            updated_at=now,
        )
        assert resp.enabled is True
        assert resp.last_triggered_at is None
