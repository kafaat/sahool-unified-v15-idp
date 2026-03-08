# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
WhatsApp Cloud API Client.
عميل API واتساب السحابي.

Handles:
- Sending text messages
- Sending image messages
- Sending location messages
- Sending interactive buttons/lists
- Sending template messages
- Marking messages as read
- Downloading media
"""

from typing import Any

import httpx
import structlog

logger = structlog.get_logger(__name__)


class WhatsAppClient:
    """
    Client for WhatsApp Cloud API.
    عميل لـ API واتساب السحابي.
    """

    def __init__(
        self,
        access_token: str,
        phone_number_id: str,
        api_version: str = "v17.0",
    ):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{api_version}"
        self.messages_url = f"{self.base_url}/{phone_number_id}/messages"
        self.media_url = f"{self.base_url}/{phone_number_id}/media"

        self._http_client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )

    @property
    def is_configured(self) -> bool:
        """Check if WhatsApp is properly configured."""
        return bool(self.access_token and self.phone_number_id)

    async def send_text(
        self,
        to: str,
        text: str,
        preview_url: bool = False,
        context: dict[str, str] | None = None,
    ) -> str | None:
        """
        Send a text message.
        إرسال رسالة نصية.
        """
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self._format_phone(to),
            "type": "text",
            "text": {
                "body": text,
                "preview_url": preview_url,
            },
        }

        if context and "message_id" in context:
            payload["context"] = {"message_id": context["message_id"]}

        return await self._send_message(payload)

    async def send_image(
        self,
        to: str,
        image_url: str | None = None,
        image_id: str | None = None,
        caption: str | None = None,
        context: dict[str, str] | None = None,
    ) -> str | None:
        """
        Send an image message.
        إرسال رسالة صورة.
        """
        if not image_url and not image_id:
            logger.error("send_image_error", error="Either image_url or image_id is required")
            return None

        image_content = {}
        if image_id:
            image_content["id"] = image_id
        else:
            image_content["link"] = image_url

        if caption:
            image_content["caption"] = caption

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self._format_phone(to),
            "type": "image",
            "image": image_content,
        }

        if context and "message_id" in context:
            payload["context"] = {"message_id": context["message_id"]}

        return await self._send_message(payload)

    async def send_location(
        self,
        to: str,
        latitude: float,
        longitude: float,
        name: str | None = None,
        address: str | None = None,
        context: dict[str, str] | None = None,
    ) -> str | None:
        """
        Send a location message.
        إرسال رسالة موقع.
        """
        location_content = {
            "latitude": latitude,
            "longitude": longitude,
        }

        if name:
            location_content["name"] = name
        if address:
            location_content["address"] = address

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self._format_phone(to),
            "type": "location",
            "location": location_content,
        }

        if context and "message_id" in context:
            payload["context"] = {"message_id": context["message_id"]}

        return await self._send_message(payload)

    async def send_interactive(
        self,
        to: str,
        interactive_type: str,
        body_text: str,
        header: Any | None = None,
        footer: Any | None = None,
        action: Any | None = None,
        context: dict[str, str] | None = None,
    ) -> str | None:
        """
        Send an interactive message (buttons or list).
        إرسال رسالة تفاعلية (أزرار أو قائمة).
        """
        interactive_content = {
            "type": interactive_type,
            "body": {"text": body_text},
        }

        if header:
            if hasattr(header, "dict"):
                interactive_content["header"] = header.dict(exclude_none=True)
            else:
                interactive_content["header"] = header

        if footer:
            if hasattr(footer, "dict"):
                interactive_content["footer"] = footer.dict(exclude_none=True)
            else:
                interactive_content["footer"] = footer

        if action:
            if hasattr(action, "dict"):
                interactive_content["action"] = action.dict(exclude_none=True)
            else:
                interactive_content["action"] = action

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self._format_phone(to),
            "type": "interactive",
            "interactive": interactive_content,
        }

        if context and "message_id" in context:
            payload["context"] = {"message_id": context["message_id"]}

        return await self._send_message(payload)

    async def send_interactive_buttons(
        self,
        to: str,
        body_text: str,
        buttons: list[dict[str, str]],
        header_text: str | None = None,
        footer_text: str | None = None,
    ) -> str | None:
        """
        Send an interactive button message (max 3 buttons).
        إرسال رسالة أزرار تفاعلية (حد أقصى 3 أزرار).
        """
        if len(buttons) > 3:
            logger.warning("too_many_buttons", count=len(buttons))
            buttons = buttons[:3]

        interactive_content: dict[str, Any] = {
            "type": "button",
            "body": {"text": body_text},
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": btn["id"],
                            "title": btn["title"][:20],  # Max 20 chars
                        },
                    }
                    for btn in buttons
                ],
            },
        }

        if header_text:
            interactive_content["header"] = {"type": "text", "text": header_text}

        if footer_text:
            interactive_content["footer"] = {"text": footer_text}

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self._format_phone(to),
            "type": "interactive",
            "interactive": interactive_content,
        }

        return await self._send_message(payload)

    async def send_interactive_list(
        self,
        to: str,
        body_text: str,
        button_text: str,
        sections: list[dict[str, Any]],
        header_text: str | None = None,
        footer_text: str | None = None,
    ) -> str | None:
        """
        Send an interactive list message.
        إرسال رسالة قائمة تفاعلية.
        """
        interactive_content: dict[str, Any] = {
            "type": "list",
            "body": {"text": body_text},
            "action": {
                "button": button_text,
                "sections": sections,
            },
        }

        if header_text:
            interactive_content["header"] = {"type": "text", "text": header_text}

        if footer_text:
            interactive_content["footer"] = {"text": footer_text}

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self._format_phone(to),
            "type": "interactive",
            "interactive": interactive_content,
        }

        return await self._send_message(payload)

    async def send_template(
        self,
        to: str,
        template_name: str,
        language_code: str = "ar",
        components: list[dict[str, Any]] | None = None,
    ) -> str | None:
        """
        Send a template message.
        إرسال رسالة قالب.
        """
        template_content = {
            "name": template_name,
            "language": {"code": language_code},
        }

        if components:
            template_content["components"] = components

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self._format_phone(to),
            "type": "template",
            "template": template_content,
        }

        return await self._send_message(payload)

    async def mark_as_read(self, message_id: str) -> bool:
        """
        Mark a message as read.
        وضع علامة مقروء على الرسالة.
        """
        try:
            payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id,
            }

            response = await self._http_client.post(self.messages_url, json=payload)

            if response.status_code == 200:
                logger.debug("message_marked_read", message_id=message_id)
                return True
            else:
                logger.warning(
                    "mark_read_failed",
                    status_code=response.status_code,
                    response=response.text,
                )
                return False

        except Exception as e:
            logger.error("mark_read_error", error=str(e), message_id=message_id)
            return False

    async def download_media(self, media_id: str) -> bytes | None:
        """
        Download media (image, video, etc.) from WhatsApp.
        تحميل الوسائط (صورة، فيديو، إلخ) من واتساب.
        """
        try:
            # First, get the media URL
            media_info_url = f"{self.base_url}/{media_id}"
            response = await self._http_client.get(media_info_url)

            if response.status_code != 200:
                logger.error(
                    "get_media_url_failed",
                    status_code=response.status_code,
                    media_id=media_id,
                )
                return None

            data = response.json()
            media_url = data.get("url")

            if not media_url:
                logger.error("media_url_not_found", media_id=media_id)
                return None

            # Download the media
            media_response = await self._http_client.get(media_url)

            if media_response.status_code == 200:
                logger.info("media_downloaded", media_id=media_id, size=len(media_response.content))
                return media_response.content
            else:
                logger.error(
                    "media_download_failed",
                    status_code=media_response.status_code,
                    media_id=media_id,
                )
                return None

        except Exception as e:
            logger.error("media_download_error", error=str(e), media_id=media_id)
            return None

    async def upload_media(
        self,
        media_data: bytes,
        mime_type: str,
        filename: str = "media",
    ) -> str | None:
        """
        Upload media to WhatsApp.
        رفع الوسائط إلى واتساب.
        """
        try:
            files = {
                "file": (filename, media_data, mime_type),
            }
            data = {
                "messaging_product": "whatsapp",
                "type": mime_type,
            }

            # Use form data for upload
            response = await self._http_client.post(
                self.media_url,
                files=files,
                data=data,
            )

            if response.status_code == 200:
                result = response.json()
                media_id = result.get("id")
                logger.info("media_uploaded", media_id=media_id)
                return media_id
            else:
                logger.error(
                    "media_upload_failed",
                    status_code=response.status_code,
                    response=response.text,
                )
                return None

        except Exception as e:
            logger.error("media_upload_error", error=str(e))
            return None

    async def _send_message(self, payload: dict) -> str | None:
        """
        Send message to WhatsApp API.
        إرسال رسالة إلى API واتساب.
        """
        if not self.is_configured:
            logger.warning("whatsapp_not_configured")
            return None

        try:
            response = await self._http_client.post(self.messages_url, json=payload)

            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                if messages:
                    message_id = messages[0].get("id")
                    logger.info(
                        "message_sent",
                        to=payload.get("to", "")[-4:] + "...",
                        type=payload.get("type"),
                        message_id=message_id,
                    )
                    return message_id
                return None
            else:
                error_data = (
                    response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                )
                error = error_data.get("error", {})
                logger.error(
                    "send_message_failed",
                    status_code=response.status_code,
                    error_code=error.get("code"),
                    error_message=error.get("message"),
                    to=payload.get("to", "")[-4:] + "...",
                )
                return None

        except httpx.TimeoutException:
            logger.error("send_message_timeout", to=payload.get("to", "")[-4:] + "...")
            return None

        except Exception as e:
            logger.error("send_message_error", error=str(e))
            return None

    def _format_phone(self, phone: str) -> str:
        """
        Format phone number for WhatsApp API.
        تنسيق رقم الهاتف لـ API واتساب.
        """
        # Remove any non-digit characters except +
        phone = "".join(c for c in phone if c.isdigit() or c == "+")

        # Remove leading + if present
        if phone.startswith("+"):
            phone = phone[1:]

        return phone

    async def close(self) -> None:
        """Close HTTP client."""
        await self._http_client.aclose()
