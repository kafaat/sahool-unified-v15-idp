"""
SAHOOL Irrigation Smart Service - Database Utilities
======================================================
Provides optimized database operations for irrigation service.

Features:
- Connection pool management
- Query builder with parameterized queries
- Batch operations for sensor data
- Retry logic for transient failures
- Historical data aggregation
"""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PoolConfig:
    """Configuration for database connection pool."""

    min_connections: int = 2
    max_connections: int = 10
    command_timeout: int = 60
    idle_timeout: int = 300

    @classmethod
    def from_env(cls) -> PoolConfig:
        return cls(
            min_connections=int(os.getenv("DB_POOL_MIN", "2")),
            max_connections=int(os.getenv("DB_POOL_MAX", "10")),
            command_timeout=int(os.getenv("DB_COMMAND_TIMEOUT", "60")),
            idle_timeout=int(os.getenv("DB_IDLE_TIMEOUT", "300")),
        )


class IrrigationDatabase:
    """
    Database helper for irrigation service.
    Provides optimized queries for irrigation data.
    """

    def __init__(self, pool):
        self.pool = pool

    async def get_field_irrigation_history(
        self,
        field_id: str,
        days: int = 30,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get irrigation history for a field."""
        sql = """
            SELECT
                id, field_id, plan_id, schedule_id,
                amount_mm, duration_minutes, method,
                executed_at, created_at
            FROM irrigation_executions
            WHERE field_id = $1
              AND executed_at >= $2
            ORDER BY executed_at DESC
            LIMIT $3
        """
        start_date = datetime.now(UTC) - timedelta(days=days)

        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(sql, field_id, start_date, limit)
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching irrigation history: {e}")
            return []

    async def get_sensor_readings_summary(
        self,
        field_id: str,
        hours: int = 24,
    ) -> dict[str, Any]:
        """Get summary of sensor readings for a field."""
        sql = """
            SELECT
                COUNT(*) as reading_count,
                AVG(moisture_percent) as avg_moisture,
                MIN(moisture_percent) as min_moisture,
                MAX(moisture_percent) as max_moisture,
                AVG(temperature_c) as avg_temperature
            FROM soil_moisture_readings
            WHERE field_id = $1
              AND reading_time >= $2
        """
        start_time = datetime.now(UTC) - timedelta(hours=hours)

        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(sql, field_id, start_time)
                if row:
                    return {
                        "reading_count": row["reading_count"] or 0,
                        "avg_moisture": round(row["avg_moisture"] or 0, 2),
                        "min_moisture": round(row["min_moisture"] or 0, 2),
                        "max_moisture": round(row["max_moisture"] or 0, 2),
                        "avg_temperature": round(row["avg_temperature"] or 0, 2),
                    }
                return {}
        except Exception as e:
            logger.error(f"Error fetching sensor summary: {e}")
            return {}

    async def save_irrigation_plan(
        self,
        plan_id: str,
        field_id: str,
        crop: str,
        growth_stage: str,
        total_water_m3: float,
        estimated_cost: float,
        schedules: list[dict[str, Any]],
        tenant_id: str | None = None,
    ) -> bool:
        """Save irrigation plan to database."""
        plan_sql = """
            INSERT INTO irrigation_plans (
                id, field_id, crop, growth_stage,
                total_water_m3, estimated_cost_yer,
                schedules_count, tenant_id, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT (id) DO UPDATE SET
                total_water_m3 = EXCLUDED.total_water_m3,
                estimated_cost_yer = EXCLUDED.estimated_cost_yer,
                updated_at = NOW()
        """

        schedule_sql = """
            INSERT INTO irrigation_schedules (
                id, plan_id, field_id, irrigation_date,
                start_time, duration_minutes, water_amount_liters,
                urgency, method, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """

        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    # Save plan
                    await conn.execute(
                        plan_sql,
                        plan_id,
                        field_id,
                        crop,
                        growth_stage,
                        total_water_m3,
                        estimated_cost,
                        len(schedules),
                        tenant_id,
                        datetime.now(UTC),
                    )

                    # Save schedules
                    for schedule in schedules:
                        await conn.execute(
                            schedule_sql,
                            schedule.get("schedule_id"),
                            plan_id,
                            field_id,
                            schedule.get("irrigation_date"),
                            schedule.get("start_time"),
                            schedule.get("duration_minutes"),
                            schedule.get("water_amount_liters"),
                            schedule.get("urgency"),
                            schedule.get("method"),
                            datetime.now(UTC),
                        )

            logger.info(f"Saved irrigation plan {plan_id} with {len(schedules)} schedules")
            return True

        except Exception as e:
            logger.error(f"Error saving irrigation plan: {e}")
            return False

    async def save_irrigation_execution(
        self,
        execution_id: str,
        field_id: str,
        plan_id: str | None,
        schedule_id: str | None,
        amount_mm: float,
        duration_minutes: int,
        method: str,
        executed_at: datetime,
        tenant_id: str | None = None,
    ) -> bool:
        """Save irrigation execution record."""
        sql = """
            INSERT INTO irrigation_executions (
                id, field_id, plan_id, schedule_id,
                amount_mm, duration_minutes, method,
                executed_at, tenant_id, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """

        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    sql,
                    execution_id,
                    field_id,
                    plan_id,
                    schedule_id,
                    amount_mm,
                    duration_minutes,
                    method,
                    executed_at,
                    tenant_id,
                    datetime.now(UTC),
                )

            logger.info(f"Saved irrigation execution {execution_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving irrigation execution: {e}")
            return False

    async def batch_save_sensor_readings(
        self,
        readings: list[dict[str, Any]],
    ) -> int:
        """Batch insert sensor readings."""
        if not readings:
            return 0

        sql = """
            INSERT INTO soil_moisture_readings (
                id, field_id, sensor_id, reading_time,
                depth_cm, moisture_percent, temperature_c, ec_ds_m
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (sensor_id, reading_time) DO NOTHING
        """

        try:
            async with self.pool.acquire() as conn:
                async with conn.transaction():
                    for reading in readings:
                        await conn.execute(
                            sql,
                            reading.get("id"),
                            reading.get("field_id"),
                            reading.get("sensor_id"),
                            reading.get("reading_time"),
                            reading.get("depth_cm", 30),
                            reading.get("moisture_percent"),
                            reading.get("temperature_c"),
                            reading.get("ec_ds_m"),
                        )

            logger.info(f"Saved {len(readings)} sensor readings in batch")
            return len(readings)

        except Exception as e:
            logger.error(f"Error batch saving sensor readings: {e}")
            return 0

    async def get_water_balance_summary(
        self,
        field_id: str,
        days: int = 14,
    ) -> dict[str, Any]:
        """Get water balance summary for planning."""
        sql = """
            SELECT
                SUM(et_mm) as total_et,
                SUM(rainfall_mm) as total_rainfall,
                SUM(irrigation_mm) as total_irrigation,
                SUM(et_mm) - SUM(rainfall_mm) - SUM(irrigation_mm) as cumulative_deficit
            FROM water_balance
            WHERE field_id = $1
              AND date >= $2
        """
        start_date = date.today() - timedelta(days=days)

        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(sql, field_id, start_date)
                if row:
                    return {
                        "total_et_mm": round(row["total_et"] or 0, 2),
                        "total_rainfall_mm": round(row["total_rainfall"] or 0, 2),
                        "total_irrigation_mm": round(row["total_irrigation"] or 0, 2),
                        "cumulative_deficit_mm": round(row["cumulative_deficit"] or 0, 2),
                        "period_days": days,
                    }
                return {}
        except Exception as e:
            logger.error(f"Error fetching water balance: {e}")
            return {}


async def with_retry(
    func,
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
):
    """Execute async function with retry logic."""
    last_exception = None

    for attempt in range(1, max_attempts + 1):
        try:
            return await func()
        except Exception as e:
            last_exception = e
            if attempt == max_attempts:
                logger.error(f"Operation failed after {max_attempts} attempts: {e}")
                raise

            logger.warning(f"Retry {attempt}/{max_attempts}: {e}")
            await asyncio.sleep(delay)
            delay *= backoff

    raise last_exception


async def create_pool(database_url: str, config: PoolConfig | None = None):
    """Create database connection pool."""
    try:
        import asyncpg

        config = config or PoolConfig.from_env()

        pool = await asyncpg.create_pool(
            database_url,
            min_size=config.min_connections,
            max_size=config.max_connections,
            command_timeout=config.command_timeout,
        )

        logger.info(f"Database pool created (min={config.min_connections}, max={config.max_connections})")

        return pool

    except ImportError:
        logger.warning("asyncpg not available, database features disabled")
        return None
    except Exception as e:
        logger.error(f"Failed to create database pool: {e}")
        return None
