# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
WhatsApp Webhook Endpoints
نقاط نهاية webhook لواتساب

Handles:
- Webhook verification (GET /webhook)
- Incoming message processing (POST /webhook)
- Send message API (POST /api/v1/send)
- Send template API (POST /api/v1/send-template)
"""

import hashlib
import hmac

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Query, Request, Response

from ...core.config import settings

# Authentication guard - requires valid JWT for send/template/mark-read endpoints
try:
    from shared.auth.dependencies import get_current_user
except ImportError:

    async def get_current_user():  # type: ignore[misc]
        """Fail-closed when shared auth is not available."""
        raise HTTPException(
            status_code=503,
            detail="Auth module unavailable | وحدة المصادقة غير متوفرة",
        )


from ..schemas import (
    SendMessageRequest,
    SendMessageResponse,
    SendTemplateRequest,
    WhatsAppWebhookPayload,
)

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["WhatsApp Webhook"])


def _verify_meta_signature(body: bytes, signature_header: str | None) -> bool:
    """
    Verify the X-Hub-Signature-256 header sent by Meta.
    التحقق من رأس X-Hub-Signature-256 المرسل من Meta.

    Meta signs all webhook payloads with HMAC-SHA256 using the App Secret.
    يوقّع Meta جميع حمولات webhook بـ HMAC-SHA256 باستخدام سر التطبيق.

    Returns True when:
    - app_secret is not configured (dev/test mode – allows all)
    - signature matches HMAC-SHA256(app_secret, body)

    Returns False (reject) when:
    - app_secret IS configured but the header is absent or does not match.
    """
    app_secret = settings.whatsapp_app_secret
    if not app_secret:
        # Secret not configured: skip enforcement (dev/test only).
        # Log a warning so operators notice in production.
        logger.warning(
            "whatsapp_app_secret_not_set",
            message="HMAC signature verification is DISABLED – set WHATSAPP_APP_SECRET in production",
        )
        return True

    if not signature_header:
        logger.warning("webhook_signature_missing", detail="X-Hub-Signature-256 header absent")
        return False

    # Header format: "sha256=<hex_digest>"
    if not signature_header.startswith("sha256="):
        logger.warning("webhook_signature_bad_format", header=signature_header[:20])
        return False

    expected = hmac.new(
        app_secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()

    received = signature_header[len("sha256="):]
    # Use constant-time comparison to prevent timing attacks.
    if not hmac.compare_digest(expected, received):
        logger.warning("webhook_signature_mismatch")
        return False

    return True


# ============================================================================
# Webhook Verification Endpoint
# ============================================================================


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str | None = Query(None, alias="hub.mode"),
    hub_verify_token: str | None = Query(None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(None, alias="hub.challenge"),
):
    """
    WhatsApp webhook verification endpoint.
    نقطة التحقق من webhook لواتساب.

    Meta sends this request when you configure the webhook URL.
    يرسل Meta هذا الطلب عند تكوين رابط webhook.
    """
    logger.info(
        "webhook_verification_request",
        mode=hub_mode,
        has_token=hub_verify_token is not None,
        has_challenge=hub_challenge is not None,
    )

    # Verify the webhook subscription (reject if verify token is unconfigured)
    if (
        hub_mode == "subscribe"
        and settings.whatsapp_verify_token
        and hub_verify_token == settings.whatsapp_verify_token
    ):
        logger.info("webhook_verification_success")
        # Must return the challenge as plain text
        return Response(content=hub_challenge, media_type="text/plain")

    logger.warning(
        "webhook_verification_failed",
        expected_token=(settings.whatsapp_verify_token[:8] + "...") if settings.whatsapp_verify_token else None,
        received_token=hub_verify_token[:8] + "..." if hub_verify_token else None,
    )
    raise HTTPException(
        status_code=403,
        detail="Verification token mismatch | عدم تطابق رمز التحقق",
    )


# ============================================================================
# Webhook Message Handler Endpoint
# ============================================================================


@router.post("/webhook")
async def receive_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str | None = Header(None, alias="X-Hub-Signature-256"),
):
    """
    Receive incoming WhatsApp messages and status updates.
    استقبال رسائل واتساب الواردة وتحديثات الحالة.

    This endpoint:
    1. Verifies the X-Hub-Signature-256 HMAC signature from Meta
    2. Validates the webhook payload
    3. Extracts messages from the payload
    4. Processes messages asynchronously via background tasks
    5. Returns 200 OK immediately (WhatsApp requirement)
    """
    # ── Step 1: Read the raw body for HMAC verification ───────────────────────
    body = await request.body()

    # ── Step 2: Verify Meta HMAC signature ────────────────────────────────────
    if not _verify_meta_signature(body, x_hub_signature_256):
        logger.warning(
            "webhook_signature_rejected",
            remote=request.client.host if request.client else "unknown",
        )
        # Return 403; do NOT silently swallow – callers must send valid signatures.
        raise HTTPException(
            status_code=403,
            detail="Invalid webhook signature | توقيع webhook غير صالح",
        )

    try:
        # Parse the webhook payload
        import json as _json

        body_dict = _json.loads(body)
        logger.debug("webhook_received", payload_keys=list(body_dict.keys()))

        # Validate and parse payload
        payload = WhatsAppWebhookPayload(**body_dict)

        # Process each entry
        for entry in payload.entry:
            for change in entry.changes:
                if change.field != "messages":
                    continue

                value = change.value

                # Process status updates
                if value.statuses:
                    for status in value.statuses:
                        logger.info(
                            "message_status_update",
                            message_id=status.id,
                            status=status.status,
                            recipient=status.recipient_id[-4:] + "...",
                        )

                # Process incoming messages
                if value.messages:
                    message_handler = request.app.state.message_handler

                    for message in value.messages:
                        # Get sender info from contacts
                        sender_name = None
                        if value.contacts:
                            for contact in value.contacts:
                                if contact.wa_id == message.from_:
                                    sender_name = contact.profile.get("name") if contact.profile else None
                                    break

                        logger.info(
                            "message_received",
                            from_number=message.from_[-4:] + "...",
                            message_type=message.type.value,
                            message_id=message.id,
                            sender_name=sender_name,
                        )

                        # Process message in background to return 200 quickly
                        background_tasks.add_task(
                            message_handler.handle_message,
                            message=message,
                            sender_name=sender_name,
                            metadata=value.metadata,
                        )

        # WhatsApp requires 200 OK response within 20 seconds
        return {"status": "received"}

    except Exception as e:
        logger.error("webhook_processing_error", error=str(e))
        # Still return 200 to prevent WhatsApp from retrying
        # Don't expose exception details to external users
        return {"status": "error", "message": "Processing error"}


# ============================================================================
# Send Message API
# ============================================================================


@router.post("/api/v1/send", response_model=SendMessageResponse)
async def send_message(
    request: Request,
    message_request: SendMessageRequest,
    _current_user=Depends(get_current_user),
):
    """
    Send a message to a WhatsApp user.
    إرسال رسالة إلى مستخدم واتساب.

    Supports:
    - Text messages | رسائل نصية
    - Image messages | رسائل صور
    - Location messages | رسائل مواقع
    - Interactive buttons | أزرار تفاعلية
    """
    try:
        whatsapp_client = request.app.state.whatsapp_client

        if not whatsapp_client.is_configured:
            return SendMessageResponse(
                success=False,
                error="WhatsApp not configured",
                error_ar="واتساب غير مكون",
            )

        # Send based on message type
        message_id = None

        if message_request.type.value == "text" and message_request.text:
            message_id = await whatsapp_client.send_text(
                to=message_request.to,
                text=message_request.text.body,
                preview_url=message_request.text.preview_url,
                context=message_request.context,
            )

        elif message_request.type.value == "image" and message_request.image:
            message_id = await whatsapp_client.send_image(
                to=message_request.to,
                image_url=message_request.image.link,
                image_id=message_request.image.id,
                caption=message_request.image.caption,
                context=message_request.context,
            )

        elif message_request.type.value == "location" and message_request.location:
            message_id = await whatsapp_client.send_location(
                to=message_request.to,
                latitude=message_request.location.latitude,
                longitude=message_request.location.longitude,
                name=message_request.location.name,
                address=message_request.location.address,
                context=message_request.context,
            )

        elif message_request.type.value == "interactive" and message_request.interactive:
            message_id = await whatsapp_client.send_interactive(
                to=message_request.to,
                interactive_type=message_request.interactive.type.value,
                body_text=message_request.interactive.body.text,
                header=message_request.interactive.header,
                footer=message_request.interactive.footer,
                action=message_request.interactive.action,
                context=message_request.context,
            )

        else:
            return SendMessageResponse(
                success=False,
                error=f"Unsupported message type: {message_request.type.value}",
                error_ar=f"نوع رسالة غير مدعوم: {message_request.type.value}",
            )

        if message_id:
            logger.info(
                "message_sent",
                to=message_request.to[-4:] + "...",
                type=message_request.type.value,
                message_id=message_id,
            )
            return SendMessageResponse(success=True, message_id=message_id)
        else:
            return SendMessageResponse(
                success=False,
                error="Failed to send message",
                error_ar="فشل في إرسال الرسالة",
            )

    except Exception as e:
        logger.error("send_message_error", error=str(e))
        return SendMessageResponse(
            success=False,
            error=str(e),
            error_ar="حدث خطأ أثناء إرسال الرسالة",
        )


# ============================================================================
# Send Template Message API
# ============================================================================


@router.post("/api/v1/send-template", response_model=SendMessageResponse)
async def send_template_message(
    request: Request,
    template_request: SendTemplateRequest,
    _current_user=Depends(get_current_user),
):
    """
    Send a template message to a WhatsApp user.
    إرسال رسالة قالب إلى مستخدم واتساب.

    Template messages are pre-approved messages that can be sent
    outside the 24-hour messaging window.
    رسائل القوالب هي رسائل معتمدة مسبقا يمكن إرسالها
    خارج نافذة الرسائل لمدة 24 ساعة.
    """
    try:
        whatsapp_client = request.app.state.whatsapp_client

        if not whatsapp_client.is_configured:
            return SendMessageResponse(
                success=False,
                error="WhatsApp not configured",
                error_ar="واتساب غير مكون",
            )

        # Build components for the template
        components = None
        if template_request.components:
            components = [
                {
                    "type": comp.type,
                    "parameters": comp.parameters,
                }
                for comp in template_request.components
            ]

        message_id = await whatsapp_client.send_template(
            to=template_request.to,
            template_name=template_request.template_name,
            language_code=template_request.language_code,
            components=components,
        )

        if message_id:
            logger.info(
                "template_sent",
                to=template_request.to[-4:] + "...",
                template=template_request.template_name,
                message_id=message_id,
            )
            return SendMessageResponse(success=True, message_id=message_id)
        else:
            return SendMessageResponse(
                success=False,
                error="Failed to send template message",
                error_ar="فشل في إرسال رسالة القالب",
            )

    except Exception as e:
        logger.error("send_template_error", error=str(e))
        return SendMessageResponse(
            success=False,
            error=str(e),
            error_ar="حدث خطأ أثناء إرسال رسالة القالب",
        )


# ============================================================================
# Mark as Read API
# ============================================================================


@router.post("/api/v1/mark-read")
async def mark_message_as_read(
    request: Request,
    message_id: str = Query(..., description="Message ID to mark as read"),
    _current_user=Depends(get_current_user),
):
    """
    Mark a message as read.
    وضع علامة مقروء على الرسالة.
    """
    try:
        whatsapp_client = request.app.state.whatsapp_client

        if not whatsapp_client.is_configured:
            raise HTTPException(
                status_code=503,
                detail="WhatsApp not configured | واتساب غير مكون",
            )

        success = await whatsapp_client.mark_as_read(message_id)

        if success:
            return {"success": True, "message_id": message_id}
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to mark message as read | فشل في وضع علامة مقروء",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("mark_read_error", error=str(e), message_id=message_id)
        raise HTTPException(status_code=500, detail=str(e))
