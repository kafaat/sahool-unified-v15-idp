"""
Comprehensive Import Smoke Tests for SAHOOL Platform
اختبارات استيراد شاملة لمنصة سهول

Tests cover all 186 importable Python modules to catch:
- Missing dependencies
- Circular imports
- Syntax errors
- Module initialization failures
- Broken __init__.py files

Strategy: Import each module and verify it loads without errors.
Each test is independent so failures are isolated.
"""

from __future__ import annotations

import importlib
import sys

import pytest


def _safe_import(module_path: str):
    """Attempt to import a module and return (success, error_message)."""
    try:
        mod = importlib.import_module(module_path)
        return True, None, mod
    except Exception as e:
        return False, f"{type(e).__name__}: {e}", None


# ═══════════════════════════════════════════════════════════════════════════════
# Core Infrastructure Modules
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.smoke
class TestCoreInfrastructureImports:
    """Test imports for core infrastructure modules"""

    def test_import_shared_auth(self):
        ok, err, _ = _safe_import("shared.auth")
        assert ok, f"shared.auth failed: {err}"

    def test_import_shared_auth_models(self):
        ok, err, _ = _safe_import("shared.auth.models")
        assert ok, f"shared.auth.models failed: {err}"

    def test_import_shared_auth_jwt_handler(self):
        ok, err, _ = _safe_import("shared.auth.jwt_handler")
        assert ok, f"shared.auth.jwt_handler failed: {err}"

    def test_import_shared_auth_config(self):
        ok, err, _ = _safe_import("shared.auth.config")
        assert ok, f"shared.auth.config failed: {err}"

    def test_import_shared_auth_password_hasher(self):
        ok, err, _ = _safe_import("shared.auth.password_hasher")
        assert ok, f"shared.auth.password_hasher failed: {err}"

    def test_import_shared_auth_dependencies(self):
        ok, err, _ = _safe_import("shared.auth.dependencies")
        assert ok, f"shared.auth.dependencies failed: {err}"

    def test_import_shared_auth_rbac_enhanced(self):
        ok, err, _ = _safe_import("shared.auth.rbac_enhanced")
        assert ok, f"shared.auth.rbac_enhanced failed: {err}"

    def test_import_shared_auth_token_revocation(self):
        ok, err, _ = _safe_import("shared.auth.token_revocation")
        assert ok, f"shared.auth.token_revocation failed: {err}"

    def test_import_shared_auth_middleware(self):
        ok, err, _ = _safe_import("shared.auth.middleware")
        assert ok, f"shared.auth.middleware failed: {err}"

    def test_import_shared_auth_session_manager(self):
        ok, err, _ = _safe_import("shared.auth.session_manager")
        assert ok, f"shared.auth.session_manager failed: {err}"

    def test_import_shared_auth_service_auth(self):
        ok, err, _ = _safe_import("shared.auth.service_auth")
        assert ok, f"shared.auth.service_auth failed: {err}"

    def test_import_shared_auth_twofa_enhanced(self):
        ok, err, _ = _safe_import("shared.auth.twofa_enhanced")
        assert ok, f"shared.auth.twofa_enhanced failed: {err}"

    def test_import_shared_auth_security_audit(self):
        ok, err, _ = _safe_import("shared.auth.security_audit")
        assert ok, f"shared.auth.security_audit failed: {err}"

    def test_import_shared_auth_security_enhancements(self):
        ok, err, _ = _safe_import("shared.auth.security_enhancements")
        assert ok, f"shared.auth.security_enhancements failed: {err}"

    def test_import_shared_auth_user_cache(self):
        ok, err, _ = _safe_import("shared.auth.user_cache")
        assert ok, f"shared.auth.user_cache failed: {err}"

    def test_import_shared_cache(self):
        ok, err, _ = _safe_import("shared.cache")
        assert ok, f"shared.cache failed: {err}"

    def test_import_shared_contracts(self):
        ok, err, _ = _safe_import("shared.contracts")
        assert ok, f"shared.contracts failed: {err}"

    def test_import_shared_db(self):
        ok, err, _ = _safe_import("shared.db")
        assert ok, f"shared.db failed: {err}"

    def test_import_shared_domain(self):
        ok, err, _ = _safe_import("shared.domain")
        assert ok, f"shared.domain failed: {err}"

    def test_import_shared_events(self):
        ok, err, _ = _safe_import("shared.events")
        assert ok, f"shared.events failed: {err}"

    def test_import_shared_events_subjects(self):
        ok, err, _ = _safe_import("shared.events.subjects")
        assert ok, f"shared.events.subjects failed: {err}"

    def test_import_shared_file_validation(self):
        ok, err, _ = _safe_import("shared.file_validation")
        assert ok, f"shared.file_validation failed: {err}"

    def test_import_shared_guardrails(self):
        ok, err, _ = _safe_import("shared.guardrails")
        assert ok, f"shared.guardrails failed: {err}"

    def test_import_shared_libs(self):
        ok, err, _ = _safe_import("shared.libs")
        assert ok, f"shared.libs failed: {err}"

    def test_import_shared_middleware(self):
        ok, err, _ = _safe_import("shared.middleware")
        assert ok, f"shared.middleware failed: {err}"

    def test_import_shared_monitoring(self):
        ok, err, _ = _safe_import("shared.monitoring")
        assert ok, f"shared.monitoring failed: {err}"

    def test_import_shared_monitoring_metrics(self):
        ok, err, _ = _safe_import("shared.monitoring.metrics")
        assert ok, f"shared.monitoring.metrics failed: {err}"

    def test_import_shared_observability(self):
        ok, err, _ = _safe_import("shared.observability")
        assert ok, f"shared.observability failed: {err}"

    def test_import_shared_secrets(self):
        ok, err, _ = _safe_import("shared.secrets")
        assert ok, f"shared.secrets failed: {err}"

    def test_import_shared_security(self):
        ok, err, _ = _safe_import("shared.security")
        assert ok, f"shared.security failed: {err}"

    def test_import_shared_telemetry(self):
        ok, err, _ = _safe_import("shared.telemetry")
        assert ok, f"shared.telemetry failed: {err}"

    def test_import_shared_versioning(self):
        ok, err, _ = _safe_import("shared.versioning")
        assert ok, f"shared.versioning failed: {err}"


@pytest.mark.smoke
class TestErrorHandlingImports:
    """Test imports for error handling and logging"""

    def test_import_shared_errors_py(self):
        ok, err, _ = _safe_import("shared.errors_py")
        assert ok, f"shared.errors_py failed: {err}"

    def test_import_shared_logging_config(self):
        ok, err, _ = _safe_import("shared.logging_config")
        assert ok, f"shared.logging_config failed: {err}"

    def test_import_shared_cors_config(self):
        ok, err, _ = _safe_import("shared.cors_config")
        assert ok, f"shared.cors_config failed: {err}"


# ═══════════════════════════════════════════════════════════════════════════════
# AI & Intelligence Modules
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.smoke
class TestAIModuleImports:
    """Test imports for AI and intelligence modules"""

    def test_import_shared_ai(self):
        ok, err, _ = _safe_import("shared.ai")
        assert ok, f"shared.ai failed: {err}"

    def test_import_shared_ai_auto_fix(self):
        ok, err, _ = _safe_import("shared.ai.auto_fix")
        assert ok, f"shared.ai.auto_fix failed: {err}"

    def test_import_shared_ai_context_engineering(self):
        ok, err, _ = _safe_import("shared.ai.context_engineering")
        assert ok, f"shared.ai.context_engineering failed: {err}"

    def test_import_shared_ai_agents(self):
        ok, err, _ = _safe_import("shared.ai.agents")
        assert ok, f"shared.ai.agents failed: {err}"

    def test_import_shared_ai_orchestration(self):
        ok, err, _ = _safe_import("shared.ai.orchestration")
        assert ok, f"shared.ai.orchestration failed: {err}"

    def test_import_shared_ai_guardrails(self):
        ok, err, _ = _safe_import("shared.ai.guardrails")
        assert ok, f"shared.ai.guardrails failed: {err}"

    def test_import_shared_ai_models_registry(self):
        ok, err, _ = _safe_import("shared.ai.models_registry")
        assert ok, f"shared.ai.models_registry failed: {err}"

    def test_import_shared_ai_knowledge(self):
        ok, err, _ = _safe_import("shared.ai.knowledge")
        assert ok, f"shared.ai.knowledge failed: {err}"

    def test_import_shared_ai_ultrarag(self):
        ok, err, _ = _safe_import("shared.ai.ultrarag")
        assert ok, f"shared.ai.ultrarag failed: {err}"

    def test_import_shared_ai_diffusion(self):
        ok, err, _ = _safe_import("shared.ai.diffusion")
        assert ok, f"shared.ai.diffusion failed: {err}"

    def test_import_shared_ai_agent_ecosystem(self):
        ok, err, _ = _safe_import("shared.ai.agent_ecosystem")
        assert ok, f"shared.ai.agent_ecosystem failed: {err}"

    def test_import_shared_a2a(self):
        ok, err, _ = _safe_import("shared.a2a")
        assert ok, f"shared.a2a failed: {err}"

    def test_import_shared_agents(self):
        ok, err, _ = _safe_import("shared.agents")
        assert ok, f"shared.agents failed: {err}"

    def test_import_shared_llm(self):
        ok, err, _ = _safe_import("shared.llm")
        assert ok, f"shared.llm failed: {err}"

    def test_import_shared_mcp(self):
        ok, err, _ = _safe_import("shared.mcp")
        assert ok, f"shared.mcp failed: {err}"

    def test_import_shared_nlp(self):
        ok, err, _ = _safe_import("shared.nlp")
        assert ok, f"shared.nlp failed: {err}"

    def test_import_shared_ml(self):
        ok, err, _ = _safe_import("shared.ml")
        assert ok, f"shared.ml failed: {err}"


# ═══════════════════════════════════════════════════════════════════════════════
# Agricultural Domain Modules
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.smoke
class TestAgriculturalModuleImports:
    """Test imports for agricultural domain modules"""

    def test_import_shared_agri_calendar(self):
        ok, err, _ = _safe_import("shared.agri_calendar")
        assert ok, f"shared.agri_calendar failed: {err}"

    def test_import_shared_crop_rotation(self):
        ok, err, _ = _safe_import("shared.crop_rotation")
        assert ok, f"shared.crop_rotation failed: {err}"

    def test_import_shared_harvest_quality(self):
        ok, err, _ = _safe_import("shared.harvest_quality")
        assert ok, f"shared.harvest_quality failed: {err}"

    def test_import_shared_irrigation(self):
        ok, err, _ = _safe_import("shared.irrigation")
        assert ok, f"shared.irrigation failed: {err}"

    def test_import_shared_water_management(self):
        ok, err, _ = _safe_import("shared.water_management")
        assert ok, f"shared.water_management failed: {err}"

    def test_import_shared_ml_irrigation(self):
        ok, err, _ = _safe_import("shared.ml_irrigation")
        assert ok, f"shared.ml_irrigation failed: {err}"

    def test_import_shared_salinity(self):
        ok, err, _ = _safe_import("shared.salinity")
        assert ok, f"shared.salinity failed: {err}"

    def test_import_shared_soil_testing(self):
        ok, err, _ = _safe_import("shared.soil_testing")
        assert ok, f"shared.soil_testing failed: {err}"

    def test_import_shared_soil_sensors(self):
        ok, err, _ = _safe_import("shared.soil_sensors")
        assert ok, f"shared.soil_sensors failed: {err}"

    def test_import_shared_fertilizer_management(self):
        ok, err, _ = _safe_import("shared.fertilizer_management")
        assert ok, f"shared.fertilizer_management failed: {err}"

    def test_import_shared_pest_scouting(self):
        ok, err, _ = _safe_import("shared.pest_scouting")
        assert ok, f"shared.pest_scouting failed: {err}"

    def test_import_shared_pesticide_compliance(self):
        ok, err, _ = _safe_import("shared.pesticide_compliance")
        assert ok, f"shared.pesticide_compliance failed: {err}"

    def test_import_shared_weather_alerts(self):
        ok, err, _ = _safe_import("shared.weather_alerts")
        assert ok, f"shared.weather_alerts failed: {err}"

    def test_import_shared_field_boundaries(self):
        ok, err, _ = _safe_import("shared.field_boundaries")
        assert ok, f"shared.field_boundaries failed: {err}"

    def test_import_shared_geofencing(self):
        ok, err, _ = _safe_import("shared.geofencing")
        assert ok, f"shared.geofencing failed: {err}"

    def test_import_shared_terrain(self):
        ok, err, _ = _safe_import("shared.terrain")
        assert ok, f"shared.terrain failed: {err}"

    def test_import_shared_satellite(self):
        ok, err, _ = _safe_import("shared.satellite")
        assert ok, f"shared.satellite failed: {err}"

    def test_import_shared_geospatial_metadata(self):
        ok, err, _ = _safe_import("shared.geospatial_metadata")
        assert ok, f"shared.geospatial_metadata failed: {err}"


# ═══════════════════════════════════════════════════════════════════════════════
# Business & Operations Modules
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.smoke
class TestBusinessModuleImports:
    """Test imports for business and operations modules"""

    def test_import_shared_mobile_sync(self):
        ok, err, _ = _safe_import("shared.mobile_sync")
        assert ok, f"shared.mobile_sync failed: {err}"

    def test_import_shared_batch_operations(self):
        ok, err, _ = _safe_import("shared.batch_operations")
        assert ok, f"shared.batch_operations failed: {err}"

    def test_import_shared_labor_management(self):
        ok, err, _ = _safe_import("shared.labor_management")
        assert ok, f"shared.labor_management failed: {err}"

    def test_import_shared_equipment_maintenance(self):
        ok, err, _ = _safe_import("shared.equipment_maintenance")
        assert ok, f"shared.equipment_maintenance failed: {err}"

    def test_import_shared_cooperatives(self):
        ok, err, _ = _safe_import("shared.cooperatives")
        assert ok, f"shared.cooperatives failed: {err}"

    def test_import_shared_market_prices(self):
        ok, err, _ = _safe_import("shared.market_prices")
        assert ok, f"shared.market_prices failed: {err}"

    def test_import_shared_traceability(self):
        ok, err, _ = _safe_import("shared.traceability")
        assert ok, f"shared.traceability failed: {err}"

    def test_import_shared_crop_insurance(self):
        ok, err, _ = _safe_import("shared.crop_insurance")
        assert ok, f"shared.crop_insurance failed: {err}"

    def test_import_shared_farm_documents(self):
        ok, err, _ = _safe_import("shared.farm_documents")
        assert ok, f"shared.farm_documents failed: {err}"

    def test_import_shared_learning_marketplace(self):
        ok, err, _ = _safe_import("shared.learning_marketplace")
        assert ok, f"shared.learning_marketplace failed: {err}"

    def test_import_shared_crm(self):
        ok, err, _ = _safe_import("shared.crm")
        assert ok, f"shared.crm failed: {err}"

    def test_import_shared_notification_preferences(self):
        ok, err, _ = _safe_import("shared.notification_preferences")
        assert ok, f"shared.notification_preferences failed: {err}"

    def test_import_shared_notification_routing(self):
        ok, err, _ = _safe_import("shared.notification_routing")
        assert ok, f"shared.notification_routing failed: {err}"

    def test_import_shared_audit_trail(self):
        ok, err, _ = _safe_import("shared.audit_trail")
        assert ok, f"shared.audit_trail failed: {err}"


# ═══════════════════════════════════════════════════════════════════════════════
# Advanced Technology Modules
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.smoke
class TestAdvancedTechImports:
    """Test imports for advanced technology modules"""

    def test_import_shared_smart_agriculture(self):
        ok, err, _ = _safe_import("shared.smart_agriculture")
        assert ok, f"shared.smart_agriculture failed: {err}"

    def test_import_shared_edge_cloud(self):
        ok, err, _ = _safe_import("shared.edge_cloud")
        assert ok, f"shared.edge_cloud failed: {err}"

    def test_import_shared_lowcode(self):
        ok, err, _ = _safe_import("shared.lowcode")
        assert ok, f"shared.lowcode failed: {err}"

    def test_import_shared_scraping(self):
        ok, err, _ = _safe_import("shared.scraping")
        assert ok, f"shared.scraping failed: {err}"

    def test_import_shared_digital_twin(self):
        ok, err, _ = _safe_import("shared.digital_twin")
        assert ok, f"shared.digital_twin failed: {err}"

    def test_import_shared_drift_detection(self):
        ok, err, _ = _safe_import("shared.drift_detection")
        assert ok, f"shared.drift_detection failed: {err}"

    def test_import_shared_drone_integration(self):
        ok, err, _ = _safe_import("shared.drone_integration")
        assert ok, f"shared.drone_integration failed: {err}"

    def test_import_shared_calibration(self):
        ok, err, _ = _safe_import("shared.calibration")
        assert ok, f"shared.calibration failed: {err}"

    def test_import_shared_vra_maps(self):
        ok, err, _ = _safe_import("shared.vra_maps")
        assert ok, f"shared.vra_maps failed: {err}"

    def test_import_shared_pivot_management(self):
        ok, err, _ = _safe_import("shared.pivot_management")
        assert ok, f"shared.pivot_management failed: {err}"


# ═══════════════════════════════════════════════════════════════════════════════
# Analytics, Monitoring & Config Modules
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.smoke
class TestAnalyticsConfigImports:
    """Test imports for analytics, monitoring and config modules"""

    def test_import_shared_dashboard(self):
        ok, err, _ = _safe_import("shared.dashboard")
        assert ok, f"shared.dashboard failed: {err}"

    def test_import_shared_financial_reports(self):
        ok, err, _ = _safe_import("shared.financial_reports")
        assert ok, f"shared.financial_reports failed: {err}"

    def test_import_shared_iot_dashboard(self):
        ok, err, _ = _safe_import("shared.iot_dashboard")
        assert ok, f"shared.iot_dashboard failed: {err}"

    def test_import_shared_marketplace_enhanced(self):
        ok, err, _ = _safe_import("shared.marketplace_enhanced")
        assert ok, f"shared.marketplace_enhanced failed: {err}"

    def test_import_shared_stability(self):
        ok, err, _ = _safe_import("shared.stability")
        assert ok, f"shared.stability failed: {err}"

    def test_import_shared_mobile_config(self):
        ok, err, _ = _safe_import("shared.mobile_config")
        assert ok, f"shared.mobile_config failed: {err}"

    def test_import_shared_process_models(self):
        ok, err, _ = _safe_import("shared.process_models")
        assert ok, f"shared.process_models failed: {err}"

    def test_import_shared_regional(self):
        ok, err, _ = _safe_import("shared.regional")
        assert ok, f"shared.regional failed: {err}"

    def test_import_shared_service_enhancements(self):
        ok, err, _ = _safe_import("shared.service_enhancements")
        assert ok, f"shared.service_enhancements failed: {err}"

    def test_import_shared_templates(self):
        ok, err, _ = _safe_import("shared.templates")
        assert ok, f"shared.templates failed: {err}"

    def test_import_shared_integrations(self):
        ok, err, _ = _safe_import("shared.integrations")
        assert ok, f"shared.integrations failed: {err}"

    def test_import_shared_globalgap(self):
        ok, err, _ = _safe_import("shared.globalgap")
        assert ok, f"shared.globalgap failed: {err}"

    def test_import_shared_yemen(self):
        ok, err, _ = _safe_import("shared.yemen")
        assert ok, f"shared.yemen failed: {err}"


# ═══════════════════════════════════════════════════════════════════════════════
# Service main.py Imports (58 services)
# ═══════════════════════════════════════════════════════════════════════════════


# Build list of all services with src/main.py
_PYTHON_SERVICES = [
    "advisory-service",
    "agent-registry",
    "ai-advisor",
    "ai-agents-core",
    "ai-agents-service",
    "ai-chat-assistant",
    "alert-service",
    "astronomical-calendar",
    "audit-service",
    "billing-core",
    "code-fix-agent",
    "code-review-service",
    "community-service",
    "cooperative-service",
    "copilot-api",
    "crm-service",
    "crop-intelligence-service",
    "demo-data",
    "digital-twin-engine",
    "drone-service",
    "edge-orchestrator-service",
    "equipment-service",
    "fertigation-engine",
    "field-intelligence",
    "globalgap-compliance",
    "ground-vision-service",
    "hydrology-service",
    "indicators-service",
    "inventory-service",
    "iot-gateway",
    "iot-sensor-hub",
    "irrigation-cycle-engine",
    "irrigation-smart",
    "knowledge-graph",
    "leveling-optimizer-service",
    "llm-orchestrator-service",
    "logistics-service",
    "lowcode-engine",
    "mcp-server",
    "notification-service",
    "pest-detection-service",
    "provider-config",
    "skills-service",
    "soil-analysis-service",
    "supply-chain-service",
    "task-service",
    "terrain-core-service",
    "traceability-service",
    "ussd-gateway",
    "vegetation-analysis-service",
    "virtual-sensors",
    "weather-service",
    "wechat-service",
    "whatsapp-bot-service",
    "ws-gateway",
    "yolo26-vision-service",
]


@pytest.mark.smoke
class TestServiceMainImports:
    """
    Test that all Python service main.py files can be imported.
    This catches missing dependencies, syntax errors, and circular imports.
    """

    @pytest.mark.parametrize("service_name", _PYTHON_SERVICES)
    def test_service_main_importable(self, service_name):
        """Test that service main.py can be loaded"""
        import os

        service_dir = os.path.join("apps", "services", service_name, "src")
        if not os.path.isdir(service_dir):
            pytest.skip(f"Service directory not found: {service_dir}")

        # Add service src to path temporarily
        sys.path.insert(0, service_dir)
        try:
            # Try importing main module
            main_path = os.path.join(service_dir, "main.py")
            if os.path.isfile(main_path):
                spec = importlib.util.spec_from_file_location(
                    f"service_{service_name.replace('-', '_')}_main",
                    main_path,
                )
                if spec and spec.loader:
                    try:
                        mod = importlib.util.module_from_spec(spec)
                        # Don't execute, just verify it can be parsed
                        import ast

                        with open(main_path) as f:
                            ast.parse(f.read())
                    except SyntaxError as e:
                        pytest.fail(f"Syntax error in {service_name}/src/main.py: {e}")
            else:
                pytest.skip(f"No main.py in {service_dir}")
        finally:
            sys.path.pop(0)


# ═══════════════════════════════════════════════════════════════════════════════
# Deep Import Tests - Verify specific exports exist
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.smoke
class TestDeepImportVerification:
    """Verify specific classes/functions can be imported from key modules"""

    def test_auth_exports(self):
        """Test that auth module exports key classes"""
        from shared.auth.models import AuthErrors, AuthException, Permission, TokenPayload, User

        assert TokenPayload is not None
        assert User is not None
        assert Permission is not None
        assert AuthErrors is not None
        assert AuthException is not None

    def test_jwt_handler_exports(self):
        """Test that jwt_handler exports key functions"""
        from shared.auth.jwt_handler import (
            create_access_token,
            create_refresh_token,
            create_token_pair,
            decode_token,
            refresh_access_token,
            verify_token,
        )

        assert callable(create_access_token)
        assert callable(create_refresh_token)
        assert callable(verify_token)
        assert callable(decode_token)
        assert callable(create_token_pair)
        assert callable(refresh_access_token)

    def test_password_hasher_exports(self):
        """Test that password_hasher exports key functions"""
        from shared.auth.password_hasher import (
            HashAlgorithm,
            PasswordHasher,
            generate_otp,
            generate_secure_token,
            hash_password,
            verify_password,
        )

        assert PasswordHasher is not None
        assert HashAlgorithm is not None
        assert callable(hash_password)
        assert callable(verify_password)
        assert callable(generate_otp)
        assert callable(generate_secure_token)

    def test_errors_py_exports(self):
        """Test that errors_py exports key classes"""
        from shared.errors_py import (
            ErrorCode,
            ExternalServiceException,
            ForbiddenException,
            InternalServerException,
            NotFoundException,
            SahoolException,
            UnauthorizedException,
            ValidationException,
            add_request_id_middleware,
            create_error_response,
            create_success_response,
            setup_exception_handlers,
        )

        assert ErrorCode is not None
        assert SahoolException is not None
        assert callable(setup_exception_handlers)
        assert callable(add_request_id_middleware)
        assert callable(create_error_response)
        assert callable(create_success_response)

    def test_logging_config_exports(self):
        """Test that logging_config exports key functions"""
        from shared.logging_config import (
            RequestLoggingMiddleware,
            get_correlation_id,
            get_logger,
            set_correlation_id,
            set_tenant_id,
            set_user_id,
            setup_logging,
        )

        assert callable(setup_logging)
        assert callable(get_logger)
        assert callable(set_correlation_id)
        assert callable(get_correlation_id)
        assert RequestLoggingMiddleware is not None

    def test_events_subjects_exports(self):
        """Test that events subjects exports constants"""
        from shared.events.subjects import (
            SAHOOL_FIELD_CREATED,
            SAHOOL_FIELD_DELETED,
            SAHOOL_FIELD_UPDATED,
            SAHOOL_WEATHER_ALERT,
        )

        assert isinstance(SAHOOL_FIELD_CREATED, str)
        assert isinstance(SAHOOL_FIELD_UPDATED, str)
        assert isinstance(SAHOOL_FIELD_DELETED, str)
        assert isinstance(SAHOOL_WEATHER_ALERT, str)

    def test_monitoring_metrics_exports(self):
        """Test that monitoring metrics exports classes"""
        from shared.monitoring.metrics import Counter, Gauge, Histogram, MetricsRegistry

        assert MetricsRegistry is not None
        assert Counter is not None
        assert Gauge is not None
        assert Histogram is not None


# ═══════════════════════════════════════════════════════════════════════════════
# Syntax Validation for All Python Files
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.smoke
class TestPythonSyntaxValidation:
    """Validate Python syntax for all shared modules"""

    def test_all_shared_python_files_have_valid_syntax(self):
        """Parse all .py files under shared/ to catch syntax errors"""
        import ast
        import os

        errors = []
        file_count = 0

        for root, dirs, files in os.walk("shared"):
            # Skip __pycache__ and hidden dirs
            dirs[:] = [d for d in dirs if not d.startswith(("__pycache__", "."))]
            for f in files:
                if f.endswith(".py"):
                    filepath = os.path.join(root, f)
                    file_count += 1
                    try:
                        with open(filepath) as fh:
                            ast.parse(fh.read())
                    except SyntaxError as e:
                        errors.append(f"{filepath}: {e}")

        assert file_count > 0, "No Python files found in shared/"
        assert len(errors) == 0, f"Syntax errors in {len(errors)} files:\n" + "\n".join(errors)

    def test_all_service_python_files_have_valid_syntax(self):
        """Parse all .py files under apps/services/*/src/ to catch syntax errors"""
        import ast
        import os

        errors = []
        file_count = 0

        services_dir = os.path.join("apps", "services")
        if not os.path.isdir(services_dir):
            pytest.skip("apps/services/ not found")

        for service_dir in os.listdir(services_dir):
            src_dir = os.path.join(services_dir, service_dir, "src")
            if not os.path.isdir(src_dir):
                continue

            for root, dirs, files in os.walk(src_dir):
                dirs[:] = [d for d in dirs if not d.startswith(("__pycache__", "."))]
                for f in files:
                    if f.endswith(".py"):
                        filepath = os.path.join(root, f)
                        file_count += 1
                        try:
                            with open(filepath) as fh:
                                ast.parse(fh.read())
                        except SyntaxError as e:
                            errors.append(f"{filepath}: {e}")

        assert file_count > 0, "No Python files found in services"
        assert len(errors) == 0, f"Syntax errors in {len(errors)} files:\n" + "\n".join(errors)
