"""Tests for voice assistant."""
import pytest
from shared.ai.voice_assistant import VoiceAssistant, VoiceCommand, VoiceLanguage


class TestVoiceAssistant:
    def setup_method(self):
        self.va = VoiceAssistant()

    def test_detect_irrigation_intent(self):
        intent, cmd, conf = self.va.detect_intent("القمح يحتاج سقي")
        assert intent == "irrigation"

    def test_detect_disease_intent(self):
        intent, cmd, conf = self.va.detect_intent("الورق اصفر عندي ذبول")
        assert intent == "disease"

    def test_detect_pest_intent(self):
        intent, cmd, conf = self.va.detect_intent("فيه سوسة في النخل")
        assert intent == "pest"
        assert cmd == VoiceCommand.ALERT

    def test_wake_word(self):
        assert self.va.has_wake_word("يا سهول ورق القمح اصفر")
        assert not self.va.has_wake_word("ورق القمح اصفر")

    def test_process_voice_input(self):
        response = self.va.process_voice_input("القمح يحتاج سقي")
        assert response.intent == "irrigation"
        assert response.text_ar != ""

    def test_supported_languages(self):
        langs = self.va.get_supported_languages()
        assert len(langs) >= 6
