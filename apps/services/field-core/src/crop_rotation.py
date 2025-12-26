"""
SAHOOL Crop Rotation Planner
مخطط تدوير المحاصيل لمنصة سهول

Helps farmers plan crop rotations for soil health and disease prevention.
يساعد المزارعين على التخطيط لتدوير المحاصيل للحفاظ على صحة التربة ومنع الأمراض.

Based on agronomic principles from OneSoil and LiteFarm.
"""

from dataclasses import dataclass, field as dataclass_field
from typing import List, Dict, Optional, Tuple
from datetime import date, datetime
from enum import Enum
import sys
from pathlib import Path

# Add shared modules to path
SHARED_PATH = Path(__file__).parent.parent.parent.parent / "shared"
if str(SHARED_PATH) not in sys.path:
    sys.path.insert(0, str(SHARED_PATH))


class CropFamily(Enum):
    """
    Crop families for rotation planning
    العائلات النباتية للتخطيط للتدوير
    """
    # Major families
    CEREALS = "cereals"           # Wheat, barley, sorghum - قمح، شعير، ذرة
    LEGUMES = "legumes"           # Faba bean, lentil, chickpea - فول، عدس، حمص
    SOLANACEAE = "solanaceae"     # Tomato, potato, pepper - طماطم، بطاطس، فلفل
    CUCURBITS = "cucurbits"       # Cucumber, melon, watermelon - خيار، شمام، بطيخ
    BRASSICAS = "brassicas"       # Cabbage, cauliflower - ملفوف، قرنبيط
    ALLIUMS = "alliums"           # Onion, garlic - بصل، ثوم
    ROOT_CROPS = "root_crops"     # Carrot, beet - جزر، شمندر
    FIBER = "fiber"               # Cotton - قطن
    OILSEEDS = "oilseeds"         # Sesame, sunflower - سمسم، عباد الشمس
    FODDER = "fodder"             # Alfalfa, clover - برسيم، نفل
    FALLOW = "fallow"             # Rest period - فترة راحة
    FRUITS = "fruits"             # Fruit trees - أشجار الفاكهة
    SPICES = "spices"             # Herbs and spices - أعشاب وتوابل
    SUGAR = "sugar"               # Sugar crops - محاصيل سكرية
    STIMULANTS = "stimulants"     # Coffee, qat - قهوة، قات


@dataclass
class RotationRule:
    """
    Rules for crop rotation by family
    قواعد تدوير المحاصيل حسب العائلة
    """
    crop_family: CropFamily
    min_years_between: int        # Minimum years before repeating
    good_predecessors: List[CropFamily]
    bad_predecessors: List[CropFamily]
    nitrogen_effect: str          # "fix", "neutral", "deplete", "heavy_deplete"
    disease_risk: Dict[str, float]  # Disease buildup risk (0-1)
    root_depth: str               # "shallow", "medium", "deep"
    nutrient_demand: str          # "light", "medium", "heavy"


@dataclass
class SeasonPlan:
    """
    Plan for a single growing season
    خطة موسم زراعي واحد
    """
    season_id: str
    year: int
    season: str                   # "winter", "summer", "spring", "autumn"
    crop_code: str
    crop_name_ar: str
    crop_name_en: str
    crop_family: CropFamily
    planting_date: Optional[date] = None
    harvest_date: Optional[date] = None
    expected_yield: Optional[float] = None
    notes: Optional[str] = None


@dataclass
class RotationPlan:
    """
    Complete rotation plan for a field
    خطة تدوير كاملة للحقل
    """
    field_id: str
    field_name: str
    created_at: date
    start_year: int
    end_year: int
    seasons: List[SeasonPlan]

    # Analysis scores
    diversity_score: float = 0.0        # 0-100
    soil_health_score: float = 0.0      # 0-100
    disease_risk_score: float = 0.0     # 0-100 (lower is better)
    nitrogen_balance: str = "neutral"   # "positive", "neutral", "negative"

    # Recommendations
    recommendations_ar: List[str] = dataclass_field(default_factory=list)
    recommendations_en: List[str] = dataclass_field(default_factory=list)

    # Warnings
    warnings_ar: List[str] = dataclass_field(default_factory=list)
    warnings_en: List[str] = dataclass_field(default_factory=list)


@dataclass
class CropSuggestion:
    """
    Crop suggestion for next season
    اقتراح محصول للموسم القادم
    """
    crop_code: str
    crop_name_ar: str
    crop_name_en: str
    crop_family: CropFamily
    suitability_score: float      # 0-100
    reasons_ar: List[str]
    reasons_en: List[str]
    warnings_ar: List[str] = dataclass_field(default_factory=list)
    warnings_en: List[str] = dataclass_field(default_factory=list)


class CropRotationPlanner:
    """
    Plan crop rotations for soil health and disease prevention
    مخطط تدوير المحاصيل لصحة التربة ومنع الأمراض
    """

    # Crop family mapping - maps crop codes to families
    CROP_FAMILY_MAP: Dict[str, CropFamily] = {
        # Cereals - الحبوب
        "WHEAT": CropFamily.CEREALS,
        "BARLEY": CropFamily.CEREALS,
        "SORGHUM": CropFamily.CEREALS,
        "MAIZE": CropFamily.CEREALS,
        "MILLET": CropFamily.CEREALS,
        "RICE": CropFamily.CEREALS,

        # Legumes - البقوليات
        "FABA_BEAN": CropFamily.LEGUMES,
        "LENTIL": CropFamily.LEGUMES,
        "CHICKPEA": CropFamily.LEGUMES,
        "COWPEA": CropFamily.LEGUMES,
        "PEANUT": CropFamily.LEGUMES,
        "ALFALFA": CropFamily.FODDER,  # Leguminous fodder
        "CLOVER": CropFamily.FODDER,

        # Solanaceae - الباذنجانيات
        "TOMATO": CropFamily.SOLANACEAE,
        "POTATO": CropFamily.SOLANACEAE,
        "PEPPER": CropFamily.SOLANACEAE,
        "EGGPLANT": CropFamily.SOLANACEAE,

        # Cucurbits - القرعيات
        "CUCUMBER": CropFamily.CUCURBITS,
        "MELON": CropFamily.CUCURBITS,
        "WATERMELON": CropFamily.CUCURBITS,
        "SQUASH": CropFamily.CUCURBITS,
        "PUMPKIN": CropFamily.CUCURBITS,

        # Brassicas - الكرنبيات
        "CABBAGE": CropFamily.BRASSICAS,
        "CAULIFLOWER": CropFamily.BRASSICAS,
        "BROCCOLI": CropFamily.BRASSICAS,

        # Alliums - الثوميات
        "ONION": CropFamily.ALLIUMS,
        "GARLIC": CropFamily.ALLIUMS,
        "LEEK": CropFamily.ALLIUMS,

        # Root crops - المحاصيل الجذرية
        "CARROT": CropFamily.ROOT_CROPS,
        "BEET": CropFamily.ROOT_CROPS,
        "RADISH": CropFamily.ROOT_CROPS,
        "TURNIP": CropFamily.ROOT_CROPS,

        # Fiber - الألياف
        "COTTON": CropFamily.FIBER,

        # Oilseeds - البذور الزيتية
        "SESAME": CropFamily.OILSEEDS,
        "SUNFLOWER": CropFamily.OILSEEDS,

        # Fruits - الفواكه
        "MANGO": CropFamily.FRUITS,
        "BANANA": CropFamily.FRUITS,
        "PAPAYA": CropFamily.FRUITS,
        "GUAVA": CropFamily.FRUITS,
        "DATE_PALM": CropFamily.FRUITS,
        "GRAPES": CropFamily.FRUITS,
        "POMEGRANATE": CropFamily.FRUITS,

        # Spices - التوابل
        "CORIANDER": CropFamily.SPICES,
        "CUMIN": CropFamily.SPICES,
        "FENUGREEK": CropFamily.SPICES,
        "BLACK_CUMIN": CropFamily.SPICES,

        # Stimulants - المنبهات
        "COFFEE": CropFamily.STIMULANTS,
        "QAT": CropFamily.STIMULANTS,

        # Sugar - السكريات
        "SUGARCANE": CropFamily.SUGAR,
    }

    # Rotation rules by crop family
    ROTATION_RULES: Dict[CropFamily, RotationRule] = {
        CropFamily.CEREALS: RotationRule(
            crop_family=CropFamily.CEREALS,
            min_years_between=1,
            good_predecessors=[CropFamily.LEGUMES, CropFamily.FODDER, CropFamily.FALLOW],
            bad_predecessors=[CropFamily.CEREALS],
            nitrogen_effect="deplete",
            disease_risk={"fusarium": 0.3, "rust": 0.2, "smut": 0.2},
            root_depth="medium",
            nutrient_demand="medium"
        ),
        CropFamily.LEGUMES: RotationRule(
            crop_family=CropFamily.LEGUMES,
            min_years_between=3,
            good_predecessors=[CropFamily.CEREALS, CropFamily.ROOT_CROPS, CropFamily.BRASSICAS],
            bad_predecessors=[CropFamily.LEGUMES, CropFamily.FODDER],
            nitrogen_effect="fix",
            disease_risk={"root_rot": 0.4, "fusarium": 0.3},
            root_depth="medium",
            nutrient_demand="light"
        ),
        CropFamily.SOLANACEAE: RotationRule(
            crop_family=CropFamily.SOLANACEAE,
            min_years_between=4,
            good_predecessors=[CropFamily.CEREALS, CropFamily.LEGUMES, CropFamily.FODDER],
            bad_predecessors=[CropFamily.SOLANACEAE, CropFamily.CUCURBITS],
            nitrogen_effect="heavy_deplete",
            disease_risk={"bacterial_wilt": 0.5, "nematodes": 0.4, "verticillium": 0.3},
            root_depth="deep",
            nutrient_demand="heavy"
        ),
        CropFamily.CUCURBITS: RotationRule(
            crop_family=CropFamily.CUCURBITS,
            min_years_between=3,
            good_predecessors=[CropFamily.LEGUMES, CropFamily.CEREALS, CropFamily.FODDER],
            bad_predecessors=[CropFamily.CUCURBITS, CropFamily.SOLANACEAE],
            nitrogen_effect="deplete",
            disease_risk={"fusarium": 0.4, "powdery_mildew": 0.3, "downy_mildew": 0.3},
            root_depth="shallow",
            nutrient_demand="heavy"
        ),
        CropFamily.BRASSICAS: RotationRule(
            crop_family=CropFamily.BRASSICAS,
            min_years_between=3,
            good_predecessors=[CropFamily.LEGUMES, CropFamily.CEREALS, CropFamily.ALLIUMS],
            bad_predecessors=[CropFamily.BRASSICAS],
            nitrogen_effect="deplete",
            disease_risk={"clubroot": 0.5, "black_rot": 0.3},
            root_depth="shallow",
            nutrient_demand="heavy"
        ),
        CropFamily.ALLIUMS: RotationRule(
            crop_family=CropFamily.ALLIUMS,
            min_years_between=4,
            good_predecessors=[CropFamily.LEGUMES, CropFamily.CEREALS, CropFamily.CUCURBITS],
            bad_predecessors=[CropFamily.ALLIUMS],
            nitrogen_effect="neutral",
            disease_risk={"white_rot": 0.6, "downy_mildew": 0.3},
            root_depth="shallow",
            nutrient_demand="medium"
        ),
        CropFamily.ROOT_CROPS: RotationRule(
            crop_family=CropFamily.ROOT_CROPS,
            min_years_between=2,
            good_predecessors=[CropFamily.LEGUMES, CropFamily.FODDER, CropFamily.ALLIUMS],
            bad_predecessors=[CropFamily.ROOT_CROPS, CropFamily.BRASSICAS],
            nitrogen_effect="neutral",
            disease_risk={"root_rot": 0.3, "nematodes": 0.2},
            root_depth="deep",
            nutrient_demand="medium"
        ),
        CropFamily.FIBER: RotationRule(
            crop_family=CropFamily.FIBER,
            min_years_between=2,
            good_predecessors=[CropFamily.LEGUMES, CropFamily.CEREALS, CropFamily.FALLOW],
            bad_predecessors=[CropFamily.FIBER, CropFamily.SOLANACEAE],
            nitrogen_effect="heavy_deplete",
            disease_risk={"fusarium": 0.3, "verticillium": 0.3, "bacterial_blight": 0.2},
            root_depth="deep",
            nutrient_demand="heavy"
        ),
        CropFamily.OILSEEDS: RotationRule(
            crop_family=CropFamily.OILSEEDS,
            min_years_between=2,
            good_predecessors=[CropFamily.CEREALS, CropFamily.LEGUMES, CropFamily.FALLOW],
            bad_predecessors=[CropFamily.OILSEEDS],
            nitrogen_effect="neutral",
            disease_risk={"fusarium": 0.2, "rust": 0.2},
            root_depth="medium",
            nutrient_demand="medium"
        ),
        CropFamily.FODDER: RotationRule(
            crop_family=CropFamily.FODDER,
            min_years_between=3,
            good_predecessors=[CropFamily.CEREALS, CropFamily.ROOT_CROPS],
            bad_predecessors=[CropFamily.LEGUMES, CropFamily.FODDER],
            nitrogen_effect="fix",
            disease_risk={"root_rot": 0.3},
            root_depth="deep",
            nutrient_demand="light"
        ),
        CropFamily.FALLOW: RotationRule(
            crop_family=CropFamily.FALLOW,
            min_years_between=5,
            good_predecessors=[CropFamily.SOLANACEAE, CropFamily.FIBER, CropFamily.CUCURBITS],
            bad_predecessors=[],
            nitrogen_effect="neutral",
            disease_risk={},
            root_depth="none",
            nutrient_demand="none"
        ),
        CropFamily.FRUITS: RotationRule(
            crop_family=CropFamily.FRUITS,
            min_years_between=20,  # Perennials
            good_predecessors=[CropFamily.LEGUMES, CropFamily.CEREALS, CropFamily.FALLOW],
            bad_predecessors=[CropFamily.FRUITS],
            nitrogen_effect="neutral",
            disease_risk={},
            root_depth="deep",
            nutrient_demand="medium"
        ),
        CropFamily.SPICES: RotationRule(
            crop_family=CropFamily.SPICES,
            min_years_between=2,
            good_predecessors=[CropFamily.CEREALS, CropFamily.LEGUMES],
            bad_predecessors=[CropFamily.SPICES, CropFamily.ALLIUMS],
            nitrogen_effect="neutral",
            disease_risk={"root_rot": 0.2},
            root_depth="shallow",
            nutrient_demand="light"
        ),
        CropFamily.SUGAR: RotationRule(
            crop_family=CropFamily.SUGAR,
            min_years_between=3,
            good_predecessors=[CropFamily.LEGUMES, CropFamily.FALLOW],
            bad_predecessors=[CropFamily.SUGAR, CropFamily.FIBER],
            nitrogen_effect="heavy_deplete",
            disease_risk={"mosaic_virus": 0.3, "red_rot": 0.2},
            root_depth="deep",
            nutrient_demand="heavy"
        ),
        CropFamily.STIMULANTS: RotationRule(
            crop_family=CropFamily.STIMULANTS,
            min_years_between=20,  # Perennials
            good_predecessors=[CropFamily.LEGUMES, CropFamily.FALLOW],
            bad_predecessors=[CropFamily.STIMULANTS],
            nitrogen_effect="neutral",
            disease_risk={},
            root_depth="deep",
            nutrient_demand="medium"
        ),
    }

    def get_crop_family(self, crop_code: str) -> CropFamily:
        """Get crop family for a crop code"""
        return self.CROP_FAMILY_MAP.get(crop_code.upper(), CropFamily.CEREALS)

    async def create_rotation_plan(
        self,
        field_id: str,
        field_name: str,
        start_year: int,
        num_years: int = 5,
        history: Optional[List[SeasonPlan]] = None,
        preferences: Optional[List[str]] = None
    ) -> RotationPlan:
        """
        Generate optimal crop rotation plan.
        إنشاء خطة تدوير محاصيل مثلى.

        Algorithm:
        1. Analyze field history (last 3-5 years)
        2. Identify disease risks from repeated crops
        3. Check nitrogen balance
        4. Suggest diverse rotation
        5. Optimize for profitability and soil health
        """
        # Initialize plan
        plan = RotationPlan(
            field_id=field_id,
            field_name=field_name,
            created_at=date.today(),
            start_year=start_year,
            end_year=start_year + num_years - 1,
            seasons=[]
        )

        # Combine history with planned seasons
        all_history = history or []

        # Simple rotation strategy: Cereals -> Legumes -> Vegetables -> Fallow
        rotation_cycle = [
            CropFamily.CEREALS,
            CropFamily.LEGUMES,
            CropFamily.SOLANACEAE,
            CropFamily.CEREALS,
            CropFamily.FALLOW
        ]

        # Generate seasons for each year
        for year_offset in range(num_years):
            year = start_year + year_offset

            # Determine next crop family based on history
            if all_history:
                last_crop_family = all_history[-1].crop_family
                suggestions = await self.suggest_next_crop(
                    field_id=field_id,
                    history=all_history,
                    season="winter"
                )
                next_family = suggestions[0].crop_family if suggestions else CropFamily.CEREALS
            else:
                next_family = rotation_cycle[year_offset % len(rotation_cycle)]

            # Create season plan
            season = SeasonPlan(
                season_id=f"{field_id}_{year}_winter",
                year=year,
                season="winter",
                crop_code=self._get_crop_for_family(next_family),
                crop_name_ar=self._get_crop_name_ar(next_family),
                crop_name_en=self._get_crop_name_en(next_family),
                crop_family=next_family,
                planting_date=date(year, 10, 1),
                harvest_date=date(year + 1, 3, 1),
            )

            plan.seasons.append(season)
            all_history.append(season)

        # Evaluate the plan
        evaluation = self.evaluate_rotation(plan.seasons)
        plan.diversity_score = evaluation["diversity_score"]
        plan.soil_health_score = evaluation["soil_health_score"]
        plan.disease_risk_score = evaluation["disease_risk_score"]
        plan.nitrogen_balance = evaluation["nitrogen_balance"]
        plan.recommendations_ar = evaluation["recommendations_ar"]
        plan.recommendations_en = evaluation["recommendations_en"]
        plan.warnings_ar = evaluation["warnings_ar"]
        plan.warnings_en = evaluation["warnings_en"]

        return plan

    async def suggest_next_crop(
        self,
        field_id: str,
        history: List[SeasonPlan],
        season: str = "winter"
    ) -> List[CropSuggestion]:
        """
        Suggest best crops for next season based on history.
        اقتراح أفضل المحاصيل للموسم القادم بناءً على السجل.

        Returns ranked list of suggestions.
        """
        suggestions = []

        # Get recent history (last 5 seasons)
        recent_history = history[-5:] if len(history) > 5 else history

        # Score each potential crop family
        for family, rule in self.ROTATION_RULES.items():
            if family == CropFamily.FALLOW:
                continue  # Handle separately

            score = 100.0
            reasons_ar = []
            reasons_en = []
            warnings_ar = []
            warnings_en = []

            # Check rotation rules
            is_valid, rule_messages = self.check_rotation_rule(family, recent_history)

            if not is_valid:
                score -= 40
                warnings_ar.extend([msg[0] for msg in rule_messages])
                warnings_en.extend([msg[1] for msg in rule_messages])
            else:
                reasons_ar.append("يتوافق مع قواعد التدوير")
                reasons_en.append("Complies with rotation rules")

            # Check predecessor compatibility
            if recent_history:
                last_family = recent_history[-1].crop_family
                if last_family in rule.good_predecessors:
                    score += 20
                    reasons_ar.append(f"سلف جيد بعد {last_family.value}")
                    reasons_en.append(f"Good successor after {last_family.value}")
                elif last_family in rule.bad_predecessors:
                    score -= 30
                    warnings_ar.append(f"سلف سيء بعد {last_family.value}")
                    warnings_en.append(f"Poor successor after {last_family.value}")

            # Nitrogen balance consideration
            nitrogen_depleted = self._check_nitrogen_depletion(recent_history)
            if nitrogen_depleted and rule.nitrogen_effect == "fix":
                score += 25
                reasons_ar.append("يثبت النيتروجين في التربة")
                reasons_en.append("Fixes nitrogen in soil")
            elif nitrogen_depleted and rule.nitrogen_effect == "heavy_deplete":
                score -= 20
                warnings_ar.append("يستنزف النيتروجين بشكل كبير")
                warnings_en.append("Heavily depletes nitrogen")

            # Disease risk consideration
            disease_risk = self._calculate_family_disease_risk(family, recent_history)
            if disease_risk > 0.5:
                score -= 30
                warnings_ar.append("خطر مرتفع لتراكم الأمراض")
                warnings_en.append("High disease accumulation risk")
            elif disease_risk < 0.2:
                score += 15
                reasons_ar.append("خطر منخفض للأمراض")
                reasons_en.append("Low disease risk")

            # Root depth alternation
            if recent_history and self._check_root_alternation(family, recent_history[-1].crop_family):
                score += 10
                reasons_ar.append("تبديل جيد لعمق الجذور")
                reasons_en.append("Good root depth alternation")

            # Create suggestion
            suggestions.append(CropSuggestion(
                crop_code=self._get_crop_for_family(family),
                crop_name_ar=self._get_crop_name_ar(family),
                crop_name_en=self._get_crop_name_en(family),
                crop_family=family,
                suitability_score=max(0, min(100, score)),
                reasons_ar=reasons_ar,
                reasons_en=reasons_en,
                warnings_ar=warnings_ar,
                warnings_en=warnings_en
            ))

        # Add fallow suggestion if intensive cultivation detected
        if self._check_intensive_cultivation(recent_history):
            suggestions.append(CropSuggestion(
                crop_code="FALLOW",
                crop_name_ar="بور (راحة)",
                crop_name_en="Fallow (Rest)",
                crop_family=CropFamily.FALLOW,
                suitability_score=75,
                reasons_ar=["يعيد تجديد التربة", "يقطع دورة الأمراض"],
                reasons_en=["Regenerates soil", "Breaks disease cycle"],
                warnings_ar=[],
                warnings_en=[]
            ))

        # Sort by suitability score
        suggestions.sort(key=lambda x: x.suitability_score, reverse=True)

        return suggestions

    def evaluate_rotation(self, seasons: List[SeasonPlan]) -> Dict:
        """
        Evaluate a rotation plan.
        تقييم خطة التدوير.

        Returns diversity, soil health, and disease risk scores.
        """
        if not seasons:
            return {
                "diversity_score": 0,
                "soil_health_score": 0,
                "disease_risk_score": 100,
                "nitrogen_balance": "unknown",
                "recommendations_ar": [],
                "recommendations_en": [],
                "warnings_ar": [],
                "warnings_en": []
            }

        # Calculate diversity score
        unique_families = len(set(s.crop_family for s in seasons))
        diversity_score = min(100, (unique_families / len(seasons)) * 100 * 2)

        # Calculate soil health score
        soil_health_score = 50  # Base score

        # Check for nitrogen fixers
        nitrogen_fixers = sum(1 for s in seasons if self.ROTATION_RULES[s.crop_family].nitrogen_effect == "fix")
        if nitrogen_fixers > 0:
            soil_health_score += 20

        # Check for root depth alternation
        root_alternations = sum(
            1 for i in range(1, len(seasons))
            if self._check_root_alternation(seasons[i].crop_family, seasons[i-1].crop_family)
        )
        soil_health_score += min(20, root_alternations * 5)

        # Check for fallow periods
        fallow_periods = sum(1 for s in seasons if s.crop_family == CropFamily.FALLOW)
        if fallow_periods > 0:
            soil_health_score += 10

        # Calculate disease risk score
        disease_risks = self.get_disease_risk(seasons)
        avg_disease_risk = sum(disease_risks.values()) / max(1, len(disease_risks)) if disease_risks else 0
        disease_risk_score = avg_disease_risk * 100

        # Calculate nitrogen balance
        nitrogen_balance = self.calculate_nitrogen_balance(seasons)

        # Generate recommendations
        recommendations_ar = []
        recommendations_en = []
        warnings_ar = []
        warnings_en = []

        if diversity_score < 40:
            recommendations_ar.append("زيادة تنوع المحاصيل لتحسين صحة التربة")
            recommendations_en.append("Increase crop diversity for better soil health")

        if nitrogen_balance == "negative":
            recommendations_ar.append("إضافة محاصيل بقولية لتثبيت النيتروجين")
            recommendations_en.append("Add legume crops to fix nitrogen")

        if disease_risk_score > 60:
            warnings_ar.append("خطر مرتفع لتراكم الأمراض - تجنب تكرار نفس العائلة")
            warnings_en.append("High disease risk - avoid repeating same family")

        if fallow_periods == 0 and len(seasons) > 4:
            recommendations_ar.append("النظر في إضافة فترة بور لتجديد التربة")
            recommendations_en.append("Consider adding fallow period for soil regeneration")

        return {
            "diversity_score": diversity_score,
            "soil_health_score": min(100, soil_health_score),
            "disease_risk_score": disease_risk_score,
            "nitrogen_balance": nitrogen_balance,
            "recommendations_ar": recommendations_ar,
            "recommendations_en": recommendations_en,
            "warnings_ar": warnings_ar,
            "warnings_en": warnings_en
        }

    def check_rotation_rule(
        self,
        proposed_crop: CropFamily,
        history: List[SeasonPlan]
    ) -> Tuple[bool, List[Tuple[str, str]]]:
        """
        Check if proposed crop violates rotation rules.
        التحقق من أن المحصول المقترح لا يخالف قواعد التدوير.

        Returns (is_valid, messages)
        """
        if proposed_crop not in self.ROTATION_RULES:
            return True, []

        rule = self.ROTATION_RULES[proposed_crop]
        messages = []
        is_valid = True

        # Check minimum years between same family
        for i, season in enumerate(reversed(history)):
            years_ago = i
            if season.crop_family == proposed_crop:
                if years_ago < rule.min_years_between:
                    is_valid = False
                    messages.append((
                        f"يجب الانتظار {rule.min_years_between} سنة بين زراعة {proposed_crop.value}",
                        f"Must wait {rule.min_years_between} years between {proposed_crop.value} crops"
                    ))
                break

        return is_valid, messages

    def calculate_nitrogen_balance(self, seasons: List[SeasonPlan]) -> str:
        """
        Calculate nitrogen balance over rotation.
        حساب توازن النيتروجين خلال التدوير.
        """
        if not seasons:
            return "neutral"

        nitrogen_score = 0

        for season in seasons:
            if season.crop_family not in self.ROTATION_RULES:
                continue

            effect = self.ROTATION_RULES[season.crop_family].nitrogen_effect

            if effect == "fix":
                nitrogen_score += 2
            elif effect == "neutral":
                nitrogen_score += 0
            elif effect == "deplete":
                nitrogen_score -= 1
            elif effect == "heavy_deplete":
                nitrogen_score -= 2

        if nitrogen_score > 0:
            return "positive"
        elif nitrogen_score < -2:
            return "negative"
        else:
            return "neutral"

    def get_disease_risk(self, seasons: List[SeasonPlan]) -> Dict[str, float]:
        """
        Calculate accumulated disease risk.
        حساب خطر تراكم الأمراض.
        """
        disease_risks = {}

        # Track disease accumulation over seasons
        for i, season in enumerate(seasons):
            if season.crop_family not in self.ROTATION_RULES:
                continue

            rule = self.ROTATION_RULES[season.crop_family]

            # Diseases accumulate more if crops are repeated
            decay_factor = 0.7 ** (len(seasons) - i - 1)  # Recent seasons have higher impact

            for disease, risk in rule.disease_risk.items():
                if disease not in disease_risks:
                    disease_risks[disease] = 0
                disease_risks[disease] += risk * decay_factor

        return disease_risks

    def _get_crop_for_family(self, family: CropFamily) -> str:
        """Get a representative crop code for a family"""
        family_crops = {
            CropFamily.CEREALS: "WHEAT",
            CropFamily.LEGUMES: "FABA_BEAN",
            CropFamily.SOLANACEAE: "TOMATO",
            CropFamily.CUCURBITS: "CUCUMBER",
            CropFamily.BRASSICAS: "CABBAGE",
            CropFamily.ALLIUMS: "ONION",
            CropFamily.ROOT_CROPS: "CARROT",
            CropFamily.FIBER: "COTTON",
            CropFamily.OILSEEDS: "SESAME",
            CropFamily.FODDER: "ALFALFA",
            CropFamily.FALLOW: "FALLOW",
            CropFamily.FRUITS: "MANGO",
            CropFamily.SPICES: "CORIANDER",
            CropFamily.SUGAR: "SUGARCANE",
            CropFamily.STIMULANTS: "COFFEE",
        }
        return family_crops.get(family, "WHEAT")

    def _get_crop_name_ar(self, family: CropFamily) -> str:
        """Get Arabic name for crop family"""
        names = {
            CropFamily.CEREALS: "قمح",
            CropFamily.LEGUMES: "فول",
            CropFamily.SOLANACEAE: "طماطم",
            CropFamily.CUCURBITS: "خيار",
            CropFamily.BRASSICAS: "ملفوف",
            CropFamily.ALLIUMS: "بصل",
            CropFamily.ROOT_CROPS: "جزر",
            CropFamily.FIBER: "قطن",
            CropFamily.OILSEEDS: "سمسم",
            CropFamily.FODDER: "برسيم",
            CropFamily.FALLOW: "بور",
            CropFamily.FRUITS: "مانجو",
            CropFamily.SPICES: "كزبرة",
            CropFamily.SUGAR: "قصب السكر",
            CropFamily.STIMULANTS: "قهوة",
        }
        return names.get(family, "قمح")

    def _get_crop_name_en(self, family: CropFamily) -> str:
        """Get English name for crop family"""
        names = {
            CropFamily.CEREALS: "Wheat",
            CropFamily.LEGUMES: "Faba Bean",
            CropFamily.SOLANACEAE: "Tomato",
            CropFamily.CUCURBITS: "Cucumber",
            CropFamily.BRASSICAS: "Cabbage",
            CropFamily.ALLIUMS: "Onion",
            CropFamily.ROOT_CROPS: "Carrot",
            CropFamily.FIBER: "Cotton",
            CropFamily.OILSEEDS: "Sesame",
            CropFamily.FODDER: "Alfalfa",
            CropFamily.FALLOW: "Fallow",
            CropFamily.FRUITS: "Mango",
            CropFamily.SPICES: "Coriander",
            CropFamily.SUGAR: "Sugarcane",
            CropFamily.STIMULANTS: "Coffee",
        }
        return names.get(family, "Wheat")

    def _check_nitrogen_depletion(self, history: List[SeasonPlan]) -> bool:
        """Check if soil nitrogen is likely depleted"""
        if not history:
            return False

        recent = history[-3:] if len(history) >= 3 else history
        nitrogen_score = sum(
            -1 if self.ROTATION_RULES.get(s.crop_family, None) and
                  self.ROTATION_RULES[s.crop_family].nitrogen_effect in ["deplete", "heavy_deplete"]
            else 0
            for s in recent
        )

        return nitrogen_score <= -2

    def _calculate_family_disease_risk(self, family: CropFamily, history: List[SeasonPlan]) -> float:
        """Calculate disease risk for a specific family based on history"""
        if family not in self.ROTATION_RULES:
            return 0.0

        rule = self.ROTATION_RULES[family]
        risk = 0.0

        # Check how recently this family was grown
        for i, season in enumerate(reversed(history[-5:])):
            if season.crop_family == family:
                years_ago = i
                # Risk increases if grown recently
                risk += (1.0 - years_ago / 5.0) * 0.5

        # Check for related families that share diseases
        for i, season in enumerate(reversed(history[-3:])):
            if season.crop_family in rule.bad_predecessors:
                risk += 0.2

        return min(1.0, risk)

    def _check_root_alternation(self, family1: CropFamily, family2: CropFamily) -> bool:
        """Check if two families have different root depths"""
        if family1 not in self.ROTATION_RULES or family2 not in self.ROTATION_RULES:
            return False

        depth1 = self.ROTATION_RULES[family1].root_depth
        depth2 = self.ROTATION_RULES[family2].root_depth

        depth_order = {"shallow": 1, "medium": 2, "deep": 3, "none": 0}

        return abs(depth_order.get(depth1, 0) - depth_order.get(depth2, 0)) >= 1

    def _check_intensive_cultivation(self, history: List[SeasonPlan]) -> bool:
        """Check if field has been intensively cultivated without rest"""
        if len(history) < 4:
            return False

        # Check if no fallow in last 4 seasons
        recent = history[-4:]
        has_fallow = any(s.crop_family == CropFamily.FALLOW for s in recent)

        # Check if heavy feeders dominate
        heavy_feeders = sum(
            1 for s in recent
            if s.crop_family in self.ROTATION_RULES and
               self.ROTATION_RULES[s.crop_family].nutrient_demand == "heavy"
        )

        return not has_fallow and heavy_feeders >= 3

    async def get_field_history(
        self,
        field_id: str,
        years: int = 5
    ) -> List[SeasonPlan]:
        """
        Get crop history for a field.
        الحصول على سجل المحاصيل للحقل.

        This would typically query a database.
        In this implementation, it returns an empty list.
        """
        # TODO: Implement database query
        # This is a placeholder that would connect to field-core database
        return []


# Helper function to serialize dataclasses to dict
def to_dict(obj):
    """Convert dataclass to dictionary"""
    if hasattr(obj, '__dataclass_fields__'):
        result = {}
        for field_name in obj.__dataclass_fields__:
            value = getattr(obj, field_name)
            if isinstance(value, Enum):
                result[field_name] = value.value
            elif isinstance(value, (date, datetime)):
                result[field_name] = value.isoformat()
            elif isinstance(value, list):
                result[field_name] = [to_dict(item) if hasattr(item, '__dataclass_fields__') else item for item in value]
            elif hasattr(value, '__dataclass_fields__'):
                result[field_name] = to_dict(value)
            else:
                result[field_name] = value
        return result
    return obj
