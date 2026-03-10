"""
Tests for Voice Assistant | اختبارات المساعد الصوتي

Tests cover initialization, intent detection, wake word detection,
voice processing, and language support.
"""

from __future__ import annotations

import pytest

from shared.ai.voice_assistant import (
    LANGUAGE_AR,
    VOICE_PATTERNS,
    VoiceAssistant,
    VoiceCommand,
    VoiceInput,
    VoiceLanguage,
    VoiceResponse,
    VoiceSession,
)


class TestVoiceAssistantInit:
    """Tests for VoiceAssistant initialization | اختبارات التهيئة"""

    def test_default_model(self) -> None:
        """Default model should be 'small'."""
        va = VoiceAssistant()
        assert va.model == "small"

    def test_custom_model(self) -> None:
        """Custom model parameter is stored correctly."""
        va = VoiceAssistant(model="medium")
        assert va.model == "medium"

    def test_whisper_models_defined(self) -> None:
        """All Whisper model variants should be registered."""
        assert "tiny" in VoiceAssistant.WHISPER_MODELS
        assert "base" in VoiceAssistant.WHISPER_MODELS
        assert "small" in VoiceAssistant.WHISPER_MODELS
        assert "medium" in VoiceAssistant.WHISPER_MODELS
        assert "large-v3" in VoiceAssistant.WHISPER_MODELS

    def test_sessions_empty_on_init(self) -> None:
        """Sessions dict is empty after creation."""
        va = VoiceAssistant()
        assert va._sessions == {}


class TestIntentDetection:
    """Tests for intent detection | اختبارات كشف النية"""

    def setup_method(self) -> None:
        self.va = VoiceAssistant()

    def test_detect_irrigation_arabic(self) -> None:
        """Detect irrigation intent from Arabic text | كشف نية الري من نص عربي"""
        intent, cmd, conf = self.va.detect_intent("القمح يحتاج سقي")
        assert intent == "irrigation"
        assert cmd == VoiceCommand.QUERY
        assert conf > 0.0

    def test_detect_irrigation_english(self) -> None:
        """Detect irrigation intent from English text."""
        intent, cmd, conf = self.va.detect_intent("I need to irrigate the field")
        assert intent == "irrigation"

    def test_detect_disease_arabic(self) -> None:
        """Detect disease intent from Arabic text | كشف نية الأمراض"""
        intent, cmd, conf = self.va.detect_intent("الورق اصفر عندي ذبول")
        assert intent == "disease"
        assert cmd == VoiceCommand.QUERY

    def test_detect_pest_arabic(self) -> None:
        """Detect pest intent from Arabic text | كشف نية الآفات"""
        intent, cmd, conf = self.va.detect_intent("فيه سوسة في النخل")
        assert intent == "pest"
        assert cmd == VoiceCommand.ALERT

    def test_detect_weather_intent(self) -> None:
        """Detect weather intent | كشف نية الطقس"""
        intent, cmd, conf = self.va.detect_intent("كيف حالة الطقس اليوم")
        assert intent == "weather"

    def test_detect_harvest_intent(self) -> None:
        """Detect harvest intent | كشف نية الحصاد"""
        intent, cmd, conf = self.va.detect_intent("متى موعد الحصاد")
        assert intent == "harvest"

    def test_detect_fertilize_intent(self) -> None:
        """Detect fertilize intent | كشف نية التسميد"""
        intent, cmd, conf = self.va.detect_intent("أحتاج سماد نيتروجين تسميد")
        assert intent == "fertilize"
        assert cmd == VoiceCommand.ACTION

    def test_detect_report_intent(self) -> None:
        """Detect report intent | كشف نية التقرير"""
        intent, cmd, conf = self.va.detect_intent("أريد تقرير ملخص")
        assert intent == "report"
        assert cmd == VoiceCommand.REPORT

    def test_detect_note_intent(self) -> None:
        """Detect note recording intent | كشف نية تسجيل ملاحظة"""
        intent, cmd, conf = self.va.detect_intent("ملاحظة: الحقل بحاجة صيانة")
        assert intent == "note"
        assert cmd == VoiceCommand.RECORD

    def test_unknown_intent_returns_empty(self) -> None:
        """Unknown text returns empty intent with zero confidence."""
        intent, cmd, conf = self.va.detect_intent("مرحبا كيف الحال")
        assert intent == ""
        assert conf == 0.0

    def test_multiple_keywords_higher_confidence(self) -> None:
        """More keywords should give higher confidence | كلمات أكثر = ثقة أعلى"""
        _, _, conf_single = self.va.detect_intent("ري")
        _, _, conf_multi = self.va.detect_intent("ري ماء سقي رطوبة")
        assert conf_multi > conf_single


class TestWakeWordDetection:
    """Tests for wake word detection | اختبارات كشف كلمة التنبيه"""

    def setup_method(self) -> None:
        self.va = VoiceAssistant()

    def test_arabic_wake_word(self) -> None:
        """Detect Arabic wake word 'يا سهول'."""
        assert self.va.has_wake_word("يا سهول ورق القمح اصفر") is True

    def test_short_arabic_wake_word(self) -> None:
        """Detect short Arabic wake word 'سهول'."""
        assert self.va.has_wake_word("سهول ساعدني") is True

    def test_english_wake_word(self) -> None:
        """Detect English wake word 'ya sahool'."""
        assert self.va.has_wake_word("ya sahool what is the weather") is True

    def test_english_short_wake_word(self) -> None:
        """Detect English short wake word 'sahool'."""
        assert self.va.has_wake_word("sahool help me") is True

    def test_no_wake_word(self) -> None:
        """No wake word in regular text."""
        assert self.va.has_wake_word("ورق القمح اصفر") is False

    def test_case_insensitive(self) -> None:
        """Wake word detection is case insensitive."""
        assert self.va.has_wake_word("SAHOOL help") is True


class TestProcessVoiceInput:
    """Tests for full voice input processing | اختبارات معالجة المدخل الصوتي"""

    def setup_method(self) -> None:
        self.va = VoiceAssistant()

    def test_irrigation_response(self) -> None:
        """Processing irrigation query yields bilingual response."""
        resp = self.va.process_voice_input("القمح يحتاج سقي")
        assert isinstance(resp, VoiceResponse)
        assert resp.intent == "irrigation"
        assert resp.text != ""
        assert resp.text_ar != ""
        assert resp.response_id.startswith("VR-")
        assert resp.timestamp != ""

    def test_disease_suggested_actions(self) -> None:
        """Disease intent should suggest take_photo and consult_expert."""
        resp = self.va.process_voice_input("الورق اصفر ذبول")
        assert resp.intent == "disease"
        action_types = [a["action"] for a in resp.suggested_actions]
        assert "take_photo" in action_types
        assert "consult_expert" in action_types

    def test_irrigation_suggested_actions(self) -> None:
        """Irrigation intent should suggest view_schedule."""
        resp = self.va.process_voice_input("متى أسقي")
        assert resp.intent == "irrigation"
        action_types = [a["action"] for a in resp.suggested_actions]
        assert "view_schedule" in action_types

    def test_unknown_intent_default_response(self) -> None:
        """Unknown intent returns a helpful default response."""
        resp = self.va.process_voice_input("مرحبا")
        assert resp.intent == "general"
        assert "هنا للمساعدة" in resp.text_ar

    def test_field_context_passed_to_data(self) -> None:
        """Field context dict is passed through to response data."""
        ctx = {"field_id": "F-001", "crop": "wheat"}
        resp = self.va.process_voice_input("سقي", field_context=ctx)
        assert resp.data == ctx

    def test_confidence_in_response(self) -> None:
        """Response confidence should be between 0 and 1."""
        resp = self.va.process_voice_input("ري ماء")
        assert 0.0 <= resp.confidence <= 1.0


class TestSupportedLanguages:
    """Tests for supported language listing | اختبارات اللغات المدعومة"""

    def setup_method(self) -> None:
        self.va = VoiceAssistant()

    def test_returns_all_languages(self) -> None:
        """Should return all defined VoiceLanguage members."""
        langs = self.va.get_supported_languages()
        assert len(langs) == len(VoiceLanguage)

    def test_language_has_code_and_label(self) -> None:
        """Each language entry should have code and label."""
        for lang in self.va.get_supported_languages():
            assert "code" in lang
            assert "label" in lang

    def test_arabic_msa_present(self) -> None:
        """Arabic MSA should be in the list."""
        codes = [l["code"] for l in self.va.get_supported_languages()]
        assert "ar_msa" in codes

    def test_arabic_labels_populated(self) -> None:
        """Arabic labels should be populated from LANGUAGE_AR."""
        for lang_entry in self.va.get_supported_languages():
            assert lang_entry["label"] != ""


class TestDataClasses:
    """Tests for voice assistant dataclasses | اختبارات فئات البيانات"""

    def test_voice_input_defaults(self) -> None:
        """VoiceInput should have sensible defaults."""
        vi = VoiceInput()
        assert vi.audio_duration_seconds == 0.0
        assert vi.detected_language == VoiceLanguage.AR_MSA
        assert vi.confidence == 0.0
        assert vi.is_offline is False

    def test_voice_response_defaults(self) -> None:
        """VoiceResponse should have sensible defaults."""
        vr = VoiceResponse()
        assert vr.command_type == VoiceCommand.QUERY
        assert vr.data == {}
        assert vr.suggested_actions == []

    def test_voice_session_defaults(self) -> None:
        """VoiceSession should have sensible defaults."""
        vs = VoiceSession()
        assert vs.is_active is True
        assert vs.interactions == []
