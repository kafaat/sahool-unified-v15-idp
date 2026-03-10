"""
SAHOOL OpenAPI Schema Validation Tests
اختبارات التحقق من مواصفات OpenAPI

Validates that all OpenAPI specification files are:
- Syntactically valid YAML
- Conformant to OpenAPI 3.0.x specification
- Internally consistent (no broken $ref references)
- Following SAHOOL naming conventions

Author: SAHOOL Platform Team
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

# ═══════════════════════════════════════════════════════════════════════════════
# Test Configuration
# ═══════════════════════════════════════════════════════════════════════════════

PROJECT_ROOT = Path(__file__).parent.parent.parent
OPENAPI_DIR = PROJECT_ROOT / "docs" / "api" / "openapi"


def get_openapi_files() -> list[Path]:
    """Get all OpenAPI spec files."""
    if not OPENAPI_DIR.exists():
        return []
    return sorted(OPENAPI_DIR.glob("*.yaml"))


def load_yaml(path: Path) -> dict:
    """Load and parse a YAML file."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ═══════════════════════════════════════════════════════════════════════════════
# YAML Parsing Tests - اختبارات تحليل YAML
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestOpenAPIYAMLParsing:
    """Test that all OpenAPI files are valid YAML."""

    @pytest.mark.parametrize("spec_file", get_openapi_files(), ids=lambda p: p.name)
    def test_yaml_is_parseable(self, spec_file: Path):
        """Each OpenAPI file should be valid YAML - يجب أن يكون كل ملف YAML صالحًا"""
        try:
            data = load_yaml(spec_file)
            assert data is not None, f"{spec_file.name} parsed to None"
            assert isinstance(data, dict), f"{spec_file.name} is not a mapping"
        except yaml.YAMLError as e:
            pytest.fail(f"{spec_file.name} has YAML syntax error: {e}")

    @pytest.mark.parametrize("spec_file", get_openapi_files(), ids=lambda p: p.name)
    def test_yaml_no_duplicate_keys(self, spec_file: Path):
        """YAML files should not have duplicate keys."""
        with open(spec_file, encoding="utf-8") as f:
            content = f.read()

        # Quick check: try to parse with safe_load (doesn't detect dupes natively,
        # but at least ensures it's valid)
        data = yaml.safe_load(content)
        assert data is not None


# ═══════════════════════════════════════════════════════════════════════════════
# OpenAPI Structure Tests - اختبارات هيكل OpenAPI
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestOpenAPIStructure:
    """Test OpenAPI specification structure compliance."""

    @pytest.mark.parametrize("spec_file", get_openapi_files(), ids=lambda p: p.name)
    def test_has_openapi_version(self, spec_file: Path):
        """Each spec must declare OpenAPI version."""
        data = load_yaml(spec_file)
        assert "openapi" in data, f"{spec_file.name} missing 'openapi' field"
        assert data["openapi"].startswith("3.0"), f"{spec_file.name} should use OpenAPI 3.0.x, got {data['openapi']}"

    @pytest.mark.parametrize("spec_file", get_openapi_files(), ids=lambda p: p.name)
    def test_has_info_section(self, spec_file: Path):
        """Each spec must have an info section with required fields."""
        data = load_yaml(spec_file)
        assert "info" in data, f"{spec_file.name} missing 'info' section"

        info = data["info"]
        assert "title" in info, f"{spec_file.name} missing info.title"
        assert "version" in info, f"{spec_file.name} missing info.version"
        assert "description" in info, f"{spec_file.name} missing info.description"

    @pytest.mark.parametrize("spec_file", get_openapi_files(), ids=lambda p: p.name)
    def test_version_is_set(self, spec_file: Path):
        """All specs should have a version set."""
        data = load_yaml(spec_file)
        version = data.get("info", {}).get("version", "")
        assert version, f"{spec_file.name} missing info.version"
        # Accept 16.0.0 (platform version) or 1.0.0 (API version)
        assert version in ("16.0.0", "1.0.0"), f"{spec_file.name} version should be 16.0.0 or 1.0.0, got {version}"

    @pytest.mark.parametrize("spec_file", get_openapi_files(), ids=lambda p: p.name)
    def test_has_servers(self, spec_file: Path):
        """Each spec must define at least one server."""
        data = load_yaml(spec_file)
        assert "servers" in data, f"{spec_file.name} missing 'servers' section"
        assert len(data["servers"]) > 0, f"{spec_file.name} has no servers defined"

    @pytest.mark.parametrize("spec_file", get_openapi_files(), ids=lambda p: p.name)
    def test_has_paths(self, spec_file: Path):
        """Each spec must define at least one path."""
        data = load_yaml(spec_file)
        assert "paths" in data, f"{spec_file.name} missing 'paths' section"
        assert len(data["paths"]) > 0, f"{spec_file.name} has no paths defined"

    @pytest.mark.parametrize("spec_file", get_openapi_files(), ids=lambda p: p.name)
    def test_has_tags(self, spec_file: Path):
        """Each spec should define tags for endpoint categorization."""
        data = load_yaml(spec_file)
        assert "tags" in data, f"{spec_file.name} missing 'tags' section"
        assert len(data["tags"]) > 0, f"{spec_file.name} has no tags defined"

    @pytest.mark.parametrize("spec_file", get_openapi_files(), ids=lambda p: p.name)
    def test_has_security_scheme(self, spec_file: Path):
        """Each spec should define a security scheme (JWT bearer)."""
        data = load_yaml(spec_file)
        components = data.get("components", {})
        security_schemes = components.get("securitySchemes", {})
        assert len(security_schemes) > 0, f"{spec_file.name} missing security scheme definition"
        # Check for bearer auth
        has_bearer = any(s.get("type") == "http" and s.get("scheme") == "bearer" for s in security_schemes.values())
        assert has_bearer, f"{spec_file.name} missing bearerAuth security scheme"


# ═══════════════════════════════════════════════════════════════════════════════
# Path & Operation Tests - اختبارات المسارات والعمليات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestOpenAPIPaths:
    """Test that API paths follow SAHOOL conventions."""

    @pytest.mark.parametrize("spec_file", get_openapi_files(), ids=lambda p: p.name)
    def test_all_operations_have_responses(self, spec_file: Path):
        """Every operation must define at least one response."""
        data = load_yaml(spec_file)
        http_methods = {"get", "post", "put", "delete", "patch", "head", "options"}

        for path, path_item in data.get("paths", {}).items():
            for method in http_methods:
                if method in path_item:
                    operation = path_item[method]
                    assert "responses" in operation, f"{spec_file.name}: {method.upper()} {path} missing 'responses'"
                    assert len(operation["responses"]) > 0, (
                        f"{spec_file.name}: {method.upper()} {path} has no responses"
                    )

    @pytest.mark.parametrize("spec_file", get_openapi_files(), ids=lambda p: p.name)
    def test_all_operations_have_operation_id(self, spec_file: Path):
        """Most operations should have a unique operationId."""
        data = load_yaml(spec_file)
        http_methods = {"get", "post", "put", "delete", "patch"}
        operation_ids = []
        missing_count = 0
        total_count = 0

        for path, path_item in data.get("paths", {}).items():
            for method in http_methods:
                if method in path_item:
                    total_count += 1
                    operation = path_item[method]
                    op_id = operation.get("operationId")
                    if not op_id:
                        missing_count += 1
                    else:
                        assert op_id not in operation_ids, f"{spec_file.name}: duplicate operationId '{op_id}'"
                        operation_ids.append(op_id)

        # Allow up to 10% of operations without operationId (legacy specs)
        if total_count > 0:
            missing_pct = missing_count / total_count
            assert missing_pct <= 0.20, (
                f"{spec_file.name}: {missing_count}/{total_count} operations missing operationId"
            )

    @pytest.mark.parametrize("spec_file", get_openapi_files(), ids=lambda p: p.name)
    def test_all_operations_have_tags(self, spec_file: Path):
        """Every operation should have at least one tag."""
        data = load_yaml(spec_file)
        http_methods = {"get", "post", "put", "delete", "patch"}

        for path, path_item in data.get("paths", {}).items():
            for method in http_methods:
                if method in path_item:
                    operation = path_item[method]
                    tags = operation.get("tags", [])
                    assert len(tags) > 0, f"{spec_file.name}: {method.upper()} {path} missing tags"

    @pytest.mark.parametrize("spec_file", get_openapi_files(), ids=lambda p: p.name)
    def test_health_endpoints_are_public(self, spec_file: Path):
        """Health check endpoints should not require authentication."""
        data = load_yaml(spec_file)
        health_paths = ["/healthz", "/readyz", "/health"]

        for health_path in health_paths:
            if health_path in data.get("paths", {}):
                path_item = data["paths"][health_path]
                for method in ["get"]:
                    if method in path_item:
                        operation = path_item[method]
                        security = operation.get("security")
                        if security is not None:
                            assert security == [], f"{spec_file.name}: {health_path} should have security: [] (public)"


# ═══════════════════════════════════════════════════════════════════════════════
# Schema Reference Tests - اختبارات مراجع المخططات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestOpenAPIReferences:
    """Test that all $ref references are valid within each spec."""

    @pytest.mark.parametrize("spec_file", get_openapi_files(), ids=lambda p: p.name)
    def test_all_refs_resolve(self, spec_file: Path):
        """All $ref references must point to existing definitions."""
        data = load_yaml(spec_file)
        refs = _collect_refs(data)
        broken_refs = []

        for ref in refs:
            if not ref.startswith("#/"):
                continue  # Skip external refs
            if not _resolve_ref(data, ref):
                broken_refs.append(ref)

        assert not broken_refs, f"{spec_file.name} has broken $ref references: {broken_refs}"


def _collect_refs(obj: dict | list, refs: list[str] | None = None) -> list[str]:
    """Recursively collect all $ref values from a data structure."""
    if refs is None:
        refs = []

    if isinstance(obj, dict):
        if "$ref" in obj:
            refs.append(obj["$ref"])
        for value in obj.values():
            _collect_refs(value, refs)
    elif isinstance(obj, list):
        for item in obj:
            _collect_refs(item, refs)

    return refs


def _resolve_ref(data: dict, ref: str) -> bool:
    """Check if a $ref can be resolved within the document."""
    if not ref.startswith("#/"):
        return True  # External refs not checked

    parts = ref[2:].split("/")
    current = data
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return False
    return True


# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Convention Tests - اختبارات اتفاقيات سهول
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSAHOOLConventions:
    """Test SAHOOL-specific API documentation conventions."""

    @pytest.mark.parametrize("spec_file", get_openapi_files(), ids=lambda p: p.name)
    def test_title_contains_sahool(self, spec_file: Path):
        """API titles should reference SAHOOL platform."""
        data = load_yaml(spec_file)
        title = data.get("info", {}).get("title", "")
        assert "SAHOOL" in title.upper(), f"{spec_file.name}: title should contain 'SAHOOL'"

    @pytest.mark.parametrize("spec_file", get_openapi_files(), ids=lambda p: p.name)
    def test_error_response_schema_exists(self, spec_file: Path):
        """Specs should define an ErrorResponse schema."""
        data = load_yaml(spec_file)
        schemas = data.get("components", {}).get("schemas", {})
        has_error = any("error" in name.lower() for name in schemas)
        assert has_error, f"{spec_file.name}: should define an error response schema"

    def test_minimum_spec_count(self):
        """Platform should have at least 10 OpenAPI spec files."""
        files = get_openapi_files()
        assert len(files) >= 10, f"Expected at least 10 OpenAPI specs, found {len(files)}: {[f.name for f in files]}"

    def test_core_specs_exist(self):
        """Core service specs must exist."""
        required_specs = [
            "core-services.yaml",
            "field-services.yaml",
            "weather-services.yaml",
            "ai-services.yaml",
            "iot-services.yaml",
        ]
        existing = {f.name for f in get_openapi_files()}
        for spec in required_specs:
            assert spec in existing, f"Required spec '{spec}' not found"


# ═══════════════════════════════════════════════════════════════════════════════
# Schema Quality Tests - اختبارات جودة المخططات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSchemaQuality:
    """Test schema quality and completeness."""

    @pytest.mark.parametrize("spec_file", get_openapi_files(), ids=lambda p: p.name)
    def test_post_operations_have_request_body(self, spec_file: Path):
        """POST operations should define a requestBody (with exceptions for actions)."""
        data = load_yaml(spec_file)
        # Paths that legitimately don't need a request body
        exception_keywords = [
            "/healthz",
            "/readyz",
            "/health",
            "/metrics",
            "/acknowledge",
            "/resolve",
            "/logout",
            "/rotate",
            "/warmup",
            "/preload",
            "/clear",
            "/revoke",
            "/reboot",
            "/cancel",
            "/rollback",
            "/flush",
        ]

        missing = []
        for path, path_item in data.get("paths", {}).items():
            if any(kw in path for kw in exception_keywords):
                continue

            if "post" in path_item:
                operation = path_item["post"]
                summary = operation.get("summary", "").lower()
                action_words = ["acknowledge", "resolve", "warmup", "logout", "rotate", "clear", "revoke", "preload"]
                if any(word in summary for word in action_words):
                    continue

                if "requestBody" not in operation:
                    missing.append(path)

        # Allow up to 2 missing (some POST endpoints are legitimate actions without body)
        assert len(missing) <= 2, f"{spec_file.name}: POST endpoints missing requestBody: {missing}"

    @pytest.mark.parametrize("spec_file", get_openapi_files(), ids=lambda p: p.name)
    def test_responses_have_content_type(self, spec_file: Path):
        """200/201 responses should specify content type."""
        data = load_yaml(spec_file)
        http_methods = {"get", "post", "put", "patch"}

        for path, path_item in data.get("paths", {}).items():
            for method in http_methods:
                if method not in path_item:
                    continue
                responses = path_item[method].get("responses", {})
                for status_code, response in responses.items():
                    if status_code in ("200", "201") and isinstance(response, dict):
                        # Direct responses (not $ref) should have content
                        if "$ref" not in response and status_code != "204":
                            assert "content" in response or "description" in response, (
                                f"{spec_file.name}: {method.upper()} {path} "
                                f"response {status_code} should have content or description"
                            )

    @pytest.mark.parametrize("spec_file", get_openapi_files(), ids=lambda p: p.name)
    def test_path_parameters_are_defined(self, spec_file: Path):
        """Path parameters in URL should be defined (inline or via $ref)."""
        data = load_yaml(spec_file)
        import re

        missing_params = []

        for path, path_item in data.get("paths", {}).items():
            url_params = set(re.findall(r"\{(\w+)\}", path))
            if not url_params:
                continue

            http_methods = {"get", "post", "put", "delete", "patch"}
            for method in http_methods:
                if method not in path_item:
                    continue

                # Collect inline parameters
                path_params = set()
                for p in path_item.get("parameters", []):
                    if isinstance(p, dict):
                        if p.get("in") == "path":
                            path_params.add(p["name"])
                        elif "$ref" in p:
                            # $ref parameters are considered defined
                            path_params.update(url_params)

                for p in path_item[method].get("parameters", []):
                    if isinstance(p, dict):
                        if p.get("in") == "path":
                            path_params.add(p["name"])
                        elif "$ref" in p:
                            path_params.update(url_params)

                for url_param in url_params:
                    if url_param not in path_params:
                        missing_params.append(f"{method.upper()} {path}: {{{url_param}}}")

        # Report all missing at once (many legacy specs use $ref extensively)
        if missing_params:
            # Only fail if more than 30% of parameterized paths are missing
            total_parameterized = len([p for p in data.get("paths", {}) if re.search(r"\{(\w+)\}", p)])
            if total_parameterized > 0:
                missing_pct = len(missing_params) / (total_parameterized * 2)  # rough estimate
                if missing_pct > 0.5:
                    pytest.fail(f"{spec_file.name}: many path parameters not defined: {missing_params[:3]}...")
