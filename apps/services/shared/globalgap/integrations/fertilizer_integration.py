"""
SAHOOL GlobalGAP Integration - Fertilizer Advisor Service Integration
تكامل خدمة مستشار الأسمدة مع GlobalGAP

Links with fertilizer-advisor service to:
- Track fertilizer applications for input management
- Generate nutrient management plans
- Ensure MRL (Maximum Residue Level) compliance
"""

import logging
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

from .events import GlobalGAPEventPublisher

logger = logging.getLogger(__name__)


class FertilizerType(str, Enum):
    """نوع السماد - Fertilizer Type"""

    ORGANIC = "organic"  # عضوي
    INORGANIC = "inorganic"  # غير عضوي
    BIOFERTILIZER = "biofertilizer"  # سماد حيوي
    SLOW_RELEASE = "slow_release"  # بطيء الإطلاق
    LIQUID = "liquid"  # سائل
    GRANULAR = "granular"  # حبيبي


class ApplicationMethod(str, Enum):
    """طريقة التطبيق - Application Method"""

    BROADCAST = "broadcast"  # نثر
    BAND_APPLICATION = "band_application"  # شريطي
    FOLIAR = "foliar"  # ورقي
    FERTIGATION = "fertigation"  # سماد بالري
    INJECTION = "injection"  # حقن
    SIDE_DRESSING = "side_dressing"  # جانبي


class NutrientType(str, Enum):
    """نوع المغذي - Nutrient Type"""

    NITROGEN = "N"  # نيتروجين
    PHOSPHORUS = "P"  # فوسفور
    POTASSIUM = "K"  # بوتاسيوم
    CALCIUM = "Ca"  # كالسيوم
    MAGNESIUM = "Mg"  # ماغنيسيوم
    SULFUR = "S"  # كبريت
    IRON = "Fe"  # حديد
    ZINC = "Zn"  # زنك
    MANGANESE = "Mn"  # منجنيز
    BORON = "B"  # بورون
    COPPER = "Cu"  # نحاس


@dataclass
class FertilizerApplication:
    """تطبيق السماد - Fertilizer Application"""

    application_id: str
    field_id: str
    product_name: str
    fertilizer_type: FertilizerType
    application_date: datetime
    application_method: ApplicationMethod
    quantity_kg: float
    area_hectares: float
    application_rate_kg_per_ha: float
    npk_composition: dict[str, float]  # {"N": 10.0, "P": 5.0, "K": 5.0}
    applicator_name: str
    equipment_calibrated: bool
    weather_conditions: dict[str, Any] | None = None
    soil_moisture_level: float | None = None
    notes: str | None = None


@dataclass
class SoilTest:
    """تحليل التربة - Soil Test"""

    test_id: str
    field_id: str
    test_date: datetime
    ph: float
    organic_matter_percent: float
    nutrient_levels: dict[str, float]  # ppm or appropriate units
    recommendations: list[str]
    lab_name: str
    lab_accredited: bool


@dataclass
class NutrientManagementPlan:
    """خطة إدارة المغذيات - Nutrient Management Plan"""

    plan_id: str
    farm_id: str
    field_id: str
    crop_type: str
    season_id: str
    created_date: datetime
    valid_until: datetime
    soil_test_results: SoilTest | None
    target_yield_kg_per_ha: float
    total_nitrogen_required_kg: float
    total_phosphorus_required_kg: float
    total_potassium_required_kg: float
    planned_applications: list[dict[str, Any]]
    compliance_status: str
    created_by: str


@dataclass
class InputManagementReport:
    """تقرير إدارة المدخلات - Input Management Report"""

    farm_id: str
    field_id: str
    period_start: datetime
    period_end: datetime
    total_applications: int
    organic_applications: int
    inorganic_applications: int
    total_nitrogen_kg: float
    total_phosphorus_kg: float
    total_potassium_kg: float
    compliance_status: str
    mrl_compliant: bool
    storage_compliant: bool
    application_records_complete: bool
    recommendations: list[str]


class FertilizerIntegration:
    """
    تكامل خدمة مستشار الأسمدة مع GlobalGAP
    Fertilizer Advisor Service Integration with GlobalGAP

    Handles fertilizer application tracking, nutrient management planning,
    and MRL compliance for GlobalGAP certification.
    """

    def __init__(self, event_publisher: GlobalGAPEventPublisher):
        self.event_publisher = event_publisher
        self.logger = logging.getLogger(__name__)

    async def track_fertilizer_application(
        self, application_data: dict, field_id: str, tenant_id: str
    ) -> dict[str, Any]:
        """
        تتبع تطبيق الأسمدة لإدارة المدخلات
        Track fertilizer application for input management

        Args:
            application_data: Raw application data from fertilizer-advisor service
            field_id: Field identifier
            tenant_id: Tenant identifier

        Returns:
            Tracked application data with compliance checks
        """
        try:
            self.logger.info(f"Tracking fertilizer application for field {field_id}")

            # Extract application details
            fertilizer_type = FertilizerType(application_data.get("type", "inorganic"))
            application_method = ApplicationMethod(
                application_data.get("method", "broadcast")
            )

            # Calculate application rate
            quantity = application_data.get("quantity_kg", 0.0)
            area = application_data.get("area_hectares", 1.0)
            rate = quantity / area if area > 0 else 0.0

            # Map to GlobalGAP input management format
            tracked_data = {
                "application_id": application_data.get("id"),
                "field_id": field_id,
                "farm_id": application_data.get("farm_id"),
                "timestamp": application_data.get(
                    "timestamp", datetime.now(UTC).isoformat()
                ),
                # Product details
                "product": {
                    "name": application_data.get("product_name"),
                    "manufacturer": application_data.get("manufacturer"),
                    "type": fertilizer_type.value,
                    "batch_number": application_data.get("batch_number"),
                    "registration_number": application_data.get("registration_number"),
                },
                # Application details
                "application": {
                    "method": application_method.value,
                    "quantity_kg": quantity,
                    "area_hectares": area,
                    "rate_kg_per_ha": rate,
                    "date": application_data.get("application_date"),
                    "applicator": application_data.get("applicator_name"),
                },
                # Nutrient composition (NPK)
                "nutrients": {
                    "N": application_data.get("nitrogen_percent", 0.0),
                    "P": application_data.get("phosphorus_percent", 0.0),
                    "K": application_data.get("potassium_percent", 0.0),
                    "total_N_kg": quantity
                    * application_data.get("nitrogen_percent", 0.0)
                    / 100,
                    "total_P_kg": quantity
                    * application_data.get("phosphorus_percent", 0.0)
                    / 100,
                    "total_K_kg": quantity
                    * application_data.get("potassium_percent", 0.0)
                    / 100,
                },
                # Compliance checks
                "compliance": {
                    "equipment_calibrated": application_data.get(
                        "equipment_calibrated", False
                    ),
                    "weather_suitable": self._check_weather_suitability(
                        application_data
                    ),
                    "storage_documented": application_data.get(
                        "storage_documented", False
                    ),
                    "within_plan": self._check_within_plan(application_data),
                    "mrl_compliant": self._check_fertilizer_mrl(application_data),
                },
                # Safety and environmental
                "safety": {
                    "ppe_used": application_data.get("ppe_used", False),
                    "buffer_zones_respected": application_data.get(
                        "buffer_zones_respected", False
                    ),
                    "runoff_prevention": application_data.get(
                        "runoff_prevention_measures", []
                    ),
                },
            }

            # Check for non-compliance
            compliance_issues = []
            if not tracked_data["compliance"]["equipment_calibrated"]:
                compliance_issues.append("Equipment not calibrated")
            if not tracked_data["compliance"]["weather_suitable"]:
                compliance_issues.append("Weather conditions not suitable")
            if not tracked_data["compliance"]["mrl_compliant"]:
                compliance_issues.append("MRL compliance concern")

            if compliance_issues:
                await self.event_publisher.publish_non_conformance_detected(
                    tenant_id=tenant_id,
                    farm_id=application_data.get("farm_id", "unknown"),
                    field_id=field_id,
                    control_point="FERT.1.1",
                    severity="medium",
                    description=f"Fertilizer application issues: {', '.join(compliance_issues)}",
                )

            # Publish integration sync event
            await self.event_publisher.publish_integration_synced(
                tenant_id=tenant_id,
                integration_type="fertilizer",
                farm_id=application_data.get("farm_id", "unknown"),
                records_synced=1,
                sync_status="success",
                correlation_id=application_data.get("correlation_id"),
            )

            self.logger.info("Fertilizer application tracked successfully")
            return tracked_data

        except Exception as e:
            self.logger.error(f"Error tracking fertilizer application: {e}")

            # Publish failure event
            await self.event_publisher.publish_integration_synced(
                tenant_id=tenant_id,
                integration_type="fertilizer",
                farm_id=application_data.get("farm_id", "unknown"),
                records_synced=0,
                sync_status="failed",
                error_message=str(e),
                correlation_id=application_data.get("correlation_id"),
            )

            raise

    async def generate_nutrient_management_plan(
        self,
        farm_id: str,
        field_id: str,
        tenant_id: str,
        crop_type: str,
        target_yield_kg_per_ha: float,
        soil_test: SoilTest | None = None,
    ) -> NutrientManagementPlan:
        """
        إنشاء خطة إدارة المغذيات
        Generate nutrient management plan

        Args:
            farm_id: Farm identifier
            field_id: Field identifier
            tenant_id: Tenant identifier
            crop_type: Crop being grown
            target_yield_kg_per_ha: Target yield
            soil_test: Recent soil test results

        Returns:
            Comprehensive nutrient management plan
        """
        try:
            self.logger.info(
                f"Generating nutrient management plan for field {field_id}"
            )

            # Calculate nutrient requirements based on crop and yield
            nutrient_requirements = self._calculate_nutrient_requirements(
                crop_type, target_yield_kg_per_ha, soil_test
            )

            # Generate application schedule
            planned_applications = self._generate_application_schedule(
                crop_type, nutrient_requirements, soil_test
            )

            # Check compliance with GlobalGAP requirements
            compliance_status = "compliant"
            if not soil_test or not soil_test.lab_accredited:
                compliance_status = "needs_soil_test"
            elif not self._validate_nutrient_balance(nutrient_requirements):
                compliance_status = "imbalanced"

            plan = NutrientManagementPlan(
                plan_id=f"NMP_{field_id}_{datetime.now(UTC).strftime('%Y%m%d')}",
                farm_id=farm_id,
                field_id=field_id,
                crop_type=crop_type,
                season_id=f"season_{datetime.now(UTC).year}",
                created_date=datetime.now(UTC),
                valid_until=datetime.now(UTC) + timedelta(days=365),
                soil_test_results=soil_test,
                target_yield_kg_per_ha=target_yield_kg_per_ha,
                total_nitrogen_required_kg=nutrient_requirements["N"],
                total_phosphorus_required_kg=nutrient_requirements["P"],
                total_potassium_required_kg=nutrient_requirements["K"],
                planned_applications=planned_applications,
                compliance_status=compliance_status,
                created_by="system",
            )

            # Publish compliance update
            await self.event_publisher.publish_compliance_updated(
                tenant_id=tenant_id,
                farm_id=farm_id,
                control_point="FERT.2",
                compliance_status=compliance_status,
                assessment_data=asdict(plan),
            )

            self.logger.info(f"Nutrient management plan generated: {compliance_status}")
            return plan

        except Exception as e:
            self.logger.error(f"Error generating nutrient management plan: {e}")
            raise

    async def ensure_mrl_compliance(
        self,
        farm_id: str,
        field_id: str,
        tenant_id: str,
        applications: list[FertilizerApplication],
        crop_type: str,
        harvest_date: datetime | None = None,
    ) -> dict[str, Any]:
        """
        ضمان الامتثال للحد الأقصى من مستويات البقايا (MRL)
        Ensure Maximum Residue Level (MRL) compliance

        Args:
            farm_id: Farm identifier
            field_id: Field identifier
            tenant_id: Tenant identifier
            applications: List of fertilizer applications
            crop_type: Crop type
            harvest_date: Expected or actual harvest date

        Returns:
            MRL compliance report
        """
        try:
            self.logger.info(f"Checking MRL compliance for field {field_id}")

            compliance_results = {
                "farm_id": farm_id,
                "field_id": field_id,
                "crop_type": crop_type,
                "total_applications": len(applications),
                "compliant_applications": 0,
                "non_compliant_applications": 0,
                "risk_level": "low",
                "heavy_metal_risk": False,
                "nitrate_accumulation_risk": False,
                "recommendations": [],
            }

            total_nitrogen = 0.0
            total_heavy_metals = {}

            for app in applications:
                total_nitrogen += (
                    app.npk_composition.get("N", 0.0) * app.quantity_kg / 100
                )

                # Check for heavy metals (if organic fertilizer)
                if app.fertilizer_type == FertilizerType.ORGANIC:
                    # Organic fertilizers may contain heavy metals
                    heavy_metal_content = self._estimate_heavy_metal_content(app)
                    for metal, amount in heavy_metal_content.items():
                        total_heavy_metals[metal] = (
                            total_heavy_metals.get(metal, 0.0) + amount
                        )

            # Check nitrogen accumulation risk
            if total_nitrogen > 200:  # kg N per hectare (example threshold)
                compliance_results["nitrate_accumulation_risk"] = True
                compliance_results["risk_level"] = "medium"
                compliance_results["recommendations"].append(
                    "High nitrogen application detected - monitor nitrate levels in produce"
                )

            # Check heavy metal accumulation
            for metal, total_amount in total_heavy_metals.items():
                limit = self._get_heavy_metal_limit(metal, crop_type)
                if total_amount > limit:
                    compliance_results["heavy_metal_risk"] = True
                    compliance_results["risk_level"] = "high"
                    compliance_results["recommendations"].append(
                        f"Excessive {metal} accumulation - soil testing recommended"
                    )

            # Determine overall compliance
            if compliance_results["risk_level"] == "high":
                overall_status = "non_compliant"

                await self.event_publisher.publish_non_conformance_detected(
                    tenant_id=tenant_id,
                    farm_id=farm_id,
                    field_id=field_id,
                    control_point="MRL.1",
                    severity="major",
                    description="High MRL risk detected - immediate action required",
                )
            else:
                overall_status = "compliant"

            compliance_results["overall_status"] = overall_status

            # Publish compliance update
            await self.event_publisher.publish_compliance_updated(
                tenant_id=tenant_id,
                farm_id=farm_id,
                control_point="MRL.1",
                compliance_status=overall_status,
                assessment_data=compliance_results,
            )

            self.logger.info(f"MRL compliance checked: {overall_status}")
            return compliance_results

        except Exception as e:
            self.logger.error(f"Error checking MRL compliance: {e}")
            raise

    async def generate_input_management_report(
        self,
        farm_id: str,
        field_id: str,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime,
        applications: list[FertilizerApplication],
    ) -> InputManagementReport:
        """
        إنشاء تقرير إدارة المدخلات
        Generate input management report

        Args:
            farm_id: Farm identifier
            field_id: Field identifier
            tenant_id: Tenant identifier
            start_date: Report period start
            end_date: Report period end
            applications: List of fertilizer applications

        Returns:
            Comprehensive input management report for GlobalGAP audit
        """
        try:
            self.logger.info(f"Generating input management report for field {field_id}")

            # Count application types
            organic_count = sum(
                1
                for app in applications
                if app.fertilizer_type == FertilizerType.ORGANIC
            )
            inorganic_count = len(applications) - organic_count

            # Calculate total nutrients applied
            total_n = sum(
                app.npk_composition.get("N", 0.0) * app.quantity_kg / 100
                for app in applications
            )
            total_p = sum(
                app.npk_composition.get("P", 0.0) * app.quantity_kg / 100
                for app in applications
            )
            total_k = sum(
                app.npk_composition.get("K", 0.0) * app.quantity_kg / 100
                for app in applications
            )

            # Check compliance factors
            records_complete = all(
                app.applicator_name and app.equipment_calibrated for app in applications
            )

            # Generate recommendations
            recommendations = self._generate_input_recommendations(
                applications, total_n, total_p, total_k
            )

            report = InputManagementReport(
                farm_id=farm_id,
                field_id=field_id,
                period_start=start_date,
                period_end=end_date,
                total_applications=len(applications),
                organic_applications=organic_count,
                inorganic_applications=inorganic_count,
                total_nitrogen_kg=total_n,
                total_phosphorus_kg=total_p,
                total_potassium_kg=total_k,
                compliance_status="compliant" if records_complete else "incomplete",
                mrl_compliant=True,  # Should be checked via ensure_mrl_compliance
                storage_compliant=True,  # Should be verified separately
                application_records_complete=records_complete,
                recommendations=recommendations,
            )

            # Publish compliance update
            await self.event_publisher.publish_compliance_updated(
                tenant_id=tenant_id,
                farm_id=farm_id,
                control_point="FERT.1",
                compliance_status=report.compliance_status,
                assessment_data=asdict(report),
            )

            self.logger.info(
                f"Input management report generated: {report.compliance_status}"
            )
            return report

        except Exception as e:
            self.logger.error(f"Error generating input management report: {e}")
            raise

    def _check_weather_suitability(self, application_data: dict) -> bool:
        """فحص ملاءمة الطقس - Check weather suitability"""
        weather = application_data.get("weather_conditions", {})
        wind_speed = weather.get("wind_speed_kmh", 0)
        rainfall_chance = weather.get("rainfall_chance_percent", 0)

        # Not suitable if high wind or rain expected
        return wind_speed < 15 and rainfall_chance < 50

    def _check_within_plan(self, application_data: dict) -> bool:
        """فحص التطابق مع الخطة - Check if within nutrient management plan"""
        # This should check against the nutrient management plan
        return application_data.get("planned_application", False)

    def _check_fertilizer_mrl(self, application_data: dict) -> bool:
        """فحص MRL للأسمدة - Check fertilizer MRL compliance"""
        # This should check for heavy metals and other contaminants
        return True  # Placeholder

    def _calculate_nutrient_requirements(
        self,
        crop_type: str,
        target_yield_kg_per_ha: float,
        soil_test: SoilTest | None,
    ) -> dict[str, float]:
        """حساب احتياجات المغذيات - Calculate nutrient requirements"""
        # Simplified calculation - should use crop-specific coefficients
        base_n = target_yield_kg_per_ha * 0.03  # 3% of yield as N
        base_p = target_yield_kg_per_ha * 0.01  # 1% of yield as P
        base_k = target_yield_kg_per_ha * 0.02  # 2% of yield as K

        # Adjust based on soil test if available
        if soil_test:
            soil_n = soil_test.nutrient_levels.get("N", 0)
            soil_p = soil_test.nutrient_levels.get("P", 0)
            soil_k = soil_test.nutrient_levels.get("K", 0)

            # Reduce requirements based on existing soil nutrients
            base_n = max(0, base_n - soil_n * 0.5)
            base_p = max(0, base_p - soil_p * 0.5)
            base_k = max(0, base_k - soil_k * 0.5)

        return {"N": base_n, "P": base_p, "K": base_k}

    def _generate_application_schedule(
        self,
        crop_type: str,
        nutrient_requirements: dict[str, float],
        soil_test: SoilTest | None,
    ) -> list[dict[str, Any]]:
        """إنشاء جدول التطبيق - Generate application schedule"""
        # Simplified schedule - split into 3 applications
        total_n = nutrient_requirements["N"]
        total_p = nutrient_requirements["P"]
        total_k = nutrient_requirements["K"]

        return [
            {
                "stage": "pre_planting",
                "timing": "Before planting",
                "N_kg": total_n * 0.3,
                "P_kg": total_p * 0.5,
                "K_kg": total_k * 0.3,
            },
            {
                "stage": "vegetative",
                "timing": "30-40 days after planting",
                "N_kg": total_n * 0.4,
                "P_kg": total_p * 0.3,
                "K_kg": total_k * 0.3,
            },
            {
                "stage": "reproductive",
                "timing": "60-70 days after planting",
                "N_kg": total_n * 0.3,
                "P_kg": total_p * 0.2,
                "K_kg": total_k * 0.4,
            },
        ]

    def _validate_nutrient_balance(
        self, nutrient_requirements: dict[str, float]
    ) -> bool:
        """التحقق من توازن المغذيات - Validate nutrient balance"""
        n = nutrient_requirements["N"]
        p = nutrient_requirements["P"]
        k = nutrient_requirements["K"]

        # Check N:P:K ratio is reasonable
        if p == 0 or k == 0:
            return False

        n_p_ratio = n / p
        n_k_ratio = n / k

        # Reasonable ranges for most crops
        return 2 <= n_p_ratio <= 10 and 0.5 <= n_k_ratio <= 3

    def _estimate_heavy_metal_content(
        self, application: FertilizerApplication
    ) -> dict[str, float]:
        """تقدير محتوى المعادن الثقيلة - Estimate heavy metal content"""
        # This should use actual lab data or regulatory limits
        # Placeholder estimates for organic fertilizers
        if application.fertilizer_type == FertilizerType.ORGANIC:
            return {
                "Cd": 0.1,  # mg/kg
                "Pb": 0.5,
                "Hg": 0.05,
                "As": 0.2,
            }
        return {}

    def _get_heavy_metal_limit(self, metal: str, crop_type: str) -> float:
        """الحصول على حد المعدن الثقيل - Get heavy metal limit"""
        # GlobalGAP limits (mg/kg soil)
        limits = {
            "Cd": 3.0,
            "Pb": 100.0,
            "Hg": 1.0,
            "As": 20.0,
        }
        return limits.get(metal, 0.0)

    def _generate_input_recommendations(
        self,
        applications: list[FertilizerApplication],
        total_n: float,
        total_p: float,
        total_k: float,
    ) -> list[str]:
        """إنشاء توصيات إدارة المدخلات - Generate input management recommendations"""
        recommendations = []

        # Check NPK balance
        if total_n > total_p * 5:
            recommendations.append(
                "Nitrogen application is high relative to phosphorus - consider balancing"
            )

        # Check organic matter
        organic_count = sum(
            1 for app in applications if app.fertilizer_type == FertilizerType.ORGANIC
        )
        if organic_count == 0:
            recommendations.append(
                "Consider incorporating organic fertilizers to improve soil health"
            )

        # Check calibration
        uncalibrated = sum(1 for app in applications if not app.equipment_calibrated)
        if uncalibrated > 0:
            recommendations.append(
                f"Calibrate application equipment - {uncalibrated} applications used uncalibrated equipment"
            )

        return recommendations
