"""
Emergency Response Agent Usage Example
مثال استخدام وكيل الاستجابة للطوارئ

This example demonstrates how to use the EmergencyResponseAgent
for various agricultural emergency scenarios.

يوضح هذا المثال كيفية استخدام وكيل الاستجابة للطوارئ
لسيناريوهات الطوارئ الزراعية المختلفة.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any

# Import the Emergency Response Agent
# استيراد وكيل الاستجابة للطوارئ
from src.agents.emergency_response_agent import (
    EmergencyResponseAgent,
    EmergencyType,
    SeverityLevel
)


async def example_drought_emergency():
    """
    Example: Handle drought emergency
    مثال: التعامل مع طوارئ الجفاف
    """
    print("\n" + "="*80)
    print("DROUGHT EMERGENCY EXAMPLE | مثال طوارئ الجفاف")
    print("="*80 + "\n")

    # Initialize agent | تهيئة الوكيل
    agent = EmergencyResponseAgent()

    # Simulate field data during drought | محاكاة بيانات الحقل أثناء الجفاف
    field_data = {
        "field_id": "FIELD-001",
        "location": "Riyadh Region",
        "crop_type": "wheat",
        "growth_stage": "grain_filling",
        "soil_moisture": 12,  # Very low - critical
        "temperature": 42,  # High temperature
        "humidity": 15,  # Low humidity
        "last_irrigation": "7_days_ago",
        "expected_yield_loss": "40-60%"
    }

    # Step 1: Rapid Emergency Assessment | الخطوة 1: التقييم السريع للطوارئ
    print("Step 1: Emergency Assessment...")
    assessment = await agent.assess_emergency(
        emergency_type=EmergencyType.DROUGHT.value,
        field_data=field_data
    )

    print(f"Emergency ID: {assessment['emergency_id']}")
    print(f"Severity: {assessment['severity']}")
    print(f"Response Time: {assessment['response_time_seconds']:.2f} seconds")
    print(f"Alert (EN): {assessment['alert_en']}")
    print(f"Alert (AR): {assessment['alert_ar']}\n")

    # Step 2: Create Response Plan | الخطوة 2: إنشاء خطة الاستجابة
    print("Step 2: Creating Response Plan...")
    response_plan = await agent.create_response_plan(
        emergency_type=EmergencyType.DROUGHT.value,
        assessment=assessment
    )
    print(f"Response plan created at: {response_plan['created_at']}\n")

    # Step 3: Prioritize Actions | الخطوة 3: تحديد أولويات الإجراءات
    print("Step 3: Prioritizing Actions...")
    actions = [
        {"action": "Emergency irrigation", "cost": 5000, "time_hours": 2},
        {"action": "Mulching to reduce evaporation", "cost": 2000, "time_hours": 8},
        {"action": "Adjust irrigation schedule", "cost": 0, "time_hours": 1},
        {"action": "Apply anti-transpirants", "cost": 3000, "time_hours": 4},
    ]
    resources = {
        "budget_sar": 8000,
        "water_m3": 500,
        "labor_hours": 16,
        "equipment": ["drip_irrigation", "sprinklers"]
    }
    prioritized = await agent.prioritize_actions(
        actions=actions,
        resources=resources,
        time_constraint=12  # 12 hours to act
    )
    print("Actions prioritized based on resources and time.\n")

    # Step 4: Coordinate with Other Agents | الخطوة 4: التنسيق مع الوكلاء الآخرين
    print("Step 4: Multi-Agent Coordination...")
    available_agents = [
        "irrigation_advisor",
        "soil_science",
        "yield_predictor",
        "market_intelligence"
    ]
    coordination = await agent.coordinate_response(
        plan=response_plan,
        available_agents=available_agents
    )
    print(f"Coordination strategy created with {len(available_agents)} agents.\n")

    # Step 5: Estimate Damage | الخطوة 5: تقدير الأضرار
    print("Step 5: Damage Estimation...")
    crop_data = {
        "crop": "wheat",
        "area_hectares": 10,
        "growth_stage": "grain_filling",
        "expected_yield_tons": 30,
        "market_price_sar": 1200
    }
    damage = await agent.estimate_damage(
        emergency_type=EmergencyType.DROUGHT.value,
        affected_area=10.0,
        crop_data=crop_data
    )
    print(f"Damage estimated at: {damage['estimated_at']}\n")

    # Step 6: Generate Insurance Documentation | الخطوة 6: إنشاء وثائق التأمين
    print("Step 6: Insurance Documentation...")
    emergency_data = {
        "emergency_id": assessment['emergency_id'],
        "type": EmergencyType.DROUGHT.value,
        "severity": assessment['severity'],
        "field_data": field_data,
        "damage_estimate": damage,
        "response_actions": prioritized
    }
    insurance_docs = await agent.insurance_documentation(
        emergency_data=emergency_data
    )
    print(f"Insurance package generated in {', '.join(insurance_docs['languages'])}\n")

    print("✓ Drought emergency handled successfully!\n")


async def example_flood_emergency():
    """
    Example: Handle flood emergency
    مثال: التعامل مع طوارئ الفيضان
    """
    print("\n" + "="*80)
    print("FLOOD EMERGENCY EXAMPLE | مثال طوارئ الفيضان")
    print("="*80 + "\n")

    agent = EmergencyResponseAgent()

    # Simulate flood field data | محاكاة بيانات حقل الفيضان
    field_data = {
        "field_id": "FIELD-002",
        "location": "Jizan Region",
        "crop_type": "vegetables",
        "growth_stage": "flowering",
        "water_level_cm": 25,  # Critical waterlogging
        "soil_saturation": 95,  # Fully saturated
        "drainage_capacity": "poor",
        "rainfall_24h_mm": 120,
        "flood_duration_hours": 18
    }

    # Quick assessment | تقييم سريع
    assessment = await agent.assess_emergency(
        emergency_type=EmergencyType.FLOOD.value,
        field_data=field_data,
        severity=SeverityLevel.CRITICAL.value
    )

    print(f"Flood Emergency: {assessment['severity']}")
    print(f"Alert (AR): {assessment['alert_ar']}")
    print(f"Response Time: {assessment['response_time_seconds']:.2f}s\n")

    # Monitor recovery | مراقبة التعافي
    print("Initiating recovery monitoring...")
    recovery = await agent.monitor_recovery(
        field_id=field_data["field_id"],
        emergency_type=EmergencyType.FLOOD.value
    )
    print(f"Recovery status monitored at: {recovery['monitored_at']}\n")

    print("✓ Flood emergency assessed and recovery monitoring initiated!\n")


async def example_pest_outbreak():
    """
    Example: Handle severe pest outbreak
    مثال: التعامل مع تفشي الآفات الشديد
    """
    print("\n" + "="*80)
    print("PEST OUTBREAK EMERGENCY | طوارئ تفشي الآفات")
    print("="*80 + "\n")

    agent = EmergencyResponseAgent()

    field_data = {
        "field_id": "FIELD-003",
        "crop_type": "tomatoes",
        "pest_type": "whitefly",
        "infestation_percentage": 75,  # Severe outbreak
        "spread_rate": "rapid",
        "affected_area_hectares": 5,
        "neighboring_fields_affected": True,
        "beneficial_insects_present": False
    }

    # Rapid assessment | تقييم سريع
    assessment = await agent.assess_emergency(
        emergency_type=EmergencyType.PEST_OUTBREAK.value,
        field_data=field_data
    )

    print(f"Pest Outbreak Severity: {assessment['severity']}")
    print(f"Alert (EN): {assessment['alert_en']}\n")

    # Create response plan with multi-agent coordination
    # إنشاء خطة الاستجابة مع التنسيق متعدد الوكلاء
    response_plan = await agent.create_response_plan(
        emergency_type=EmergencyType.PEST_OUTBREAK.value,
        assessment=assessment
    )

    # Coordinate with pest management and other agents
    # التنسيق مع إدارة الآفات والوكلاء الآخرين
    coordination = await agent.coordinate_response(
        plan=response_plan,
        available_agents=["pest_management", "ecological_expert", "disease_expert"]
    )

    print("✓ Pest outbreak emergency coordinated with specialized agents!\n")


async def example_frost_alert():
    """
    Example: Handle frost damage risk
    مثال: التعامل مع خطر أضرار الصقيع
    """
    print("\n" + "="*80)
    print("FROST ALERT EMERGENCY | طوارئ تنبيه الصقيع")
    print("="*80 + "\n")

    agent = EmergencyResponseAgent()

    field_data = {
        "field_id": "FIELD-004",
        "crop_type": "citrus",
        "growth_stage": "flowering",  # Very sensitive stage
        "temperature": 1,  # Near freezing
        "forecast_min_temp": -3,  # Below freezing expected
        "wind_speed": 15,  # Increases frost risk
        "frost_protection": "none",
        "hours_until_frost": 6
    }

    assessment = await agent.assess_emergency(
        emergency_type=EmergencyType.FROST.value,
        field_data=field_data
    )

    print(f"Frost Risk: {assessment['severity']}")
    print(f"Alert (AR): {assessment['alert_ar']}")
    print(f"Time to respond: {field_data['hours_until_frost']} hours\n")

    # Prioritize immediate protective actions
    # تحديد أولويات الإجراءات الوقائية الفورية
    actions = [
        {"action": "Deploy wind machines", "cost": 8000, "time_hours": 2},
        {"action": "Activate sprinkler irrigation", "cost": 3000, "time_hours": 1},
        {"action": "Cover sensitive plants", "cost": 5000, "time_hours": 4},
        {"action": "Deploy smudge pots", "cost": 2000, "time_hours": 2},
    ]

    prioritized = await agent.prioritize_actions(
        actions=actions,
        resources={"budget_sar": 10000, "time_hours": 5},
        time_constraint=6
    )

    print("✓ Frost protection measures prioritized for immediate deployment!\n")


async def example_lessons_learned():
    """
    Example: Post-emergency analysis
    مثال: التحليل بعد الطوارئ
    """
    print("\n" + "="*80)
    print("POST-EMERGENCY ANALYSIS | التحليل بعد الطوارئ")
    print("="*80 + "\n")

    agent = EmergencyResponseAgent()

    # First create an emergency to analyze
    # أولاً إنشاء طوارئ للتحليل
    field_data = {
        "field_id": "FIELD-005",
        "crop_type": "dates",
        "temperature": 48,
        "duration_hours": 72
    }

    assessment = await agent.assess_emergency(
        emergency_type=EmergencyType.HEAT_WAVE.value,
        field_data=field_data
    )

    emergency_id = assessment['emergency_id']
    print(f"Analyzing emergency: {emergency_id}\n")

    # Conduct lessons learned analysis
    # إجراء تحليل الدروس المستفادة
    lessons = await agent.lessons_learned(emergency_id=emergency_id)

    print(f"Analysis Status: {lessons['status']}")
    print(f"Analyzed at: {lessons['analyzed_at']}")
    print("\nLessons learned documented for future emergency preparedness.\n")

    # Check active emergencies
    # التحقق من الطوارئ النشطة
    active = agent.get_active_emergencies()
    print(f"Active emergencies tracked: {len(active)}")

    # Clear the emergency
    # مسح الطوارئ
    cleared = agent.clear_emergency(emergency_id)
    print(f"Emergency {emergency_id} resolved: {cleared}\n")

    print("✓ Post-emergency analysis completed!\n")


async def example_comprehensive_scenario():
    """
    Comprehensive emergency scenario with all features
    سيناريو طوارئ شامل مع جميع الميزات
    """
    print("\n" + "="*80)
    print("COMPREHENSIVE EMERGENCY SCENARIO | سيناريو الطوارئ الشامل")
    print("="*80 + "\n")

    agent = EmergencyResponseAgent()

    # Scenario: Heat wave causing drought stress during critical growth
    # السيناريو: موجة حر تسبب إجهاد الجفاف خلال النمو الحرج
    field_data = {
        "field_id": "FIELD-MAIN",
        "location": "Al-Qassim Region",
        "crop_type": "wheat",
        "area_hectares": 50,
        "growth_stage": "grain_filling",
        "temperature": 46,
        "soil_moisture": 15,
        "humidity": 10,
        "wind_speed": 25,
        "water_availability": "limited",
        "expected_duration_days": 5
    }

    print("SCENARIO: Heat wave with drought stress during grain filling")
    print("السيناريو: موجة حر مع إجهاد الجفاف خلال ملء الحبوب\n")

    # Phase 1: Assessment (< 5 seconds)
    # المرحلة 1: التقييم (< 5 ثوانٍ)
    print("Phase 1: RAPID ASSESSMENT")
    start_time = datetime.now()
    assessment = await agent.assess_emergency(
        emergency_type=EmergencyType.HEAT_WAVE.value,
        field_data=field_data
    )
    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"✓ Assessment completed in {elapsed:.2f}s (Target: <5s)")
    print(f"  Severity: {assessment['severity']}")
    print(f"  Emergency ID: {assessment['emergency_id']}\n")

    # Phase 2: Response Planning
    # المرحلة 2: تخطيط الاستجابة
    print("Phase 2: RESPONSE PLANNING")
    response_plan = await agent.create_response_plan(
        emergency_type=EmergencyType.HEAT_WAVE.value,
        assessment=assessment
    )
    print("✓ Comprehensive action plan created\n")

    # Phase 3: Resource Prioritization
    # المرحلة 3: تحديد أولويات الموارد
    print("Phase 3: RESOURCE PRIORITIZATION")
    actions = [
        {"action": "Emergency cooling irrigation", "cost": 15000, "time_hours": 3},
        {"action": "Deploy shade structures", "cost": 25000, "time_hours": 12},
        {"action": "Apply anti-transpirants", "cost": 8000, "time_hours": 6},
        {"action": "Increase irrigation frequency", "cost": 5000, "time_hours": 2},
        {"action": "Install misting systems", "cost": 20000, "time_hours": 8},
    ]
    resources = {
        "budget_sar": 35000,
        "water_m3": 2000,
        "labor_hours": 24,
        "equipment": ["irrigation_system", "water_tanks"]
    }
    prioritized = await agent.prioritize_actions(
        actions=actions,
        resources=resources,
        time_constraint=24
    )
    print("✓ Actions prioritized within resource constraints\n")

    # Phase 4: Multi-Agent Coordination
    # المرحلة 4: التنسيق متعدد الوكلاء
    print("Phase 4: MULTI-AGENT COORDINATION")
    available_agents = [
        "irrigation_advisor",     # Water management
        "soil_science",          # Soil moisture optimization
        "yield_predictor",       # Impact on yield
        "market_intelligence",   # Economic impact
        "field_analyst"          # Real-time monitoring
    ]
    coordination = await agent.coordinate_response(
        plan=response_plan,
        available_agents=available_agents
    )
    print(f"✓ Coordinated response with {len(available_agents)} specialized agents\n")

    # Phase 5: Damage Estimation
    # المرحلة 5: تقدير الأضرار
    print("Phase 5: DAMAGE ESTIMATION")
    crop_data = {
        "crop": "wheat",
        "area_hectares": 50,
        "growth_stage": "grain_filling",
        "expected_yield_tons": 150,
        "market_price_sar_per_ton": 1200,
        "investment_to_date": 180000
    }
    damage = await agent.estimate_damage(
        emergency_type=EmergencyType.HEAT_WAVE.value,
        affected_area=50.0,
        crop_data=crop_data
    )
    print("✓ Financial and crop damage estimated\n")

    # Phase 6: Insurance Documentation
    # المرحلة 6: توثيق التأمين
    print("Phase 6: INSURANCE DOCUMENTATION")
    emergency_data = {
        "emergency_id": assessment['emergency_id'],
        "type": EmergencyType.HEAT_WAVE.value,
        "severity": assessment['severity'],
        "field_data": field_data,
        "damage_estimate": damage,
        "response_plan": response_plan,
        "actions_taken": prioritized
    }
    insurance_docs = await agent.insurance_documentation(
        emergency_data=emergency_data
    )
    print(f"✓ Insurance package prepared in {', '.join(insurance_docs['languages'])}\n")

    # Phase 7: Recovery Monitoring
    # المرحلة 7: مراقبة التعافي
    print("Phase 7: RECOVERY MONITORING")
    recovery = await agent.monitor_recovery(
        field_id=field_data["field_id"],
        emergency_type=EmergencyType.HEAT_WAVE.value
    )
    print("✓ Recovery monitoring initiated\n")

    # Phase 8: Lessons Learned
    # المرحلة 8: الدروس المستفادة
    print("Phase 8: LESSONS LEARNED")
    lessons = await agent.lessons_learned(
        emergency_id=assessment['emergency_id']
    )
    print("✓ Post-emergency analysis completed\n")

    print("="*80)
    print("COMPREHENSIVE EMERGENCY HANDLED SUCCESSFULLY!")
    print("تم التعامل مع الطوارئ الشاملة بنجاح!")
    print("="*80 + "\n")


async def main():
    """
    Run all emergency response examples
    تشغيل جميع أمثلة الاستجابة للطوارئ
    """
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*15 + "EMERGENCY RESPONSE AGENT EXAMPLES" + " "*30 + "║")
    print("║" + " "*15 + "أمثلة وكيل الاستجابة للطوارئ" + " "*30 + "║")
    print("╚" + "="*78 + "╝")

    try:
        # Run individual emergency examples
        # تشغيل أمثلة الطوارئ الفردية
        await example_drought_emergency()
        await example_flood_emergency()
        await example_pest_outbreak()
        await example_frost_alert()
        await example_lessons_learned()

        # Run comprehensive scenario
        # تشغيل السيناريو الشامل
        await example_comprehensive_scenario()

        print("\n" + "="*80)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("جميع الأمثلة اكتملت بنجاح!")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\nError running examples: {e}")
        print(f"خطأ في تشغيل الأمثلة: {e}\n")


if __name__ == "__main__":
    # Run the examples
    # تشغيل الأمثلة
    asyncio.run(main())
