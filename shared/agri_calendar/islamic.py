"""
Islamic Calendar Utilities - أدوات التقويم الهجري

Islamic (Hijri) calendar integration for agricultural planning.
Provides Hijri-Gregorian conversion and Islamic events affecting agriculture.

Features:
- Hijri to Gregorian conversion (and vice versa)
- Islamic holidays and events
- Agricultural significance of Islamic calendar
- Market and labor impact analysis

Author: SAHOOL Platform Team
Updated: January 2026

Note: This module uses the Umm al-Qura calendar calculation method,
which is the official calendar used in Saudi Arabia.
"""

from __future__ import annotations

import math
from datetime import date, timedelta
from typing import Any

from .models import (
    HijriDate,
    HijriMonth,
    IslamicEvent,
)

# =============================================================================
# Hijri Month Information - معلومات الأشهر الهجرية
# =============================================================================


HIJRI_MONTH_NAMES: dict[int, dict[str, str]] = {
    1: {"ar": "محرم", "en": "Muharram"},
    2: {"ar": "صفر", "en": "Safar"},
    3: {"ar": "ربيع الأول", "en": "Rabi al-Awwal"},
    4: {"ar": "ربيع الثاني", "en": "Rabi al-Thani"},
    5: {"ar": "جمادى الأولى", "en": "Jumada al-Awwal"},
    6: {"ar": "جمادى الثانية", "en": "Jumada al-Thani"},
    7: {"ar": "رجب", "en": "Rajab"},
    8: {"ar": "شعبان", "en": "Shaban"},
    9: {"ar": "رمضان", "en": "Ramadan"},
    10: {"ar": "شوال", "en": "Shawwal"},
    11: {"ar": "ذو القعدة", "en": "Dhu al-Qidah"},
    12: {"ar": "ذو الحجة", "en": "Dhu al-Hijjah"},
}

HIJRI_MONTH_ENUM: dict[int, HijriMonth] = {
    1: HijriMonth.MUHARRAM,
    2: HijriMonth.SAFAR,
    3: HijriMonth.RABI_AL_AWWAL,
    4: HijriMonth.RABI_AL_THANI,
    5: HijriMonth.JUMADA_AL_AWWAL,
    6: HijriMonth.JUMADA_AL_THANI,
    7: HijriMonth.RAJAB,
    8: HijriMonth.SHABAN,
    9: HijriMonth.RAMADAN,
    10: HijriMonth.SHAWWAL,
    11: HijriMonth.DHU_AL_QIDAH,
    12: HijriMonth.DHU_AL_HIJJAH,
}

DAY_NAMES: dict[int, dict[str, str]] = {
    0: {"ar": "السبت", "en": "Saturday"},
    1: {"ar": "الأحد", "en": "Sunday"},
    2: {"ar": "الإثنين", "en": "Monday"},
    3: {"ar": "الثلاثاء", "en": "Tuesday"},
    4: {"ar": "الأربعاء", "en": "Wednesday"},
    5: {"ar": "الخميس", "en": "Thursday"},
    6: {"ar": "الجمعة", "en": "Friday"},
}


# =============================================================================
# Islamic Events Database - قاعدة بيانات الأحداث الإسلامية
# =============================================================================


def _create_islamic_events() -> list[IslamicEvent]:
    """Create database of Islamic events relevant to agriculture"""
    events = []

    # Ramadan - رمضان
    events.append(
        IslamicEvent(
            name_en="Ramadan (Start)",
            name_ar="بداية رمضان",
            description_en="Beginning of the holy month of fasting",
            description_ar="بداية شهر الصيام المبارك",
            hijri_month=HijriMonth.RAMADAN,
            hijri_day=1,
            agricultural_significance_en=(
                "Labor productivity decreases during fasting hours. "
                "Plan heavy agricultural work for early morning or after iftar. "
                "Increased demand for dates and certain vegetables."
            ),
            agricultural_significance_ar=(
                "تنخفض إنتاجية العمال خلال ساعات الصيام. "
                "خطط للأعمال الزراعية الثقيلة في الصباح الباكر أو بعد الإفطار. "
                "زيادة الطلب على التمور وبعض الخضروات."
            ),
            affects_market=True,
            market_impact_en=(
                "High demand for dates, vegetables (especially tomatoes, onions, "
                "cucumbers), and herbs. Prices typically increase 20-40%."
            ),
            market_impact_ar=(
                "طلب عالي على التمور والخضروات (خاصة الطماطم والبصل والخيار) والأعشاب. ترتفع الأسعار عادة 20-40%."
            ),
            affects_labor=True,
            labor_impact_en=(
                "Reduced working hours. Workers prefer early morning shifts. "
                "Heavy machinery operation limited to cooler hours."
            ),
            labor_impact_ar=(
                "ساعات عمل مخفضة. يفضل العمال الورديات الصباحية الباكرة. "
                "تقتصر عمليات الآلات الثقيلة على الساعات الأقل حرارة."
            ),
            duration_days=30,
        )
    )

    # Eid al-Fitr - عيد الفطر
    events.append(
        IslamicEvent(
            name_en="Eid al-Fitr",
            name_ar="عيد الفطر",
            description_en="Festival marking the end of Ramadan",
            description_ar="عيد يحتفل بنهاية رمضان",
            hijri_month=HijriMonth.SHAWWAL,
            hijri_day=1,
            agricultural_significance_en=(
                "Major holiday - no farm work expected. Markets closed for 4-5 days. "
                "Plan harvests before or after the holiday."
            ),
            agricultural_significance_ar=(
                "عطلة كبرى - لا يُتوقع عمل زراعي. الأسواق مغلقة 4-5 أيام. خطط للحصاد قبل أو بعد العطلة."
            ),
            affects_market=True,
            market_impact_en=(
                "Markets closed. Pre-holiday rush for produce. Post-holiday prices may drop due to reduced demand."
            ),
            market_impact_ar=(
                "الأسواق مغلقة. اندفاع قبل العطلة على المنتجات. قد تنخفض الأسعار بعد العطلة بسبب تراجع الطلب."
            ),
            affects_labor=True,
            labor_impact_en="All workers on leave for 4-5 days minimum",
            labor_impact_ar="جميع العمال في إجازة لمدة 4-5 أيام على الأقل",
            duration_days=5,
        )
    )

    # Eid al-Adha - عيد الأضحى
    events.append(
        IslamicEvent(
            name_en="Eid al-Adha",
            name_ar="عيد الأضحى",
            description_en="Festival of Sacrifice",
            description_ar="عيد الأضحى المبارك",
            hijri_month=HijriMonth.DHU_AL_HIJJAH,
            hijri_day=10,
            agricultural_significance_en=(
                "Major holiday - no farm work expected. Markets closed for 5-7 days. "
                "Livestock markets very active before the holiday. "
                "High demand for fodder and animal feed."
            ),
            agricultural_significance_ar=(
                "عطلة كبرى - لا يُتوقع عمل زراعي. الأسواق مغلقة 5-7 أيام. "
                "أسواق الماشية نشطة جداً قبل العطلة. "
                "طلب عالي على الأعلاف."
            ),
            affects_market=True,
            market_impact_en=(
                "Livestock markets peak before Eid. Fodder prices increase. "
                "Fresh produce markets closed during holiday."
            ),
            market_impact_ar=(
                "أسواق الماشية تبلغ ذروتها قبل العيد. ترتفع أسعار الأعلاف. أسواق المنتجات الطازجة مغلقة خلال العطلة."
            ),
            affects_labor=True,
            labor_impact_en="All workers on leave for 5-7 days minimum",
            labor_impact_ar="جميع العمال في إجازة لمدة 5-7 أيام على الأقل",
            duration_days=7,
        )
    )

    # Hajj Season - موسم الحج
    events.append(
        IslamicEvent(
            name_en="Hajj Season",
            name_ar="موسم الحج",
            description_en="Annual Islamic pilgrimage to Makkah",
            description_ar="موسم الحج السنوي إلى مكة",
            hijri_month=HijriMonth.DHU_AL_HIJJAH,
            hijri_day=8,  # Starts 8th, peaks 9th (Arafat)
            agricultural_significance_en=(
                "Major pilgrim influx affects logistics in western Saudi Arabia. "
                "Some workers may be on Hajj leave. "
                "Increased demand for food supplies in Makkah/Madinah region."
            ),
            agricultural_significance_ar=(
                "تدفق الحجاج الكبير يؤثر على اللوجستيات في غرب السعودية. "
                "بعض العمال قد يكونون في إجازة الحج. "
                "زيادة الطلب على المواد الغذائية في منطقة مكة/المدينة."
            ),
            affects_market=True,
            market_impact_en=(
                "High demand in Makkah/Madinah region. Transportation challenges. "
                "Good opportunity for suppliers near holy sites."
            ),
            market_impact_ar=(
                "طلب عالي في منطقة مكة/المدينة. تحديات في النقل. فرصة جيدة للموردين قرب الأماكن المقدسة."
            ),
            affects_labor=True,
            labor_impact_en="Some workers may take Hajj leave (varies by arrangement)",
            labor_impact_ar="بعض العمال قد يأخذون إجازة الحج (حسب الترتيبات)",
            duration_days=6,
        )
    )

    # Islamic New Year - رأس السنة الهجرية
    events.append(
        IslamicEvent(
            name_en="Islamic New Year",
            name_ar="رأس السنة الهجرية",
            description_en="First day of Muharram",
            description_ar="أول يوم من محرم",
            hijri_month=HijriMonth.MUHARRAM,
            hijri_day=1,
            agricultural_significance_en=(
                "Official holiday. Good time for agricultural planning for the new year. "
                "Traditional time to assess previous year's performance."
            ),
            agricultural_significance_ar=(
                "عطلة رسمية. وقت مناسب للتخطيط الزراعي للعام الجديد. وقت تقليدي لتقييم أداء العام السابق."
            ),
            affects_market=True,
            market_impact_en="Markets closed for 1-2 days",
            market_impact_ar="الأسواق مغلقة ليوم أو يومين",
            affects_labor=True,
            labor_impact_en="Public holiday - no work",
            labor_impact_ar="عطلة رسمية - لا عمل",
            duration_days=1,
        )
    )

    # Day of Ashura - يوم عاشوراء
    events.append(
        IslamicEvent(
            name_en="Day of Ashura",
            name_ar="يوم عاشوراء",
            description_en="10th of Muharram",
            description_ar="العاشر من محرم",
            hijri_month=HijriMonth.MUHARRAM,
            hijri_day=10,
            agricultural_significance_en=("Many Muslims fast on this day. Consider reduced productivity."),
            agricultural_significance_ar=("كثير من المسلمين يصومون في هذا اليوم. يُتوقع انخفاض في الإنتاجية."),
            affects_labor=True,
            labor_impact_en="Some workers may fast",
            labor_impact_ar="بعض العمال قد يصومون",
            duration_days=1,
        )
    )

    # Mawlid al-Nabi - المولد النبوي
    events.append(
        IslamicEvent(
            name_en="Mawlid al-Nabi (Prophet's Birthday)",
            name_ar="المولد النبوي الشريف",
            description_en="Prophet Muhammad's birthday",
            description_ar="ذكرى مولد النبي محمد صلى الله عليه وسلم",
            hijri_month=HijriMonth.RABI_AL_AWWAL,
            hijri_day=12,
            agricultural_significance_en=("Holiday in some countries. Check local observance."),
            agricultural_significance_ar=("عطلة في بعض البلدان. تحقق من الاحتفال المحلي."),
            affects_market=False,
            affects_labor=False,
            duration_days=1,
        )
    )

    # Laylat al-Qadr Period - ليالي القدر
    events.append(
        IslamicEvent(
            name_en="Laylat al-Qadr Period (Last 10 days of Ramadan)",
            name_ar="العشر الأواخر من رمضان",
            description_en="Most blessed nights of Ramadan",
            description_ar="أكثر ليالي رمضان بركة",
            hijri_month=HijriMonth.RAMADAN,
            hijri_day=21,  # Starts from 21st
            agricultural_significance_en=(
                "Many workers increase religious observance. Expect minimal availability for night work."
            ),
            agricultural_significance_ar=("كثير من العمال يزيدون من العبادة. توقع الحد الأدنى من التوفر للعمل الليلي."),
            affects_labor=True,
            labor_impact_en="Workers focused on worship, especially at night",
            labor_impact_ar="العمال مركزون على العبادة، خاصة في الليل",
            duration_days=10,
        )
    )

    return events


ISLAMIC_EVENTS: list[IslamicEvent] = _create_islamic_events()


# =============================================================================
# Hijri Calendar Calculations - حسابات التقويم الهجري
# =============================================================================


class HijriCalendar:
    """
    Hijri (Islamic) calendar calculations
    حسابات التقويم الهجري

    Uses the Umm al-Qura calculation method (official in Saudi Arabia).

    Note: Hijri calendar is lunar-based, with months determined by moon sighting.
    This implementation uses astronomical calculations which may differ by 1-2 days
    from actual moon sighting declarations.
    """

    # Julian Day Number for the epoch of the Islamic calendar
    # 1 Muharram 1 AH = July 16, 622 CE (Julian)
    HIJRI_EPOCH = 1948439.5

    def gregorian_to_hijri(self, gregorian_date: date) -> HijriDate:
        """
        Convert Gregorian date to Hijri date
        تحويل التاريخ الميلادي إلى هجري

        Args:
            gregorian_date: Gregorian date to convert

        Returns:
            HijriDate object with converted date
        """
        # Convert Gregorian to Julian Day Number
        jd = self._gregorian_to_jd(gregorian_date)

        # Convert JD to Hijri
        hijri_year, hijri_month, hijri_day = self._jd_to_hijri(jd)

        # Get month and day names
        month_info = HIJRI_MONTH_NAMES.get(hijri_month, {"ar": "", "en": ""})
        month_enum = HIJRI_MONTH_ENUM.get(hijri_month)

        # Get day of week (Saturday = 0 in Islamic week)
        day_of_week = (gregorian_date.weekday() + 2) % 7  # Convert from Monday=0 to Saturday=0
        day_info = DAY_NAMES.get(day_of_week, {"ar": "", "en": ""})

        return HijriDate(
            year=hijri_year,
            month=hijri_month,
            day=hijri_day,
            month_name=month_enum,
            month_name_ar=month_info["ar"],
            month_name_en=month_info["en"],
            day_of_week=day_of_week,
            day_name_ar=day_info["ar"],
            day_name_en=day_info["en"],
            gregorian_date=gregorian_date,
        )

    def hijri_to_gregorian(
        self,
        hijri_year: int,
        hijri_month: int,
        hijri_day: int,
    ) -> date:
        """
        Convert Hijri date to Gregorian date
        تحويل التاريخ الهجري إلى ميلادي

        Args:
            hijri_year: Hijri year
            hijri_month: Hijri month (1-12)
            hijri_day: Hijri day (1-30)

        Returns:
            Gregorian date
        """
        # Convert Hijri to Julian Day Number
        jd = self._hijri_to_jd(hijri_year, hijri_month, hijri_day)

        # Convert JD to Gregorian
        return self._jd_to_gregorian(jd)

    def get_hijri_month_length(self, hijri_year: int, hijri_month: int) -> int:
        """
        Get the length of a Hijri month
        الحصول على طول الشهر الهجري
        """
        # Hijri months alternate between 30 and 29 days
        # Odd months have 30 days, even months have 29 days
        # In leap years, the 12th month has 30 days
        if hijri_month % 2 == 1 or hijri_month == 12 and self._is_hijri_leap_year(hijri_year):
            return 30
        else:
            return 29

    def get_hijri_year_length(self, hijri_year: int) -> int:
        """
        Get the length of a Hijri year
        الحصول على طول السنة الهجرية
        """
        return 355 if self._is_hijri_leap_year(hijri_year) else 354

    def add_hijri_months(
        self,
        hijri_date: HijriDate,
        months: int,
    ) -> HijriDate:
        """
        Add months to a Hijri date
        إضافة أشهر إلى تاريخ هجري
        """
        year = hijri_date.year
        month = hijri_date.month + months
        day = hijri_date.day

        # Handle month overflow
        while month > 12:
            month -= 12
            year += 1
        while month < 1:
            month += 12
            year -= 1

        # Adjust day if necessary
        max_day = self.get_hijri_month_length(year, month)
        day = min(day, max_day)

        # Convert back to verify
        gregorian = self.hijri_to_gregorian(year, month, day)
        return self.gregorian_to_hijri(gregorian)

    def get_current_hijri_date(self) -> HijriDate:
        """
        Get the current Hijri date
        الحصول على التاريخ الهجري الحالي
        """
        return self.gregorian_to_hijri(date.today())

    def format_hijri_date(
        self,
        hijri_date: HijriDate,
        format_type: str = "full",
        language: str = "both",
    ) -> str:
        """
        Format a Hijri date as string
        تنسيق التاريخ الهجري كنص
        """
        if format_type == "short":
            return f"{hijri_date.day}/{hijri_date.month}/{hijri_date.year}"

        if language == "ar":
            return f"{hijri_date.day} {hijri_date.month_name_ar} {hijri_date.year} هـ"
        elif language == "en":
            return f"{hijri_date.day} {hijri_date.month_name_en} {hijri_date.year} AH"
        else:  # both
            return (
                f"{hijri_date.day} {hijri_date.month_name_en} {hijri_date.year} AH / "
                f"{hijri_date.day} {hijri_date.month_name_ar} {hijri_date.year} هـ"
            )

    # =========================================================================
    # Private calculation methods
    # =========================================================================

    def _gregorian_to_jd(self, gregorian_date: date) -> float:
        """Convert Gregorian date to Julian Day Number"""
        year = gregorian_date.year
        month = gregorian_date.month
        day = gregorian_date.day

        if month <= 2:
            year -= 1
            month += 12

        a = math.floor(year / 100)
        b = 2 - a + math.floor(a / 4)

        jd = math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + b - 1524.5
        return jd

    def _jd_to_gregorian(self, jd: float) -> date:
        """Convert Julian Day Number to Gregorian date"""
        z = math.floor(jd + 0.5)
        _ = jd + 0.5 - z  # Fractional day (unused but kept for algorithm clarity)

        if z < 2299161:
            a = z
        else:
            alpha = math.floor((z - 1867216.25) / 36524.25)
            a = z + 1 + alpha - math.floor(alpha / 4)

        b = a + 1524
        c = math.floor((b - 122.1) / 365.25)
        d = math.floor(365.25 * c)
        e = math.floor((b - d) / 30.6001)

        day = b - d - math.floor(30.6001 * e)

        if e < 14:
            month = e - 1
        else:
            month = e - 13

        if month > 2:
            year = c - 4716
        else:
            year = c - 4715

        return date(year, month, day)

    def _hijri_to_jd(self, year: int, month: int, day: int) -> float:
        """Convert Hijri date to Julian Day Number"""
        return (
            day
            + math.ceil(29.5001 * (month - 1))
            + (year - 1) * 354
            + math.floor((3 + 11 * year) / 30)
            + self.HIJRI_EPOCH
            - 1
        )

    def _jd_to_hijri(self, jd: float) -> tuple[int, int, int]:
        """Convert Julian Day Number to Hijri date"""
        jd = math.floor(jd) + 0.5
        year = math.floor((30 * (jd - self.HIJRI_EPOCH) + 10646) / 10631)
        month = min(12, math.ceil((jd - (29 + self._hijri_to_jd(year, 1, 1))) / 29.5) + 1)
        day = int(jd - self._hijri_to_jd(year, month, 1)) + 1

        return year, month, day

    def _is_hijri_leap_year(self, year: int) -> bool:
        """Check if a Hijri year is a leap year"""
        return (14 + 11 * year) % 30 < 11


# =============================================================================
# Islamic Events Manager - مدير الأحداث الإسلامية
# =============================================================================


class IslamicEventsManager:
    """
    Manager for Islamic events relevant to agriculture
    مدير الأحداث الإسلامية ذات الصلة بالزراعة
    """

    def __init__(self):
        """Initialize the events manager"""
        self.calendar = HijriCalendar()
        self.events = ISLAMIC_EVENTS

    def get_all_events(self) -> list[IslamicEvent]:
        """
        Get all Islamic events
        الحصول على جميع الأحداث الإسلامية
        """
        return self.events

    def get_event_gregorian_date(
        self,
        event: IslamicEvent,
        gregorian_year: int,
    ) -> date | None:
        """
        Get the Gregorian date for an Islamic event in a specific year
        الحصول على التاريخ الميلادي لحدث إسلامي في سنة محددة
        """
        if not event.hijri_month or not event.hijri_day:
            return None

        # Get the Hijri year that falls in this Gregorian year
        # Estimate: Hijri year is approximately Gregorian year - 579
        hijri_year_estimate = gregorian_year - 579

        # Try to find the event in this or adjacent Hijri years
        for hijri_year in [hijri_year_estimate, hijri_year_estimate + 1]:
            try:
                # Get month number from HijriMonth enum
                if isinstance(event.hijri_month, HijriMonth):
                    # Find the month number by looking up the enum in the reverse mapping
                    hijri_month_num = None
                    for month_num, month_enum in HIJRI_MONTH_ENUM.items():
                        if month_enum == event.hijri_month:
                            hijri_month_num = month_num
                            break
                    if hijri_month_num is None:
                        continue
                else:
                    hijri_month_num = event.hijri_month

                event_date = self.calendar.hijri_to_gregorian(
                    hijri_year,
                    hijri_month_num,
                    event.hijri_day,
                )
                if event_date.year == gregorian_year:
                    return event_date
            except (ValueError, IndexError):
                continue

        return None

    def get_upcoming_events(
        self,
        days_ahead: int = 90,
        from_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get upcoming Islamic events
        الحصول على الأحداث الإسلامية القادمة
        """
        if from_date is None:
            from_date = date.today()

        end_date = from_date + timedelta(days=days_ahead)
        upcoming = []

        for event in self.events:
            if not event.hijri_month or not event.hijri_day:
                continue

            # Check current and next year
            for year in [from_date.year, from_date.year + 1]:
                event_date = self.get_event_gregorian_date(event, year)
                if event_date is None:
                    continue
                event_end_date = event_date + timedelta(days=event.duration_days - 1)
                # Include events that start within the window OR are still ongoing
                if event_end_date >= from_date and event_date <= end_date:
                    hijri_date = self.calendar.gregorian_to_hijri(event_date)
                    upcoming.append(
                        {
                            "event": event,
                            "gregorian_date": event_date,
                            "hijri_date": hijri_date,
                            "days_until": (event_date - from_date).days,
                        }
                    )

        # Sort by date
        upcoming.sort(key=lambda x: x["gregorian_date"])
        return upcoming

    def get_events_affecting_agriculture(
        self,
        days_ahead: int = 90,
        from_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get events that affect agricultural operations
        الحصول على الأحداث التي تؤثر على العمليات الزراعية
        """
        upcoming = self.get_upcoming_events(days_ahead, from_date)
        return [e for e in upcoming if e["event"].affects_market or e["event"].affects_labor]

    def get_market_impact_calendar(
        self,
        gregorian_year: int,
    ) -> list[dict[str, Any]]:
        """
        Get full year calendar of events with market impact
        الحصول على تقويم السنة للأحداث ذات التأثير على السوق
        """
        calendar = []

        for event in self.events:
            if not event.affects_market:
                continue

            event_date = self.get_event_gregorian_date(event, gregorian_year)
            if event_date:
                hijri_date = self.calendar.gregorian_to_hijri(event_date)
                calendar.append(
                    {
                        "event": event,
                        "gregorian_date": event_date,
                        "hijri_date": hijri_date,
                        "end_date": event_date + timedelta(days=event.duration_days - 1),
                        "market_impact_en": event.market_impact_en,
                        "market_impact_ar": event.market_impact_ar,
                    }
                )

        calendar.sort(key=lambda x: x["gregorian_date"])
        return calendar

    def is_date_during_event(
        self,
        check_date: date,
        event_name_contains: str | None = None,
    ) -> list[IslamicEvent]:
        """
        Check if a date falls during any Islamic event
        التحقق مما إذا كان التاريخ يقع خلال أي حدث إسلامي
        """
        matching_events = []

        for event in self.events:
            if not event.hijri_month or not event.hijri_day:
                continue

            event_start = self.get_event_gregorian_date(event, check_date.year)
            if not event_start:
                continue

            event_end = event_start + timedelta(days=event.duration_days - 1)

            if event_start <= check_date <= event_end:
                if event_name_contains:
                    if event_name_contains.lower() in event.name_en.lower():
                        matching_events.append(event)
                else:
                    matching_events.append(event)

        return matching_events

    def get_labor_advisory(self, check_date: date) -> dict[str, Any]:
        """
        Get labor availability advisory for a date
        الحصول على استشارة توفر العمالة لتاريخ
        """
        events = self.is_date_during_event(check_date)

        if not events:
            return {
                "date": check_date.isoformat(),
                "labor_available": True,
                "advisory_en": "Normal labor availability expected",
                "advisory_ar": "توفر طبيعي للعمالة متوقع",
                "events": [],
            }

        # Find most impactful event
        labor_events = [e for e in events if e.affects_labor]

        if not labor_events:
            return {
                "date": check_date.isoformat(),
                "labor_available": True,
                "advisory_en": "Normal labor availability expected",
                "advisory_ar": "توفر طبيعي للعمالة متوقع",
                "events": [e.name_en for e in events],
            }

        # During major events like Eid
        major_events = ["Eid al-Fitr", "Eid al-Adha"]
        for event in labor_events:
            if any(m in event.name_en for m in major_events):
                return {
                    "date": check_date.isoformat(),
                    "labor_available": False,
                    "advisory_en": f"Major holiday ({event.name_en}) - No labor available",
                    "advisory_ar": f"عطلة كبرى ({event.name_ar}) - لا عمالة متوفرة",
                    "events": [e.name_en for e in labor_events],
                }

        # During Ramadan
        ramadan_events = [e for e in labor_events if "Ramadan" in e.name_en]
        if ramadan_events:
            return {
                "date": check_date.isoformat(),
                "labor_available": True,
                "reduced_hours": True,
                "advisory_en": "Ramadan - Reduced working hours. Plan heavy work for early morning.",
                "advisory_ar": "رمضان - ساعات عمل مخفضة. خطط للأعمال الثقيلة في الصباح الباكر.",
                "events": [e.name_en for e in labor_events],
            }

        return {
            "date": check_date.isoformat(),
            "labor_available": True,
            "advisory_en": f"Event ongoing: {labor_events[0].name_en}",
            "advisory_ar": f"حدث جارٍ: {labor_events[0].name_ar}",
            "events": [e.name_en for e in labor_events],
        }


# =============================================================================
# Helper Functions - الدوال المساعدة
# =============================================================================


def gregorian_to_hijri(gregorian_date: date) -> HijriDate:
    """
    Quick helper to convert Gregorian to Hijri
    دالة مساعدة للتحويل من ميلادي إلى هجري
    """
    calendar = HijriCalendar()
    return calendar.gregorian_to_hijri(gregorian_date)


def hijri_to_gregorian(
    hijri_year: int,
    hijri_month: int,
    hijri_day: int,
) -> date:
    """
    Quick helper to convert Hijri to Gregorian
    دالة مساعدة للتحويل من هجري إلى ميلادي
    """
    calendar = HijriCalendar()
    return calendar.hijri_to_gregorian(hijri_year, hijri_month, hijri_day)


def get_current_hijri_date() -> HijriDate:
    """
    Quick helper to get current Hijri date
    دالة مساعدة للحصول على التاريخ الهجري الحالي
    """
    calendar = HijriCalendar()
    return calendar.get_current_hijri_date()


def get_upcoming_islamic_events(days_ahead: int = 90) -> list[dict[str, Any]]:
    """
    Quick helper to get upcoming Islamic events
    دالة مساعدة للحصول على الأحداث الإسلامية القادمة
    """
    manager = IslamicEventsManager()
    return manager.get_upcoming_events(days_ahead)


def get_labor_advisory(check_date: date) -> dict[str, Any]:
    """
    Quick helper to get labor advisory for a date
    دالة مساعدة للحصول على استشارة العمالة لتاريخ
    """
    manager = IslamicEventsManager()
    return manager.get_labor_advisory(check_date)


def format_dual_date(gregorian_date: date) -> dict[str, str]:
    """
    Format a date in both Gregorian and Hijri calendars
    تنسيق تاريخ بالتقويمين الميلادي والهجري
    """
    calendar = HijriCalendar()
    hijri = calendar.gregorian_to_hijri(gregorian_date)

    return {
        "gregorian": gregorian_date.strftime("%Y-%m-%d"),
        "gregorian_formatted": gregorian_date.strftime("%B %d, %Y"),
        "hijri": f"{hijri.year}-{hijri.month:02d}-{hijri.day:02d}",
        "hijri_formatted_ar": f"{hijri.day} {hijri.month_name_ar} {hijri.year} هـ",
        "hijri_formatted_en": f"{hijri.day} {hijri.month_name_en} {hijri.year} AH",
        "combined": (f"{gregorian_date.strftime('%Y-%m-%d')} / {hijri.day} {hijri.month_name_ar} {hijri.year} هـ"),
    }
