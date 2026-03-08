"""
Market Price Tracker
====================
متتبع أسعار السوق

Tracks crop prices across markets, maintains price history,
and manages price alerts.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from .models import (
    ALL_REGIONS,
    CROP_TYPES,
    MAJOR_MARKETS,
    AlertStatus,
    AlertType,
    Country,
    CropPrice,
    Currency,
    Market,
    MarketPriceErrors,
    MarketPriceException,
    PriceAlert,
    PriceQuality,
    PriceUnit,
    Region,
)

logger = logging.getLogger(__name__)


class PriceStorage:
    """
    Storage backend for price data
    التخزين الخلفي لبيانات الأسعار
    """

    def __init__(self, storage_path: str | None = None):
        """Initialize storage"""
        # Default to /var/lib/sahool in production, /tmp for development only
        default_path = (
            "/var/lib/sahool/market_prices" if os.getenv("ENVIRONMENT") == "production" else "/tmp/sahool_market_prices"
        )  # nosec B108
        self.storage_path = Path(storage_path or os.getenv("MARKET_PRICES_STORAGE_PATH", default_path))
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()

    async def save_price(self, price: CropPrice) -> None:
        """Save a price record"""
        async with self._lock:
            file_path = self.storage_path / f"prices_{price.market_id}.jsonl"
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(price.to_dict(), ensure_ascii=False) + "\n")

    async def save_prices_batch(self, prices: list[CropPrice]) -> None:
        """Save multiple price records"""
        for price in prices:
            await self.save_price(price)

    async def load_prices(
        self,
        market_id: str | None = None,
        crop_id: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int | None = None,
    ) -> list[CropPrice]:
        """Load price records with optional filters"""
        prices = []
        pattern = f"prices_{market_id}.jsonl" if market_id else "prices_*.jsonl"

        async with self._lock:
            for file_path in self.storage_path.glob(pattern):
                with open(file_path, encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            price = CropPrice.from_dict(data)

                            # Apply filters
                            if crop_id and price.crop_id != crop_id:
                                continue

                            if start_date and price.price_date < start_date:
                                continue

                            if end_date and price.price_date > end_date:
                                continue

                            prices.append(price)

        # Sort by date descending
        prices.sort(key=lambda p: (p.price_date, p.recorded_at), reverse=True)

        if limit:
            prices = prices[:limit]

        return prices

    async def load_latest_price(
        self,
        crop_id: str,
        market_id: str | None = None,
        region_id: str | None = None,
    ) -> CropPrice | None:
        """Load the most recent price for a crop"""
        prices = await self.load_prices(
            market_id=market_id,
            crop_id=crop_id,
            limit=100,
        )

        if region_id:
            prices = [p for p in prices if p.region_id == region_id]

        return prices[0] if prices else None

    async def load_price_history(
        self,
        crop_id: str,
        market_id: str | None = None,
        days: int = 30,
    ) -> list[CropPrice]:
        """Load price history for specified days"""
        start_date = date.today() - timedelta(days=days)
        return await self.load_prices(
            market_id=market_id,
            crop_id=crop_id,
            start_date=start_date,
        )


class AlertStorage:
    """
    Storage backend for price alerts
    التخزين الخلفي لتنبيهات الأسعار
    """

    def __init__(self, storage_path: str | None = None):
        """Initialize storage"""
        # Default to /var/lib/sahool in production, /tmp for development only
        default_path = (
            "/var/lib/sahool/market_alerts" if os.getenv("ENVIRONMENT") == "production" else "/tmp/sahool_market_alerts"
        )  # nosec B108
        self.storage_path = Path(storage_path or os.getenv("MARKET_ALERTS_STORAGE_PATH", default_path))
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()

    async def save_alert(self, alert: PriceAlert) -> None:
        """Save an alert"""
        async with self._lock:
            file_path = self.storage_path / f"alerts_{alert.tenant_id}.json"

            # Load existing alerts
            alerts_data = []
            if file_path.exists():
                with open(file_path, encoding="utf-8") as f:
                    alerts_data = json.load(f)

            # Update or add
            found = False
            for i, data in enumerate(alerts_data):
                if data.get("id") == alert.id:
                    alerts_data[i] = alert.to_dict()
                    found = True
                    break

            if not found:
                alerts_data.append(alert.to_dict())

            # Save
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(alerts_data, f, ensure_ascii=False, indent=2)

    async def load_alerts(
        self,
        tenant_id: str,
        status: AlertStatus | None = None,
        crop_id: str | None = None,
    ) -> list[PriceAlert]:
        """Load alerts for a tenant"""
        file_path = self.storage_path / f"alerts_{tenant_id}.json"

        if not file_path.exists():
            return []

        async with self._lock:
            with open(file_path, encoding="utf-8") as f:
                alerts_data = json.load(f)

        alerts = []
        for data in alerts_data:
            alert = PriceAlert(
                id=data.get("id", str(uuid.uuid4())),
                tenant_id=data.get("tenant_id", ""),
                user_id=data.get("user_id", ""),
                farmer_id=data.get("farmer_id", ""),
                crop_id=data.get("crop_id", ""),
                crop_name=data.get("crop_name", ""),
                crop_name_ar=data.get("crop_name_ar", ""),
                market_id=data.get("market_id"),
                region_id=data.get("region_id"),
                alert_type=AlertType(data.get("alert_type", "price_above")),
                threshold_value=Decimal(str(data.get("threshold_value", "0"))),
                threshold_unit=PriceUnit(data.get("threshold_unit", "kg")),
                currency=Currency(data.get("currency", "SAR")),
                percentage_threshold=data.get("percentage_threshold"),
                reference_price=Decimal(str(data["reference_price"])) if data.get("reference_price") else None,
                time_window_days=data.get("time_window_days", 7),
                status=AlertStatus(data.get("status", "active")),
                notify_sms=data.get("notify_sms", True),
                notify_email=data.get("notify_email", False),
                notify_push=data.get("notify_push", True),
                phone_number=data.get("phone_number", ""),
                email=data.get("email", ""),
                last_triggered_at=datetime.fromisoformat(data["last_triggered_at"])
                if data.get("last_triggered_at")
                else None,
                trigger_count=data.get("trigger_count", 0),
                last_triggered_price=Decimal(str(data["last_triggered_price"]))
                if data.get("last_triggered_price")
                else None,
                last_triggered_market_id=data.get("last_triggered_market_id"),
                valid_from=date.fromisoformat(data["valid_from"]) if data.get("valid_from") else date.today(),
                valid_until=date.fromisoformat(data["valid_until"]) if data.get("valid_until") else None,
                max_triggers=data.get("max_triggers"),
                name=data.get("name", ""),
                name_ar=data.get("name_ar", ""),
                description=data.get("description", ""),
                description_ar=data.get("description_ar", ""),
            )

            # Apply filters
            if status and alert.status != status:
                continue

            if crop_id and alert.crop_id != crop_id:
                continue

            alerts.append(alert)

        return alerts

    async def delete_alert(self, tenant_id: str, alert_id: str) -> bool:
        """Delete an alert"""
        file_path = self.storage_path / f"alerts_{tenant_id}.json"

        if not file_path.exists():
            return False

        async with self._lock:
            with open(file_path, encoding="utf-8") as f:
                alerts_data = json.load(f)

            original_len = len(alerts_data)
            alerts_data = [a for a in alerts_data if a.get("id") != alert_id]

            if len(alerts_data) == original_len:
                return False

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(alerts_data, f, ensure_ascii=False, indent=2)

        return True


class MarketPriceTracker:
    """
    Main tracker for market prices
    المتتبع الرئيسي لأسعار السوق

    Features:
    - Price recording and retrieval
    - Price history management
    - Alert management
    - Market and region queries

    Usage:
        tracker = MarketPriceTracker(tenant_id="farm_001")

        # Record a price
        await tracker.record_price(
            crop_id="wheat",
            market_id="riyadh_central",
            price=Decimal("2500"),
            unit=PriceUnit.TON,
        )

        # Get latest price
        price = await tracker.get_latest_price("wheat", "riyadh_central")

        # Create alert
        await tracker.create_alert(
            crop_id="wheat",
            alert_type=AlertType.PRICE_ABOVE,
            threshold=Decimal("3000"),
        )
    """

    def __init__(
        self,
        tenant_id: str,
        price_storage: PriceStorage | None = None,
        alert_storage: AlertStorage | None = None,
    ):
        """
        Initialize the tracker

        Args:
            tenant_id: Tenant identifier
            price_storage: Storage for prices (default: file-based)
            alert_storage: Storage for alerts (default: file-based)
        """
        self.tenant_id = tenant_id
        self.price_storage = price_storage or PriceStorage()
        self.alert_storage = alert_storage or AlertStorage()

        # Cache for frequently accessed data
        self._markets_cache: dict[str, Market] = dict(MAJOR_MARKETS)
        self._regions_cache: dict[str, Region] = dict(ALL_REGIONS)

    # =========================================================================
    # Price Recording
    # =========================================================================

    async def record_price(
        self,
        crop_id: str,
        market_id: str,
        price: Decimal,
        unit: PriceUnit = PriceUnit.KG,
        currency: Currency = Currency.SAR,
        quality: PriceQuality = PriceQuality.STANDARD,
        variety: str = "",
        variety_ar: str = "",
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        available_quantity: float | None = None,
        source: str = "manual",
        notes: str = "",
        notes_ar: str = "",
        price_date: date | None = None,
    ) -> CropPrice:
        """
        Record a crop price
        تسجيل سعر محصول

        Args:
            crop_id: Crop identifier (e.g., "wheat", "dates")
            market_id: Market identifier
            price: Price value
            unit: Price unit (kg, ton, etc.)
            currency: Currency (SAR, YER, USD)
            quality: Quality grade
            variety: Crop variety
            variety_ar: Crop variety in Arabic
            min_price: Minimum price in range
            max_price: Maximum price in range
            available_quantity: Available quantity
            source: Data source
            notes: Additional notes
            notes_ar: Notes in Arabic
            price_date: Date of the price (default: today)

        Returns:
            CropPrice record created
        """
        # Validate crop
        crop_type = CROP_TYPES.get(crop_id)
        if not crop_type:
            raise MarketPriceException(MarketPriceErrors.CROP_NOT_FOUND, f"Crop ID: {crop_id}")

        # Validate market
        market = self._markets_cache.get(market_id)
        if not market:
            raise MarketPriceException(MarketPriceErrors.MARKET_NOT_FOUND, f"Market ID: {market_id}")

        # Create price record
        price_record = CropPrice(
            crop_id=crop_id,
            crop_name=crop_type.name,
            crop_name_ar=crop_type.name_ar,
            variety=variety,
            variety_ar=variety_ar,
            market_id=market_id,
            market_name=market.name,
            market_name_ar=market.name_ar,
            region_id=market.region_id,
            price=price,
            currency=currency,
            unit=unit,
            quality=quality,
            min_price=min_price,
            max_price=max_price,
            available_quantity=available_quantity,
            quantity_unit=PriceUnit.TON,
            price_date=price_date or date.today(),
            source=source,
            notes=notes,
            notes_ar=notes_ar,
        )

        # Save
        await self.price_storage.save_price(price_record)

        # Check alerts
        await self._check_alerts_for_price(price_record)

        return price_record

    async def record_prices_batch(
        self,
        prices_data: list[dict[str, Any]],
    ) -> list[CropPrice]:
        """
        Record multiple prices in batch
        تسجيل أسعار متعددة دفعة واحدة

        Args:
            prices_data: List of price data dictionaries

        Returns:
            List of CropPrice records created
        """
        prices = []
        for data in prices_data:
            price = await self.record_price(
                crop_id=data["crop_id"],
                market_id=data["market_id"],
                price=Decimal(str(data["price"])),
                unit=PriceUnit(data.get("unit", "kg")),
                currency=Currency(data.get("currency", "SAR")),
                quality=PriceQuality(data.get("quality", "standard")),
                variety=data.get("variety", ""),
                variety_ar=data.get("variety_ar", ""),
                min_price=Decimal(str(data["min_price"])) if data.get("min_price") else None,
                max_price=Decimal(str(data["max_price"])) if data.get("max_price") else None,
                available_quantity=data.get("available_quantity"),
                source=data.get("source", "batch"),
                notes=data.get("notes", ""),
                notes_ar=data.get("notes_ar", ""),
                price_date=date.fromisoformat(data["price_date"]) if data.get("price_date") else None,
            )
            prices.append(price)

        return prices

    # =========================================================================
    # Price Retrieval
    # =========================================================================

    async def get_latest_price(
        self,
        crop_id: str,
        market_id: str | None = None,
        region_id: str | None = None,
    ) -> CropPrice | None:
        """
        Get the latest price for a crop
        الحصول على أحدث سعر لمحصول

        Args:
            crop_id: Crop identifier
            market_id: Optional market filter
            region_id: Optional region filter

        Returns:
            Latest CropPrice or None
        """
        return await self.price_storage.load_latest_price(
            crop_id=crop_id,
            market_id=market_id,
            region_id=region_id,
        )

    async def get_price_history(
        self,
        crop_id: str,
        market_id: str | None = None,
        days: int = 30,
    ) -> list[CropPrice]:
        """
        Get price history for a crop
        الحصول على تاريخ أسعار محصول

        Args:
            crop_id: Crop identifier
            market_id: Optional market filter
            days: Number of days of history

        Returns:
            List of CropPrice records
        """
        return await self.price_storage.load_price_history(
            crop_id=crop_id,
            market_id=market_id,
            days=days,
        )

    async def get_prices_by_region(
        self,
        crop_id: str,
        region_id: str,
        price_date: date | None = None,
    ) -> list[CropPrice]:
        """
        Get all prices for a crop in a region
        الحصول على جميع أسعار محصول في منطقة

        Args:
            crop_id: Crop identifier
            region_id: Region identifier
            price_date: Optional date filter (default: today)

        Returns:
            List of CropPrice records
        """
        price_date = price_date or date.today()
        all_prices = await self.price_storage.load_prices(
            crop_id=crop_id,
            start_date=price_date - timedelta(days=1),
            end_date=price_date,
        )

        return [p for p in all_prices if p.region_id == region_id]

    async def get_prices_by_country(
        self,
        crop_id: str,
        country: Country,
        price_date: date | None = None,
    ) -> list[CropPrice]:
        """
        Get all prices for a crop in a country
        الحصول على جميع أسعار محصول في دولة

        Args:
            crop_id: Crop identifier
            country: Country enum
            price_date: Optional date filter

        Returns:
            List of CropPrice records
        """
        price_date = price_date or date.today()

        # Get region IDs for the country
        country_region_ids = [r.id for r in self._regions_cache.values() if r.country == country]

        all_prices = await self.price_storage.load_prices(
            crop_id=crop_id,
            start_date=price_date - timedelta(days=1),
            end_date=price_date,
        )

        return [p for p in all_prices if p.region_id in country_region_ids]

    # =========================================================================
    # Alert Management
    # =========================================================================

    async def create_alert(
        self,
        crop_id: str,
        alert_type: AlertType,
        threshold_value: Decimal,
        user_id: str = "",
        farmer_id: str = "",
        market_id: str | None = None,
        region_id: str | None = None,
        threshold_unit: PriceUnit = PriceUnit.KG,
        currency: Currency = Currency.SAR,
        percentage_threshold: float | None = None,
        time_window_days: int = 7,
        notify_sms: bool = True,
        notify_email: bool = False,
        notify_push: bool = True,
        phone_number: str = "",
        email: str = "",
        valid_until: date | None = None,
        max_triggers: int | None = None,
        name: str = "",
        name_ar: str = "",
        description: str = "",
        description_ar: str = "",
    ) -> PriceAlert:
        """
        Create a price alert
        إنشاء تنبيه سعر

        Args:
            crop_id: Crop to monitor
            alert_type: Type of alert
            threshold_value: Price threshold
            user_id: User identifier
            farmer_id: Farmer identifier
            market_id: Specific market (None = all)
            region_id: Specific region (None = all)
            threshold_unit: Unit for threshold
            currency: Currency for threshold
            percentage_threshold: For percentage-based alerts
            time_window_days: Lookback period for change calculations
            notify_sms: Enable SMS notifications
            notify_email: Enable email notifications
            notify_push: Enable push notifications
            phone_number: Phone for SMS
            email: Email address
            valid_until: Alert expiry date
            max_triggers: Maximum times to trigger
            name: Alert name
            name_ar: Alert name in Arabic
            description: Alert description
            description_ar: Description in Arabic

        Returns:
            Created PriceAlert
        """
        # Validate crop
        crop_type = CROP_TYPES.get(crop_id)
        if not crop_type:
            raise MarketPriceException(MarketPriceErrors.CROP_NOT_FOUND, f"Crop ID: {crop_id}")

        # Get reference price for percentage alerts
        reference_price = None
        if alert_type in [AlertType.PRICE_CHANGE_PCT, AlertType.PRICE_DROP, AlertType.PRICE_SPIKE]:
            latest = await self.get_latest_price(crop_id, market_id, region_id)
            if latest:
                reference_price = latest.price

        # Auto-generate name if not provided
        if not name:
            name = f"{crop_type.name} - {alert_type.value.replace('_', ' ').title()}"
        if not name_ar:
            alert_type_ar = {
                AlertType.PRICE_ABOVE: "السعر فوق",
                AlertType.PRICE_BELOW: "السعر تحت",
                AlertType.PRICE_CHANGE_PCT: "تغير السعر",
                AlertType.PRICE_DROP: "انخفاض السعر",
                AlertType.PRICE_SPIKE: "ارتفاع السعر",
                AlertType.BEST_SELLING_TIME: "أفضل وقت للبيع",
                AlertType.MARKET_OPPORTUNITY: "فرصة سوقية",
            }
            name_ar = f"{crop_type.name_ar} - {alert_type_ar.get(alert_type, alert_type.value)}"

        alert = PriceAlert(
            tenant_id=self.tenant_id,
            user_id=user_id,
            farmer_id=farmer_id,
            crop_id=crop_id,
            crop_name=crop_type.name,
            crop_name_ar=crop_type.name_ar,
            market_id=market_id,
            region_id=region_id,
            alert_type=alert_type,
            threshold_value=threshold_value,
            threshold_unit=threshold_unit,
            currency=currency,
            percentage_threshold=percentage_threshold,
            reference_price=reference_price,
            time_window_days=time_window_days,
            status=AlertStatus.ACTIVE,
            notify_sms=notify_sms,
            notify_email=notify_email,
            notify_push=notify_push,
            phone_number=phone_number,
            email=email,
            valid_until=valid_until,
            max_triggers=max_triggers,
            name=name,
            name_ar=name_ar,
            description=description,
            description_ar=description_ar,
        )

        await self.alert_storage.save_alert(alert)
        return alert

    async def get_alerts(
        self,
        status: AlertStatus | None = None,
        crop_id: str | None = None,
    ) -> list[PriceAlert]:
        """
        Get price alerts
        الحصول على تنبيهات الأسعار

        Args:
            status: Filter by status
            crop_id: Filter by crop

        Returns:
            List of PriceAlert
        """
        return await self.alert_storage.load_alerts(
            tenant_id=self.tenant_id,
            status=status,
            crop_id=crop_id,
        )

    async def update_alert_status(
        self,
        alert_id: str,
        status: AlertStatus,
    ) -> PriceAlert | None:
        """
        Update alert status
        تحديث حالة التنبيه

        Args:
            alert_id: Alert identifier
            status: New status

        Returns:
            Updated alert or None if not found
        """
        alerts = await self.alert_storage.load_alerts(self.tenant_id)

        for alert in alerts:
            if alert.id == alert_id:
                alert.status = status
                alert.updated_at = datetime.now(UTC)
                await self.alert_storage.save_alert(alert)
                return alert

        return None

    async def delete_alert(self, alert_id: str) -> bool:
        """
        Delete a price alert
        حذف تنبيه سعر

        Args:
            alert_id: Alert identifier

        Returns:
            True if deleted, False if not found
        """
        return await self.alert_storage.delete_alert(self.tenant_id, alert_id)

    async def _check_alerts_for_price(self, price: CropPrice) -> list[PriceAlert]:
        """
        Check and trigger alerts for a new price
        التحقق من التنبيهات وتفعيلها لسعر جديد
        """
        triggered_alerts = []

        # Get active alerts for this crop
        alerts = await self.alert_storage.load_alerts(
            tenant_id=self.tenant_id,
            status=AlertStatus.ACTIVE,
            crop_id=price.crop_id,
        )

        for alert in alerts:
            # Check market filter
            if alert.market_id and alert.market_id != price.market_id:
                continue

            # Check region filter
            if alert.region_id and alert.region_id != price.region_id:
                continue

            # Get previous price for comparison
            previous_price = alert.reference_price
            if not previous_price:
                history = await self.get_price_history(
                    crop_id=price.crop_id,
                    market_id=price.market_id,
                    days=alert.time_window_days,
                )
                if len(history) > 1:
                    previous_price = history[1].price

            # Check if alert should trigger
            if alert.check_trigger(price.price, previous_price):
                alert.last_triggered_at = datetime.now(UTC)
                alert.trigger_count += 1
                alert.last_triggered_price = price.price
                alert.last_triggered_market_id = price.market_id
                alert.status = AlertStatus.TRIGGERED
                alert.updated_at = datetime.now(UTC)

                await self.alert_storage.save_alert(alert)
                triggered_alerts.append(alert)

                # Send notifications via NATS to notification-service
                await self._send_price_alert_notification(alert, price)

        return triggered_alerts

    async def _send_price_alert_notification(
        self,
        alert: PriceAlert,
        price: CropPrice,
    ) -> bool:
        """
        Send notification for triggered price alert
        إرسال إشعار لتنبيه السعر المفعّل

        Publishes a notification event to NATS which is consumed by
        notification-service to send SMS, email, and push notifications.

        Args:
            alert: The triggered price alert
            price: The price that triggered the alert

        Returns:
            True if notification was published successfully
        """
        try:
            # Lazy import to avoid circular dependencies
            from shared.libs.events.nats_publisher import (
                AnalysisEvent,
                get_publisher,
            )
        except ImportError:
            logger.warning(
                "NATS publisher not available. Skipping notification for alert %s",
                alert.id,
            )
            return False

        # Determine notification channels based on alert settings
        channels = []
        if alert.notify_push:
            channels.append("push")
        if alert.notify_sms:
            channels.append("sms")
        if alert.notify_email:
            channels.append("email")
        channels.append("in_app")  # Always include in-app

        # Determine priority based on alert type
        priority = "medium"
        if alert.alert_type in (AlertType.PRICE_SPIKE, AlertType.PRICE_DROP):
            priority = "high"

        # Build notification messages
        alert_type_messages = {
            AlertType.PRICE_ABOVE: (
                f"Price Alert: {price.crop_name} above {alert.threshold_value} {alert.currency.value}",
                f"تنبيه سعر: {price.crop_name_ar} تجاوز {alert.threshold_value} {alert.currency.value}",
            ),
            AlertType.PRICE_BELOW: (
                f"Price Alert: {price.crop_name} below {alert.threshold_value} {alert.currency.value}",
                f"تنبيه سعر: {price.crop_name_ar} أقل من {alert.threshold_value} {alert.currency.value}",
            ),
            AlertType.PRICE_CHANGE_PCT: (
                f"Price Alert: {price.crop_name} changed by {alert.percentage_threshold}%",
                f"تنبيه سعر: تغير سعر {price.crop_name_ar} بنسبة {alert.percentage_threshold}%",
            ),
            AlertType.PRICE_DROP: (
                f"Price Drop Alert: {price.crop_name} price has dropped",
                f"تنبيه انخفاض: انخفض سعر {price.crop_name_ar}",
            ),
            AlertType.PRICE_SPIKE: (
                f"Price Spike Alert: {price.crop_name} price has spiked",
                f"تنبيه ارتفاع: ارتفع سعر {price.crop_name_ar} بشكل مفاجئ",
            ),
            AlertType.BEST_SELLING_TIME: (
                f"Best Selling Time: Good time to sell {price.crop_name}",
                f"أفضل وقت للبيع: وقت مناسب لبيع {price.crop_name_ar}",
            ),
            AlertType.MARKET_OPPORTUNITY: (
                f"Market Opportunity: {price.crop_name} in {price.market_name}",
                f"فرصة سوقية: {price.crop_name_ar} في {price.market_name_ar}",
            ),
        }

        title, title_ar = alert_type_messages.get(
            alert.alert_type,
            (
                f"Price Alert: {price.crop_name}",
                f"تنبيه سعر: {price.crop_name_ar}",
            ),
        )

        body = f"Current price: {price.price} {price.currency.value}/{price.unit.value} at {price.market_name}"
        body_ar = f"السعر الحالي: {price.price} {price.currency.value}/{price.unit.value} في {price.market_name_ar}"

        try:
            publisher = await get_publisher()

            if not publisher.is_connected:
                logger.warning(
                    "NATS not connected. Cannot send notification for alert %s",
                    alert.id,
                )
                return False

            # Create and publish the event
            event = AnalysisEvent(
                event_type="market_price.alert_triggered",
                source_service="market-price-tracker",
                tenant_id=alert.tenant_id,
                farmer_id=alert.farmer_id or alert.user_id,
                data={
                    "type": "market_price",
                    "title": title,
                    "title_ar": title_ar,
                    "body": body,
                    "body_ar": body_ar,
                    "alert_id": alert.id,
                    "alert_type": alert.alert_type.value,
                    "crop_id": price.crop_id,
                    "crop_name": price.crop_name,
                    "crop_name_ar": price.crop_name_ar,
                    "market_id": price.market_id,
                    "market_name": price.market_name,
                    "market_name_ar": price.market_name_ar,
                    "current_price": str(price.price),
                    "threshold_value": str(alert.threshold_value),
                    "currency": price.currency.value,
                    "unit": price.unit.value,
                    "trigger_count": alert.trigger_count,
                },
                notification_priority=priority,
                notification_channels=channels,
            )

            success = await publisher.publish_analysis_event(event)

            if success:
                logger.info(
                    "Price alert notification sent: alert_id=%s crop=%s market=%s",
                    alert.id,
                    price.crop_id,
                    price.market_id,
                )
            else:
                logger.warning(
                    "Failed to publish price alert notification: alert_id=%s",
                    alert.id,
                )

            return success

        except Exception as e:
            logger.error(
                "Error sending price alert notification: %s (alert_id=%s)",
                str(e),
                alert.id,
            )
            return False

    # =========================================================================
    # Market and Region Queries
    # =========================================================================

    def get_markets(
        self,
        country: Country | None = None,
        region_id: str | None = None,
        market_type: str | None = None,
    ) -> list[Market]:
        """
        Get available markets
        الحصول على الأسواق المتاحة

        Args:
            country: Filter by country
            region_id: Filter by region
            market_type: Filter by market type

        Returns:
            List of markets
        """
        markets = list(self._markets_cache.values())

        if country:
            markets = [m for m in markets if m.country == country]

        if region_id:
            markets = [m for m in markets if m.region_id == region_id]

        if market_type:
            markets = [m for m in markets if m.market_type.value == market_type]

        return markets

    def get_regions(
        self,
        country: Country | None = None,
    ) -> list[Region]:
        """
        Get available regions
        الحصول على المناطق المتاحة

        Args:
            country: Filter by country

        Returns:
            List of regions
        """
        regions = list(self._regions_cache.values())

        if country:
            regions = [r for r in regions if r.country == country]

        return regions

    def get_market(self, market_id: str) -> Market | None:
        """Get a specific market by ID"""
        return self._markets_cache.get(market_id)

    def get_region(self, region_id: str) -> Region | None:
        """Get a specific region by ID"""
        return self._regions_cache.get(region_id)

    def add_market(self, market: Market) -> None:
        """Add a custom market to the tracker"""
        self._markets_cache[market.id] = market

    def add_region(self, region: Region) -> None:
        """Add a custom region to the tracker"""
        self._regions_cache[region.id] = region


# Convenience functions
_trackers: dict[str, MarketPriceTracker] = {}


def get_price_tracker(tenant_id: str) -> MarketPriceTracker:
    """Get or create a price tracker for a tenant"""
    if tenant_id not in _trackers:
        _trackers[tenant_id] = MarketPriceTracker(tenant_id)
    return _trackers[tenant_id]


async def record_price(
    tenant_id: str,
    crop_id: str,
    market_id: str,
    price: Decimal,
    **kwargs: Any,
) -> CropPrice:
    """Record a price using the default tracker"""
    tracker = get_price_tracker(tenant_id)
    return await tracker.record_price(crop_id, market_id, price, **kwargs)


async def get_latest_price(
    tenant_id: str,
    crop_id: str,
    market_id: str | None = None,
) -> CropPrice | None:
    """Get latest price using the default tracker"""
    tracker = get_price_tracker(tenant_id)
    return await tracker.get_latest_price(crop_id, market_id)


async def get_price_history(
    tenant_id: str,
    crop_id: str,
    market_id: str | None = None,
    days: int = 30,
) -> list[CropPrice]:
    """Get price history using the default tracker"""
    tracker = get_price_tracker(tenant_id)
    return await tracker.get_price_history(crop_id, market_id, days)


async def create_price_alert(
    tenant_id: str,
    crop_id: str,
    alert_type: AlertType,
    threshold_value: Decimal,
    **kwargs: Any,
) -> PriceAlert:
    """Create a price alert using the default tracker"""
    tracker = get_price_tracker(tenant_id)
    return await tracker.create_alert(crop_id, alert_type, threshold_value, **kwargs)
