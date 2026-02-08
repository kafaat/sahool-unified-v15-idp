"""
Yemen soil profile data for SAHOOL platform.

Provides soil hydraulic properties for major Yemen soil types including
field capacity, wilting point, bulk density, and infiltration rates.

Sources:
- FAO Digital Soil Map of the World (Yemen)
- UNDP SIERY soil surveys (Hadhramaut)
- Yemen Ministry of Agriculture soil data
- Published research on Yemeni soils
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class YemenSoilProfile:
    """Soil hydraulic and physical properties for irrigation calculations."""
    name: str
    name_ar: str
    soil_type: str  # FAO soil classification
    region: str  # Primary Yemen region
    # Hydraulic properties (volumetric, cm³/cm³)
    field_capacity: float  # θfc - Field capacity
    wilting_point: float  # θwp - Permanent wilting point
    saturation: float  # θsat - Saturation water content
    # Physical properties
    bulk_density: float  # ρb (g/cm³)
    infiltration_rate: float  # mm/hr (basic intake rate)
    hydraulic_conductivity: float  # Ksat (mm/hr)
    # Depth and layers
    effective_depth_m: float  # Effective rooting depth limit (m)
    gravel_pct: float  # Gravel content (%)
    # Salinity context
    ec_natural: float  # Natural soil EC (dS/m)
    sar_natural: float  # Natural soil SAR
    # Derived properties
    notes: str = ""
    notes_ar: str = ""

    @property
    def available_water(self) -> float:
        """Available Water Content (AWC) in mm/m."""
        return (self.field_capacity - self.wilting_point) * 1000.0

    @property
    def readily_available_water(self) -> float:
        """Readily Available Water assuming p=0.5 (mm/m)."""
        return self.available_water * 0.5


YEMEN_SOIL_PROFILES: dict[str, YemenSoilProfile] = {
    "tihama_sandy_loam": YemenSoilProfile(
        name="Tihama Sandy Loam",
        name_ar="لوم رملي تهامة",
        soil_type="Arenosol / Sandy Loam",
        region="tihama",
        field_capacity=0.18,
        wilting_point=0.08,
        saturation=0.38,
        bulk_density=1.55,
        infiltration_rate=25.0,
        hydraulic_conductivity=40.0,
        effective_depth_m=1.5,
        gravel_pct=5.0,
        ec_natural=1.5,
        sar_natural=3.0,
        notes="Dominant in Tihama plain. Low water holding capacity. Needs frequent irrigation.",
        notes_ar="سائد في سهل تهامة. قدرة احتجاز مياه منخفضة. يحتاج ري متكرر.",
    ),
    "tihama_alluvial": YemenSoilProfile(
        name="Tihama Alluvial (Wadi deposits)",
        name_ar="رسوبي تهامة (ترسبات الأودية)",
        soil_type="Fluvisol / Loam",
        region="tihama",
        field_capacity=0.25,
        wilting_point=0.11,
        saturation=0.42,
        bulk_density=1.45,
        infiltration_rate=15.0,
        hydraulic_conductivity=25.0,
        effective_depth_m=2.0,
        gravel_pct=10.0,
        ec_natural=2.0,
        sar_natural=4.0,
        notes="Found in wadi flood plains. Better fertility. Spate irrigation areas.",
        notes_ar="يوجد في سهول فيضان الأودية. خصوبة أفضل. مناطق الري بالسيول.",
    ),
    "highland_clay_loam": YemenSoilProfile(
        name="Highland Clay Loam (Terraced)",
        name_ar="لوم طيني المرتفعات (المدرجات)",
        soil_type="Cambisol / Clay Loam",
        region="highlands",
        field_capacity=0.32,
        wilting_point=0.15,
        saturation=0.48,
        bulk_density=1.35,
        infiltration_rate=8.0,
        hydraulic_conductivity=12.0,
        effective_depth_m=0.8,
        gravel_pct=15.0,
        ec_natural=0.5,
        sar_natural=1.0,
        notes="Terraced agriculture. Good water retention but shallow. Low salinity.",
        notes_ar="زراعة المدرجات. احتجاز مياه جيد لكن سطحية. ملوحة منخفضة.",
    ),
    "highland_volcanic": YemenSoilProfile(
        name="Highland Volcanic Soil",
        name_ar="تربة بركانية المرتفعات",
        soil_type="Andosol / Loam",
        region="highlands",
        field_capacity=0.35,
        wilting_point=0.17,
        saturation=0.55,
        bulk_density=1.10,
        infiltration_rate=20.0,
        hydraulic_conductivity=30.0,
        effective_depth_m=1.2,
        gravel_pct=10.0,
        ec_natural=0.3,
        sar_natural=0.5,
        notes="Excellent coffee-growing soil. High organic matter. Found near Ibb and Taiz.",
        notes_ar="تربة ممتازة لزراعة البن. مادة عضوية عالية. توجد قرب إب وتعز.",
    ),
    "hadhramaut_silt_loam": YemenSoilProfile(
        name="Hadhramaut Wadi Silt Loam",
        name_ar="لوم طميي وادي حضرموت",
        soil_type="Fluvisol / Silt Loam",
        region="hadhramaut",
        field_capacity=0.28,
        wilting_point=0.12,
        saturation=0.45,
        bulk_density=1.40,
        infiltration_rate=12.0,
        hydraulic_conductivity=18.0,
        effective_depth_m=2.0,
        gravel_pct=8.0,
        ec_natural=1.5,
        sar_natural=3.0,
        notes="Primary date palm soil. UNDP SIERY trial area (Tarim, 31 farms).",
        notes_ar="تربة رئيسية لزراعة النخيل. منطقة تجارب UNDP (تريم، 31 مزرعة).",
    ),
    "eastern_plateau_loam": YemenSoilProfile(
        name="Eastern Plateau Loam",
        name_ar="لوم الهضبة الشرقية",
        soil_type="Calcisol / Loam",
        region="eastern_plateau",
        field_capacity=0.24,
        wilting_point=0.10,
        saturation=0.40,
        bulk_density=1.50,
        infiltration_rate=10.0,
        hydraulic_conductivity=15.0,
        effective_depth_m=1.5,
        gravel_pct=20.0,
        ec_natural=1.0,
        sar_natural=2.0,
        notes="Calcareous soil. Moderate water holding. Ancient Marib agriculture.",
        notes_ar="تربة كلسية. احتجاز مياه معتدل. زراعة مأرب القديمة.",
    ),
    "southern_coast_saline": YemenSoilProfile(
        name="Southern Coast Saline Sandy",
        name_ar="رملي مالح الساحل الجنوبي",
        soil_type="Solonchak / Sandy",
        region="southern_coast",
        field_capacity=0.15,
        wilting_point=0.06,
        saturation=0.35,
        bulk_density=1.60,
        infiltration_rate=30.0,
        hydraulic_conductivity=50.0,
        effective_depth_m=1.0,
        gravel_pct=5.0,
        ec_natural=5.0,
        sar_natural=8.0,
        notes="Highly saline. Seawater intrusion. Requires intensive leaching management.",
        notes_ar="ملوحة عالية. تسرب مياه بحر. يتطلب إدارة غسيل مكثفة.",
    ),
    "abyan_delta": YemenSoilProfile(
        name="Abyan Delta Alluvial",
        name_ar="رسوبي دلتا أبين",
        soil_type="Fluvisol / Clay Loam",
        region="southern_coast",
        field_capacity=0.30,
        wilting_point=0.14,
        saturation=0.46,
        bulk_density=1.38,
        infiltration_rate=6.0,
        hydraulic_conductivity=10.0,
        effective_depth_m=2.0,
        gravel_pct=3.0,
        ec_natural=2.5,
        sar_natural=5.0,
        notes="Rich alluvial delta. Cotton and sorghum. Moderate salinity from irrigation.",
        notes_ar="دلتا رسوبية غنية. قطن وذرة رفيعة. ملوحة معتدلة من الري.",
    ),
}


def get_soil_profile(name: str) -> Optional[YemenSoilProfile]:
    """Get soil profile by name (case-insensitive, underscores optional)."""
    key = name.lower().replace(" ", "_")
    return YEMEN_SOIL_PROFILES.get(key)


def list_soil_profiles(region: Optional[str] = None) -> list[YemenSoilProfile]:
    """List soil profiles with optional region filter."""
    profiles = list(YEMEN_SOIL_PROFILES.values())
    if region:
        profiles = [p for p in profiles if p.region == region.lower()]
    return profiles
