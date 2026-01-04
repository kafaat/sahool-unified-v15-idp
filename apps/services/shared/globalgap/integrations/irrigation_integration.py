"""
SAHOOL GlobalGAP Integration - Irrigation Service Integration
تكامل خدمة الري مع GlobalGAP

Links with irrigation-smart service to:
- Map irrigation data to SPRING water management requirements
- Generate water usage reports for GlobalGAP audits
- Track water source compliance
"""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

from .events import GlobalGAPEventPublisher

logger = logging.getLogger(__name__)


class WaterSource(str, Enum):
    """مصادر المياه - Water Sources"""

    GROUNDWATER = "groundwater"  # مياه جوفية
    SURFACE_WATER = "surface_water"  # مياه سطحية
    RAINWATER = "rainwater"  # مياه أمطار
    RECYCLED = "recycled"  # مياه معاد تدويرها
    MUNICIPAL = "municipal"  # مياه البلدية
    UNKNOWN = "unknown"  # غير معروف


class WaterQualityStatus(str, Enum):
    """حالة جودة المياه - Water Quality Status"""

    COMPLIANT = "compliant"  # متوافق
    NON_COMPLIANT = "non_compliant"  # غير متوافق
    PENDING_TEST = "pending_test"  # في انتظار الاختبار
    UNKNOWN = "unknown"  # غير معروف


@dataclass
class IrrigationRecord:
    """سجل الري - Irrigation Record"""

    field_id: str
    irrigation_date: datetime
    water_volume_m3: float
    water_source: WaterSource
    irrigation_method: str
    duration_minutes: int
    water_quality_status: WaterQualityStatus
    ph_level: float | None = None
    ec_level: float | None = None  # Electrical Conductivity
    test_date: datetime | None = None
    notes: str | None = None


@dataclass
class WaterUsageReport:
    """تقرير استخدام المياه - Water Usage Report"""

    farm_id: str
    field_id: str
    period_start: datetime
    period_end: datetime
    total_volume_m3: float
    average_daily_volume_m3: float
    source_breakdown: dict[str, float]
    compliance_status: str
    non_compliant_records: list[str]
    recommendations: list[str]


class IrrigationIntegration:
    """
    تكامل خدمة الري مع GlobalGAP
    Irrigation Service Integration with GlobalGAP

    Handles mapping irrigation data to SPRING water management requirements
    and ensures water source compliance.
    """

    def __init__(self, event_publisher: GlobalGAPEventPublisher):
        self.event_publisher = event_publisher
        self.logger = logging.getLogger(__name__)

    async def map_irrigation_to_spring(
        self, irrigation_data: dict, field_id: str, tenant_id: str
    ) -> dict[str, Any]:
        """
        تعيين بيانات الري إلى متطلبات إدارة المياه SPRING
        Map irrigation data to SPRING water management requirements

        SPRING = Sustainable Programme for Irrigation and Groundwater

        Args:
            irrigation_data: Raw irrigation data from irrigation-smart service
            field_id: Field identifier
            tenant_id: Tenant identifier

        Returns:
            Mapped data compliant with SPRING requirements
        """
        try:
            self.logger.info(f"Mapping irrigation data for field {field_id}")

            # Extract irrigation details
            water_volume = (
                irrigation_data.get("water_volume_liters", 0) / 1000
            )  # Convert to m3
            water_source = WaterSource(irrigation_data.get("water_source", "unknown"))
            irrigation_method = irrigation_data.get("irrigation_method", "unknown")

            # Map to SPRING format
            spring_data = {
                "field_id": field_id,
                "irrigation_event_id": irrigation_data.get("id"),
                "date": irrigation_data.get("timestamp", datetime.now(UTC).isoformat()),
                # Water quantity
                "water_volume_m3": water_volume,
                "irrigation_method": irrigation_method,
                "application_efficiency": self._calculate_efficiency(irrigation_method),
                # Water source tracking (SPRING requirement)
                "water_source": {
                    "type": water_source.value,
                    "location": irrigation_data.get("source_location"),
                    "license_number": irrigation_data.get("source_license"),
                    "quality_status": irrigation_data.get(
                        "quality_status", "pending_test"
                    ),
                },
                # Water quality parameters
                "water_quality": {
                    "ph": irrigation_data.get("ph_level"),
                    "ec": irrigation_data.get("ec_level"),  # μS/cm
                    "test_date": irrigation_data.get("quality_test_date"),
                    "meets_standards": self._check_water_quality(irrigation_data),
                },
                # Compliance tracking
                "compliance": {
                    "spring_compliant": self._check_spring_compliance(irrigation_data),
                    "license_valid": irrigation_data.get("license_valid", False),
                    "quality_verified": irrigation_data.get("quality_verified", False),
                },
            }

            # Publish integration sync event
            await self.event_publisher.publish_integration_synced(
                tenant_id=tenant_id,
                integration_type="irrigation",
                farm_id=irrigation_data.get("farm_id", "unknown"),
                records_synced=1,
                sync_status="success",
                correlation_id=irrigation_data.get("correlation_id"),
            )

            self.logger.info(
                f"Successfully mapped irrigation data for field {field_id}"
            )
            return spring_data

        except Exception as e:
            self.logger.error(f"Error mapping irrigation data: {e}")

            # Publish failure event
            await self.event_publisher.publish_integration_synced(
                tenant_id=tenant_id,
                integration_type="irrigation",
                farm_id=irrigation_data.get("farm_id", "unknown"),
                records_synced=0,
                sync_status="failed",
                error_message=str(e),
                correlation_id=irrigation_data.get("correlation_id"),
            )

            raise

    async def generate_water_usage_report(
        self,
        farm_id: str,
        field_id: str,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime,
        irrigation_records: list[IrrigationRecord],
    ) -> WaterUsageReport:
        """
        إنشاء تقرير استخدام المياه لتدقيق GlobalGAP
        Generate water usage report for GlobalGAP audit

        Args:
            farm_id: Farm identifier
            field_id: Field identifier
            tenant_id: Tenant identifier
            start_date: Report period start
            end_date: Report period end
            irrigation_records: List of irrigation records

        Returns:
            Water usage report compliant with GlobalGAP requirements
        """
        try:
            self.logger.info(f"Generating water usage report for field {field_id}")

            # Calculate total volume
            total_volume = sum(record.water_volume_m3 for record in irrigation_records)

            # Calculate average daily volume
            days = (end_date - start_date).days or 1
            average_daily = total_volume / days

            # Source breakdown
            source_breakdown = {}
            for record in irrigation_records:
                source = record.water_source.value
                source_breakdown[source] = (
                    source_breakdown.get(source, 0) + record.water_volume_m3
                )

            # Check compliance
            non_compliant = []
            for record in irrigation_records:
                if record.water_quality_status == WaterQualityStatus.NON_COMPLIANT:
                    non_compliant.append(
                        f"{record.field_id}_{record.irrigation_date.isoformat()}"
                    )

            compliance_status = (
                "compliant" if len(non_compliant) == 0 else "non_compliant"
            )

            # Generate recommendations
            recommendations = self._generate_water_recommendations(
                total_volume, source_breakdown, irrigation_records
            )

            report = WaterUsageReport(
                farm_id=farm_id,
                field_id=field_id,
                period_start=start_date,
                period_end=end_date,
                total_volume_m3=total_volume,
                average_daily_volume_m3=average_daily,
                source_breakdown=source_breakdown,
                compliance_status=compliance_status,
                non_compliant_records=non_compliant,
                recommendations=recommendations,
            )

            # Check if compliance update is needed
            if compliance_status == "non_compliant":
                await self.event_publisher.publish_non_conformance_detected(
                    tenant_id=tenant_id,
                    farm_id=farm_id,
                    field_id=field_id,
                    control_point="SPRING.1.1",  # Water management control point
                    severity="major",
                    description=f"Non-compliant water quality detected in {len(non_compliant)} irrigation events",
                )

            self.logger.info(f"Water usage report generated: {compliance_status}")
            return report

        except Exception as e:
            self.logger.error(f"Error generating water usage report: {e}")
            raise

    async def track_water_source_compliance(
        self, farm_id: str, tenant_id: str, water_sources: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        تتبع امتثال مصادر المياه
        Track water source compliance

        Ensures all water sources meet GlobalGAP requirements:
        - Valid licenses/permits
        - Regular quality testing
        - Proper documentation

        Args:
            farm_id: Farm identifier
            tenant_id: Tenant identifier
            water_sources: List of water source configurations

        Returns:
            Compliance status for all water sources
        """
        try:
            self.logger.info(f"Tracking water source compliance for farm {farm_id}")

            compliance_results = {
                "farm_id": farm_id,
                "total_sources": len(water_sources),
                "compliant_sources": 0,
                "non_compliant_sources": 0,
                "pending_sources": 0,
                "sources": [],
            }

            for source in water_sources:
                source_id = source.get("id")
                source_type = source.get("type")

                # Check license validity
                license_valid = self._check_license_validity(source)

                # Check quality test date
                quality_recent = self._check_quality_test_recency(source)

                # Determine compliance status
                if license_valid and quality_recent:
                    status = "compliant"
                    compliance_results["compliant_sources"] += 1
                elif not license_valid or not quality_recent:
                    status = "non_compliant"
                    compliance_results["non_compliant_sources"] += 1

                    # Publish non-conformance
                    await self.event_publisher.publish_non_conformance_detected(
                        tenant_id=tenant_id,
                        farm_id=farm_id,
                        control_point="SPRING.1.2",
                        severity="major",
                        description=f"Water source {source_id} ({source_type}) is non-compliant",
                    )
                else:
                    status = "pending"
                    compliance_results["pending_sources"] += 1

                compliance_results["sources"].append(
                    {
                        "source_id": source_id,
                        "source_type": source_type,
                        "status": status,
                        "license_valid": license_valid,
                        "quality_recent": quality_recent,
                        "last_test_date": source.get("last_quality_test_date"),
                    }
                )

            # Publish compliance update
            overall_status = (
                "compliant"
                if compliance_results["non_compliant_sources"] == 0
                else "non_compliant"
            )
            await self.event_publisher.publish_compliance_updated(
                tenant_id=tenant_id,
                farm_id=farm_id,
                control_point="SPRING.1",
                compliance_status=overall_status,
                assessment_data=compliance_results,
            )

            self.logger.info(f"Water source compliance tracked: {overall_status}")
            return compliance_results

        except Exception as e:
            self.logger.error(f"Error tracking water source compliance: {e}")
            raise

    def _calculate_efficiency(self, irrigation_method: str) -> float:
        """حساب كفاءة طريقة الري - Calculate irrigation method efficiency"""
        efficiency_map = {
            "drip": 0.90,
            "sprinkler": 0.75,
            "flood": 0.60,
            "furrow": 0.65,
            "pivot": 0.85,
        }
        return efficiency_map.get(irrigation_method.lower(), 0.70)

    def _check_water_quality(self, irrigation_data: dict) -> bool:
        """فحص جودة المياه - Check water quality"""
        ph = irrigation_data.get("ph_level")
        ec = irrigation_data.get("ec_level")

        # GlobalGAP acceptable ranges
        ph_ok = 6.0 <= ph <= 8.5 if ph else False
        ec_ok = ec <= 3000 if ec else False  # μS/cm

        return ph_ok and ec_ok

    def _check_spring_compliance(self, irrigation_data: dict) -> bool:
        """فحص امتثال SPRING - Check SPRING compliance"""
        has_source_license = bool(irrigation_data.get("source_license"))
        quality_verified = bool(irrigation_data.get("quality_verified"))
        license_valid = bool(irrigation_data.get("license_valid"))

        return has_source_license and quality_verified and license_valid

    def _check_license_validity(self, water_source: dict) -> bool:
        """فحص صلاحية الترخيص - Check license validity"""
        expiry_date = water_source.get("license_expiry_date")
        if not expiry_date:
            return False

        try:
            expiry = datetime.fromisoformat(expiry_date.replace("Z", "+00:00"))
            return expiry > datetime.now(UTC)
        except (ValueError, AttributeError):
            return False

    def _check_quality_test_recency(self, water_source: dict) -> bool:
        """فحص حداثة اختبار الجودة - Check quality test recency"""
        test_date = water_source.get("last_quality_test_date")
        if not test_date:
            return False

        try:
            last_test = datetime.fromisoformat(test_date.replace("Z", "+00:00"))
            # GlobalGAP requires annual testing
            one_year_ago = datetime.now(UTC) - timedelta(days=365)
            return last_test > one_year_ago
        except (ValueError, AttributeError):
            return False

    def _generate_water_recommendations(
        self,
        total_volume: float,
        source_breakdown: dict[str, float],
        records: list[IrrigationRecord],
    ) -> list[str]:
        """إنشاء توصيات إدارة المياه - Generate water management recommendations"""
        recommendations = []

        # Check for excessive water use
        if total_volume > 1000:  # Example threshold
            recommendations.append(
                "Consider implementing water-saving irrigation methods"
            )

        # Check source diversity
        if len(source_breakdown) == 1:
            recommendations.append("Diversify water sources to improve resilience")

        # Check for non-compliant records
        non_compliant_count = sum(
            1
            for r in records
            if r.water_quality_status == WaterQualityStatus.NON_COMPLIANT
        )
        if non_compliant_count > 0:
            recommendations.append(
                f"Address {non_compliant_count} water quality issues immediately"
            )

        # Check for pending tests
        pending_count = sum(
            1
            for r in records
            if r.water_quality_status == WaterQualityStatus.PENDING_TEST
        )
        if pending_count > 0:
            recommendations.append(
                f"Complete {pending_count} pending water quality tests"
            )

        return recommendations
