"""
Market Price Data Models
========================
نماذج بيانات أسعار السوق

Data models for crop prices, markets, price alerts, and market comparisons.
Supports major agricultural markets in Saudi Arabia and Yemen.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any


class Currency(StrEnum):
    """Supported currencies | العملات المدعومة"""

    SAR = "SAR"  # Saudi Riyal | ريال سعودي
    YER = "YER"  # Yemeni Rial | ريال يمني
    USD = "USD"  # US Dollar | دولار أمريكي


class PriceUnit(StrEnum):
    """Price measurement units | وحدات قياس السعر"""

    KG = "kg"  # Kilogram | كيلوجرام
    TON = "ton"  # Metric ton | طن
    QUINTAL = "quintal"  # 100 kg | قنطار
    SACK = "sack"  # Sack (varies by crop) | كيس
    BOX = "box"  # Box/crate | صندوق
    PIECE = "piece"  # Individual item | قطعة


class PriceQuality(StrEnum):
    """Quality grade for pricing | درجة الجودة للتسعير"""

    PREMIUM = "premium"  # ممتاز
    GRADE_A = "grade_a"  # درجة أولى
    GRADE_B = "grade_b"  # درجة ثانية
    GRADE_C = "grade_c"  # درجة ثالثة
    STANDARD = "standard"  # عادي
    MIXED = "mixed"  # مخلوط


class MarketType(StrEnum):
    """Type of market | نوع السوق"""

    WHOLESALE = "wholesale"  # سوق الجملة
    RETAIL = "retail"  # سوق التجزئة
    FARM_GATE = "farm_gate"  # سعر المزرعة
    EXPORT = "export"  # سعر التصدير
    IMPORT = "import"  # سعر الاستيراد
    FUTURES = "futures"  # العقود الآجلة


class AlertType(StrEnum):
    """Type of price alert | نوع تنبيه السعر"""

    PRICE_ABOVE = "price_above"  # السعر فوق الحد
    PRICE_BELOW = "price_below"  # السعر تحت الحد
    PRICE_CHANGE_PCT = "price_change_pct"  # تغير نسبة السعر
    PRICE_DROP = "price_drop"  # انخفاض السعر
    PRICE_SPIKE = "price_spike"  # ارتفاع مفاجئ
    BEST_SELLING_TIME = "best_selling_time"  # أفضل وقت للبيع
    MARKET_OPPORTUNITY = "market_opportunity"  # فرصة سوقية


class AlertStatus(StrEnum):
    """Alert status | حالة التنبيه"""

    ACTIVE = "active"  # نشط
    TRIGGERED = "triggered"  # تم تفعيله
    EXPIRED = "expired"  # منتهي
    DISABLED = "disabled"  # معطل
    ACKNOWLEDGED = "acknowledged"  # تم الاطلاع عليه


class TrendDirection(StrEnum):
    """Price trend direction | اتجاه الاتجاه السعري"""

    RISING = "rising"  # صاعد
    FALLING = "falling"  # هابط
    STABLE = "stable"  # مستقر
    VOLATILE = "volatile"  # متقلب
    UNKNOWN = "unknown"  # غير معروف


class Season(StrEnum):
    """Agricultural season | الموسم الزراعي"""

    WINTER = "winter"  # شتوي
    SUMMER = "summer"  # صيفي
    SPRING = "spring"  # ربيعي
    AUTUMN = "autumn"  # خريفي
    YEAR_ROUND = "year_round"  # على مدار السنة


class Country(StrEnum):
    """Supported countries | الدول المدعومة"""

    SAUDI_ARABIA = "SA"  # المملكة العربية السعودية
    YEMEN = "YE"  # اليمن


@dataclass
class Region:
    """Geographic region | المنطقة الجغرافية"""

    id: str
    name: str
    name_ar: str
    country: Country
    parent_region_id: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timezone: str = "Asia/Riyadh"
    is_active: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "name_ar": self.name_ar,
            "country": self.country.value,
            "parent_region_id": self.parent_region_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone": self.timezone,
            "is_active": self.is_active,
        }


# Predefined Saudi Arabian Regions
SAUDI_REGIONS: dict[str, Region] = {
    "riyadh": Region(
        id="riyadh",
        name="Riyadh",
        name_ar="الرياض",
        country=Country.SAUDI_ARABIA,
        latitude=24.7136,
        longitude=46.6753,
    ),
    "jeddah": Region(
        id="jeddah",
        name="Jeddah",
        name_ar="جدة",
        country=Country.SAUDI_ARABIA,
        latitude=21.4858,
        longitude=39.1925,
    ),
    "dammam": Region(
        id="dammam",
        name="Dammam",
        name_ar="الدمام",
        country=Country.SAUDI_ARABIA,
        latitude=26.4207,
        longitude=50.0888,
    ),
    "al_ahsa": Region(
        id="al_ahsa",
        name="Al-Ahsa",
        name_ar="الأحساء",
        country=Country.SAUDI_ARABIA,
        latitude=25.3881,
        longitude=49.5866,
    ),
    "qassim": Region(
        id="qassim",
        name="Qassim",
        name_ar="القصيم",
        country=Country.SAUDI_ARABIA,
        latitude=26.3266,
        longitude=43.9745,
    ),
    "tabuk": Region(
        id="tabuk",
        name="Tabuk",
        name_ar="تبوك",
        country=Country.SAUDI_ARABIA,
        latitude=28.3838,
        longitude=36.5550,
    ),
    "hail": Region(
        id="hail",
        name="Hail",
        name_ar="حائل",
        country=Country.SAUDI_ARABIA,
        latitude=27.5114,
        longitude=41.7208,
    ),
    "madinah": Region(
        id="madinah",
        name="Madinah",
        name_ar="المدينة المنورة",
        country=Country.SAUDI_ARABIA,
        latitude=24.5247,
        longitude=39.5692,
    ),
    "jizan": Region(
        id="jizan",
        name="Jizan",
        name_ar="جازان",
        country=Country.SAUDI_ARABIA,
        latitude=16.8892,
        longitude=42.5511,
    ),
    "asir": Region(
        id="asir",
        name="Asir",
        name_ar="عسير",
        country=Country.SAUDI_ARABIA,
        latitude=18.2164,
        longitude=42.5053,
    ),
}

# Predefined Yemeni Regions
YEMEN_REGIONS: dict[str, Region] = {
    "sanaa": Region(
        id="sanaa",
        name="Sana'a",
        name_ar="صنعاء",
        country=Country.YEMEN,
        latitude=15.3694,
        longitude=44.1910,
        timezone="Asia/Aden",
    ),
    "aden": Region(
        id="aden",
        name="Aden",
        name_ar="عدن",
        country=Country.YEMEN,
        latitude=12.8008,
        longitude=45.0347,
        timezone="Asia/Aden",
    ),
    "taiz": Region(
        id="taiz",
        name="Taiz",
        name_ar="تعز",
        country=Country.YEMEN,
        latitude=13.5789,
        longitude=44.0219,
        timezone="Asia/Aden",
    ),
    "hodeidah": Region(
        id="hodeidah",
        name="Hodeidah",
        name_ar="الحديدة",
        country=Country.YEMEN,
        latitude=14.7979,
        longitude=42.9540,
        timezone="Asia/Aden",
    ),
    "ibb": Region(
        id="ibb",
        name="Ibb",
        name_ar="إب",
        country=Country.YEMEN,
        latitude=13.9759,
        longitude=44.1709,
        timezone="Asia/Aden",
    ),
    "hadramaut": Region(
        id="hadramaut",
        name="Hadramaut",
        name_ar="حضرموت",
        country=Country.YEMEN,
        latitude=15.9323,
        longitude=48.8944,
        timezone="Asia/Aden",
    ),
    "dhamar": Region(
        id="dhamar",
        name="Dhamar",
        name_ar="ذمار",
        country=Country.YEMEN,
        latitude=14.5430,
        longitude=44.4054,
        timezone="Asia/Aden",
    ),
    "lahij": Region(
        id="lahij",
        name="Lahij",
        name_ar="لحج",
        country=Country.YEMEN,
        latitude=13.0488,
        longitude=44.8836,
        timezone="Asia/Aden",
    ),
}

# All regions combined
ALL_REGIONS: dict[str, Region] = {**SAUDI_REGIONS, **YEMEN_REGIONS}


@dataclass
class Market:
    """Agricultural market | السوق الزراعي"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    name_ar: str = ""
    market_type: MarketType = MarketType.WHOLESALE
    region_id: str = ""
    country: Country = Country.SAUDI_ARABIA

    # Location
    address: str = ""
    address_ar: str = ""
    latitude: float | None = None
    longitude: float | None = None

    # Contact
    phone: str = ""
    email: str = ""
    website: str = ""

    # Operating hours
    opening_time: str = "06:00"
    closing_time: str = "18:00"
    operating_days: list[str] = field(default_factory=lambda: ["sat", "sun", "mon", "tue", "wed", "thu"])

    # Supported crops
    supported_crops: list[str] = field(default_factory=list)

    # Status
    is_active: bool = True
    data_source: str = "manual"  # manual, api, scraper
    last_price_update: datetime | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "name_ar": self.name_ar,
            "market_type": self.market_type.value,
            "region_id": self.region_id,
            "country": self.country.value,
            "address": self.address,
            "address_ar": self.address_ar,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "phone": self.phone,
            "email": self.email,
            "website": self.website,
            "opening_time": self.opening_time,
            "closing_time": self.closing_time,
            "operating_days": self.operating_days,
            "supported_crops": self.supported_crops,
            "is_active": self.is_active,
            "data_source": self.data_source,
            "last_price_update": self.last_price_update.isoformat() if self.last_price_update else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


# Predefined major markets
MAJOR_MARKETS: dict[str, Market] = {
    # Saudi Arabia
    "riyadh_central": Market(
        id="riyadh_central",
        name="Riyadh Central Market",
        name_ar="سوق الرياض المركزي",
        market_type=MarketType.WHOLESALE,
        region_id="riyadh",
        country=Country.SAUDI_ARABIA,
        supported_crops=["wheat", "barley", "dates", "tomatoes", "potatoes", "onions"],
    ),
    "jeddah_wholesale": Market(
        id="jeddah_wholesale",
        name="Jeddah Wholesale Market",
        name_ar="سوق جدة للجملة",
        market_type=MarketType.WHOLESALE,
        region_id="jeddah",
        country=Country.SAUDI_ARABIA,
        supported_crops=["vegetables", "fruits", "dates", "grains"],
    ),
    "dammam_agricultural": Market(
        id="dammam_agricultural",
        name="Dammam Agricultural Market",
        name_ar="سوق الدمام الزراعي",
        market_type=MarketType.WHOLESALE,
        region_id="dammam",
        country=Country.SAUDI_ARABIA,
        supported_crops=["dates", "vegetables", "fodder"],
    ),
    "qassim_dates": Market(
        id="qassim_dates",
        name="Qassim Dates Market",
        name_ar="سوق القصيم للتمور",
        market_type=MarketType.WHOLESALE,
        region_id="qassim",
        country=Country.SAUDI_ARABIA,
        supported_crops=["dates"],
    ),
    "al_ahsa_agricultural": Market(
        id="al_ahsa_agricultural",
        name="Al-Ahsa Agricultural Market",
        name_ar="سوق الأحساء الزراعي",
        market_type=MarketType.WHOLESALE,
        region_id="al_ahsa",
        country=Country.SAUDI_ARABIA,
        supported_crops=["dates", "rice", "vegetables"],
    ),
    # Yemen
    "sanaa_central": Market(
        id="sanaa_central",
        name="Sana'a Central Market",
        name_ar="السوق المركزي صنعاء",
        market_type=MarketType.WHOLESALE,
        region_id="sanaa",
        country=Country.YEMEN,
        supported_crops=["qat", "grapes", "coffee", "grains", "vegetables"],
    ),
    "aden_port": Market(
        id="aden_port",
        name="Aden Port Market",
        name_ar="سوق ميناء عدن",
        market_type=MarketType.WHOLESALE,
        region_id="aden",
        country=Country.YEMEN,
        supported_crops=["fish", "vegetables", "fruits", "grains"],
    ),
    "hodeidah_agricultural": Market(
        id="hodeidah_agricultural",
        name="Hodeidah Agricultural Market",
        name_ar="سوق الحديدة الزراعي",
        market_type=MarketType.WHOLESALE,
        region_id="hodeidah",
        country=Country.YEMEN,
        supported_crops=["mangoes", "bananas", "vegetables", "grains"],
    ),
}


@dataclass
class CropType:
    """Crop type information | معلومات نوع المحصول"""

    id: str
    name: str
    name_ar: str
    category: str  # grains, vegetables, fruits, dates, fodder
    category_ar: str
    default_unit: PriceUnit = PriceUnit.KG
    seasons: list[Season] = field(default_factory=list)
    is_active: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "name_ar": self.name_ar,
            "category": self.category,
            "category_ar": self.category_ar,
            "default_unit": self.default_unit.value,
            "seasons": [s.value for s in self.seasons],
            "is_active": self.is_active,
        }


# Common crops in Saudi Arabia and Yemen
CROP_TYPES: dict[str, CropType] = {
    "wheat": CropType(
        id="wheat",
        name="Wheat",
        name_ar="قمح",
        category="grains",
        category_ar="حبوب",
        default_unit=PriceUnit.TON,
        seasons=[Season.WINTER],
    ),
    "barley": CropType(
        id="barley",
        name="Barley",
        name_ar="شعير",
        category="grains",
        category_ar="حبوب",
        default_unit=PriceUnit.TON,
        seasons=[Season.WINTER],
    ),
    "dates": CropType(
        id="dates",
        name="Dates",
        name_ar="تمور",
        category="dates",
        category_ar="تمور",
        default_unit=PriceUnit.KG,
        seasons=[Season.SUMMER, Season.AUTUMN],
    ),
    "tomatoes": CropType(
        id="tomatoes",
        name="Tomatoes",
        name_ar="طماطم",
        category="vegetables",
        category_ar="خضروات",
        default_unit=PriceUnit.KG,
        seasons=[Season.YEAR_ROUND],
    ),
    "potatoes": CropType(
        id="potatoes",
        name="Potatoes",
        name_ar="بطاطس",
        category="vegetables",
        category_ar="خضروات",
        default_unit=PriceUnit.KG,
        seasons=[Season.YEAR_ROUND],
    ),
    "onions": CropType(
        id="onions",
        name="Onions",
        name_ar="بصل",
        category="vegetables",
        category_ar="خضروات",
        default_unit=PriceUnit.KG,
        seasons=[Season.YEAR_ROUND],
    ),
    "cucumbers": CropType(
        id="cucumbers",
        name="Cucumbers",
        name_ar="خيار",
        category="vegetables",
        category_ar="خضروات",
        default_unit=PriceUnit.KG,
        seasons=[Season.YEAR_ROUND],
    ),
    "watermelon": CropType(
        id="watermelon",
        name="Watermelon",
        name_ar="بطيخ",
        category="fruits",
        category_ar="فواكه",
        default_unit=PriceUnit.KG,
        seasons=[Season.SUMMER],
    ),
    "grapes": CropType(
        id="grapes",
        name="Grapes",
        name_ar="عنب",
        category="fruits",
        category_ar="فواكه",
        default_unit=PriceUnit.KG,
        seasons=[Season.SUMMER],
    ),
    "coffee": CropType(
        id="coffee",
        name="Coffee",
        name_ar="بن",
        category="beverages",
        category_ar="مشروبات",
        default_unit=PriceUnit.KG,
        seasons=[Season.YEAR_ROUND],
    ),
    "alfalfa": CropType(
        id="alfalfa",
        name="Alfalfa",
        name_ar="برسيم",
        category="fodder",
        category_ar="أعلاف",
        default_unit=PriceUnit.TON,
        seasons=[Season.YEAR_ROUND],
    ),
    "corn": CropType(
        id="corn",
        name="Corn",
        name_ar="ذرة",
        category="grains",
        category_ar="حبوب",
        default_unit=PriceUnit.TON,
        seasons=[Season.SUMMER],
    ),
    "sorghum": CropType(
        id="sorghum",
        name="Sorghum",
        name_ar="ذرة رفيعة",
        category="grains",
        category_ar="حبوب",
        default_unit=PriceUnit.TON,
        seasons=[Season.SUMMER],
    ),
    "mangoes": CropType(
        id="mangoes",
        name="Mangoes",
        name_ar="مانجو",
        category="fruits",
        category_ar="فواكه",
        default_unit=PriceUnit.KG,
        seasons=[Season.SUMMER],
    ),
    "bananas": CropType(
        id="bananas",
        name="Bananas",
        name_ar="موز",
        category="fruits",
        category_ar="فواكه",
        default_unit=PriceUnit.KG,
        seasons=[Season.YEAR_ROUND],
    ),
}


@dataclass
class CropPrice:
    """
    Crop price record
    سجل سعر المحصول
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Crop identification
    crop_id: str = ""
    crop_name: str = ""
    crop_name_ar: str = ""
    variety: str = ""  # Specific variety (e.g., Sukkari dates)
    variety_ar: str = ""

    # Market information
    market_id: str = ""
    market_name: str = ""
    market_name_ar: str = ""
    region_id: str = ""

    # Price details
    price: Decimal = Decimal("0")
    currency: Currency = Currency.SAR
    unit: PriceUnit = PriceUnit.KG
    quality: PriceQuality = PriceQuality.STANDARD

    # Price range (if available)
    min_price: Decimal | None = None
    max_price: Decimal | None = None

    # Quantity
    available_quantity: float | None = None
    quantity_unit: PriceUnit = PriceUnit.TON

    # Timestamp
    price_date: date = field(default_factory=date.today)
    recorded_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Source
    source: str = "market_report"  # market_report, trader, api, manual
    source_id: str | None = None
    verified: bool = False
    verified_by: str | None = None

    # Metadata
    notes: str = ""
    notes_ar: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "crop_id": self.crop_id,
            "crop_name": self.crop_name,
            "crop_name_ar": self.crop_name_ar,
            "variety": self.variety,
            "variety_ar": self.variety_ar,
            "market_id": self.market_id,
            "market_name": self.market_name,
            "market_name_ar": self.market_name_ar,
            "region_id": self.region_id,
            "price": str(self.price),
            "currency": self.currency.value,
            "unit": self.unit.value,
            "quality": self.quality.value,
            "min_price": str(self.min_price) if self.min_price else None,
            "max_price": str(self.max_price) if self.max_price else None,
            "available_quantity": self.available_quantity,
            "quantity_unit": self.quantity_unit.value,
            "price_date": self.price_date.isoformat(),
            "recorded_at": self.recorded_at.isoformat(),
            "source": self.source,
            "source_id": self.source_id,
            "verified": self.verified,
            "verified_by": self.verified_by,
            "notes": self.notes,
            "notes_ar": self.notes_ar,
            "tags": self.tags,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CropPrice:
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            crop_id=data.get("crop_id", ""),
            crop_name=data.get("crop_name", ""),
            crop_name_ar=data.get("crop_name_ar", ""),
            variety=data.get("variety", ""),
            variety_ar=data.get("variety_ar", ""),
            market_id=data.get("market_id", ""),
            market_name=data.get("market_name", ""),
            market_name_ar=data.get("market_name_ar", ""),
            region_id=data.get("region_id", ""),
            price=Decimal(str(data.get("price", "0"))),
            currency=Currency(data.get("currency", "SAR")),
            unit=PriceUnit(data.get("unit", "kg")),
            quality=PriceQuality(data.get("quality", "standard")),
            min_price=Decimal(str(data["min_price"])) if data.get("min_price") else None,
            max_price=Decimal(str(data["max_price"])) if data.get("max_price") else None,
            available_quantity=data.get("available_quantity"),
            quantity_unit=PriceUnit(data.get("quantity_unit", "ton")),
            price_date=date.fromisoformat(data["price_date"]) if data.get("price_date") else date.today(),
            recorded_at=datetime.fromisoformat(data["recorded_at"]) if data.get("recorded_at") else datetime.now(UTC),
            source=data.get("source", "market_report"),
            source_id=data.get("source_id"),
            verified=data.get("verified", False),
            verified_by=data.get("verified_by"),
            notes=data.get("notes", ""),
            notes_ar=data.get("notes_ar", ""),
            tags=data.get("tags", []),
        )


@dataclass
class PriceAlert:
    """
    Price alert configuration
    تكوين تنبيه السعر
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Owner
    tenant_id: str = ""
    user_id: str = ""
    farmer_id: str = ""

    # Alert target
    crop_id: str = ""
    crop_name: str = ""
    crop_name_ar: str = ""
    market_id: str | None = None  # None = all markets
    region_id: str | None = None  # None = all regions

    # Alert type and threshold
    alert_type: AlertType = AlertType.PRICE_ABOVE
    threshold_value: Decimal = Decimal("0")
    threshold_unit: PriceUnit = PriceUnit.KG
    currency: Currency = Currency.SAR

    # For percentage-based alerts
    percentage_threshold: float | None = None  # e.g., 10.0 for 10%
    reference_price: Decimal | None = None  # Base price for comparison
    time_window_days: int = 7  # Look back period for change calculation

    # Alert status
    status: AlertStatus = AlertStatus.ACTIVE

    # Notification settings
    notify_sms: bool = True
    notify_email: bool = False
    notify_push: bool = True
    phone_number: str = ""
    email: str = ""

    # Trigger history
    last_triggered_at: datetime | None = None
    trigger_count: int = 0
    last_triggered_price: Decimal | None = None
    last_triggered_market_id: str | None = None

    # Validity
    valid_from: date = field(default_factory=date.today)
    valid_until: date | None = None
    max_triggers: int | None = None  # None = unlimited

    # Metadata
    name: str = ""
    name_ar: str = ""
    description: str = ""
    description_ar: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def is_valid(self) -> bool:
        """Check if alert is currently valid"""
        if self.status != AlertStatus.ACTIVE:
            return False

        today = date.today()
        if today < self.valid_from:
            return False

        if self.valid_until and today > self.valid_until:
            return False

        if self.max_triggers and self.trigger_count >= self.max_triggers:
            return False

        return True

    def check_trigger(self, current_price: Decimal, previous_price: Decimal | None = None) -> bool:
        """
        Check if alert should be triggered
        التحقق مما إذا كان يجب تفعيل التنبيه
        """
        if not self.is_valid():
            return False

        if self.alert_type == AlertType.PRICE_ABOVE:
            return current_price >= self.threshold_value

        elif self.alert_type == AlertType.PRICE_BELOW:
            return current_price <= self.threshold_value

        elif self.alert_type == AlertType.PRICE_CHANGE_PCT:
            if previous_price is None or previous_price == 0:
                return False
            change_pct = abs((current_price - previous_price) / previous_price * 100)
            return change_pct >= (self.percentage_threshold or 0)

        elif self.alert_type == AlertType.PRICE_DROP:
            if previous_price is None:
                return False
            return current_price < previous_price

        elif self.alert_type == AlertType.PRICE_SPIKE:
            if previous_price is None or previous_price == 0:
                return False
            increase_pct = (current_price - previous_price) / previous_price * 100
            return increase_pct >= (self.percentage_threshold or 10)

        return False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "farmer_id": self.farmer_id,
            "crop_id": self.crop_id,
            "crop_name": self.crop_name,
            "crop_name_ar": self.crop_name_ar,
            "market_id": self.market_id,
            "region_id": self.region_id,
            "alert_type": self.alert_type.value,
            "threshold_value": str(self.threshold_value),
            "threshold_unit": self.threshold_unit.value,
            "currency": self.currency.value,
            "percentage_threshold": self.percentage_threshold,
            "reference_price": str(self.reference_price) if self.reference_price else None,
            "time_window_days": self.time_window_days,
            "status": self.status.value,
            "notify_sms": self.notify_sms,
            "notify_email": self.notify_email,
            "notify_push": self.notify_push,
            "phone_number": self.phone_number[-4:] if self.phone_number else "",  # Masked
            "email": self.email,
            "last_triggered_at": self.last_triggered_at.isoformat() if self.last_triggered_at else None,
            "trigger_count": self.trigger_count,
            "last_triggered_price": str(self.last_triggered_price) if self.last_triggered_price else None,
            "last_triggered_market_id": self.last_triggered_market_id,
            "valid_from": self.valid_from.isoformat(),
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "max_triggers": self.max_triggers,
            "name": self.name,
            "name_ar": self.name_ar,
            "description": self.description,
            "description_ar": self.description_ar,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_valid": self.is_valid(),
        }


@dataclass
class PriceTrend:
    """
    Price trend analysis result
    نتيجة تحليل اتجاه السعر
    """

    crop_id: str = ""
    crop_name: str = ""
    crop_name_ar: str = ""
    market_id: str | None = None
    region_id: str | None = None

    # Trend direction
    direction: TrendDirection = TrendDirection.UNKNOWN
    strength: float = 0.0  # 0-100, strength of the trend

    # Price statistics
    current_price: Decimal = Decimal("0")
    previous_price: Decimal = Decimal("0")
    price_change: Decimal = Decimal("0")
    price_change_percent: float = 0.0

    # Period statistics
    period_high: Decimal = Decimal("0")
    period_low: Decimal = Decimal("0")
    period_average: Decimal = Decimal("0")
    period_median: Decimal = Decimal("0")
    period_std_dev: float = 0.0

    # Analysis period
    start_date: date = field(default_factory=date.today)
    end_date: date = field(default_factory=date.today)
    data_points: int = 0

    # Volatility
    volatility_score: float = 0.0  # 0-100
    is_volatile: bool = False

    # Prediction (if available)
    predicted_direction: TrendDirection | None = None
    predicted_price: Decimal | None = None
    prediction_confidence: float = 0.0

    # Seasonal factors
    is_seasonal_peak: bool = False
    is_seasonal_low: bool = False
    seasonal_factor: float = 1.0  # Multiplier vs. annual average

    # Analysis timestamp
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "crop_id": self.crop_id,
            "crop_name": self.crop_name,
            "crop_name_ar": self.crop_name_ar,
            "market_id": self.market_id,
            "region_id": self.region_id,
            "direction": self.direction.value,
            "strength": self.strength,
            "current_price": str(self.current_price),
            "previous_price": str(self.previous_price),
            "price_change": str(self.price_change),
            "price_change_percent": self.price_change_percent,
            "period_high": str(self.period_high),
            "period_low": str(self.period_low),
            "period_average": str(self.period_average),
            "period_median": str(self.period_median),
            "period_std_dev": self.period_std_dev,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "data_points": self.data_points,
            "volatility_score": self.volatility_score,
            "is_volatile": self.is_volatile,
            "predicted_direction": self.predicted_direction.value if self.predicted_direction else None,
            "predicted_price": str(self.predicted_price) if self.predicted_price else None,
            "prediction_confidence": self.prediction_confidence,
            "is_seasonal_peak": self.is_seasonal_peak,
            "is_seasonal_low": self.is_seasonal_low,
            "seasonal_factor": self.seasonal_factor,
            "analyzed_at": self.analyzed_at.isoformat(),
        }


@dataclass
class MarketComparison:
    """
    Market price comparison result
    نتيجة مقارنة أسعار السوق
    """

    crop_id: str = ""
    crop_name: str = ""
    crop_name_ar: str = ""

    # Comparison date
    comparison_date: date = field(default_factory=date.today)

    # Markets being compared
    markets: list[dict[str, Any]] = field(default_factory=list)
    # [{"market_id": "...", "market_name": "...", "price": "...", "rank": 1}]

    # Best options
    best_price_market_id: str = ""
    best_price_market_name: str = ""
    best_price_market_name_ar: str = ""
    best_price: Decimal = Decimal("0")

    worst_price_market_id: str = ""
    worst_price_market_name: str = ""
    worst_price_market_name_ar: str = ""
    worst_price: Decimal = Decimal("0")

    # Statistics
    average_price: Decimal = Decimal("0")
    price_spread: Decimal = Decimal("0")  # best - worst
    price_spread_percent: float = 0.0

    # Recommendation
    recommended_market_id: str = ""
    recommended_market_name: str = ""
    recommended_market_name_ar: str = ""
    recommendation_reason: str = ""
    recommendation_reason_ar: str = ""
    potential_gain: Decimal = Decimal("0")  # vs average
    potential_gain_percent: float = 0.0

    # Analysis metadata
    markets_compared: int = 0
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "crop_id": self.crop_id,
            "crop_name": self.crop_name,
            "crop_name_ar": self.crop_name_ar,
            "comparison_date": self.comparison_date.isoformat(),
            "markets": self.markets,
            "best_price_market_id": self.best_price_market_id,
            "best_price_market_name": self.best_price_market_name,
            "best_price_market_name_ar": self.best_price_market_name_ar,
            "best_price": str(self.best_price),
            "worst_price_market_id": self.worst_price_market_id,
            "worst_price_market_name": self.worst_price_market_name,
            "worst_price_market_name_ar": self.worst_price_market_name_ar,
            "worst_price": str(self.worst_price),
            "average_price": str(self.average_price),
            "price_spread": str(self.price_spread),
            "price_spread_percent": self.price_spread_percent,
            "recommended_market_id": self.recommended_market_id,
            "recommended_market_name": self.recommended_market_name,
            "recommended_market_name_ar": self.recommended_market_name_ar,
            "recommendation_reason": self.recommendation_reason,
            "recommendation_reason_ar": self.recommendation_reason_ar,
            "potential_gain": str(self.potential_gain),
            "potential_gain_percent": self.potential_gain_percent,
            "markets_compared": self.markets_compared,
            "analyzed_at": self.analyzed_at.isoformat(),
        }


@dataclass
class SellingRecommendation:
    """
    Best selling time recommendation
    توصية أفضل وقت للبيع
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Target
    crop_id: str = ""
    crop_name: str = ""
    crop_name_ar: str = ""
    farmer_id: str = ""
    field_id: str = ""

    # Recommendation
    action: str = "sell"  # sell, hold, wait
    action_ar: str = "بيع"
    confidence: float = 0.0  # 0-100

    # Timing
    recommended_date: date | None = None
    recommended_date_range_start: date | None = None
    recommended_date_range_end: date | None = None
    urgency: str = "normal"  # urgent, normal, flexible
    urgency_ar: str = "عادي"

    # Market recommendation
    recommended_market_id: str = ""
    recommended_market_name: str = ""
    recommended_market_name_ar: str = ""

    # Price expectations
    expected_price: Decimal = Decimal("0")
    expected_price_range_low: Decimal | None = None
    expected_price_range_high: Decimal | None = None
    current_price: Decimal = Decimal("0")
    price_unit: PriceUnit = PriceUnit.KG
    currency: Currency = Currency.SAR

    # Potential earnings
    quantity_to_sell: float = 0.0
    quantity_unit: PriceUnit = PriceUnit.TON
    estimated_revenue: Decimal = Decimal("0")
    potential_additional_revenue: Decimal = Decimal("0")  # vs selling now

    # Reasons
    reasons: list[str] = field(default_factory=list)
    reasons_ar: list[str] = field(default_factory=list)

    # Risks
    risks: list[str] = field(default_factory=list)
    risks_ar: list[str] = field(default_factory=list)

    # Factors considered
    factors_considered: list[str] = field(default_factory=list)
    # e.g., ["seasonal_trend", "market_demand", "weather_forecast", "storage_costs"]

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    valid_until: date | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "crop_id": self.crop_id,
            "crop_name": self.crop_name,
            "crop_name_ar": self.crop_name_ar,
            "farmer_id": self.farmer_id,
            "field_id": self.field_id,
            "action": self.action,
            "action_ar": self.action_ar,
            "confidence": self.confidence,
            "recommended_date": self.recommended_date.isoformat() if self.recommended_date else None,
            "recommended_date_range_start": self.recommended_date_range_start.isoformat()
            if self.recommended_date_range_start
            else None,
            "recommended_date_range_end": self.recommended_date_range_end.isoformat()
            if self.recommended_date_range_end
            else None,
            "urgency": self.urgency,
            "urgency_ar": self.urgency_ar,
            "recommended_market_id": self.recommended_market_id,
            "recommended_market_name": self.recommended_market_name,
            "recommended_market_name_ar": self.recommended_market_name_ar,
            "expected_price": str(self.expected_price),
            "expected_price_range_low": str(self.expected_price_range_low) if self.expected_price_range_low else None,
            "expected_price_range_high": str(self.expected_price_range_high)
            if self.expected_price_range_high
            else None,
            "current_price": str(self.current_price),
            "price_unit": self.price_unit.value,
            "currency": self.currency.value,
            "quantity_to_sell": self.quantity_to_sell,
            "quantity_unit": self.quantity_unit.value,
            "estimated_revenue": str(self.estimated_revenue),
            "potential_additional_revenue": str(self.potential_additional_revenue),
            "reasons": self.reasons,
            "reasons_ar": self.reasons_ar,
            "risks": self.risks,
            "risks_ar": self.risks_ar,
            "factors_considered": self.factors_considered,
            "created_at": self.created_at.isoformat(),
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
        }


# Error messages
@dataclass
class MarketPriceError:
    """Error message for market price operations"""

    code: str
    message: str
    message_ar: str


class MarketPriceErrors:
    """Market price error messages"""

    CROP_NOT_FOUND = MarketPriceError(
        code="crop_not_found",
        message="Crop type not found",
        message_ar="نوع المحصول غير موجود",
    )

    MARKET_NOT_FOUND = MarketPriceError(
        code="market_not_found",
        message="Market not found",
        message_ar="السوق غير موجود",
    )

    REGION_NOT_FOUND = MarketPriceError(
        code="region_not_found",
        message="Region not found",
        message_ar="المنطقة غير موجودة",
    )

    NO_PRICE_DATA = MarketPriceError(
        code="no_price_data",
        message="No price data available for the specified criteria",
        message_ar="لا تتوفر بيانات أسعار للمعايير المحددة",
    )

    INVALID_DATE_RANGE = MarketPriceError(
        code="invalid_date_range",
        message="Invalid date range specified",
        message_ar="نطاق تاريخ غير صالح",
    )

    ALERT_NOT_FOUND = MarketPriceError(
        code="alert_not_found",
        message="Price alert not found",
        message_ar="تنبيه السعر غير موجود",
    )

    INSUFFICIENT_DATA = MarketPriceError(
        code="insufficient_data",
        message="Insufficient data for analysis",
        message_ar="بيانات غير كافية للتحليل",
    )


class MarketPriceException(Exception):
    """Base exception for market price operations"""

    def __init__(self, error: MarketPriceError, details: str = ""):
        self.error = error
        self.details = details
        super().__init__(error.message)

    def to_dict(self, lang: str = "en") -> dict[str, Any]:
        message = self.error.message_ar if lang == "ar" else self.error.message
        return {
            "error": self.error.code,
            "message": message,
            "details": self.details,
        }
