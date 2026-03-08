# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Response Builder for WhatsApp Bot Service.
بناء الردود لخدمة روبوت واتساب.

Builds:
- Text responses (bilingual)
- Interactive button messages
- List messages (menus)
- Image responses with captions
"""

from ..api.schemas import Language


class ResponseBuilder:
    """
    Builder for WhatsApp response messages.
    بناء رسائل الرد لواتساب.
    """

    # Greeting templates
    GREETINGS = {
        Language.ARABIC: {
            "with_name": "مرحباً {name}! 👋\n\nأنا المساعد الزراعي الذكي من سهول. يمكنني مساعدتك في:\n\n🌱 تشخيص أمراض المحاصيل\n💧 نصائح الري\n🌤️ معلومات الطقس\n🧪 توصيات التسميد\n🐛 الكشف عن الآفات",
            "without_name": "مرحباً! 👋\n\nأنا المساعد الزراعي الذكي من سهول. يمكنني مساعدتك في:\n\n🌱 تشخيص أمراض المحاصيل\n💧 نصائح الري\n🌤️ معلومات الطقس\n🧪 توصيات التسميد\n🐛 الكشف عن الآفات",
        },
        Language.ENGLISH: {
            "with_name": "Hello {name}! 👋\n\nI'm the SAHOOL Smart Agricultural Assistant. I can help you with:\n\n🌱 Crop disease diagnosis\n💧 Irrigation advice\n🌤️ Weather information\n🧪 Fertilizer recommendations\n🐛 Pest detection",
            "without_name": "Hello! 👋\n\nI'm the SAHOOL Smart Agricultural Assistant. I can help you with:\n\n🌱 Crop disease diagnosis\n💧 Irrigation advice\n🌤️ Weather information\n🧪 Fertilizer recommendations\n🐛 Pest detection",
        },
    }

    # Help message templates
    HELP_MESSAGES = {
        Language.ARABIC: """📖 دليل الاستخدام

🔹 **الرسائل النصية**
اكتب سؤالك مباشرة وسأحاول مساعدتك.
مثال: "ما هو أفضل وقت لري القمح؟"

🔹 **الصور**
أرسل صورة للمحصول لتشخيص الأمراض أو الآفات.

🔹 **الموقع**
شارك موقعك للحصول على معلومات الطقس المحلية.

🔹 **الأزرار**
استخدم الأزرار للوصول السريع للخدمات.

🔹 **تغيير اللغة**
اكتب "English" للتحويل إلى الإنجليزية.""",
        Language.ENGLISH: """📖 User Guide

🔹 **Text Messages**
Type your question directly and I'll try to help.
Example: "What's the best time to irrigate wheat?"

🔹 **Images**
Send a crop photo to diagnose diseases or pests.

🔹 **Location**
Share your location to get local weather information.

🔹 **Buttons**
Use buttons for quick access to services.

🔹 **Change Language**
Type "عربي" to switch to Arabic.""",
    }

    # Main menu buttons
    MAIN_MENU_BUTTONS = {
        Language.ARABIC: [
            {"id": "btn_crop_disease", "title": "🌱 أمراض المحاصيل"},
            {"id": "btn_irrigation", "title": "💧 الري"},
            {"id": "btn_weather", "title": "🌤️ الطقس"},
        ],
        Language.ENGLISH: [
            {"id": "btn_crop_disease", "title": "🌱 Crop Diseases"},
            {"id": "btn_irrigation", "title": "💧 Irrigation"},
            {"id": "btn_weather", "title": "🌤️ Weather"},
        ],
    }

    # Extended menu sections (for list messages)
    MENU_SECTIONS = {
        Language.ARABIC: [
            {
                "title": "🌱 المحاصيل",
                "rows": [
                    {
                        "id": "menu_disease",
                        "title": "تشخيص الأمراض",
                        "description": "كشف أمراض المحاصيل من الصور",
                    },
                    {
                        "id": "menu_pest",
                        "title": "الآفات",
                        "description": "التعرف على الآفات ومكافحتها",
                    },
                    {"id": "menu_fertilizer", "title": "التسميد", "description": "توصيات الأسمدة"},
                ],
            },
            {
                "title": "💧 الري والطقس",
                "rows": [
                    {
                        "id": "menu_irrigation",
                        "title": "جدول الري",
                        "description": "نصائح الري حسب المحصول",
                    },
                    {"id": "menu_weather", "title": "الطقس", "description": "توقعات الطقس لموقعك"},
                ],
            },
            {
                "title": "⚙️ الإعدادات",
                "rows": [
                    {
                        "id": "btn_language",
                        "title": "تغيير اللغة",
                        "description": "English / العربية",
                    },
                    {"id": "btn_help", "title": "المساعدة", "description": "دليل الاستخدام"},
                ],
            },
        ],
        Language.ENGLISH: [
            {
                "title": "🌱 Crops",
                "rows": [
                    {
                        "id": "menu_disease",
                        "title": "Disease Diagnosis",
                        "description": "Detect crop diseases from photos",
                    },
                    {
                        "id": "menu_pest",
                        "title": "Pests",
                        "description": "Identify and control pests",
                    },
                    {
                        "id": "menu_fertilizer",
                        "title": "Fertilization",
                        "description": "Fertilizer recommendations",
                    },
                ],
            },
            {
                "title": "💧 Irrigation & Weather",
                "rows": [
                    {
                        "id": "menu_irrigation",
                        "title": "Irrigation Schedule",
                        "description": "Irrigation tips by crop",
                    },
                    {
                        "id": "menu_weather",
                        "title": "Weather",
                        "description": "Weather forecast for your location",
                    },
                ],
            },
            {
                "title": "⚙️ Settings",
                "rows": [
                    {
                        "id": "btn_language",
                        "title": "Change Language",
                        "description": "English / العربية",
                    },
                    {"id": "btn_help", "title": "Help", "description": "User guide"},
                ],
            },
        ],
    }

    def build_greeting(
        self,
        language: Language,
        name: str | None = None,
    ) -> str:
        """Build greeting message."""
        templates = self.GREETINGS[language]
        if name:
            return templates["with_name"].format(name=name)
        return templates["without_name"]

    def build_help_message(self, language: Language) -> str:
        """Build help message."""
        return self.HELP_MESSAGES[language]

    def get_main_menu_buttons(self, language: Language) -> list[dict]:
        """Get main menu buttons for language."""
        return self.MAIN_MENU_BUTTONS[language]

    def get_menu_sections(self, language: Language) -> list[dict]:
        """Get full menu sections for list message."""
        return self.MENU_SECTIONS[language]

    def build_vision_response(
        self,
        vision_result: dict,
        language: Language,
    ) -> str:
        """
        Build response from vision service analysis.
        بناء الرد من تحليل خدمة الرؤية.
        """
        is_arabic = language == Language.ARABIC

        # Check for detections
        detections = vision_result.get("detections", [])

        if not detections:
            return (
                "لم أتمكن من اكتشاف أي مشاكل واضحة في الصورة. إذا كنت تلاحظ أعراضا معينة، يرجى وصفها لي."
                if is_arabic
                else "I couldn't detect any obvious issues in the image. If you notice specific symptoms, please describe them to me."
            )

        # Build response with detections
        response_parts = []

        if is_arabic:
            response_parts.append("🔍 **نتائج التحليل:**\n")
        else:
            response_parts.append("🔍 **Analysis Results:**\n")

        for i, detection in enumerate(detections, 1):
            label = detection.get("label_ar" if is_arabic else "label", detection.get("label", "Unknown"))
            confidence = detection.get("confidence", 0) * 100
            detection.get("category", "")

            if is_arabic:
                response_parts.append(f"{i}. **{label}** (ثقة: {confidence:.0f}%)")
            else:
                response_parts.append(f"{i}. **{label}** (confidence: {confidence:.0f}%)")

        # Add recommendations if available
        recommendations = vision_result.get("recommendations_ar" if is_arabic else "recommendations", [])
        if recommendations:
            if is_arabic:
                response_parts.append("\n\n📋 **التوصيات:**")
            else:
                response_parts.append("\n\n📋 **Recommendations:**")

            for rec in recommendations:
                response_parts.append(f"• {rec}")

        # Add severity if available
        severity = vision_result.get("severity")
        if severity:
            severity_labels = {
                "low": ("منخفضة 🟢", "Low 🟢"),
                "medium": ("متوسطة 🟡", "Medium 🟡"),
                "high": ("عالية 🟠", "High 🟠"),
                "critical": ("حرجة 🔴", "Critical 🔴"),
            }
            label = severity_labels.get(severity, (severity, severity))
            if is_arabic:
                response_parts.append(f"\n\n⚠️ **درجة الخطورة:** {label[0]}")
            else:
                response_parts.append(f"\n\n⚠️ **Severity:** {label[1]}")

        return "\n".join(response_parts)

    def build_weather_response(
        self,
        weather_data: dict,
        language: Language,
    ) -> str:
        """
        Build response from weather service.
        بناء الرد من خدمة الطقس.
        """
        is_arabic = language == Language.ARABIC

        temp = weather_data.get("temperature", "N/A")
        humidity = weather_data.get("humidity", "N/A")
        description = weather_data.get("description_ar" if is_arabic else "description", "")
        wind_speed = weather_data.get("wind_speed", "N/A")

        if is_arabic:
            return f"""🌤️ **حالة الطقس:**

🌡️ درجة الحرارة: {temp}°C
💧 الرطوبة: {humidity}%
💨 سرعة الرياح: {wind_speed} كم/س
📝 الحالة: {description}"""
        else:
            return f"""🌤️ **Weather Conditions:**

🌡️ Temperature: {temp}°C
💧 Humidity: {humidity}%
💨 Wind Speed: {wind_speed} km/h
📝 Condition: {description}"""

    def build_irrigation_response(
        self,
        irrigation_data: dict,
        language: Language,
    ) -> str:
        """
        Build response from irrigation service.
        بناء الرد من خدمة الري.
        """
        is_arabic = language == Language.ARABIC

        recommendation = irrigation_data.get("recommendation_ar" if is_arabic else "recommendation", "")
        water_amount = irrigation_data.get("water_amount_mm", "N/A")
        next_irrigation = irrigation_data.get("next_irrigation", "")
        soil_moisture = irrigation_data.get("soil_moisture", "N/A")

        if is_arabic:
            response = f"""💧 **توصية الري:**

{recommendation}

📊 **التفاصيل:**
• كمية المياه المطلوبة: {water_amount} ملم
• رطوبة التربة الحالية: {soil_moisture}%"""
            if next_irrigation:
                response += f"\n• موعد الري القادم: {next_irrigation}"
        else:
            response = f"""💧 **Irrigation Recommendation:**

{recommendation}

📊 **Details:**
• Required water amount: {water_amount} mm
• Current soil moisture: {soil_moisture}%"""
            if next_irrigation:
                response += f"\n• Next irrigation: {next_irrigation}"

        return response

    def build_fertilizer_response(
        self,
        fertilizer_data: dict,
        language: Language,
    ) -> str:
        """
        Build response from fertilizer advisory.
        بناء الرد من استشارة التسميد.
        """
        is_arabic = language == Language.ARABIC

        recommendation = fertilizer_data.get("recommendation_ar" if is_arabic else "recommendation", "")
        fertilizer_type = fertilizer_data.get("fertilizer_type_ar" if is_arabic else "fertilizer_type", "")
        application_rate = fertilizer_data.get("application_rate", "N/A")
        timing = fertilizer_data.get("timing_ar" if is_arabic else "timing", "")

        if is_arabic:
            return f"""🧪 **توصية التسميد:**

{recommendation}

📊 **التفاصيل:**
• نوع السماد: {fertilizer_type}
• معدل التطبيق: {application_rate} كجم/هكتار
• التوقيت المناسب: {timing}"""
        else:
            return f"""🧪 **Fertilizer Recommendation:**

{recommendation}

📊 **Details:**
• Fertilizer type: {fertilizer_type}
• Application rate: {application_rate} kg/ha
• Best timing: {timing}"""

    def build_error_response(
        self,
        language: Language,
        error_type: str = "general",
    ) -> str:
        """Build error response message."""
        is_arabic = language == Language.ARABIC

        error_messages = {
            "general": (
                "عذرا، حدث خطأ. يرجى المحاولة مرة أخرى.",
                "Sorry, an error occurred. Please try again.",
            ),
            "timeout": (
                "عذرا، استغرق الطلب وقتا طويلا. يرجى المحاولة لاحقا.",
                "Sorry, the request timed out. Please try later.",
            ),
            "image_failed": (
                "عذرا، لم أتمكن من تحليل الصورة. يرجى إرسال صورة أوضح.",
                "Sorry, I couldn't analyze the image. Please send a clearer photo.",
            ),
            "unsupported": (
                "عذرا، هذه الميزة غير متوفرة حاليا.",
                "Sorry, this feature is not available yet.",
            ),
        }

        message = error_messages.get(error_type, error_messages["general"])
        return message[0] if is_arabic else message[1]

    def build_confirmation_response(
        self,
        language: Language,
        action: str,
    ) -> str:
        """Build confirmation response."""
        is_arabic = language == Language.ARABIC

        confirmations = {
            "location_saved": (
                "تم حفظ موقعك بنجاح.",
                "Your location has been saved successfully.",
            ),
            "preferences_updated": (
                "تم تحديث تفضيلاتك.",
                "Your preferences have been updated.",
            ),
            "language_changed": (
                "تم تغيير اللغة.",
                "Language has been changed.",
            ),
        }

        message = confirmations.get(action, ("تم.", "Done."))
        return message[0] if is_arabic else message[1]
