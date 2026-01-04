"""
Compliance Service
خدمة الامتثال

Business logic for tracking farm compliance against IFA v6 standards.
منطق العمل لتتبع امتثال المزارع لمعايير IFA v6.
"""

from datetime import datetime, timedelta
from typing import Any

from ..models import (
    ChecklistAssessment,
    ComplianceRecord,
    ComplianceStatus,
    ControlPointStatus,
    NonConformity,
    SeverityLevel,
)


class ComplianceService:
    """
    Service for managing farm compliance records
    خدمة إدارة سجلات امتثال المزارع
    """

    def __init__(self):
        """Initialize compliance service"""
        # In a real implementation, this would connect to database
        # في التطبيق الفعلي، سيتصل هذا بقاعدة البيانات
        self.compliance_records: dict[str, ComplianceRecord] = {}
        self.non_conformities: dict[str, list[NonConformity]] = {}

    async def calculate_compliance_status(
        self, farm_id: str, assessments: list[ChecklistAssessment]
    ) -> ComplianceRecord:
        """
        Calculate overall compliance status based on assessments
        حساب حالة الامتثال الإجمالية بناءً على التقييمات

        Args:
            farm_id: Farm identifier | معرف المزرعة
            assessments: List of checklist assessments | قائمة تقييمات قائمة المراجعة

        Returns:
            ComplianceRecord with calculated status | سجل الامتثال مع الحالة المحسوبة
        """
        if not assessments:
            return ComplianceRecord(
                farm_id=farm_id,
                tenant_id="",
                overall_status=ComplianceStatus.NOT_ASSESSED,
            )

        # Count control points by status
        # عد نقاط التحكم حسب الحالة
        total_points = len(assessments)
        compliant_points = sum(
            1 for a in assessments if a.status == ControlPointStatus.COMPLIANT
        )
        non_compliant_points = sum(
            1 for a in assessments if a.status == ControlPointStatus.NON_COMPLIANT
        )

        # Count Major Must and Minor Must failures
        # عد إخفاقات النقاط الإلزامية الرئيسية والثانوية
        major_must_fails = 0
        minor_must_fails = 0

        for assessment in assessments:
            if assessment.status == ControlPointStatus.NON_COMPLIANT:
                # In real implementation, we would check the checklist item's compliance level
                # في التطبيق الفعلي، سنتحقق من مستوى الامتثال لعنصر قائمة المراجعة
                # For now, we'll simulate this
                # الآن، سنحاكي هذا
                if "MAJOR" in assessment.control_point_number.upper():
                    major_must_fails += 1
                else:
                    minor_must_fails += 1

        # Calculate compliance percentage
        # حساب نسبة الامتثال
        applicable_points = total_points - sum(
            1 for a in assessments if a.status == ControlPointStatus.NOT_APPLICABLE
        )
        compliance_percentage = (
            (compliant_points / applicable_points * 100)
            if applicable_points > 0
            else 0.0
        )

        # Determine overall status
        # تحديد الحالة الإجمالية
        overall_status = self._determine_overall_status(
            major_must_fails=major_must_fails,
            compliance_percentage=compliance_percentage,
        )

        # Create compliance record
        # إنشاء سجل الامتثال
        compliance_record = ComplianceRecord(
            farm_id=farm_id,
            tenant_id=assessments[0].tenant_id if assessments else "",
            overall_status=overall_status,
            compliance_percentage=round(compliance_percentage, 2),
            total_control_points=total_points,
            compliant_points=compliant_points,
            non_compliant_points=non_compliant_points,
            major_must_fails=major_must_fails,
            minor_must_fails=minor_must_fails,
            assessment_date=datetime.utcnow(),
            next_assessment_date=datetime.utcnow() + timedelta(days=365),
        )

        return compliance_record

    def _determine_overall_status(
        self, major_must_fails: int, compliance_percentage: float
    ) -> ComplianceStatus:
        """
        Determine overall compliance status based on IFA rules
        تحديد حالة الامتثال الإجمالية بناءً على قواعد IFA

        IFA Rules:
        - Any Major Must failure = NON_COMPLIANT
        - Minor Must compliance < 95% = NON_COMPLIANT
        - Otherwise = COMPLIANT

        Args:
            major_must_fails: Number of Major Must failures | عدد إخفاقات النقاط الإلزامية الرئيسية
            compliance_percentage: Overall compliance percentage | نسبة الامتثال الإجمالية

        Returns:
            Overall compliance status | حالة الامتثال الإجمالية
        """
        # Any Major Must failure means non-compliant
        # أي إخفاق في النقاط الإلزامية الرئيسية يعني عدم الامتثال
        if major_must_fails > 0:
            return ComplianceStatus.NON_COMPLIANT

        # Check Minor Must compliance threshold (95%)
        # التحقق من عتبة الامتثال للنقاط الإلزامية الثانوية (95%)
        if compliance_percentage < 95.0:
            return ComplianceStatus.PARTIALLY_COMPLIANT

        # Full compliance
        # امتثال كامل
        return ComplianceStatus.COMPLIANT

    async def get_farm_compliance(
        self, farm_id: str, tenant_id: str
    ) -> ComplianceRecord | None:
        """
        Get current compliance record for a farm
        الحصول على سجل الامتثال الحالي للمزرعة

        Args:
            farm_id: Farm identifier | معرف المزرعة
            tenant_id: Tenant identifier | معرف المستأجر

        Returns:
            Compliance record or None | سجل الامتثال أو None
        """
        # In real implementation, query database
        # في التطبيق الفعلي، الاستعلام من قاعدة البيانات
        key = f"{tenant_id}:{farm_id}"
        return self.compliance_records.get(key)

    async def save_compliance_record(
        self, compliance_record: ComplianceRecord
    ) -> ComplianceRecord:
        """
        Save compliance record to database
        حفظ سجل الامتثال في قاعدة البيانات

        Args:
            compliance_record: Compliance record to save | سجل الامتثال للحفظ

        Returns:
            Saved compliance record | سجل الامتثال المحفوظ
        """
        # In real implementation, save to database
        # في التطبيق الفعلي، الحفظ في قاعدة البيانات
        key = f"{compliance_record.tenant_id}:{compliance_record.farm_id}"
        compliance_record.id = key
        compliance_record.updated_at = datetime.utcnow()
        self.compliance_records[key] = compliance_record
        return compliance_record

    async def get_non_conformities(
        self,
        farm_id: str,
        tenant_id: str,
        severity: SeverityLevel | None = None,
        resolved: bool | None = None,
    ) -> list[NonConformity]:
        """
        Get non-conformities for a farm
        الحصول على عدم المطابقات للمزرعة

        Args:
            farm_id: Farm identifier | معرف المزرعة
            tenant_id: Tenant identifier | معرف المستأجر
            severity: Filter by severity level | تصفية حسب مستوى الخطورة
            resolved: Filter by resolution status | تصفية حسب حالة الحل

        Returns:
            List of non-conformities | قائمة عدم المطابقات
        """
        key = f"{tenant_id}:{farm_id}"
        non_conformities = self.non_conformities.get(key, [])

        # Apply filters
        # تطبيق المرشحات
        if severity is not None:
            non_conformities = [
                nc for nc in non_conformities if nc.severity == severity
            ]

        if resolved is not None:
            non_conformities = [
                nc
                for nc in non_conformities
                if nc.corrective_action_completed == resolved
            ]

        return non_conformities

    async def create_non_conformity(
        self, non_conformity: NonConformity
    ) -> NonConformity:
        """
        Create a new non-conformity record
        إنشاء سجل عدم مطابقة جديد

        Args:
            non_conformity: Non-conformity to create | عدم المطابقة للإنشاء

        Returns:
            Created non-conformity | عدم المطابقة المنشأ
        """
        # Extract farm_id from compliance_record_id (simplified)
        # استخراج farm_id من compliance_record_id (مبسط)
        non_conformity.id = f"nc_{datetime.utcnow().timestamp()}"
        non_conformity.identified_date = datetime.utcnow()

        # In real implementation, save to database
        # في التطبيق الفعلي، الحفظ في قاعدة البيانات
        # For now, store in memory
        # الآن، التخزين في الذاكرة
        key = non_conformity.compliance_record_id
        if key not in self.non_conformities:
            self.non_conformities[key] = []
        self.non_conformities[key].append(non_conformity)

        return non_conformity

    async def update_corrective_action(
        self,
        non_conformity_id: str,
        action_plan: str,
        deadline: datetime,
        status: str = "in_progress",
    ) -> NonConformity | None:
        """
        Update corrective action for a non-conformity
        تحديث الإجراء التصحيحي لعدم المطابقة

        Args:
            non_conformity_id: Non-conformity identifier | معرف عدم المطابقة
            action_plan: Corrective action plan | خطة الإجراء التصحيحي
            deadline: Action deadline | الموعد النهائي للإجراء
            status: Action status | حالة الإجراء

        Returns:
            Updated non-conformity or None | عدم المطابقة المحدث أو None
        """
        # In real implementation, query and update database
        # في التطبيق الفعلي، الاستعلام والتحديث في قاعدة البيانات
        for _key, ncs in self.non_conformities.items():
            for nc in ncs:
                if nc.id == non_conformity_id:
                    nc.corrective_action_plan = action_plan
                    nc.corrective_action_deadline = deadline
                    nc.corrective_action_status = status
                    if status == "completed":
                        nc.corrective_action_completed = True
                        nc.resolved_date = datetime.utcnow()
                    return nc

        return None

    async def get_compliance_trends(
        self, farm_id: str, tenant_id: str, months: int = 12
    ) -> list[dict[str, Any]]:
        """
        Get compliance trends over time
        الحصول على اتجاهات الامتثال عبر الزمن

        Args:
            farm_id: Farm identifier | معرف المزرعة
            tenant_id: Tenant identifier | معرف المستأجر
            months: Number of months to retrieve | عدد الأشهر للاسترجاع

        Returns:
            List of compliance data points | قائمة نقاط بيانات الامتثال
        """
        # In real implementation, query historical data
        # في التطبيق الفعلي، الاستعلام عن البيانات التاريخية
        trends = []

        # Simulate historical data
        # محاكاة البيانات التاريخية
        for i in range(months):
            date = datetime.utcnow() - timedelta(days=30 * i)
            trends.append(
                {
                    "date": date.isoformat(),
                    "compliance_percentage": 85.0 + (i * 2),  # Simulated improvement
                    "major_must_fails": max(0, 3 - i),
                    "minor_must_fails": max(0, 10 - i),
                }
            )

        return trends
