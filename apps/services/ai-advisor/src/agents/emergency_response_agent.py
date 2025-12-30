"""
Emergency Response Agent
وكيل الاستجابة للطوارئ

Specialized agent for rapid agricultural emergency response.
وكيل متخصص في الاستجابة السريعة للطوارئ الزراعية.
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime
import structlog
from langchain_core.tools import Tool

from .base_agent import BaseAgent

logger = structlog.get_logger()


class EmergencyType(Enum):
    """
    Types of agricultural emergencies
    أنواع الطوارئ الزراعية
    """
    DROUGHT = "drought"  # Water scarcity crisis | أزمة ندرة المياه
    FLOOD = "flood"  # Excess water/waterlogging | المياه الزائدة/التشبع بالمياه
    FROST = "frost"  # Frost damage risk | خطر أضرار الصقيع
    HEAT_WAVE = "heat_wave"  # Extreme heat stress | إجهاد حراري شديد
    PEST_OUTBREAK = "pest_outbreak"  # Severe pest infestation | غزو آفات شديد
    DISEASE_EPIDEMIC = "disease_epidemic"  # Rapid disease spread | انتشار سريع للأمراض
    HAIL_DAMAGE = "hail_damage"  # Post-hail recovery | التعافي بعد البرد
    FIRE_RISK = "fire_risk"  # Wildfire threats | تهديدات الحرائق


class SeverityLevel(Enum):
    """
    Emergency severity levels
    مستويات شدة الطوارئ
    """
    LOW = "low"  # Monitoring required | مطلوب مراقبة
    MODERATE = "moderate"  # Action recommended | إجراء موصى به
    HIGH = "high"  # Immediate action needed | حاجة لإجراء فوري
    CRITICAL = "critical"  # Emergency response | استجابة طوارئ


class EmergencyResponseAgent(BaseAgent):
    """
    Emergency Response Agent for rapid agricultural crisis management
    وكيل الاستجابة للطوارئ لإدارة الأزمات الزراعية السريعة

    Specializes in:
    - Rapid emergency assessment (< 5 seconds)
    - Crisis response planning
    - Multi-agent coordination
    - Resource optimization
    - Damage estimation
    - Insurance documentation
    - Recovery monitoring
    - Post-emergency analysis

    متخصص في:
    - التقييم السريع للطوارئ (< 5 ثوانٍ)
    - تخطيط الاستجابة للأزمات
    - التنسيق متعدد الوكلاء
    - تحسين الموارد
    - تقدير الأضرار
    - توثيق التأمين
    - مراقبة التعافي
    - التحليل بعد الطوارئ
    """

    # Emergency response time target in seconds | الهدف الزمني للاستجابة للطوارئ بالثواني
    RESPONSE_TIME_TARGET = 5

    # Bilingual emergency messages | رسائل الطوارئ ثنائية اللغة
    EMERGENCY_MESSAGES = {
        EmergencyType.DROUGHT: {
            "en": "DROUGHT ALERT: Water scarcity detected. Immediate irrigation optimization required.",
            "ar": "تنبيه الجفاف: تم اكتشاف ندرة المياه. مطلوب تحسين الري الفوري."
        },
        EmergencyType.FLOOD: {
            "en": "FLOOD WARNING: Excess water detected. Drainage action required immediately.",
            "ar": "تحذير الفيضان: تم اكتشاف مياه زائدة. مطلوب إجراء الصرف فوراً."
        },
        EmergencyType.FROST: {
            "en": "FROST ALERT: Freezing temperatures imminent. Protective measures needed now.",
            "ar": "تنبيه الصقيع: درجات حرارة متجمدة وشيكة. التدابير الوقائية مطلوبة الآن."
        },
        EmergencyType.HEAT_WAVE: {
            "en": "HEAT WAVE WARNING: Extreme temperatures detected. Crop stress mitigation urgent.",
            "ar": "تحذير موجة الحر: تم اكتشاف درجات حرارة شديدة. تخفيف إجهاد المحاصيل عاجل."
        },
        EmergencyType.PEST_OUTBREAK: {
            "en": "PEST OUTBREAK: Severe infestation detected. Immediate control measures required.",
            "ar": "تفشي الآفات: تم اكتشاف إصابة شديدة. تدابير المكافحة الفورية مطلوبة."
        },
        EmergencyType.DISEASE_EPIDEMIC: {
            "en": "DISEASE EPIDEMIC: Rapid pathogen spread detected. Urgent containment needed.",
            "ar": "وباء المرض: تم اكتشاف انتشار سريع للممرض. احتواء عاجل مطلوب."
        },
        EmergencyType.HAIL_DAMAGE: {
            "en": "HAIL DAMAGE ALERT: Crop damage from hail. Recovery plan activation required.",
            "ar": "تنبيه أضرار البرد: أضرار المحاصيل من البرد. تفعيل خطة التعافي مطلوب."
        },
        EmergencyType.FIRE_RISK: {
            "en": "FIRE RISK WARNING: High wildfire danger. Immediate prevention measures needed.",
            "ar": "تحذير خطر الحريق: خطر حرائق مرتفع. تدابير الوقاية الفورية مطلوبة."
        }
    }

    def __init__(
        self,
        tools: Optional[List[Tool]] = None,
        retriever: Optional[Any] = None,
    ):
        """
        Initialize Emergency Response Agent
        تهيئة وكيل الاستجابة للطوارئ
        """
        super().__init__(
            name="emergency_response",
            role="Agricultural Emergency Response Coordinator",
            tools=tools,
            retriever=retriever,
        )

        # Track active emergencies | تتبع الطوارئ النشطة
        self.active_emergencies: Dict[str, Dict[str, Any]] = {}

        logger.info("emergency_response_agent_initialized")

    def get_system_prompt(self) -> str:
        """
        Get system prompt for Emergency Response Agent
        الحصول على موجه النظام لوكيل الاستجابة للطوارئ
        """
        return """You are an expert Agricultural Emergency Response Coordinator with rapid crisis management capabilities.

Your expertise includes:
- Rapid emergency assessment and triage (< 5 seconds response time)
- Crisis response planning for agricultural disasters
- Multi-agent coordination during emergencies
- Resource allocation under time and budget constraints
- Damage estimation and impact assessment
- Insurance documentation and claims support
- Recovery monitoring and adaptive management
- Post-emergency analysis and continuous improvement

Emergency Types You Handle:
1. DROUGHT - Water scarcity, irrigation failure, crop stress
2. FLOOD - Waterlogging, drainage issues, soil erosion
3. FROST - Freezing damage, cold stress, crop protection
4. HEAT_WAVE - Heat stress, water demand spikes, crop damage
5. PEST_OUTBREAK - Rapid pest population explosion, widespread damage
6. DISEASE_EPIDEMIC - Fast-spreading plant diseases, containment challenges
7. HAIL_DAMAGE - Physical crop damage, recovery strategies
8. FIRE_RISK - Wildfire threats, prevention, evacuation planning

Your Emergency Response Protocol:
1. ASSESS - Rapid situation analysis (severity, scope, urgency)
2. ALERT - Immediate bilingual notifications to stakeholders
3. PLAN - Create prioritized action plans with timelines
4. COORDINATE - Engage specialized agents and resources
5. EXECUTE - Guide implementation with real-time monitoring
6. DOCUMENT - Track all actions for insurance and learning
7. RECOVER - Monitor recovery progress and adapt strategies
8. ANALYZE - Extract lessons learned for future preparedness

Key Principles:
- Speed is critical: Provide actionable guidance within 5 seconds
- Clear communication: Use bilingual messages (Arabic/English)
- Evidence-based: Use sensor data, weather forecasts, historical patterns
- Resource-aware: Optimize for available time, budget, and materials
- Multi-agent coordination: Leverage specialized agents when needed
- Recovery-focused: Plan not just for crisis, but for full recovery
- Documentation: Ensure complete records for insurance and analysis
- Continuous learning: Extract and apply lessons from each emergency

Response Priorities by Severity:
- CRITICAL: Immediate action, mobilize all resources, real-time coordination
- HIGH: Urgent action within hours, coordinate key resources
- MODERATE: Action within 24-48 hours, scheduled resource allocation
- LOW: Monitoring and preventive measures, scheduled follow-up

Always provide:
- Clear severity assessment
- Immediate action items
- Resource requirements
- Timeline expectations
- Risk mitigation strategies
- Recovery milestones
- Documentation requirements

Communicate with urgency, clarity, and empathy in both Arabic and English.

أنت منسق خبير للاستجابة لطوارئ الزراعية مع قدرات إدارة الأزمات السريعة.

خبرتك تشمل:
- التقييم السريع للطوارئ والفرز (وقت استجابة أقل من 5 ثوانٍ)
- تخطيط الاستجابة للأزمات الزراعية
- التنسيق متعدد الوكلاء خلال الطوارئ
- تخصيص الموارد تحت قيود الوقت والميزانية
- تقدير الأضرار وتقييم التأثير
- توثيق التأمين ودعم المطالبات
- مراقبة التعافي والإدارة التكيفية
- التحليل بعد الطوارئ والتحسين المستمر

قدم استجابات سريعة وواضحة وعملية بالعربية والإنجليزية."""

    async def assess_emergency(
        self,
        emergency_type: str,
        field_data: Dict[str, Any],
        severity: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Quick emergency assessment (< 5 seconds target)
        التقييم السريع للطوارئ (هدف < 5 ثوانٍ)

        Args:
            emergency_type: Type of emergency | نوع الطوارئ
            field_data: Field conditions and sensor data | بيانات الحقل والمستشعرات
            severity: Optional severity override | تجاوز خطورة اختياري

        Returns:
            Emergency assessment with severity and actions | تقييم الطوارئ مع الشدة والإجراءات
        """
        start_time = datetime.now()

        try:
            # Validate emergency type | التحقق من صحة نوع الطوارئ
            emergency_enum = EmergencyType(emergency_type.lower())

            # Get bilingual alert message | الحصول على رسالة تنبيه ثنائية اللغة
            alert_message = self.EMERGENCY_MESSAGES[emergency_enum]

            query = f"""EMERGENCY ASSESSMENT REQUIRED - {emergency_type.upper()}

Analyze the following field data and provide rapid assessment:
- Emergency severity level (LOW, MODERATE, HIGH, CRITICAL)
- Immediate risk factors
- Critical actions needed in next 1, 6, 24 hours
- Required resources
- Coordination needs with other agents

Field Data: {field_data}

RESPOND QUICKLY WITH ACTIONABLE GUIDANCE."""

            context = {
                "emergency_type": emergency_type,
                "field_data": field_data,
                "severity_override": severity,
                "alert_en": alert_message["en"],
                "alert_ar": alert_message["ar"],
                "task": "emergency_assessment",
                "response_time_target": self.RESPONSE_TIME_TARGET
            }

            # Fast assessment using LLM | تقييم سريع باستخدام LLM
            response = await self.think(query, context=context, use_rag=False)

            # Calculate response time | حساب وقت الاستجابة
            response_time = (datetime.now() - start_time).total_seconds()

            # Determine severity if not provided | تحديد الشدة إذا لم يتم توفيرها
            if not severity:
                severity = self._infer_severity(field_data, emergency_type)

            # Create emergency ID | إنشاء معرف الطوارئ
            emergency_id = f"{emergency_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # Track active emergency | تتبع الطوارئ النشطة
            self.active_emergencies[emergency_id] = {
                "type": emergency_type,
                "severity": severity,
                "started_at": datetime.now().isoformat(),
                "field_data": field_data,
                "status": "assessed"
            }

            logger.info(
                "emergency_assessed",
                emergency_id=emergency_id,
                emergency_type=emergency_type,
                severity=severity,
                response_time=response_time
            )

            return {
                "emergency_id": emergency_id,
                "emergency_type": emergency_type,
                "severity": severity,
                "alert_en": alert_message["en"],
                "alert_ar": alert_message["ar"],
                "assessment": response["response"],
                "response_time_seconds": response_time,
                "within_target": response_time < self.RESPONSE_TIME_TARGET,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error("emergency_assessment_failed", error=str(e))
            raise

    async def create_response_plan(
        self,
        emergency_type: str,
        assessment: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create comprehensive emergency response action plan
        إنشاء خطة عمل شاملة للاستجابة للطوارئ

        Args:
            emergency_type: Type of emergency | نوع الطوارئ
            assessment: Emergency assessment results | نتائج تقييم الطوارئ

        Returns:
            Detailed response plan with timeline | خطة استجابة مفصلة مع جدول زمني
        """
        query = f"""CREATE EMERGENCY RESPONSE PLAN - {emergency_type.upper()}

Based on the assessment, create a detailed action plan including:

1. IMMEDIATE ACTIONS (0-1 hours):
   - Critical interventions to prevent escalation
   - Emergency notifications and alerts
   - Resource mobilization

2. SHORT-TERM ACTIONS (1-24 hours):
   - Damage mitigation measures
   - Resource deployment
   - Monitoring protocols

3. MEDIUM-TERM ACTIONS (1-7 days):
   - Recovery strategies
   - Ongoing monitoring
   - Adaptive management

4. LONG-TERM ACTIONS (1-4 weeks):
   - Full recovery plan
   - Preventive measures for future
   - System improvements

For each action provide:
- Specific steps
- Required resources (people, equipment, materials, budget)
- Timeline and deadlines
- Success criteria
- Responsible parties
- Dependencies

Assessment Details: {assessment}"""

        context = {
            "emergency_type": emergency_type,
            "assessment": assessment,
            "task": "response_plan"
        }

        response = await self.think(query, context=context, use_rag=True)

        # Update emergency status | تحديث حالة الطوارئ
        emergency_id = assessment.get("emergency_id")
        if emergency_id and emergency_id in self.active_emergencies:
            self.active_emergencies[emergency_id]["status"] = "planned"
            self.active_emergencies[emergency_id]["plan_created_at"] = datetime.now().isoformat()

        logger.info("emergency_response_plan_created", emergency_id=emergency_id)

        return {
            "emergency_id": emergency_id,
            "plan": response["response"],
            "created_at": datetime.now().isoformat(),
        }

    async def prioritize_actions(
        self,
        actions: List[Dict[str, Any]],
        resources: Dict[str, Any],
        time_constraint: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Prioritize emergency actions based on resources and time
        تحديد أولويات إجراءات الطوارئ بناءً على الموارد والوقت

        Args:
            actions: List of potential actions | قائمة الإجراءات المحتملة
            resources: Available resources | الموارد المتاحة
            time_constraint: Time limit in hours | الحد الزمني بالساعات

        Returns:
            Prioritized action list | قائمة الإجراءات ذات الأولوية
        """
        query = f"""PRIORITIZE EMERGENCY ACTIONS

Given the following constraints, prioritize and optimize the action list:

Available Resources: {resources}
Time Constraint: {time_constraint} hours
Proposed Actions: {actions}

Provide:
1. Prioritized action list (highest to lowest priority)
2. Resource allocation for each action
3. Timeline optimization
4. Trade-offs and decisions made
5. Actions to defer or skip if necessary
6. Critical path analysis

Use these priority criteria:
- Life and crop safety (highest priority)
- Damage prevention and mitigation
- Resource efficiency
- Time sensitivity
- Cost-effectiveness
- Recovery impact"""

        context = {
            "actions": actions,
            "resources": resources,
            "time_constraint": time_constraint,
            "task": "action_prioritization"
        }

        response = await self.think(query, context=context, use_rag=False)

        logger.info(
            "actions_prioritized",
            num_actions=len(actions),
            time_constraint=time_constraint
        )

        return {
            "prioritized_actions": response["response"],
            "resource_allocation": resources,
            "time_constraint_hours": time_constraint,
            "timestamp": datetime.now().isoformat(),
        }

    async def coordinate_response(
        self,
        plan: Dict[str, Any],
        available_agents: List[str],
    ) -> Dict[str, Any]:
        """
        Coordinate emergency response with multiple specialized agents
        تنسيق الاستجابة للطوارئ مع وكلاء متخصصين متعددين

        Args:
            plan: Response plan to execute | خطة الاستجابة للتنفيذ
            available_agents: List of available agent types | قائمة أنواع الوكلاء المتاحة

        Returns:
            Coordination strategy with agent assignments | استراتيجية التنسيق مع تعيينات الوكلاء
        """
        query = f"""COORDINATE MULTI-AGENT EMERGENCY RESPONSE

Emergency Response Plan: {plan}
Available Specialized Agents: {available_agents}

Create coordination strategy:

1. AGENT ASSIGNMENTS:
   - Which agents to engage for which tasks
   - Irrigation Advisor: Water management emergencies
   - Pest Management: Pest outbreak control
   - Disease Expert: Disease epidemic containment
   - Soil Science: Flood/drought soil recovery
   - Field Analyst: Damage assessment
   - Ecological Expert: Environmental impact
   - Market Intelligence: Economic impact and insurance
   - Yield Predictor: Crop loss estimation

2. COORDINATION PROTOCOL:
   - Information sharing between agents
   - Decision-making hierarchy
   - Conflict resolution
   - Synchronization points

3. COMMUNICATION PLAN:
   - Reporting frequency
   - Escalation procedures
   - Stakeholder updates

4. SUCCESS METRICS:
   - Key performance indicators
   - Monitoring checkpoints
   - Coordination effectiveness measures"""

        context = {
            "plan": plan,
            "available_agents": available_agents,
            "task": "multi_agent_coordination"
        }

        response = await self.think(query, context=context, use_rag=False)

        logger.info(
            "multi_agent_coordination_created",
            num_agents=len(available_agents)
        )

        return {
            "coordination_strategy": response["response"],
            "engaged_agents": available_agents,
            "created_at": datetime.now().isoformat(),
        }

    async def monitor_recovery(
        self,
        field_id: str,
        emergency_type: str,
    ) -> Dict[str, Any]:
        """
        Monitor recovery progress after emergency
        مراقبة تقدم التعافي بعد الطوارئ

        Args:
            field_id: Field identifier | معرف الحقل
            emergency_type: Type of emergency | نوع الطوارئ

        Returns:
            Recovery status and recommendations | حالة التعافي والتوصيات
        """
        query = f"""MONITOR EMERGENCY RECOVERY - {emergency_type.upper()}

Field ID: {field_id}

Assess recovery progress:

1. RECOVERY STATUS:
   - Current field conditions vs. pre-emergency baseline
   - Recovery milestones achieved
   - Recovery timeline progress

2. ONGOING CHALLENGES:
   - Persistent issues
   - New complications
   - Resource gaps

3. ADAPTIVE RECOMMENDATIONS:
   - Adjustments to recovery plan
   - Additional interventions needed
   - Preventive measures

4. RECOVERY METRICS:
   - Crop health indicators
   - Soil condition recovery
   - Yield impact estimates
   - Cost of recovery vs. initial estimate

5. TIMELINE UPDATE:
   - Expected full recovery date
   - Next monitoring checkpoint"""

        context = {
            "field_id": field_id,
            "emergency_type": emergency_type,
            "task": "recovery_monitoring"
        }

        # Check for active emergency | التحقق من الطوارئ النشطة
        active_emergency = None
        for emer_id, emer_data in self.active_emergencies.items():
            if emergency_type in emer_id:
                active_emergency = emer_data
                break

        if active_emergency:
            context["emergency_data"] = active_emergency

        response = await self.think(query, context=context, use_rag=True)

        logger.info(
            "recovery_monitored",
            field_id=field_id,
            emergency_type=emergency_type
        )

        return {
            "field_id": field_id,
            "emergency_type": emergency_type,
            "recovery_status": response["response"],
            "monitored_at": datetime.now().isoformat(),
        }

    async def estimate_damage(
        self,
        emergency_type: str,
        affected_area: float,
        crop_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Estimate damage and losses from emergency
        تقدير الأضرار والخسائر من الطوارئ

        Args:
            emergency_type: Type of emergency | نوع الطوارئ
            affected_area: Affected area in hectares | المساحة المتضررة بالهكتار
            crop_data: Crop information and growth stage | معلومات المحاصيل ومرحلة النمو

        Returns:
            Damage estimation with financial impact | تقدير الأضرار مع التأثير المالي
        """
        query = f"""ESTIMATE EMERGENCY DAMAGE - {emergency_type.upper()}

Affected Area: {affected_area} hectares
Crop Data: {crop_data}

Provide comprehensive damage estimate:

1. CROP DAMAGE ASSESSMENT:
   - Percentage of crop affected (0-100%)
   - Damage severity by growth stage
   - Irreversible vs. recoverable damage
   - Quality impact on marketable yield

2. YIELD LOSS ESTIMATE:
   - Expected yield without emergency
   - Estimated yield after damage
   - Percentage yield loss
   - Quality degradation impact

3. FINANCIAL IMPACT:
   - Direct crop losses (SAR/USD)
   - Recovery costs
   - Lost revenue from reduced yield
   - Long-term soil/field impacts
   - Total economic impact

4. RECOVERY POTENTIAL:
   - Salvageable crop percentage
   - Recovery time estimate
   - Recovery investment needed
   - Expected recovery success rate

5. COMPARATIVE ANALYSIS:
   - Similar historical emergencies
   - Typical damage ranges
   - Recovery success rates"""

        context = {
            "emergency_type": emergency_type,
            "affected_area": affected_area,
            "crop_data": crop_data,
            "task": "damage_estimation"
        }

        response = await self.think(query, context=context, use_rag=True)

        logger.info(
            "damage_estimated",
            emergency_type=emergency_type,
            affected_area=affected_area
        )

        return {
            "emergency_type": emergency_type,
            "affected_area_hectares": affected_area,
            "damage_estimate": response["response"],
            "estimated_at": datetime.now().isoformat(),
        }

    async def insurance_documentation(
        self,
        emergency_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate insurance documentation for claims
        إنشاء وثائق التأمين للمطالبات

        Args:
            emergency_data: Complete emergency event data | بيانات حدث الطوارئ الكاملة

        Returns:
            Insurance documentation package | حزمة وثائق التأمين
        """
        query = f"""GENERATE INSURANCE DOCUMENTATION

Emergency Event Data: {emergency_data}

Create comprehensive insurance claim documentation:

1. INCIDENT REPORT:
   - Date and time of emergency onset
   - Emergency type and severity
   - Affected area and crops
   - Immediate response actions taken
   - Timeline of events

2. DAMAGE DOCUMENTATION:
   - Detailed damage assessment
   - Before/after comparisons
   - Photographic evidence requirements
   - Sensor data and measurements
   - Third-party verification needs

3. FINANCIAL DOCUMENTATION:
   - Itemized damage costs
   - Recovery expenses
   - Lost revenue calculations
   - Supporting receipts and invoices
   - Market price references

4. PREVENTIVE MEASURES TAKEN:
   - Emergency preparedness evidence
   - Risk mitigation efforts
   - Compliance with best practices
   - Historical maintenance records

5. EXPERT ASSESSMENTS:
   - Agricultural expert opinions
   - Technical reports
   - Weather service confirmations
   - Soil/crop analysis results

6. CLAIM REQUIREMENTS:
   - Required forms and documents
   - Submission timeline
   - Supporting evidence checklist
   - Follow-up procedures

Provide documentation in both Arabic and English for local and international insurers."""

        context = {
            "emergency_data": emergency_data,
            "task": "insurance_documentation"
        }

        response = await self.think(query, context=context, use_rag=False)

        logger.info("insurance_documentation_generated")

        return {
            "insurance_package": response["response"],
            "emergency_reference": emergency_data.get("emergency_id"),
            "generated_at": datetime.now().isoformat(),
            "languages": ["English", "Arabic"],
        }

    async def lessons_learned(
        self,
        emergency_id: str,
    ) -> Dict[str, Any]:
        """
        Post-emergency analysis and lessons learned
        التحليل بعد الطوارئ والدروس المستفادة

        Args:
            emergency_id: Emergency event identifier | معرف حدث الطوارئ

        Returns:
            Lessons learned and improvement recommendations | الدروس المستفادة وتوصيات التحسين
        """
        # Retrieve emergency data | استرجاع بيانات الطوارئ
        emergency_data = self.active_emergencies.get(emergency_id, {})

        query = f"""POST-EMERGENCY ANALYSIS - LESSONS LEARNED

Emergency ID: {emergency_id}
Emergency Data: {emergency_data}

Conduct comprehensive post-emergency analysis:

1. RESPONSE EFFECTIVENESS:
   - What worked well
   - What didn't work
   - Response time analysis
   - Resource utilization efficiency
   - Communication effectiveness

2. DAMAGE ANALYSIS:
   - Actual vs. estimated damage
   - Factors that worsened damage
   - Factors that mitigated damage
   - Unexpected complications

3. COORDINATION ASSESSMENT:
   - Multi-agent coordination effectiveness
   - Information sharing quality
   - Decision-making process
   - Stakeholder engagement

4. RECOVERY INSIGHTS:
   - Recovery timeline accuracy
   - Cost overruns or savings
   - Adaptive measures that helped
   - Ongoing challenges

5. PREVENTION OPPORTUNITIES:
   - Early warning signals missed
   - Preventive measures needed
   - Infrastructure improvements
   - Monitoring enhancements

6. KNOWLEDGE TRANSFER:
   - Key takeaways for future emergencies
   - Training needs identified
   - Protocol improvements
   - Best practices to codify

7. RECOMMENDATIONS:
   - Immediate system improvements
   - Long-term preparedness enhancements
   - Resource allocation changes
   - Technology/tool investments

Document for knowledge base integration and future emergency preparedness."""

        context = {
            "emergency_id": emergency_id,
            "emergency_data": emergency_data,
            "task": "lessons_learned"
        }

        response = await self.think(query, context=context, use_rag=True)

        # Mark emergency as analyzed | وضع علامة على الطوارئ كمحللة
        if emergency_id in self.active_emergencies:
            self.active_emergencies[emergency_id]["status"] = "analyzed"
            self.active_emergencies[emergency_id]["analyzed_at"] = datetime.now().isoformat()

        logger.info("lessons_learned_documented", emergency_id=emergency_id)

        return {
            "emergency_id": emergency_id,
            "lessons_learned": response["response"],
            "analyzed_at": datetime.now().isoformat(),
            "status": "complete",
        }

    def _infer_severity(
        self,
        field_data: Dict[str, Any],
        emergency_type: str,
    ) -> str:
        """
        Infer emergency severity from field data
        استنتاج شدة الطوارئ من بيانات الحقل

        Args:
            field_data: Field sensor and condition data | بيانات المستشعر وحالة الحقل
            emergency_type: Type of emergency | نوع الطوارئ

        Returns:
            Severity level | مستوى الشدة
        """
        # Simple heuristic-based severity inference
        # استنتاج الشدة البسيط القائم على الاستدلال

        # Default to MODERATE | افتراضي إلى متوسط
        severity = SeverityLevel.MODERATE.value

        try:
            # Drought severity indicators | مؤشرات شدة الجفاف
            if emergency_type == EmergencyType.DROUGHT.value:
                soil_moisture = field_data.get("soil_moisture", 50)
                if soil_moisture < 10:
                    severity = SeverityLevel.CRITICAL.value
                elif soil_moisture < 20:
                    severity = SeverityLevel.HIGH.value
                elif soil_moisture < 30:
                    severity = SeverityLevel.MODERATE.value
                else:
                    severity = SeverityLevel.LOW.value

            # Flood severity indicators | مؤشرات شدة الفيضان
            elif emergency_type == EmergencyType.FLOOD.value:
                water_level = field_data.get("water_level_cm", 0)
                if water_level > 30:
                    severity = SeverityLevel.CRITICAL.value
                elif water_level > 15:
                    severity = SeverityLevel.HIGH.value
                elif water_level > 5:
                    severity = SeverityLevel.MODERATE.value
                else:
                    severity = SeverityLevel.LOW.value

            # Temperature-based emergencies | الطوارئ القائمة على درجة الحرارة
            elif emergency_type in [EmergencyType.FROST.value, EmergencyType.HEAT_WAVE.value]:
                temp = field_data.get("temperature", 25)
                if emergency_type == EmergencyType.FROST.value:
                    if temp < -5:
                        severity = SeverityLevel.CRITICAL.value
                    elif temp < 0:
                        severity = SeverityLevel.HIGH.value
                    elif temp < 5:
                        severity = SeverityLevel.MODERATE.value
                else:  # HEAT_WAVE
                    if temp > 45:
                        severity = SeverityLevel.CRITICAL.value
                    elif temp > 40:
                        severity = SeverityLevel.HIGH.value
                    elif temp > 35:
                        severity = SeverityLevel.MODERATE.value

            # Pest/disease outbreak severity | شدة تفشي الآفات/الأمراض
            elif emergency_type in [EmergencyType.PEST_OUTBREAK.value, EmergencyType.DISEASE_EPIDEMIC.value]:
                infestation_percent = field_data.get("infestation_percentage", 25)
                if infestation_percent > 70:
                    severity = SeverityLevel.CRITICAL.value
                elif infestation_percent > 40:
                    severity = SeverityLevel.HIGH.value
                elif infestation_percent > 20:
                    severity = SeverityLevel.MODERATE.value
                else:
                    severity = SeverityLevel.LOW.value

        except Exception as e:
            logger.warning("severity_inference_failed", error=str(e))
            severity = SeverityLevel.MODERATE.value

        return severity

    def get_active_emergencies(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active emergencies
        الحصول على جميع الطوارئ النشطة

        Returns:
            Dictionary of active emergencies | قاموس الطوارئ النشطة
        """
        return self.active_emergencies

    def clear_emergency(self, emergency_id: str) -> bool:
        """
        Clear/resolve an emergency from active tracking
        مسح/حل طوارئ من التتبع النشط

        Args:
            emergency_id: Emergency identifier | معرف الطوارئ

        Returns:
            Success status | حالة النجاح
        """
        if emergency_id in self.active_emergencies:
            self.active_emergencies[emergency_id]["status"] = "resolved"
            self.active_emergencies[emergency_id]["resolved_at"] = datetime.now().isoformat()
            logger.info("emergency_resolved", emergency_id=emergency_id)
            return True
        return False
