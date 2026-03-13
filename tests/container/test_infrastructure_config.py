"""
Infrastructure Configuration Tests for SAHOOL Platform.

Validates Docker Compose and infrastructure configuration for:
1. PostgreSQL graceful shutdown (stop_grace_period)
2. PgBouncer init-readiness check in entrypoint
3. Kong worker processes limit
4. Service dependency health conditions
5. NATS healthcheck availability

FIX (2026-03-13): Created after discovering startup race conditions between
PostgreSQL init scripts, PgBouncer, and Kong workers.
"""

import re
import pytest
import yaml
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
DOCKER_COMPOSE_PATH = REPO_ROOT / "docker-compose.yml"
PGBOUNCER_ENTRYPOINT = REPO_ROOT / "infrastructure" / "core" / "pgbouncer" / "entrypoint.sh"


@pytest.fixture(scope="module")
def compose_config():
    """Parse docker-compose.yml."""
    content = DOCKER_COMPOSE_PATH.read_text()
    # Handle docker compose env var syntax that yaml parser can't handle
    # Replace ${VAR:?msg} and ${VAR:-default} with placeholder strings
    # Use unquoted placeholder to avoid breaking YAML strings that already have quotes
    sanitized = re.sub(r"\$\{[^}]+\}", "placeholder", content)
    return yaml.safe_load(sanitized)


@pytest.fixture(scope="module")
def pgbouncer_entrypoint():
    return PGBOUNCER_ENTRYPOINT.read_text()


class TestPostgresConfig:
    """Validate PostgreSQL Docker Compose configuration."""

    def test_stop_grace_period_set(self, compose_config):
        """PostgreSQL must have stop_grace_period for clean shutdown."""
        postgres = compose_config["services"]["postgres"]
        assert "stop_grace_period" in postgres, (
            "PostgreSQL service missing stop_grace_period. "
            "This causes WAL recovery on restart due to unclean shutdown."
        )

    def test_stop_grace_period_sufficient(self, compose_config):
        """stop_grace_period should be at least 15s for checkpoint completion."""
        postgres = compose_config["services"]["postgres"]
        grace = postgres.get("stop_grace_period", "0s")
        seconds = int(re.match(r"(\d+)", str(grace)).group(1))
        assert seconds >= 15, (
            f"PostgreSQL stop_grace_period is {grace}, should be at least 15s "
            "to allow checkpoint completion."
        )

    def test_healthcheck_configured(self, compose_config):
        """PostgreSQL must have healthcheck for dependency ordering."""
        postgres = compose_config["services"]["postgres"]
        assert "healthcheck" in postgres
        hc = postgres["healthcheck"]
        assert "test" in hc
        assert hc.get("retries", 0) >= 3

    def test_start_period_sufficient(self, compose_config):
        """PostgreSQL start_period should be >= 60s for PostGIS init."""
        postgres = compose_config["services"]["postgres"]
        hc = postgres.get("healthcheck", {})
        start = hc.get("start_period", "0s")
        seconds = int(re.match(r"(\d+)", str(start)).group(1))
        assert seconds >= 60, (
            f"PostgreSQL start_period is {start}, should be >= 60s for PostGIS initialization."
        )


class TestPgBouncerConfig:
    """Validate PgBouncer configuration."""

    def test_depends_on_postgres_healthy(self, compose_config):
        """PgBouncer must depend on postgres with service_healthy condition."""
        pgbouncer = compose_config["services"]["pgbouncer"]
        deps = pgbouncer.get("depends_on", {})
        assert "postgres" in deps
        assert deps["postgres"].get("condition") == "service_healthy", (
            "PgBouncer must depend on postgres with condition: service_healthy"
        )

    def test_entrypoint_waits_for_init_scripts(self, pgbouncer_entrypoint):
        """PgBouncer entrypoint must check for pgbouncer schema (not just port)."""
        assert "pgbouncer" in pgbouncer_entrypoint.lower()
        # Must check for schema existence, not just TCP port
        assert "schema" in pgbouncer_entrypoint.lower() or "information_schema" in pgbouncer_entrypoint, (
            "PgBouncer entrypoint should check for pgbouncer schema existence, "
            "not just TCP port availability. The port opens before init scripts complete."
        )

    def test_entrypoint_has_two_phase_wait(self, pgbouncer_entrypoint):
        """Entrypoint should have Phase 1 (port check) + Phase 2 (schema check)."""
        # Should have nc -z for port check
        assert "nc -z" in pgbouncer_entrypoint, "Missing TCP port check (nc -z)"
        # Should also have a schema/query check
        assert "information_schema" in pgbouncer_entrypoint or "pgbouncer" in pgbouncer_entrypoint

    def test_scram_hash_generation(self, pgbouncer_entrypoint):
        """Entrypoint should attempt SCRAM-SHA-256 hash generation."""
        assert "SCRAM-SHA-256" in pgbouncer_entrypoint, (
            "PgBouncer entrypoint should attempt SCRAM-SHA-256 hash generation"
        )

    def test_localhost_port_binding(self, compose_config):
        """PgBouncer port must be bound to localhost only."""
        pgbouncer = compose_config["services"]["pgbouncer"]
        ports = pgbouncer.get("ports", [])
        for port in ports:
            assert "127.0.0.1" in str(port), (
                f"PgBouncer port {port} not bound to localhost. Security risk!"
            )


class TestKongConfig:
    """Validate Kong API Gateway configuration."""

    def test_worker_processes_limited(self, compose_config):
        """Kong worker_processes must not be 'auto' (causes 24+ workers on high-core hosts)."""
        kong = compose_config["services"]["kong"]
        env = kong.get("environment", {})
        worker_processes = env.get("KONG_NGINX_WORKER_PROCESSES", "auto")
        assert str(worker_processes) != "auto", (
            "KONG_NGINX_WORKER_PROCESSES should not be 'auto'. "
            "On high-core hosts, 'auto' spawns 24+ workers causing startup timeouts "
            "and event broker connection resets. Use a fixed value like 4."
        )

    def test_worker_processes_reasonable(self, compose_config):
        """Kong worker count should be between 1 and 8."""
        kong = compose_config["services"]["kong"]
        env = kong.get("environment", {})
        workers = env.get("KONG_NGINX_WORKER_PROCESSES", "auto")
        if str(workers) != "auto":
            count = int(str(workers).strip('"'))
            assert 1 <= count <= 8, (
                f"KONG_NGINX_WORKER_PROCESSES is {count}, should be between 1-8. "
                "More workers increase startup contention without proportional throughput gain."
            )

    def test_healthcheck_retries(self, compose_config):
        """Kong healthcheck should have sufficient retries for config loading."""
        kong = compose_config["services"]["kong"]
        hc = kong.get("healthcheck", {})
        retries = hc.get("retries", 0)
        assert retries >= 5, (
            f"Kong healthcheck retries is {retries}, should be >= 5 "
            "to handle declarative config loading time."
        )

    def test_stop_grace_period_set(self, compose_config):
        """Kong must have stop_grace_period for connection draining."""
        kong = compose_config["services"]["kong"]
        assert "stop_grace_period" in kong, (
            "Kong service missing stop_grace_period for graceful connection draining."
        )

    def test_dbless_mode(self, compose_config):
        """Kong should run in DB-less mode for declarative config."""
        kong = compose_config["services"]["kong"]
        env = kong.get("environment", {})
        assert env.get("KONG_DATABASE") == "off", (
            "Kong should use KONG_DATABASE=off for DB-less declarative mode"
        )


class TestNATSConfig:
    """Validate NATS configuration."""

    def test_nats_has_healthcheck(self, compose_config):
        """NATS must have a healthcheck for service_healthy dependencies."""
        nats = compose_config["services"]["nats"]
        assert "healthcheck" in nats, "NATS service must have a healthcheck"

    def test_nats_healthcheck_uses_healthz(self, compose_config):
        """NATS healthcheck should use /healthz monitoring endpoint."""
        nats = compose_config["services"]["nats"]
        hc = nats.get("healthcheck", {})
        test_cmd = str(hc.get("test", ""))
        assert "healthz" in test_cmd or "8222" in test_cmd, (
            "NATS healthcheck should use the /healthz monitoring endpoint"
        )


class TestServiceDependencies:
    """Validate service dependency health conditions."""

    def test_no_service_started_for_db_dependencies(self, compose_config):
        """No service should use service_started for database-related dependencies."""
        services = compose_config.get("services", {})
        violations = []
        db_services = {"postgres", "pgbouncer", "redis", "nats"}

        for svc_name, svc_config in services.items():
            deps = svc_config.get("depends_on", {})
            if isinstance(deps, dict):
                for dep_name, dep_config in deps.items():
                    if dep_name in db_services and isinstance(dep_config, dict):
                        condition = dep_config.get("condition", "")
                        if condition == "service_started":
                            violations.append(f"{svc_name} -> {dep_name}: service_started")

        assert len(violations) == 0, (
            f"Services using service_started for infrastructure dependencies:\n"
            + "\n".join(f"  - {v}" for v in violations)
            + "\nUse service_healthy instead to avoid race conditions."
        )

    def test_pgbouncer_depends_on_postgres(self, compose_config):
        """PgBouncer must depend on PostgreSQL."""
        pgbouncer = compose_config["services"]["pgbouncer"]
        deps = pgbouncer.get("depends_on", {})
        assert "postgres" in deps

    def test_all_healthchecked_services_have_start_period(self, compose_config):
        """Services with healthchecks should have start_period to avoid premature failures."""
        services = compose_config.get("services", {})
        missing_start_period = []

        for svc_name, svc_config in services.items():
            hc = svc_config.get("healthcheck", {})
            if hc and "test" in hc:
                if "start_period" not in hc:
                    missing_start_period.append(svc_name)

        # Allow some services without start_period (they might have very fast startup)
        critical_services = {"postgres", "pgbouncer", "kong", "nats", "redis"}
        missing_critical = [s for s in missing_start_period if s in critical_services]

        assert len(missing_critical) == 0, (
            f"Critical services missing healthcheck start_period: {missing_critical}"
        )
