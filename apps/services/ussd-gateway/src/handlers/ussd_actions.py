"""
USSD Action Handlers - معالجات إجراءات USSD
Implementations for all USSD menu actions
"""

from datetime import datetime, timedelta
from typing import Any

from fastapi import FastAPI


async def weather_today(app: FastAPI, phone_number: str, language: str) -> str:
    """Get today's weather"""
    # In production, fetch from weather-service
    if language == "ar":
        return """🌤️ طقس اليوم - الرياض

الحرارة: 18°-28° م
الرطوبة: 35%
الرياح: شمالية غربية 15 كم/س
الحالة: صافي

✅ ظروف مناسبة للرش
⚠️ تجنب الري في الظهيرة"""
    return """🌤️ Today's Weather - Riyadh

Temperature: 18°-28° C
Humidity: 35%
Wind: NW 15 km/h
Condition: Clear

✅ Good spraying conditions
⚠️ Avoid midday irrigation"""


async def weather_3day(app: FastAPI, phone_number: str, language: str) -> str:
    """Get 3-day forecast"""
    today = datetime.now()
    if language == "ar":
        return f"""📅 توقعات 3 أيام

{today.strftime("%m/%d")}: ☀️ 18-28° صافي
{(today + timedelta(1)).strftime("%m/%d")}: ⛅ 16-25° غائم جزئي
{(today + timedelta(2)).strftime("%m/%d")}: 🌧️ 14-22° احتمال مطر 60%

💡 نصيحة: أجّل الرش ليوم {(today + timedelta(2)).strftime("%m/%d")}"""
    return f"""📅 3-Day Forecast

{today.strftime("%m/%d")}: ☀️ 18-28° Clear
{(today + timedelta(1)).strftime("%m/%d")}: ⛅ 16-25° Partly cloudy
{(today + timedelta(2)).strftime("%m/%d")}: 🌧️ 14-22° Rain 60%

💡 Tip: Delay spraying until {(today + timedelta(2)).strftime("%m/%d")}"""


async def weather_rain(app: FastAPI, phone_number: str, language: str) -> str:
    """Rain alert subscription"""
    if language == "ar":
        return """🌧️ تنبيهات المطر

✅ تم تفعيل تنبيهات المطر
سنرسل لك إشعار قبل 24 ساعة من أي أمطار متوقعة

للإلغاء: أرسل "الغاء مطر" """
    return """🌧️ Rain Alerts

✅ Rain alerts activated
We'll notify you 24h before expected rain

To cancel: Send "CANCEL RAIN" """


async def field_status(app: FastAPI, phone_number: str, language: str) -> str:
    """Get field status summary"""
    # In production, fetch from field-service
    if language == "ar":
        return """🌾 حالة الحقول

حقل 1 (قمح - 5.2 هـ):
• المرحلة: التفريع
• NDVI: 0.68 (جيد)
• رطوبة التربة: 45%

حقل 2 (شعير - 3.8 هـ):
• المرحلة: السنبلة
• NDVI: 0.65 (جيد)
• رطوبة التربة: 52%

⚠️ حقل 1 يحتاج ري خلال يومين"""
    return """🌾 Field Status

Field 1 (Wheat - 5.2 ha):
• Stage: Tillering
• NDVI: 0.68 (Good)
• Soil moisture: 45%

Field 2 (Barley - 3.8 ha):
• Stage: Heading
• NDVI: 0.65 (Good)
• Soil moisture: 52%

⚠️ Field 1 needs irrigation in 2 days"""


async def field_ndvi(app: FastAPI, phone_number: str, language: str) -> str:
    """Get field NDVI/health status"""
    if language == "ar":
        return """🌿 صحة المحصول (NDVI)

حقل 1: 0.68 ✅ جيد
  ↗️ تحسن 5% عن الأسبوع الماضي

حقل 2: 0.65 ✅ جيد
  → مستقر

حقل 3: 0.52 ⚠️ يحتاج مراجعة
  ↘️ انخفاض 8%
  💡 فحص نقص النيتروجين"""
    return """🌿 Crop Health (NDVI)

Field 1: 0.68 ✅ Good
  ↗️ +5% from last week

Field 2: 0.65 ✅ Good
  → Stable

Field 3: 0.52 ⚠️ Needs attention
  ↘️ -8%
  💡 Check nitrogen deficiency"""


async def field_alerts(app: FastAPI, phone_number: str, language: str) -> str:
    """Get recent field alerts"""
    if language == "ar":
        return """🔔 التنبيهات الأخيرة

1. ⚠️ حقل 3: نقص نيتروجين محتمل
   منذ ساعتين

2. ℹ️ حقل 1: موعد الري غداً
   منذ 5 ساعات

3. ✅ حقل 2: اكتمل الرش بنجاح
   منذ يوم

للتفاصيل أرسل رقم التنبيه"""
    return """🔔 Recent Alerts

1. ⚠️ Field 3: Possible N deficiency
   2 hours ago

2. ℹ️ Field 1: Irrigation due tomorrow
   5 hours ago

3. ✅ Field 2: Spraying completed
   1 day ago

Send alert number for details"""


async def irr_today(app: FastAPI, phone_number: str, language: str) -> str:
    """Get today's irrigation schedule"""
    if language == "ar":
        return """💧 جدول الري - اليوم

الصباح (6:00-8:00):
• حقل 1: 25 مم (مُجدول)

المساء (17:00-19:00):
• حقل 3: 20 مم (موصى)

الإجمالي: 45 مم
تكلفة المياه المقدرة: 180 ريال

للبدء: أرسل "بدء 1" """
    return """💧 Irrigation Schedule - Today

Morning (6:00-8:00):
• Field 1: 25mm (Scheduled)

Evening (17:00-19:00):
• Field 3: 20mm (Recommended)

Total: 45mm
Est. water cost: 180 SAR

To start: Send "START 1" """


async def irr_moisture(app: FastAPI, phone_number: str, language: str) -> str:
    """Get soil moisture readings"""
    if language == "ar":
        return """💦 رطوبة التربة

حقل 1:
• السطح (10سم): 42%
• العمق (30سم): 48%
• الحالة: ⚠️ متوسط

حقل 2:
• السطح: 55%
• العمق: 58%
• الحالة: ✅ جيد

حقل 3:
• السطح: 35%
• العمق: 40%
• الحالة: 🔴 يحتاج ري"""
    return """💦 Soil Moisture

Field 1:
• Surface (10cm): 42%
• Deep (30cm): 48%
• Status: ⚠️ Moderate

Field 2:
• Surface: 55%
• Deep: 58%
• Status: ✅ Good

Field 3:
• Surface: 35%
• Deep: 40%
• Status: 🔴 Needs water"""


async def irr_start(app: FastAPI, phone_number: str, language: str) -> str:
    """Start irrigation"""
    if language == "ar":
        return """💧 بدء الري

اختر الحقل:
1. حقل 1 (قمح) - 25 مم
2. حقل 2 (شعير) - 15 مم
3. حقل 3 (قمح) - 20 مم

أرسل رقم الحقل للتأكيد
مثال: "بدء 1" """
    return """💧 Start Irrigation

Select field:
1. Field 1 (Wheat) - 25mm
2. Field 2 (Barley) - 15mm
3. Field 3 (Wheat) - 20mm

Send field number to confirm
Example: "START 1" """


async def irr_stop(app: FastAPI, phone_number: str, language: str) -> str:
    """Stop irrigation"""
    if language == "ar":
        return """🛑 إيقاف الري

الري النشط حالياً:
• حقل 1: يعمل منذ 45 دقيقة

للإيقاف: أرسل "وقف 1"
للإيقاف الطارئ: أرسل "طوارئ" """
    return """🛑 Stop Irrigation

Currently active:
• Field 1: Running for 45 min

To stop: Send "STOP 1"
Emergency stop: Send "EMERGENCY" """


async def alerts_unread(app: FastAPI, phone_number: str, language: str) -> str:
    """Get unread alerts"""
    if language == "ar":
        return """📬 تنبيهات غير مقروءة (3)

1. 🔴 حرج: اشتباه سرقة معدة
   المعدة: جرار 102
   الموقع: خارج حدود المزرعة
   منذ: 15 دقيقة

2. ⚠️ تحذير: تجاوز PHI
   الحقل: حقل 2
   المبيد: دايميثوات

3. ℹ️ إعلام: تقرير الأسبوع جاهز

أرسل رقم التنبيه للتفاصيل"""
    return """📬 Unread Alerts (3)

1. 🔴 Critical: Equipment theft suspected
   Equipment: Tractor 102
   Location: Outside farm boundary
   Since: 15 minutes

2. ⚠️ Warning: PHI violation
   Field: Field 2
   Pesticide: Dimethoate

3. ℹ️ Info: Weekly report ready

Send alert number for details"""


async def alerts_critical(app: FastAPI, phone_number: str, language: str) -> str:
    """Get critical alerts only"""
    if language == "ar":
        return """🚨 التنبيهات الحرجة

1. اشتباه سرقة - جرار 102
   📍 خارج حدود المزرعة بـ 2.5 كم
   🚗 سرعة: 45 كم/س
   ⏰ منذ 15 دقيقة

   إجراءات فورية:
   • تتبع الموقع: أرسل "تتبع 102"
   • إبلاغ الأمن: 911

لا توجد تنبيهات حرجة أخرى ✅"""
    return """🚨 Critical Alerts

1. Theft Suspected - Tractor 102
   📍 2.5km outside farm boundary
   🚗 Speed: 45 km/h
   ⏰ Since 15 minutes

   Immediate actions:
   • Track location: Send "TRACK 102"
   • Report to security: 911

No other critical alerts ✅"""


async def price_wheat(app: FastAPI, phone_number: str, language: str) -> str:
    """Get wheat prices"""
    if language == "ar":
        return """🌾 أسعار القمح

السعر الحالي: 1,850 ريال/طن
التغير: ↗️ +2.5% هذا الأسبوع

أسعار المناطق:
• الرياض: 1,850 ريال
• جدة: 1,920 ريال
• الدمام: 1,880 ريال

المشترون النشطون: 12
أفضل عرض: 1,870 ريال (الراشد للتجارة)"""
    return """🌾 Wheat Prices

Current: 1,850 SAR/ton
Change: ↗️ +2.5% this week

Regional prices:
• Riyadh: 1,850 SAR
• Jeddah: 1,920 SAR
• Dammam: 1,880 SAR

Active buyers: 12
Best offer: 1,870 SAR (Al-Rashid Trading)"""


async def price_barley(app: FastAPI, phone_number: str, language: str) -> str:
    """Get barley prices"""
    if language == "ar":
        return """🌾 أسعار الشعير

السعر الحالي: 1,200 ريال/طن
التغير: → مستقر

الاستخدامات:
• علف حيواني: 1,200 ريال
• صناعي: 1,350 ريال

💡 نصيحة: الطلب مرتفع للعلف"""
    return """🌾 Barley Prices

Current: 1,200 SAR/ton
Change: → Stable

Uses:
• Animal feed: 1,200 SAR
• Industrial: 1,350 SAR

💡 Tip: High demand for feed"""


async def price_dates(app: FastAPI, phone_number: str, language: str) -> str:
    """Get dates prices"""
    if language == "ar":
        return """🌴 أسعار التمور

السكري (ممتاز): 35 ريال/كجم
السكري (عادي): 18 ريال/كجم
الخلاص: 28 ريال/كجم
العجوة: 55 ريال/كجم
الصفري: 22 ريال/كجم

التغير الأسبوعي: ↗️ +5%
الموسم: بداية الطلب المرتفع"""
    return """🌴 Dates Prices

Sukkari (Premium): 35 SAR/kg
Sukkari (Regular): 18 SAR/kg
Khalas: 28 SAR/kg
Ajwa: 55 SAR/kg
Safri: 22 SAR/kg

Weekly change: ↗️ +5%
Season: High demand starting"""


async def price_vegetables(app: FastAPI, phone_number: str, language: str) -> str:
    """Get vegetable prices"""
    if language == "ar":
        return """🥬 أسعار الخضروات (الجملة)

طماطم: 3.5 ريال/كجم ↘️
خيار: 2.8 ريال/كجم →
بصل: 1.5 ريال/كجم ↗️
بطاطس: 2.2 ريال/كجم →
كوسة: 3.0 ريال/كجم ↗️
فلفل: 4.5 ريال/كجم ↘️

📍 سوق الخضار المركزي - الرياض
⏰ آخر تحديث: اليوم 6:00 ص"""
    return """🥬 Vegetable Prices (Wholesale)

Tomatoes: 3.5 SAR/kg ↘️
Cucumber: 2.8 SAR/kg →
Onion: 1.5 SAR/kg ↗️
Potato: 2.2 SAR/kg →
Zucchini: 3.0 SAR/kg ↗️
Pepper: 4.5 SAR/kg ↘️

📍 Central Veg Market - Riyadh
⏰ Last update: Today 6:00 AM"""


async def help_usage(app: FastAPI, phone_number: str, language: str) -> str:
    """Help on how to use"""
    if language == "ar":
        return """📖 كيفية استخدام سهول

عبر USSD (*384#):
• اتصل بـ *384#
• اتبع القوائم

عبر SMS:
• طقس - للحصول على الطقس
• حقل - لحالة الحقول
• ري - لجدول الري
• سعر - لأسعار السوق
• مساعدة - للمساعدة

عبر واتساب:
أرسل "مرحبا" إلى +966500000000"""
    return """📖 How to Use SAHOOL

Via USSD (*384#):
• Dial *384#
• Follow menus

Via SMS:
• WEATHER - Get weather
• FIELD - Field status
• WATER - Irrigation
• PRICE - Market prices
• HELP - Get help

Via WhatsApp:
Send "Hi" to +966500000000"""


async def help_contact(app: FastAPI, phone_number: str, language: str) -> str:
    """Contact support"""
    if language == "ar":
        return """📞 تواصل معنا

الدعم الفني:
📱 +966-11-XXX-XXXX
⏰ 8 صباحاً - 10 مساءً

واتساب: +966500000000

البريد: support@sahool.sa

للشكاوى الطارئة:
📱 +966-11-XXX-YYYY (24/7)"""
    return """📞 Contact Us

Technical Support:
📱 +966-11-XXX-XXXX
⏰ 8 AM - 10 PM

WhatsApp: +966500000000

Email: support@sahool.sa

Emergency complaints:
📱 +966-11-XXX-YYYY (24/7)"""


async def help_register(app: FastAPI, phone_number: str, language: str) -> str:
    """Register new farm"""
    if language == "ar":
        return """📝 تسجيل مزرعة جديدة

لتسجيل مزرعتك:

1. أرسل SMS بالتنسيق:
   تسجيل [اسمك] [مساحة المزرعة] [المنطقة]

   مثال:
   تسجيل محمد 50 الرياض

2. سنتصل بك خلال 24 ساعة للتأكيد

أو زر موقعنا:
www.sahool.sa/register"""
    return """📝 Register New Farm

To register your farm:

1. Send SMS in format:
   REGISTER [Name] [Area-ha] [Region]

   Example:
   REGISTER Mohammed 50 Riyadh

2. We'll call within 24h to confirm

Or visit:
www.sahool.sa/register"""


# Action registry
USSD_ACTIONS: dict[str, Any] = {
    # Weather
    "weather_today": weather_today,
    "weather_3day": weather_3day,
    "weather_rain": weather_rain,
    # Fields
    "field_status": field_status,
    "field_ndvi": field_ndvi,
    "field_alerts": field_alerts,
    # Irrigation
    "irr_today": irr_today,
    "irr_moisture": irr_moisture,
    "irr_start": irr_start,
    "irr_stop": irr_stop,
    # Alerts
    "alerts_unread": alerts_unread,
    "alerts_critical": alerts_critical,
    # Prices
    "price_wheat": price_wheat,
    "price_barley": price_barley,
    "price_dates": price_dates,
    "price_vegetables": price_vegetables,
    # Help
    "help_usage": help_usage,
    "help_contact": help_contact,
    "help_register": help_register,
}
