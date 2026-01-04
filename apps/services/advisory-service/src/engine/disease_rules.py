"""
Disease Rules Engine - SAHOOL Agro Advisor
Rule-based disease assessment and recommendation generation
"""

from ..kb.diseases import DISEASES, get_disease


class DiseaseAssessment:
    """Result of disease assessment"""

    def __init__(
        self,
        disease_id: str,
        category: str,
        severity: str,
        title_ar: str,
        title_en: str,
        actions: list[str],
        confidence: float,
        urgency_hours: int,
        details: dict = None,
    ):
        self.disease_id = disease_id
        self.category = category
        self.severity = severity
        self.title_ar = title_ar
        self.title_en = title_en
        self.actions = actions
        self.confidence = confidence
        self.urgency_hours = urgency_hours
        self.details = details or {}

    def to_dict(self) -> dict:
        return {
            "disease_id": self.disease_id,
            "category": self.category,
            "severity": self.severity,
            "title_ar": self.title_ar,
            "title_en": self.title_en,
            "actions": self.actions,
            "confidence": self.confidence,
            "urgency_hours": self.urgency_hours,
            "details": self.details,
        }


def assess_from_image_event(
    condition_id: str,
    confidence: float,
    crop: str = None,
    weather_context: dict = None,
) -> DiseaseAssessment | None:
    """
    Assess disease from image classification event

    Args:
        condition_id: Disease ID from classifier
        confidence: Classification confidence (0-1)
        crop: Optional crop type for context
        weather_context: Optional weather data for severity adjustment

    Returns:
        DiseaseAssessment if condition warrants action, None otherwise
    """
    # Minimum confidence threshold
    if confidence < 0.60:
        return None

    disease = get_disease(condition_id)
    if not disease:
        return None

    # Adjust severity based on weather conditions
    severity = disease["severity_default"]
    urgency = disease["urgency_hours"]

    if weather_context:
        severity, urgency = _adjust_for_weather(
            disease, weather_context, severity, urgency
        )

    # Build assessment
    return DiseaseAssessment(
        disease_id=condition_id,
        category="disease",
        severity=severity,
        title_ar=f"اشتباه {disease['name_ar']}",
        title_en=f"Suspected {disease['name_en']}",
        actions=disease["actions"],
        confidence=confidence,
        urgency_hours=urgency,
        details={
            "symptoms_ar": disease["symptoms_ar"],
            "symptoms_en": disease["symptoms_en"],
            "pathogen": disease.get("pathogen"),
        },
    )


def assess_from_symptoms(
    symptoms: list[str],
    crop: str,
    lang: str = "ar",
) -> list[DiseaseAssessment]:
    """
    Assess possible diseases from reported symptoms

    Args:
        symptoms: List of symptom descriptions
        crop: Crop type
        lang: Language of symptoms (ar/en)

    Returns:
        List of possible disease assessments ordered by match score
    """
    assessments = []
    symptoms_lower = [s.lower() for s in symptoms]
    symptoms_field = "symptoms_ar" if lang == "ar" else "symptoms_en"

    for disease_id, disease in DISEASES.items():
        # Check crop match
        if disease["crop"] != crop and disease["crop"] != "general":
            continue

        # Calculate symptom match score
        disease_symptoms = [s.lower() for s in disease[symptoms_field]]
        matches = sum(
            1
            for symptom in symptoms_lower
            if any(symptom in ds or ds in symptom for ds in disease_symptoms)
        )

        if matches > 0:
            match_ratio = matches / len(disease_symptoms)
            confidence = min(0.9, match_ratio + 0.3)  # Base confidence + match bonus

            assessments.append(
                DiseaseAssessment(
                    disease_id=disease_id,
                    category="disease",
                    severity=disease["severity_default"],
                    title_ar=f"اشتباه {disease['name_ar']}",
                    title_en=f"Suspected {disease['name_en']}",
                    actions=disease["actions"],
                    confidence=round(confidence, 2),
                    urgency_hours=disease["urgency_hours"],
                    details={
                        "matched_symptoms": matches,
                        "total_symptoms": len(disease_symptoms),
                    },
                )
            )

    # Sort by confidence descending
    assessments.sort(key=lambda x: x.confidence, reverse=True)
    return assessments[:5]  # Top 5 matches


def _adjust_for_weather(
    disease: dict,
    weather: dict,
    base_severity: str,
    base_urgency: int,
) -> tuple[str, int]:
    """
    Adjust disease severity and urgency based on weather conditions
    """
    severity = base_severity
    urgency = base_urgency

    conditions = disease.get("conditions", {})

    # Check humidity
    if "humidity_min" in conditions:
        current_humidity = weather.get("humidity", 50)
        if current_humidity >= conditions["humidity_min"]:
            # Favorable conditions - increase severity
            if severity == "medium":
                severity = "high"
            urgency = max(12, urgency // 2)  # Reduce urgency time

    # Check temperature
    if "temp_range" in conditions:
        current_temp = weather.get("temperature", 25)
        temp_min, temp_max = conditions["temp_range"]
        if temp_min <= current_temp <= temp_max:
            # Optimal disease conditions
            urgency = max(12, urgency // 2)

    # Check for rain (spreads many diseases)
    if weather.get("precipitation", 0) > 5:  # mm
        if conditions.get("spread") in ["rain_splash", "wind_rain"]:
            if severity == "medium":
                severity = "high"
            urgency = max(6, urgency // 3)

    return severity, urgency


def get_action_details(action_id: str, lang: str = "ar") -> dict:
    """
    Get detailed instructions for a recommended action
    """
    ACTIONS = {
        "spray_copper": {
            "name_ar": "رش بالنحاس",
            "name_en": "Copper Spray",
            "instructions_ar": "رش بمبيد نحاسي (هيدروكسيد النحاس) بمعدل 2-3 جم/لتر",
            "instructions_en": "Spray with copper fungicide (copper hydroxide) at 2-3 g/L",
            "task_type": "spray",
            "priority": "high",
        },
        "spray_mancozeb": {
            "name_ar": "رش مانكوزيب",
            "name_en": "Mancozeb Spray",
            "instructions_ar": "رش بمبيد مانكوزيب بمعدل 2.5 جم/لتر",
            "instructions_en": "Spray with Mancozeb at 2.5 g/L",
            "task_type": "spray",
            "priority": "high",
        },
        "remove_infected_parts": {
            "name_ar": "إزالة الأجزاء المصابة",
            "name_en": "Remove Infected Parts",
            "instructions_ar": "إزالة وحرق الأوراق والأجزاء المصابة بعيداً عن الحقل",
            "instructions_en": "Remove and burn infected leaves and parts away from field",
            "task_type": "manual",
            "priority": "medium",
        },
        "avoid_overhead_irrigation": {
            "name_ar": "تجنب الري الرذاذي",
            "name_en": "Avoid Overhead Irrigation",
            "instructions_ar": "التحول للري بالتنقيط أو الري الأرضي",
            "instructions_en": "Switch to drip irrigation or surface irrigation",
            "task_type": "irrigation",
            "priority": "medium",
        },
        "improve_air_circulation": {
            "name_ar": "تحسين التهوية",
            "name_en": "Improve Air Circulation",
            "instructions_ar": "تقليم النباتات وإزالة الأوراق السفلية لتحسين التهوية",
            "instructions_en": "Prune plants and remove lower leaves for better air flow",
            "task_type": "manual",
            "priority": "low",
        },
        "spray_sulfur": {
            "name_ar": "رش بالكبريت",
            "name_en": "Sulfur Spray",
            "instructions_ar": "رش بالكبريت الميكروني بمعدل 2-3 جم/لتر",
            "instructions_en": "Spray with micronized sulfur at 2-3 g/L",
            "task_type": "spray",
            "priority": "medium",
        },
        "spray_neem_oil": {
            "name_ar": "رش بزيت النيم",
            "name_en": "Neem Oil Spray",
            "instructions_ar": "رش بزيت النيم المخفف 1% مع مادة ناشرة",
            "instructions_en": "Spray with 1% neem oil solution with spreader",
            "task_type": "spray",
            "priority": "medium",
        },
        "use_yellow_sticky_traps": {
            "name_ar": "استخدام المصائد الصفراء",
            "name_en": "Use Yellow Sticky Traps",
            "instructions_ar": "تعليق مصائد صفراء لاصقة بمعدل 20-30 مصيدة/دونم",
            "instructions_en": "Hang yellow sticky traps at 20-30 traps per dunum",
            "task_type": "monitoring",
            "priority": "medium",
        },
    }

    action = ACTIONS.get(action_id, {})
    if not action:
        return {
            "name_ar": action_id,
            "name_en": action_id,
            "instructions_ar": "راجع المختص الزراعي",
            "instructions_en": "Consult agricultural specialist",
            "task_type": "general",
            "priority": "medium",
        }

    return action
