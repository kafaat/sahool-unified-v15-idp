"""
Pesticide Compliance Checker - فاحص الامتثال للمبيدات
Main compliance checking logic for PHI, REI, tank mix, and drift risk
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from .database import (
    PPE_ENHANCED,
    PPE_MAXIMUM,
    get_pesticide,
)
from .models import (
    ComplianceCheck,
    ComplianceStatus,
    MixCompatibility,
    PesticideApplication,
    PHIViolation,
    PPERequirement,
    REIViolation,
    SprayDriftRisk,
    TankMixCompatibility,
)


class PesticideComplianceChecker:
    """
    Main compliance checker class - فاحص الامتثال الرئيسي

    Provides comprehensive pesticide safety compliance checking including:
    - Pre-Harvest Interval (PHI) - فترة ما قبل الحصاد
    - Re-Entry Interval (REI) - فترة إعادة الدخول
    - Tank mix compatibility - توافق خلطات الخزان
    - Spray drift risk assessment - تقييم مخاطر انجراف الرش
    """

    def __init__(self):
        self.applications: list[PesticideApplication] = []

    def add_application(self, application: PesticideApplication) -> None:
        """Add a pesticide application record"""
        pesticide = get_pesticide(application.pesticide_id)
        if pesticide:
            # Calculate PHI and REI expiry
            application.phi_expiry_date = application.application_date + timedelta(days=pesticide.phi_days)
            application.rei_expiry_time = application.application_date + timedelta(hours=pesticide.rei_hours)
        self.applications.append(application)

    def check_phi_compliance(
        self,
        field_id: str,
        planned_harvest_date: datetime,
        check_date: datetime | None = None,
    ) -> list[PHIViolation]:
        """
        Check Pre-Harvest Interval compliance - فحص فترة ما قبل الحصاد

        Returns list of violations if harvest is planned too early
        """
        if check_date is None:
            check_date = datetime.now(UTC)

        violations = []

        # Get applications for this field
        field_applications = [
            app for app in self.applications if app.field_id == field_id and app.application_date <= check_date
        ]

        for app in field_applications:
            pesticide = get_pesticide(app.pesticide_id)
            if not pesticide:
                continue

            earliest_harvest = app.application_date + timedelta(days=pesticide.phi_days)
            days_remaining = (earliest_harvest - planned_harvest_date).days

            if planned_harvest_date < earliest_harvest:
                status = ComplianceStatus.VIOLATION
                if days_remaining <= 3:
                    status = ComplianceStatus.CRITICAL

                violation = PHIViolation(
                    field_id=field_id,
                    pesticide_id=pesticide.id,
                    pesticide_name=pesticide.trade_name,
                    pesticide_name_ar=pesticide.trade_name_ar,
                    application_date=app.application_date,
                    phi_days=pesticide.phi_days,
                    earliest_harvest_date=earliest_harvest,
                    planned_harvest_date=planned_harvest_date,
                    days_remaining=days_remaining,
                    status=status,
                    message_en=f"Harvest planned {abs(days_remaining)} days too early. "
                    f"{pesticide.trade_name} requires {pesticide.phi_days} day PHI.",
                    message_ar=f"الحصاد مخطط له مبكراً بـ {abs(days_remaining)} يوم. "
                    f"{pesticide.trade_name_ar} يتطلب فترة {pesticide.phi_days} يوم قبل الحصاد.",
                    recommendations_en=[
                        f"Delay harvest until {earliest_harvest.strftime('%Y-%m-%d')}",
                        "Test produce for pesticide residue before sale",
                        "Consider market channels with different PHI requirements",
                    ],
                    recommendations_ar=[
                        f"أجّل الحصاد حتى {earliest_harvest.strftime('%Y-%m-%d')}",
                        "افحص المنتج لمتبقيات المبيدات قبل البيع",
                        "فكر في قنوات تسويق بمتطلبات PHI مختلفة",
                    ],
                )
                violations.append(violation)

        return violations

    def check_rei_compliance(
        self,
        field_id: str,
        entry_time: datetime | None = None,
    ) -> list[REIViolation]:
        """
        Check Re-Entry Interval compliance - فحص فترة إعادة الدخول

        Returns list of violations if field entry is too early
        """
        if entry_time is None:
            entry_time = datetime.now(UTC)

        violations = []

        # Get recent applications for this field
        field_applications = [app for app in self.applications if app.field_id == field_id]

        for app in field_applications:
            pesticide = get_pesticide(app.pesticide_id)
            if not pesticide:
                continue

            safe_entry_time = app.application_date + timedelta(hours=pesticide.rei_hours)

            if entry_time < safe_entry_time:
                hours_remaining = (safe_entry_time - entry_time).total_seconds() / 3600
                status = ComplianceStatus.VIOLATION
                if hours_remaining <= 4:
                    status = ComplianceStatus.WARNING

                # Get PPE for early entry
                early_entry_ppe = None
                if hours_remaining <= (pesticide.rei_hours / 2):
                    early_entry_ppe = PPE_MAXIMUM if pesticide.toxicity_class.value in ["Ia", "Ib"] else PPE_ENHANCED

                violation = REIViolation(
                    field_id=field_id,
                    pesticide_id=pesticide.id,
                    pesticide_name=pesticide.trade_name,
                    pesticide_name_ar=pesticide.trade_name_ar,
                    application_date=app.application_date,
                    rei_hours=pesticide.rei_hours,
                    safe_entry_time=safe_entry_time,
                    status=status,
                    message_en=f"Field entry too early. {pesticide.trade_name} requires "
                    f"{pesticide.rei_hours} hour REI. Safe entry at {safe_entry_time.strftime('%Y-%m-%d %H:%M')}",
                    message_ar=f"دخول الحقل مبكر جداً. {pesticide.trade_name_ar} يتطلب "
                    f"فترة {pesticide.rei_hours} ساعة. الدخول الآمن في {safe_entry_time.strftime('%Y-%m-%d %H:%M')}",
                    early_entry_ppe=early_entry_ppe,
                )
                violations.append(violation)

        return violations

    def full_compliance_check(
        self,
        field_id: str,
        planned_harvest_date: datetime | None = None,
        weather: dict | None = None,
    ) -> ComplianceCheck:
        """
        Perform full compliance check - فحص الامتثال الشامل
        """
        check_date = datetime.now(UTC)

        # Check PHI if harvest date provided
        phi_violations = []
        phi_status = ComplianceStatus.COMPLIANT
        if planned_harvest_date:
            phi_violations = self.check_phi_compliance(field_id, planned_harvest_date, check_date)
            if any(v.status == ComplianceStatus.CRITICAL for v in phi_violations):
                phi_status = ComplianceStatus.CRITICAL
            elif any(v.status == ComplianceStatus.VIOLATION for v in phi_violations):
                phi_status = ComplianceStatus.VIOLATION

        # Check REI
        rei_violations = self.check_rei_compliance(field_id, check_date)
        rei_status = ComplianceStatus.COMPLIANT
        if any(v.status == ComplianceStatus.VIOLATION for v in rei_violations):
            rei_status = ComplianceStatus.VIOLATION

        # Check tank mix for recent applications
        tank_mix_issues = []
        tank_mix_status = ComplianceStatus.COMPLIANT
        recent_apps = [app for app in self.applications if app.field_id == field_id and len(app.tank_mix_products) > 1]
        for app in recent_apps:
            for i, product_a in enumerate(app.tank_mix_products):
                for product_b in app.tank_mix_products[i + 1 :]:
                    issue = check_tank_mix_compatibility(product_a, product_b)
                    if issue.compatibility in [
                        MixCompatibility.INCOMPATIBLE,
                        MixCompatibility.CAUTION,
                    ]:
                        tank_mix_issues.append(issue)
                        if issue.compatibility == MixCompatibility.INCOMPATIBLE:
                            tank_mix_status = ComplianceStatus.VIOLATION

        # Check drift risk if weather provided
        drift_assessment = None
        drift_status = ComplianceStatus.COMPLIANT
        if weather:
            drift_assessment = assess_spray_drift_risk(
                field_id=field_id,
                wind_speed_kmh=weather.get("wind_speed_kmh", 0),
                wind_direction=weather.get("wind_direction", "N"),
                temperature_c=weather.get("temperature_c", 25),
                humidity_percent=weather.get("humidity_percent", 50),
            )
            if drift_assessment.risk_level == "extreme":
                drift_status = ComplianceStatus.CRITICAL
            elif drift_assessment.risk_level == "high":
                drift_status = ComplianceStatus.VIOLATION

        # Determine overall status
        statuses = [phi_status, rei_status, tank_mix_status, drift_status]
        if ComplianceStatus.CRITICAL in statuses:
            overall_status = ComplianceStatus.CRITICAL
        elif ComplianceStatus.VIOLATION in statuses:
            overall_status = ComplianceStatus.VIOLATION
        elif ComplianceStatus.WARNING in statuses:
            overall_status = ComplianceStatus.WARNING
        else:
            overall_status = ComplianceStatus.COMPLIANT

        # Generate summary
        summary_en = self._generate_summary_en(phi_violations, rei_violations, tank_mix_issues, drift_assessment)
        summary_ar = self._generate_summary_ar(phi_violations, rei_violations, tank_mix_issues, drift_assessment)

        # Generate recommendations
        recommendations_en, recommendations_ar = self._generate_recommendations(
            phi_violations, rei_violations, tank_mix_issues, drift_assessment
        )

        return ComplianceCheck(
            field_id=field_id,
            check_date=check_date,
            overall_status=overall_status,
            phi_status=phi_status,
            rei_status=rei_status,
            tank_mix_status=tank_mix_status,
            drift_risk_status=drift_status,
            phi_violations=phi_violations,
            rei_violations=rei_violations,
            tank_mix_issues=tank_mix_issues,
            drift_assessment=drift_assessment,
            summary_en=summary_en,
            summary_ar=summary_ar,
            recommendations_en=recommendations_en,
            recommendations_ar=recommendations_ar,
        )

    def _generate_summary_en(
        self,
        phi_violations: list[PHIViolation],
        rei_violations: list[REIViolation],
        tank_mix_issues: list[TankMixCompatibility],
        drift_assessment: SprayDriftRisk | None,
    ) -> str:
        """Generate English summary"""
        parts = []
        if phi_violations:
            parts.append(f"{len(phi_violations)} PHI violation(s)")
        if rei_violations:
            parts.append(f"{len(rei_violations)} REI violation(s)")
        if tank_mix_issues:
            parts.append(f"{len(tank_mix_issues)} tank mix issue(s)")
        if drift_assessment and not drift_assessment.can_spray:
            parts.append("spray drift risk too high")

        if parts:
            return "Compliance issues found: " + ", ".join(parts)
        return "All compliance checks passed"

    def _generate_summary_ar(
        self,
        phi_violations: list[PHIViolation],
        rei_violations: list[REIViolation],
        tank_mix_issues: list[TankMixCompatibility],
        drift_assessment: SprayDriftRisk | None,
    ) -> str:
        """Generate Arabic summary"""
        parts = []
        if phi_violations:
            parts.append(f"{len(phi_violations)} مخالفة لفترة ما قبل الحصاد")
        if rei_violations:
            parts.append(f"{len(rei_violations)} مخالفة لفترة إعادة الدخول")
        if tank_mix_issues:
            parts.append(f"{len(tank_mix_issues)} مشكلة في خلط المبيدات")
        if drift_assessment and not drift_assessment.can_spray:
            parts.append("خطر انجراف الرش مرتفع جداً")

        if parts:
            return "تم العثور على مشاكل امتثال: " + "، ".join(parts)
        return "جميع فحوصات الامتثال ناجحة"

    def _generate_recommendations(
        self,
        phi_violations: list[PHIViolation],
        rei_violations: list[REIViolation],
        tank_mix_issues: list[TankMixCompatibility],
        drift_assessment: SprayDriftRisk | None,
    ) -> tuple[list[str], list[str]]:
        """Generate recommendations in English and Arabic"""
        rec_en = []
        rec_ar = []

        if phi_violations:
            rec_en.append("Review planned harvest date to ensure PHI compliance")
            rec_ar.append("راجع تاريخ الحصاد المخطط لضمان الامتثال لفترة ما قبل الحصاد")

        if rei_violations:
            rec_en.append("Restrict field access until REI period expires")
            rec_ar.append("قيّد الوصول للحقل حتى انتهاء فترة إعادة الدخول")

        if tank_mix_issues:
            rec_en.append("Review tank mix compatibility before future applications")
            rec_ar.append("راجع توافق خلطات الخزان قبل التطبيقات المستقبلية")

        if drift_assessment and not drift_assessment.can_spray:
            rec_en.extend(drift_assessment.recommendations_en)
            rec_ar.extend(drift_assessment.recommendations_ar)

        return rec_en, rec_ar


def check_phi_compliance(
    pesticide_id: str,
    application_date: datetime,
    planned_harvest_date: datetime,
) -> PHIViolation | None:
    """
    Quick PHI compliance check - فحص سريع لفترة ما قبل الحصاد

    Returns violation if non-compliant, None if compliant
    """
    pesticide = get_pesticide(pesticide_id)
    if not pesticide:
        return None

    earliest_harvest = application_date + timedelta(days=pesticide.phi_days)
    days_remaining = (earliest_harvest - planned_harvest_date).days

    if planned_harvest_date < earliest_harvest:
        status = ComplianceStatus.CRITICAL if days_remaining <= 3 else ComplianceStatus.VIOLATION

        return PHIViolation(
            field_id="",
            pesticide_id=pesticide.id,
            pesticide_name=pesticide.trade_name,
            pesticide_name_ar=pesticide.trade_name_ar,
            application_date=application_date,
            phi_days=pesticide.phi_days,
            earliest_harvest_date=earliest_harvest,
            planned_harvest_date=planned_harvest_date,
            days_remaining=days_remaining,
            status=status,
            message_en=f"⚠️ PHI VIOLATION: Cannot harvest until {earliest_harvest.strftime('%Y-%m-%d')}. "
            f"{pesticide.trade_name} applied on {application_date.strftime('%Y-%m-%d')} "
            f"requires {pesticide.phi_days} day pre-harvest interval.",
            message_ar=f"⚠️ انتهاك فترة ما قبل الحصاد: لا يمكن الحصاد حتى {earliest_harvest.strftime('%Y-%m-%d')}. "
            f"{pesticide.trade_name_ar} المطبق في {application_date.strftime('%Y-%m-%d')} "
            f"يتطلب فترة {pesticide.phi_days} يوم قبل الحصاد.",
            recommendations_en=[
                f"Wait {abs(days_remaining)} more days before harvesting",
                "Document the delay for traceability",
                "Consider testing for pesticide residues before sale",
            ],
            recommendations_ar=[
                f"انتظر {abs(days_remaining)} يوم إضافي قبل الحصاد",
                "وثّق التأخير للتتبع",
                "فكر في فحص متبقيات المبيدات قبل البيع",
            ],
        )

    return None


def check_rei_compliance(
    pesticide_id: str,
    application_date: datetime,
    entry_time: datetime | None = None,
) -> REIViolation | None:
    """
    Quick REI compliance check - فحص سريع لفترة إعادة الدخول

    Returns violation if non-compliant, None if compliant
    """
    if entry_time is None:
        entry_time = datetime.now(UTC)

    pesticide = get_pesticide(pesticide_id)
    if not pesticide:
        return None

    safe_entry_time = application_date + timedelta(hours=pesticide.rei_hours)

    if entry_time < safe_entry_time:
        hours_remaining = (safe_entry_time - entry_time).total_seconds() / 3600
        status = ComplianceStatus.WARNING if hours_remaining <= 4 else ComplianceStatus.VIOLATION

        # Get PPE for early entry
        early_entry_ppe = None
        if hours_remaining <= (pesticide.rei_hours / 2):
            early_entry_ppe = PPE_MAXIMUM if pesticide.toxicity_class.value in ["Ia", "Ib"] else PPE_ENHANCED

        return REIViolation(
            field_id="",
            pesticide_id=pesticide.id,
            pesticide_name=pesticide.trade_name,
            pesticide_name_ar=pesticide.trade_name_ar,
            application_date=application_date,
            rei_hours=pesticide.rei_hours,
            safe_entry_time=safe_entry_time,
            status=status,
            message_en=f"⚠️ REI VIOLATION: Field is unsafe for entry. "
            f"{pesticide.trade_name} requires {pesticide.rei_hours}h REI. "
            f"Safe entry: {safe_entry_time.strftime('%Y-%m-%d %H:%M')}",
            message_ar=f"⚠️ انتهاك فترة إعادة الدخول: الحقل غير آمن للدخول. "
            f"{pesticide.trade_name_ar} يتطلب فترة {pesticide.rei_hours} ساعة. "
            f"الدخول الآمن: {safe_entry_time.strftime('%Y-%m-%d %H:%M')}",
            early_entry_ppe=early_entry_ppe,
        )

    return None


def check_tank_mix_compatibility(
    product_a_id: str,
    product_b_id: str,
) -> TankMixCompatibility:
    """
    Check tank mix compatibility - فحص توافق خلط المبيدات
    """
    from .database import get_tank_mix_compatibility as db_get_compatibility

    product_a = get_pesticide(product_a_id)
    product_b = get_pesticide(product_b_id)

    product_a_name = product_a.trade_name if product_a else product_a_id
    product_b_name = product_b.trade_name if product_b else product_b_id

    compatibility, warnings_en, warnings_ar, mixing_order = db_get_compatibility(product_a_id, product_b_id)

    if compatibility == MixCompatibility.COMPATIBLE:
        message_en = f"✅ {product_a_name} and {product_b_name} are compatible for tank mixing."
        message_ar = f"✅ {product_a_name} و {product_b_name} متوافقان للخلط في الخزان."
    elif compatibility == MixCompatibility.CAUTION:
        message_en = f"⚠️ {product_a_name} and {product_b_name} require caution when mixing."
        message_ar = f"⚠️ {product_a_name} و {product_b_name} يتطلبان حذراً عند الخلط."
    elif compatibility == MixCompatibility.INCOMPATIBLE:
        message_en = f"❌ {product_a_name} and {product_b_name} are INCOMPATIBLE. Do NOT mix."
        message_ar = f"❌ {product_a_name} و {product_b_name} غير متوافقين. لا تخلط."
    else:
        message_en = f"❓ Compatibility of {product_a_name} and {product_b_name} is unknown. Perform jar test."
        message_ar = f"❓ توافق {product_a_name} و {product_b_name} غير معروف. أجرِ اختبار الجرة."

    return TankMixCompatibility(
        product_a_id=product_a_id,
        product_a_name=product_a_name,
        product_b_id=product_b_id,
        product_b_name=product_b_name,
        compatibility=compatibility,
        message_en=message_en,
        message_ar=message_ar,
        warnings_en=warnings_en,
        warnings_ar=warnings_ar,
        mixing_order=mixing_order,
    )


def get_ppe_requirements(pesticide_id: str) -> PPERequirement | None:
    """
    Get PPE requirements for a pesticide - الحصول على متطلبات الحماية الشخصية
    """
    pesticide = get_pesticide(pesticide_id)
    if pesticide:
        return pesticide.ppe_requirements
    return None


def assess_spray_drift_risk(
    field_id: str,
    wind_speed_kmh: float,
    wind_direction: str,
    temperature_c: float,
    humidity_percent: float,
) -> SprayDriftRisk:
    """
    Assess spray drift risk based on weather conditions - تقييم مخاطر انجراف الرش

    Based on:
    - Wind speed (ideal: < 10 km/h, max: 15 km/h)
    - Temperature (ideal: 15-25°C)
    - Humidity (ideal: 40-90%)
    - Delta T (wet bulb depression, ideal: 2-8°C)
    """
    assessment_time = datetime.now(UTC)

    # Calculate Delta T (simplified - assumes 40% RH gives ~8°C delta)
    delta_t = temperature_c * (1 - humidity_percent / 100) * 0.4

    # Determine risk level
    if wind_speed_kmh > 20:
        risk_level = "extreme"
        risk_level_ar = "خطير جداً"
        can_spray = False
        recommended_buffer_m = 500
    elif wind_speed_kmh > 15 or delta_t > 10:
        risk_level = "high"
        risk_level_ar = "مرتفع"
        can_spray = False
        recommended_buffer_m = 300
    elif wind_speed_kmh > 10 or delta_t > 8 or temperature_c > 30:
        risk_level = "medium"
        risk_level_ar = "متوسط"
        can_spray = True
        recommended_buffer_m = 150
    else:
        risk_level = "low"
        risk_level_ar = "منخفض"
        can_spray = True
        recommended_buffer_m = 50

    # Generate recommendations
    recommendations_en = []
    recommendations_ar = []

    if wind_speed_kmh > 15:
        recommendations_en.append(f"Wind speed ({wind_speed_kmh} km/h) too high. Wait for calmer conditions.")
        recommendations_ar.append(f"سرعة الرياح ({wind_speed_kmh} كم/س) مرتفعة جداً. انتظر ظروفاً أهدأ.")

    if delta_t > 8:
        recommendations_en.append("High evaporation conditions. Spray early morning or late evening.")
        recommendations_ar.append("ظروف تبخر عالية. رش في الصباح الباكر أو المساء.")

    if temperature_c > 30:
        recommendations_en.append(f"Temperature ({temperature_c}°C) too high. Risk of phytotoxicity.")
        recommendations_ar.append(f"درجة الحرارة ({temperature_c}°م) مرتفعة جداً. خطر السمية النباتية.")

    if can_spray:
        recommendations_en.append(f"Maintain minimum {recommended_buffer_m}m buffer from sensitive areas.")
        recommendations_ar.append(f"حافظ على مسافة عازلة {recommended_buffer_m} متر من المناطق الحساسة.")
        recommendations_en.append("Use low-drift nozzles and reduce pressure if possible.")
        recommendations_ar.append("استخدم فوهات منخفضة الانجراف وقلل الضغط إن أمكن.")

    # Generate message
    if can_spray:
        message_en = f"✅ Spray conditions acceptable with {risk_level} drift risk. Buffer: {recommended_buffer_m}m"
        message_ar = f"✅ ظروف الرش مقبولة مع خطر انجراف {risk_level_ar}. المسافة العازلة: {recommended_buffer_m}م"
    else:
        message_en = f"❌ DO NOT SPRAY. {risk_level.upper()} drift risk. Wind: {wind_speed_kmh} km/h"
        message_ar = f"❌ لا ترش. خطر انجراف {risk_level_ar}. الرياح: {wind_speed_kmh} كم/س"

    return SprayDriftRisk(
        field_id=field_id,
        assessment_time=assessment_time,
        wind_speed_kmh=wind_speed_kmh,
        wind_direction=wind_direction,
        temperature_c=temperature_c,
        humidity_percent=humidity_percent,
        delta_t=round(delta_t, 1),
        risk_level=risk_level,
        risk_level_ar=risk_level_ar,
        recommended_buffer_m=recommended_buffer_m,
        can_spray=can_spray,
        message_en=message_en,
        message_ar=message_ar,
        recommendations_en=recommendations_en,
        recommendations_ar=recommendations_ar,
    )
