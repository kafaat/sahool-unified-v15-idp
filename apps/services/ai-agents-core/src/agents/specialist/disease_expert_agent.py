"""
SAHOOL Disease Expert Agent
وكيل خبير الأمراض

Specialized agent for:
- Plant disease diagnosis
- Treatment recommendations
- Prevention strategies
- Severity assessment
- Yemen-specific disease knowledge

Uses Utility-Based decision making to select best treatment.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from ..base_agent import (
    AgentAction,
    AgentContext,
    AgentLayer,
    AgentPercept,
    AgentType,
    BaseAgent,
)

logger = logging.getLogger(__name__)


@dataclass
class Disease:
    """معلومات المرض"""

    disease_id: str
    name: str
    name_ar: str
    crop_types: list[str]
    symptoms: list[str]
    symptoms_ar: list[str]
    severity: str  # low, medium, high, critical
    spread_rate: str  # slow, moderate, fast
    treatments: list[dict[str, Any]]
    prevention: list[str]
    prevention_ar: list[str]


@dataclass
class DiagnosisResult:
    """نتيجة التشخيص"""

    disease: Disease
    confidence: float
    severity_level: str
    affected_area_percent: float
    progression_stage: str  # early, mid, late
    urgency: str  # immediate, soon, scheduled


class DiseaseExpertAgent(BaseAgent):
    """
    وكيل خبير الأمراض
    Disease Expert Agent for comprehensive plant disease management
    """

    # Yemen-specific disease database
    DISEASE_DATABASE: dict[str, Disease] = {
        "wheat_leaf_rust": Disease(
            disease_id="wheat_leaf_rust",
            name="Wheat Leaf Rust",
            name_ar="صدأ أوراق القمح",
            crop_types=["wheat", "barley"],
            symptoms=["orange pustules on leaves", "yellowing", "premature leaf death"],
            symptoms_ar=["بثور برتقالية على الأوراق", "اصفرار", "موت الأوراق المبكر"],
            severity="high",
            spread_rate="fast",
            treatments=[
                {
                    "name": "Propiconazole",
                    "name_ar": "بروبيكونازول",
                    "dosage": "0.5 L/ha",
                    "application": "foliar spray",
                    "effectiveness": 0.85,
                    "cost_yer": 5000,
                    "waiting_period_days": 21,
                },
                {
                    "name": "Tebuconazole",
                    "name_ar": "تيبوكونازول",
                    "dosage": "0.4 L/ha",
                    "application": "foliar spray",
                    "effectiveness": 0.80,
                    "cost_yer": 4500,
                    "waiting_period_days": 14,
                },
            ],
            prevention=["resistant varieties", "crop rotation", "timely sowing"],
            prevention_ar=[
                "أصناف مقاومة",
                "تناوب المحاصيل",
                "الزراعة في الوقت المناسب",
            ],
        ),
        "tomato_late_blight": Disease(
            disease_id="tomato_late_blight",
            name="Tomato Late Blight",
            name_ar="اللفحة المتأخرة للطماطم",
            crop_types=["tomato", "potato"],
            symptoms=["water-soaked lesions", "white mold", "rapid plant death"],
            symptoms_ar=["بقع مائية", "عفن أبيض", "موت سريع للنبات"],
            severity="critical",
            spread_rate="fast",
            treatments=[
                {
                    "name": "Copper Hydroxide",
                    "name_ar": "هيدروكسيد النحاس",
                    "dosage": "2.5 kg/ha",
                    "application": "foliar spray",
                    "effectiveness": 0.75,
                    "cost_yer": 3000,
                    "waiting_period_days": 7,
                },
                {
                    "name": "Mancozeb",
                    "name_ar": "مانكوزيب",
                    "dosage": "2 kg/ha",
                    "application": "foliar spray",
                    "effectiveness": 0.70,
                    "cost_yer": 2500,
                    "waiting_period_days": 14,
                },
            ],
            prevention=[
                "proper spacing",
                "avoid overhead irrigation",
                "destroy infected plants",
            ],
            prevention_ar=["تباعد مناسب", "تجنب الري العلوي", "إتلاف النباتات المصابة"],
        ),
        "coffee_leaf_rust": Disease(
            disease_id="coffee_leaf_rust",
            name="Coffee Leaf Rust",
            name_ar="صدأ أوراق البن",
            crop_types=["coffee"],
            symptoms=["yellow-orange spots", "premature leaf drop", "reduced yield"],
            symptoms_ar=["بقع برتقالية صفراء", "سقوط الأوراق المبكر", "انخفاض الإنتاج"],
            severity="high",
            spread_rate="moderate",
            treatments=[
                {
                    "name": "Bordeaux Mixture",
                    "name_ar": "خليط بوردو",
                    "dosage": "3 kg/ha",
                    "application": "foliar spray",
                    "effectiveness": 0.80,
                    "cost_yer": 4000,
                    "waiting_period_days": 21,
                }
            ],
            prevention=["shade management", "resistant varieties", "proper nutrition"],
            prevention_ar=["إدارة الظل", "أصناف مقاومة", "تغذية سليمة"],
        ),
        "date_palm_bayoud": Disease(
            disease_id="date_palm_bayoud",
            name="Date Palm Bayoud Disease",
            name_ar="مرض البيوض في النخيل",
            crop_types=["date_palm"],
            symptoms=["frond wilting", "vascular browning", "tree death"],
            symptoms_ar=["ذبول السعف", "اسمرار الأوعية", "موت الشجرة"],
            severity="critical",
            spread_rate="slow",
            treatments=[
                {
                    "name": "Carbendazim",
                    "name_ar": "كاربندازيم",
                    "dosage": "1 g/L soil drench",
                    "application": "soil drench",
                    "effectiveness": 0.50,
                    "cost_yer": 8000,
                    "waiting_period_days": 60,
                }
            ],
            prevention=[
                "certified planting material",
                "quarantine",
                "resistant varieties",
            ],
            prevention_ar=["مواد زراعة معتمدة", "الحجر الصحي", "أصناف مقاومة"],
        ),
        "mango_anthracnose": Disease(
            disease_id="mango_anthracnose",
            name="Mango Anthracnose",
            name_ar="أنثراكنوز المانجو",
            crop_types=["mango"],
            symptoms=["black spots on fruit", "flower blight", "leaf spots"],
            symptoms_ar=["بقع سوداء على الثمار", "آفة الزهور", "بقع الأوراق"],
            severity="medium",
            spread_rate="moderate",
            treatments=[
                {
                    "name": "Mancozeb",
                    "name_ar": "مانكوزيب",
                    "dosage": "2.5 g/L",
                    "application": "foliar spray",
                    "effectiveness": 0.75,
                    "cost_yer": 2500,
                    "waiting_period_days": 14,
                }
            ],
            prevention=[
                "prune infected parts",
                "good air circulation",
                "avoid wetting foliage",
            ],
            prevention_ar=["تقليم الأجزاء المصابة", "تهوية جيدة", "تجنب ترطيب الأوراق"],
        ),
    }

    # Symptom to disease mapping
    SYMPTOM_DISEASE_MAP = {
        "yellowing": ["wheat_leaf_rust", "coffee_leaf_rust"],
        "orange_spots": ["wheat_leaf_rust", "coffee_leaf_rust"],
        "water_soaked": ["tomato_late_blight"],
        "white_mold": ["tomato_late_blight"],
        "black_spots": ["mango_anthracnose"],
        "wilting": ["date_palm_bayoud", "tomato_late_blight"],
        "leaf_drop": ["coffee_leaf_rust", "mango_anthracnose"],
    }

    def __init__(self, agent_id: str = "disease_expert_001"):
        super().__init__(
            agent_id=agent_id,
            name="Disease Expert Agent",
            name_ar="وكيل خبير الأمراض",
            agent_type=AgentType.UTILITY_BASED,
            layer=AgentLayer.SPECIALIST,
            description="Expert agent for plant disease diagnosis and treatment",
            description_ar="وكيل خبير لتشخيص أمراض النباتات وعلاجها",
        )

        # Diagnosis history for learning
        self.diagnosis_history: list[DiagnosisResult] = []

        # Set utility function for treatment selection
        self.set_utility_function(self._treatment_utility)

    def _treatment_utility(self, action: AgentAction, context: AgentContext) -> float:
        """
        دالة المنفعة لاختيار العلاج
        Utility function to evaluate treatment options
        """
        if action.action_type != "apply_treatment":
            return 0.0

        treatment = action.parameters.get("treatment", {})

        # Factors for utility calculation
        effectiveness = treatment.get("effectiveness", 0.5)
        cost = treatment.get("cost_yer", 10000)
        waiting_period = treatment.get("waiting_period_days", 30)
        urgency = action.parameters.get("urgency", "scheduled")

        # Normalize cost (lower is better)
        cost_factor = 1 - (cost / 10000)  # Normalize to 10000 YER max

        # Normalize waiting period (shorter is better for urgent cases)
        wait_factor = 1 - (waiting_period / 60)  # Max 60 days

        # Urgency weight
        urgency_weights = {
            "immediate": {"effectiveness": 0.5, "cost": 0.1, "wait": 0.4},
            "soon": {"effectiveness": 0.4, "cost": 0.3, "wait": 0.3},
            "scheduled": {"effectiveness": 0.3, "cost": 0.4, "wait": 0.3},
        }

        weights = urgency_weights.get(urgency, urgency_weights["scheduled"])

        utility = (
            weights["effectiveness"] * effectiveness
            + weights["cost"] * cost_factor
            + weights["wait"] * wait_factor
        )

        return utility

    async def perceive(self, percept: AgentPercept) -> None:
        """استقبال المدخلات للتشخيص"""
        if percept.percept_type == "image_analysis":
            # Results from CNN disease detection
            self.state.beliefs["image_classification"] = percept.data

        elif percept.percept_type == "symptoms_report":
            # User-reported symptoms
            self.state.beliefs["reported_symptoms"] = percept.data

        elif percept.percept_type == "field_history":
            # Historical disease data
            self.state.beliefs["field_history"] = percept.data

        elif percept.percept_type == "weather_conditions":
            # Weather affects disease spread
            self.state.beliefs["weather"] = percept.data

        # Update context
        if self.context:
            self.context.metadata["disease_beliefs"] = self.state.beliefs
        else:
            self.context = AgentContext(
                metadata={"disease_beliefs": self.state.beliefs}
            )

    async def think(self) -> AgentAction | None:
        """التشخيص واختيار العلاج"""
        # Step 1: Diagnose
        diagnosis = await self._diagnose()

        if not diagnosis:
            return AgentAction(
                action_type="no_disease_detected",
                parameters={},
                confidence=0.7,
                priority=4,
                reasoning="لم يتم اكتشاف مرض واضح",
                source_agent=self.agent_id,
            )

        self.diagnosis_history.append(diagnosis)

        # Step 2: Evaluate treatment options
        treatment_actions = await self._generate_treatment_options(diagnosis)

        if not treatment_actions:
            return AgentAction(
                action_type="diagnosis_only",
                parameters={"diagnosis": diagnosis.__dict__},
                confidence=diagnosis.confidence,
                priority=2,
                reasoning=f"تم تشخيص {diagnosis.disease.name_ar} - لا توجد علاجات متاحة",
                source_agent=self.agent_id,
            )

        # Step 3: Select best treatment using utility function
        best_treatment = self.select_best_action(treatment_actions, self.context)
        best_treatment.source_agent = self.agent_id

        return best_treatment

    async def _diagnose(self) -> DiagnosisResult | None:
        """تشخيص المرض"""
        candidates: list[tuple[str, float]] = []

        # From CNN image classification
        if "image_classification" in self.state.beliefs:
            img_result = self.state.beliefs["image_classification"]
            disease_id = img_result.get("disease_id")
            confidence = img_result.get("confidence", 0)

            if disease_id in self.DISEASE_DATABASE:
                candidates.append((disease_id, confidence))

        # From reported symptoms
        if "reported_symptoms" in self.state.beliefs:
            symptoms = self.state.beliefs["reported_symptoms"]
            symptom_matches = await self._match_symptoms(symptoms)
            candidates.extend(symptom_matches)

        # From field history
        if "field_history" in self.state.beliefs:
            history = self.state.beliefs["field_history"]
            if history.get("previous_diseases"):
                for prev in history["previous_diseases"]:
                    if prev["disease_id"] in self.DISEASE_DATABASE:
                        # Slight boost for recurring diseases
                        candidates.append((prev["disease_id"], 0.3))

        if not candidates:
            return None

        # Aggregate confidences
        disease_scores: dict[str, float] = {}
        for disease_id, score in candidates:
            disease_scores[disease_id] = disease_scores.get(disease_id, 0) + score

        # Select highest scoring disease
        best_disease_id = max(disease_scores, key=disease_scores.get)
        final_confidence = min(disease_scores[best_disease_id], 1.0)

        disease = self.DISEASE_DATABASE[best_disease_id]

        # Assess severity based on symptoms and conditions
        severity = await self._assess_severity(disease)
        progression = await self._assess_progression()

        return DiagnosisResult(
            disease=disease,
            confidence=final_confidence,
            severity_level=severity,
            affected_area_percent=self.state.beliefs.get("affected_area", 10),
            progression_stage=progression,
            urgency=self._determine_urgency(disease, severity, progression),
        )

    async def _match_symptoms(self, symptoms: list[str]) -> list[tuple[str, float]]:
        """مطابقة الأعراض مع الأمراض"""
        matches = []
        for symptom in symptoms:
            symptom_lower = symptom.lower().replace(" ", "_")
            if symptom_lower in self.SYMPTOM_DISEASE_MAP:
                for disease_id in self.SYMPTOM_DISEASE_MAP[symptom_lower]:
                    matches.append((disease_id, 0.2))  # 0.2 per matching symptom
        return matches

    async def _assess_severity(self, disease: Disease) -> str:
        """تقييم شدة المرض"""
        base_severity = disease.severity
        affected_area = self.state.beliefs.get("affected_area", 10)

        if affected_area > 50:
            return "critical"
        elif affected_area > 30:
            return "high" if base_severity != "low" else "medium"
        elif affected_area > 10:
            return base_severity
        else:
            return "low" if base_severity not in ["critical", "high"] else "medium"

    async def _assess_progression(self) -> str:
        """تقييم مرحلة تقدم المرض"""
        days_since_first_symptom = self.state.beliefs.get("days_since_symptoms", 0)

        if days_since_first_symptom < 3:
            return "early"
        elif days_since_first_symptom < 10:
            return "mid"
        else:
            return "late"

    def _determine_urgency(
        self, disease: Disease, severity: str, progression: str
    ) -> str:
        """تحديد الأولوية"""
        if disease.severity == "critical" or severity == "critical":
            return "immediate"
        elif disease.spread_rate == "fast" or progression == "late":
            return "soon"
        else:
            return "scheduled"

    async def _generate_treatment_options(
        self, diagnosis: DiagnosisResult
    ) -> list[AgentAction]:
        """إنشاء خيارات العلاج"""
        actions = []

        for treatment in diagnosis.disease.treatments:
            action = AgentAction(
                action_type="apply_treatment",
                parameters={
                    "treatment": treatment,
                    "disease": diagnosis.disease.name,
                    "disease_ar": diagnosis.disease.name_ar,
                    "urgency": diagnosis.urgency,
                    "severity": diagnosis.severity_level,
                    "application_instructions": {
                        "method": treatment["application"],
                        "dosage": treatment["dosage"],
                        "timing": "early morning or late afternoon",
                        "precautions": "wear protective equipment",
                    },
                },
                confidence=diagnosis.confidence * treatment["effectiveness"],
                priority=1 if diagnosis.urgency == "immediate" else 2,
                reasoning=f"علاج {diagnosis.disease.name_ar} باستخدام {treatment['name_ar']}",
            )
            actions.append(action)

        # Add prevention action
        actions.append(
            AgentAction(
                action_type="prevention_measures",
                parameters={
                    "disease": diagnosis.disease.name_ar,
                    "measures": diagnosis.disease.prevention_ar,
                },
                confidence=0.9,
                priority=3,
                reasoning=f"إجراءات وقائية من {diagnosis.disease.name_ar}",
            )
        )

        return actions

    async def act(self, action: AgentAction) -> dict[str, Any]:
        """تنفيذ التوصية"""
        result = {
            "action_type": action.action_type,
            "executed_at": datetime.now().isoformat(),
            "success": True,
        }

        if action.action_type == "apply_treatment":
            treatment = action.parameters.get("treatment", {})
            result["recommendation"] = {
                "title_ar": f"علاج {action.parameters.get('disease_ar')}",
                "treatment_name": treatment.get("name"),
                "treatment_name_ar": treatment.get("name_ar"),
                "dosage": treatment.get("dosage"),
                "application_method": treatment.get("application"),
                "estimated_cost_yer": treatment.get("cost_yer"),
                "waiting_period_days": treatment.get("waiting_period_days"),
                "instructions": action.parameters.get("application_instructions"),
                "urgency": action.parameters.get("urgency"),
                "confidence": action.confidence,
            }

        elif action.action_type == "prevention_measures":
            result["prevention"] = {
                "disease": action.parameters.get("disease"),
                "measures": action.parameters.get("measures"),
            }

        elif action.action_type == "no_disease_detected":
            result["status"] = "healthy"
            result["message_ar"] = "النبات يبدو سليماً"

        return result

    def get_disease_info(self, disease_id: str) -> dict[str, Any] | None:
        """الحصول على معلومات المرض"""
        disease = self.DISEASE_DATABASE.get(disease_id)
        if disease:
            return {
                "id": disease.disease_id,
                "name": disease.name,
                "name_ar": disease.name_ar,
                "symptoms": disease.symptoms,
                "symptoms_ar": disease.symptoms_ar,
                "severity": disease.severity,
                "treatments": disease.treatments,
                "prevention": disease.prevention,
                "prevention_ar": disease.prevention_ar,
            }
        return None

    def list_diseases_for_crop(self, crop_type: str) -> list[dict[str, Any]]:
        """قائمة الأمراض حسب المحصول"""
        diseases = []
        for disease in self.DISEASE_DATABASE.values():
            if crop_type in disease.crop_types:
                diseases.append(
                    {
                        "id": disease.disease_id,
                        "name": disease.name,
                        "name_ar": disease.name_ar,
                        "severity": disease.severity,
                    }
                )
        return diseases
