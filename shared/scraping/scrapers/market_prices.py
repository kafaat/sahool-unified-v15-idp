"""Market price scraper for agricultural commodities.

This module provides the MarketPriceScraper class for collecting
agricultural commodity prices from various market sources.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from ..browser import BrowserManager
from ..config import ScrapingConfig
from ..utils import (
    clean_text,
    extract_first_number,
    normalize_location,
    parse_price,
)
from .base import BaseScraper, ScrapingResult, ScrapingStatus

logger = logging.getLogger(__name__)


class PriceUnit(Enum):
    """Units for agricultural prices."""

    KG = "kg"
    TON = "ton"
    QUINTAL = "quintal"
    CARTON = "carton"
    BAG = "bag"
    PIECE = "piece"
    LITER = "liter"


class CropCategory(Enum):
    """Categories of agricultural products."""

    GRAINS = "grains"
    VEGETABLES = "vegetables"
    FRUITS = "fruits"
    DATES = "dates"
    LIVESTOCK = "livestock"
    DAIRY = "dairy"
    FODDER = "fodder"
    SPICES = "spices"


# Crop name translations
CROP_TRANSLATIONS: dict[str, dict[str, str]] = {
    "wheat": {"ar": "قمح", "category": "grains"},
    "barley": {"ar": "شعير", "category": "grains"},
    "rice": {"ar": "أرز", "category": "grains"},
    "corn": {"ar": "ذرة", "category": "grains"},
    "tomato": {"ar": "طماطم", "category": "vegetables"},
    "cucumber": {"ar": "خيار", "category": "vegetables"},
    "onion": {"ar": "بصل", "category": "vegetables"},
    "potato": {"ar": "بطاطس", "category": "vegetables"},
    "eggplant": {"ar": "باذنجان", "category": "vegetables"},
    "pepper": {"ar": "فلفل", "category": "vegetables"},
    "lettuce": {"ar": "خس", "category": "vegetables"},
    "carrot": {"ar": "جزر", "category": "vegetables"},
    "date": {"ar": "تمر", "category": "dates"},
    "apple": {"ar": "تفاح", "category": "fruits"},
    "orange": {"ar": "برتقال", "category": "fruits"},
    "grape": {"ar": "عنب", "category": "fruits"},
    "watermelon": {"ar": "بطيخ", "category": "fruits"},
    "melon": {"ar": "شمام", "category": "fruits"},
    "lemon": {"ar": "ليمون", "category": "fruits"},
    "alfalfa": {"ar": "برسيم", "category": "fodder"},
    "clover": {"ar": "برسيم حجازي", "category": "fodder"},
}


@dataclass
class CropPrice:
    """Agricultural commodity price data."""

    crop_name: str
    crop_name_ar: str | None = None
    category: str | None = None
    price: float = 0.0
    currency: str = "SAR"
    unit: str = "kg"
    min_price: float | None = None
    max_price: float | None = None
    avg_price: float | None = None
    change_percent: float | None = None
    market: str | None = None
    market_ar: str | None = None
    location: str | None = None
    location_ar: str | None = None
    date: datetime | None = None
    quality_grade: str | None = None
    source: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "crop_name": self.crop_name,
            "crop_name_ar": self.crop_name_ar,
            "category": self.category,
            "price": self.price,
            "currency": self.currency,
            "unit": self.unit,
            "min_price": self.min_price,
            "max_price": self.max_price,
            "avg_price": self.avg_price,
            "change_percent": self.change_percent,
            "market": self.market,
            "market_ar": self.market_ar,
            "location": self.location,
            "location_ar": self.location_ar,
            "date": self.date.isoformat() if self.date else None,
            "quality_grade": self.quality_grade,
            "source": self.source,
        }


@dataclass
class MarketPriceReport:
    """Collection of market prices."""

    prices: list[CropPrice] = field(default_factory=list)
    market: str | None = None
    market_ar: str | None = None
    location: str | None = None
    date: datetime | None = None
    source: str | None = None
    fetched_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "prices": [p.to_dict() for p in self.prices],
            "market": self.market,
            "market_ar": self.market_ar,
            "location": self.location,
            "date": self.date.isoformat() if self.date else None,
            "source": self.source,
            "fetched_at": self.fetched_at.isoformat(),
        }

    def get_by_category(self, category: str) -> list[CropPrice]:
        """Get prices by category."""
        return [p for p in self.prices if p.category == category]

    def get_by_crop(self, crop_name: str) -> CropPrice | None:
        """Get price for a specific crop."""
        crop_lower = crop_name.lower()
        for price in self.prices:
            if price.crop_name.lower() == crop_lower or price.crop_name_ar == crop_name:
                return price
        return None


class MarketPriceScraper(BaseScraper):
    """Scraper for agricultural market prices.

    This scraper collects commodity prices from various agricultural
    markets and price reporting sources.

    Example:
        >>> async with BrowserManager() as browser:
        ...     scraper = MarketPriceScraper(browser)
        ...     result = await scraper.scrape_prices(market="riyadh")
        ...     if result.status == ScrapingStatus.SUCCESS:
        ...         for price in result.data.prices:
        ...             print(f"{price.crop_name}: {price.price} {price.currency}")
    """

    # Market source URLs
    SOURCES = {
        "mewa": "https://mewa.gov.sa/ar/InformationCenter/Pages/vegetable-prices.aspx",
        "almarai": "https://www.almarai.com/",
    }

    # Saudi markets
    MARKETS = {
        "riyadh": {"ar": "سوق الرياض المركزي", "en": "Riyadh Central Market"},
        "jeddah": {"ar": "سوق جدة المركزي", "en": "Jeddah Central Market"},
        "dammam": {"ar": "سوق الدمام المركزي", "en": "Dammam Central Market"},
        "makkah": {"ar": "سوق مكة المكرمة", "en": "Makkah Market"},
        "madinah": {"ar": "سوق المدينة المنورة", "en": "Madinah Market"},
    }

    def __init__(
        self,
        browser: BrowserManager,
        config: ScrapingConfig | None = None,
    ) -> None:
        """Initialize the market price scraper.

        Args:
            browser: Browser manager instance.
            config: Scraping configuration.
        """
        super().__init__(browser, config)

    def _translate_crop(self, crop_name: str) -> dict[str, str | None]:
        """Translate crop name and get category.

        Args:
            crop_name: Crop name in English or Arabic.

        Returns:
            Dictionary with ar name and category.
        """
        crop_lower = crop_name.lower().strip()

        # Check English names
        if crop_lower in CROP_TRANSLATIONS:
            trans = CROP_TRANSLATIONS[crop_lower]
            return {"ar": trans["ar"], "category": trans.get("category")}

        # Check Arabic names
        for eng, trans in CROP_TRANSLATIONS.items():
            if trans["ar"] == crop_name:
                return {"ar": trans["ar"], "en": eng, "category": trans.get("category")}

        return {"ar": None, "category": None}

    async def scrape_prices(
        self,
        market: str | None = None,
        category: str | None = None,
        crops: list[str] | None = None,
        source: str = "mewa",
    ) -> ScrapingResult[MarketPriceReport]:
        """Scrape market prices for agricultural commodities.

        Args:
            market: Market name or location.
            category: Filter by crop category.
            crops: List of specific crops to get prices for.
            source: Data source to use.

        Returns:
            ScrapingResult containing MarketPriceReport.
        """
        import time

        start_time = time.time()

        # Normalize market name
        market_normalized = market.lower().strip() if market else "riyadh"

        # Check cache
        cache_key = f"prices_{market_normalized}_{category}_{source}"
        cached = self.get_cached(cache_key)
        if cached:
            return ScrapingResult(
                status=ScrapingStatus.CACHED,
                data=cached,
                cached=True,
                duration_ms=(time.time() - start_time) * 1000,
            )

        try:
            if source == "mewa":
                report = await self._scrape_mewa_prices(market_normalized, category, crops)
            else:
                # Fallback to generic scraping
                report = await self._scrape_generic_prices(market_normalized, category, crops)

            # Cache result
            self.set_cached(
                cache_key,
                report,
                ttl=self._config.cache.market_price_ttl,
            )

            duration_ms = (time.time() - start_time) * 1000
            logger.info(
                f"Market prices scraped for {market_normalized} ({len(report.prices)} items) in {duration_ms:.0f}ms"
            )

            return ScrapingResult(
                status=ScrapingStatus.SUCCESS,
                data=report,
                url=self._page.url if self._page else None,
                duration_ms=duration_ms,
            )

        except Exception as e:
            logger.error(f"Market price scraping failed: {e}")
            return ScrapingResult(
                status=ScrapingStatus.FAILED,
                error=str(e),
                duration_ms=(time.time() - start_time) * 1000,
            )

    async def _scrape_mewa_prices(
        self,
        market: str,
        category: str | None,
        crops: list[str] | None,
    ) -> MarketPriceReport:
        """Scrape prices from Saudi Ministry of Environment, Water and Agriculture.

        Args:
            market: Market name.
            category: Crop category filter.
            crops: Specific crops to scrape.

        Returns:
            MarketPriceReport with scraped data.
        """
        url = self.SOURCES["mewa"]

        await self.with_retry(
            "Navigate to MEWA prices page",
            self.navigate,
            url,
            wait_until="networkidle",
        )

        prices: list[CropPrice] = []
        market_info = self.MARKETS.get(market, {"ar": market, "en": market})

        # Extract price table
        try:
            await self.wait_for("table", timeout=10000)
        except Exception:
            logger.debug("Price table not found, trying alternative selectors")

        # Try to find price data in tables
        tables = await self.extract_table("table.price-table, table.data-table, table")

        for row in tables:
            if len(row) < 2:
                continue

            # Parse row data
            crop_name = clean_text(row[0])
            if not crop_name or crop_name.lower() in ["الصنف", "المنتج", "crop", "product"]:
                continue

            # Get translation
            translation = self._translate_crop(crop_name)

            # Extract prices
            price_data = row[1] if len(row) > 1 else ""
            parsed = parse_price(price_data)
            price_value = parsed[0] if parsed else extract_first_number(price_data)
            currency = parsed[1] if parsed else "SAR"

            if price_value is None:
                continue

            # Filter by category if specified
            if category and translation.get("category") != category:
                continue

            # Filter by specific crops if specified
            if crops:
                if not any(c.lower() in crop_name.lower() or c == translation.get("ar") for c in crops):
                    continue

            crop_price = CropPrice(
                crop_name=crop_name,
                crop_name_ar=translation.get("ar"),
                category=translation.get("category"),
                price=price_value,
                currency=currency,
                unit="kg",
                market=market_info.get("en"),
                market_ar=market_info.get("ar"),
                location=normalize_location(market),
                date=datetime.now(),
                source="mewa.gov.sa",
            )

            # Extract min/max if available
            if len(row) > 2:
                crop_price.min_price = extract_first_number(row[2])
            if len(row) > 3:
                crop_price.max_price = extract_first_number(row[3])

            prices.append(crop_price)

        return MarketPriceReport(
            prices=prices,
            market=market_info.get("en"),
            market_ar=market_info.get("ar"),
            location=normalize_location(market),
            date=datetime.now(),
            source="mewa.gov.sa",
        )

    async def _scrape_generic_prices(
        self,
        market: str,
        category: str | None,
        crops: list[str] | None,
    ) -> MarketPriceReport:
        """Generic price scraping for various sources.

        Args:
            market: Market name.
            category: Crop category filter.
            crops: Specific crops to scrape.

        Returns:
            MarketPriceReport with scraped data.
        """
        # This is a fallback implementation that creates sample data
        # In production, this would scrape from actual sources
        prices: list[CropPrice] = []
        market_info = self.MARKETS.get(market, {"ar": market, "en": market})

        # Sample data for demonstration
        sample_prices = [
            ("wheat", 2.5, "grains"),
            ("barley", 2.2, "grains"),
            ("tomato", 4.5, "vegetables"),
            ("cucumber", 3.8, "vegetables"),
            ("onion", 2.8, "vegetables"),
            ("potato", 3.2, "vegetables"),
            ("date", 15.0, "dates"),
            ("apple", 8.5, "fruits"),
            ("orange", 6.0, "fruits"),
        ]

        for crop_name, price_value, crop_category in sample_prices:
            # Filter by category
            if category and crop_category != category:
                continue

            # Filter by specific crops
            if crops and crop_name not in [c.lower() for c in crops]:
                continue

            translation = self._translate_crop(crop_name)

            prices.append(
                CropPrice(
                    crop_name=crop_name,
                    crop_name_ar=translation.get("ar"),
                    category=crop_category,
                    price=price_value,
                    currency="SAR",
                    unit="kg",
                    market=market_info.get("en"),
                    market_ar=market_info.get("ar"),
                    location=normalize_location(market),
                    date=datetime.now(),
                    source="sample_data",
                )
            )

        return MarketPriceReport(
            prices=prices,
            market=market_info.get("en"),
            market_ar=market_info.get("ar"),
            location=normalize_location(market),
            date=datetime.now(),
            source="sample_data",
        )

    async def scrape(self, **kwargs: Any) -> ScrapingResult[MarketPriceReport]:
        """Perform market price scraping.

        Args:
            **kwargs: Scraping parameters (market, category, crops, source).

        Returns:
            ScrapingResult with MarketPriceReport.
        """
        return await self.scrape_prices(**kwargs)

    async def get_price_trends(
        self,
        crop: str,
        market: str = "riyadh",
        days: int = 7,
    ) -> dict[str, Any]:
        """Get price trends for a specific crop.

        Args:
            crop: Crop name.
            market: Market name.
            days: Number of days for trend analysis.

        Returns:
            Dictionary with price trend data.
        """
        result = await self.scrape_prices(market=market, crops=[crop])

        if result.status != ScrapingStatus.SUCCESS or not result.data:
            return {"error": result.error, "status": result.status.value}

        price_info = result.data.get_by_crop(crop)
        if not price_info:
            return {"error": f"Price not found for {crop}"}

        return {
            "crop": crop,
            "crop_ar": price_info.crop_name_ar,
            "current_price": price_info.price,
            "currency": price_info.currency,
            "unit": price_info.unit,
            "market": market,
            "trend": "stable",  # Would calculate from historical data
            "change_percent": price_info.change_percent or 0,
            "last_updated": price_info.date.isoformat() if price_info.date else None,
        }

    async def compare_markets(
        self,
        crop: str,
        markets: list[str] | None = None,
    ) -> dict[str, Any]:
        """Compare prices across multiple markets.

        Args:
            crop: Crop name to compare.
            markets: List of markets to compare.

        Returns:
            Dictionary with market comparison.
        """
        markets = markets or list(self.MARKETS.keys())
        comparison: dict[str, Any] = {
            "crop": crop,
            "markets": [],
            "lowest_price": None,
            "highest_price": None,
            "average_price": None,
        }

        prices = []

        for market in markets:
            result = await self.scrape_prices(market=market, crops=[crop])
            if result.status == ScrapingStatus.SUCCESS and result.data:
                price_info = result.data.get_by_crop(crop)
                if price_info:
                    comparison["markets"].append(
                        {
                            "market": market,
                            "market_ar": price_info.market_ar,
                            "price": price_info.price,
                            "currency": price_info.currency,
                        }
                    )
                    prices.append(price_info.price)

        if prices:
            comparison["lowest_price"] = min(prices)
            comparison["highest_price"] = max(prices)
            comparison["average_price"] = sum(prices) / len(prices)

        return comparison
