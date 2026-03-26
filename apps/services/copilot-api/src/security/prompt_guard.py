"""
Prompt injection detection for copilot-api - كشف حقن الأوامر للمستشار الذكي
"""

import re

import structlog

logger = structlog.get_logger()

# Patterns indicating prompt injection attempts
INJECTION_PATTERNS: list[tuple[str, str]] = [
    # English injection patterns
    (r"ignore\s+(previous|all|above|prior)\s+(?:[\w-]+\s+)?(instructions|prompts|context)", "ignore_instructions"),
    (r"disregard\s+(your|all|the)\s+(instructions|rules|guidelines)", "disregard_rules"),
    (r"you\s+are\s+now\s+(?:a|an)\s+", "role_override"),
    (r"pretend\s+(?:you(?:'re|\s+are)|to\s+be)\s+", "pretend_role"),
    (r"new\s+(?:system\s+)?(?:instructions?|prompt)", "new_instructions"),
    (r"override\s+(?:system|safety|security)", "override_system"),
    (r"(?:reveal|show|display|output)\s+(?:your|the|system)\s+(?:prompt|instructions|rules)", "reveal_prompt"),
    (r"ADMIN[_\s]?OVERRIDE", "admin_override"),
    # Arabic injection patterns
    (r"تجاهل\s+(?:التعليمات|الأوامر|القواعد)\s+السابقة", "ignore_instructions_ar"),
    (r"أنت\s+الآن\s+", "role_override_ar"),
    (r"تظاهر\s+(?:بأنك|أنك)", "pretend_role_ar"),
    (r"اكشف\s+(?:التعليمات|الأوامر|النظام)", "reveal_prompt_ar"),
    # Technical injection patterns
    (r"<\|(?:im_start|system|endoftext)\|>", "special_tokens"),
    (r"\[INST\]|\[/INST\]|<<SYS>>|<</SYS>>", "llama_tokens"),
    (r"system\s*:\s*(?:you|your|ignore|override|new)", "system_prefix"),
]

# Compile patterns for performance
_COMPILED_PATTERNS = [(re.compile(p, re.IGNORECASE), name) for p, name in INJECTION_PATTERNS]


def detect_prompt_injection(text: str) -> tuple[bool, str | None]:
    """
    Detect potential prompt injection in user input.
    كشف محاولات حقن الأوامر في مدخلات المستخدم.

    Returns:
        Tuple of (is_injection, pattern_name)
    """
    if not text:
        return False, None

    for pattern, name in _COMPILED_PATTERNS:
        if pattern.search(text):
            logger.warning(
                "prompt_injection_detected",
                pattern=name,
                text_preview=text[:100],
            )
            return True, name

    return False, None


def sanitize_input(text: str) -> str:
    """
    Sanitize user input by removing potential injection tokens.
    تنظيف مدخلات المستخدم بإزالة رموز الحقن المحتملة.
    """
    # Remove special LLM tokens
    sanitized = re.sub(r"<\|[^|]+\|>", "", text)
    sanitized = re.sub(r"\[INST\]|\[/INST\]|<<SYS>>|<</SYS>>", "", sanitized)
    # Remove excessive whitespace
    sanitized = re.sub(r"\s+", " ", sanitized).strip()
    return sanitized
