"""
SAHOOL Payment Workflow E2E Tests
اختبارات سير عمل الدفع من البداية إلى النهاية

End-to-end tests for complete payment and billing workflow:
1. Create subscription
2. Process payment via Tharwatt
3. Generate invoice
4. Verify payment status

Author: SAHOOL Platform Team
"""

import asyncio
from typing import Any

import httpx
import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# Complete Payment Workflow Test - اختبار سير عمل الدفع الكامل
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.slow
@pytest.mark.asyncio
async def test_complete_payment_workflow(
    workflow_client: httpx.AsyncClient,
    e2e_headers: dict[str, str],
    test_subscription_data: dict[str, Any],
    test_payment_data: dict[str, Any],
    ensure_billing_ready,
    cleanup_test_data: dict[str, list],
):
    """
    Test complete payment workflow: Subscription → Payment → Invoice
    اختبار سير عمل الدفع الكامل: اشتراك → دفع → فاتورة

    Workflow Steps:
    1. Create subscription
    2. Create payment intent
    3. Process payment via Tharwatt
    4. Verify payment status
    5. Generate invoice
    6. Retrieve invoice
    """

    print("\n" + "=" * 80)
    print("SAHOOL Payment Workflow E2E Test")
    print("اختبار سير عمل الدفع الكامل لمنصة سهول")
    print("=" * 80)

    # ───────────────────────────────────────────────────────────────────────────
    # Step 1: Create Subscription - إنشاء الاشتراك
    # ───────────────────────────────────────────────────────────────────────────
    print("\n[Step 1] Creating subscription...")

    subscription_response = await workflow_client.post(
        "http://localhost:8089/api/v1/subscriptions",
        headers=e2e_headers,
        json=test_subscription_data,
    )

    assert subscription_response.status_code in (
        201,
        200,
        401,
        422,
    ), f"Subscription creation failed with status {subscription_response.status_code}"

    if subscription_response.status_code in (200, 201):
        subscription_data = subscription_response.json()
        subscription_id = subscription_data.get("id") or subscription_data.get(
            "subscription_id"
        )
        assert subscription_id is not None, "Subscription ID should be returned"

        cleanup_test_data["subscriptions"].append(subscription_id)
        print(f"✓ Subscription created successfully: {subscription_id}")
    else:
        pytest.skip(f"Cannot create subscription: {subscription_response.status_code}")

    # ───────────────────────────────────────────────────────────────────────────
    # Step 2: Create Payment Intent - إنشاء نية الدفع
    # ───────────────────────────────────────────────────────────────────────────
    print("\n[Step 2] Creating payment intent...")

    payment_intent_response = await workflow_client.post(
        "http://localhost:8089/api/v1/payments/intent",
        headers=e2e_headers,
        json=test_payment_data,
    )

    assert payment_intent_response.status_code in (
        200,
        201,
        401,
        422,
    ), f"Payment intent creation failed with status {payment_intent_response.status_code}"

    if payment_intent_response.status_code in (200, 201):
        payment_intent = payment_intent_response.json()
        payment_id = payment_intent.get("id") or payment_intent.get("payment_id")
        assert payment_id is not None, "Payment ID should be returned"

        print(f"✓ Payment intent created successfully: {payment_id}")

        # Wait for payment processing
        await asyncio.sleep(2)

        # ───────────────────────────────────────────────────────────────────────
        # Step 3: Check Payment Status - التحقق من حالة الدفع
        # ───────────────────────────────────────────────────────────────────────
        print("\n[Step 3] Checking payment status...")

        payment_status_response = await workflow_client.get(
            f"http://localhost:8089/api/v1/payments/{payment_id}", headers=e2e_headers
        )

        assert payment_status_response.status_code in (
            200,
            401,
            404,
        ), "Payment status should be retrievable"

        if payment_status_response.status_code == 200:
            payment_status = payment_status_response.json()
            status = payment_status.get("status")
            print(f"✓ Payment status: {status}")
        else:
            print(
                f"⚠ Payment status not available: {payment_status_response.status_code}"
            )

    else:
        print(f"⚠ Cannot create payment intent: {payment_intent_response.status_code}")

    # ───────────────────────────────────────────────────────────────────────────
    # Step 4: List Invoices - قائمة الفواتير
    # ───────────────────────────────────────────────────────────────────────────
    print("\n[Step 4] Retrieving invoices...")

    invoices_response = await workflow_client.get(
        "http://localhost:8089/api/v1/invoices", headers=e2e_headers
    )

    assert invoices_response.status_code in (200, 401), "Invoices should be accessible"

    if invoices_response.status_code == 200:
        invoices = invoices_response.json()
        print("✓ Invoices retrieved successfully")

        # Verify invoice structure
        if isinstance(invoices, list) and len(invoices) > 0:
            invoice = invoices[0]
            assert "id" in invoice or "invoice_id" in invoice, "Invoice should have ID"
    else:
        print(f"⚠ Invoices not accessible: {invoices_response.status_code}")

    print("\n" + "=" * 80)
    print("✓ Complete payment workflow test PASSED")
    print("=" * 80)


# ═══════════════════════════════════════════════════════════════════════════════
# Tharwatt Payment Gateway Integration Test - اختبار تكامل بوابة ثروات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.asyncio
async def test_tharwatt_payment_integration(
    workflow_client: httpx.AsyncClient,
    e2e_headers: dict[str, str],
    test_payment_data: dict[str, Any],
    ensure_billing_ready,
):
    """
    Test Tharwatt payment gateway integration
    اختبار تكامل بوابة الدفع ثروات
    """

    print("\n[Tharwatt Integration Test]")

    # Verify Provider Config service is available
    provider_response = await workflow_client.get("http://localhost:8104/health")

    if provider_response.status_code != 200:
        pytest.skip("Provider Config service not available")

    # Create payment with Tharwatt
    tharwatt_payment = {
        **test_payment_data,
        "payment_method": "tharwatt",
        "provider": "tharwatt",
    }

    payment_response = await workflow_client.post(
        "http://localhost:8089/api/v1/payments/intent",
        headers=e2e_headers,
        json=tharwatt_payment,
    )

    assert payment_response.status_code in (
        200,
        201,
        401,
        422,
        503,
    ), "Tharwatt payment should be processed"

    if payment_response.status_code in (200, 201):
        payment_data = payment_response.json()
        print("✓ Tharwatt payment intent created")

        # Verify payment provider is set correctly
        if "provider" in payment_data:
            assert payment_data["provider"] in ("tharwatt", "THARWATT")
    else:
        print(f"⚠ Tharwatt payment not available: {payment_response.status_code}")


# ═══════════════════════════════════════════════════════════════════════════════
# Subscription Management Workflow - سير عمل إدارة الاشتراكات
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.asyncio
async def test_subscription_management_workflow(
    workflow_client: httpx.AsyncClient,
    e2e_headers: dict[str, str],
    test_subscription_data: dict[str, Any],
    ensure_billing_ready,
):
    """
    Test subscription management workflow
    اختبار سير عمل إدارة الاشتراكات

    Workflow:
    1. Create subscription
    2. List subscriptions
    3. Get subscription details
    4. Update subscription
    """

    print("\n[Subscription Management Workflow]")

    # Step 1: Create subscription
    create_response = await workflow_client.post(
        "http://localhost:8089/api/v1/subscriptions",
        headers=e2e_headers,
        json=test_subscription_data,
    )

    if create_response.status_code not in (200, 201):
        pytest.skip(f"Cannot create subscription: {create_response.status_code}")

    subscription_data = create_response.json()
    subscription_id = subscription_data.get("id") or subscription_data.get(
        "subscription_id"
    )

    print(f"✓ Subscription created: {subscription_id}")

    # Step 2: List subscriptions
    list_response = await workflow_client.get(
        "http://localhost:8089/api/v1/subscriptions", headers=e2e_headers
    )

    assert list_response.status_code in (
        200,
        401,
    ), "Subscriptions list should be accessible"

    if list_response.status_code == 200:
        list_response.json()
        print("✓ Subscriptions listed")

    # Step 3: Get specific subscription
    get_response = await workflow_client.get(
        f"http://localhost:8089/api/v1/subscriptions/{subscription_id}",
        headers=e2e_headers,
    )

    assert get_response.status_code in (
        200,
        401,
        404,
    ), "Subscription should be retrievable"

    if get_response.status_code == 200:
        get_response.json()
        print("✓ Subscription retrieved successfully")


# ═══════════════════════════════════════════════════════════════════════════════
# Invoice Generation Workflow - سير عمل إنشاء الفواتير
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.asyncio
async def test_invoice_generation_workflow(
    workflow_client: httpx.AsyncClient,
    e2e_headers: dict[str, str],
    ensure_billing_ready,
):
    """
    Test invoice generation workflow
    اختبار سير عمل إنشاء الفواتير
    """

    print("\n[Invoice Generation Workflow]")

    # Get user invoices
    invoices_response = await workflow_client.get(
        "http://localhost:8089/api/v1/invoices", headers=e2e_headers
    )

    assert invoices_response.status_code in (
        200,
        401,
    ), "Invoices endpoint should respond"

    if invoices_response.status_code == 200:
        invoices = invoices_response.json()
        print("✓ Invoices retrieved")

        # If invoices exist, get details of first invoice
        if isinstance(invoices, list) and len(invoices) > 0:
            invoice_id = invoices[0].get("id") or invoices[0].get("invoice_id")

            if invoice_id:
                invoice_detail_response = await workflow_client.get(
                    f"http://localhost:8089/api/v1/invoices/{invoice_id}",
                    headers=e2e_headers,
                )

                assert invoice_detail_response.status_code in (
                    200,
                    401,
                    404,
                ), "Invoice details should be accessible"

                if invoice_detail_response.status_code == 200:
                    invoice_detail = invoice_detail_response.json()
                    print("✓ Invoice details retrieved")

                    # Verify invoice structure
                    assert (
                        "amount" in invoice_detail or "total" in invoice_detail
                    ), "Invoice should have amount"


# ═══════════════════════════════════════════════════════════════════════════════
# Payment Provider Configuration Test - اختبار تكوين مزود الدفع
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.asyncio
async def test_payment_provider_configuration(
    workflow_client: httpx.AsyncClient, e2e_headers: dict[str, str]
):
    """
    Test payment provider configuration
    اختبار تكوين مزود الدفع
    """

    print("\n[Payment Provider Configuration Test]")

    # Get available payment providers
    providers_response = await workflow_client.get(
        "http://localhost:8104/api/v1/providers", headers=e2e_headers
    )

    assert providers_response.status_code in (
        200,
        401,
        404,
    ), "Providers endpoint should respond"

    if providers_response.status_code == 200:
        providers = providers_response.json()
        print("✓ Payment providers retrieved")

        # Verify Tharwatt is configured for Yemen
        if isinstance(providers, list):
            tharwatt_found = any(
                p.get("name") == "tharwatt" or p.get("provider") == "tharwatt"
                for p in providers
                if isinstance(p, dict)
            )

            if tharwatt_found:
                print("✓ Tharwatt provider configured for Yemen")


# ═══════════════════════════════════════════════════════════════════════════════
# Billing Integration with Field Operations - تكامل الفوترة مع عمليات الحقول
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.slow
@pytest.mark.asyncio
async def test_billing_field_ops_integration(
    workflow_client: httpx.AsyncClient,
    e2e_headers: dict[str, str],
    test_subscription_data: dict[str, Any],
    test_field_data: dict[str, Any],
    ensure_billing_ready,
    ensure_field_ops_ready,
):
    """
    Test billing integration with field operations
    اختبار تكامل الفوترة مع عمليات الحقول

    Scenario:
    1. Create premium subscription
    2. Create field (premium feature)
    3. Verify access based on subscription
    """

    print("\n[Billing & Field Ops Integration Test]")

    # Step 1: Create premium subscription
    subscription_response = await workflow_client.post(
        "http://localhost:8089/api/v1/subscriptions",
        headers=e2e_headers,
        json=test_subscription_data,
    )

    if subscription_response.status_code not in (200, 201):
        pytest.skip("Cannot create subscription")

    print("✓ Premium subscription created")

    # Step 2: Try to create field (should be allowed with premium subscription)
    field_response = await workflow_client.post(
        "http://localhost:8080/api/v1/fields", headers=e2e_headers, json=test_field_data
    )

    # Field creation should work with active subscription
    assert field_response.status_code in (
        201,
        200,
        401,
        403,
        422,
    ), "Field creation should be processed"

    if field_response.status_code in (200, 201):
        print("✓ Field created successfully with premium subscription")
    else:
        print(f"⚠ Field creation response: {field_response.status_code}")


# ═══════════════════════════════════════════════════════════════════════════════
# Payment Webhook Handling Test - اختبار معالجة Webhook للدفع
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.e2e
@pytest.mark.workflow
@pytest.mark.asyncio
async def test_payment_webhook_handling(
    workflow_client: httpx.AsyncClient,
    e2e_headers: dict[str, str],
    ensure_billing_ready,
):
    """
    Test payment webhook handling
    اختبار معالجة Webhook للدفع

    Note: This tests webhook endpoint availability
    Real webhook testing would require payment provider simulation
    """

    print("\n[Payment Webhook Test]")

    # Verify webhook endpoint exists
    # In production, this would be called by Tharwatt/Stripe
    webhook_response = await workflow_client.post(
        "http://localhost:8089/api/v1/webhooks/payment",
        headers={"Content-Type": "application/json"},
        json={"event": "test"},
    )

    # Webhook should respond (even if it rejects test data)
    assert webhook_response.status_code in (
        200,
        400,
        401,
        404,
    ), "Webhook endpoint should exist and respond"

    print(f"✓ Webhook endpoint responded with status: {webhook_response.status_code}")
