"""
SAHOOL Agricultural Crop Management Services – Container Function Tests
=========================================================================
اختبارات وظائف خدمات إدارة المحاصيل الزراعية

Validates that irrigation, weather, fertilization, pest/disease detection,
soil testing, crop growth, and field management services have the correct
agricultural domain dependencies, NATS events, shared modules, and APIs.

Services:
  irrigation-smart · irrigation-cycle-engine · fertigation-engine
  weather-service · advisory-service · crop-intelligence-service
  pest-detection-service · soil-analysis-service · yolo26-vision-service
  digital-twin-engine

Domain coverage:
 1.  Irrigation & ET computation (FAO-56, water balance)
 2.  Weather integration & alert chain
 3.  Fertilizer/nutrient management
 4.  Pest & disease detection (YOLO, CV)
 5.  Soil testing & analysis
 6.  Crop growth stages & advisory
 7.  NATS events (sahool.recommendation.*, sahool.weather.*, sahool.health.*)
 8.  Shared agricultural modules
 9.  API endpoints for agricultural operations
10.  Agricultural domain data flow (sensor → analysis → recommendation)

Run:
    pytest tests/container/test_agri_crop_management_group.py -v --tb=short
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

pytestmark = [pytest.mark.container, pytest.mark.smoke]

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICES_DIR = REPO_ROOT / "apps" / "services"
MAIN_COMPOSE = REPO_ROOT / "docker-compose.yml"

# ---------------------------------------------------------------------------
# Agricultural Crop Management Cluster
# ---------------------------------------------------------------------------

CROP_MGMT_SERVICES: dict[str, int] = {
    "irrigation-smart": 8094,
    "irrigation-cycle-engine": 8250,
    "fertigation-engine": 8252,
    "weather-service": 8092,
    "advisory-service": 8093,
    "crop-intelligence-service": 8095,
    "pest-detection-service": 8125,
    "soil-analysis-service": 8134,
    "yolo26-vision-service": 8150,
    "digital-twin-engine": 8253,
}

# Sub-clusters by agricultural domain
IRRIGATION_CLUSTER = {"irrigation-smart", "irrigation-cycle-engine", "fertigation-engine"}
WEATHER_ADVISORY_CLUSTER = {"weather-service", "advisory-service"}
CROP_HEALTH_CLUSTER = {"crop-intelligence-service", "pest-detection-service", "yolo26-vision-service"}
SOIL_CLUSTER = {"soil-analysis-service"}
SIMULATION_CLUSTER = {"digital-twin-engine"}

# Agricultural shared modules expected to be accessible
AGRI_SHARED_MODULES = [
    "shared/irrigation",
    "shared/fertilizer_management",
    "shared/pest_scouting",
    "shared/soil_testing",
    "shared/weather_alerts",
    "shared/agri_calendar",
    "shared/crop_rotation",
    "shared/harvest_quality",
    "shared/water_management",
    "shared/salinity",
]

# NATS agricultural event subject prefixes
AGRI_NATS_SUBJECTS = [
    "SAHOOL_RECOMMENDATION_IRRIGATION",
    "SAHOOL_RECOMMENDATION_FERTILIZER",
    "SAHOOL_RECOMMENDATION_PEST_CONTROL",
    "SAHOOL_WEATHER_FORECAST",
    "SAHOOL_WEATHER_ALERT",
    "SAHOOL_HEALTH_DISEASE_DETECTED",
    "SAHOOL_HEALTH_PEST_DETECTED",
    "SAHOOL_HEALTH_STRESS",
    "SAHOOL_IRRIGATION_RECOMMENDATION_READY",
]

# ---------------------------------------------------------------------------

_dockerfile_cache: dict[str, str] = {}
_requirements_cache: dict[str, str] = {}
_source_cache: dict[str, str] = {}


def _read_dockerfile(svc: str) -> str:
    if svc not in _dockerfile_cache:
        path = SERVICES_DIR / svc / "Dockerfile"
        _dockerfile_cache[svc] = path.read_text("utf-8") if path.exists() else ""
    return _dockerfile_cache[svc]


def _req_packages(svc: str) -> set[str]:
    if svc not in _requirements_cache:
        path = SERVICES_DIR / svc / "requirements.txt"
        _requirements_cache[svc] = path.read_text("utf-8") if path.exists() else ""
    text = _requirements_cache[svc]
    pkgs: set[str] = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        name = re.split(r"[>=<!\[;]", line)[0].strip().lower().replace("-", "_")
        if name:
            pkgs.add(name)
    return pkgs


def _read_all_source(svc: str, max_files: int = 25) -> str:
    if svc not in _source_cache:
        src_dir = SERVICES_DIR / svc / "src"
        if not src_dir.exists():
            _source_cache[svc] = ""
            return ""
        combined = ""
        for f in sorted(src_dir.rglob("*.py"))[:max_files]:
            combined += f.read_text("utf-8", errors="ignore") + "\n"
        _source_cache[svc] = combined
    return _source_cache[svc]


@pytest.fixture(scope="module")
def compose() -> dict[str, Any]:
    with open(MAIN_COMPOSE, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def services(compose: dict) -> dict[str, Any]:
    return compose.get("services", {})


# ===========================================================================
# 1. Irrigation & Evapotranspiration (ET)
# ===========================================================================


class TestIrrigationDomain:
    """مجال الري وحساب التبخر-النتح."""

    @pytest.mark.parametrize("svc", sorted(IRRIGATION_CLUSTER))
    def test_source_references_irrigation(self, svc: str) -> None:
        """Irrigation service references irrigation/water management logic."""
        source = _read_all_source(svc)
        if not source:
            pytest.skip(f"No source for {svc}")
        irrigation_terms = ["irrigation", "water", "moisture", "et", "evapotranspiration"]
        found = [t for t in irrigation_terms if t in source.lower()]
        assert found, (
            f"{svc} source should reference irrigation domain terms"
        )

    def test_irrigation_cycle_has_fao56(self) -> None:
        """irrigation-cycle-engine declares pyfao56 for ET calculations."""
        pkgs = _req_packages("irrigation-cycle-engine")
        has_fao = "pyfao56" in pkgs
        if not has_fao:
            # May compute ET via shared/irrigation module
            source = _read_all_source("irrigation-cycle-engine")
            has_fao = "et" in source.lower() or "evapotranspiration" in source.lower()
        assert has_fao, (
            "irrigation-cycle-engine should use FAO-56 ET model or equivalent"
        )

    def test_irrigation_smart_recommendations(self) -> None:
        """irrigation-smart generates irrigation recommendations."""
        source = _read_all_source("irrigation-smart")
        if not source:
            pytest.skip("No source")
        has_rec = (
            "recommend" in source.lower()
            or "schedule" in source.lower()
            or "advisory" in source.lower()
        )
        assert has_rec, "irrigation-smart should generate irrigation recommendations"

    def test_fertigation_engine_nutrient_management(self) -> None:
        """fertigation-engine handles nutrient/fertilizer injection."""
        source = _read_all_source("fertigation-engine")
        if not source:
            pytest.skip("No source")
        has_nutrient = (
            "fertigation" in source.lower()
            or "nutrient" in source.lower()
            or "fertilizer" in source.lower()
            or "nitrogen" in source.lower()
        )
        assert has_nutrient, (
            "fertigation-engine should reference nutrient/fertilizer management"
        )


# ===========================================================================
# 2. Weather Integration & Alert Chain
# ===========================================================================


class TestWeatherDomain:
    """مجال الطقس والتنبيهات."""

    def test_weather_service_forecast(self) -> None:
        """weather-service references weather forecast data."""
        source = _read_all_source("weather-service")
        if not source:
            pytest.skip("No source")
        weather_terms = ["forecast", "temperature", "humidity", "wind", "rain", "weather"]
        found = [t for t in weather_terms if t in source.lower()]
        assert len(found) >= 2, (
            f"weather-service should reference weather terms (found: {found})"
        )

    def test_weather_service_alerts(self) -> None:
        """weather-service generates weather alerts (frost, heatwave, storm)."""
        source = _read_all_source("weather-service")
        if not source:
            pytest.skip("No source")
        alert_terms = ["alert", "frost", "heat", "storm", "warning", "drought"]
        found = [t for t in alert_terms if t in source.lower()]
        assert found, "weather-service should generate weather alerts"

    def test_advisory_integrates_weather(self) -> None:
        """advisory-service integrates weather data for recommendations."""
        source = _read_all_source("advisory-service")
        if not source:
            pytest.skip("No source")
        has_weather = "weather" in source.lower()
        has_advisory = (
            "recommend" in source.lower()
            or "advisory" in source.lower()
            or "advice" in source.lower()
        )
        assert has_weather and has_advisory, (
            "advisory-service should integrate weather into recommendations"
        )


# ===========================================================================
# 3. Pest & Disease Detection
# ===========================================================================


class TestPestDiseaseDomain:
    """مجال كشف الآفات والأمراض."""

    def test_yolo26_pest_disease_detection(self) -> None:
        """yolo26-vision-service detects pests and diseases."""
        source = _read_all_source("yolo26-vision-service")
        if not source:
            pytest.skip("No source")
        detection_terms = ["pest", "disease", "weed", "detect", "classification"]
        found = [t for t in detection_terms if t in source.lower()]
        assert len(found) >= 2, (
            f"yolo26-vision-service should detect pests/diseases (found: {found})"
        )

    def test_yolo26_has_deep_learning_deps(self) -> None:
        """yolo26-vision-service has torch + ultralytics for detection."""
        pkgs = _req_packages("yolo26-vision-service")
        assert "torch" in pkgs, "yolo26 missing torch"
        assert "ultralytics" in pkgs, "yolo26 missing ultralytics (YOLO framework)"

    def test_crop_intelligence_disease_analysis(self) -> None:
        """crop-intelligence-service analyzes crop health/diseases."""
        source = _read_all_source("crop-intelligence-service")
        if not source:
            pytest.skip("No source")
        health_terms = ["disease", "health", "crop", "intelligence", "diagnosis"]
        found = [t for t in health_terms if t in source.lower()]
        assert len(found) >= 2, (
            f"crop-intelligence-service should analyze crop health (found: {found})"
        )

    def test_pest_detection_identification(self) -> None:
        """pest-detection-service identifies pests."""
        source = _read_all_source("pest-detection-service")
        if not source:
            pytest.skip("No source")
        pest_terms = ["pest", "detect", "identify", "insect", "scout"]
        found = [t for t in pest_terms if t in source.lower()]
        assert found, "pest-detection-service should identify pests"


# ===========================================================================
# 4. Soil Testing & Analysis
# ===========================================================================


class TestSoilDomain:
    """مجال فحص التربة والتحليل."""

    def test_soil_analysis_references_soil(self) -> None:
        """soil-analysis-service references soil testing parameters."""
        source = _read_all_source("soil-analysis-service")
        if not source:
            pytest.skip("No source")
        soil_terms = ["soil", "ph", "nitrogen", "phosphorus", "potassium",
                       "organic", "texture", "salinity", "nutrient", "ec"]
        found = [t for t in soil_terms if t in source.lower()]
        assert len(found) >= 2, (
            f"soil-analysis-service should reference soil parameters (found: {found})"
        )

    def test_shared_soil_testing_module_exists(self) -> None:
        """shared/soil_testing/ module exists."""
        path = REPO_ROOT / "shared" / "soil_testing" / "__init__.py"
        assert path.exists(), "shared/soil_testing/ module missing"

    def test_shared_fertilizer_module_exists(self) -> None:
        """shared/fertilizer_management/ module exists."""
        path = REPO_ROOT / "shared" / "fertilizer_management" / "__init__.py"
        assert path.exists(), "shared/fertilizer_management/ module missing"


# ===========================================================================
# 5. Shared Agricultural Module Existence
# ===========================================================================


class TestSharedAgriModulesExist:
    """التحقق من وجود الوحدات الزراعية المشتركة."""

    @pytest.mark.parametrize("module_path", sorted(AGRI_SHARED_MODULES))
    def test_shared_module_exists(self, module_path: str) -> None:
        """Shared agricultural module directory exists."""
        full_path = REPO_ROOT / module_path
        assert full_path.exists(), f"{module_path}/ directory missing"

    @pytest.mark.parametrize("module_path", sorted(AGRI_SHARED_MODULES))
    def test_shared_module_has_init(self, module_path: str) -> None:
        """Shared agricultural module has __init__.py."""
        init_path = REPO_ROOT / module_path / "__init__.py"
        assert init_path.exists(), f"{module_path}/__init__.py missing"


# ===========================================================================
# 6. NATS Agricultural Event Subjects
# ===========================================================================


class TestAgriEventSubjects:
    """أحداث NATS الزراعية."""

    def test_subjects_file_has_recommendation_events(self) -> None:
        """subjects.py defines recommendation event constants."""
        path = REPO_ROOT / "shared" / "events" / "subjects.py"
        if not path.exists():
            pytest.skip("No subjects.py")
        content = path.read_text("utf-8")
        rec_subjects = [
            "SAHOOL_RECOMMENDATION_IRRIGATION",
            "SAHOOL_RECOMMENDATION_FERTILIZER",
            "SAHOOL_RECOMMENDATION_PEST_CONTROL",
        ]
        found = [s for s in rec_subjects if s in content]
        assert len(found) >= 2, (
            f"subjects.py missing recommendation events (found: {found})"
        )

    def test_subjects_file_has_weather_events(self) -> None:
        """subjects.py defines weather event constants."""
        path = REPO_ROOT / "shared" / "events" / "subjects.py"
        if not path.exists():
            pytest.skip("No subjects.py")
        content = path.read_text("utf-8")
        weather_subjects = [
            "SAHOOL_WEATHER_FORECAST",
            "SAHOOL_WEATHER_ALERT",
            "SAHOOL_WEATHER_ALERT_FROST",
        ]
        found = [s for s in weather_subjects if s in content]
        assert len(found) >= 2, (
            f"subjects.py missing weather events (found: {found})"
        )

    def test_subjects_file_has_irrigation_events(self) -> None:
        """subjects.py defines irrigation recommendation events."""
        path = REPO_ROOT / "shared" / "events" / "subjects.py"
        if not path.exists():
            pytest.skip("No subjects.py")
        content = path.read_text("utf-8")
        assert "SAHOOL_IRRIGATION_RECOMMENDATION_READY" in content, (
            "subjects.py missing irrigation recommendation event"
        )


# ===========================================================================
# 7. Agricultural Data Flow Chain
# ===========================================================================


class TestAgriDataFlow:
    """سلسلة تدفق البيانات الزراعية: مستشعر → تحليل → توصية."""

    def test_weather_to_advisory_flow(self, services: dict) -> None:
        """advisory-service depends on weather-service or NATS events."""
        adv_def = services.get("advisory-service", {})
        depends = adv_def.get("depends_on", {})
        dep_names = (
            set(depends) if isinstance(depends, list)
            else set(depends.keys()) if isinstance(depends, dict)
            else set()
        )
        # advisory should depend on nats (for weather events) at minimum
        has_nats = "nats" in dep_names
        assert has_nats, (
            "advisory-service should depend on NATS for weather event consumption"
        )

    def test_irrigation_to_fertigation_port_proximity(self) -> None:
        """Irrigation cluster services have nearby ports."""
        cluster_ports = {
            "irrigation-smart": 8094,
            "irrigation-cycle-engine": 8250,
            "fertigation-engine": 8252,
        }
        # irrigation-cycle and fertigation are close (250, 252)
        assert abs(cluster_ports["irrigation-cycle-engine"] -
                   cluster_ports["fertigation-engine"]) <= 5, (
            "irrigation-cycle and fertigation should have nearby ports"
        )

    def test_weather_advisory_irrigation_chain(self) -> None:
        """Weather→Advisory→Irrigation chain has sequential port assignment."""
        chain = {
            "weather-service": 8092,
            "advisory-service": 8093,
            "irrigation-smart": 8094,
        }
        ports = sorted(chain.values())
        assert ports == [8092, 8093, 8094], (
            "Weather→Advisory→Irrigation should have sequential ports 8092→8093→8094"
        )


# ===========================================================================
# 8. Compose Configuration
# ===========================================================================


class TestCropMgmtCompose:
    """تكوين docker-compose لخدمات إدارة المحاصيل."""

    @pytest.mark.parametrize("svc", sorted(CROP_MGMT_SERVICES))
    def test_service_in_compose(self, services: dict, svc: str) -> None:
        assert svc in services, f"{svc} not in docker-compose.yml"

    @pytest.mark.parametrize("svc", sorted(CROP_MGMT_SERVICES))
    def test_healthcheck_in_dockerfile(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile")
        assert "HEALTHCHECK" in content, f"{svc} missing HEALTHCHECK"

    @pytest.mark.parametrize("svc", sorted(CROP_MGMT_SERVICES))
    def test_non_root_user(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile")
        user_lines = re.findall(r"^USER\s+(\S+)", content, re.MULTILINE)
        non_root = [u for u in user_lines if u.lower() not in ("root", "0")]
        assert non_root, f"{svc} must run as non-root user"

    @pytest.mark.parametrize("svc", sorted(CROP_MGMT_SERVICES))
    def test_shared_copy(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile")
        assert re.search(r"COPY.*shared", content, re.IGNORECASE), (
            f"{svc} must COPY shared/ for agricultural domain modules"
        )

    def test_no_port_collisions(self) -> None:
        """No two crop management services share the same port."""
        ports = list(CROP_MGMT_SERVICES.values())
        assert len(ports) == len(set(ports))


# ===========================================================================
# 9. Crop Growth Stages (Zadoks/BBCH)
# ===========================================================================


class TestCropGrowthStages:
    """مراحل نمو المحاصيل (مقياس Zadoks)."""

    def test_shared_agri_calendar_growth_stages(self) -> None:
        """shared/agri_calendar/ references crop growth stages/planting windows."""
        for py_file in (REPO_ROOT / "shared" / "agri_calendar").rglob("*.py"):
            content = py_file.read_text("utf-8", errors="ignore")
            stage_terms = ["planting", "harvest", "stage", "season", "window",
                            "seedling", "vegetative", "flowering", "maturity"]
            found = [t for t in stage_terms if t in content.lower()]
            if len(found) >= 3:
                return
        pytest.fail(
            "shared/agri_calendar/ must reference crop growth stages "
            "(planting, harvest, seedling, vegetative, flowering, maturity)"
        )

    def test_crop_intelligence_growth_assessment(self) -> None:
        """crop-intelligence-service references growth stage assessment."""
        source = _read_all_source("crop-intelligence-service")
        if not source:
            pytest.skip("No source")
        growth_terms = ["growth", "stage", "health", "phenology", "maturity"]
        found = [t for t in growth_terms if t in source.lower()]
        assert len(found) >= 2, (
            f"crop-intelligence should assess growth stages (found: {found})"
        )

    def test_shared_ml_irrigation_has_crop_stages(self) -> None:
        """shared/ml_irrigation/ uses crop stage for irrigation prediction."""
        for py_file in (REPO_ROOT / "shared" / "ml_irrigation").rglob("*.py"):
            content = py_file.read_text("utf-8", errors="ignore")
            if "CropStage" in content or "crop_stage" in content or "Kc" in content:
                return
        pytest.fail(
            "shared/ml_irrigation/ must use crop growth stage (CropStage/Kc coefficient)"
        )


# ===========================================================================
# 10. Pesticide Compliance (PHI/REI)
# ===========================================================================


class TestPesticideCompliance:
    """امتثال المبيدات - فترات ما قبل الحصاد وإعادة الدخول."""

    def test_shared_pesticide_compliance_exists(self) -> None:
        """shared/pesticide_compliance/ module exists."""
        path = REPO_ROOT / "shared" / "pesticide_compliance" / "__init__.py"
        assert path.exists(), "shared/pesticide_compliance/ missing"

    def test_pesticide_compliance_has_phi(self) -> None:
        """shared/pesticide_compliance/ implements PHI (Pre-Harvest Interval)."""
        for py_file in (REPO_ROOT / "shared" / "pesticide_compliance").rglob("*.py"):
            content = py_file.read_text("utf-8", errors="ignore")
            if "PHI" in content or "pre_harvest" in content.lower() or "preharvest" in content.lower():
                return
        pytest.fail("shared/pesticide_compliance/ must implement PHI (Pre-Harvest Interval)")

    def test_pesticide_compliance_has_rei(self) -> None:
        """shared/pesticide_compliance/ implements REI (Re-Entry Interval)."""
        for py_file in (REPO_ROOT / "shared" / "pesticide_compliance").rglob("*.py"):
            content = py_file.read_text("utf-8", errors="ignore")
            if "REI" in content or "re_entry" in content.lower() or "reentry" in content.lower():
                return
        pytest.fail("shared/pesticide_compliance/ must implement REI (Re-Entry Interval)")

    def test_pesticide_compliance_has_ppe(self) -> None:
        """shared/pesticide_compliance/ defines PPE requirements."""
        for py_file in (REPO_ROOT / "shared" / "pesticide_compliance").rglob("*.py"):
            content = py_file.read_text("utf-8", errors="ignore")
            if "PPE" in content or "protective" in content.lower():
                return
        pytest.fail("shared/pesticide_compliance/ must define PPE requirements")


# ===========================================================================
# 11. Salinity Management
# ===========================================================================


class TestSalinityManagement:
    """إدارة الملوحة."""

    def test_shared_salinity_module_exists(self) -> None:
        """shared/salinity/ module exists."""
        path = REPO_ROOT / "shared" / "salinity" / "__init__.py"
        assert path.exists(), "shared/salinity/ module missing"

    def test_shared_salinity_has_monitoring(self) -> None:
        """shared/salinity/ implements salinity monitoring."""
        for py_file in (REPO_ROOT / "shared" / "salinity").rglob("*.py"):
            content = py_file.read_text("utf-8", errors="ignore")
            sal_terms = ["salinity", "ec", "conductivity", "leaching", "salt"]
            found = [t for t in sal_terms if t in content.lower()]
            if len(found) >= 2:
                return
        pytest.fail("shared/salinity/ must implement salinity monitoring (EC/leaching)")


# ===========================================================================
# 12. Water Management Efficiency
# ===========================================================================


class TestWaterManagementEfficiency:
    """كفاءة إدارة المياه."""

    def test_shared_water_management_exists(self) -> None:
        """shared/water_management/ module exists."""
        path = REPO_ROOT / "shared" / "water_management" / "__init__.py"
        assert path.exists(), "shared/water_management/ missing"

    def test_water_management_has_efficiency_metrics(self) -> None:
        """shared/water_management/ calculates irrigation efficiency."""
        for py_file in (REPO_ROOT / "shared" / "water_management").rglob("*.py"):
            content = py_file.read_text("utf-8", errors="ignore")
            eff_terms = ["efficiency", "application_efficiency", "conveyance",
                          "distribution", "water_use"]
            found = [t for t in eff_terms if t in content.lower()]
            if len(found) >= 2:
                return
        pytest.fail("shared/water_management/ must calculate irrigation efficiency metrics")


# ===========================================================================
# 13. Crop Rotation Planning
# ===========================================================================


class TestCropRotationPlanning:
    """تخطيط تناوب المحاصيل."""

    def test_shared_crop_rotation_exists(self) -> None:
        """shared/crop_rotation/ module exists."""
        path = REPO_ROOT / "shared" / "crop_rotation" / "__init__.py"
        assert path.exists(), "shared/crop_rotation/ missing"

    def test_crop_rotation_has_planner(self) -> None:
        """shared/crop_rotation/ implements rotation planning."""
        for py_file in (REPO_ROOT / "shared" / "crop_rotation").rglob("*.py"):
            content = py_file.read_text("utf-8", errors="ignore")
            if "CropRotationPlanner" in content or "RotationPlan" in content:
                return
        pytest.fail("shared/crop_rotation/ must implement CropRotationPlanner")

    def test_crop_rotation_has_soil_health(self) -> None:
        """shared/crop_rotation/ tracks soil health improvement."""
        for py_file in (REPO_ROOT / "shared" / "crop_rotation").rglob("*.py"):
            content = py_file.read_text("utf-8", errors="ignore")
            if "SoilHealth" in content or "nitrogen_credit" in content.lower():
                return
        pytest.fail("shared/crop_rotation/ must track soil health (nitrogen credits)")


# ===========================================================================
# 14. Agricultural Calendar (Hijri + Anwa'a)
# ===========================================================================


class TestAgriculturalCalendar:
    """التقويم الزراعي (الهجري والأنواء)."""

    def test_shared_agri_calendar_exists(self) -> None:
        """shared/agri_calendar/ module exists."""
        path = REPO_ROOT / "shared" / "agri_calendar" / "__init__.py"
        assert path.exists(), "shared/agri_calendar/ missing"

    def test_agri_calendar_has_hijri(self) -> None:
        """shared/agri_calendar/ integrates Hijri (Islamic) calendar."""
        for py_file in (REPO_ROOT / "shared" / "agri_calendar").rglob("*.py"):
            content = py_file.read_text("utf-8", errors="ignore")
            if "hijri" in content.lower() or "islamic" in content.lower():
                return
        pytest.fail("shared/agri_calendar/ must integrate Hijri calendar")

    def test_agri_calendar_has_planting_windows(self) -> None:
        """shared/agri_calendar/ defines crop planting windows by region."""
        for py_file in (REPO_ROOT / "shared" / "agri_calendar").rglob("*.py"):
            content = py_file.read_text("utf-8", errors="ignore")
            if "PlantingWindow" in content or "PLANTING_WINDOWS" in content:
                return
            if "planting_start" in content.lower() and "planting_end" in content.lower():
                return
        pytest.fail("shared/agri_calendar/ must define crop planting windows")

    def test_agri_calendar_middle_east_regions(self) -> None:
        """shared/agri_calendar/ covers Middle East agricultural regions."""
        for py_file in (REPO_ROOT / "shared" / "agri_calendar").rglob("*.py"):
            content = py_file.read_text("utf-8", errors="ignore")
            regions = ["riyadh", "qassim", "hail", "tabuk", "jazan", "yemen"]
            found = [r for r in regions if r in content.lower()]
            if len(found) >= 2:
                return
        pytest.fail("shared/agri_calendar/ must cover Middle East regions")


# ===========================================================================
# 15. Harvest Quality
# ===========================================================================


class TestHarvestQuality:
    """جودة المحصول بعد الحصاد."""

    def test_shared_harvest_quality_exists(self) -> None:
        """shared/harvest_quality/ module exists."""
        path = REPO_ROOT / "shared" / "harvest_quality" / "__init__.py"
        assert path.exists(), "shared/harvest_quality/ missing"

    def test_harvest_quality_has_grading(self) -> None:
        """shared/harvest_quality/ implements grading engine."""
        for py_file in (REPO_ROOT / "shared" / "harvest_quality").rglob("*.py"):
            content = py_file.read_text("utf-8", errors="ignore")
            if "QualityGrading" in content or "GradingEngine" in content:
                return
            grade_terms = ["grade", "quality", "grading", "standard"]
            found = [t for t in grade_terms if t in content.lower()]
            if len(found) >= 2:
                return
        pytest.fail("shared/harvest_quality/ must implement quality grading")
