"""
Tests for Health Check Module
==============================
اختبارات وحدة فحص الصحة

Comprehensive tests for platform health monitoring.

Author: SAHOOL Platform Team
Created: January 2026
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shared.ai.auto_fix.health_check import (
    ComponentType,
    HealthCheckResult,
    HealthChecker,
    HealthReport,
    HealthStatus,
    quick_health_check,
)


# ═══════════════════════════════════════════════════════════════════════════
# Test HealthStatus Enum
# ═══════════════════════════════════════════════════════════════════════════


class TestHealthStatus:
    """Tests for HealthStatus enum."""

    def test_status_values(self):
        """Test all health status values."""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
        assert HealthStatus.UNKNOWN.value == "unknown"


# ═══════════════════════════════════════════════════════════════════════════
# Test ComponentType Enum
# ═══════════════════════════════════════════════════════════════════════════


class TestComponentType:
    """Tests for ComponentType enum."""

    def test_component_values(self):
        """Test all component type values."""
        assert ComponentType.DATABASE.value == "database"
        assert ComponentType.CACHE.value == "cache"
        assert ComponentType.MESSAGE_QUEUE.value == "message_queue"
        assert ComponentType.API_GATEWAY.value == "api_gateway"
        assert ComponentType.SERVICE.value == "service"
        assert ComponentType.CONTAINER.value == "container"


# ═══════════════════════════════════════════════════════════════════════════
# Test HealthCheckResult
# ═══════════════════════════════════════════════════════════════════════════


class TestHealthCheckResult:
    """Tests for HealthCheckResult dataclass."""

    def test_create_result(self):
        """Test creating a health check result."""
        result = HealthCheckResult(
            component="PostgreSQL",
            component_type=ComponentType.DATABASE,
            status=HealthStatus.HEALTHY,
            message="Connection successful",
            message_ar="الاتصال ناجح",
            latency_ms=15.5,
            details={"version": "16.0"},
        )

        assert result.component == "PostgreSQL"
        assert result.status == HealthStatus.HEALTHY
        assert result.latency_ms == 15.5
        assert result.details["version"] == "16.0"

    def test_result_is_healthy(self):
        """Test is_healthy property."""
        healthy = HealthCheckResult(
            component="test",
            component_type=ComponentType.SERVICE,
            status=HealthStatus.HEALTHY,
            message="OK",
            message_ar="تمام",
        )
        assert healthy.is_healthy is True

        unhealthy = HealthCheckResult(
            component="test",
            component_type=ComponentType.SERVICE,
            status=HealthStatus.UNHEALTHY,
            message="Failed",
            message_ar="فشل",
        )
        assert unhealthy.is_healthy is False

    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = HealthCheckResult(
            component="Redis",
            component_type=ComponentType.CACHE,
            status=HealthStatus.DEGRADED,
            message="High latency",
            message_ar="تأخر عالي",
            latency_ms=500.0,
        )

        data = result.to_dict()

        assert data["component"] == "Redis"
        assert data["component_type"] == "cache"
        assert data["status"] == "degraded"
        assert data["latency_ms"] == 500.0


# ═══════════════════════════════════════════════════════════════════════════
# Test HealthReport
# ═══════════════════════════════════════════════════════════════════════════


class TestHealthReport:
    """Tests for HealthReport dataclass."""

    @pytest.fixture
    def sample_results(self):
        """Create sample health check results."""
        return [
            HealthCheckResult(
                component="PostgreSQL",
                component_type=ComponentType.DATABASE,
                status=HealthStatus.HEALTHY,
                message="OK",
                message_ar="تمام",
                latency_ms=10.0,
            ),
            HealthCheckResult(
                component="Redis",
                component_type=ComponentType.CACHE,
                status=HealthStatus.HEALTHY,
                message="OK",
                message_ar="تمام",
                latency_ms=5.0,
            ),
            HealthCheckResult(
                component="NATS",
                component_type=ComponentType.MESSAGE_QUEUE,
                status=HealthStatus.UNHEALTHY,
                message="Connection refused",
                message_ar="تم رفض الاتصال",
            ),
        ]

    def test_report_counts(self, sample_results):
        """Test report counting properties."""
        report = HealthReport(results=sample_results)

        assert report.total_count == 3
        assert report.healthy_count == 2
        assert report.unhealthy_count == 1
        assert report.degraded_count == 0

    def test_overall_status_healthy(self):
        """Test overall status when all healthy."""
        results = [
            HealthCheckResult(
                component="test1",
                component_type=ComponentType.SERVICE,
                status=HealthStatus.HEALTHY,
                message="OK",
                message_ar="تمام",
            ),
            HealthCheckResult(
                component="test2",
                component_type=ComponentType.SERVICE,
                status=HealthStatus.HEALTHY,
                message="OK",
                message_ar="تمام",
            ),
        ]
        report = HealthReport(results=results)

        assert report.overall_status == HealthStatus.HEALTHY

    def test_overall_status_degraded(self):
        """Test overall status when some degraded."""
        results = [
            HealthCheckResult(
                component="test1",
                component_type=ComponentType.SERVICE,
                status=HealthStatus.HEALTHY,
                message="OK",
                message_ar="تمام",
            ),
            HealthCheckResult(
                component="test2",
                component_type=ComponentType.SERVICE,
                status=HealthStatus.DEGRADED,
                message="Slow",
                message_ar="بطيء",
            ),
        ]
        report = HealthReport(results=results)

        assert report.overall_status == HealthStatus.DEGRADED

    def test_overall_status_unhealthy(self, sample_results):
        """Test overall status when any unhealthy."""
        report = HealthReport(results=sample_results)

        assert report.overall_status == HealthStatus.UNHEALTHY

    def test_report_to_dict(self, sample_results):
        """Test converting report to dictionary."""
        report = HealthReport(results=sample_results)
        data = report.to_dict()

        assert data["overall_status"] == "unhealthy"
        assert data["total_count"] == 3
        assert data["healthy_count"] == 2
        assert len(data["results"]) == 3


# ═══════════════════════════════════════════════════════════════════════════
# Test HealthChecker
# ═══════════════════════════════════════════════════════════════════════════


class TestHealthChecker:
    """Tests for HealthChecker class."""

    def test_create_checker(self):
        """Test creating a health checker."""
        from pathlib import Path

        checker = HealthChecker(working_dir="/tmp")

        assert checker.working_dir == Path("/tmp")

    @pytest.mark.asyncio
    async def test_check_port_open(self):
        """Test port checking with mocked connection."""
        checker = HealthChecker()

        with patch("asyncio.wait_for", new_callable=AsyncMock) as mock_wait:
            mock_writer = MagicMock()
            mock_writer.close = MagicMock()
            mock_writer.wait_closed = AsyncMock()
            mock_wait.return_value = (MagicMock(), mock_writer)

            is_open, latency = await checker._check_port("localhost", 5432)

            assert is_open is True
            assert latency >= 0

    @pytest.mark.asyncio
    async def test_check_port_closed(self):
        """Test port checking when connection fails."""
        checker = HealthChecker()

        with patch("asyncio.wait_for", new_callable=AsyncMock) as mock_wait:
            mock_wait.side_effect = ConnectionRefusedError()

            is_open, latency = await checker._check_port("localhost", 5432)

            assert is_open is False

    @pytest.mark.asyncio
    async def test_check_postgresql(self):
        """Test PostgreSQL health check."""
        checker = HealthChecker()

        with patch.object(checker, "_check_port", new_callable=AsyncMock) as mock_port:
            mock_port.return_value = (True, 10.0)

            result = await checker.check_postgresql()

            assert result.component == "PostgreSQL"
            assert result.status == HealthStatus.HEALTHY
            assert result.latency_ms == 10.0

    @pytest.mark.asyncio
    async def test_check_postgresql_down(self):
        """Test PostgreSQL health check when down."""
        checker = HealthChecker()

        with patch.object(checker, "_check_port", new_callable=AsyncMock) as mock_port:
            mock_port.return_value = (False, 0.0)

            result = await checker.check_postgresql()

            assert result.status == HealthStatus.UNHEALTHY

    @pytest.mark.asyncio
    async def test_check_redis(self):
        """Test Redis health check."""
        checker = HealthChecker()

        with patch.object(checker, "_check_port", new_callable=AsyncMock) as mock_port:
            mock_port.return_value = (True, 5.0)

            result = await checker.check_redis()

            assert result.component == "Redis"
            assert result.status == HealthStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_check_nats(self):
        """Test NATS health check."""
        checker = HealthChecker()

        with patch.object(checker, "_check_port", new_callable=AsyncMock) as mock_port:
            mock_port.return_value = (True, 3.0)

            result = await checker.check_nats()

            assert result.component == "NATS"
            assert result.status == HealthStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_check_pgbouncer(self):
        """Test PgBouncer health check."""
        checker = HealthChecker()

        with patch.object(checker, "_check_port", new_callable=AsyncMock) as mock_port:
            mock_port.return_value = (True, 2.0)

            result = await checker.check_pgbouncer()

            assert result.component == "PgBouncer"
            assert result.status == HealthStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_run_full_health_check(self):
        """Test running full health check."""
        checker = HealthChecker()

        with patch.object(checker, "_check_port", new_callable=AsyncMock) as mock_port:
            mock_port.return_value = (True, 5.0)

            with patch.object(checker, "check_docker_containers", new_callable=AsyncMock) as mock_docker:
                mock_docker.return_value = []

                with patch.object(checker, "check_python_dependencies", new_callable=AsyncMock) as mock_py:
                    mock_py.return_value = HealthCheckResult(
                        component="Python Dependencies",
                        component_type=ComponentType.DEPENDENCY,
                        status=HealthStatus.HEALTHY,
                        message="OK",
                        message_ar="تمام",
                    )

                    with patch.object(checker, "check_node_dependencies", new_callable=AsyncMock) as mock_node:
                        mock_node.return_value = HealthCheckResult(
                            component="Node.js Dependencies",
                            component_type=ComponentType.DEPENDENCY,
                            status=HealthStatus.HEALTHY,
                            message="OK",
                            message_ar="تمام",
                        )

                        report = await checker.run_full_health_check()

                        assert report.total_count >= 4
                        assert report.healthy_count >= 4

    @pytest.mark.asyncio
    async def test_check_docker_containers(self):
        """Test Docker container health check."""
        checker = HealthChecker()

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_proc:
            mock_process = MagicMock()
            mock_process.communicate = AsyncMock(
                return_value=(
                    b'{"Name":"postgres","State":"running","Health":""}\n{"Name":"redis","State":"running","Health":""}',
                    b"",
                )
            )
            mock_proc.return_value = mock_process

            results = await checker.check_docker_containers()

            assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_check_docker_containers_not_running(self):
        """Test Docker container check when Docker not running."""
        checker = HealthChecker()

        with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_proc:
            mock_proc.side_effect = Exception("Docker not running")

            results = await checker.check_docker_containers()

            assert len(results) == 1
            assert results[0].status == HealthStatus.UNKNOWN


# ═══════════════════════════════════════════════════════════════════════════
# Test Quick Health Check
# ═══════════════════════════════════════════════════════════════════════════


class TestQuickHealthCheck:
    """Tests for quick_health_check function."""

    @pytest.mark.asyncio
    async def test_quick_health_check(self):
        """Test quick health check function."""
        with patch.object(
            HealthChecker,
            "run_full_health_check",
            new_callable=AsyncMock,
        ) as mock_check:
            mock_check.return_value = HealthReport(
                results=[
                    HealthCheckResult(
                        component="test",
                        component_type=ComponentType.SERVICE,
                        status=HealthStatus.HEALTHY,
                        message="OK",
                        message_ar="تمام",
                    ),
                ]
            )

            report = await quick_health_check()

            assert report.total_count == 1
            assert report.overall_status == HealthStatus.HEALTHY


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
