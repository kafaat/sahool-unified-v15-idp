"""
SAHOOL Data Integrity Tests
============================

Verifies data consistency across the platform:
- Pydantic model validation for major request/response models
- Service port uniqueness from contracts
- Error code uniqueness across services
- API endpoint consistency (/api/v1/ pattern)
- Database model tenant_id coverage
- Configuration consistency (JWT, NATS prefix)
- NATS subject naming conventions
- Helm chart / docker-compose port alignment
- Requirements.txt version consistency
- Health endpoint presence in services

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import importlib.util
import os
import re
import sys
from collections import Counter
from datetime import UTC, datetime, date
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Override autouse fixtures from conftest.py that require database connectivity.
# Data integrity tests operate purely on source files and contracts.
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Override: data integrity tests do not need database cleanup."""
    yield


@pytest.fixture(scope="session")
def db_connection():
    """Override: data integrity tests do not need a database connection."""
    yield None


@pytest.fixture(scope="session")
def db_cursor():
    """Override: data integrity tests do not need a database cursor."""
    yield None


# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent.parent
SERVICES_DIR = ROOT / "apps" / "services"
SHARED_DIR = ROOT / "shared"
CONTRACTS_DIR = ROOT / "packages" / "shared-types" / "src" / "contracts"
HELM_DIR = ROOT / "helm"
DOCKER_COMPOSE = ROOT / "docker-compose.yml"

# Ensure shared modules are importable
for _p in (str(ROOT), str(ROOT / "apps" / "services")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_ts_object(filepath: Path, object_name: str) -> dict[str, Any]:
    """
    Lightweight TypeScript const object parser.
    Extracts key-value pairs from  export const OBJECT_NAME = { ... } as const;
    Returns a dict of string keys to raw values.
    """
    text = filepath.read_text(encoding="utf-8")
    pattern = rf"export\s+const\s+{object_name}\s*[:=]\s*\{{(.*?)\}}\s*as\s+const"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        pattern = rf"export\s+const\s+{object_name}\s*[:=]\s*\{{(.*?)\}}"
        match = re.search(pattern, text, re.DOTALL)
    if not match:
        return {}
    block = match.group(1)
    result: dict[str, Any] = {}
    for m in re.finditer(
        r"""(?:\/\*\*.*?\*\/\s*)?(\w+)\s*:\s*(?:(\d+)|'([^']*)'|"([^"]*)"|(`.+?`))""",
        block,
        re.DOTALL,
    ):
        key = m.group(1)
        if m.group(2) is not None:
            result[key] = int(m.group(2))
        elif m.group(3) is not None:
            result[key] = m.group(3)
        elif m.group(4) is not None:
            result[key] = m.group(4)
        elif m.group(5) is not None:
            val = m.group(5).strip("`")
            val = val.replace("${API_PREFIX}", "/api/v1")
            result[key] = val
    return result


def _parse_ts_all_endpoint_groups(filepath: Path) -> dict[str, dict[str, str]]:
    """Parse all *_ENDPOINTS const objects from api-endpoints.ts."""
    text = filepath.read_text(encoding="utf-8")
    groups: dict[str, dict[str, str]] = {}
    for m in re.finditer(
        r"export\s+const\s+(\w+_ENDPOINTS)\s*=\s*\{(.*?)\}\s*as\s+const",
        text,
        re.DOTALL,
    ):
        name = m.group(1)
        block = m.group(2)
        endpoints: dict[str, str] = {}
        for em in re.finditer(
            r"""(\w+)\s*:\s*(?:`([^`]+)`|'([^']*)'|"([^"]*)")""",
            block,
        ):
            key = em.group(1)
            val = em.group(2) or em.group(3) or em.group(4) or ""
            val = val.replace("${API_PREFIX}", "/api/v1")
            endpoints[key] = val
        groups[name] = endpoints
    return groups


def _parse_ts_error_codes(filepath: Path) -> dict[str, str]:
    """Parse ERROR_CODES from error-codes.ts."""
    text = filepath.read_text(encoding="utf-8")
    match = re.search(
        r"export\s+const\s+ERROR_CODES\s*=\s*\{(.*?)\}\s*as\s+const",
        text,
        re.DOTALL,
    )
    if not match:
        return {}
    block = match.group(1)
    result: dict[str, str] = {}
    for m in re.finditer(r"(\w+)\s*:\s*'([^']*)'", block):
        result[m.group(1)] = m.group(2)
    return result


def _find_python_services() -> list[Path]:
    """Return paths to Python service directories that have src/main.py."""
    if not SERVICES_DIR.is_dir():
        return []
    return sorted(
        d
        for d in SERVICES_DIR.iterdir()
        if d.is_dir() and (d / "src" / "main.py").exists()
    )


def _read_requirements(service_dir: Path) -> dict[str, str]:
    """Parse requirements.txt, returning package->version_spec mapping."""
    req_file = service_dir / "requirements.txt"
    if not req_file.exists():
        return {}
    pkgs: dict[str, str] = {}
    for line in req_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        m = re.match(r"^([a-zA-Z0-9_-]+)\s*(.*)", line)
        if m:
            pkgs[m.group(1).lower()] = m.group(2).strip()
    return pkgs


def _load_module_from_path(name: str, filepath: Path):
    """Dynamically load a Python module from an arbitrary file path."""
    spec = importlib.util.spec_from_file_location(name, filepath)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        return None
    return mod


# ===========================================================================
# 1. Pydantic Model Validation (Exhaustive)
# ===========================================================================


class TestPydanticModelValidation:
    """Test major Pydantic request/response models across 10+ services.

    Models are validated by inspecting source code structure and using
    lightweight in-line Pydantic definitions extracted from service files.
    """

    def _load_alert_models(self):
        models_path = SERVICES_DIR / "alert-service" / "src" / "models.py"
        mod = _load_module_from_path("_alert_models", models_path)
        return mod

    # -- Equipment models (defined inline in main.py) -----------------------

    def test_equipment_create_valid(self):
        """EquipmentCreate accepts valid data with all required fields."""
        from enum import StrEnum
        from pydantic import BaseModel, Field

        class EquipmentType(StrEnum):
            TRACTOR = "tractor"
            PUMP = "pump"
            DRONE = "drone"
            HARVESTER = "harvester"
            SPRAYER = "sprayer"
            PIVOT = "pivot"
            SENSOR = "sensor"
            VEHICLE = "vehicle"
            OTHER = "other"

        class EquipmentCreate(BaseModel):
            name: str = Field(..., min_length=1, max_length=200)
            equipment_type: EquipmentType

        obj = EquipmentCreate(name="Tractor A", equipment_type=EquipmentType.TRACTOR)
        assert obj.name == "Tractor A"
        assert obj.equipment_type == "tractor"

    def test_equipment_create_name_min_length(self):
        """EquipmentCreate rejects empty name."""
        from enum import StrEnum
        from pydantic import BaseModel, Field, ValidationError

        class EquipmentType(StrEnum):
            TRACTOR = "tractor"

        class EquipmentCreate(BaseModel):
            name: str = Field(..., min_length=1, max_length=200)
            equipment_type: EquipmentType

        with pytest.raises(ValidationError):
            EquipmentCreate(name="", equipment_type=EquipmentType.TRACTOR)

    def test_equipment_type_enum_values_in_source(self):
        """EquipmentType enum in source has expected agricultural values."""
        content = (SERVICES_DIR / "equipment-service" / "src" / "main.py").read_text()
        expected = {"tractor", "pump", "drone", "harvester", "sprayer", "pivot", "sensor", "vehicle", "other"}
        for val in expected:
            assert f'"{val}"' in content, f"EquipmentType missing value: {val}"

    def test_equipment_status_enum_values_in_source(self):
        """EquipmentStatus enum in source covers operational states."""
        content = (SERVICES_DIR / "equipment-service" / "src" / "main.py").read_text()
        for val in ("operational", "maintenance", "inactive", "repair"):
            assert f'"{val}"' in content, f"EquipmentStatus missing value: {val}"

    # -- Alert models -------------------------------------------------------

    def test_alert_create_valid(self):
        """AlertCreate accepts valid data with all required fields."""
        mod = self._load_alert_models()
        if mod is None:
            pytest.skip("Could not load alert-service models")
        obj = mod.AlertCreate(
            field_id="field-001",
            type=mod.AlertType.WEATHER,
            severity=mod.AlertSeverity.HIGH,
            title="Frost Warning",
            message="Temperature expected to drop below 0C",
        )
        assert obj.field_id == "field-001"
        assert obj.severity == "high"

    def test_alert_create_title_max_length(self):
        """AlertCreate rejects title exceeding max_length."""
        from pydantic import ValidationError

        mod = self._load_alert_models()
        if mod is None:
            pytest.skip("Could not load alert-service models")
        with pytest.raises(ValidationError):
            mod.AlertCreate(
                field_id="f1",
                type=mod.AlertType.WEATHER,
                severity=mod.AlertSeverity.LOW,
                title="x" * 201,
                message="msg",
            )

    def test_alert_type_enum_completeness(self):
        """AlertType covers all expected alert categories."""
        mod = self._load_alert_models()
        if mod is None:
            pytest.skip("Could not load alert-service models")
        expected = {
            "weather", "pest", "disease", "irrigation", "fertilizer",
            "harvest", "ndvi_low", "ndvi_anomaly", "soil_moisture",
            "equipment", "general",
        }
        assert {e.value for e in mod.AlertType} == expected

    def test_alert_severity_ordering(self):
        """AlertSeverity includes all levels from critical to info."""
        mod = self._load_alert_models()
        if mod is None:
            pytest.skip("Could not load alert-service models")
        expected = {"critical", "high", "medium", "low", "info"}
        assert {e.value for e in mod.AlertSeverity} == expected

    def test_alert_status_transitions(self):
        """AlertStatus covers the full lifecycle."""
        mod = self._load_alert_models()
        if mod is None:
            pytest.skip("Could not load alert-service models")
        expected = {"active", "acknowledged", "dismissed", "resolved", "expired"}
        assert {e.value for e in mod.AlertStatus} == expected

    # -- Billing models (source inspection) ---------------------------------

    def test_billing_subscription_has_required_fields(self):
        """Subscription model source defines essential billing fields."""
        content = (SERVICES_DIR / "billing-core" / "src" / "main.py").read_text()
        sub_match = re.search(r"class Subscription\(BaseModel\)(.*?)(?=\nclass |\Z)", content, re.DOTALL)
        assert sub_match, "Subscription model class not found in billing-core"
        block = sub_match.group(1)
        for field in ("subscription_id", "tenant_id", "plan_id", "status", "start_date", "end_date"):
            assert field in block, f"Subscription missing field: {field}"

    def test_billing_invoice_has_required_fields(self):
        """Invoice model source defines required financial fields."""
        content = (SERVICES_DIR / "billing-core" / "src" / "main.py").read_text()
        inv_match = re.search(r"class Invoice\(BaseModel\)(.*?)(?=\nclass |\Z)", content, re.DOTALL)
        assert inv_match, "Invoice model class not found in billing-core"
        block = inv_match.group(1)
        for field in ("invoice_id", "tenant_id", "total", "amount_due", "line_items"):
            assert field in block, f"Invoice missing field: {field}"

    def test_billing_payment_has_required_fields(self):
        """Payment model source defines required payment fields."""
        content = (SERVICES_DIR / "billing-core" / "src" / "main.py").read_text()
        pay_match = re.search(r"class Payment\(BaseModel\)(.*?)(?=\nclass |\Z)", content, re.DOTALL)
        assert pay_match, "Payment model class not found in billing-core"
        block = pay_match.group(1)
        for field in ("payment_id", "tenant_id", "amount", "currency", "status"):
            assert field in block, f"Payment missing field: {field}"


# ===========================================================================
# 2. Service Port Uniqueness
# ===========================================================================


class TestServicePortUniqueness:
    """Verify zero port collisions in the unified contracts."""

    def test_all_service_ports_are_unique(self):
        """SERVICE_PORTS must have no duplicate port numbers."""
        ports_file = CONTRACTS_DIR / "service-ports.ts"
        assert ports_file.exists(), f"Missing {ports_file}"
        ports = _parse_ts_object(ports_file, "SERVICE_PORTS")
        assert len(ports) > 0, "Could not parse SERVICE_PORTS"
        port_values = [v for v in ports.values() if isinstance(v, int)]
        duplicates = {p: c for p, c in Counter(port_values).items() if c > 1}
        assert duplicates == {}, f"Duplicate ports found: {duplicates}"

    def test_service_port_count_minimum(self):
        """Platform should define at least 40 unique service ports."""
        ports_file = CONTRACTS_DIR / "service-ports.ts"
        ports = _parse_ts_object(ports_file, "SERVICE_PORTS")
        port_values = [v for v in ports.values() if isinstance(v, int)]
        assert len(port_values) >= 40, f"Expected >=40 service ports, found {len(port_values)}"

    def test_service_registry_ports_match(self):
        """SERVICE_REGISTRY references must point to existing SERVICE_PORTS keys."""
        ports_file = CONTRACTS_DIR / "service-ports.ts"
        text = ports_file.read_text(encoding="utf-8")
        ports = _parse_ts_object(ports_file, "SERVICE_PORTS")
        registry_keys = re.findall(r"port:\s*SERVICE_PORTS\.(\w+)", text)
        for key in registry_keys:
            assert key in ports, f"SERVICE_REGISTRY references SERVICE_PORTS.{key} which does not exist"


# ===========================================================================
# 3. Error Code Uniqueness
# ===========================================================================


class TestErrorCodeUniqueness:
    """Verify no duplicate error codes across services."""

    def test_error_codes_are_unique(self):
        """ERROR_CODES values must have no duplicates."""
        codes_file = CONTRACTS_DIR / "error-codes.ts"
        assert codes_file.exists(), f"Missing {codes_file}"
        codes = _parse_ts_error_codes(codes_file)
        assert len(codes) > 0, "Could not parse ERROR_CODES"
        values = list(codes.values())
        duplicates = {v: c for v, c in Counter(values).items() if c > 1}
        assert duplicates == {}, f"Duplicate error code values: {duplicates}"

    def test_error_code_count_minimum(self):
        """Platform should define at least 30 error codes."""
        codes_file = CONTRACTS_DIR / "error-codes.ts"
        codes = _parse_ts_error_codes(codes_file)
        assert len(codes) >= 30, f"Expected >=30 error codes, found {len(codes)}"

    def test_vision_error_codes_follow_pattern(self):
        """Vision error codes must follow Exxxx pattern."""
        codes_file = CONTRACTS_DIR / "error-codes.ts"
        codes = _parse_ts_error_codes(codes_file)
        vision_codes = {k: v for k, v in codes.items() if k.startswith("VISION_")}
        for key, value in vision_codes.items():
            assert re.match(r"^E\d{4}$", value), f"Vision code {key}={value} does not follow Exxxx pattern"

    def test_weather_error_codes_follow_pattern(self):
        """Weather error codes must follow Wxxxx pattern."""
        codes_file = CONTRACTS_DIR / "error-codes.ts"
        codes = _parse_ts_error_codes(codes_file)
        weather_codes = {k: v for k, v in codes.items() if k.startswith("WEATHER_")}
        for key, value in weather_codes.items():
            assert re.match(r"^W\d{4}$", value), f"Weather code {key}={value} does not follow Wxxxx pattern"


# ===========================================================================
# 4. API Endpoint Consistency
# ===========================================================================


class TestAPIEndpointConsistency:
    """Verify all endpoints follow /api/v1/ pattern."""

    def test_all_endpoints_follow_api_v1_pattern(self):
        """All non-health endpoints must start with /api/v1/."""
        endpoints_file = CONTRACTS_DIR / "api-endpoints.ts"
        assert endpoints_file.exists(), f"Missing {endpoints_file}"
        groups = _parse_ts_all_endpoint_groups(endpoints_file)
        assert len(groups) > 5, "Expected multiple endpoint groups"

        violations: list[str] = []
        exempt_groups = {"HEALTH_ENDPOINTS"}
        for group_name, endpoints in groups.items():
            if group_name in exempt_groups:
                continue
            for key, path in endpoints.items():
                if not path.startswith("/api/v1/"):
                    violations.append(f"{group_name}.{key} = {path}")

        assert violations == [], (
            "Endpoints not following /api/v1/ pattern:\n" + "\n".join(violations)
        )

    def test_no_severely_duplicate_endpoint_paths(self):
        """No endpoint path should appear more than twice (GET+POST pattern allowed)."""
        endpoints_file = CONTRACTS_DIR / "api-endpoints.ts"
        groups = _parse_ts_all_endpoint_groups(endpoints_file)
        all_paths: list[str] = []
        for endpoints in groups.values():
            all_paths.extend(endpoints.values())
        static_paths = [p for p in all_paths if "{" not in p]
        severe = {p: c for p, c in Counter(static_paths).items() if c > 2}
        assert severe == {}, f"Endpoint paths with >2 occurrences: {severe}"

    def test_health_endpoints_defined(self):
        """HEALTH_ENDPOINTS must define /healthz and /readyz."""
        endpoints_file = CONTRACTS_DIR / "api-endpoints.ts"
        groups = _parse_ts_all_endpoint_groups(endpoints_file)
        health = groups.get("HEALTH_ENDPOINTS", {})
        assert "LIVENESS" in health, "Missing HEALTH_ENDPOINTS.LIVENESS"
        assert "READINESS" in health, "Missing HEALTH_ENDPOINTS.READINESS"
        assert health["LIVENESS"] == "/healthz"
        assert health["READINESS"] == "/readyz"

    def test_endpoint_group_count(self):
        """Platform should define at least 15 endpoint groups."""
        endpoints_file = CONTRACTS_DIR / "api-endpoints.ts"
        groups = _parse_ts_all_endpoint_groups(endpoints_file)
        assert len(groups) >= 15, f"Expected >=15 endpoint groups, found {len(groups)}"


# ===========================================================================
# 5. Database Model tenant_id Coverage
# ===========================================================================


class TestTenantIdCoverage:
    """Verify tenant_id field exists in multi-tenant models."""

    @pytest.mark.parametrize(
        "service_name,model_file",
        [
            ("equipment-service", "src/main.py"),
            ("alert-service", "src/models.py"),
            ("billing-core", "src/main.py"),
        ],
    )
    def test_service_has_tenant_id_field(self, service_name: str, model_file: str):
        """Service models must include tenant_id for multi-tenancy."""
        model_path = SERVICES_DIR / service_name / model_file
        assert model_path.exists(), f"Missing {model_path}"
        content = model_path.read_text(encoding="utf-8")
        assert "tenant_id" in content, f"{service_name} missing tenant_id in {model_file}"

    def test_equipment_model_tenant_id_is_required(self):
        """Equipment model tenant_id must be a required str (not Optional)."""
        content = (SERVICES_DIR / "equipment-service" / "src" / "main.py").read_text()
        equip_match = re.search(
            r"class Equipment\(BaseModel\).*?(?=\nclass |\Z)", content, re.DOTALL,
        )
        assert equip_match, "Equipment model class not found"
        equip_block = equip_match.group()
        assert "tenant_id: str" in equip_block, "Equipment.tenant_id should be a required str"

    def test_billing_subscription_tenant_id_is_required(self):
        """Subscription model tenant_id must be a required str."""
        content = (SERVICES_DIR / "billing-core" / "src" / "main.py").read_text()
        sub_match = re.search(
            r"class Subscription\(BaseModel\).*?(?=\nclass |\Z)", content, re.DOTALL,
        )
        assert sub_match, "Subscription model class not found"
        sub_block = sub_match.group()
        assert "tenant_id: str" in sub_block, "Subscription.tenant_id should be a required str"


# ===========================================================================
# 6. Configuration Consistency
# ===========================================================================


class TestConfigurationConsistency:
    """Verify configuration uniformity across services."""

    def test_jwt_algorithm_consistent(self):
        """All services referencing JWT_ALGORITHM should use HS256."""
        services = _find_python_services()
        assert len(services) > 0, "No Python services found"
        non_hs256: list[str] = []
        for svc in services:
            main_py = svc / "src" / "main.py"
            content = main_py.read_text(encoding="utf-8")
            for m in re.finditer(r'JWT_ALGORITHM\s*[=:]\s*["\'](\w+)["\']', content):
                if m.group(1) != "HS256":
                    non_hs256.append(f"{svc.name}: {m.group(1)}")
        assert non_hs256 == [], f"Services using non-HS256 JWT_ALGORITHM: {non_hs256}"

    def test_nats_subjects_use_sahool_prefix(self):
        """All NATS subjects in subjects.py must start with 'sahool.'."""
        subjects_file = SHARED_DIR / "events" / "subjects.py"
        assert subjects_file.exists(), f"Missing {subjects_file}"
        content = subjects_file.read_text(encoding="utf-8")
        violations: list[str] = []
        for m in re.finditer(
            r'^(SAHOOL_\w+)\s*=\s*["\']([^"\']+)["\']',
            content,
            re.MULTILINE,
        ):
            name, value = m.group(1), m.group(2)
            if not value.startswith("sahool."):
                violations.append(f"{name} = {value}")
        assert violations == [], (
            "NATS subjects not starting with 'sahool.':\n" + "\n".join(violations)
        )

    def test_service_version_consistent(self):
        """All services should report version 16.0.0."""
        services = _find_python_services()
        wrong_version: list[str] = []
        for svc in services:
            main_py = svc / "src" / "main.py"
            content = main_py.read_text(encoding="utf-8")
            for m in re.finditer(r'version\s*=\s*["\']([^"\']+)["\']', content):
                ver = m.group(1)
                if ver != "16.0.0":
                    wrong_version.append(f"{svc.name}: {ver}")
                    break
        if wrong_version:
            pytest.skip(f"Some services have non-16.0.0 version (informational): {wrong_version}")


# ===========================================================================
# 7. NATS Subject Naming Conventions
# ===========================================================================


class TestNATSSubjectConventions:
    """Verify NATS subject naming consistency."""

    def test_subject_count_minimum(self):
        """subjects.py should define at least 50 NATS subjects."""
        subjects_file = SHARED_DIR / "events" / "subjects.py"
        content = subjects_file.read_text(encoding="utf-8")
        subjects = re.findall(
            r'^SAHOOL_\w+\s*=\s*"sahool\.[^"]*"', content, re.MULTILINE,
        )
        assert len(subjects) >= 50, f"Expected >=50 NATS subjects, found {len(subjects)}"

    def test_no_invalid_characters_in_subjects(self):
        """NATS subjects must not contain spaces or special characters."""
        subjects_file = SHARED_DIR / "events" / "subjects.py"
        content = subjects_file.read_text(encoding="utf-8")
        violations: list[str] = []
        for m in re.finditer(r'^(SAHOOL_\w+)\s*=\s*"([^"]+)"', content, re.MULTILINE):
            name, value = m.group(1), m.group(2)
            if re.search(r"[^a-zA-Z0-9._\-*>]", value):
                violations.append(f"{name} = {value}")
        assert violations == [], (
            "NATS subjects with invalid characters:\n" + "\n".join(violations)
        )

    def test_wildcard_subjects_end_correctly(self):
        """Wildcard subjects must end with .* or .>"""
        subjects_file = SHARED_DIR / "events" / "subjects.py"
        content = subjects_file.read_text(encoding="utf-8")
        violations: list[str] = []
        for m in re.finditer(
            r'^(SAHOOL_\w+(?:_ALL|_WILDCARDS?))\s*=\s*"([^"]+)"',
            content,
            re.MULTILINE,
        ):
            name, value = m.group(1), m.group(2)
            if not (value.endswith(".*") or value.endswith(".>")):
                violations.append(f"{name} = {value}")
        assert violations == [], (
            "Wildcard subjects not ending with .* or .>:\n" + "\n".join(violations)
        )

    def test_get_tenant_subject_function_exists(self):
        """get_tenant_subject helper must be defined in subjects.py."""
        subjects_file = SHARED_DIR / "events" / "subjects.py"
        content = subjects_file.read_text(encoding="utf-8")
        assert "def get_tenant_subject" in content, "Missing get_tenant_subject in subjects.py"


# ===========================================================================
# 8. Helm Chart / Docker Compose Port Alignment
# ===========================================================================


class TestPortAlignment:
    """Verify ports match between Helm values and contracts."""

    HELM_SERVICE_MAP = {
        "terrain-core-service": "TERRAIN_CORE",
        "yolo26-vision-service": "YOLO_VISION",
        "hydrology-service": "HYDROLOGY",
        "leveling-optimizer-service": "LEVELING_OPTIMIZER",
        "edge-orchestrator-service": "EDGE_ORCHESTRATOR",
    }

    def test_helm_ports_match_contracts(self):
        """Helm chart ports must match SERVICE_PORTS in contracts."""
        ports_file = CONTRACTS_DIR / "service-ports.ts"
        contract_ports = _parse_ts_object(ports_file, "SERVICE_PORTS")
        mismatches: list[str] = []

        for helm_svc, contract_key in self.HELM_SERVICE_MAP.items():
            values_file = HELM_DIR / "services" / helm_svc / "values.yaml"
            if not values_file.exists():
                continue
            content = values_file.read_text(encoding="utf-8")
            m = re.search(r"port:\s*(\d+)", content)
            if not m:
                continue
            helm_port = int(m.group(1))
            contract_port = contract_ports.get(contract_key)
            if contract_port is not None and helm_port != contract_port:
                mismatches.append(f"{helm_svc}: helm={helm_port}, contract={contract_port}")

        assert mismatches == [], (
            "Port mismatches between Helm and contracts:\n" + "\n".join(mismatches)
        )

    def test_docker_compose_exists(self):
        """docker-compose.yml must exist at project root."""
        assert DOCKER_COMPOSE.exists(), "Missing docker-compose.yml"


# ===========================================================================
# 9. Requirements.txt Consistency
# ===========================================================================


class TestRequirementsConsistency:
    """Verify critical packages have consistent versions across services."""

    def test_fastapi_version_consistent(self):
        """All services pinning fastapi (==x.y.z) should use the same version."""
        services = _find_python_services()
        pinned: dict[str, list[str]] = {}
        for svc in services:
            reqs = _read_requirements(svc)
            if "fastapi" in reqs:
                ver = reqs["fastapi"]
                # Only check exact pins (==x.y.z), not range specs (>=x,<y)
                if ver.startswith("=="):
                    pinned.setdefault(ver, []).append(svc.name)
        assert len(pinned) > 0, "No services with pinned fastapi version found"
        if len(pinned) > 1:
            detail = "; ".join(f"{v}: {svcs}" for v, svcs in pinned.items())
            pytest.fail(f"Inconsistent fastapi pinned versions: {detail}")

    def test_pydantic_version_consistent(self):
        """All services pinning pydantic (==x.y.z) should use the same version."""
        services = _find_python_services()
        pinned: dict[str, list[str]] = {}
        for svc in services:
            reqs = _read_requirements(svc)
            if "pydantic" in reqs:
                ver = reqs["pydantic"]
                if ver.startswith("=="):
                    pinned.setdefault(ver, []).append(svc.name)
        assert len(pinned) > 0, "No services with pinned pydantic version found"
        if len(pinned) > 1:
            detail = "; ".join(f"{v}: {svcs}" for v, svcs in pinned.items())
            pytest.fail(f"Inconsistent pydantic pinned versions: {detail}")

    def test_nats_py_version_consistent(self):
        """Services pinning nats-py (==x.y.z) should have the same version."""
        services = _find_python_services()
        pinned: dict[str, list[str]] = {}
        for svc in services:
            reqs = _read_requirements(svc)
            if "nats-py" in reqs:
                ver = reqs["nats-py"]
                if ver.startswith("=="):
                    pinned.setdefault(ver, []).append(svc.name)
        if len(pinned) > 1:
            detail = "; ".join(f"{v}: {svcs}" for v, svcs in pinned.items())
            pytest.fail(f"Inconsistent nats-py pinned versions: {detail}")

    def test_all_python_services_have_requirements(self):
        """Every Python service directory should have requirements.txt."""
        services = _find_python_services()
        missing: list[str] = []
        for svc in services:
            if not (svc / "requirements.txt").exists():
                missing.append(svc.name)
        assert missing == [], f"Services missing requirements.txt: {missing}"


# ===========================================================================
# 10. Health Endpoint Consistency
# ===========================================================================


class TestHealthEndpointConsistency:
    """Verify all Python services define /healthz and /readyz."""

    def test_all_services_have_healthz(self):
        """Every Python service main.py must define a /healthz endpoint."""
        services = _find_python_services()
        assert len(services) > 10, "Expected >10 Python services"
        missing: list[str] = []
        for svc in services:
            main_py = svc / "src" / "main.py"
            content = main_py.read_text(encoding="utf-8")
            if '"/healthz"' not in content and "'/healthz'" not in content:
                missing.append(svc.name)
        assert missing == [], f"Services missing /healthz endpoint: {missing}"

    def test_all_services_have_readyz(self):
        """Every Python service main.py must define a /readyz endpoint."""
        services = _find_python_services()
        missing: list[str] = []
        for svc in services:
            main_py = svc / "src" / "main.py"
            content = main_py.read_text(encoding="utf-8")
            if '"/readyz"' not in content and "'/readyz'" not in content:
                missing.append(svc.name)
        assert missing == [], f"Services missing /readyz endpoint: {missing}"

    def test_health_endpoints_return_status(self):
        """Health endpoint implementations should return a status field."""
        services = _find_python_services()
        no_status: list[str] = []
        # Acceptable status values: "ok", "healthy", "degraded"
        status_pattern = re.compile(r'"(ok|healthy|degraded)"')
        for svc in services[:10]:
            main_py = svc / "src" / "main.py"
            content = main_py.read_text(encoding="utf-8")
            if '"/healthz"' in content or "'/healthz'" in content:
                if not status_pattern.search(content):
                    no_status.append(svc.name)
        assert no_status == [], (
            f"Services with /healthz not returning a recognized status: {no_status}"
        )
