"""
SAHOOL Agricultural Mock Services for E2E Testing
خوادم محاكاة الخدمات الزراعية لاختبارات التكامل

12 services: advisory, irrigation-smart, crop-intelligence, indicators,
equipment, task, notification, alert, soil-analysis, pest-detection,
ai-advisor, inventory.
"""

from __future__ import annotations

import random
import threading
import time
import uuid
from datetime import UTC, datetime, timedelta

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

# ═══════════════════════════════════════════════════════════════════════════════
# Shared data
# ═══════════════════════════════════════════════════════════════════════════════

CROPS = {
    "wheat": {"name_ar": "قمح", "kc": 1.15, "gdd_total": 2000},
    "barley": {"name_ar": "شعير", "kc": 1.10, "gdd_total": 1500},
    "date_palm": {"name_ar": "نخيل", "kc": 0.95, "gdd_total": 5000},
    "tomato": {"name_ar": "طماطم", "kc": 1.20, "gdd_total": 1200},
    "corn": {"name_ar": "ذرة", "kc": 1.20, "gdd_total": 2500},
    "cucumber": {"name_ar": "خيار", "kc": 1.00, "gdd_total": 1000},
}

DISEASES = [
    {"id": "wheat_rust", "name": "Wheat Rust", "name_ar": "صدأ القمح", "crop": "wheat", "severity": "high"},
    {"id": "blight", "name": "Late Blight", "name_ar": "اللفحة المتأخرة", "crop": "tomato", "severity": "high"},
    {"id": "fusarium", "name": "Fusarium Wilt", "name_ar": "ذبول الفيوزاريوم", "crop": "wheat", "severity": "medium"},
    {"id": "powdery_mildew", "name": "Powdery Mildew", "name_ar": "البياض الدقيقي", "crop": "cucumber", "severity": "medium"},
]

PESTS = [
    {"id": "rpw", "name": "Red Palm Weevil", "name_ar": "سوسة النخيل الحمراء", "crop": "date_palm", "quarantine": True},
    {"id": "whitefly", "name": "Whitefly", "name_ar": "الذبابة البيضاء", "crop": "tomato", "quarantine": False},
    {"id": "aphid", "name": "Aphid", "name_ar": "المن", "crop": "wheat", "quarantine": False},
    {"id": "locust", "name": "Desert Locust", "name_ar": "الجراد الصحراوي", "crop": "wheat", "quarantine": True},
]

EQUIPMENT_STORE: dict[str, dict] = {}
ALERT_STORE: dict[str, dict] = {}
ALERT_RULES: dict[str, dict] = {}
TASK_STORE: dict[str, dict] = {}
NOTIFICATION_STORE: list[dict] = []
SOIL_STORE: dict[str, dict] = {}
INVENTORY_STORE: dict[str, dict] = {}


def _ts():
    return datetime.now(UTC).isoformat()


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Advisory Service (8093)
# ═══════════════════════════════════════════════════════════════════════════════

advisory_app = FastAPI(title="Mock Advisory Service")
advisory_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@advisory_app.get("/healthz")
def adv_health():
    return {"status": "ok", "service": "advisory-service"}


@advisory_app.post("/api/v1/disease/assess")
async def adv_disease_assess(request: Request):
    await request.json()  # consume body
    d = random.choice(DISEASES)
    return {"disease_id": d["id"], "disease_name": d["name"], "disease_name_ar": d["name_ar"],
            "confidence": round(random.uniform(0.7, 0.98), 2), "severity": d["severity"],
            "treatment": f"Apply fungicide for {d['name']}", "treatment_ar": f"رش مبيد فطري لمكافحة {d['name_ar']}"}


@advisory_app.get("/api/v1/disease/crop/{crop}")
def adv_diseases_by_crop(crop: str):
    return {"crop": crop, "diseases": [d for d in DISEASES if d["crop"] == crop]}


@advisory_app.post("/api/v1/fertilizer/plan")
async def adv_fertilizer_plan(request: Request):
    body = await request.json()
    return {"crop": body.get("crop", "wheat"), "nutrients_needed": {"nitrogen_kg": 46, "phosphorus_kg": 20, "potassium_kg": 30},
            "products": [{"name": "Urea 46%", "name_ar": "يوريا 46%", "rate_kg_ha": 100}],
            "application_schedule": [{"stage": "tillering", "stage_ar": "التفريع", "day": 30}]}


@advisory_app.get("/api/v1/crops")
def adv_list_crops():
    return {"crops": [{"code": k, "name": k.replace("_", " ").title(), "name_ar": v["name_ar"]} for k, v in CROPS.items()]}


@advisory_app.get("/api/v1/crops/{crop_code}")
def adv_crop_detail(crop_code: str):
    c = CROPS.get(crop_code)
    if not c:
        raise HTTPException(404, "Crop not found")
    return {"code": crop_code, "name_ar": c["name_ar"], "kc": c["kc"], "gdd_total": c["gdd_total"],
            "stages": ["germination", "tillering", "heading", "ripening"],
            "requirements": {"water_mm": 450, "nitrogen_kg": 120, "temperature_min": 5, "temperature_max": 35}}


@advisory_app.get("/api/v1/crops/{crop_code}/varieties")
def adv_crop_varieties(crop_code: str):
    return {"crop": crop_code, "varieties": [
        {"name": f"{crop_code.title()} Var-1", "name_ar": "صنف 1", "yield_potential": "high"},
        {"name": f"{crop_code.title()} Var-2", "name_ar": "صنف 2", "yield_potential": "medium"},
    ]}


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Irrigation Smart (8094)
# ═══════════════════════════════════════════════════════════════════════════════

irrigation_app = FastAPI(title="Mock Irrigation Smart")
irrigation_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@irrigation_app.get("/healthz")
def irr_health():
    return {"status": "ok", "service": "irrigation-smart"}


@irrigation_app.get("/v1/crops")
def irr_crops():
    return {"crops": [{"code": k, "name_ar": v["name_ar"], "kc": v["kc"]} for k, v in CROPS.items()]}


@irrigation_app.get("/v1/methods")
def irr_methods():
    return {"methods": [
        {"id": "drip", "name": "Drip", "name_ar": "تنقيط", "efficiency": 0.92},
        {"id": "sprinkler", "name": "Sprinkler", "name_ar": "رشاش", "efficiency": 0.78},
        {"id": "flood", "name": "Flood", "name_ar": "غمر", "efficiency": 0.55},
        {"id": "pivot", "name": "Center Pivot", "name_ar": "محوري", "efficiency": 0.85},
    ]}


@irrigation_app.post("/v1/calculate")
async def irr_calculate(request: Request):
    body = await request.json()
    et0 = body.get("et0", 5.5)
    kc = CROPS.get(body.get("crop", "wheat"), {}).get("kc", 1.0)
    eff = 0.85
    mm = round(et0 * kc / eff, 1)
    return {"recommended_mm": mm, "duration_hours": round(mm / 8, 1), "frequency_days": 5,
            "efficiency": eff, "crop_kc": kc, "et0": et0}


@irrigation_app.get("/v1/water-balance/{field_id}")
def irr_water_balance(field_id: str):
    return {"field_id": field_id, "deficit_mm": round(random.uniform(5, 30), 1),
            "rainfall_mm": round(random.uniform(0, 10), 1), "et0": round(random.uniform(4, 7), 1),
            "irrigation_applied_mm": round(random.uniform(10, 25), 1), "soil_moisture_pct": round(random.uniform(25, 55), 1)}


@irrigation_app.get("/v1/efficiency-report/{field_id}")
def irr_efficiency(field_id: str):
    return {"field_id": field_id, "efficiency_pct": round(random.uniform(70, 95), 1),
            "water_saved_m3": round(random.uniform(50, 200), 0), "cost_saved_sar": round(random.uniform(100, 500), 0)}


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Crop Intelligence (8095)
# ═══════════════════════════════════════════════════════════════════════════════

crop_intel_app = FastAPI(title="Mock Crop Intelligence")
crop_intel_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@crop_intel_app.get("/healthz")
def ci_health():
    return {"status": "ok", "service": "crop-intelligence-service"}


@crop_intel_app.post("/api/v1/diagnose")
async def ci_diagnose(request: Request):
    await request.json()  # consume body
    d = random.choice(DISEASES)
    return {"diagnosis": d["name"], "diagnosis_ar": d["name_ar"], "confidence": round(random.uniform(0.75, 0.95), 2),
            "severity": d["severity"], "recommendations": [f"Apply treatment for {d['name']}", "Monitor for 7 days"]}


@crop_intel_app.post("/api/v1/disease/detect")
async def ci_disease_detect(request: Request):
    return {"detected_diseases": [{"name": d["name"], "name_ar": d["name_ar"], "severity": d["severity"],
                                    "confidence": round(random.uniform(0.6, 0.95), 2)} for d in random.sample(DISEASES, min(2, len(DISEASES)))]}


@crop_intel_app.get("/api/v1/disease/types")
def ci_disease_types():
    return {"types": [{"id": d["id"], "name": d["name"], "name_ar": d["name_ar"]} for d in DISEASES]}


@crop_intel_app.post("/api/v1/yield/predict")
async def ci_yield_predict(request: Request):
    await request.json()  # consume body
    return {"predicted_yield_tons": round(random.uniform(2.5, 6.0), 2), "confidence": round(random.uniform(0.7, 0.9), 2),
            "factors": {"soil_quality": "good", "irrigation": "adequate", "weather": "favorable"}}


@crop_intel_app.post("/api/v1/nutrients/detect")
async def ci_nutrients_detect(request: Request):
    return {"deficiencies": [
        {"nutrient": "nitrogen", "nutrient_ar": "نيتروجين", "severity": "medium", "level_ppm": 18},
        {"nutrient": "phosphorus", "nutrient_ar": "فوسفور", "severity": "low", "level_ppm": 22},
    ]}


@crop_intel_app.get("/api/v1/fields/{field_id}/diagnosis")
def ci_field_diagnosis(field_id: str):
    return {"field_id": field_id, "diagnoses": [
        {"date": _ts(), "type": "disease", "name": "Wheat Rust", "severity": "medium"},
    ]}


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Indicators Service (8091)
# ═══════════════════════════════════════════════════════════════════════════════

indicators_app = FastAPI(title="Mock Indicators Service")
indicators_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@indicators_app.get("/healthz")
def ind_health():
    return {"status": "ok", "service": "indicators-service"}


@indicators_app.get("/v1/indicators/definitions")
def ind_definitions():
    return {"indicators": [
        {"id": "ndvi", "name": "NDVI", "name_ar": "مؤشر الغطاء النباتي", "unit": "index", "range": [-1, 1]},
        {"id": "soil_moisture", "name": "Soil Moisture", "name_ar": "رطوبة التربة", "unit": "%", "range": [0, 100]},
        {"id": "temperature", "name": "Temperature", "name_ar": "درجة الحرارة", "unit": "°C", "range": [-10, 50]},
        {"id": "et0", "name": "ET0", "name_ar": "التبخر-نتح", "unit": "mm/day", "range": [0, 15]},
    ]}


@indicators_app.get("/v1/field/{field_id}/indicators")
def ind_field_indicators(field_id: str):
    return {"field_id": field_id, "indicators": {
        "ndvi": round(random.uniform(0.3, 0.85), 3), "soil_moisture": round(random.uniform(25, 60), 1),
        "temperature": round(random.uniform(20, 38), 1), "et0": round(random.uniform(3, 7), 1),
    }, "timestamp": _ts()}


@indicators_app.get("/v1/dashboard/{tenant_id}")
def ind_dashboard(tenant_id: str):
    return {"tenant_id": tenant_id, "total_fields": random.randint(5, 50),
            "avg_ndvi": round(random.uniform(0.4, 0.7), 2), "avg_health_score": round(random.uniform(60, 90), 1),
            "active_alerts": random.randint(0, 5), "timestamp": _ts()}


@indicators_app.get("/v1/alerts/{tenant_id}")
def ind_alerts(tenant_id: str):
    return {"tenant_id": tenant_id, "alerts": [
        {"type": "ndvi_low", "field_id": str(uuid.uuid4()), "value": 0.18, "threshold": 0.2, "message_ar": "مؤشر NDVI منخفض"},
    ]}


@indicators_app.get("/v1/trends/{field_id}/{indicator_id}")
def ind_trends(field_id: str, indicator_id: str):
    data = [{"date": (datetime.now(UTC) - timedelta(days=i)).strftime("%Y-%m-%d"),
             "value": round(random.uniform(0.3, 0.8), 3)} for i in range(30, 0, -5)]
    return {"field_id": field_id, "indicator": indicator_id, "data": data}


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Equipment Service (8101)
# ═══════════════════════════════════════════════════════════════════════════════

equipment_app = FastAPI(title="Mock Equipment Service")
equipment_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@equipment_app.get("/healthz")
def eq_health():
    return {"status": "ok", "service": "equipment-service"}


@equipment_app.get("/api/v1/equipment")
def eq_list():
    return {"data": list(EQUIPMENT_STORE.values()), "total": len(EQUIPMENT_STORE)}


@equipment_app.post("/api/v1/equipment", status_code=201)
async def eq_create(request: Request):
    body = await request.json()
    eid = str(uuid.uuid4())
    eq = {"id": eid, "name": body.get("name", "Equipment"), "type": body.get("type", "tractor"),
          "status": "operational", "created_at": _ts()}
    EQUIPMENT_STORE[eid] = eq
    return eq


@equipment_app.get("/api/v1/equipment/stats")
def eq_stats():
    items = list(EQUIPMENT_STORE.values())
    return {"total": len(items), "active": sum(1 for e in items if e.get("status") == "operational"),
            "maintenance_due": random.randint(0, 3)}


@equipment_app.get("/api/v1/equipment/{equipment_id}")
def eq_detail(equipment_id: str):
    eq = EQUIPMENT_STORE.get(equipment_id)
    if not eq:
        raise HTTPException(404, "Equipment not found")
    return eq


@equipment_app.get("/api/v1/equipment/{equipment_id}/maintenance")
def eq_maintenance(equipment_id: str):
    return {"equipment_id": equipment_id, "records": [
        {"date": _ts(), "type": "preventive", "description": "Oil change", "description_ar": "تغيير زيت"},
    ]}


# ═══════════════════════════════════════════════════════════════════════════════
# 6. Task Service (8103)
# ═══════════════════════════════════════════════════════════════════════════════

task_app = FastAPI(title="Mock Task Service")
task_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@task_app.get("/healthz")
def task_health():
    return {"status": "ok", "service": "task-service"}


@task_app.post("/api/v1/tasks/from-ndvi-alert")
async def task_from_ndvi(request: Request):
    body = await request.json()
    tid = str(uuid.uuid4())
    task = {"id": tid, "type": "ndvi_alert", "field_id": body.get("field_id"), "status": "pending",
            "title": "Investigate low NDVI", "title_ar": "فحص انخفاض NDVI", "created_at": _ts()}
    TASK_STORE[tid] = task
    return task


@task_app.get("/api/v1/tasks/suggest-for-field/{field_id}")
def task_suggestions(field_id: str):
    return {"field_id": field_id, "suggestions": [
        {"type": "irrigation", "title": "Schedule irrigation", "title_ar": "جدولة الري", "priority": "high"},
        {"type": "fertilizer", "title": "Apply nitrogen", "title_ar": "تطبيق النيتروجين", "priority": "medium"},
    ]}


@task_app.post("/api/v1/tasks/auto-create")
async def task_auto_create(request: Request):
    body = await request.json()
    tasks = []
    for s in ["irrigation", "scouting"]:
        tid = str(uuid.uuid4())
        t = {"id": tid, "type": s, "field_id": body.get("field_id"), "status": "pending", "created_at": _ts()}
        TASK_STORE[tid] = t
        tasks.append(t)
    return {"tasks_created": len(tasks), "tasks": tasks}


# ═══════════════════════════════════════════════════════════════════════════════
# 7. Notification Service (8110)
# ═══════════════════════════════════════════════════════════════════════════════

notification_app = FastAPI(title="Mock Notification Service")
notification_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@notification_app.get("/healthz")
def notif_health():
    return {"status": "ok", "service": "notification-service"}


@notification_app.post("/")
async def notif_send(request: Request):
    body = await request.json()
    n = {"id": str(uuid.uuid4()), "type": body.get("type", "general"), "farmer_id": body.get("farmer_id"),
         "message": body.get("message", ""), "status": "delivered", "created_at": _ts()}
    NOTIFICATION_STORE.append(n)
    return n


@notification_app.post("/weather")
async def notif_weather(request: Request):
    body = await request.json()
    n = {"id": str(uuid.uuid4()), "type": "weather", "message": body.get("message", "Weather alert"),
         "message_ar": "تنبيه طقس", "status": "delivered"}
    NOTIFICATION_STORE.append(n)
    return n


@notification_app.post("/pest")
async def notif_pest(request: Request):
    await request.json()  # consume body
    return {"id": str(uuid.uuid4()), "type": "pest", "status": "delivered", "message_ar": "تنبيه آفات"}


@notification_app.post("/irrigation")
async def notif_irrigation(request: Request):
    return {"id": str(uuid.uuid4()), "type": "irrigation", "status": "delivered", "message_ar": "تذكير ري"}


@notification_app.get("/farmer/{farmer_id}")
def notif_farmer(farmer_id: str):
    farmer_notifs = [n for n in NOTIFICATION_STORE if n.get("farmer_id") == farmer_id]
    return {"farmer_id": farmer_id, "notifications": farmer_notifs[-20:], "total": len(farmer_notifs)}


@notification_app.get("/stats")
def notif_stats():
    return {"total_sent": len(NOTIFICATION_STORE), "delivered": len(NOTIFICATION_STORE), "failed": 0}


# ═══════════════════════════════════════════════════════════════════════════════
# 8. Alert Service (8113)
# ═══════════════════════════════════════════════════════════════════════════════

alert_app = FastAPI(title="Mock Alert Service")
alert_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@alert_app.get("/healthz")
def alert_health():
    return {"status": "ok", "service": "alert-service"}


@alert_app.get("/alerts/stats")
def alert_stats():
    active = sum(1 for a in ALERT_STORE.values() if a.get("status") == "active")
    return {"total": len(ALERT_STORE), "active": active, "resolved": len(ALERT_STORE) - active}


@alert_app.post("/alerts", status_code=201)
async def alert_create(request: Request):
    body = await request.json()
    aid = str(uuid.uuid4())
    alert = {"id": aid, "type": body.get("type", "general"), "severity": body.get("severity", "medium"),
             "field_id": body.get("field_id"), "message": body.get("message", ""),
             "message_ar": body.get("message_ar", ""), "status": "active", "created_at": _ts()}
    ALERT_STORE[aid] = alert
    return alert


@alert_app.get("/alerts/field/{field_id}")
def alert_by_field(field_id: str):
    return {"alerts": [a for a in ALERT_STORE.values() if a.get("field_id") == field_id]}


@alert_app.post("/alerts/{alert_id}/resolve")
def alert_resolve(alert_id: str):
    alert = ALERT_STORE.get(alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")
    alert["status"] = "resolved"
    return alert


@alert_app.post("/alerts/rules", status_code=201)
async def alert_create_rule(request: Request):
    body = await request.json()
    rid = str(uuid.uuid4())
    rule = {"id": rid, "name": body.get("name", "Rule"), "condition": body.get("condition", {}),
            "severity": body.get("severity", "medium"), "enabled": True}
    ALERT_RULES[rid] = rule
    return rule


@alert_app.get("/alerts/rules")
def alert_list_rules():
    return {"rules": list(ALERT_RULES.values())}


# ═══════════════════════════════════════════════════════════════════════════════
# 9. Soil Analysis Service (8134)
# ═══════════════════════════════════════════════════════════════════════════════

soil_app = FastAPI(title="Mock Soil Analysis Service")
soil_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@soil_app.get("/healthz")
def soil_health():
    return {"status": "ok", "service": "soil-analysis-service"}


@soil_app.post("/v1/tests", status_code=201)
async def soil_create_test(request: Request):
    body = await request.json()
    sid = str(uuid.uuid4())
    test = {"id": sid, "field_id": body.get("field_id"), "ph": body.get("ph", 7.2),
            "nitrogen_ppm": body.get("nitrogen_ppm", 22), "phosphorus_ppm": body.get("phosphorus_ppm", 18),
            "potassium_ppm": body.get("potassium_ppm", 180), "ec": body.get("ec", 1.2),
            "organic_matter_pct": body.get("organic_matter_pct", 2.1), "status": "completed", "created_at": _ts()}
    SOIL_STORE[sid] = test
    return test


@soil_app.get("/v1/tests/{test_id}")
def soil_get_test(test_id: str):
    t = SOIL_STORE.get(test_id)
    if not t:
        raise HTTPException(404, "Soil test not found")
    return t


@soil_app.get("/v1/tests/field/{field_id}")
def soil_field_tests(field_id: str):
    return {"tests": [t for t in SOIL_STORE.values() if t.get("field_id") == field_id]}


@soil_app.post("/v1/interpret")
async def soil_interpret(request: Request):
    body = await request.json()
    ph = body.get("ph", 7.2)
    n = body.get("nitrogen_ppm", 22)
    status = "good" if 6.0 <= ph <= 7.5 and n >= 20 else "needs_attention"
    return {"status": status, "status_ar": "جيد" if status == "good" else "يحتاج اهتمام",
            "recommendations": [{"nutrient": "nitrogen", "action": "apply_urea" if n < 25 else "adequate", "action_ar": "إضافة يوريا" if n < 25 else "كافي"}],
            "ph_status": "optimal" if 6.0 <= ph <= 7.5 else "out_of_range"}


@soil_app.post("/v1/recommendations/amendment-plan")
async def soil_amendment(request: Request):
    return {"amendments": [
        {"product": "Urea 46%", "product_ar": "يوريا 46%", "rate_kg_ha": 100, "timing": "before planting"},
        {"product": "DAP", "product_ar": "DAP", "rate_kg_ha": 50, "timing": "at planting"},
    ], "estimated_cost_sar": 850}


@soil_app.get("/v1/crops/{crop}/requirements")
def soil_crop_requirements(crop: str):
    return {"crop": crop, "ph_range": [6.0, 7.5], "nitrogen_min_ppm": 20, "phosphorus_min_ppm": 15,
            "potassium_min_ppm": 150, "organic_matter_min_pct": 1.5}


# ═══════════════════════════════════════════════════════════════════════════════
# 10. Pest Detection Service (8125)
# ═══════════════════════════════════════════════════════════════════════════════

pest_app = FastAPI(title="Mock Pest Detection Service")
pest_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@pest_app.get("/healthz")
def pest_health():
    return {"status": "ok", "service": "pest-detection-service"}


@pest_app.get("/v1/pests")
def pest_list():
    return {"pests": PESTS}


@pest_app.get("/v1/pests/crop/{crop}")
def pest_by_crop(crop: str):
    return {"crop": crop, "pests": [p for p in PESTS if p["crop"] == crop]}


@pest_app.post("/v1/pests/identify")
async def pest_identify(request: Request):
    await request.json()  # consume body
    p = random.choice(PESTS)
    return {"pest_id": p["id"], "name": p["name"], "name_ar": p["name_ar"],
            "confidence": round(random.uniform(0.7, 0.95), 2), "quarantine": p["quarantine"]}


@pest_app.post("/v1/treatments/recommend")
async def pest_treatment(request: Request):
    body = await request.json()
    return {"pest_id": body.get("pest_id", "aphid"),
            "treatments": [{"method": "chemical", "product": "Imidacloprid", "product_ar": "إيميداكلوبريد", "rate": "0.5 L/ha"},
                           {"method": "biological", "product": "Ladybugs", "product_ar": "خنفساء أبو العيد", "rate": "5000/ha"}],
            "ipm_priority": "biological_first"}


@pest_app.post("/v1/thresholds/assess")
async def pest_threshold(request: Request):
    body = await request.json()
    count = body.get("pest_count", 5)
    threshold = body.get("threshold", 10)
    exceeded = count >= threshold
    return {"exceeded": exceeded, "pest_count": count, "threshold": threshold,
            "action_required": exceeded, "action_ar": "مطلوب تدخل" if exceeded else "مراقبة فقط"}


# ═══════════════════════════════════════════════════════════════════════════════
# 11. AI Advisor (8112)
# ═══════════════════════════════════════════════════════════════════════════════

ai_advisor_app = FastAPI(title="Mock AI Advisor")
ai_advisor_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@ai_advisor_app.get("/healthz")
def ai_health():
    return {"status": "ok", "service": "ai-advisor"}


@ai_advisor_app.post("/v1/advisor/ask")
async def ai_ask(request: Request):
    body = await request.json()
    q = body.get("question", "")
    return {"answer": f"Based on analysis, the recommendation for '{q[:50]}' is to optimize irrigation.",
            "answer_ar": "بناءً على التحليل، التوصية هي تحسين الري.",
            "confidence": round(random.uniform(0.7, 0.95), 2), "sources": ["agricultural_knowledge_base"]}


@ai_advisor_app.post("/v1/advisor/diagnose")
async def ai_diagnose(request: Request):
    d = random.choice(DISEASES)
    return {"diagnosis": d["name"], "diagnosis_ar": d["name_ar"], "confidence": 0.85,
            "recommendations": [{"action": "Apply treatment", "action_ar": "تطبيق العلاج", "priority": "high"}]}


@ai_advisor_app.post("/v1/advisor/recommend")
async def ai_recommend(request: Request):
    return {"recommendations": [
        {"action": "Increase irrigation frequency", "action_ar": "زيادة تواتر الري", "priority": "high"},
        {"action": "Apply nitrogen fertilizer", "action_ar": "تطبيق سماد نيتروجيني", "priority": "medium"},
    ]}


@ai_advisor_app.post("/v1/advisor/analyze-field")
async def ai_analyze_field(request: Request):
    return {"health_score": round(random.uniform(60, 90), 1),
            "issues": [{"type": "water_stress", "severity": "medium", "description_ar": "إجهاد مائي"}],
            "overall": "good", "overall_ar": "جيد"}


@ai_advisor_app.get("/v1/advisor/agents")
def ai_agents():
    return {"agents": [
        {"id": "crop_advisor", "name": "Crop Advisor", "name_ar": "مستشار المحاصيل"},
        {"id": "irrigation_expert", "name": "Irrigation Expert", "name_ar": "خبير الري"},
        {"id": "pest_controller", "name": "Pest Controller", "name_ar": "مكافح الآفات"},
    ]}


# ═══════════════════════════════════════════════════════════════════════════════
# 12. Inventory Service (8116)
# ═══════════════════════════════════════════════════════════════════════════════

inventory_app = FastAPI(title="Mock Inventory Service")
inventory_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@inventory_app.get("/healthz")
def inv_health():
    return {"status": "ok", "service": "inventory-service"}


@inventory_app.post("/v1/categories", status_code=201)
async def inv_create_category(request: Request):
    body = await request.json()
    cid = str(uuid.uuid4())
    cat = {"id": cid, "name": body.get("name", "Category"), "name_ar": body.get("name_ar", "فئة")}
    INVENTORY_STORE[cid] = cat
    return cat


@inventory_app.get("/v1/analytics/dashboard")
def inv_dashboard():
    return {"total_items": random.randint(50, 200), "total_value_sar": round(random.uniform(10000, 100000), 0),
            "low_stock_count": random.randint(2, 10), "categories": 8}


@inventory_app.get("/v1/analytics/reorder-recommendations")
def inv_reorder():
    return {"recommendations": [
        {"item": "Urea 46%", "item_ar": "يوريا 46%", "current_stock": 50, "reorder_point": 100, "suggested_qty": 200},
        {"item": "Drip tape", "item_ar": "شريط تنقيط", "current_stock": 10, "reorder_point": 50, "suggested_qty": 100},
    ]}


@inventory_app.get("/v1/analytics/abc-analysis")
def inv_abc():
    return {"analysis": [
        {"category": "A", "items_count": 10, "value_pct": 70, "description_ar": "أصناف عالية القيمة"},
        {"category": "B", "items_count": 30, "value_pct": 20, "description_ar": "أصناف متوسطة القيمة"},
        {"category": "C", "items_count": 60, "value_pct": 10, "description_ar": "أصناف منخفضة القيمة"},
    ]}


# ═══════════════════════════════════════════════════════════════════════════════
# Server runner
# ═══════════════════════════════════════════════════════════════════════════════

AGRI_SERVERS = {
    "advisory-service": (advisory_app, 8093),
    "irrigation-smart": (irrigation_app, 8094),
    "crop-intelligence": (crop_intel_app, 8095),
    "indicators-service": (indicators_app, 8091),
    "equipment-service": (equipment_app, 8101),
    "task-service": (task_app, 8103),
    "notification-service": (notification_app, 8110),
    "alert-service": (alert_app, 8113),
    "soil-analysis": (soil_app, 8134),
    "pest-detection": (pest_app, 8125),
    "ai-advisor": (ai_advisor_app, 8112),
    "inventory-service": (inventory_app, 8116),
}


def start_all_agri_servers():
    """Start all 12 agricultural mock servers in background threads."""
    for name, (app, port) in AGRI_SERVERS.items():
        config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
        server = uvicorn.Server(config)
        t = threading.Thread(target=server.run, daemon=True)
        t.start()

    # Wait for readiness
    for name, (_, port) in AGRI_SERVERS.items():
        ready = False
        last_error = None
        for _ in range(30):
            try:
                r = httpx.get(f"http://127.0.0.1:{port}/healthz", timeout=2)
                if r.status_code == 200:
                    ready = True
                    break
                last_error = f"unexpected status {r.status_code}"
            except Exception as exc:
                last_error = str(exc)
                time.sleep(0.3)
                continue
            time.sleep(0.3)
        if not ready:
            raise RuntimeError(
                f"Mock agri service '{name}' on port {port} did not become ready "
                f"after 30 attempts. Last error: {last_error or 'unknown error'}"
            )
