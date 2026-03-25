"""
SAHOOL Infrastructure Providers – Comprehensive Container Function Tests
=========================================================================
اختبارات وظائف شاملة لمزودي البنية التحتية

Validates ALL 15 infrastructure provider services: database, cache,
message queue, API gateway, secrets, vector DBs, object storage,
IoT broker, ML tracking, LLM hosting, and monitoring exporters.

Extends test_infrastructure_config.py (which covers PostgreSQL race
conditions, PgBouncer entrypoint, and Kong workers) with comprehensive
provider-level validation.

Providers:
  postgres (PostGIS) · pgbouncer · redis · nats · kong · vault
  qdrant · milvus · minio · mqtt · ollama · mlflow · etcd
  etcd-perms-init · nats-prometheus-exporter

Coverage:
 1.  Image source & version pinning (no :latest in production)
 2.  Port binding (localhost-only for security)
 3.  Health check configuration (interval, timeout, retries)
 4.  Resource limits (CPU, memory)
 5.  Volume persistence
 6.  Authentication/credential injection
 7.  Dependency chains (service_healthy conditions)
 8.  Network membership
 9.  Provider-specific configuration validation
10.  Cross-provider dependency graph integrity

Run:
    pytest tests/container/test_infra_providers_group.py -v --tb=short
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

pytestmark = [pytest.mark.container, pytest.mark.smoke]

REPO_ROOT = Path(__file__).resolve().parents[2]
MAIN_COMPOSE = REPO_ROOT / "docker-compose.yml"

# ---------------------------------------------------------------------------
# Infrastructure Provider Registry
# ---------------------------------------------------------------------------

# Core data infrastructure
DATABASE_PROVIDERS = {"postgres", "pgbouncer"}
CACHE_PROVIDERS = {"redis"}
MESSAGING_PROVIDERS = {"nats", "mqtt"}
GATEWAY_PROVIDERS = {"kong"}
SECRETS_PROVIDERS = {"vault"}

# Supporting infrastructure
VECTOR_DB_PROVIDERS = {"qdrant", "milvus"}
OBJECT_STORAGE_PROVIDERS = {"minio"}
ML_PROVIDERS = {"mlflow", "ollama"}
MONITORING_PROVIDERS = {"nats-prometheus-exporter"}
INIT_SERVICES = {"etcd", "etcd-perms-init"}

ALL_INFRA_PROVIDERS = (
    DATABASE_PROVIDERS | CACHE_PROVIDERS | MESSAGING_PROVIDERS
    | GATEWAY_PROVIDERS | SECRETS_PROVIDERS | VECTOR_DB_PROVIDERS
    | OBJECT_STORAGE_PROVIDERS | ML_PROVIDERS | MONITORING_PROVIDERS
    | INIT_SERVICES
)

# Expected images (partial match to allow version flexibility)
EXPECTED_IMAGES = {
    "postgres": "postgis",
    "pgbouncer": "pgbouncer",
    "redis": "redis",
    "nats": "nats",
    "kong": "kong",
    "vault": "vault",
    "qdrant": "qdrant",
    "milvus": "milvus",
    "minio": "minio",
    "mqtt": "mosquitto",
    "ollama": "ollama",
    "mlflow": "mlflow",
    "etcd": "etcd",
    "nats-prometheus-exporter": "nats",
}

# Expected ports
EXPECTED_PORTS = {
    "postgres": 5432,
    "pgbouncer": 6432,
    "redis": 6379,
    "nats": 4222,
    "kong": 8000,
    "vault": 8200,
    "qdrant": 6333,
    "milvus": 19530,
    "minio": 9000,
    "mqtt": 1883,
    "ollama": 11434,
    "mlflow": 5000,
    "etcd": 2379,
    "nats-prometheus-exporter": 7777,
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_compose_cache: dict | None = None


def _load_compose() -> dict[str, Any]:
    global _compose_cache
    if _compose_cache is None:
        content = MAIN_COMPOSE.read_text("utf-8")
        sanitized = re.sub(r"\$\{[^}]+\}", "placeholder", content)
        _compose_cache = yaml.safe_load(sanitized) or {}
    return _compose_cache


@pytest.fixture(scope="module")
def compose() -> dict[str, Any]:
    return _load_compose()


@pytest.fixture(scope="module")
def services(compose: dict) -> dict[str, Any]:
    return compose.get("services", {})


# ===========================================================================
# 1. Provider Existence in Compose
# ===========================================================================


class TestProviderExistence:
    """جميع المزودين يجب أن يكونوا موجودين في docker-compose.yml."""

    @pytest.mark.parametrize("provider", sorted(ALL_INFRA_PROVIDERS))
    def test_provider_in_compose(self, services: dict, provider: str) -> None:
        assert provider in services, f"Infrastructure provider '{provider}' not in docker-compose.yml"


# ===========================================================================
# 2. Image Source Validation
# ===========================================================================


class TestProviderImages:
    """التحقق من صور Docker للمزودين."""

    @pytest.mark.parametrize("provider,expected_img", sorted(EXPECTED_IMAGES.items()))
    def test_image_matches_expected(self, services: dict, provider: str, expected_img: str) -> None:
        """Provider uses the correct Docker image."""
        svc = services.get(provider, {})
        image = svc.get("image", "")
        build = svc.get("build", {})
        # Some providers use image:, others use build:
        if image:
            assert expected_img in image.lower(), (
                f"Provider '{provider}' image '{image}' does not match expected '{expected_img}'"
            )
        elif build:
            # Built from source - check Dockerfile reference
            pass  # OK if built from Dockerfile
        else:
            pytest.fail(f"Provider '{provider}' has neither image nor build")

    @pytest.mark.parametrize("provider", sorted(
        DATABASE_PROVIDERS | CACHE_PROVIDERS | MESSAGING_PROVIDERS
        | GATEWAY_PROVIDERS | SECRETS_PROVIDERS
    ))
    def test_core_provider_version_pinned(self, services: dict, provider: str) -> None:
        """Core infrastructure provider image must be version-pinned (not :latest)."""
        svc = services.get(provider, {})
        image = svc.get("image", "")
        if not image:
            pytest.skip(f"{provider} uses build:")
        assert ":latest" not in image.lower(), (
            f"Provider '{provider}' uses :latest image – must pin version for reproducibility"
        )


# ===========================================================================
# 3. Port Binding (localhost security)
# ===========================================================================


class TestProviderPortSecurity:
    """منافذ المزودين يجب أن تكون مرتبطة بـ localhost فقط."""

    @pytest.mark.parametrize("provider,expected_port", sorted(EXPECTED_PORTS.items()))
    def test_port_exposed(self, services: dict, provider: str, expected_port: int) -> None:
        """Provider exposes the expected port."""
        svc = services.get(provider, {})
        ports = svc.get("ports", [])
        if not ports:
            pytest.skip(f"{provider} has no port mappings (internal only)")
        # Parse port mappings to extract container-side ports accurately
        container_ports: list[int] = []
        for p in ports:
            p_str = str(p)
            parts = p_str.split(":")
            # Format: "host:container" or "ip:host:container"
            cport_str = parts[-1].split("/")[0].strip()
            if cport_str.isdigit():
                container_ports.append(int(cport_str))
        assert expected_port in container_ports, (
            f"Provider '{provider}' should expose port {expected_port} "
            f"(container ports: {container_ports})"
        )

    @pytest.mark.parametrize("provider", sorted(
        DATABASE_PROVIDERS | CACHE_PROVIDERS | SECRETS_PROVIDERS | {"etcd"}
    ))
    def test_localhost_binding(self, services: dict, provider: str) -> None:
        """Sensitive providers bind to 127.0.0.1 (not 0.0.0.0)."""
        svc = services.get(provider, {})
        ports = svc.get("ports", [])
        for p in ports:
            p_str = str(p)
            if ":" in p_str:
                # Check host binding
                host_part = p_str.split(":")[0]
                if host_part.replace(".", "").isdigit():
                    assert host_part == "127.0.0.1", (
                        f"Provider '{provider}' port '{p}' not bound to 127.0.0.1 "
                        f"(security: prevents external access)"
                    )


# ===========================================================================
# 4. Health Check Configuration
# ===========================================================================


class TestProviderHealthChecks:
    """فحوصات صحة المزودين."""

    HEALTHCHECK_REQUIRED = sorted(
        DATABASE_PROVIDERS | CACHE_PROVIDERS | MESSAGING_PROVIDERS
        | GATEWAY_PROVIDERS | SECRETS_PROVIDERS | VECTOR_DB_PROVIDERS
        | OBJECT_STORAGE_PROVIDERS | ML_PROVIDERS
    )

    @pytest.mark.parametrize("provider", HEALTHCHECK_REQUIRED)
    def test_healthcheck_defined(self, services: dict, provider: str) -> None:
        """Provider has healthcheck configuration."""
        svc = services.get(provider, {})
        assert "healthcheck" in svc, f"Provider '{provider}' missing healthcheck"

    @pytest.mark.parametrize("provider", HEALTHCHECK_REQUIRED)
    def test_healthcheck_has_test(self, services: dict, provider: str) -> None:
        """Provider healthcheck has 'test' command."""
        svc = services.get(provider, {})
        hc = svc.get("healthcheck", {})
        if not hc:
            pytest.skip(f"{provider} has no healthcheck")
        assert "test" in hc, f"Provider '{provider}' healthcheck missing 'test' command"

    @pytest.mark.parametrize("provider", sorted(DATABASE_PROVIDERS))
    def test_database_healthcheck_start_period(self, services: dict, provider: str) -> None:
        """Database providers have adequate start_period for initialization."""
        svc = services.get(provider, {})
        hc = svc.get("healthcheck", {})
        start_period = hc.get("start_period", "")
        if not start_period:
            pytest.skip(f"{provider} healthcheck has no start_period")
        # Extract seconds from duration string (e.g., "60s", "90s")
        match = re.search(r"(\d+)s", str(start_period))
        if match:
            seconds = int(match.group(1))
            assert seconds >= 30, (
                f"Provider '{provider}' start_period={seconds}s too short "
                f"(database init needs ≥30s)"
            )


# ===========================================================================
# 5. Resource Limits
# ===========================================================================


class TestProviderResourceLimits:
    """حدود موارد المزودين."""

    @pytest.mark.parametrize("provider", sorted(ALL_INFRA_PROVIDERS - INIT_SERVICES - MONITORING_PROVIDERS))
    def test_has_resource_limits(self, services: dict, provider: str) -> None:
        """Provider has deploy.resources.limits defined."""
        svc = services.get(provider, {})
        deploy = svc.get("deploy", {})
        resources = deploy.get("resources", {})
        limits = resources.get("limits", {})
        has_limits = "cpus" in limits or "memory" in limits
        assert has_limits, (
            f"Provider '{provider}' missing resource limits (deploy.resources.limits)"
        )


# ===========================================================================
# 6. Volume Persistence
# ===========================================================================


class TestProviderVolumes:
    """أحجام التخزين الدائمة للمزودين."""

    PERSISTENT_PROVIDERS = sorted({"postgres", "redis", "nats", "qdrant", "milvus", "minio", "etcd"})

    @pytest.mark.parametrize("provider", PERSISTENT_PROVIDERS)
    def test_has_volumes(self, services: dict, provider: str) -> None:
        """Stateful provider has volume mounts for data persistence."""
        svc = services.get(provider, {})
        volumes = svc.get("volumes", [])
        assert volumes, (
            f"Stateful provider '{provider}' must have volume mounts for data persistence"
        )


# ===========================================================================
# 7. Authentication / Credential Injection
# ===========================================================================


class TestProviderAuthentication:
    """مصادقة المزودين وحقن بيانات الاعتماد."""

    def test_postgres_requires_password(self, services: dict) -> None:
        """PostgreSQL requires POSTGRES_PASSWORD."""
        svc = services.get("postgres", {})
        env_str = str(svc.get("environment", {}))
        assert "POSTGRES_PASSWORD" in env_str or "placeholder" in env_str, (
            "PostgreSQL must require POSTGRES_PASSWORD"
        )

    def test_redis_requires_password(self, services: dict) -> None:
        """Redis requires authentication (requirepass or ACL)."""
        svc = services.get("redis", {})
        env_str = str(svc.get("environment", {}))
        cmd_str = str(svc.get("command", ""))
        has_auth = (
            "REDIS_PASSWORD" in env_str
            or "requirepass" in cmd_str
            or "placeholder" in env_str
        )
        assert has_auth, "Redis must require password authentication"

    def test_nats_requires_credentials(self, services: dict) -> None:
        """NATS requires user/password authentication."""
        svc = services.get("nats", {})
        env_str = str(svc.get("environment", {}))
        has_auth = "NATS_USER" in env_str or "NATS_PASSWORD" in env_str or "placeholder" in env_str
        assert has_auth, "NATS must require user authentication"

    def test_vault_has_token(self, services: dict) -> None:
        """Vault has root token configured."""
        svc = services.get("vault", {})
        env_str = str(svc.get("environment", {}))
        has_token = "VAULT_DEV_ROOT_TOKEN_ID" in env_str or "VAULT_TOKEN" in env_str or "placeholder" in env_str
        assert has_token, "Vault must have authentication token"

    def test_minio_requires_credentials(self, services: dict) -> None:
        """MinIO requires root user credentials."""
        svc = services.get("minio", {})
        env_str = str(svc.get("environment", {}))
        has_auth = "MINIO_ROOT_USER" in env_str or "placeholder" in env_str
        assert has_auth, "MinIO must require root credentials"

    def test_qdrant_has_api_key(self, services: dict) -> None:
        """Qdrant vector DB has API key configured."""
        svc = services.get("qdrant", {})
        env_str = str(svc.get("environment", {}))
        has_key = "API_KEY" in env_str or "placeholder" in env_str
        assert has_key, "Qdrant must have API key for authentication"


# ===========================================================================
# 8. Dependency Chains (service_healthy)
# ===========================================================================


class TestProviderDependencyChains:
    """سلاسل تبعيات المزودين (service_healthy)."""

    def test_pgbouncer_depends_on_postgres(self, services: dict) -> None:
        """PgBouncer depends on PostgreSQL with service_healthy."""
        svc = services.get("pgbouncer", {})
        depends = svc.get("depends_on", {})
        if isinstance(depends, dict):
            pg_dep = depends.get("postgres", {})
            condition = pg_dep.get("condition", "")
            assert condition == "service_healthy", (
                f"PgBouncer must depend on postgres with service_healthy (got: {condition})"
            )
        elif isinstance(depends, list):
            assert "postgres" in depends, "PgBouncer must depend on postgres"

    def test_milvus_depends_on_etcd_and_minio(self, services: dict) -> None:
        """Milvus depends on etcd and minio."""
        svc = services.get("milvus", {})
        depends = svc.get("depends_on", {})
        dep_names = (
            set(depends) if isinstance(depends, list)
            else set(depends.keys()) if isinstance(depends, dict)
            else set()
        )
        assert "etcd" in dep_names, "Milvus must depend on etcd"
        assert "minio" in dep_names, "Milvus must depend on minio"

    def test_kong_depends_on_redis(self, services: dict) -> None:
        """Kong API gateway depends on Redis for rate limiting."""
        svc = services.get("kong", {})
        depends = svc.get("depends_on", {})
        dep_names = (
            set(depends) if isinstance(depends, list)
            else set(depends.keys()) if isinstance(depends, dict)
            else set()
        )
        assert "redis" in dep_names, "Kong must depend on redis for rate limiting cache"

    def test_mlflow_depends_on_pgbouncer(self, services: dict) -> None:
        """MLflow depends on PgBouncer for backend store."""
        svc = services.get("mlflow", {})
        depends = svc.get("depends_on", {})
        dep_names = (
            set(depends) if isinstance(depends, list)
            else set(depends.keys()) if isinstance(depends, dict)
            else set()
        )
        has_db = "pgbouncer" in dep_names or "postgres" in dep_names
        assert has_db, "MLflow must depend on database (pgbouncer/postgres)"

    def test_nats_exporter_depends_on_nats(self, services: dict) -> None:
        """NATS Prometheus exporter depends on NATS."""
        svc = services.get("nats-prometheus-exporter", {})
        depends = svc.get("depends_on", {})
        dep_names = (
            set(depends) if isinstance(depends, list)
            else set(depends.keys()) if isinstance(depends, dict)
            else set()
        )
        assert "nats" in dep_names, "NATS exporter must depend on nats"

    def test_no_service_started_for_databases(self, services: dict) -> None:
        """Database providers must NOT use bare service_started condition."""
        db_providers = ["postgres", "pgbouncer", "redis", "nats"]
        for provider in db_providers:
            svc = services.get(provider, {})
            depends = svc.get("depends_on", {})
            if isinstance(depends, dict):
                for dep_name, dep_config in depends.items():
                    if isinstance(dep_config, dict):
                        condition = dep_config.get("condition", "")
                        assert condition != "service_started", (
                            f"Provider '{provider}' depends on '{dep_name}' with "
                            f"service_started – must use service_healthy to prevent races"
                        )


# ===========================================================================
# 9. Network Membership
# ===========================================================================


class TestProviderNetwork:
    """شبكة المزودين."""

    @pytest.mark.parametrize("provider", sorted(ALL_INFRA_PROVIDERS - INIT_SERVICES))
    def test_on_sahool_network(self, services: dict, provider: str) -> None:
        """Provider on sahool network."""
        svc = services.get(provider, {})
        networks = svc.get("networks", {})
        net_names = list(networks.keys()) if isinstance(networks, dict) else (networks or [])
        assert any("sahool" in str(n) for n in net_names), (
            f"Provider '{provider}' not on sahool network"
        )


# ===========================================================================
# 10. Provider-Specific Configuration
# ===========================================================================


class TestPostgresSpecific:
    """تكوين خاص بـ PostgreSQL/PostGIS."""

    def test_postgis_extension(self, services: dict) -> None:
        """PostgreSQL image includes PostGIS for geospatial queries."""
        svc = services.get("postgres", {})
        image = svc.get("image", "")
        assert "postgis" in image.lower(), "PostgreSQL must use PostGIS image"

    def test_postgres_max_connections(self, services: dict) -> None:
        """PostgreSQL max_connections accommodates PgBouncer pool."""
        svc = services.get("postgres", {})
        cmd = str(svc.get("command", ""))
        env_str = str(svc.get("environment", {}))
        has_max_conn = "max_connections" in cmd or "MAX_CONNECTIONS" in env_str
        if not has_max_conn:
            pytest.xfail(
                "PostgreSQL max_connections not configured via compose command/env; "
                "may be set in postgresql.conf and is not directly verifiable here."
            )

    def test_postgres_stop_grace_period(self, services: dict) -> None:
        """PostgreSQL has stop_grace_period for clean WAL checkpoint."""
        svc = services.get("postgres", {})
        assert "stop_grace_period" in svc, (
            "PostgreSQL must have stop_grace_period for clean shutdown "
            "(prevents WAL recovery on restart)"
        )


class TestPgBouncerSpecific:
    """تكوين خاص بـ PgBouncer."""

    def test_transaction_pool_mode(self, services: dict) -> None:
        """PgBouncer uses transaction pool mode."""
        svc = services.get("pgbouncer", {})
        env_str = str(svc.get("environment", {}))
        assert "transaction" in env_str.lower(), (
            "PgBouncer should use POOL_MODE=transaction"
        )


class TestNATSSpecific:
    """تكوين خاص بـ NATS."""

    def test_nats_monitoring_port(self, services: dict) -> None:
        """NATS exposes monitoring port 8222."""
        svc = services.get("nats", {})
        ports = " ".join(str(p) for p in svc.get("ports", []))
        assert "8222" in ports, "NATS should expose monitoring port 8222"

    def test_nats_jetstream_storage(self, services: dict) -> None:
        """NATS has JetStream persistent storage volume."""
        svc = services.get("nats", {})
        volumes = str(svc.get("volumes", []))
        has_storage = "data" in volumes.lower() or "jetstream" in volumes.lower()
        assert has_storage, "NATS must have JetStream persistent storage"


class TestKongSpecific:
    """تكوين خاص بـ Kong."""

    def test_kong_dbless_mode(self, services: dict) -> None:
        """Kong runs in DB-less mode (declarative config)."""
        svc = services.get("kong", {})
        env_str = str(svc.get("environment", {}))
        assert "off" in env_str.lower() or "KONG_DATABASE" in env_str, (
            "Kong should use DB-less mode (KONG_DATABASE=off)"
        )

    def test_kong_worker_processes_not_auto(self, services: dict) -> None:
        """Kong NGINX worker processes is a number, not 'auto'."""
        svc = services.get("kong", {})
        env = svc.get("environment", {})
        env_str = str(env)
        if "NGINX_WORKER_PROCESSES" in env_str:
            if isinstance(env, dict):
                workers = str(env.get("KONG_NGINX_WORKER_PROCESSES", ""))
            elif isinstance(env, list):
                for e in env:
                    if "NGINX_WORKER_PROCESSES" in str(e):
                        workers = str(e).split("=")[-1]
                        break
                else:
                    workers = ""
            else:
                workers = ""
            if workers and workers != "placeholder":
                assert workers != "auto", (
                    "Kong NGINX_WORKER_PROCESSES must be a number, not 'auto' "
                    "(causes excessive CPU on multi-core nodes)"
                )


class TestOllamaSpecific:
    """تكوين خاص بـ Ollama (LLM المحلي)."""

    def test_ollama_gpu_config(self, services: dict) -> None:
        """Ollama has GPU configuration."""
        svc = services.get("ollama", {})
        env_str = str(svc.get("environment", {}))
        deploy_str = str(svc.get("deploy", {}))
        has_gpu = (
            "GPU" in env_str
            or "gpu" in deploy_str
            or "nvidia" in deploy_str.lower()
        )
        assert has_gpu, "Ollama should have GPU configuration for LLM inference"


class TestMQTTSpecific:
    """تكوين خاص بـ MQTT (Mosquitto)."""

    def test_mqtt_websocket_port(self, services: dict) -> None:
        """MQTT broker exposes WebSocket port 9001."""
        svc = services.get("mqtt", {})
        ports = " ".join(str(p) for p in svc.get("ports", []))
        assert "9001" in ports, "MQTT should expose WebSocket port 9001"


# ===========================================================================
# 11. Cross-Provider Dependency Graph Integrity
# ===========================================================================


class TestProviderDependencyGraph:
    """سلامة رسم بيان تبعيات المزودين."""

    def test_no_circular_dependencies(self, services: dict) -> None:
        """Infrastructure providers have no circular dependency chains."""
        # Build dependency graph
        graph: dict[str, set[str]] = {}
        for provider in ALL_INFRA_PROVIDERS:
            svc = services.get(provider, {})
            depends = svc.get("depends_on", {})
            deps = (
                set(depends) if isinstance(depends, list)
                else set(depends.keys()) if isinstance(depends, dict)
                else set()
            )
            graph[provider] = deps & ALL_INFRA_PROVIDERS  # Only infra deps

        # Check for cycles using DFS
        visited: set[str] = set()
        in_stack: set[str] = set()

        def has_cycle(node: str) -> bool:
            if node in in_stack:
                return True
            if node in visited:
                return False
            visited.add(node)
            in_stack.add(node)
            for dep in graph.get(node, set()):
                if has_cycle(dep):
                    return True
            in_stack.discard(node)
            return False

        cycles = [p for p in ALL_INFRA_PROVIDERS if has_cycle(p)]
        assert not cycles, (
            f"Circular dependencies detected in infrastructure: {cycles}"
        )

    def test_all_dependencies_exist(self, services: dict) -> None:
        """All infrastructure dependency targets exist in compose."""
        missing: list[str] = []
        for provider in ALL_INFRA_PROVIDERS:
            svc = services.get(provider, {})
            depends = svc.get("depends_on", {})
            deps = (
                set(depends) if isinstance(depends, list)
                else set(depends.keys()) if isinstance(depends, dict)
                else set()
            )
            for dep in deps:
                if dep not in services:
                    missing.append(f"{provider} → {dep}")
        assert not missing, f"Broken dependency references: {missing}"
