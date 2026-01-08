"""
Unit Tests for Disease Expert Agent
اختبارات الوحدة لوكيل خبير الأمراض

Tests for disease expert functionality:
- Disease diagnosis from symptoms
- Disease diagnosis from images
- Treatment selection (utility-based)
- Prevention recommendations
- Yemen-specific disease knowledge
- Severity assessment
"""

import pytest
from datetime import datetime

from agents import AgentContext, AgentPercept, DiseaseExpertAgent


# ============================================================================
# Test Disease Expert Agent Initialization
# ============================================================================


@pytest.mark.unit
@pytest.mark.specialist
@pytest.mark.agent
class TestDiseaseExpertInitialization:
    """Test disease expert agent initialization"""

    def test_disease_expert_initialization(self):
        """Test basic disease expert initialization"""
        agent = DiseaseExpertAgent(agent_id="test_disease_001")

        assert agent.agent_id == "test_disease_001"
        assert agent.name == "Disease Expert Agent"
        assert agent.name_ar == "وكيل خبير الأمراض"

    def test_disease_database_loaded(self):
        """Test disease database is loaded"""
        agent = DiseaseExpertAgent()

        assert len(agent.DISEASE_DATABASE) > 0
        assert "wheat_leaf_rust" in agent.DISEASE_DATABASE
        assert "tomato_late_blight" in agent.DISEASE_DATABASE

    def test_symptom_disease_mapping(self):
        """Test symptom to disease mapping exists"""
        agent = DiseaseExpertAgent()

        assert len(agent.SYMPTOM_DISEASE_MAP) > 0
        assert "yellowing" in agent.SYMPTOM_DISEASE_MAP
        assert "orange_spots" in agent.SYMPTOM_DISEASE_MAP

    def test_utility_function_set(self):
        """Test utility function is set"""
        agent = DiseaseExpertAgent()

        assert agent.utility_function is not None


# ============================================================================
# Test Disease Diagnosis from Symptoms
# ============================================================================


@pytest.mark.unit
@pytest.mark.specialist
@pytest.mark.asyncio
class TestDiseaseDiagnosisSymptoms:
    """Test disease diagnosis from symptoms"""

    async def test_diagnose_from_reported_symptoms(self):
        """Test diagnosis from user-reported symptoms"""
        agent = DiseaseExpertAgent()

        # Report symptoms of wheat leaf rust
        percept = AgentPercept(
            percept_type="symptoms_report",
            data=["yellowing", "orange_spots"],
            source="farmer",
        )

        await agent.perceive(percept)

        diagnosis = await agent._diagnose()

        assert diagnosis is not None
        # Should match a disease with these symptoms
        assert diagnosis.disease.disease_id in ["wheat_leaf_rust", "coffee_leaf_rust"]

    async def test_match_symptoms_to_diseases(self):
        """Test symptom matching algorithm"""
        agent = DiseaseExpertAgent()

        symptoms = ["yellowing", "orange_spots", "leaf_drop"]

        matches = await agent._match_symptoms(symptoms)

        assert len(matches) > 0
        # Should find multiple disease matches
        disease_ids = [m[0] for m in matches]
        assert "wheat_leaf_rust" in disease_ids or "coffee_leaf_rust" in disease_ids

    async def test_no_diagnosis_without_symptoms(self):
        """Test no diagnosis without symptoms"""
        agent = DiseaseExpertAgent()

        diagnosis = await agent._diagnose()

        assert diagnosis is None

    async def test_multiple_symptom_increases_confidence(self):
        """Test multiple matching symptoms increase confidence"""
        agent = DiseaseExpertAgent()

        # Add multiple symptoms
        percept = AgentPercept(
            percept_type="symptoms_report",
            data=["yellowing", "orange_spots", "leaf_drop"],
            source="farmer",
        )

        await agent.perceive(percept)

        diagnosis = await agent._diagnose()

        # More symptoms should give higher confidence
        assert diagnosis is not None
        assert diagnosis.confidence > 0.3  # Each symptom adds 0.2


# ============================================================================
# Test Disease Diagnosis from Images
# ============================================================================


@pytest.mark.unit
@pytest.mark.specialist
@pytest.mark.asyncio
class TestDiseaseDiagnosisImages:
    """Test disease diagnosis from image analysis"""

    async def test_diagnose_from_image_classification(self, mock_image_data):
        """Test diagnosis from CNN image classification"""
        agent = DiseaseExpertAgent()

        percept = AgentPercept(
            percept_type="image_analysis", data=mock_image_data, source="cnn_model"
        )

        await agent.perceive(percept)

        diagnosis = await agent._diagnose()

        assert diagnosis is not None
        assert diagnosis.disease.disease_id == "wheat_leaf_rust"
        assert diagnosis.confidence == 0.87

    async def test_image_classification_stored_in_beliefs(self, mock_image_data):
        """Test image classification is stored in agent beliefs"""
        agent = DiseaseExpertAgent()

        percept = AgentPercept(
            percept_type="image_analysis", data=mock_image_data, source="cnn_model"
        )

        await agent.perceive(percept)

        assert "image_classification" in agent.state.beliefs
        assert agent.state.beliefs["image_classification"]["disease_id"] == "wheat_leaf_rust"

    async def test_combine_image_and_symptoms(self, mock_image_data):
        """Test combining image and symptom diagnosis"""
        agent = DiseaseExpertAgent()

        # Add image classification
        percept1 = AgentPercept(
            percept_type="image_analysis", data=mock_image_data, source="cnn_model"
        )
        await agent.perceive(percept1)

        # Add reported symptoms
        percept2 = AgentPercept(
            percept_type="symptoms_report", data=["yellowing", "orange_spots"], source="farmer"
        )
        await agent.perceive(percept2)

        diagnosis = await agent._diagnose()

        # Combined evidence should increase confidence
        assert diagnosis is not None
        assert diagnosis.confidence > 0.87  # Higher than image alone


# ============================================================================
# Test Severity Assessment
# ============================================================================


@pytest.mark.unit
@pytest.mark.specialist
@pytest.mark.asyncio
class TestSeverityAssessment:
    """Test disease severity assessment"""

    async def test_assess_severity_high_affected_area(self):
        """Test severity assessment with high affected area"""
        agent = DiseaseExpertAgent()

        agent.state.beliefs["affected_area"] = 60  # 60% affected

        disease = agent.DISEASE_DATABASE["wheat_leaf_rust"]
        severity = await agent._assess_severity(disease)

        assert severity == "critical"

    async def test_assess_severity_medium_affected_area(self):
        """Test severity assessment with medium affected area"""
        agent = DiseaseExpertAgent()

        agent.state.beliefs["affected_area"] = 35  # 35% affected

        disease = agent.DISEASE_DATABASE["wheat_leaf_rust"]
        severity = await agent._assess_severity(disease)

        assert severity in ["high", "medium"]

    async def test_assess_severity_low_affected_area(self):
        """Test severity assessment with low affected area"""
        agent = DiseaseExpertAgent()

        agent.state.beliefs["affected_area"] = 5  # 5% affected

        disease = agent.DISEASE_DATABASE["mango_anthracnose"]
        severity = await agent._assess_severity(disease)

        assert severity == "low"

    async def test_assess_progression_early(self):
        """Test early stage progression assessment"""
        agent = DiseaseExpertAgent()

        agent.state.beliefs["days_since_symptoms"] = 2

        progression = await agent._assess_progression()

        assert progression == "early"

    async def test_assess_progression_mid(self):
        """Test mid stage progression assessment"""
        agent = DiseaseExpertAgent()

        agent.state.beliefs["days_since_symptoms"] = 7

        progression = await agent._assess_progression()

        assert progression == "mid"

    async def test_assess_progression_late(self):
        """Test late stage progression assessment"""
        agent = DiseaseExpertAgent()

        agent.state.beliefs["days_since_symptoms"] = 15

        progression = await agent._assess_progression()

        assert progression == "late"


# ============================================================================
# Test Treatment Selection (Utility-Based)
# ============================================================================


@pytest.mark.unit
@pytest.mark.specialist
@pytest.mark.asyncio
class TestTreatmentSelection:
    """Test utility-based treatment selection"""

    async def test_generate_treatment_options(self):
        """Test generating treatment options from diagnosis"""
        agent = DiseaseExpertAgent()

        # Create mock diagnosis
        disease = agent.DISEASE_DATABASE["wheat_leaf_rust"]

        from agents.specialist.disease_expert_agent import DiagnosisResult

        diagnosis = DiagnosisResult(
            disease=disease,
            confidence=0.85,
            severity_level="medium",
            affected_area_percent=25.0,
            progression_stage="mid",
            urgency="soon",
        )

        options = await agent._generate_treatment_options(diagnosis)

        assert len(options) > 0
        # Should have treatment actions plus prevention
        treatment_actions = [opt for opt in options if opt.action_type == "apply_treatment"]
        assert len(treatment_actions) > 0

    async def test_utility_function_prefers_effective_treatment(self):
        """Test utility function prefers more effective treatment"""
        agent = DiseaseExpertAgent()

        context = AgentContext(crop_type="wheat")

        from agents import AgentAction

        # High effectiveness treatment
        action1 = AgentAction(
            action_type="apply_treatment",
            parameters={
                "treatment": {
                    "effectiveness": 0.90,
                    "cost_yer": 5000,
                    "waiting_period_days": 21,
                },
                "urgency": "soon",
            },
            confidence=0.85,
            priority=1,
            reasoning="High effectiveness",
        )

        # Low effectiveness treatment
        action2 = AgentAction(
            action_type="apply_treatment",
            parameters={
                "treatment": {
                    "effectiveness": 0.60,
                    "cost_yer": 5000,
                    "waiting_period_days": 21,
                },
                "urgency": "soon",
            },
            confidence=0.85,
            priority=1,
            reasoning="Low effectiveness",
        )

        utility1 = agent._treatment_utility(action1, context)
        utility2 = agent._treatment_utility(action2, context)

        assert utility1 > utility2

    async def test_utility_function_emergency_prioritizes_speed(self):
        """Test utility function prioritizes speed for emergencies"""
        agent = DiseaseExpertAgent()

        context = AgentContext(crop_type="tomato")

        from agents import AgentAction

        # Fast but less effective
        action1 = AgentAction(
            action_type="apply_treatment",
            parameters={
                "treatment": {
                    "effectiveness": 0.75,
                    "cost_yer": 3000,
                    "waiting_period_days": 7,
                },
                "urgency": "immediate",
            },
            confidence=0.85,
            priority=1,
            reasoning="Fast treatment",
        )

        # Slow but more effective
        action2 = AgentAction(
            action_type="apply_treatment",
            parameters={
                "treatment": {
                    "effectiveness": 0.85,
                    "cost_yer": 3000,
                    "waiting_period_days": 30,
                },
                "urgency": "immediate",
            },
            confidence=0.85,
            priority=1,
            reasoning="Slow treatment",
        )

        utility1 = agent._treatment_utility(action1, context)
        utility2 = agent._treatment_utility(action2, context)

        # For emergency, faster treatment should have higher utility
        assert utility1 > utility2

    async def test_select_best_treatment(self, mock_image_data):
        """Test selecting best treatment from options"""
        agent = DiseaseExpertAgent()

        # Diagnose disease
        percept = AgentPercept(
            percept_type="image_analysis", data=mock_image_data, source="cnn_model"
        )

        await agent.perceive(percept)
        agent.context = AgentContext(crop_type="wheat")

        action = await agent.think()

        assert action is not None
        # Should select a treatment or prevention action
        assert action.action_type in ["apply_treatment", "prevention_measures", "diagnosis_only"]


# ============================================================================
# Test Complete Diagnosis Workflow
# ============================================================================


@pytest.mark.unit
@pytest.mark.specialist
@pytest.mark.asyncio
class TestDiagnosisWorkflow:
    """Test complete diagnosis workflow"""

    async def test_full_diagnosis_and_treatment_workflow(self, mock_image_data):
        """Test full workflow from perception to action"""
        agent = DiseaseExpertAgent()

        # Set context
        context = AgentContext(
            field_id="test_field",
            crop_type="wheat",
            sensor_data={"temperature": 28.0, "humidity": 60},
        )
        agent.update_context(context)

        # Perceive disease
        percept = AgentPercept(
            percept_type="image_analysis", data=mock_image_data, source="cnn_model"
        )

        result = await agent.run(percept)

        assert result["success"] is True
        assert "action" in result
        assert result["result"]["success"] is True

    async def test_no_disease_detected_action(self):
        """Test action when no disease is detected"""
        agent = DiseaseExpertAgent()

        action = await agent.think()

        assert action is not None
        assert action.action_type == "no_disease_detected"

    async def test_diagnosis_history_tracking(self, mock_image_data):
        """Test diagnosis history is tracked"""
        agent = DiseaseExpertAgent()

        percept = AgentPercept(
            percept_type="image_analysis", data=mock_image_data, source="cnn_model"
        )

        await agent.perceive(percept)
        await agent.think()

        assert len(agent.diagnosis_history) > 0

    async def test_act_treatment_recommendation(self):
        """Test acting on treatment recommendation"""
        agent = DiseaseExpertAgent()

        from agents import AgentAction

        action = AgentAction(
            action_type="apply_treatment",
            parameters={
                "treatment": {
                    "name": "Propiconazole",
                    "name_ar": "بروبيكونازول",
                    "dosage": "0.5 L/ha",
                    "application": "foliar spray",
                    "cost_yer": 5000,
                    "waiting_period_days": 21,
                },
                "disease_ar": "صدأ أوراق القمح",
                "urgency": "soon",
                "application_instructions": {"method": "spray", "timing": "morning"},
            },
            confidence=0.85,
            priority=2,
            reasoning="Treatment recommendation",
        )

        result = await agent.act(action)

        assert result["success"] is True
        assert "recommendation" in result
        assert result["recommendation"]["treatment_name"] == "Propiconazole"

    async def test_act_prevention_measures(self):
        """Test acting on prevention recommendation"""
        agent = DiseaseExpertAgent()

        from agents import AgentAction

        action = AgentAction(
            action_type="prevention_measures",
            parameters={
                "disease": "صدأ أوراق القمح",
                "measures": ["crop rotation", "resistant varieties"],
            },
            confidence=0.90,
            priority=3,
            reasoning="Prevention",
        )

        result = await agent.act(action)

        assert result["success"] is True
        assert "prevention" in result


# ============================================================================
# Test Disease Database Queries
# ============================================================================


@pytest.mark.unit
@pytest.mark.specialist
class TestDiseaseDatabase:
    """Test disease database queries"""

    def test_get_disease_info(self):
        """Test getting disease information"""
        agent = DiseaseExpertAgent()

        info = agent.get_disease_info("wheat_leaf_rust")

        assert info is not None
        assert info["name"] == "Wheat Leaf Rust"
        assert info["name_ar"] == "صدأ أوراق القمح"
        assert len(info["symptoms"]) > 0
        assert len(info["treatments"]) > 0

    def test_get_disease_info_nonexistent(self):
        """Test getting info for nonexistent disease"""
        agent = DiseaseExpertAgent()

        info = agent.get_disease_info("nonexistent_disease")

        assert info is None

    def test_list_diseases_for_crop(self):
        """Test listing diseases for specific crop"""
        agent = DiseaseExpertAgent()

        diseases = agent.list_diseases_for_crop("wheat")

        assert len(diseases) > 0
        # Should include wheat leaf rust
        disease_ids = [d["id"] for d in diseases]
        assert "wheat_leaf_rust" in disease_ids

    def test_list_diseases_for_crop_no_matches(self):
        """Test listing diseases for crop with no diseases"""
        agent = DiseaseExpertAgent()

        diseases = agent.list_diseases_for_crop("banana")

        # May or may not have banana diseases
        assert isinstance(diseases, list)


# ============================================================================
# Test Yemen-Specific Diseases
# ============================================================================


@pytest.mark.unit
@pytest.mark.specialist
class TestYemenSpecificDiseases:
    """Test Yemen-specific disease knowledge"""

    def test_yemen_relevant_crops(self):
        """Test database includes Yemen-relevant crops"""
        agent = DiseaseExpertAgent()

        # Yemen important crops
        yemen_crops = ["wheat", "coffee", "date_palm", "mango"]

        for crop in yemen_crops:
            diseases = agent.list_diseases_for_crop(crop)
            # Should have at least one disease for these crops
            if crop in ["wheat", "coffee", "date_palm", "mango"]:
                assert len(diseases) > 0

    def test_coffee_leaf_rust_exists(self):
        """Test Coffee Leaf Rust (major issue in Yemen)"""
        agent = DiseaseExpertAgent()

        assert "coffee_leaf_rust" in agent.DISEASE_DATABASE

        coffee_rust = agent.DISEASE_DATABASE["coffee_leaf_rust"]
        assert "coffee" in coffee_rust.crop_types

    def test_date_palm_bayoud_exists(self):
        """Test Date Palm Bayoud (critical for Yemen date palms)"""
        agent = DiseaseExpertAgent()

        assert "date_palm_bayoud" in agent.DISEASE_DATABASE

        bayoud = agent.DISEASE_DATABASE["date_palm_bayoud"]
        assert bayoud.severity == "critical"
        assert "date_palm" in bayoud.crop_types


# ============================================================================
# Test Urgency Determination
# ============================================================================


@pytest.mark.unit
@pytest.mark.specialist
class TestUrgencyDetermination:
    """Test urgency determination logic"""

    def test_critical_disease_immediate_urgency(self):
        """Test critical diseases get immediate urgency"""
        agent = DiseaseExpertAgent()

        disease = agent.DISEASE_DATABASE["tomato_late_blight"]  # Critical severity

        urgency = agent._determine_urgency(disease, "critical", "mid")

        assert urgency == "immediate"

    def test_fast_spread_soon_urgency(self):
        """Test fast-spreading diseases get soon urgency"""
        agent = DiseaseExpertAgent()

        disease = agent.DISEASE_DATABASE["wheat_leaf_rust"]  # Fast spread

        urgency = agent._determine_urgency(disease, "medium", "mid")

        assert urgency == "soon"

    def test_late_progression_soon_urgency(self):
        """Test late progression gets soon urgency"""
        agent = DiseaseExpertAgent()

        disease = agent.DISEASE_DATABASE["mango_anthracnose"]

        urgency = agent._determine_urgency(disease, "medium", "late")

        assert urgency == "soon"

    def test_normal_disease_scheduled_urgency(self):
        """Test normal diseases get scheduled urgency"""
        agent = DiseaseExpertAgent()

        disease = agent.DISEASE_DATABASE["mango_anthracnose"]

        urgency = agent._determine_urgency(disease, "low", "early")

        assert urgency == "scheduled"
