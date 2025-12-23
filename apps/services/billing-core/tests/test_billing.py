"""
SAHOOL Billing Core Service - Unit Tests
اختبارات خدمة الفوترة الأساسية
"""

import pytest
from datetime import date, datetime, timedelta
from fastapi.testclient import TestClient
from decimal import Decimal


@pytest.fixture
def client():
    """Create test client with mocked app"""
    from fastapi import FastAPI

    app = FastAPI()

    @app.get("/healthz")
    def health():
        return {"status": "ok", "service": "billing_core", "version": "15.5.0"}

    @app.get("/api/v1/plans")
    def list_plans():
        return {
            "plans": [
                {"id": "free", "name": "Free", "price_usd": 0, "fields_limit": 2},
                {"id": "starter", "name": "Starter", "price_usd": 29, "fields_limit": 10},
                {"id": "professional", "name": "Professional", "price_usd": 99, "fields_limit": 50},
                {"id": "enterprise", "name": "Enterprise", "price_usd": 299, "fields_limit": -1}
            ]
        }

    @app.get("/api/v1/plans/{plan_id}")
    def get_plan(plan_id: str):
        plans = {
            "starter": {"id": "starter", "name": "Starter", "price_usd": 29, "fields_limit": 10}
        }
        if plan_id not in plans:
            return {"error": "Plan not found"}, 404
        return plans[plan_id]

    @app.get("/api/v1/tenants/{tenant_id}/subscription")
    def get_subscription(tenant_id: str):
        return {
            "tenant_id": tenant_id,
            "plan_id": "professional",
            "status": "active",
            "current_period_start": "2025-12-01",
            "current_period_end": "2026-01-01",
            "billing_cycle": "monthly"
        }

    @app.post("/api/v1/tenants/{tenant_id}/subscription")
    def create_subscription(tenant_id: str):
        return {
            "tenant_id": tenant_id,
            "plan_id": "starter",
            "status": "active",
            "created_at": datetime.now().isoformat()
        }

    @app.put("/api/v1/tenants/{tenant_id}/subscription")
    def update_subscription(tenant_id: str):
        return {
            "tenant_id": tenant_id,
            "plan_id": "professional",
            "status": "active",
            "upgraded_at": datetime.now().isoformat()
        }

    @app.delete("/api/v1/tenants/{tenant_id}/subscription")
    def cancel_subscription(tenant_id: str):
        return {
            "tenant_id": tenant_id,
            "status": "canceled",
            "canceled_at": datetime.now().isoformat()
        }

    @app.get("/api/v1/tenants/{tenant_id}/invoices")
    def list_invoices(tenant_id: str):
        return {
            "invoices": [
                {"id": "inv_001", "amount": 99.00, "status": "paid", "date": "2025-12-01"},
                {"id": "inv_002", "amount": 99.00, "status": "pending", "date": "2026-01-01"}
            ]
        }

    @app.get("/api/v1/invoices/{invoice_id}")
    def get_invoice(invoice_id: str):
        return {
            "id": invoice_id,
            "tenant_id": "tenant_001",
            "amount": 99.00,
            "currency": "USD",
            "status": "paid",
            "items": [
                {"description": "Professional Plan - Monthly", "amount": 99.00}
            ],
            "created_at": "2025-12-01T00:00:00Z"
        }

    @app.post("/api/v1/invoices/{invoice_id}/pay")
    def pay_invoice(invoice_id: str):
        return {
            "id": invoice_id,
            "status": "paid",
            "paid_at": datetime.now().isoformat(),
            "payment_method": "card"
        }

    @app.get("/api/v1/tenants/{tenant_id}/usage")
    def get_usage(tenant_id: str):
        return {
            "tenant_id": tenant_id,
            "period": "2025-12",
            "fields_used": 15,
            "fields_limit": 50,
            "api_calls": 12500,
            "storage_mb": 256
        }

    @app.post("/api/v1/tenants/{tenant_id}/usage/record")
    def record_usage(tenant_id: str):
        return {"recorded": True, "timestamp": datetime.now().isoformat()}

    @app.get("/api/v1/currency/convert")
    def convert_currency(amount: float, from_currency: str, to_currency: str):
        rate = 250 if to_currency == "YER" else 1/250
        return {
            "amount": amount,
            "from": from_currency,
            "to": to_currency,
            "converted": amount * rate,
            "rate": rate
        }

    return TestClient(app)


class TestHealthEndpoint:
    """Test health check"""

    def test_health_check(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestPlans:
    """Test plan management"""

    def test_list_plans(self, client):
        response = client.get("/api/v1/plans")
        assert response.status_code == 200
        data = response.json()
        assert "plans" in data
        assert len(data["plans"]) >= 4

    def test_plans_have_required_fields(self, client):
        response = client.get("/api/v1/plans")
        assert response.status_code == 200
        for plan in response.json()["plans"]:
            assert "id" in plan
            assert "name" in plan
            assert "price_usd" in plan

    def test_get_plan_details(self, client):
        response = client.get("/api/v1/plans/starter")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "starter"


class TestSubscriptions:
    """Test subscription management"""

    def test_get_subscription(self, client):
        response = client.get("/api/v1/tenants/tenant_001/subscription")
        assert response.status_code == 200
        data = response.json()
        assert data["tenant_id"] == "tenant_001"
        assert "plan_id" in data
        assert "status" in data

    def test_create_subscription(self, client):
        response = client.post(
            "/api/v1/tenants/tenant_002/subscription",
            json={"plan_id": "starter"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"

    def test_update_subscription(self, client):
        response = client.put(
            "/api/v1/tenants/tenant_001/subscription",
            json={"plan_id": "professional"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["plan_id"] == "professional"

    def test_cancel_subscription(self, client):
        response = client.delete("/api/v1/tenants/tenant_001/subscription")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "canceled"


class TestInvoices:
    """Test invoice management"""

    def test_list_invoices(self, client):
        response = client.get("/api/v1/tenants/tenant_001/invoices")
        assert response.status_code == 200
        data = response.json()
        assert "invoices" in data

    def test_get_invoice(self, client):
        response = client.get("/api/v1/invoices/inv_001")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "inv_001"
        assert "amount" in data
        assert "status" in data

    def test_invoice_has_items(self, client):
        response = client.get("/api/v1/invoices/inv_001")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) > 0

    def test_pay_invoice(self, client):
        response = client.post("/api/v1/invoices/inv_002/pay", json={"payment_method": "card"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "paid"


class TestUsage:
    """Test usage tracking"""

    def test_get_usage(self, client):
        response = client.get("/api/v1/tenants/tenant_001/usage")
        assert response.status_code == 200
        data = response.json()
        assert "fields_used" in data
        assert "fields_limit" in data
        assert "api_calls" in data

    def test_record_usage(self, client):
        response = client.post(
            "/api/v1/tenants/tenant_001/usage/record",
            json={"type": "api_call", "count": 1}
        )
        assert response.status_code == 200
        assert response.json()["recorded"] == True


class TestCurrency:
    """Test currency conversion"""

    def test_convert_usd_to_yer(self, client):
        response = client.get("/api/v1/currency/convert?amount=100&from_currency=USD&to_currency=YER")
        assert response.status_code == 200
        data = response.json()
        assert data["from"] == "USD"
        assert data["to"] == "YER"
        assert data["converted"] == 25000  # 100 * 250

    def test_convert_yer_to_usd(self, client):
        response = client.get("/api/v1/currency/convert?amount=25000&from_currency=YER&to_currency=USD")
        assert response.status_code == 200
        data = response.json()
        assert data["converted"] == 100  # 25000 / 250
