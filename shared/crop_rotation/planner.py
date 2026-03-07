"""
Crop Rotation Planning Algorithms - خوارزميات تخطيط الدورة الزراعية

Provides intelligent crop rotation planning based on:
- Agronomic principles (crop families, nutrient needs)
- Pest and disease break requirements
- Soil health improvement
- Economic optimization
- Water efficiency
- Local climate and conditions

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any

from .models import (
    CropCharacteristics,
    CropFamily,
    CropType,
    FieldRotationHistory,
    MultiYearPlan,
    NutrientBalance,
    PestBreakRecommendation,
    PestDiseaseRisk,
    RecommendationPriority,
    RotationBenefit,
    RotationRecommendation,
    Season,
)

# =============================================================================
# Crop Database - قاعدة بيانات المحاصيل
# =============================================================================


# Comprehensive crop characteristics for Middle East agriculture
CROP_DATABASE: dict[CropType, CropCharacteristics] = {
    # Cereals - الحبوب
    CropType.WHEAT: CropCharacteristics(
        crop_type=CropType.WHEAT,
        crop_family=CropFamily.POACEAE,
        name_en="Wheat",
        name_ar="قمح",
        scientific_name="Triticum aestivum",
        growing_season=Season.WINTER,
        growing_days_min=120,
        growing_days_max=150,
        optimal_temp_min_c=15.0,
        optimal_temp_max_c=24.0,
        water_requirement_mm=450,
        drought_tolerance=0.4,
        preferred_ph_min=6.0,
        preferred_ph_max=7.5,
        salt_tolerance=0.5,
        is_nitrogen_fixer=False,
        nitrogen_demand=0.7,
        phosphorus_demand=0.5,
        potassium_demand=0.4,
        residue_nitrogen_kg_ha=0,
        root_depth_cm=120,
        root_type="fibrous",
        min_rotation_years=2,
        break_crop_for=["alfalfa", "clover"],
        major_pests=["aphids", "stem_borer", "armyworm"],
        major_diseases=["rust", "powdery_mildew", "septoria"],
    ),
    CropType.BARLEY: CropCharacteristics(
        crop_type=CropType.BARLEY,
        crop_family=CropFamily.POACEAE,
        name_en="Barley",
        name_ar="شعير",
        scientific_name="Hordeum vulgare",
        growing_season=Season.WINTER,
        growing_days_min=90,
        growing_days_max=120,
        optimal_temp_min_c=12.0,
        optimal_temp_max_c=22.0,
        water_requirement_mm=350,
        drought_tolerance=0.6,
        preferred_ph_min=6.0,
        preferred_ph_max=8.0,
        salt_tolerance=0.7,
        is_nitrogen_fixer=False,
        nitrogen_demand=0.5,
        phosphorus_demand=0.4,
        potassium_demand=0.4,
        residue_nitrogen_kg_ha=0,
        root_depth_cm=100,
        root_type="fibrous",
        min_rotation_years=2,
        break_crop_for=["alfalfa"],
        major_pests=["aphids", "stem_borer"],
        major_diseases=["rust", "net_blotch", "scald"],
    ),
    CropType.MAIZE: CropCharacteristics(
        crop_type=CropType.MAIZE,
        crop_family=CropFamily.POACEAE,
        name_en="Maize (Corn)",
        name_ar="ذرة",
        scientific_name="Zea mays",
        growing_season=Season.SUMMER,
        growing_days_min=90,
        growing_days_max=140,
        optimal_temp_min_c=20.0,
        optimal_temp_max_c=30.0,
        water_requirement_mm=600,
        drought_tolerance=0.3,
        preferred_ph_min=5.8,
        preferred_ph_max=7.0,
        salt_tolerance=0.3,
        is_nitrogen_fixer=False,
        nitrogen_demand=0.8,
        phosphorus_demand=0.5,
        potassium_demand=0.6,
        residue_nitrogen_kg_ha=0,
        root_depth_cm=150,
        root_type="fibrous",
        min_rotation_years=2,
        break_crop_for=["wheat", "barley"],
        major_pests=["stem_borer", "fall_armyworm", "rootworm"],
        major_diseases=["rust", "leaf_blight", "stalk_rot"],
    ),
    CropType.SORGHUM: CropCharacteristics(
        crop_type=CropType.SORGHUM,
        crop_family=CropFamily.POACEAE,
        name_en="Sorghum",
        name_ar="ذرة رفيعة",
        scientific_name="Sorghum bicolor",
        growing_season=Season.SUMMER,
        growing_days_min=100,
        growing_days_max=140,
        optimal_temp_min_c=25.0,
        optimal_temp_max_c=35.0,
        water_requirement_mm=400,
        drought_tolerance=0.8,
        preferred_ph_min=5.5,
        preferred_ph_max=7.5,
        salt_tolerance=0.6,
        is_nitrogen_fixer=False,
        nitrogen_demand=0.5,
        phosphorus_demand=0.4,
        potassium_demand=0.5,
        residue_nitrogen_kg_ha=0,
        root_depth_cm=180,
        root_type="fibrous",
        min_rotation_years=2,
        break_crop_for=["wheat"],
        major_pests=["stem_borer", "shoot_fly", "midge"],
        major_diseases=["anthracnose", "downy_mildew", "grain_mold"],
    ),
    # Legumes - البقوليات
    CropType.ALFALFA: CropCharacteristics(
        crop_type=CropType.ALFALFA,
        crop_family=CropFamily.FABACEAE,
        name_en="Alfalfa",
        name_ar="برسيم حجازي",
        scientific_name="Medicago sativa",
        growing_season=Season.PERENNIAL,
        growing_days_min=365,
        growing_days_max=1825,  # 3-5 years perennial
        optimal_temp_min_c=15.0,
        optimal_temp_max_c=30.0,
        water_requirement_mm=1000,
        drought_tolerance=0.6,
        preferred_ph_min=6.5,
        preferred_ph_max=7.5,
        salt_tolerance=0.4,
        is_nitrogen_fixer=True,
        nitrogen_demand=0.0,  # Fixes own N
        phosphorus_demand=0.6,
        potassium_demand=0.7,
        residue_nitrogen_kg_ha=150,  # Significant N contribution
        root_depth_cm=300,
        root_type="taproot",
        min_rotation_years=3,  # Before replanting alfalfa
        break_crop_for=["wheat", "barley", "maize", "sorghum"],
        major_pests=["aphids", "weevil", "leafhopper"],
        major_diseases=["wilt", "crown_rot", "leaf_spot"],
    ),
    CropType.CLOVER: CropCharacteristics(
        crop_type=CropType.CLOVER,
        crop_family=CropFamily.FABACEAE,
        name_en="Clover (Berseem)",
        name_ar="برسيم مصري",
        scientific_name="Trifolium alexandrinum",
        growing_season=Season.WINTER,
        growing_days_min=180,
        growing_days_max=240,
        optimal_temp_min_c=15.0,
        optimal_temp_max_c=25.0,
        water_requirement_mm=600,
        drought_tolerance=0.3,
        preferred_ph_min=6.0,
        preferred_ph_max=7.5,
        salt_tolerance=0.3,
        is_nitrogen_fixer=True,
        nitrogen_demand=0.0,
        phosphorus_demand=0.5,
        potassium_demand=0.5,
        residue_nitrogen_kg_ha=100,
        root_depth_cm=100,
        root_type="taproot",
        min_rotation_years=2,
        break_crop_for=["wheat", "maize"],
        major_pests=["aphids", "clover_seed_weevil"],
        major_diseases=["root_rot", "powdery_mildew"],
    ),
    CropType.FABA_BEAN: CropCharacteristics(
        crop_type=CropType.FABA_BEAN,
        crop_family=CropFamily.FABACEAE,
        name_en="Faba Bean (Fava Bean)",
        name_ar="فول",
        scientific_name="Vicia faba",
        growing_season=Season.WINTER,
        growing_days_min=120,
        growing_days_max=180,
        optimal_temp_min_c=15.0,
        optimal_temp_max_c=22.0,
        water_requirement_mm=400,
        drought_tolerance=0.4,
        preferred_ph_min=6.0,
        preferred_ph_max=7.5,
        salt_tolerance=0.3,
        is_nitrogen_fixer=True,
        nitrogen_demand=0.0,
        phosphorus_demand=0.5,
        potassium_demand=0.4,
        residue_nitrogen_kg_ha=80,
        root_depth_cm=100,
        root_type="taproot",
        min_rotation_years=3,
        break_crop_for=["wheat", "barley"],
        major_pests=["aphids", "bean_weevil"],
        major_diseases=["chocolate_spot", "rust", "root_rot"],
    ),
    CropType.CHICKPEA: CropCharacteristics(
        crop_type=CropType.CHICKPEA,
        crop_family=CropFamily.FABACEAE,
        name_en="Chickpea",
        name_ar="حمص",
        scientific_name="Cicer arietinum",
        growing_season=Season.WINTER,
        growing_days_min=90,
        growing_days_max=150,
        optimal_temp_min_c=15.0,
        optimal_temp_max_c=25.0,
        water_requirement_mm=350,
        drought_tolerance=0.6,
        preferred_ph_min=6.0,
        preferred_ph_max=8.0,
        salt_tolerance=0.4,
        is_nitrogen_fixer=True,
        nitrogen_demand=0.0,
        phosphorus_demand=0.5,
        potassium_demand=0.4,
        residue_nitrogen_kg_ha=60,
        root_depth_cm=100,
        root_type="taproot",
        min_rotation_years=3,
        break_crop_for=["wheat"],
        major_pests=["pod_borer", "leaf_miner"],
        major_diseases=["ascochyta_blight", "fusarium_wilt"],
    ),
    # Vegetables - الخضروات
    CropType.TOMATO: CropCharacteristics(
        crop_type=CropType.TOMATO,
        crop_family=CropFamily.SOLANACEAE,
        name_en="Tomato",
        name_ar="طماطم",
        scientific_name="Solanum lycopersicum",
        growing_season=Season.SUMMER,
        growing_days_min=90,
        growing_days_max=150,
        optimal_temp_min_c=20.0,
        optimal_temp_max_c=30.0,
        water_requirement_mm=600,
        drought_tolerance=0.3,
        preferred_ph_min=6.0,
        preferred_ph_max=7.0,
        salt_tolerance=0.3,
        is_nitrogen_fixer=False,
        nitrogen_demand=0.7,
        phosphorus_demand=0.6,
        potassium_demand=0.8,
        residue_nitrogen_kg_ha=0,
        root_depth_cm=100,
        root_type="taproot",
        min_rotation_years=3,
        break_crop_for=[],
        major_pests=["whitefly", "tomato_leafminer", "spider_mites"],
        major_diseases=["early_blight", "late_blight", "fusarium_wilt", "bacterial_wilt"],
    ),
    CropType.POTATO: CropCharacteristics(
        crop_type=CropType.POTATO,
        crop_family=CropFamily.SOLANACEAE,
        name_en="Potato",
        name_ar="بطاطس",
        scientific_name="Solanum tuberosum",
        growing_season=Season.WINTER,
        growing_days_min=90,
        growing_days_max=120,
        optimal_temp_min_c=15.0,
        optimal_temp_max_c=22.0,
        water_requirement_mm=500,
        drought_tolerance=0.3,
        preferred_ph_min=5.5,
        preferred_ph_max=6.5,
        salt_tolerance=0.2,
        is_nitrogen_fixer=False,
        nitrogen_demand=0.6,
        phosphorus_demand=0.7,
        potassium_demand=0.9,
        residue_nitrogen_kg_ha=0,
        root_depth_cm=60,
        root_type="fibrous",
        min_rotation_years=3,
        break_crop_for=[],
        major_pests=["colorado_beetle", "aphids", "tuber_moth"],
        major_diseases=["late_blight", "early_blight", "bacterial_wilt", "scab"],
    ),
    CropType.ONION: CropCharacteristics(
        crop_type=CropType.ONION,
        crop_family=CropFamily.LILIACEAE,
        name_en="Onion",
        name_ar="بصل",
        scientific_name="Allium cepa",
        growing_season=Season.WINTER,
        growing_days_min=120,
        growing_days_max=180,
        optimal_temp_min_c=13.0,
        optimal_temp_max_c=24.0,
        water_requirement_mm=450,
        drought_tolerance=0.3,
        preferred_ph_min=6.0,
        preferred_ph_max=7.0,
        salt_tolerance=0.3,
        is_nitrogen_fixer=False,
        nitrogen_demand=0.5,
        phosphorus_demand=0.4,
        potassium_demand=0.5,
        residue_nitrogen_kg_ha=0,
        root_depth_cm=40,
        root_type="fibrous",
        min_rotation_years=3,
        break_crop_for=["tomato", "potato"],
        major_pests=["thrips", "onion_fly"],
        major_diseases=["downy_mildew", "purple_blotch", "white_rot"],
    ),
    CropType.CUCUMBER: CropCharacteristics(
        crop_type=CropType.CUCUMBER,
        crop_family=CropFamily.CUCURBITACEAE,
        name_en="Cucumber",
        name_ar="خيار",
        scientific_name="Cucumis sativus",
        growing_season=Season.SUMMER,
        growing_days_min=50,
        growing_days_max=70,
        optimal_temp_min_c=20.0,
        optimal_temp_max_c=30.0,
        water_requirement_mm=400,
        drought_tolerance=0.2,
        preferred_ph_min=6.0,
        preferred_ph_max=7.0,
        salt_tolerance=0.2,
        is_nitrogen_fixer=False,
        nitrogen_demand=0.6,
        phosphorus_demand=0.5,
        potassium_demand=0.6,
        residue_nitrogen_kg_ha=0,
        root_depth_cm=60,
        root_type="fibrous",
        min_rotation_years=2,
        break_crop_for=[],
        major_pests=["whitefly", "spider_mites", "aphids"],
        major_diseases=["powdery_mildew", "downy_mildew", "fusarium_wilt"],
    ),
    CropType.MELON: CropCharacteristics(
        crop_type=CropType.MELON,
        crop_family=CropFamily.CUCURBITACEAE,
        name_en="Melon (Cantaloupe)",
        name_ar="بطيخ أصفر (شمام)",
        scientific_name="Cucumis melo",
        growing_season=Season.SUMMER,
        growing_days_min=80,
        growing_days_max=110,
        optimal_temp_min_c=22.0,
        optimal_temp_max_c=32.0,
        water_requirement_mm=500,
        drought_tolerance=0.4,
        preferred_ph_min=6.0,
        preferred_ph_max=7.5,
        salt_tolerance=0.3,
        is_nitrogen_fixer=False,
        nitrogen_demand=0.6,
        phosphorus_demand=0.5,
        potassium_demand=0.7,
        residue_nitrogen_kg_ha=0,
        root_depth_cm=100,
        root_type="taproot",
        min_rotation_years=2,
        break_crop_for=[],
        major_pests=["aphids", "melon_fly", "spider_mites"],
        major_diseases=["powdery_mildew", "fusarium_wilt", "gummy_stem_blight"],
    ),
    CropType.WATERMELON: CropCharacteristics(
        crop_type=CropType.WATERMELON,
        crop_family=CropFamily.CUCURBITACEAE,
        name_en="Watermelon",
        name_ar="بطيخ أحمر",
        scientific_name="Citrullus lanatus",
        growing_season=Season.SUMMER,
        growing_days_min=80,
        growing_days_max=100,
        optimal_temp_min_c=24.0,
        optimal_temp_max_c=35.0,
        water_requirement_mm=500,
        drought_tolerance=0.5,
        preferred_ph_min=6.0,
        preferred_ph_max=7.0,
        salt_tolerance=0.3,
        is_nitrogen_fixer=False,
        nitrogen_demand=0.5,
        phosphorus_demand=0.4,
        potassium_demand=0.6,
        residue_nitrogen_kg_ha=0,
        root_depth_cm=150,
        root_type="taproot",
        min_rotation_years=3,
        break_crop_for=[],
        major_pests=["aphids", "whitefly"],
        major_diseases=["fusarium_wilt", "anthracnose", "powdery_mildew"],
    ),
    # Fodder - محاصيل العلف
    CropType.RHODES_GRASS: CropCharacteristics(
        crop_type=CropType.RHODES_GRASS,
        crop_family=CropFamily.POACEAE,
        name_en="Rhodes Grass",
        name_ar="حشيشة رودس",
        scientific_name="Chloris gayana",
        growing_season=Season.PERENNIAL,
        growing_days_min=365,
        growing_days_max=1095,
        optimal_temp_min_c=25.0,
        optimal_temp_max_c=35.0,
        water_requirement_mm=800,
        drought_tolerance=0.7,
        preferred_ph_min=5.5,
        preferred_ph_max=8.0,
        salt_tolerance=0.6,
        is_nitrogen_fixer=False,
        nitrogen_demand=0.6,
        phosphorus_demand=0.4,
        potassium_demand=0.5,
        residue_nitrogen_kg_ha=0,
        root_depth_cm=200,
        root_type="fibrous",
        min_rotation_years=3,
        break_crop_for=["wheat", "vegetables"],
        major_pests=["armyworm", "stem_borer"],
        major_diseases=["rust", "leaf_blight"],
    ),
    # Industrial crops
    CropType.COTTON: CropCharacteristics(
        crop_type=CropType.COTTON,
        crop_family=CropFamily.MALVACEAE,
        name_en="Cotton",
        name_ar="قطن",
        scientific_name="Gossypium hirsutum",
        growing_season=Season.SUMMER,
        growing_days_min=150,
        growing_days_max=180,
        optimal_temp_min_c=25.0,
        optimal_temp_max_c=35.0,
        water_requirement_mm=700,
        drought_tolerance=0.4,
        preferred_ph_min=6.0,
        preferred_ph_max=7.5,
        salt_tolerance=0.5,
        is_nitrogen_fixer=False,
        nitrogen_demand=0.7,
        phosphorus_demand=0.5,
        potassium_demand=0.6,
        residue_nitrogen_kg_ha=0,
        root_depth_cm=150,
        root_type="taproot",
        min_rotation_years=2,
        break_crop_for=["wheat"],
        major_pests=["bollworm", "whitefly", "aphids", "pink_bollworm"],
        major_diseases=["verticillium_wilt", "fusarium_wilt", "root_rot"],
    ),
    # Date Palm
    CropType.DATE_PALM: CropCharacteristics(
        crop_type=CropType.DATE_PALM,
        crop_family=CropFamily.ARECACEAE,
        name_en="Date Palm",
        name_ar="نخيل",
        scientific_name="Phoenix dactylifera",
        growing_season=Season.PERENNIAL,
        growing_days_min=365,
        growing_days_max=36500,  # Very long-lived
        optimal_temp_min_c=25.0,
        optimal_temp_max_c=45.0,
        water_requirement_mm=1500,
        drought_tolerance=0.8,
        preferred_ph_min=7.0,
        preferred_ph_max=8.5,
        salt_tolerance=0.7,
        is_nitrogen_fixer=False,
        nitrogen_demand=0.5,
        phosphorus_demand=0.4,
        potassium_demand=0.6,
        residue_nitrogen_kg_ha=0,
        root_depth_cm=600,
        root_type="fibrous",
        min_rotation_years=0,  # Perennial, no rotation
        break_crop_for=[],
        major_pests=["red_palm_weevil", "dubas_bug", "scale_insects"],
        major_diseases=["bayoud", "black_scorch", "leaf_spot"],
    ),
    # Fallow
    CropType.FALLOW: CropCharacteristics(
        crop_type=CropType.FALLOW,
        crop_family=CropFamily.OTHER,
        name_en="Fallow",
        name_ar="أرض بور",
        scientific_name="N/A",
        growing_season=Season.YEAR_ROUND,
        growing_days_min=90,
        growing_days_max=365,
        optimal_temp_min_c=0.0,
        optimal_temp_max_c=50.0,
        water_requirement_mm=0,
        drought_tolerance=1.0,
        preferred_ph_min=0.0,
        preferred_ph_max=14.0,
        salt_tolerance=1.0,
        is_nitrogen_fixer=False,
        nitrogen_demand=0.0,
        phosphorus_demand=0.0,
        potassium_demand=0.0,
        residue_nitrogen_kg_ha=0,
        root_depth_cm=0,
        root_type="none",
        min_rotation_years=0,
        break_crop_for=["all"],
        major_pests=[],
        major_diseases=[],
    ),
    CropType.GREEN_MANURE: CropCharacteristics(
        crop_type=CropType.GREEN_MANURE,
        crop_family=CropFamily.FABACEAE,
        name_en="Green Manure",
        name_ar="سماد أخضر",
        scientific_name="Various",
        growing_season=Season.WINTER,
        growing_days_min=60,
        growing_days_max=90,
        optimal_temp_min_c=15.0,
        optimal_temp_max_c=25.0,
        water_requirement_mm=200,
        drought_tolerance=0.5,
        preferred_ph_min=6.0,
        preferred_ph_max=7.5,
        salt_tolerance=0.4,
        is_nitrogen_fixer=True,
        nitrogen_demand=0.0,
        phosphorus_demand=0.3,
        potassium_demand=0.3,
        residue_nitrogen_kg_ha=80,
        root_depth_cm=60,
        root_type="taproot",
        min_rotation_years=0,
        break_crop_for=["all"],
        major_pests=[],
        major_diseases=[],
    ),
}


# =============================================================================
# Pest/Disease Database - قاعدة بيانات الآفات والأمراض
# =============================================================================


PEST_DISEASE_DATABASE: list[PestDiseaseRisk] = [
    # Wheat diseases
    PestDiseaseRisk(
        name_en="Wheat Rust",
        name_ar="صدأ القمح",
        scientific_name="Puccinia spp.",
        is_pest=False,
        disease_type="fungal",
        host_crops=[CropType.WHEAT, CropType.BARLEY],
        primary_host=CropType.WHEAT,
        soil_persistence_years=0,  # Not soil-borne
        requires_host_crop=True,
        break_crops=[CropType.ALFALFA, CropType.CLOVER, CropType.TOMATO, CropType.ONION],
        recommended_break_years=1,
        yield_loss_potential_percent=40.0,
        economic_impact_level="high",
        cultural_controls=[
            "Use resistant varieties",
            "Crop rotation with non-hosts",
            "Remove volunteer wheat",
        ],
        cultural_controls_ar=[
            "استخدام أصناف مقاومة",
            "تناوب المحاصيل مع غير العوائل",
            "إزالة القمح المتطوع",
        ],
    ),
    # Solanaceae diseases
    PestDiseaseRisk(
        name_en="Fusarium Wilt",
        name_ar="ذبول الفيوزاريوم",
        scientific_name="Fusarium oxysporum",
        is_pest=False,
        disease_type="fungal",
        host_crops=[CropType.TOMATO, CropType.POTATO, CropType.MELON, CropType.WATERMELON],
        primary_host=CropType.TOMATO,
        soil_persistence_years=5,
        requires_host_crop=False,
        break_crops=[CropType.WHEAT, CropType.BARLEY, CropType.ONION, CropType.ALFALFA],
        recommended_break_years=4,
        yield_loss_potential_percent=80.0,
        economic_impact_level="severe",
        cultural_controls=[
            "4+ year rotation with non-host crops",
            "Use resistant varieties",
            "Soil solarization",
            "Improve drainage",
        ],
        cultural_controls_ar=[
            "تناوب 4+ سنوات مع محاصيل غير عائلة",
            "استخدام أصناف مقاومة",
            "تشميس التربة",
            "تحسين الصرف",
        ],
    ),
    # Nematodes
    PestDiseaseRisk(
        name_en="Root-knot Nematode",
        name_ar="نيماتودا تعقد الجذور",
        scientific_name="Meloidogyne spp.",
        is_pest=True,
        pest_type="nematode",
        host_crops=[CropType.TOMATO, CropType.POTATO, CropType.CUCUMBER, CropType.MELON],
        primary_host=CropType.TOMATO,
        soil_persistence_years=3,
        requires_host_crop=False,
        break_crops=[CropType.WHEAT, CropType.BARLEY, CropType.SORGHUM, CropType.ONION],
        recommended_break_years=3,
        yield_loss_potential_percent=60.0,
        economic_impact_level="high",
        cultural_controls=[
            "Rotate with non-host cereals",
            "Use resistant varieties",
            "Soil solarization",
            "Deep plowing",
        ],
        cultural_controls_ar=[
            "تناوب مع الحبوب غير العائلة",
            "استخدام أصناف مقاومة",
            "تشميس التربة",
            "الحرث العميق",
        ],
    ),
    # Cereal pests
    PestDiseaseRisk(
        name_en="Stem Borer",
        name_ar="حفار الساق",
        scientific_name="Sesamia spp., Chilo spp.",
        is_pest=True,
        pest_type="insect",
        host_crops=[CropType.MAIZE, CropType.SORGHUM, CropType.WHEAT, CropType.RICE],
        primary_host=CropType.MAIZE,
        soil_persistence_years=1,
        requires_host_crop=True,
        overwinters_in_residue=True,
        break_crops=[CropType.ALFALFA, CropType.CHICKPEA, CropType.TOMATO],
        recommended_break_years=2,
        yield_loss_potential_percent=30.0,
        economic_impact_level="high",
        cultural_controls=[
            "Remove and destroy crop residues",
            "Rotate with non-host crops",
            "Early planting",
            "Use resistant varieties",
        ],
        cultural_controls_ar=[
            "إزالة وتدمير مخلفات المحاصيل",
            "تناوب مع محاصيل غير عائلة",
            "الزراعة المبكرة",
            "استخدام أصناف مقاومة",
        ],
    ),
    # Cucurbit diseases
    PestDiseaseRisk(
        name_en="Powdery Mildew (Cucurbits)",
        name_ar="البياض الدقيقي (القرعيات)",
        scientific_name="Podosphaera xanthii",
        is_pest=False,
        disease_type="fungal",
        host_crops=[CropType.CUCUMBER, CropType.MELON, CropType.WATERMELON, CropType.SQUASH],
        primary_host=CropType.CUCUMBER,
        soil_persistence_years=0,
        requires_host_crop=True,
        break_crops=[CropType.WHEAT, CropType.ONION, CropType.TOMATO],
        recommended_break_years=2,
        yield_loss_potential_percent=40.0,
        economic_impact_level="medium",
        cultural_controls=[
            "Avoid overcrowding",
            "Improve air circulation",
            "Use resistant varieties",
            "Remove infected plant material",
        ],
        cultural_controls_ar=[
            "تجنب الازدحام",
            "تحسين دوران الهواء",
            "استخدام أصناف مقاومة",
            "إزالة المواد النباتية المصابة",
        ],
    ),
    # Date palm pests
    PestDiseaseRisk(
        name_en="Red Palm Weevil",
        name_ar="سوسة النخيل الحمراء",
        scientific_name="Rhynchophorus ferrugineus",
        is_pest=True,
        pest_type="insect",
        host_crops=[CropType.DATE_PALM],
        primary_host=CropType.DATE_PALM,
        soil_persistence_years=0,
        requires_host_crop=True,
        break_crops=[],  # Perennial - different management
        recommended_break_years=0,
        yield_loss_potential_percent=100.0,  # Tree death
        economic_impact_level="severe",
        cultural_controls=[
            "Regular inspection",
            "Pheromone traps",
            "Remove and destroy infested palms",
            "Treat wounds with insecticide",
        ],
        cultural_controls_ar=[
            "الفحص المنتظم",
            "مصائد فرمونية",
            "إزالة وتدمير النخيل المصاب",
            "معالجة الجروح بالمبيدات",
        ],
    ),
]


# =============================================================================
# Rotation Compatibility Matrix - مصفوفة توافق الدورة
# =============================================================================


# Good (1.0), Neutral (0.5), Poor (0.0) - previous crop → next crop
ROTATION_COMPATIBILITY: dict[CropType, dict[CropType, float]] = {
    CropType.WHEAT: {
        CropType.WHEAT: 0.2,  # Avoid same crop
        CropType.BARLEY: 0.3,  # Same family - not ideal
        CropType.ALFALFA: 0.9,  # Excellent - N fixation
        CropType.CLOVER: 0.9,
        CropType.FABA_BEAN: 0.9,
        CropType.CHICKPEA: 0.8,
        CropType.TOMATO: 0.7,
        CropType.POTATO: 0.7,
        CropType.ONION: 0.8,
        CropType.CUCUMBER: 0.7,
        CropType.MELON: 0.7,
        CropType.MAIZE: 0.5,  # Same family
        CropType.SORGHUM: 0.5,
        CropType.COTTON: 0.7,
        CropType.FALLOW: 0.8,
        CropType.GREEN_MANURE: 0.9,
    },
    CropType.ALFALFA: {
        CropType.WHEAT: 0.95,  # Excellent - benefits from N
        CropType.BARLEY: 0.9,
        CropType.MAIZE: 0.9,
        CropType.SORGHUM: 0.85,
        CropType.COTTON: 0.85,
        CropType.TOMATO: 0.8,
        CropType.POTATO: 0.8,
        CropType.ALFALFA: 0.2,  # Need break before replanting
        CropType.CLOVER: 0.3,
        CropType.FABA_BEAN: 0.4,
    },
    CropType.TOMATO: {
        CropType.TOMATO: 0.1,  # Severe disease buildup
        CropType.POTATO: 0.2,  # Same family
        CropType.WHEAT: 0.8,
        CropType.BARLEY: 0.8,
        CropType.ALFALFA: 0.9,
        CropType.ONION: 0.8,
        CropType.CUCUMBER: 0.6,  # Some shared diseases
        CropType.FALLOW: 0.9,
    },
    CropType.POTATO: {
        CropType.POTATO: 0.1,
        CropType.TOMATO: 0.2,
        CropType.WHEAT: 0.8,
        CropType.BARLEY: 0.8,
        CropType.ALFALFA: 0.9,
        CropType.CLOVER: 0.85,
        CropType.MAIZE: 0.7,
        CropType.ONION: 0.8,
    },
    CropType.MAIZE: {
        CropType.MAIZE: 0.3,
        CropType.SORGHUM: 0.4,
        CropType.WHEAT: 0.6,
        CropType.ALFALFA: 0.9,
        CropType.FABA_BEAN: 0.85,
        CropType.TOMATO: 0.7,
        CropType.COTTON: 0.7,
    },
}


def get_rotation_compatibility(previous: CropType, next_crop: CropType) -> float:
    """
    Get rotation compatibility score between two crops
    الحصول على درجة توافق الدورة بين محصولين

    Returns a score from 0-1:
    - 1.0: Excellent rotation (e.g., legume → cereal)
    - 0.5: Neutral
    - 0.0: Poor (same crop/family issues)
    """
    if previous in ROTATION_COMPATIBILITY:
        if next_crop in ROTATION_COMPATIBILITY[previous]:
            return ROTATION_COMPATIBILITY[previous][next_crop]

    # Default scoring based on crop families
    prev_char = CROP_DATABASE.get(previous)
    next_char = CROP_DATABASE.get(next_crop)

    if not prev_char or not next_char:
        return 0.5  # Unknown crops

    # Same crop
    if previous == next_crop:
        return 0.2

    # Same family
    if prev_char.crop_family == next_char.crop_family:
        return 0.4

    # Legume before non-legume is good
    if prev_char.is_nitrogen_fixer and not next_char.is_nitrogen_fixer:
        return 0.85

    # Default neutral
    return 0.6


# =============================================================================
# Rotation Planner Class - فئة مخطط الدورة الزراعية
# =============================================================================


@dataclass
class RotationPlannerConfig:
    """Configuration for rotation planner"""

    # Planning parameters
    planning_horizon_years: int = 5
    consider_economic: bool = True
    consider_water: bool = True
    consider_soil_health: bool = True

    # Constraints
    max_same_family_consecutive: int = 2
    min_legume_frequency_percent: float = 25.0  # Include legumes at least 25% of time
    required_fallow_years: int = 0  # 0 = no fallow required

    # Weights for scoring (must sum to 1.0)
    weight_soil_health: float = 0.25
    weight_pest_break: float = 0.25
    weight_economic: float = 0.30
    weight_water: float = 0.20

    # Climate zone
    climate_zone: str = "arid"  # arid, semi-arid, mediterranean

    # Default market prices (SAR/ton)
    default_prices: dict[str, float] = field(
        default_factory=lambda: {
            "wheat": 1850,
            "barley": 1500,
            "alfalfa": 800,
            "tomato": 2500,
            "potato": 2000,
            "onion": 1800,
            "maize": 1400,
        }
    )


class CropRotationPlanner:
    """
    Intelligent crop rotation planning engine
    محرك تخطيط الدورة الزراعية الذكي

    Features:
    - Multi-year rotation planning
    - Pest and disease break recommendations
    - Soil health optimization
    - Nutrient cycling analysis
    - Economic projections
    - Water efficiency consideration
    """

    def __init__(self, config: RotationPlannerConfig | None = None):
        """Initialize planner with configuration"""
        self.config = config or RotationPlannerConfig()
        self.crop_db = CROP_DATABASE
        self.pest_disease_db = PEST_DISEASE_DATABASE

    def get_crop_info(self, crop_type: CropType) -> CropCharacteristics | None:
        """Get crop characteristics from database"""
        return self.crop_db.get(crop_type)

    def analyze_field_history(self, history: FieldRotationHistory) -> dict[str, Any]:
        """
        Analyze field rotation history for patterns and issues
        تحليل سجل دورة الحقل للأنماط والمشاكل
        """
        analysis = {
            "total_years": history.years_of_data,
            "crops_grown": [],
            "family_frequency": {},
            "legume_frequency": 0.0,
            "same_family_consecutive_max": 0,
            "pest_disease_pressure": [],
            "soil_health_trend": history.soil_health_trend,
            "recommendations": [],
            "recommendations_ar": [],
        }

        if not history.records:
            return analysis

        # Analyze crop sequence
        sorted_records = sorted(history.records, key=lambda r: (r.year, r.season.value))

        # Track consecutive same-family crops
        consecutive_count = 1
        max_consecutive = 1
        prev_family = None

        for record in sorted_records:
            crop_info = self.get_crop_info(record.crop_type)
            if crop_info:
                analysis["crops_grown"].append(
                    {
                        "crop": record.crop_type.value,
                        "year": record.year,
                        "season": record.season.value,
                        "yield": record.yield_tons_ha,
                    }
                )

                # Track family frequency
                family = crop_info.crop_family.value
                analysis["family_frequency"][family] = analysis["family_frequency"].get(family, 0) + 1

                # Track consecutive
                if prev_family == crop_info.crop_family:
                    consecutive_count += 1
                    max_consecutive = max(max_consecutive, consecutive_count)
                else:
                    consecutive_count = 1
                prev_family = crop_info.crop_family

                # Track legume frequency
                if crop_info.is_nitrogen_fixer:
                    analysis["legume_frequency"] = analysis.get("legume_frequency", 0) + 1

        analysis["same_family_consecutive_max"] = max_consecutive

        # Calculate legume percentage
        total_crops = len(sorted_records)
        if total_crops > 0:
            analysis["legume_frequency"] = analysis["legume_frequency"] / total_crops * 100

        # Analyze pest/disease pressure from recurring issues
        pest_issues = {}
        disease_issues = {}
        for record in sorted_records:
            for pest in record.pest_issues:
                pest_issues[pest] = pest_issues.get(pest, 0) + 1
            for disease in record.disease_issues:
                disease_issues[disease] = disease_issues.get(disease, 0) + 1

        if pest_issues:
            analysis["pest_disease_pressure"].append(
                {
                    "type": "pests",
                    "issues": dict(sorted(pest_issues.items(), key=lambda x: x[1], reverse=True)[:5]),
                }
            )
        if disease_issues:
            analysis["pest_disease_pressure"].append(
                {
                    "type": "diseases",
                    "issues": dict(sorted(disease_issues.items(), key=lambda x: x[1], reverse=True)[:5]),
                }
            )

        # Generate recommendations based on analysis
        if max_consecutive > 2:
            analysis["recommendations"].append(f"Reduce consecutive same-family crops (current max: {max_consecutive})")
            analysis["recommendations_ar"].append(
                f"تقليل المحاصيل المتتالية من نفس العائلة (الحد الأقصى الحالي: {max_consecutive})"
            )

        if analysis["legume_frequency"] < 20:
            analysis["recommendations"].append("Increase legume frequency to improve nitrogen cycling")
            analysis["recommendations_ar"].append("زيادة تكرار البقوليات لتحسين دورة النيتروجين")

        return analysis

    def get_suitable_crops(
        self,
        previous_crops: list[CropType],
        season: Season,
        soil_ph: float | None = None,
        water_available_mm: float | None = None,
        constraints: list[str] | None = None,
    ) -> list[tuple[CropType, float]]:
        """
        Get list of suitable crops with scores based on rotation principles
        الحصول على قائمة المحاصيل المناسبة مع درجات بناءً على مبادئ الدورة

        Returns list of (crop_type, suitability_score) sorted by score descending
        """
        suitable = []
        constraints = constraints or []

        for crop_type, crop_info in self.crop_db.items():
            # Skip if crop doesn't match season
            if crop_info.growing_season not in [season, Season.YEAR_ROUND, Season.PERENNIAL]:
                continue

            # Skip if explicitly constrained
            if crop_type.value in constraints:
                continue

            # Calculate suitability score
            score = self._calculate_crop_suitability(
                crop_type=crop_type,
                crop_info=crop_info,
                previous_crops=previous_crops,
                soil_ph=soil_ph,
                water_available_mm=water_available_mm,
            )

            if score > 0.3:  # Minimum threshold
                suitable.append((crop_type, score))

        # Sort by score descending
        suitable.sort(key=lambda x: x[1], reverse=True)
        return suitable

    def _calculate_crop_suitability(
        self,
        crop_type: CropType,
        crop_info: CropCharacteristics,
        previous_crops: list[CropType],
        soil_ph: float | None = None,
        water_available_mm: float | None = None,
    ) -> float:
        """Calculate overall suitability score for a crop"""
        scores = []

        # 1. Rotation compatibility with previous crop
        if previous_crops:
            prev_crop = previous_crops[-1]
            rotation_score = get_rotation_compatibility(prev_crop, crop_type)
            scores.append(("rotation", rotation_score, 0.3))

            # Check family repetition
            prev_families = []
            for pc in previous_crops[-3:]:
                pc_info = self.get_crop_info(pc)
                if pc_info:
                    prev_families.append(pc_info.crop_family)

            if crop_info.crop_family in prev_families:
                # Penalize if same family recently
                family_penalty = 0.15 * prev_families.count(crop_info.crop_family)
                scores.append(("family_repetition", 1.0 - family_penalty, 0.15))
        else:
            scores.append(("rotation", 0.7, 0.3))  # No history - neutral

        # 2. Soil pH compatibility
        if soil_ph is not None:
            if crop_info.preferred_ph_min <= soil_ph <= crop_info.preferred_ph_max:
                ph_score = 1.0
            else:
                # Distance from optimal range
                if soil_ph < crop_info.preferred_ph_min:
                    diff = crop_info.preferred_ph_min - soil_ph
                else:
                    diff = soil_ph - crop_info.preferred_ph_max
                ph_score = max(0, 1.0 - (diff * 0.3))
            scores.append(("soil_ph", ph_score, 0.15))

        # 3. Water availability
        if water_available_mm is not None:
            if water_available_mm >= crop_info.water_requirement_mm:
                water_score = 1.0
            else:
                ratio = water_available_mm / crop_info.water_requirement_mm
                # Adjust by drought tolerance
                water_score = min(1.0, ratio + (crop_info.drought_tolerance * 0.3))
            scores.append(("water", water_score, 0.2))

        # 4. Nitrogen benefit (legumes help following crops)
        if previous_crops:
            prev_crop = previous_crops[-1]
            prev_info = self.get_crop_info(prev_crop)
            if prev_info and prev_info.is_nitrogen_fixer and crop_info.nitrogen_demand > 0.5:
                # High N-demand crop following N-fixer is good
                scores.append(("nitrogen_benefit", 0.95, 0.2))
            elif crop_info.is_nitrogen_fixer:
                # Legumes are generally good for rotation
                scores.append(("nitrogen_benefit", 0.85, 0.2))
            else:
                scores.append(("nitrogen_benefit", 0.6, 0.2))

        # Calculate weighted average
        if not scores:
            return 0.5

        total_weight = sum(s[2] for s in scores)
        weighted_sum = sum(s[1] * s[2] for s in scores)
        return weighted_sum / total_weight if total_weight > 0 else 0.5

    def generate_recommendation(
        self,
        field_id: str,
        tenant_id: str,
        previous_crops: list[CropType],
        season: Season,
        field_conditions: dict[str, Any] | None = None,
    ) -> RotationRecommendation:
        """
        Generate AI-powered rotation recommendation
        توليد توصية دورة زراعية مدعومة بالذكاء الاصطناعي
        """
        conditions = field_conditions or {}
        soil_ph = conditions.get("soil_ph")
        water_available = conditions.get("water_available_mm")
        constraints = conditions.get("constraints", [])
        area_ha = conditions.get("area_ha", 1.0)

        # Get suitable crops
        suitable_crops = self.get_suitable_crops(
            previous_crops=previous_crops,
            season=season,
            soil_ph=soil_ph,
            water_available_mm=water_available,
            constraints=constraints,
        )

        if not suitable_crops:
            # Fallback to fallow if nothing suitable
            suitable_crops = [(CropType.FALLOW, 0.8)]

        # Top recommendation
        best_crop, best_score = suitable_crops[0]
        best_info = self.get_crop_info(best_crop)

        # Alternative crops
        alternatives = [c for c, s in suitable_crops[1:4]]

        # Calculate detailed scores
        soil_health_score = self._calculate_soil_health_impact(best_crop, previous_crops)
        pest_break_score = self._calculate_pest_break_score(best_crop, previous_crops)
        economic_score = self._calculate_economic_score(best_crop, area_ha)
        water_score = self._calculate_water_efficiency_score(best_crop, water_available)

        # Generate reasoning
        reasoning_en, reasoning_ar = self._generate_reasoning(
            recommended_crop=best_crop,
            previous_crops=previous_crops,
            scores={
                "soil_health": soil_health_score,
                "pest_break": pest_break_score,
                "economic": economic_score,
                "water_efficiency": water_score,
            },
        )

        # Identify factors
        positive_factors, positive_factors_ar = self._identify_positive_factors(best_crop, previous_crops)
        negative_factors, negative_factors_ar = self._identify_negative_factors(best_crop, previous_crops, conditions)

        # Generate warnings
        warnings, warnings_ar = self._generate_warnings(best_crop, previous_crops)

        # Economic projections
        projected_yield = self._estimate_yield(best_crop, conditions)
        projected_revenue = self._estimate_revenue(best_crop, projected_yield, area_ha)
        projected_cost = self._estimate_cost(best_crop, area_ha)
        projected_profit = projected_revenue - projected_cost if projected_revenue and projected_cost else None

        # Determine benefits
        expected_benefits = self._determine_benefits(best_crop, previous_crops)

        return RotationRecommendation(
            tenant_id=tenant_id,
            field_id=field_id,
            previous_crops=previous_crops,
            priority=self._determine_priority(best_score),
            recommended_crop=best_crop,
            recommended_crop_name_ar=best_info.name_ar if best_info else "",
            alternative_crops=alternatives,
            recommended_season=season,
            expected_benefits=expected_benefits,
            overall_suitability_score=best_score * 100,
            soil_health_score=soil_health_score,
            pest_break_score=pest_break_score,
            economic_score=economic_score,
            water_efficiency_score=water_score,
            reasoning_en=reasoning_en,
            reasoning_ar=reasoning_ar,
            positive_factors=positive_factors,
            positive_factors_ar=positive_factors_ar,
            negative_factors=negative_factors,
            negative_factors_ar=negative_factors_ar,
            warnings=warnings,
            warnings_ar=warnings_ar,
            projected_yield_tons_ha=projected_yield,
            projected_revenue_per_ha=projected_revenue / area_ha if projected_revenue and area_ha else None,
            projected_cost_per_ha=projected_cost / area_ha if projected_cost and area_ha else None,
            projected_profit_per_ha=projected_profit / area_ha if projected_profit and area_ha else None,
            confidence=min(0.95, best_score + 0.1),
        )

    def _calculate_soil_health_impact(self, crop: CropType, previous_crops: list[CropType]) -> float:
        """Calculate soil health impact score (0-100)"""
        crop_info = self.get_crop_info(crop)
        if not crop_info:
            return 50.0

        score = 50.0  # Base score

        # Nitrogen fixation bonus
        if crop_info.is_nitrogen_fixer:
            score += 25.0

        # Deep rooting bonus
        if crop_info.root_depth_cm > 100:
            score += 10.0

        # Different root type from previous
        if previous_crops:
            prev_info = self.get_crop_info(previous_crops[-1])
            if prev_info and prev_info.root_type != crop_info.root_type:
                score += 10.0

        # Same family penalty
        if previous_crops:
            for pc in previous_crops[-2:]:
                pc_info = self.get_crop_info(pc)
                if pc_info and pc_info.crop_family == crop_info.crop_family:
                    score -= 15.0

        return max(0, min(100, score))

    def _calculate_pest_break_score(self, crop: CropType, previous_crops: list[CropType]) -> float:
        """Calculate pest/disease break effectiveness score (0-100)"""
        crop_info = self.get_crop_info(crop)
        if not crop_info:
            return 50.0

        score = 70.0  # Base score

        if not previous_crops:
            return score

        # Check if this crop breaks pest cycles
        for prev_crop in previous_crops[-3:]:
            prev_info = self.get_crop_info(prev_crop)
            if not prev_info:
                continue

            # Different family is good
            if prev_info.crop_family != crop_info.crop_family:
                score += 5.0

            # Check specific break crop relationships
            if prev_crop.value in crop_info.break_crop_for:
                score += 15.0

            # Same major pests/diseases is bad
            shared_pests = set(prev_info.major_pests) & set(crop_info.major_pests)
            shared_diseases = set(prev_info.major_diseases) & set(crop_info.major_diseases)
            score -= len(shared_pests) * 5
            score -= len(shared_diseases) * 5

        return max(0, min(100, score))

    def _calculate_economic_score(self, crop: CropType, area_ha: float) -> float:
        """Calculate economic viability score (0-100)"""
        # Simplified economic scoring - in production, use actual market data
        high_value_crops = [
            CropType.TOMATO,
            CropType.POTATO,
            CropType.MELON,
            CropType.WATERMELON,
            CropType.CUCUMBER,
            CropType.ONION,
        ]
        medium_value_crops = [CropType.WHEAT, CropType.BARLEY, CropType.COTTON, CropType.ALFALFA]

        if crop in high_value_crops:
            return 85.0
        elif crop in medium_value_crops:
            return 70.0
        elif crop == CropType.FALLOW:
            return 40.0  # No direct income but soil benefits
        elif crop == CropType.GREEN_MANURE:
            return 50.0
        else:
            return 60.0

    def _calculate_water_efficiency_score(self, crop: CropType, water_available: float | None) -> float:
        """Calculate water efficiency score (0-100)"""
        crop_info = self.get_crop_info(crop)
        if not crop_info:
            return 50.0

        # Base score on drought tolerance
        score = crop_info.drought_tolerance * 60 + 40

        # If water availability is known, factor it in
        if water_available is not None:
            if water_available >= crop_info.water_requirement_mm:
                score = min(100, score + 10)
            else:
                ratio = water_available / crop_info.water_requirement_mm
                if ratio < 0.5:
                    score -= 30
                elif ratio < 0.75:
                    score -= 15

        return max(0, min(100, score))

    def _generate_reasoning(
        self, recommended_crop: CropType, previous_crops: list[CropType], scores: dict[str, float]
    ) -> tuple[str, str]:
        """Generate bilingual reasoning for recommendation"""
        crop_info = self.get_crop_info(recommended_crop)
        if not crop_info:
            return (
                "Recommended based on rotation principles.",
                "موصى به بناءً على مبادئ الدورة الزراعية.",
            )

        reasons_en = []
        reasons_ar = []

        # Soil health
        if scores.get("soil_health", 0) > 70:
            if crop_info.is_nitrogen_fixer:
                reasons_en.append("Fixes atmospheric nitrogen, reducing fertilizer needs")
                reasons_ar.append("يثبت النيتروجين الجوي، مما يقلل الحاجة للأسمدة")
            if crop_info.root_depth_cm > 100:
                reasons_en.append("Deep roots improve soil structure")
                reasons_ar.append("الجذور العميقة تحسن بنية التربة")

        # Pest break
        if scores.get("pest_break", 0) > 70:
            reasons_en.append("Breaks pest and disease cycles from previous crops")
            reasons_ar.append("يكسر دورة الآفات والأمراض من المحاصيل السابقة")

        # Water efficiency
        if scores.get("water_efficiency", 0) > 70:
            reasons_en.append("Good water use efficiency for local conditions")
            reasons_ar.append("كفاءة جيدة في استخدام المياه للظروف المحلية")

        # Economic
        if scores.get("economic", 0) > 70:
            reasons_en.append("Good market value and economic returns")
            reasons_ar.append("قيمة سوقية جيدة وعوائد اقتصادية")

        if not reasons_en:
            reasons_en.append("Suitable crop for the planned season and field conditions")
            reasons_ar.append("محصول مناسب للموسم المخطط وظروف الحقل")

        reasoning_en = f"{crop_info.name_en} is recommended because it: " + "; ".join(reasons_en) + "."
        reasoning_ar = f"يوصى بـ {crop_info.name_ar} لأنه: " + "؛ ".join(reasons_ar) + "."

        return reasoning_en, reasoning_ar

    def _identify_positive_factors(self, crop: CropType, previous_crops: list[CropType]) -> tuple[list[str], list[str]]:
        """Identify positive factors for the recommendation"""
        factors_en = []
        factors_ar = []
        crop_info = self.get_crop_info(crop)

        if crop_info:
            if crop_info.is_nitrogen_fixer:
                factors_en.append("Nitrogen fixation benefit")
                factors_ar.append("فائدة تثبيت النيتروجين")

            if crop_info.drought_tolerance > 0.6:
                factors_en.append("High drought tolerance")
                factors_ar.append("تحمل عالي للجفاف")

            if crop_info.salt_tolerance > 0.5:
                factors_en.append("Good salt tolerance")
                factors_ar.append("تحمل جيد للملوحة")

            # Check rotation compatibility
            if previous_crops:
                prev_crop = previous_crops[-1]
                compat = get_rotation_compatibility(prev_crop, crop)
                if compat > 0.8:
                    factors_en.append("Excellent rotation fit with previous crop")
                    factors_ar.append("تناسب ممتاز في الدورة مع المحصول السابق")

        return factors_en, factors_ar

    def _identify_negative_factors(
        self, crop: CropType, previous_crops: list[CropType], conditions: dict[str, Any]
    ) -> tuple[list[str], list[str]]:
        """Identify potential concerns or negative factors"""
        factors_en = []
        factors_ar = []
        crop_info = self.get_crop_info(crop)

        if crop_info:
            # Water concerns
            water_available = conditions.get("water_available_mm")
            if water_available and water_available < crop_info.water_requirement_mm * 0.8:
                factors_en.append("May need supplemental irrigation")
                factors_ar.append("قد يحتاج ري إضافي")

            # pH concerns
            soil_ph = conditions.get("soil_ph")
            if soil_ph:
                if soil_ph < crop_info.preferred_ph_min:
                    factors_en.append("Soil pH may be too low - consider liming")
                    factors_ar.append("قد تكون حموضة التربة منخفضة - يُنصح بالتجيير")
                elif soil_ph > crop_info.preferred_ph_max:
                    factors_en.append("Soil pH may be too high")
                    factors_ar.append("قد تكون حموضة التربة مرتفعة")

            # Family repetition
            if previous_crops:
                for pc in previous_crops[-2:]:
                    pc_info = self.get_crop_info(pc)
                    if pc_info and pc_info.crop_family == crop_info.crop_family:
                        factors_en.append("Same crop family as recent crop - monitor for pests")
                        factors_ar.append("نفس عائلة المحصول السابق - راقب الآفات")
                        break

        return factors_en, factors_ar

    def _generate_warnings(self, crop: CropType, previous_crops: list[CropType]) -> tuple[list[str], list[str]]:
        """Generate warnings for the recommendation"""
        warnings_en = []
        warnings_ar = []
        crop_info = self.get_crop_info(crop)

        if crop_info:
            # Check for repeated same-family
            if previous_crops:
                consecutive_same_family = 0
                for pc in reversed(previous_crops):
                    pc_info = self.get_crop_info(pc)
                    if pc_info and pc_info.crop_family == crop_info.crop_family:
                        consecutive_same_family += 1
                    else:
                        break

                if consecutive_same_family >= 2:
                    warnings_en.append(
                        f"Warning: {consecutive_same_family} consecutive crops from same family - "
                        "consider different family next rotation"
                    )
                    warnings_ar.append(
                        f"تحذير: {consecutive_same_family} محاصيل متتالية من نفس العائلة - "
                        "يُنصح باختيار عائلة مختلفة في الدورة القادمة"
                    )

            # Major pest/disease warnings
            if crop_info.major_diseases:
                for disease in crop_info.major_diseases[:2]:
                    warnings_en.append(f"Monitor for {disease.replace('_', ' ')}")
                    warnings_ar.append(f"راقب {disease.replace('_', ' ')}")

        return warnings_en, warnings_ar

    def _estimate_yield(self, crop: CropType, conditions: dict[str, Any]) -> float | None:
        """Estimate expected yield (tons/ha)"""
        # Simplified yield estimates - in production, use regional data
        base_yields = {
            CropType.WHEAT: 4.5,
            CropType.BARLEY: 3.5,
            CropType.MAIZE: 8.0,
            CropType.SORGHUM: 5.0,
            CropType.ALFALFA: 15.0,  # Multiple cuts
            CropType.TOMATO: 60.0,
            CropType.POTATO: 30.0,
            CropType.ONION: 35.0,
            CropType.CUCUMBER: 40.0,
            CropType.MELON: 25.0,
            CropType.WATERMELON: 35.0,
        }
        return base_yields.get(crop)

    def _estimate_revenue(self, crop: CropType, yield_tons: float | None, area_ha: float) -> float | None:
        """Estimate revenue"""
        if not yield_tons:
            return None
        price = self.config.default_prices.get(crop.value, 1500)
        return yield_tons * price * area_ha

    def _estimate_cost(self, crop: CropType, area_ha: float) -> float | None:
        """Estimate production cost"""
        # Simplified cost estimates (SAR/ha)
        base_costs = {
            CropType.WHEAT: 3500,
            CropType.BARLEY: 3000,
            CropType.MAIZE: 5000,
            CropType.ALFALFA: 6000,
            CropType.TOMATO: 25000,
            CropType.POTATO: 18000,
            CropType.ONION: 15000,
            CropType.CUCUMBER: 20000,
        }
        cost_per_ha = base_costs.get(crop, 5000)
        return cost_per_ha * area_ha

    def _determine_benefits(self, crop: CropType, previous_crops: list[CropType]) -> list[RotationBenefit]:
        """Determine rotation benefits provided by crop"""
        benefits = []
        crop_info = self.get_crop_info(crop)

        if crop_info:
            if crop_info.is_nitrogen_fixer:
                benefits.append(RotationBenefit.NITROGEN_FIXATION)
                benefits.append(RotationBenefit.NUTRIENT_CYCLING)

            if crop_info.root_depth_cm > 100:
                benefits.append(RotationBenefit.SOIL_STRUCTURE)

            # Check for pest break
            if previous_crops:
                prev_info = self.get_crop_info(previous_crops[-1])
                if prev_info and prev_info.crop_family != crop_info.crop_family:
                    benefits.append(RotationBenefit.PEST_BREAK)
                    benefits.append(RotationBenefit.DISEASE_BREAK)

            if crop_info.residue_nitrogen_kg_ha > 0:
                benefits.append(RotationBenefit.ORGANIC_MATTER)

            if crop_info.drought_tolerance > 0.6:
                benefits.append(RotationBenefit.WATER_EFFICIENCY)

        return list(set(benefits))  # Remove duplicates

    def _determine_priority(self, score: float) -> RecommendationPriority:
        """Determine recommendation priority based on score"""
        if score >= 0.85:
            return RecommendationPriority.HIGH
        elif score >= 0.7:
            return RecommendationPriority.MEDIUM
        elif score >= 0.5:
            return RecommendationPriority.LOW
        else:
            return RecommendationPriority.OPTIONAL

    def generate_multi_year_plan(
        self,
        field_id: str,
        tenant_id: str,
        field_name: str,
        field_name_ar: str,
        area_ha: float,
        starting_crop: CropType | None,
        start_year: int,
        years: int = 5,
        field_conditions: dict[str, Any] | None = None,
    ) -> MultiYearPlan:
        """
        Generate complete multi-year rotation plan
        توليد خطة دورة زراعية متعددة السنوات
        """
        conditions = field_conditions or {}
        yearly_recommendations = []
        previous_crops = [starting_crop] if starting_crop else []

        # Generate recommendation for each year
        for year_offset in range(years):
            current_year = start_year + year_offset

            # Alternate seasons
            for season in [Season.WINTER, Season.SUMMER]:
                rec = self.generate_recommendation(
                    field_id=field_id,
                    tenant_id=tenant_id,
                    previous_crops=previous_crops.copy(),
                    season=season,
                    field_conditions=conditions,
                )
                rec.recommended_planting_window_start = date(current_year, 10 if season == Season.WINTER else 4, 1)
                yearly_recommendations.append(rec)

                # Add to history for next iteration
                if rec.recommended_crop:
                    previous_crops.append(rec.recommended_crop)
                    if len(previous_crops) > 5:
                        previous_crops.pop(0)

        # Calculate cumulative projections
        total_revenue = sum(
            r.projected_revenue_per_ha * area_ha for r in yearly_recommendations if r.projected_revenue_per_ha
        )
        total_cost = sum(r.projected_cost_per_ha * area_ha for r in yearly_recommendations if r.projected_cost_per_ha)
        total_profit = total_revenue - total_cost

        # Calculate nutrient balance
        nutrient_balance = self._calculate_nutrient_balance(yearly_recommendations)

        # Risk assessment
        risk_level, risk_factors, risk_factors_ar, mitigation, mitigation_ar = self._assess_plan_risks(
            yearly_recommendations
        )

        # Generate summary
        summary_en, summary_ar = self._generate_plan_summary(yearly_recommendations, total_profit, area_ha, years)

        # Key recommendations
        key_recs, key_recs_ar = self._generate_key_recommendations(yearly_recommendations)

        return MultiYearPlan(
            tenant_id=tenant_id,
            field_id=field_id,
            field_name=field_name,
            field_name_ar=field_name_ar,
            total_area_ha=area_ha,
            start_year=start_year,
            end_year=start_year + years - 1,
            total_years=years,
            yearly_recommendations=yearly_recommendations,
            total_projected_revenue=total_revenue,
            total_projected_cost=total_cost,
            total_projected_profit=total_profit,
            average_annual_profit_per_ha=total_profit / (years * area_ha) if area_ha > 0 else 0,
            nutrient_balance=nutrient_balance,
            overall_risk_level=risk_level,
            risk_factors=risk_factors,
            risk_factors_ar=risk_factors_ar,
            risk_mitigation=mitigation,
            risk_mitigation_ar=mitigation_ar,
            summary_en=summary_en,
            summary_ar=summary_ar,
            key_recommendations=key_recs,
            key_recommendations_ar=key_recs_ar,
        )

    def _calculate_nutrient_balance(self, recommendations: list[RotationRecommendation]) -> NutrientBalance:
        """Calculate overall nutrient balance for plan"""
        balance = NutrientBalance()

        for rec in recommendations:
            if not rec.recommended_crop:
                continue
            crop_info = self.get_crop_info(rec.recommended_crop)
            if not crop_info:
                continue

            # N fixation
            if crop_info.is_nitrogen_fixer:
                balance.nitrogen_fixation_contribution += crop_info.residue_nitrogen_kg_ha
                balance.nitrogen_inputs += crop_info.residue_nitrogen_kg_ha

            # Estimate nutrient removal (simplified)
            balance.nitrogen_outputs += crop_info.nitrogen_demand * 100  # Rough estimate
            balance.phosphorus_outputs += crop_info.phosphorus_demand * 30
            balance.potassium_outputs += crop_info.potassium_demand * 50

        balance.nitrogen_balance = balance.nitrogen_inputs - balance.nitrogen_outputs
        balance.phosphorus_balance = balance.phosphorus_inputs - balance.phosphorus_outputs
        balance.potassium_balance = balance.potassium_inputs - balance.potassium_outputs

        # Assess sustainability
        balance.is_sustainable = balance.nitrogen_balance > -50
        balance.sustainability_score = min(100, max(0, 50 + balance.nitrogen_balance / 2))

        return balance

    def _assess_plan_risks(
        self, recommendations: list[RotationRecommendation]
    ) -> tuple[str, list[str], list[str], list[str], list[str]]:
        """Assess overall plan risks"""
        risk_factors = []
        risk_factors_ar = []
        mitigation = []
        mitigation_ar = []

        # Check for same family repetition
        families = []
        for rec in recommendations:
            if rec.recommended_crop:
                crop_info = self.get_crop_info(rec.recommended_crop)
                if crop_info:
                    families.append(crop_info.crop_family)

        # Check consecutive same family
        max_consecutive = 1
        current_consecutive = 1
        for i in range(1, len(families)):
            if families[i] == families[i - 1]:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 1

        if max_consecutive > 2:
            risk_factors.append(f"Same crop family repeated {max_consecutive} times consecutively")
            risk_factors_ar.append(f"تكرار نفس عائلة المحصول {max_consecutive} مرات متتالية")
            mitigation.append("Consider inserting a break crop between same-family plantings")
            mitigation_ar.append("يُنصح بإدراج محصول كسر بين زراعات نفس العائلة")

        # Check legume frequency
        legume_count = sum(
            1
            for rec in recommendations
            if rec.recommended_crop
            and self.get_crop_info(rec.recommended_crop)
            and self.get_crop_info(rec.recommended_crop).is_nitrogen_fixer
        )
        legume_percent = legume_count / len(recommendations) * 100 if recommendations else 0

        if legume_percent < 20:
            risk_factors.append("Low legume frequency may lead to nitrogen depletion")
            risk_factors_ar.append("قلة البقوليات قد تؤدي إلى استنزاف النيتروجين")
            mitigation.append("Increase legume crops or use nitrogen fertilizer")
            mitigation_ar.append("زيادة محاصيل البقوليات أو استخدام سماد نيتروجيني")

        # Determine overall risk level
        if len(risk_factors) == 0:
            risk_level = "low"
        elif len(risk_factors) <= 2:
            risk_level = "medium"
        else:
            risk_level = "high"

        return risk_level, risk_factors, risk_factors_ar, mitigation, mitigation_ar

    def _generate_plan_summary(
        self,
        recommendations: list[RotationRecommendation],
        total_profit: float,
        area_ha: float,
        years: int,
    ) -> tuple[str, str]:
        """Generate plan summary"""
        crop_names = []
        crop_names_ar = []

        for rec in recommendations[:6]:  # First 3 years
            if rec.recommended_crop:
                crop_info = self.get_crop_info(rec.recommended_crop)
                if crop_info:
                    crop_names.append(crop_info.name_en)
                    crop_names_ar.append(crop_info.name_ar)

        profit_per_ha = total_profit / (area_ha * years) if area_ha > 0 else 0

        summary_en = (
            f"This {years}-year rotation plan covers {area_ha} hectares with a sequence "
            f"including {', '.join(crop_names[:4])}. "
            f"Projected average annual profit: {profit_per_ha:,.0f} SAR/ha."
        )

        summary_ar = (
            f"خطة الدورة الزراعية لـ {years} سنوات تغطي {area_ha} هكتار بتسلسل "
            f"يشمل {', '.join(crop_names_ar[:4])}. "
            f"الربح السنوي المتوقع: {profit_per_ha:,.0f} ريال/هكتار."
        )

        return summary_en, summary_ar

    def _generate_key_recommendations(
        self, recommendations: list[RotationRecommendation]
    ) -> tuple[list[str], list[str]]:
        """Generate key recommendations for the plan"""
        key_recs = [
            "Follow the rotation sequence to maximize soil health benefits",
            "Include legumes regularly to reduce fertilizer costs",
            "Monitor for pests and diseases during family-repeated plantings",
            "Adjust planting dates based on actual weather conditions",
        ]
        key_recs_ar = [
            "اتبع تسلسل الدورة لتعظيم فوائد صحة التربة",
            "أدرج البقوليات بانتظام لتقليل تكاليف الأسمدة",
            "راقب الآفات والأمراض خلال زراعات العائلة المتكررة",
            "عدّل مواعيد الزراعة بناءً على ظروف الطقس الفعلية",
        ]
        return key_recs, key_recs_ar

    def generate_pest_break_recommendation(
        self,
        field_id: str,
        current_crop: CropType,
        pest_disease_history: list[str],
    ) -> PestBreakRecommendation:
        """
        Generate pest/disease break recommendation
        توليد توصية لكسر دورة الآفات/الأمراض
        """
        # Find relevant pest/disease risks
        relevant_risks = []
        for risk in self.pest_disease_db:
            # Check if current crop is a host
            if current_crop in risk.host_crops:
                relevant_risks.append(risk)
            # Check if pest/disease in history
            for issue in pest_disease_history:
                if issue.lower() in risk.name_en.lower() or issue in risk.scientific_name:
                    if risk not in relevant_risks:
                        relevant_risks.append(risk)

        if not relevant_risks:
            return PestBreakRecommendation(
                field_id=field_id,
                current_crop=current_crop,
                priority=RecommendationPriority.LOW,
                reasoning_en="No specific pest or disease concerns identified.",
                reasoning_ar="لم يتم تحديد مخاوف محددة بشأن الآفات أو الأمراض.",
            )

        # Collect break crops from all relevant risks
        break_crops_scores: dict[CropType, float] = {}
        max_break_years = 1

        for risk in relevant_risks:
            max_break_years = max(max_break_years, risk.recommended_break_years)
            for crop in risk.break_crops:
                break_crops_scores[crop] = break_crops_scores.get(crop, 0) + 1

        # Sort by frequency (how many risks they help with)
        recommended_crops = sorted(break_crops_scores.keys(), key=lambda c: break_crops_scores[c], reverse=True)[:5]

        # Calculate expected improvement
        avg_yield_loss = sum(r.yield_loss_potential_percent for r in relevant_risks) / len(relevant_risks)
        expected_reduction = min(80, avg_yield_loss * 0.7)

        # Generate reasoning
        risk_names = ", ".join(r.name_en for r in relevant_risks[:3])
        risk_names_ar = "، ".join(r.name_ar for r in relevant_risks[:3])

        reasoning_en = (
            f"Based on identified risks ({risk_names}), "
            f"a {max_break_years}-year break with non-host crops is recommended "
            f"to reduce pest and disease pressure by approximately {expected_reduction:.0f}%."
        )
        reasoning_ar = (
            f"بناءً على المخاطر المحددة ({risk_names_ar})، "
            f"يوصى بفترة انقطاع {max_break_years} سنة مع محاصيل غير عائلة "
            f"لتقليل ضغط الآفات والأمراض بنسبة تقارب {expected_reduction:.0f}%."
        )

        # Generate warnings
        warnings_en = []
        warnings_ar = []
        for risk in relevant_risks:
            if risk.soil_persistence_years > 2:
                warnings_en.append(f"{risk.name_en} persists in soil for {risk.soil_persistence_years} years")
                warnings_ar.append(f"{risk.name_ar} يستمر في التربة لـ {risk.soil_persistence_years} سنوات")

        return PestBreakRecommendation(
            field_id=field_id,
            current_crop=current_crop,
            pest_disease_risks=relevant_risks,
            priority=RecommendationPriority.HIGH if len(relevant_risks) > 1 else RecommendationPriority.MEDIUM,
            recommended_break_crops=recommended_crops,
            minimum_break_years=max_break_years,
            reasoning_en=reasoning_en,
            reasoning_ar=reasoning_ar,
            expected_risk_reduction_percent=expected_reduction,
            expected_yield_improvement_percent=expected_reduction * 0.5,
            warnings_en=warnings_en,
            warnings_ar=warnings_ar,
        )


# =============================================================================
# Helper Functions - الدوال المساعدة
# =============================================================================


def get_crop_characteristics(crop_type: CropType) -> CropCharacteristics | None:
    """Get crop characteristics from database"""
    return CROP_DATABASE.get(crop_type)


def get_crop_arabic_name(crop_type: CropType) -> str:
    """Get Arabic name for a crop type"""
    crop_info = CROP_DATABASE.get(crop_type)
    return crop_info.name_ar if crop_info else crop_type.value


def get_recommended_break_crops(current_crop: CropType, min_score: float = 0.7) -> list[CropType]:
    """Get list of good break crops for a given crop"""
    break_crops = []
    for next_crop in CROP_DATABASE:
        score = get_rotation_compatibility(current_crop, next_crop)
        if score >= min_score:
            break_crops.append(next_crop)
    return break_crops


def calculate_rotation_score(crop_sequence: list[CropType]) -> float:
    """
    Calculate overall rotation score for a sequence of crops
    حساب درجة الدورة الإجمالية لتسلسل من المحاصيل
    """
    if len(crop_sequence) < 2:
        return 0.5

    scores = []
    for i in range(1, len(crop_sequence)):
        prev_crop = crop_sequence[i - 1]
        next_crop = crop_sequence[i]
        scores.append(get_rotation_compatibility(prev_crop, next_crop))

    return sum(scores) / len(scores)
