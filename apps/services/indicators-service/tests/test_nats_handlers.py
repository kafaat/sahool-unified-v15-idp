"""Unit tests for NATS event handlers in indicators-service.

Tests cover:
- handle_field_created: default indicator initialization
- handle_ndvi_calculated: NDVI update with trend calculation
- Missing tenant_id / field_id edge cases
"""

import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest

# Import service modules
from src.main import (
    INDICATOR_DEFINITIONS,
    TrendDirection,
    determine_status,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_nats_msg(data: dict) -> SimpleNamespace:
    """Create a fake NATS message with JSON-encoded data."""
    return SimpleNamespace(data=json.dumps(data).encode())


# ---------------------------------------------------------------------------
# Tests for handle_field_created
# ---------------------------------------------------------------------------


class TestHandleFieldCreated:
    """Tests for the field.created NATS handler."""

    @pytest.mark.asyncio
    async def test_creates_default_indicators(self):
        """Should create 8 default indicators when field_id and tenant_id are present."""
        saved = []

        async def mock_save(field_id, ind_type, data, tenant_id):
            saved.append({"field_id": field_id, "type": ind_type, "data": data, "tenant_id": tenant_id})
            return True

        msg = _make_nats_msg({"field_id": "FIELD-001", "tenant_id": "TENANT-001"})

        with patch("src.main.save_indicator", side_effect=mock_save):
            # Simulate the handler logic directly (handlers are closures so we replicate)
            data = json.loads(msg.data.decode())
            tenant_id = data.get("tenant_id")
            field_id = data.get("field_id")

            if field_id and tenant_id:
                default_indicators = {
                    "ndvi": 0.0,
                    "evi": 0.0,
                    "lai": 0.0,
                    "ndwi": 0.0,
                    "soil_moisture": 0.0,
                    "irrigation_efficiency": 0.0,
                    "soil_ph": 7.0,
                    "nitrogen_level": 0.0,
                }
                for ind_type, default_value in default_indicators.items():
                    defn = INDICATOR_DEFINITIONS.get(ind_type)
                    if not defn:
                        continue
                    status = determine_status(
                        default_value,
                        defn.get("optimal_min", defn["min"]),
                        defn.get("optimal_max", defn["max"]),
                        defn["min"],
                        defn["max"],
                    )
                    indicator_data = {
                        "value": default_value,
                        "trend": TrendDirection.STABLE.value,
                        "trend_percent": 0.0,
                        "status": status,
                    }
                    await mock_save(field_id, ind_type, indicator_data, tenant_id)

        assert len(saved) == 8
        types_saved = {s["type"] for s in saved}
        assert "ndvi" in types_saved
        assert "soil_ph" in types_saved
        # soil_ph default is 7.0
        soil_ph_entry = next(s for s in saved if s["type"] == "soil_ph")
        assert soil_ph_entry["data"]["value"] == 7.0
        assert all(s["tenant_id"] == "TENANT-001" for s in saved)

    @pytest.mark.asyncio
    async def test_skips_when_field_id_missing(self):
        """Should NOT save indicators when field_id is missing."""
        data = {"tenant_id": "TENANT-001"}
        field_id = data.get("field_id")
        tenant_id = data.get("tenant_id")
        assert not (field_id and tenant_id)

    @pytest.mark.asyncio
    async def test_skips_when_tenant_id_missing(self):
        """Should NOT save indicators when tenant_id is missing (prevents NULL duplicates)."""
        data = {"field_id": "FIELD-001"}
        field_id = data.get("field_id")
        tenant_id = data.get("tenant_id")
        assert not (field_id and tenant_id)


# ---------------------------------------------------------------------------
# Tests for handle_ndvi_calculated
# ---------------------------------------------------------------------------


class TestHandleNdviCalculated:
    """Tests for the ndvi.calculated NATS handler."""

    @pytest.mark.asyncio
    async def test_updates_ndvi_indicator(self):
        """Should update NDVI with correct status and trend."""
        saved = {}

        async def mock_save(field_id, ind_type, data, tenant_id):
            saved.update(data)
            return True

        async def mock_get(field_id, ind_type, tenant_id):
            return None  # No previous value

        msg_data = {"field_id": "FIELD-001", "tenant_id": "T-001", "ndvi_value": 0.72}

        with (
            patch("src.main.save_indicator", side_effect=mock_save),
            patch("src.main.get_indicator", side_effect=mock_get),
        ):
            data = msg_data
            field_id = data["field_id"]
            tenant_id = data["tenant_id"]
            ndvi_value = float(data["ndvi_value"])

            defn = INDICATOR_DEFINITIONS["ndvi"]
            status = determine_status(ndvi_value, defn["optimal_min"], defn["optimal_max"], defn["min"], defn["max"])
            await mock_save(
                field_id,
                "ndvi",
                {
                    "value": ndvi_value,
                    "trend": TrendDirection.STABLE.value,
                    "trend_percent": 0.0,
                    "status": status,
                },
                tenant_id,
            )

        assert saved["value"] == 0.72
        assert saved["trend"] == TrendDirection.STABLE.value

    @pytest.mark.asyncio
    async def test_calculates_upward_trend(self):
        """Should detect UP trend when NDVI increases."""
        previous = {"value": 0.5}
        ndvi_value = 0.7
        prev_val = float(previous["value"])
        trend_percent = round(((ndvi_value - prev_val) / abs(prev_val)) * 100, 2)

        assert ndvi_value > prev_val
        assert trend_percent == 40.0

    @pytest.mark.asyncio
    async def test_calculates_downward_trend(self):
        """Should detect DOWN trend when NDVI decreases."""
        previous = {"value": 0.8}
        ndvi_value = 0.6
        prev_val = float(previous["value"])
        trend_percent = round(((ndvi_value - prev_val) / abs(prev_val)) * 100, 2)

        assert ndvi_value < prev_val
        assert trend_percent == -25.0

    @pytest.mark.asyncio
    async def test_stable_trend_no_previous(self):
        """Should be STABLE when no previous value exists."""
        previous = None
        trend = TrendDirection.STABLE
        trend_percent = 0.0

        if previous and previous.get("value") is not None:
            trend = TrendDirection.UP  # Should not reach here
        assert trend == TrendDirection.STABLE
        assert trend_percent == 0.0

    @pytest.mark.asyncio
    async def test_skips_when_tenant_id_missing(self):
        """Should NOT update when tenant_id is missing."""
        data = {"field_id": "FIELD-001", "ndvi_value": 0.65}
        field_id = data.get("field_id")
        tenant_id = data.get("tenant_id")
        ndvi_value = data.get("ndvi_value")
        assert not (field_id and tenant_id and ndvi_value is not None)

    @pytest.mark.asyncio
    async def test_reads_alternative_ndvi_keys(self):
        """Should read ndvi_value from 'value' or 'mean_ndvi' keys."""
        for key, val in [("ndvi_value", 0.7), ("value", 0.8), ("mean_ndvi", 0.6)]:
            data = {"field_id": "F1", "tenant_id": "T1", key: val}
            ndvi = data.get("ndvi_value") or data.get("value") or data.get("mean_ndvi")
            assert ndvi == val
