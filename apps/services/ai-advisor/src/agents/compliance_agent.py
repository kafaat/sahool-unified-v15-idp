"""
Compliance Agent
وكيل الامتثال

Specialized agent for certification compliance (GlobalGAP, Organic, etc.).
وكيل متخصص في الامتثال للشهادات (GlobalGAP، العضوية، إلخ).
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
from langchain_core.tools import Tool

from .base_agent import BaseAgent


class CertificationStandard(str, Enum):
    """
    Supported certification standards
    معايير الشهادات المدعومة
    """
    GLOBALGAP_IFA_V6 = "GLOBALGAP_IFA_V6"  # GlobalGAP Integrated Farm Assurance
    ORGANIC_EU = "ORGANIC_EU"  # EU Organic certification
    ORGANIC_USDA = "ORGANIC_USDA"  # USDA Organic
    SAUDI_GAP = "SAUDI_GAP"  # Saudi GAP standards
    ISO_22000 = "ISO_22000"  # Food safety management


class ControlPointCategory(str, Enum):
    """
    Control point categories for certification
    فئات نقاط المراقبة للشهادة
    """
    SITE_MANAGEMENT = "SITE_MANAGEMENT"  # إدارة الموقع
    RECORD_KEEPING = "RECORD_KEEPING"  # حفظ السجلات
    TRACEABILITY = "TRACEABILITY"  # التتبع
    IPM = "IPM"  # الإدارة المتكاملة للآفات
    FERTILIZER_USE = "FERTILIZER_USE"  # استخدام الأسمدة
    IRRIGATION = "IRRIGATION"  # الري
    HARVEST = "HARVEST"  # الحصاد
    POST_HARVEST = "POST_HARVEST"  # ما بعد الحصاد
    WORKER_SAFETY = "WORKER_SAFETY"  # سلامة العمال
    ENVIRONMENT = "ENVIRONMENT"  # البيئة
    WASTE_MANAGEMENT = "WASTE_MANAGEMENT"  # إدارة النفايات


class ComplianceAgent(BaseAgent):
    """
    Compliance Agent for certification standards (GlobalGAP, Organic, etc.)
    وكيل الامتثال لمعايير الشهادات (GlobalGAP، العضوية، إلخ)

    Specializes in:
    - Real-time compliance checking for farm operations
    - GlobalGAP IFA v6 control points
    - Organic certification requirements (EU, USDA)
    - Saudi GAP and ISO 22000 standards
    - Audit readiness assessment
    - Documentation management
    - Input validation (pesticides, fertilizers)
    - Waiting period calculations
    - Certification pathway planning
    - Non-compliance reporting

    متخصص في:
    - فحص الامتثال في الوقت الفعلي لعمليات المزرعة
    - نقاط المراقبة GlobalGAP IFA v6
    - متطلبات الشهادة العضوية (EU، USDA)
    - معايير Saudi GAP و ISO 22000
    - تقييم الجاهزية للتدقيق
    - إدارة الوثائق
    - التحقق من صحة المدخلات (المبيدات، الأسمدة)
    - حساب فترات الانتظار
    - تخطيط مسار الشهادة
    - الإبلاغ عن عدم الامتثال
    """

    # GlobalGAP control points mapping
    # خريطة نقاط المراقبة GlobalGAP
    GLOBALGAP_CONTROL_POINTS = {
        ControlPointCategory.SITE_MANAGEMENT: [
            "AF.1.1.1 - Site history and risk assessment documented",
            "AF.1.2.1 - Soil maps and management plans available",
            "AF.1.3.1 - Previous land use documented (3 years)",
            "AF.2.1.1 - Conservation of existing natural vegetation",
        ],
        ControlPointCategory.RECORD_KEEPING: [
            "AF.3.1.1 - All records kept for minimum 2 years",
            "AF.3.2.1 - Traceability system implemented",
            "AF.3.3.1 - Internal self-assessment records",
            "AF.3.4.1 - Complaint handling procedures documented",
        ],
        ControlPointCategory.TRACEABILITY: [
            "AF.4.1.1 - Lot identification system in place",
            "AF.4.2.1 - Product flow diagram documented",
            "AF.4.3.1 - Mass balance records maintained",
            "AF.4.4.1 - Harvest and post-harvest traceability",
        ],
        ControlPointCategory.IPM: [
            "CB.5.1.1 - IPM plan documented and implemented",
            "CB.5.2.1 - Pest monitoring records maintained",
            "CB.5.3.1 - Economic threshold levels defined",
            "CB.5.4.1 - Beneficial organisms promoted",
            "CB.5.5.1 - Pesticide use as last resort only",
        ],
        ControlPointCategory.FERTILIZER_USE: [
            "CB.6.1.1 - Fertilization plan based on soil/leaf analysis",
            "CB.6.2.1 - Application records with dates and quantities",
            "CB.6.3.1 - Organic matter incorporation plan",
            "CB.6.4.1 - Nutrient management to prevent pollution",
        ],
        ControlPointCategory.IRRIGATION: [
            "CB.7.1.1 - Water source quality tested annually",
            "CB.7.2.1 - Irrigation scheduling based on crop needs",
            "CB.7.3.1 - Water use efficiency measures",
            "CB.7.4.1 - Drainage and runoff management",
        ],
        ControlPointCategory.HARVEST: [
            "CB.8.1.1 - Hygiene procedures for harvest workers",
            "CB.8.2.1 - Harvest containers cleaned and maintained",
            "CB.8.3.1 - Field hygiene standards enforced",
            "CB.8.4.1 - Pre-harvest interval respected",
        ],
        ControlPointCategory.POST_HARVEST: [
            "FV.9.1.1 - Packhouse hygiene program implemented",
            "FV.9.2.1 - Temperature monitoring for storage",
            "FV.9.3.1 - Pest control in storage facilities",
            "FV.9.4.1 - Cleaning and sanitation records",
        ],
        ControlPointCategory.WORKER_SAFETY: [
            "WH.1.1.1 - Risk assessment for all activities",
            "WH.2.1.1 - PPE provided and used",
            "WH.3.1.1 - Training records for all workers",
            "WH.4.1.1 - First aid facilities available",
            "WH.5.1.1 - No child labor policy enforced",
        ],
        ControlPointCategory.ENVIRONMENT: [
            "ENV.1.1.1 - Environmental impact assessment conducted",
            "ENV.2.1.1 - Energy efficiency measures implemented",
            "ENV.3.1.1 - Biodiversity conservation plan",
            "ENV.4.1.1 - Soil conservation practices",
        ],
        ControlPointCategory.WASTE_MANAGEMENT: [
            "ENV.5.1.1 - Waste management plan documented",
            "ENV.5.2.1 - Recycling program implemented",
            "ENV.5.3.1 - Hazardous waste disposal records",
            "ENV.5.4.1 - Empty pesticide container management",
        ],
    }

    # Organic certification prohibited substances
    # المواد المحظورة في الشهادة العضوية
    ORGANIC_PROHIBITED_INPUTS = {
        "pesticides": [
            "synthetic chemical pesticides",
            "organophosphates",
            "neonicotinoids",
            "synthetic pyrethroids",
            "GMO-derived products",
        ],
        "fertilizers": [
            "synthetic nitrogen fertilizers",
            "urea",
            "ammonium nitrate",
            "phosphate rock (non-organic)",
            "potassium chloride (non-organic)",
        ],
        "growth_regulators": [
            "synthetic hormones",
            "synthetic gibberellins",
            "ethylene (synthetic)",
        ],
    }

    # Organic approved inputs
    # المدخلات المعتمدة للزراعة العضوية
    ORGANIC_APPROVED_INPUTS = {
        "pesticides": [
            "neem oil",
            "pyrethrum (natural)",
            "Bacillus thuringiensis (Bt)",
            "kaolin clay",
            "horticultural oils",
            "sulfur",
            "copper compounds (limited use)",
            "beneficial insects",
        ],
        "fertilizers": [
            "compost (organic)",
            "animal manure (composted)",
            "green manure",
            "bone meal",
            "blood meal",
            "fish emulsion",
            "seaweed extracts",
            "rock phosphate (natural)",
        ],
    }

    # Waiting periods for organic certification (days)
    # فترات الانتظار للشهادة العضوية (أيام)
    ORGANIC_WAITING_PERIODS = {
        "ORGANIC_EU": {
            "annual_crops": 730,  # 2 years
            "perennial_crops": 1095,  # 3 years
            "grassland": 730,  # 2 years
        },
        "ORGANIC_USDA": {
            "annual_crops": 1095,  # 3 years
            "perennial_crops": 1095,  # 3 years
            "grassland": 1095,  # 3 years
        },
    }

    def __init__(
        self,
        tools: Optional[List[Tool]] = None,
        retriever: Optional[Any] = None,
    ):
        """
        Initialize Compliance Agent
        تهيئة وكيل الامتثال
        """
        super().__init__(
            name="compliance_agent",
            role="Certification Compliance Specialist",
            tools=tools,
            retriever=retriever,
        )

    def get_system_prompt(self) -> str:
        """
        Get system prompt for Compliance Agent
        الحصول على موجه النظام لوكيل الامتثال
        """
        return """You are an expert Certification Compliance Specialist with deep knowledge of agricultural certification standards.

Your expertise includes:
- GlobalGAP Integrated Farm Assurance (IFA) v6 standards and control points
- EU Organic Regulation (EC) 834/2007 and 889/2008
- USDA National Organic Program (NOP) standards
- Saudi GAP certification requirements
- ISO 22000 food safety management systems
- Audit preparation and documentation management
- Input validation (pesticides, fertilizers, amendments)
- Traceability and record-keeping requirements
- Worker safety and welfare standards
- Environmental compliance and sustainability

When checking compliance:
1. Real-time compliance verification:
   - Analyze proposed action against certification requirements
   - Identify potential violations before they occur
   - Provide specific control point references
   - Suggest compliant alternatives
   - Calculate risk levels (critical, major, minor)

2. Control points assessment:
   - Map activities to specific control points
   - Distinguish between mandatory and recommended practices
   - Provide evidence requirements for each control point
   - Explain scoring criteria (full compliance, minor deficiency, major deficiency, non-compliance)

3. Audit readiness evaluation:
   - Review documentation completeness
   - Identify gaps in records
   - Assess implementation level of procedures
   - Calculate readiness score
   - Prioritize improvement areas

4. Documentation management:
   - List required documents for certification
   - Specify retention periods
   - Provide templates and examples
   - Track document status
   - Generate missing document alerts

5. Input validation:
   - Check if inputs are allowed under certification
   - Verify organic status of products
   - Calculate pre-harvest intervals (PHI)
   - Assess environmental impact
   - Recommend compliant alternatives

6. Waiting period calculations:
   - Calculate conversion period completion
   - Track prohibited substance applications
   - Determine eligibility dates
   - Monitor parallel production requirements

7. Certification roadmap:
   - Assess current compliance level
   - Create step-by-step implementation plan
   - Estimate timeline to certification
   - Identify required investments
   - Prioritize actions by impact

8. Non-compliance management:
   - Document non-conformities
   - Assess severity and impact
   - Recommend corrective actions
   - Set deadlines for remediation
   - Track correction verification

Always provide:
- Specific control point references (e.g., AF.3.1.1)
- Clear compliance status (compliant, non-compliant, needs verification)
- Practical corrective actions
- Timeline estimates
- Risk assessment (critical, high, medium, low)
- Both Arabic and English explanations

أنت خبير متخصص في الامتثال للشهادات الزراعية مع معرفة عميقة بمعايير الشهادات.

خبرتك تشمل:
- معايير GlobalGAP IFA v6 ونقاط المراقبة
- لائحة الاتحاد الأوروبي العضوية (EC) 834/2007 و 889/2008
- معايير البرنامج العضوي الوطني USDA (NOP)
- متطلبات شهادة Saudi GAP
- أنظمة إدارة سلامة الغذاء ISO 22000
- إعداد التدقيق وإدارة الوثائق
- التحقق من صحة المدخلات
- متطلبات التتبع وحفظ السجلات
- معايير سلامة ورفاهية العمال
- الامتثال البيئي والاستدامة

قدم تقييمات دقيقة مع مراجع محددة وإجراءات تصحيحية عملية."""

    async def check_compliance(
        self,
        action: Dict[str, Any],
        certification: CertificationStandard,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Check if a proposed action complies with certification requirements
        التحقق مما إذا كان الإجراء المقترح يتوافق مع متطلبات الشهادة

        Args:
            action: Proposed farm action (e.g., pesticide application, harvest)
                الإجراء المقترح للمزرعة
            certification: Certification standard to check against
                معيار الشهادة للتحقق منه
            context: Additional context (crop, stage, location, etc.)
                سياق إضافي

        Returns:
            Compliance check result with status and recommendations
            نتيجة فحص الامتثال مع الحالة والتوصيات
        """
        query = f"""Check compliance of the following action with {certification.value} certification:
Action: {action.get('type', 'Unknown')} - {action.get('description', '')}

Provide:
1. Compliance status (compliant/non-compliant/needs verification)
2. Relevant control point references
3. Risk level if non-compliant
4. Specific concerns or violations
5. Recommended corrective actions
6. Compliant alternatives if applicable"""

        context_dict = context or {}
        context_dict.update({
            "action": action,
            "certification": certification.value,
            "task": "compliance_check",
            "control_points": self._get_relevant_control_points(
                action.get("type"), certification
            ),
        })

        return await self.think(query, context=context_dict, use_rag=True)

    async def get_control_points(
        self,
        certification: CertificationStandard,
        category: Optional[ControlPointCategory] = None,
    ) -> Dict[str, Any]:
        """
        Get control points for a certification standard
        الحصول على نقاط المراقبة لمعيار الشهادة

        Args:
            certification: Certification standard
                معيار الشهادة
            category: Optional category filter
                فئة اختيارية للتصفية

        Returns:
            List of control points with details
            قائمة نقاط المراقبة مع التفاصيل
        """
        if certification == CertificationStandard.GLOBALGAP_IFA_V6:
            if category:
                control_points = {
                    category.value: self.GLOBALGAP_CONTROL_POINTS.get(category, [])
                }
            else:
                control_points = self.GLOBALGAP_CONTROL_POINTS
        else:
            control_points = {}

        query = f"""Provide detailed information about control points for {certification.value}
{f'in category {category.value}' if category else 'all categories'}.

For each control point, explain:
1. Requirement description
2. Compliance level (mandatory/recommended)
3. Evidence needed
4. Common non-conformities
5. Best practices for compliance"""

        context = {
            "certification": certification.value,
            "category": category.value if category else "all",
            "control_points": control_points,
            "task": "control_points_details",
        }

        return await self.think(query, context=context, use_rag=True)

    async def audit_readiness(
        self,
        farm_id: str,
        certification: CertificationStandard,
        farm_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Assess farm's readiness for certification audit
        تقييم جاهزية المزرعة لتدقيق الشهادة

        Args:
            farm_id: Farm identifier
                معرف المزرعة
            certification: Target certification
                الشهادة المستهدفة
            farm_data: Farm operations and documentation data
                بيانات عمليات المزرعة والوثائق

        Returns:
            Audit readiness assessment with score and gaps
            تقييم الجاهزية للتدقيق مع النتيجة والفجوات
        """
        query = f"""Assess audit readiness for farm {farm_id} for {certification.value} certification.

Evaluate:
1. Documentation completeness (%)
2. Implementation of required procedures
3. Record-keeping quality
4. Critical non-conformities
5. Major gaps requiring immediate attention
6. Minor improvements needed
7. Overall readiness score (0-100)
8. Estimated time to audit-ready status
9. Priority action plan

Provide a detailed gap analysis and remediation roadmap."""

        context = {
            "farm_id": farm_id,
            "certification": certification.value,
            "farm_data": farm_data or {},
            "task": "audit_readiness",
            "required_categories": list(ControlPointCategory),
        }

        return await self.think(query, context=context, use_rag=True)

    async def generate_checklist(
        self,
        certification: CertificationStandard,
        farm_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate customized audit preparation checklist
        إنشاء قائمة مراجعة مخصصة لإعداد التدقيق

        Args:
            certification: Certification standard
                معيار الشهادة
            farm_data: Farm information (crops, operations, etc.)
                معلومات المزرعة

        Returns:
            Detailed checklist with tasks and priorities
            قائمة مراجعة مفصلة مع المهام والأولويات
        """
        query = f"""Generate a comprehensive audit preparation checklist for {certification.value} certification.

The checklist should include:
1. Documentation to prepare (by category)
2. Records to collect and organize
3. Procedures to implement
4. Physical preparations needed
5. Training requirements
6. Timeline for each task
7. Priority level (critical/high/medium/low)
8. Responsible party suggestions
9. Verification methods

Organize by control point category and prioritize by audit impact."""

        context = {
            "certification": certification.value,
            "farm_data": farm_data,
            "task": "checklist_generation",
            "control_point_categories": [cat.value for cat in ControlPointCategory],
        }

        return await self.think(query, context=context, use_rag=True)

    async def track_documentation(
        self,
        farm_id: str,
        certification: CertificationStandard,
        current_docs: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Track required documentation status
        تتبع حالة الوثائق المطلوبة

        Args:
            farm_id: Farm identifier
                معرف المزرعة
            certification: Certification standard
                معيار الشهادة
            current_docs: List of currently available documents
                قائمة الوثائق المتاحة حالياً

        Returns:
            Documentation status report with missing items
            تقرير حالة الوثائق مع العناصر المفقودة
        """
        query = f"""Track documentation requirements for {certification.value} certification.

Analyze:
1. Required documents list (comprehensive)
2. Current documentation status
3. Missing documents (critical vs. non-critical)
4. Document quality assessment
5. Retention period compliance
6. Document organization recommendations
7. Templates needed
8. Next review dates

Provide a status dashboard and action items."""

        context = {
            "farm_id": farm_id,
            "certification": certification.value,
            "current_docs": current_docs or [],
            "task": "documentation_tracking",
        }

        return await self.think(query, context=context, use_rag=True)

    async def validate_input(
        self,
        input_type: str,
        product: str,
        certification: CertificationStandard,
        additional_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Validate if an input (pesticide, fertilizer, etc.) is compliant
        التحقق مما إذا كان المدخل (مبيد، سماد، إلخ) متوافقاً

        Args:
            input_type: Type of input (pesticide, fertilizer, amendment, etc.)
                نوع المدخل
            product: Product name or active ingredient
                اسم المنتج أو المادة الفعالة
            certification: Certification standard
                معيار الشهادة
            additional_info: Additional product information
                معلومات إضافية عن المنتج

        Returns:
            Validation result with approval status and alternatives
            نتيجة التحقق مع حالة الموافقة والبدائل
        """
        # Check against prohibited/approved lists
        # التحقق من قوائم المحظور/المسموح
        is_prohibited = False
        is_approved = False

        if certification in [CertificationStandard.ORGANIC_EU, CertificationStandard.ORGANIC_USDA]:
            prohibited_list = self.ORGANIC_PROHIBITED_INPUTS.get(input_type + "s", [])
            approved_list = self.ORGANIC_APPROVED_INPUTS.get(input_type + "s", [])

            product_lower = product.lower()
            is_prohibited = any(
                prohibited.lower() in product_lower for prohibited in prohibited_list
            )
            is_approved = any(
                approved.lower() in product_lower for approved in approved_list
            )

        query = f"""Validate the following input for {certification.value} certification:
Input Type: {input_type}
Product: {product}

Provide:
1. Approval status (approved/prohibited/restricted/needs verification)
2. Specific regulations or restrictions
3. Usage conditions if approved
4. Pre-harvest interval (PHI) requirements
5. Application restrictions
6. Maximum residue limits (MRL)
7. Compliant alternatives if prohibited
8. Documentation requirements for use

Be specific about any limitations or conditions."""

        context = {
            "input_type": input_type,
            "product": product,
            "certification": certification.value,
            "additional_info": additional_info or {},
            "is_prohibited": is_prohibited,
            "is_approved": is_approved,
            "task": "input_validation",
        }

        return await self.think(query, context=context, use_rag=True)

    async def calculate_waiting_period(
        self,
        product: str,
        application_date: datetime,
        certification: CertificationStandard,
        crop_type: str = "annual_crops",
    ) -> Dict[str, Any]:
        """
        Calculate waiting period for organic certification
        حساب فترة الانتظار للشهادة العضوية

        Args:
            product: Product applied (pesticide, fertilizer, etc.)
                المنتج المطبق
            application_date: Date of last prohibited substance application
                تاريخ آخر تطبيق لمادة محظورة
            certification: Target organic certification
                الشهادة العضوية المستهدفة
            crop_type: Type of crop (annual, perennial, grassland)
                نوع المحصول

        Returns:
            Waiting period calculation with eligibility date
            حساب فترة الانتظار مع تاريخ الأهلية
        """
        # Get waiting period in days
        # الحصول على فترة الانتظار بالأيام
        waiting_days = 0
        if certification in [CertificationStandard.ORGANIC_EU, CertificationStandard.ORGANIC_USDA]:
            periods = self.ORGANIC_WAITING_PERIODS.get(certification.value, {})
            waiting_days = periods.get(crop_type, 730)

        # Calculate eligibility date
        # حساب تاريخ الأهلية
        eligibility_date = application_date + timedelta(days=waiting_days)
        days_remaining = (eligibility_date - datetime.now()).days

        query = f"""Calculate the organic conversion waiting period:
Product Applied: {product}
Last Application Date: {application_date.strftime('%Y-%m-%d')}
Certification: {certification.value}
Crop Type: {crop_type}

Calculated Waiting Period: {waiting_days} days
Eligibility Date: {eligibility_date.strftime('%Y-%m-%d')}
Days Remaining: {max(0, days_remaining)} days

Provide:
1. Confirmation of waiting period calculation
2. Requirements during conversion period
3. Allowed and prohibited practices
4. Documentation needed for conversion
5. Parallel production rules if applicable
6. Steps to maintain organic status
7. Monitoring and record-keeping requirements"""

        context = {
            "product": product,
            "application_date": application_date.isoformat(),
            "certification": certification.value,
            "crop_type": crop_type,
            "waiting_days": waiting_days,
            "eligibility_date": eligibility_date.isoformat(),
            "days_remaining": max(0, days_remaining),
            "task": "waiting_period_calculation",
        }

        return await self.think(query, context=context, use_rag=True)

    async def certification_roadmap(
        self,
        farm_data: Dict[str, Any],
        target_certification: CertificationStandard,
        current_practices: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a roadmap to achieve certification
        إنشاء خريطة طريق لتحقيق الشهادة

        Args:
            farm_data: Current farm information
                معلومات المزرعة الحالية
            target_certification: Desired certification
                الشهادة المرغوبة
            current_practices: Current farming practices
                الممارسات الزراعية الحالية

        Returns:
            Step-by-step certification roadmap with timeline
            خريطة طريق الشهادة خطوة بخطوة مع الجدول الزمني
        """
        query = f"""Create a comprehensive roadmap for achieving {target_certification.value} certification.

Provide:
1. Current compliance assessment
   - Strengths and existing compliant practices
   - Major gaps and deficiencies
   - Critical non-conformities to address

2. Phased implementation plan
   - Phase 1: Critical requirements (Month 1-3)
   - Phase 2: Major requirements (Month 4-6)
   - Phase 3: Minor requirements (Month 7-9)
   - Phase 4: Final preparation (Month 10-12)

3. Required investments
   - Infrastructure improvements
   - Equipment purchases
   - Training programs
   - Documentation systems
   - Estimated costs

4. Training needs
   - Worker training topics
   - Management training
   - Specialist consultations needed

5. Documentation development
   - Policies and procedures to write
   - Record-keeping systems to implement
   - Templates to create

6. Timeline to certification
   - Conversion period if applicable
   - Implementation milestones
   - Internal audit schedule
   - Target certification audit date

7. Success metrics
   - KPIs to track progress
   - Milestone completion targets
   - Budget adherence

8. Risk mitigation
   - Potential obstacles
   - Contingency plans
   - Support resources needed

Prioritize actions by impact and feasibility."""

        context = {
            "farm_data": farm_data,
            "target_certification": target_certification.value,
            "current_practices": current_practices or {},
            "task": "certification_roadmap",
            "control_point_categories": [cat.value for cat in ControlPointCategory],
        }

        return await self.think(query, context=context, use_rag=True)

    async def non_compliance_report(
        self,
        farm_id: str,
        issues: List[Dict[str, Any]],
        certification: CertificationStandard,
    ) -> Dict[str, Any]:
        """
        Generate non-compliance report with corrective actions
        إنشاء تقرير عدم الامتثال مع الإجراءات التصحيحية

        Args:
            farm_id: Farm identifier
                معرف المزرعة
            issues: List of non-compliance issues identified
                قائمة مشكلات عدم الامتثال المحددة
            certification: Certification standard
                معيار الشهادة

        Returns:
            Comprehensive non-compliance report
            تقرير شامل لعدم الامتثال
        """
        query = f"""Generate a comprehensive non-compliance report for farm {farm_id} regarding {certification.value} certification.

Analyze the following issues and provide:

1. Non-conformity classification
   - Critical (immediate action required)
   - Major (significant impact on certification)
   - Minor (low impact but needs correction)

2. For each issue:
   - Control point reference
   - Description of non-conformity
   - Evidence of non-compliance
   - Impact assessment
   - Root cause analysis
   - Corrective action required
   - Preventive measures
   - Deadline for correction
   - Verification method
   - Responsible party

3. Overall impact assessment
   - Certification status (at risk/delayed/minor impact)
   - Estimated delay if critical issues not resolved
   - Cost of corrections

4. Corrective Action Plan
   - Immediate actions (within 7 days)
   - Short-term corrections (within 30 days)
   - Long-term improvements (within 90 days)
   - Resource requirements

5. Verification and follow-up
   - Verification schedule
   - Documentation requirements
   - Internal audit plan
   - Management review process

Prioritize by severity and certification impact."""

        context = {
            "farm_id": farm_id,
            "issues": issues,
            "certification": certification.value,
            "task": "non_compliance_report",
            "num_issues": len(issues),
        }

        return await self.think(query, context=context, use_rag=True)

    def _get_relevant_control_points(
        self,
        action_type: Optional[str],
        certification: CertificationStandard,
    ) -> List[str]:
        """
        Get relevant control points for an action type
        الحصول على نقاط المراقبة ذات الصلة لنوع الإجراء

        Args:
            action_type: Type of farm action
                نوع إجراء المزرعة
            certification: Certification standard
                معيار الشهادة

        Returns:
            List of relevant control points
            قائمة نقاط المراقبة ذات الصلة
        """
        if certification != CertificationStandard.GLOBALGAP_IFA_V6:
            return []

        # Map action types to control point categories
        # ربط أنواع الإجراءات بفئات نقاط المراقبة
        action_category_map = {
            "pesticide_application": ControlPointCategory.IPM,
            "fertilizer_application": ControlPointCategory.FERTILIZER_USE,
            "irrigation": ControlPointCategory.IRRIGATION,
            "harvest": ControlPointCategory.HARVEST,
            "post_harvest": ControlPointCategory.POST_HARVEST,
            "worker_activity": ControlPointCategory.WORKER_SAFETY,
            "waste_disposal": ControlPointCategory.WASTE_MANAGEMENT,
        }

        category = action_category_map.get(action_type)
        if category:
            return self.GLOBALGAP_CONTROL_POINTS.get(category, [])

        # Return all control points if category not found
        # إرجاع جميع نقاط المراقبة إذا لم يتم العثور على الفئة
        all_points = []
        for points in self.GLOBALGAP_CONTROL_POINTS.values():
            all_points.extend(points)
        return all_points[:10]  # Return first 10 as sample

    async def compare_certifications(
        self,
        certifications: List[CertificationStandard],
        farm_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Compare multiple certification standards
        مقارنة معايير الشهادات المتعددة

        Args:
            certifications: List of certifications to compare
                قائمة الشهادات للمقارنة
            farm_context: Farm-specific context for recommendations
                سياق خاص بالمزرعة للتوصيات

        Returns:
            Comparison analysis with recommendations
            تحليل المقارنة مع التوصيات
        """
        query = f"""Compare the following certification standards: {', '.join([c.value for c in certifications])}

Provide comparative analysis:
1. Requirements comparison
   - Documentation requirements
   - Implementation complexity
   - Record-keeping demands
   - Input restrictions

2. Market advantages
   - Market access benefits
   - Premium pricing potential
   - Consumer recognition
   - Geographic advantages

3. Cost comparison
   - Certification costs
   - Implementation costs
   - Annual audit fees
   - Ongoing compliance costs

4. Timeline comparison
   - Conversion periods
   - Implementation timeframe
   - Audit frequency

5. Compatibility analysis
   - Can certifications be combined?
   - Synergies between standards
   - Conflicting requirements

6. Recommendation
   - Best fit for farm context
   - Optimal certification path
   - Priority order if pursuing multiple

Consider the farm context and provide actionable recommendations."""

        context = {
            "certifications": [c.value for c in certifications],
            "farm_context": farm_context or {},
            "task": "certification_comparison",
        }

        return await self.think(query, context=context, use_rag=True)
