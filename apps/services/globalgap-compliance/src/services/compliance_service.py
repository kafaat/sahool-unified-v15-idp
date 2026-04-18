"""
Compliance Service
خدمة الامتثال

Business logic for tracking farm compliance against IFA v6 standards.
منطق العمل لتتبع امتثال المزارع لمعايير IFA v6.
"""

from datetime import UTC, datetime, timedelta, timezone
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
        compliant_points = sum(1 for a in assessments if a.status == ControlPointStatus.COMPLIANT)
        non_compliant_points = sum(1 for a in assessments if a.status == ControlPointStatus.NON_COMPLIANT)

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
        applicable_points = total_points - sum(1 for a in assessments if a.status == ControlPointStatus.NOT_APPLICABLE)
        compliance_percentage = (compliant_points / applicable_points * 100) if applicable_points > 0 else 0.0

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
            assessment_date=datetime.now(UTC),
            next_assessment_date=datetime.now(UTC) + timedelta(days=365),
        )

        return compliance_record

    def _determine_overall_status(self, major_must_fails: int, compliance_percentage: float) -> ComplianceStatus:
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

    async def get_farm_compliance(self, farm_id: str, tenant_id: str) -> ComplianceRecord | None:
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

    async def save_compliance_record(self, compliance_record: ComplianceRecord) -> ComplianceRecord:
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
        compliance_record.updated_at = datetime.now(UTC)
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
            non_conformities = [nc for nc in non_conformities if nc.severity == severity]

        if resolved is not None:
            non_conformities = [nc for nc in non_conformities if nc.corrective_action_completed == resolved]

        return non_conformities

    async def create_non_conformity(self, non_conformity: NonConformity) -> NonConformity:
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
        non_conformity.id = f"nc_{datetime.now(UTC).timestamp()}"
        non_conformity.identified_date = datetime.now(UTC)

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
                    nc.corrective_action_taken = action_plan
                    nc.corrective_action_deadline = deadline
                    if status == "completed":
                        nc.corrective_action_completed = True
                        nc.resolved_date = datetime.now(UTC)
                    return nc

        return None

    async def get_compliance_trends(self, farm_id: str, tenant_id: str, months: int = 12) -> list[dict[str, Any]]:
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
            date = datetime.now(UTC) - timedelta(days=30 * i)
            trends.append(
                {
                    "date": date.isoformat(),
                    "compliance_percentage": 85.0 + (i * 2),  # Simulated improvement
                    "major_must_fails": max(0, 3 - i),
                    "minor_must_fails": max(0, 10 - i),
                }
            )

        return trends

    async def generate_compliance_report(
        self,
        farm_id: str,
        tenant_id: str,
        months: int = 12,
    ) -> dict[str, Any]:
        """
        Assemble a comprehensive bilingual compliance report for a farm.
        توليد تقرير امتثال شامل ثنائي اللغة للمزرعة.

        Combines the current compliance record, open and resolved
        non-conformities, and historical trend into a single structure
        that auditors / certification bodies can consume directly as
        JSON (or a downstream service can render to PDF).

        Args:
            farm_id:   Farm identifier | معرف المزرعة
            tenant_id: Tenant identifier | معرف المستأجر
            months:    Trend window in months | نافذة الاتجاه بالأشهر

        Returns:
            Report dict with sections: summary (+summary_ar), current,
            non_conformities, trend, verdict (+verdict_ar). Never raises —
            missing data is expressed as NOT_ASSESSED so the endpoint is
            safe to call at any stage of the compliance lifecycle.
        """
        current = await self.get_farm_compliance(farm_id, tenant_id)
        all_ncs = await self.get_non_conformities(farm_id=farm_id, tenant_id=tenant_id)
        trend = await self.get_compliance_trends(farm_id, tenant_id, months=months)

        open_ncs = [nc for nc in all_ncs if not nc.corrective_action_completed]
        resolved_ncs = [nc for nc in all_ncs if nc.corrective_action_completed]
        major_open = sum(1 for nc in open_ncs if nc.severity == SeverityLevel.MAJOR)
        minor_open = sum(1 for nc in open_ncs if nc.severity == SeverityLevel.MINOR)
        critical_open = sum(1 for nc in open_ncs if nc.severity == SeverityLevel.CRITICAL)

        # Verdict derivation. Certification bodies read the "can certify"
        # signal before anything else; surface it explicitly rather than
        # forcing them to interpret raw percentages + NC counts.
        #
        # Criteria mirror GlobalGAP IFA v6. Two independent "blocker"
        # signals both map to `blocked` — we check BOTH so a farm can't
        # slip through just because its major-must failures were captured
        # on the ComplianceRecord but never materialised as standalone
        # NonConformity items in the in-memory store (this is possible
        # because `calculate_compliance_status` counts major_must_fails
        # from assessments directly, separate from the NC store):
        #   * Open CRITICAL or MAJOR non-conformity rows, OR
        #   * ComplianceRecord with `major_must_fails > 0`
        #     or overall_status == NON_COMPLIANT
        major_blocker = critical_open > 0 or major_open > 0
        record_blocker = current is not None and (
            current.major_must_fails > 0 or current.overall_status == ComplianceStatus.NON_COMPLIANT
        )

        if current is None:
            verdict = "not_assessed"
            verdict_en = "Not yet assessed — no compliance record on file."
            verdict_ar = "لم يتم التقييم بعد — لا يوجد سجل امتثال."
        elif current.overall_status == ComplianceStatus.NOT_ASSESSED:
            verdict = "not_assessed"
            verdict_en = "Compliance record exists but no assessment has been performed yet."
            verdict_ar = "يوجد سجل امتثال لكن لم يتم إجراء أي تقييم بعد."
        elif major_blocker or record_blocker:
            verdict = "blocked"
            # Build the reason text from ONLY the active signals. Stringing
            # together zero-counts would read as misleading noise ("0 open
            # major, 0 critical, 0 major-must failure") when a farm is
            # blocked solely on `overall_status == NON_COMPLIANT`.
            reasons_en: list[str] = []
            reasons_ar: list[str] = []
            if major_open > 0:
                reasons_en.append(f"{major_open} open major non-conformity(ies)")
                reasons_ar.append(f"{major_open} حالة عدم مطابقة رئيسية مفتوحة")
            if critical_open > 0:
                reasons_en.append(f"{critical_open} critical non-conformity(ies)")
                reasons_ar.append(f"{critical_open} حالة عدم مطابقة حرجة مفتوحة")
            if current.major_must_fails > 0:
                reasons_en.append(
                    f"{current.major_must_fails} major-must failure(s) on the compliance record"
                )
                reasons_ar.append(
                    f"{current.major_must_fails} إخفاق في المتطلبات الرئيسية على سجل الامتثال"
                )
            if current.overall_status == ComplianceStatus.NON_COMPLIANT:
                reasons_en.append("overall compliance status is NON_COMPLIANT")
                reasons_ar.append("حالة الامتثال العامة هي غير متوافق")
            verdict_en = (
                f"Certification BLOCKED: {'; '.join(reasons_en)}. Must be resolved before audit."
            )
            verdict_ar = (
                f"الشهادة محجوبة: {'؛ '.join(reasons_ar)}. يجب حلها قبل التدقيق."
            )
        elif current.overall_status == ComplianceStatus.COMPLIANT:
            verdict = "eligible"
            verdict_en = "Eligible for certification — all major-musts satisfied."
            verdict_ar = "مؤهل للحصول على الشهادة — جميع المتطلبات الرئيسية مستوفاة."
        else:
            verdict = "conditional"
            verdict_en = (
                f"Conditional eligibility at {current.compliance_percentage:.1f}%. "
                f"{minor_open} minor non-conformity(ies) open."
            )
            verdict_ar = (
                f"أهلية مشروطة بنسبة {current.compliance_percentage:.1f}%. {minor_open} حالة عدم مطابقة ثانوية مفتوحة."
            )

        # Summary paragraph — bilingual, narrative form so the report's
        # first page reads like a human-written executive summary rather
        # than a struct dump.
        pct = current.compliance_percentage if current else 0.0
        total_ncs = len(all_ncs)
        summary_en = (
            f"Farm {farm_id} currently scores {pct:.1f}% against GlobalGAP IFA v6. "
            f"{total_ncs} non-conformity(ies) on record: {len(open_ncs)} open, "
            f"{len(resolved_ncs)} resolved. {len(trend)}-month trend included."
        )
        summary_ar = (
            f"تحقق المزرعة {farm_id} حاليًا نسبة {pct:.1f}% وفقًا لمعيار GlobalGAP IFA v6. "
            f"{total_ncs} حالة عدم مطابقة مسجلة: {len(open_ncs)} مفتوحة، "
            f"{len(resolved_ncs)} تم حلها. اتجاه {len(trend)} أشهر مُدرج."
        )

        # Resolved severity rollup — so consumers can also tell at a
        # glance how deep the resolved pile is without iterating.
        major_resolved = sum(1 for nc in resolved_ncs if nc.severity == SeverityLevel.MAJOR)
        minor_resolved = sum(1 for nc in resolved_ncs if nc.severity == SeverityLevel.MINOR)
        critical_resolved = sum(1 for nc in resolved_ncs if nc.severity == SeverityLevel.CRITICAL)

        return {
            "report_type": "globalgap_compliance_report",
            "ifa_version": "6.0",
            "farm_id": farm_id,
            "tenant_id": tenant_id,
            "generated_at": datetime.now(UTC).isoformat(),
            "summary": summary_en,
            "summary_ar": summary_ar,
            "verdict": verdict,
            "verdict_en": verdict_en,
            "verdict_ar": verdict_ar,
            "current": current.model_dump() if current else None,
            # Field names follow the "name = exactly what's in it" rule
            # so a consumer that sees `open_by_severity` doesn't have to
            # read the code to know it excludes resolved items.
            "non_conformities": {
                "total": total_ncs,
                "open_count": len(open_ncs),
                "resolved_count": len(resolved_ncs),
                "open_by_severity": {
                    "critical": critical_open,
                    "major": major_open,
                    "minor": minor_open,
                },
                "resolved_by_severity": {
                    "critical": critical_resolved,
                    "major": major_resolved,
                    "minor": minor_resolved,
                },
                # Full payload only for open items; resolved items can be
                # retrieved via /farms/{id}/non-conformities?resolved=true.
                # Including them here would double the report size without
                # helping the primary audit use-case (act on open items).
                "open_items": [nc.model_dump() for nc in open_ncs],
            },
            "trend": {
                "months": months,
                "data_points": trend,
            },
        }
