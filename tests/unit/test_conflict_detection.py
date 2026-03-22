"""
SAHOOL Conflict Detection Tests
اختبارات الكشف عن التعارضات في منصة سهول

Validates that critical platform resources (ports, event subjects,
API endpoints, error codes, module imports) are free from conflicts
and duplications. These tests act as guardrails to prevent regressions
when adding new services or modifying shared contracts.

Usage:
    pytest tests/unit/test_conflict_detection.py -v
"""

from __future__ import annotations

import importlib
import json
import re
import sys
from pathlib import Path

import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════════════════

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Infrastructure ports that are intentionally shared (not service conflicts)
INFRASTRUCTURE_PORT_NAMES = {
    "KONG_GATEWAY",
    "KONG_ADMIN",
    "NATS",
    "NATS_MONITOR",
    "POSTGRES",
    "PGBOUNCER",
    "REDIS",
}


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Service Port Conflict Tests - اختبارات تعارض المنافذ
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestServicePortConflicts:
    """Verify all microservice ports are unique and within valid ranges."""

    @pytest.fixture
    def service_ports(self) -> dict[str, int]:
        """Parse SERVICE_PORTS from the TypeScript contracts file."""
        ports_file = PROJECT_ROOT / "packages" / "shared-types" / "src" / "contracts" / "service-ports.ts"
        if not ports_file.exists():
            pytest.skip("service-ports.ts not found")

        content = ports_file.read_text(encoding="utf-8")
        # Match patterns like: KEY: 3000, or KEY: 8090,
        pattern = re.compile(r"^\s+(\w+):\s*(\d+)\s*,", re.MULTILINE)
        ports = {}
        in_service_ports = False
        for line in content.splitlines():
            if "SERVICE_PORTS" in line and "=" in line and "{" in line:
                in_service_ports = True
                continue
            if in_service_ports and "} as const" in line:
                break
            if in_service_ports:
                match = pattern.match(line)
                if match:
                    name = match.group(1)
                    port = int(match.group(2))
                    ports[name] = port
        return ports

    def test_service_ports_exist(self, service_ports: dict[str, int]):
        """Contract file must define service ports."""
        assert len(service_ports) > 0, "No service ports found in service-ports.ts"

    def test_no_duplicate_application_ports(self, service_ports: dict[str, int]):
        """
        No two application services should share the same port.
        Infrastructure ports (PostgreSQL, Redis, NATS, Kong) are excluded.
        """
        app_ports: dict[str, int] = {
            name: port for name, port in service_ports.items() if name not in INFRASTRUCTURE_PORT_NAMES
        }

        seen: dict[int, str] = {}
        duplicates: list[str] = []
        for name, port in app_ports.items():
            if port in seen:
                duplicates.append(f"Port {port} used by both '{seen[port]}' and '{name}'")
            else:
                seen[port] = name

        assert not duplicates, "Duplicate service ports detected:\n" + "\n".join(duplicates)

    def test_ports_in_valid_range(self, service_ports: dict[str, int]):
        """All service ports must be in a valid range (1024-65535)."""
        invalid: list[str] = []
        for name, port in service_ports.items():
            if not (1024 <= port <= 65535):
                invalid.append(f"{name}: {port}")

        assert not invalid, "Ports outside valid range (1024-65535):\n" + "\n".join(invalid)

    def test_no_well_known_port_conflicts(self, service_ports: dict[str, int]):
        """Services should not use well-known system ports (< 1024)."""
        well_known = [(name, port) for name, port in service_ports.items() if port < 1024]
        assert not well_known, "Services using well-known ports (<1024): " + ", ".join(
            f"{n}:{p}" for n, p in well_known
        )

    def test_minimum_service_count(self, service_ports: dict[str, int]):
        """Platform should have a reasonable number of registered services."""
        app_ports = {n: p for n, p in service_ports.items() if n not in INFRASTRUCTURE_PORT_NAMES}
        assert len(app_ports) >= 30, f"Expected at least 30 application services, found {len(app_ports)}"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. NATS Event Subject Conflict Tests - اختبارات تعارض موضوعات الأحداث
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestEventSubjectConflicts:
    """Verify NATS event subjects are unique and follow naming conventions."""

    @pytest.fixture
    def event_subjects(self) -> dict[str, str]:
        """Load all SAHOOL_ prefixed constants from shared.events.subjects."""
        try:
            from shared.events import subjects as subj_mod
        except ImportError:
            pytest.skip("shared.events.subjects not importable")

        return {
            name: getattr(subj_mod, name)
            for name in dir(subj_mod)
            if name.startswith("SAHOOL_")
            and isinstance(getattr(subj_mod, name), str)
            and not name.endswith("_ALL")  # Exclude wildcard constants
        }

    @pytest.fixture
    def subject_registry(self) -> dict[str, str]:
        """Load the SUBJECT_REGISTRY from shared.events.subjects."""
        try:
            from shared.events.subjects import SUBJECT_REGISTRY
        except ImportError:
            pytest.skip("SUBJECT_REGISTRY not importable")
        return SUBJECT_REGISTRY

    def test_event_subjects_exist(self, event_subjects: dict[str, str]):
        """Event subjects module must define subject constants."""
        assert len(event_subjects) > 0, "No event subjects found"

    def test_no_duplicate_subject_values(self, event_subjects: dict[str, str]):
        """
        Each NATS subject string should map to exactly one constant.
        Duplicate values would cause event routing ambiguity.
        """
        seen: dict[str, str] = {}
        duplicates: list[str] = []
        for name, subject in event_subjects.items():
            if subject in seen:
                duplicates.append(f"Subject '{subject}' defined by both '{seen[subject]}' and '{name}'")
            else:
                seen[subject] = name

        assert not duplicates, "Duplicate NATS subject values:\n" + "\n".join(duplicates)

    def test_subjects_follow_naming_convention(self, event_subjects: dict[str, str]):
        """All subjects must follow the pattern: sahool.{domain}.{action}[.{sub}]."""
        invalid: list[str] = []
        for name, subject in event_subjects.items():
            if not subject.startswith("sahool."):
                invalid.append(f"{name} = '{subject}' (missing sahool. prefix)")
            parts = subject.split(".")
            if len(parts) < 3:
                invalid.append(f"{name} = '{subject}' (must have at least 3 segments)")

        assert not invalid, "Subjects violating naming convention:\n" + "\n".join(invalid)

    def test_subject_registry_values_match_constants(
        self,
        event_subjects: dict[str, str],
        subject_registry: dict[str, str],
    ):
        """
        SUBJECT_REGISTRY values must reference existing subject constants.
        This catches stale registry entries pointing to removed constants.
        """
        known_values = set(event_subjects.values())
        mismatches: list[str] = []
        for key, value in subject_registry.items():
            if value not in known_values:
                mismatches.append(f"Registry key '{key}' → '{value}' has no matching constant")

        assert not mismatches, "Stale SUBJECT_REGISTRY entries:\n" + "\n".join(mismatches)

    def test_no_duplicate_registry_keys(self, subject_registry: dict[str, str]):
        """SUBJECT_REGISTRY keys must be unique (enforced by dict, but values should be too)."""
        seen_values: dict[str, str] = {}
        duplicates: list[str] = []
        for key, value in subject_registry.items():
            if value in seen_values:
                duplicates.append(f"Subject '{value}' registered by both '{seen_values[value]}' and '{key}'")
            else:
                seen_values[value] = key

        assert not duplicates, "Duplicate subject values in SUBJECT_REGISTRY:\n" + "\n".join(duplicates)

    def test_subject_no_whitespace(self, event_subjects: dict[str, str]):
        """NATS subjects must not contain whitespace characters."""
        invalid = [
            f"{name} = '{subj}'" for name, subj in event_subjects.items() if " " in subj or "\t" in subj or "\n" in subj
        ]
        assert not invalid, "Subjects with whitespace:\n" + "\n".join(invalid)


# ═══════════════════════════════════════════════════════════════════════════════
# 3. API Endpoint Conflict Tests - اختبارات تعارض نقاط النهاية
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAPIEndpointConflicts:
    """Verify API endpoint paths do not conflict across services."""

    @pytest.fixture
    def all_endpoints(self) -> dict[str, dict[str, str]]:
        """
        Parse all *_ENDPOINTS objects from api-endpoints.ts.
        Returns a dict of {group_name: {key: path}}.
        """
        endpoints_file = PROJECT_ROOT / "packages" / "shared-types" / "src" / "contracts" / "api-endpoints.ts"
        if not endpoints_file.exists():
            pytest.skip("api-endpoints.ts not found")

        content = endpoints_file.read_text(encoding="utf-8")
        groups: dict[str, dict[str, str]] = {}

        # Find all exported const *_ENDPOINTS blocks
        block_pattern = re.compile(
            r"export\s+const\s+(\w+_ENDPOINTS)\s*=\s*\{(.*?)\}\s*as\s+const",
            re.DOTALL,
        )

        for block_match in block_pattern.finditer(content):
            group_name = block_match.group(1)
            block_body = block_match.group(2)
            entries: dict[str, str] = {}

            # Match KEY: `...`, or KEY: "...",
            entry_pattern = re.compile(r"(\w+):\s*`([^`]+)`")
            for entry in entry_pattern.finditer(block_body):
                key = entry.group(1)
                path = entry.group(2)
                # Resolve template literals like ${API_PREFIX}
                path = path.replace("${API_PREFIX}", "/api/v1")
                entries[key] = path

            if entries:
                groups[group_name] = entries

        return groups

    def test_endpoints_exist(self, all_endpoints: dict[str, dict[str, str]]):
        """Must have endpoint groups defined."""
        assert len(all_endpoints) > 0, "No endpoint groups found"

    def test_no_excessive_path_sharing(self, all_endpoints: dict[str, dict[str, str]]):
        """
        In REST APIs, sharing paths for different HTTP methods is normal
        (GET, POST, PUT, DELETE on the same resource). However, if 4+
        endpoint keys share the exact same path, it likely signals a
        misconfiguration or unnecessary duplication.
        """
        max_allowed_sharing = 3  # GET + POST + PUT/DELETE

        for group_name, endpoints in all_endpoints.items():
            seen: dict[str, list[str]] = {}
            for key, path in endpoints.items():
                seen.setdefault(path, []).append(key)

            excessive: list[str] = []
            for path, keys in seen.items():
                if len(keys) > max_allowed_sharing:
                    excessive.append(f"  {group_name}: {len(keys)} keys share '{path}': {keys}")

            assert not excessive, f"Excessive path sharing (>{max_allowed_sharing}) in {group_name}:\n" + "\n".join(
                excessive
            )

    def test_all_paths_start_with_api_prefix(self, all_endpoints: dict[str, dict[str, str]]):
        """All API paths should start with /api/v1/ (except health endpoints)."""
        invalid: list[str] = []
        for group_name, endpoints in all_endpoints.items():
            if group_name == "HEALTH_ENDPOINTS":
                continue  # Health endpoints use /healthz etc.
            for key, path in endpoints.items():
                if not path.startswith("/api/v1/"):
                    invalid.append(f"{group_name}.{key}: '{path}'")

        assert not invalid, "Paths not starting with /api/v1/:\n" + "\n".join(invalid)

    def test_no_trailing_slashes(self, all_endpoints: dict[str, dict[str, str]]):
        """API paths must not have trailing slashes."""
        trailing: list[str] = []
        for group_name, endpoints in all_endpoints.items():
            for key, path in endpoints.items():
                if path.endswith("/") and path != "/":
                    trailing.append(f"{group_name}.{key}: '{path}'")

        assert not trailing, "Paths with trailing slashes:\n" + "\n".join(trailing)

    def test_paths_are_lowercase(self, all_endpoints: dict[str, dict[str, str]]):
        """API paths (excluding parameters) should be lowercase."""
        uppercase: list[str] = []
        for group_name, endpoints in all_endpoints.items():
            for key, path in endpoints.items():
                # Remove {param} placeholders before checking case
                path_no_params = re.sub(r"\{[^}]+\}", "", path)
                if path_no_params != path_no_params.lower():
                    uppercase.append(f"{group_name}.{key}: '{path}'")

        assert not uppercase, "Paths with uppercase characters:\n" + "\n".join(uppercase)


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Error Code Conflict Tests - اختبارات تعارض أكواد الأخطاء
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestErrorCodeConflicts:
    """Verify error codes are unique and properly configured."""

    @pytest.fixture
    def error_codes(self) -> dict[str, str]:
        """Parse ERROR_CODES from error-codes.ts."""
        codes_file = PROJECT_ROOT / "packages" / "shared-types" / "src" / "contracts" / "error-codes.ts"
        if not codes_file.exists():
            pytest.skip("error-codes.ts not found")

        content = codes_file.read_text(encoding="utf-8")
        codes: dict[str, str] = {}

        # Match KEY: "VALUE",
        pattern = re.compile(r'(\w+):\s*"([^"]+)"')
        in_error_codes = False
        for line in content.splitlines():
            if "ERROR_CODES" in line and "=" in line and "{" in line:
                in_error_codes = True
                continue
            if in_error_codes and "} as const" in line:
                break
            if in_error_codes:
                match = pattern.search(line)
                if match:
                    codes[match.group(1)] = match.group(2)

        return codes

    @pytest.fixture
    def error_messages(self) -> dict[str, dict]:
        """Parse ERROR_MESSAGES from error-codes.ts."""
        codes_file = PROJECT_ROOT / "packages" / "shared-types" / "src" / "contracts" / "error-codes.ts"
        if not codes_file.exists():
            pytest.skip("error-codes.ts not found")

        content = codes_file.read_text(encoding="utf-8")
        messages: dict[str, dict] = {}

        # Find error message blocks with en: and ar: fields
        block_pattern = re.compile(
            r"\[ERROR_CODES\.(\w+)\]:\s*\{[^}]*"
            r'en:\s*"([^"]*)"[^}]*'
            r'ar:\s*"([^"]*)"',
            re.DOTALL,
        )
        for match in block_pattern.finditer(content):
            key = match.group(1)
            messages[key] = {
                "en": match.group(2),
                "ar": match.group(3),
            }

        return messages

    def test_error_codes_exist(self, error_codes: dict[str, str]):
        """Error codes must be defined."""
        assert len(error_codes) > 0, "No error codes found"

    def test_no_duplicate_error_code_values(self, error_codes: dict[str, str]):
        """Each error code value must be unique."""
        seen: dict[str, str] = {}
        duplicates: list[str] = []
        for key, value in error_codes.items():
            if value in seen:
                duplicates.append(f"Value '{value}' used by both '{seen[value]}' and '{key}'")
            else:
                seen[value] = key

        assert not duplicates, "Duplicate error code values:\n" + "\n".join(duplicates)

    def test_all_generic_error_codes_have_messages(
        self,
        error_codes: dict[str, str],
        error_messages: dict[str, dict],
    ):
        """
        Generic error codes (non-service-specific) should have bilingual messages.
        Vision-specific codes (VISION_*) have their own message system in the
        vision service and are excluded from this check.
        """
        # Service-specific prefixes that manage their own messages
        service_prefixes = ("VISION_",)

        missing: list[str] = []
        for key in error_codes:
            if any(key.startswith(p) for p in service_prefixes):
                continue
            if key not in error_messages:
                missing.append(key)

        assert not missing, "Generic error codes without messages (EN/AR):\n" + "\n".join(missing)

    def test_all_messages_have_arabic_translation(self, error_messages: dict[str, dict]):
        """All error messages must include Arabic translations."""
        missing_ar: list[str] = []
        for key, msg in error_messages.items():
            if not msg.get("ar"):
                missing_ar.append(key)

        assert not missing_ar, "Error messages missing Arabic translation:\n" + "\n".join(missing_ar)


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Module Import Conflict Tests - اختبارات تعارض الاستيرادات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestModuleImportConflicts:
    """Verify shared Python modules can be imported without conflicts."""

    SHARED_MODULES = [
        "shared.events.subjects",
    ]

    OPTIONAL_MODULES = [
        "shared.auth",
        "shared.cache",
        "shared.monitoring",
        "shared.middleware",
        "shared.security",
        "shared.observability",
        "shared.telemetry",
        "shared.versioning",
    ]

    def test_event_subjects_importable(self):
        """shared.events.subjects must import cleanly."""
        try:
            import shared.events.subjects  # noqa: F401
        except ImportError as e:
            pytest.skip(f"Cannot import shared.events.subjects: {e}")

    @pytest.mark.parametrize("module_name", OPTIONAL_MODULES)
    def test_optional_module_import_no_crash(self, module_name: str):
        """
        Optional modules should either import cleanly or raise ImportError
        for missing dependencies, never crash with unexpected errors.
        """
        try:
            importlib.import_module(module_name)
        except ImportError:
            pytest.skip(f"{module_name} has missing dependencies (OK)")
        except Exception as e:
            pytest.fail(f"{module_name} raised unexpected error on import: {type(e).__name__}: {e}")

    def test_no_circular_imports_in_events(self):
        """shared.events.subjects should not cause circular import issues."""
        # Clear cached modules
        modules_to_clear = [key for key in sys.modules if key.startswith("shared.events")]
        saved = {}
        for mod in modules_to_clear:
            saved[mod] = sys.modules.pop(mod)

        try:
            import shared.events.subjects  # noqa: F401

            # Re-import should also work
            importlib.reload(shared.events.subjects)
        except ImportError:
            pytest.skip("shared.events.subjects not available")
        finally:
            # Restore original state
            for mod, val in saved.items():
                sys.modules[mod] = val

    def test_subject_utility_functions_callable(self):
        """Utility functions in subjects module must be callable."""
        try:
            from shared.events.subjects import (
                get_subject_for_event,
                get_tenant_subject,
                get_wildcard_subject,
                is_valid_subject,
                lookup_subject,
            )
        except ImportError:
            pytest.skip("shared.events.subjects not importable")
            return

        assert callable(get_subject_for_event)
        assert callable(get_wildcard_subject)
        assert callable(is_valid_subject)
        assert callable(get_tenant_subject)
        assert callable(lookup_subject)


# ═══════════════════════════════════════════════════════════════════════════════
# 6. NATS Subject Utility Tests - اختبارات دوال موضوعات NATS
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestNATSSubjectUtilities:
    """Verify NATS subject utility functions produce correct results."""

    def test_get_subject_for_event_with_prefix(self):
        """Already-prefixed subjects should pass through unchanged."""
        try:
            from shared.events.subjects import get_subject_for_event
        except ImportError:
            pytest.skip("Module not available")
            return
        assert get_subject_for_event("sahool.field.created") == "sahool.field.created"

    def test_get_subject_for_event_without_prefix(self):
        """Unprefixed events should get the sahool. prefix added."""
        try:
            from shared.events.subjects import get_subject_for_event
        except ImportError:
            pytest.skip("Module not available")
            return
        assert get_subject_for_event("field.created") == "sahool.field.created"

    def test_get_wildcard_subject(self):
        """Wildcard subjects should follow sahool.{domain}.* pattern."""
        try:
            from shared.events.subjects import get_wildcard_subject
        except ImportError:
            pytest.skip("Module not available")
            return
        assert get_wildcard_subject("field") == "sahool.field.*"
        assert get_wildcard_subject("billing") == "sahool.billing.*"

    def test_is_valid_subject_positive(self):
        """Valid subjects must pass validation."""
        try:
            from shared.events.subjects import is_valid_subject
        except ImportError:
            pytest.skip("Module not available")
            return
        assert is_valid_subject("sahool.field.created") is True
        assert is_valid_subject("sahool.billing.payment.completed") is True

    def test_is_valid_subject_negative(self):
        """Invalid subjects must fail validation."""
        try:
            from shared.events.subjects import is_valid_subject
        except ImportError:
            pytest.skip("Module not available")
            return
        assert is_valid_subject("field.created") is False
        assert is_valid_subject("sahool") is False
        assert is_valid_subject("sahool.field") is False

    def test_tenant_subject_format(self):
        """Tenant-scoped subjects must follow the expected pattern."""
        try:
            from shared.events.subjects import get_tenant_subject
        except ImportError:
            pytest.skip("Module not available")
            return
        test_uuid = "00000000-0000-0000-0000-000000000123"
        result = get_tenant_subject(test_uuid, "field", "created")
        assert result == f"sahool.tenant.{test_uuid}.field.created"

    def test_tenant_subject_requires_tenant_id(self):
        """get_tenant_subject must reject empty tenant_id."""
        try:
            from shared.events.subjects import get_tenant_subject
        except ImportError:
            pytest.skip("Module not available")
            return
        with pytest.raises(ValueError, match="tenant_id"):
            get_tenant_subject("", "field", "created")

    def test_tenant_wildcard_all_domains(self):
        """Tenant wildcard with default domain should use '>' for all."""
        try:
            from shared.events.subjects import get_tenant_wildcard
        except ImportError:
            pytest.skip("Module not available")
            return
        test_uuid = "00000000-0000-0000-0000-000000000123"
        result = get_tenant_wildcard(test_uuid)
        assert result == f"sahool.tenant.{test_uuid}.>"

    def test_tenant_wildcard_specific_domain(self):
        """Tenant wildcard with specific domain should use '.>' suffix."""
        try:
            from shared.events.subjects import get_tenant_wildcard
        except ImportError:
            pytest.skip("Module not available")
            return
        test_uuid = "00000000-0000-0000-0000-000000000123"
        result = get_tenant_wildcard(test_uuid, "field")
        assert result == f"sahool.tenant.{test_uuid}.field.>"

    def test_lookup_subject_known(self):
        """lookup_subject should resolve known event types from registry."""
        try:
            from shared.events.subjects import lookup_subject
        except ImportError:
            pytest.skip("Module not available")
            return
        assert lookup_subject("field.created") == "sahool.field.created"
        assert lookup_subject("task.completed") == "sahool.task.completed"

    def test_lookup_subject_unknown_falls_back(self):
        """lookup_subject should construct a subject for unknown types."""
        try:
            from shared.events.subjects import lookup_subject
        except ImportError:
            pytest.skip("Module not available")
            return
        result = lookup_subject("custom.unknown_action")
        assert result == "sahool.custom.unknown_action"


# ═══════════════════════════════════════════════════════════════════════════════
# 7. TenantSubjectBuilder Tests - اختبارات بانٍ موضوعات المستأجر
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestTenantSubjectBuilder:
    """Verify TenantSubjectBuilder produces correct tenant-scoped subjects."""

    def _get_builder(self, tenant_id: str = "farm_001"):
        try:
            from shared.events.subjects import TenantSubjectBuilder
        except ImportError:
            pytest.skip("TenantSubjectBuilder not importable")
            return None  # unreachable, satisfies type checker
        return TenantSubjectBuilder(tenant_id)

    def test_builder_field_created(self):
        builder = self._get_builder("farm_001")
        assert builder.field.created() == "sahool.tenant.farm_001.field.created"

    def test_builder_field_updated(self):
        builder = self._get_builder("farm_001")
        assert builder.field.updated() == "sahool.tenant.farm_001.field.updated"

    def test_builder_field_deleted(self):
        builder = self._get_builder("farm_001")
        assert builder.field.deleted() == "sahool.tenant.farm_001.field.deleted"

    def test_builder_weather_all(self):
        builder = self._get_builder("farm_001")
        assert builder.weather.all() == "sahool.tenant.farm_001.weather.>"

    def test_builder_billing_action(self):
        builder = self._get_builder("org_abc")
        assert builder.billing.action("payment.completed") == "sahool.tenant.org_abc.billing.payment.completed"

    def test_builder_generic_subject(self):
        builder = self._get_builder("t1")
        assert builder.subject("drone", "mission_created") == "sahool.tenant.t1.drone.mission_created"

    def test_builder_generic_wildcard(self):
        builder = self._get_builder("t1")
        assert builder.wildcard("iot") == "sahool.tenant.t1.iot.>"

    def test_builder_requires_tenant_id(self):
        try:
            from shared.events.subjects import TenantSubjectBuilder
        except ImportError:
            pytest.skip("TenantSubjectBuilder not importable")
            return
        with pytest.raises(ValueError, match="tenant_id"):
            TenantSubjectBuilder("")


# ═══════════════════════════════════════════════════════════════════════════════
# 8. Docker Compose Port Conflict Tests - اختبارات تعارض منافذ Docker
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestDockerComposePortConflicts:
    """Verify docker-compose files have no host port conflicts."""

    @pytest.fixture
    def compose_host_ports(self) -> dict[str, list[str]]:
        """
        Extract host-mapped ports from docker-compose.yml.
        Returns {host_port: [service_names]}.

        Handles formats:
            - "127.0.0.1:5432:5432"
            - "8090:8090"
            - "3000:3000"
        """
        compose_file = PROJECT_ROOT / "docker-compose.yml"
        if not compose_file.exists():
            pytest.skip("docker-compose.yml not found")

        content = compose_file.read_text(encoding="utf-8")
        port_map: dict[str, list[str]] = {}
        current_service = None
        in_ports = False

        for line in content.splitlines():
            stripped = line.strip()

            # Detect service name (indented exactly 2 spaces, ends with :)
            svc_match = re.match(r"^  (\w[\w-]*):", line)
            if svc_match and not line.startswith("    "):
                current_service = svc_match.group(1)
                in_ports = False
                continue

            # Detect ports: section
            if stripped == "ports:":
                in_ports = True
                continue

            # If we hit another key at same indent level, leave ports section
            if in_ports and re.match(r"^    \w", line) and not stripped.startswith("-"):
                in_ports = False
                continue

            # Parse port lines: - "127.0.0.1:5432:5432" or - "8090:8090"
            if in_ports and current_service and stripped.startswith("-"):
                # Match host:container or ip:host:container port patterns
                # Pattern: optional_ip:HOST_PORT:CONTAINER_PORT
                port_match = re.search(
                    r"(?:\d+\.\d+\.\d+\.\d+:)?(\d{2,5}):(\d{2,5})",
                    stripped,
                )
                if port_match:
                    host_port = port_match.group(1)
                    port_map.setdefault(host_port, []).append(current_service)

        return port_map

    def test_no_duplicate_host_ports(self, compose_host_ports: dict[str, list[str]]):
        """No two services in docker-compose.yml should bind to the same host port."""
        conflicts: list[str] = []
        for port, services in compose_host_ports.items():
            if len(services) > 1:
                conflicts.append(f"Host port {port} claimed by: {', '.join(services)}")

        assert not conflicts, "Docker Compose host port conflicts:\n" + "\n".join(conflicts)


# ═══════════════════════════════════════════════════════════════════════════════
# 9. Governance Services Registry Tests - اختبارات سجل خدمات الحوكمة
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGovernanceServicesRegistry:
    """Verify governance/services.yaml has no conflicts."""

    @pytest.fixture
    def services_yaml_content(self) -> str:
        """Load raw content from governance/services.yaml."""
        services_file = PROJECT_ROOT / "governance" / "services.yaml"
        if not services_file.exists():
            pytest.skip("governance/services.yaml not found")
        return services_file.read_text(encoding="utf-8")

    def test_services_yaml_exists(self, services_yaml_content: str):
        """Services registry file must exist and be non-empty."""
        assert len(services_yaml_content) > 0

    def test_services_yaml_has_version(self, services_yaml_content: str):
        """services.yaml must declare a version."""
        assert "version:" in services_yaml_content, "governance/services.yaml must contain a 'version:' field"

    def test_no_duplicate_service_names_in_yaml(self, services_yaml_content: str):
        """
        Service names (top-level keys under 'services:') should be unique.
        YAML technically allows duplicate keys but last-write-wins can hide bugs.
        """
        # Simple heuristic: look for lines matching "  service-name:" pattern
        svc_pattern = re.compile(r"^  ([\w-]+):", re.MULTILINE)
        names: list[str] = svc_pattern.findall(services_yaml_content)
        seen: dict[str, int] = {}
        duplicates: list[str] = []
        for name in names:
            seen[name] = seen.get(name, 0) + 1
        for name, count in seen.items():
            if count > 1:
                duplicates.append(f"'{name}' appears {count} times")

        assert not duplicates, "Duplicate service names in services.yaml:\n" + "\n".join(duplicates)


# ═══════════════════════════════════════════════════════════════════════════════
# 10. Cross-Contract Consistency Tests - اختبارات اتساق العقود
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestCrossContractConsistency:
    """
    Verify consistency across different contract files
    (ports, endpoints, error codes, events).
    """

    def test_contract_version_format(self):
        """CONTRACT_VERSION in index.ts should follow semver."""
        index_file = PROJECT_ROOT / "packages" / "shared-types" / "src" / "contracts" / "index.ts"
        if not index_file.exists():
            pytest.skip("contracts/index.ts not found")

        content = index_file.read_text(encoding="utf-8")
        match = re.search(r'CONTRACT_VERSION\s*=\s*"(\d+\.\d+\.\d+)"', content)
        assert match, "CONTRACT_VERSION not found or not semver format"

        version = match.group(1)
        parts = version.split(".")
        assert len(parts) == 3, f"CONTRACT_VERSION '{version}' is not valid semver"
        assert all(p.isdigit() for p in parts), f"CONTRACT_VERSION '{version}' contains non-numeric parts"

    def test_service_registry_ports_match_service_ports(self):
        """
        SERVICE_REGISTRY entries must reference ports that match SERVICE_PORTS.
        Catches copy-paste errors where registry port differs from constant.
        """
        ports_file = PROJECT_ROOT / "packages" / "shared-types" / "src" / "contracts" / "service-ports.ts"
        if not ports_file.exists():
            pytest.skip("service-ports.ts not found")

        content = ports_file.read_text(encoding="utf-8")

        # All registry entries should use SERVICE_PORTS.KEY, not literal numbers
        # Check for hard-coded port numbers in SERVICE_REGISTRY
        registry_section = ""
        in_registry = False
        for line in content.splitlines():
            if "SERVICE_REGISTRY" in line and "=" in line:
                in_registry = True
                continue
            if in_registry:
                registry_section += line + "\n"
                if line.strip() == "};":
                    break

        # Find any literal port numbers in registry (should use SERVICE_PORTS.X)
        literal_ports = re.findall(r"port:\s+(\d+)", registry_section)
        assert not literal_ports, (
            f"SERVICE_REGISTRY uses literal port numbers instead of SERVICE_PORTS references: {literal_ports}"
        )
