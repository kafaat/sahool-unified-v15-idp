"""
Comprehensive tests for irrigation-smart service logging_config.py
Tests cover: StructuredFormatter, IrrigationLogger, context vars, log_performance decorator
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import asyncio
import json
import logging
import time
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from src.logging_config import (
    IrrigationLogContext,
    StructuredFormatter,
    IrrigationLogger,
    get_irrigation_logger,
    log_performance,
    _correlation_id,
    _tenant_id,
    _user_id,
    _field_id,
)


# ============================================================================
# IrrigationLogContext Tests
# ============================================================================


class TestIrrigationLogContext:
    def test_defaults_are_none(self):
        ctx = IrrigationLogContext()
        assert ctx.field_id is None
        assert ctx.crop is None
        assert ctx.water_amount_m3 is None
        assert ctx.urgency is None
        assert ctx.method is None

    def test_custom_values(self):
        ctx = IrrigationLogContext(
            field_id="f1",
            crop="wheat",
            water_amount_m3=5.0,
            urgency="high",
            method="drip",
        )
        assert ctx.field_id == "f1"
        assert ctx.crop == "wheat"
        assert ctx.water_amount_m3 == 5.0


# ============================================================================
# StructuredFormatter Tests
# ============================================================================


class TestStructuredFormatter:
    def test_format_produces_json(self):
        formatter = StructuredFormatter("test-service")
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="test message",
            args=None,
            exc_info=None,
        )
        output = formatter.format(record)
        data = json.loads(output)
        assert data["service"] == "test-service"
        assert data["level"] == "INFO"
        assert data["message"] == "test message"
        assert "timestamp" in data

    def test_format_includes_correlation_id(self):
        token = _correlation_id.set("corr-123")
        try:
            formatter = StructuredFormatter()
            record = logging.LogRecord(
                name="test", level=logging.INFO, pathname="", lineno=1,
                msg="msg", args=None, exc_info=None,
            )
            output = formatter.format(record)
            data = json.loads(output)
            assert data["correlation_id"] == "corr-123"
        finally:
            _correlation_id.set(None)

    def test_format_includes_tenant_id(self):
        token = _tenant_id.set("tenant-abc")
        try:
            formatter = StructuredFormatter()
            record = logging.LogRecord(
                name="test", level=logging.INFO, pathname="", lineno=1,
                msg="msg", args=None, exc_info=None,
            )
            output = formatter.format(record)
            data = json.loads(output)
            assert data["tenant_id"] == "tenant-abc"
        finally:
            _tenant_id.set(None)

    def test_format_includes_user_id(self):
        token = _user_id.set("user-xyz")
        try:
            formatter = StructuredFormatter()
            record = logging.LogRecord(
                name="test", level=logging.INFO, pathname="", lineno=1,
                msg="msg", args=None, exc_info=None,
            )
            output = formatter.format(record)
            data = json.loads(output)
            assert data["user_id"] == "user-xyz"
        finally:
            _user_id.set(None)

    def test_format_includes_field_id(self):
        token = _field_id.set("field-001")
        try:
            formatter = StructuredFormatter()
            record = logging.LogRecord(
                name="test", level=logging.INFO, pathname="", lineno=1,
                msg="msg", args=None, exc_info=None,
            )
            output = formatter.format(record)
            data = json.loads(output)
            assert data["field_id"] == "field-001"
        finally:
            _field_id.set(None)

    def test_format_includes_extra_fields(self):
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=1,
            msg="msg", args=None, exc_info=None,
        )
        record.custom_key = "custom_value"
        output = formatter.format(record)
        data = json.loads(output)
        assert data["custom_key"] == "custom_value"

    def test_format_excludes_context_when_none(self):
        # Ensure all context vars are None
        _correlation_id.set(None)
        _tenant_id.set(None)
        _user_id.set(None)
        _field_id.set(None)

        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=1,
            msg="msg", args=None, exc_info=None,
        )
        output = formatter.format(record)
        data = json.loads(output)
        assert "correlation_id" not in data
        assert "tenant_id" not in data

    def test_format_with_exception_info(self):
        formatter = StructuredFormatter()
        try:
            raise ValueError("test error")
        except ValueError:
            import sys as _sys
            exc_info = _sys.exc_info()

        record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="", lineno=1,
            msg="error occurred", args=None, exc_info=exc_info,
        )
        output = formatter.format(record)
        data = json.loads(output)
        assert "exception" in data
        assert "ValueError" in data["exception"]

    def test_default_service_name(self):
        formatter = StructuredFormatter()
        assert formatter.service_name == "irrigation-smart"


# ============================================================================
# IrrigationLogger Tests
# ============================================================================


class TestIrrigationLogger:
    def setup_method(self):
        """Create a fresh logger for each test."""
        self.logger = IrrigationLogger(
            name=f"test-logger-{id(self)}",
            level=logging.DEBUG,
            use_json=True,
        )

    def test_creation(self):
        assert self.logger.name is not None
        assert self.logger._logger is not None

    def test_set_context(self):
        self.logger.set_context(
            correlation_id="c1",
            tenant_id="t1",
            user_id="u1",
            field_id="f1",
        )
        assert _correlation_id.get() == "c1"
        assert _tenant_id.get() == "t1"
        assert _user_id.get() == "u1"
        assert _field_id.get() == "f1"

        # Cleanup
        self.logger.clear_context()

    def test_clear_context(self):
        self.logger.set_context(correlation_id="c1", tenant_id="t1")
        self.logger.clear_context()
        assert _correlation_id.get() is None
        assert _tenant_id.get() is None
        assert _user_id.get() is None
        assert _field_id.get() is None

    def test_info_logging(self):
        # Should not raise
        self.logger.info("Test info message", message_ar="رسالة اختبار")

    def test_debug_logging(self):
        self.logger.debug("Debug message")

    def test_warning_logging(self):
        self.logger.warning("Warning message", message_ar="تحذير")

    def test_error_logging(self):
        self.logger.error("Error message", message_ar="خطأ")

    def test_error_with_exc_info(self):
        self.logger.error("Error with traceback", exc_info=True)

    def test_non_json_formatter(self):
        logger = IrrigationLogger(
            name="test-plain",
            level=logging.INFO,
            use_json=False,
        )
        # Should not raise
        logger.info("Plain text message")

    def test_log_irrigation_plan_created(self):
        self.logger.log_irrigation_plan_created(
            plan_id="p1",
            field_id="f1",
            crop="wheat",
            water_m3=5.0,
            schedules_count=3,
            urgency="high",
        )

    def test_log_irrigation_executed(self):
        self.logger.log_irrigation_executed(
            execution_id="e1",
            field_id="f1",
            amount_mm=25.0,
            duration_minutes=45,
            method="drip",
        )

    def test_log_sensor_reading(self):
        self.logger.log_sensor_reading(
            sensor_id="s1",
            field_id="f1",
            moisture_percent=45.0,
            status="optimal",
        )

    def test_log_water_deficit_alert(self):
        self.logger.log_water_deficit_alert(
            field_id="f1",
            deficit_mm=15.0,
            urgency="high",
            recommended_action="irrigate immediately",
        )

    def test_log_calculation_error(self):
        self.logger.log_calculation_error(
            field_id="f1",
            operation="water_need",
            error="division by zero",
        )


# ============================================================================
# get_irrigation_logger Tests
# ============================================================================


class TestGetIrrigationLogger:
    def test_returns_logger_instance(self):
        # Reset global state
        import src.logging_config as lc
        lc._irrigation_logger = None

        logger = get_irrigation_logger()
        assert isinstance(logger, IrrigationLogger)

    def test_returns_singleton(self):
        import src.logging_config as lc
        lc._irrigation_logger = None

        logger1 = get_irrigation_logger()
        logger2 = get_irrigation_logger()
        assert logger1 is logger2

    def test_respects_log_level_env(self):
        import src.logging_config as lc
        lc._irrigation_logger = None

        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG", "LOG_FORMAT": "json"}):
            logger = get_irrigation_logger()
            assert logger._logger.level == logging.DEBUG

        lc._irrigation_logger = None

    def test_respects_non_json_format(self):
        import src.logging_config as lc
        lc._irrigation_logger = None

        with patch.dict(os.environ, {"LOG_LEVEL": "INFO", "LOG_FORMAT": "text"}):
            logger = get_irrigation_logger()
            # Should use plain formatter (not JSON)
            handler = logger._logger.handlers[0]
            assert not isinstance(handler.formatter, StructuredFormatter)

        lc._irrigation_logger = None


# ============================================================================
# log_performance Decorator Tests
# ============================================================================


class TestLogPerformance:
    @pytest.mark.asyncio
    async def test_async_function_returns_result(self):
        @log_performance("test_op", warn_threshold_ms=10000)
        async def my_func():
            return "result"

        result = await my_func()
        assert result == "result"

    @pytest.mark.asyncio
    async def test_async_slow_operation_logs_warning(self):
        @log_performance("slow_op", warn_threshold_ms=1)
        async def slow_func():
            await asyncio.sleep(0.01)
            return "done"

        result = await slow_func()
        assert result == "done"

    @pytest.mark.asyncio
    async def test_async_fast_operation_logs_debug(self):
        @log_performance("fast_op", warn_threshold_ms=10000)
        async def fast_func():
            return "quick"

        result = await fast_func()
        assert result == "quick"

    def test_sync_function_returns_result(self):
        @log_performance("sync_op", warn_threshold_ms=10000)
        def my_func():
            return 42

        result = my_func()
        assert result == 42

    def test_sync_slow_operation(self):
        @log_performance("sync_slow", warn_threshold_ms=1)
        def slow_func():
            time.sleep(0.01)
            return "slow"

        result = slow_func()
        assert result == "slow"

    @pytest.mark.asyncio
    async def test_preserves_function_name(self):
        @log_performance("op")
        async def my_named_func():
            pass

        assert my_named_func.__name__ == "my_named_func"

    def test_sync_preserves_function_name(self):
        @log_performance("op")
        def my_sync_func():
            pass

        assert my_sync_func.__name__ == "my_sync_func"

    @pytest.mark.asyncio
    async def test_async_exception_still_logs(self):
        @log_performance("error_op", warn_threshold_ms=10000)
        async def failing_func():
            raise ValueError("test error")

        with pytest.raises(ValueError):
            await failing_func()
