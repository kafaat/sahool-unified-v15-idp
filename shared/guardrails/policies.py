"""
AI Safety Guardrails - Policy Definitions
=========================================
Defines security policies, allowed topics, and trust levels for SAHOOL AI system.
Based on Google's Secure AI Agents framework.

Author: SAHOOL Platform Team
Updated: December 2025
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


# ─────────────────────────────────────────────────────────────────────────────
# Trust Levels & User Tiers
# ─────────────────────────────────────────────────────────────────────────────


class TrustLevel(str, Enum):
    """User trust level determines guardrail strictness"""

    BLOCKED = "blocked"  # Blocked user - reject all requests
    UNTRUSTED = "untrusted"  # New/unverified users - strictest guardrails
    BASIC = "basic"  # Verified users - standard guardrails
    TRUSTED = "trusted"  # Established users - relaxed guardrails
    PREMIUM = "premium"  # Premium subscribers - minimal guardrails
    ADMIN = "admin"  # System administrators - bypass most guardrails


class ContentSafetyLevel(str, Enum):
    """Content safety classification levels"""

    SAFE = "safe"  # Content is safe
    LOW_RISK = "low_risk"  # Minor concerns, allow with logging
    MEDIUM_RISK = "medium_risk"  # Moderate concerns, filter/redact
    HIGH_RISK = "high_risk"  # High risk, block with warning
    CRITICAL = "critical"  # Critical risk, block and alert admins


# ─────────────────────────────────────────────────────────────────────────────
# Topic Policies
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class TopicPolicy:
    """
    Defines allowed and blocked topics for SAHOOL agricultural platform.

    SAHOOL focuses on agriculture, weather, and crop management.
    """

    # Allowed topics - SAHOOL's core domains
    allowed_topics: Set[str] = field(
        default_factory=lambda: {
            # Agriculture & Farming
            "agriculture",
            "farming",
            "زراعة",
            "فلاحة",
            "crops",
            "محاصيل",
            "زرع",
            "irrigation",
            "ري",
            "سقي",
            "fertilizer",
            "سماد",
            "تسميد",
            "pesticides",
            "مبيدات",
            "harvest",
            "حصاد",
            "جني",
            "planting",
            "زراعة",
            "بذر",
            "soil",
            "تربة",
            # Weather & Climate
            "weather",
            "طقس",
            "جو",
            "climate",
            "مناخ",
            "temperature",
            "حرارة",
            "درجة حرارة",
            "rainfall",
            "أمطار",
            "مطر",
            "humidity",
            "رطوبة",
            "drought",
            "جفاف",
            "season",
            "موسم",
            "فصل",
            # Crops & Plants
            "wheat",
            "قمح",
            "corn",
            "ذرة",
            "rice",
            "أرز",
            "barley",
            "شعير",
            "vegetables",
            "خضروات",
            "fruits",
            "فواكه",
            "dates",
            "تمر",
            "نخيل",
            "olives",
            "زيتون",
            # Livestock & Animals
            "livestock",
            "ماشية",
            "مواشي",
            "cattle",
            "أبقار",
            "بقر",
            "sheep",
            "أغنام",
            "خراف",
            "goats",
            "ماعز",
            "poultry",
            "دواجن",
            "chickens",
            "دجاج",
            # Technology & Equipment
            "tractor",
            "جرار",
            "تراكتور",
            "equipment",
            "معدات",
            "machinery",
            "آلات",
            "sensors",
            "مستشعرات",
            "حساسات",
            "iot",
            "إنترنت الأشياء",
            "precision agriculture",
            "زراعة دقيقة",
            "smart farming",
            "زراعة ذكية",
            # Business & Economics
            "market",
            "سوق",
            "price",
            "سعر",
            "subsidy",
            "دعم",
            "loan",
            "قرض",
            "insurance",
            "تأمين",
            "cooperative",
            "تعاونية",
            # General agricultural knowledge
            "agronomy",
            "علم المحاصيل",
            "horticulture",
            "بستنة",
            "organic farming",
            "زراعة عضوية",
            "sustainable agriculture",
            "زراعة مستدامة",
        }
    )

    # Blocked topics - out of scope or dangerous
    blocked_topics: Set[str] = field(
        default_factory=lambda: {
            # Illegal content
            "terrorism",
            "إرهاب",
            "weapons",
            "أسلحة",
            "drugs",
            "مخدرات",
            "violence",
            "عنف",
            "illegal",
            "غير قانوني",
            # Harmful content
            "self-harm",
            "إيذاء النفس",
            "suicide",
            "انتحار",
            "hate speech",
            "خطاب الكراهية",
            "discrimination",
            "تمييز",
            # Misinformation vectors
            "medical advice",
            "نصائح طبية",
            "legal advice",
            "نصائح قانونية",
            "financial advice",
            "نصائح مالية",
            # Off-topic domains
            "politics",
            "سياسة",
            "religion",
            "دين",
            "gambling",
            "مقامرة",
            "adult content",
            "محتوى للبالغين",
        }
    )

    # Sensitive topics - allow but log and monitor
    sensitive_topics: Set[str] = field(
        default_factory=lambda: {
            "pesticide toxicity",
            "سمية المبيدات",
            "chemical safety",
            "السلامة الكيميائية",
            "water scarcity",
            "ندرة المياه",
            "land disputes",
            "نزاعات الأراضي",
            "debt",
            "ديون",
            "bankruptcy",
            "إفلاس",
        }
    )

    def is_allowed(self, text: str) -> bool:
        """Check if text contains allowed topics"""
        text_lower = text.lower()
        return any(topic.lower() in text_lower for topic in self.allowed_topics)

    def is_blocked(self, text: str) -> bool:
        """Check if text contains blocked topics"""
        text_lower = text.lower()
        return any(topic.lower() in text_lower for topic in self.blocked_topics)

    def is_sensitive(self, text: str) -> bool:
        """Check if text contains sensitive topics"""
        text_lower = text.lower()
        return any(topic.lower() in text_lower for topic in self.sensitive_topics)


# ─────────────────────────────────────────────────────────────────────────────
# Rate Limiting Policies
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class RateLimitPolicy:
    """Rate limiting configuration per trust level"""

    # Requests per minute
    requests_per_minute: int

    # Tokens per minute (for LLM calls)
    tokens_per_minute: int

    # Maximum tokens per request
    max_tokens_per_request: int

    # Maximum requests per day
    requests_per_day: int

    # Burst allowance (temporary spike)
    burst_allowance: int = 0


# Default rate limits per trust level
RATE_LIMIT_POLICIES: Dict[TrustLevel, RateLimitPolicy] = {
    TrustLevel.BLOCKED: RateLimitPolicy(
        requests_per_minute=0,
        tokens_per_minute=0,
        max_tokens_per_request=0,
        requests_per_day=0,
        burst_allowance=0,
    ),
    TrustLevel.UNTRUSTED: RateLimitPolicy(
        requests_per_minute=5,
        tokens_per_minute=1000,
        max_tokens_per_request=500,
        requests_per_day=100,
        burst_allowance=2,
    ),
    TrustLevel.BASIC: RateLimitPolicy(
        requests_per_minute=20,
        tokens_per_minute=5000,
        max_tokens_per_request=2000,
        requests_per_day=500,
        burst_allowance=10,
    ),
    TrustLevel.TRUSTED: RateLimitPolicy(
        requests_per_minute=60,
        tokens_per_minute=15000,
        max_tokens_per_request=4000,
        requests_per_day=2000,
        burst_allowance=30,
    ),
    TrustLevel.PREMIUM: RateLimitPolicy(
        requests_per_minute=120,
        tokens_per_minute=30000,
        max_tokens_per_request=8000,
        requests_per_day=5000,
        burst_allowance=60,
    ),
    TrustLevel.ADMIN: RateLimitPolicy(
        requests_per_minute=300,
        tokens_per_minute=100000,
        max_tokens_per_request=16000,
        requests_per_day=50000,
        burst_allowance=150,
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# Input Validation Policies
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class InputValidationPolicy:
    """Input validation rules per trust level"""

    # Maximum input length (characters)
    max_input_length: int

    # Enable prompt injection detection
    check_prompt_injection: bool

    # Enable PII detection
    check_pii: bool

    # Enable toxic content filtering
    check_toxicity: bool

    # Require topic relevance check
    require_topic_relevance: bool

    # Toxicity threshold (0-1, higher = more strict)
    toxicity_threshold: float = 0.7


# Input validation policies per trust level
INPUT_VALIDATION_POLICIES: Dict[TrustLevel, InputValidationPolicy] = {
    TrustLevel.BLOCKED: InputValidationPolicy(
        max_input_length=0,
        check_prompt_injection=True,
        check_pii=True,
        check_toxicity=True,
        require_topic_relevance=True,
        toxicity_threshold=0.0,
    ),
    TrustLevel.UNTRUSTED: InputValidationPolicy(
        max_input_length=2000,
        check_prompt_injection=True,
        check_pii=True,
        check_toxicity=True,
        require_topic_relevance=True,
        toxicity_threshold=0.5,
    ),
    TrustLevel.BASIC: InputValidationPolicy(
        max_input_length=5000,
        check_prompt_injection=True,
        check_pii=True,
        check_toxicity=True,
        require_topic_relevance=True,
        toxicity_threshold=0.6,
    ),
    TrustLevel.TRUSTED: InputValidationPolicy(
        max_input_length=10000,
        check_prompt_injection=True,
        check_pii=True,
        check_toxicity=True,
        require_topic_relevance=False,
        toxicity_threshold=0.7,
    ),
    TrustLevel.PREMIUM: InputValidationPolicy(
        max_input_length=20000,
        check_prompt_injection=True,
        check_pii=True,
        check_toxicity=False,
        require_topic_relevance=False,
        toxicity_threshold=0.8,
    ),
    TrustLevel.ADMIN: InputValidationPolicy(
        max_input_length=50000,
        check_prompt_injection=False,
        check_pii=False,
        check_toxicity=False,
        require_topic_relevance=False,
        toxicity_threshold=1.0,
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# Output Validation Policies
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class OutputValidationPolicy:
    """Output validation rules per trust level"""

    # Check for PII in outputs
    check_pii_leakage: bool

    # Check for hallucination markers
    check_hallucinations: bool

    # Check safety/toxicity in outputs
    check_safety: bool

    # Require source citations
    require_citations: bool

    # Add hallucination disclaimer
    add_disclaimer: bool


# Output validation policies per trust level
OUTPUT_VALIDATION_POLICIES: Dict[TrustLevel, OutputValidationPolicy] = {
    TrustLevel.BLOCKED: OutputValidationPolicy(
        check_pii_leakage=True,
        check_hallucinations=True,
        check_safety=True,
        require_citations=True,
        add_disclaimer=True,
    ),
    TrustLevel.UNTRUSTED: OutputValidationPolicy(
        check_pii_leakage=True,
        check_hallucinations=True,
        check_safety=True,
        require_citations=True,
        add_disclaimer=True,
    ),
    TrustLevel.BASIC: OutputValidationPolicy(
        check_pii_leakage=True,
        check_hallucinations=True,
        check_safety=True,
        require_citations=False,
        add_disclaimer=True,
    ),
    TrustLevel.TRUSTED: OutputValidationPolicy(
        check_pii_leakage=True,
        check_hallucinations=True,
        check_safety=True,
        require_citations=False,
        add_disclaimer=False,
    ),
    TrustLevel.PREMIUM: OutputValidationPolicy(
        check_pii_leakage=True,
        check_hallucinations=False,
        check_safety=False,
        require_citations=False,
        add_disclaimer=False,
    ),
    TrustLevel.ADMIN: OutputValidationPolicy(
        check_pii_leakage=False,
        check_hallucinations=False,
        check_safety=False,
        require_citations=False,
        add_disclaimer=False,
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# Policy Manager
# ─────────────────────────────────────────────────────────────────────────────


class PolicyManager:
    """
    Central policy management for AI Safety Guardrails.

    Usage:
        policy_mgr = PolicyManager()
        trust_level = policy_mgr.get_user_trust_level(user_id)
        input_policy = policy_mgr.get_input_policy(trust_level)
    """

    def __init__(self):
        self.topic_policy = TopicPolicy()
        self._user_trust_cache: Dict[str, TrustLevel] = {}

    def get_user_trust_level(
        self,
        user_id: Optional[str] = None,
        roles: Optional[List[str]] = None,
        is_premium: bool = False,
        is_verified: bool = False,
        account_age_days: int = 0,
    ) -> TrustLevel:
        """
        Determine user trust level based on multiple factors.

        Args:
            user_id: User identifier
            roles: User roles
            is_premium: Premium subscriber flag
            is_verified: Account verified flag
            account_age_days: Age of account in days

        Returns:
            TrustLevel for the user
        """
        # Check cache
        if user_id and user_id in self._user_trust_cache:
            return self._user_trust_cache[user_id]

        # Determine trust level
        roles = roles or []

        # Admin users
        if "admin" in roles or "super_admin" in roles:
            trust_level = TrustLevel.ADMIN

        # Premium users
        elif is_premium:
            trust_level = TrustLevel.PREMIUM

        # Trusted users (verified + old account)
        elif is_verified and account_age_days > 90:
            trust_level = TrustLevel.TRUSTED

        # Basic users (verified or old account)
        elif is_verified or account_age_days > 30:
            trust_level = TrustLevel.BASIC

        # New/unverified users
        else:
            trust_level = TrustLevel.UNTRUSTED

        # Cache result
        if user_id:
            self._user_trust_cache[user_id] = trust_level

        return trust_level

    def get_input_policy(self, trust_level: TrustLevel) -> InputValidationPolicy:
        """Get input validation policy for trust level"""
        return INPUT_VALIDATION_POLICIES[trust_level]

    def get_output_policy(self, trust_level: TrustLevel) -> OutputValidationPolicy:
        """Get output validation policy for trust level"""
        return OUTPUT_VALIDATION_POLICIES[trust_level]

    def get_rate_limit_policy(self, trust_level: TrustLevel) -> RateLimitPolicy:
        """Get rate limiting policy for trust level"""
        return RATE_LIMIT_POLICIES[trust_level]

    def is_topic_allowed(self, text: str, strict: bool = False) -> bool:
        """
        Check if topic is allowed.

        Args:
            text: Input text to check
            strict: If True, require explicit topic match

        Returns:
            True if allowed, False otherwise
        """
        # Always block dangerous topics
        if self.topic_policy.is_blocked(text):
            return False

        # In strict mode, require explicit topic match
        if strict:
            return self.topic_policy.is_allowed(text)

        # In permissive mode, allow unless blocked
        return True

    def get_content_safety_level(
        self,
        has_blocked_topic: bool = False,
        has_sensitive_topic: bool = False,
        has_pii: bool = False,
        toxicity_score: float = 0.0,
        has_prompt_injection: bool = False,
    ) -> ContentSafetyLevel:
        """
        Determine overall content safety level.

        Args:
            has_blocked_topic: Contains blocked topic
            has_sensitive_topic: Contains sensitive topic
            has_pii: Contains PII
            toxicity_score: Toxicity score (0-1)
            has_prompt_injection: Contains prompt injection

        Returns:
            ContentSafetyLevel
        """
        # Critical - immediate block
        if has_blocked_topic or has_prompt_injection:
            return ContentSafetyLevel.CRITICAL

        # High risk - block with warning
        if toxicity_score > 0.8:
            return ContentSafetyLevel.HIGH_RISK

        # Medium risk - filter/redact
        if has_pii or toxicity_score > 0.6 or has_sensitive_topic:
            return ContentSafetyLevel.MEDIUM_RISK

        # Low risk - allow with logging
        if toxicity_score > 0.3:
            return ContentSafetyLevel.LOW_RISK

        # Safe
        return ContentSafetyLevel.SAFE


# Global policy manager instance
policy_manager = PolicyManager()
