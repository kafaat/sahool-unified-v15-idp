"""
Wave 2 regression tests for billing-core.

Covers three billing-core correctness improvements:

1. ``Decimal`` monetary values are serialized as JSON strings (not floats)
   so cents precision is preserved over the wire.
2. Legacy wallet routes return ``HTTP 410 Gone`` with the full RFC 8594
   deprecation header set and a bilingual body.
3. The currency allow-list (``{SAR, YER, USD, AED, EUR}``) helper rejects
   unknown currencies with a bilingual 400 error.

All external dependencies (DB / NATS / auth) are stubbed via mocks — these
tests run in the standard unit test environment (``ENVIRONMENT=test``).
"""

from __future__ import annotations

import os
import uuid
from datetime import UTC, date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NATS_URL", "")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")


_TEST_TENANT_UUID = "00000000-0000-0000-0000-000000000001"


def _make_invoice_with_decimals() -> MagicMock:
    """Build a mock DB invoice with fractional Decimal amounts."""
    inv = MagicMock()
    inv.id = uuid.uuid4()
    inv.invoice_number = "SAH-2026-0042"
    inv.tenant_id = _TEST_TENANT_UUID
    inv.subscription_id = uuid.uuid4()
    inv.status = MagicMock(value="pending")
    inv.currency = MagicMock(value="USD")
    inv.issue_date = date(2026, 4, 1)
    inv.due_date = date(2026, 4, 8)
    inv.paid_date = None
    # Precisely the value that reveals float binary rounding:
    #   float(Decimal("12.34")) == 12.34 looks fine, but
    #   float(Decimal("0.1") + Decimal("0.2")) == 0.30000000000000004
    inv.subtotal = Decimal("12.34")
    inv.tax_amount = Decimal("0.00")
    inv.discount_amount = Decimal("0.00")
    inv.total = Decimal("12.34")
    inv.amount_paid = Decimal("0.00")
    inv.amount_due = Decimal("12.34")
    inv.line_items = [{"description": "Wave2 line", "amount": "12.34"}]
    inv.notes = None
    inv.notes_ar = None
    inv.created_at = datetime(2026, 4, 1, tzinfo=UTC)
    return inv


def _make_tenant() -> MagicMock:
    tenant = MagicMock()
    tenant.tenant_id = _TEST_TENANT_UUID
    tenant.name = "Wave 2 Farm"
    tenant.name_ar = "مزرعة Wave 2"
    tenant.contact = {"email": "wave2@example.com", "phone": "+967123456"}
    tenant.tax_id = None
    tenant.is_active = True
    tenant.created_at = datetime(2026, 4, 1, tzinfo=UTC)
    return tenant


# ============================================================
# 1. Decimal serialization tests
# ============================================================
class TestMoneyStrHelper:
    """Unit tests for the ``_money_str`` helper."""

    def test_decimal_preserves_cents(self):
        from src.main import _money_str

        assert _money_str(Decimal("12.34")) == "12.34"

    def test_decimal_zero(self):
        from src.main import _money_str

        # format("f") on Decimal("0") returns "0" which is JSON-safe.
        assert _money_str(Decimal("0")) in ("0", "0.00")

    def test_none_returns_zero_string(self):
        from src.main import _money_str

        assert _money_str(None) == "0"

    def test_float_input_normalised_to_string(self):
        from src.main import _money_str

        # Even when a float slips in, output is a JSON-safe string,
        # not a binary float literal.
        result = _money_str(12.34)
        assert isinstance(result, str)
        assert result.startswith("12.34")


class TestInvoiceSerializationPrecision:
    """
    End-to-end: GET /api/v1/invoices/{id} must return money fields as
    strings so clients do not see float rounding.
    """

    def test_invoice_amounts_are_strings_not_floats(self):
        from fastapi.testclient import TestClient

        from src.main import app

        invoice = _make_invoice_with_decimals()
        tenant = _make_tenant()

        # User's tenant matches the invoice's tenant so require_tenant_or_admin
        # passes without needing super_admin trickery. ``verify_tenant_access``
        # pulls ``.tenant_id`` off the current_user attr — hence an object-like
        # stub rather than a plain dict.
        fake_user = MagicMock()
        fake_user.id = "dev-user-00000000"
        fake_user.username = "dev-billing-user"
        fake_user.email = "dev@sahool.local"
        fake_user.tenant_id = _TEST_TENANT_UUID
        fake_user.roles = ["tenant_admin"]
        fake_user.is_active = True
        fake_user.has_any_role = lambda *args: False

        async def _fake_user_dep():
            return fake_user

        async def _fake_db_dep():
            return AsyncMock()

        with patch("src.main.BillingRepository") as MockRepo:
            repo_instance = MagicMock()
            repo_instance.invoices.get_by_id = AsyncMock(return_value=invoice)
            repo_instance.tenants.get_by_tenant_id = AsyncMock(return_value=tenant)
            MockRepo.return_value = repo_instance

            from src.main import get_current_active_user, get_db

            app.dependency_overrides[get_current_active_user] = _fake_user_dep
            app.dependency_overrides[get_db] = _fake_db_dep
            try:
                client = TestClient(app, raise_server_exceptions=False)
                # TenantContextMiddleware requires a valid UUID tenant header
                # when no JWT principal is on request.state.
                response = client.get(
                    f"/api/v1/invoices/{invoice.id}",
                    headers={"X-Tenant-ID": "00000000-0000-0000-0000-000000000001"},
                )
            finally:
                app.dependency_overrides.clear()

            assert response.status_code == 200, response.text
            body = response.json()
            inv = body["invoice"]

            # Critical assertion: amount fields are strings, preserving
            # cents precision. ``12.34`` as a float would serialise to a
            # JSON number that Python's JSON parser reifies as a float
            # and would lose precision for edge values.
            assert inv["total"] == "12.34"
            assert isinstance(inv["total"], str)
            assert inv["amount_due"] == "12.34"
            assert isinstance(inv["amount_due"], str)
            assert inv["subtotal"] == "12.34"
            assert isinstance(inv["subtotal"], str)
            # Tax/discount default to "0" or "0.00"
            assert isinstance(inv["tax_amount"], str)
            assert isinstance(inv["discount_amount"], str)


# ============================================================
# 2. Wallet deprecation middleware tests (RFC 8594)
# ============================================================
class TestWalletDeprecationMiddleware:
    """
    The legacy wallet routes must emit RFC 8594 deprecation headers and
    short-circuit with HTTP 410 Gone, because wallet functionality now
    lives in marketplace-service.
    """

    @pytest.mark.parametrize(
        "path",
        [
            "/api/v1/wallet/balance",
            "/api/v1/wallet",
            "/api/v1/wallet/deposit",
            "/api/v1/billing/wallet",
            "/api/v1/billing/wallet/transfer",
        ],
    )
    def test_legacy_wallet_routes_return_410(self, path: str):
        from fastapi.testclient import TestClient

        from src.main import app

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get(path)

        assert response.status_code == 410, f"Expected 410 Gone for {path!r}, got {response.status_code}"

        # RFC 8594 headers - exact per spec
        assert response.headers.get("Deprecation") == "true"
        assert response.headers.get("Sunset") == "2026-09-01"
        assert "successor-version" in response.headers.get("Link", "")

        # Platform convenience headers
        assert response.headers.get("X-API-Deprecated") == "true"
        assert "marketplace-service" in response.headers.get("X-API-Successor", "")
        warning = response.headers.get("Warning", "")
        assert "deprecated" in warning.lower()

        # Bilingual body
        body = response.json()
        assert "error" in body
        assert "error_ar" in body
        assert body["sunset"] == "2026-09-01"
        assert "marketplace-service" in body["successor"]

    def test_non_wallet_routes_still_work(self):
        """Regression: non-wallet routes must NOT be affected by the middleware."""
        from fastapi.testclient import TestClient

        from src.main import app

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/healthz")
        assert response.status_code == 200
        assert "Deprecation" not in response.headers


# ============================================================
# 3. Currency allow-list validation tests
# ============================================================
class TestCurrencyAllowList:
    """The ``_validate_currency_code`` helper enforces the billing allow-list."""

    @pytest.mark.parametrize("code", ["SAR", "YER", "USD", "AED", "EUR"])
    def test_accepts_allowed_currencies(self, code: str):
        from src.main import _validate_currency_code

        assert _validate_currency_code(code) == code

    def test_uppercases_lowercase_input(self):
        from src.main import _validate_currency_code

        assert _validate_currency_code("usd") == "USD"

    @pytest.mark.parametrize("bad_code", ["JPY", "GBP", "XYZ", "", "123"])
    def test_rejects_unknown_currency(self, bad_code: str):
        from fastapi import HTTPException

        from src.main import _validate_currency_code

        with pytest.raises(HTTPException) as exc_info:
            _validate_currency_code(bad_code)

        assert exc_info.value.status_code == 400
        detail = exc_info.value.detail
        assert isinstance(detail, dict)
        # Bilingual response body.
        assert "error" in detail
        assert "error_ar" in detail

    def test_create_tenant_request_rejects_unknown_currency(self):
        from pydantic import ValidationError

        from src.main import CreateTenantRequest

        with pytest.raises(ValidationError):
            CreateTenantRequest(
                name="Wave2",
                name_ar="ويف2",
                email="wave2@example.com",
                phone="+967123456",
                plan_id="starter",
                currency="JPY",  # not in allow-list
            )

    def test_create_tenant_request_accepts_sar(self):
        from src.main import CreateTenantRequest

        req = CreateTenantRequest(
            name="Wave2",
            name_ar="ويف2",
            email="wave2@example.com",
            phone="+967123456",
            plan_id="starter",
            currency="SAR",
        )
        assert req.currency == "SAR"
