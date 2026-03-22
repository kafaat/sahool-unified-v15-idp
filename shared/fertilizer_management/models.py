"""
Fertilizer Management Models - نماذج إدارة الأسمدة

Data models for fertilizer inventory, applications, and nutrient tracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum


class FertilizerType(StrEnum):
    """Type of fertilizer - نوع السماد"""

    NITROGEN = "nitrogen"  # نيتروجيني
    PHOSPHORUS = "phosphorus"  # فسفوري
    POTASSIUM = "potassium"  # بوتاسي
    NPK_COMPOUND = "npk_compound"  # مركب NPK
    ORGANIC = "organic"  # عضوي
    MICRONUTRIENT = "micronutrient"  # عناصر صغرى
    SLOW_RELEASE = "slow_release"  # بطيء الإطلاق
    LIQUID = "liquid"  # سائل
    FOLIAR = "foliar"  # ورقي


class FertilizerForm(StrEnum):
    """Physical form of fertilizer - الشكل الفيزيائي للسماد"""

    GRANULAR = "granular"  # حبيبي
    PRILLED = "prilled"  # حبيبات مكورة
    POWDER = "powder"  # مسحوق
    LIQUID = "liquid"  # سائل
    SUSPENSION = "suspension"  # معلق
    CRYSTALLINE = "crystalline"  # بلوري
    PELLET = "pellet"  # قرصي


class ApplicationMethod(StrEnum):
    """Method of fertilizer application - طريقة التطبيق"""

    BROADCAST = "broadcast"  # نثر
    BANDING = "banding"  # شريطي
    SIDE_DRESS = "side_dress"  # تسميد جانبي
    TOPDRESS = "topdress"  # تسميد سطحي
    FERTIGATION = "fertigation"  # تسميد بالري
    FOLIAR_SPRAY = "foliar_spray"  # رش ورقي
    INJECTION = "injection"  # حقن
    INCORPORATION = "incorporation"  # خلط بالتربة


class NutrientStatus(StrEnum):
    """Nutrient level status - حالة مستوى العنصر"""

    DEFICIENT = "deficient"  # نقص
    LOW = "low"  # منخفض
    OPTIMAL = "optimal"  # مثالي
    HIGH = "high"  # مرتفع
    EXCESSIVE = "excessive"  # زائد


class InventoryStatus(StrEnum):
    """Inventory status - حالة المخزون"""

    IN_STOCK = "in_stock"  # متوفر
    LOW_STOCK = "low_stock"  # مخزون منخفض
    OUT_OF_STOCK = "out_of_stock"  # نفد المخزون
    EXPIRED = "expired"  # منتهي الصلاحية
    RESERVED = "reserved"  # محجوز


class ComplianceLevel(StrEnum):
    """Environmental compliance level - مستوى الامتثال البيئي"""

    COMPLIANT = "compliant"  # ممتثل
    WARNING = "warning"  # تحذير
    VIOLATION = "violation"  # مخالفة
    RESTRICTED = "restricted"  # مقيد


@dataclass
class NutrientComposition:
    """
    Nutrient composition of a fertilizer - التركيب الغذائي للسماد
    Values in percentage (%)
    """

    nitrogen_n: float = 0.0  # نيتروجين N
    phosphorus_p2o5: float = 0.0  # فسفور P2O5
    potassium_k2o: float = 0.0  # بوتاسيوم K2O
    sulfur_s: float = 0.0  # كبريت S
    calcium_ca: float = 0.0  # كالسيوم Ca
    magnesium_mg: float = 0.0  # مغنيسيوم Mg
    iron_fe: float = 0.0  # حديد Fe
    zinc_zn: float = 0.0  # زنك Zn
    manganese_mn: float = 0.0  # منجنيز Mn
    copper_cu: float = 0.0  # نحاس Cu
    boron_b: float = 0.0  # بورون B
    molybdenum_mo: float = 0.0  # موليبدنوم Mo
    chlorine_cl: float = 0.0  # كلور Cl

    @property
    def npk_ratio(self) -> str:
        """Get NPK ratio string (e.g., 20-20-20)"""
        return f"{int(self.nitrogen_n)}-{int(self.phosphorus_p2o5)}-{int(self.potassium_k2o)}"

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "N": self.nitrogen_n,
            "P2O5": self.phosphorus_p2o5,
            "K2O": self.potassium_k2o,
            "S": self.sulfur_s,
            "Ca": self.calcium_ca,
            "Mg": self.magnesium_mg,
            "Fe": self.iron_fe,
            "Zn": self.zinc_zn,
            "Mn": self.manganese_mn,
            "Cu": self.copper_cu,
            "B": self.boron_b,
            "Mo": self.molybdenum_mo,
            "Cl": self.chlorine_cl,
        }


@dataclass
class Fertilizer:
    """
    Fertilizer product definition - تعريف منتج السماد
    """

    id: str
    name: str
    name_ar: str
    fertilizer_type: FertilizerType
    form: FertilizerForm

    # Composition
    composition: NutrientComposition

    # Product details
    manufacturer: str = ""
    manufacturer_ar: str = ""
    trade_name: str = ""
    trade_name_ar: str = ""
    registration_number: str = ""

    # Physical properties
    density_kg_per_liter: float | None = None  # For liquids
    bulk_density_kg_per_m3: float | None = None  # For solids
    solubility_g_per_liter: float | None = None

    # Application info
    recommended_crops: list[str] = field(default_factory=list)
    application_methods: list[ApplicationMethod] = field(default_factory=list)
    max_application_rate_kg_ha: float | None = None
    min_application_rate_kg_ha: float | None = None

    # Safety and compliance
    is_organic_certified: bool = False
    organic_certification: str = ""
    environmental_restrictions: list[str] = field(default_factory=list)
    environmental_restrictions_ar: list[str] = field(default_factory=list)
    buffer_zone_m: int = 0  # Distance from water bodies

    # Cost
    unit_price: Decimal = Decimal("0.00")
    price_currency: str = "SAR"
    unit_size_kg: float = 50.0

    # Metadata
    is_active: bool = True
    notes: str = ""
    notes_ar: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "name_ar": self.name_ar,
            "type": self.fertilizer_type.value,
            "form": self.form.value,
            "composition": self.composition.to_dict(),
            "npk_ratio": self.composition.npk_ratio,
            "manufacturer": self.manufacturer,
            "is_organic_certified": self.is_organic_certified,
            "unit_price": float(self.unit_price),
            "unit_size_kg": self.unit_size_kg,
        }


@dataclass
class InventoryItem:
    """
    Fertilizer inventory item - عنصر مخزون السماد
    """

    id: str
    tenant_id: str
    fertilizer_id: str
    fertilizer_name: str
    fertilizer_name_ar: str

    # Quantity
    quantity_kg: float
    reserved_kg: float = 0.0

    # Location
    warehouse_id: str = ""
    warehouse_name: str = ""
    storage_location: str = ""  # Bin/shelf location

    # Batch info
    batch_number: str = ""
    purchase_date: datetime | None = None
    expiry_date: datetime | None = None

    # Cost tracking
    purchase_price_per_kg: Decimal = Decimal("0.00")
    currency: str = "SAR"

    # Status
    status: InventoryStatus = InventoryStatus.IN_STOCK
    minimum_stock_kg: float = 100.0  # Alert threshold
    reorder_point_kg: float = 200.0

    # Metadata
    supplier: str = ""
    supplier_ar: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))
    notes: str = ""
    notes_ar: str = ""

    @property
    def available_kg(self) -> float:
        """Get available quantity (total - reserved)"""
        return max(0.0, self.quantity_kg - self.reserved_kg)

    @property
    def is_low_stock(self) -> bool:
        """Check if stock is below minimum"""
        return self.available_kg <= self.minimum_stock_kg

    @property
    def is_expired(self) -> bool:
        """Check if item is expired"""
        if self.expiry_date:
            return datetime.now(UTC).replace(tzinfo=None)() > self.expiry_date
        return False

    @property
    def total_value(self) -> Decimal:
        """Calculate total inventory value"""
        return self.purchase_price_per_kg * Decimal(str(self.quantity_kg))

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "fertilizer_id": self.fertilizer_id,
            "fertilizer_name": self.fertilizer_name,
            "fertilizer_name_ar": self.fertilizer_name_ar,
            "quantity_kg": self.quantity_kg,
            "available_kg": self.available_kg,
            "reserved_kg": self.reserved_kg,
            "status": self.status.value,
            "is_low_stock": self.is_low_stock,
            "is_expired": self.is_expired,
            "total_value": float(self.total_value),
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
        }


@dataclass
class FertilizerApplication:
    """
    Record of fertilizer application - سجل تطبيق السماد
    """

    id: str
    tenant_id: str
    field_id: str
    fertilizer_id: str
    inventory_item_id: str | None = None

    # Application details
    application_date: datetime = field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))
    application_method: ApplicationMethod = ApplicationMethod.BROADCAST

    # Quantities
    application_rate_kg_ha: float = 0.0
    total_quantity_kg: float = 0.0
    area_treated_ha: float = 0.0

    # Nutrients applied (calculated from fertilizer composition)
    nitrogen_applied_kg_ha: float = 0.0
    phosphorus_applied_kg_ha: float = 0.0
    potassium_applied_kg_ha: float = 0.0

    # Crop info
    crop: str = ""
    crop_ar: str = ""
    growth_stage: str = ""
    growth_stage_ar: str = ""

    # Weather conditions
    temperature_c: float | None = None
    humidity_percent: float | None = None
    soil_moisture_percent: float | None = None
    wind_speed_kmh: float | None = None

    # Applicator
    applicator_id: str | None = None
    applicator_name: str = ""
    equipment_used: str = ""

    # Cost
    total_cost: Decimal = Decimal("0.00")
    cost_per_ha: Decimal = Decimal("0.00")
    currency: str = "SAR"

    # Compliance
    compliance_status: ComplianceLevel = ComplianceLevel.COMPLIANT
    compliance_notes: str = ""
    compliance_notes_ar: str = ""

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))
    notes: str = ""
    notes_ar: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for NATS publishing"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "field_id": self.field_id,
            "fertilizer_id": self.fertilizer_id,
            "application_date": self.application_date.isoformat(),
            "application_method": self.application_method.value,
            "application_rate_kg_ha": self.application_rate_kg_ha,
            "total_quantity_kg": self.total_quantity_kg,
            "area_treated_ha": self.area_treated_ha,
            "nutrients_applied": {
                "N": self.nitrogen_applied_kg_ha,
                "P2O5": self.phosphorus_applied_kg_ha,
                "K2O": self.potassium_applied_kg_ha,
            },
            "crop": self.crop,
            "growth_stage": self.growth_stage,
            "compliance_status": self.compliance_status.value,
            "total_cost": float(self.total_cost),
        }


@dataclass
class SoilTest:
    """
    Soil test results - نتائج تحليل التربة
    """

    id: str
    tenant_id: str
    field_id: str
    sample_date: datetime
    lab_name: str = ""

    # Macronutrients (ppm or mg/kg)
    nitrogen_ppm: float = 0.0
    phosphorus_ppm: float = 0.0
    potassium_ppm: float = 0.0

    # Secondary nutrients
    sulfur_ppm: float = 0.0
    calcium_ppm: float = 0.0
    magnesium_ppm: float = 0.0

    # Micronutrients
    iron_ppm: float = 0.0
    zinc_ppm: float = 0.0
    manganese_ppm: float = 0.0
    copper_ppm: float = 0.0
    boron_ppm: float = 0.0

    # Soil properties
    ph: float = 7.0
    ec_ds_m: float = 0.0  # Electrical conductivity dS/m
    organic_matter_percent: float = 0.0
    cec_meq_100g: float = 0.0  # Cation Exchange Capacity

    # Texture
    sand_percent: float = 0.0
    silt_percent: float = 0.0
    clay_percent: float = 0.0
    soil_texture: str = ""  # sandy, loam, clay, etc.
    soil_texture_ar: str = ""

    # Metadata
    sample_depth_cm: int = 30
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))
    notes: str = ""
    notes_ar: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "field_id": self.field_id,
            "sample_date": self.sample_date.isoformat(),
            "macronutrients": {
                "N": self.nitrogen_ppm,
                "P": self.phosphorus_ppm,
                "K": self.potassium_ppm,
            },
            "secondary_nutrients": {
                "S": self.sulfur_ppm,
                "Ca": self.calcium_ppm,
                "Mg": self.magnesium_ppm,
            },
            "micronutrients": {
                "Fe": self.iron_ppm,
                "Zn": self.zinc_ppm,
                "Mn": self.manganese_ppm,
                "Cu": self.copper_ppm,
                "B": self.boron_ppm,
            },
            "soil_properties": {
                "pH": self.ph,
                "EC": self.ec_ds_m,
                "OM": self.organic_matter_percent,
                "CEC": self.cec_meq_100g,
            },
            "texture": {
                "sand": self.sand_percent,
                "silt": self.silt_percent,
                "clay": self.clay_percent,
                "class": self.soil_texture,
            },
        }


@dataclass
class NutrientBalance:
    """
    Nutrient balance for a field - ميزان العناصر الغذائية للحقل
    """

    field_id: str
    season: str
    crop: str
    crop_ar: str
    calculation_date: datetime = field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))

    # Soil available (from soil test)
    soil_n_kg_ha: float = 0.0
    soil_p_kg_ha: float = 0.0
    soil_k_kg_ha: float = 0.0

    # Crop requirement
    crop_n_requirement_kg_ha: float = 0.0
    crop_p_requirement_kg_ha: float = 0.0
    crop_k_requirement_kg_ha: float = 0.0

    # Applied so far
    applied_n_kg_ha: float = 0.0
    applied_p_kg_ha: float = 0.0
    applied_k_kg_ha: float = 0.0

    # Balance (negative = deficit, positive = surplus)
    n_balance_kg_ha: float = 0.0
    p_balance_kg_ha: float = 0.0
    k_balance_kg_ha: float = 0.0

    # Status
    n_status: NutrientStatus = NutrientStatus.OPTIMAL
    p_status: NutrientStatus = NutrientStatus.OPTIMAL
    k_status: NutrientStatus = NutrientStatus.OPTIMAL

    # Additional nutrients
    s_balance_kg_ha: float = 0.0
    ca_balance_kg_ha: float = 0.0
    mg_balance_kg_ha: float = 0.0

    # Micronutrient status
    micronutrient_deficiencies: list[str] = field(default_factory=list)
    micronutrient_deficiencies_ar: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "field_id": self.field_id,
            "season": self.season,
            "crop": self.crop,
            "balance": {
                "N": self.n_balance_kg_ha,
                "P2O5": self.p_balance_kg_ha,
                "K2O": self.k_balance_kg_ha,
            },
            "status": {
                "N": self.n_status.value,
                "P": self.p_status.value,
                "K": self.k_status.value,
            },
            "micronutrient_deficiencies": self.micronutrient_deficiencies,
        }


@dataclass
class EnvironmentalCompliance:
    """
    Environmental compliance assessment - تقييم الامتثال البيئي
    """

    field_id: str
    assessment_date: datetime = field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))

    # Overall status
    overall_status: ComplianceLevel = ComplianceLevel.COMPLIANT

    # Nitrogen management
    total_n_applied_kg_ha: float = 0.0
    max_n_allowed_kg_ha: float = 200.0
    n_compliance: ComplianceLevel = ComplianceLevel.COMPLIANT

    # Phosphorus management
    total_p_applied_kg_ha: float = 0.0
    max_p_allowed_kg_ha: float = 50.0
    p_compliance: ComplianceLevel = ComplianceLevel.COMPLIANT

    # Buffer zones
    water_body_distance_m: float | None = None
    required_buffer_m: float = 10.0
    buffer_compliance: ComplianceLevel = ComplianceLevel.COMPLIANT

    # Application timing
    restricted_period_violation: bool = False
    restricted_period_message: str = ""
    restricted_period_message_ar: str = ""

    # Soil protection
    soil_erosion_risk: str = "low"  # low, medium, high
    soil_erosion_risk_ar: str = ""

    # Recommendations
    recommendations_en: list[str] = field(default_factory=list)
    recommendations_ar: list[str] = field(default_factory=list)

    # Violations
    violations_en: list[str] = field(default_factory=list)
    violations_ar: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "field_id": self.field_id,
            "assessment_date": self.assessment_date.isoformat(),
            "overall_status": self.overall_status.value,
            "nitrogen": {
                "applied": self.total_n_applied_kg_ha,
                "max_allowed": self.max_n_allowed_kg_ha,
                "status": self.n_compliance.value,
            },
            "phosphorus": {
                "applied": self.total_p_applied_kg_ha,
                "max_allowed": self.max_p_allowed_kg_ha,
                "status": self.p_compliance.value,
            },
            "buffer_compliance": self.buffer_compliance.value,
            "violations": self.violations_en,
            "recommendations": self.recommendations_en,
        }


@dataclass
class CostAnalysis:
    """
    Fertilizer cost analysis - تحليل تكلفة الأسمدة
    """

    field_id: str
    season: str
    analysis_date: datetime = field(default_factory=lambda: datetime.now(UTC).replace(tzinfo=None))

    # Area
    area_ha: float = 0.0

    # Costs
    total_fertilizer_cost: Decimal = Decimal("0.00")
    total_application_cost: Decimal = Decimal("0.00")
    total_cost: Decimal = Decimal("0.00")
    cost_per_ha: Decimal = Decimal("0.00")
    currency: str = "SAR"

    # By nutrient
    cost_per_kg_n: Decimal = Decimal("0.00")
    cost_per_kg_p: Decimal = Decimal("0.00")
    cost_per_kg_k: Decimal = Decimal("0.00")

    # Comparison
    previous_season_cost: Decimal = Decimal("0.00")
    cost_change_percent: float = 0.0

    # Breakdown by fertilizer type
    costs_by_fertilizer: dict = field(default_factory=dict)

    # Recommendations for cost optimization
    savings_opportunities_en: list[str] = field(default_factory=list)
    savings_opportunities_ar: list[str] = field(default_factory=list)
    potential_savings: Decimal = Decimal("0.00")

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "field_id": self.field_id,
            "season": self.season,
            "total_cost": float(self.total_cost),
            "cost_per_ha": float(self.cost_per_ha),
            "currency": self.currency,
            "cost_by_nutrient": {
                "N": float(self.cost_per_kg_n),
                "P": float(self.cost_per_kg_p),
                "K": float(self.cost_per_kg_k),
            },
            "cost_change_percent": self.cost_change_percent,
            "potential_savings": float(self.potential_savings),
            "savings_opportunities": self.savings_opportunities_en,
        }
