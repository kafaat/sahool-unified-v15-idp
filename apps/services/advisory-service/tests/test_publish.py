"""
Event Publisher Tests - Advisory Service
Tests for EventEnvelope, AdvisorPublisher, and get_publisher.
Uses unittest.mock to avoid real NATS connections.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

try:
    from src.events.publish import (
        AdvisorPublisher,
        EventEnvelope,
        get_publisher,
    )
    from src.events.types import (
        SUBJECTS,
        VERSIONS,
        get_subject,
        get_version,
    )
except ImportError:
    pytest.skip("advisory-service dependencies not installed", allow_module_level=True)


# ---------------------------------------------------------------------------
# EventEnvelope
# ---------------------------------------------------------------------------


class TestEventEnvelope:
    """Test EventEnvelope data class."""

    def test_create_factory(self):
        env = EventEnvelope.create(
            event_type="recommendation_issued",
            version=1,
            aggregate_id="field_123",
            tenant_id="tenant_abc",
            correlation_id="corr_1",
            payload={"key": "value"},
        )
        assert env.event_type == "recommendation_issued"
        assert env.version == 1
        assert env.aggregate_id == "field_123"
        assert env.tenant_id == "tenant_abc"
        assert env.correlation_id == "corr_1"
        assert env.payload == {"key": "value"}
        assert env.event_id  # UUID string
        assert env.timestamp  # ISO timestamp

    def test_event_id_is_unique(self):
        env1 = EventEnvelope.create("a", 1, "agg", "t", "c", {})
        env2 = EventEnvelope.create("a", 1, "agg", "t", "c", {})
        assert env1.event_id != env2.event_id

    def test_to_dict(self):
        env = EventEnvelope.create(
            event_type="test_type",
            version=2,
            aggregate_id="agg_1",
            tenant_id="t1",
            correlation_id="c1",
            payload={"data": 42},
        )
        d = env.to_dict()
        assert isinstance(d, dict)
        assert d["event_type"] == "test_type"
        assert d["version"] == 2
        assert d["aggregate_id"] == "agg_1"
        assert d["tenant_id"] == "t1"
        assert d["correlation_id"] == "c1"
        assert d["payload"] == {"data": 42}
        assert "event_id" in d
        assert "timestamp" in d

    def test_to_dict_serializable(self):
        """to_dict result should be JSON-serializable."""
        env = EventEnvelope.create("t", 1, "a", "t", "c", {"val": 1})
        serialized = json.dumps(env.to_dict())
        assert isinstance(serialized, str)


# ---------------------------------------------------------------------------
# Event types helpers
# ---------------------------------------------------------------------------


class TestEventTypes:
    """Test event type constants and helpers."""

    def test_get_subject_known(self):
        subject = get_subject("recommendation_issued")
        assert subject == "sahool.advisory.recommendation_issued"

    def test_get_subject_unknown_fallback(self):
        subject = get_subject("unknown_event_xyz")
        assert subject == "sahool.advisory.unknown_event_xyz"

    def test_get_version_known(self):
        version = get_version("recommendation_issued")
        assert version == 1

    def test_get_version_unknown_defaults_to_1(self):
        version = get_version("unknown_event_xyz")
        assert version == 1

    def test_all_subjects_defined(self):
        expected_types = [
            "recommendation_issued",
            "fertilizer_plan_issued",
            "nutrient_assessment_issued",
            "disease_detected",
        ]
        for et in expected_types:
            assert et in SUBJECTS
            assert SUBJECTS[et].startswith("sahool.advisory.")

    def test_all_versions_defined(self):
        for et in SUBJECTS:
            assert et in VERSIONS


# ---------------------------------------------------------------------------
# AdvisorPublisher
# ---------------------------------------------------------------------------


class TestAdvisorPublisher:
    """Test AdvisorPublisher with mocked NATS."""

    @pytest.fixture
    def publisher(self):
        """Create publisher with mocked NATS."""
        pub = AdvisorPublisher(nats_url="nats://test:4222")
        # Mock the NATS client
        mock_nc = AsyncMock()
        mock_nc.publish = AsyncMock()
        mock_nc.close = AsyncMock()
        pub.nc = mock_nc
        pub._connected = True
        return pub

    @pytest.mark.asyncio
    async def test_publish_sends_message(self, publisher):
        event_id = await publisher.publish(
            event_type="recommendation_issued",
            tenant_id="t1",
            aggregate_id="field_1",
            payload={"severity": "high"},
        )
        assert event_id  # returns UUID string
        publisher.nc.publish.assert_called_once()
        call_args = publisher.nc.publish.call_args
        assert call_args[0][0] == "sahool.advisory.recommendation_issued"

    @pytest.mark.asyncio
    async def test_publish_message_format(self, publisher):
        await publisher.publish(
            event_type="recommendation_issued",
            tenant_id="t1",
            aggregate_id="field_1",
            payload={"key": "val"},
            correlation_id="corr_1",
        )
        call_args = publisher.nc.publish.call_args
        message_bytes = call_args[0][1]
        message = json.loads(message_bytes.decode())
        assert message["event_type"] == "recommendation_issued"
        assert message["tenant_id"] == "t1"
        assert message["aggregate_id"] == "field_1"
        assert message["correlation_id"] == "corr_1"
        assert message["payload"] == {"key": "val"}

    @pytest.mark.asyncio
    async def test_publish_auto_generates_correlation_id(self, publisher):
        await publisher.publish(
            event_type="recommendation_issued",
            tenant_id="t1",
            aggregate_id="f1",
            payload={},
            correlation_id=None,
        )
        call_args = publisher.nc.publish.call_args
        message = json.loads(call_args[0][1].decode())
        assert message["correlation_id"]  # auto-generated UUID

    @pytest.mark.asyncio
    async def test_publish_custom_subject(self, publisher):
        await publisher.publish(
            event_type="recommendation_issued",
            tenant_id="t1",
            aggregate_id="f1",
            payload={},
            subject="custom.subject.here",
        )
        call_args = publisher.nc.publish.call_args
        assert call_args[0][0] == "custom.subject.here"

    @pytest.mark.asyncio
    async def test_publish_recommendation(self, publisher):
        event_id = await publisher.publish_recommendation(
            tenant_id="t1",
            field_id="field_1",
            category="disease",
            severity="high",
            title_ar="تنبيه",
            title_en="Alert",
            actions=["spray_copper"],
            confidence=0.85,
            correlation_id="corr_1",
            details={"extra": True},
        )
        assert event_id
        publisher.nc.publish.assert_called_once()
        call_args = publisher.nc.publish.call_args
        message = json.loads(call_args[0][1].decode())
        assert message["event_type"] == "recommendation_issued"
        assert message["payload"]["category"] == "disease"
        assert message["payload"]["severity"] == "high"
        assert message["payload"]["confidence"] == 0.85
        assert message["payload"]["details"] == {"extra": True}

    @pytest.mark.asyncio
    async def test_publish_recommendation_no_details(self, publisher):
        await publisher.publish_recommendation(
            tenant_id="t1",
            field_id="f1",
            category="disease",
            severity="medium",
            title_ar="ع",
            title_en="E",
            actions=[],
            confidence=0.5,
        )
        call_args = publisher.nc.publish.call_args
        message = json.loads(call_args[0][1].decode())
        assert message["payload"]["details"] == {}

    @pytest.mark.asyncio
    async def test_publish_fertilizer_plan(self, publisher):
        event_id = await publisher.publish_fertilizer_plan(
            tenant_id="t1",
            field_id="field_1",
            crop="tomato",
            stage="vegetative",
            plan=[{"product": "urea", "dose": 50}],
            correlation_id="corr_2",
            notes=["Apply early morning"],
        )
        assert event_id
        call_args = publisher.nc.publish.call_args
        message = json.loads(call_args[0][1].decode())
        assert message["event_type"] == "fertilizer_plan_issued"
        assert message["payload"]["crop"] == "tomato"
        assert message["payload"]["stage"] == "vegetative"
        assert message["payload"]["notes"] == ["Apply early morning"]

    @pytest.mark.asyncio
    async def test_publish_fertilizer_plan_no_notes(self, publisher):
        await publisher.publish_fertilizer_plan(
            tenant_id="t1",
            field_id="f1",
            crop="wheat",
            stage="tillering",
            plan=[],
        )
        call_args = publisher.nc.publish.call_args
        message = json.loads(call_args[0][1].decode())
        assert message["payload"]["notes"] == []

    @pytest.mark.asyncio
    async def test_publish_nutrient_assessment(self, publisher):
        event_id = await publisher.publish_nutrient_assessment(
            tenant_id="t1",
            field_id="field_1",
            deficiency_id="nitrogen_deficiency",
            nutrient="N",
            severity="high",
            title_ar="نقص النيتروجين",
            title_en="Nitrogen Deficiency",
            corrections=[{"type": "fertilizer", "product": "urea"}],
            confidence=0.8,
            correlation_id="corr_3",
        )
        assert event_id
        call_args = publisher.nc.publish.call_args
        message = json.loads(call_args[0][1].decode())
        assert message["event_type"] == "nutrient_assessment_issued"
        assert message["payload"]["deficiency_id"] == "nitrogen_deficiency"
        assert message["payload"]["nutrient"] == "N"

    @pytest.mark.asyncio
    async def test_close_disconnects(self, publisher):
        await publisher.close()
        publisher.nc.close.assert_called_once()
        assert publisher._connected is False

    @pytest.mark.asyncio
    async def test_close_when_not_connected(self):
        pub = AdvisorPublisher()
        pub.nc = None
        pub._connected = False
        await pub.close()  # should not raise

    @pytest.mark.asyncio
    async def test_publish_calls_connect_when_disconnected(self):
        """If not connected, publish should trigger connect."""
        pub = AdvisorPublisher(nats_url="nats://test:4222")
        pub._connected = False
        pub.nc = None

        # Mock connect to set up the nc mock
        async def fake_connect():
            pub.nc = AsyncMock()
            pub.nc.publish = AsyncMock()
            pub._connected = True

        pub.connect = AsyncMock(side_effect=fake_connect)

        event_id = await pub.publish(
            event_type="recommendation_issued",
            tenant_id="t1",
            aggregate_id="f1",
            payload={},
        )
        pub.connect.assert_called_once()
        assert event_id

    @pytest.mark.asyncio
    async def test_publish_raises_on_nats_error(self, publisher):
        """NATS publish error should propagate."""
        publisher.nc.publish.side_effect = Exception("NATS timeout")
        with pytest.raises(Exception, match="NATS timeout"):
            await publisher.publish(
                event_type="recommendation_issued",
                tenant_id="t1",
                aggregate_id="f1",
                payload={},
            )


# ---------------------------------------------------------------------------
# get_publisher singleton
# ---------------------------------------------------------------------------


class TestGetPublisher:
    """Test get_publisher singleton factory."""

    @pytest.mark.asyncio
    async def test_get_publisher_creates_instance(self):
        """get_publisher should return an AdvisorPublisher."""
        import src.events.publish as publish_module

        # Reset singleton
        publish_module._publisher = None

        with patch.object(AdvisorPublisher, "connect", new_callable=AsyncMock):
            publisher = await get_publisher()
            assert isinstance(publisher, AdvisorPublisher)

        # Clean up singleton
        publish_module._publisher = None

    @pytest.mark.asyncio
    async def test_get_publisher_returns_same_instance(self):
        """Subsequent calls should return the same instance."""
        import src.events.publish as publish_module

        publish_module._publisher = None

        with patch.object(AdvisorPublisher, "connect", new_callable=AsyncMock):
            pub1 = await get_publisher()
            pub2 = await get_publisher()
            assert pub1 is pub2

        publish_module._publisher = None
