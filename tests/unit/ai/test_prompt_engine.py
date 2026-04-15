"""
SAHOOL Prompt Engine Tests
Sprint 9: Unit tests for prompt template rendering
"""

import pytest

from advisor.ai.prompt_engine import get_template, list_templates, render_prompt


@pytest.mark.unit
class TestRenderPrompt:
    """Test prompt rendering"""

    def test_prompt_includes_question(self):
        """Question is injected into prompt"""
        prompt = render_prompt(
            question="ما هو أفضل وقت للري؟",
            field_context="CTX",
            retrieved_chunks="CHUNKS",
        )
        assert "ما هو أفضل وقت للري؟" in prompt

    def test_prompt_includes_context(self):
        """Field context is injected into prompt"""
        prompt = render_prompt(
            question="Q",
            field_context="Field Alpha - wheat - 50 hectares",
            retrieved_chunks="CHUNKS",
        )
        assert "Field Alpha - wheat - 50 hectares" in prompt

    def test_prompt_includes_chunks(self):
        """Retrieved chunks are injected into prompt"""
        prompt = render_prompt(
            question="Q",
            field_context="CTX",
            retrieved_chunks="[doc1/0] Important info about irrigation",
        )
        assert "[doc1/0] Important info about irrigation" in prompt

    def test_prompt_is_arabic(self):
        """Prompt template contains Arabic instructions"""
        prompt = render_prompt(
            question="Q",
            field_context="CTX",
            retrieved_chunks="CH",
        )
        assert "أنت مستشار زراعي" in prompt

    def test_render_all_placeholders(self):
        """All placeholders are replaced"""
        prompt = render_prompt(
            question="Q",
            field_context="CTX",
            retrieved_chunks="CH",
        )
        assert "{{question}}" not in prompt
        assert "{{field_context}}" not in prompt
        assert "{{retrieved_chunks}}" not in prompt


@pytest.mark.unit
class TestGetTemplate:
    """Test template loading"""

    def test_load_default_template(self):
        """Default template can be loaded"""
        template = get_template("field_advice_v1")
        assert len(template) > 0
        assert "{{question}}" in template

    def test_missing_template_raises(self):
        """Missing template raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            get_template("nonexistent_template_xyz")


@pytest.mark.unit
class TestListTemplates:
    """Test template listing"""

    def test_list_includes_default(self):
        """Default template appears in list"""
        templates = list_templates()
        assert "field_advice_v1" in templates
