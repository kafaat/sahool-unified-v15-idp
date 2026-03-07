"""
Smart Agriculture Data Models | نماذج بيانات الزراعة الذكية

This module defines core data structures for smart agriculture control systems
including fertilizer ratios, crop growth stages, environmental thresholds,
and blockchain traceability records.

هذه الوحدة تحدد هياكل البيانات الأساسية لأنظمة التحكم في الزراعة الذكية
بما في ذلك نسب الأسمدة، مراحل نمو المحاصيل، عتبات البيئة، وسجلات تتبع البلوكتشين.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class CropGrowthStage(Enum):
    """
    Crop growth stages with fertility period indicators.
    مراحل نمو المحاصيل مع مؤشرات فترات الخصوبة.

    Each stage has specific nutrient requirements and environmental needs.
    كل مرحلة لها متطلبات غذائية واحتياجات بيئية محددة.
    """

    # Germination / الإنبات
    GERMINATION = "germination"

    # Seedling / الشتلة
    SEEDLING = "seedling"

    # Vegetative Growth / النمو الخضري
    VEGETATIVE = "vegetative"

    # Flowering / الإزهار
    FLOWERING = "flowering"

    # Fruit Setting / عقد الثمار
    FRUIT_SETTING = "fruit_setting"

    # Fruit Development / نمو الثمار
    FRUIT_DEVELOPMENT = "fruit_development"

    # Ripening / النضج
    RIPENING = "ripening"

    # Harvest / الحصاد
    HARVEST = "harvest"

    # Dormancy / السكون
    DORMANCY = "dormancy"

    @property
    def fertility_period(self) -> str:
        """
        Get the fertility period classification for this growth stage.
        الحصول على تصنيف فترة الخصوبة لمرحلة النمو هذه.

        Returns:
            str: Fertility period ('high', 'medium', 'low')
        """
        high_fertility = {
            self.VEGETATIVE,
            self.FLOWERING,
            self.FRUIT_SETTING,
        }
        medium_fertility = {
            self.SEEDLING,
            self.FRUIT_DEVELOPMENT,
        }

        if self in high_fertility:
            return "high"
        elif self in medium_fertility:
            return "medium"
        else:
            return "low"

    @property
    def npk_multiplier(self) -> tuple[float, float, float]:
        """
        Get NPK requirement multipliers for this growth stage.
        الحصول على معاملات متطلبات NPK لمرحلة النمو هذه.

        Returns:
            tuple: (N_multiplier, P_multiplier, K_multiplier)
        """
        multipliers = {
            self.GERMINATION: (0.3, 0.5, 0.3),
            self.SEEDLING: (0.5, 0.6, 0.4),
            self.VEGETATIVE: (1.2, 0.8, 0.7),
            self.FLOWERING: (0.8, 1.2, 1.0),
            self.FRUIT_SETTING: (0.7, 1.0, 1.2),
            self.FRUIT_DEVELOPMENT: (0.6, 0.8, 1.3),
            self.RIPENING: (0.4, 0.5, 1.0),
            self.HARVEST: (0.2, 0.2, 0.3),
            self.DORMANCY: (0.1, 0.1, 0.1),
        }
        return multipliers.get(self, (1.0, 1.0, 1.0))

    @property
    def name_ar(self) -> str:
        """Get Arabic name for the growth stage."""
        names = {
            self.GERMINATION: "الإنبات",
            self.SEEDLING: "الشتلة",
            self.VEGETATIVE: "النمو الخضري",
            self.FLOWERING: "الإزهار",
            self.FRUIT_SETTING: "عقد الثمار",
            self.FRUIT_DEVELOPMENT: "نمو الثمار",
            self.RIPENING: "النضج",
            self.HARVEST: "الحصاد",
            self.DORMANCY: "السكون",
        }
        return names.get(self, self.value)


@dataclass
class FertilizerRatio:
    """
    NPK fertilizer ratio configuration.
    تكوين نسبة أسمدة NPK.

    Represents the nitrogen (N), phosphorus (P), and potassium (K) ratio
    for fertilizer applications in smart agriculture systems.

    يمثل نسبة النيتروجين (N) والفوسفور (P) والبوتاسيوم (K)
    لتطبيقات الأسمدة في أنظمة الزراعة الذكية.

    Attributes:
        n_ratio: Nitrogen ratio (0.0-1.0) | نسبة النيتروجين
        p_ratio: Phosphorus ratio (0.0-1.0) | نسبة الفوسفور
        k_ratio: Potassium ratio (0.0-1.0) | نسبة البوتاسيوم
    """

    n_ratio: float
    p_ratio: float
    k_ratio: float

    def __post_init__(self):
        """Validate ratio values are within acceptable range."""
        for name, value in [
            ("n_ratio", self.n_ratio),
            ("p_ratio", self.p_ratio),
            ("k_ratio", self.k_ratio),
        ]:
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0.0 and 1.0, got {value}")

    @property
    def total(self) -> float:
        """
        Get total NPK ratio sum.
        الحصول على مجموع نسبة NPK الإجمالية.
        """
        return self.n_ratio + self.p_ratio + self.k_ratio

    def normalize(self) -> FertilizerRatio:
        """
        Normalize ratios to sum to 1.0.
        تطبيع النسب لتكون مجموعها 1.0.
        """
        total = self.total
        if total == 0:
            return FertilizerRatio(0.33, 0.33, 0.34)
        return FertilizerRatio(
            n_ratio=self.n_ratio / total,
            p_ratio=self.p_ratio / total,
            k_ratio=self.k_ratio / total,
        )

    def to_concentration(self, total_ppm: float) -> tuple[float, float, float]:
        """
        Convert ratios to actual concentrations in ppm.
        تحويل النسب إلى تركيزات فعلية بـ ppm.

        Args:
            total_ppm: Total fertilizer concentration in ppm

        Returns:
            tuple: (N_ppm, P_ppm, K_ppm)
        """
        normalized = self.normalize()
        return (
            normalized.n_ratio * total_ppm,
            normalized.p_ratio * total_ppm,
            normalized.k_ratio * total_ppm,
        )

    def __str__(self) -> str:
        """Format as NPK ratio string (e.g., '10-5-8')."""
        return f"{int(self.n_ratio * 100)}-{int(self.p_ratio * 100)}-{int(self.k_ratio * 100)}"


@dataclass
class EnvironmentThreshold:
    """
    Environmental control thresholds.
    عتبات التحكم البيئي.

    Defines acceptable ranges for temperature, humidity, and light
    for optimal crop growth conditions.

    يحدد النطاقات المقبولة لدرجة الحرارة والرطوبة والضوء
    لظروف نمو المحاصيل المثلى.

    Attributes:
        temperature_min: Minimum temperature in Celsius | الحد الأدنى لدرجة الحرارة
        temperature_max: Maximum temperature in Celsius | الحد الأقصى لدرجة الحرارة
        humidity_min: Minimum relative humidity (0-100%) | الحد الأدنى للرطوبة
        humidity_max: Maximum relative humidity (0-100%) | الحد الأقصى للرطوبة
        light_hours: Required daily light hours | ساعات الإضاءة اليومية المطلوبة
        co2_min: Minimum CO2 concentration (ppm) | الحد الأدنى لتركيز CO2
        co2_max: Maximum CO2 concentration (ppm) | الحد الأقصى لتركيز CO2
    """

    temperature_min: float
    temperature_max: float
    humidity_min: float
    humidity_max: float
    light_hours: float
    co2_min: float = 400.0
    co2_max: float = 1000.0

    def __post_init__(self):
        """Validate threshold values."""
        if self.temperature_min > self.temperature_max:
            raise ValueError("temperature_min cannot exceed temperature_max")
        if self.humidity_min > self.humidity_max:
            raise ValueError("humidity_min cannot exceed humidity_max")
        if not 0 <= self.humidity_min <= 100 or not 0 <= self.humidity_max <= 100:
            raise ValueError("Humidity values must be between 0 and 100")
        if not 0 <= self.light_hours <= 24:
            raise ValueError("light_hours must be between 0 and 24")

    def is_within_range(
        self,
        temperature: float,
        humidity: float,
        light_hours: float | None = None,
    ) -> dict[str, bool]:
        """
        Check if environmental conditions are within thresholds.
        التحقق مما إذا كانت الظروف البيئية ضمن العتبات.

        Args:
            temperature: Current temperature in Celsius
            humidity: Current relative humidity (%)
            light_hours: Current daily light hours (optional)

        Returns:
            dict: Status for each parameter
        """
        result = {
            "temperature": self.temperature_min <= temperature <= self.temperature_max,
            "humidity": self.humidity_min <= humidity <= self.humidity_max,
        }
        if light_hours is not None:
            result["light"] = light_hours >= self.light_hours
        return result

    def get_deviation(
        self,
        temperature: float,
        humidity: float,
    ) -> dict[str, float]:
        """
        Calculate deviation from optimal range midpoint.
        حساب الانحراف عن نقطة منتصف النطاق الأمثل.

        Returns:
            dict: Deviation values (negative = below, positive = above)
        """
        temp_mid = (self.temperature_min + self.temperature_max) / 2
        humidity_mid = (self.humidity_min + self.humidity_max) / 2

        return {
            "temperature_deviation": temperature - temp_mid,
            "humidity_deviation": humidity - humidity_mid,
        }

    @classmethod
    def for_crop(cls, crop_type: str, growth_stage: CropGrowthStage) -> EnvironmentThreshold:
        """
        Get recommended thresholds for specific crop and growth stage.
        الحصول على العتبات الموصى بها لمحصول ومرحلة نمو محددين.

        Args:
            crop_type: Type of crop (e.g., 'tomato', 'wheat')
            growth_stage: Current growth stage

        Returns:
            EnvironmentThreshold: Recommended thresholds
        """
        # Crop-specific base thresholds
        crop_thresholds = {
            "tomato": {"temp": (18, 30), "humidity": (60, 80), "light": 14},
            "wheat": {"temp": (10, 25), "humidity": (40, 70), "light": 10},
            "cucumber": {"temp": (20, 32), "humidity": (70, 90), "light": 12},
            "lettuce": {"temp": (10, 22), "humidity": (50, 70), "light": 10},
            "pepper": {"temp": (20, 30), "humidity": (60, 80), "light": 14},
            "date_palm": {"temp": (25, 45), "humidity": (30, 60), "light": 12},
        }

        base = crop_thresholds.get(crop_type.lower(), {"temp": (15, 30), "humidity": (50, 80), "light": 12})

        # Adjust for growth stage
        stage_adjustment = {
            CropGrowthStage.GERMINATION: {"temp_adj": -2, "humidity_adj": 10},
            CropGrowthStage.FLOWERING: {"temp_adj": 0, "humidity_adj": -5},
            CropGrowthStage.FRUIT_DEVELOPMENT: {"temp_adj": 2, "humidity_adj": 0},
        }

        adj = stage_adjustment.get(growth_stage, {"temp_adj": 0, "humidity_adj": 0})

        return cls(
            temperature_min=base["temp"][0] + adj["temp_adj"],
            temperature_max=base["temp"][1] + adj["temp_adj"],
            humidity_min=max(0, base["humidity"][0] + adj["humidity_adj"]),
            humidity_max=min(100, base["humidity"][1] + adj["humidity_adj"]),
            light_hours=base["light"],
        )


@dataclass
class BlockchainRecord:
    """
    Blockchain record for agricultural traceability.
    سجل البلوكتشين للتتبع الزراعي.

    Immutable record stored on blockchain for supply chain transparency.
    سجل غير قابل للتغيير مخزن على البلوكتشين لشفافية سلسلة التوريد.

    Attributes:
        batch_id: Unique batch identifier | معرف الدفعة الفريد
        hash: Cryptographic hash of the record | التجزئة المشفرة للسجل
        timestamp: Record creation timestamp | الطابع الزمني لإنشاء السجل
        data: Record payload data | بيانات حمولة السجل
        previous_hash: Hash of previous record in chain | تجزئة السجل السابق في السلسلة
        block_number: Block number in the chain | رقم الكتلة في السلسلة
    """

    batch_id: str
    hash: str
    timestamp: datetime
    data: dict[str, Any]
    previous_hash: str = ""
    block_number: int = 0

    def to_dict(self) -> dict[str, Any]:
        """
        Convert record to dictionary format.
        تحويل السجل إلى تنسيق القاموس.
        """
        return {
            "batch_id": self.batch_id,
            "hash": self.hash,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "previous_hash": self.previous_hash,
            "block_number": self.block_number,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BlockchainRecord:
        """
        Create record from dictionary.
        إنشاء سجل من القاموس.
        """
        return cls(
            batch_id=data["batch_id"],
            hash=data["hash"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            data=data["data"],
            previous_hash=data.get("previous_hash", ""),
            block_number=data.get("block_number", 0),
        )


@dataclass
class OperationRecord:
    """
    Agricultural operation record for traceability.
    سجل العمليات الزراعية للتتبع.

    Attributes:
        operation_id: Unique operation identifier | معرف العملية الفريد
        operation_type: Type of operation | نوع العملية
        timestamp: Operation timestamp | الطابع الزمني للعملية
        details: Operation details | تفاصيل العملية
        operator_id: ID of person/system performing operation | معرف المشغل
        location: GPS coordinates or field ID | الإحداثيات أو معرف الحقل
        verified: Whether operation was verified | هل تم التحقق من العملية
    """

    operation_id: str
    operation_type: str
    timestamp: datetime
    details: dict[str, Any]
    operator_id: str = ""
    location: str = ""
    verified: bool = False


@dataclass
class Certification:
    """
    Agricultural certification record.
    سجل الشهادات الزراعية.

    Attributes:
        cert_id: Certification identifier | معرف الشهادة
        cert_type: Type of certification (e.g., 'organic', 'GlobalGAP') | نوع الشهادة
        issuer: Certifying organization | المنظمة المصدرة
        issue_date: Date of issuance | تاريخ الإصدار
        expiry_date: Date of expiration | تاريخ الانتهاء
        scope: Certification scope/products covered | نطاق الشهادة
        status: Current status | الحالة الحالية
    """

    cert_id: str
    cert_type: str
    issuer: str
    issue_date: datetime
    expiry_date: datetime
    scope: list[str]
    status: str = "active"

    @property
    def is_valid(self) -> bool:
        """Check if certification is currently valid."""
        return self.status == "active" and datetime.now() < self.expiry_date


@dataclass
class TraceabilityReport:
    """
    Complete traceability report for a crop batch.
    تقرير التتبع الكامل لدفعة المحصول.

    Comprehensive report containing all operations, certifications,
    and quality records for full supply chain transparency.

    تقرير شامل يحتوي على جميع العمليات والشهادات
    وسجلات الجودة لشفافية سلسلة التوريد الكاملة.

    Attributes:
        batch_id: Unique batch identifier | معرف الدفعة
        crop: Crop type and variety | نوع المحصول والصنف
        operations: List of all operations | قائمة جميع العمليات
        certifications: Active certifications | الشهادات النشطة
        test_reports: Quality test reports | تقارير اختبار الجودة
        origin_farm: Source farm information | معلومات المزرعة المصدر
        harvest_date: Date of harvest | تاريخ الحصاد
        blockchain_hash: Immutable blockchain reference | مرجع البلوكتشين غير القابل للتغيير
    """

    batch_id: str
    crop: str
    operations: list[OperationRecord] = field(default_factory=list)
    certifications: list[Certification] = field(default_factory=list)
    test_reports: list[dict[str, Any]] = field(default_factory=list)
    origin_farm: str = ""
    harvest_date: datetime | None = None
    blockchain_hash: str = ""

    def add_operation(self, operation: OperationRecord) -> None:
        """
        Add operation to the report.
        إضافة عملية إلى التقرير.
        """
        self.operations.append(operation)

    def add_certification(self, certification: Certification) -> None:
        """
        Add certification to the report.
        إضافة شهادة إلى التقرير.
        """
        self.certifications.append(certification)

    def get_active_certifications(self) -> list[Certification]:
        """
        Get list of currently valid certifications.
        الحصول على قائمة الشهادات الصالحة حاليا.
        """
        return [cert for cert in self.certifications if cert.is_valid]

    def get_operations_by_type(self, operation_type: str) -> list[OperationRecord]:
        """
        Filter operations by type.
        تصفية العمليات حسب النوع.
        """
        return [op for op in self.operations if op.operation_type == operation_type]

    def to_dict(self) -> dict[str, Any]:
        """
        Convert report to dictionary format for serialization.
        تحويل التقرير إلى تنسيق قاموس للتسلسل.
        """
        return {
            "batch_id": self.batch_id,
            "crop": self.crop,
            "operations": [
                {
                    "operation_id": op.operation_id,
                    "operation_type": op.operation_type,
                    "timestamp": op.timestamp.isoformat(),
                    "details": op.details,
                    "operator_id": op.operator_id,
                    "location": op.location,
                    "verified": op.verified,
                }
                for op in self.operations
            ],
            "certifications": [
                {
                    "cert_id": cert.cert_id,
                    "cert_type": cert.cert_type,
                    "issuer": cert.issuer,
                    "issue_date": cert.issue_date.isoformat(),
                    "expiry_date": cert.expiry_date.isoformat(),
                    "scope": cert.scope,
                    "status": cert.status,
                }
                for cert in self.certifications
            ],
            "test_reports": self.test_reports,
            "origin_farm": self.origin_farm,
            "harvest_date": self.harvest_date.isoformat() if self.harvest_date else None,
            "blockchain_hash": self.blockchain_hash,
        }

    def generate_summary(self, language: str = "en") -> str:
        """
        Generate human-readable summary of the report.
        إنشاء ملخص مقروء للتقرير.

        Args:
            language: Output language ('en' or 'ar')

        Returns:
            str: Formatted summary
        """
        if language == "ar":
            return self._generate_summary_ar()
        return self._generate_summary_en()

    def _generate_summary_en(self) -> str:
        """Generate English summary."""
        lines = [
            f"Traceability Report - Batch: {self.batch_id}",
            f"Crop: {self.crop}",
            f"Origin: {self.origin_farm}",
            f"Total Operations: {len(self.operations)}",
            f"Active Certifications: {len(self.get_active_certifications())}",
            f"Test Reports: {len(self.test_reports)}",
        ]
        if self.blockchain_hash:
            lines.append(f"Blockchain Hash: {self.blockchain_hash[:16]}...")
        return "\n".join(lines)

    def _generate_summary_ar(self) -> str:
        """Generate Arabic summary."""
        lines = [
            f"تقرير التتبع - الدفعة: {self.batch_id}",
            f"المحصول: {self.crop}",
            f"المصدر: {self.origin_farm}",
            f"إجمالي العمليات: {len(self.operations)}",
            f"الشهادات النشطة: {len(self.get_active_certifications())}",
            f"تقارير الاختبار: {len(self.test_reports)}",
        ]
        if self.blockchain_hash:
            lines.append(f"تجزئة البلوكتشين: ...{self.blockchain_hash[:16]}")
        return "\n".join(lines)


@dataclass
class FertilizerCommand:
    """
    Command output from PID controller for fertilizer application.
    أمر الإخراج من متحكم PID لتطبيق الأسمدة.

    Attributes:
        n_amount: Nitrogen amount (kg/ha) | كمية النيتروجين
        p_amount: Phosphorus amount (kg/ha) | كمية الفوسفور
        k_amount: Potassium amount (kg/ha) | كمية البوتاسيوم
        water_volume: Water volume (liters/ha) | حجم المياه
        application_rate: Application rate (L/min) | معدل التطبيق
        duration_minutes: Application duration | مدة التطبيق
        timestamp: Command generation time | وقت توليد الأمر
    """

    n_amount: float
    p_amount: float
    k_amount: float
    water_volume: float
    application_rate: float
    duration_minutes: float
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def total_fertilizer(self) -> float:
        """Get total fertilizer amount in kg/ha."""
        return self.n_amount + self.p_amount + self.k_amount

    def to_dict(self) -> dict[str, Any]:
        """Convert command to dictionary."""
        return {
            "npk": {
                "n": self.n_amount,
                "p": self.p_amount,
                "k": self.k_amount,
            },
            "water_volume_l_ha": self.water_volume,
            "application_rate_l_min": self.application_rate,
            "duration_minutes": self.duration_minutes,
            "timestamp": self.timestamp.isoformat(),
        }
