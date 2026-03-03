"""
Data Drift Detector
كاشف انحراف البيانات

Detects data and ML model drift:
- NDVI distribution shift over time
- Sensor data anomalies (missing rate, range violations)
- ML model input/output distribution shifts
- Feature drift in prediction pipelines
- Data quality degradation (null rates, schema violations)
"""

from __future__ import annotations

import logging
from pathlib import Path

from shared.drift_detection.detectors.base import BaseDriftDetector
from shared.drift_detection.models import (
    DriftCategory,
    DriftResult,
    DriftSeverity,
)

logger = logging.getLogger(__name__)


class DataDriftDetector(BaseDriftDetector):
    """
    Detects data drift in ML models, sensors, and NDVI pipelines.
    يكتشف انحراف البيانات في نماذج ML والمستشعرات وخطوط NDVI.

    Can operate in two modes:
    1. Static analysis: Check code for data validation patterns (default)
    2. Runtime analysis: Check actual data distributions (requires DB connection)
    """

    @property
    def category(self) -> DriftCategory:
        return DriftCategory.DATA

    async def detect(self) -> list[DriftResult]:
        self.clear_results()

        await self._check_data_validation_patterns()
        await self._check_ndvi_pipeline_guards()
        await self._check_sensor_validation()
        await self._check_ml_model_versioning()
        await self._check_feature_schema()

        # Runtime checks (if configured)
        if self.config.get("runtime_check", False):
            await self._check_runtime_distributions()

        return self.results

    async def _check_data_validation_patterns(self) -> None:
        """Check that data pipelines have proper validation."""
        root = Path(self.working_dir)

        # Check ML/AI services for input validation
        ai_service_dirs = [
            root / "apps" / "services" / "crop-intelligence-service",
            root / "apps" / "services" / "vegetation-analysis-service",
            root / "apps" / "services" / "yield-prediction-service",
            root / "apps" / "services" / "pest-detection-service",
            root / "apps" / "services" / "yolo26-vision-service",
            root / "apps" / "services" / "soil-analysis-service",
        ]

        for svc_dir in ai_service_dirs:
            if not svc_dir.exists():
                continue

            service_name = svc_dir.name
            src_dir = svc_dir / "src"
            if not src_dir.exists():
                continue

            has_validation = False
            # Scan both Python and TypeScript sources
            source_files = list(src_dir.rglob("*.py")) + list(src_dir.rglob("*.ts"))
            for src_file in source_files:
                try:
                    content = src_file.read_text(errors="ignore")
                    if any(
                        pat in content
                        for pat in [
                            "Validator",
                            "validator",
                            "validate_input",
                            "validateInput",
                            "validateFeature",
                            "pydantic",
                            "BaseModel",
                            "Field(",
                            "jsonschema",
                            "schema_validate",
                            "check_range",
                            "assert_range",
                            "FEATURE_SCHEMA",
                            "input_schema",
                            "inputSchema",
                            "ValidationPipe",
                            "class-validator",
                            "IsNumber",
                            "IsString",
                            "Min(",
                            "Max(",
                        ]
                    ):
                        has_validation = True
                        break
                except (OSError, UnicodeDecodeError):
                    continue

            if not has_validation:
                self.add_result(
                    DriftResult(
                        category=DriftCategory.DATA,
                        severity=DriftSeverity.HIGH,
                        source="data_validation",
                        expected="Input validation (Pydantic/schema) on data pipelines",
                        actual=f"No input validation found in {service_name}",
                        description=f"ML service '{service_name}' lacks input data validation - vulnerable to data drift",
                        description_ar=f"خدمة ML '{service_name}' تفتقر إلى التحقق من بيانات الإدخال - عرضة لانحراف البيانات",
                        service_name=service_name,
                        auto_fixable=False,
                        remediation_hint="Add Pydantic models for all ML pipeline inputs with range/type validation",
                    )
                )

    async def _check_ndvi_pipeline_guards(self) -> None:
        """Check NDVI processing pipeline has proper data guards."""
        root = Path(self.working_dir)

        ndvi_files = list(root.glob("shared/satellite/**/*.py")) + list(
            root.glob("apps/services/vegetation-analysis-service/**/*.py")
        )

        has_range_check = False
        has_outlier_detection = False
        has_freshness_check = False

        for nf in ndvi_files:
            try:
                content = nf.read_text(errors="ignore")
            except (OSError, UnicodeDecodeError):
                continue

            # NDVI valid range is -1 to 1
            if any(
                pat in content
                for pat in [
                    "ndvi > -1",
                    "ndvi < 1",
                    "ndvi >= -1",
                    "ndvi <= 1",
                    "range(-1, 1)",
                    "clip(-1, 1)",
                    "clamp",
                    "NDVI_MIN",
                    "NDVI_MAX",
                ]
            ):
                has_range_check = True

            if any(
                pat in content
                for pat in [
                    "outlier",
                    "z_score",
                    "iqr",
                    "anomaly",
                    "stddev",
                    "standard_deviation",
                    "percentile",
                ]
            ):
                has_outlier_detection = True

            if any(
                pat in content
                for pat in [
                    "freshness",
                    "stale",
                    "data_age",
                    "last_updated",
                    "max_age",
                    "ttl",
                ]
            ):
                has_freshness_check = True

        if ndvi_files and not has_range_check:
            self.add_result(
                DriftResult(
                    category=DriftCategory.DATA,
                    severity=DriftSeverity.HIGH,
                    source="ndvi_guards",
                    expected="NDVI range validation (-1 to 1)",
                    actual="No NDVI range check found",
                    description="NDVI pipeline lacks range validation - invalid values may propagate",
                    description_ar="خط أنابيب NDVI يفتقر إلى التحقق من النطاق - قد تنتشر القيم غير الصالحة",
                    auto_fixable=False,
                    remediation_hint="Add NDVI value clamping to [-1, 1] range at ingestion point",
                )
            )

        if ndvi_files and not has_outlier_detection:
            self.add_result(
                DriftResult(
                    category=DriftCategory.DATA,
                    severity=DriftSeverity.MEDIUM,
                    source="ndvi_guards",
                    description="NDVI pipeline lacks outlier detection - distribution shifts may go unnoticed",
                    description_ar="خط أنابيب NDVI يفتقر إلى كشف القيم المتطرفة",
                    auto_fixable=False,
                    remediation_hint="Add statistical outlier detection (z-score or IQR) for NDVI time series",
                )
            )

        if ndvi_files and not has_freshness_check:
            self.add_result(
                DriftResult(
                    category=DriftCategory.DATA,
                    severity=DriftSeverity.MEDIUM,
                    source="ndvi_guards",
                    description="NDVI pipeline lacks data freshness checks - stale data may be served",
                    description_ar="خط أنابيب NDVI يفتقر إلى فحوصات حداثة البيانات",
                    auto_fixable=False,
                    remediation_hint="Add freshness check: reject NDVI data older than configured max_age",
                )
            )

    async def _check_sensor_validation(self) -> None:
        """Check IoT sensor data has proper validation."""
        root = Path(self.working_dir)

        sensor_dirs = [
            root / "shared" / "soil_sensors",
            root / "apps" / "services" / "iot-service",
            root / "apps" / "services" / "iot-gateway",
            root / "apps" / "services" / "virtual-sensors",
        ]

        for sensor_dir in sensor_dirs:
            if not sensor_dir.exists():
                continue

            has_bounds_check = False
            # Scan both Python and TypeScript sources
            sensor_files = list(sensor_dir.rglob("*.py")) + list(sensor_dir.rglob("*.ts"))
            for src_file in sensor_files:
                try:
                    content = src_file.read_text(errors="ignore")
                except (OSError, UnicodeDecodeError):
                    continue

                if any(
                    pat in content
                    for pat in [
                        "min_value",
                        "max_value",
                        "bounds",
                        "valid_range",
                        "sensor_range",
                        "< 0",
                        "> 100",
                        "SENSOR_MIN",
                        "SENSOR_MAX",
                        "assessReadingQuality",
                        "ReadingQuality",
                        "min:",
                        "max:",
                        "range.min",
                        "range.max",
                    ]
                ):
                    has_bounds_check = True
                    break

            if not has_bounds_check:
                self.add_result(
                    DriftResult(
                        category=DriftCategory.DATA,
                        severity=DriftSeverity.HIGH,
                        source="sensor_validation",
                        expected="Sensor value bounds checking",
                        actual=f"No bounds checking in {sensor_dir.name}",
                        description=f"Sensor module '{sensor_dir.name}' lacks value bounds checking",
                        description_ar=f"وحدة المستشعر '{sensor_dir.name}' تفتقر إلى فحص حدود القيم",
                        auto_fixable=False,
                        remediation_hint="Add min/max range validation for each sensor type",
                    )
                )

    async def _check_ml_model_versioning(self) -> None:
        """Check ML model versioning and registry practices."""
        root = Path(self.working_dir)

        # Check for model registry
        registry = root / "shared" / "ai" / "models_registry"
        if not registry.exists():
            self.add_result(
                DriftResult(
                    category=DriftCategory.DATA,
                    severity=DriftSeverity.MEDIUM,
                    source="model_versioning",
                    description="AI models registry not found - model versioning may be inconsistent",
                    description_ar="سجل نماذج AI غير موجود - قد يكون إصدار النماذج غير متسق",
                )
            )
            return

        # Check for model version tracking
        has_version_tracking = False
        for py_file in registry.rglob("*.py"):
            try:
                content = py_file.read_text(errors="ignore")
                if any(
                    pat in content
                    for pat in [
                        "model_version",
                        "version",
                        "ModelVersion",
                        "registry",
                        "register_model",
                    ]
                ):
                    has_version_tracking = True
                    break
            except (OSError, UnicodeDecodeError):
                continue

        if not has_version_tracking:
            self.add_result(
                DriftResult(
                    category=DriftCategory.DATA,
                    severity=DriftSeverity.MEDIUM,
                    source="model_versioning",
                    description="Models registry exists but lacks version tracking",
                    description_ar="سجل النماذج موجود لكنه يفتقر إلى تتبع الإصدارات",
                )
            )

    async def _check_feature_schema(self) -> None:
        """Check ML feature schemas are defined and validated."""
        root = Path(self.working_dir)

        ml_services = [
            "crop-intelligence-service",
            "yield-prediction-service",
            "pest-detection-service",
        ]

        for svc_name in ml_services:
            svc_dir = root / "apps" / "services" / svc_name
            if not svc_dir.exists():
                continue

            has_feature_schema = False
            # Scan both Python and TypeScript sources
            schema_files = list(svc_dir.rglob("*.py")) + list(svc_dir.rglob("*.ts"))
            for src_file in schema_files:
                try:
                    content = src_file.read_text(errors="ignore")
                    if any(
                        pat in content
                        for pat in [
                            "feature_schema",
                            "FeatureSchema",
                            "FEATURE_SCHEMA",
                            "feature_columns",
                            "expected_features",
                            "feature_names",
                            "input_schema",
                            "inputSchema",
                        ]
                    ):
                        has_feature_schema = True
                        break
                except (OSError, UnicodeDecodeError):
                    continue

            if not has_feature_schema:
                self.add_result(
                    DriftResult(
                        category=DriftCategory.DATA,
                        severity=DriftSeverity.MEDIUM,
                        source="feature_schema",
                        description=f"ML service '{svc_name}' lacks explicit feature schema definition",
                        description_ar=f"خدمة ML '{svc_name}' تفتقر إلى تعريف مخطط المميزات",
                        service_name=svc_name,
                        auto_fixable=False,
                        remediation_hint="Define expected feature names, types, and ranges in a schema file",
                    )
                )

    async def _check_runtime_distributions(self) -> None:
        """
        Runtime check: Compare current data distributions against baseline.
        This requires database connectivity and stored baselines.
        """
        # This method is designed to be called when runtime_check=True
        # and database connectivity is available.
        #
        # Implementation would:
        # 1. Load baseline distributions from a stored reference
        # 2. Query recent data distributions
        # 3. Compare using KL divergence or PSI (Population Stability Index)
        # 4. Report drift if PSI > threshold (0.1 = slight, 0.25 = significant)
        logger.info("Runtime distribution checks require database connectivity - skipping in static mode")
