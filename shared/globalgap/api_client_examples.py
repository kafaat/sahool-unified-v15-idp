"""
GlobalGAP Supply Chain Portal API Client - Usage Examples
أمثلة استخدام عميل واجهة برمجة بوابة سلسلة التوريد GlobalGAP

Demonstrates various use cases for the GlobalGAP API client.
توضح حالات الاستخدام المختلفة لعميل واجهة برمجة GlobalGAP.

Author: SAHOOL Platform Team
"""

import asyncio
from datetime import datetime
from typing import List

from shared.globalgap import (
    GlobalGAPClient,
    CertificateInfo,
    CertificateStatus,
    Producer,
    CertificateNotFound,
    InvalidGGN,
    GlobalGAPAPIError,
)


# ═══════════════════════════════════════════════════════════════════════════
# Example 1: Basic Certificate Verification
# مثال 1: التحقق الأساسي من الشهادة
# ═══════════════════════════════════════════════════════════════════════════


async def example_verify_certificate():
    """
    Verify a single certificate
    التحقق من شهادة واحدة
    """
    print("\n" + "=" * 80)
    print("Example 1: Verify Certificate / مثال 1: التحقق من الشهادة")
    print("=" * 80)

    # Initialize client in mock mode for testing
    # تهيئة العميل في وضع المحاكاة للاختبار
    async with GlobalGAPClient(
        api_key="demo-api-key",
        mock_mode=True,  # Set to False when using real API
    ) as client:
        try:
            # Verify certificate
            # التحقق من الشهادة
            cert = await client.verify_certificate("4063061891234")

            print(f"\nCertificate Information / معلومات الشهادة:")
            print(f"  GGN: {cert.ggn}")
            print(f"  Status / الحالة: {cert.status.value}")
            print(f"  Producer / المنتج: {cert.producer_name}")
            print(f"  Country / البلد: {cert.country}")
            print(f"  Valid From / صالح من: {cert.valid_from.date()}")
            print(f"  Valid To / صالح حتى: {cert.valid_to.date()}")
            print(f"  Scope / النطاق: {cert.scope}")
            print(f"  CB Name / جهة الشهادة: {cert.cb_name}")
            print(f"  Products / المنتجات: {', '.join(cert.product_categories)}")
            print(f"\n  Is Valid? / هل هي صالحة؟ {cert.is_valid()}")
            print(
                f"  Days Until Expiry / الأيام حتى الانتهاء: {cert.days_until_expiry()}"
            )

        except CertificateNotFound as e:
            print(f"\n❌ Certificate not found / الشهادة غير موجودة")
            print(f"   English: {e.message}")
            print(f"   Arabic: {e.message_ar}")

        except InvalidGGN as e:
            print(f"\n❌ Invalid GGN / رقم GGN غير صالح")
            print(f"   English: {e.message}")
            print(f"   Arabic: {e.message_ar}")

        except GlobalGAPAPIError as e:
            print(f"\n❌ API Error / خطأ في واجهة البرمجة")
            print(f"   English: {e.message}")
            print(f"   Arabic: {e.message_ar}")


# ═══════════════════════════════════════════════════════════════════════════
# Example 2: Quick Status Check
# مثال 2: فحص سريع للحالة
# ═══════════════════════════════════════════════════════════════════════════


async def example_check_status():
    """
    Quick certificate status check
    فحص سريع لحالة الشهادة
    """
    print("\n" + "=" * 80)
    print("Example 2: Quick Status Check / مثال 2: فحص سريع للحالة")
    print("=" * 80)

    async with GlobalGAPClient(mock_mode=True) as client:
        ggn = "4063061891234"

        try:
            status = await client.get_certificate_status(ggn)

            print(f"\nCertificate Status for GGN {ggn}:")

            if status == CertificateStatus.VALID:
                print("  ✅ VALID / صالح")
            elif status == CertificateStatus.EXPIRED:
                print("  ⏰ EXPIRED / منتهي الصلاحية")
            elif status == CertificateStatus.SUSPENDED:
                print("  ⚠️  SUSPENDED / معلق")
            elif status == CertificateStatus.WITHDRAWN:
                print("  ❌ WITHDRAWN / مسحوب")

        except Exception as e:
            print(f"❌ Error: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# Example 3: Search Producers
# مثال 3: البحث عن المنتجين
# ═══════════════════════════════════════════════════════════════════════════


async def example_search_producers():
    """
    Search for certified producers
    البحث عن المنتجين المعتمدين
    """
    print("\n" + "=" * 80)
    print("Example 3: Search Producers / مثال 3: البحث عن المنتجين")
    print("=" * 80)

    async with GlobalGAPClient(mock_mode=True) as client:
        try:
            # Search by query
            # البحث بالاستعلام
            producers = await client.search_producers(
                query="organic",
                country="SA",  # Saudi Arabia
                limit=10,
            )

            print(
                f"\nFound {len(producers)} producers / تم العثور على {len(producers)} منتج"
            )
            print("-" * 80)

            for i, producer in enumerate(producers, 1):
                print(f"\n{i}. {producer.name}")
                print(f"   Country / البلد: {producer.country}")
                print(f"   Products / المنتجات: {', '.join(producer.products)}")
                print(f"   Status / الحالة: {producer.certification_status.value}")
                if producer.ggn:
                    print(f"   GGN: {producer.ggn}")
                if producer.location:
                    print(f"   Location / الموقع: {producer.location}")

        except GlobalGAPAPIError as e:
            print(f"❌ Search failed / فشل البحث: {e.message}")


# ═══════════════════════════════════════════════════════════════════════════
# Example 4: Batch Certificate Verification
# مثال 4: التحقق من شهادات متعددة
# ═══════════════════════════════════════════════════════════════════════════


async def example_batch_verification():
    """
    Verify multiple certificates at once
    التحقق من شهادات متعددة في وقت واحد
    """
    print("\n" + "=" * 80)
    print("Example 4: Batch Verification / مثال 4: التحقق المجمع")
    print("=" * 80)

    async with GlobalGAPClient(mock_mode=True) as client:
        # List of GGNs to verify
        # قائمة أرقام GGN للتحقق منها
        ggns = [
            "4063061891234",
            "4063061891235",
            "4063061891236",
            "4063061891237",
        ]

        print(f"\nVerifying {len(ggns)} certificates...")
        print(f"التحقق من {len(ggns)} شهادة...")

        results = await client.batch_verify_certificates(ggns)

        print(f"\nSuccessfully verified {len(results)} out of {len(ggns)} certificates")
        print(f"تم التحقق بنجاح من {len(results)} من أصل {len(ggns)} شهادة")
        print("-" * 80)

        for ggn, cert in results.items():
            status_icon = "✅" if cert.is_valid() else "❌"
            print(f"{status_icon} {ggn}: {cert.status.value} - {cert.producer_name}")


# ═══════════════════════════════════════════════════════════════════════════
# Example 5: Certificate Expiry Monitoring
# مثال 5: مراقبة انتهاء صلاحية الشهادات
# ═══════════════════════════════════════════════════════════════════════════


async def example_expiry_monitoring():
    """
    Monitor certificate expiry dates
    مراقبة تواريخ انتهاء صلاحية الشهادات
    """
    print("\n" + "=" * 80)
    print("Example 5: Expiry Monitoring / مثال 5: مراقبة انتهاء الصلاحية")
    print("=" * 80)

    async with GlobalGAPClient(mock_mode=True) as client:
        ggns = ["4063061891234", "4063061891235", "4063061891236"]

        print("\nCertificate Expiry Report / تقرير انتهاء صلاحية الشهادات")
        print("-" * 80)

        results = await client.batch_verify_certificates(ggns)

        # Categorize by expiry status
        # التصنيف حسب حالة الانتهاء
        expiring_soon = []  # < 30 days
        valid = []  # > 30 days
        expired = []

        for ggn, cert in results.items():
            days_left = cert.days_until_expiry()

            if days_left < 0:
                expired.append((ggn, cert, days_left))
            elif days_left <= 30:
                expiring_soon.append((ggn, cert, days_left))
            else:
                valid.append((ggn, cert, days_left))

        # Report expired
        # تقرير منتهية الصلاحية
        if expired:
            print(f"\n❌ EXPIRED ({len(expired)}) / منتهية الصلاحية")
            for ggn, cert, days in expired:
                print(f"   {ggn}: {cert.producer_name} - Expired {abs(days)} days ago")

        # Report expiring soon
        # تقرير على وشك الانتهاء
        if expiring_soon:
            print(f"\n⚠️  EXPIRING SOON ({len(expiring_soon)}) / على وشك الانتهاء")
            for ggn, cert, days in expiring_soon:
                print(f"   {ggn}: {cert.producer_name} - {days} days left")

        # Report valid
        # تقرير صالحة
        if valid:
            print(f"\n✅ VALID ({len(valid)}) / صالحة")
            for ggn, cert, days in valid:
                print(f"   {ggn}: {cert.producer_name} - {days} days left")


# ═══════════════════════════════════════════════════════════════════════════
# Example 6: Integration with SAHOOL Platform
# مثال 6: التكامل مع منصة SAHOOL
# ═══════════════════════════════════════════════════════════════════════════


async def example_sahool_integration():
    """
    Example integration with SAHOOL farm management
    مثال التكامل مع إدارة المزارع SAHOOL
    """
    print("\n" + "=" * 80)
    print("Example 6: SAHOOL Integration / مثال 6: التكامل مع SAHOOL")
    print("=" * 80)

    async with GlobalGAPClient(mock_mode=True) as client:
        # Simulate farm data from SAHOOL database
        # محاكاة بيانات المزرعة من قاعدة بيانات SAHOOL
        farm = {
            "id": "farm-12345",
            "name": "مزرعة الخير الزراعية",
            "name_en": "Al-Khair Agricultural Farm",
            "ggn": "4063061891234",
            "owner": "Ahmed Al-Saud",
        }

        print(f"\nValidating GlobalGAP certificate for farm: {farm['name_en']}")
        print(f"التحقق من شهادة GlobalGAP للمزرعة: {farm['name']}")

        try:
            # Verify the farm's certificate
            # التحقق من شهادة المزرعة
            cert = await client.verify_certificate(farm["ggn"])

            # Check if certificate is valid
            # التحقق من صحة الشهادة
            if cert.is_valid():
                print(f"\n✅ Certificate is VALID / الشهادة صالحة")
                print(f"   Valid until / صالحة حتى: {cert.valid_to.date()}")
                print(
                    f"   Days remaining / الأيام المتبقية: {cert.days_until_expiry()}"
                )

                # Update farm record in database
                # تحديث سجل المزرعة في قاعدة البيانات
                print(f"\n📝 Updating farm record...")
                farm_update = {
                    "globalgap_status": "VALID",
                    "globalgap_valid_until": cert.valid_to,
                    "globalgap_verified_at": datetime.now(),
                    "certification_body": cert.cb_name,
                    "certified_products": cert.product_categories,
                }
                print(
                    f"   Farm record updated successfully / تم تحديث سجل المزرعة بنجاح"
                )

                # Check expiry warning
                # فحص تحذير الانتهاء
                days_left = cert.days_until_expiry()
                if days_left <= 60:
                    print(f"\n⚠️  WARNING: Certificate expires in {days_left} days")
                    print(f"   تحذير: الشهادة تنتهي في {days_left} يوماً")
                    print(f"   Consider scheduling renewal audit")
                    print(f"   يُنصح بجدولة تدقيق التجديد")

            else:
                print(f"\n❌ Certificate is NOT VALID / الشهادة غير صالحة")
                print(f"   Status / الحالة: {cert.status.value}")

                # Update farm record
                # تحديث سجل المزرعة
                farm_update = {
                    "globalgap_status": cert.status.value.upper(),
                    "globalgap_verified_at": datetime.now(),
                }
                print(f"\n⚠️  Farm certification needs attention")
                print(f"   شهادة المزرعة تحتاج إلى اهتمام")

        except CertificateNotFound:
            print(f"\n❌ Certificate not found in GlobalGAP database")
            print(f"   الشهادة غير موجودة في قاعدة بيانات GlobalGAP")
            print(f"   Farm may not be certified or GGN is incorrect")
            print(f"   قد لا تكون المزرعة معتمدة أو رقم GGN غير صحيح")

        except InvalidGGN:
            print(f"\n❌ Invalid GGN format: {farm['ggn']}")
            print(f"   تنسيق GGN غير صالح: {farm['ggn']}")
            print(f"   Please verify the GGN number")
            print(f"   يرجى التحقق من رقم GGN")


# ═══════════════════════════════════════════════════════════════════════════
# Example 7: Error Handling
# مثال 7: معالجة الأخطاء
# ═══════════════════════════════════════════════════════════════════════════


async def example_error_handling():
    """
    Comprehensive error handling examples
    أمثلة شاملة لمعالجة الأخطاء
    """
    print("\n" + "=" * 80)
    print("Example 7: Error Handling / مثال 7: معالجة الأخطاء")
    print("=" * 80)

    async with GlobalGAPClient(mock_mode=True) as client:
        # Test 1: Invalid GGN format
        # اختبار 1: تنسيق GGN غير صالح
        print("\nTest 1: Invalid GGN format / اختبار 1: تنسيق GGN غير صالح")
        try:
            await client.verify_certificate("123456")  # Invalid
        except InvalidGGN as e:
            print(f"  ✓ Caught InvalidGGN / تم اكتشاف GGN غير صالح")
            print(f"    English: {e.message}")
            print(f"    Arabic: {e.message_ar}")

        # Test 2: Empty GGN
        # اختبار 2: GGN فارغ
        print("\nTest 2: Empty GGN / اختبار 2: GGN فارغ")
        try:
            await client.verify_certificate("")
        except InvalidGGN as e:
            print(f"  ✓ Caught InvalidGGN / تم اكتشاف GGN غير صالح")
            print(f"    English: {e.message}")
            print(f"    Arabic: {e.message_ar}")

        # Test 3: Error dict for API response
        # اختبار 3: قاموس الخطأ لاستجابة واجهة البرمجة
        print("\nTest 3: Error response format / اختبار 3: تنسيق استجابة الخطأ")
        try:
            await client.verify_certificate("invalid")
        except GlobalGAPAPIError as e:
            error_dict_en = e.to_dict(lang="en")
            error_dict_ar = e.to_dict(lang="ar")
            print(f"  English response: {error_dict_en}")
            print(f"  Arabic response: {error_dict_ar}")


# ═══════════════════════════════════════════════════════════════════════════
# Example 8: Using Real API (Production)
# مثال 8: استخدام واجهة البرمجة الحقيقية (الإنتاج)
# ═══════════════════════════════════════════════════════════════════════════


async def example_production_usage():
    """
    Example of using real GlobalGAP API in production
    مثال استخدام واجهة برمجة GlobalGAP الحقيقية في الإنتاج

    NOTE: This requires a valid API key from GlobalGAP
    ملاحظة: يتطلب هذا مفتاح واجهة برمجة صالح من GlobalGAP
    """
    print("\n" + "=" * 80)
    print("Example 8: Production Usage / مثال 8: الاستخدام في الإنتاج")
    print("=" * 80)

    print("\nTo use the real GlobalGAP API:")
    print("لاستخدام واجهة برمجة GlobalGAP الحقيقية:")
    print("\n1. Obtain API key from GlobalGAP")
    print("   احصل على مفتاح واجهة البرمجة من GlobalGAP")
    print("\n2. Set environment variable:")
    print("   export GLOBALGAP_API_KEY='your-api-key'")
    print("\n3. Initialize client:")

    print(
        """
    import os

    api_key = os.getenv("GLOBALGAP_API_KEY")

    async with GlobalGAPClient(
        api_key=api_key,
        base_url="https://www.globalgap.org/api/v1",
        mock_mode=False,  # Use real API
        timeout=30,
        max_retries=3,
        rate_limit=10,  # 10 requests per minute
        rate_limit_period=60,
    ) as client:
        cert = await client.verify_certificate("4063061891234")
        print(f"Status: {cert.status}")
    """
    )


# ═══════════════════════════════════════════════════════════════════════════
# Main Execution
# التنفيذ الرئيسي
# ═══════════════════════════════════════════════════════════════════════════


async def main():
    """Run all examples / تشغيل جميع الأمثلة"""
    print("\n" + "=" * 80)
    print("GlobalGAP Supply Chain Portal API Client - Examples")
    print("عميل واجهة برمجة بوابة سلسلة التوريد GlobalGAP - أمثلة")
    print("=" * 80)

    # Run examples
    # تشغيل الأمثلة
    await example_verify_certificate()
    await example_check_status()
    await example_search_producers()
    await example_batch_verification()
    await example_expiry_monitoring()
    await example_sahool_integration()
    await example_error_handling()
    await example_production_usage()

    print("\n" + "=" * 80)
    print("All examples completed! / اكتملت جميع الأمثلة!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    # Run the examples
    # تشغيل الأمثلة
    asyncio.run(main())
