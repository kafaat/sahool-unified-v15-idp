"""
Inventory Analytics and Forecasting
تحليلات وتوقعات المخزون

Comprehensive analytics for agricultural inventory management:
- Consumption forecasting
- Inventory valuation (FIFO, weighted average)
- ABC/Pareto analysis
- Turnover ratio calculation
- Slow-moving and dead stock identification
- Reorder point optimization
- Cost analysis by field/crop
- Waste tracking
"""

import statistics
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models.inventory import (
    InventoryItem,
    InventoryMovement,
    InventoryTransaction,
    ItemCategory,
    MovementType,
    Supplier,
    TransactionType,
    Warehouse,
)


@dataclass
class ConsumptionForecast:
    """Forecast for item consumption"""

    item_id: str
    item_name: str
    current_stock: float
    avg_daily_consumption: float
    avg_weekly_consumption: float
    avg_monthly_consumption: float
    days_until_stockout: int
    reorder_date: date
    recommended_order_qty: float
    confidence: float

    def to_dict(self) -> dict:
        result = asdict(self)
        result["reorder_date"] = self.reorder_date.isoformat()
        return result


@dataclass
class InventoryValuation:
    """Inventory valuation breakdown"""

    total_value: float
    currency: str
    by_category: dict[str, float]
    by_warehouse: dict[str, float]
    top_items: list[dict]  # [{item, value, percentage}]
    expiring_value: float  # Value of items expiring in 30 days

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TurnoverMetrics:
    """Inventory turnover metrics for an item"""

    item_id: str
    item_name: str
    turnover_ratio: float  # Annual turnover
    days_of_inventory: float  # Average days in stock
    velocity: str  # "fast", "medium", "slow", "dead"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SeasonalPattern:
    """Seasonal consumption patterns"""

    item_id: str
    item_name: str
    peak_months: list[int]  # 1-12
    low_months: list[int]
    seasonal_factor: dict[int, float]  # month -> multiplier

    def to_dict(self) -> dict:
        return asdict(self)


class InventoryAnalytics:
    """Comprehensive inventory analytics and forecasting"""

    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id

    async def get_consumption_forecast(
        self, item_id: str, forecast_days: int = 90
    ) -> ConsumptionForecast | None:
        """
        Forecast future consumption based on historical data.
        Uses moving average and seasonal adjustment.
        """
        # Get item details
        item = await self.db.get(InventoryItem, item_id)
        if not item or item.tenant_id != self.tenant_id:
            return None

        # Calculate consumption from movements (last 90 days)
        lookback_date = datetime.now() - timedelta(days=90)

        # Get issue movements (consumption)
        stmt = (
            select(
                func.date_trunc("day", InventoryMovement.movement_date).label("day"),
                func.sum(InventoryMovement.quantity).label("total_qty"),
            )
            .where(
                and_(
                    InventoryMovement.tenant_id == self.tenant_id,
                    InventoryMovement.item_id == item_id,
                    InventoryMovement.movement_type == MovementType.ISSUE,
                    InventoryMovement.movement_date >= lookback_date,
                )
            )
            .group_by("day")
        )

        result = await self.db.execute(stmt)
        daily_consumption = {row.day.date(): float(row.total_qty) for row in result}

        if not daily_consumption:
            # No consumption history
            return ConsumptionForecast(
                item_id=str(item.id),
                item_name=item.name_en,
                current_stock=item.current_stock,
                avg_daily_consumption=0.0,
                avg_weekly_consumption=0.0,
                avg_monthly_consumption=0.0,
                days_until_stockout=999,
                reorder_date=date.today() + timedelta(days=999),
                recommended_order_qty=item.reorder_quantity,
                confidence=0.0,
            )

        # Calculate averages
        total_consumption = sum(daily_consumption.values())
        days_with_data = len(daily_consumption)

        # Prevent division by zero
        avg_daily = total_consumption / max(days_with_data, 1)
        avg_weekly = avg_daily * 7
        avg_monthly = avg_daily * 30

        # Calculate days until stockout - prevent division by zero
        days_until_stockout = int(item.available_stock / avg_daily) if avg_daily > 0 else 999

        # Calculate reorder date (considering lead time)
        supplier_lead_time = 7  # Default
        if item.supplier:
            supplier = await self.db.get(Supplier, item.supplier_id)
            if supplier:
                supplier_lead_time = supplier.lead_time_days

        safety_stock_days = 7  # Buffer
        reorder_days = max(0, days_until_stockout - supplier_lead_time - safety_stock_days)
        reorder_date = date.today() + timedelta(days=reorder_days)

        # Recommended order quantity
        # Order enough for forecast_days plus safety stock
        recommended_qty = (avg_daily * forecast_days) + (avg_daily * safety_stock_days)

        # Confidence based on data consistency
        if days_with_data >= 30:
            # Calculate coefficient of variation
            values = list(daily_consumption.values())
            if len(values) > 1 and avg_daily > 0:
                std_dev = statistics.stdev(values)
                cv = std_dev / avg_daily  # avg_daily > 0 checked above
                confidence = max(0.0, min(1.0, 1.0 - (cv / 2)))
            else:
                confidence = 0.5
        else:
            confidence = 0.3  # Low confidence with little data

        return ConsumptionForecast(
            item_id=str(item.id),
            item_name=item.name_en,
            current_stock=item.current_stock,
            avg_daily_consumption=round(avg_daily, 2),
            avg_weekly_consumption=round(avg_weekly, 2),
            avg_monthly_consumption=round(avg_monthly, 2),
            days_until_stockout=days_until_stockout,
            reorder_date=reorder_date,
            recommended_order_qty=round(recommended_qty, 2),
            confidence=round(confidence, 2),
        )

    async def get_all_forecasts(
        self, category: str | None = None, low_stock_only: bool = False
    ) -> list[ConsumptionForecast]:
        """Get forecasts for all items or filtered subset"""
        # Build query
        stmt = select(InventoryItem).where(
            and_(
                InventoryItem.tenant_id == self.tenant_id,
                InventoryItem.is_active is True,
            )
        )

        if category:
            stmt = stmt.join(ItemCategory).where(ItemCategory.code == category)

        if low_stock_only:
            stmt = stmt.where(InventoryItem.current_stock <= InventoryItem.reorder_level)

        result = await self.db.execute(stmt)
        items = result.scalars().all()

        forecasts = []
        for item in items:
            forecast = await self.get_consumption_forecast(str(item.id))
            if forecast:
                forecasts.append(forecast)

        return forecasts

    async def get_inventory_valuation(
        self, as_of_date: date | None = None, warehouse_id: str | None = None
    ) -> InventoryValuation:
        """Calculate total inventory value with breakdowns"""
        if as_of_date is None:
            as_of_date = date.today()

        # Build base query
        stmt = (
            select(
                InventoryItem,
                ItemCategory.name_en.label("category_name"),
                Warehouse.name.label("warehouse_name"),
            )
            .join(ItemCategory)
            .outerjoin(Warehouse)
            .where(
                and_(
                    InventoryItem.tenant_id == self.tenant_id,
                    InventoryItem.is_active is True,
                )
            )
        )

        if warehouse_id:
            stmt = stmt.where(InventoryItem.warehouse_id == warehouse_id)

        result = await self.db.execute(stmt)
        rows = result.all()

        total_value = 0.0
        by_category = {}
        by_warehouse = {}
        item_values = []
        expiring_value = 0.0

        expiring_threshold = as_of_date + timedelta(days=30)

        for row in rows:
            item = row.InventoryItem
            category_name = row.category_name
            warehouse_name = row.warehouse_name or "Unassigned"

            item_value = float(item.current_stock * item.average_cost)
            total_value += item_value

            # By category
            by_category[category_name] = by_category.get(category_name, 0.0) + item_value

            # By warehouse
            by_warehouse[warehouse_name] = by_warehouse.get(warehouse_name, 0.0) + item_value

            # Track for top items
            item_values.append(
                {
                    "item_id": str(item.id),
                    "item_name": item.name_en,
                    "value": round(item_value, 2),
                    "quantity": item.current_stock,
                    "unit_cost": float(item.average_cost),
                }
            )

            # Expiring items
            if item.has_expiry and item.expiry_date and item.expiry_date <= expiring_threshold:
                expiring_value += item_value

        # Sort and get top items
        item_values.sort(key=lambda x: x["value"], reverse=True)
        top_items = item_values[:10]

        # Add percentages - prevent division by zero
        for item in top_items:
            item["percentage"] = (
                round((item["value"] / total_value * 100), 2) if total_value > 0 else 0.0
            )

        return InventoryValuation(
            total_value=round(total_value, 2),
            currency="YER",  # Yemeni Rial
            by_category={k: round(v, 2) for k, v in by_category.items()},
            by_warehouse={k: round(v, 2) for k, v in by_warehouse.items()},
            top_items=top_items,
            expiring_value=round(expiring_value, 2),
        )

    async def get_turnover_analysis(self, period_days: int = 365) -> list[TurnoverMetrics]:
        """
        Analyze inventory turnover.

        Turnover Ratio = Cost of Goods Used / Average Inventory Value
        Days of Inventory = 365 / Turnover Ratio
        """
        start_date = datetime.now() - timedelta(days=period_days)

        # Get all active items
        items_stmt = select(InventoryItem).where(
            and_(
                InventoryItem.tenant_id == self.tenant_id,
                InventoryItem.is_active is True,
            )
        )
        items_result = await self.db.execute(items_stmt)
        items = items_result.scalars().all()

        metrics = []

        for item in items:
            # Calculate total cost of goods used (issued)
            cogs_stmt = select(func.sum(InventoryMovement.total_cost)).where(
                and_(
                    InventoryMovement.tenant_id == self.tenant_id,
                    InventoryMovement.item_id == item.id,
                    InventoryMovement.movement_type == MovementType.ISSUE,
                    InventoryMovement.movement_date >= start_date,
                )
            )
            cogs_result = await self.db.execute(cogs_stmt)
            cogs = cogs_result.scalar() or Decimal("0.0")

            # Average inventory value (simplified: current stock * average cost)
            avg_inventory_value = item.current_stock * item.average_cost

            # Calculate turnover ratio - prevent division by zero
            if avg_inventory_value > 0:
                turnover_ratio = float(cogs / avg_inventory_value)
                days_of_inventory = 365 / turnover_ratio if turnover_ratio > 0 else 999.0
            else:
                turnover_ratio = 0.0
                days_of_inventory = 999.0

            # Classify velocity
            if turnover_ratio >= 4:  # Turns over 4+ times per year
                velocity = "fast"
            elif turnover_ratio >= 2:
                velocity = "medium"
            elif turnover_ratio >= 0.5:
                velocity = "slow"
            else:
                velocity = "dead"

            metrics.append(
                TurnoverMetrics(
                    item_id=str(item.id),
                    item_name=item.name_en,
                    turnover_ratio=round(turnover_ratio, 2),
                    days_of_inventory=round(days_of_inventory, 1),
                    velocity=velocity,
                )
            )

        return metrics

    async def identify_slow_moving(self, days_threshold: int = 90) -> list[dict]:
        """Identify items with no movement in N days"""
        datetime.now() - timedelta(days=days_threshold)

        # Get items with last movement before threshold
        stmt = (
            select(
                InventoryItem,
                func.max(InventoryMovement.movement_date).label("last_movement"),
            )
            .outerjoin(
                InventoryMovement,
                and_(
                    InventoryMovement.item_id == InventoryItem.id,
                    InventoryMovement.movement_type == MovementType.ISSUE,
                ),
            )
            .where(
                and_(
                    InventoryItem.tenant_id == self.tenant_id,
                    InventoryItem.is_active is True,
                    InventoryItem.current_stock > 0,
                )
            )
            .group_by(InventoryItem.id)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        slow_moving = []
        for row in rows:
            item = row.InventoryItem
            last_movement = row.last_movement

            days_since_movement = 999
            if last_movement:
                days_since_movement = (datetime.now() - last_movement).days

            if last_movement is None or days_since_movement >= days_threshold:
                item_value = float(item.current_stock * item.average_cost)

                slow_moving.append(
                    {
                        "item_id": str(item.id),
                        "item_name": item.name_en,
                        "sku": item.sku,
                        "current_stock": item.current_stock,
                        "unit_cost": float(item.average_cost),
                        "total_value": round(item_value, 2),
                        "last_movement_date": (
                            last_movement.date().isoformat() if last_movement else None
                        ),
                        "days_since_movement": days_since_movement,
                    }
                )

        # Sort by value (highest first)
        slow_moving.sort(key=lambda x: x["total_value"], reverse=True)

        return slow_moving

    async def identify_dead_stock(self, days_threshold: int = 180) -> list[dict]:
        """
        Identify dead stock (no movement + near expiry or very long time)
        """
        datetime.now() - timedelta(days=days_threshold)
        expiry_threshold = date.today() + timedelta(days=60)

        stmt = (
            select(
                InventoryItem,
                func.max(InventoryMovement.movement_date).label("last_movement"),
            )
            .outerjoin(
                InventoryMovement,
                and_(
                    InventoryMovement.item_id == InventoryItem.id,
                    InventoryMovement.movement_type == MovementType.ISSUE,
                ),
            )
            .where(
                and_(
                    InventoryItem.tenant_id == self.tenant_id,
                    InventoryItem.is_active is True,
                    InventoryItem.current_stock > 0,
                )
            )
            .group_by(InventoryItem.id)
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        dead_stock = []
        for row in rows:
            item = row.InventoryItem
            last_movement = row.last_movement

            days_since_movement = 999
            if last_movement:
                days_since_movement = (datetime.now() - last_movement).days

            # Criteria: No movement for 180+ days OR expiring within 60 days
            is_dead = False
            reason = ""

            if last_movement is None or days_since_movement >= days_threshold:
                is_dead = True
                reason = f"No movement for {days_since_movement} days"

            if item.has_expiry and item.expiry_date and item.expiry_date <= expiry_threshold:
                is_dead = True
                days_to_expiry = (item.expiry_date - date.today()).days
                if reason:
                    reason += f" and expiring in {days_to_expiry} days"
                else:
                    reason = f"Expiring in {days_to_expiry} days"

            if is_dead:
                item_value = float(item.current_stock * item.average_cost)

                dead_stock.append(
                    {
                        "item_id": str(item.id),
                        "item_name": item.name_en,
                        "sku": item.sku,
                        "current_stock": item.current_stock,
                        "unit_cost": float(item.average_cost),
                        "total_value": round(item_value, 2),
                        "reason": reason,
                        "expiry_date": (item.expiry_date.isoformat() if item.expiry_date else None),
                        "last_movement_date": (
                            last_movement.date().isoformat() if last_movement else None
                        ),
                    }
                )

        # Sort by value
        dead_stock.sort(key=lambda x: x["total_value"], reverse=True)

        return dead_stock

    async def get_seasonal_patterns(self, item_id: str) -> SeasonalPattern | None:
        """Analyze seasonal consumption patterns"""
        # Get 2 years of history
        lookback_date = datetime.now() - timedelta(days=730)

        stmt = (
            select(
                func.extract("month", InventoryMovement.movement_date).label("month"),
                func.sum(InventoryMovement.quantity).label("total_qty"),
                func.count(InventoryMovement.id).label("count"),
            )
            .where(
                and_(
                    InventoryMovement.tenant_id == self.tenant_id,
                    InventoryMovement.item_id == item_id,
                    InventoryMovement.movement_type == MovementType.ISSUE,
                    InventoryMovement.movement_date >= lookback_date,
                )
            )
            .group_by("month")
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        if not rows:
            return None

        # Get item name
        item = await self.db.get(InventoryItem, item_id)
        if not item:
            return None

        # Calculate monthly consumption
        monthly_consumption = {int(row.month): float(row.total_qty) for row in rows}

        # Calculate average - prevent division by zero
        avg_consumption = sum(monthly_consumption.values()) / max(len(monthly_consumption), 1)

        # Calculate seasonal factors (relative to average) - prevent division by zero
        seasonal_factor = {}
        for month, consumption in monthly_consumption.items():
            seasonal_factor[month] = (
                round(consumption / avg_consumption, 2) if avg_consumption > 0 else 1.0
            )

        # Identify peak and low months
        sorted_months = sorted(seasonal_factor.items(), key=lambda x: x[1], reverse=True)
        peak_months = [m for m, f in sorted_months[:3] if f > 1.2]
        low_months = [m for m, f in sorted_months[-3:] if f < 0.8]

        return SeasonalPattern(
            item_id=str(item.id),
            item_name=item.name_en,
            peak_months=peak_months,
            low_months=low_months,
            seasonal_factor=seasonal_factor,
        )

    async def get_reorder_recommendations(self) -> list[dict]:
        """
        Get items that need reordering.
        Considers:
        - Current stock vs reorder level
        - Forecast consumption
        - Lead time from supplier
        - Seasonal demand
        """
        # Get items below reorder level
        stmt = (
            select(InventoryItem, Supplier)
            .outerjoin(Supplier, InventoryItem.supplier_id == Supplier.id)
            .where(
                and_(
                    InventoryItem.tenant_id == self.tenant_id,
                    InventoryItem.is_active is True,
                    InventoryItem.available_stock <= InventoryItem.reorder_level,
                )
            )
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        recommendations = []
        for row in rows:
            item = row.InventoryItem
            supplier = row.Supplier

            # Get forecast
            forecast = await self.get_consumption_forecast(str(item.id))

            recommendations.append(
                {
                    "item_id": str(item.id),
                    "item_name": item.name_en,
                    "sku": item.sku,
                    "current_stock": item.current_stock,
                    "available_stock": item.available_stock,
                    "reorder_level": item.reorder_level,
                    "reorder_quantity": item.reorder_quantity,
                    "recommended_order_qty": (
                        forecast.recommended_order_qty if forecast else item.reorder_quantity
                    ),
                    "days_until_stockout": (forecast.days_until_stockout if forecast else 0),
                    "supplier_name": supplier.name if supplier else None,
                    "lead_time_days": supplier.lead_time_days if supplier else 7,
                    "urgency": (
                        "critical"
                        if item.available_stock <= 0
                        else (
                            "high" if forecast and forecast.days_until_stockout <= 7 else "medium"
                        )
                    ),
                }
            )

        # Sort by urgency
        urgency_order = {"critical": 0, "high": 1, "medium": 2}
        recommendations.sort(key=lambda x: urgency_order.get(x["urgency"], 3))

        return recommendations

    async def get_abc_analysis(self) -> dict:
        """
        ABC analysis (Pareto):
        - A items: 80% of value (top ~20%)
        - B items: 15% of value (next ~30%)
        - C items: 5% of value (bottom ~50%)
        """
        # Get all items with their values
        stmt = select(InventoryItem).where(
            and_(
                InventoryItem.tenant_id == self.tenant_id,
                InventoryItem.is_active is True,
            )
        )

        result = await self.db.execute(stmt)
        items = result.scalars().all()

        # Calculate values
        item_values = []
        total_value = 0.0

        for item in items:
            value = float(item.current_stock * item.average_cost)
            total_value += value
            item_values.append(
                {
                    "item_id": str(item.id),
                    "item_name": item.name_en,
                    "sku": item.sku,
                    "stock": item.current_stock,
                    "value": value,
                }
            )

        # Sort by value (descending)
        item_values.sort(key=lambda x: x["value"], reverse=True)

        # Classify into ABC
        cumulative_value = 0.0
        a_items = []
        b_items = []
        c_items = []

        for item in item_values:
            cumulative_value += item["value"]
            # Prevent division by zero
            percentage = (cumulative_value / total_value * 100) if total_value > 0 else 0.0

            item["cumulative_value"] = round(cumulative_value, 2)
            item["cumulative_percentage"] = round(percentage, 2)
            item["value"] = round(item["value"], 2)

            if percentage <= 80:
                item["class"] = "A"
                a_items.append(item)
            elif percentage <= 95:
                item["class"] = "B"
                b_items.append(item)
            else:
                item["class"] = "C"
                c_items.append(item)

        return {
            "total_value": round(total_value, 2),
            "total_items": len(item_values),
            "a_class": {
                "items": a_items,
                "count": len(a_items),
                "percentage_of_items": (
                    round(len(a_items) / len(item_values) * 100, 1) if item_values else 0
                ),
                "value": round(sum(i["value"] for i in a_items), 2),
                "percentage_of_value": (
                    round(sum(i["value"] for i in a_items) / total_value * 100, 1)
                    if total_value > 0
                    else 0
                ),
            },
            "b_class": {
                "items": b_items,
                "count": len(b_items),
                "percentage_of_items": (
                    round(len(b_items) / len(item_values) * 100, 1) if item_values else 0
                ),
                "value": round(sum(i["value"] for i in b_items), 2),
                "percentage_of_value": (
                    round(sum(i["value"] for i in b_items) / total_value * 100, 1)
                    if total_value > 0
                    else 0
                ),
            },
            "c_class": {
                "items": c_items,
                "count": len(c_items),
                "percentage_of_items": (
                    round(len(c_items) / len(item_values) * 100, 1) if item_values else 0
                ),
                "value": round(sum(i["value"] for i in c_items), 2),
                "percentage_of_value": (
                    round(sum(i["value"] for i in c_items) / total_value * 100, 1)
                    if total_value > 0
                    else 0
                ),
            },
        }

    async def get_cost_analysis(
        self,
        field_id: str | None = None,
        crop_season_id: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> dict:
        """
        Analyze input costs:
        - By category (fertilizer, pesticide, etc.)
        - By field
        - By crop
        - Trend over time
        """
        if start_date is None:
            start_date = date.today() - timedelta(days=365)
        if end_date is None:
            end_date = date.today()

        # Build query for transactions
        conditions = [
            InventoryTransaction.tenant_id == self.tenant_id,
            InventoryTransaction.transaction_date
            >= datetime.combine(start_date, datetime.min.time()),
            InventoryTransaction.transaction_date
            <= datetime.combine(end_date, datetime.max.time()),
            InventoryTransaction.transaction_type == TransactionType.USE,
        ]

        if field_id:
            conditions.append(InventoryTransaction.field_id == field_id)

        if crop_season_id:
            conditions.append(InventoryTransaction.crop_season_id == crop_season_id)

        # Get transactions with item details
        stmt = (
            select(InventoryTransaction, InventoryItem, ItemCategory)
            .join(InventoryItem, InventoryTransaction.item_id == InventoryItem.id)
            .join(ItemCategory, InventoryItem.category_id == ItemCategory.id)
            .where(and_(*conditions))
        )

        result = await self.db.execute(stmt)
        rows = result.all()

        # Analyze
        total_cost = Decimal("0.0")
        by_category = {}
        by_field = {}
        by_crop = {}
        monthly_trend = {}

        for row in rows:
            txn = row.InventoryTransaction
            category = row.ItemCategory

            cost = txn.total_amount + txn.additional_costs
            total_cost += cost

            # By category
            cat_name = category.name_en
            by_category[cat_name] = by_category.get(cat_name, Decimal("0.0")) + cost

            # By field
            if txn.field_id:
                by_field[txn.field_id] = by_field.get(txn.field_id, Decimal("0.0")) + cost

            # By crop
            if txn.crop_season_id:
                by_crop[txn.crop_season_id] = by_crop.get(txn.crop_season_id, Decimal("0.0")) + cost

            # Monthly trend
            month_key = txn.transaction_date.strftime("%Y-%m")
            monthly_trend[month_key] = monthly_trend.get(month_key, Decimal("0.0")) + cost

        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "total_cost": float(total_cost),
            "by_category": {k: float(v) for k, v in by_category.items()},
            "by_field": {k: float(v) for k, v in by_field.items()},
            "by_crop_season": {k: float(v) for k, v in by_crop.items()},
            "monthly_trend": {k: float(v) for k, v in sorted(monthly_trend.items())},
        }

    async def get_waste_analysis(self, period_days: int = 365) -> dict:
        """
        Analyze inventory waste:
        - Expired items
        - Damaged items
        - Returns
        - Write-offs
        """
        start_date = datetime.now() - timedelta(days=period_days)

        # Get write-off movements
        writeoff_stmt = (
            select(InventoryMovement, InventoryItem, ItemCategory)
            .join(InventoryItem, InventoryMovement.item_id == InventoryItem.id)
            .join(ItemCategory, InventoryItem.category_id == ItemCategory.id)
            .where(
                and_(
                    InventoryMovement.tenant_id == self.tenant_id,
                    InventoryMovement.movement_type == MovementType.WRITE_OFF,
                    InventoryMovement.movement_date >= start_date,
                )
            )
        )

        result = await self.db.execute(writeoff_stmt)
        rows = result.all()

        total_waste_qty = 0.0
        total_waste_value = Decimal("0.0")
        by_category = {}
        waste_items = []

        for row in rows:
            movement = row.InventoryMovement
            item = row.InventoryItem
            category = row.ItemCategory

            qty = movement.quantity
            value = movement.total_cost

            total_waste_qty += qty
            total_waste_value += value

            # By category
            cat_name = category.name_en
            if cat_name not in by_category:
                by_category[cat_name] = {"quantity": 0.0, "value": 0.0, "count": 0}

            by_category[cat_name]["quantity"] += qty
            by_category[cat_name]["value"] += float(value)
            by_category[cat_name]["count"] += 1

            waste_items.append(
                {
                    "date": movement.movement_date.date().isoformat(),
                    "item_name": item.name_en,
                    "category": cat_name,
                    "quantity": qty,
                    "unit_cost": float(movement.unit_cost),
                    "total_value": float(value),
                    "reason": movement.notes or "Not specified",
                }
            )

        # Get currently expired items
        expired_items = []
        expired_stmt = (
            select(InventoryItem, ItemCategory)
            .join(ItemCategory)
            .where(
                and_(
                    InventoryItem.tenant_id == self.tenant_id,
                    InventoryItem.is_active is True,
                    InventoryItem.has_expiry is True,
                    InventoryItem.expiry_date <= date.today(),
                    InventoryItem.current_stock > 0,
                )
            )
        )

        expired_result = await self.db.execute(expired_stmt)
        expired_rows = expired_result.all()

        expired_value = Decimal("0.0")
        for row in expired_rows:
            item = row.InventoryItem
            category = row.ItemCategory

            value = item.current_stock * item.average_cost
            expired_value += value

            expired_items.append(
                {
                    "item_id": str(item.id),
                    "item_name": item.name_en,
                    "category": category.name_en,
                    "quantity": item.current_stock,
                    "unit_cost": float(item.average_cost),
                    "total_value": float(value),
                    "expiry_date": item.expiry_date.isoformat(),
                }
            )

        return {
            "period_days": period_days,
            "total_writeoffs": {
                "quantity": round(total_waste_qty, 2),
                "value": float(total_waste_value),
                "count": len(waste_items),
            },
            "by_category": {
                k: {
                    "quantity": round(v["quantity"], 2),
                    "value": round(v["value"], 2),
                    "count": v["count"],
                }
                for k, v in by_category.items()
            },
            "writeoff_items": waste_items[-20:],  # Last 20
            "currently_expired": {
                "count": len(expired_items),
                "value": float(expired_value),
                "items": expired_items,
            },
        }

    async def generate_dashboard_metrics(self) -> dict:
        """
        Generate key metrics for dashboard:
        - Total SKUs
        - Total inventory value
        - Low stock count
        - Expiring soon count
        - Turnover rate
        - Top consumed items
        - Recent movements
        """
        # Total SKUs
        total_skus_stmt = select(func.count(InventoryItem.id)).where(
            and_(
                InventoryItem.tenant_id == self.tenant_id,
                InventoryItem.is_active is True,
            )
        )
        total_skus = (await self.db.execute(total_skus_stmt)).scalar() or 0

        # Total inventory value
        valuation = await self.get_inventory_valuation()

        # Low stock count
        low_stock_stmt = select(func.count(InventoryItem.id)).where(
            and_(
                InventoryItem.tenant_id == self.tenant_id,
                InventoryItem.is_active is True,
                InventoryItem.available_stock <= InventoryItem.reorder_level,
            )
        )
        low_stock_count = (await self.db.execute(low_stock_stmt)).scalar() or 0

        # Expiring soon (30 days)
        expiring_date = date.today() + timedelta(days=30)
        expiring_stmt = select(func.count(InventoryItem.id)).where(
            and_(
                InventoryItem.tenant_id == self.tenant_id,
                InventoryItem.is_active is True,
                InventoryItem.has_expiry is True,
                InventoryItem.expiry_date <= expiring_date,
                InventoryItem.current_stock > 0,
            )
        )
        expiring_count = (await self.db.execute(expiring_stmt)).scalar() or 0

        # Top consumed items (last 30 days)
        last_30_days = datetime.now() - timedelta(days=30)
        top_consumed_stmt = (
            select(
                InventoryItem.name_en,
                func.sum(InventoryMovement.quantity).label("total_consumed"),
            )
            .join(InventoryMovement, InventoryItem.id == InventoryMovement.item_id)
            .where(
                and_(
                    InventoryMovement.tenant_id == self.tenant_id,
                    InventoryMovement.movement_type == MovementType.ISSUE,
                    InventoryMovement.movement_date >= last_30_days,
                )
            )
            .group_by(InventoryItem.name_en)
            .order_by(desc("total_consumed"))
            .limit(5)
        )

        top_consumed_result = await self.db.execute(top_consumed_stmt)
        top_consumed = [
            {"item_name": row.name_en, "quantity": float(row.total_consumed)}
            for row in top_consumed_result
        ]

        # Recent movements
        recent_movements_stmt = (
            select(InventoryMovement, InventoryItem.name_en)
            .join(InventoryItem, InventoryMovement.item_id == InventoryItem.id)
            .where(InventoryMovement.tenant_id == self.tenant_id)
            .order_by(desc(InventoryMovement.movement_date))
            .limit(10)
        )

        recent_movements_result = await self.db.execute(recent_movements_stmt)
        recent_movements = [
            {
                "date": row.InventoryMovement.movement_date.isoformat(),
                "type": row.InventoryMovement.movement_type.value,
                "item_name": row.name_en,
                "quantity": row.InventoryMovement.quantity,
                "reference": row.InventoryMovement.reference_no,
            }
            for row in recent_movements_result
        ]

        # Average turnover
        turnover_metrics = await self.get_turnover_analysis()
        avg_turnover = (
            statistics.mean([m.turnover_ratio for m in turnover_metrics])
            if turnover_metrics
            else 0.0
        )

        return {
            "total_skus": total_skus,
            "total_value": valuation.total_value,
            "currency": valuation.currency,
            "low_stock_count": low_stock_count,
            "expiring_soon_count": expiring_count,
            "expiring_soon_value": valuation.expiring_value,
            "average_turnover_ratio": round(avg_turnover, 2),
            "top_consumed_items": top_consumed,
            "recent_movements": recent_movements,
            "by_category": valuation.by_category,
            "by_warehouse": valuation.by_warehouse,
        }
