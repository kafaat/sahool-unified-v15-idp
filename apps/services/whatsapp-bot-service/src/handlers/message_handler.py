# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Message Handler for WhatsApp Bot Service.
معالج الرسائل لخدمة روبوت واتساب.

Handles:
- Text messages (forward to LLM orchestrator)
- Image messages (forward to vision service)
- Location messages
- Button/Interactive responses
- Language detection and switching
"""

import re
from typing import TYPE_CHECKING

import httpx
import structlog

from ..api.schemas import (
    ConversationIntent,
    ConversationState,
    Language,
    MessageType,
    WhatsAppMessage,
    WhatsAppMetadata,
)
from .response_builder import ResponseBuilder

if TYPE_CHECKING:
    from ..utils.session_manager import SessionManager
    from ..utils.whatsapp_client import WhatsAppClient

logger = structlog.get_logger(__name__)

# Arabic text patterns for intent detection
ARABIC_PATTERNS = {
    ConversationIntent.GREETING: [
        r"مرحبا",
        r"السلام",
        r"أهلا",
        r"صباح",
        r"مساء",
        r"هاي",
    ],
    ConversationIntent.CROP_DISEASE: [
        r"مرض",
        r"أمراض",
        r"آفة",
        r"إصابة",
        r"اصفرار",
        r"ذبول",
        r"تبقع",
        r"عفن",
        r"صدأ",
    ],
    ConversationIntent.IRRIGATION: [
        r"ري",
        r"سقي",
        r"ماء",
        r"رطوبة",
        r"جفاف",
    ],
    ConversationIntent.FERTILIZER: [
        r"سماد",
        r"تسميد",
        r"نيتروجين",
        r"فوسفور",
        r"بوتاسيوم",
        r"يوريا",
    ],
    ConversationIntent.PEST_DETECTION: [
        r"حشر",
        r"آفة",
        r"دود",
        r"سوسة",
        r"ذبابة",
        r"من",
    ],
    ConversationIntent.WEATHER: [
        r"طقس",
        r"جو",
        r"حرارة",
        r"مطر",
        r"رياح",
        r"رطوبة الجو",
    ],
    ConversationIntent.MENU: [
        r"قائمة",
        r"خيارات",
        r"بداية",
        r"رجوع",
    ],
    ConversationIntent.HELP: [
        r"مساعدة",
        r"كيف",
        r"ماذا",
        r"شرح",
    ],
    ConversationIntent.LANGUAGE_SWITCH: [
        r"إنجليزي",
        r"عربي",
        r"لغة",
        r"english",
        r"arabic",
    ],
}

# English text patterns for intent detection
ENGLISH_PATTERNS = {
    ConversationIntent.GREETING: [
        r"hello",
        r"hi",
        r"hey",
        r"good morning",
        r"good evening",
        r"salam",
    ],
    ConversationIntent.CROP_DISEASE: [
        r"disease",
        r"sick",
        r"yellow",
        r"wilt",
        r"spot",
        r"rot",
        r"rust",
        r"infection",
    ],
    ConversationIntent.IRRIGATION: [
        r"irrigat",
        r"water",
        r"moisture",
        r"dry",
        r"drought",
    ],
    ConversationIntent.FERTILIZER: [
        r"fertilizer",
        r"nutrient",
        r"nitrogen",
        r"phosphorus",
        r"potassium",
        r"urea",
    ],
    ConversationIntent.PEST_DETECTION: [
        r"pest",
        r"insect",
        r"bug",
        r"worm",
        r"weevil",
        r"fly",
        r"aphid",
    ],
    ConversationIntent.WEATHER: [
        r"weather",
        r"temperature",
        r"rain",
        r"wind",
        r"humidity",
        r"forecast",
    ],
    ConversationIntent.MENU: [
        r"menu",
        r"options",
        r"start",
        r"back",
        r"home",
    ],
    ConversationIntent.HELP: [
        r"help",
        r"how",
        r"what",
        r"explain",
    ],
    ConversationIntent.LANGUAGE_SWITCH: [
        r"english",
        r"arabic",
        r"language",
        r"عربي",
    ],
}


class MessageHandler:
    """
    Handler for processing incoming WhatsApp messages.
    معالج لمعالجة رسائل واتساب الواردة.
    """

    def __init__(
        self,
        whatsapp_client: "WhatsAppClient",
        session_manager: "SessionManager",
        llm_orchestrator_url: str,
        vision_service_url: str,
        default_language: str = "ar",
    ):
        self.whatsapp_client = whatsapp_client
        self.session_manager = session_manager
        self.llm_orchestrator_url = llm_orchestrator_url
        self.vision_service_url = vision_service_url
        self.default_language = Language(default_language)
        self.response_builder = ResponseBuilder()
        self.http_client = httpx.AsyncClient(timeout=60.0)

    async def handle_message(
        self,
        message: WhatsAppMessage,
        sender_name: str | None,
        metadata: WhatsAppMetadata,
    ) -> None:
        """
        Main entry point for handling incoming messages.
        نقطة الدخول الرئيسية لمعالجة الرسائل الواردة.
        """
        phone_number = message.from_

        try:
            # Mark message as read
            await self.whatsapp_client.mark_as_read(message.id)

            # Get or create session
            session = await self.session_manager.get_session(phone_number)
            if not session:
                session = await self.session_manager.create_session(
                    phone_number=phone_number,
                    sender_name=sender_name,
                    language=self.default_language,
                )

            # Update sender name if available
            if sender_name and session.profile:
                session.profile.name = sender_name

            # Route to appropriate handler based on message type
            if message.type == MessageType.TEXT:
                await self._handle_text_message(message, session)

            elif message.type == MessageType.IMAGE:
                await self._handle_image_message(message, session)

            elif message.type == MessageType.LOCATION:
                await self._handle_location_message(message, session)

            elif message.type == MessageType.INTERACTIVE:
                await self._handle_interactive_response(message, session)

            elif message.type == MessageType.BUTTON:
                await self._handle_button_response(message, session)

            else:
                await self._handle_unsupported_message(message, session)

            # Save updated session
            await self.session_manager.save_session(session)

        except Exception as e:
            logger.error(
                "message_handling_error",
                error=str(e),
                phone=phone_number[-4:] + "...",
                message_type=message.type.value,
            )
            # Send error message to user
            await self._send_error_message(phone_number, session)

    async def _handle_text_message(
        self,
        message: WhatsAppMessage,
        session: ConversationState,
    ) -> None:
        """Handle text messages."""
        text = message.text.body if message.text else ""
        phone_number = message.from_

        logger.info(
            "handling_text_message",
            phone=phone_number[-4:] + "...",
            text_preview=text[:50] + "..." if len(text) > 50 else text,
        )

        # Detect language from text
        detected_language = self._detect_language(text)
        if detected_language != session.language:
            session.language = detected_language

        # Detect intent from text
        intent = self._detect_intent(text, session.language)
        session.current_intent = intent

        # Add message to session history
        session.add_message(
            message_id=message.id,
            role="user",
            content=text,
            content_type=MessageType.TEXT,
        )

        # Handle special intents
        if intent == ConversationIntent.GREETING:
            await self._send_greeting(phone_number, session)
            return

        if intent == ConversationIntent.MENU:
            await self._send_main_menu(phone_number, session)
            return

        if intent == ConversationIntent.HELP:
            await self._send_help(phone_number, session)
            return

        if intent == ConversationIntent.LANGUAGE_SWITCH:
            await self._handle_language_switch(phone_number, session, text)
            return

        # Forward to LLM orchestrator for advisory
        await self._forward_to_llm_orchestrator(phone_number, session, text)

    async def _handle_image_message(
        self,
        message: WhatsAppMessage,
        session: ConversationState,
    ) -> None:
        """Handle image messages - forward to vision service for disease detection."""
        phone_number = message.from_
        image = message.image

        if not image:
            return

        logger.info(
            "handling_image_message",
            phone=phone_number[-4:] + "...",
            image_id=image.id,
            caption=image.caption,
        )

        # Add message to session
        session.add_message(
            message_id=message.id,
            role="user",
            content=image.caption or "[Image]",
            content_type=MessageType.IMAGE,
            metadata={"image_id": image.id, "mime_type": image.mime_type},
        )

        # Send acknowledgment
        is_arabic = session.language == Language.ARABIC
        ack_text = (
            "جاري تحليل الصورة للكشف عن أي أمراض أو مشاكل..."
            if is_arabic
            else "Analyzing image for any diseases or issues..."
        )
        await self.whatsapp_client.send_text(phone_number, ack_text)

        try:
            # Download image from WhatsApp
            image_data = await self.whatsapp_client.download_media(image.id)

            if image_data:
                # Send to vision service for analysis
                response = await self._analyze_image(image_data, image.caption, session)

                if response:
                    # Build and send response
                    response_text = self.response_builder.build_vision_response(
                        response,
                        session.language,
                    )
                    await self.whatsapp_client.send_text(phone_number, response_text)

                    # Add response to session
                    session.add_message(
                        message_id=f"assistant_{message.id}",
                        role="assistant",
                        content=response_text,
                    )
                else:
                    error_text = (
                        "عذرا، لم أتمكن من تحليل الصورة. يرجى المحاولة مرة أخرى."
                        if is_arabic
                        else "Sorry, I couldn't analyze the image. Please try again."
                    )
                    await self.whatsapp_client.send_text(phone_number, error_text)
            else:
                error_text = (
                    "عذرا، لم أتمكن من تحميل الصورة. يرجى إرسالها مرة أخرى."
                    if is_arabic
                    else "Sorry, I couldn't download the image. Please send it again."
                )
                await self.whatsapp_client.send_text(phone_number, error_text)

        except Exception as e:
            logger.error("image_analysis_error", error=str(e))
            error_text = (
                "حدث خطأ أثناء تحليل الصورة. يرجى المحاولة لاحقا."
                if is_arabic
                else "An error occurred while analyzing the image. Please try later."
            )
            await self.whatsapp_client.send_text(phone_number, error_text)

    async def _handle_location_message(
        self,
        message: WhatsAppMessage,
        session: ConversationState,
    ) -> None:
        """Handle location messages."""
        phone_number = message.from_
        location = message.location

        if not location:
            return

        logger.info(
            "handling_location_message",
            phone=phone_number[-4:] + "...",
            lat=location.latitude,
            lng=location.longitude,
        )

        # Store location in session
        if session.profile:
            session.profile.location = {
                "lat": location.latitude,
                "lng": location.longitude,
            }

        session.add_message(
            message_id=message.id,
            role="user",
            content=f"Location: {location.latitude}, {location.longitude}",
            content_type=MessageType.LOCATION,
            metadata={
                "latitude": location.latitude,
                "longitude": location.longitude,
                "name": location.name,
                "address": location.address,
            },
        )

        # Acknowledge location receipt
        is_arabic = session.language == Language.ARABIC
        response_text = (
            "تم استلام موقعك. يمكنني الآن تقديم نصائح مخصصة بناءً على موقعك وظروف الطقس المحلية."
            if is_arabic
            else "Location received. I can now provide customized advice based on your location and local weather conditions."
        )

        await self.whatsapp_client.send_text(phone_number, response_text)

        # Send menu with location-based options
        await self._send_location_menu(phone_number, session)

    async def _handle_interactive_response(
        self,
        message: WhatsAppMessage,
        session: ConversationState,
    ) -> None:
        """Handle interactive button/list responses."""
        phone_number = message.from_
        interactive = message.interactive

        if not interactive:
            return

        # Get the selected option
        selected_id = None
        selected_title = None

        if interactive.button_reply:
            selected_id = interactive.button_reply.id
            selected_title = interactive.button_reply.title
        elif interactive.list_reply:
            selected_id = interactive.list_reply.id
            selected_title = interactive.list_reply.title

        logger.info(
            "handling_interactive_response",
            phone=phone_number[-4:] + "...",
            selected_id=selected_id,
            selected_title=selected_title,
        )

        if not selected_id:
            return

        session.add_message(
            message_id=message.id,
            role="user",
            content=selected_title or selected_id,
            content_type=MessageType.INTERACTIVE,
            metadata={"button_id": selected_id},
        )

        # Route based on button ID
        await self._handle_button_action(phone_number, session, selected_id)

    async def _handle_button_response(
        self,
        message: WhatsAppMessage,
        session: ConversationState,
    ) -> None:
        """Handle quick reply button responses."""
        phone_number = message.from_
        button = message.button

        if not button:
            return

        logger.info(
            "handling_button_response",
            phone=phone_number[-4:] + "...",
            button_id=button.id,
            button_title=button.title,
        )

        session.add_message(
            message_id=message.id,
            role="user",
            content=button.title,
            content_type=MessageType.BUTTON,
            metadata={"button_id": button.id},
        )

        await self._handle_button_action(phone_number, session, button.id)

    async def _handle_button_action(
        self,
        phone_number: str,
        session: ConversationState,
        button_id: str,
    ) -> None:
        """Route button actions to appropriate handlers."""
        # Menu buttons
        if button_id == "btn_menu" or button_id == "btn_main_menu":
            await self._send_main_menu(phone_number, session)

        elif button_id == "btn_disease" or button_id == "btn_crop_disease":
            session.current_intent = ConversationIntent.CROP_DISEASE
            await self._prompt_for_crop_disease(phone_number, session)

        elif button_id == "btn_irrigation":
            session.current_intent = ConversationIntent.IRRIGATION
            await self._prompt_for_irrigation(phone_number, session)

        elif button_id == "btn_weather":
            session.current_intent = ConversationIntent.WEATHER
            await self._forward_to_llm_orchestrator(
                phone_number,
                session,
                "What's the weather forecast for my location?"
                if session.language == Language.ENGLISH
                else "ما هو توقع الطقس لموقعي؟",
            )

        elif button_id == "btn_fertilizer":
            session.current_intent = ConversationIntent.FERTILIZER
            await self._prompt_for_fertilizer(phone_number, session)

        elif button_id == "btn_language":
            await self._prompt_language_change(phone_number, session)

        elif button_id == "btn_arabic":
            session.language = Language.ARABIC
            await self.whatsapp_client.send_text(
                phone_number,
                "تم تغيير اللغة إلى العربية. كيف يمكنني مساعدتك؟",
            )
            await self._send_main_menu(phone_number, session)

        elif button_id == "btn_english":
            session.language = Language.ENGLISH
            await self.whatsapp_client.send_text(
                phone_number,
                "Language changed to English. How can I help you?",
            )
            await self._send_main_menu(phone_number, session)

        elif button_id == "btn_help":
            await self._send_help(phone_number, session)

        elif button_id == "btn_contact":
            await self._send_contact_info(phone_number, session)

        else:
            # Unknown button - forward to LLM
            await self._forward_to_llm_orchestrator(phone_number, session, button_id)

    async def _handle_unsupported_message(
        self,
        message: WhatsAppMessage,
        session: ConversationState,
    ) -> None:
        """Handle unsupported message types."""
        phone_number = message.from_
        is_arabic = session.language == Language.ARABIC

        response_text = (
            f"عذرا، لا أدعم هذا النوع من الرسائل ({message.type.value}) حاليا.\nيمكنك إرسال:\n- رسائل نصية\n- صور المحاصيل\n- الموقع"
            if is_arabic
            else f"Sorry, I don't support this message type ({message.type.value}) yet.\nYou can send:\n- Text messages\n- Crop images\n- Location"
        )

        await self.whatsapp_client.send_text(phone_number, response_text)

    async def _forward_to_llm_orchestrator(
        self,
        phone_number: str,
        session: ConversationState,
        text: str,
    ) -> None:
        """Forward message to LLM orchestrator service."""
        is_arabic = session.language == Language.ARABIC

        try:
            # Prepare context for LLM
            context = session.get_context_for_llm(limit=5)

            # Add farmer profile info if available
            farmer_info = {}
            if session.profile:
                if session.profile.location:
                    farmer_info["location"] = session.profile.location
                if session.profile.crops:
                    farmer_info["crops"] = session.profile.crops

            payload = {
                "query": text,
                "language": session.language.value,
                "context": context,
                "farmer_info": farmer_info,
                "intent": session.current_intent.value,
            }

            response = await self.http_client.post(
                f"{self.llm_orchestrator_url}/api/v1/orchestrate",
                json=payload,
            )

            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", data.get("response_ar" if is_arabic else "response_en", ""))

                if response_text:
                    # Send response to user
                    await self.whatsapp_client.send_text(phone_number, response_text)

                    # Add to session
                    session.add_message(
                        message_id=f"assistant_{session.session_id}",
                        role="assistant",
                        content=response_text,
                    )

                    # Check if there are action buttons
                    actions = data.get("actions", [])
                    if actions:
                        await self._send_action_buttons(phone_number, session, actions)
                else:
                    await self._send_fallback_response(phone_number, session)
            else:
                logger.warning(
                    "llm_orchestrator_error",
                    status_code=response.status_code,
                    response=response.text[:200],
                )
                await self._send_fallback_response(phone_number, session)

        except httpx.TimeoutException:
            logger.error("llm_orchestrator_timeout")
            error_text = (
                "عذرا، استغرق الطلب وقتا طويلا. يرجى المحاولة مرة أخرى."
                if is_arabic
                else "Sorry, the request took too long. Please try again."
            )
            await self.whatsapp_client.send_text(phone_number, error_text)

        except Exception as e:
            logger.error("llm_orchestrator_error", error=str(e))
            await self._send_fallback_response(phone_number, session)

    async def _analyze_image(
        self,
        image_data: bytes,
        caption: str | None,
        session: ConversationState,
    ) -> dict | None:
        """Send image to vision service for analysis."""
        try:
            # Send to YOLO vision service
            files = {"image": ("image.jpg", image_data, "image/jpeg")}
            data = {"language": session.language.value}
            if caption:
                data["context"] = caption

            response = await self.http_client.post(
                f"{self.vision_service_url}/api/v1/vision/detect",
                files=files,
                data=data,
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(
                    "vision_service_error",
                    status_code=response.status_code,
                )
                return None

        except Exception as e:
            logger.error("vision_analysis_error", error=str(e))
            return None

    def _detect_language(self, text: str) -> Language:
        """Detect language from text (Arabic or English)."""
        # Simple heuristic: check for Arabic characters
        arabic_pattern = re.compile(r"[\u0600-\u06FF]")
        if arabic_pattern.search(text):
            return Language.ARABIC
        return Language.ENGLISH

    def _detect_intent(self, text: str, language: Language) -> ConversationIntent:
        """Detect intent from text."""
        text_lower = text.lower()

        patterns = ARABIC_PATTERNS if language == Language.ARABIC else ENGLISH_PATTERNS

        for intent, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return intent

        return ConversationIntent.GENERAL_ADVISORY

    async def _send_greeting(
        self,
        phone_number: str,
        session: ConversationState,
    ) -> None:
        """Send greeting message with main menu."""
        name = session.profile.name if session.profile else None

        greeting = self.response_builder.build_greeting(
            language=session.language,
            name=name,
        )

        await self.whatsapp_client.send_text(phone_number, greeting)
        await self._send_main_menu(phone_number, session)

    async def _send_main_menu(
        self,
        phone_number: str,
        session: ConversationState,
    ) -> None:
        """Send main menu with options."""
        is_arabic = session.language == Language.ARABIC

        buttons = self.response_builder.get_main_menu_buttons(session.language)
        body_text = "اختر أحد الخيارات التالية:" if is_arabic else "Choose one of the following options:"

        await self.whatsapp_client.send_interactive_buttons(
            to=phone_number,
            body_text=body_text,
            buttons=buttons,
        )

    async def _send_help(
        self,
        phone_number: str,
        session: ConversationState,
    ) -> None:
        """Send help message."""
        help_text = self.response_builder.build_help_message(session.language)
        await self.whatsapp_client.send_text(phone_number, help_text)

    async def _send_location_menu(
        self,
        phone_number: str,
        session: ConversationState,
    ) -> None:
        """Send menu with location-based options."""
        is_arabic = session.language == Language.ARABIC

        buttons = [
            {"id": "btn_weather", "title": "الطقس" if is_arabic else "Weather"},
            {"id": "btn_irrigation", "title": "نصائح الري" if is_arabic else "Irrigation Tips"},
            {"id": "btn_menu", "title": "القائمة الرئيسية" if is_arabic else "Main Menu"},
        ]

        body_text = (
            "بناءً على موقعك، يمكنني مساعدتك في:" if is_arabic else "Based on your location, I can help you with:"
        )

        await self.whatsapp_client.send_interactive_buttons(
            to=phone_number,
            body_text=body_text,
            buttons=buttons,
        )

    async def _prompt_for_crop_disease(
        self,
        phone_number: str,
        session: ConversationState,
    ) -> None:
        """Prompt user to send crop image or describe symptoms."""
        is_arabic = session.language == Language.ARABIC

        prompt_text = (
            "للكشف عن أمراض المحاصيل:\n\n1. أرسل صورة واضحة للنبات المصاب\n2. أو صف الأعراض التي تراها\n\nمثال: أوراق صفراء، بقع بنية، ذبول"
            if is_arabic
            else "To detect crop diseases:\n\n1. Send a clear photo of the affected plant\n2. Or describe the symptoms you see\n\nExample: yellow leaves, brown spots, wilting"
        )

        await self.whatsapp_client.send_text(phone_number, prompt_text)

    async def _prompt_for_irrigation(
        self,
        phone_number: str,
        session: ConversationState,
    ) -> None:
        """Prompt user for irrigation query."""
        is_arabic = session.language == Language.ARABIC

        prompt_text = (
            "للحصول على نصائح الري:\n\n- ما هو المحصول الذي تزرعه؟\n- ما هي مساحة الحقل؟\n- متى آخر مرة قمت بالري؟"
            if is_arabic
            else "For irrigation advice:\n\n- What crop are you growing?\n- What is the field area?\n- When did you last irrigate?"
        )

        await self.whatsapp_client.send_text(phone_number, prompt_text)

    async def _prompt_for_fertilizer(
        self,
        phone_number: str,
        session: ConversationState,
    ) -> None:
        """Prompt user for fertilizer query."""
        is_arabic = session.language == Language.ARABIC

        prompt_text = (
            "للحصول على نصائح التسميد:\n\n- ما هو المحصول؟\n- ما هي مرحلة النمو الحالية؟\n- هل لديك نتائج تحليل التربة؟"
            if is_arabic
            else "For fertilizer advice:\n\n- What is the crop?\n- What is the current growth stage?\n- Do you have soil test results?"
        )

        await self.whatsapp_client.send_text(phone_number, prompt_text)

    async def _prompt_language_change(
        self,
        phone_number: str,
        session: ConversationState,
    ) -> None:
        """Prompt user to select language."""
        buttons = [
            {"id": "btn_arabic", "title": "العربية"},
            {"id": "btn_english", "title": "English"},
        ]

        is_arabic = session.language == Language.ARABIC
        body_text = "اختر اللغة:" if is_arabic else "Select language:"

        await self.whatsapp_client.send_interactive_buttons(
            to=phone_number,
            body_text=body_text,
            buttons=buttons,
        )

    async def _handle_language_switch(
        self,
        phone_number: str,
        session: ConversationState,
        text: str,
    ) -> None:
        """Handle language switch request."""
        text_lower = text.lower()

        if "english" in text_lower or "إنجليزي" in text:
            session.language = Language.ENGLISH
            await self.whatsapp_client.send_text(
                phone_number,
                "Language changed to English. How can I help you?",
            )
        elif "arabic" in text_lower or "عربي" in text:
            session.language = Language.ARABIC
            await self.whatsapp_client.send_text(
                phone_number,
                "تم تغيير اللغة إلى العربية. كيف يمكنني مساعدتك؟",
            )
        else:
            await self._prompt_language_change(phone_number, session)

        await self._send_main_menu(phone_number, session)

    async def _send_contact_info(
        self,
        phone_number: str,
        session: ConversationState,
    ) -> None:
        """Send contact information."""
        is_arabic = session.language == Language.ARABIC

        contact_text = (
            "للتواصل مع الدعم:\n\n📧 البريد الإلكتروني: support@sahool.io\n📞 الهاتف: +967-XXX-XXXX\n🌐 الموقع: www.sahool.io"
            if is_arabic
            else "Contact Support:\n\n📧 Email: support@sahool.io\n📞 Phone: +967-XXX-XXXX\n🌐 Website: www.sahool.io"
        )

        await self.whatsapp_client.send_text(phone_number, contact_text)

    async def _send_action_buttons(
        self,
        phone_number: str,
        session: ConversationState,
        actions: list[dict],
    ) -> None:
        """Send action buttons based on LLM response."""
        if not actions or len(actions) > 3:
            return

        is_arabic = session.language == Language.ARABIC

        buttons = [
            {
                "id": action.get("id", f"action_{i}"),
                "title": action.get("title_ar" if is_arabic else "title", action.get("title", ""))[:20],
            }
            for i, action in enumerate(actions)
        ]

        body_text = "إجراءات مقترحة:" if is_arabic else "Suggested actions:"

        await self.whatsapp_client.send_interactive_buttons(
            to=phone_number,
            body_text=body_text,
            buttons=buttons,
        )

    async def _send_fallback_response(
        self,
        phone_number: str,
        session: ConversationState,
    ) -> None:
        """Send fallback response when LLM fails."""
        is_arabic = session.language == Language.ARABIC

        fallback_text = (
            "عذرا، لم أتمكن من معالجة طلبك. يرجى المحاولة بطريقة أخرى أو اختيار من القائمة."
            if is_arabic
            else "Sorry, I couldn't process your request. Please try a different approach or choose from the menu."
        )

        await self.whatsapp_client.send_text(phone_number, fallback_text)
        await self._send_main_menu(phone_number, session)

    async def _send_error_message(
        self,
        phone_number: str,
        session: ConversationState | None,
    ) -> None:
        """Send error message to user."""
        is_arabic = session.language == Language.ARABIC if session else True

        error_text = (
            "عذرا، حدث خطأ. يرجى المحاولة مرة أخرى لاحقا."
            if is_arabic
            else "Sorry, an error occurred. Please try again later."
        )

        try:
            await self.whatsapp_client.send_text(phone_number, error_text)
        except Exception:
            pass  # Silently fail if we can't send error message

    async def close(self) -> None:
        """Close HTTP client."""
        await self.http_client.aclose()
