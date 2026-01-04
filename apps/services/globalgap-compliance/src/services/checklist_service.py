"""
Checklist Service
خدمة قوائم المراجعة

Business logic for generating and managing GlobalGAP IFA checklists.
منطق العمل لإنشاء وإدارة قوائم المراجعة الخاصة بمعايير GlobalGAP IFA.
"""

from datetime import datetime
from typing import Any

from ..models import (
    Checklist,
    ChecklistAssessment,
    ChecklistCategory,
    ChecklistItem,
    ComplianceLevel,
    ControlPointStatus,
)


class ChecklistService:
    """
    Service for managing GlobalGAP IFA checklists
    خدمة إدارة قوائم المراجعة الخاصة بمعايير GlobalGAP IFA
    """

    def __init__(self):
        """Initialize checklist service"""
        # In a real implementation, this would load from database
        # في التطبيق الفعلي، سيتم التحميل من قاعدة البيانات
        self.checklist_items: dict[str, ChecklistItem] = {}
        self.checklists: dict[str, Checklist] = {}
        self._initialize_sample_items()

    def _initialize_sample_items(self):
        """
        Initialize sample checklist items for demonstration
        تهيئة عناصر قائمة المراجعة النموذجية للعرض التوضيحي
        """
        # Sample IFA v6 control points
        # نقاط تحكم IFA v6 النموذجية
        sample_items = [
            ChecklistItem(
                id="cp_af_1_1_1",
                control_point_number="AF.1.1.1",
                category=ChecklistCategory.AF_SITE_MANAGEMENT,
                compliance_level=ComplianceLevel.MAJOR_MUST,
                title_ar="يجب الاحتفاظ بالسجلات",
                title_en="Records must be kept",
                requirement_ar="يجب الاحتفاظ بسجلات موثقة لجميع الأنشطة الزراعية ذات الصلة بالمعايير لمدة عامين على الأقل",
                requirement_en="Documented records of all farm activities relevant to the standard must be kept for at least 2 years",
                compliance_criteria_ar=[
                    "وجود نظام لحفظ السجلات",
                    "السجلات متاحة للمراجعة",
                    "السجلات محفوظة لمدة عامين على الأقل",
                ],
                compliance_criteria_en=[
                    "Record keeping system exists",
                    "Records available for review",
                    "Records kept for at least 2 years",
                ],
                verification_methods=["document_review", "interview"],
                required_evidence=["record_keeping_system", "sample_records"],
            ),
            ChecklistItem(
                id="cp_af_5_1_1",
                control_point_number="AF.5.1.1",
                category=ChecklistCategory.AF_CROP_PROTECTION,
                compliance_level=ComplianceLevel.MAJOR_MUST,
                title_ar="يجب أن تكون جميع منتجات وقاية النباتات المستخدمة مسجلة رسميًا",
                title_en="All plant protection products used must be officially registered",
                requirement_ar="يجب أن تكون جميع منتجات وقاية النباتات المستخدمة في المزرعة مسجلة رسميًا في الدولة للاستخدام على المحاصيل المستهدفة",
                requirement_en="All plant protection products used on the farm must be officially registered in the country for use on the target crops",
                compliance_criteria_ar=[
                    "قائمة بجميع المبيدات المستخدمة",
                    "أرقام التسجيل الرسمية متاحة",
                    "المبيدات مسجلة للمحاصيل المستهدفة",
                ],
                compliance_criteria_en=[
                    "List of all pesticides used",
                    "Official registration numbers available",
                    "Pesticides registered for target crops",
                ],
                verification_methods=["document_review", "visual_inspection"],
                required_evidence=["pesticide_list", "registration_certificates"],
            ),
            ChecklistItem(
                id="cp_af_3_2_1",
                control_point_number="AF.3.2.1",
                category=ChecklistCategory.AF_FERTILIZER_USE,
                compliance_level=ComplianceLevel.MINOR_MUST,
                title_ar="يجب الاحتفاظ بسجلات استخدام الأسمدة",
                title_en="Fertilizer application records must be kept",
                requirement_ar="يجب الاحتفاظ بسجلات تطبيق الأسمدة لجميع المحاصيل المعتمدة",
                requirement_en="Fertilizer application records must be kept for all certified crops",
                compliance_criteria_ar=[
                    "سجلات تطبيق الأسمدة متاحة",
                    "السجلات تتضمن التاريخ والنوع والكمية",
                    "السجلات محدثة",
                ],
                compliance_criteria_en=[
                    "Fertilizer application records available",
                    "Records include date, type, and quantity",
                    "Records are up to date",
                ],
                verification_methods=["document_review"],
                required_evidence=["fertilizer_application_records"],
            ),
            ChecklistItem(
                id="cp_af_4_1_1",
                control_point_number="AF.4.1.1",
                category=ChecklistCategory.AF_IRRIGATION,
                compliance_level=ComplianceLevel.MINOR_MUST,
                title_ar="يجب إجراء تحليل للمياه",
                title_en="Water analysis must be conducted",
                requirement_ar="يجب إجراء تحليل للمياه المستخدمة في الري قبل الاستخدام الأول وكل عام بعد ذلك",
                requirement_en="Water analysis must be conducted for irrigation water before first use and annually thereafter",
                compliance_criteria_ar=[
                    "تقارير تحليل المياه متاحة",
                    "التحليل يشمل المعايير الميكروبيولوجية",
                    "التحليل حديث (خلال العام الماضي)",
                ],
                compliance_criteria_en=[
                    "Water analysis reports available",
                    "Analysis includes microbiological parameters",
                    "Analysis is recent (within last year)",
                ],
                verification_methods=["document_review"],
                required_evidence=["water_analysis_reports"],
            ),
            ChecklistItem(
                id="cp_af_10_1_1",
                control_point_number="AF.10.1.1",
                category=ChecklistCategory.AF_ENVIRONMENT,
                compliance_level=ComplianceLevel.RECOMMENDATION,
                title_ar="يُوصى بوجود خطة لإدارة التنوع البيولوجي",
                title_en="A biodiversity management plan is recommended",
                requirement_ar="يُوصى بوجود خطة موثقة لحماية وتعزيز التنوع البيولوجي في المزرعة",
                requirement_en="A documented plan for protecting and enhancing biodiversity on the farm is recommended",
                compliance_criteria_ar=[
                    "وجود خطة موثقة",
                    "الخطة تحدد مناطق الحماية",
                    "الخطة تتضمن إجراءات محددة",
                ],
                compliance_criteria_en=[
                    "Documented plan exists",
                    "Plan identifies protection areas",
                    "Plan includes specific actions",
                ],
                verification_methods=["document_review", "visual_inspection"],
                required_evidence=["biodiversity_plan"],
            ),
        ]

        for item in sample_items:
            self.checklist_items[item.id] = item

    async def get_checklist_by_category(
        self, category: ChecklistCategory, ifa_version: str = "6.0"
    ) -> list[ChecklistItem]:
        """
        Get checklist items for a specific category
        الحصول على عناصر قائمة المراجعة لفئة معينة

        Args:
            category: Checklist category | فئة قائمة المراجعة
            ifa_version: IFA version | إصدار معايير IFA

        Returns:
            List of checklist items | قائمة عناصر قائمة المراجعة
        """
        items = [
            item
            for item in self.checklist_items.values()
            if item.category == category and item.ifa_version == ifa_version
        ]
        return items

    async def get_all_checklist_items(
        self,
        ifa_version: str = "6.0",
        compliance_level: ComplianceLevel | None = None,
    ) -> list[ChecklistItem]:
        """
        Get all checklist items
        الحصول على جميع عناصر قائمة المراجعة

        Args:
            ifa_version: IFA version | إصدار معايير IFA
            compliance_level: Filter by compliance level | تصفية حسب مستوى الامتثال

        Returns:
            List of checklist items | قائمة عناصر قائمة المراجعة
        """
        items = [
            item
            for item in self.checklist_items.values()
            if item.ifa_version == ifa_version
        ]

        if compliance_level:
            items = [
                item for item in items if item.compliance_level == compliance_level
            ]

        return items

    async def get_checklist_item(
        self, control_point_number: str
    ) -> ChecklistItem | None:
        """
        Get a specific checklist item by control point number
        الحصول على عنصر قائمة المراجعة حسب رقم نقطة التحكم

        Args:
            control_point_number: Control point number (e.g., AF.1.1.1) | رقم نقطة التحكم

        Returns:
            Checklist item or None | عنصر قائمة المراجعة أو None
        """
        for item in self.checklist_items.values():
            if item.control_point_number == control_point_number:
                return item
        return None

    async def generate_farm_checklist(
        self, farm_id: str, tenant_id: str, crop_types: list[str], scope: str = "full"
    ) -> Checklist:
        """
        Generate a customized checklist for a farm
        إنشاء قائمة مراجعة مخصصة للمزرعة

        Args:
            farm_id: Farm identifier | معرف المزرعة
            tenant_id: Tenant identifier | معرف المستأجر
            crop_types: List of crop types | قائمة أنواع المحاصيل
            scope: Checklist scope (full, partial) | نطاق قائمة المراجعة

        Returns:
            Generated checklist | قائمة المراجعة المُنشأة
        """
        # Get all applicable items
        # الحصول على جميع العناصر القابلة للتطبيق
        all_items = await self.get_all_checklist_items()

        # Count by compliance level
        # العد حسب مستوى الامتثال
        major_must = sum(
            1
            for item in all_items
            if item.compliance_level == ComplianceLevel.MAJOR_MUST
        )
        minor_must = sum(
            1
            for item in all_items
            if item.compliance_level == ComplianceLevel.MINOR_MUST
        )
        recommendations = sum(
            1
            for item in all_items
            if item.compliance_level == ComplianceLevel.RECOMMENDATION
        )

        # Create checklist
        # إنشاء قائمة المراجعة
        checklist = Checklist(
            id=f"checklist_{farm_id}_{datetime.utcnow().timestamp()}",
            name_ar=f"قائمة المراجعة الخاصة بالمزرعة {farm_id}",
            name_en=f"Checklist for Farm {farm_id}",
            ifa_version="6.0",
            checklist_type=scope,
            applicable_categories=list(ChecklistCategory),
            crop_types=crop_types,
            total_items=len(all_items),
            major_must_count=major_must,
            minor_must_count=minor_must,
            recommendation_count=recommendations,
        )

        self.checklists[checklist.id] = checklist
        return checklist

    async def create_assessment(
        self, assessment: ChecklistAssessment
    ) -> ChecklistAssessment:
        """
        Create a new checklist assessment
        إنشاء تقييم جديد لقائمة المراجعة

        Args:
            assessment: Assessment to create | التقييم للإنشاء

        Returns:
            Created assessment | التقييم المنشأ
        """
        # In real implementation, save to database
        # في التطبيق الفعلي، الحفظ في قاعدة البيانات
        assessment.id = f"assessment_{datetime.utcnow().timestamp()}"
        assessment.created_at = datetime.utcnow()
        assessment.updated_at = datetime.utcnow()
        return assessment

    async def update_assessment(
        self,
        assessment_id: str,
        status: ControlPointStatus,
        evidence_description: str | None = None,
        assessor_notes: str | None = None,
    ) -> ChecklistAssessment | None:
        """
        Update an existing checklist assessment
        تحديث تقييم قائمة المراجعة الموجود

        Args:
            assessment_id: Assessment identifier | معرف التقييم
            status: New assessment status | حالة التقييم الجديدة
            evidence_description: Evidence description | وصف الأدلة
            assessor_notes: Assessor notes | ملاحظات المقيم

        Returns:
            Updated assessment or None | التقييم المحدث أو None
        """
        # In real implementation, query and update database
        # في التطبيق الفعلي، الاستعلام والتحديث في قاعدة البيانات
        # For now, return a mock updated assessment
        # الآن، إرجاع تقييم محدث وهمي
        return None

    async def get_farm_assessments(
        self, farm_id: str, tenant_id: str
    ) -> list[ChecklistAssessment]:
        """
        Get all assessments for a farm
        الحصول على جميع التقييمات للمزرعة

        Args:
            farm_id: Farm identifier | معرف المزرعة
            tenant_id: Tenant identifier | معرف المستأجر

        Returns:
            List of assessments | قائمة التقييمات
        """
        # In real implementation, query database
        # في التطبيق الفعلي، الاستعلام من قاعدة البيانات
        return []

    async def get_assessment_summary(
        self, farm_id: str, tenant_id: str
    ) -> dict[str, Any]:
        """
        Get assessment summary for a farm
        الحصول على ملخص التقييم للمزرعة

        Args:
            farm_id: Farm identifier | معرف المزرعة
            tenant_id: Tenant identifier | معرف المستأجر

        Returns:
            Assessment summary | ملخص التقييم
        """
        assessments = await self.get_farm_assessments(farm_id, tenant_id)

        summary = {
            "total_assessments": len(assessments),
            "compliant": sum(
                1 for a in assessments if a.status == ControlPointStatus.COMPLIANT
            ),
            "non_compliant": sum(
                1 for a in assessments if a.status == ControlPointStatus.NON_COMPLIANT
            ),
            "not_applicable": sum(
                1 for a in assessments if a.status == ControlPointStatus.NOT_APPLICABLE
            ),
            "not_assessed": sum(
                1 for a in assessments if a.status == ControlPointStatus.NOT_ASSESSED
            ),
            "completion_percentage": (
                len(
                    [
                        a
                        for a in assessments
                        if a.status != ControlPointStatus.NOT_ASSESSED
                    ]
                )
                / len(assessments)
                * 100
                if assessments
                else 0
            ),
        }

        return summary

    async def search_checklist_items(
        self, query: str, language: str = "ar"
    ) -> list[ChecklistItem]:
        """
        Search checklist items by keyword
        البحث في عناصر قائمة المراجعة بالكلمات الرئيسية

        Args:
            query: Search query | استعلام البحث
            language: Search language (ar, en) | لغة البحث

        Returns:
            Matching checklist items | عناصر قائمة المراجعة المطابقة
        """
        query_lower = query.lower()
        results = []

        for item in self.checklist_items.values():
            if language == "ar":
                if (
                    query_lower in item.title_ar.lower()
                    or query_lower in item.requirement_ar.lower()
                ):
                    results.append(item)
            else:
                if (
                    query_lower in item.title_en.lower()
                    or query_lower in item.requirement_en.lower()
                ):
                    results.append(item)

        return results
