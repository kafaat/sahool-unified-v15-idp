"""
SAHOOL Mock Service Servers for E2E Testing
خوادم خدمات محاكاة لاختبارات التكامل الشاملة

Simulates: user-service, field-management-service, weather-service,
           vegetation-analysis-service — all in one process on different ports.

Usage:
    python tests/e2e/mock_services.py          # Start all mock servers
    pytest tests/e2e/test_e2e_mock.py          # Run E2E tests against mocks
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import random
import threading
import time
import uuid
from datetime import UTC, datetime, timedelta


import uvicorn
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ═══════════════════════════════════════════════════════════════════════════════
# Shared State (in-memory database)
# ═══════════════════════════════════════════════════════════════════════════════

USERS: dict[str, dict] = {}
FIELDS: dict[str, dict] = {}
REFRESH_TOKENS: dict[str, dict] = {}
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "test-only-jwt-secret-not-for-production")
DEFAULT_TENANT = "a0000000-0000-0000-0000-000000000001"


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()  # noqa: S324 — test-only mock, not production


def _make_jwt(user_id: str, email: str, roles: list[str], tenant_id: str) -> str:
    """Simple base64 'JWT' for testing (no real signing needed for mocks)."""
    import base64

    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().rstrip("=")
    payload_data = {
        "sub": user_id,
        "email": email,
        "roles": roles,
        "tid": tenant_id,
        "jti": str(uuid.uuid4()),
        "type": "access",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
        "iss": "sahool-platform",
        "aud": "sahool-api",
    }
    payload = base64.urlsafe_b64encode(json.dumps(payload_data).encode()).decode().rstrip("=")
    sig = base64.urlsafe_b64encode(b"mock-signature").decode().rstrip("=")
    return f"{header}.{payload}.{sig}"


def _decode_token(token: str) -> dict | None:
    """Decode our mock JWT."""
    import base64

    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        raw = parts[1]
        padding = (4 - len(raw) % 4) % 4  # 0 when already aligned
        payload = raw + "=" * padding
        return json.loads(base64.urlsafe_b64decode(payload))
    except Exception:  # noqa: BLE001 — catch-all OK for test mock
        return None


def _get_user_from_auth(authorization: str | None) -> dict | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization[7:]
    payload = _decode_token(token)
    if not payload:
        return None
    if payload.get("exp", 0) < time.time():
        return None
    return payload


# ═══════════════════════════════════════════════════════════════════════════════
# 1. User Service (port 3025)
# ═══════════════════════════════════════════════════════════════════════════════

user_app = FastAPI(title="Mock User Service", version="16.0.0")
user_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@user_app.get("/health")
@user_app.get("/healthz")
@user_app.get("/readyz")
def user_health():
    return {"status": "ok", "service": "user-service", "version": "16.0.0"}


class RegisterRequest(BaseModel):
    email: str
    password: str
    firstName: str
    lastName: str
    phone: str | None = None
    tenantId: str | None = None


@user_app.post("/api/v1/auth/register", status_code=201)
def register(req: RegisterRequest):
    if req.email in USERS:
        raise HTTPException(409, "User already exists")
    user_id = str(uuid.uuid4())
    tenant_id = req.tenantId or DEFAULT_TENANT
    USERS[req.email] = {
        "id": user_id,
        "email": req.email,
        "password_hash": _hash_password(req.password),
        "firstName": req.firstName,
        "lastName": req.lastName,
        "role": "FARMER",
        "status": "ACTIVE",
        "tenantId": tenant_id,
    }
    access_token = _make_jwt(user_id, req.email, ["FARMER"], tenant_id)
    refresh_jti = str(uuid.uuid4())
    refresh_token = _make_jwt(user_id, req.email, ["FARMER"], tenant_id)
    REFRESH_TOKENS[refresh_jti] = {"user_id": user_id, "email": req.email, "tenant_id": tenant_id}
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": 1800,
        "token_type": "Bearer",
        "user": {
            "id": user_id,
            "email": req.email,
            "firstName": req.firstName,
            "lastName": req.lastName,
            "role": "FARMER",
            "tenantId": tenant_id,
        },
    }


class LoginRequest(BaseModel):
    email: str
    password: str


@user_app.post("/api/v1/auth/login")
def login(req: LoginRequest):
    user = USERS.get(req.email)
    if not user or user["password_hash"] != _hash_password(req.password):
        raise HTTPException(401, "Invalid credentials")
    access_token = _make_jwt(user["id"], user["email"], [user["role"]], user["tenantId"])
    refresh_token = _make_jwt(user["id"], user["email"], [user["role"]], user["tenantId"])
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_in": 1800,
        "token_type": "Bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "firstName": user["firstName"],
            "lastName": user["lastName"],
            "role": user["role"],
            "tenantId": user["tenantId"],
        },
    }


class RefreshRequest(BaseModel):
    refreshToken: str


@user_app.post("/api/v1/auth/refresh")
def refresh(req: RefreshRequest):
    payload = _decode_token(req.refreshToken)
    if not payload:
        raise HTTPException(401, "Invalid refresh token")
    new_access = _make_jwt(payload["sub"], payload["email"], payload["roles"], payload["tid"])
    new_refresh = _make_jwt(payload["sub"], payload["email"], payload["roles"], payload["tid"])
    return {"access_token": new_access, "refresh_token": new_refresh, "expires_in": 1800, "token_type": "Bearer"}


@user_app.get("/api/v1/auth/me")
def me(authorization: str | None = Header(None)):
    user = _get_user_from_auth(authorization)
    if not user:
        raise HTTPException(401, "Unauthorized")
    return {"id": user["sub"], "email": user["email"], "roles": user["roles"], "tenantId": user["tid"]}


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Field Management Service (port 3000)
# ═══════════════════════════════════════════════════════════════════════════════

field_app = FastAPI(title="Mock Field Management Service", version="16.0.0")
field_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@field_app.get("/healthz")
@field_app.get("/readyz")
@field_app.get("/health")
def field_health():
    return {"status": "ok", "service": "field-management-service", "version": "16.0.0"}


@field_app.post("/api/v1/fields", status_code=201)
async def create_field(request: Request, authorization: str | None = Header(None)):
    user = _get_user_from_auth(authorization)
    if not user:
        raise HTTPException(401, "Unauthorized")

    body = await request.json()
    name = body.get("name")
    if not name:
        raise HTTPException(400, "Field name is required")

    coords = body.get("coordinates", [])
    # Calculate bbox and centroid
    if coords and len(coords) >= 3:
        lngs = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        bbox = [min(lngs), min(lats), max(lngs), max(lats)]
        centroid = {"lat": sum(lats) / len(lats), "lng": sum(lngs) / len(lngs)}
        # Approximate area (hectares)
        avg_lat = sum(lats) / len(lats)
        cos_lat = math.cos(math.radians(avg_lat))
        # Shoelace formula
        n = len(coords)
        area_deg = 0
        for i in range(n):
            j = (i + 1) % n
            area_deg += coords[i][0] * coords[j][1]
            area_deg -= coords[j][0] * coords[i][1]
        area_deg = abs(area_deg) / 2
        area_ha = area_deg * 111.32 * 111.32 * cos_lat * 100
    else:
        bbox = None
        centroid = None
        area_ha = 0

    field_id = str(uuid.uuid4())
    field = {
        "id": field_id,
        "name": name,
        "nameAr": body.get("nameAr"),
        "tenantId": user["tid"],
        "cropType": body.get("cropType", "wheat"),
        "irrigationType": body.get("irrigationType"),
        "status": "active",
        "areaHectares": round(area_ha, 2),
        "healthScore": round(random.uniform(0.5, 0.95), 2),
        "ndviValue": round(random.uniform(0.3, 0.85), 3),
        "coordinates": centroid,
        "boundary": [coords] if coords else None,
        "bbox": bbox,
        "version": 1,
        "etag": f"{field_id}-v1",
        "createdAt": datetime.now(UTC).isoformat(),
        "updatedAt": datetime.now(UTC).isoformat(),
    }
    FIELDS[field_id] = field
    return field


@field_app.get("/api/v1/fields")
def list_fields(
    authorization: str | None = Header(None),
    page: int = 1,
    limit: int = 20,
):
    user = _get_user_from_auth(authorization)
    if not user:
        raise HTTPException(401, "Unauthorized")

    tenant_fields = [f for f in FIELDS.values() if f["tenantId"] == user["tid"]]
    start = (page - 1) * limit
    end = start + limit
    return {
        "data": tenant_fields[start:end],
        "meta": {"total": len(tenant_fields), "page": page, "limit": limit},
    }


@field_app.get("/api/v1/fields/nearby")
def nearby_fields(lat: float, lng: float, radius: float = 10, authorization: str | None = Header(None)):
    user = _get_user_from_auth(authorization)
    if not user:
        raise HTTPException(401, "Unauthorized")
    return {"data": [], "meta": {"total": 0}}


@field_app.get("/api/v1/fields/{field_id}")
def get_field(field_id: str, authorization: str | None = Header(None)):
    user = _get_user_from_auth(authorization)
    if not user:
        raise HTTPException(401, "Unauthorized")
    field = FIELDS.get(field_id)
    if not field or field["tenantId"] != user["tid"]:
        raise HTTPException(404, "Field not found")
    return field


@field_app.delete("/api/v1/fields/{field_id}")
def delete_field(field_id: str, authorization: str | None = Header(None)):
    user = _get_user_from_auth(authorization)
    if not user:
        raise HTTPException(401, "Unauthorized")
    field = FIELDS.get(field_id)
    if not field or field["tenantId"] != user["tid"]:
        raise HTTPException(404, "Field not found")
    field["status"] = "inactive"
    field["isDeleted"] = True
    return {"message": "Field deleted successfully"}


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Weather Service (port 8092)
# ═══════════════════════════════════════════════════════════════════════════════

weather_app = FastAPI(title="Mock Weather Service", version="16.0.0")
weather_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@weather_app.get("/healthz")
@weather_app.get("/readyz")
def weather_health():
    return {"status": "ok", "service": "weather-service", "version": "16.0.0"}


@weather_app.post("/weather/current")
async def weather_current(request: Request):
    body = await request.json()
    lat = body.get("lat", 15.35)
    lon = body.get("lon", 44.21)
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise HTTPException(400, "Invalid coordinates")

    # Simulate realistic Yemen weather
    base_temp = 25 + 10 * math.sin(time.time() / 86400 * 2 * math.pi)
    return {
        "data": {
            "temperature_c": round(base_temp + random.uniform(-3, 3), 1),
            "humidity_pct": round(random.uniform(25, 65), 1),
            "wind_speed_kmh": round(random.uniform(5, 25), 1),
            "wind_direction_deg": random.randint(0, 360),
            "precipitation_mm": round(random.uniform(0, 2), 1),
            "cloud_cover_pct": random.randint(0, 80),
            "pressure_hpa": round(random.uniform(1010, 1025), 1),
            "uv_index": round(random.uniform(5, 11), 1),
            "condition": "Partly Cloudy",
            "condition_ar": "غائم جزئياً",
        },
        "provider": "open-meteo",
        "is_cached": False,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@weather_app.post("/weather/forecast")
async def weather_forecast(request: Request):
    body = await request.json()
    days = min(body.get("days", 7), 16)
    forecast = []
    for i in range(days):
        date = datetime.now(UTC) + timedelta(days=i)
        temp_base = 25 + 10 * math.sin((time.time() + i * 86400) / 86400 * 2 * math.pi)
        forecast.append({
            "date": date.strftime("%Y-%m-%d"),
            "temp_max_c": round(temp_base + random.uniform(2, 6), 1),
            "temp_min_c": round(temp_base - random.uniform(4, 8), 1),
            "precipitation_mm": round(random.uniform(0, 5), 1),
            "precipitation_probability": random.randint(0, 40),
            "wind_speed_max_kmh": round(random.uniform(10, 30), 1),
            "uv_index_max": round(random.uniform(6, 11), 1),
            "condition": random.choice(["Sunny", "Partly Cloudy", "Cloudy"]),
            "condition_ar": random.choice(["مشمس", "غائم جزئياً", "غائم"]),
        })
    return {"data": {"forecast": forecast}, "provider": "open-meteo"}


@weather_app.post("/weather/agricultural-report")
async def weather_agri_report(request: Request):
    body = await request.json()
    temp = random.uniform(22, 35)
    humidity = random.uniform(30, 60)
    wind = random.uniform(5, 20)
    et0 = round((0.0023 * (temp + 17.8) * ((temp + 5) ** 0.5) * 15), 2)
    gdd = round(max(0, ((temp + 5 + temp - 5) / 2) - 10), 1)
    spray_ok = 15 <= temp <= 28 and 40 <= humidity <= 80 and wind < 20
    return {
        "data": {
            "evapotranspiration": {"et0": et0, "classification": "moderate", "unit": "mm/day"},
            "growing_degree_days": {"gdd": gdd, "growth_rate": "normal", "base_temp_c": 10},
            "spray_window": {
                "suitable": spray_ok,
                "suitability": "optimal" if spray_ok else "marginal",
                "conditions": {"temperature_ok": True, "humidity_ok": True, "wind_ok": wind < 20},
            },
            "frost_risk": {"risk_level": "none", "probability": 0},
            "heat_stress": {"index": round(temp * 0.8 + humidity * 0.2, 1), "level": "low"},
        },
        "timestamp": datetime.now(UTC).isoformat(),
    }


@weather_app.post("/weather/evapotranspiration")
async def weather_et0(request: Request):
    body = await request.json()
    temp = body.get("temperature_c", 28)
    humidity = body.get("humidity_pct", 45)
    et0 = round((0.0023 * (temp + 17.8) * ((temp + 5) ** 0.5) * 15), 2)
    return {"et0": et0, "classification": "moderate" if et0 < 6 else "high", "unit": "mm/day"}


@weather_app.post("/weather/gdd")
async def weather_gdd(request: Request):
    body = await request.json()
    t_max = body.get("temp_max_c", 32)
    t_min = body.get("temp_min_c", 18)
    base = body.get("base_temp_c", 10)
    gdd = max(0, (t_max + t_min) / 2 - base)
    return {"gdd": round(gdd, 1), "growth_rate": "normal" if gdd < 20 else "rapid", "base_temp_c": base}


@weather_app.post("/weather/spray-window")
async def weather_spray(request: Request):
    body = await request.json()
    temp = body.get("temperature_c", 22)
    humidity = body.get("humidity_pct", 55)
    wind = body.get("wind_speed_kmh", 8)
    precip = body.get("precipitation_mm", 0)
    ok = 15 <= temp <= 28 and 40 <= humidity <= 80 and wind < 20 and precip < 2
    return {
        "suitable": ok,
        "suitability": "optimal" if ok else "unsuitable",
        "conditions": {"temperature_ok": 15 <= temp <= 28, "humidity_ok": 40 <= humidity <= 80, "wind_ok": wind < 20},
    }


@weather_app.get("/weather/providers")
def weather_providers():
    return {
        "providers": [
            {"name": "open-meteo", "status": "active", "priority": "primary"},
            {"name": "openweathermap", "status": "active", "priority": "secondary"},
        ]
    }


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Vegetation Analysis Service (port 8090)
# ═══════════════════════════════════════════════════════════════════════════════

vegetation_app = FastAPI(title="Mock Vegetation Analysis Service", version="16.0.0")
vegetation_app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@vegetation_app.get("/healthz")
@vegetation_app.get("/readyz")
def vegetation_health():
    return {"status": "ok", "service": "vegetation-analysis-service", "version": "16.0.0"}


@vegetation_app.get("/v1/eo-status")
def eo_status():
    sentinel_id = os.getenv("SENTINEL_HUB_CLIENT_ID", "")
    return {
        "sentinel_hub_configured": bool(sentinel_id),
        "sentinel_hub_client_id_set": bool(sentinel_id),
        "data_source": "mock" if not sentinel_id else "sentinel-2",
        "status": "operational",
    }


@vegetation_app.get("/v1/providers")
def veg_providers():
    return {
        "providers": [
            {"name": "sentinel-2", "type": "optical", "resolution": "10m", "revisit_days": 5},
            {"name": "mock", "type": "simulated", "resolution": "10m", "revisit_days": 1},
        ]
    }


@vegetation_app.get("/v1/satellites")
def veg_satellites():
    return {"satellites": ["Sentinel-2A", "Sentinel-2B", "Landsat-8", "Landsat-9"]}


@vegetation_app.post("/v1/analyze")
async def veg_analyze(request: Request):
    body = await request.json()
    field_id = body.get("field_id")
    if not field_id:
        raise HTTPException(400, "field_id is required")

    ndvi = round(random.uniform(0.2, 0.85), 3)
    health = "healthy" if ndvi >= 0.6 else "moderate" if ndvi >= 0.4 else "stressed" if ndvi >= 0.2 else "critical"
    return {
        "field_id": field_id,
        "analysis_type": body.get("analysis_type", "ndvi"),
        "ndvi": ndvi,
        "ndvi_mean": ndvi,
        "ndvi_min": round(ndvi - 0.1, 3),
        "ndvi_max": round(ndvi + 0.1, 3),
        "health_status": health,
        "health_status_ar": {"healthy": "صحي", "moderate": "معتدل", "stressed": "مجهد", "critical": "حرج"}[health],
        "lai": round(ndvi * 4.5, 2),
        "cloud_cover_pct": random.randint(0, 20),
        "data_source": "mock",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@vegetation_app.get("/v1/indices/{field_id}")
def veg_indices(field_id: str):
    ndvi = round(random.uniform(0.3, 0.85), 3)
    return {
        "field_id": field_id,
        "indices": {
            "ndvi": ndvi,
            "ndwi": round(random.uniform(-0.1, 0.3), 3),
            "evi": round(ndvi * 0.8, 3),
            "savi": round(ndvi * 0.9, 3),
            "lai": round(ndvi * 4.5, 2),
        },
        "health_status": "healthy" if ndvi >= 0.6 else "moderate",
        "trend": random.choice(["up", "stable", "down"]),
        "last_capture": datetime.now(UTC).isoformat(),
        "data_source": "mock",
    }


@vegetation_app.get("/v1/timeseries/{field_id}")
def veg_timeseries(field_id: str, days: int = 90):
    data = []
    for i in range(0, days, 5):
        date = datetime.now(UTC) - timedelta(days=days - i)
        base_ndvi = 0.5 + 0.2 * math.sin(i / 30 * math.pi)
        data.append({
            "date": date.strftime("%Y-%m-%d"),
            "ndvi": round(base_ndvi + random.uniform(-0.05, 0.05), 3),
            "cloud_cover": random.randint(0, 30),
        })
    return {"field_id": field_id, "timeseries": data, "interval_days": 5}


# ═══════════════════════════════════════════════════════════════════════════════
# Server Runner
# ═══════════════════════════════════════════════════════════════════════════════

SERVERS = {
    "user-service": (user_app, 3025),
    "field-management": (field_app, 3000),
    "weather-service": (weather_app, 8092),
    "vegetation-analysis": (vegetation_app, 8090),
}


def run_server(app: FastAPI, port: int, name: str):
    """Run a single uvicorn server in a thread."""
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    server.run()


def start_all_servers():
    """Start all mock servers in background threads."""
    threads = []
    for name, (app, port) in SERVERS.items():
        t = threading.Thread(target=run_server, args=(app, port, name), daemon=True)
        t.start()
        threads.append(t)
        print(f"  ✓ {name} started on port {port}")

    # Wait for servers to be ready
    import httpx

    for name, (_, port) in SERVERS.items():
        for attempt in range(30):
            try:
                r = httpx.get(f"http://127.0.0.1:{port}/healthz", timeout=2)
                if r.status_code == 200:
                    break
            except Exception:  # noqa: BLE001 — expected during server startup
                time.sleep(0.3)
                continue
            time.sleep(0.3)

    return threads


if __name__ == "__main__":
    print("Starting SAHOOL mock services...")
    start_all_servers()
    print("\nAll mock services running. Press Ctrl+C to stop.\n")
    print("  User Service:       http://localhost:3025")
    print("  Field Management:   http://localhost:3000")
    print("  Weather Service:    http://localhost:8092")
    print("  Vegetation Service: http://localhost:8090")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
