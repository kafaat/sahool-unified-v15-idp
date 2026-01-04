"""
AI Safety Guardrails - Input Filtering
======================================
Comprehensive input validation and filtering for AI requests.
Implements prompt injection detection, PII masking, toxic content filtering.

Based on Google's Secure AI Agents framework and OWASP LLM Top 10.

Author: SAHOOL Platform Team
Updated: December 2025
"""

import hashlib
import logging
import re
from dataclasses import dataclass

from .policies import (
    ContentSafetyLevel,
    PolicyManager,
    TrustLevel,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Input Filter Results
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class InputFilterResult:
    """Result from input filtering"""

    is_safe: bool
    filtered_text: str
    safety_level: ContentSafetyLevel
    violations: list[str]
    warnings: list[str]
    metadata: dict[str, any]

    # Arabic translations for violations
    violations_ar: list[str] = None
    warnings_ar: list[str] = None

    def __post_init__(self):
        if self.violations_ar is None:
            self.violations_ar = []
        if self.warnings_ar is None:
            self.warnings_ar = []


# ─────────────────────────────────────────────────────────────────────────────
# Prompt Injection Detector
# ─────────────────────────────────────────────────────────────────────────────


class PromptInjectionDetector:
    """
    Detects prompt injection attacks using pattern matching and heuristics.

    Based on OWASP LLM01: Prompt Injection vulnerabilities.
    """

    def __init__(self):
        # System prompt override patterns
        self.override_patterns = [
            r"ignore\s+(previous|above|prior)\s+(instructions|prompts?|commands?)",
            r"disregard\s+(previous|above|all)\s+(instructions|prompts?)",
            r"forget\s+(everything|all|previous|above)",
            r"new\s+(instructions|commands?|task|role)",
            r"you\s+are\s+now\s+a?\s*\w+",
            r"act\s+as\s+a?\s*\w+",
            r"pretend\s+to\s+be",
            r"تجاهل\s+التعليمات",
            r"انسى\s+كل\s+شيء",
        ]

        # Data exfiltration patterns
        self.exfiltration_patterns = [
            r"show\s+(me\s+)?(the\s+)?system\s+(prompt|instructions)",
            r"reveal\s+(the\s+)?(system|hidden)\s+(prompt|instructions)",
            r"what\s+(are|were)\s+your\s+(original|system)\s+instructions",
            r"repeat\s+(your|the)\s+(instructions|prompt)",
            r"أظهر\s+التعليمات",
        ]

        # Role confusion patterns
        self.role_confusion_patterns = [
            r"(as|like)\s+a\s+(developer|admin|system|root|superuser)",
            r"sudo\s+",
            r"with\s+(admin|root|system)\s+(access|privileges|rights)",
        ]

        # Escape sequence patterns
        self.escape_patterns = [
            r"```\s*system",
            r"```\s*assistant",
            r"<\|im_start\|>",
            r"<\|im_end\|>",
            r"\[SYSTEM\]",
            r"\[INST\]",
        ]

        # Compile all patterns
        self.all_patterns = (
            self.override_patterns
            + self.exfiltration_patterns
            + self.role_confusion_patterns
            + self.escape_patterns
        )
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.all_patterns
        ]

    def detect(self, text: str) -> tuple[bool, list[str]]:
        """
        Detect prompt injection attempts.

        Args:
            text: Input text to analyze

        Returns:
            Tuple of (is_injection_detected, list_of_matched_patterns)
        """
        detected_patterns = []

        for pattern, compiled_pattern in zip(self.all_patterns, self.compiled_patterns, strict=False):
            if compiled_pattern.search(text):
                detected_patterns.append(pattern)
                logger.warning(f"Prompt injection pattern detected: {pattern}")

        # Check for excessive special characters (potential encoding attack)
        special_char_ratio = sum(
            1 for c in text if not c.isalnum() and not c.isspace()
        ) / max(len(text), 1)
        if special_char_ratio > 0.4:
            detected_patterns.append("excessive_special_characters")
            logger.warning(f"Excessive special characters: {special_char_ratio:.2%}")

        # Check for repeated newlines (potential prompt boundary confusion)
        if "\n\n\n" in text or text.count("\n") > len(text) / 20:
            detected_patterns.append("excessive_newlines")

        is_detected = len(detected_patterns) > 0
        return is_detected, detected_patterns


# ─────────────────────────────────────────────────────────────────────────────
# PII Detector & Masker
# ─────────────────────────────────────────────────────────────────────────────


class PIIDetector:
    """
    Detects and masks Personally Identifiable Information (PII).

    Supports:
    - Email addresses
    - Phone numbers (international & Saudi formats)
    - National IDs / SSN
    - Credit card numbers
    - IP addresses
    - Saudi-specific: Iqama numbers, CR numbers
    """

    def __init__(self):
        # PII patterns
        self.patterns = {
            "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
            "phone": re.compile(
                r"(\+?966|00966|0)?[-\s]?5\d{8}"  # Saudi phone
                r"|\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}"  # International
            ),
            "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # US SSN
            "iqama": re.compile(
                r"\b[12]\d{9}\b"
            ),  # Saudi Iqama (10 digits starting with 1 or 2)
            "national_id": re.compile(r"\b1\d{9}\b"),  # Saudi National ID
            "cr_number": re.compile(r"\b[47]\d{9}\b"),  # Saudi CR number
            "credit_card": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),  # 16-digit card
            "ipv4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
            "ipv6": re.compile(r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b"),
        }

    def detect_and_mask(
        self, text: str, mask_char: str = "*"
    ) -> tuple[str, dict[str, int]]:
        """
        Detect and mask PII in text.

        Args:
            text: Input text
            mask_char: Character to use for masking

        Returns:
            Tuple of (masked_text, pii_counts_by_type)
        """
        masked_text = text
        pii_counts = {}

        for pii_type, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                count = len(matches)
                pii_counts[pii_type] = count

                # Mask each match
                for match in matches:
                    # Handle tuple matches (from groups)
                    match_str = match if isinstance(match, str) else match[0]

                    # Keep first and last 2 characters visible for debugging
                    if len(match_str) > 6:
                        masked = (
                            match_str[:2]
                            + mask_char * (len(match_str) - 4)
                            + match_str[-2:]
                        )
                    else:
                        masked = mask_char * len(match_str)

                    masked_text = masked_text.replace(match_str, masked)

                logger.info(f"Masked {count} instances of {pii_type}")

        return masked_text, pii_counts

    def contains_pii(self, text: str) -> bool:
        """Quick check if text contains any PII"""
        for pattern in self.patterns.values():
            if pattern.search(text):
                return True
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Toxicity Filter
# ─────────────────────────────────────────────────────────────────────────────


class ToxicityFilter:
    """
    Detects toxic, harmful, or offensive content.

    Uses keyword-based approach for production readiness.
    Can be extended with ML models (e.g., Perspective API, Detoxify).
    """

    def __init__(self):
        # Toxic keywords - English & Arabic
        self.toxic_keywords = {
            # Profanity
            "profanity": {
                "fuck",
                "shit",
                "damn",
                "ass",
                "bitch",
                "كلب",
                "حمار",
                "غبي",
            },
            # Hate speech
            "hate": {
                "hate",
                "kill",
                "die",
                "death",
                "اقتل",
                "موت",
                "كراهية",
            },
            # Threats
            "threats": {
                "threat",
                "attack",
                "bomb",
                "weapon",
                "تهديد",
                "هجوم",
                "قنبلة",
            },
            # Sexual content
            "sexual": {
                "sex",
                "porn",
                "nude",
                "xxx",
            },
        }

        # Compile keyword patterns
        all_keywords = set()
        for category_keywords in self.toxic_keywords.values():
            all_keywords.update(category_keywords)

        self.keyword_pattern = re.compile(
            r"\b(" + "|".join(re.escape(k) for k in all_keywords) + r")\b",
            re.IGNORECASE,
        )

    def analyze(self, text: str) -> tuple[float, dict[str, int]]:
        """
        Analyze text for toxicity.

        Args:
            text: Input text

        Returns:
            Tuple of (toxicity_score, category_counts)
        """
        text_lower = text.lower()
        category_counts = {}
        total_toxic_words = 0

        # Count toxic words by category
        for category, keywords in self.toxic_keywords.items():
            count = sum(1 for keyword in keywords if keyword.lower() in text_lower)
            if count > 0:
                category_counts[category] = count
                total_toxic_words += count

        # Calculate toxicity score (0-1)
        # Simple heuristic: ratio of toxic words to total words
        words = text.split()
        word_count = len(words)
        if word_count == 0:
            toxicity_score = 0.0
        else:
            toxicity_score = min(total_toxic_words / word_count * 5, 1.0)

        return toxicity_score, category_counts

    def is_toxic(self, text: str, threshold: float = 0.7) -> bool:
        """Check if text exceeds toxicity threshold"""
        score, _ = self.analyze(text)
        return score >= threshold


# ─────────────────────────────────────────────────────────────────────────────
# Main Input Filter
# ─────────────────────────────────────────────────────────────────────────────


class InputFilter:
    """
    Main input filter coordinating all safety checks.

    Usage:
        filter = InputFilter()
        result = filter.filter_input(
            text="User input here",
            trust_level=TrustLevel.BASIC
        )
        if not result.is_safe:
            raise HTTPException(400, detail=result.violations)
    """

    def __init__(self, policy_manager: PolicyManager | None = None):
        self.policy_manager = policy_manager or PolicyManager()
        self.prompt_injection_detector = PromptInjectionDetector()
        self.pii_detector = PIIDetector()
        self.toxicity_filter = ToxicityFilter()

    def filter_input(
        self,
        text: str,
        trust_level: TrustLevel = TrustLevel.BASIC,
        mask_pii: bool = True,
        strict_topic_check: bool = False,
    ) -> InputFilterResult:
        """
        Comprehensive input filtering.

        Args:
            text: Input text to filter
            trust_level: User's trust level
            mask_pii: Whether to mask PII
            strict_topic_check: Require explicit topic match

        Returns:
            InputFilterResult with safety assessment
        """
        violations = []
        violations_ar = []
        warnings = []
        warnings_ar = []
        metadata = {}
        filtered_text = text

        # Get policy for trust level
        policy = self.policy_manager.get_input_policy(trust_level)

        # 1. Check input length
        if len(text) > policy.max_input_length:
            violations.append(
                f"Input exceeds maximum length ({len(text)} > {policy.max_input_length})"
            )
            violations_ar.append(
                f"المدخل يتجاوز الحد الأقصى للطول ({len(text)} > {policy.max_input_length})"
            )
            metadata["input_length"] = len(text)

        # 2. Check for prompt injection
        if policy.check_prompt_injection:
            is_injection, patterns = self.prompt_injection_detector.detect(text)
            if is_injection:
                violations.append(f"Prompt injection detected: {patterns}")
                violations_ar.append(f"تم اكتشاف حقن التعليمات: {patterns}")
                metadata["injection_patterns"] = patterns

        # 3. Check for PII
        if policy.check_pii:
            has_pii = self.pii_detector.contains_pii(text)
            if has_pii:
                if mask_pii:
                    filtered_text, pii_counts = self.pii_detector.detect_and_mask(text)
                    warnings.append(f"PII detected and masked: {pii_counts}")
                    warnings_ar.append(
                        f"تم اكتشاف وإخفاء المعلومات الشخصية: {pii_counts}"
                    )
                    metadata["pii_masked"] = pii_counts
                else:
                    violations.append("PII detected in input")
                    violations_ar.append("تم اكتشاف معلومات شخصية في المدخل")
                    metadata["has_pii"] = True

        # 4. Check toxicity
        if policy.check_toxicity:
            toxicity_score, toxic_categories = self.toxicity_filter.analyze(text)
            metadata["toxicity_score"] = toxicity_score
            metadata["toxic_categories"] = toxic_categories

            if toxicity_score >= policy.toxicity_threshold:
                violations.append(
                    f"Content toxicity too high: {toxicity_score:.2f} >= {policy.toxicity_threshold}"
                )
                violations_ar.append(
                    f"محتوى سام: {toxicity_score:.2f} >= {policy.toxicity_threshold}"
                )
            elif toxicity_score > 0.3:
                warnings.append(f"Moderate toxicity detected: {toxicity_score:.2f}")
                warnings_ar.append(f"تم اكتشاف سمية معتدلة: {toxicity_score:.2f}")

        # 5. Check topic relevance
        if policy.require_topic_relevance or strict_topic_check:
            # Check for blocked topics
            if self.policy_manager.topic_policy.is_blocked(text):
                violations.append("Input contains blocked topics")
                violations_ar.append("المدخل يحتوي على مواضيع محظورة")
                metadata["blocked_topic"] = True

            # Check for allowed topics in strict mode
            if strict_topic_check:
                if not self.policy_manager.topic_policy.is_allowed(text):
                    violations.append("Input topic not relevant to agriculture")
                    violations_ar.append("موضوع المدخل غير متعلق بالزراعة")
                    metadata["topic_irrelevant"] = True

            # Check for sensitive topics
            if self.policy_manager.topic_policy.is_sensitive(text):
                warnings.append("Input contains sensitive topics")
                warnings_ar.append("المدخل يحتوي على مواضيع حساسة")
                metadata["sensitive_topic"] = True

        # Determine overall safety level
        safety_level = self.policy_manager.get_content_safety_level(
            has_blocked_topic=metadata.get("blocked_topic", False),
            has_sensitive_topic=metadata.get("sensitive_topic", False),
            has_pii=metadata.get("has_pii", False),
            toxicity_score=metadata.get("toxicity_score", 0.0),
            has_prompt_injection=bool(metadata.get("injection_patterns")),
        )

        is_safe = len(violations) == 0 and safety_level not in [
            ContentSafetyLevel.CRITICAL,
            ContentSafetyLevel.HIGH_RISK,
        ]

        return InputFilterResult(
            is_safe=is_safe,
            filtered_text=filtered_text,
            safety_level=safety_level,
            violations=violations,
            warnings=warnings,
            violations_ar=violations_ar,
            warnings_ar=warnings_ar,
            metadata=metadata,
        )

    def quick_check(self, text: str) -> bool:
        """
        Quick safety check without full filtering.

        Returns:
            True if appears safe, False otherwise
        """
        # Quick checks
        if len(text) > 50000:
            return False

        if self.prompt_injection_detector.detect(text)[0]:
            return False

        if self.toxicity_filter.is_toxic(text, threshold=0.8):
            return False

        return True


# ─────────────────────────────────────────────────────────────────────────────
# Utility Functions
# ─────────────────────────────────────────────────────────────────────────────


def sanitize_input(text: str) -> str:
    """
    Basic input sanitization.

    Args:
        text: Input text

    Returns:
        Sanitized text
    """
    # Remove null bytes
    text = text.replace("\x00", "")

    # Normalize whitespace
    text = " ".join(text.split())

    # Remove control characters (except newline, tab, carriage return)
    text = "".join(
        char for char in text if char.isprintable() or char in ["\n", "\t", "\r"]
    )

    return text.strip()


def compute_input_hash(text: str) -> str:
    """
    Compute hash of input for deduplication/caching.

    Args:
        text: Input text

    Returns:
        SHA256 hash
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# Global input filter instance
input_filter = InputFilter()
