# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Test fixtures for WhatsApp Bot Service.
fixtures اختبار لخدمة روبوت واتساب.
"""

import os
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

# Set test environment
os.environ["ENVIRONMENT"] = "test"
os.environ["WHATSAPP_TOKEN"] = "test_token"
os.environ["WHATSAPP_PHONE_ID"] = "123456789012345"
os.environ["WHATSAPP_VERIFY_TOKEN"] = "test_verify_token"
os.environ["LLM_ORCHESTRATOR_URL"] = "http://localhost:8220"
os.environ["VISION_SERVICE_URL"] = "http://localhost:8150"
os.environ["REDIS_URL"] = ""
os.environ["DATABASE_URL"] = ""
os.environ["NATS_URL"] = ""

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
# Clear cached src modules from other services to avoid cross-contamination in CI
_service_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _mod in list(sys.modules):
    if not (_mod == "src" or _mod.startswith("src.")):
        continue
    _mod_obj = sys.modules.get(_mod)
    _mod_file = getattr(_mod_obj, "__file__", None) or ""
    if not _mod_file or not os.path.abspath(_mod_file).startswith(_service_root):
        del sys.modules[_mod]
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
# Clear cached src modules from other services to avoid cross-contamination in CI
_service_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _mod in list(sys.modules):
    if not (_mod == "src" or _mod.startswith("src.")):
        continue
    _mod_obj = sys.modules.get(_mod)
    _mod_file = getattr(_mod_obj, "__file__", None) or ""
    if not _mod_file or not os.path.abspath(_mod_file).startswith(_service_root):
        del sys.modules[_mod]


@pytest.fixture
def anyio_backend():
    """Use asyncio for async tests."""
    return "asyncio"


@pytest.fixture
def mock_whatsapp_client():
    """Mock WhatsApp client."""
    client = MagicMock()
    client.is_configured = True
    client.send_text = AsyncMock(return_value="msg_123")
    client.send_image = AsyncMock(return_value="msg_124")
    client.send_location = AsyncMock(return_value="msg_125")
    client.send_interactive_buttons = AsyncMock(return_value="msg_126")
    client.send_interactive_list = AsyncMock(return_value="msg_127")
    client.send_template = AsyncMock(return_value="msg_128")
    client.mark_as_read = AsyncMock(return_value=True)
    client.download_media = AsyncMock(return_value=b"fake_image_data")
    return client


@pytest.fixture
def mock_session_manager():
    """Mock session manager."""
    from src.api.schemas import ConversationIntent, ConversationState, FarmerProfile, Language

    manager = MagicMock()

    # Create a default session
    profile = FarmerProfile(
        phone_number="967123456789",
        name="Test Farmer",
        language=Language.ARABIC,
    )
    session = ConversationState(
        phone_number="967123456789",
        session_id="test-session-123",
        profile=profile,
        language=Language.ARABIC,
        current_intent=ConversationIntent.UNKNOWN,
    )

    manager.get_session = AsyncMock(return_value=session)
    manager.create_session = AsyncMock(return_value=session)
    manager.save_session = AsyncMock(return_value=True)
    manager.delete_session = AsyncMock(return_value=True)

    return manager


@pytest.fixture
def mock_message_handler(mock_whatsapp_client, mock_session_manager):
    """Mock message handler."""
    from src.handlers.message_handler import MessageHandler

    handler = MessageHandler(
        whatsapp_client=mock_whatsapp_client,
        session_manager=mock_session_manager,
        llm_orchestrator_url="http://localhost:8220",
        vision_service_url="http://localhost:8150",
        default_language="ar",
    )

    return handler


@pytest.fixture
def sample_text_message():
    """Sample incoming text message."""
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123456789012345",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "967123456789",
                                "phone_number_id": "123456789012345",
                            },
                            "contacts": [
                                {
                                    "wa_id": "967123456789",
                                    "profile": {"name": "Test Farmer"},
                                }
                            ],
                            "messages": [
                                {
                                    "from": "967123456789",
                                    "id": "wamid.test123",
                                    "timestamp": "1704067200",
                                    "type": "text",
                                    "text": {"body": "مرحبا، كيف أسقي القمح؟"},
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }


@pytest.fixture
def sample_image_message():
    """Sample incoming image message."""
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123456789012345",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "967123456789",
                                "phone_number_id": "123456789012345",
                            },
                            "contacts": [
                                {
                                    "wa_id": "967123456789",
                                    "profile": {"name": "Test Farmer"},
                                }
                            ],
                            "messages": [
                                {
                                    "from": "967123456789",
                                    "id": "wamid.test124",
                                    "timestamp": "1704067200",
                                    "type": "image",
                                    "image": {
                                        "id": "media_123",
                                        "mime_type": "image/jpeg",
                                        "caption": "ما هذا المرض؟",
                                    },
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }


@pytest.fixture
def sample_location_message():
    """Sample incoming location message."""
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123456789012345",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "967123456789",
                                "phone_number_id": "123456789012345",
                            },
                            "contacts": [
                                {
                                    "wa_id": "967123456789",
                                    "profile": {"name": "Test Farmer"},
                                }
                            ],
                            "messages": [
                                {
                                    "from": "967123456789",
                                    "id": "wamid.test125",
                                    "timestamp": "1704067200",
                                    "type": "location",
                                    "location": {
                                        "latitude": 15.3694,
                                        "longitude": 44.1910,
                                        "name": "Sana'a, Yemen",
                                        "address": "Sana'a City",
                                    },
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }


@pytest.fixture
def sample_button_response():
    """Sample incoming button response."""
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123456789012345",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "967123456789",
                                "phone_number_id": "123456789012345",
                            },
                            "contacts": [
                                {
                                    "wa_id": "967123456789",
                                    "profile": {"name": "Test Farmer"},
                                }
                            ],
                            "messages": [
                                {
                                    "from": "967123456789",
                                    "id": "wamid.test126",
                                    "timestamp": "1704067200",
                                    "type": "interactive",
                                    "interactive": {
                                        "type": "button_reply",
                                        "button_reply": {
                                            "id": "btn_irrigation",
                                            "title": "الري",
                                        },
                                    },
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }


@pytest.fixture
def sample_status_update():
    """Sample status update webhook."""
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123456789012345",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "967123456789",
                                "phone_number_id": "123456789012345",
                            },
                            "statuses": [
                                {
                                    "id": "wamid.test123",
                                    "status": "delivered",
                                    "timestamp": "1704067300",
                                    "recipient_id": "967123456789",
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }
