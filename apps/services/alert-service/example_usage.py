"""
SAHOOL Alert Service - Usage Examples
أمثلة على استخدام خدمة التنبيهات مع قاعدة البيانات

هذا الملف يوضح كيفية استخدام repository layer
"""

from datetime import UTC, datetime, timedelta, timezone
from uuid import uuid4

from src import repository
from src.database import SessionLocal
from src.db_models import Alert, AlertRule


def example_create_alert():
    """مثال على إنشاء تنبيه جديد"""
    db = SessionLocal()
    try:
        # إنشاء تنبيه
        alert = Alert(
            id=uuid4(),
            tenant_id=uuid4(),
            field_id="field_12345",
            type="weather",
            severity="high",
            status="active",
            title="تحذير من عاصفة قوية",
            title_en="Severe Storm Warning",
            message="متوقع عاصفة قوية خلال الساعات القادمة. يُنصح باتخاذ الاحتياطات اللازمة.",
            message_en="Severe storm expected in the coming hours. Please take necessary precautions.",
            recommendations=[
                "تأمين المعدات الزراعية",
                "حماية المحاصيل",
                "البقاء في مكان آمن",
            ],
            recommendations_en=[
                "Secure farm equipment",
                "Protect crops",
                "Stay in a safe place",
            ],
            metadata={"wind_speed": 80, "precipitation": "heavy"},
            source_service="weather-service",
            expires_at=datetime.now(UTC) + timedelta(hours=24),
        )

        created_alert = repository.create_alert(db, alert)
        db.commit()

        print(f"✅ تم إنشاء التنبيه: {created_alert.id}")
        print(f"   النوع: {created_alert.type}")
        print(f"   الخطورة: {created_alert.severity}")

        return created_alert.id

    except Exception as e:
        db.rollback()
        print(f"❌ خطأ في إنشاء التنبيه: {e}")
        raise
    finally:
        db.close()


def example_get_alerts_by_field(field_id: str):
    """مثال على جلب تنبيهات حقل معين"""
    db = SessionLocal()
    try:
        alerts, total = repository.get_alerts_by_field(db, field_id=field_id, status="active", skip=0, limit=10)

        print(f"\n📋 تنبيهات الحقل {field_id}:")
        print(f"   إجمالي: {total}")

        for alert in alerts:
            print(f"   - {alert.title} ({alert.severity})")

        return alerts

    finally:
        db.close()


def example_update_alert_status(alert_id, new_status: str):
    """مثال على تحديث حالة تنبيه"""
    db = SessionLocal()
    try:
        updated_alert = repository.update_alert_status(
            db,
            alert_id=alert_id,
            status=new_status,
            user_id="user_123",
            note="تم حل المشكلة" if new_status == "resolved" else None,
        )

        if updated_alert:
            db.commit()
            print(f"✅ تم تحديث التنبيه {alert_id} إلى: {new_status}")
        else:
            print(f"❌ التنبيه {alert_id} غير موجود")

        return updated_alert

    except Exception as e:
        db.rollback()
        print(f"❌ خطأ في تحديث التنبيه: {e}")
        raise
    finally:
        db.close()


def example_get_active_alerts():
    """مثال على جلب التنبيهات النشطة"""
    db = SessionLocal()
    try:
        active_alerts = repository.get_active_alerts(db)

        print(f"\n🔔 التنبيهات النشطة: {len(active_alerts)}")

        for alert in active_alerts:
            print(f"   - [{alert.severity}] {alert.title}")

        return active_alerts

    finally:
        db.close()


def example_create_alert_rule():
    """مثال على إنشاء قاعدة تنبيه"""
    db = SessionLocal()
    try:
        rule = AlertRule(
            id=uuid4(),
            tenant_id=uuid4(),
            field_id="field_12345",
            name="تنبيه انخفاض رطوبة التربة",
            name_en="Low Soil Moisture Alert",
            enabled=True,
            condition={
                "metric": "soil_moisture",
                "operator": "lt",
                "value": 30.0,
                "duration_minutes": 60,
            },
            alert_config={
                "type": "soil_moisture",
                "severity": "medium",
                "title": "انخفاض رطوبة التربة",
                "title_en": "Low Soil Moisture",
                "message_template": "رطوبة التربة منخفضة: {value}%",
            },
            cooldown_hours=12,
        )

        created_rule = repository.create_alert_rule(db, rule)
        db.commit()

        print(f"✅ تم إنشاء القاعدة: {created_rule.id}")
        print(f"   الاسم: {created_rule.name}")
        print(f"   الشرط: {created_rule.condition}")

        return created_rule.id

    except Exception as e:
        db.rollback()
        print(f"❌ خطأ في إنشاء القاعدة: {e}")
        raise
    finally:
        db.close()


def example_get_alert_statistics():
    """مثال على جلب إحصائيات التنبيهات"""
    db = SessionLocal()
    try:
        stats = repository.get_alert_statistics(db, days=30)

        print("\n📊 إحصائيات التنبيهات (آخر 30 يوم):")
        print(f"   إجمالي التنبيهات: {stats['total_alerts']}")
        print(f"   التنبيهات النشطة: {stats['active_alerts']}")
        print(f"   حسب النوع: {stats['by_type']}")
        print(f"   حسب الخطورة: {stats['by_severity']}")
        print(f"   متوسط وقت الحل: {stats['average_resolution_hours']} ساعة")

        return stats

    finally:
        db.close()


def example_get_rules_ready_to_trigger():
    """مثال على جلب القواعد الجاهزة للتفعيل"""
    db = SessionLocal()
    try:
        ready_rules = repository.get_rules_ready_to_trigger(db)

        print(f"\n⚡ القواعد الجاهزة للتفعيل: {len(ready_rules)}")

        for rule in ready_rules:
            print(f"   - {rule.name} (Field: {rule.field_id})")

        return ready_rules

    finally:
        db.close()


def main():
    """تشغيل جميع الأمثلة"""
    print("=" * 60)
    print("SAHOOL Alert Service - أمثلة الاستخدام")
    print("=" * 60)

    try:
        # 1. إنشاء تنبيه
        print("\n1️⃣ إنشاء تنبيه جديد")
        alert_id = example_create_alert()

        # 2. جلب تنبيهات حقل
        print("\n2️⃣ جلب تنبيهات الحقل")
        example_get_alerts_by_field("field_12345")

        # 3. جلب التنبيهات النشطة
        print("\n3️⃣ جلب التنبيهات النشطة")
        example_get_active_alerts()

        # 4. تحديث حالة تنبيه
        print("\n4️⃣ تحديث حالة التنبيه")
        example_update_alert_status(alert_id, "acknowledged")

        # 5. إنشاء قاعدة تنبيه
        print("\n5️⃣ إنشاء قاعدة تنبيه")
        example_create_alert_rule()

        # 6. جلب إحصائيات
        print("\n6️⃣ جلب الإحصائيات")
        example_get_alert_statistics()

        # 7. جلب القواعد الجاهزة
        print("\n7️⃣ القواعد الجاهزة للتفعيل")
        example_get_rules_ready_to_trigger()

        print("\n✅ تم تنفيذ جميع الأمثلة بنجاح!")

    except Exception as e:
        print(f"\n❌ حدث خطأ: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # تأكد من تشغيل migrations أولاً:
    # alembic upgrade head

    # تأكد من ضبط DATABASE_URL:
    # export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/sahool_alerts"

    main()
