"""
SAHOOL Docker Compose Core Configuration Tests
اختبارات تكوين Docker Compose الأساسية لمنصة سهول

Tests that validate the docker-compose-core.yml service definitions,
Kong gateway configuration, and environment variable requirements.

These tests run without Docker and verify configuration correctness
by parsing YAML files and .env templates.

Author: SAHOOL Platform Team
"""

from __future__ import annotations

from pathlib import Path

import pytest

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = PROJECT_ROOT / "docker-compose-core.yml"
KONG_CONFIG_FILE = PROJECT_ROOT / "infrastructure" / "gateway" / "kong" / "kong-core.yml"
ENV_FILE = PROJECT_ROOT / ".env"
ENV_EXAMPLE_FILE = PROJECT_ROOT / ".env.example"

# Core services that must be defined in docker-compose-core.yml
CORE_SERVICES = [
    "postgres",
    "pgbouncer",
    "redis",
    "nats",
    "kong",
    "user-service",
    "field-management-service",
    "weather-service",
    "vegetation-analysis-service",
    "admin",
]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

# Override autouse fixtures from conftest.py that require psycopg2
# These config-validation tests don't need a database connection

@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Override conftest's cleanup_test_data that requires db_cursor."""
    yield


@pytest.fixture(scope="session")
def db_connection():
    """Override conftest's db_connection - not needed for config tests."""
    yield None


@pytest.fixture(scope="session")
def db_cursor():
    """Override conftest's db_cursor - not needed for config tests."""
    yield None


def _skip_if_no_yaml():
    if not HAS_YAML:
        pytest.skip("PyYAML not installed")


@pytest.fixture(scope="module")
def compose_data() -> dict:
    """Load and parse docker-compose-core.yml."""
    _skip_if_no_yaml()
    if not COMPOSE_FILE.exists():
        pytest.skip(f"Compose file not found: {COMPOSE_FILE}")
    with open(COMPOSE_FILE) as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def kong_config() -> dict:
    """Load and parse kong-core.yml."""
    _skip_if_no_yaml()
    if not KONG_CONFIG_FILE.exists():
        pytest.skip(f"Kong config not found: {KONG_CONFIG_FILE}")
    with open(KONG_CONFIG_FILE) as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def env_vars() -> dict[str, str]:
    """Load environment variables from .env file (if present)."""
    env = {}
    # Try .env first, then .env.example
    env_path = ENV_FILE if ENV_FILE.exists() else ENV_EXAMPLE_FILE
    if not env_path.exists():
        return env
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip().strip("'\"")
    return env


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Environment Variable Validation
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
def test_env_file_exists():
    """Verify .env file (or .env.example) exists with required variables."""
    has_env = ENV_FILE.exists() or ENV_EXAMPLE_FILE.exists()
    assert has_env, (
        f"Neither {ENV_FILE} nor {ENV_EXAMPLE_FILE} found. "
        "Copy .env.example to .env and configure."
    )


@pytest.mark.integration
def test_sentinel_hub_configured(env_vars: dict[str, str]):
    """Verify SENTINEL_HUB_CLIENT_ID is present and non-empty."""
    if not env_vars:
        pytest.skip("No .env file available")
    key = "SENTINEL_HUB_CLIENT_ID"
    # In CI or dev, the value may be empty but must be defined
    assert key in env_vars, f"{key} not defined in .env file"


@pytest.mark.integration
def test_openweather_configured(env_vars: dict[str, str]):
    """Verify OPENWEATHER_API_KEY is present in env file."""
    if not env_vars:
        pytest.skip("No .env file available")
    # The compose file uses both OPENWEATHERMAP_API_KEY and OPENWEATHER_API_KEY
    has_key = (
        "OPENWEATHER_API_KEY" in env_vars
        or "OPENWEATHERMAP_API_KEY" in env_vars
    )
    assert has_key, (
        "Neither OPENWEATHER_API_KEY nor OPENWEATHERMAP_API_KEY defined in .env file"
    )


@pytest.mark.integration
def test_jwt_secret_configured(env_vars: dict[str, str]):
    """Verify JWT_SECRET_KEY meets minimum 32 character length."""
    if not env_vars:
        pytest.skip("No .env file available")
    key = "JWT_SECRET_KEY"
    value = env_vars.get(key, "")
    if not value:
        pytest.skip(f"{key} not set in .env")
    assert len(value) >= 32, (
        f"{key} must be at least 32 characters (got {len(value)})"
    )


@pytest.mark.integration
def test_postgres_password_set(env_vars: dict[str, str]):
    """Verify POSTGRES_PASSWORD is set and not a common default."""
    if not env_vars:
        pytest.skip("No .env file available")
    key = "POSTGRES_PASSWORD"
    value = env_vars.get(key, "")
    if not value:
        pytest.skip(f"{key} not set in .env")
    insecure_defaults = {"password", "postgres", "sahool", "changeme", "123456", "admin"}
    assert value.lower() not in insecure_defaults, (
        f"{key} is set to an insecure default value"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Docker Compose Configuration
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
def test_compose_file_valid_yaml():
    """Verify docker-compose-core.yml is valid YAML."""
    _skip_if_no_yaml()
    assert COMPOSE_FILE.exists(), f"Compose file not found: {COMPOSE_FILE}"
    with open(COMPOSE_FILE) as f:
        data = yaml.safe_load(f)
    assert isinstance(data, dict), "Compose file root should be a mapping"
    assert "services" in data, "Compose file missing 'services' key"


@pytest.mark.integration
def test_all_core_services_defined(compose_data: dict):
    """Verify all core services are defined in docker-compose-core.yml."""
    services = compose_data.get("services", {})
    for svc in CORE_SERVICES:
        assert svc in services, (
            f"Core service '{svc}' is not defined in docker-compose-core.yml"
        )


@pytest.mark.integration
def test_service_network_connectivity(compose_data: dict):
    """Verify all core services are attached to sahool-network."""
    services = compose_data.get("services", {})
    for svc_name in CORE_SERVICES:
        svc = services.get(svc_name, {})
        networks = svc.get("networks", [])
        # Networks can be a list of strings or a dict
        if isinstance(networks, list):
            net_names = networks
        elif isinstance(networks, dict):
            net_names = list(networks.keys())
        else:
            net_names = []
        assert "sahool-network" in net_names, (
            f"Service '{svc_name}' is not on sahool-network (found: {net_names})"
        )


@pytest.mark.integration
def test_service_healthchecks_defined(compose_data: dict):
    """Verify all core services have healthcheck configuration."""
    services = compose_data.get("services", {})
    for svc_name in CORE_SERVICES:
        svc = services.get(svc_name, {})
        assert "healthcheck" in svc, (
            f"Service '{svc_name}' is missing a healthcheck definition"
        )
        hc = svc["healthcheck"]
        assert "test" in hc, f"Service '{svc_name}' healthcheck missing 'test' command"
        assert "interval" in hc, f"Service '{svc_name}' healthcheck missing 'interval'"
        assert "retries" in hc, f"Service '{svc_name}' healthcheck missing 'retries'"


@pytest.mark.integration
def test_admin_service_defined(compose_data: dict):
    """Verify admin service exists with correct port mapping."""
    services = compose_data.get("services", {})
    assert "admin" in services, "admin service not defined"
    admin = services["admin"]

    # Check port mapping includes 3002
    ports = admin.get("ports", [])
    port_strs = [str(p) for p in ports]
    has_3002 = any("3002" in p for p in port_strs)
    assert has_3002, f"admin service should expose port 3002 (found: {port_strs})"


@pytest.mark.integration
def test_weather_service_has_redis(compose_data: dict):
    """Verify weather-service has REDIS_URL environment variable."""
    services = compose_data.get("services", {})
    weather = services.get("weather-service", {})
    env_list = weather.get("environment", [])
    env_str = " ".join(str(e) for e in env_list)
    assert "REDIS_URL" in env_str, (
        "weather-service is missing REDIS_URL environment variable"
    )


@pytest.mark.integration
def test_user_service_has_nats(compose_data: dict):
    """Verify user-service has NATS_URL environment variable."""
    services = compose_data.get("services", {})
    user_svc = services.get("user-service", {})
    env_list = user_svc.get("environment", [])
    env_str = " ".join(str(e) for e in env_list)
    assert "NATS_URL" in env_str, (
        "user-service is missing NATS_URL environment variable"
    )


@pytest.mark.integration
def test_vegetation_service_has_sentinel_creds(compose_data: dict):
    """Verify vegetation-analysis-service has SENTINEL_HUB_CLIENT_ID env var."""
    services = compose_data.get("services", {})
    veg_svc = services.get("vegetation-analysis-service", {})
    env_list = veg_svc.get("environment", [])
    env_str = " ".join(str(e) for e in env_list)
    assert "SENTINEL_HUB_CLIENT_ID" in env_str, (
        "vegetation-analysis-service is missing SENTINEL_HUB_CLIENT_ID environment variable"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Kong Configuration
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
def test_kong_config_valid_yaml():
    """Verify kong-core.yml is valid YAML with expected structure."""
    _skip_if_no_yaml()
    assert KONG_CONFIG_FILE.exists(), f"Kong config not found: {KONG_CONFIG_FILE}"
    with open(KONG_CONFIG_FILE) as f:
        data = yaml.safe_load(f)
    assert isinstance(data, dict), "Kong config root should be a mapping"
    assert "services" in data, "Kong config missing 'services' key"
    assert "_format_version" in data, "Kong config missing '_format_version'"


@pytest.mark.integration
def test_field_management_route_no_strip(kong_config: dict):
    """Verify field-management strip_path is false (paths are forwarded as-is)."""
    services = kong_config.get("services", [])
    fm_service = None
    for svc in services:
        if svc.get("name") == "field-management-service":
            fm_service = svc
            break
    assert fm_service is not None, (
        "field-management-service not found in Kong config"
    )

    routes = fm_service.get("routes", [])
    assert len(routes) > 0, "field-management-service has no routes"
    for route in routes:
        assert route.get("strip_path") is False, (
            f"field-management-service route '{route.get('name')}' "
            f"should have strip_path: false (got: {route.get('strip_path')})"
        )


@pytest.mark.integration
def test_weather_route_has_path_prefix(kong_config: dict):
    """Verify weather-service Kong service has /weather path prefix."""
    services = kong_config.get("services", [])
    weather_svc = None
    for svc in services:
        if svc.get("name") == "weather-service":
            weather_svc = svc
            break
    assert weather_svc is not None, "weather-service not found in Kong config"

    # The weather-service has a 'path' key set to /weather
    svc_path = weather_svc.get("path", "")
    assert "/weather" in svc_path, (
        f"weather-service should have path '/weather' (got: '{svc_path}')"
    )


@pytest.mark.integration
def test_user_service_public_routes(kong_config: dict):
    """Verify auth routes (login, register, refresh) are on the public service (no JWT plugin)."""
    services = kong_config.get("services", [])
    public_svc = None
    for svc in services:
        if svc.get("name") == "user-service-public":
            public_svc = svc
            break
    assert public_svc is not None, (
        "user-service-public not found in Kong config"
    )

    routes = public_svc.get("routes", [])
    assert len(routes) > 0, "user-service-public has no routes defined"

    # Collect all paths from routes
    all_paths = []
    for route in routes:
        all_paths.extend(route.get("paths", []))

    expected_public_paths = [
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/auth/refresh",
    ]
    for path in expected_public_paths:
        assert path in all_paths, (
            f"Public auth path '{path}' not found in user-service-public routes "
            f"(found: {all_paths})"
        )

    # Verify no JWT plugin on this service
    plugins = public_svc.get("plugins", [])
    plugin_names = [p.get("name") for p in plugins]
    assert "jwt" not in plugin_names, (
        "user-service-public should NOT have a JWT plugin "
        "(auth routes must be accessible without a token)"
    )


@pytest.mark.integration
def test_all_services_have_kong_routes(kong_config: dict):
    """Verify core backend services have Kong route definitions."""
    services = kong_config.get("services", [])
    service_names = [svc.get("name", "") for svc in services]

    # These core services must have routes in Kong
    expected_services = [
        "field-management-service",
        "weather-service",
        "vegetation-analysis-service",
    ]

    # user-service may appear as user-service-public and/or user-service
    user_svc_found = any(
        name.startswith("user-service") for name in service_names
    )
    assert user_svc_found, (
        "No user-service route found in Kong config "
        f"(service names: {service_names})"
    )

    for expected in expected_services:
        assert expected in service_names, (
            f"Service '{expected}' not found in Kong config "
            f"(defined services: {service_names})"
        )

    # Verify each expected service has at least one route with paths
    for svc in services:
        if svc.get("name") in expected_services:
            routes = svc.get("routes", [])
            assert len(routes) > 0, (
                f"Service '{svc['name']}' has no routes in Kong config"
            )
            for route in routes:
                paths = route.get("paths", [])
                assert len(paths) > 0, (
                    f"Route '{route.get('name')}' for service "
                    f"'{svc['name']}' has no paths defined"
                )
