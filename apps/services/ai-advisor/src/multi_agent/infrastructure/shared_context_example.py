"""
Example Usage of Shared Context Store
مثال على استخدام مخزن السياق المشترك

This file demonstrates how to use the SharedContextStore for multi-agent collaboration.
يوضح هذا الملف كيفية استخدام SharedContextStore للتعاون متعدد الوكلاء.
"""

from datetime import datetime, timedelta
from shared_context import (
    FarmContext,
    SharedContextStore,
    SoilAnalysis,
    WeatherData,
    SatelliteIndices,
    FarmAction,
    Issue,
    get_shared_context_store,
)


def example_create_context():
    """
    Example: Create and store farm context
    مثال: إنشاء وتخزين سياق المزرعة
    """
    print("=== Creating Farm Context ===")
    print("=== إنشاء سياق المزرعة ===\n")

    # Create soil analysis data | إنشاء بيانات تحليل التربة
    soil_data = SoilAnalysis(
        ph=6.8,
        nitrogen=45.0,
        phosphorus=20.0,
        potassium=150.0,
        organic_matter=3.5,
        texture="loamy",
        moisture=25.0,
        ec=1.2,
        analysis_date="2025-12-20"
    )

    # Create weather data | إنشاء بيانات الطقس
    weather_data = WeatherData(
        temperature=28.5,
        humidity=65.0,
        precipitation=2.5,
        wind_speed=12.0,
        wind_direction="NW",
        conditions="partly_cloudy",
        forecast_days=7,
        daily_forecasts=[
            {"date": "2025-12-30", "temp_max": 32, "temp_min": 18, "rain": 0},
            {"date": "2025-12-31", "temp_max": 30, "temp_min": 17, "rain": 5},
        ]
    )

    # Create satellite indices | إنشاء مؤشرات الأقمار الصناعية
    satellite_indices = SatelliteIndices(
        ndvi=0.75,
        ndwi=0.35,
        evi=0.68,
        savi=0.72,
        ndmi=0.42,
        capture_date="2025-12-28",
        cloud_coverage=10.0
    )

    # Create farm actions | إنشاء عمليات المزرعة
    recent_actions = [
        FarmAction(
            action_id="ACT001",
            action_type="fertilization",
            date="2025-12-15",
            description="Applied NPK fertilizer",
            products_used=["NPK 20-10-10"],
            quantity=50.0,
            unit="kg",
            cost=250.0,
            notes="Applied to entire field"
        ),
        FarmAction(
            action_id="ACT002",
            action_type="irrigation",
            date="2025-12-25",
            description="Drip irrigation",
            quantity=500.0,
            unit="m3",
            cost=100.0
        ),
    ]

    # Create active issues | إنشاء المشاكل النشطة
    active_issues = [
        Issue(
            issue_id="ISS001",
            issue_type="disease",
            severity="medium",
            description="Early signs of powdery mildew on leaves",
            detected_date="2025-12-27",
            affected_area=5.0,
            status="active"
        ),
    ]

    # Create farm context | إنشاء سياق المزرعة
    context = FarmContext(
        farm_id="FARM001",
        field_id="FLD001",
        tenant_id="TENANT001",
        crop_type="tomato",
        growth_stage="flowering",
        planting_date="2025-10-15",
        soil_data=soil_data,
        weather_data=weather_data,
        satellite_indices=satellite_indices,
        recent_actions=recent_actions,
        active_issues=active_issues,
    )

    # Store context | تخزين السياق
    store = get_shared_context_store()
    success = store.set_context("FLD001", context)

    if success:
        print(f"✓ Context stored successfully for field FLD001")
        print(f"✓ تم تخزين السياق بنجاح للحقل FLD001\n")
    else:
        print(f"✗ Failed to store context")
        print(f"✗ فشل تخزين السياق\n")

    return context


def example_retrieve_context():
    """
    Example: Retrieve stored context
    مثال: استرجاع السياق المخزن
    """
    print("=== Retrieving Farm Context ===")
    print("=== استرجاع سياق المزرعة ===\n")

    store = get_shared_context_store()
    context = store.get_context("FLD001")

    if context:
        print(f"✓ Context retrieved successfully")
        print(f"✓ تم استرجاع السياق بنجاح\n")
        print(f"  Farm ID: {context.farm_id}")
        print(f"  Field ID: {context.field_id}")
        print(f"  Crop: {context.crop_type}")
        print(f"  Growth Stage: {context.growth_stage}")
        print(f"  Soil pH: {context.soil_data.ph if context.soil_data else 'N/A'}")
        print(f"  NDVI: {context.satellite_indices.ndvi if context.satellite_indices else 'N/A'}")
        print(f"  Active Issues: {len(context.active_issues)}")
        print(f"  Recent Actions: {len(context.recent_actions)}\n")
    else:
        print(f"✗ Context not found")
        print(f"✗ لم يتم العثور على السياق\n")

    return context


def example_add_agent_opinions():
    """
    Example: Add opinions from multiple agents
    مثال: إضافة آراء من وكلاء متعددين
    """
    print("=== Adding Agent Opinions ===")
    print("=== إضافة آراء الوكلاء ===\n")

    store = get_shared_context_store()

    # Disease Expert Opinion | رأي خبير الأمراض
    disease_opinion = {
        "diagnosis": "Powdery Mildew (Erysiphe spp.)",
        "confidence": 0.85,
        "severity": "medium",
        "recommendation": "Apply sulfur-based fungicide immediately",
        "reasoning": "White powdery spots on leaves, favorable humid conditions",
        "priority": "high"
    }
    store.add_agent_opinion("FLD001", "disease_expert", disease_opinion)
    print("✓ Disease expert opinion added")
    print("✓ تمت إضافة رأي خبير الأمراض\n")

    # Irrigation Advisor Opinion | رأي مستشار الري
    irrigation_opinion = {
        "current_status": "adequate",
        "recommendation": "Maintain current irrigation schedule",
        "next_irrigation": "2025-12-30",
        "estimated_water_need": "450 m3",
        "reasoning": "Soil moisture at 25%, weather forecast shows no rain for 3 days",
        "priority": "medium"
    }
    store.add_agent_opinion("FLD001", "irrigation_advisor", irrigation_opinion)
    print("✓ Irrigation advisor opinion added")
    print("✓ تمت إضافة رأي مستشار الري\n")

    # Field Analyst Opinion | رأي محلل الحقل
    field_opinion = {
        "overall_health": "good",
        "ndvi_trend": "stable",
        "areas_of_concern": ["Northeast corner showing lower NDVI"],
        "recommendation": "Focus disease treatment on affected area",
        "confidence": 0.78,
        "priority": "medium"
    }
    store.add_agent_opinion("FLD001", "field_analyst", field_opinion)
    print("✓ Field analyst opinion added")
    print("✓ تمت إضافة رأي محلل الحقل\n")


def example_get_all_opinions():
    """
    Example: Retrieve all agent opinions
    مثال: استرجاع جميع آراء الوكلاء
    """
    print("=== Retrieving All Agent Opinions ===")
    print("=== استرجاع جميع آراء الوكلاء ===\n")

    store = get_shared_context_store()
    opinions = store.get_all_opinions("FLD001")

    print(f"Found {len(opinions)} agent opinions:")
    print(f"وجد {len(opinions)} آراء الوكلاء:\n")

    for agent_id, opinion in opinions.items():
        print(f"Agent: {agent_id}")
        print(f"الوكيل: {agent_id}")
        print(f"  Timestamp: {opinion.get('timestamp', 'N/A')}")
        print(f"  Priority: {opinion.get('priority', 'N/A')}")
        print(f"  Recommendation: {opinion.get('recommendation', 'N/A')}")
        print()


def example_update_context():
    """
    Example: Update specific fields in context
    مثال: تحديث حقول محددة في السياق
    """
    print("=== Updating Context ===")
    print("=== تحديث السياق ===\n")

    store = get_shared_context_store()

    # Update growth stage | تحديث مرحلة النمو
    updates = {
        "growth_stage": "fruiting",
    }

    success = store.update_context("FLD001", updates)

    if success:
        print("✓ Context updated successfully")
        print("✓ تم تحديث السياق بنجاح\n")

        # Verify update | التحقق من التحديث
        context = store.get_context("FLD001")
        print(f"  New growth stage: {context.growth_stage}\n")
    else:
        print("✗ Failed to update context")
        print("✗ فشل تحديث السياق\n")


def example_health_check():
    """
    Example: Check store health
    مثال: فحص صحة المخزن
    """
    print("=== Health Check ===")
    print("=== فحص الصحة ===\n")

    store = get_shared_context_store()
    health = store.health_check()

    print(f"Status: {health['status']}")
    print(f"الحالة: {health['status']}")
    print(f"Redis Connected: {health['redis_connected']}")
    print(f"اتصال Redis: {health['redis_connected']}")
    print(f"TTL: {health.get('ttl', 'N/A')} seconds")
    print(f"Key Prefix: {health.get('key_prefix', 'N/A')}\n")


def example_clear_opinions():
    """
    Example: Clear agent opinions after decision is made
    مثال: مسح آراء الوكلاء بعد اتخاذ القرار
    """
    print("=== Clearing Agent Opinions ===")
    print("=== مسح آراء الوكلاء ===\n")

    store = get_shared_context_store()
    success = store.clear_opinions("FLD001")

    if success:
        print("✓ Agent opinions cleared successfully")
        print("✓ تم مسح آراء الوكلاء بنجاح\n")

        # Verify | التحقق
        opinions = store.get_all_opinions("FLD001")
        print(f"  Remaining opinions: {len(opinions)}\n")
    else:
        print("✗ Failed to clear opinions")
        print("✗ فشل مسح الآراء\n")


def main():
    """
    Run all examples
    تشغيل جميع الأمثلة
    """
    print("\n" + "="*70)
    print("Shared Context Store Examples")
    print("أمثلة مخزن السياق المشترك")
    print("="*70 + "\n")

    try:
        # 1. Create and store context | إنشاء وتخزين السياق
        example_create_context()

        # 2. Retrieve context | استرجاع السياق
        example_retrieve_context()

        # 3. Add agent opinions | إضافة آراء الوكلاء
        example_add_agent_opinions()

        # 4. Get all opinions | الحصول على جميع الآراء
        example_get_all_opinions()

        # 5. Update context | تحديث السياق
        example_update_context()

        # 6. Health check | فحص الصحة
        example_health_check()

        # 7. Clear opinions | مسح الآراء
        example_clear_opinions()

        print("="*70)
        print("✓ All examples completed successfully!")
        print("✓ تم إكمال جميع الأمثلة بنجاح!")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        print(f"✗ خطأ في تشغيل الأمثلة: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
