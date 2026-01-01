"""
SAHOOL Crop Profitability Analyzer
Inspired by LiteFarm - helps farmers understand which crops are most profitable
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import date, datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CostCategory(Enum):
    SEEDS = "seeds"
    FERTILIZER = "fertilizer"
    PESTICIDES = "pesticides"
    IRRIGATION = "irrigation"
    LABOR = "labor"
    MACHINERY = "machinery"
    LAND = "land"
    MARKETING = "marketing"
    OTHER = "other"


@dataclass
class CostItem:
    category: CostCategory
    description: str
    amount: float
    unit: str
    quantity: float
    unit_cost: float
    total_cost: float


@dataclass
class RevenueItem:
    description: str
    quantity: float
    unit: str
    unit_price: float
    total_revenue: float
    grade: Optional[str] = None  # Quality grade


@dataclass
class CropProfitability:
    field_id: str
    crop_season_id: str
    crop_code: str
    crop_name_ar: str
    crop_name_en: str

    # Area
    area_ha: float

    # Costs
    costs: List[CostItem]
    total_costs: float
    cost_per_ha: float

    # Revenue
    revenues: List[RevenueItem]
    total_revenue: float
    revenue_per_ha: float

    # Profitability
    gross_profit: float
    gross_margin_percent: float
    net_profit: float
    net_margin_percent: float
    profit_per_ha: float

    # Ratios
    break_even_yield: float  # kg/ha needed to break even
    actual_yield: float  # kg/ha achieved
    return_on_investment: float  # ROI %

    # Comparison
    vs_regional_average: float  # % above/below average
    rank_in_portfolio: int  # Rank among farmer's crops


@dataclass
class SeasonSummary:
    season_year: str
    total_area_ha: float
    total_costs: float
    total_revenue: float
    total_profit: float
    overall_margin: float

    crops: List[CropProfitability]
    best_crop: str
    worst_crop: str

    recommendations_ar: List[str]
    recommendations_en: List[str]


class ProfitabilityAnalyzer:
    """Analyze crop profitability and provide insights"""

    # Regional average costs per hectare (YER - Yemeni Rial)
    # Updated for 2025 Yemen market conditions
    REGIONAL_COSTS = {
        "wheat": {
            "seeds": 75000,  # ~30 kg/ha @ 2500 YER/kg
            "fertilizer": 120000,  # NPK and urea
            "pesticides": 45000,
            "irrigation": 80000,
            "labor": 150000,  # Planting, weeding, harvesting
            "machinery": 100000,  # Tractor rental, threshing
            "land": 50000,  # Rental if applicable
            "marketing": 30000,
            "other": 20000,
        },
        "tomato": {
            "seeds": 45000,  # Seedlings
            "fertilizer": 200000,  # High nutrient demand
            "pesticides": 120000,  # Disease prone
            "irrigation": 180000,  # High water needs
            "labor": 300000,  # Labor intensive
            "machinery": 80000,
            "land": 60000,
            "marketing": 50000,
            "other": 30000,
        },
        "sorghum": {
            "seeds": 30000,
            "fertilizer": 60000,
            "pesticides": 20000,
            "irrigation": 40000,  # Drought tolerant
            "labor": 120000,
            "machinery": 70000,
            "land": 40000,
            "marketing": 25000,
            "other": 15000,
        },
        "potato": {
            "seeds": 180000,  # Seed tubers expensive
            "fertilizer": 150000,
            "pesticides": 100000,
            "irrigation": 140000,
            "labor": 250000,
            "machinery": 90000,
            "land": 55000,
            "marketing": 45000,
            "other": 25000,
        },
        "onion": {
            "seeds": 50000,
            "fertilizer": 130000,
            "pesticides": 80000,
            "irrigation": 110000,
            "labor": 220000,
            "machinery": 60000,
            "land": 50000,
            "marketing": 40000,
            "other": 20000,
        },
        "coffee": {
            "seeds": 100000,  # Or seedlings for new plants
            "fertilizer": 180000,
            "pesticides": 90000,
            "irrigation": 100000,
            "labor": 350000,  # Very labor intensive
            "machinery": 50000,  # Minimal machinery
            "land": 80000,
            "marketing": 70000,
            "other": 40000,
        },
        "qat": {
            "seeds": 120000,
            "fertilizer": 200000,
            "pesticides": 100000,
            "irrigation": 150000,
            "labor": 400000,  # Extremely labor intensive
            "machinery": 40000,
            "land": 100000,
            "marketing": 60000,
            "other": 50000,
        },
        "barley": {
            "seeds": 70000,
            "fertilizer": 100000,
            "pesticides": 35000,
            "irrigation": 60000,
            "labor": 130000,
            "machinery": 90000,
            "land": 45000,
            "marketing": 28000,
            "other": 18000,
        },
        "maize": {
            "seeds": 55000,
            "fertilizer": 110000,
            "pesticides": 60000,
            "irrigation": 120000,
            "labor": 180000,
            "machinery": 85000,
            "land": 50000,
            "marketing": 35000,
            "other": 22000,
        },
        "cucumber": {
            "seeds": 40000,
            "fertilizer": 140000,
            "pesticides": 110000,
            "irrigation": 160000,
            "labor": 280000,
            "machinery": 50000,
            "land": 55000,
            "marketing": 45000,
            "other": 28000,
        },
        "watermelon": {
            "seeds": 35000,
            "fertilizer": 120000,
            "pesticides": 70000,
            "irrigation": 140000,
            "labor": 200000,
            "machinery": 60000,
            "land": 50000,
            "marketing": 50000,
            "other": 25000,
        },
        "mango": {
            "seeds": 150000,  # For new orchards
            "fertilizer": 160000,
            "pesticides": 95000,
            "irrigation": 130000,
            "labor": 300000,
            "machinery": 55000,
            "land": 90000,
            "marketing": 65000,
            "other": 35000,
        },
    }

    # Regional average prices (YER/kg) - 2025 market prices
    REGIONAL_PRICES = {
        "wheat": 550,  # Staple grain
        "tomato": 280,  # Fresh vegetable
        "sorghum": 400,  # Feed grain
        "potato": 350,
        "onion": 300,
        "coffee": 8500,  # Premium Yemen coffee
        "qat": 3500,  # High value cash crop
        "barley": 480,
        "maize": 520,
        "cucumber": 250,
        "watermelon": 180,
        "mango": 800,
    }

    # Regional average yields (kg/ha) - Yemen conditions
    REGIONAL_YIELDS = {
        "wheat": 2800,
        "tomato": 25000,  # Greenhouse can be much higher
        "sorghum": 2200,
        "potato": 18000,
        "onion": 22000,
        "coffee": 800,  # Mature trees
        "qat": 3500,
        "barley": 2500,
        "maize": 3200,
        "cucumber": 20000,
        "watermelon": 30000,
        "mango": 12000,  # Mature trees
    }

    # Crop names in Arabic
    CROP_NAMES_AR = {
        "wheat": "قمح",
        "tomato": "طماطم",
        "sorghum": "ذرة رفيعة",
        "potato": "بطاطس",
        "onion": "بصل",
        "coffee": "بن",
        "qat": "قات",
        "barley": "شعير",
        "maize": "ذرة شامية",
        "cucumber": "خيار",
        "watermelon": "بطيخ",
        "mango": "مانجو",
    }

    # Crop names in English
    CROP_NAMES_EN = {
        "wheat": "Wheat",
        "tomato": "Tomato",
        "sorghum": "Sorghum",
        "potato": "Potato",
        "onion": "Onion",
        "coffee": "Coffee",
        "qat": "Qat",
        "barley": "Barley",
        "maize": "Maize",
        "cucumber": "Cucumber",
        "watermelon": "Watermelon",
        "mango": "Mango",
    }

    def __init__(self, db_pool=None):
        self.db_pool = db_pool

    async def analyze_crop(
        self,
        field_id: str,
        crop_season_id: str,
        crop_code: str,
        area_ha: float,
        costs: Optional[List[Dict]] = None,
        revenues: Optional[List[Dict]] = None,
    ) -> CropProfitability:
        """
        Analyze profitability of a single crop season.
        If costs/revenues not provided, use regional estimates.
        """
        logger.info(f"Analyzing profitability for crop {crop_code} on field {field_id}")

        # Get crop names
        crop_name_ar = self.CROP_NAMES_AR.get(crop_code, crop_code)
        crop_name_en = self.CROP_NAMES_EN.get(crop_code, crop_code.title())

        # Process costs
        cost_items = []
        if costs:
            for cost_dict in costs:
                cost_items.append(
                    CostItem(
                        category=CostCategory(cost_dict.get("category", "other")),
                        description=cost_dict["description"],
                        amount=cost_dict["amount"],
                        unit=cost_dict.get("unit", "unit"),
                        quantity=cost_dict.get("quantity", 1.0),
                        unit_cost=cost_dict.get("unit_cost", cost_dict["amount"]),
                        total_cost=cost_dict["amount"],
                    )
                )
            total_costs = sum(item.total_cost for item in cost_items)
        else:
            # Use regional estimates
            regional_costs = self.REGIONAL_COSTS.get(
                crop_code, self.REGIONAL_COSTS["wheat"]
            )
            for category, cost_per_ha in regional_costs.items():
                cost = cost_per_ha * area_ha
                cost_items.append(
                    CostItem(
                        category=CostCategory(category),
                        description=f"{category.title()} costs",
                        amount=cost,
                        unit="YER",
                        quantity=area_ha,
                        unit_cost=cost_per_ha,
                        total_cost=cost,
                    )
                )
            total_costs = sum(item.total_cost for item in cost_items)

        # Process revenues
        revenue_items = []
        if revenues:
            for rev_dict in revenues:
                revenue_items.append(
                    RevenueItem(
                        description=rev_dict["description"],
                        quantity=rev_dict["quantity"],
                        unit=rev_dict.get("unit", "kg"),
                        unit_price=rev_dict["unit_price"],
                        total_revenue=rev_dict["quantity"] * rev_dict["unit_price"],
                        grade=rev_dict.get("grade"),
                    )
                )
            total_revenue = sum(item.total_revenue for item in revenue_items)
            actual_yield = sum(item.quantity for item in revenue_items) / area_ha
        else:
            # Use regional estimates
            regional_yield = self.REGIONAL_YIELDS.get(crop_code, 2000)
            regional_price = self.REGIONAL_PRICES.get(crop_code, 400)

            total_yield = regional_yield * area_ha
            total_revenue = total_yield * regional_price
            actual_yield = regional_yield

            revenue_items.append(
                RevenueItem(
                    description=f"{crop_name_en} harvest",
                    quantity=total_yield,
                    unit="kg",
                    unit_price=regional_price,
                    total_revenue=total_revenue,
                    grade="standard",
                )
            )

        # Calculate profitability metrics
        cost_per_ha = total_costs / area_ha if area_ha > 0 else 0
        revenue_per_ha = total_revenue / area_ha if area_ha > 0 else 0

        gross_profit = total_revenue - total_costs
        gross_margin_percent = (
            (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
        )

        # For this simple model, net profit = gross profit (no separate overhead)
        net_profit = gross_profit
        net_margin_percent = gross_margin_percent
        profit_per_ha = net_profit / area_ha if area_ha > 0 else 0

        # Calculate break-even yield
        avg_price = (
            total_revenue / sum(item.quantity for item in revenue_items)
            if revenue_items
            else self.REGIONAL_PRICES.get(crop_code, 400)
        )
        break_even_yield = (
            (total_costs / avg_price) / area_ha if area_ha > 0 and avg_price > 0 else 0
        )

        # Calculate ROI
        roi = (net_profit / total_costs * 100) if total_costs > 0 else 0

        # Compare to regional average
        regional_revenue = self.REGIONAL_YIELDS.get(
            crop_code, 2000
        ) * self.REGIONAL_PRICES.get(crop_code, 400)
        regional_costs_total = sum(self.REGIONAL_COSTS.get(crop_code, {}).values())
        regional_profit = regional_revenue - regional_costs_total

        vs_regional_avg = (
            ((profit_per_ha - regional_profit) / regional_profit * 100)
            if regional_profit != 0
            else 0
        )

        return CropProfitability(
            field_id=field_id,
            crop_season_id=crop_season_id,
            crop_code=crop_code,
            crop_name_ar=crop_name_ar,
            crop_name_en=crop_name_en,
            area_ha=area_ha,
            costs=cost_items,
            total_costs=total_costs,
            cost_per_ha=cost_per_ha,
            revenues=revenue_items,
            total_revenue=total_revenue,
            revenue_per_ha=revenue_per_ha,
            gross_profit=gross_profit,
            gross_margin_percent=gross_margin_percent,
            net_profit=net_profit,
            net_margin_percent=net_margin_percent,
            profit_per_ha=profit_per_ha,
            break_even_yield=break_even_yield,
            actual_yield=actual_yield,
            return_on_investment=roi,
            vs_regional_average=vs_regional_avg,
            rank_in_portfolio=1,  # Will be set by season analysis
        )

    async def analyze_season(
        self, farmer_id: str, season_year: str, crops_data: List[Dict]
    ) -> SeasonSummary:
        """Analyze all crops for a farmer in a season"""
        logger.info(f"Analyzing season {season_year} for farmer {farmer_id}")

        crop_analyses = []
        for crop_data in crops_data:
            analysis = await self.analyze_crop(
                field_id=crop_data["field_id"],
                crop_season_id=crop_data.get(
                    "crop_season_id", f"{crop_data['field_id']}-{season_year}"
                ),
                crop_code=crop_data["crop_code"],
                area_ha=crop_data["area_ha"],
                costs=crop_data.get("costs"),
                revenues=crop_data.get("revenues"),
            )
            crop_analyses.append(analysis)

        # Rank crops by profit per hectare
        sorted_crops = sorted(
            crop_analyses, key=lambda x: x.profit_per_ha, reverse=True
        )
        for idx, crop in enumerate(sorted_crops, 1):
            crop.rank_in_portfolio = idx

        # Calculate totals
        total_area = sum(c.area_ha for c in crop_analyses)
        total_costs = sum(c.total_costs for c in crop_analyses)
        total_revenue = sum(c.total_revenue for c in crop_analyses)
        total_profit = total_revenue - total_costs
        overall_margin = (
            (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        )

        best_crop = sorted_crops[0].crop_name_en if sorted_crops else "None"
        worst_crop = sorted_crops[-1].crop_name_en if sorted_crops else "None"

        # Generate recommendations
        recommendations_en, recommendations_ar = self._generate_season_recommendations(
            crop_analyses, total_profit, overall_margin
        )

        return SeasonSummary(
            season_year=season_year,
            total_area_ha=total_area,
            total_costs=total_costs,
            total_revenue=total_revenue,
            total_profit=total_profit,
            overall_margin=overall_margin,
            crops=crop_analyses,
            best_crop=best_crop,
            worst_crop=worst_crop,
            recommendations_ar=recommendations_ar,
            recommendations_en=recommendations_en,
        )

    async def compare_crops(
        self, crop_codes: List[str], area_ha: float = 1.0, region: str = "sanaa"
    ) -> List[Dict]:
        """
        Compare profitability of different crops.
        Useful for planning next season.
        """
        logger.info(f"Comparing crops: {crop_codes} for {area_ha} ha")

        comparisons = []
        for crop_code in crop_codes:
            if crop_code not in self.REGIONAL_COSTS:
                logger.warning(f"Crop {crop_code} not found in regional data")
                continue

            regional_costs = self.REGIONAL_COSTS[crop_code]
            total_cost = sum(regional_costs.values()) * area_ha

            regional_yield = self.REGIONAL_YIELDS.get(crop_code, 2000)
            regional_price = self.REGIONAL_PRICES.get(crop_code, 400)

            total_yield = regional_yield * area_ha
            total_revenue = total_yield * regional_price
            profit = total_revenue - total_cost
            roi = (profit / total_cost * 100) if total_cost > 0 else 0

            comparisons.append(
                {
                    "crop_code": crop_code,
                    "crop_name_en": self.CROP_NAMES_EN.get(crop_code, crop_code),
                    "crop_name_ar": self.CROP_NAMES_AR.get(crop_code, crop_code),
                    "area_ha": area_ha,
                    "estimated_costs": total_cost,
                    "estimated_revenue": total_revenue,
                    "estimated_profit": profit,
                    "profit_per_ha": profit / area_ha if area_ha > 0 else 0,
                    "roi_percent": roi,
                    "break_even_yield_kg_ha": (
                        (total_cost / regional_price) / area_ha
                        if area_ha > 0 and regional_price > 0
                        else 0
                    ),
                    "expected_yield_kg_ha": regional_yield,
                    "market_price_yer_kg": regional_price,
                }
            )

        # Sort by profit per hectare
        comparisons.sort(key=lambda x: x["profit_per_ha"], reverse=True)
        return comparisons

    async def calculate_break_even(
        self, crop_code: str, area_ha: float, total_costs: float, expected_price: float
    ) -> Dict:
        """Calculate break-even yield and price"""
        logger.info(f"Calculating break-even for {crop_code}")

        # Break-even yield (kg) at expected price
        break_even_yield_kg = total_costs / expected_price if expected_price > 0 else 0
        break_even_yield_kg_ha = break_even_yield_kg / area_ha if area_ha > 0 else 0

        # Regional average yield for comparison
        regional_yield = self.REGIONAL_YIELDS.get(crop_code, 2000)

        # Break-even price at regional yield
        total_yield_kg = regional_yield * area_ha
        break_even_price = total_costs / total_yield_kg if total_yield_kg > 0 else 0

        # Regional market price
        regional_price = self.REGIONAL_PRICES.get(crop_code, 400)

        return {
            "crop_code": crop_code,
            "crop_name_en": self.CROP_NAMES_EN.get(crop_code, crop_code),
            "crop_name_ar": self.CROP_NAMES_AR.get(crop_code, crop_code),
            "area_ha": area_ha,
            "total_costs": total_costs,
            "break_even_yield_kg": break_even_yield_kg,
            "break_even_yield_kg_ha": break_even_yield_kg_ha,
            "regional_average_yield_kg_ha": regional_yield,
            "yield_gap_percent": (
                ((regional_yield - break_even_yield_kg_ha) / regional_yield * 100)
                if regional_yield > 0
                else 0
            ),
            "break_even_price_yer_kg": break_even_price,
            "expected_price_yer_kg": expected_price,
            "regional_market_price_yer_kg": regional_price,
            "price_cushion_percent": (
                ((expected_price - break_even_price) / break_even_price * 100)
                if break_even_price > 0
                else 0
            ),
        }

    async def get_cost_breakdown(
        self, crop_code: str, area_ha: float = 1.0
    ) -> Dict[str, float]:
        """Get cost breakdown by category"""
        logger.info(f"Getting cost breakdown for {crop_code}")

        if crop_code not in self.REGIONAL_COSTS:
            return {}

        regional_costs = self.REGIONAL_COSTS[crop_code]
        breakdown = {
            category: cost * area_ha for category, cost in regional_costs.items()
        }
        breakdown["total"] = sum(breakdown.values())

        # Add percentages
        total = breakdown["total"]
        breakdown_pct = {
            f"{k}_percent": (v / total * 100) if total > 0 else 0
            for k, v in breakdown.items()
            if k != "total"
        }
        breakdown.update(breakdown_pct)

        return breakdown

    async def get_historical_profitability(
        self, field_id: str, crop_code: str, years: int = 5
    ) -> List[Dict]:
        """Get historical profitability for a crop on a field"""
        # This would query the database in production
        # For now, return mock data
        logger.info(
            f"Getting historical profitability for {crop_code} on field {field_id}"
        )

        historical = []
        current_year = datetime.now().year

        for i in range(years):
            year = current_year - i
            # Simulate some variation
            variation = 1.0 + (i * 0.05 - 0.1)  # ±10% variation

            regional_yield = self.REGIONAL_YIELDS.get(crop_code, 2000)
            regional_price = self.REGIONAL_PRICES.get(crop_code, 400)
            regional_costs = sum(self.REGIONAL_COSTS.get(crop_code, {}).values())

            revenue = regional_yield * regional_price * variation
            costs = regional_costs * variation
            profit = revenue - costs

            historical.append(
                {
                    "year": year,
                    "revenue": revenue,
                    "costs": costs,
                    "profit": profit,
                    "roi_percent": (profit / costs * 100) if costs > 0 else 0,
                }
            )

        return historical

    async def get_regional_benchmarks(
        self, crop_code: str, region: str = "sanaa"
    ) -> Dict:
        """Get regional benchmark costs and revenues"""
        logger.info(f"Getting regional benchmarks for {crop_code} in {region}")

        if crop_code not in self.REGIONAL_COSTS:
            return {}

        costs = self.REGIONAL_COSTS[crop_code]
        total_costs = sum(costs.values())
        yield_kg_ha = self.REGIONAL_YIELDS.get(crop_code, 2000)
        price = self.REGIONAL_PRICES.get(crop_code, 400)
        revenue = yield_kg_ha * price
        profit = revenue - total_costs

        return {
            "crop_code": crop_code,
            "crop_name_en": self.CROP_NAMES_EN.get(crop_code, crop_code),
            "crop_name_ar": self.CROP_NAMES_AR.get(crop_code, crop_code),
            "region": region,
            "benchmarks": {
                "costs_per_ha": costs,
                "total_costs_per_ha": total_costs,
                "yield_kg_ha": yield_kg_ha,
                "price_yer_kg": price,
                "revenue_per_ha": revenue,
                "profit_per_ha": profit,
                "roi_percent": (profit / total_costs * 100) if total_costs > 0 else 0,
            },
        }

    def generate_recommendations(
        self, analysis: CropProfitability
    ) -> Dict[str, List[str]]:
        """Generate improvement recommendations"""
        recommendations_en = []
        recommendations_ar = []

        # Check if yield is below regional average
        regional_yield = self.REGIONAL_YIELDS.get(analysis.crop_code, 2000)
        if analysis.actual_yield < regional_yield * 0.8:
            recommendations_en.append(
                f"Your yield ({analysis.actual_yield:.0f} kg/ha) is below the regional average ({regional_yield:.0f} kg/ha). "
                "Consider improving soil fertility or using better seeds."
            )
            recommendations_ar.append(
                f"إنتاجيتك ({analysis.actual_yield:.0f} كجم/هكتار) أقل من المتوسط الإقليمي ({regional_yield:.0f} كجم/هكتار). "
                "فكر في تحسين خصوبة التربة أو استخدام بذور أفضل."
            )

        # Check if costs are too high
        regional_costs = sum(self.REGIONAL_COSTS.get(analysis.crop_code, {}).values())
        if analysis.cost_per_ha > regional_costs * 1.2:
            recommendations_en.append(
                f"Your costs ({analysis.cost_per_ha:.0f} YER/ha) are significantly higher than regional average. "
                "Review input costs and negotiate better prices with suppliers."
            )
            recommendations_ar.append(
                f"تكاليفك ({analysis.cost_per_ha:.0f} ريال/هكتار) أعلى بكثير من المتوسط الإقليمي. "
                "راجع تكاليف المدخلات وتفاوض على أسعار أفضل مع الموردين."
            )

        # Check profitability
        if analysis.net_margin_percent < 20:
            recommendations_en.append(
                f"Your profit margin ({analysis.net_margin_percent:.1f}%) is low. "
                "Consider diversifying to higher-value crops or improving efficiency."
            )
            recommendations_ar.append(
                f"هامش الربح ({analysis.net_margin_percent:.1f}%) منخفض. "
                "فكر في التنويع إلى محاصيل ذات قيمة أعلى أو تحسين الكفاءة."
            )
        elif analysis.net_margin_percent > 40:
            recommendations_en.append(
                f"Excellent profit margin ({analysis.net_margin_percent:.1f}%)! "
                "Consider expanding this crop or sharing your practices with others."
            )
            recommendations_ar.append(
                f"هامش ربح ممتاز ({analysis.net_margin_percent:.1f}%)! "
                "فكر في توسيع هذا المحصول أو مشاركة ممارساتك مع الآخرين."
            )

        # ROI recommendations
        if analysis.return_on_investment < 30:
            recommendations_en.append(
                "Low return on investment. Focus on reducing costs or increasing yields."
            )
            recommendations_ar.append(
                "عائد منخفض على الاستثمار. ركز على خفض التكاليف أو زيادة الإنتاجية."
            )

        return {"english": recommendations_en, "arabic": recommendations_ar}

    def _generate_season_recommendations(
        self,
        crop_analyses: List[CropProfitability],
        total_profit: float,
        overall_margin: float,
    ) -> tuple[List[str], List[str]]:
        """Generate season-level recommendations"""
        recommendations_en = []
        recommendations_ar = []

        if not crop_analyses:
            return recommendations_en, recommendations_ar

        # Find best and worst performing crops
        sorted_crops = sorted(
            crop_analyses, key=lambda x: x.profit_per_ha, reverse=True
        )
        best = sorted_crops[0]
        worst = sorted_crops[-1]

        # Recommendation to expand best crop
        if best.profit_per_ha > 0:
            recommendations_en.append(
                f"Consider allocating more area to {best.crop_name_en}, which showed the highest profit per hectare "
                f"({best.profit_per_ha:.0f} YER/ha)."
            )
            recommendations_ar.append(
                f"فكر في تخصيص مساحة أكبر لـ{best.crop_name_ar}، والذي أظهر أعلى ربح لكل هكتار "
                f"({best.profit_per_ha:.0f} ريال/هكتار)."
            )

        # Recommendation about worst crop
        if worst.profit_per_ha < 0:
            recommendations_en.append(
                f"{worst.crop_name_en} resulted in a loss. Consider replacing it with a more profitable crop "
                f"or improving management practices."
            )
            recommendations_ar.append(
                f"{worst.crop_name_ar} نتج عنه خسارة. فكر في استبداله بمحصول أكثر ربحية "
                f"أو تحسين ممارسات الإدارة."
            )

        # Overall profitability
        if total_profit > 0:
            recommendations_en.append(
                f"Overall season was profitable with {overall_margin:.1f}% margin. "
                "Maintain good practices and look for incremental improvements."
            )
            recommendations_ar.append(
                f"كان الموسم الإجمالي مربحًا بهامش {overall_margin:.1f}%. "
                "حافظ على الممارسات الجيدة وابحث عن تحسينات تدريجية."
            )
        else:
            recommendations_en.append(
                "Season resulted in an overall loss. Review costs across all crops "
                "and consider technical assistance."
            )
            recommendations_ar.append(
                "نتج عن الموسم خسارة إجمالية. راجع التكاليف عبر جميع المحاصيل "
                "وفكر في الحصول على مساعدة فنية."
            )

        # Diversification
        if len(crop_analyses) == 1:
            recommendations_en.append(
                "Consider diversifying with additional crops to reduce risk and improve soil health."
            )
            recommendations_ar.append(
                "فكر في التنويع بمحاصيل إضافية لتقليل المخاطر وتحسين صحة التربة."
            )

        return recommendations_en, recommendations_ar

    async def export_report(
        self, analysis: CropProfitability, format: str = "pdf"
    ) -> str:
        """Export profitability report"""
        # This would generate actual PDF/Excel in production
        logger.info(f"Exporting report for {analysis.crop_code} in {format} format")

        return f"report_{analysis.crop_season_id}_{format}"
