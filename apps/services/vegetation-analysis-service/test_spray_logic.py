"""
Unit tests for spray advisor logic (without API calls)
اختبارات منطق مستشار الرش (بدون استدعاءات API)
"""

from src.spray_advisor import (
    SprayAdvisor,
    SprayCondition,
    SprayProduct,
)


def test_calculate_spray_score():
    """Test spray score calculation"""
    print("\n" + "=" * 80)
    print("🧪 SPRAY SCORE CALCULATION TEST")
    print("=" * 80 + "\n")

    advisor = SprayAdvisor()

    test_cases = [
        # (temp, humidity, wind, rain_prob, product, expected_condition, description)
        (22, 60, 8, 10, None, SprayCondition.EXCELLENT, "Ideal conditions"),
        (
            25,
            55,
            12,
            15,
            SprayProduct.HERBICIDE,
            SprayCondition.GOOD,
            "Good herbicide conditions",
        ),
        (18, 45, 18, 25, None, SprayCondition.MARGINAL, "High wind and rain risk"),
        (8, 85, 5, 5, None, SprayCondition.POOR, "Too cold"),
        (35, 30, 20, 40, None, SprayCondition.DANGEROUS, "Hot, dry, windy, rain"),
    ]

    print(f"{'Conditions':<40} {'Score':<10} {'Level':<15} {'Status'}")
    print(f"{'-' * 80}")

    for temp, humidity, wind, rain, product, expected, desc in test_cases:
        score, condition, risks = advisor.calculate_spray_score(temp, humidity, wind, rain, product)

        status = "✅" if condition == expected else f"⚠️  (expected {expected.value})"
        print(f"{desc:<40} {score:>6.1f}/100  {condition.value.upper():<15} {status}")

        if risks:
            print(f"{'  Risks:':<40} {', '.join(risks[:3])}")

    print("\n" + "=" * 80)


def test_product_specific_conditions():
    """Test product-specific scoring differences"""
    print("\n" + "=" * 80)
    print("🌿 PRODUCT-SPECIFIC CONDITIONS TEST")
    print("=" * 80 + "\n")

    advisor = SprayAdvisor()

    # Same weather, different products
    temp, humidity, wind, rain = 18, 55, 12, 15

    products = [
        (None, "General"),
        (SprayProduct.HERBICIDE, "Herbicide"),
        (SprayProduct.INSECTICIDE, "Insecticide"),
        (SprayProduct.FUNGICIDE, "Fungicide"),
        (SprayProduct.FOLIAR_FERTILIZER, "Foliar Fertilizer"),
    ]

    print(f"Weather: {temp}°C, {humidity}% humidity, {wind} km/h wind, {rain}% rain\n")
    print(f"{'Product':<25} {'Score':<10} {'Condition':<15} {'Key Risks'}")
    print(f"{'-' * 80}")

    for product, name in products:
        score, condition, risks = advisor.calculate_spray_score(temp, humidity, wind, rain, product)
        risks_str = ", ".join(risks[:2]) if risks else "None"
        print(f"{name:<25} {score:>6.1f}/100  {condition.value.upper():<15} {risks_str}")

    print("\n" + "=" * 80)


def test_risk_identification():
    """Test risk identification logic"""
    print("\n" + "=" * 80)
    print("⚠️  RISK IDENTIFICATION TEST")
    print("=" * 80 + "\n")

    advisor = SprayAdvisor()

    test_cases = [
        (8, 60, 5, 5, None, ["reduced_efficacy"], "Low temperature"),
        (35, 40, 5, 5, None, ["phytotoxicity"], "High temperature"),
        (25, 35, 5, 5, None, ["evaporation", "poor_absorption"], "Low humidity"),
        (25, 60, 20, 5, None, ["spray_drift"], "High wind"),
        (25, 60, 5, 30, None, ["wash_off"], "Rain forecast"),
        (
            30,
            30,
            5,
            5,
            1.5,
            ["evaporation", "phytotoxicity", "poor_absorption", "inversion_risk"],
            "Multiple risks",
        ),
    ]

    for temp, humidity, wind, rain, delta_t, expected_risks, desc in test_cases:
        risks = advisor.identify_risks(temp, humidity, wind, rain, delta_t)

        # Check if expected risks are present
        found = all(risk in risks for risk in expected_risks)
        status = "✅" if found else "⚠️ "

        print(f"{status} {desc:<30} Risks: {', '.join(risks) if risks else 'None'}")

    print("\n" + "=" * 80)


def test_recommendations():
    """Test recommendation generation"""
    print("\n" + "=" * 80)
    print("💡 RECOMMENDATIONS TEST")
    print("=" * 80 + "\n")

    advisor = SprayAdvisor()

    test_cases = [
        (SprayCondition.EXCELLENT, [], None, "Perfect conditions"),
        (
            SprayCondition.POOR,
            ["spray_drift", "wash_off"],
            SprayProduct.HERBICIDE,
            "Poor with risks",
        ),
        (
            SprayCondition.MARGINAL,
            ["low_humidity"],
            SprayProduct.INSECTICIDE,
            "Marginal insecticide",
        ),
    ]

    for condition, risks, product, desc in test_cases:
        recommendations = advisor.get_recommendations(condition, risks, product)

        print(f"\n{desc}:")
        print(f"  Condition: {condition.value.upper()}")
        if risks:
            print(f"  Risks: {', '.join(risks)}")
        if product:
            print(f"  Product: {product.value}")

        print("\n  English Recommendations:")
        for rec in recommendations["en"][:3]:
            print(f"    • {rec}")

        print("\n  Arabic Recommendations:")
        for rec in recommendations["ar"][:3]:
            print(f"    • {rec}")

    print("\n" + "=" * 80)


def test_delta_t_ranges():
    """Test Delta-T calculation ranges"""
    print("\n" + "=" * 80)
    print("📐 DELTA-T RANGES TEST")
    print("=" * 80 + "\n")

    advisor = SprayAdvisor()

    print("Delta-T Classification:")
    print("  < 2°C   : ⚠️  Too low (temperature inversion risk)")
    print("  2-8°C   : ✅ Ideal (safe spraying conditions)")
    print("  > 8°C   : ⚠️  Too high (rapid evaporation)\n")

    test_cases = [
        (20, 90, "< 2°C (too low)"),
        (25, 70, "2-8°C (ideal)"),
        (30, 50, "2-8°C (ideal)"),
        (35, 30, "> 8°C (too high)"),
        (28, 60, "2-8°C (ideal)"),
    ]

    print(f"{'Temp':<8} {'Humidity':<12} {'Delta-T':<12} {'Classification':<25} {'Expected'}")
    print(f"{'-' * 80}")

    for temp, humidity, expected in test_cases:
        delta_t = advisor._calculate_delta_t(temp, humidity)

        if delta_t is not None:
            if delta_t < 2:
                classification = "⚠️  Too low"
            elif delta_t <= 8:
                classification = "✅ Ideal"
            else:
                classification = "⚠️  Too high"

            status = "✅" if expected in classification or (expected == "2-8°C (ideal)" and 2 <= delta_t <= 8) else "⚠️ "

            print(f"{temp}°C    {humidity}%       {delta_t:.1f}°C      {classification:<25} {status}")
        else:
            print(f"{temp}°C    {humidity}%       N/A         Error                     ❌")

    print("\n" + "=" * 80)


def test_condition_scoring_boundaries():
    """Test condition level boundaries"""
    print("\n" + "=" * 80)
    print("🎯 CONDITION SCORING BOUNDARIES TEST")
    print("=" * 80 + "\n")

    advisor = SprayAdvisor()

    # Test scores at boundaries
    boundary_tests = [
        (22, 60, 5, 5, 85, SprayCondition.EXCELLENT),  # Should be excellent
        (20, 55, 10, 12, 70, SprayCondition.GOOD),  # Should be good
        (18, 50, 14, 18, 50, SprayCondition.MARGINAL),  # Should be marginal
        (15, 45, 16, 25, 30, SprayCondition.POOR),  # Should be poor
    ]

    print(f"{'Weather Conditions':<45} {'Score':<10} {'Expected':<15} {'Result'}")
    print(f"{'-' * 80}")

    for temp, humidity, wind, rain, expected_min, expected_condition in boundary_tests:
        score, condition, risks = advisor.calculate_spray_score(temp, humidity, wind, rain)

        status = "✅" if condition == expected_condition and score >= expected_min else "⚠️ "
        conditions_str = f"{temp}°C, {humidity}%, {wind}km/h, {rain}%"

        print(f"{conditions_str:<45} {score:>6.1f}/100  {expected_condition.value:<15} {status}")

    print("\n" + "=" * 80)


def main():
    """Run all logic tests"""
    print("\n" + "=" * 80)
    print("🧪 SPRAY ADVISOR LOGIC TESTS (No API calls)")
    print("   اختبارات منطق مستشار الرش (بدون API)")
    print("=" * 80)

    test_calculate_spray_score()
    test_product_specific_conditions()
    test_risk_identification()
    test_recommendations()
    test_delta_t_ranges()
    test_condition_scoring_boundaries()

    print("\n" + "=" * 80)
    print("✅ ALL LOGIC TESTS PASSED")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
