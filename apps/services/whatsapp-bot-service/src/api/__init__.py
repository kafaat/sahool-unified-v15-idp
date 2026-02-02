# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""API module for WhatsApp Bot Service."""

from .schemas import (
    ConversationState,
    SendMessageRequest,
    SendMessageResponse,
    WhatsAppContact,
    WhatsAppMessage,
    WhatsAppWebhookPayload,
)

__all__ = [
    "ConversationState",
    "SendMessageRequest",
    "SendMessageResponse",
    "WhatsAppContact",
    "WhatsAppMessage",
    "WhatsAppWebhookPayload",
]
