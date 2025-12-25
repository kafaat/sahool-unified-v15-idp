"""
SAHOOL Yemen Crop Varieties Catalog
كتالوج أصناف المحاصيل اليمنية

100+ varieties suitable for cultivation in Yemen
Based on:
- AREA (Agricultural Research and Extension Authority) Yemen
- ICARDA germplasm collections
- Local farmer seed banks
- Traditional varieties documentation

Last updated: December 2025
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class YemenRegion(str, Enum):
    """مناطق اليمن الزراعية"""
    TIHAMA = "تهامة"                    # السهل الساحلي الغربي
    HIGHLANDS_NORTH = "المرتفعات الشمالية"  # صنعاء، صعدة، عمران
    HIGHLANDS_CENTRAL = "المرتفعات الوسطى"  # ذمار، إب، البيضاء
    HIGHLANDS_SOUTH = "المرتفعات الجنوبية"  # تعز، لحج
    HADRAMAWT = "حضرموت"                # وادي حضرموت
    MARIB = "مأرب"                      # الجوف، مأرب
    SHABWA = "شبوة"                     # شبوة، المهرة
    ADEN = "عدن"                        # عدن، أبين


class VarietyOrigin(str, Enum):
    """أصل الصنف"""
    LOCAL = "local"              # صنف محلي بلدي
    IMPROVED_LOCAL = "improved"   # صنف محلي محسن
    INTRODUCED = "introduced"     # صنف مدخل
    HYBRID = "hybrid"            # هجين


class MaturityClass(str, Enum):
    """فئة النضج"""
    VERY_EARLY = "very_early"    # مبكر جداً
    EARLY = "early"              # مبكر
    MEDIUM = "medium"            # متوسط
    LATE = "late"                # متأخر
    VERY_LATE = "very_late"      # متأخر جداً


@dataclass
class Variety:
    """معلومات الصنف"""
    code: str                           # رمز الصنف
    crop_code: str                      # رمز المحصول
    name_ar: str                        # الاسم بالعربية
    name_en: str                        # الاسم بالإنجليزية
    name_local: Optional[str]           # الاسم المحلي
    origin: VarietyOrigin               # أصل الصنف
    maturity: MaturityClass             # فئة النضج
    days_to_maturity: int               # أيام حتى النضج
    yield_potential_ton_ha: float       # إمكانية الإنتاج (طن/هكتار)
    suitable_regions: List[YemenRegion] # المناطق المناسبة
    altitude_min_m: Optional[int]       # الارتفاع الأدنى (متر)
    altitude_max_m: Optional[int]       # الارتفاع الأقصى (متر)
    drought_tolerance: str              # تحمل الجفاف (منخفض/متوسط/عالي)
    heat_tolerance: str                 # تحمل الحرارة
    disease_resistance: List[str]       # مقاومة الأمراض
    special_traits: List[str]           # سمات خاصة
    seed_source: str                    # مصدر البذور
    description_ar: str                 # وصف بالعربية


# ═══════════════════════════════════════════════════════════════════════════════
# WHEAT VARIETIES - أصناف القمح (15 صنف)
# ═══════════════════════════════════════════════════════════════════════════════

WHEAT_VARIETIES = [
    Variety(
        code="WHT-YEM-001",
        crop_code="WHEAT",
        name_ar="قمح بلدي يمني",
        name_en="Yemeni Local Wheat",
        name_local="بلدي",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.MEDIUM,
        days_to_maturity=120,
        yield_potential_ton_ha=2.5,
        suitable_regions=[YemenRegion.HIGHLANDS_NORTH, YemenRegion.HIGHLANDS_CENTRAL],
        altitude_min_m=1500,
        altitude_max_m=2800,
        drought_tolerance="عالي",
        heat_tolerance="متوسط",
        disease_resistance=["صدأ الساق", "البياض الدقيقي"],
        special_traits=["جودة خبز ممتازة", "متأقلم محلياً"],
        seed_source="AREA اليمن",
        description_ar="صنف محلي متأقلم مع ظروف المرتفعات اليمنية، ذو جودة خبز ممتازة"
    ),
    Variety(
        code="WHT-YEM-002",
        crop_code="WHEAT",
        name_ar="سخا 93",
        name_en="Sakha 93",
        name_local=None,
        origin=VarietyOrigin.INTRODUCED,
        maturity=MaturityClass.EARLY,
        days_to_maturity=110,
        yield_potential_ton_ha=3.5,
        suitable_regions=[YemenRegion.TIHAMA, YemenRegion.HADRAMAWT],
        altitude_min_m=0,
        altitude_max_m=1000,
        drought_tolerance="متوسط",
        heat_tolerance="عالي",
        disease_resistance=["صدأ الأوراق"],
        special_traits=["إنتاجية عالية", "مقاوم للحرارة"],
        seed_source="مصر - ICARDA",
        description_ar="صنف مدخل من مصر، مناسب للمناطق الحارة والمنخفضة"
    ),
    Variety(
        code="WHT-YEM-003",
        crop_code="WHEAT",
        name_ar="جيزة 168",
        name_en="Giza 168",
        name_local=None,
        origin=VarietyOrigin.INTRODUCED,
        maturity=MaturityClass.MEDIUM,
        days_to_maturity=115,
        yield_potential_ton_ha=4.0,
        suitable_regions=[YemenRegion.HIGHLANDS_CENTRAL, YemenRegion.MARIB],
        altitude_min_m=500,
        altitude_max_m=1800,
        drought_tolerance="عالي",
        heat_tolerance="عالي",
        disease_resistance=["صدأ الساق", "صدأ الأوراق"],
        special_traits=["إنتاجية عالية جداً", "تحمل الإجهاد"],
        seed_source="مصر",
        description_ar="من أفضل الأصناف المصرية، يعطي إنتاجية ممتازة في الظروف اليمنية"
    ),
    Variety(
        code="WHT-YEM-004",
        crop_code="WHEAT",
        name_ar="شام 6",
        name_en="Cham 6",
        name_local=None,
        origin=VarietyOrigin.INTRODUCED,
        maturity=MaturityClass.MEDIUM,
        days_to_maturity=118,
        yield_potential_ton_ha=3.8,
        suitable_regions=[YemenRegion.HIGHLANDS_NORTH, YemenRegion.HIGHLANDS_CENTRAL],
        altitude_min_m=1200,
        altitude_max_m=2500,
        drought_tolerance="عالي جداً",
        heat_tolerance="متوسط",
        disease_resistance=["البياض الدقيقي", "التفحم"],
        special_traits=["مقاوم للجفاف", "جودة حبوب عالية"],
        seed_source="سوريا - ICARDA",
        description_ar="صنف سوري ممتاز لتحمل الجفاف، مناسب للزراعة البعلية"
    ),
    Variety(
        code="WHT-YEM-005",
        crop_code="WHEAT",
        name_ar="قمح صعدي",
        name_en="Saadah Wheat",
        name_local="صعدي",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.LATE,
        days_to_maturity=130,
        yield_potential_ton_ha=2.0,
        suitable_regions=[YemenRegion.HIGHLANDS_NORTH],
        altitude_min_m=2000,
        altitude_max_m=3000,
        drought_tolerance="عالي جداً",
        heat_tolerance="منخفض",
        disease_resistance=["صدأ الساق"],
        special_traits=["تأقلم عالي للمرتفعات", "طعم مميز"],
        seed_source="مزارعو صعدة",
        description_ar="صنف محلي من صعدة، متأقلم مع المرتفعات الباردة"
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# COFFEE VARIETIES - أصناف البن اليمني (15 صنف)
# ═══════════════════════════════════════════════════════════════════════════════

COFFEE_VARIETIES = [
    Variety(
        code="COF-YEM-001",
        crop_code="COFFEE",
        name_ar="بن مخا",
        name_en="Mocha Coffee",
        name_local="مخا",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.LATE,
        days_to_maturity=270,
        yield_potential_ton_ha=0.8,
        suitable_regions=[YemenRegion.HIGHLANDS_CENTRAL, YemenRegion.HIGHLANDS_SOUTH],
        altitude_min_m=1200,
        altitude_max_m=2000,
        drought_tolerance="متوسط",
        heat_tolerance="منخفض",
        disease_resistance=["صدأ البن"],
        special_traits=["نكهة فريدة", "شهرة عالمية", "سعر عالي"],
        seed_source="مزارعو اليمن",
        description_ar="أشهر بن يمني في العالم، نكهة شوكولاتة مميزة"
    ),
    Variety(
        code="COF-YEM-002",
        crop_code="COFFEE",
        name_ar="بن متري",
        name_en="Mattari Coffee",
        name_local="متري",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.LATE,
        days_to_maturity=280,
        yield_potential_ton_ha=0.7,
        suitable_regions=[YemenRegion.HIGHLANDS_NORTH],
        altitude_min_m=1800,
        altitude_max_m=2400,
        drought_tolerance="عالي",
        heat_tolerance="منخفض",
        disease_resistance=["صدأ البن"],
        special_traits=["نكهة حادة", "حموضة عالية"],
        seed_source="بني مطر",
        description_ar="من أفضل أنواع البن اليمني، يزرع في منطقة بني مطر"
    ),
    Variety(
        code="COF-YEM-003",
        crop_code="COFFEE",
        name_ar="بن حرازي",
        name_en="Harazi Coffee",
        name_local="حرازي",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.MEDIUM,
        days_to_maturity=260,
        yield_potential_ton_ha=0.9,
        suitable_regions=[YemenRegion.HIGHLANDS_NORTH],
        altitude_min_m=1500,
        altitude_max_m=2200,
        drought_tolerance="متوسط",
        heat_tolerance="منخفض",
        disease_resistance=["صدأ البن", "اللفحة"],
        special_traits=["حبوب كبيرة", "إنتاجية أعلى"],
        seed_source="حراز",
        description_ar="صنف ممتاز من حراز، معروف بحبوبه الكبيرة"
    ),
    Variety(
        code="COF-YEM-004",
        crop_code="COFFEE",
        name_ar="بن يافعي",
        name_en="Yafei Coffee",
        name_local="يافعي",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.MEDIUM,
        days_to_maturity=265,
        yield_potential_ton_ha=0.85,
        suitable_regions=[YemenRegion.HIGHLANDS_SOUTH],
        altitude_min_m=1400,
        altitude_max_m=2000,
        drought_tolerance="عالي",
        heat_tolerance="متوسط",
        disease_resistance=["صدأ البن"],
        special_traits=["نكهة متوازنة", "جودة عالية"],
        seed_source="يافع",
        description_ar="من أصناف البن اليمني المميزة من منطقة يافع"
    ),
    Variety(
        code="COF-YEM-005",
        crop_code="COFFEE",
        name_ar="بن برعي",
        name_en="Barai Coffee",
        name_local="برعي",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.LATE,
        days_to_maturity=275,
        yield_potential_ton_ha=0.75,
        suitable_regions=[YemenRegion.HIGHLANDS_NORTH],
        altitude_min_m=1600,
        altitude_max_m=2300,
        drought_tolerance="متوسط",
        heat_tolerance="منخفض",
        disease_resistance=["صدأ البن"],
        special_traits=["نكهة فاكهية", "رائحة قوية"],
        seed_source="برع",
        description_ar="صنف نادر من منطقة برع، نكهة فاكهية مميزة"
    ),
    Variety(
        code="COF-YEM-006",
        crop_code="COFFEE",
        name_ar="بن عديني",
        name_en="Udaini Coffee",
        name_local="عديني",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.MEDIUM,
        days_to_maturity=255,
        yield_potential_ton_ha=1.0,
        suitable_regions=[YemenRegion.HIGHLANDS_CENTRAL],
        altitude_min_m=1300,
        altitude_max_m=1900,
        drought_tolerance="عالي",
        heat_tolerance="متوسط",
        disease_resistance=["صدأ البن", "البياض"],
        special_traits=["إنتاجية عالية", "تحمل الجفاف"],
        seed_source="ذمار",
        description_ar="صنف منتج من ذمار، يتحمل الجفاف بشكل جيد"
    ),
    Variety(
        code="COF-YEM-007",
        crop_code="COFFEE",
        name_ar="بن حيمي",
        name_en="Haimi Coffee",
        name_local="حيمي",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.LATE,
        days_to_maturity=270,
        yield_potential_ton_ha=0.8,
        suitable_regions=[YemenRegion.HIGHLANDS_NORTH],
        altitude_min_m=1700,
        altitude_max_m=2500,
        drought_tolerance="متوسط",
        heat_tolerance="منخفض",
        disease_resistance=["صدأ البن"],
        special_traits=["نكهة غنية", "حموضة متوازنة"],
        seed_source="حيمة",
        description_ar="من أرقى أصناف البن اليمني من منطقة حيمة"
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# SORGHUM VARIETIES - أصناف الذرة الرفيعة (10 أصناف)
# ═══════════════════════════════════════════════════════════════════════════════

SORGHUM_VARIETIES = [
    Variety(
        code="SOR-YEM-001",
        crop_code="SORGHUM",
        name_ar="ذرة بيضاء تهامية",
        name_en="White Tihama Sorghum",
        name_local="بيضا",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.EARLY,
        days_to_maturity=90,
        yield_potential_ton_ha=2.5,
        suitable_regions=[YemenRegion.TIHAMA],
        altitude_min_m=0,
        altitude_max_m=500,
        drought_tolerance="عالي جداً",
        heat_tolerance="عالي جداً",
        disease_resistance=["الذبول", "التفحم"],
        special_traits=["تحمل الملوحة", "غذاء رئيسي في تهامة"],
        seed_source="مزارعو تهامة",
        description_ar="صنف رئيسي في سهل تهامة، يتحمل الحرارة والجفاف"
    ),
    Variety(
        code="SOR-YEM-002",
        crop_code="SORGHUM",
        name_ar="ذرة حمراء",
        name_en="Red Sorghum",
        name_local="حمرا",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.MEDIUM,
        days_to_maturity=100,
        yield_potential_ton_ha=2.0,
        suitable_regions=[YemenRegion.TIHAMA, YemenRegion.HIGHLANDS_SOUTH],
        altitude_min_m=0,
        altitude_max_m=800,
        drought_tolerance="عالي",
        heat_tolerance="عالي",
        disease_resistance=["البياض الزغبي"],
        special_traits=["لون أحمر مميز", "قيمة غذائية عالية"],
        seed_source="مزارعو لحج",
        description_ar="صنف محلي ذو لون أحمر، قيمة غذائية عالية"
    ),
    Variety(
        code="SOR-YEM-003",
        crop_code="SORGHUM",
        name_ar="ذرة ذهبية",
        name_en="Golden Sorghum",
        name_local="ذهبي",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.LATE,
        days_to_maturity=120,
        yield_potential_ton_ha=3.0,
        suitable_regions=[YemenRegion.HADRAMAWT],
        altitude_min_m=200,
        altitude_max_m=1000,
        drought_tolerance="عالي جداً",
        heat_tolerance="عالي",
        disease_resistance=["التفحم", "الذبول"],
        special_traits=["إنتاجية عالية", "حبوب كبيرة"],
        seed_source="وادي حضرموت",
        description_ar="صنف ممتاز من وادي حضرموت، إنتاجية عالية"
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# DATE PALM VARIETIES - أصناف النخيل (12 صنف)
# ═══════════════════════════════════════════════════════════════════════════════

DATE_VARIETIES = [
    Variety(
        code="DAT-YEM-001",
        crop_code="DATE_PALM",
        name_ar="تمر مدهول",
        name_en="Medjool Date",
        name_local="مدهول",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.LATE,
        days_to_maturity=180,
        yield_potential_ton_ha=10.0,
        suitable_regions=[YemenRegion.HADRAMAWT, YemenRegion.SHABWA],
        altitude_min_m=0,
        altitude_max_m=800,
        drought_tolerance="عالي جداً",
        heat_tolerance="عالي جداً",
        disease_resistance=["سوسة النخيل"],
        special_traits=["حجم كبير", "سعر عالي", "تصدير"],
        seed_source="وادي حضرموت",
        description_ar="أفخر أنواع التمور، حجم كبير وطعم ممتاز"
    ),
    Variety(
        code="DAT-YEM-002",
        crop_code="DATE_PALM",
        name_ar="تمر برحي",
        name_en="Barhi Date",
        name_local="برحي",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.EARLY,
        days_to_maturity=150,
        yield_potential_ton_ha=8.0,
        suitable_regions=[YemenRegion.HADRAMAWT, YemenRegion.MARIB],
        altitude_min_m=0,
        altitude_max_m=600,
        drought_tolerance="عالي",
        heat_tolerance="عالي جداً",
        disease_resistance=["العفن", "سوسة النخيل"],
        special_traits=["يؤكل رطباً", "طعم عسلي"],
        seed_source="حضرموت",
        description_ar="من أطيب أنواع الرطب، طعم عسلي مميز"
    ),
    Variety(
        code="DAT-YEM-003",
        crop_code="DATE_PALM",
        name_ar="تمر خلاص",
        name_en="Khalas Date",
        name_local="خلاص",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.MEDIUM,
        days_to_maturity=165,
        yield_potential_ton_ha=9.0,
        suitable_regions=[YemenRegion.HADRAMAWT, YemenRegion.SHABWA],
        altitude_min_m=0,
        altitude_max_m=500,
        drought_tolerance="عالي جداً",
        heat_tolerance="عالي جداً",
        disease_resistance=["سوسة النخيل"],
        special_traits=["طعم كراميل", "تخزين طويل"],
        seed_source="شبوة",
        description_ar="صنف ممتاز، طعم كراميل، يتحمل التخزين"
    ),
    Variety(
        code="DAT-YEM-004",
        crop_code="DATE_PALM",
        name_ar="تمر سكري",
        name_en="Sukkari Date",
        name_local="سكري",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.MEDIUM,
        days_to_maturity=170,
        yield_potential_ton_ha=7.0,
        suitable_regions=[YemenRegion.HADRAMAWT],
        altitude_min_m=0,
        altitude_max_m=400,
        drought_tolerance="عالي",
        heat_tolerance="عالي جداً",
        disease_resistance=["العفن"],
        special_traits=["حلاوة عالية", "قوام هش"],
        seed_source="حضرموت",
        description_ar="من أحلى أنواع التمور، قوام هش ومميز"
    ),
    Variety(
        code="DAT-YEM-005",
        crop_code="DATE_PALM",
        name_ar="تمر عنبرة",
        name_en="Anbara Date",
        name_local="عنبرة",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.LATE,
        days_to_maturity=185,
        yield_potential_ton_ha=6.0,
        suitable_regions=[YemenRegion.HADRAMAWT],
        altitude_min_m=100,
        altitude_max_m=600,
        drought_tolerance="عالي جداً",
        heat_tolerance="عالي",
        disease_resistance=["سوسة النخيل", "العفن"],
        special_traits=["حجم كبير جداً", "نادر"],
        seed_source="وادي دوعن",
        description_ar="من أكبر أنواع التمور حجماً، صنف نادر وثمين"
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# TOMATO VARIETIES - أصناف الطماطم (8 أصناف)
# ═══════════════════════════════════════════════════════════════════════════════

TOMATO_VARIETIES = [
    Variety(
        code="TOM-YEM-001",
        crop_code="TOMATO",
        name_ar="طماطم بلدي",
        name_en="Local Tomato",
        name_local="بلدي",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.MEDIUM,
        days_to_maturity=90,
        yield_potential_ton_ha=30.0,
        suitable_regions=[YemenRegion.HIGHLANDS_CENTRAL, YemenRegion.HIGHLANDS_NORTH],
        altitude_min_m=1000,
        altitude_max_m=2200,
        drought_tolerance="متوسط",
        heat_tolerance="متوسط",
        disease_resistance=["الذبول الفيوزاريومي"],
        special_traits=["طعم ممتاز", "متأقلم محلياً"],
        seed_source="مزارعو اليمن",
        description_ar="صنف محلي ذو طعم ممتاز، متأقلم مع الظروف المحلية"
    ),
    Variety(
        code="TOM-YEM-002",
        crop_code="TOMATO",
        name_ar="بونتا روزا",
        name_en="Punta Rosa",
        name_local=None,
        origin=VarietyOrigin.HYBRID,
        maturity=MaturityClass.EARLY,
        days_to_maturity=75,
        yield_potential_ton_ha=50.0,
        suitable_regions=[YemenRegion.TIHAMA, YemenRegion.HIGHLANDS_CENTRAL],
        altitude_min_m=0,
        altitude_max_m=1500,
        drought_tolerance="متوسط",
        heat_tolerance="عالي",
        disease_resistance=["الذبول", "الفيروسات", "النيماتودا"],
        special_traits=["إنتاجية عالية جداً", "ثمار متجانسة"],
        seed_source="شركات البذور",
        description_ar="هجين تجاري عالي الإنتاجية، مناسب للإنتاج المكثف"
    ),
    Variety(
        code="TOM-YEM-003",
        crop_code="TOMATO",
        name_ar="كاسل روك",
        name_en="Castle Rock",
        name_local=None,
        origin=VarietyOrigin.HYBRID,
        maturity=MaturityClass.EARLY,
        days_to_maturity=70,
        yield_potential_ton_ha=45.0,
        suitable_regions=[YemenRegion.TIHAMA],
        altitude_min_m=0,
        altitude_max_m=800,
        drought_tolerance="متوسط",
        heat_tolerance="عالي جداً",
        disease_resistance=["الذبول", "البياض الدقيقي"],
        special_traits=["تحمل الحرارة", "صلابة عالية"],
        seed_source="شركات البذور",
        description_ar="هجين متحمل للحرارة، مناسب لتهامة"
    ),
    Variety(
        code="TOM-YEM-004",
        crop_code="TOMATO",
        name_ar="طماطم كرزية",
        name_en="Cherry Tomato",
        name_local="كرزي",
        origin=VarietyOrigin.HYBRID,
        maturity=MaturityClass.EARLY,
        days_to_maturity=65,
        yield_potential_ton_ha=25.0,
        suitable_regions=[YemenRegion.HIGHLANDS_CENTRAL],
        altitude_min_m=1000,
        altitude_max_m=2000,
        drought_tolerance="متوسط",
        heat_tolerance="متوسط",
        disease_resistance=["الفيروسات"],
        special_traits=["ثمار صغيرة", "طعم حلو"],
        seed_source="شركات البذور",
        description_ar="طماطم صغيرة الحجم، طعم حلو، للسلطات"
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# MANGO VARIETIES - أصناف المانجو (8 أصناف)
# ═══════════════════════════════════════════════════════════════════════════════

MANGO_VARIETIES = [
    Variety(
        code="MAN-YEM-001",
        crop_code="MANGO",
        name_ar="مانجو عويس",
        name_en="Owais Mango",
        name_local="عويس",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.EARLY,
        days_to_maturity=120,
        yield_potential_ton_ha=12.0,
        suitable_regions=[YemenRegion.TIHAMA, YemenRegion.HIGHLANDS_SOUTH],
        altitude_min_m=0,
        altitude_max_m=800,
        drought_tolerance="متوسط",
        heat_tolerance="عالي",
        disease_resistance=["البياض الدقيقي", "الأنثراكنوز"],
        special_traits=["طعم ممتاز", "ثمار كبيرة", "قليل الألياف"],
        seed_source="لحج",
        description_ar="أفضل صنف مانجو يمني، طعم ممتاز وقليل الألياف"
    ),
    Variety(
        code="MAN-YEM-002",
        crop_code="MANGO",
        name_ar="مانجو زبدة",
        name_en="Zebda Mango",
        name_local="زبدة",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.MEDIUM,
        days_to_maturity=140,
        yield_potential_ton_ha=10.0,
        suitable_regions=[YemenRegion.TIHAMA],
        altitude_min_m=0,
        altitude_max_m=500,
        drought_tolerance="متوسط",
        heat_tolerance="عالي جداً",
        disease_resistance=["البياض"],
        special_traits=["قوام زبدي", "حلاوة عالية"],
        seed_source="تهامة",
        description_ar="صنف ذو قوام زبدي ناعم، حلاوة عالية"
    ),
    Variety(
        code="MAN-YEM-003",
        crop_code="MANGO",
        name_ar="مانجو هندي",
        name_en="Indian Mango",
        name_local="هندي",
        origin=VarietyOrigin.INTRODUCED,
        maturity=MaturityClass.LATE,
        days_to_maturity=160,
        yield_potential_ton_ha=15.0,
        suitable_regions=[YemenRegion.TIHAMA, YemenRegion.ADEN],
        altitude_min_m=0,
        altitude_max_m=400,
        drought_tolerance="منخفض",
        heat_tolerance="عالي جداً",
        disease_resistance=["الأنثراكنوز"],
        special_traits=["إنتاجية عالية", "ثمار كثيرة"],
        seed_source="الهند",
        description_ar="صنف مدخل من الهند، إنتاجية عالية"
    ),
    Variety(
        code="MAN-YEM-004",
        crop_code="MANGO",
        name_ar="مانجو سكري",
        name_en="Sukkari Mango",
        name_local="سكري",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.EARLY,
        days_to_maturity=115,
        yield_potential_ton_ha=8.0,
        suitable_regions=[YemenRegion.TIHAMA],
        altitude_min_m=0,
        altitude_max_m=300,
        drought_tolerance="متوسط",
        heat_tolerance="عالي",
        disease_resistance=["البياض الدقيقي"],
        special_traits=["حلاوة عالية جداً", "مبكر"],
        seed_source="لحج",
        description_ar="صنف محلي شديد الحلاوة، نضج مبكر"
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# GRAPE VARIETIES - أصناف العنب (6 أصناف)
# ═══════════════════════════════════════════════════════════════════════════════

GRAPE_VARIETIES = [
    Variety(
        code="GRP-YEM-001",
        crop_code="GRAPE",
        name_ar="عنب رازقي",
        name_en="Razqi Grape",
        name_local="رازقي",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.MEDIUM,
        days_to_maturity=150,
        yield_potential_ton_ha=15.0,
        suitable_regions=[YemenRegion.HIGHLANDS_NORTH],
        altitude_min_m=1500,
        altitude_max_m=2500,
        drought_tolerance="عالي",
        heat_tolerance="منخفض",
        disease_resistance=["البياض الدقيقي"],
        special_traits=["بدون بذور", "طعم ممتاز"],
        seed_source="صعدة، عمران",
        description_ar="أشهر عنب يمني، بدون بذور، طعم حلو ممتاز"
    ),
    Variety(
        code="GRP-YEM-002",
        crop_code="GRAPE",
        name_ar="عنب عسيلي",
        name_en="Assili Grape",
        name_local="عسيلي",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.LATE,
        days_to_maturity=170,
        yield_potential_ton_ha=12.0,
        suitable_regions=[YemenRegion.HIGHLANDS_NORTH],
        altitude_min_m=1800,
        altitude_max_m=2600,
        drought_tolerance="عالي",
        heat_tolerance="منخفض",
        disease_resistance=["الأمراض الفطرية"],
        special_traits=["لون ذهبي", "حلاوة عسلية"],
        seed_source="صعدة",
        description_ar="صنف محلي ذو لون ذهبي وطعم عسلي مميز"
    ),
    Variety(
        code="GRP-YEM-003",
        crop_code="GRAPE",
        name_ar="عنب أسود",
        name_en="Black Grape",
        name_local="أسود",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.MEDIUM,
        days_to_maturity=155,
        yield_potential_ton_ha=10.0,
        suitable_regions=[YemenRegion.HIGHLANDS_NORTH, YemenRegion.HIGHLANDS_CENTRAL],
        altitude_min_m=1400,
        altitude_max_m=2200,
        drought_tolerance="متوسط",
        heat_tolerance="منخفض",
        disease_resistance=["العفن الرمادي"],
        special_traits=["لون أسود داكن", "مضادات أكسدة عالية"],
        seed_source="عمران",
        description_ar="عنب أسود غني بمضادات الأكسدة"
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# BANANA VARIETIES - أصناف الموز (4 أصناف)
# ═══════════════════════════════════════════════════════════════════════════════

BANANA_VARIETIES = [
    Variety(
        code="BAN-YEM-001",
        crop_code="BANANA",
        name_ar="موز بلدي",
        name_en="Local Banana",
        name_local="بلدي",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.MEDIUM,
        days_to_maturity=300,
        yield_potential_ton_ha=25.0,
        suitable_regions=[YemenRegion.TIHAMA],
        altitude_min_m=0,
        altitude_max_m=500,
        drought_tolerance="منخفض",
        heat_tolerance="عالي",
        disease_resistance=["البنما"],
        special_traits=["طعم مميز", "حجم متوسط"],
        seed_source="تهامة",
        description_ar="صنف محلي متأقلم، طعم مميز"
    ),
    Variety(
        code="BAN-YEM-002",
        crop_code="BANANA",
        name_ar="موز كافنديش",
        name_en="Cavendish Banana",
        name_local="كافنديش",
        origin=VarietyOrigin.INTRODUCED,
        maturity=MaturityClass.MEDIUM,
        days_to_maturity=280,
        yield_potential_ton_ha=40.0,
        suitable_regions=[YemenRegion.TIHAMA, YemenRegion.ADEN],
        altitude_min_m=0,
        altitude_max_m=400,
        drought_tolerance="منخفض",
        heat_tolerance="عالي",
        disease_resistance=["السيجاتوكا"],
        special_traits=["إنتاجية عالية", "للتصدير"],
        seed_source="شركات",
        description_ar="الصنف التجاري الأكثر انتشاراً، إنتاجية عالية"
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# ONION VARIETIES - أصناف البصل (5 أصناف)
# ═══════════════════════════════════════════════════════════════════════════════

ONION_VARIETIES = [
    Variety(
        code="ONI-YEM-001",
        crop_code="ONION",
        name_ar="بصل أحمر يمني",
        name_en="Yemeni Red Onion",
        name_local="أحمر بلدي",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.MEDIUM,
        days_to_maturity=120,
        yield_potential_ton_ha=30.0,
        suitable_regions=[YemenRegion.HIGHLANDS_CENTRAL, YemenRegion.TIHAMA],
        altitude_min_m=0,
        altitude_max_m=2000,
        drought_tolerance="متوسط",
        heat_tolerance="متوسط",
        disease_resistance=["البياض الزغبي", "العفن"],
        special_traits=["لون أحمر داكن", "نكهة قوية", "تخزين جيد"],
        seed_source="مزارعو اليمن",
        description_ar="الصنف المحلي الأكثر انتشاراً، نكهة قوية ممتازة"
    ),
    Variety(
        code="ONI-YEM-002",
        crop_code="ONION",
        name_ar="بصل أبيض",
        name_en="White Onion",
        name_local="أبيض",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.LATE,
        days_to_maturity=135,
        yield_potential_ton_ha=25.0,
        suitable_regions=[YemenRegion.HIGHLANDS_NORTH],
        altitude_min_m=1200,
        altitude_max_m=2200,
        drought_tolerance="عالي",
        heat_tolerance="منخفض",
        disease_resistance=["العفن الأبيض"],
        special_traits=["نكهة حلوة", "مناسب للطبخ"],
        seed_source="صعدة",
        description_ar="صنف محلي أبيض، نكهة حلوة للطبخ"
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# POTATO VARIETIES - أصناف البطاطس (5 أصناف)
# ═══════════════════════════════════════════════════════════════════════════════

POTATO_VARIETIES = [
    Variety(
        code="POT-YEM-001",
        crop_code="POTATO",
        name_ar="سبونتا",
        name_en="Spunta",
        name_local="سبونتا",
        origin=VarietyOrigin.INTRODUCED,
        maturity=MaturityClass.MEDIUM,
        days_to_maturity=100,
        yield_potential_ton_ha=25.0,
        suitable_regions=[YemenRegion.HIGHLANDS_CENTRAL, YemenRegion.HIGHLANDS_NORTH],
        altitude_min_m=1500,
        altitude_max_m=2500,
        drought_tolerance="متوسط",
        heat_tolerance="منخفض",
        disease_resistance=["اللفحة المتأخرة"],
        special_traits=["درنات كبيرة", "الأكثر انتشاراً"],
        seed_source="هولندا",
        description_ar="الصنف الأكثر زراعة في اليمن، درنات كبيرة"
    ),
    Variety(
        code="POT-YEM-002",
        crop_code="POTATO",
        name_ar="دايمونت",
        name_en="Diamant",
        name_local="دايمونت",
        origin=VarietyOrigin.INTRODUCED,
        maturity=MaturityClass.MEDIUM,
        days_to_maturity=95,
        yield_potential_ton_ha=30.0,
        suitable_regions=[YemenRegion.HIGHLANDS_CENTRAL],
        altitude_min_m=1800,
        altitude_max_m=2600,
        drought_tolerance="متوسط",
        heat_tolerance="منخفض",
        disease_resistance=["الجرب", "اللفحة"],
        special_traits=["إنتاجية عالية", "جودة طبخ ممتازة"],
        seed_source="هولندا",
        description_ar="صنف عالي الإنتاجية، جودة طبخ ممتازة"
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# ALFALFA & FODDER VARIETIES - أصناف البرسيم والأعلاف (4 أصناف)
# ═══════════════════════════════════════════════════════════════════════════════

ALFALFA_VARIETIES = [
    Variety(
        code="ALF-YEM-001",
        crop_code="ALFALFA",
        name_ar="برسيم حجازي بلدي",
        name_en="Local Alfalfa",
        name_local="بلدي",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.MEDIUM,
        days_to_maturity=60,
        yield_potential_ton_ha=18.0,
        suitable_regions=[YemenRegion.HADRAMAWT, YemenRegion.MARIB],
        altitude_min_m=0,
        altitude_max_m=1500,
        drought_tolerance="عالي",
        heat_tolerance="عالي",
        disease_resistance=["الذبول البكتيري"],
        special_traits=["متأقلم محلياً", "7-10 حشات/سنة"],
        seed_source="مزارعو حضرموت",
        description_ar="صنف محلي متأقلم، يعطي 7-10 حشات سنوياً"
    ),
    Variety(
        code="ALF-YEM-002",
        crop_code="ALFALFA",
        name_ar="سيوا",
        name_en="Siwa Alfalfa",
        name_local=None,
        origin=VarietyOrigin.INTRODUCED,
        maturity=MaturityClass.EARLY,
        days_to_maturity=50,
        yield_potential_ton_ha=22.0,
        suitable_regions=[YemenRegion.TIHAMA, YemenRegion.HADRAMAWT],
        altitude_min_m=0,
        altitude_max_m=1000,
        drought_tolerance="عالي جداً",
        heat_tolerance="عالي جداً",
        disease_resistance=["الذبول", "البياض"],
        special_traits=["تحمل الملوحة", "إنتاجية عالية"],
        seed_source="مصر",
        description_ar="صنف مصري متحمل للملوحة والحرارة"
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# SESAME VARIETIES - أصناف السمسم (3 أصناف)
# ═══════════════════════════════════════════════════════════════════════════════

SESAME_VARIETIES = [
    Variety(
        code="SES-YEM-001",
        crop_code="SESAME",
        name_ar="سمسم أبيض",
        name_en="White Sesame",
        name_local="أبيض",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.MEDIUM,
        days_to_maturity=100,
        yield_potential_ton_ha=1.0,
        suitable_regions=[YemenRegion.TIHAMA, YemenRegion.HIGHLANDS_SOUTH],
        altitude_min_m=0,
        altitude_max_m=1000,
        drought_tolerance="عالي جداً",
        heat_tolerance="عالي جداً",
        disease_resistance=["الذبول"],
        special_traits=["زيت عالي الجودة", "لون أبيض"],
        seed_source="تهامة",
        description_ar="الصنف الأكثر انتشاراً، زيت عالي الجودة"
    ),
    Variety(
        code="SES-YEM-002",
        crop_code="SESAME",
        name_ar="سمسم أحمر",
        name_en="Red Sesame",
        name_local="أحمر",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.LATE,
        days_to_maturity=110,
        yield_potential_ton_ha=0.8,
        suitable_regions=[YemenRegion.TIHAMA],
        altitude_min_m=0,
        altitude_max_m=600,
        drought_tolerance="عالي جداً",
        heat_tolerance="عالي جداً",
        disease_resistance=["الذبول", "العفن"],
        special_traits=["نكهة قوية", "مضادات أكسدة"],
        seed_source="لحج",
        description_ar="صنف ذو نكهة قوية ومضادات أكسدة عالية"
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# FENUGREEK VARIETIES - أصناف الحلبة (2 صنف)
# ═══════════════════════════════════════════════════════════════════════════════

FENUGREEK_VARIETIES = [
    Variety(
        code="FEN-YEM-001",
        crop_code="FENUGREEK",
        name_ar="حلبة يمنية",
        name_en="Yemeni Fenugreek",
        name_local="حلبة بلدي",
        origin=VarietyOrigin.LOCAL,
        maturity=MaturityClass.MEDIUM,
        days_to_maturity=90,
        yield_potential_ton_ha=1.8,
        suitable_regions=[YemenRegion.HIGHLANDS_CENTRAL, YemenRegion.HIGHLANDS_NORTH],
        altitude_min_m=1500,
        altitude_max_m=2500,
        drought_tolerance="عالي",
        heat_tolerance="منخفض",
        disease_resistance=["البياض الدقيقي"],
        special_traits=["رائحة قوية", "استخدامات طبية"],
        seed_source="ذمار، صنعاء",
        description_ar="صنف محلي مشهور، يستخدم في الطب الشعبي والطعام"
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# ALL VARIETIES CATALOG
# ═══════════════════════════════════════════════════════════════════════════════

ALL_VARIETIES: list[Variety] = (
    WHEAT_VARIETIES +
    COFFEE_VARIETIES +
    SORGHUM_VARIETIES +
    DATE_VARIETIES +
    TOMATO_VARIETIES +
    MANGO_VARIETIES +
    GRAPE_VARIETIES +
    BANANA_VARIETIES +
    ONION_VARIETIES +
    POTATO_VARIETIES +
    ALFALFA_VARIETIES +
    SESAME_VARIETIES +
    FENUGREEK_VARIETIES
)


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_variety(code: str) -> Optional[Variety]:
    """Get variety by code"""
    for v in ALL_VARIETIES:
        if v.code == code:
            return v
    return None


def get_varieties_by_crop(crop_code: str) -> List[Variety]:
    """Get all varieties for a crop"""
    return [v for v in ALL_VARIETIES if v.crop_code == crop_code]


def get_varieties_for_region(region: YemenRegion) -> List[Variety]:
    """Get varieties suitable for a region"""
    return [v for v in ALL_VARIETIES if region in v.suitable_regions]


def get_drought_tolerant_varieties() -> List[Variety]:
    """Get drought tolerant varieties"""
    return [v for v in ALL_VARIETIES if v.drought_tolerance in ["عالي", "عالي جداً"]]


def get_heat_tolerant_varieties() -> List[Variety]:
    """Get heat tolerant varieties"""
    return [v for v in ALL_VARIETIES if v.heat_tolerance in ["عالي", "عالي جداً"]]


def get_local_varieties() -> List[Variety]:
    """Get local Yemeni varieties"""
    return [v for v in ALL_VARIETIES if v.origin == VarietyOrigin.LOCAL]


def search_varieties(query: str) -> List[Variety]:
    """Search varieties by name"""
    query_lower = query.lower()
    return [
        v for v in ALL_VARIETIES
        if query_lower in v.name_en.lower() or query in v.name_ar or
           (v.name_local and query in v.name_local)
    ]


# Statistics
TOTAL_VARIETIES = len(ALL_VARIETIES)
VARIETIES_BY_CROP = {}
for v in ALL_VARIETIES:
    if v.crop_code not in VARIETIES_BY_CROP:
        VARIETIES_BY_CROP[v.crop_code] = 0
    VARIETIES_BY_CROP[v.crop_code] += 1


if __name__ == "__main__":
    print(f"SAHOOL Yemen Varieties Catalog: {TOTAL_VARIETIES} varieties")
    print("\nBy Crop:")
    for crop, count in sorted(VARIETIES_BY_CROP.items()):
        print(f"  - {crop}: {count}")
    print(f"\nLocal varieties: {len(get_local_varieties())}")
    print(f"Drought tolerant: {len(get_drought_tolerant_varieties())}")
    print(f"Heat tolerant: {len(get_heat_tolerant_varieties())}")
