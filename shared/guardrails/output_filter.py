"""
AI Safety Guardrails - Output Filtering
=======================================
Comprehensive output validation and filtering for AI responses.
Implements safety checks, PII leakage prevention, hallucination detection.

Based on Google's Secure AI Agents framework.

Author: SAHOOL Platform Team
Updated: December 2025
"""

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
# Output Filter Results
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class OutputFilterResult:
    """Result from output filtering"""

    is_safe: bool
    filtered_output: str
    safety_level: ContentSafetyLevel
    warnings: list[str]
    metadata: dict[str, any]

    # Flags for specific issues
    has_pii_leakage: bool = False
    has_hallucination_markers: bool = False
    requires_citation: bool = False


# ─────────────────────────────────────────────────────────────────────────────
# Hallucination Detector
# ─────────────────────────────────────────────────────────────────────────────


class HallucinationDetector:
    """
    Detects potential hallucinations in AI-generated content.

    Uses heuristics to identify:
    - Uncertainty markers
    - Contradictions
    - Unverifiable claims
    - Lack of grounding
    """

    def __init__(self):
        # Uncertainty markers (phrases indicating the model is unsure)
        self.uncertainty_markers = [
            # English
            r"\bi\s+(think|believe|assume|suppose|guess)",
            r"(probably|possibly|perhaps|maybe|might|could be|may be)",
            r"i'?m not (sure|certain|confident)",
            r"to the best of my knowledge",
            r"i don'?t have (access|information)",
            r"i cannot (verify|confirm)",
            # Arabic
            r"أعتقد",
            r"ربما",
            r"قد يكون",
            r"لست متأكد",
            r"ليس لدي معلومات",
        ]

        # Unverifiable claim markers
        self.unverifiable_patterns = [
            r"studies show",
            r"research indicates",
            r"experts say",
            r"it is known that",
            r"according to (recent|latest) (data|research|studies)",
        ]

        # Self-referential statements (model referring to itself)
        self.self_reference_patterns = [
            r"\bas an AI",
            r"\bi am (a|an) (AI|language model|assistant)",
            r"i was (trained|created|developed)",
            r"my (training|knowledge) (data|cutoff)",
        ]

        # Compile patterns
        self.uncertainty_regex = re.compile("|".join(self.uncertainty_markers), re.IGNORECASE)
        self.unverifiable_regex = re.compile("|".join(self.unverifiable_patterns), re.IGNORECASE)
        self.self_reference_regex = re.compile(
            "|".join(self.self_reference_patterns), re.IGNORECASE
        )

    def detect(self, text: str) -> tuple[bool, list[str], float]:
        """
        Detect hallucination markers in text.

        Args:
            text: Output text to analyze

        Returns:
            Tuple of (has_markers, list_of_markers, confidence_score)
        """
        markers = []
        confidence_score = 1.0  # Start with high confidence

        # Check for uncertainty
        uncertainty_matches = self.uncertainty_regex.findall(text)
        if uncertainty_matches:
            markers.append("uncertainty")
            confidence_score -= len(uncertainty_matches) * 0.1

        # Check for unverifiable claims
        unverifiable_matches = self.unverifiable_regex.findall(text)
        if unverifiable_matches:
            markers.append("unverifiable_claims")
            confidence_score -= len(unverifiable_matches) * 0.15

        # Check for self-reference (model breaking character)
        self_ref_matches = self.self_reference_regex.findall(text)
        if self_ref_matches:
            markers.append("self_reference")
            confidence_score -= len(self_ref_matches) * 0.2

        # Check for specific numbers/dates (often hallucinated)
        specific_numbers = re.findall(r"\b\d{4,}\b", text)  # 4+ digit numbers
        if len(specific_numbers) > 5:
            markers.append("excessive_specific_numbers")
            confidence_score -= 0.1

        # Check for contradictions (simple check: repeated negations)
        negations = len(re.findall(r"\b(not|no|never|neither|nor)\b", text, re.IGNORECASE))
        if negations > len(text.split()) * 0.1:  # More than 10% negations
            markers.append("excessive_negations")
            confidence_score -= 0.1

        # Clamp confidence score
        confidence_score = max(0.0, min(1.0, confidence_score))

        has_markers = len(markers) > 0
        return has_markers, markers, confidence_score

    def add_disclaimer(self, text: str, language: str = "en") -> str:
        """
        Add hallucination disclaimer to output.

        Args:
            text: Original text
            language: 'en' or 'ar'

        Returns:
            Text with disclaimer
        """
        if language == "ar":
            disclaimer = (
                "\n\n⚠️ تنبيه: هذه المعلومات مُولدة بواسطة الذكاء الاصطناعي. "
                "يُرجى التحقق من المعلومات الهامة مع مصادر موثوقة."
            )
        else:
            disclaimer = (
                "\n\n⚠️ Disclaimer: This information is AI-generated. "
                "Please verify important information with authoritative sources."
            )

        return text + disclaimer


# ─────────────────────────────────────────────────────────────────────────────
# Safety Content Checker
# ─────────────────────────────────────────────────────────────────────────────


class SafetyContentChecker:
    """
    Checks output content for safety issues.

    Ensures AI doesn't generate:
    - Harmful instructions
    - Dangerous advice
    - Biased content
    - Inappropriate content
    """

    def __init__(self):
        # Harmful instruction patterns
        self.harmful_patterns = [
            r"how to (make|create|build) (a )?(bomb|weapon|explosive)",
            r"how to (harm|hurt|kill|attack)",
            r"instructions for (illegal|harmful)",
            # Arabic
            r"كيف (تصنع|تعمل) (قنبلة|سلاح)",
            r"كيف (تؤذي|تقتل)",
        ]

        # Dangerous agricultural advice (specific to SAHOOL)
        self.dangerous_agricultural_patterns = [
            r"(mix|combine|use) (bleach|ammonia|gasoline) (with|as) (fertilizer|pesticide)",
            r"(exceed|use more than|increase) (recommended|safe) (dose|amount|concentration)",
            r"skip (safety|protective) (equipment|gear|measures)",
        ]

        # Compile patterns
        self.harmful_regex = re.compile("|".join(self.harmful_patterns), re.IGNORECASE)
        self.dangerous_ag_regex = re.compile(
            "|".join(self.dangerous_agricultural_patterns), re.IGNORECASE
        )

    def check_safety(self, text: str) -> tuple[bool, list[str]]:
        """
        Check if output is safe.

        Args:
            text: Output text

        Returns:
            Tuple of (is_safe, list_of_safety_issues)
        """
        issues = []

        # Check for harmful instructions
        if self.harmful_regex.search(text):
            issues.append("harmful_instructions")

        # Check for dangerous agricultural advice
        if self.dangerous_ag_regex.search(text):
            issues.append("dangerous_agricultural_advice")

        # Check for excessive disclaimer language (model refusing to help)
        refusal_patterns = [
            r"i cannot (help|assist|provide)",
            r"i (must|should) not",
            r"that would be (dangerous|harmful|illegal)",
        ]
        refusal_count = sum(
            1 for pattern in refusal_patterns if re.search(pattern, text, re.IGNORECASE)
        )
        if refusal_count > 2:
            issues.append("excessive_refusals")

        is_safe = len(issues) == 0
        return is_safe, issues


# ─────────────────────────────────────────────────────────────────────────────
# Citation Checker
# ─────────────────────────────────────────────────────────────────────────────


class CitationChecker:
    """
    Checks if output includes proper citations/sources.

    Encourages grounded, verifiable responses.
    """

    def __init__(self):
        # Citation patterns
        self.citation_patterns = [
            r"\[(\d+)\]",  # [1], [2], etc.
            r"\(Source:.*?\)",  # (Source: ...)
            r"According to (.*?),",  # According to X,
            r"Reference:.*",  # Reference: ...
            r"المصدر:",  # Arabic: Source
        ]

        self.citation_regex = re.compile("|".join(self.citation_patterns), re.IGNORECASE)

    def has_citations(self, text: str) -> bool:
        """Check if text has citations"""
        return bool(self.citation_regex.search(text))

    def count_citations(self, text: str) -> int:
        """Count number of citations"""
        return len(self.citation_regex.findall(text))

    def add_citation_reminder(self, text: str, language: str = "en") -> str:
        """Add reminder to include sources"""
        if language == "ar":
            reminder = "\n\nملاحظة: يُرجى الرجوع إلى مصادر موثوقة للتحقق."
        else:
            reminder = "\n\nNote: Please refer to authoritative sources for verification."

        return text + reminder


# ─────────────────────────────────────────────────────────────────────────────
# PII Leakage Detector
# ─────────────────────────────────────────────────────────────────────────────


class PIILeakageDetector:
    """
    Detects if AI output leaks PII from training data or context.

    Uses similar patterns to input PII detector but focused on leakage scenarios.
    """

    def __init__(self):
        # Import from input_filter to reuse PII patterns
        from .input_filter import PIIDetector

        self.pii_detector = PIIDetector()

        # Additional leakage patterns
        self.leakage_patterns = [
            r"(my|the) (email|phone|address) is",
            r"(contact|reach) me at",
            r"you can call me",
            # Arabic
            r"(بريدي|هاتفي|عنواني) هو",
        ]

        self.leakage_regex = re.compile("|".join(self.leakage_patterns), re.IGNORECASE)

    def detect_leakage(self, text: str) -> tuple[bool, dict[str, int]]:
        """
        Detect PII leakage in output.

        Args:
            text: Output text

        Returns:
            Tuple of (has_leakage, pii_counts_by_type)
        """
        # Check for PII patterns
        _, pii_counts = self.pii_detector.detect_and_mask(text)

        # Check for explicit leakage phrases
        has_explicit_leakage = bool(self.leakage_regex.search(text))

        has_leakage = bool(pii_counts) or has_explicit_leakage

        if has_explicit_leakage and "explicit_leakage" not in pii_counts:
            pii_counts["explicit_leakage"] = 1

        return has_leakage, pii_counts


# ─────────────────────────────────────────────────────────────────────────────
# Main Output Filter
# ─────────────────────────────────────────────────────────────────────────────


class OutputFilter:
    """
    Main output filter coordinating all safety checks.

    Usage:
        filter = OutputFilter()
        result = filter.filter_output(
            text="AI-generated response",
            trust_level=TrustLevel.BASIC
        )
        if not result.is_safe:
            # Handle unsafe output
    """

    def __init__(self, policy_manager: PolicyManager | None = None):
        self.policy_manager = policy_manager or PolicyManager()
        self.hallucination_detector = HallucinationDetector()
        self.safety_checker = SafetyContentChecker()
        self.citation_checker = CitationChecker()
        self.pii_leakage_detector = PIILeakageDetector()

    def filter_output(
        self,
        text: str,
        trust_level: TrustLevel = TrustLevel.BASIC,
        language: str = "en",
        mask_pii: bool = True,
    ) -> OutputFilterResult:
        """
        Comprehensive output filtering.

        Args:
            text: Output text to filter
            trust_level: User's trust level
            language: Output language ('en' or 'ar')
            mask_pii: Whether to mask PII leakage

        Returns:
            OutputFilterResult with safety assessment
        """
        warnings = []
        metadata = {}
        filtered_output = text

        # Get policy for trust level
        policy = self.policy_manager.get_output_policy(trust_level)

        # 1. Check for PII leakage
        if policy.check_pii_leakage:
            has_leakage, pii_counts = self.pii_leakage_detector.detect_leakage(text)
            if has_leakage:
                warnings.append(f"PII leakage detected: {pii_counts}")
                metadata["pii_leakage"] = pii_counts

                if mask_pii:
                    from .input_filter import PIIDetector

                    pii_detector = PIIDetector()
                    filtered_output, _ = pii_detector.detect_and_mask(filtered_output)
                    warnings.append("PII masked in output")

        # 2. Check for hallucination markers
        has_hallucination_markers = False
        confidence_score = 1.0
        if policy.check_hallucinations:
            has_markers, markers, confidence = self.hallucination_detector.detect(text)
            if has_markers:
                has_hallucination_markers = True
                confidence_score = confidence
                warnings.append(f"Hallucination markers detected: {markers}")
                metadata["hallucination_markers"] = markers
                metadata["confidence_score"] = confidence_score

        # 3. Check safety
        if policy.check_safety:
            is_safe_content, safety_issues = self.safety_checker.check_safety(text)
            if not is_safe_content:
                warnings.append(f"Safety issues detected: {safety_issues}")
                metadata["safety_issues"] = safety_issues

        # 4. Check citations
        has_citations = self.citation_checker.has_citations(text)
        citation_count = self.citation_checker.count_citations(text)
        metadata["citation_count"] = citation_count

        requires_citation = policy.require_citations and not has_citations
        if requires_citation:
            warnings.append("Output lacks required citations")
            filtered_output = self.citation_checker.add_citation_reminder(filtered_output, language)

        # 5. Add disclaimer if needed
        if policy.add_disclaimer:
            filtered_output = self.hallucination_detector.add_disclaimer(filtered_output, language)
            metadata["disclaimer_added"] = True

        # Determine overall safety
        is_safe = not metadata.get("safety_issues") and confidence_score > 0.5

        safety_level = (
            ContentSafetyLevel.HIGH_RISK
            if metadata.get("safety_issues")
            else (
                ContentSafetyLevel.MEDIUM_RISK
                if has_hallucination_markers or metadata.get("pii_leakage")
                else ContentSafetyLevel.SAFE
            )
        )

        return OutputFilterResult(
            is_safe=is_safe,
            filtered_output=filtered_output,
            safety_level=safety_level,
            warnings=warnings,
            metadata=metadata,
            has_pii_leakage=bool(metadata.get("pii_leakage")),
            has_hallucination_markers=has_hallucination_markers,
            requires_citation=requires_citation,
        )

    def post_process(
        self,
        text: str,
        add_context: bool = True,
        language: str = "en",
    ) -> str:
        """
        Post-process output with context-specific formatting.

        Args:
            text: Output text
            add_context: Whether to add SAHOOL context
            language: Output language

        Returns:
            Post-processed text
        """
        processed = text

        # Add SAHOOL context for agricultural advice
        if add_context:
            if language == "ar":
                context = (
                    "\n\nسهول - منصة الزراعة الذكية"
                    "\nللمزيد من المعلومات، تواصل مع مهندس زراعي معتمد."
                )
            else:
                context = (
                    "\n\nSAHOOL - Smart Agriculture Platform"
                    "\nFor more information, consult a certified agricultural engineer."
                )
            processed = processed + context

        return processed


# ─────────────────────────────────────────────────────────────────────────────
# Utility Functions
# ─────────────────────────────────────────────────────────────────────────────


def sanitize_output(text: str) -> str:
    """
    Basic output sanitization.

    Args:
        text: Output text

    Returns:
        Sanitized text
    """
    # Remove any embedded scripts (defensive)
    text = re.sub(r"<script.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL)

    # Remove null bytes
    text = text.replace("\x00", "")

    # Normalize whitespace (but preserve paragraph breaks)
    lines = text.split("\n")
    lines = [" ".join(line.split()) for line in lines]
    text = "\n".join(lines)

    return text.strip()


def truncate_output(text: str, max_length: int = 4000) -> str:
    """
    Truncate output to maximum length.

    Args:
        text: Output text
        max_length: Maximum characters

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    # Truncate and add ellipsis
    return text[: max_length - 3] + "..."


# Global output filter instance
output_filter = OutputFilter()
