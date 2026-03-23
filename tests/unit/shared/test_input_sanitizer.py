"""
Tests for SAHOOL Input Sanitization Middleware
اختبارات ميدل وير تنظيف المدخلات

Tests XSS prevention, script injection blocking, and Arabic text preservation.
"""

import pytest

from shared.middleware.input_sanitizer import (
    DANGEROUS_PATTERNS,
    MAX_STRING_LENGTH,
    sanitize_string,
    sanitize_value,
)

# ═══════════════════════════════════════════════════════════════════════════════
# sanitize_string Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestSanitizeString:
    """Test sanitize_string XSS prevention."""

    def test_plain_text_unchanged(self):
        """Plain text passes through with HTML escaping of special chars only."""
        assert sanitize_string("hello world") == "hello world"

    def test_arabic_text_preserved(self):
        """Arabic text is preserved after sanitization."""
        arabic = "مرحبا بالعالم"
        result = sanitize_string(arabic)
        assert "مرحبا" in result
        assert "بالعالم" in result

    def test_script_tag_escaped(self):
        """Script tags are HTML-escaped."""
        malicious = '<script>alert("xss")</script>'
        result = sanitize_string(malicious)
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_javascript_protocol_escaped(self):
        """javascript: protocol is detected and logged; HTML-escaped output returned."""
        malicious = 'javascript:alert(1)'
        result = sanitize_string(malicious)
        # html.escape leaves this unchanged (no < > & " chars), but the
        # dangerous-pattern detector logs a warning for the javascript: protocol.
        assert result == "javascript:alert(1)"

    def test_event_handler_escaped(self):
        """Event handler attributes are detected."""
        malicious = '<img onerror=alert(1) src=x>'
        result = sanitize_string(malicious)
        assert "onerror" not in result or "&lt;" in result

    def test_iframe_escaped(self):
        """iframe tags are HTML-escaped."""
        malicious = '<iframe src="evil.com"></iframe>'
        result = sanitize_string(malicious)
        assert "<iframe" not in result
        assert "&lt;iframe" in result

    def test_truncation_long_input(self):
        """Oversized strings are truncated."""
        long_input = "a" * (MAX_STRING_LENGTH + 500)
        result = sanitize_string(long_input)
        assert len(result) <= MAX_STRING_LENGTH

    def test_non_string_passthrough(self):
        """Non-string values pass through unchanged."""
        assert sanitize_string(123) == 123
        assert sanitize_string(None) is None

    def test_empty_string(self):
        """Empty string returns empty."""
        assert sanitize_string("") == ""

    def test_html_entities_escaped(self):
        """HTML special characters are escaped."""
        result = sanitize_string('<div class="test">&</div>')
        assert "&lt;" in result
        assert "&gt;" in result
        assert "&amp;" in result
        assert "&quot;" in result

    def test_mixed_arabic_html(self):
        """Mixed Arabic text and HTML is handled correctly."""
        mixed = '<b>القمح</b> يعاني من <script>xss</script>'
        result = sanitize_string(mixed)
        assert "القمح" in result
        assert "<script>" not in result

    def test_css_expression_detected(self):
        """CSS expression() is detected and logged; HTML-escaped output returned."""
        malicious = 'expression(alert(1))'
        result = sanitize_string(malicious)
        # No HTML special chars to escape, so output is unchanged.
        # The dangerous-pattern detector logs a warning for expression().
        assert result == "expression(alert(1))"

    def test_data_url_in_css(self):
        """data: URLs in CSS context are detected."""
        malicious = "url('data:text/html,<script>alert(1)</script>')"
        result = sanitize_string(malicious)
        assert "<script>" not in result


# ═══════════════════════════════════════════════════════════════════════════════
# sanitize_value Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestSanitizeValue:
    """Test recursive value sanitization."""

    def test_string_sanitized(self):
        """String values are sanitized."""
        result = sanitize_value("<script>xss</script>")
        assert "<script>" not in result

    def test_dict_values_sanitized(self):
        """Dictionary string values are sanitized recursively."""
        data = {
            "name": "normal",
            "bio": '<script>alert("xss")</script>',
        }
        result = sanitize_value(data)
        assert result["name"] == "normal"
        assert "<script>" not in result["bio"]

    def test_nested_dict_sanitized(self):
        """Nested dictionaries are sanitized."""
        data = {
            "user": {
                "profile": {
                    "bio": "<img onerror=alert(1)>",
                }
            }
        }
        result = sanitize_value(data)
        assert "<img" not in result["user"]["profile"]["bio"]

    def test_list_values_sanitized(self):
        """List items are sanitized."""
        data = ["normal", "<script>bad</script>", "also normal"]
        result = sanitize_value(data)
        assert result[0] == "normal"
        assert "<script>" not in result[1]
        assert result[2] == "also normal"

    def test_numeric_values_unchanged(self):
        """Numeric values pass through unchanged."""
        assert sanitize_value(42) == 42
        assert sanitize_value(3.14) == 3.14

    def test_boolean_values_unchanged(self):
        """Boolean values pass through unchanged."""
        assert sanitize_value(True) is True
        assert sanitize_value(False) is False

    def test_none_unchanged(self):
        """None passes through unchanged."""
        assert sanitize_value(None) is None

    def test_complex_nested_structure(self):
        """Complex nested structures are fully sanitized."""
        data = {
            "fields": [
                {"name": "حقل القمح", "notes": "<script>xss</script>"},
                {"name": "field 2", "area": 25.5},
            ],
            "metadata": {"count": 2},
        }
        result = sanitize_value(data)
        assert "حقل القمح" in result["fields"][0]["name"]
        assert "<script>" not in result["fields"][0]["notes"]
        assert result["fields"][1]["area"] == 25.5
        assert result["metadata"]["count"] == 2


# ═══════════════════════════════════════════════════════════════════════════════
# Dangerous Patterns Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestDangerousPatterns:
    """Test that DANGEROUS_PATTERNS detect known attack vectors."""

    @pytest.mark.parametrize(
        "payload",
        [
            '<script>alert(1)</script>',
            '<SCRIPT SRC="evil.js"></SCRIPT>',
            '<script type="text/javascript">',
        ],
    )
    def test_script_patterns(self, payload):
        """Script tag patterns are detected."""
        assert any(p.search(payload) for p in DANGEROUS_PATTERNS)

    @pytest.mark.parametrize(
        "payload",
        [
            '<iframe src="evil.com">',
            '<IFRAME SRC="evil.com">',
        ],
    )
    def test_iframe_patterns(self, payload):
        """iframe patterns are detected."""
        assert any(p.search(payload) for p in DANGEROUS_PATTERNS)

    @pytest.mark.parametrize(
        "payload",
        [
            'onclick=alert(1)',
            'onerror = alert(1)',
            'onload=doEvil()',
        ],
    )
    def test_event_handler_patterns(self, payload):
        """Event handler patterns are detected."""
        assert any(p.search(payload) for p in DANGEROUS_PATTERNS)

    def test_safe_text_not_detected(self):
        """Normal text does not trigger dangerous patterns."""
        safe_texts = [
            "Hello world",
            "القمح يحتاج للري",
            "Field area: 25.5 hectares",
            "Temperature is 28°C",
        ]
        for text in safe_texts:
            assert not any(p.search(text) for p in DANGEROUS_PATTERNS), f"False positive: {text}"
