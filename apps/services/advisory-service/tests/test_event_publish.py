"""
Tests for Event Publisher - advisory-service
"""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.events.publish import AdvisorPublisher, EventEnvelope


class TestEventEnvelope:
    """Tests for EventEnvelope model"""

    def test_create(self):
        envelope = EventEnvelope.create(
            event_type="recommendation_issued",
            version=1,
            aggregate_id="field_123",
            tenant_id="tenant_001",
            correlation_id="corr_123",
            payload={"key": "value"},
        )
        assert envelope.event_type == "recommendation_issued"
        assert envelope.version == 1
        assert envelope.aggregate_id == "field_123"
        assert envelope.tenant_id == "tenant_001"
        assert envelope.correlation_id == "corr_123"
        assert envelope.payload == {"key": "value"}
        # event_id and timestamp should be auto-generated
        assert envelope.event_id is not None
        assert envelope.timestamp is not None

    def test_to_dict(self):
        envelope = EventEnvelope.create(
            event_type="test",
            version=1,
            aggregate_id="agg_1",
            tenant_id="t_1",
            correlation_id="c_1",
            payload={"data": "test"},
        )
        d = envelope.to_dict()
        assert d["event_type"] == "test"
        assert d["version"] == 1
        assert d["aggregate_id"] == "agg_1"
        assert d["tenant_id"] == "t_1"
        assert d["correlation_id"] == "c_1"
        assert d["payload"] == {"data": "test"}
        assert "event_id" in d
        assert "timestamp" in d

    def test_unique_event_ids(self):
        e1 = EventEnvelope.create("t", 1, "a", "t", "c", {})
        e2 = EventEnvelope.create("t", 1, "a", "t", "c", {})
        assert e1.event_id != e2.event_id
class TestAdvisorPublisher:
    """Tests for AdvisorPublisher"""

    @pytest.mark.asyncio
    async def test_connect(self):
        publisher = AdvisorPublisher(nats_url="nats://test:4222")
        mock_nc = AsyncMock()
        with patch("src.events.publish.NATS", return_value=mock_nc):
            await publisher.connect()
            mock_nc.connect.assert_called_once_with("nats://test:4222")
            assert publisher._connected is True

    @pytest.mark.asyncio
    async def test_connect_already_connected(self):
        publisher = AdvisorPublisher()
        publisher._connected = True
        publisher.nc = AsyncMock()
        # Should not reconnect
        await publisher.connect()
        publisher.nc.connect.assert_not_called()

    @pytest.mark.asyncio
    async def test_close(self):
        publisher = AdvisorPublisher()
        publisher.nc = AsyncMock()
        publisher._connected = True
        await publisher.close()
        publisher.nc.close.assert_called_once()
        assert publisher._connected is False

    @pytest.mark.asyncio
    async def test_close_when_not_connected(self):
        publisher = AdvisorPublisher()
        publisher._connected = False
        publisher.nc = None
        await publisher.close()  # Should not raise

    @pytest.mark.asyncio
    async def test_publish(self):
        publisher = AdvisorPublisher()
        publisher.nc = AsyncMock()
        publisher._connected = True

        event_id = await publisher.publish(
            event_type="recommendation_issued",
            tenant_id="t1",
            aggregate_id="f1",
            payload={"test": True},
        )
        assert event_id is not None
        publisher.nc.publish.assert_called_once()
        call_args = publisher.nc.publish.call_args
        subject = call_args[0][0]
        assert subject == "sahool.advisory.recommendation_issued"

    @pytest.mark.asyncio
    async def test_publish_auto_connects(self):
        publisher = AdvisorPublisher(nats_url="nats://test:4222")
        publisher._connected = False
        mock_nc = AsyncMock()
        with patch("src.events.publish.NATS", return_value=mock_nc):
            event_id = await publisher.publish(
                event_type="test",
                tenant_id="t1",
                aggregate_id="a1",
                payload={},
            )
            mock_nc.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_recommendation(self):
        publisher = AdvisorPublisher()
        publisher.nc = AsyncMock()
        publisher._connected = True

        event_id = await publisher.publish_recommendation(
            tenant_id="t1",
            field_id="f1",
            category="disease",
            severity="high",
            title_ar="اشتباه",
            title_en="Suspected",
            actions=["spray_copper"],
            confidence=0.85,
        )
        assert event_id is not None
        publisher.nc.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_fertilizer_plan(self):
        publisher = AdvisorPublisher()
        publisher.nc = AsyncMock()
        publisher._connected = True

        event_id = await publisher.publish_fertilizer_plan(
            tenant_id="t1",
            field_id="f1",
            crop="tomato",
            stage="vegetative",
            plan=[{"product": "Urea", "dose_kg_per_ha": 50}],
            notes=["Apply after irrigation"],
        )
        assert event_id is not None

    @pytest.mark.asyncio
    async def test_publish_nutrient_assessment(self):
        publisher = AdvisorPublisher()
        publisher.nc = AsyncMock()
        publisher._connected = True

        event_id = await publisher.publish_nutrient_assessment(
            tenant_id="t1",
            field_id="f1",
            deficiency_id="nitrogen_deficiency",
            nutrient="N",
            severity="high",
            title_ar="نقص النيتروجين",
            title_en="Nitrogen Deficiency",
            corrections=[],
            confidence=0.7,
        )
        assert event_id is not None
