"""Regression tests for the two new vegetation-analysis-service
consumers:

  * ``sahool.satellite.ndvi.trend``   — multi-week NDVI trend summary
  * ``sahool.phenology.stage_detected`` — phenology-stage detection

These close the "published-but-nobody-listens" gap identified after
PR #1703 (residual gaps + FPAR/fAPAR). Each subscriber must:
  1. accept the AnalysisEvent envelope shape (``data`` + ``action_template``);
  2. create a FieldOps task for actionable signals;
  3. stay quiet for healthy/non-actionable signals;
  4. deduplicate by ``event_id``;
  5. swallow malformed JSON without crashing.
"""

from __future__ import annotations

import json

import pytest

try:
    from unittest.mock import AsyncMock, MagicMock

    from src.rules import (
        rule_from_ndvi_trend,
        rule_from_phenology,
    )
    from src.worker import AgroRulesWorker
except ImportError:  # pragma: no cover
    pytest.skip("agro-rules dependencies not installed", allow_module_level=True)


def _analysis_env(
    event_type: str,
    field_id: str,
    data: dict,
    *,
    event_id: str = "evt-1",
    tenant_id: str = "t1",
    action_template: dict | None = None,
) -> MagicMock:
    """Mirror the envelope produced by ``publish_analysis_event``."""
    msg = MagicMock()
    msg.data = json.dumps(
        {
            "event_id": event_id,
            "event_type": event_type,
            "source_service": "vegetation-analysis-service",
            "tenant_id": tenant_id,
            "field_id": field_id,
            "farmer_id": None,
            "data": data,
            "action_template": action_template,
            "notification_priority": "medium",
        }
    ).encode()
    return msg


# =============================================================================
# rule_from_ndvi_trend — pure function pins
# =============================================================================


class TestRuleFromNdviTrend:
    def test_declining_trend_returns_high_priority_task(self):
        rule = rule_from_ndvi_trend(
            trend_direction="declining",
            anomaly_count=3,
            period_days=30,
            current_ndvi=0.35,
        )
        assert rule is not None
        assert rule.priority == "high"
        assert rule.task_type == "inspection"
        assert "هبوط" in rule.title_ar
        assert "Declining" in rule.title_en

    def test_volatile_with_anomalies_returns_inspection(self):
        rule = rule_from_ndvi_trend(
            trend_direction="volatile",
            anomaly_count=4,
            period_days=45,
            current_ndvi=0.55,
        )
        assert rule is not None
        assert rule.priority == "medium"
        assert rule.task_type == "inspection"

    def test_volatile_single_anomaly_returns_none(self):
        """One anomaly in a volatile series is noise — no task."""
        rule = rule_from_ndvi_trend(
            trend_direction="volatile",
            anomaly_count=1,
            period_days=30,
        )
        assert rule is None

    @pytest.mark.parametrize("direction", ["increasing", "stable"])
    def test_healthy_trends_return_none(self, direction):
        """Increasing and stable trends must NOT generate tasks — otherwise
        every healthy field would spam FieldOps weekly."""
        rule = rule_from_ndvi_trend(
            trend_direction=direction,
            anomaly_count=0,
            period_days=30,
        )
        assert rule is None


# =============================================================================
# rule_from_phenology — pure function pins
# =============================================================================


class TestRuleFromPhenology:
    def test_action_template_wins_over_default(self):
        """When the publisher attaches an action_template, the rule must
        use it verbatim — the vegetation service already ran the
        crop-aware mapping, we just forward."""
        template = {
            "title_ar": "من الخدمة",
            "title_en": "From service",
            "description_ar": "تفاصيل من الخدمة",
            "description_en": "Details from service",
            "action_type": "fertilization",
            "urgency": "urgent",
        }
        rule = rule_from_phenology(
            current_stage="flowering",
            confidence=0.9,
            action_template=template,
        )
        assert rule is not None
        assert rule.title_en == "From service"
        assert rule.task_type == "fertilization"
        assert rule.priority == "urgent"
        assert rule.urgency_hours == 12  # urgent -> 12h per the map

    @pytest.mark.parametrize(
        "urgency,expected_priority,expected_hours",
        [
            ("critical", "critical", 6),
            ("urgent", "urgent", 12),
            ("high", "high", 24),
            ("medium", "medium", 48),
            ("low", "low", 72),
            ("bogus", "medium", 48),  # unknown collapses to the medium default
        ],
    )
    def test_urgency_round_trips_to_priority_including_critical(self, urgency, expected_priority, expected_hours):
        """Regression pin (Copilot review #1704): ``critical`` must pass
        through to ``priority`` — previously it was silently downgraded
        to ``medium`` because the whitelist excluded it, while
        ``hours_map`` still set the right 6h urgency. Keep these two
        tables in lockstep."""
        rule = rule_from_phenology(
            current_stage="flowering",
            confidence=0.9,
            action_template={"urgency": urgency},
        )
        assert rule is not None
        assert rule.priority == expected_priority
        assert rule.urgency_hours == expected_hours

    @pytest.mark.parametrize(
        "stage,expected_priority",
        [
            ("flowering", "high"),
            ("fruiting", "high"),
            ("grain_filling", "high"),
            ("maturity", "medium"),
            ("harvest_ready", "urgent"),
            ("senescence", "medium"),
        ],
    )
    def test_fallback_table_covers_major_stages(self, stage, expected_priority):
        rule = rule_from_phenology(current_stage=stage, confidence=0.8)
        assert rule is not None
        assert rule.priority == expected_priority

    def test_early_stages_return_none(self):
        """Germination/vegetative transitions are not actionable on their
        own — covered by NDVI rules already."""
        for stage in ("germination", "vegetative", "unknown"):
            assert rule_from_phenology(current_stage=stage, confidence=0.9) is None

    def test_low_confidence_returns_none(self):
        """Don't create tasks off low-confidence detections."""
        rule = rule_from_phenology(current_stage="flowering", confidence=0.3)
        assert rule is None


# =============================================================================
# Worker — _handle_ndvi_trend
# =============================================================================


class TestHandleNdviTrend:
    @pytest.mark.asyncio
    async def test_declining_creates_task(self):
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock(return_value={"id": "t1"})

        msg = _analysis_env(
            event_type="satellite.ndvi.trend",
            field_id="field-7",
            event_id="trend-1",
            data={
                "field_id": "field-7",
                "trend_direction": "declining",
                "current_ndvi": 0.38,
                "average_ndvi": 0.45,
                "period_days": 30,
                "data_points": 12,
                "has_anomalies": True,
                "anomaly_count": 3,
            },
        )

        await worker._handle_ndvi_trend(msg)
        worker.fieldops.create_task.assert_called_once()
        kwargs = worker.fieldops.create_task.call_args.kwargs
        assert kwargs["priority"] == "high"
        assert kwargs["tenant_id"] == "t1"
        assert kwargs["field_id"] == "field-7"
        assert kwargs["task_type"] == "inspection"

    @pytest.mark.asyncio
    async def test_increasing_trend_no_task(self):
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock()

        msg = _analysis_env(
            event_type="satellite.ndvi.trend",
            field_id="field-8",
            event_id="trend-healthy",
            data={
                "trend_direction": "increasing",
                "anomaly_count": 0,
                "period_days": 30,
            },
        )
        await worker._handle_ndvi_trend(msg)
        worker.fieldops.create_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_deduplicates_by_event_id(self):
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock(return_value={"id": "t1"})

        msg = _analysis_env(
            event_type="satellite.ndvi.trend",
            field_id="field-9",
            event_id="trend-dup",
            data={"trend_direction": "declining", "anomaly_count": 2, "period_days": 30},
        )
        await worker._handle_ndvi_trend(msg)
        await worker._handle_ndvi_trend(msg)
        assert worker.fieldops.create_task.call_count == 1

    @pytest.mark.asyncio
    async def test_swallows_malformed_json(self):
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock()

        bad = MagicMock()
        bad.data = b"not-json"

        # Must not raise
        await worker._handle_ndvi_trend(bad)
        worker.fieldops.create_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_missing_field_id_skipped(self):
        """Envelope without field_id/aggregate_id must not call fieldops —
        otherwise we'd create unroutable tasks."""
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock()

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "event_id": "trend-no-field",
                "tenant_id": "t1",
                "data": {"trend_direction": "declining", "anomaly_count": 2, "period_days": 30},
            }
        ).encode()
        await worker._handle_ndvi_trend(msg)
        worker.fieldops.create_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_accepts_legacy_aggregate_id_key(self):
        """ndvi-processor events ship `aggregate_id` instead of `field_id` —
        the handler must accept both so we don't need a flag day."""
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock(return_value={"id": "t1"})

        msg = MagicMock()
        msg.data = json.dumps(
            {
                "event_id": "trend-legacy",
                "tenant_id": "t1",
                "aggregate_id": "legacy-field",
                "data": {"trend_direction": "declining", "anomaly_count": 3, "period_days": 30},
            }
        ).encode()
        await worker._handle_ndvi_trend(msg)
        worker.fieldops.create_task.assert_called_once()
        assert worker.fieldops.create_task.call_args.kwargs["field_id"] == "legacy-field"


# =============================================================================
# Worker — _handle_phenology_stage_detected
# =============================================================================


class TestHandlePhenologyStageDetected:
    @pytest.mark.asyncio
    async def test_uses_attached_action_template(self):
        """If the publisher attached an action_template the task body
        must come from that template, not the fallback table."""
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock(return_value={"id": "t1"})

        msg = _analysis_env(
            event_type="phenology.stage_detected",
            field_id="field-10",
            event_id="pheno-1",
            data={
                "crop_type": "wheat",
                "current_stage": "flowering",
                "stage_ar": "إزهار",
                "stage_en": "Flowering",
                "days_in_stage": 5,
                "season_progress_percent": 55.0,
                "confidence": 0.9,
            },
            action_template={
                "title_ar": "توصية إزهار مخصصة",
                "title_en": "Custom flowering advisory",
                "description_ar": "تفاصيل مخصصة",
                "description_en": "Custom details",
                "action_type": "fertilization",
                "urgency": "urgent",
            },
        )

        await worker._handle_phenology_stage_detected(msg)
        worker.fieldops.create_task.assert_called_once()
        kwargs = worker.fieldops.create_task.call_args.kwargs
        assert kwargs["priority"] == "urgent"
        assert kwargs["task_type"] == "fertilization"
        assert kwargs["title"] == "توصية إزهار مخصصة"

    @pytest.mark.asyncio
    async def test_falls_back_to_stage_table_when_no_template(self):
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock(return_value={"id": "t1"})

        msg = _analysis_env(
            event_type="phenology.stage_detected",
            field_id="field-11",
            event_id="pheno-2",
            data={
                "crop_type": "wheat",
                "current_stage": "harvest_ready",
                "confidence": 0.85,
            },
        )

        await worker._handle_phenology_stage_detected(msg)
        worker.fieldops.create_task.assert_called_once()
        kwargs = worker.fieldops.create_task.call_args.kwargs
        assert kwargs["priority"] == "urgent"
        assert kwargs["task_type"] == "phenology"

    @pytest.mark.asyncio
    async def test_early_stage_no_task(self):
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock()

        msg = _analysis_env(
            event_type="phenology.stage_detected",
            field_id="field-12",
            event_id="pheno-early",
            data={
                "crop_type": "wheat",
                "current_stage": "germination",
                "confidence": 0.9,
            },
        )
        await worker._handle_phenology_stage_detected(msg)
        worker.fieldops.create_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_low_confidence_no_task(self):
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock()

        msg = _analysis_env(
            event_type="phenology.stage_detected",
            field_id="field-13",
            event_id="pheno-lowconf",
            data={
                "crop_type": "wheat",
                "current_stage": "flowering",
                "confidence": 0.3,
            },
        )
        await worker._handle_phenology_stage_detected(msg)
        worker.fieldops.create_task.assert_not_called()

    @pytest.mark.asyncio
    async def test_deduplicates_by_event_id(self):
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock(return_value={"id": "t1"})

        msg = _analysis_env(
            event_type="phenology.stage_detected",
            field_id="field-14",
            event_id="pheno-dup",
            data={"current_stage": "fruiting", "confidence": 0.9},
        )
        await worker._handle_phenology_stage_detected(msg)
        await worker._handle_phenology_stage_detected(msg)
        assert worker.fieldops.create_task.call_count == 1

    @pytest.mark.asyncio
    async def test_swallows_malformed_json(self):
        worker = AgroRulesWorker()
        worker.fieldops.create_task = AsyncMock()

        bad = MagicMock()
        bad.data = b"not-json"

        await worker._handle_phenology_stage_detected(bad)
        worker.fieldops.create_task.assert_not_called()


# =============================================================================
# Subscribers are actually registered on start()
# =============================================================================


class TestSubscribersRegistered:
    """Pin that both new subjects are subscribed at startup — otherwise
    the events stay orphaned even if the handlers exist."""

    @pytest.mark.asyncio
    async def test_start_subscribes_to_trend_and_phenology_subjects(self, monkeypatch):
        worker = AgroRulesWorker()

        fake_nc = AsyncMock()
        fake_nc.connect = AsyncMock()
        fake_nc.subscribe = AsyncMock()

        async def _fake_connect(url):
            return None

        fake_nc.connect = AsyncMock(side_effect=_fake_connect)

        def _nats_factory():
            return fake_nc

        monkeypatch.setattr("src.worker.NATS", _nats_factory)

        await worker.start()

        subscribed_subjects = [
            call.args[0] if call.args else call.kwargs.get("subject") for call in fake_nc.subscribe.call_args_list
        ]

        assert "sahool.satellite.ndvi.trend" in subscribed_subjects
        assert "sahool.tenant.*.satellite.ndvi.trend" in subscribed_subjects
        assert "sahool.phenology.stage_detected" in subscribed_subjects
        assert "sahool.tenant.*.phenology.stage_detected" in subscribed_subjects
