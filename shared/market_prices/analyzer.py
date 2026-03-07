"""
Market Price Analyzer
=====================
محلل أسعار السوق

Provides price trend analysis, predictions, market comparisons,
and best selling time recommendations.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import math
from datetime import date, timedelta
from decimal import Decimal
from statistics import mean, median, stdev
from typing import Any

from .models import (
    CROP_TYPES,
    Country,
    Currency,
    MarketComparison,
    MarketPriceErrors,
    MarketPriceException,
    PriceTrend,
    PriceUnit,
    SellingRecommendation,
    TrendDirection,
)
from .tracker import MarketPriceTracker, get_price_tracker


class PriceAnalyzer:
    """
    Analyzer for market price data
    محلل بيانات أسعار السوق

    Features:
    - Price trend analysis
    - Volatility calculation
    - Market comparisons
    - Selling time recommendations
    - Price predictions (simple)

    Usage:
        tracker = MarketPriceTracker(tenant_id="farm_001")
        analyzer = PriceAnalyzer(tracker)

        # Analyze trend
        trend = await analyzer.analyze_trend("wheat", "riyadh_central", days=30)

        # Compare markets
        comparison = await analyzer.compare_markets("wheat")

        # Get selling recommendation
        recommendation = await analyzer.get_selling_recommendation(
            crop_id="wheat",
            quantity=10.0,
            farmer_id="farmer_001",
        )
    """

    # Seasonal price factors for common crops
    # Values > 1.0 indicate higher prices, < 1.0 indicate lower prices
    SEASONAL_FACTORS: dict[str, dict[int, float]] = {
        "wheat": {
            1: 0.95,
            2: 0.92,
            3: 0.90,
            4: 1.05,
            5: 1.10,
            6: 1.15,
            7: 1.10,
            8: 1.05,
            9: 1.00,
            10: 0.95,
            11: 0.92,
            12: 0.95,
        },
        "dates": {
            1: 0.85,
            2: 0.82,
            3: 0.80,
            4: 0.82,
            5: 0.85,
            6: 0.90,
            7: 1.00,
            8: 1.15,
            9: 1.25,
            10: 1.20,
            11: 1.10,
            12: 0.95,
        },
        "tomatoes": {
            1: 1.10,
            2: 1.05,
            3: 0.95,
            4: 0.85,
            5: 0.80,
            6: 0.85,
            7: 0.95,
            8: 1.05,
            9: 1.10,
            10: 1.15,
            11: 1.15,
            12: 1.10,
        },
        "potatoes": {
            1: 1.05,
            2: 1.00,
            3: 0.95,
            4: 0.90,
            5: 0.85,
            6: 0.85,
            7: 0.90,
            8: 0.95,
            9: 1.00,
            10: 1.05,
            11: 1.10,
            12: 1.10,
        },
        "onions": {
            1: 0.95,
            2: 0.90,
            3: 0.85,
            4: 0.85,
            5: 0.90,
            6: 0.95,
            7: 1.00,
            8: 1.05,
            9: 1.10,
            10: 1.15,
            11: 1.10,
            12: 1.00,
        },
    }

    def __init__(self, tracker: MarketPriceTracker | None = None, tenant_id: str = ""):
        """
        Initialize the analyzer

        Args:
            tracker: MarketPriceTracker instance
            tenant_id: Tenant ID (used if tracker not provided)
        """
        if tracker:
            self.tracker = tracker
        elif tenant_id:
            self.tracker = get_price_tracker(tenant_id)
        else:
            raise ValueError("Either tracker or tenant_id must be provided")

    # =========================================================================
    # Trend Analysis
    # =========================================================================

    async def analyze_trend(
        self,
        crop_id: str,
        market_id: str | None = None,
        region_id: str | None = None,
        days: int = 30,
    ) -> PriceTrend:
        """
        Analyze price trend for a crop
        تحليل اتجاه الأسعار لمحصول

        Args:
            crop_id: Crop identifier
            market_id: Optional market filter
            region_id: Optional region filter
            days: Number of days to analyze

        Returns:
            PriceTrend with analysis results
        """
        # Validate crop
        crop_type = CROP_TYPES.get(crop_id)
        if not crop_type:
            raise MarketPriceException(MarketPriceErrors.CROP_NOT_FOUND, f"Crop ID: {crop_id}")

        # Get price history
        prices = await self.tracker.get_price_history(crop_id, market_id, days)

        # Filter by region if specified
        if region_id:
            prices = [p for p in prices if p.region_id == region_id]

        if not prices:
            raise MarketPriceException(
                MarketPriceErrors.NO_PRICE_DATA,
                f"No data for crop {crop_id} in the last {days} days",
            )

        if len(prices) < 2:
            raise MarketPriceException(
                MarketPriceErrors.INSUFFICIENT_DATA,
                f"Need at least 2 data points, found {len(prices)}",
            )

        # Extract price values (convert to float for statistics)
        price_values = [float(p.price) for p in prices]

        # Calculate statistics
        current_price = Decimal(str(price_values[0]))
        previous_price = Decimal(str(price_values[-1]))
        price_change = current_price - previous_price
        price_change_pct = float(price_change / previous_price * 100) if previous_price else 0.0

        period_high = Decimal(str(max(price_values)))
        period_low = Decimal(str(min(price_values)))
        period_avg = Decimal(str(mean(price_values)))
        period_med = Decimal(str(median(price_values)))

        # Calculate standard deviation (volatility measure)
        price_std = stdev(price_values) if len(price_values) > 1 else 0.0

        # Determine trend direction
        direction, strength = self._calculate_trend_direction(price_values)

        # Calculate volatility score (0-100)
        volatility_score = self._calculate_volatility_score(price_values)
        is_volatile = volatility_score > 30

        # Check seasonal factors
        current_month = date.today().month
        seasonal_factors = self.SEASONAL_FACTORS.get(crop_id, {})
        seasonal_factor = seasonal_factors.get(current_month, 1.0)

        # Determine if at seasonal peak or low
        if seasonal_factors:
            max_factor = max(seasonal_factors.values())
            min_factor = min(seasonal_factors.values())
            is_peak = seasonal_factor >= max_factor * 0.95
            is_low = seasonal_factor <= min_factor * 1.05
        else:
            is_peak = False
            is_low = False

        # Simple prediction (extrapolation)
        predicted_direction, predicted_price, confidence = self._predict_price(price_values, days=7)

        trend = PriceTrend(
            crop_id=crop_id,
            crop_name=crop_type.name,
            crop_name_ar=crop_type.name_ar,
            market_id=market_id,
            region_id=region_id,
            direction=direction,
            strength=strength,
            current_price=current_price,
            previous_price=previous_price,
            price_change=price_change,
            price_change_percent=price_change_pct,
            period_high=period_high,
            period_low=period_low,
            period_average=period_avg,
            period_median=period_med,
            period_std_dev=price_std,
            start_date=prices[-1].price_date,
            end_date=prices[0].price_date,
            data_points=len(prices),
            volatility_score=volatility_score,
            is_volatile=is_volatile,
            predicted_direction=predicted_direction,
            predicted_price=predicted_price,
            prediction_confidence=confidence,
            is_seasonal_peak=is_peak,
            is_seasonal_low=is_low,
            seasonal_factor=seasonal_factor,
        )

        return trend

    def _calculate_trend_direction(
        self,
        prices: list[float],
    ) -> tuple[TrendDirection, float]:
        """
        Calculate trend direction and strength
        حساب اتجاه وقوة الاتجاه
        """
        if len(prices) < 2:
            return TrendDirection.UNKNOWN, 0.0

        # Calculate simple linear regression slope
        n = len(prices)
        x_values = list(range(n))
        x_mean = mean(x_values)
        y_mean = mean(prices)

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, prices))
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        if denominator == 0:
            return TrendDirection.STABLE, 0.0

        slope = numerator / denominator

        # Normalize slope to percentage of average price
        slope_pct = (slope / y_mean * 100) if y_mean else 0

        # Determine direction based on slope
        if abs(slope_pct) < 0.5:
            direction = TrendDirection.STABLE
        elif slope_pct > 0:
            direction = TrendDirection.RISING
        else:
            direction = TrendDirection.FALLING

        # Check for volatility (high variance around trend line)
        if len(prices) > 3:
            residuals = []
            for i, price in enumerate(prices):
                predicted = y_mean + slope * (i - x_mean)
                residuals.append((price - predicted) ** 2)
            mse = mean(residuals)
            rmse = math.sqrt(mse)

            # If RMSE is high relative to average, mark as volatile
            if rmse / y_mean > 0.1:  # More than 10% average deviation
                direction = TrendDirection.VOLATILE

        # Calculate strength (0-100)
        strength = min(abs(slope_pct) * 10, 100)

        return direction, strength

    def _calculate_volatility_score(self, prices: list[float]) -> float:
        """
        Calculate volatility score (0-100)
        حساب درجة التقلب
        """
        if len(prices) < 2:
            return 0.0

        avg_price = mean(prices)
        if avg_price == 0:
            return 0.0

        # Calculate coefficient of variation (CV)
        std = stdev(prices)
        cv = (std / avg_price) * 100

        # Calculate max daily change
        daily_changes = []
        for i in range(len(prices) - 1):
            change = abs(prices[i] - prices[i + 1]) / prices[i + 1] * 100
            daily_changes.append(change)

        max_change = max(daily_changes) if daily_changes else 0

        # Combine CV and max change for volatility score
        volatility = cv * 0.6 + max_change * 0.4

        return min(volatility, 100)

    def _predict_price(
        self,
        prices: list[float],
        days: int = 7,
    ) -> tuple[TrendDirection | None, Decimal | None, float]:
        """
        Simple price prediction using linear extrapolation
        تنبؤ بسيط بالأسعار باستخدام الاستقراء الخطي
        """
        if len(prices) < 5:
            return None, None, 0.0

        # Use recent prices for prediction
        recent_prices = prices[: min(14, len(prices))]

        # Calculate linear regression
        n = len(recent_prices)
        x_values = list(range(n))
        x_mean = mean(x_values)
        y_mean = mean(recent_prices)

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, recent_prices))
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        if denominator == 0:
            return None, None, 0.0

        slope = numerator / denominator
        intercept = y_mean - slope * x_mean

        # Predict price for future date
        predicted_x = -days  # Negative because prices are in reverse order
        predicted_value = intercept + slope * predicted_x

        # Ensure prediction is positive
        predicted_value = max(predicted_value, recent_prices[0] * 0.5)

        # Calculate confidence based on R-squared
        y_pred = [intercept + slope * x for x in x_values]
        ss_res = sum((y - yp) ** 2 for y, yp in zip(recent_prices, y_pred))
        ss_tot = sum((y - y_mean) ** 2 for y in recent_prices)

        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        confidence = max(0, min(r_squared * 100, 100))

        # Determine predicted direction
        if predicted_value > recent_prices[0] * 1.02:
            direction = TrendDirection.RISING
        elif predicted_value < recent_prices[0] * 0.98:
            direction = TrendDirection.FALLING
        else:
            direction = TrendDirection.STABLE

        return direction, Decimal(str(round(predicted_value, 2))), confidence

    # =========================================================================
    # Market Comparison
    # =========================================================================

    async def compare_markets(
        self,
        crop_id: str,
        region_ids: list[str] | None = None,
        country: Country | None = None,
        price_date: date | None = None,
    ) -> MarketComparison:
        """
        Compare prices across markets
        مقارنة الأسعار عبر الأسواق

        Args:
            crop_id: Crop identifier
            region_ids: List of regions to compare (None = all)
            country: Filter by country
            price_date: Date for comparison (default: today)

        Returns:
            MarketComparison with results
        """
        # Validate crop
        crop_type = CROP_TYPES.get(crop_id)
        if not crop_type:
            raise MarketPriceException(MarketPriceErrors.CROP_NOT_FOUND, f"Crop ID: {crop_id}")

        price_date = price_date or date.today()

        # Get all markets
        markets = self.tracker.get_markets(country=country)

        if region_ids:
            markets = [m for m in markets if m.region_id in region_ids]

        # Collect prices from each market
        market_prices: list[dict[str, Any]] = []

        for market in markets:
            latest = await self.tracker.get_latest_price(crop_id, market.id)
            if latest and latest.price_date >= price_date - timedelta(days=7):
                market_prices.append(
                    {
                        "market_id": market.id,
                        "market_name": market.name,
                        "market_name_ar": market.name_ar,
                        "region_id": market.region_id,
                        "price": str(latest.price),
                        "price_decimal": latest.price,
                        "unit": latest.unit.value,
                        "currency": latest.currency.value,
                        "price_date": latest.price_date.isoformat(),
                    }
                )

        if not market_prices:
            raise MarketPriceException(MarketPriceErrors.NO_PRICE_DATA, f"No recent price data for {crop_id}")

        # Sort by price (ascending for buying, descending for selling)
        market_prices.sort(key=lambda x: x["price_decimal"])

        # Assign ranks
        for i, mp in enumerate(market_prices):
            mp["rank"] = i + 1

        # Calculate statistics
        prices = [mp["price_decimal"] for mp in market_prices]
        avg_price = Decimal(str(mean([float(p) for p in prices])))

        best = market_prices[-1]  # Highest price (best for selling)
        worst = market_prices[0]  # Lowest price

        price_spread = best["price_decimal"] - worst["price_decimal"]
        price_spread_pct = float(price_spread / worst["price_decimal"] * 100) if worst["price_decimal"] else 0

        # Recommendation (best market for selling)
        potential_gain = best["price_decimal"] - avg_price
        potential_gain_pct = float(potential_gain / avg_price * 100) if avg_price else 0

        # Generate recommendation reason
        reason = f"Highest price at {best['price_decimal']} {best['currency']}/{best['unit']}"
        reason_ar = f"أعلى سعر {best['price_decimal']} {best['currency']}/{best['unit']}"

        if price_spread_pct > 10:
            reason += f". Price spread of {price_spread_pct:.1f}% presents opportunity."
            reason_ar += f". فرق السعر {price_spread_pct:.1f}% يمثل فرصة."

        # Clean up decimal objects for serialization
        for mp in market_prices:
            mp["price"] = str(mp["price_decimal"])
            del mp["price_decimal"]

        comparison = MarketComparison(
            crop_id=crop_id,
            crop_name=crop_type.name,
            crop_name_ar=crop_type.name_ar,
            comparison_date=price_date,
            markets=market_prices,
            best_price_market_id=best["market_id"],
            best_price_market_name=best["market_name"],
            best_price_market_name_ar=best["market_name_ar"],
            best_price=Decimal(best["price"]),
            worst_price_market_id=worst["market_id"],
            worst_price_market_name=worst["market_name"],
            worst_price_market_name_ar=worst["market_name_ar"],
            worst_price=Decimal(worst["price"]),
            average_price=avg_price,
            price_spread=price_spread,
            price_spread_percent=price_spread_pct,
            recommended_market_id=best["market_id"],
            recommended_market_name=best["market_name"],
            recommended_market_name_ar=best["market_name_ar"],
            recommendation_reason=reason,
            recommendation_reason_ar=reason_ar,
            potential_gain=potential_gain,
            potential_gain_percent=potential_gain_pct,
            markets_compared=len(market_prices),
        )

        return comparison

    # =========================================================================
    # Selling Recommendations
    # =========================================================================

    async def get_selling_recommendation(
        self,
        crop_id: str,
        quantity: float = 0.0,
        quantity_unit: PriceUnit = PriceUnit.TON,
        farmer_id: str = "",
        field_id: str = "",
        preferred_region_id: str | None = None,
        max_days_to_wait: int = 30,
    ) -> SellingRecommendation:
        """
        Get recommendation for best selling time
        الحصول على توصية أفضل وقت للبيع

        Args:
            crop_id: Crop identifier
            quantity: Quantity to sell
            quantity_unit: Unit for quantity
            farmer_id: Farmer identifier
            field_id: Field identifier
            preferred_region_id: Preferred region for selling
            max_days_to_wait: Maximum days farmer is willing to wait

        Returns:
            SellingRecommendation with advice
        """
        # Validate crop
        crop_type = CROP_TYPES.get(crop_id)
        if not crop_type:
            raise MarketPriceException(MarketPriceErrors.CROP_NOT_FOUND, f"Crop ID: {crop_id}")

        # Analyze current trend
        try:
            trend = await self.analyze_trend(crop_id, days=30)
        except MarketPriceException:
            # Not enough data for trend analysis
            trend = None

        # Get market comparison
        try:
            comparison = await self.compare_markets(crop_id)
        except MarketPriceException:
            comparison = None

        # Seasonal factors
        current_month = date.today().month
        seasonal_factors = self.SEASONAL_FACTORS.get(crop_id, {})
        current_seasonal = seasonal_factors.get(current_month, 1.0)

        # Find best upcoming month
        best_month = current_month
        best_factor = current_seasonal
        for month_offset in range(1, min(max_days_to_wait // 30 + 1, 4)):
            future_month = ((current_month - 1 + month_offset) % 12) + 1
            future_factor = seasonal_factors.get(future_month, 1.0)
            if future_factor > best_factor:
                best_factor = future_factor
                best_month = future_month

        # Determine action and timing
        reasons = []
        reasons_ar = []
        risks = []
        risks_ar = []
        factors_considered = ["seasonal_trend"]

        # Default values
        action = "sell"
        action_ar = "بيع"
        urgency = "normal"
        urgency_ar = "عادي"
        confidence = 50.0
        recommended_date = date.today()

        # Analyze situation
        if trend:
            factors_considered.append("price_trend")

            if trend.direction == TrendDirection.RISING:
                action = "hold"
                action_ar = "انتظار"
                reasons.append("Prices are currently rising")
                reasons_ar.append("الأسعار في ارتفاع حاليًا")
                confidence += 15

                # Wait for peak
                recommended_date = date.today() + timedelta(days=7)
                risks.append("Prices may peak soon and reverse")
                risks_ar.append("قد تصل الأسعار للذروة وتنعكس قريبًا")

            elif trend.direction == TrendDirection.FALLING:
                action = "sell"
                action_ar = "بيع"
                urgency = "urgent"
                urgency_ar = "عاجل"
                reasons.append("Prices are falling - sell before further decline")
                reasons_ar.append("الأسعار في انخفاض - بيع قبل المزيد من الهبوط")
                confidence += 20

            elif trend.is_volatile:
                risks.append("Market is volatile - prices may change rapidly")
                risks_ar.append("السوق متقلب - الأسعار قد تتغير سريعًا")
                confidence -= 10

        # Seasonal analysis
        if seasonal_factors:
            factors_considered.append("seasonal_pattern")

            if best_factor > current_seasonal * 1.1 and best_month != current_month:
                # Significant improvement expected
                wait_days = (best_month - current_month) * 30
                if wait_days < 0:
                    wait_days += 365

                if wait_days <= max_days_to_wait:
                    action = "wait"
                    action_ar = "انتظار"
                    recommended_date = date.today() + timedelta(days=wait_days)
                    expected_gain_pct = (best_factor - current_seasonal) / current_seasonal * 100

                    reasons.append(f"Seasonal prices typically {expected_gain_pct:.0f}% higher in {wait_days} days")
                    reasons_ar.append(
                        f"الأسعار الموسمية عادة أعلى بنسبة {expected_gain_pct:.0f}% خلال {wait_days} يومًا"
                    )
                    confidence += 10
                else:
                    reasons.append(f"Best seasonal timing too far away ({wait_days} days)")
                    reasons_ar.append(f"أفضل توقيت موسمي بعيد جدًا ({wait_days} يوم)")

            if trend and trend.is_seasonal_peak:
                action = "sell"
                action_ar = "بيع"
                urgency = "urgent"
                urgency_ar = "عاجل"
                reasons.append("Currently at seasonal price peak")
                reasons_ar.append("حاليًا في ذروة الأسعار الموسمية")
                confidence += 15

            if trend and trend.is_seasonal_low:
                action = "hold"
                action_ar = "انتظار"
                reasons.append("Currently at seasonal price low")
                reasons_ar.append("حاليًا في أدنى الأسعار الموسمية")
                risks.append("Storage costs will accumulate while waiting")
                risks_ar.append("تكاليف التخزين ستتراكم أثناء الانتظار")

        # Market recommendation
        recommended_market_id = ""
        recommended_market_name = ""
        recommended_market_name_ar = ""

        if comparison:
            factors_considered.append("market_comparison")
            recommended_market_id = comparison.recommended_market_id
            recommended_market_name = comparison.recommended_market_name
            recommended_market_name_ar = comparison.recommended_market_name_ar

            if comparison.price_spread_percent > 15:
                reasons.append(f"Price difference of {comparison.price_spread_percent:.0f}% between markets")
                reasons_ar.append(f"فرق سعر {comparison.price_spread_percent:.0f}% بين الأسواق")

        elif preferred_region_id:
            # Use preferred region's market
            region_markets = self.tracker.get_markets(region_id=preferred_region_id)
            if region_markets:
                recommended_market_id = region_markets[0].id
                recommended_market_name = region_markets[0].name
                recommended_market_name_ar = region_markets[0].name_ar

        # Calculate expected prices and revenue
        current_price = trend.current_price if trend else Decimal("0")
        expected_price = current_price

        if action == "wait" and trend and trend.predicted_price:
            # Adjust expected price based on prediction and seasonal factor
            adjustment = Decimal(str(best_factor / current_seasonal))
            expected_price = current_price * adjustment

        # Revenue calculations
        estimated_revenue = expected_price * Decimal(str(quantity))
        current_revenue = current_price * Decimal(str(quantity))
        potential_additional = estimated_revenue - current_revenue

        # Normalize confidence
        confidence = max(20, min(confidence, 95))

        # Set date range
        if action == "sell":
            date_range_start = date.today()
            date_range_end = date.today() + timedelta(days=7)
        elif action == "wait":
            date_range_start = recommended_date - timedelta(days=7)
            date_range_end = recommended_date + timedelta(days=7)
        else:  # hold
            date_range_start = date.today() + timedelta(days=3)
            date_range_end = date.today() + timedelta(days=14)

        recommendation = SellingRecommendation(
            crop_id=crop_id,
            crop_name=crop_type.name,
            crop_name_ar=crop_type.name_ar,
            farmer_id=farmer_id,
            field_id=field_id,
            action=action,
            action_ar=action_ar,
            confidence=confidence,
            recommended_date=recommended_date,
            recommended_date_range_start=date_range_start,
            recommended_date_range_end=date_range_end,
            urgency=urgency,
            urgency_ar=urgency_ar,
            recommended_market_id=recommended_market_id,
            recommended_market_name=recommended_market_name,
            recommended_market_name_ar=recommended_market_name_ar,
            expected_price=expected_price,
            expected_price_range_low=expected_price * Decimal("0.95"),
            expected_price_range_high=expected_price * Decimal("1.05"),
            current_price=current_price,
            price_unit=crop_type.default_unit,
            currency=Currency.SAR,
            quantity_to_sell=quantity,
            quantity_unit=quantity_unit,
            estimated_revenue=estimated_revenue,
            potential_additional_revenue=potential_additional,
            reasons=reasons,
            reasons_ar=reasons_ar,
            risks=risks,
            risks_ar=risks_ar,
            factors_considered=factors_considered,
            valid_until=date.today() + timedelta(days=7),
        )

        return recommendation

    # =========================================================================
    # Utility Methods
    # =========================================================================

    async def get_price_statistics(
        self,
        crop_id: str,
        market_id: str | None = None,
        days: int = 30,
    ) -> dict[str, Any]:
        """
        Get price statistics summary
        الحصول على ملخص إحصائيات الأسعار

        Args:
            crop_id: Crop identifier
            market_id: Optional market filter
            days: Period for statistics

        Returns:
            Dictionary with statistics
        """
        prices = await self.tracker.get_price_history(crop_id, market_id, days)

        if not prices:
            return {
                "crop_id": crop_id,
                "data_points": 0,
                "period_days": days,
            }

        price_values = [float(p.price) for p in prices]

        stats = {
            "crop_id": crop_id,
            "market_id": market_id,
            "data_points": len(prices),
            "period_days": days,
            "start_date": prices[-1].price_date.isoformat(),
            "end_date": prices[0].price_date.isoformat(),
            "current": str(prices[0].price),
            "high": str(max(price_values)),
            "low": str(min(price_values)),
            "average": str(round(mean(price_values), 2)),
            "median": str(round(median(price_values), 2)),
            "std_dev": str(round(stdev(price_values), 2)) if len(price_values) > 1 else "0",
            "unit": prices[0].unit.value,
            "currency": prices[0].currency.value,
        }

        # Add change metrics
        if len(prices) >= 2:
            change = float(prices[0].price) - float(prices[-1].price)
            change_pct = (change / float(prices[-1].price) * 100) if prices[-1].price else 0
            stats["change"] = str(round(change, 2))
            stats["change_percent"] = round(change_pct, 2)

        return stats

    async def get_volatility_report(
        self,
        crop_ids: list[str] | None = None,
        days: int = 30,
    ) -> list[dict[str, Any]]:
        """
        Get volatility report for multiple crops
        الحصول على تقرير التقلب لمحاصيل متعددة

        Args:
            crop_ids: List of crops to analyze (None = all)
            days: Period for analysis

        Returns:
            List of volatility data per crop
        """
        if crop_ids is None:
            crop_ids = list(CROP_TYPES.keys())

        results = []

        for crop_id in crop_ids:
            try:
                trend = await self.analyze_trend(crop_id, days=days)
                results.append(
                    {
                        "crop_id": crop_id,
                        "crop_name": trend.crop_name,
                        "crop_name_ar": trend.crop_name_ar,
                        "volatility_score": trend.volatility_score,
                        "is_volatile": trend.is_volatile,
                        "direction": trend.direction.value,
                        "change_percent": trend.price_change_percent,
                        "data_points": trend.data_points,
                    }
                )
            except MarketPriceException:
                # Skip crops without data
                continue

        # Sort by volatility score descending
        results.sort(key=lambda x: x["volatility_score"], reverse=True)

        return results


# Convenience functions
_analyzers: dict[str, PriceAnalyzer] = {}


def get_price_analyzer(tenant_id: str) -> PriceAnalyzer:
    """Get or create a price analyzer for a tenant"""
    if tenant_id not in _analyzers:
        _analyzers[tenant_id] = PriceAnalyzer(tenant_id=tenant_id)
    return _analyzers[tenant_id]


async def analyze_price_trend(
    tenant_id: str,
    crop_id: str,
    market_id: str | None = None,
    days: int = 30,
) -> PriceTrend:
    """Analyze price trend using the default analyzer"""
    analyzer = get_price_analyzer(tenant_id)
    return await analyzer.analyze_trend(crop_id, market_id, days=days)


async def compare_crop_markets(
    tenant_id: str,
    crop_id: str,
    country: Country | None = None,
) -> MarketComparison:
    """Compare markets using the default analyzer"""
    analyzer = get_price_analyzer(tenant_id)
    return await analyzer.compare_markets(crop_id, country=country)


async def get_selling_advice(
    tenant_id: str,
    crop_id: str,
    quantity: float = 0.0,
    farmer_id: str = "",
) -> SellingRecommendation:
    """Get selling recommendation using the default analyzer"""
    analyzer = get_price_analyzer(tenant_id)
    return await analyzer.get_selling_recommendation(
        crop_id=crop_id,
        quantity=quantity,
        farmer_id=farmer_id,
    )
