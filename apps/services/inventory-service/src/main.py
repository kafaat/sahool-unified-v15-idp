"""
SAHOOL Inventory Service - Main API
Agricultural inventory management and analytics
Port: 8115
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

import sys
# Use relative path instead of hardcoded absolute path
shared_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
sys.path.append(shared_path)
from database.base import Base

from .models.inventory import (
    InventoryItem, InventoryMovement, InventoryTransaction,
    Warehouse, ItemCategory, Supplier, MovementType, TransactionType
)
from .inventory_analytics import InventoryAnalytics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/sahool_inventory")
engine = create_async_engine(DATABASE_URL, echo=os.getenv("SQL_ECHO", "false").lower() == "true", pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Inventory Service...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables ready")
    except Exception as e:
        logger.warning(f"Database setup warning: {e}")
    logger.info("Inventory Service ready on port 8115")
    yield
    await engine.dispose()
    logger.info("Inventory Service shutting down")

app = FastAPI(title="SAHOOL Inventory Service", description="Agricultural inventory management, forecasting, and analytics", version="1.0.0", lifespan=lifespan)

# CORS Configuration - secure origins from environment
CORS_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:8080").split(",")
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=True, allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"], allow_headers=["Content-Type", "Authorization", "X-Tenant-Id"])

@app.get("/healthz")
def health():
    return {"status": "healthy", "service": "inventory-service", "version": "1.0.0"}

class ItemCategoryCreate(BaseModel):
    name_en: str
    name_ar: str
    code: str
    description: Optional[str] = None

class ItemCategoryResponse(BaseModel):
    id: str
    name_en: str
    name_ar: str
    code: str
    is_active: bool

@app.post("/v1/categories", response_model=ItemCategoryResponse)
async def create_category(category: ItemCategoryCreate, db: AsyncSession = Depends(get_db)):
    db_category = ItemCategory(name_en=category.name_en, name_ar=category.name_ar, code=category.code, description=category.description)
    db.add(db_category)
    await db.flush()
    return ItemCategoryResponse(id=str(db_category.id), name_en=db_category.name_en, name_ar=db_category.name_ar, code=db_category.code, is_active=db_category.is_active)

@app.get("/v1/analytics/forecast/{item_id}")
async def get_forecast(item_id: str, tenant_id: str = Query(...), forecast_days: int = Query(90, ge=1, le=365), db: AsyncSession = Depends(get_db)):
    analytics = InventoryAnalytics(db, tenant_id)
    forecast = await analytics.get_consumption_forecast(item_id, forecast_days)
    if not forecast:
        raise HTTPException(status_code=404, detail="Item not found")
    return forecast.to_dict()

@app.get("/v1/analytics/forecasts")
async def get_all_forecasts(tenant_id: str = Query(...), category: Optional[str] = None, low_stock_only: bool = False, db: AsyncSession = Depends(get_db)):
    analytics = InventoryAnalytics(db, tenant_id)
    forecasts = await analytics.get_all_forecasts(category, low_stock_only)
    return [f.to_dict() for f in forecasts]

@app.get("/v1/analytics/reorder-recommendations")
async def get_reorder_recommendations(tenant_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    analytics = InventoryAnalytics(db, tenant_id)
    recommendations = await analytics.get_reorder_recommendations()
    return {"tenant_id": tenant_id, "count": len(recommendations), "recommendations": recommendations}

@app.get("/v1/analytics/valuation")
async def get_valuation(tenant_id: str = Query(...), warehouse_id: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    analytics = InventoryAnalytics(db, tenant_id)
    valuation = await analytics.get_inventory_valuation(warehouse_id=warehouse_id)
    return valuation.to_dict()

@app.get("/v1/analytics/turnover")
async def get_turnover(tenant_id: str = Query(...), period_days: int = Query(365, ge=30, le=730), db: AsyncSession = Depends(get_db)):
    analytics = InventoryAnalytics(db, tenant_id)
    metrics = await analytics.get_turnover_analysis(period_days)
    return {"tenant_id": tenant_id, "period_days": period_days, "items": [m.to_dict() for m in metrics]}

@app.get("/v1/analytics/slow-moving")
async def get_slow_moving(tenant_id: str = Query(...), days_threshold: int = Query(90, ge=30, le=365), db: AsyncSession = Depends(get_db)):
    analytics = InventoryAnalytics(db, tenant_id)
    items = await analytics.identify_slow_moving(days_threshold)
    return {"tenant_id": tenant_id, "days_threshold": days_threshold, "count": len(items), "total_value": sum(item['total_value'] for item in items), "items": items}

@app.get("/v1/analytics/dead-stock")
async def get_dead_stock(tenant_id: str = Query(...), days_threshold: int = Query(180, ge=90, le=730), db: AsyncSession = Depends(get_db)):
    analytics = InventoryAnalytics(db, tenant_id)
    items = await analytics.identify_dead_stock(days_threshold)
    return {"tenant_id": tenant_id, "days_threshold": days_threshold, "count": len(items), "total_value": sum(item['total_value'] for item in items), "items": items}

@app.get("/v1/analytics/abc-analysis")
async def get_abc_analysis(tenant_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    analytics = InventoryAnalytics(db, tenant_id)
    analysis = await analytics.get_abc_analysis()
    return {"tenant_id": tenant_id, **analysis}

@app.get("/v1/analytics/seasonal-patterns/{item_id}")
async def get_seasonal_patterns(item_id: str, tenant_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    analytics = InventoryAnalytics(db, tenant_id)
    pattern = await analytics.get_seasonal_patterns(item_id)
    if not pattern:
        raise HTTPException(status_code=404, detail="Item not found or insufficient historical data")
    return pattern.to_dict()

@app.get("/v1/analytics/cost-analysis")
async def get_cost_analysis(tenant_id: str = Query(...), field_id: Optional[str] = None, crop_season_id: Optional[str] = None, start_date: Optional[date] = None, end_date: Optional[date] = None, db: AsyncSession = Depends(get_db)):
    analytics = InventoryAnalytics(db, tenant_id)
    analysis = await analytics.get_cost_analysis(field_id=field_id, crop_season_id=crop_season_id, start_date=start_date, end_date=end_date)
    return {"tenant_id": tenant_id, **analysis}

@app.get("/v1/analytics/waste-analysis")
async def get_waste_analysis(tenant_id: str = Query(...), period_days: int = Query(365, ge=30, le=730), db: AsyncSession = Depends(get_db)):
    analytics = InventoryAnalytics(db, tenant_id)
    analysis = await analytics.get_waste_analysis(period_days)
    return {"tenant_id": tenant_id, **analysis}

@app.get("/v1/analytics/dashboard")
async def get_dashboard_metrics(tenant_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    analytics = InventoryAnalytics(db, tenant_id)
    metrics = await analytics.generate_dashboard_metrics()
    return {"tenant_id": tenant_id, **metrics}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8115))
    uvicorn.run(app, host="0.0.0.0", port=port)
