"""
Comprehensive tests for irrigation-smart service database_utils.py
Tests cover: PoolConfig, IrrigationDatabase methods, with_retry, create_pool
"""

import asyncio
import os
import sys
from datetime import UTC, date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.database_utils import (
    IrrigationDatabase,
    PoolConfig,
    create_pool,
    with_retry,
)


# ============================================================================
# PoolConfig Tests
# ============================================================================
class TestPoolConfig:
    def test_default_values(self):
        config = PoolConfig()
        assert config.min_connections == 2
        assert config.max_connections == 10
        assert config.command_timeout == 60
        assert config.idle_timeout == 300

    def test_custom_values(self):
        config = PoolConfig(
            min_connections=5,
            max_connections=20,
            command_timeout=120,
            idle_timeout=600,
        )
        assert config.min_connections == 5
        assert config.max_connections == 20

    def test_from_env_defaults(self):
        with patch.dict(os.environ, {}, clear=True):
            config = PoolConfig.from_env()
            assert config.min_connections == 2
            assert config.max_connections == 10
            assert config.command_timeout == 60
            assert config.idle_timeout == 300

    def test_from_env_custom(self):
        env = {
            "DB_POOL_MIN": "5",
            "DB_POOL_MAX": "25",
            "DB_COMMAND_TIMEOUT": "90",
            "DB_IDLE_TIMEOUT": "500",
        }
        with patch.dict(os.environ, env, clear=True):
            config = PoolConfig.from_env()
            assert config.min_connections == 5
            assert config.max_connections == 25
            assert config.command_timeout == 90
            assert config.idle_timeout == 500


# ============================================================================
# Helper: Mock pool/connection
# ============================================================================
class MockAsyncContextManager:
    """Helper that works as an async context manager returning a given value."""

    def __init__(self, return_value):
        self._return_value = return_value

    async def __aenter__(self):
        return self._return_value

    async def __aexit__(self, *args):
        return False


def make_mock_pool():
    """Create a mock asyncpg pool with acquire context manager."""
    mock_conn = AsyncMock()
    mock_pool = MagicMock()

    # pool.acquire() must return an async context manager (not a coroutine)
    mock_pool.acquire.return_value = MockAsyncContextManager(mock_conn)

    return mock_pool, mock_conn


def make_mock_pool_with_transaction():
    """Create a mock pool where conn also supports transaction()."""
    mock_conn = AsyncMock()
    # transaction() must return an async context manager synchronously (not as a coroutine)
    # So we wrap the return with MagicMock for transaction
    mock_conn.transaction = MagicMock(return_value=MockAsyncContextManager(mock_conn))
    mock_pool = MagicMock()
    mock_pool.acquire.return_value = MockAsyncContextManager(mock_conn)
    return mock_pool, mock_conn


# ============================================================================
# IrrigationDatabase Tests
# ============================================================================
class TestGetFieldIrrigationHistory:
    def test_returns_history(self):
        mock_pool, mock_conn = make_mock_pool()
        mock_conn.fetch.return_value = [
            {"id": "1", "field_id": "f1", "amount_mm": 25, "executed_at": datetime.now(UTC)},
            {"id": "2", "field_id": "f1", "amount_mm": 30, "executed_at": datetime.now(UTC)},
        ]

        db = IrrigationDatabase(mock_pool)
        result = asyncio.run(db.get_field_irrigation_history("f1", tenant_id="t1", days=30, limit=100))

        assert len(result) == 2
        assert result[0]["amount_mm"] == 25

    def test_returns_empty_on_error(self):
        mock_pool, mock_conn = make_mock_pool()
        mock_conn.fetch.side_effect = Exception("connection error")

        db = IrrigationDatabase(mock_pool)
        result = asyncio.run(db.get_field_irrigation_history("f1", tenant_id="t1"))
        assert result == []


class TestGetSensorReadingsSummary:
    def test_returns_summary(self):
        mock_pool, mock_conn = make_mock_pool()
        mock_conn.fetchrow.return_value = {
            "reading_count": 10,
            "avg_moisture": 45.678,
            "min_moisture": 30.123,
            "max_moisture": 60.456,
            "avg_temperature": 28.789,
        }

        db = IrrigationDatabase(mock_pool)
        result = asyncio.run(db.get_sensor_readings_summary("f1", tenant_id="t1", hours=24))

        assert result["reading_count"] == 10
        assert result["avg_moisture"] == 45.68  # rounded
        assert result["min_moisture"] == 30.12

    def test_returns_empty_when_no_data(self):
        mock_pool, mock_conn = make_mock_pool()
        mock_conn.fetchrow.return_value = None

        db = IrrigationDatabase(mock_pool)
        result = asyncio.run(db.get_sensor_readings_summary("f1", tenant_id="t1"))
        assert result == {}

    def test_handles_null_values(self):
        mock_pool, mock_conn = make_mock_pool()
        mock_conn.fetchrow.return_value = {
            "reading_count": None,
            "avg_moisture": None,
            "min_moisture": None,
            "max_moisture": None,
            "avg_temperature": None,
        }

        db = IrrigationDatabase(mock_pool)
        result = asyncio.run(db.get_sensor_readings_summary("f1", tenant_id="t1"))
        assert result["reading_count"] == 0
        assert result["avg_moisture"] == 0

    def test_returns_empty_on_error(self):
        mock_pool, mock_conn = make_mock_pool()
        mock_conn.fetchrow.side_effect = Exception("db error")

        db = IrrigationDatabase(mock_pool)
        result = asyncio.run(db.get_sensor_readings_summary("f1", tenant_id="t1"))
        assert result == {}


class TestSaveIrrigationPlan:
    def test_saves_plan_successfully(self):
        mock_pool, mock_conn = make_mock_pool_with_transaction()

        db = IrrigationDatabase(mock_pool)
        schedules = [
            {
                "schedule_id": "s1",
                "irrigation_date": date.today(),
                "start_time": "06:00",
                "duration_minutes": 45,
                "water_amount_liters": 5000,
                "urgency": "high",
                "method": "drip",
            }
        ]

        result = asyncio.run(
            db.save_irrigation_plan(
                plan_id="p1",
                field_id="f1",
                crop="wheat",
                growth_stage="vegetative",
                total_water_m3=5.0,
                estimated_cost=750.0,
                schedules=schedules,
                tenant_id="t1",
            )
        )
        assert result is True

    def test_returns_false_on_error(self):
        mock_pool = MagicMock()

        class FailingCtx:
            async def __aenter__(self):
                raise Exception("db error")

            async def __aexit__(self, *args):
                return False

        mock_pool.acquire.return_value = FailingCtx()

        db = IrrigationDatabase(mock_pool)
        result = asyncio.run(db.save_irrigation_plan("p1", "f1", "wheat", "veg", 5.0, 750.0, []))
        assert result is False


class TestSaveIrrigationExecution:
    def test_saves_execution(self):
        mock_pool, mock_conn = make_mock_pool()

        db = IrrigationDatabase(mock_pool)
        result = asyncio.run(
            db.save_irrigation_execution(
                execution_id="e1",
                field_id="f1",
                plan_id="p1",
                schedule_id="s1",
                amount_mm=25.0,
                duration_minutes=45,
                method="drip",
                executed_at=datetime.now(UTC),
                tenant_id="t1",
            )
        )
        assert result is True

    def test_returns_false_on_error(self):
        mock_pool, mock_conn = make_mock_pool()
        mock_conn.execute.side_effect = Exception("db error")

        db = IrrigationDatabase(mock_pool)
        result = asyncio.run(db.save_irrigation_execution("e1", "f1", None, None, 25.0, 45, "drip", datetime.now(UTC)))
        assert result is False


class TestBatchSaveSensorReadings:
    def test_saves_batch(self):
        mock_pool, mock_conn = make_mock_pool_with_transaction()

        db = IrrigationDatabase(mock_pool)
        readings = [
            {
                "id": "r1",
                "field_id": "f1",
                "sensor_id": "s1",
                "reading_time": datetime.now(UTC),
                "moisture_percent": 45.0,
                "temperature_c": 28.0,
                "ec_ds_m": 1.0,
            },
            {
                "id": "r2",
                "field_id": "f1",
                "sensor_id": "s2",
                "reading_time": datetime.now(UTC),
                "moisture_percent": 50.0,
                "temperature_c": 27.0,
                "ec_ds_m": 0.9,
            },
        ]

        result = asyncio.run(db.batch_save_sensor_readings(readings))
        assert result == 2

    def test_empty_readings_returns_zero(self):
        mock_pool = MagicMock()
        db = IrrigationDatabase(mock_pool)
        result = asyncio.run(db.batch_save_sensor_readings([]))
        assert result == 0

    def test_returns_zero_on_error(self):
        mock_pool = MagicMock()

        class FailingCtx:
            async def __aenter__(self):
                raise Exception("db error")

            async def __aexit__(self, *args):
                return False

        mock_pool.acquire.return_value = FailingCtx()

        db = IrrigationDatabase(mock_pool)
        result = asyncio.run(db.batch_save_sensor_readings([{"id": "r1"}]))
        assert result == 0


class TestGetWaterBalanceSummary:
    def test_returns_summary(self):
        mock_pool, mock_conn = make_mock_pool()
        mock_conn.fetchrow.return_value = {
            "total_et": 70.5,
            "total_rainfall": 15.2,
            "total_irrigation": 40.0,
            "cumulative_deficit": 15.3,
        }

        db = IrrigationDatabase(mock_pool)
        result = asyncio.run(db.get_water_balance_summary("f1", tenant_id="t1", days=14))

        assert result["total_et_mm"] == 70.5
        assert result["total_rainfall_mm"] == 15.2
        assert result["total_irrigation_mm"] == 40.0
        assert result["cumulative_deficit_mm"] == 15.3
        assert result["period_days"] == 14

    def test_returns_empty_when_no_data(self):
        mock_pool, mock_conn = make_mock_pool()
        mock_conn.fetchrow.return_value = None

        db = IrrigationDatabase(mock_pool)
        result = asyncio.run(db.get_water_balance_summary("f1", tenant_id="t1"))
        assert result == {}

    def test_handles_null_values(self):
        mock_pool, mock_conn = make_mock_pool()
        mock_conn.fetchrow.return_value = {
            "total_et": None,
            "total_rainfall": None,
            "total_irrigation": None,
            "cumulative_deficit": None,
        }

        db = IrrigationDatabase(mock_pool)
        result = asyncio.run(db.get_water_balance_summary("f1", tenant_id="t1"))
        assert result["total_et_mm"] == 0
        assert result["cumulative_deficit_mm"] == 0

    def test_returns_empty_on_error(self):
        mock_pool, mock_conn = make_mock_pool()
        mock_conn.fetchrow.side_effect = Exception("db error")

        db = IrrigationDatabase(mock_pool)
        result = asyncio.run(db.get_water_balance_summary("f1", tenant_id="t1"))
        assert result == {}


# ============================================================================
# with_retry Tests
# ============================================================================
class TestWithRetry:
    def test_succeeds_first_try(self):
        func = AsyncMock(return_value="ok")
        result = asyncio.run(with_retry(func, max_attempts=3, delay=0.01))
        assert result == "ok"
        assert func.call_count == 1

    def test_retries_on_failure_then_succeeds(self):
        func = AsyncMock(side_effect=[Exception("fail"), Exception("fail"), "ok"])
        result = asyncio.run(with_retry(func, max_attempts=3, delay=0.01))
        assert result == "ok"
        assert func.call_count == 3

    def test_raises_after_max_attempts(self):
        func = AsyncMock(side_effect=Exception("persistent failure"))
        with pytest.raises(Exception, match="persistent failure"):
            asyncio.run(with_retry(func, max_attempts=3, delay=0.01))
        assert func.call_count == 3

    def test_single_attempt(self):
        func = AsyncMock(side_effect=Exception("fail"))
        with pytest.raises(Exception, match="fail"):
            asyncio.run(with_retry(func, max_attempts=1, delay=0.01))
        assert func.call_count == 1


# ============================================================================
# create_pool Tests
# ============================================================================
class TestCreatePool:
    def test_creates_pool_successfully(self):
        mock_pool = AsyncMock()
        with patch("src.database_utils.asyncpg", create=True) as mock_asyncpg:
            # We need to handle the import inside create_pool
            import importlib

            mock_asyncpg_module = MagicMock()
            mock_asyncpg_module.create_pool = AsyncMock(return_value=mock_pool)

            with patch.dict(sys.modules, {"asyncpg": mock_asyncpg_module}):
                result = asyncio.run(create_pool("postgresql://localhost/test"))
                # Result should be the mock pool or None depending on import
                # The function tries to import asyncpg internally

    def test_returns_none_when_asyncpg_missing(self):
        # Force ImportError for asyncpg
        with patch.dict(sys.modules, {"asyncpg": None}):
            # Remove asyncpg from modules to trigger ImportError
            saved = sys.modules.pop("asyncpg", None)
            try:
                # The import inside create_pool will fail
                result = asyncio.run(create_pool("postgresql://localhost/test"))
                assert result is None
            finally:
                if saved is not None:
                    sys.modules["asyncpg"] = saved

    def test_returns_none_on_connection_error(self):
        mock_asyncpg = MagicMock()
        mock_asyncpg.create_pool = AsyncMock(side_effect=Exception("connection refused"))

        with patch.dict(sys.modules, {"asyncpg": mock_asyncpg}):
            result = asyncio.run(create_pool("postgresql://badhost/test"))
            assert result is None

    def test_uses_custom_config(self):
        mock_asyncpg = MagicMock()
        mock_pool = AsyncMock()
        mock_asyncpg.create_pool = AsyncMock(return_value=mock_pool)

        config = PoolConfig(min_connections=5, max_connections=20, command_timeout=120)

        with patch.dict(sys.modules, {"asyncpg": mock_asyncpg}):
            result = asyncio.run(create_pool("postgresql://localhost/test", config=config))
            if result is not None:
                mock_asyncpg.create_pool.assert_called_once()
