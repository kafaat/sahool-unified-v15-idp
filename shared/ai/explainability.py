"""
Explainability Layer Module
===========================
طبقة التفسير - شرح سبب التوصيات

Provides explanations for AI recommendations answering:
- "Why this recommendation?" (لماذا هذه التوصية؟)
- What factors contributed to the decision
- Confidence levels and supporting evidence
- Alternative recommendations that were considered

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from datetime import datetime
import json


class ExplanationType(str, Enum):
    """Types of explanations | أنواع التفسيرات"""
    FACTOR_BASED = "factor_based"  # Based on input factors
    RULE_BASED = "rule_based"  # Based on agronomic rules
    DATA_DRIVEN = "data_driven"  # Based on historical data
    COMPARATIVE = "comparative"  # Compared to alternatives
    CONFIDENCE_BASED = "confidence_based"  # Based on model confidence


class FactorType(str, Enum):
    """Types of contributing factors | أنواع العوامل المساهمة"""
    WEATHER = "weather"  # الطقس
    SOIL = "soil"  # التربة
    CROP_STAGE = "crop_stage"  # مرحلة المحصول
    HISTORICAL = "historical"  # البيانات التاريخية
    SENSOR = "sensor"  # بيانات الحساسات
    MARKET = "market"  # السوق
    RESOURCE = "resource"  # الموارد
    CALENDAR = "calendar"  # التقويم الزراعي
    USER_PREFERENCE = "user_preference"  # تفضيلات المستخدم


class ImpactLevel(str, Enum):
    """Impact level of a factor | مستوى تأثير العامل"""
    CRITICAL = "critical"  # حرج - must have
    HIGH = "high"  # عالي - strongly influences
    MEDIUM = "medium"  # متوسط - moderately influences
    LOW = "low"  # منخفض - slightly influences


@dataclass
class ContributingFactor:
    """A factor that contributed to a recommendation | عامل مساهم في التوصية"""

    # Factor identification
    factor_type: FactorType
    name: str
    name_ar: str

    # Factor details
    value: Any
    description: str
    description_ar: str

    # Impact assessment
    impact: ImpactLevel
    weight: float  # 0.0 to 1.0
    direction: str  # "supports", "opposes", "neutral"

    # Evidence
    evidence: str | None = None
    evidence_ar: str | None = None
    source: str | None = None
    confidence: float = 0.8

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "factor_type": self.factor_type.value,
            "name": self.name,
            "name_ar": self.name_ar,
            "value": self.value,
            "description": self.description,
            "description_ar": self.description_ar,
            "impact": self.impact.value,
            "weight": self.weight,
            "direction": self.direction,
            "evidence": self.evidence,
            "evidence_ar": self.evidence_ar,
            "source": self.source,
            "confidence": self.confidence,
        }


@dataclass
class AlternativeRecommendation:
    """An alternative recommendation that was considered | توصية بديلة تم النظر فيها"""

    # Recommendation details
    title: str
    title_ar: str
    description: str
    description_ar: str

    # Comparison
    score: float  # Relative score (0-100)
    rank: int  # Ranking position

    # Why not selected
    rejection_reasons: list[str] = field(default_factory=list)
    rejection_reasons_ar: list[str] = field(default_factory=list)

    # Trade-offs
    pros: list[str] = field(default_factory=list)
    cons: list[str] = field(default_factory=list)
    pros_ar: list[str] = field(default_factory=list)
    cons_ar: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "title": self.title,
            "title_ar": self.title_ar,
            "description": self.description,
            "description_ar": self.description_ar,
            "score": self.score,
            "rank": self.rank,
            "rejection_reasons": self.rejection_reasons,
            "rejection_reasons_ar": self.rejection_reasons_ar,
            "pros": self.pros,
            "cons": self.cons,
            "pros_ar": self.pros_ar,
            "cons_ar": self.cons_ar,
        }


@dataclass
class RuleExplanation:
    """Explanation based on agronomic rules | تفسير مبني على القواعد الزراعية"""

    # Rule identification
    rule_id: str
    rule_name: str
    rule_name_ar: str

    # Rule details
    condition: str
    condition_ar: str
    action: str
    action_ar: str

    # Application context
    matched: bool
    match_details: str
    match_details_ar: str

    # Source
    source: str = "SAHOOL Agronomic Rules"
    category: str = "general"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "rule_name_ar": self.rule_name_ar,
            "condition": self.condition,
            "condition_ar": self.condition_ar,
            "action": self.action,
            "action_ar": self.action_ar,
            "matched": self.matched,
            "match_details": self.match_details,
            "match_details_ar": self.match_details_ar,
            "source": self.source,
            "category": self.category,
        }


@dataclass
class Explanation:
    """
    Complete explanation for a recommendation
    التفسير الكامل للتوصية

    Answers the question: "Why this recommendation?"
    يجيب على السؤال: "لماذا هذه التوصية؟"
    """

    # Identification
    recommendation_id: str
    explanation_type: ExplanationType
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Summary explanation (human-readable)
    summary: str = ""
    summary_ar: str = ""

    # Detailed explanation
    detailed_explanation: str = ""
    detailed_explanation_ar: str = ""

    # Contributing factors
    factors: list[ContributingFactor] = field(default_factory=list)

    # Rules that applied
    rules: list[RuleExplanation] = field(default_factory=list)

    # Alternatives considered
    alternatives: list[AlternativeRecommendation] = field(default_factory=list)

    # Confidence and uncertainty
    overall_confidence: float = 0.8
    uncertainty_reasons: list[str] = field(default_factory=list)
    uncertainty_reasons_ar: list[str] = field(default_factory=list)

    # Data sources used
    data_sources: list[str] = field(default_factory=list)

    # Additional context
    context: dict[str, Any] = field(default_factory=dict)

    @property
    def primary_factors(self) -> list[ContributingFactor]:
        """Get factors with HIGH or CRITICAL impact"""
        return [
            f for f in self.factors
            if f.impact in [ImpactLevel.CRITICAL, ImpactLevel.HIGH]
        ]

    @property
    def factor_summary(self) -> str:
        """Generate a brief summary of key factors"""
        key_factors = self.primary_factors[:3]
        if not key_factors:
            return "No specific factors identified"

        factor_names = [f.name for f in key_factors]
        return f"Based on: {', '.join(factor_names)}"

    @property
    def factor_summary_ar(self) -> str:
        """Generate Arabic summary of key factors"""
        key_factors = self.primary_factors[:3]
        if not key_factors:
            return "لم يتم تحديد عوامل محددة"

        factor_names = [f.name_ar for f in key_factors]
        return f"بناءً على: {', '.join(factor_names)}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "recommendation_id": self.recommendation_id,
            "explanation_type": self.explanation_type.value,
            "created_at": self.created_at.isoformat(),
            "summary": self.summary,
            "summary_ar": self.summary_ar,
            "detailed_explanation": self.detailed_explanation,
            "detailed_explanation_ar": self.detailed_explanation_ar,
            "factors": [f.to_dict() for f in self.factors],
            "rules": [r.to_dict() for r in self.rules],
            "alternatives": [a.to_dict() for a in self.alternatives],
            "overall_confidence": self.overall_confidence,
            "uncertainty_reasons": self.uncertainty_reasons,
            "uncertainty_reasons_ar": self.uncertainty_reasons_ar,
            "data_sources": self.data_sources,
            "context": self.context,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


class ExplainabilityEngine:
    """
    Engine for generating explanations for AI recommendations
    محرك لتوليد تفسيرات توصيات الذكاء الاصطناعي

    Features:
    - Factor-based explanations
    - Rule-based explanations
    - Comparative explanations
    - Confidence analysis
    - Bilingual support (Arabic/English)

    Usage:
        engine = ExplainabilityEngine()

        # Generate explanation
        explanation = engine.explain(
            recommendation_id="rec_001",
            recommendation_type="irrigation",
            factors=factors,
            rules_applied=rules,
            alternatives_considered=alternatives,
        )

        # Get human-readable summary
        print(explanation.summary)
        print(explanation.summary_ar)
    """

    # Common factor templates
    FACTOR_TEMPLATES = {
        FactorType.WEATHER: {
            "en": "Weather conditions ({value}) {direction} this recommendation",
            "ar": "الظروف الجوية ({value}) {direction_ar} هذه التوصية",
        },
        FactorType.SOIL: {
            "en": "Soil {name} ({value}) indicates {description}",
            "ar": "التربة {name_ar} ({value}) تشير إلى {description_ar}",
        },
        FactorType.CROP_STAGE: {
            "en": "Current growth stage ({value}) requires {description}",
            "ar": "مرحلة النمو الحالية ({value}) تتطلب {description_ar}",
        },
        FactorType.SENSOR: {
            "en": "Sensor data shows {name}: {value}",
            "ar": "بيانات الحساسات تظهر {name_ar}: {value}",
        },
        FactorType.HISTORICAL: {
            "en": "Historical data shows {description}",
            "ar": "البيانات التاريخية تظهر {description_ar}",
        },
    }

    # Direction translations
    DIRECTION_AR = {
        "supports": "تدعم",
        "opposes": "تعارض",
        "neutral": "محايدة تجاه",
    }

    def __init__(self, language: str = "both"):
        """
        Initialize the explainability engine

        Args:
            language: Output language ("en", "ar", or "both")
        """
        self.language = language

    def explain(
        self,
        recommendation_id: str,
        recommendation_type: str,
        recommendation_text: str = "",
        recommendation_text_ar: str = "",
        factors: list[ContributingFactor] | None = None,
        rules_applied: list[RuleExplanation] | None = None,
        alternatives_considered: list[AlternativeRecommendation] | None = None,
        confidence: float = 0.8,
        context: dict[str, Any] | None = None,
    ) -> Explanation:
        """
        Generate a complete explanation for a recommendation

        Args:
            recommendation_id: Unique ID of the recommendation
            recommendation_type: Type (irrigation, fertilizer, pest, etc.)
            recommendation_text: The recommendation text (English)
            recommendation_text_ar: The recommendation text (Arabic)
            factors: Contributing factors
            rules_applied: Agronomic rules that were applied
            alternatives_considered: Other options that were considered
            confidence: Overall confidence level (0-1)
            context: Additional context information

        Returns:
            Explanation object with complete explanation
        """
        factors = factors or []
        rules_applied = rules_applied or []
        alternatives_considered = alternatives_considered or []
        context = context or {}

        # Determine explanation type
        explanation_type = self._determine_type(factors, rules_applied)

        # Generate summary
        summary, summary_ar = self._generate_summary(
            recommendation_type=recommendation_type,
            factors=factors,
            rules=rules_applied,
            confidence=confidence,
        )

        # Generate detailed explanation
        detailed, detailed_ar = self._generate_detailed(
            recommendation_type=recommendation_type,
            factors=factors,
            rules=rules_applied,
            alternatives=alternatives_considered,
        )

        # Identify uncertainty reasons
        uncertainty_reasons, uncertainty_reasons_ar = self._identify_uncertainties(
            factors=factors,
            confidence=confidence,
        )

        # Collect data sources
        data_sources = self._collect_data_sources(factors, rules_applied)

        return Explanation(
            recommendation_id=recommendation_id,
            explanation_type=explanation_type,
            summary=summary,
            summary_ar=summary_ar,
            detailed_explanation=detailed,
            detailed_explanation_ar=detailed_ar,
            factors=factors,
            rules=rules_applied,
            alternatives=alternatives_considered,
            overall_confidence=confidence,
            uncertainty_reasons=uncertainty_reasons,
            uncertainty_reasons_ar=uncertainty_reasons_ar,
            data_sources=data_sources,
            context=context,
        )

    def explain_irrigation(
        self,
        recommendation_id: str,
        soil_moisture: float,
        weather_forecast: dict[str, Any],
        crop_stage: str,
        et_value: float,
        recommended_amount_mm: float,
        alternatives: list[dict] | None = None,
    ) -> Explanation:
        """
        Generate explanation for irrigation recommendation
        توليد تفسير لتوصية الري

        Args:
            recommendation_id: Recommendation ID
            soil_moisture: Current soil moisture (%)
            weather_forecast: Weather forecast data
            crop_stage: Current crop growth stage
            et_value: Evapotranspiration value (mm/day)
            recommended_amount_mm: Recommended irrigation amount
            alternatives: Alternative irrigation options

        Returns:
            Explanation for the irrigation recommendation
        """
        factors = []

        # Soil moisture factor
        moisture_impact = ImpactLevel.HIGH if soil_moisture < 40 else ImpactLevel.MEDIUM
        factors.append(ContributingFactor(
            factor_type=FactorType.SOIL,
            name="Soil Moisture",
            name_ar="رطوبة التربة",
            value=f"{soil_moisture}%",
            description=f"Current soil moisture is {soil_moisture}%",
            description_ar=f"رطوبة التربة الحالية {soil_moisture}%",
            impact=moisture_impact,
            weight=0.35,
            direction="supports" if soil_moisture < 50 else "opposes",
            evidence=f"Sensor reading: {soil_moisture}%",
            evidence_ar=f"قراءة الحساس: {soil_moisture}%",
            source="IoT Sensors",
        ))

        # Weather factor
        rain_expected = weather_forecast.get("rain_probability", 0) > 50
        temp = weather_forecast.get("temperature", 25)
        factors.append(ContributingFactor(
            factor_type=FactorType.WEATHER,
            name="Weather Forecast",
            name_ar="توقعات الطقس",
            value=f"Rain: {weather_forecast.get('rain_probability', 0)}%, Temp: {temp}°C",
            description=f"{'Rain expected, irrigation may be delayed' if rain_expected else 'No rain expected, irrigation needed'}",
            description_ar=f"{'أمطار متوقعة، قد يتأخر الري' if rain_expected else 'لا أمطار متوقعة، الري مطلوب'}",
            impact=ImpactLevel.HIGH,
            weight=0.25,
            direction="opposes" if rain_expected else "supports",
            source="Weather Service",
        ))

        # Crop stage factor
        factors.append(ContributingFactor(
            factor_type=FactorType.CROP_STAGE,
            name="Crop Growth Stage",
            name_ar="مرحلة نمو المحصول",
            value=crop_stage,
            description=f"Crop is in {crop_stage} stage with specific water needs",
            description_ar=f"المحصول في مرحلة {crop_stage} مع احتياجات مائية محددة",
            impact=ImpactLevel.MEDIUM,
            weight=0.20,
            direction="supports",
            source="Field Observation",
        ))

        # ET factor
        factors.append(ContributingFactor(
            factor_type=FactorType.SENSOR,
            name="Evapotranspiration",
            name_ar="النتح والتبخر",
            value=f"{et_value} mm/day",
            description=f"ET rate indicates daily water loss of {et_value}mm",
            description_ar=f"معدل التبخر يشير إلى فقدان مائي يومي {et_value}مم",
            impact=ImpactLevel.MEDIUM,
            weight=0.20,
            direction="supports",
            source="Calculated from weather data",
        ))

        # Create alternatives
        alt_recommendations = []
        if alternatives:
            for i, alt in enumerate(alternatives):
                alt_recommendations.append(AlternativeRecommendation(
                    title=alt.get("title", f"Alternative {i+1}"),
                    title_ar=alt.get("title_ar", f"البديل {i+1}"),
                    description=alt.get("description", ""),
                    description_ar=alt.get("description_ar", ""),
                    score=alt.get("score", 50),
                    rank=i + 2,
                    rejection_reasons=alt.get("rejection_reasons", []),
                    rejection_reasons_ar=alt.get("rejection_reasons_ar", []),
                ))

        return self.explain(
            recommendation_id=recommendation_id,
            recommendation_type="irrigation",
            recommendation_text=f"Apply {recommended_amount_mm}mm of irrigation water",
            recommendation_text_ar=f"تطبيق {recommended_amount_mm}مم من مياه الري",
            factors=factors,
            alternatives_considered=alt_recommendations,
            confidence=0.85 if not rain_expected else 0.65,
            context={
                "recommended_amount_mm": recommended_amount_mm,
                "et_value": et_value,
                "rain_expected": rain_expected,
            },
        )

    def explain_fertilizer(
        self,
        recommendation_id: str,
        soil_test: dict[str, float],
        crop_type: str,
        crop_stage: str,
        target_yield: float,
        recommended_fertilizer: str,
        recommended_rate: float,
    ) -> Explanation:
        """
        Generate explanation for fertilizer recommendation
        توليد تفسير لتوصية التسميد
        """
        factors = []

        # Soil nutrient factors
        n_level = soil_test.get("nitrogen", 0)
        _p_level = soil_test.get("phosphorus", 0)  # Reserved for future P factor
        _k_level = soil_test.get("potassium", 0)  # Reserved for future K factor

        factors.append(ContributingFactor(
            factor_type=FactorType.SOIL,
            name="Soil Nitrogen",
            name_ar="نيتروجين التربة",
            value=f"{n_level} ppm",
            description=f"Nitrogen level is {'deficient' if n_level < 25 else 'adequate'}",
            description_ar=f"مستوى النيتروجين {'منخفض' if n_level < 25 else 'كافي'}",
            impact=ImpactLevel.CRITICAL if n_level < 25 else ImpactLevel.LOW,
            weight=0.40,
            direction="supports" if n_level < 25 else "neutral",
            source="Soil Test Results",
        ))

        factors.append(ContributingFactor(
            factor_type=FactorType.CROP_STAGE,
            name="Growth Stage Requirements",
            name_ar="متطلبات مرحلة النمو",
            value=crop_stage,
            description=f"{crop_type} in {crop_stage} has high nutrient demand",
            description_ar=f"{crop_type} في مرحلة {crop_stage} يحتاج تغذية عالية",
            impact=ImpactLevel.HIGH,
            weight=0.30,
            direction="supports",
            source="Crop Science Guidelines",
        ))

        # Rule for fertilizer application
        rules = [RuleExplanation(
            rule_id="FERT_001",
            rule_name="Nitrogen Application Rule",
            rule_name_ar="قاعدة تطبيق النيتروجين",
            condition="Soil N < 25 ppm AND crop in active growth",
            condition_ar="نيتروجين التربة < 25 جزء بالمليون والمحصول في نمو نشط",
            action=f"Apply {recommended_fertilizer} at {recommended_rate} kg/ha",
            action_ar=f"تطبيق {recommended_fertilizer} بمعدل {recommended_rate} كجم/هـ",
            matched=True,
            match_details=f"Soil N={n_level}ppm, Stage={crop_stage}",
            match_details_ar=f"نيتروجين التربة={n_level}، المرحلة={crop_stage}",
            category="fertilizer",
        )]

        return self.explain(
            recommendation_id=recommendation_id,
            recommendation_type="fertilizer",
            recommendation_text=f"Apply {recommended_fertilizer} at {recommended_rate} kg/ha",
            recommendation_text_ar=f"تطبيق {recommended_fertilizer} بمعدل {recommended_rate} كجم/هكتار",
            factors=factors,
            rules_applied=rules,
            confidence=0.90,
            context={
                "soil_test": soil_test,
                "crop_type": crop_type,
                "target_yield": target_yield,
            },
        )

    def _determine_type(
        self,
        factors: list[ContributingFactor],
        rules: list[RuleExplanation],
    ) -> ExplanationType:
        """Determine the primary explanation type"""
        if rules and len(rules) > len(factors):
            return ExplanationType.RULE_BASED
        elif factors:
            return ExplanationType.FACTOR_BASED
        else:
            return ExplanationType.CONFIDENCE_BASED

    def _generate_summary(
        self,
        recommendation_type: str,
        factors: list[ContributingFactor],
        rules: list[RuleExplanation],
        confidence: float,
    ) -> tuple[str, str]:
        """Generate summary explanation"""
        # Get primary factors
        primary = [f for f in factors if f.impact in [ImpactLevel.CRITICAL, ImpactLevel.HIGH]]

        if primary:
            factor_names_en = ", ".join(f.name for f in primary[:3])
            factor_names_ar = ", ".join(f.name_ar for f in primary[:3])

            summary_en = f"This {recommendation_type} recommendation is based on {factor_names_en}. "
            summary_ar = f"هذه التوصية بشأن {recommendation_type} مبنية على {factor_names_ar}. "

            if confidence >= 0.8:
                summary_en += "High confidence based on available data."
                summary_ar += "ثقة عالية بناءً على البيانات المتاحة."
            elif confidence >= 0.6:
                summary_en += "Moderate confidence; some uncertainty exists."
                summary_ar += "ثقة متوسطة؛ يوجد بعض عدم اليقين."
            else:
                summary_en += "Lower confidence; consider additional verification."
                summary_ar += "ثقة منخفضة؛ يُنصح بالتحقق الإضافي."
        else:
            summary_en = f"This {recommendation_type} recommendation is based on general guidelines."
            summary_ar = f"هذه التوصية بشأن {recommendation_type} مبنية على إرشادات عامة."

        return summary_en, summary_ar

    def _generate_detailed(
        self,
        recommendation_type: str,
        factors: list[ContributingFactor],
        rules: list[RuleExplanation],
        alternatives: list[AlternativeRecommendation],
    ) -> tuple[str, str]:
        """Generate detailed explanation"""
        detailed_en = []
        detailed_ar = []

        # Factors section
        if factors:
            detailed_en.append("## Contributing Factors\n")
            detailed_ar.append("## العوامل المساهمة\n")

            for factor in sorted(factors, key=lambda x: x.weight, reverse=True):
                detailed_en.append(
                    f"- **{factor.name}** ({factor.impact.value}): {factor.description}"
                )
                detailed_ar.append(
                    f"- **{factor.name_ar}** ({factor.impact.value}): {factor.description_ar}"
                )

        # Rules section
        if rules:
            detailed_en.append("\n## Applied Rules\n")
            detailed_ar.append("\n## القواعد المطبقة\n")

            for rule in rules:
                if rule.matched:
                    detailed_en.append(f"- **{rule.rule_name}**: {rule.action}")
                    detailed_ar.append(f"- **{rule.rule_name_ar}**: {rule.action_ar}")

        # Alternatives section
        if alternatives:
            detailed_en.append("\n## Alternatives Considered\n")
            detailed_ar.append("\n## البدائل المدروسة\n")

            for alt in alternatives:
                reasons = ", ".join(alt.rejection_reasons) if alt.rejection_reasons else "Lower score"
                reasons_ar = ", ".join(alt.rejection_reasons_ar) if alt.rejection_reasons_ar else "درجة أقل"

                detailed_en.append(f"- **{alt.title}** (Score: {alt.score}): Not selected because {reasons}")
                detailed_ar.append(f"- **{alt.title_ar}** (الدرجة: {alt.score}): لم يُختر لأن {reasons_ar}")

        return "\n".join(detailed_en), "\n".join(detailed_ar)

    def _identify_uncertainties(
        self,
        factors: list[ContributingFactor],
        confidence: float,
    ) -> tuple[list[str], list[str]]:
        """Identify reasons for uncertainty"""
        uncertainties_en = []
        uncertainties_ar = []

        # Low confidence factors
        low_confidence_factors = [f for f in factors if f.confidence < 0.7]
        if low_confidence_factors:
            for f in low_confidence_factors:
                uncertainties_en.append(f"Uncertainty in {f.name} data (confidence: {f.confidence:.0%})")
                uncertainties_ar.append(f"عدم يقين في بيانات {f.name_ar} (الثقة: {f.confidence:.0%})")

        # Missing data
        if confidence < 0.7:
            uncertainties_en.append("Limited historical data available for this scenario")
            uncertainties_ar.append("بيانات تاريخية محدودة متاحة لهذا السيناريو")

        return uncertainties_en, uncertainties_ar

    def _collect_data_sources(
        self,
        factors: list[ContributingFactor],
        rules: list[RuleExplanation],
    ) -> list[str]:
        """Collect all data sources used"""
        sources = set()

        for factor in factors:
            if factor.source:
                sources.add(factor.source)

        for rule in rules:
            sources.add(rule.source)

        return list(sources)

    def format_for_display(
        self,
        explanation: Explanation,
        language: str = "both",
        format: str = "markdown",
    ) -> str:
        """
        Format explanation for display
        تنسيق التفسير للعرض

        Args:
            explanation: The explanation to format
            language: "en", "ar", or "both"
            format: "markdown", "text", or "html"

        Returns:
            Formatted explanation string
        """
        if format == "markdown":
            return self._format_markdown(explanation, language)
        elif format == "text":
            return self._format_text(explanation, language)
        else:
            return self._format_markdown(explanation, language)

    def _format_markdown(self, explanation: Explanation, language: str) -> str:
        """Format as markdown"""
        lines = []

        if language in ["en", "both"]:
            lines.append("# Why This Recommendation?\n")
            lines.append(explanation.summary)
            lines.append(f"\n**Confidence**: {explanation.overall_confidence:.0%}\n")
            lines.append(explanation.detailed_explanation)

        if language == "both":
            lines.append("\n---\n")

        if language in ["ar", "both"]:
            lines.append("# لماذا هذه التوصية؟\n")
            lines.append(explanation.summary_ar)
            lines.append(f"\n**الثقة**: {explanation.overall_confidence:.0%}\n")
            lines.append(explanation.detailed_explanation_ar)

        return "\n".join(lines)

    def _format_text(self, explanation: Explanation, language: str) -> str:
        """Format as plain text"""
        lines = []

        if language in ["en", "both"]:
            lines.append("WHY THIS RECOMMENDATION?")
            lines.append("-" * 40)
            lines.append(explanation.summary)
            lines.append(f"Confidence: {explanation.overall_confidence:.0%}")

        if language in ["ar", "both"]:
            lines.append("")
            lines.append("لماذا هذه التوصية؟")
            lines.append("-" * 40)
            lines.append(explanation.summary_ar)
            lines.append(f"الثقة: {explanation.overall_confidence:.0%}")

        return "\n".join(lines)


# Convenience functions
_default_engine: ExplainabilityEngine | None = None


def get_explainability_engine(language: str = "both") -> ExplainabilityEngine:
    """Get or create the default explainability engine"""
    global _default_engine
    if _default_engine is None:
        _default_engine = ExplainabilityEngine(language=language)
    return _default_engine


def explain_recommendation(
    recommendation_id: str,
    recommendation_type: str,
    factors: list[ContributingFactor],
    **kwargs,
) -> Explanation:
    """Generate explanation using the default engine"""
    engine = get_explainability_engine()
    return engine.explain(
        recommendation_id=recommendation_id,
        recommendation_type=recommendation_type,
        factors=factors,
        **kwargs,
    )
