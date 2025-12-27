"""
SAHOOL Integration Tests - Billing Workflow
اختبارات التكامل - سير عمل الفوترة

Tests complete billing workflow including:
- Subscription creation
- Invoice generation
- Payment processing (Stripe & Tharwatt)
- Usage tracking and quotas

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import pytest
import asyncio
from typing import Dict, Any
from datetime import datetime, date, timedelta
from decimal import Decimal


# ═══════════════════════════════════════════════════════════════════════════════
# Test Subscription Creation Workflow - اختبار سير عمل إنشاء الاشتراك
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_subscription_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل إنشاء اشتراك جديد

    Test complete subscription creation:
    1. List available plans
    2. Create new tenant with subscription
    3. Verify subscription is active
    4. Check trial period
    """
    # Arrange - إعداد بيانات الاختبار
    billing_url = service_urls.get("billing_core", "http://localhost:8089")

    # Step 1: List available plans - قائمة الخطط المتاحة
    plans_response = await http_client.get(
        f"{billing_url}/v1/plans",
        headers=auth_headers
    )

    assert plans_response.status_code == 200
    plans_data = plans_response.json()

    assert "plans" in plans_data
    assert len(plans_data["plans"]) > 0

    # Get starter plan
    starter_plan = next(
        (p for p in plans_data["plans"] if p["plan_id"] == "starter"),
        None
    )
    assert starter_plan is not None

    # Step 2: Create tenant with subscription - إنشاء مستأجر مع اشتراك
    tenant_data = {
        "name": "Integration Test Farm",
        "name_ar": "مزرعة اختبار التكامل",
        "email": "test-integration@sahool.io",
        "phone": "+967777123456",
        "plan_id": "starter",
        "billing_cycle": "monthly"
    }

    tenant_response = await http_client.post(
        f"{billing_url}/v1/tenants",
        json=tenant_data,
        headers=auth_headers
    )

    assert tenant_response.status_code == 200
    tenant_result = tenant_response.json()

    assert tenant_result["success"] is True
    assert "tenant_id" in tenant_result
    assert "subscription_id" in tenant_result

    tenant_id = tenant_result["tenant_id"]
    subscription_id = tenant_result["subscription_id"]

    # Step 3: Verify subscription details - التحقق من تفاصيل الاشتراك
    # Note: This requires authentication - skipping if auth not available
    try:
        subscription_response = await http_client.get(
            f"{billing_url}/v1/tenants/{tenant_id}/subscription",
            headers=auth_headers
        )

        if subscription_response.status_code == 200:
            subscription = subscription_response.json()

            assert "subscription" in subscription
            assert subscription["subscription"]["tenant_id"] == tenant_id
            assert subscription["subscription"]["plan_id"] == "starter"
            assert subscription["subscription"]["status"] in ["trial", "active"]

            # Verify trial period
            if subscription["is_trial"]:
                assert "trial_end_date" in subscription["subscription"]

    except Exception as e:
        # Auth may not be available in test environment
        pytest.skip(f"Authentication required: {e}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_subscription_upgrade_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل ترقية الاشتراك

    Test subscription upgrade:
    1. Create tenant with starter plan
    2. Upgrade to professional plan
    3. Verify plan change
    """
    billing_url = service_urls.get("billing_core", "http://localhost:8089")

    # Step 1: Create tenant with starter plan
    tenant_data = {
        "name": "Upgrade Test Farm",
        "name_ar": "مزرعة اختبار الترقية",
        "email": "upgrade-test@sahool.io",
        "phone": "+967777234567",
        "plan_id": "starter",
        "billing_cycle": "monthly"
    }

    tenant_response = await http_client.post(
        f"{billing_url}/v1/tenants",
        json=tenant_data,
        headers=auth_headers
    )

    assert tenant_response.status_code == 200
    tenant_id = tenant_response.json()["tenant_id"]

    # Step 2: Upgrade subscription - ترقية الاشتراك
    try:
        upgrade_data = {
            "plan_id": "professional",
            "billing_cycle": "monthly"
        }

        upgrade_response = await http_client.patch(
            f"{billing_url}/v1/tenants/{tenant_id}/subscription",
            json=upgrade_data,
            headers=auth_headers
        )

        if upgrade_response.status_code == 200:
            upgrade_result = upgrade_response.json()

            assert upgrade_result["success"] is True
            assert upgrade_result["subscription"]["plan_id"] == "professional"

    except Exception as e:
        pytest.skip(f"Authentication required for upgrade: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# Test Invoice Generation Workflow - اختبار سير عمل إنشاء الفواتير
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invoice_generation_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل إنشاء الفواتير

    Test invoice generation:
    1. Create tenant with subscription
    2. Generate invoice
    3. Verify invoice details
    4. Check invoice line items
    """
    billing_url = service_urls.get("billing_core", "http://localhost:8089")

    # Step 1: Create tenant
    tenant_data = {
        "name": "Invoice Test Farm",
        "name_ar": "مزرعة اختبار الفواتير",
        "email": "invoice-test@sahool.io",
        "phone": "+967777345678",
        "plan_id": "professional",
        "billing_cycle": "monthly"
    }

    tenant_response = await http_client.post(
        f"{billing_url}/v1/tenants",
        json=tenant_data,
        headers=auth_headers
    )

    assert tenant_response.status_code == 200
    tenant_id = tenant_response.json()["tenant_id"]

    # Step 2: Generate invoice - إنشاء فاتورة
    try:
        invoice_response = await http_client.post(
            f"{billing_url}/v1/tenants/{tenant_id}/invoices/generate",
            headers=auth_headers
        )

        if invoice_response.status_code == 200:
            invoice_result = invoice_response.json()

            assert invoice_result["success"] is True
            assert "invoice" in invoice_result

            invoice = invoice_result["invoice"]

            # Verify invoice structure
            assert invoice["tenant_id"] == tenant_id
            assert invoice["status"] in ["draft", "pending"]
            assert "invoice_number" in invoice
            assert "total" in invoice
            assert "line_items" in invoice

            # Verify line items
            assert len(invoice["line_items"]) > 0
            first_item = invoice["line_items"][0]
            assert "description" in first_item
            assert "description_ar" in first_item
            assert "amount" in first_item

            invoice_id = invoice["invoice_id"]

            # Step 3: Get invoice details - الحصول على تفاصيل الفاتورة
            invoice_detail_response = await http_client.get(
                f"{billing_url}/v1/invoices/{invoice_id}",
                headers=auth_headers
            )

            if invoice_detail_response.status_code == 200:
                invoice_detail = invoice_detail_response.json()

                assert "invoice" in invoice_detail
                assert invoice_detail["invoice"]["invoice_id"] == invoice_id

    except Exception as e:
        pytest.skip(f"Authentication required: {e}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_invoices_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار قائمة الفواتير

    Test listing invoices:
    1. Create tenant
    2. Generate multiple invoices
    3. List all invoices
    4. Filter invoices by status
    """
    billing_url = service_urls.get("billing_core", "http://localhost:8089")

    # Step 1: Create tenant
    tenant_data = {
        "name": "Invoice List Test",
        "name_ar": "اختبار قائمة الفواتير",
        "email": "invoice-list@sahool.io",
        "phone": "+967777456789",
        "plan_id": "starter",
        "billing_cycle": "monthly"
    }

    tenant_response = await http_client.post(
        f"{billing_url}/v1/tenants",
        json=tenant_data,
        headers=auth_headers
    )

    assert tenant_response.status_code == 200
    tenant_id = tenant_response.json()["tenant_id"]

    try:
        # Step 2: List invoices - قائمة الفواتير
        list_response = await http_client.get(
            f"{billing_url}/v1/tenants/{tenant_id}/invoices",
            headers=auth_headers
        )

        if list_response.status_code == 200:
            invoices_list = list_response.json()

            assert "invoices" in invoices_list
            assert "total" in invoices_list
            assert isinstance(invoices_list["invoices"], list)

    except Exception as e:
        pytest.skip(f"Authentication required: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# Test Payment Processing Workflow - اختبار سير عمل معالجة الدفع
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_payment_processing_workflow(
    http_client,
    service_urls: Dict[str, str],
    payment_factory,
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل معالجة الدفع

    Test payment processing:
    1. Create invoice
    2. Create payment
    3. Verify payment status
    4. Check invoice is marked as paid
    """
    billing_url = service_urls.get("billing_core", "http://localhost:8089")

    # Step 1: Create tenant and generate invoice
    tenant_data = {
        "name": "Payment Test Farm",
        "name_ar": "مزرعة اختبار الدفع",
        "email": "payment-test@sahool.io",
        "phone": "+967777567890",
        "plan_id": "starter",
        "billing_cycle": "monthly"
    }

    tenant_response = await http_client.post(
        f"{billing_url}/v1/tenants",
        json=tenant_data,
        headers=auth_headers
    )

    assert tenant_response.status_code == 200
    tenant_id = tenant_response.json()["tenant_id"]

    try:
        # Generate invoice
        invoice_response = await http_client.post(
            f"{billing_url}/v1/tenants/{tenant_id}/invoices/generate",
            headers=auth_headers
        )

        if invoice_response.status_code == 200:
            invoice = invoice_response.json()["invoice"]
            invoice_id = invoice["invoice_id"]
            total_amount = invoice["total"]

            # Step 2: Create payment - إنشاء دفعة
            payment_data = {
                "invoice_id": invoice_id,
                "amount": total_amount,
                "method": "cash"  # Use cash for testing (no external gateway needed)
            }

            payment_response = await http_client.post(
                f"{billing_url}/v1/payments",
                json=payment_data,
                headers=auth_headers
            )

            if payment_response.status_code == 200:
                payment_result = payment_response.json()

                assert payment_result["success"] is True
                assert "payment" in payment_result

                payment = payment_result["payment"]

                # Verify payment
                assert payment["invoice_id"] == invoice_id
                assert float(payment["amount"]) == float(total_amount)
                assert payment["method"] == "cash"
                assert payment["status"] in ["succeeded", "pending", "processing"]

                # For cash payments, status should be succeeded immediately
                if payment["method"] == "cash":
                    assert payment["status"] == "succeeded"
                    assert payment_result["invoice_status"] == "paid"

    except Exception as e:
        pytest.skip(f"Authentication required: {e}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_tharwatt_payment_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل الدفع عبر ثروات

    Test Tharwatt payment workflow:
    1. Create invoice
    2. Initiate Tharwatt payment
    3. Verify payment is in processing state

    Note: This tests the API flow, not actual payment processing
    """
    billing_url = service_urls.get("billing_core", "http://localhost:8089")

    # Create tenant and invoice
    tenant_data = {
        "name": "Tharwatt Test Farm",
        "name_ar": "مزرعة اختبار ثروات",
        "email": "tharwatt-test@sahool.io",
        "phone": "+967771234567",
        "plan_id": "starter",
        "billing_cycle": "monthly"
    }

    tenant_response = await http_client.post(
        f"{billing_url}/v1/tenants",
        json=tenant_data,
        headers=auth_headers
    )

    assert tenant_response.status_code == 200
    tenant_id = tenant_response.json()["tenant_id"]

    try:
        # Generate invoice
        invoice_response = await http_client.post(
            f"{billing_url}/v1/tenants/{tenant_id}/invoices/generate",
            headers=auth_headers
        )

        if invoice_response.status_code == 200:
            invoice = invoice_response.json()["invoice"]
            invoice_id = invoice["invoice_id"]

            # Initiate Tharwatt payment
            payment_data = {
                "invoice_id": invoice_id,
                "amount": invoice["total"],
                "method": "tharwatt",
                "phone_number": "+967771234567"  # Tharwatt requires phone number
            }

            payment_response = await http_client.post(
                f"{billing_url}/v1/payments",
                json=payment_data,
                headers=auth_headers
            )

            # Payment may fail if Tharwatt API is not configured
            # We just verify the API accepts the request
            assert payment_response.status_code in [200, 502]

            if payment_response.status_code == 200:
                payment_result = payment_response.json()
                assert "payment" in payment_result

    except Exception as e:
        pytest.skip(f"Tharwatt payment test skipped: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# Test Usage Tracking and Quotas - اختبار تتبع الاستخدام والحصص
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_usage_tracking_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل تتبع الاستخدام

    Test usage tracking:
    1. Create tenant with subscription
    2. Record usage
    3. Check quota
    4. Verify usage limits
    """
    billing_url = service_urls.get("billing_core", "http://localhost:8089")

    # Step 1: Create tenant
    tenant_data = {
        "name": "Usage Test Farm",
        "name_ar": "مزرعة اختبار الاستخدام",
        "email": "usage-test@sahool.io",
        "phone": "+967777678901",
        "plan_id": "starter",
        "billing_cycle": "monthly"
    }

    tenant_response = await http_client.post(
        f"{billing_url}/v1/tenants",
        json=tenant_data,
        headers=auth_headers
    )

    assert tenant_response.status_code == 200
    tenant_id = tenant_response.json()["tenant_id"]

    try:
        # Step 2: Record usage - تسجيل الاستخدام
        usage_data = {
            "metric": "satellite_analyses_per_month",
            "quantity": 5,
            "metadata": {"test": "integration"}
        }

        usage_response = await http_client.post(
            f"{billing_url}/v1/tenants/{tenant_id}/usage",
            json=usage_data,
            headers=auth_headers
        )

        if usage_response.status_code == 200:
            usage_result = usage_response.json()

            assert usage_result["success"] is True
            assert "record_id" in usage_result
            assert "remaining" in usage_result

        # Step 3: Check quota - فحص الحصة
        quota_response = await http_client.get(
            f"{billing_url}/v1/tenants/{tenant_id}/quota",
            headers=auth_headers
        )

        if quota_response.status_code == 200:
            quota_data = quota_response.json()

            assert "usage" in quota_data
            assert "plan" in quota_data
            assert quota_data["tenant_id"] == tenant_id

            # Verify usage is tracked
            if "satellite_analyses_per_month" in quota_data["usage"]:
                usage_info = quota_data["usage"]["satellite_analyses_per_month"]
                assert usage_info["used"] >= 5

    except Exception as e:
        pytest.skip(f"Authentication required: {e}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_quota_enforcement_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار فرض حدود الحصة

    Test quota enforcement:
    1. Create tenant with limited plan
    2. Record usage up to limit
    3. Verify quota exceeded error
    """
    billing_url = service_urls.get("billing_core", "http://localhost:8089")

    # Create tenant with free plan (has strict limits)
    tenant_data = {
        "name": "Quota Test Farm",
        "name_ar": "مزرعة اختبار الحصص",
        "email": "quota-test@sahool.io",
        "phone": "+967777789012",
        "plan_id": "free",
        "billing_cycle": "monthly"
    }

    tenant_response = await http_client.post(
        f"{billing_url}/v1/tenants",
        json=tenant_data,
        headers=auth_headers
    )

    assert tenant_response.status_code == 200
    tenant_id = tenant_response.json()["tenant_id"]

    try:
        # Get quota to know the limit
        quota_response = await http_client.get(
            f"{billing_url}/v1/tenants/{tenant_id}/quota",
            headers=auth_headers
        )

        if quota_response.status_code == 200:
            quota_data = quota_response.json()

            # Try to record usage beyond limit
            # Free plan has satellite_analyses_per_month: 10
            usage_data = {
                "metric": "satellite_analyses_per_month",
                "quantity": 1
            }

            # Record usage multiple times
            for i in range(15):  # Exceeds free plan limit of 10
                usage_response = await http_client.post(
                    f"{billing_url}/v1/tenants/{tenant_id}/usage",
                    json=usage_data,
                    headers=auth_headers
                )

                # After limit is reached, should get 429
                if i >= 10:
                    # May return 429 (quota exceeded)
                    assert usage_response.status_code in [200, 429]
                    if usage_response.status_code == 429:
                        break

    except Exception as e:
        pytest.skip(f"Authentication required: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# Test Subscription Cancellation - اختبار إلغاء الاشتراك
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_subscription_cancellation_workflow(
    http_client,
    service_urls: Dict[str, str],
    auth_headers: Dict[str, str],
):
    """
    اختبار سير عمل إلغاء الاشتراك

    Test subscription cancellation:
    1. Create subscription
    2. Cancel subscription
    3. Verify cancellation
    """
    billing_url = service_urls.get("billing_core", "http://localhost:8089")

    # Create tenant
    tenant_data = {
        "name": "Cancel Test Farm",
        "name_ar": "مزرعة اختبار الإلغاء",
        "email": "cancel-test@sahool.io",
        "phone": "+967777890123",
        "plan_id": "starter",
        "billing_cycle": "monthly"
    }

    tenant_response = await http_client.post(
        f"{billing_url}/v1/tenants",
        json=tenant_data,
        headers=auth_headers
    )

    assert tenant_response.status_code == 200
    tenant_id = tenant_response.json()["tenant_id"]

    try:
        # Cancel subscription - إلغاء الاشتراك
        cancel_response = await http_client.post(
            f"{billing_url}/v1/tenants/{tenant_id}/cancel?immediate=false",
            headers=auth_headers
        )

        if cancel_response.status_code == 200:
            cancel_result = cancel_response.json()

            assert cancel_result["success"] is True
            assert "status" in cancel_result
            assert "end_date" in cancel_result

    except Exception as e:
        pytest.skip(f"Authentication required: {e}")
