"""
AI Input/Output Validation Module
=================================
وحدة التحقق من مدخلات ومخرجات الذكاء الاصطناعي

Provides comprehensive validation for AI operations including:
- Prompt injection detection
- Output safety validation
- Agricultural advice verification
- Content filtering

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class ValidationLevel(StrEnum):
    """Validation strictness levels."""

    STRICT = "strict"  # Block on any concern
    MODERATE = "moderate"  # Block on medium+ severity
    LENIENT = "lenient"  # Only block critical issues


class ThreatCategory(StrEnum):
    """Categories of detected threats."""

    PROMPT_INJECTION = "prompt_injection"
    JAILBREAK_ATTEMPT = "jailbreak_attempt"
    DATA_EXFILTRATION = "data_exfiltration"
    HARMFUL_CONTENT = "harmful_content"
    PII_EXPOSURE = "pii_exposure"
    UNSAFE_ADVICE = "unsafe_advice"
    HALLUCINATION = "hallucination"
    OFF_TOPIC = "off_topic"


class Severity(StrEnum):
    """Severity levels for validation issues."""

    CRITICAL = "critical"  # Must block
    HIGH = "high"  # Should block
    MEDIUM = "medium"  # Review recommended
    LOW = "low"  # Log only
    INFO = "info"  # Informational


@dataclass
class ValidationIssue:
    """A single validation issue."""

    category: ThreatCategory
    severity: Severity
    message: str
    message_ar: str
    details: dict[str, Any] = field(default_factory=dict)
    location: str | None = None  # Where in the text

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "category": self.category.value,
            "severity": self.severity.value,
            "message": self.message,
            "message_ar": self.message_ar,
            "details": self.details,
            "location": self.location,
        }


@dataclass
class ValidationResult:
    """Result of validation check."""

    is_valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    score: float = 1.0  # 0.0 = unsafe, 1.0 = safe
    processed_text: str | None = None  # Sanitized version if applicable
    metadata: dict[str, Any] = field(default_factory=dict)
    validated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "issues": [i.to_dict() for i in self.issues],
            "score": self.score,
            "has_processed_text": self.processed_text is not None,
            "metadata": self.metadata,
            "validated_at": self.validated_at.isoformat(),
        }

    @property
    def critical_issues(self) -> list[ValidationIssue]:
        """Get critical severity issues."""
        return [i for i in self.issues if i.severity == Severity.CRITICAL]

    @property
    def high_issues(self) -> list[ValidationIssue]:
        """Get high severity issues."""
        return [i for i in self.issues if i.severity == Severity.HIGH]


# Prompt injection patterns
PROMPT_INJECTION_PATTERNS = [
    # Direct instruction override
    (r"ignore\s+(previous|all|above)\s+(instructions?|prompts?)", Severity.CRITICAL),
    (r"disregard\s+(previous|all|above)\s+(instructions?|prompts?)", Severity.CRITICAL),
    (r"forget\s+(everything|all|previous)", Severity.CRITICAL),
    # Role manipulation
    (r"you\s+are\s+now\s+(?:a|an)\s+\w+", Severity.HIGH),
    (r"pretend\s+(?:to\s+be|you\s+are)", Severity.HIGH),
    (r"act\s+as\s+(?:if|a|an)", Severity.HIGH),
    (r"roleplay\s+as", Severity.HIGH),
    # System prompt extraction
    (
        r"(what|show|reveal|display)\s+(is|are)?\s*(your|the)\s+(system|initial)\s+prompt",
        Severity.CRITICAL,
    ),
    (r"repeat\s+(your|the)\s+(system|initial)\s+(prompt|instructions)", Severity.CRITICAL),
    # Encoding tricks
    (r"base64\s*[:=]", Severity.MEDIUM),
    (r"\\x[0-9a-f]{2}", Severity.MEDIUM),
    (r"&#\d+;", Severity.MEDIUM),
    # Delimiter injection
    (r"```\s*(system|assistant|user)\s*\n", Severity.HIGH),
    (r"\[INST\]|\[/INST\]", Severity.HIGH),
    (r"<\|?(system|user|assistant)\|?>", Severity.HIGH),
]

# Jailbreak patterns
JAILBREAK_PATTERNS = [
    (r"DAN\s+mode", Severity.CRITICAL),
    (r"developer\s+mode", Severity.HIGH),
    (r"unrestricted\s+mode", Severity.HIGH),
    (r"no\s+restrictions", Severity.HIGH),
    (r"bypass\s+(safety|filter|restriction)", Severity.CRITICAL),
    (r"disable\s+(safety|filter|restriction)", Severity.CRITICAL),
]

# Unsafe agricultural advice patterns (things we should flag)
UNSAFE_AGRICULTURAL_PATTERNS = [
    # Pesticide misuse
    (
        r"(increase|double|triple)\s+(the\s+)?(dosage|dose|amount)\s+of\s+(pesticide|herbicide|insecticide)",
        Severity.CRITICAL,
    ),
    (r"mix\s+(different\s+)?(pesticides?|chemicals?)\s+together", Severity.HIGH),
    (r"spray\s+during\s+(rain|wind|hot)", Severity.MEDIUM),
    # Food safety
    (r"harvest\s+(immediately|right)\s+after\s+spraying", Severity.CRITICAL),
    (r"ignore\s+(pre-harvest|phi|waiting)\s+(interval|period)", Severity.CRITICAL),
    # Animal welfare
    (r"(withhold|deny)\s+(water|food)\s+from\s+(animals?|livestock)", Severity.HIGH),
]

# PII patterns
PII_PATTERNS = [
    # Credit cards
    (r"\b(?:\d{4}[-\s]?){3}\d{4}\b", Severity.HIGH, "credit_card"),
    # Phone numbers (various formats)
    (r"\b(?:\+966|00966|05)\d{8,9}\b", Severity.MEDIUM, "phone_sa"),
    (r"\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", Severity.MEDIUM, "phone"),
    # Email
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", Severity.LOW, "email"),
    # Saudi ID
    (r"\b[12]\d{9}\b", Severity.HIGH, "saudi_id"),
    # Passport
    (r"\b[A-Z]{1,2}\d{6,9}\b", Severity.MEDIUM, "passport"),
]


class AIValidator:
    """
    Validator for AI inputs and outputs.

    مدقق لمدخلات ومخرجات الذكاء الاصطناعي

    Example:
        validator = AIValidator(level=ValidationLevel.MODERATE)

        # Validate input prompt
        input_result = validator.validate_input("Tell me about wheat irrigation")
        if not input_result.is_valid:
            raise ValueError(f"Invalid input: {input_result.issues}")

        # Get AI response...

        # Validate output
        output_result = validator.validate_output(
            response_text,
            context={"crop_type": "wheat", "topic": "irrigation"}
        )
        if not output_result.is_valid:
            # Handle unsafe output
            pass
    """

    def __init__(
        self,
        level: ValidationLevel = ValidationLevel.MODERATE,
        enable_pii_detection: bool = True,
        enable_agricultural_safety: bool = True,
        custom_patterns: list[tuple[str, Severity]] | None = None,
    ):
        """
        Initialize AIValidator.

        Args:
            level: Validation strictness level
            enable_pii_detection: Enable PII detection
            enable_agricultural_safety: Enable agricultural advice validation
            custom_patterns: Additional custom regex patterns
        """
        self.level = level
        self.enable_pii_detection = enable_pii_detection
        self.enable_agricultural_safety = enable_agricultural_safety
        self.custom_patterns = custom_patterns or []

    def validate_input(
        self,
        text: str,
        context: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """
        Validate input text (user prompt).

        التحقق من نص المدخل (طلب المستخدم)

        Args:
            text: Input text to validate
            context: Optional context (user_id, tenant_id, etc.)

        Returns:
            ValidationResult
        """
        issues: list[ValidationIssue] = []
        text_lower = text.lower()

        # Check prompt injection
        for pattern, severity in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                issues.append(
                    ValidationIssue(
                        category=ThreatCategory.PROMPT_INJECTION,
                        severity=severity,
                        message="Potential prompt injection detected",
                        message_ar="تم اكتشاف محاولة حقن أوامر محتملة",
                        details={"pattern": pattern},
                    )
                )

        # Check jailbreak attempts
        for pattern, severity in JAILBREAK_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                issues.append(
                    ValidationIssue(
                        category=ThreatCategory.JAILBREAK_ATTEMPT,
                        severity=severity,
                        message="Potential jailbreak attempt detected",
                        message_ar="تم اكتشاف محاولة تجاوز القيود",
                        details={"pattern": pattern},
                    )
                )

        # Check PII in input
        if self.enable_pii_detection:
            pii_issues = self._detect_pii(text)
            issues.extend(pii_issues)

        # Check custom patterns
        for pattern, severity in self.custom_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append(
                    ValidationIssue(
                        category=ThreatCategory.HARMFUL_CONTENT,
                        severity=severity,
                        message="Custom pattern matched",
                        message_ar="تم مطابقة نمط مخصص",
                        details={"pattern": pattern},
                    )
                )

        return self._build_result(text, issues)

    def validate_output(
        self,
        text: str,
        context: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """
        Validate output text (AI response).

        التحقق من نص المخرج (استجابة الذكاء الاصطناعي)

        Args:
            text: Output text to validate
            context: Optional context (crop_type, topic, etc.)

        Returns:
            ValidationResult
        """
        issues: list[ValidationIssue] = []
        context = context or {}

        # Check PII in output
        if self.enable_pii_detection:
            pii_issues = self._detect_pii(text)
            issues.extend(pii_issues)

        # Check agricultural safety
        if self.enable_agricultural_safety:
            ag_issues = self._check_agricultural_safety(text, context)
            issues.extend(ag_issues)

        # Check for potential hallucination indicators
        hallucination_issues = self._check_hallucination_indicators(text)
        issues.extend(hallucination_issues)

        # Check for harmful content
        harmful_issues = self._check_harmful_content(text)
        issues.extend(harmful_issues)

        return self._build_result(text, issues)

    def _detect_pii(self, text: str) -> list[ValidationIssue]:
        """Detect PII in text."""
        issues = []
        for item in PII_PATTERNS:
            pattern, severity, pii_type = item[0], item[1], item[2] if len(item) > 2 else "unknown"
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                issues.append(
                    ValidationIssue(
                        category=ThreatCategory.PII_EXPOSURE,
                        severity=severity,
                        message=f"Potential PII detected: {pii_type}",
                        message_ar=f"تم اكتشاف بيانات شخصية محتملة: {pii_type}",
                        details={"type": pii_type, "count": len(matches)},
                    )
                )
        return issues

    def _check_agricultural_safety(
        self,
        text: str,
        context: dict[str, Any],
    ) -> list[ValidationIssue]:
        """Check agricultural advice safety."""
        issues = []
        text_lower = text.lower()

        for pattern, severity in UNSAFE_AGRICULTURAL_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                issues.append(
                    ValidationIssue(
                        category=ThreatCategory.UNSAFE_ADVICE,
                        severity=severity,
                        message="Potentially unsafe agricultural advice detected",
                        message_ar="تم اكتشاف نصيحة زراعية قد تكون غير آمنة",
                        details={"pattern": pattern},
                    )
                )

        return issues

    def _check_hallucination_indicators(self, text: str) -> list[ValidationIssue]:
        """Check for potential hallucination indicators."""
        issues = []
        text_lower = text.lower()

        # Overconfident statements about uncertain topics
        overconfident_patterns = [
            r"(definitely|certainly|absolutely|100%)\s+(will|is|are|can)",
            r"guaranteed\s+to\s+(work|succeed|help)",
            r"never\s+fails?",
            r"always\s+works?",
        ]

        for pattern in overconfident_patterns:
            if re.search(pattern, text_lower):
                issues.append(
                    ValidationIssue(
                        category=ThreatCategory.HALLUCINATION,
                        severity=Severity.LOW,
                        message="Potentially overconfident statement",
                        message_ar="عبارة قد تكون مفرطة في الثقة",
                        details={"pattern": pattern},
                    )
                )

        # Specific numbers without context (potential hallucination)
        specific_stats = re.findall(r"\b\d+(?:\.\d+)?%\b", text)
        if len(specific_stats) > 3:
            issues.append(
                ValidationIssue(
                    category=ThreatCategory.HALLUCINATION,
                    severity=Severity.INFO,
                    message="Multiple specific statistics detected - verify accuracy",
                    message_ar="تم اكتشاف إحصائيات متعددة محددة - تحقق من الدقة",
                    details={"count": len(specific_stats)},
                )
            )

        return issues

    def _check_harmful_content(self, text: str) -> list[ValidationIssue]:
        """Check for harmful content."""
        issues = []
        text_lower = text.lower()

        harmful_patterns = [
            (r"(kill|poison|harm)\s+(all\s+)?(plants?|crops?|animals?)", Severity.HIGH),
            (r"(illegal|banned|prohibited)\s+(pesticide|chemical|substance)", Severity.MEDIUM),
        ]

        for pattern, severity in harmful_patterns:
            if re.search(pattern, text_lower):
                issues.append(
                    ValidationIssue(
                        category=ThreatCategory.HARMFUL_CONTENT,
                        severity=severity,
                        message="Potentially harmful content detected",
                        message_ar="تم اكتشاف محتوى قد يكون ضاراً",
                        details={"pattern": pattern},
                    )
                )

        return issues

    def _build_result(
        self,
        text: str,
        issues: list[ValidationIssue],
    ) -> ValidationResult:
        """Build validation result based on level."""
        # Calculate score based on issues
        score = 1.0
        for issue in issues:
            if issue.severity == Severity.CRITICAL:
                score -= 0.4
            elif issue.severity == Severity.HIGH:
                score -= 0.25
            elif issue.severity == Severity.MEDIUM:
                score -= 0.15
            elif issue.severity == Severity.LOW:
                score -= 0.05
        score = max(0.0, score)

        # Determine validity based on level
        is_valid = True
        if self.level == ValidationLevel.STRICT:
            is_valid = len(issues) == 0
        elif self.level == ValidationLevel.MODERATE:
            is_valid = not any(i.severity in [Severity.CRITICAL, Severity.HIGH] for i in issues)
        else:  # LENIENT
            is_valid = not any(i.severity == Severity.CRITICAL for i in issues)

        return ValidationResult(
            is_valid=is_valid,
            issues=issues,
            score=round(score, 2),
            metadata={"level": self.level.value},
        )

    def sanitize_input(self, text: str) -> str:
        """
        Sanitize input text by removing potentially harmful patterns.

        تنظيف نص المدخل بإزالة الأنماط الضارة المحتملة
        """
        sanitized = text

        # Remove common injection patterns
        for pattern, _ in PROMPT_INJECTION_PATTERNS:
            sanitized = re.sub(pattern, "[REMOVED]", sanitized, flags=re.IGNORECASE)

        for pattern, _ in JAILBREAK_PATTERNS:
            sanitized = re.sub(pattern, "[REMOVED]", sanitized, flags=re.IGNORECASE)

        return sanitized

    def redact_pii(self, text: str) -> str:
        """
        Redact PII from text.

        حجب البيانات الشخصية من النص
        """
        redacted = text

        for item in PII_PATTERNS:
            pattern = item[0]
            pii_type = item[2] if len(item) > 2 else "PII"
            redacted = re.sub(pattern, f"[{pii_type.upper()}_REDACTED]", redacted, flags=re.IGNORECASE)

        return redacted


# ─────────────────────────────────────────────────────────────────────────────
# Prompt Sanitizer — تنظيف مدخلات الـ Prompt
# ─────────────────────────────────────────────────────────────────────────────

# Patterns that could break out of prompt structure
_DELIMITER_ESCAPE_PATTERNS = [
    (re.compile(r"```\s*(system|assistant|user|python|javascript|sql)\s*\n", re.IGNORECASE), "`` `"),
    (re.compile(r"\[INST\]", re.IGNORECASE), "[inst]"),
    (re.compile(r"\[/INST\]", re.IGNORECASE), "[/inst]"),
    (re.compile(r"<\|?(system|user|assistant)\|?>", re.IGNORECASE), r"<\1>"),
    (re.compile(r"<<SYS>>", re.IGNORECASE), "<<sys>>"),
    (re.compile(r"<</SYS>>", re.IGNORECASE), "<</sys>>"),
]


def escape_prompt_input(text: str, max_length: int = 10000) -> str:
    """
    Escape user input before embedding in LLM prompts.

    تنظيف مدخلات المستخدم قبل إدراجها في prompts الـ LLM

    This neutralizes delimiter injection attacks while preserving
    the semantic content of the input.

    Args:
        text: Raw user input to escape
        max_length: Maximum allowed length (truncate if exceeded)

    Returns:
        Escaped text safe for embedding in prompts
    """
    if not text:
        return text

    # Truncate to prevent token exhaustion
    escaped = text[:max_length]

    # Neutralize prompt delimiter patterns
    for pattern, replacement in _DELIMITER_ESCAPE_PATTERNS:
        escaped = pattern.sub(replacement, escaped)

    return escaped


# Global validator instance
_global_validator: AIValidator | None = None


def get_validator(level: ValidationLevel = ValidationLevel.MODERATE) -> AIValidator:
    """
    Get or create the global validator.

    الحصول على أو إنشاء المدقق العالمي
    """
    global _global_validator
    if _global_validator is None or _global_validator.level != level:
        _global_validator = AIValidator(level=level)
    return _global_validator


# Convenience functions
def validate_prompt(text: str, level: ValidationLevel = ValidationLevel.MODERATE) -> ValidationResult:
    """
    Validate a user prompt.

    التحقق من طلب المستخدم
    """
    return get_validator(level).validate_input(text)


def validate_response(
    text: str,
    context: dict[str, Any] | None = None,
    level: ValidationLevel = ValidationLevel.MODERATE,
) -> ValidationResult:
    """
    Validate an AI response.

    التحقق من استجابة الذكاء الاصطناعي
    """
    return get_validator(level).validate_output(text, context)


def is_safe_prompt(text: str) -> bool:
    """
    Quick check if prompt is safe.

    فحص سريع إذا كان الطلب آمناً
    """
    return validate_prompt(text, ValidationLevel.MODERATE).is_valid


def is_safe_response(text: str) -> bool:
    """
    Quick check if response is safe.

    فحص سريع إذا كانت الاستجابة آمنة
    """
    return validate_response(text, level=ValidationLevel.MODERATE).is_valid
