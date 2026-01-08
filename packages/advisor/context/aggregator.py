"""
SAHOOL Context Aggregation Service
خدمة تجميع السياق الكامل للحقل
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Any, Protocol
from uuid import UUID


class FieldService(Protocol):
    """بروتوكول خدمة بيانات الحقل."""

    def get_field(self, field_id: UUID) -> dict[str, Any]: ...


class NdviService(Protocol):
    """بروتوكول خدمة NDVI."""

    def get_latest(self, field_id: UUID) -> dict[str, Any] | None: ...
    def get_summary(self, field_id: UUID, start: date, end: date) -> dict[str, Any] | None: ...


class WeatherService(Protocol):
    """بروتوكول خدمة الطقس."""

    def get_current(self, field_id: UUID) -> dict[str, Any] | None: ...
    def get_forecast(self, field_id: UUID, days: int) -> list[dict] | None: ...


class SoilService(Protocol):
    """بروتوكول خدمة التربة."""

    def get_profile(self, field_id: UUID) -> dict[str, Any] | None: ...


@dataclass
class AggregatedContext:
    """السياق المجمّع الكامل للحقل."""

    field_id: UUID
    tenant_id: UUID

    # معلومات الحقل
    field_name: str
    farm_name: str
    crop: str
    region: str
    area_hectares: float

    # NDVI
    ndvi_current: float | None
    ndvi_trend: str | None
    ndvi_health: str | None

    # الطقس
    weather_summary: str | None
    temperature: float | None
    humidity: float | None
    precipitation_forecast: str | None

    # التربة
    soil_type: str | None
    soil_ph: float | None

    # البيانات الوصفية
    data_age_days: int
    completeness: dict[str, bool]
    aggregated_at: datetime

    def to_prompt_context(self) -> str:
        """تحويل إلى نص لحقن الـ Prompt."""
        lines = [
            f"الحقل: {self.field_name}",
            f"المزرعة: {self.farm_name}",
            f"المحصول: {self.crop}",
            f"المنطقة: {self.region}",
            f"المساحة: {self.area_hectares:.1f} هكتار",
        ]

        if self.ndvi_current is not None:
            lines.append(f"NDVI: {self.ndvi_current:.2f} ({self.ndvi_health or 'غير محدد'})")

        if self.weather_summary:
            lines.append(f"الطقس: {self.weather_summary}")

        if self.soil_type:
            lines.append(f"التربة: {self.soil_type}")

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """تحويل إلى قاموس للـ API."""
        return {
            "field_id": str(self.field_id),
            "tenant_id": str(self.tenant_id),
            "field": {
                "name": self.field_name,
                "farm_name": self.farm_name,
                "crop": self.crop,
                "region": self.region,
                "area_hectares": self.area_hectares,
            },
            "ndvi": {
                "current": self.ndvi_current,
                "trend": self.ndvi_trend,
                "health": self.ndvi_health,
            },
            "weather": {
                "summary": self.weather_summary,
                "temperature": self.temperature,
                "humidity": self.humidity,
                "precipitation_forecast": self.precipitation_forecast,
            },
            "soil": {
                "type": self.soil_type,
                "ph": self.soil_ph,
            },
            "metadata": {
                "data_age_days": self.data_age_days,
                "completeness": self.completeness,
                "aggregated_at": self.aggregated_at.isoformat(),
            },
        }


class ContextAggregator:
    """
    خدمة تجميع كل السياق للحقل.

    هذا هو المصدر الوحيد للحقيقة لسياق الحقل،
    يمنع كل خدمة من جلب البيانات بطريقة مختلفة.
    """

    def __init__(
        self,
        field_svc: FieldService,
        ndvi_svc: NdviService,
        weather_svc: WeatherService,
        soil_svc: SoilService,
    ):
        self._field_svc = field_svc
        self._ndvi_svc = ndvi_svc
        self._weather_svc = weather_svc
        self._soil_svc = soil_svc

    def aggregate(self, field_id: UUID, tenant_id: UUID) -> AggregatedContext:
        """
        تجميع كل السياق المتاح للحقل.

        Args:
            field_id: معرف الحقل
            tenant_id: معرف المستأجر

        Returns:
            السياق المجمّع الكامل
        """
        now = datetime.now(UTC)

        # جلب بيانات الحقل
        field = self._field_svc.get_field(field_id)

        # جلب NDVI
        ndvi = self._ndvi_svc.get_latest(field_id)

        # جلب الطقس
        weather = self._weather_svc.get_current(field_id)

        # جلب التربة
        soil = self._soil_svc.get_profile(field_id)

        # حساب عمر البيانات
        data_age_days = 0
        if ndvi and ndvi.get("obs_date"):
            obs_date = ndvi["obs_date"]
            if isinstance(obs_date, str):
                obs_date = datetime.fromisoformat(obs_date).date()
            data_age_days = (now.date() - obs_date).days

        # بناء خريطة الاكتمال
        completeness = {
            "field": bool(field),
            "ndvi": bool(ndvi),
            "weather": bool(weather),
            "soil": bool(soil),
            "crop": bool(field.get("current_crop")),
        }

        return AggregatedContext(
            field_id=field_id,
            tenant_id=tenant_id,
            field_name=field.get("name", "غير معروف"),
            farm_name=field.get("farm_name", "غير معروف"),
            crop=field.get("current_crop", "غير محدد"),
            region=field.get("region", "غير محدد"),
            area_hectares=field.get("area_hectares", 0.0),
            ndvi_current=ndvi.get("ndvi_mean") if ndvi else None,
            ndvi_trend=ndvi.get("trend") if ndvi else None,
            ndvi_health=ndvi.get("health_status") if ndvi else None,
            weather_summary=weather.get("summary") if weather else None,
            temperature=weather.get("temperature") if weather else None,
            humidity=weather.get("humidity") if weather else None,
            precipitation_forecast=weather.get("precipitation") if weather else None,
            soil_type=soil.get("type") if soil else None,
            soil_ph=soil.get("ph") if soil else None,
            data_age_days=data_age_days,
            completeness=completeness,
            aggregated_at=now,
        )
