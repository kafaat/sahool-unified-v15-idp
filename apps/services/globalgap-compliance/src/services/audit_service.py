"""
Audit Service
خدمة التدقيق

Business logic for preparing and managing audit reports.
منطق العمل لإعداد وإدارة تقارير التدقيق.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from ..models import (
    AuditResult,
    ComplianceRecord,
    NonConformity,
    ChecklistAssessment,
    SeverityLevel,
)


class AuditService:
    """
    Service for managing audits and audit reports
    خدمة إدارة التدقيق وتقارير التدقيق
    """

    def __init__(self):
        """Initialize audit service"""
        # In a real implementation, this would connect to database
        # في التطبيق الفعلي، سيتصل هذا بقاعدة البيانات
        self.audit_results: Dict[str, AuditResult] = {}

    async def prepare_audit_report(
        self,
        farm_id: str,
        tenant_id: str,
        compliance_record: ComplianceRecord,
        non_conformities: List[NonConformity],
        audit_type: str = "internal",
        auditor_name: str = "",
    ) -> AuditResult:
        """
        Prepare a comprehensive audit report
        إعداد تقرير تدقيق شامل

        Args:
            farm_id: Farm identifier | معرف المزرعة
            tenant_id: Tenant identifier | معرف المستأجر
            compliance_record: Compliance record | سجل الامتثال
            non_conformities: List of non-conformities | قائمة عدم المطابقات
            audit_type: Type of audit | نوع التدقيق
            auditor_name: Name of auditor | اسم المدقق

        Returns:
            Audit result | نتيجة التدقيق
        """
        # Count findings by severity
        # عد النتائج حسب الخطورة
        critical_findings = sum(
            1 for nc in non_conformities if nc.severity == SeverityLevel.CRITICAL
        )
        major_findings = sum(
            1 for nc in non_conformities if nc.severity == SeverityLevel.MAJOR
        )
        minor_findings = sum(
            1 for nc in non_conformities if nc.severity == SeverityLevel.MINOR
        )
        observations = sum(
            1 for nc in non_conformities if nc.severity == SeverityLevel.OBSERVATION
        )

        # Determine audit status
        # تحديد حالة التدقيق
        audit_status = self._determine_audit_status(
            compliance_percentage=compliance_record.compliance_percentage,
            major_must_fails=compliance_record.major_must_fails,
            critical_findings=critical_findings,
        )

        # Generate recommendations
        # إنشاء التوصيات
        recommendations = self._generate_recommendations(
            compliance_record=compliance_record, non_conformities=non_conformities
        )

        # Generate executive summary
        # إنشاء الملخص التنفيذي
        executive_summary_ar = self._generate_executive_summary_ar(
            compliance_record=compliance_record,
            audit_status=audit_status,
            total_findings=len(non_conformities),
        )

        executive_summary_en = self._generate_executive_summary_en(
            compliance_record=compliance_record,
            audit_status=audit_status,
            total_findings=len(non_conformities),
        )

        # Create audit result
        # إنشاء نتيجة التدقيق
        audit_result = AuditResult(
            farm_id=farm_id,
            tenant_id=tenant_id,
            compliance_record_id=compliance_record.id or "",
            audit_type=audit_type,
            auditor_name=auditor_name,
            audit_date=datetime.utcnow(),
            audit_status=audit_status,
            overall_score=compliance_record.compliance_percentage,
            total_findings=len(non_conformities),
            critical_findings=critical_findings,
            major_findings=major_findings,
            minor_findings=minor_findings,
            observations=observations,
            executive_summary_ar=executive_summary_ar,
            executive_summary_en=executive_summary_en,
            recommendations=recommendations,
            follow_up_required=(audit_status != "passed"),
            follow_up_deadline=(
                datetime.utcnow() + timedelta(days=90)
                if audit_status != "passed"
                else None
            ),
        )

        return audit_result

    def _determine_audit_status(
        self,
        compliance_percentage: float,
        major_must_fails: int,
        critical_findings: int,
    ) -> str:
        """
        Determine overall audit status
        تحديد حالة التدقيق الإجمالية

        Args:
            compliance_percentage: Overall compliance percentage | نسبة الامتثال الإجمالية
            major_must_fails: Number of Major Must failures | عدد إخفاقات النقاط الإلزامية الرئيسية
            critical_findings: Number of critical findings | عدد النتائج الحرجة

        Returns:
            Audit status: passed, failed, conditional | حالة التدقيق
        """
        # Critical findings or Major Must failures = FAILED
        # النتائج الحرجة أو إخفاقات النقاط الإلزامية الرئيسية = فشل
        if critical_findings > 0 or major_must_fails > 0:
            return "failed"

        # Compliance < 95% = CONDITIONAL
        # الامتثال < 95% = مشروط
        if compliance_percentage < 95.0:
            return "conditional"

        # Otherwise = PASSED
        # خلاف ذلك = نجح
        return "passed"

    def _generate_recommendations(
        self, compliance_record: ComplianceRecord, non_conformities: List[NonConformity]
    ) -> List[str]:
        """
        Generate recommendations based on audit findings
        إنشاء التوصيات بناءً على نتائج التدقيق

        Args:
            compliance_record: Compliance record | سجل الامتثال
            non_conformities: List of non-conformities | قائمة عدم المطابقات

        Returns:
            List of recommendations | قائمة التوصيات
        """
        recommendations = []

        # Recommendations for Major Must failures
        # توصيات لإخفاقات النقاط الإلزامية الرئيسية
        if compliance_record.major_must_fails > 0:
            recommendations.append(
                "إعطاء الأولوية القصوى لمعالجة جميع نقاط عدم الامتثال الإلزامية الرئيسية - "
                "Priority must be given to addressing all Major Must non-conformities"
            )

        # Recommendations for low compliance
        # توصيات للامتثال المنخفض
        if compliance_record.compliance_percentage < 95.0:
            recommendations.append(
                "تطوير خطة عمل تصحيحية لرفع نسبة الامتثال إلى ما فوق 95% - "
                "Develop corrective action plan to raise compliance above 95%"
            )

        # Recommendations for specific categories
        # توصيات لفئات محددة
        crop_protection_issues = sum(
            1
            for nc in non_conformities
            if "5." in nc.control_point_number  # AF.5.x.x = Crop Protection
        )
        if crop_protection_issues > 3:
            recommendations.append(
                "مراجعة شاملة لممارسات حماية المحاصيل واستخدام المبيدات - "
                "Comprehensive review of crop protection and pesticide use practices"
            )

        record_keeping_issues = sum(
            1
            for nc in non_conformities
            if "1." in nc.control_point_number  # AF.1.x.x = Site Management/Records
        )
        if record_keeping_issues > 2:
            recommendations.append(
                "تحسين نظام حفظ السجلات والوثائق - "
                "Improve record keeping and documentation system"
            )

        # General recommendations
        # توصيات عامة
        if len(non_conformities) > 0:
            recommendations.append(
                "تدريب الموظفين على متطلبات معايير GlobalGAP IFA - "
                "Train staff on GlobalGAP IFA standard requirements"
            )
            recommendations.append(
                "إجراء تدقيق داخلي منتظم كل 6 أشهر - "
                "Conduct regular internal audits every 6 months"
            )

        return recommendations

    def _generate_executive_summary_ar(
        self,
        compliance_record: ComplianceRecord,
        audit_status: str,
        total_findings: int,
    ) -> str:
        """
        Generate executive summary in Arabic
        إنشاء الملخص التنفيذي بالعربية
        """
        status_text = {"passed": "ناجح", "failed": "فاشل", "conditional": "مشروط"}.get(
            audit_status, "غير محدد"
        )

        summary = f"""
ملخص تنفيذي لتدقيق الامتثال لمعايير GlobalGAP IFA v6.0

نتيجة التدقيق: {status_text}
نسبة الامتثال الإجمالية: {compliance_record.compliance_percentage:.1f}%

نقاط التحكم:
- إجمالي نقاط التحكم: {compliance_record.total_control_points}
- نقاط متوافقة: {compliance_record.compliant_points}
- نقاط غير متوافقة: {compliance_record.non_compliant_points}

عدم المطابقات:
- نقاط إلزامية رئيسية غير متوافقة: {compliance_record.major_must_fails}
- نقاط إلزامية ثانوية غير متوافقة: {compliance_record.minor_must_fails}
- إجمالي النتائج: {total_findings}

التوصية: {'يتطلب إجراءات تصحيحية فورية' if audit_status != 'passed' else 'الحفاظ على مستوى الامتثال الحالي'}
"""
        return summary.strip()

    def _generate_executive_summary_en(
        self,
        compliance_record: ComplianceRecord,
        audit_status: str,
        total_findings: int,
    ) -> str:
        """
        Generate executive summary in English
        إنشاء الملخص التنفيذي بالإنجليزية
        """
        summary = f"""
Executive Summary - GlobalGAP IFA v6.0 Compliance Audit

Audit Result: {audit_status.upper()}
Overall Compliance: {compliance_record.compliance_percentage:.1f}%

Control Points:
- Total Control Points: {compliance_record.total_control_points}
- Compliant Points: {compliance_record.compliant_points}
- Non-Compliant Points: {compliance_record.non_compliant_points}

Non-Conformities:
- Major Must Failures: {compliance_record.major_must_fails}
- Minor Must Failures: {compliance_record.minor_must_fails}
- Total Findings: {total_findings}

Recommendation: {'Immediate corrective actions required' if audit_status != 'passed' else 'Maintain current compliance level'}
"""
        return summary.strip()

    async def save_audit_result(self, audit_result: AuditResult) -> AuditResult:
        """
        Save audit result to database
        حفظ نتيجة التدقيق في قاعدة البيانات

        Args:
            audit_result: Audit result to save | نتيجة التدقيق للحفظ

        Returns:
            Saved audit result | نتيجة التدقيق المحفوظة
        """
        # In real implementation, save to database
        # في التطبيق الفعلي، الحفظ في قاعدة البيانات
        audit_result.id = f"audit_{datetime.utcnow().timestamp()}"
        audit_result.created_at = datetime.utcnow()
        self.audit_results[audit_result.id] = audit_result
        return audit_result

    async def get_audit_result(self, audit_id: str) -> Optional[AuditResult]:
        """
        Get audit result by ID
        الحصول على نتيجة التدقيق حسب المعرف

        Args:
            audit_id: Audit identifier | معرف التدقيق

        Returns:
            Audit result or None | نتيجة التدقيق أو None
        """
        return self.audit_results.get(audit_id)

    async def get_farm_audit_history(
        self, farm_id: str, tenant_id: str, limit: int = 10
    ) -> List[AuditResult]:
        """
        Get audit history for a farm
        الحصول على سجل التدقيق للمزرعة

        Args:
            farm_id: Farm identifier | معرف المزرعة
            tenant_id: Tenant identifier | معرف المستأجر
            limit: Maximum number of results | الحد الأقصى لعدد النتائج

        Returns:
            List of audit results | قائمة نتائج التدقيق
        """
        # In real implementation, query database
        # في التطبيق الفعلي، الاستعلام من قاعدة البيانات
        results = [
            audit
            for audit in self.audit_results.values()
            if audit.farm_id == farm_id and audit.tenant_id == tenant_id
        ]

        # Sort by date descending
        # ترتيب حسب التاريخ تنازليًا
        results.sort(key=lambda x: x.audit_date, reverse=True)

        return results[:limit]

    async def schedule_follow_up_audit(
        self, audit_id: str, follow_up_date: datetime
    ) -> Optional[Dict[str, Any]]:
        """
        Schedule a follow-up audit
        جدولة تدقيق متابعة

        Args:
            audit_id: Original audit identifier | معرف التدقيق الأصلي
            follow_up_date: Scheduled date for follow-up | التاريخ المحدد للمتابعة

        Returns:
            Follow-up audit details or None | تفاصيل تدقيق المتابعة أو None
        """
        audit = await self.get_audit_result(audit_id)
        if not audit:
            return None

        follow_up = {
            "original_audit_id": audit_id,
            "farm_id": audit.farm_id,
            "tenant_id": audit.tenant_id,
            "scheduled_date": follow_up_date.isoformat(),
            "audit_type": "follow_up",
            "focus_areas": [
                f"Control point {nc.control_point_number}"
                for nc in []  # Would be loaded from non-conformities
            ],
            "created_at": datetime.utcnow().isoformat(),
        }

        return follow_up

    async def generate_audit_certificate_recommendation(
        self, audit_result: AuditResult, compliance_record: ComplianceRecord
    ) -> Dict[str, Any]:
        """
        Generate recommendation for certification based on audit
        إنشاء توصية للحصول على الشهادة بناءً على التدقيق

        Args:
            audit_result: Audit result | نتيجة التدقيق
            compliance_record: Compliance record | سجل الامتثال

        Returns:
            Certification recommendation | توصية الشهادة
        """
        # Check certification eligibility
        # التحقق من الأهلية للحصول على الشهادة
        is_eligible = (
            audit_result.audit_status == "passed"
            and compliance_record.major_must_fails == 0
            and compliance_record.compliance_percentage >= 95.0
        )

        recommendation = {
            "eligible_for_certification": is_eligible,
            "audit_id": audit_result.id,
            "farm_id": audit_result.farm_id,
            "overall_score": audit_result.overall_score,
            "audit_status": audit_result.audit_status,
            "major_must_compliance": compliance_record.major_must_fails == 0,
            "minor_must_compliance_percentage": compliance_record.compliance_percentage,
            "recommendation_ar": (
                "المزرعة مؤهلة للحصول على شهادة GlobalGAP"
                if is_eligible
                else "يجب معالجة نقاط عدم الامتثال قبل التقدم للحصول على الشهادة"
            ),
            "recommendation_en": (
                "Farm is eligible for GlobalGAP certification"
                if is_eligible
                else "Non-conformities must be addressed before applying for certification"
            ),
            "next_steps_ar": (
                ["التقدم بطلب للحصول على شهادة GGN", "جدولة تدقيق خارجي"]
                if is_eligible
                else ["معالجة نقاط عدم الامتثال", "إجراء تدقيق متابعة"]
            ),
            "next_steps_en": (
                ["Apply for GGN certificate", "Schedule external audit"]
                if is_eligible
                else ["Address non-conformities", "Conduct follow-up audit"]
            ),
        }

        return recommendation
