"""
SAHOOL Market Service - Agricultural Market Prices & Analytics
==============================================================
Layer: Signal Producer (Layer 2)
Purpose: Track crop prices, market trends, and provide selling recommendations
"""

import os
from datetime import datetime, date, timedelta
from typing import Optional, List, Tuple
from contextlib import asynccontextmanager
import uuid

from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, ForeignKey, Integer, Float, Date, select, func, and_
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import structlog
import enum

# Shared imports
import sys
sys.path.insert(0, '/app/shared')
from database import Database, BaseModel as DBBaseModel  # noqa: E402
from events.base_event import EventBus  # noqa: E402
from utils.logging import setup_logging  # noqa: E402


# ============================================================================
# Configuration
# ============================================================================

class Settings:
    """Market service configuration"""
    SERVICE_NAME = "market-service"
    SERVICE_PORT = int(os.getenv("MARKET_SERVICE_PORT", "8088"))
    SERVICE_LAYER = "signal-producer"
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://sahool:sahool@postgres:5432/sahool_market")
    NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")
    
    # Default currency
    DEFAULT_CURRENCY = "YER"  # Yemeni Rial
    
    # Price change thresholds for alerts
    SIGNIFICANT_CHANGE_PERCENT = 10  # Trigger alert if price changes > 10%

settings = Settings()

# ============================================================================
# Logging & Metrics
# ============================================================================

setup_logging(settings.SERVICE_NAME)
logger = structlog.get_logger()

market_events = Counter('market_events_total', 'Market events', ['event_type', 'status'])
price_updates = Counter('price_updates_total', 'Price updates', ['crop', 'market'])

# ============================================================================
# Database Models
# ============================================================================

class PriceUnit(str, enum.Enum):
    KG = "kg"
    TON = "ton"
    QUINTAL = "quintal"  # 100 kg
    MANN = "mann"  # Traditional Yemeni unit (~40 kg)
    PIECE = "piece"
    BUNDLE = "bundle"
    BOX = "box"
    CRATE = "crate"

class PriceTrend(str, enum.Enum):
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    VOLATILE = "volatile"

class Market(DBBaseModel):
    """Agricultural market"""
    __tablename__ = "markets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=True)
    code = Column(String(50), unique=True, nullable=False)
    
    # Location
    governorate = Column(String(100), nullable=False)
    district = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Market details
    market_type = Column(String(50), default="wholesale")  # wholesale, retail, farm_gate
    operating_days = Column(ARRAY(String), default=["sat", "sun", "mon", "tue", "wed", "thu"])
    opening_time = Column(String(10), nullable=True)
    closing_time = Column(String(10), nullable=True)
    
    # Contact
    contact_phone = Column(String(20), nullable=True)
    contact_email = Column(String(255), nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    prices = relationship("CropPrice", back_populates="market", cascade="all, delete-orphan")

class Crop(DBBaseModel):
    """Crop catalog"""
    __tablename__ = "crops"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    name = Column(String(255), nullable=False)
    name_ar = Column(String(255), nullable=False)
    scientific_name = Column(String(255), nullable=True)
    
    category = Column(String(50), nullable=False)  # vegetables, fruits, grains, cash_crops
    subcategory = Column(String(50), nullable=True)
    
    # Common varieties in Yemen
    varieties = Column(JSON, default=[])  # [{name, name_ar, characteristics}]
    
    # Default units
    default_unit = Column(String(20), default=PriceUnit.KG.value)
    
    # Seasonality
    harvest_months = Column(ARRAY(Integer), default=[])  # 1-12
    peak_months = Column(ARRAY(Integer), default=[])
    
    # Storage
    shelf_life_days = Column(Integer, nullable=True)
    storage_requirements = Column(Text, nullable=True)
    
    image_url = Column(String(500), nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    prices = relationship("CropPrice", back_populates="crop", cascade="all, delete-orphan")

class CropPrice(DBBaseModel):
    """Crop price record"""
    __tablename__ = "crop_prices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    crop_id = Column(UUID(as_uuid=True), ForeignKey('crops.id', ondelete='CASCADE'), nullable=False)
    market_id = Column(UUID(as_uuid=True), ForeignKey('markets.id', ondelete='CASCADE'), nullable=False)
    
    # Price data
    price_date = Column(Date, nullable=False, index=True)
    
    price_min = Column(Float, nullable=False)  # Minimum observed price
    price_max = Column(Float, nullable=False)  # Maximum observed price
    price_avg = Column(Float, nullable=False)  # Average price
    price_mode = Column(Float, nullable=True)  # Most common price
    
    unit = Column(String(20), default=PriceUnit.KG.value)
    currency = Column(String(10), default="YER")
    
    # Quality grades
    grade_a_price = Column(Float, nullable=True)
    grade_b_price = Column(Float, nullable=True)
    grade_c_price = Column(Float, nullable=True)
    
    # Volume
    volume_available = Column(Float, nullable=True)  # in tons
    volume_unit = Column(String(20), default="ton")
    
    # Supply/Demand indicators
    supply_level = Column(String(20), nullable=True)  # scarce, low, moderate, abundant, surplus
    demand_level = Column(String(20), nullable=True)
    
    # Change from previous
    price_change_percent = Column(Float, nullable=True)
    price_trend = Column(String(20), nullable=True)  # rising, falling, stable
    
    # Source
    source = Column(String(100), nullable=True)  # manual, api, scraper
    verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    crop = relationship("Crop", back_populates="prices")
    market = relationship("Market", back_populates="prices")

class PriceAlert(DBBaseModel):
    """Price alerts for users"""
    __tablename__ = "price_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    crop_id = Column(UUID(as_uuid=True), ForeignKey('crops.id', ondelete='CASCADE'), nullable=False)
    market_id = Column(UUID(as_uuid=True), ForeignKey('markets.id', ondelete='CASCADE'), nullable=True)
    
    # Alert conditions
    alert_type = Column(String(50), nullable=False)  # price_above, price_below, price_change
    threshold_value = Column(Float, nullable=False)
    
    is_active = Column(Boolean, default=True)
    last_triggered = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class MarketForecast(DBBaseModel):
    """Price forecasts"""
    __tablename__ = "market_forecasts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    crop_id = Column(UUID(as_uuid=True), ForeignKey('crops.id', ondelete='CASCADE'), nullable=False)
    market_id = Column(UUID(as_uuid=True), ForeignKey('markets.id', ondelete='CASCADE'), nullable=True)
    
    forecast_date = Column(Date, nullable=False)  # Date being forecasted
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Forecast values
    predicted_price_low = Column(Float, nullable=False)
    predicted_price_high = Column(Float, nullable=False)
    predicted_price_avg = Column(Float, nullable=False)
    
    confidence_level = Column(Float, nullable=True)  # 0-100
    
    # Factors considered
    factors = Column(JSON, default=[])  # [{factor, impact, description}]
    
    # Model info
    model_version = Column(String(50), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# ============================================================================
# Pydantic Schemas
# ============================================================================

class MarketCreate(BaseModel):
    """Create market"""
    name: str
    name_ar: Optional[str] = None
    code: str
    governorate: str
    district: Optional[str] = None
    city: Optional[str] = None
    market_type: str = "wholesale"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class MarketResponse(BaseModel):
    """Market response"""
    id: uuid.UUID
    name: str
    name_ar: Optional[str]
    code: str
    governorate: str
    district: Optional[str]
    city: Optional[str]
    market_type: str
    latitude: Optional[float]
    longitude: Optional[float]
    is_active: bool
    
    class Config:
        from_attributes = True

class CropCreate(BaseModel):
    """Create crop"""
    name: str
    name_ar: str
    scientific_name: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    default_unit: str = "kg"
    harvest_months: List[int] = []
    peak_months: List[int] = []

class CropResponse(BaseModel):
    """Crop response"""
    id: uuid.UUID
    name: str
    name_ar: str
    scientific_name: Optional[str]
    category: str
    subcategory: Optional[str]
    default_unit: str
    harvest_months: List[int]
    peak_months: List[int]
    is_active: bool
    
    class Config:
        from_attributes = True

class PriceCreate(BaseModel):
    """Create price record"""
    crop_id: uuid.UUID
    market_id: uuid.UUID
    price_date: date
    price_min: float
    price_max: float
    price_avg: float
    unit: str = "kg"
    currency: str = "YER"
    grade_a_price: Optional[float] = None
    grade_b_price: Optional[float] = None
    grade_c_price: Optional[float] = None
    volume_available: Optional[float] = None
    supply_level: Optional[str] = None
    demand_level: Optional[str] = None
    source: Optional[str] = None

class PriceResponse(BaseModel):
    """Price response"""
    id: uuid.UUID
    crop_id: uuid.UUID
    market_id: uuid.UUID
    price_date: date
    price_min: float
    price_max: float
    price_avg: float
    unit: str
    currency: str
    grade_a_price: Optional[float]
    grade_b_price: Optional[float]
    price_change_percent: Optional[float]
    price_trend: Optional[str]
    supply_level: Optional[str]
    demand_level: Optional[str]
    
    class Config:
        from_attributes = True

class PriceWithDetails(PriceResponse):
    """Price with crop and market details"""
    crop_name: str
    crop_name_ar: str
    market_name: str
    market_name_ar: Optional[str]

class PriceAlertCreate(BaseModel):
    """Create price alert"""
    crop_id: uuid.UUID
    market_id: Optional[uuid.UUID] = None
    alert_type: str
    threshold_value: float

class PriceAlertResponse(BaseModel):
    """Price alert response"""
    id: uuid.UUID
    crop_id: uuid.UUID
    market_id: Optional[uuid.UUID]
    alert_type: str
    threshold_value: float
    is_active: bool
    last_triggered: Optional[datetime]
    
    class Config:
        from_attributes = True

class MarketSummary(BaseModel):
    """Market summary for a crop"""
    crop_id: uuid.UUID
    crop_name: str
    crop_name_ar: str
    
    avg_price: float
    min_price: float
    max_price: float
    
    price_change_24h: Optional[float]
    price_change_7d: Optional[float]
    price_change_30d: Optional[float]
    
    trend: str
    
    best_market: Optional[str]
    best_market_price: Optional[float]
    
    markets_reporting: int

class SeasonalAnalysis(BaseModel):
    """Seasonal price analysis"""
    crop_id: uuid.UUID
    month: int
    
    avg_price: float
    price_volatility: float
    
    is_harvest_month: bool
    is_peak_month: bool
    
    recommendation: str
    recommendation_ar: str

# ============================================================================
# Market Analysis Engine
# ============================================================================

class MarketAnalysisEngine:
    """Market price analysis engine"""
    
    def calculate_trend(self, prices: List[float]) -> str:
        """Calculate price trend from series"""
        if len(prices) < 2:
            return PriceTrend.STABLE.value
        
        # Simple moving average comparison
        recent = sum(prices[-3:]) / min(3, len(prices[-3:]))
        older = sum(prices[:3]) / min(3, len(prices[:3]))
        
        change_percent = ((recent - older) / older) * 100 if older > 0 else 0
        
        if change_percent > 5:
            return PriceTrend.RISING.value
        elif change_percent < -5:
            return PriceTrend.FALLING.value
        else:
            return PriceTrend.STABLE.value
    
    def calculate_volatility(self, prices: List[float]) -> float:
        """Calculate price volatility (coefficient of variation)"""
        if len(prices) < 2:
            return 0
        
        avg = sum(prices) / len(prices)
        if avg == 0:
            return 0
        
        variance = sum((p - avg) ** 2 for p in prices) / len(prices)
        std_dev = variance ** 0.5
        
        return (std_dev / avg) * 100  # CV as percentage
    
    def get_selling_recommendation(
        self,
        current_price: float,
        avg_price_30d: float,
        trend: str,
        is_harvest_month: bool,
        is_peak_month: bool
    ) -> Tuple[str, str]:
        """Generate selling recommendation"""
        
        price_vs_avg = ((current_price - avg_price_30d) / avg_price_30d) * 100 if avg_price_30d > 0 else 0
        
        if price_vs_avg > 15 and trend == PriceTrend.RISING.value:
            return (
                "Strong Sell - Prices above average and rising. Good time to sell.",
                "بيع قوي - الأسعار أعلى من المتوسط وفي ارتفاع. وقت جيد للبيع."
            )
        elif price_vs_avg > 10:
            return (
                "Sell - Prices above average. Consider selling.",
                "بيع - الأسعار أعلى من المتوسط. يُنصح بالبيع."
            )
        elif price_vs_avg < -15 and not is_harvest_month:
            return (
                "Hold - Prices below average. Consider storing if possible.",
                "احتفظ - الأسعار أقل من المتوسط. يُنصح بالتخزين إن أمكن."
            )
        elif is_harvest_month and trend == PriceTrend.FALLING.value:
            return (
                "Caution - Harvest season typically brings lower prices.",
                "تحذير - موسم الحصاد عادة يعني انخفاض الأسعار."
            )
        elif is_peak_month:
            return (
                "Monitor - Peak demand month. Prices may rise.",
                "راقب - شهر ذروة الطلب. الأسعار قد ترتفع."
            )
        else:
            return (
                "Hold - Current prices are around average.",
                "احتفظ - الأسعار الحالية قريبة من المتوسط."
            )

# ============================================================================
# Market Service
# ============================================================================

class MarketService:
    """Core market service"""
    
    def __init__(self, db: Database, event_bus: EventBus):
        self.db = db
        self.event_bus = event_bus
        self.analysis_engine = MarketAnalysisEngine()
    
    async def create_market(self, data: MarketCreate) -> Market:
        """Create market"""
        async with self.db.session() as session:
            market = Market(**data.dict())
            session.add(market)
            await session.commit()
            await session.refresh(market)
            return market
    
    async def get_markets(
        self,
        governorate: Optional[str] = None,
        market_type: Optional[str] = None
    ) -> List[Market]:
        """Get markets with filters"""
        async with self.db.session() as session:
            query = select(Market).where(Market.is_active == True)
            
            if governorate:
                query = query.where(Market.governorate == governorate)
            if market_type:
                query = query.where(Market.market_type == market_type)
            
            result = await session.execute(query)
            return result.scalars().all()
    
    async def create_crop(self, data: CropCreate) -> Crop:
        """Create crop"""
        async with self.db.session() as session:
            crop = Crop(**data.dict())
            session.add(crop)
            await session.commit()
            await session.refresh(crop)
            return crop
    
    async def get_crops(
        self,
        category: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Crop]:
        """Get crops with filters"""
        async with self.db.session() as session:
            query = select(Crop).where(Crop.is_active == True)
            
            if category:
                query = query.where(Crop.category == category)
            
            if search:
                search_filter = f"%{search}%"
                query = query.where(
                    (Crop.name.ilike(search_filter)) |
                    (Crop.name_ar.ilike(search_filter))
                )
            
            result = await session.execute(query)
            return result.scalars().all()
    
    async def record_price(self, data: PriceCreate) -> CropPrice:
        """Record crop price"""
        async with self.db.session() as session:
            # Get previous price for comparison
            prev_result = await session.execute(
                select(CropPrice)
                .where(
                    CropPrice.crop_id == data.crop_id,
                    CropPrice.market_id == data.market_id,
                    CropPrice.price_date < data.price_date
                )
                .order_by(CropPrice.price_date.desc())
                .limit(1)
            )
            prev_price = prev_result.scalar_one_or_none()
            
            # Calculate change
            price_change = None
            price_trend = None
            
            if prev_price:
                price_change = ((data.price_avg - prev_price.price_avg) / prev_price.price_avg) * 100
                if price_change > 5:
                    price_trend = PriceTrend.RISING.value
                elif price_change < -5:
                    price_trend = PriceTrend.FALLING.value
                else:
                    price_trend = PriceTrend.STABLE.value
            
            price = CropPrice(
                **data.dict(),
                price_change_percent=round(price_change, 2) if price_change else None,
                price_trend=price_trend
            )
            
            session.add(price)
            await session.commit()
            await session.refresh(price)
            
            # Emit event
            await self.event_bus.publish(
                "market.price.recorded",
                {
                    "crop_id": str(data.crop_id),
                    "market_id": str(data.market_id),
                    "price_avg": data.price_avg,
                    "price_change_percent": price_change,
                    "price_trend": price_trend,
                    "price_date": data.price_date.isoformat()
                }
            )
            
            # Check for significant price change
            if price_change and abs(price_change) > settings.SIGNIFICANT_CHANGE_PERCENT:
                await self.event_bus.publish(
                    "market.price.significant_change",
                    {
                        "crop_id": str(data.crop_id),
                        "market_id": str(data.market_id),
                        "change_percent": price_change,
                        "direction": "up" if price_change > 0 else "down"
                    }
                )
            
            price_updates.labels(
                crop=str(data.crop_id)[:8],
                market=str(data.market_id)[:8]
            ).inc()
            
            return price
    
    async def get_prices(
        self,
        crop_id: Optional[uuid.UUID] = None,
        market_id: Optional[uuid.UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100
    ) -> List[CropPrice]:
        """Get prices with filters"""
        async with self.db.session() as session:
            query = select(CropPrice)
            
            if crop_id:
                query = query.where(CropPrice.crop_id == crop_id)
            if market_id:
                query = query.where(CropPrice.market_id == market_id)
            if start_date:
                query = query.where(CropPrice.price_date >= start_date)
            if end_date:
                query = query.where(CropPrice.price_date <= end_date)
            
            query = query.order_by(CropPrice.price_date.desc()).limit(limit)
            
            result = await session.execute(query)
            return result.scalars().all()
    
    async def get_latest_prices(
        self,
        crop_id: uuid.UUID,
        market_id: Optional[uuid.UUID] = None
    ) -> List[CropPrice]:
        """Get latest prices for a crop across markets"""
        async with self.db.session() as session:
            # Subquery for latest date per market
            subq = (
                select(
                    CropPrice.market_id,
                    func.max(CropPrice.price_date).label("max_date")
                )
                .where(CropPrice.crop_id == crop_id)
                .group_by(CropPrice.market_id)
            ).subquery()
            
            query = (
                select(CropPrice)
                .join(
                    subq,
                    and_(
                        CropPrice.market_id == subq.c.market_id,
                        CropPrice.price_date == subq.c.max_date
                    )
                )
                .where(CropPrice.crop_id == crop_id)
            )
            
            if market_id:
                query = query.where(CropPrice.market_id == market_id)
            
            result = await session.execute(query)
            return result.scalars().all()
    
    async def get_market_summary(self, crop_id: uuid.UUID) -> MarketSummary:
        """Get market summary for a crop"""
        async with self.db.session() as session:
            # Get crop info
            crop_result = await session.execute(
                select(Crop).where(Crop.id == crop_id)
            )
            crop = crop_result.scalar_one_or_none()
            
            if not crop:
                raise HTTPException(status_code=404, detail="Crop not found")
            
            # Get latest prices
            latest_prices = await self.get_latest_prices(crop_id)
            
            if not latest_prices:
                return MarketSummary(
                    crop_id=crop_id,
                    crop_name=crop.name,
                    crop_name_ar=crop.name_ar,
                    avg_price=0,
                    min_price=0,
                    max_price=0,
                    price_change_24h=None,
                    price_change_7d=None,
                    price_change_30d=None,
                    trend=PriceTrend.STABLE.value,
                    best_market=None,
                    best_market_price=None,
                    markets_reporting=0
                )
            
            prices = [p.price_avg for p in latest_prices]
            
            # Find best market
            best_price_record = max(latest_prices, key=lambda p: p.price_avg)
            
            # Get market name
            market_result = await session.execute(
                select(Market).where(Market.id == best_price_record.market_id)
            )
            best_market = market_result.scalar_one_or_none()
            
            # Calculate changes
            async def get_price_change(days: int) -> Optional[float]:
                old_date = date.today() - timedelta(days=days)
                result = await session.execute(
                    select(func.avg(CropPrice.price_avg))
                    .where(
                        CropPrice.crop_id == crop_id,
                        CropPrice.price_date == old_date
                    )
                )
                old_price = result.scalar()
                if old_price:
                    current_avg = sum(prices) / len(prices)
                    return ((current_avg - old_price) / old_price) * 100
                return None
            
            # Determine trend
            trends = [p.price_trend for p in latest_prices if p.price_trend]
            trend = max(set(trends), key=trends.count) if trends else PriceTrend.STABLE.value
            
            return MarketSummary(
                crop_id=crop_id,
                crop_name=crop.name,
                crop_name_ar=crop.name_ar,
                avg_price=round(sum(prices) / len(prices), 2),
                min_price=min(prices),
                max_price=max(prices),
                price_change_24h=await get_price_change(1),
                price_change_7d=await get_price_change(7),
                price_change_30d=await get_price_change(30),
                trend=trend,
                best_market=best_market.name if best_market else None,
                best_market_price=best_price_record.price_avg,
                markets_reporting=len(latest_prices)
            )
    
    async def create_price_alert(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        data: PriceAlertCreate
    ) -> PriceAlert:
        """Create price alert"""
        async with self.db.session() as session:
            alert = PriceAlert(
                tenant_id=tenant_id,
                user_id=user_id,
                **data.dict()
            )
            session.add(alert)
            await session.commit()
            await session.refresh(alert)
            return alert
    
    async def get_user_alerts(
        self,
        user_id: uuid.UUID,
        tenant_id: uuid.UUID
    ) -> List[PriceAlert]:
        """Get user's price alerts"""
        async with self.db.session() as session:
            result = await session.execute(
                select(PriceAlert).where(
                    PriceAlert.user_id == user_id,
                    PriceAlert.tenant_id == tenant_id,
                    PriceAlert.is_active == True
                )
            )
            return result.scalars().all()
    
    async def check_alerts(self, crop_id: uuid.UUID, market_id: uuid.UUID, current_price: float):
        """Check and trigger price alerts"""
        async with self.db.session() as session:
            result = await session.execute(
                select(PriceAlert).where(
                    PriceAlert.crop_id == crop_id,
                    PriceAlert.is_active == True,
                    (PriceAlert.market_id == market_id) | (PriceAlert.market_id.is_(None))
                )
            )
            alerts = result.scalars().all()
            
            for alert in alerts:
                should_trigger = False
                
                if alert.alert_type == "price_above" and current_price > alert.threshold_value:
                    should_trigger = True
                elif alert.alert_type == "price_below" and current_price < alert.threshold_value:
                    should_trigger = True
                
                if should_trigger:
                    alert.last_triggered = datetime.utcnow()
                    
                    # Emit alert event
                    await self.event_bus.publish(
                        "market.price_alert.triggered",
                        {
                            "alert_id": str(alert.id),
                            "user_id": str(alert.user_id),
                            "tenant_id": str(alert.tenant_id),
                            "crop_id": str(crop_id),
                            "alert_type": alert.alert_type,
                            "threshold": alert.threshold_value,
                            "current_price": current_price
                        }
                    )
            
            await session.commit()

# ============================================================================
# Dependencies
# ============================================================================

db: Database = None
event_bus: EventBus = None
market_service: MarketService = None

# ============================================================================
# FastAPI Application
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global db, event_bus, market_service
    
    logger.info("Starting Market Service...")
    
    db = Database(settings.DATABASE_URL)
    await db.connect()
    
    event_bus = EventBus(settings.NATS_URL)
    await event_bus.connect()
    
    market_service = MarketService(db, event_bus)
    
    logger.info("Market Service started successfully")
    
    yield
    
    logger.info("Shutting down Market Service...")
    await event_bus.close()
    await db.disconnect()

app = FastAPI(
    title="SAHOOL Market Service",
    description="Agricultural Market Prices & Analytics (Layer 2 - Signal Producer)",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ============================================================================
# API Endpoints (Internal Only - Layer 2)
# ============================================================================

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.SERVICE_NAME, "layer": settings.SERVICE_LAYER}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Markets (Internal)
@app.post("/internal/markets", response_model=MarketResponse, status_code=status.HTTP_201_CREATED)
async def create_market(data: MarketCreate):
    """Create market (internal)"""
    market = await market_service.create_market(data)
    return market

@app.get("/internal/markets", response_model=List[MarketResponse])
async def get_markets(
    governorate: Optional[str] = None,
    market_type: Optional[str] = None
):
    """Get markets (internal)"""
    markets = await market_service.get_markets(governorate, market_type)
    return markets

# Crops (Internal)
@app.post("/internal/crops", response_model=CropResponse, status_code=status.HTTP_201_CREATED)
async def create_crop(data: CropCreate):
    """Create crop (internal)"""
    crop = await market_service.create_crop(data)
    return crop

@app.get("/internal/crops", response_model=List[CropResponse])
async def get_crops(category: Optional[str] = None, search: Optional[str] = None):
    """Get crops (internal)"""
    crops = await market_service.get_crops(category, search)
    return crops

# Prices (Internal)
@app.post("/internal/prices", response_model=PriceResponse, status_code=status.HTTP_201_CREATED)
async def record_price(data: PriceCreate):
    """Record price (internal)"""
    price = await market_service.record_price(data)
    return price

@app.get("/internal/prices", response_model=List[PriceResponse])
async def get_prices(
    crop_id: Optional[uuid.UUID] = None,
    market_id: Optional[uuid.UUID] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(100, le=500)
):
    """Get prices (internal)"""
    prices = await market_service.get_prices(crop_id, market_id, start_date, end_date, limit)
    return prices

@app.get("/internal/crops/{crop_id}/latest-prices", response_model=List[PriceResponse])
async def get_latest_prices(crop_id: uuid.UUID, market_id: Optional[uuid.UUID] = None):
    """Get latest prices for crop (internal)"""
    prices = await market_service.get_latest_prices(crop_id, market_id)
    return prices

@app.get("/internal/crops/{crop_id}/summary", response_model=MarketSummary)
async def get_market_summary(crop_id: uuid.UUID):
    """Get market summary for crop (internal)"""
    summary = await market_service.get_market_summary(crop_id)
    return summary

# Alerts (Internal)
@app.post("/internal/alerts", response_model=PriceAlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(tenant_id: uuid.UUID, user_id: uuid.UUID, data: PriceAlertCreate):
    """Create price alert (internal)"""
    alert = await market_service.create_price_alert(tenant_id, user_id, data)
    return alert

@app.get("/internal/users/{user_id}/alerts", response_model=List[PriceAlertResponse])
async def get_user_alerts(user_id: uuid.UUID, tenant_id: uuid.UUID):
    """Get user alerts (internal)"""
    alerts = await market_service.get_user_alerts(user_id, tenant_id)
    return alerts

# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.SERVICE_PORT)
