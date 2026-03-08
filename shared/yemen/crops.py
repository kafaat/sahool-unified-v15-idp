"""
Yemen crop parameters for SAHOOL platform.

Crop coefficients (Kc), growth stages, and agronomic parameters adapted
for Yemen's agro-ecological zones. Includes traditional crops (qat, coffee)
and major food crops grown across Yemen's diverse climate zones.

Sources:
- FAO-56 Tables (base Kc values)
- Yemen Ministry of Agriculture crop bulletins
- UNDP SIERY project field data (Hadhramaut)
- FAO Yemen IWRM project (Sana'a basin)
- Regional research papers on Yemeni agriculture
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GrowthStage:
    """Crop growth stage with duration and Kc."""

    name: str
    name_ar: str
    duration_days: int
    kc: float
    gdd_cumulative: float | None = None  # Growing Degree Days


@dataclass
class YemenCropParameters:
    """Complete crop parameters adapted for Yemen conditions."""

    name: str
    name_ar: str
    scientific_name: str
    crop_type: str  # cereal, vegetable, fruit, stimulant, legume, fodder
    root_depth_m: float  # Effective root depth (Zr) in meters
    depletion_fraction: float  # Allowable depletion fraction (p) for no stress
    yield_response_factor: float  # Ky - yield response to water stress
    salinity_threshold_dsm: float  # ECe threshold (dS/m)
    salinity_slope: float  # Yield decrease per dS/m above threshold
    growth_stages: list[GrowthStage] = field(default_factory=list)
    total_season_days: int = 0
    optimal_temp_min: float = 15.0  # °C
    optimal_temp_max: float = 35.0  # °C
    critical_temp_min: float = 5.0  # °C below which damage occurs
    critical_temp_max: float = 45.0  # °C above which damage occurs
    regions: list[str] = field(default_factory=list)  # Suitable Yemen regions
    notes: str = ""
    notes_ar: str = ""

    @property
    def kc_ini(self) -> float:
        return self.growth_stages[0].kc if self.growth_stages else 0.3

    @property
    def kc_mid(self) -> float:
        if len(self.growth_stages) >= 3:
            return self.growth_stages[2].kc
        return 1.0

    @property
    def kc_end(self) -> float:
        return self.growth_stages[-1].kc if self.growth_stages else 0.4


YEMEN_CROPS: dict[str, YemenCropParameters] = {
    "wheat": YemenCropParameters(
        name="Wheat",
        name_ar="القمح",
        scientific_name="Triticum aestivum",
        crop_type="cereal",
        root_depth_m=1.2,
        depletion_fraction=0.55,
        yield_response_factor=1.05,
        salinity_threshold_dsm=6.0,
        salinity_slope=7.1,
        growth_stages=[
            GrowthStage("Initial", "المرحلة الأولية", 30, 0.4, 100),
            GrowthStage("Development", "مرحلة النمو", 40, 0.75, 400),
            GrowthStage("Mid-season", "منتصف الموسم", 50, 1.15, 900),
            GrowthStage("Late", "المرحلة المتأخرة", 30, 0.40, 1400),
        ],
        total_season_days=150,
        optimal_temp_min=10.0,
        optimal_temp_max=25.0,
        critical_temp_min=0.0,
        critical_temp_max=35.0,
        regions=["highlands", "northern_highlands", "eastern_plateau"],
        notes="Major winter crop in Yemen highlands. Sakha varieties adapted to semi-arid.",
        notes_ar="محصول شتوي رئيسي في المرتفعات اليمنية. أصناف سخا مكيفة للمناطق شبه الجافة.",
    ),
    "barley": YemenCropParameters(
        name="Barley",
        name_ar="الشعير",
        scientific_name="Hordeum vulgare",
        crop_type="cereal",
        root_depth_m=1.0,
        depletion_fraction=0.55,
        yield_response_factor=1.0,
        salinity_threshold_dsm=8.0,
        salinity_slope=5.0,
        growth_stages=[
            GrowthStage("Initial", "المرحلة الأولية", 25, 0.3, 80),
            GrowthStage("Development", "مرحلة النمو", 35, 0.70, 350),
            GrowthStage("Mid-season", "منتصف الموسم", 45, 1.10, 800),
            GrowthStage("Late", "المرحلة المتأخرة", 25, 0.35, 1200),
        ],
        total_season_days=130,
        optimal_temp_min=8.0,
        optimal_temp_max=22.0,
        critical_temp_min=-2.0,
        critical_temp_max=35.0,
        regions=["highlands", "northern_highlands", "eastern_plateau"],
        notes="More drought and salt tolerant than wheat. Important animal feed.",
        notes_ar="أكثر تحملاً للجفاف والملوحة من القمح. علف حيواني مهم.",
    ),
    "sorghum": YemenCropParameters(
        name="Sorghum",
        name_ar="الذرة الرفيعة",
        scientific_name="Sorghum bicolor",
        crop_type="cereal",
        root_depth_m=1.2,
        depletion_fraction=0.55,
        yield_response_factor=0.9,
        salinity_threshold_dsm=6.8,
        salinity_slope=16.0,
        growth_stages=[
            GrowthStage("Initial", "المرحلة الأولية", 20, 0.35, 100),
            GrowthStage("Development", "مرحلة النمو", 35, 0.70, 450),
            GrowthStage("Mid-season", "منتصف الموسم", 45, 1.10, 1000),
            GrowthStage("Late", "المرحلة المتأخرة", 30, 0.55, 1500),
        ],
        total_season_days=130,
        optimal_temp_min=20.0,
        optimal_temp_max=37.0,
        critical_temp_min=10.0,
        critical_temp_max=45.0,
        regions=["tihama", "eastern_plateau", "highlands", "southern_coast"],
        notes="Traditional Yemen crop. Major staple in Tihama coastal plain.",
        notes_ar="محصول يمني تقليدي. غذاء أساسي في سهل تهامة الساحلي.",
    ),
    "millet": YemenCropParameters(
        name="Millet",
        name_ar="الدخن",
        scientific_name="Pennisetum glaucum",
        crop_type="cereal",
        root_depth_m=1.0,
        depletion_fraction=0.55,
        yield_response_factor=0.9,
        salinity_threshold_dsm=6.8,
        salinity_slope=16.0,
        growth_stages=[
            GrowthStage("Initial", "المرحلة الأولية", 15, 0.30, 80),
            GrowthStage("Development", "مرحلة النمو", 25, 0.65, 350),
            GrowthStage("Mid-season", "منتصف الموسم", 35, 1.00, 750),
            GrowthStage("Late", "المرحلة المتأخرة", 25, 0.40, 1100),
        ],
        total_season_days=100,
        optimal_temp_min=25.0,
        optimal_temp_max=40.0,
        critical_temp_min=12.0,
        critical_temp_max=48.0,
        regions=["tihama", "eastern_plateau"],
        notes="Highly drought tolerant. Important in marginal areas of Yemen.",
        notes_ar="شديد التحمل للجفاف. مهم في المناطق الهامشية في اليمن.",
    ),
    "qat": YemenCropParameters(
        name="Qat",
        name_ar="القات",
        scientific_name="Catha edulis",
        crop_type="stimulant",
        root_depth_m=1.5,
        depletion_fraction=0.45,
        yield_response_factor=0.8,
        salinity_threshold_dsm=2.0,
        salinity_slope=12.0,
        growth_stages=[
            GrowthStage("Winter dormancy", "سكون شتوي", 90, 0.50, 0),
            GrowthStage("Spring flush", "نمو ربيعي", 60, 0.85, 500),
            GrowthStage("Active growth", "نمو نشط", 120, 1.00, 1500),
            GrowthStage("Harvest cycles", "دورات حصاد", 95, 0.90, 2500),
        ],
        total_season_days=365,
        optimal_temp_min=15.0,
        optimal_temp_max=30.0,
        critical_temp_min=5.0,
        critical_temp_max=38.0,
        regions=["highlands", "northern_highlands"],
        notes="Consumes 30% of Sana'a basin water. Perennial. 3-4 harvests/year.",
        notes_ar="يستهلك 30% من مياه حوض صنعاء. معمر. 3-4 حصادات/سنة.",
    ),
    "coffee_arabica": YemenCropParameters(
        name="Yemen Coffee (Arabica)",
        name_ar="البن اليمني",
        scientific_name="Coffea arabica",
        crop_type="stimulant",
        root_depth_m=1.2,
        depletion_fraction=0.40,
        yield_response_factor=1.1,
        salinity_threshold_dsm=1.0,
        salinity_slope=15.0,
        growth_stages=[
            GrowthStage("Dormancy", "السكون", 60, 0.80, 0),
            GrowthStage("Flowering", "الإزهار", 30, 0.90, 300),
            GrowthStage("Berry development", "نمو الثمار", 180, 1.05, 1500),
            GrowthStage("Ripening", "النضج", 95, 0.95, 2800),
        ],
        total_season_days=365,
        optimal_temp_min=15.0,
        optimal_temp_max=28.0,
        critical_temp_min=5.0,
        critical_temp_max=35.0,
        regions=["highlands", "northern_highlands"],
        notes="World-renowned Yemen mocha coffee. Shade-grown. High value crop.",
        notes_ar="بن المخا اليمني ذو الشهرة العالمية. يُزرع في الظل. محصول عالي القيمة.",
    ),
    "date_palm": YemenCropParameters(
        name="Date Palm",
        name_ar="النخيل",
        scientific_name="Phoenix dactylifera",
        crop_type="fruit",
        root_depth_m=2.0,
        depletion_fraction=0.50,
        yield_response_factor=0.8,
        salinity_threshold_dsm=4.0,
        salinity_slope=3.6,
        growth_stages=[
            GrowthStage("Dormancy", "السكون", 60, 0.80, 0),
            GrowthStage("Pollination", "التلقيح", 30, 0.90, 250),
            GrowthStage("Fruit development", "نمو الثمار", 150, 1.00, 2500),
            GrowthStage("Ripening (Rutab)", "النضج (رطب)", 60, 0.85, 3500),
            GrowthStage("Harvest (Tamr)", "الحصاد (تمر)", 65, 0.75, 4000),
        ],
        total_season_days=365,
        optimal_temp_min=20.0,
        optimal_temp_max=45.0,
        critical_temp_min=5.0,
        critical_temp_max=52.0,
        regions=["hadhramaut", "tihama", "eastern_plateau", "southern_coast"],
        notes="Major crop in Hadhramaut. Salt tolerant. UNDP SIERY drip trials showed 40-60% water savings.",
        notes_ar="محصول رئيسي في حضرموت. متحمل للملوحة. تجارب UNDP أظهرت 40-60% توفير مياه بالتنقيط.",
    ),
    "tomato": YemenCropParameters(
        name="Tomato",
        name_ar="الطماطم",
        scientific_name="Solanum lycopersicum",
        crop_type="vegetable",
        root_depth_m=0.8,
        depletion_fraction=0.40,
        yield_response_factor=1.05,
        salinity_threshold_dsm=2.5,
        salinity_slope=9.9,
        growth_stages=[
            GrowthStage("Initial", "المرحلة الأولية", 25, 0.60, 100),
            GrowthStage("Development", "مرحلة النمو", 35, 0.80, 400),
            GrowthStage("Mid-season", "منتصف الموسم", 45, 1.15, 900),
            GrowthStage("Late", "المرحلة المتأخرة", 25, 0.80, 1300),
        ],
        total_season_days=130,
        optimal_temp_min=18.0,
        optimal_temp_max=30.0,
        critical_temp_min=5.0,
        critical_temp_max=40.0,
        regions=["highlands", "tihama", "hadhramaut", "southern_coast"],
        notes="Grown year-round in different regions. Important cash crop.",
        notes_ar="يُزرع على مدار العام في مناطق مختلفة. محصول نقدي مهم.",
    ),
    "mango": YemenCropParameters(
        name="Mango",
        name_ar="المانجو",
        scientific_name="Mangifera indica",
        crop_type="fruit",
        root_depth_m=1.8,
        depletion_fraction=0.50,
        yield_response_factor=0.8,
        salinity_threshold_dsm=1.0,
        salinity_slope=10.0,
        growth_stages=[
            GrowthStage("Dormancy", "السكون", 60, 0.70, 0),
            GrowthStage("Flowering", "الإزهار", 40, 0.85, 400),
            GrowthStage("Fruit development", "نمو الثمار", 120, 0.95, 1800),
            GrowthStage("Ripening", "النضج", 60, 0.80, 2800),
            GrowthStage("Post-harvest", "ما بعد الحصاد", 85, 0.70, 3200),
        ],
        total_season_days=365,
        optimal_temp_min=22.0,
        optimal_temp_max=38.0,
        critical_temp_min=8.0,
        critical_temp_max=48.0,
        regions=["tihama", "hadhramaut"],
        notes="Grown in Tihama and coastal areas. Sensitive to salinity.",
        notes_ar="يُزرع في تهامة والمناطق الساحلية. حساس للملوحة.",
    ),
    "banana": YemenCropParameters(
        name="Banana",
        name_ar="الموز",
        scientific_name="Musa spp.",
        crop_type="fruit",
        root_depth_m=0.6,
        depletion_fraction=0.35,
        yield_response_factor=1.2,
        salinity_threshold_dsm=1.0,
        salinity_slope=14.0,
        growth_stages=[
            GrowthStage("Establishment", "التأسيس", 60, 0.50, 200),
            GrowthStage("Vegetative", "النمو الخضري", 120, 1.00, 1500),
            GrowthStage("Flowering", "الإزهار", 60, 1.10, 2500),
            GrowthStage("Fruit filling", "امتلاء الثمار", 90, 1.05, 3500),
            GrowthStage("Harvest", "الحصاد", 35, 0.90, 4000),
        ],
        total_season_days=365,
        optimal_temp_min=22.0,
        optimal_temp_max=35.0,
        critical_temp_min=10.0,
        critical_temp_max=42.0,
        regions=["tihama"],
        notes="Major Tihama crop. Very sensitive to salinity and water stress.",
        notes_ar="محصول رئيسي في تهامة. حساس جداً للملوحة والإجهاد المائي.",
    ),
    "sesame": YemenCropParameters(
        name="Sesame",
        name_ar="السمسم",
        scientific_name="Sesamum indicum",
        crop_type="oilseed",
        root_depth_m=0.8,
        depletion_fraction=0.60,
        yield_response_factor=0.9,
        salinity_threshold_dsm=2.5,
        salinity_slope=11.0,
        growth_stages=[
            GrowthStage("Initial", "المرحلة الأولية", 20, 0.35, 80),
            GrowthStage("Development", "مرحلة النمو", 30, 0.70, 350),
            GrowthStage("Mid-season", "منتصف الموسم", 40, 1.05, 750),
            GrowthStage("Late", "المرحلة المتأخرة", 20, 0.25, 1000),
        ],
        total_season_days=110,
        optimal_temp_min=25.0,
        optimal_temp_max=40.0,
        critical_temp_min=15.0,
        critical_temp_max=45.0,
        regions=["tihama", "eastern_plateau", "southern_coast"],
        notes="Traditional oilseed crop in Yemen. Drought tolerant.",
        notes_ar="محصول زيتي تقليدي في اليمن. متحمل للجفاف.",
    ),
    "alfalfa": YemenCropParameters(
        name="Alfalfa",
        name_ar="البرسيم الحجازي",
        scientific_name="Medicago sativa",
        crop_type="fodder",
        root_depth_m=1.5,
        depletion_fraction=0.55,
        yield_response_factor=1.1,
        salinity_threshold_dsm=2.0,
        salinity_slope=7.3,
        growth_stages=[
            GrowthStage("Establishment", "التأسيس", 30, 0.40, 100),
            GrowthStage("Active growth", "النمو النشط", 60, 1.15, 600),
            GrowthStage("Cutting cycle", "دورة القطع", 240, 1.20, 3000),
            GrowthStage("Winter slowdown", "تباطؤ شتوي", 35, 0.90, 3500),
        ],
        total_season_days=365,
        optimal_temp_min=15.0,
        optimal_temp_max=35.0,
        critical_temp_min=2.0,
        critical_temp_max=42.0,
        regions=["highlands", "hadhramaut", "eastern_plateau"],
        notes="Major fodder crop. Very high water demand. 8-10 cuts/year in Yemen.",
        notes_ar="محصول علفي رئيسي. احتياج مائي عالٍ جداً. 8-10 حشات/سنة في اليمن.",
    ),
    "cotton": YemenCropParameters(
        name="Cotton",
        name_ar="القطن",
        scientific_name="Gossypium spp.",
        crop_type="fiber",
        root_depth_m=1.2,
        depletion_fraction=0.65,
        yield_response_factor=0.85,
        salinity_threshold_dsm=7.7,
        salinity_slope=5.2,
        growth_stages=[
            GrowthStage("Initial", "المرحلة الأولية", 30, 0.35, 120),
            GrowthStage("Development", "مرحلة النمو", 50, 0.70, 500),
            GrowthStage("Mid-season", "منتصف الموسم", 55, 1.20, 1200),
            GrowthStage("Late", "المرحلة المتأخرة", 45, 0.60, 1800),
        ],
        total_season_days=180,
        optimal_temp_min=20.0,
        optimal_temp_max=37.0,
        critical_temp_min=10.0,
        critical_temp_max=45.0,
        regions=["tihama", "abyan", "southern_coast"],
        notes="Grown in Abyan and Tihama. Good salt tolerance.",
        notes_ar="يُزرع في أبين وتهامة. تحمل جيد للملوحة.",
    ),
    "okra": YemenCropParameters(
        name="Okra",
        name_ar="البامية",
        scientific_name="Abelmoschus esculentus",
        crop_type="vegetable",
        root_depth_m=0.6,
        depletion_fraction=0.45,
        yield_response_factor=1.0,
        salinity_threshold_dsm=1.2,
        salinity_slope=15.0,
        growth_stages=[
            GrowthStage("Initial", "المرحلة الأولية", 20, 0.45, 80),
            GrowthStage("Development", "مرحلة النمو", 30, 0.75, 350),
            GrowthStage("Mid-season", "منتصف الموسم", 40, 1.00, 700),
            GrowthStage("Late", "المرحلة المتأخرة", 20, 0.80, 900),
        ],
        total_season_days=110,
        optimal_temp_min=22.0,
        optimal_temp_max=38.0,
        critical_temp_min=12.0,
        critical_temp_max=45.0,
        regions=["tihama", "highlands", "hadhramaut"],
        notes="Popular vegetable across Yemen. Sensitive to cold.",
        notes_ar="خضار شائع في جميع أنحاء اليمن. حساس للبرودة.",
    ),
    "onion": YemenCropParameters(
        name="Onion",
        name_ar="البصل",
        scientific_name="Allium cepa",
        crop_type="vegetable",
        root_depth_m=0.4,
        depletion_fraction=0.30,
        yield_response_factor=1.1,
        salinity_threshold_dsm=1.2,
        salinity_slope=16.0,
        growth_stages=[
            GrowthStage("Initial", "المرحلة الأولية", 20, 0.70, 80),
            GrowthStage("Development", "مرحلة النمو", 30, 0.85, 300),
            GrowthStage("Mid-season", "منتصف الموسم", 50, 1.05, 700),
            GrowthStage("Late", "المرحلة المتأخرة", 20, 0.75, 900),
        ],
        total_season_days=120,
        optimal_temp_min=12.0,
        optimal_temp_max=28.0,
        critical_temp_min=2.0,
        critical_temp_max=35.0,
        regions=["highlands", "northern_highlands"],
        notes="Major highland vegetable. Shallow roots require frequent irrigation.",
        notes_ar="خضار رئيسي في المرتفعات. الجذور السطحية تتطلب ري متكرر.",
    ),
    "grape": YemenCropParameters(
        name="Grape",
        name_ar="العنب",
        scientific_name="Vitis vinifera",
        crop_type="fruit",
        root_depth_m=1.5,
        depletion_fraction=0.45,
        yield_response_factor=0.85,
        salinity_threshold_dsm=1.5,
        salinity_slope=9.6,
        growth_stages=[
            GrowthStage("Dormancy", "السكون", 60, 0.30, 0),
            GrowthStage("Bud break", "تفتح البراعم", 30, 0.50, 150),
            GrowthStage("Active growth", "النمو النشط", 60, 0.80, 600),
            GrowthStage("Veraison", "التلون", 60, 0.70, 1200),
            GrowthStage("Harvest", "الحصاد", 30, 0.50, 1500),
            GrowthStage("Post-harvest", "ما بعد الحصاد", 125, 0.40, 1800),
        ],
        total_season_days=365,
        optimal_temp_min=15.0,
        optimal_temp_max=35.0,
        critical_temp_min=-5.0,
        critical_temp_max=42.0,
        regions=["highlands", "northern_highlands"],
        notes="Traditional highland fruit. Important in Sa'dah and highlands.",
        notes_ar="فاكهة تقليدية في المرتفعات. مهمة في صعدة والمرتفعات.",
    ),
    "pomegranate": YemenCropParameters(
        name="Pomegranate",
        name_ar="الرمان",
        scientific_name="Punica granatum",
        crop_type="fruit",
        root_depth_m=1.0,
        depletion_fraction=0.50,
        yield_response_factor=0.8,
        salinity_threshold_dsm=3.0,
        salinity_slope=8.0,
        growth_stages=[
            GrowthStage("Dormancy", "السكون", 60, 0.40, 0),
            GrowthStage("Flowering", "الإزهار", 40, 0.70, 300),
            GrowthStage("Fruit development", "نمو الثمار", 120, 0.85, 1500),
            GrowthStage("Ripening", "النضج", 60, 0.70, 2200),
            GrowthStage("Post-harvest", "ما بعد الحصاد", 85, 0.50, 2500),
        ],
        total_season_days=365,
        optimal_temp_min=15.0,
        optimal_temp_max=38.0,
        critical_temp_min=-5.0,
        critical_temp_max=45.0,
        regions=["highlands", "hadhramaut"],
        notes="Good drought and moderate salt tolerance. Growing in importance.",
        notes_ar="تحمل جيد للجفاف وملوحة معتدلة. أهميته تتزايد.",
    ),
}


def get_yemen_crop(name: str) -> YemenCropParameters | None:
    """Get crop parameters by name (case-insensitive)."""
    return YEMEN_CROPS.get(name.lower().replace(" ", "_"))


def list_yemen_crops(crop_type: str | None = None, region: str | None = None) -> list[YemenCropParameters]:
    """List crops with optional filtering by type or region."""
    crops = list(YEMEN_CROPS.values())
    if crop_type:
        crops = [c for c in crops if c.crop_type == crop_type]
    if region:
        crops = [c for c in crops if region in c.regions]
    return crops
