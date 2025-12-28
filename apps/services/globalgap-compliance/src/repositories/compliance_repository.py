"""
GlobalGAP Compliance Repository
مستودع الامتثال لـ GlobalGAP

Full repository pattern implementation with comprehensive query methods for:
- Farm compliance management / إدارة امتثال المزرعة
- Checklist response tracking / تتبع استجابة قائمة التحقق
- Non-conformance management / إدارة عدم المطابقة
- Compliance reporting and analytics / تقارير وتحليلات الامتثال

Created: 2025-12-28
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from uuid import UUID
import asyncpg

from ..database import (
    get_connection,
    transaction,
    registrations_repo,
    compliance_repo,
    checklist_repo,
    non_conformance_repo,
)

logger = logging.getLogger("globalgap-compliance")


# =============================================================================
# Main Compliance Repository
# مستودع الامتثال الرئيسي
# =============================================================================

class ComplianceRepository:
    """
    Comprehensive repository for GlobalGAP compliance operations
    مستودع شامل لعمليات الامتثال لـ GlobalGAP

    This repository provides high-level business logic methods that combine
    multiple data access operations for complex compliance workflows.

    يوفر هذا المستودع طرق منطق الأعمال عالية المستوى التي تجمع بين
    عمليات الوصول إلى البيانات المتعددة لسير عمل الامتثال المعقد.
    """

    def __init__(self):
        """Initialize repository with access to all data repositories"""
        self.registrations = registrations_repo
        self.compliance_records = compliance_repo
        self.checklist_responses = checklist_repo
        self.non_conformances = non_conformance_repo

    # =========================================================================
    # Farm Compliance Methods
    # طرق امتثال المزرعة
    # =========================================================================

    async def get_farm_compliance(
        self,
        farm_id: UUID,
        include_history: bool = True,
        include_responses: bool = False,
        include_non_conformances: bool = False
    ) -> Dict[str, Any]:
        """
        Get comprehensive compliance information for a farm
        الحصول على معلومات الامتثال الشاملة للمزرعة

        Args:
            farm_id: Farm identifier / معرف المزرعة
            include_history: Include historical compliance records / تضمين سجلات الامتثال التاريخية
            include_responses: Include checklist responses / تضمين استجابات قائمة التحقق
            include_non_conformances: Include non-conformances / تضمين عدم المطابقات

        Returns:
            Comprehensive farm compliance data / بيانات امتثال المزرعة الشاملة
        """
        try:
            # Get farm registrations / الحصول على تسجيلات المزرعة
            registrations = await self.registrations.get_by_farm_id(farm_id)

            if not registrations:
                return {
                    "farm_id": str(farm_id),
                    "registrations": [],
                    "compliance_status": "NOT_REGISTERED",
                    "message": "No GlobalGAP registrations found for this farm"
                }

            result = {
                "farm_id": str(farm_id),
                "registrations": registrations,
                "compliance_records": [],
                "summary": {}
            }

            # Get compliance records for each registration
            # الحصول على سجلات الامتثال لكل تسجيل
            all_compliance_records = []

            for registration in registrations:
                reg_id = registration['id']

                if include_history:
                    records = await self.compliance_records.get_by_registration(reg_id)
                else:
                    latest = await self.compliance_records.get_latest_by_registration(reg_id)
                    records = [latest] if latest else []

                # Enhance records with additional data
                # تحسين السجلات ببيانات إضافية
                for record in records:
                    record['registration'] = registration

                    if include_responses:
                        record['responses'] = await self.checklist_responses.get_by_compliance_record(
                            record['id']
                        )
                        record['non_compliant_count'] = sum(
                            1 for r in record['responses'] if r['response'] == 'NON_COMPLIANT'
                        )

                    if include_non_conformances:
                        record['non_conformances'] = await self.non_conformances.get_by_compliance_record(
                            record['id']
                        )
                        record['open_nc_count'] = sum(
                            1 for nc in record['non_conformances']
                            if nc['status'] in ('OPEN', 'IN_PROGRESS')
                        )

                    all_compliance_records.append(record)

            result['compliance_records'] = all_compliance_records

            # Calculate summary statistics / حساب الإحصائيات الموجزة
            result['summary'] = await self._calculate_farm_summary(
                registrations,
                all_compliance_records
            )

            return result

        except Exception as e:
            logger.error(f"Error getting farm compliance for {farm_id}: {e}")
            raise

    async def _calculate_farm_summary(
        self,
        registrations: List[Dict[str, Any]],
        compliance_records: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate summary statistics for farm compliance
        حساب الإحصائيات الموجزة لامتثال المزرعة
        """
        active_registrations = [r for r in registrations if r['certificate_status'] == 'ACTIVE']
        latest_records = sorted(
            compliance_records,
            key=lambda x: x['audit_date'] if x['audit_date'] else date.min,
            reverse=True
        )

        summary = {
            "total_registrations": len(registrations),
            "active_registrations": len(active_registrations),
            "total_audits": len(compliance_records),
            "latest_audit_date": latest_records[0]['audit_date'] if latest_records else None,
        }

        if latest_records:
            latest = latest_records[0]
            summary.update({
                "current_compliance_score": latest.get('overall_compliance'),
                "current_major_must_score": latest.get('major_must_score'),
                "current_minor_must_score": latest.get('minor_must_score'),
                "compliance_trend": await self._calculate_compliance_trend(compliance_records),
            })

        return summary

    async def _calculate_compliance_trend(
        self,
        compliance_records: List[Dict[str, Any]]
    ) -> str:
        """
        Calculate compliance trend (improving/declining/stable)
        حساب اتجاه الامتثال (تحسين/تراجع/مستقر)
        """
        if len(compliance_records) < 2:
            return "INSUFFICIENT_DATA"

        sorted_records = sorted(
            compliance_records,
            key=lambda x: x['audit_date'] if x['audit_date'] else date.min
        )

        recent = sorted_records[-2:]
        if recent[0].get('overall_compliance') and recent[1].get('overall_compliance'):
            diff = recent[1]['overall_compliance'] - recent[0]['overall_compliance']

            if diff > 5:
                return "IMPROVING"
            elif diff < -5:
                return "DECLINING"
            else:
                return "STABLE"

        return "UNKNOWN"

    # =========================================================================
    # Checklist Response Methods
    # طرق استجابة قائمة التحقق
    # =========================================================================

    async def save_checklist_response(
        self,
        compliance_record_id: UUID,
        checklist_item_id: str,
        response: str,
        evidence_path: Optional[str] = None,
        notes: Optional[str] = None,
        auto_create_non_conformance: bool = True
    ) -> Dict[str, Any]:
        """
        Save a checklist response and optionally create non-conformance
        حفظ استجابة قائمة التحقق واختياريًا إنشاء عدم مطابقة

        Args:
            compliance_record_id: Compliance record ID / معرف سجل الامتثال
            checklist_item_id: Checklist item ID / معرف عنصر قائمة التحقق
            response: Response value / قيمة الاستجابة
            evidence_path: Path to evidence / المسار إلى الأدلة
            notes: Additional notes / ملاحظات إضافية
            auto_create_non_conformance: Auto-create NC for non-compliant / إنشاء NC تلقائيًا لغير المتوافق

        Returns:
            Created response with optional non-conformance / الاستجابة المنشأة مع عدم المطابقة الاختياري
        """
        try:
            async with transaction() as conn:
                # Create the checklist response
                # إنشاء استجابة قائمة التحقق
                query = """
                    INSERT INTO checklist_responses (
                        compliance_record_id, checklist_item_id, response,
                        evidence_path, notes
                    )
                    VALUES ($1, $2, $3, $4, $5)
                    RETURNING *
                """

                row = await conn.fetchrow(
                    query, compliance_record_id, checklist_item_id, response,
                    evidence_path, notes
                )
                response_data = dict(row)

                # Auto-create non-conformance if response is NON_COMPLIANT
                # إنشاء عدم المطابقة تلقائيًا إذا كانت الاستجابة غير متوافقة
                if auto_create_non_conformance and response == 'NON_COMPLIANT':
                    nc_query = """
                        INSERT INTO non_conformances (
                            compliance_record_id, checklist_item_id, severity,
                            description, status
                        )
                        VALUES ($1, $2, 'MAJOR', $3, 'OPEN')
                        RETURNING *
                    """

                    nc_description = f"Non-compliance identified for {checklist_item_id}"
                    if notes:
                        nc_description += f": {notes}"

                    nc_row = await conn.fetchrow(
                        nc_query, compliance_record_id, checklist_item_id, nc_description
                    )
                    response_data['non_conformance'] = dict(nc_row) if nc_row else None

                logger.info(
                    f"Saved checklist response: {checklist_item_id} = {response}"
                )

                return response_data

        except Exception as e:
            logger.error(f"Error saving checklist response: {e}")
            raise

    async def save_checklist_responses_batch(
        self,
        compliance_record_id: UUID,
        responses: List[Dict[str, Any]],
        auto_create_non_conformances: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Save multiple checklist responses in a batch with transaction
        حفظ استجابات قائمة التحقق المتعددة دفعة واحدة مع المعاملة

        Args:
            compliance_record_id: Compliance record ID / معرف سجل الامتثال
            responses: List of response dictionaries / قائمة قواميس الاستجابة
            auto_create_non_conformances: Auto-create NCs / إنشاء NCs تلقائيًا

        Returns:
            List of created responses / قائمة الاستجابات المنشأة
        """
        try:
            results = []

            async with transaction() as conn:
                for resp in responses:
                    result = await self.save_checklist_response(
                        compliance_record_id=compliance_record_id,
                        checklist_item_id=resp['checklist_item_id'],
                        response=resp['response'],
                        evidence_path=resp.get('evidence_path'),
                        notes=resp.get('notes'),
                        auto_create_non_conformance=auto_create_non_conformances
                    )
                    results.append(result)

            logger.info(f"Saved {len(results)} checklist responses in batch")
            return results

        except Exception as e:
            logger.error(f"Error saving checklist responses batch: {e}")
            raise

    # =========================================================================
    # Non-Conformance Methods
    # طرق عدم المطابقة
    # =========================================================================

    async def create_non_conformance(
        self,
        compliance_record_id: UUID,
        checklist_item_id: str,
        severity: str,
        description: str,
        corrective_action: Optional[str] = None,
        due_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Create a non-conformance record
        إنشاء سجل عدم المطابقة

        Args:
            compliance_record_id: Compliance record ID / معرف سجل الامتثال
            checklist_item_id: Checklist item ID / معرف عنصر قائمة التحقق
            severity: Severity level (MAJOR/MINOR/RECOMMENDATION) / مستوى الخطورة
            description: Description of non-conformance / وصف عدم المطابقة
            corrective_action: Planned corrective action / الإجراء التصحيحي المخطط
            due_date: Due date for resolution / تاريخ الاستحقاق للحل

        Returns:
            Created non-conformance record / سجل عدم المطابقة المنشأ
        """
        try:
            # Auto-calculate due date based on severity if not provided
            # حساب تاريخ الاستحقاق تلقائيًا بناءً على الخطورة إذا لم يتم توفيره
            if due_date is None:
                days_offset = 30 if severity == 'MAJOR' else 60
                due_date = date.today() + timedelta(days=days_offset)

            nc = await self.non_conformances.create(
                compliance_record_id=compliance_record_id,
                checklist_item_id=checklist_item_id,
                severity=severity,
                description=description,
                corrective_action=corrective_action,
                due_date=due_date,
                status='OPEN'
            )

            logger.info(
                f"Created {severity} non-conformance for {checklist_item_id}"
            )

            return nc

        except Exception as e:
            logger.error(f"Error creating non-conformance: {e}")
            raise

    async def update_non_conformance_status(
        self,
        nc_id: UUID,
        status: str,
        corrective_action: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update non-conformance status with validation
        تحديث حالة عدم المطابقة مع التحقق
        """
        try:
            resolved_date = None
            if status in ('RESOLVED', 'VERIFIED'):
                resolved_date = date.today()

            nc = await self.non_conformances.update_status(
                nc_id=nc_id,
                status=status,
                corrective_action=corrective_action,
                resolved_date=resolved_date
            )

            logger.info(f"Updated non-conformance {nc_id} to status {status}")
            return nc

        except Exception as e:
            logger.error(f"Error updating non-conformance status: {e}")
            raise

    # =========================================================================
    # Reporting and Analytics Methods
    # طرق التقارير والتحليلات
    # =========================================================================

    async def get_compliance_summary_report(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        min_compliance_threshold: float = 80.0
    ) -> Dict[str, Any]:
        """
        Generate comprehensive compliance summary report
        إنشاء تقرير موجز شامل للامتثال

        Args:
            start_date: Report start date / تاريخ بداية التقرير
            end_date: Report end date / تاريخ نهاية التقرير
            min_compliance_threshold: Minimum acceptable compliance / الحد الأدنى للامتثال المقبول

        Returns:
            Comprehensive compliance report / تقرير الامتثال الشامل
        """
        try:
            async with get_connection() as conn:
                # Build date filter / بناء فلتر التاريخ
                date_filter = ""
                params = []

                if start_date and end_date:
                    date_filter = "AND cr.audit_date BETWEEN $1 AND $2"
                    params = [start_date, end_date]
                elif start_date:
                    date_filter = "AND cr.audit_date >= $1"
                    params = [start_date]
                elif end_date:
                    date_filter = "AND cr.audit_date <= $1"
                    params = [end_date]

                # Get overall compliance statistics
                # الحصول على إحصائيات الامتثال الإجمالية
                query = f"""
                    SELECT
                        COUNT(DISTINCT gr.farm_id) as total_farms,
                        COUNT(DISTINCT gr.id) as total_registrations,
                        COUNT(cr.id) as total_audits,
                        AVG(cr.overall_compliance) as avg_compliance,
                        AVG(cr.major_must_score) as avg_major_must,
                        AVG(cr.minor_must_score) as avg_minor_must,
                        MIN(cr.overall_compliance) as min_compliance,
                        MAX(cr.overall_compliance) as max_compliance,
                        COUNT(CASE WHEN cr.overall_compliance < ${'3' if params else '1'} THEN 1 END) as below_threshold_count
                    FROM compliance_records cr
                    JOIN globalgap_registrations gr ON cr.registration_id = gr.id
                    WHERE 1=1 {date_filter}
                """

                if params:
                    params.append(min_compliance_threshold)
                else:
                    params = [min_compliance_threshold]

                stats = await conn.fetchrow(query, *params)

                # Get non-conformance statistics
                # الحصول على إحصائيات عدم المطابقة
                nc_query = f"""
                    SELECT
                        COUNT(*) as total_non_conformances,
                        COUNT(CASE WHEN severity = 'MAJOR' THEN 1 END) as major_count,
                        COUNT(CASE WHEN severity = 'MINOR' THEN 1 END) as minor_count,
                        COUNT(CASE WHEN status IN ('OPEN', 'IN_PROGRESS') THEN 1 END) as open_count,
                        COUNT(CASE WHEN status = 'RESOLVED' THEN 1 END) as resolved_count,
                        COUNT(CASE WHEN due_date < CURRENT_DATE AND status IN ('OPEN', 'IN_PROGRESS') THEN 1 END) as overdue_count
                    FROM non_conformances nc
                    JOIN compliance_records cr ON nc.compliance_record_id = cr.id
                    WHERE 1=1 {date_filter}
                """

                nc_stats = await conn.fetchrow(
                    nc_query,
                    *(params[:-1] if params else [])  # Exclude threshold param
                )

                # Get compliance by scope
                # الحصول على الامتثال حسب النطاق
                scope_query = f"""
                    SELECT
                        gr.scope,
                        COUNT(cr.id) as audit_count,
                        AVG(cr.overall_compliance) as avg_compliance,
                        AVG(cr.major_must_score) as avg_major_must,
                        AVG(cr.minor_must_score) as avg_minor_must
                    FROM compliance_records cr
                    JOIN globalgap_registrations gr ON cr.registration_id = gr.id
                    WHERE gr.scope IS NOT NULL {date_filter}
                    GROUP BY gr.scope
                    ORDER BY avg_compliance DESC
                """

                scope_stats = await conn.fetch(
                    scope_query,
                    *(params[:-1] if params else [])
                )

                return {
                    "report_period": {
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                    "overall_statistics": dict(stats) if stats else {},
                    "non_conformance_statistics": dict(nc_stats) if nc_stats else {},
                    "compliance_by_scope": [dict(row) for row in scope_stats],
                    "threshold": min_compliance_threshold,
                    "generated_at": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Error generating compliance summary report: {e}")
            raise

    async def get_farm_compliance_history(
        self,
        farm_id: UUID,
        limit: Optional[int] = 10
    ) -> List[Dict[str, Any]]:
        """
        Get compliance history for a farm with trend analysis
        الحصول على سجل الامتثال للمزرعة مع تحليل الاتجاه
        """
        try:
            async with get_connection() as conn:
                query = """
                    SELECT
                        cr.*,
                        gr.ggn,
                        gr.scope,
                        gr.certificate_status,
                        COUNT(DISTINCT chk.id) as total_responses,
                        COUNT(DISTINCT CASE WHEN chk.response = 'NON_COMPLIANT' THEN chk.id END) as non_compliant_count,
                        COUNT(DISTINCT nc.id) as non_conformance_count,
                        COUNT(DISTINCT CASE WHEN nc.status IN ('OPEN', 'IN_PROGRESS') THEN nc.id END) as open_nc_count
                    FROM compliance_records cr
                    JOIN globalgap_registrations gr ON cr.registration_id = gr.id
                    LEFT JOIN checklist_responses chk ON chk.compliance_record_id = cr.id
                    LEFT JOIN non_conformances nc ON nc.compliance_record_id = cr.id
                    WHERE gr.farm_id = $1
                    GROUP BY cr.id, gr.id
                    ORDER BY cr.audit_date DESC, cr.created_at DESC
                    LIMIT $2
                """

                rows = await conn.fetch(query, farm_id, limit or 10)
                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error getting farm compliance history: {e}")
            raise

    async def get_checklist_item_analysis(
        self,
        checklist_item_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Analyze compliance patterns for a specific checklist item
        تحليل أنماط الامتثال لعنصر قائمة التحقق المحدد
        """
        try:
            async with get_connection() as conn:
                date_filter = ""
                params = [checklist_item_id]

                if start_date and end_date:
                    date_filter = "AND cr.audit_date BETWEEN $2 AND $3"
                    params.extend([start_date, end_date])
                elif start_date:
                    date_filter = "AND cr.audit_date >= $2"
                    params.append(start_date)
                elif end_date:
                    date_filter = "AND cr.audit_date <= $2"
                    params.append(end_date)

                query = f"""
                    SELECT
                        chk.response,
                        COUNT(*) as response_count,
                        COUNT(DISTINCT cr.registration_id) as affected_farms,
                        AVG(cr.overall_compliance) as avg_farm_compliance
                    FROM checklist_responses chk
                    JOIN compliance_records cr ON chk.compliance_record_id = cr.id
                    WHERE chk.checklist_item_id = $1 {date_filter}
                    GROUP BY chk.response
                    ORDER BY response_count DESC
                """

                response_stats = await conn.fetch(query, *params)

                # Get non-conformances for this item
                # الحصول على عدم المطابقات لهذا العنصر
                nc_query = f"""
                    SELECT
                        COUNT(*) as total_non_conformances,
                        COUNT(CASE WHEN status IN ('OPEN', 'IN_PROGRESS') THEN 1 END) as open_count,
                        AVG(EXTRACT(EPOCH FROM (COALESCE(resolved_date, CURRENT_DATE) - cr.audit_date)) / 86400) as avg_resolution_days
                    FROM non_conformances nc
                    JOIN compliance_records cr ON nc.compliance_record_id = cr.id
                    WHERE nc.checklist_item_id = $1 {date_filter}
                """

                nc_stats = await conn.fetchrow(nc_query, *params)

                return {
                    "checklist_item_id": checklist_item_id,
                    "analysis_period": {
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                    "response_distribution": [dict(row) for row in response_stats],
                    "non_conformance_statistics": dict(nc_stats) if nc_stats else {},
                    "generated_at": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Error analyzing checklist item {checklist_item_id}: {e}")
            raise

    async def get_overdue_corrective_actions(
        self,
        severity: Optional[str] = None,
        days_overdue: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get overdue corrective actions with farm and audit details
        الحصول على الإجراءات التصحيحية المتأخرة مع تفاصيل المزرعة والتدقيق
        """
        try:
            async with get_connection() as conn:
                filters = ["nc.status IN ('OPEN', 'IN_PROGRESS')", "nc.due_date < CURRENT_DATE"]
                params = []

                if severity:
                    filters.append(f"nc.severity = ${len(params) + 1}")
                    params.append(severity)

                if days_overdue:
                    filters.append(f"nc.due_date < CURRENT_DATE - ${len(params) + 1}::interval")
                    params.append(f"{days_overdue} days")

                where_clause = " AND ".join(filters)

                query = f"""
                    SELECT
                        nc.*,
                        cr.audit_date,
                        cr.registration_id,
                        gr.farm_id,
                        gr.ggn,
                        gr.scope,
                        CURRENT_DATE - nc.due_date as days_overdue
                    FROM non_conformances nc
                    JOIN compliance_records cr ON nc.compliance_record_id = cr.id
                    JOIN globalgap_registrations gr ON cr.registration_id = gr.id
                    WHERE {where_clause}
                    ORDER BY nc.severity DESC, days_overdue DESC, nc.due_date ASC
                """

                rows = await conn.fetch(query, *params)
                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error getting overdue corrective actions: {e}")
            raise

    async def get_expiring_certificates_report(
        self,
        days_ahead: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Get certificates expiring within specified days with compliance status
        الحصول على الشهادات المنتهية الصلاحية خلال أيام محددة مع حالة الامتثال
        """
        try:
            async with get_connection() as conn:
                query = """
                    SELECT
                        gr.*,
                        CURRENT_DATE - gr.valid_to as days_until_expiry,
                        cr.overall_compliance as latest_compliance,
                        cr.audit_date as latest_audit_date,
                        COUNT(DISTINCT nc.id) FILTER (WHERE nc.status IN ('OPEN', 'IN_PROGRESS')) as open_nc_count
                    FROM globalgap_registrations gr
                    LEFT JOIN LATERAL (
                        SELECT * FROM compliance_records
                        WHERE registration_id = gr.id
                        ORDER BY audit_date DESC, created_at DESC
                        LIMIT 1
                    ) cr ON true
                    LEFT JOIN compliance_records cr2 ON cr2.id = cr.id
                    LEFT JOIN non_conformances nc ON nc.compliance_record_id = cr2.id
                    WHERE gr.certificate_status = 'ACTIVE'
                      AND gr.valid_to IS NOT NULL
                      AND gr.valid_to <= CURRENT_DATE + $1::interval
                    GROUP BY gr.id, cr.id, cr.overall_compliance, cr.audit_date
                    ORDER BY gr.valid_to ASC
                """

                rows = await conn.fetch(query, f"{days_ahead} days")
                return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error getting expiring certificates report: {e}")
            raise

    async def get_compliance_trends(
        self,
        farm_id: Optional[UUID] = None,
        months: int = 12
    ) -> Dict[str, Any]:
        """
        Get compliance trends over time with monthly aggregation
        الحصول على اتجاهات الامتثال مع مرور الوقت مع التجميع الشهري
        """
        try:
            async with get_connection() as conn:
                farm_filter = ""
                params = [months]

                if farm_id:
                    farm_filter = "AND gr.farm_id = $2"
                    params.append(farm_id)

                query = f"""
                    SELECT
                        DATE_TRUNC('month', cr.audit_date) as month,
                        COUNT(DISTINCT gr.farm_id) as farms_audited,
                        COUNT(cr.id) as total_audits,
                        AVG(cr.overall_compliance) as avg_compliance,
                        AVG(cr.major_must_score) as avg_major_must,
                        AVG(cr.minor_must_score) as avg_minor_must,
                        COUNT(DISTINCT nc.id) as total_non_conformances,
                        COUNT(DISTINCT nc.id) FILTER (WHERE nc.severity = 'MAJOR') as major_nc_count
                    FROM compliance_records cr
                    JOIN globalgap_registrations gr ON cr.registration_id = gr.id
                    LEFT JOIN non_conformances nc ON nc.compliance_record_id = cr.id
                    WHERE cr.audit_date >= CURRENT_DATE - $1::interval {farm_filter}
                    GROUP BY DATE_TRUNC('month', cr.audit_date)
                    ORDER BY month DESC
                """

                rows = await conn.fetch(query, f"{months} months", *params[1:])

                return {
                    "period_months": months,
                    "farm_id": str(farm_id) if farm_id else None,
                    "monthly_trends": [dict(row) for row in rows],
                    "generated_at": datetime.now().isoformat(),
                }

        except Exception as e:
            logger.error(f"Error getting compliance trends: {e}")
            raise

    # =========================================================================
    # Bulk Operations
    # العمليات المجمعة
    # =========================================================================

    async def create_compliance_record_with_responses(
        self,
        registration_id: UUID,
        checklist_version: str,
        audit_date: date,
        responses: List[Dict[str, Any]],
        auditor_notes: Optional[str] = None,
        calculate_scores: bool = True
    ) -> Dict[str, Any]:
        """
        Create a complete compliance record with all responses in one transaction
        إنشاء سجل امتثال كامل مع جميع الاستجابات في معاملة واحدة
        """
        try:
            async with transaction() as conn:
                # Create compliance record
                # إنشاء سجل الامتثال
                record_query = """
                    INSERT INTO compliance_records (
                        registration_id, checklist_version, audit_date, auditor_notes
                    )
                    VALUES ($1, $2, $3, $4)
                    RETURNING *
                """

                record = await conn.fetchrow(
                    record_query, registration_id, checklist_version,
                    audit_date, auditor_notes
                )
                compliance_record = dict(record)
                compliance_record_id = record['id']

                # Save all responses
                # حفظ جميع الاستجابات
                saved_responses = []
                non_conformances = []

                for resp in responses:
                    # Save response
                    resp_query = """
                        INSERT INTO checklist_responses (
                            compliance_record_id, checklist_item_id, response,
                            evidence_path, notes
                        )
                        VALUES ($1, $2, $3, $4, $5)
                        RETURNING *
                    """

                    resp_row = await conn.fetchrow(
                        resp_query,
                        compliance_record_id,
                        resp['checklist_item_id'],
                        resp['response'],
                        resp.get('evidence_path'),
                        resp.get('notes')
                    )
                    saved_responses.append(dict(resp_row))

                    # Create non-conformance if needed
                    if resp['response'] == 'NON_COMPLIANT':
                        nc_query = """
                            INSERT INTO non_conformances (
                                compliance_record_id, checklist_item_id, severity,
                                description, status
                            )
                            VALUES ($1, $2, $3, $4, 'OPEN')
                            RETURNING *
                        """

                        severity = resp.get('severity', 'MAJOR')
                        description = resp.get('nc_description',
                            f"Non-compliance for {resp['checklist_item_id']}")

                        nc_row = await conn.fetchrow(
                            nc_query, compliance_record_id,
                            resp['checklist_item_id'], severity, description
                        )
                        non_conformances.append(dict(nc_row))

                # Calculate scores if requested
                # حساب الدرجات إذا طلب ذلك
                if calculate_scores:
                    scores = self._calculate_compliance_scores(saved_responses)

                    update_query = """
                        UPDATE compliance_records
                        SET major_must_score = $2,
                            minor_must_score = $3,
                            overall_compliance = $4
                        WHERE id = $1
                        RETURNING *
                    """

                    updated_record = await conn.fetchrow(
                        update_query, compliance_record_id,
                        scores['major_must_score'],
                        scores['minor_must_score'],
                        scores['overall_compliance']
                    )
                    compliance_record = dict(updated_record)

                compliance_record['responses'] = saved_responses
                compliance_record['non_conformances'] = non_conformances

                logger.info(
                    f"Created compliance record {compliance_record_id} with "
                    f"{len(saved_responses)} responses and {len(non_conformances)} NCs"
                )

                return compliance_record

        except Exception as e:
            logger.error(f"Error creating compliance record with responses: {e}")
            raise

    def _calculate_compliance_scores(
        self,
        responses: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Calculate compliance scores from responses
        حساب درجات الامتثال من الاستجابات

        This is a simplified calculation. In production, you would need to:
        1. Differentiate between Major Must and Minor Must items
        2. Apply proper weighting based on checklist version
        3. Follow official GlobalGAP scoring rules

        هذا حساب مبسط. في الإنتاج، ستحتاج إلى:
        1. التمييز بين العناصر الرئيسية الإلزامية والفرعية الإلزامية
        2. تطبيق الترجيح المناسب بناءً على إصدار قائمة التحقق
        3. اتباع قواعد التسجيل الرسمية لـ GlobalGAP
        """
        if not responses:
            return {
                "major_must_score": 0.0,
                "minor_must_score": 0.0,
                "overall_compliance": 0.0,
            }

        total = len(responses)
        compliant = sum(1 for r in responses if r['response'] == 'COMPLIANT')
        non_compliant = sum(1 for r in responses if r['response'] == 'NON_COMPLIANT')
        not_applicable = sum(1 for r in responses if r['response'] == 'NOT_APPLICABLE')

        # Calculate scores (simplified)
        applicable = total - not_applicable
        if applicable == 0:
            compliance_rate = 100.0
        else:
            compliance_rate = (compliant / applicable) * 100.0

        return {
            "major_must_score": compliance_rate,  # Simplified
            "minor_must_score": compliance_rate,  # Simplified
            "overall_compliance": compliance_rate,
        }


# =============================================================================
# Export
# تصدير
# =============================================================================

__all__ = ["ComplianceRepository"]
