"""
SAHOOL Crop Rotation - Example Usage
مثال على استخدام تدوير المحاصيل

This script demonstrates how to use the crop rotation planning service.
"""

import asyncio
import sys
from datetime import date
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from crop_rotation import (
    CropFamily,
    CropRotationPlanner,
    SeasonPlan,
)


async def main():
    """Run example scenarios"""

    planner = CropRotationPlanner()

    print("=" * 80)
    print("SAHOOL Crop Rotation Planning - Example Usage")
    print("مثال على تخطيط تدوير المحاصيل في سهول")
    print("=" * 80)
    print()

    # ====================================================================
    # Example 1: Create a 5-year rotation plan
    # ====================================================================

    print("Example 1: Create a 5-year rotation plan")
    print("-" * 80)

    plan = await planner.create_rotation_plan(
        field_id="FIELD_001",
        field_name="حقل التجريب - Test Field",
        start_year=2025,
        num_years=5,
    )

    print(f"Field: {plan.field_name}")
    print(f"Period: {plan.start_year} - {plan.end_year}")
    print(f"Diversity Score: {plan.diversity_score:.1f}/100")
    print(f"Soil Health Score: {plan.soil_health_score:.1f}/100")
    print(f"Disease Risk Score: {plan.disease_risk_score:.1f}/100 (lower is better)")
    print(f"Nitrogen Balance: {plan.nitrogen_balance}")
    print()

    print("Planned Seasons:")
    for season in plan.seasons:
        print(
            f"  {season.year} {season.season}: {season.crop_name_en} ({season.crop_name_ar}) - {season.crop_family.value}"
        )
    print()

    if plan.recommendations_en:
        print("Recommendations:")
        for rec in plan.recommendations_en:
            print(f"  • {rec}")
    print()

    if plan.warnings_en:
        print("Warnings:")
        for warn in plan.warnings_en:
            print(f"  ⚠ {warn}")
    print()

    # ====================================================================
    # Example 2: Suggest next crop based on field history
    # ====================================================================

    print("Example 2: Suggest next crop based on field history")
    print("-" * 80)

    # Create field history
    history = [
        SeasonPlan(
            season_id="FIELD_002_2022_winter",
            year=2022,
            season="winter",
            crop_code="WHEAT",
            crop_name_ar="قمح",
            crop_name_en="Wheat",
            crop_family=CropFamily.CEREALS,
            planting_date=date(2022, 10, 1),
            harvest_date=date(2023, 3, 1),
            expected_yield=2.5,
        ),
        SeasonPlan(
            season_id="FIELD_002_2023_winter",
            year=2023,
            season="winter",
            crop_code="BARLEY",
            crop_name_ar="شعير",
            crop_name_en="Barley",
            crop_family=CropFamily.CEREALS,
            planting_date=date(2023, 10, 1),
            harvest_date=date(2024, 3, 1),
            expected_yield=2.0,
        ),
        SeasonPlan(
            season_id="FIELD_002_2024_winter",
            year=2024,
            season="winter",
            crop_code="SORGHUM",
            crop_name_ar="ذرة رفيعة",
            crop_name_en="Sorghum",
            crop_family=CropFamily.CEREALS,
            planting_date=date(2024, 10, 1),
            harvest_date=date(2025, 3, 1),
            expected_yield=3.0,
        ),
    ]

    print("Field History (last 3 years):")
    for h in history:
        print(f"  {h.year}: {h.crop_name_en} ({h.crop_name_ar})")
    print()

    suggestions = await planner.suggest_next_crop(
        field_id="FIELD_002", history=history, season="winter"
    )

    print("Top 5 Crop Suggestions for Winter 2025:")
    print()
    for i, suggestion in enumerate(suggestions[:5], 1):
        print(f"{i}. {suggestion.crop_name_en} ({suggestion.crop_name_ar})")
        print(f"   Family: {suggestion.crop_family.value}")
        print(f"   Suitability: {suggestion.suitability_score:.1f}/100")
        print("   Reasons:")
        for reason in suggestion.reasons_en:
            print(f"     ✓ {reason}")
        if suggestion.warnings_en:
            print("   Warnings:")
            for warning in suggestion.warnings_en:
                print(f"     ⚠ {warning}")
        print()

    # ====================================================================
    # Example 3: Evaluate a custom rotation plan
    # ====================================================================

    print("Example 3: Evaluate a custom rotation plan")
    print("-" * 80)

    custom_rotation = [
        SeasonPlan(
            season_id="S1",
            year=2025,
            season="winter",
            crop_code="WHEAT",
            crop_name_ar="قمح",
            crop_name_en="Wheat",
            crop_family=CropFamily.CEREALS,
        ),
        SeasonPlan(
            season_id="S2",
            year=2026,
            season="winter",
            crop_code="FABA_BEAN",
            crop_name_ar="فول",
            crop_name_en="Faba Bean",
            crop_family=CropFamily.LEGUMES,
        ),
        SeasonPlan(
            season_id="S3",
            year=2027,
            season="winter",
            crop_code="TOMATO",
            crop_name_ar="طماطم",
            crop_name_en="Tomato",
            crop_family=CropFamily.SOLANACEAE,
        ),
        SeasonPlan(
            season_id="S4",
            year=2028,
            season="winter",
            crop_code="WHEAT",
            crop_name_ar="قمح",
            crop_name_en="Wheat",
            crop_family=CropFamily.CEREALS,
        ),
        SeasonPlan(
            season_id="S5",
            year=2029,
            season="winter",
            crop_code="FALLOW",
            crop_name_ar="بور",
            crop_name_en="Fallow",
            crop_family=CropFamily.FALLOW,
        ),
    ]

    print("Custom Rotation Plan:")
    for season in custom_rotation:
        print(f"  {season.year}: {season.crop_name_en} ({season.crop_family.value})")
    print()

    evaluation = planner.evaluate_rotation(custom_rotation)

    print("Evaluation Results:")
    print(f"  Diversity Score: {evaluation['diversity_score']:.1f}/100")
    print(f"  Soil Health Score: {evaluation['soil_health_score']:.1f}/100")
    print(f"  Disease Risk Score: {evaluation['disease_risk_score']:.1f}/100")
    print(f"  Nitrogen Balance: {evaluation['nitrogen_balance']}")
    print()

    if evaluation["recommendations_en"]:
        print("Recommendations:")
        for rec in evaluation["recommendations_en"]:
            print(f"  • {rec}")
    print()

    # ====================================================================
    # Example 4: Check rotation compatibility
    # ====================================================================

    print("Example 4: Check rotation compatibility")
    print("-" * 80)

    # Check if Solanaceae can follow cereals
    test_history = [
        SeasonPlan(
            season_id="T1",
            year=2024,
            season="winter",
            crop_code="WHEAT",
            crop_name_ar="قمح",
            crop_name_en="Wheat",
            crop_family=CropFamily.CEREALS,
        )
    ]

    is_valid, messages = planner.check_rotation_rule(
        CropFamily.SOLANACEAE, test_history
    )

    print("Test: Can we plant tomatoes (Solanaceae) after wheat?")
    print(f"Result: {'✓ Compatible' if is_valid else '✗ Not Compatible'}")
    if messages:
        for _msg_ar, msg_en in messages:
            print(f"  {msg_en}")
    print()

    # Check if we can repeat Solanaceae immediately
    test_history2 = [
        SeasonPlan(
            season_id="T2",
            year=2024,
            season="winter",
            crop_code="TOMATO",
            crop_name_ar="طماطم",
            crop_name_en="Tomato",
            crop_family=CropFamily.SOLANACEAE,
        )
    ]

    is_valid2, messages2 = planner.check_rotation_rule(
        CropFamily.SOLANACEAE, test_history2
    )

    print("Test: Can we plant tomatoes again immediately after tomatoes?")
    print(f"Result: {'✓ Compatible' if is_valid2 else '✗ Not Compatible'}")
    if messages2:
        for _msg_ar, msg_en in messages2:
            print(f"  {msg_en}")
    print()

    # ====================================================================
    # Example 5: View rotation rules
    # ====================================================================

    print("Example 5: View rotation rules for key families")
    print("-" * 80)

    for family in [CropFamily.CEREALS, CropFamily.LEGUMES, CropFamily.SOLANACEAE]:
        rule = planner.ROTATION_RULES[family]
        print(f"{family.value.upper()}:")
        print(f"  Minimum years between: {rule.min_years_between}")
        print(f"  Nitrogen effect: {rule.nitrogen_effect}")
        print(f"  Root depth: {rule.root_depth}")
        print(f"  Nutrient demand: {rule.nutrient_demand}")
        print(
            f"  Good predecessors: {', '.join(f.value for f in rule.good_predecessors)}"
        )
        print(
            f"  Bad predecessors: {', '.join(f.value for f in rule.bad_predecessors)}"
        )
        print()

    print("=" * 80)
    print("Examples completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
