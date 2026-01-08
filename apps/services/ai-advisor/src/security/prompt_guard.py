"""
Prompt Injection Guard
حماية من حقن الأوامر
"""

import logging
import re

logger = logging.getLogger(__name__)


class PromptGuard:
    """Guards against prompt injection attacks"""

    # Dangerous patterns that might indicate injection attempts
    INJECTION_PATTERNS = [
        # Ignore/override instructions
        r"ignore\s+(all\s+)?(previous|above|prior)\s+(instructions?|prompts?|rules?)",
        r"disregard\s+(all\s+)?(previous|above|prior)",
        r"forget\s+(everything|all|what)\s+(you|i)\s+(said|told|wrote)",
        # Role manipulation
        r"you\s+are\s+(now|no\s+longer)\s+a",
        r"pretend\s+(to\s+be|you\s+are)",
        r"act\s+as\s+(if|a)",
        r"roleplay\s+as",
        r"switch\s+to\s+.*\s+mode",
        # System prompt extraction
        r"(show|reveal|display|print|output)\s+(your|the)\s+(system\s+)?(prompt|instructions)",
        r"what\s+(are|is)\s+your\s+(system\s+)?(prompt|instructions)",
        r"repeat\s+(your|the)\s+(system\s+)?prompt",
        # Jailbreak attempts
        r"dan\s+mode",
        r"developer\s+mode",
        r"jailbreak",
        r"bypass\s+(safety|filter|restriction)",
        # Code execution attempts
        r"execute\s+(this\s+)?(code|command|script)",
        r"run\s+(this\s+)?(code|command|script)",
        r"eval\s*\(",
        r"exec\s*\(",
        # Data exfiltration
        r"(send|post|transmit)\s+(to|data\s+to)\s+",
        r"fetch\s+from\s+url",
        # Arabic injection patterns
        r"تجاهل\s+(كل|جميع)\s+التعليمات",
        r"انس\s+(كل|ما)\s+قلته",
        r"تصرف\s+ك",
    ]

    # Compile patterns for performance
    _compiled_patterns = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]

    # Maximum input length
    MAX_INPUT_LENGTH = 10000

    @classmethod
    def sanitize(cls, text: str) -> str:
        """Sanitize input text by removing potentially dangerous content"""
        if not text:
            return text

        # Remove null bytes
        text = text.replace("\x00", "")

        # Remove control characters (except newlines and tabs)
        text = "".join(
            char for char in text if char == "\n" or char == "\t" or not (0 <= ord(char) < 32)
        )

        # Normalize whitespace
        text = " ".join(text.split())

        # Truncate if too long
        if len(text) > cls.MAX_INPUT_LENGTH:
            text = text[: cls.MAX_INPUT_LENGTH]
            logger.warning(f"Input truncated to {cls.MAX_INPUT_LENGTH} characters")

        return text

    @classmethod
    def detect_injection(cls, text: str) -> tuple[bool, list[str]]:
        """
        Detect potential prompt injection attempts
        Returns: (is_suspicious, matched_patterns)
        """
        if not text:
            return False, []

        matched = []
        text_lower = text.lower()

        for i, pattern in enumerate(cls._compiled_patterns):
            if pattern.search(text_lower):
                matched.append(cls.INJECTION_PATTERNS[i])

        is_suspicious = len(matched) > 0

        if is_suspicious:
            logger.warning(f"Potential prompt injection detected. Patterns: {matched}")

        return is_suspicious, matched

    @classmethod
    def validate_and_sanitize(cls, text: str, strict: bool = False) -> tuple[str, bool, list[str]]:
        """
        Validate and sanitize input text

        Args:
            text: Input text to validate
            strict: If True, reject suspicious inputs entirely

        Returns:
            (sanitized_text, is_safe, warnings)
        """
        sanitized = cls.sanitize(text)
        is_suspicious, patterns = cls.detect_injection(sanitized)

        if is_suspicious and strict:
            return "", False, patterns

        return sanitized, not is_suspicious, patterns


def guard_prompt(user_input: str, strict: bool = False) -> str:
    """
    Decorator-friendly function to guard prompts

    Raises:
        ValueError: If injection detected in strict mode
    """
    sanitized, is_safe, warnings = PromptGuard.validate_and_sanitize(user_input, strict)

    if not is_safe and strict:
        raise ValueError(f"Potential prompt injection detected: {warnings}")

    return sanitized
