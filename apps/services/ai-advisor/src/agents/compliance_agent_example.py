"""
ComplianceAgent Usage Examples
أمثلة استخدام وكيل الامتثال

Example usage of the ComplianceAgent for certification compliance.
أمثلة على استخدام وكيل الامتثال للشهادات.
"""

import asyncio
from datetime import datetime
from compliance_agent import (
    ComplianceAgent,
    CertificationStandard,
    ControlPointCategory,
)


async def example_check_compliance():
    """
    Example: Check if a pesticide application complies with GlobalGAP
    مثال: التحقق من امتثال تطبيق المبيد لمعايير GlobalGAP
    """
    agent = ComplianceAgent()

    # Define the proposed action
    # تحديد الإجراء المقترح
    action = {
        "type": "pesticide_application",
        "description": "Apply synthetic pyrethroid insecticide for aphid control",
        "product": "Cypermethrin 10% EC",
        "target_pest": "Aphids",
        "application_rate": "50ml per 100L water",
    }

    context = {
        "crop": "Tomato",
        "growth_stage": "Flowering",
        "field_size": 2.5,  # hectares
        "location": "Riyadh, Saudi Arabia",
    }

    # Check compliance
    # فحص الامتثال
    result = await agent.check_compliance(
        action=action,
        certification=CertificationStandard.GLOBALGAP_IFA_V6,
        context=context,
    )

    print("Compliance Check Result:")
    print(result)


async def example_validate_organic_input():
    """
    Example: Validate if an input is allowed for organic certification
    مثال: التحقق من صحة المدخل للشهادة العضوية
    """
    agent = ComplianceAgent()

    # Check if neem oil is approved for organic
    # التحقق مما إذا كان زيت النيم معتمداً للزراعة العضوية
    result = await agent.validate_input(
        input_type="pesticide",
        product="Neem oil extract",
        certification=CertificationStandard.ORGANIC_EU,
        additional_info={
            "active_ingredient": "Azadirachtin",
            "concentration": "1%",
            "application_method": "Foliar spray",
        },
    )

    print("Input Validation Result:")
    print(result)


async def example_audit_readiness():
    """
    Example: Assess farm's readiness for GlobalGAP audit
    مثال: تقييم جاهزية المزرعة لتدقيق GlobalGAP
    """
    agent = ComplianceAgent()

    farm_data = {
        "farm_id": "SA-FARM-001",
        "farm_name": "Al Kharj Organic Farm",
        "crops": ["Tomato", "Cucumber", "Lettuce"],
        "size_hectares": 15.5,
        "worker_count": 12,
        "records_available": [
            "Harvest records (2023-2024)",
            "IPM monitoring logs",
            "Worker training records",
            "Water quality tests (2024)",
        ],
        "missing_documents": [
            "Soil analysis reports",
            "Fertilization plan",
            "Waste management procedures",
        ],
        "certifications_held": ["Saudi Organic"],
    }

    # Assess audit readiness
    # تقييم الجاهزية للتدقيق
    result = await agent.audit_readiness(
        farm_id="SA-FARM-001",
        certification=CertificationStandard.GLOBALGAP_IFA_V6,
        farm_data=farm_data,
    )

    print("Audit Readiness Assessment:")
    print(result)


async def example_certification_roadmap():
    """
    Example: Create a roadmap to achieve USDA Organic certification
    مثال: إنشاء خريطة طريق لتحقيق شهادة USDA العضوية
    """
    agent = ComplianceAgent()

    farm_data = {
        "farm_name": "Green Valley Farm",
        "location": "Qassim Region",
        "crops": ["Dates", "Wheat", "Alfalfa"],
        "size_hectares": 50,
        "current_practices": {
            "uses_synthetic_pesticides": True,
            "uses_synthetic_fertilizers": True,
            "last_synthetic_application": "2024-06-15",
            "ipm_implemented": False,
            "record_keeping": "Basic",
        },
        "goals": [
            "Export to US market",
            "Premium pricing",
            "Environmental sustainability",
        ],
    }

    current_practices = {
        "irrigation": "Drip irrigation system",
        "pest_control": "Chemical-based",
        "fertilization": "NPK synthetic fertilizers",
        "soil_management": "Conventional tillage",
    }

    # Get certification roadmap
    # الحصول على خريطة طريق الشهادة
    result = await agent.certification_roadmap(
        farm_data=farm_data,
        target_certification=CertificationStandard.ORGANIC_USDA,
        current_practices=current_practices,
    )

    print("Certification Roadmap:")
    print(result)


async def example_waiting_period():
    """
    Example: Calculate organic conversion waiting period
    مثال: حساب فترة الانتظار للتحول العضوي
    """
    agent = ComplianceAgent()

    # Last application of prohibited substance
    # آخر تطبيق لمادة محظورة
    last_application = datetime(2022, 3, 15)

    result = await agent.calculate_waiting_period(
        product="Synthetic NPK fertilizer (20-20-20)",
        application_date=last_application,
        certification=CertificationStandard.ORGANIC_USDA,
        crop_type="perennial_crops",  # For date palms
    )

    print("Waiting Period Calculation:")
    print(result)


async def example_get_control_points():
    """
    Example: Get GlobalGAP control points for IPM category
    مثال: الحصول على نقاط المراقبة GlobalGAP لفئة الإدارة المتكاملة للآفات
    """
    agent = ComplianceAgent()

    result = await agent.get_control_points(
        certification=CertificationStandard.GLOBALGAP_IFA_V6,
        category=ControlPointCategory.IPM,
    )

    print("IPM Control Points:")
    print(result)


async def example_non_compliance_report():
    """
    Example: Generate non-compliance report
    مثال: إنشاء تقرير عدم الامتثال
    """
    agent = ComplianceAgent()

    issues = [
        {
            "category": "RECORD_KEEPING",
            "control_point": "AF.3.1.1",
            "description": "Records not kept for required 2-year period",
            "evidence": "Harvest records only available for 2024, missing 2023",
            "severity": "major",
        },
        {
            "category": "IPM",
            "control_point": "CB.5.1.1",
            "description": "IPM plan not documented",
            "evidence": "No written IPM plan available",
            "severity": "critical",
        },
        {
            "category": "WORKER_SAFETY",
            "control_point": "WH.2.1.1",
            "description": "Incomplete PPE provision",
            "evidence": "Gloves not provided to all pesticide applicators",
            "severity": "major",
        },
        {
            "category": "HARVEST",
            "control_point": "CB.8.2.1",
            "description": "Harvest containers not properly cleaned",
            "evidence": "Containers have residue from previous use",
            "severity": "minor",
        },
    ]

    result = await agent.non_compliance_report(
        farm_id="SA-FARM-001",
        issues=issues,
        certification=CertificationStandard.GLOBALGAP_IFA_V6,
    )

    print("Non-Compliance Report:")
    print(result)


async def example_compare_certifications():
    """
    Example: Compare multiple certification standards
    مثال: مقارنة معايير شهادات متعددة
    """
    agent = ComplianceAgent()

    farm_context = {
        "target_markets": ["EU", "US", "GCC countries"],
        "crops": ["Tomatoes", "Cucumbers", "Bell Peppers"],
        "production_scale": "Medium (20 hectares)",
        "current_certifications": [],
        "budget": "Moderate",
        "timeline": "12-18 months",
    }

    result = await agent.compare_certifications(
        certifications=[
            CertificationStandard.GLOBALGAP_IFA_V6,
            CertificationStandard.ORGANIC_EU,
            CertificationStandard.SAUDI_GAP,
        ],
        farm_context=farm_context,
    )

    print("Certification Comparison:")
    print(result)


async def main():
    """
    Run all examples
    تشغيل جميع الأمثلة
    """
    print("=" * 80)
    print("SAHOOL Compliance Agent Examples")
    print("أمثلة وكيل الامتثال SAHOOL")
    print("=" * 80)

    print("\n1. Checking Compliance...")
    await example_check_compliance()

    print("\n2. Validating Organic Input...")
    await example_validate_organic_input()

    print("\n3. Assessing Audit Readiness...")
    await example_audit_readiness()

    print("\n4. Creating Certification Roadmap...")
    await example_certification_roadmap()

    print("\n5. Calculating Waiting Period...")
    await example_waiting_period()

    print("\n6. Getting Control Points...")
    await example_get_control_points()

    print("\n7. Generating Non-Compliance Report...")
    await example_non_compliance_report()

    print("\n8. Comparing Certifications...")
    await example_compare_certifications()


if __name__ == "__main__":
    # Run examples
    # تشغيل الأمثلة
    asyncio.run(main())
