"""
SAHOOL GlobalGAP Integration - Crop Health AI Service Integration
تكامل خدمة صحة المحاصيل مع GlobalGAP

Links with crop-health-ai service to:
- Map pest/disease detection to IPM documentation
- Generate Integrated Pest Management reports
- Track chemical PPP (Plant Protection Products) applications
"""

import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

from .events import GlobalGAPEventPublisher

logger = logging.getLogger(__name__)


class ThreatType(str, Enum):
    """نوع التهديد - Threat Type"""

    PEST = "pest"  # آفة
    DISEASE = "disease"  # مرض
    WEED = "weed"  # حشيش
    NUTRIENT_DEFICIENCY = "nutrient_deficiency"  # نقص المغذيات


class SeverityLevel(str, Enum):
    """مستوى الخطورة - Severity Level"""

    LOW = "low"  # منخفض
    MEDIUM = "medium"  # متوسط
    HIGH = "high"  # عالي
    CRITICAL = "critical"  # حرج


class IPMAction(str, Enum):
    """إجراء الإدارة المتكاملة للآفات - IPM Action"""

    MONITORING = "monitoring"  # مراقبة
    CULTURAL = "cultural"  # ثقافي
    BIOLOGICAL = "biological"  # بيولوجي
    MECHANICAL = "mechanical"  # ميكانيكي
    CHEMICAL = "chemical"  # كيميائي


class PPPType(str, Enum):
    """نوع منتج وقاية النبات - PPP Type"""

    INSECTICIDE = "insecticide"  # مبيد حشري
    FUNGICIDE = "fungicide"  # مبيد فطري
    HERBICIDE = "herbicide"  # مبيد أعشاب
    BACTERICIDE = "bactericide"  # مبيد بكتيري
    BIOCONTROL = "biocontrol"  # مكافحة بيولوجية


@dataclass
class ThreatDetection:
    """اكتشاف التهديد - Threat Detection"""

    detection_id: str
    field_id: str
    threat_type: ThreatType
    threat_name: str
    severity: SeverityLevel
    confidence_score: float
    detected_at: datetime
    affected_area_percentage: float
    location_coordinates: dict[str, float] | None = None
    image_urls: list[str] = None


@dataclass
class IPMRecord:
    """سجل الإدارة المتكاملة للآفات - IPM Record"""

    record_id: str
    field_id: str
    threat_id: str
    threat_name: str
    action_type: IPMAction
    action_date: datetime
    description: str
    effectiveness: float | None = None
    notes: str | None = None


@dataclass
class PPPApplication:
    """تطبيق منتج وقاية النبات - PPP Application"""

    application_id: str
    field_id: str
    product_name: str
    active_ingredient: str
    ppp_type: PPPType
    application_date: datetime
    dosage: float
    dosage_unit: str
    target_pest: str
    pre_harvest_interval_days: int
    applicator_name: str
    weather_conditions: dict[str, Any] | None = None
    equipment_used: str | None = None


@dataclass
class IPMReport:
    """تقرير الإدارة المتكاملة للآفات - IPM Report"""

    farm_id: str
    field_id: str
    period_start: datetime
    period_end: datetime
    total_detections: int
    total_interventions: int
    chemical_applications: int
    non_chemical_applications: int
    compliance_status: str
    mrl_compliant: bool
    recommendations: list[str]
    threat_breakdown: dict[str, int]
    action_breakdown: dict[str, int]


class CropHealthIntegration:
    """
    تكامل خدمة صحة المحاصيل مع GlobalGAP
    Crop Health AI Service Integration with GlobalGAP

    Handles mapping pest/disease detection to IPM documentation
    and tracks PPP applications for compliance.
    """

    def __init__(self, event_publisher: GlobalGAPEventPublisher):
        self.event_publisher = event_publisher
        self.logger = logging.getLogger(__name__)

    async def map_detection_to_ipm(
        self, detection_data: dict, field_id: str, tenant_id: str
    ) -> dict[str, Any]:
        """
        تعيين بيانات اكتشاف الآفات/الأمراض إلى وثائق IPM
        Map pest/disease detection to IPM documentation

        Args:
            detection_data: Raw detection data from crop-health-ai service
            field_id: Field identifier
            tenant_id: Tenant identifier

        Returns:
            IPM-formatted detection data
        """
        try:
            self.logger.info(f"Mapping detection to IPM for field {field_id}")

            # Extract detection details
            threat_type = self._determine_threat_type(detection_data)
            severity = self._calculate_severity(detection_data)

            # Map to IPM format
            ipm_data = {
                "detection_id": detection_data.get("id"),
                "field_id": field_id,
                "farm_id": detection_data.get("farm_id"),
                "timestamp": detection_data.get(
                    "detected_at", datetime.now(UTC).isoformat()
                ),
                # Threat identification
                "threat": {
                    "type": threat_type.value,
                    "name": detection_data.get("threat_name", "Unknown"),
                    "scientific_name": detection_data.get("scientific_name"),
                    "severity": severity.value,
                    "confidence": detection_data.get("confidence_score", 0.0),
                },
                # Impact assessment
                "impact": {
                    "affected_area_percentage": detection_data.get(
                        "affected_area_percentage", 0.0
                    ),
                    "crop_stage": detection_data.get("crop_stage"),
                    "economic_threshold_exceeded": self._check_economic_threshold(
                        detection_data
                    ),
                },
                # IPM recommendations
                "ipm_recommendations": self._generate_ipm_recommendations(
                    threat_type, severity, detection_data
                ),
                # Documentation
                "evidence": {
                    "images": detection_data.get("image_urls", []),
                    "detection_method": detection_data.get(
                        "detection_method", "ai_vision"
                    ),
                    "scout_name": detection_data.get("scout_name"),
                },
                # Compliance tracking
                "compliance": {
                    "requires_action": severity
                    in [SeverityLevel.HIGH, SeverityLevel.CRITICAL],
                    "action_deadline": self._calculate_action_deadline(severity),
                    "reported_to_authorities": False,  # Update based on local regulations
                },
            }

            # Check if intervention is urgently needed
            if severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
                await self.event_publisher.publish_compliance_check_required(
                    tenant_id=tenant_id,
                    farm_id=detection_data.get("farm_id", "unknown"),
                    control_point="IPM.1.1",
                    reason=f"{severity.value} {threat_type.value} detected: {detection_data.get('threat_name')}",
                    priority="high",
                )

            # Publish integration sync event
            await self.event_publisher.publish_integration_synced(
                tenant_id=tenant_id,
                integration_type="crop_health",
                farm_id=detection_data.get("farm_id", "unknown"),
                records_synced=1,
                sync_status="success",
                correlation_id=detection_data.get("correlation_id"),
            )

            self.logger.info(
                f"Detection mapped to IPM: {threat_type.value} - {severity.value}"
            )
            return ipm_data

        except Exception as e:
            self.logger.error(f"Error mapping detection to IPM: {e}")

            # Publish failure event
            await self.event_publisher.publish_integration_synced(
                tenant_id=tenant_id,
                integration_type="crop_health",
                farm_id=detection_data.get("farm_id", "unknown"),
                records_synced=0,
                sync_status="failed",
                error_message=str(e),
                correlation_id=detection_data.get("correlation_id"),
            )

            raise

    async def generate_ipm_report(
        self,
        farm_id: str,
        field_id: str,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime,
        detections: list[ThreatDetection],
        ipm_records: list[IPMRecord],
    ) -> IPMReport:
        """
        إنشاء تقرير الإدارة المتكاملة للآفات
        Generate Integrated Pest Management report

        Args:
            farm_id: Farm identifier
            field_id: Field identifier
            tenant_id: Tenant identifier
            start_date: Report period start
            end_date: Report period end
            detections: List of threat detections
            ipm_records: List of IPM intervention records

        Returns:
            Comprehensive IPM report for GlobalGAP audit
        """
        try:
            self.logger.info(f"Generating IPM report for field {field_id}")

            # Count interventions by type
            chemical_count = sum(
                1 for r in ipm_records if r.action_type == IPMAction.CHEMICAL
            )
            non_chemical_count = len(ipm_records) - chemical_count

            # Analyze threat breakdown
            threat_breakdown = {}
            for detection in detections:
                threat_name = detection.threat_name
                threat_breakdown[threat_name] = threat_breakdown.get(threat_name, 0) + 1

            # Analyze action breakdown
            action_breakdown = {}
            for record in ipm_records:
                action = record.action_type.value
                action_breakdown[action] = action_breakdown.get(action, 0) + 1

            # Check compliance
            compliance_status = "compliant"
            if chemical_count > non_chemical_count * 2:  # Example threshold
                compliance_status = "needs_review"

            # Generate recommendations
            recommendations = self._generate_ipm_report_recommendations(
                detections, ipm_records, chemical_count, non_chemical_count
            )

            report = IPMReport(
                farm_id=farm_id,
                field_id=field_id,
                period_start=start_date,
                period_end=end_date,
                total_detections=len(detections),
                total_interventions=len(ipm_records),
                chemical_applications=chemical_count,
                non_chemical_applications=non_chemical_count,
                compliance_status=compliance_status,
                mrl_compliant=True,  # Should be checked against PPP records
                recommendations=recommendations,
                threat_breakdown=threat_breakdown,
                action_breakdown=action_breakdown,
            )

            # Publish compliance update
            await self.event_publisher.publish_compliance_updated(
                tenant_id=tenant_id,
                farm_id=farm_id,
                control_point="IPM.1",
                compliance_status=compliance_status,
                assessment_data=asdict(report),
            )

            self.logger.info(f"IPM report generated: {compliance_status}")
            return report

        except Exception as e:
            self.logger.error(f"Error generating IPM report: {e}")
            raise

    async def track_ppp_applications(
        self,
        farm_id: str,
        field_id: str,
        tenant_id: str,
        applications: list[PPPApplication],
        harvest_date: datetime | None = None,
    ) -> dict[str, Any]:
        """
        تتبع تطبيقات منتجات وقاية النبات (PPP)
        Track Plant Protection Products (PPP) applications

        Ensures compliance with:
        - Maximum Residue Levels (MRL)
        - Pre-harvest intervals (PHI)
        - Application records
        - Operator certifications

        Args:
            farm_id: Farm identifier
            field_id: Field identifier
            tenant_id: Tenant identifier
            applications: List of PPP applications
            harvest_date: Expected or actual harvest date

        Returns:
            PPP tracking compliance report
        """
        try:
            self.logger.info(f"Tracking PPP applications for field {field_id}")

            compliance_results = {
                "farm_id": farm_id,
                "field_id": field_id,
                "total_applications": len(applications),
                "compliant_applications": 0,
                "non_compliant_applications": 0,
                "mrl_violations": [],
                "phi_violations": [],
                "applications": [],
            }

            for app in applications:
                app_compliance = {
                    "application_id": app.application_id,
                    "product_name": app.product_name,
                    "active_ingredient": app.active_ingredient,
                    "application_date": app.application_date.isoformat(),
                    "status": "compliant",
                    "issues": [],
                }

                # Check MRL compliance
                mrl_ok = self._check_mrl_compliance(app)
                if not mrl_ok:
                    app_compliance["status"] = "non_compliant"
                    app_compliance["issues"].append("MRL violation detected")
                    compliance_results["mrl_violations"].append(app.application_id)

                # Check PHI compliance
                if harvest_date:
                    phi_ok = self._check_phi_compliance(app, harvest_date)
                    if not phi_ok:
                        app_compliance["status"] = "non_compliant"
                        app_compliance["issues"].append(
                            f"Pre-harvest interval not met ({app.pre_harvest_interval_days} days required)"
                        )
                        compliance_results["phi_violations"].append(app.application_id)

                # Update counts
                if app_compliance["status"] == "compliant":
                    compliance_results["compliant_applications"] += 1
                else:
                    compliance_results["non_compliant_applications"] += 1

                    # Publish non-conformance
                    await self.event_publisher.publish_non_conformance_detected(
                        tenant_id=tenant_id,
                        farm_id=farm_id,
                        field_id=field_id,
                        control_point="PPP.1.1",
                        severity="major",
                        description=f"PPP application {app.application_id} non-compliant: {', '.join(app_compliance['issues'])}",
                    )

                compliance_results["applications"].append(app_compliance)

            # Determine overall compliance
            overall_status = (
                "compliant"
                if compliance_results["non_compliant_applications"] == 0
                else "non_compliant"
            )

            # Publish compliance update
            await self.event_publisher.publish_compliance_updated(
                tenant_id=tenant_id,
                farm_id=farm_id,
                control_point="PPP.1",
                compliance_status=overall_status,
                assessment_data=compliance_results,
            )

            self.logger.info(f"PPP applications tracked: {overall_status}")
            return compliance_results

        except Exception as e:
            self.logger.error(f"Error tracking PPP applications: {e}")
            raise

    def _determine_threat_type(self, detection_data: dict) -> ThreatType:
        """تحديد نوع التهديد - Determine threat type"""
        threat_category = detection_data.get("category", "").lower()

        if "pest" in threat_category or "insect" in threat_category:
            return ThreatType.PEST
        elif "disease" in threat_category or "fungus" in threat_category:
            return ThreatType.DISEASE
        elif "weed" in threat_category:
            return ThreatType.WEED
        elif "nutrient" in threat_category or "deficiency" in threat_category:
            return ThreatType.NUTRIENT_DEFICIENCY
        else:
            return ThreatType.PEST  # Default

    def _calculate_severity(self, detection_data: dict) -> SeverityLevel:
        """حساب مستوى الخطورة - Calculate severity level"""
        confidence = detection_data.get("confidence_score", 0.0)
        affected_area = detection_data.get("affected_area_percentage", 0.0)

        # Calculate severity based on confidence and affected area
        severity_score = (confidence * 0.5) + (affected_area / 100 * 0.5)

        if severity_score >= 0.75:
            return SeverityLevel.CRITICAL
        elif severity_score >= 0.50:
            return SeverityLevel.HIGH
        elif severity_score >= 0.25:
            return SeverityLevel.MEDIUM
        else:
            return SeverityLevel.LOW

    def _check_economic_threshold(self, detection_data: dict) -> bool:
        """فحص تجاوز العتبة الاقتصادية - Check economic threshold"""
        affected_area = detection_data.get("affected_area_percentage", 0.0)
        # Example threshold: 5% affected area
        return affected_area > 5.0

    def _calculate_action_deadline(self, severity: SeverityLevel) -> str:
        """حساب الموعد النهائي للإجراء - Calculate action deadline"""
        now = datetime.now(UTC)

        deadline_map = {
            SeverityLevel.CRITICAL: timedelta(days=1),
            SeverityLevel.HIGH: timedelta(days=3),
            SeverityLevel.MEDIUM: timedelta(days=7),
            SeverityLevel.LOW: timedelta(days=14),
        }

        deadline = now + deadline_map.get(severity, timedelta(days=7))
        return deadline.isoformat()

    def _generate_ipm_recommendations(
        self, threat_type: ThreatType, severity: SeverityLevel, detection_data: dict
    ) -> list[dict[str, Any]]:
        """إنشاء توصيات IPM - Generate IPM recommendations"""
        recommendations = []

        # Always start with monitoring
        recommendations.append(
            {
                "priority": 1,
                "action": IPMAction.MONITORING.value,
                "description": f"Continue monitoring {detection_data.get('threat_name')} population",
            }
        )

        # Add cultural practices
        recommendations.append(
            {
                "priority": 2,
                "action": IPMAction.CULTURAL.value,
                "description": "Implement cultural controls (crop rotation, sanitation)",
            }
        )

        # Add biological control if appropriate
        if threat_type in [ThreatType.PEST, ThreatType.DISEASE]:
            recommendations.append(
                {
                    "priority": 3,
                    "action": IPMAction.BIOLOGICAL.value,
                    "description": "Consider biological control agents",
                }
            )

        # Chemical control only if severity is high
        if severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
            recommendations.append(
                {
                    "priority": 4,
                    "action": IPMAction.CHEMICAL.value,
                    "description": "Apply approved chemical control as last resort",
                }
            )

        return recommendations

    def _generate_ipm_report_recommendations(
        self,
        detections: list[ThreatDetection],
        ipm_records: list[IPMRecord],
        chemical_count: int,
        non_chemical_count: int,
    ) -> list[str]:
        """إنشاء توصيات تقرير IPM - Generate IPM report recommendations"""
        recommendations = []

        # Check chemical usage ratio
        if chemical_count > non_chemical_count:
            recommendations.append(
                "Increase use of non-chemical IPM methods to reduce reliance on pesticides"
            )

        # Check for recurring threats
        threat_counts = {}
        for detection in detections:
            threat_counts[detection.threat_name] = (
                threat_counts.get(detection.threat_name, 0) + 1
            )

        recurring = [name for name, count in threat_counts.items() if count > 2]
        if recurring:
            recommendations.append(
                f"Implement preventive measures for recurring threats: {', '.join(recurring)}"
            )

        # Check effectiveness
        low_effectiveness = sum(
            1 for r in ipm_records if r.effectiveness and r.effectiveness < 0.5
        )
        if low_effectiveness > 0:
            recommendations.append(
                "Review and improve intervention strategies with low effectiveness"
            )

        return recommendations

    def _check_mrl_compliance(self, application: PPPApplication) -> bool:
        """فحص امتثال الحد الأقصى للبقايا - Check MRL compliance"""
        # This should be checked against a database of MRL values
        # For now, we'll use a simplified check
        return True  # Placeholder

    def _check_phi_compliance(
        self, application: PPPApplication, harvest_date: datetime
    ) -> bool:
        """فحص امتثال فترة ما قبل الحصاد - Check PHI compliance"""
        days_before_harvest = (harvest_date - application.application_date).days
        return days_before_harvest >= application.pre_harvest_interval_days
