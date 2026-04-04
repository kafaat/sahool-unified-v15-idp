"""
SAHOOL Agricultural Services E2E Tests
اختبارات التكامل الشاملة للخدمات الزراعية

Tests 12 agricultural services + 2 full workflow scenarios.
"""

from __future__ import annotations

import time
import uuid

import httpx
import pytest

# Imports via package (conftest adds project root to sys.path)
from .mock_services import start_all_servers
from .mock_agri_services import start_all_agri_servers

# Service URLs
ADVISORY = "http://127.0.0.1:8093"
IRRIGATION = "http://127.0.0.1:8094"
CROP_INTEL = "http://127.0.0.1:8095"
INDICATORS = "http://127.0.0.1:8091"
EQUIPMENT = "http://127.0.0.1:8101"
TASK = "http://127.0.0.1:8103"
NOTIFICATION = "http://127.0.0.1:8110"
ALERT = "http://127.0.0.1:8113"
SOIL = "http://127.0.0.1:8134"
PEST = "http://127.0.0.1:8125"
AI_ADVISOR = "http://127.0.0.1:8112"
INVENTORY = "http://127.0.0.1:8116"
# Core services (for workflows)
USER = "http://127.0.0.1:3025"
FIELD = "http://127.0.0.1:3000"
VEGETATION = "http://127.0.0.1:8090"

YEMEN_BOUNDARY = [[44.19, 15.35], [44.22, 15.35], [44.22, 15.37], [44.19, 15.37], [44.19, 15.35]]


def _wait_for_service(base_url: str, timeout: float = 30.0, interval: float = 0.25) -> None:
    deadline = time.time() + timeout
    health_url = f"{base_url}/healthz"
    while time.time() < deadline:
        try:
            response = httpx.get(health_url, timeout=2.0)
            if response.status_code == 200:
                return
        except httpx.HTTPError:
            pass
        time.sleep(interval)
    raise RuntimeError(f"Service did not become ready within {timeout}s: {health_url}")


@pytest.fixture(scope="session", autouse=True)
def all_servers():
    start_all_servers()
    start_all_agri_servers()
    # Verify all services are ready (start_all_agri_servers already polls, but belt-and-suspenders)
    for service_url in (ADVISORY, IRRIGATION, CROP_INTEL, INDICATORS, EQUIPMENT,
                        TASK, NOTIFICATION, ALERT, SOIL, PEST, AI_ADVISOR, INVENTORY,
                        USER, FIELD, VEGETATION):
        _wait_for_service(service_url)
    yield


@pytest.fixture
def client():
    with httpx.Client(timeout=10.0) as c:
        yield c


def _get_token(client):
    email = f"agri_{uuid.uuid4().hex[:6]}@test.com"
    reg = client.post(f"{USER}/api/v1/auth/register",
                      json={"email": email, "password": "Pass123!", "firstName": "T", "lastName": "U"})
    assert reg.status_code in (200, 201), f"Registration failed: {reg.status_code}"
    return reg.json()["access_token"]


# ═══════════════════════════════════════════════════════════════════════════════
# Health checks (12 tests)
# ═══════════════════════════════════════════════════════════════════════════════


class TestAgriServiceHealth:
    @pytest.mark.parametrize("url,name", [
        (ADVISORY, "advisory-service"), (IRRIGATION, "irrigation-smart"),
        (CROP_INTEL, "crop-intelligence-service"), (INDICATORS, "indicators-service"),
        (EQUIPMENT, "equipment-service"), (TASK, "task-service"),
        (NOTIFICATION, "notification-service"), (ALERT, "alert-service"),
        (SOIL, "soil-analysis-service"), (PEST, "pest-detection-service"),
        (AI_ADVISOR, "ai-advisor"), (INVENTORY, "inventory-service"),
    ])
    def test_health(self, client, url, name):
        r = client.get(f"{url}/healthz")
        assert r.status_code == 200
        assert r.json()["service"] == name


# ═══════════════════════════════════════════════════════════════════════════════
# Advisory Service (7 tests)
# ═══════════════════════════════════════════════════════════════════════════════


class TestAdvisoryService:
    def test_assess_disease(self, client):
        r = client.post(f"{ADVISORY}/api/v1/disease/assess", json={"crop": "wheat", "symptoms": ["yellowing"]})
        assert r.status_code == 200
        d = r.json()
        assert "disease_name" in d and "disease_name_ar" in d
        assert 0 < d["confidence"] <= 1
        assert d["severity"] in ("low", "medium", "high")

    def test_diseases_by_crop(self, client):
        r = client.get(f"{ADVISORY}/api/v1/disease/crop/wheat")
        assert r.status_code == 200
        assert len(r.json()["diseases"]) > 0

    def test_fertilizer_plan(self, client):
        r = client.post(f"{ADVISORY}/api/v1/fertilizer/plan", json={"crop": "wheat", "soil_n": 18})
        assert r.status_code == 200
        d = r.json()
        assert "nutrients_needed" in d and "products" in d
        assert d["nutrients_needed"]["nitrogen_kg"] > 0

    def test_list_crops(self, client):
        r = client.get(f"{ADVISORY}/api/v1/crops")
        assert r.status_code == 200
        crops = r.json()["crops"]
        assert any(c["name_ar"] == "قمح" for c in crops)

    def test_crop_details(self, client):
        r = client.get(f"{ADVISORY}/api/v1/crops/wheat")
        assert r.status_code == 200
        d = r.json()
        assert "stages" in d and "requirements" in d

    def test_crop_varieties(self, client):
        r = client.get(f"{ADVISORY}/api/v1/crops/wheat/varieties")
        assert r.status_code == 200
        assert len(r.json()["varieties"]) > 0

    def test_crop_not_found(self, client):
        r = client.get(f"{ADVISORY}/api/v1/crops/unknown_crop")
        assert r.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# Irrigation Smart (5 tests)
# ═══════════════════════════════════════════════════════════════════════════════


class TestIrrigationSmart:
    def test_calculate(self, client):
        r = client.post(f"{IRRIGATION}/v1/calculate", json={"crop": "wheat", "et0": 5.5})
        assert r.status_code == 200
        d = r.json()
        assert d["recommended_mm"] > 0
        assert d["duration_hours"] > 0
        assert 0 < d["efficiency"] <= 1

    def test_methods(self, client):
        r = client.get(f"{IRRIGATION}/v1/methods")
        methods = r.json()["methods"]
        assert any(m["id"] == "drip" for m in methods)
        assert any(m["name_ar"] == "تنقيط" for m in methods)

    def test_water_balance(self, client):
        r = client.get(f"{IRRIGATION}/v1/water-balance/{uuid.uuid4()}")
        assert r.status_code == 200
        assert "deficit_mm" in r.json() and "et0" in r.json()

    def test_efficiency(self, client):
        r = client.get(f"{IRRIGATION}/v1/efficiency-report/{uuid.uuid4()}")
        assert r.status_code == 200
        assert r.json()["efficiency_pct"] > 0

    def test_crop_coefficients(self, client):
        r = client.get(f"{IRRIGATION}/v1/crops")
        crops = r.json()["crops"]
        assert any(c["code"] == "wheat" and c["kc"] > 0 for c in crops)


# ═══════════════════════════════════════════════════════════════════════════════
# Crop Intelligence (6 tests)
# ═══════════════════════════════════════════════════════════════════════════════


class TestCropIntelligence:
    def test_diagnose(self, client):
        r = client.post(f"{CROP_INTEL}/api/v1/diagnose", json={"field_id": str(uuid.uuid4())})
        assert r.status_code == 200
        assert "diagnosis" in r.json() and "confidence" in r.json()

    def test_disease_detect(self, client):
        r = client.post(f"{CROP_INTEL}/api/v1/disease/detect", json={"image_data": "base64..."})
        assert r.status_code == 200
        assert len(r.json()["detected_diseases"]) > 0

    def test_yield_predict(self, client):
        r = client.post(f"{CROP_INTEL}/api/v1/yield/predict", json={"field_id": str(uuid.uuid4()), "crop": "wheat"})
        d = r.json()
        assert d["predicted_yield_tons"] > 0 and d["confidence"] > 0

    def test_nutrient_detect(self, client):
        r = client.post(f"{CROP_INTEL}/api/v1/nutrients/detect", json={"field_id": str(uuid.uuid4())})
        assert len(r.json()["deficiencies"]) > 0

    def test_disease_types(self, client):
        r = client.get(f"{CROP_INTEL}/api/v1/disease/types")
        assert len(r.json()["types"]) > 0

    def test_field_diagnosis(self, client):
        r = client.get(f"{CROP_INTEL}/api/v1/fields/{uuid.uuid4()}/diagnosis")
        assert r.status_code == 200


# ═══════════════════════════════════════════════════════════════════════════════
# Indicators (5 tests)
# ═══════════════════════════════════════════════════════════════════════════════


class TestIndicators:
    def test_definitions(self, client):
        r = client.get(f"{INDICATORS}/v1/indicators/definitions")
        inds = r.json()["indicators"]
        assert any(i["id"] == "ndvi" for i in inds)

    def test_field_indicators(self, client):
        r = client.get(f"{INDICATORS}/v1/field/{uuid.uuid4()}/indicators")
        assert "ndvi" in r.json()["indicators"]

    def test_dashboard(self, client):
        r = client.get(f"{INDICATORS}/v1/dashboard/{uuid.uuid4()}")
        assert r.json()["total_fields"] > 0

    def test_alerts(self, client):
        r = client.get(f"{INDICATORS}/v1/alerts/{uuid.uuid4()}")
        assert "alerts" in r.json()

    def test_trends(self, client):
        r = client.get(f"{INDICATORS}/v1/trends/{uuid.uuid4()}/ndvi")
        assert len(r.json()["data"]) > 0


# ═══════════════════════════════════════════════════════════════════════════════
# Equipment (5 tests)
# ═══════════════════════════════════════════════════════════════════════════════


class TestEquipment:
    def test_create(self, client):
        r = client.post(f"{EQUIPMENT}/api/v1/equipment", json={"name": "Tractor A", "type": "tractor"})
        assert r.status_code == 201
        assert r.json()["status"] == "operational"

    def test_list(self, client):
        client.post(f"{EQUIPMENT}/api/v1/equipment", json={"name": "Sprayer", "type": "sprayer"})
        r = client.get(f"{EQUIPMENT}/api/v1/equipment")
        assert r.json()["total"] >= 1

    def test_stats(self, client):
        r = client.get(f"{EQUIPMENT}/api/v1/equipment/stats")
        assert "total" in r.json() and "active" in r.json()

    def test_detail(self, client):
        c = client.post(f"{EQUIPMENT}/api/v1/equipment", json={"name": "Drone", "type": "drone"})
        eid = c.json()["id"]
        r = client.get(f"{EQUIPMENT}/api/v1/equipment/{eid}")
        assert r.json()["id"] == eid

    def test_maintenance(self, client):
        c = client.post(f"{EQUIPMENT}/api/v1/equipment", json={"name": "Pump", "type": "pump"})
        r = client.get(f"{EQUIPMENT}/api/v1/equipment/{c.json()['id']}/maintenance")
        assert "records" in r.json()


# ═══════════════════════════════════════════════════════════════════════════════
# Task Service (4 tests)
# ═══════════════════════════════════════════════════════════════════════════════


class TestTaskService:
    def test_from_ndvi(self, client):
        r = client.post(f"{TASK}/api/v1/tasks/from-ndvi-alert", json={"field_id": str(uuid.uuid4()), "ndvi": 0.15})
        assert r.status_code == 200
        assert r.json()["type"] == "ndvi_alert"

    def test_suggestions(self, client):
        r = client.get(f"{TASK}/api/v1/tasks/suggest-for-field/{uuid.uuid4()}")
        assert len(r.json()["suggestions"]) > 0

    def test_auto_create(self, client):
        r = client.post(f"{TASK}/api/v1/tasks/auto-create", json={"field_id": str(uuid.uuid4())})
        assert r.json()["tasks_created"] >= 1


# ═══════════════════════════════════════════════════════════════════════════════
# Notification (5 tests)
# ═══════════════════════════════════════════════════════════════════════════════


class TestNotification:
    def test_send(self, client):
        fid = str(uuid.uuid4())
        r = client.post(f"{NOTIFICATION}/", json={"farmer_id": fid, "message": "Test", "type": "general"})
        assert r.json()["status"] == "delivered"

    def test_weather_alert(self, client):
        r = client.post(f"{NOTIFICATION}/weather", json={"message": "Storm warning"})
        assert r.json()["type"] == "weather"

    def test_pest_alert(self, client):
        r = client.post(f"{NOTIFICATION}/pest", json={"pest": "locust"})
        assert r.json()["type"] == "pest"

    def test_farmer_notifications(self, client):
        fid = str(uuid.uuid4())
        client.post(f"{NOTIFICATION}/", json={"farmer_id": fid, "message": "Hi"})
        r = client.get(f"{NOTIFICATION}/farmer/{fid}")
        assert r.json()["total"] >= 1

    def test_stats(self, client):
        r = client.get(f"{NOTIFICATION}/stats")
        assert r.json()["total_sent"] >= 0


# ═══════════════════════════════════════════════════════════════════════════════
# Alert (6 tests)
# ═══════════════════════════════════════════════════════════════════════════════


class TestAlert:
    def test_create(self, client):
        r = client.post(f"{ALERT}/alerts", json={"type": "ndvi_low", "severity": "high",
                                                   "field_id": str(uuid.uuid4()), "message": "Low NDVI"})
        assert r.status_code == 201
        assert r.json()["status"] == "active"

    def test_field_alerts(self, client):
        fid = str(uuid.uuid4())
        client.post(f"{ALERT}/alerts", json={"type": "pest", "field_id": fid, "message": "Pest detected"})
        r = client.get(f"{ALERT}/alerts/field/{fid}")
        assert len(r.json()["alerts"]) >= 1

    def test_resolve(self, client):
        c = client.post(f"{ALERT}/alerts", json={"type": "weather", "message": "Storm"})
        aid = c.json()["id"]
        r = client.post(f"{ALERT}/alerts/{aid}/resolve")
        assert r.json()["status"] == "resolved"

    def test_create_rule(self, client):
        r = client.post(f"{ALERT}/alerts/rules", json={"name": "Low NDVI rule", "condition": {"ndvi_lt": 0.2}})
        assert r.status_code == 201

    def test_list_rules(self, client):
        client.post(f"{ALERT}/alerts/rules", json={"name": "Test rule"})
        r = client.get(f"{ALERT}/alerts/rules")
        assert len(r.json()["rules"]) >= 1

    def test_stats(self, client):
        r = client.get(f"{ALERT}/alerts/stats")
        assert "total" in r.json() and "active" in r.json()


# ═══════════════════════════════════════════════════════════════════════════════
# Soil Analysis (6 tests)
# ═══════════════════════════════════════════════════════════════════════════════


class TestSoilAnalysis:
    def test_create_test(self, client):
        r = client.post(f"{SOIL}/v1/tests", json={"field_id": str(uuid.uuid4()), "ph": 7.2, "nitrogen_ppm": 22})
        assert r.status_code == 201
        assert r.json()["ph"] == 7.2

    def test_get_test(self, client):
        c = client.post(f"{SOIL}/v1/tests", json={"field_id": str(uuid.uuid4()), "ph": 6.8})
        r = client.get(f"{SOIL}/v1/tests/{c.json()['id']}")
        assert r.json()["ph"] == 6.8

    def test_field_tests(self, client):
        fid = str(uuid.uuid4())
        client.post(f"{SOIL}/v1/tests", json={"field_id": fid, "ph": 7.0})
        r = client.get(f"{SOIL}/v1/tests/field/{fid}")
        assert len(r.json()["tests"]) >= 1

    def test_interpret(self, client):
        r = client.post(f"{SOIL}/v1/interpret", json={"ph": 7.2, "nitrogen_ppm": 22})
        d = r.json()
        assert d["status"] in ("good", "needs_attention")
        assert "recommendations" in d

    def test_amendment_plan(self, client):
        r = client.post(f"{SOIL}/v1/recommendations/amendment-plan", json={"field_id": str(uuid.uuid4())})
        assert len(r.json()["amendments"]) > 0
        assert r.json()["estimated_cost_sar"] > 0

    def test_crop_requirements(self, client):
        r = client.get(f"{SOIL}/v1/crops/wheat/requirements")
        assert r.json()["nitrogen_min_ppm"] > 0


# ═══════════════════════════════════════════════════════════════════════════════
# Pest Detection (6 tests)
# ═══════════════════════════════════════════════════════════════════════════════


class TestPestDetection:
    def test_list_pests(self, client):
        r = client.get(f"{PEST}/v1/pests")
        pests = r.json()["pests"]
        assert any(p["name_ar"] == "سوسة النخيل الحمراء" for p in pests)

    def test_pests_by_crop(self, client):
        r = client.get(f"{PEST}/v1/pests/crop/date_palm")
        assert any(p["id"] == "rpw" for p in r.json()["pests"])

    def test_identify(self, client):
        r = client.post(f"{PEST}/v1/pests/identify", json={"symptoms": ["holes in trunk"]})
        assert "pest_id" in r.json() and r.json()["confidence"] > 0

    def test_treatment(self, client):
        r = client.post(f"{PEST}/v1/treatments/recommend", json={"pest_id": "rpw"})
        assert len(r.json()["treatments"]) > 0

    def test_threshold_exceeded(self, client):
        r = client.post(f"{PEST}/v1/thresholds/assess", json={"pest_count": 15, "threshold": 10})
        assert r.json()["exceeded"] is True
        assert r.json()["action_required"] is True

    def test_threshold_safe(self, client):
        r = client.post(f"{PEST}/v1/thresholds/assess", json={"pest_count": 3, "threshold": 10})
        assert r.json()["exceeded"] is False


# ═══════════════════════════════════════════════════════════════════════════════
# AI Advisor (5 tests)
# ═══════════════════════════════════════════════════════════════════════════════


class TestAIAdvisor:
    def test_ask(self, client):
        r = client.post(f"{AI_ADVISOR}/v1/advisor/ask", json={"question": "متى أسقي القمح؟"})
        assert "answer" in r.json() and "answer_ar" in r.json()

    def test_diagnose(self, client):
        r = client.post(f"{AI_ADVISOR}/v1/advisor/diagnose", json={"field_id": str(uuid.uuid4())})
        assert "diagnosis" in r.json()

    def test_recommend(self, client):
        r = client.post(f"{AI_ADVISOR}/v1/advisor/recommend", json={"field_id": str(uuid.uuid4())})
        assert len(r.json()["recommendations"]) > 0

    def test_analyze_field(self, client):
        r = client.post(f"{AI_ADVISOR}/v1/advisor/analyze-field", json={"field_id": str(uuid.uuid4())})
        assert r.json()["health_score"] > 0

    def test_agents(self, client):
        r = client.get(f"{AI_ADVISOR}/v1/advisor/agents")
        agents = r.json()["agents"]
        assert any(a["id"] == "crop_advisor" for a in agents)


# ═══════════════════════════════════════════════════════════════════════════════
# Inventory (4 tests)
# ═══════════════════════════════════════════════════════════════════════════════


class TestInventory:
    def test_dashboard(self, client):
        r = client.get(f"{INVENTORY}/v1/analytics/dashboard")
        assert r.json()["total_items"] > 0

    def test_reorder(self, client):
        r = client.get(f"{INVENTORY}/v1/analytics/reorder-recommendations")
        assert len(r.json()["recommendations"]) > 0

    def test_abc(self, client):
        r = client.get(f"{INVENTORY}/v1/analytics/abc-analysis")
        cats = r.json()["analysis"]
        assert any(c["category"] == "A" for c in cats)

    def test_create_category(self, client):
        r = client.post(f"{INVENTORY}/v1/categories", json={"name": "Fertilizers", "name_ar": "أسمدة"})
        assert r.status_code == 201


# ═══════════════════════════════════════════════════════════════════════════════
# Full Workflow: Field → Advisory → Irrigation → Task (1 test)
# ═══════════════════════════════════════════════════════════════════════════════


class TestFullAgriculturalWorkflow:
    def test_field_to_advisory_workflow(self, client):
        """Create field → get NDVI → get advisory → get irrigation → create task."""
        token = _get_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create field
        field = client.post(f"{FIELD}/api/v1/fields", headers=headers,
                            json={"name": "Workflow Field", "cropType": "wheat", "coordinates": YEMEN_BOUNDARY})
        assert field.status_code == 201
        field_id = field.json()["id"]

        # 2. Get NDVI
        ndvi = client.post(f"{VEGETATION}/v1/analyze", json={"field_id": field_id, "analysis_type": "ndvi"})
        assert ndvi.status_code == 200

        # 3. Get advisory (disease assessment)
        advisory = client.post(f"{ADVISORY}/api/v1/disease/assess", json={"crop": "wheat"})
        assert advisory.status_code == 200

        # 4. Calculate irrigation
        irrigation = client.post(f"{IRRIGATION}/v1/calculate", json={"crop": "wheat", "et0": 5.5})
        assert irrigation.json()["recommended_mm"] > 0

        # 5. Create task from NDVI alert
        task = client.post(f"{TASK}/api/v1/tasks/from-ndvi-alert", json={"field_id": field_id, "ndvi": 0.15})
        assert task.json()["type"] == "ndvi_alert"

    def test_pest_to_treatment_workflow(self, client):
        """Detect pest → assess threshold → get treatment → create alert → notify."""
        # 1. Identify pest
        pest = client.post(f"{PEST}/v1/pests/identify", json={"symptoms": ["leaf damage"]})
        assert pest.status_code == 200
        pest_id = pest.json()["pest_id"]

        # 2. Assess threshold
        threshold = client.post(f"{PEST}/v1/thresholds/assess", json={"pest_count": 15, "threshold": 10})
        assert threshold.json()["exceeded"] is True

        # 3. Get treatment
        treatment = client.post(f"{PEST}/v1/treatments/recommend", json={"pest_id": pest_id})
        assert len(treatment.json()["treatments"]) > 0

        # 4. Create alert
        alert = client.post(f"{ALERT}/alerts",
                            json={"type": "pest", "severity": "high", "message": f"Pest {pest_id} detected"})
        assert alert.status_code == 201

        # 5. Notify farmer
        notif = client.post(f"{NOTIFICATION}/pest", json={"pest": pest_id})
        assert notif.json()["status"] == "delivered"
