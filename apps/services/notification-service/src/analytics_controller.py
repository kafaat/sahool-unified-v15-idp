"""
SAHOOL Notification Analytics Controller
مراقب تحليلات الإشعارات

Provides comprehensive API endpoints for notification analytics,
dashboard data, and performance monitoring.
"""

import logging
from datetime import UTC, datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel

from .analytics_service import NotificationAnalytics, TimeRange
from .history_controller import get_tenant_id

logger = logging.getLogger("sahool-notifications.analytics")

router = APIRouter(prefix="/analytics", tags=["Notification Analytics | تحليلات الإشعارات"])


# =============================================================================
# Response Models
# =============================================================================


class DeliveryStatsResponse(BaseModel):
    """استجابة إحصائيات التسليم"""

    time_range: str
    start_time: str
    end_time: str
    total_notifications: int
    sent: int
    failed: int
    pending: int
    read: int
    delivery_rate: float
    failure_rate: float
    read_rate: float


class ChannelPerformanceResponse(BaseModel):
    """استجابة أداء القنوات"""

    time_range: str
    channels: dict[str, Any]
    best_performing_channel: str | None
    best_success_rate: float


class DashboardSummaryResponse(BaseModel):
    """استجابة ملخص لوحة القيادة"""

    generated_at: str
    summary: dict[str, Any]
    delivery: dict[str, Any]
    channels: dict[str, Any]
    types: dict[str, Any]
    engagement: dict[str, Any]


# =============================================================================
# API Endpoints
# =============================================================================


@router.get("/delivery-stats")
async def get_delivery_statistics(
    time_range: str = Query(default="day", description="Time range: hour, day, week, month, quarter, year"),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    إحصائيات التسليم
    Get delivery statistics for specified time range

    Args:
        time_range: Time range to analyze
        tenant_id: Optional tenant filter

    Returns:
        Delivery statistics including success/failure rates
    """
    try:
        range_enum = TimeRange(time_range)
        stats = await NotificationAnalytics.get_delivery_stats(range_enum, tenant_id)
        return stats

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid time_range: {time_range}. Valid values: hour, day, week, month, quarter, year",
        )
    except Exception as e:
        logger.error(f"Error getting delivery stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/channel-performance")
async def get_channel_performance(
    time_range: str = Query(default="day", description="Time range"),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    أداء القنوات
    Get performance metrics by notification channel

    Args:
        time_range: Time range to analyze
        tenant_id: Optional tenant filter

    Returns:
        Channel performance metrics
    """
    try:
        range_enum = TimeRange(time_range)
        stats = await NotificationAnalytics.get_channel_performance(range_enum, tenant_id)
        return stats

    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid time_range: {time_range}")
    except Exception as e:
        logger.error(f"Error getting channel performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notification-types")
async def get_notification_type_breakdown(
    time_range: str = Query(default="week", description="Time range"),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    تفصيل أنواع الإشعارات
    Get breakdown of notifications by type

    Args:
        time_range: Time range to analyze
        tenant_id: Optional tenant filter

    Returns:
        Notification type breakdown with counts and percentages
    """
    try:
        range_enum = TimeRange(time_range)
        stats = await NotificationAnalytics.get_notification_type_breakdown(range_enum, tenant_id)
        return stats

    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid time_range: {time_range}")
    except Exception as e:
        logger.error(f"Error getting type breakdown: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/regional-distribution")
async def get_regional_distribution(
    time_range: str = Query(default="week", description="Time range"),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    التوزيع الجغرافي
    Get notification distribution by governorate/region

    Args:
        time_range: Time range to analyze
        tenant_id: Optional tenant filter

    Returns:
        Regional distribution data
    """
    try:
        range_enum = TimeRange(time_range)
        stats = await NotificationAnalytics.get_regional_distribution(range_enum, tenant_id)
        return stats

    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid time_range: {time_range}")
    except Exception as e:
        logger.error(f"Error getting regional distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hourly-trends")
async def get_hourly_trends(
    days: int = Query(default=7, ge=1, le=30, description="Number of days to analyze"),
    tenant_id: str | None = Query(default=None),
):
    """
    الاتجاهات بالساعة
    Get notification trends by hour of day

    Args:
        days: Number of days to analyze
        tenant_id: Optional tenant filter

    Returns:
        Hourly trend data with peak hours
    """
    try:
        stats = await NotificationAnalytics.get_hourly_trends(days, tenant_id)
        return stats

    except Exception as e:
        logger.error(f"Error getting hourly trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user-engagement")
async def get_user_engagement(
    user_id: str | None = Query(default=None, description="Specific user ID"),
    time_range: str = Query(default="week", description="Time range"),
    tenant_id: str | None = Query(default=None),
):
    """
    تفاعل المستخدم
    Get user engagement metrics

    Args:
        user_id: Optional specific user ID
        time_range: Time range to analyze
        tenant_id: Optional tenant filter

    Returns:
        User engagement metrics
    """
    try:
        range_enum = TimeRange(time_range)
        stats = await NotificationAnalytics.get_user_engagement(
            user_id=user_id,
            time_range=range_enum,
            tenant_id=tenant_id,
        )
        return stats

    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid time_range: {time_range}")
    except Exception as e:
        logger.error(f"Error getting user engagement: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/priority-distribution")
async def get_priority_distribution(
    time_range: str = Query(default="week", description="Time range"),
    tenant_id: str | None = Query(default=None),
):
    """
    توزيع الأولويات
    Get distribution of notifications by priority

    Args:
        time_range: Time range to analyze
        tenant_id: Optional tenant filter

    Returns:
        Priority distribution data
    """
    try:
        range_enum = TimeRange(time_range)
        stats = await NotificationAnalytics.get_priority_distribution(range_enum, tenant_id)
        return stats

    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid time_range: {time_range}")
    except Exception as e:
        logger.error(f"Error getting priority distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_dashboard_summary(
    tenant_id: str | None = Query(default=None),
):
    """
    ملخص لوحة القيادة
    Get comprehensive dashboard summary with all key metrics

    Args:
        tenant_id: Optional tenant filter

    Returns:
        Complete dashboard data
    """
    try:
        summary = await NotificationAnalytics.get_dashboard_summary(tenant_id)
        return summary

    except Exception as e:
        logger.error(f"Error getting dashboard summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def get_notification_health():
    """
    صحة نظام الإشعارات
    Get notification system health status

    Returns:
        System health metrics
    """
    try:
        # Get delivery stats for last hour
        hourly_stats = await NotificationAnalytics.get_delivery_stats(TimeRange.HOUR)

        # Determine health status
        delivery_rate = hourly_stats.get("delivery_rate", 0)
        failure_rate = hourly_stats.get("failure_rate", 0)

        if delivery_rate >= 95:
            health_status = "healthy"
            health_status_ar = "سليم"
        elif delivery_rate >= 80:
            health_status = "degraded"
            health_status_ar = "متدهور"
        else:
            health_status = "critical"
            health_status_ar = "حرج"

        return {
            "status": health_status,
            "status_ar": health_status_ar,
            "timestamp": datetime.now(UTC).isoformat(),
            "metrics": {
                "delivery_rate_1h": delivery_rate,
                "failure_rate_1h": failure_rate,
                "notifications_sent_1h": hourly_stats.get("sent", 0),
                "notifications_failed_1h": hourly_stats.get("failed", 0),
            },
            "thresholds": {
                "healthy": ">=95% delivery rate",
                "degraded": "80-95% delivery rate",
                "critical": "<80% delivery rate",
            },
        }

    except Exception as e:
        logger.error(f"Error getting health status: {e}")
        return {
            "status": "unknown",
            "status_ar": "غير معروف",
            "error": str(e),
            "timestamp": datetime.now(UTC).isoformat(),
        }


@router.get("/compare")
async def compare_time_periods(
    current_range: str = Query(default="week", description="Current time range"),
    previous_range: str = Query(default="week", description="Previous time range for comparison"),
    tenant_id: str | None = Query(default=None),
):
    """
    مقارنة الفترات الزمنية
    Compare notification metrics between two time periods

    Args:
        current_range: Current time range
        previous_range: Previous time range
        tenant_id: Optional tenant filter

    Returns:
        Comparison data with change percentages
    """
    try:
        current_enum = TimeRange(current_range)
        previous_enum = TimeRange(previous_range)

        # Get stats for both periods
        current_stats = await NotificationAnalytics.get_delivery_stats(current_enum, tenant_id)

        # For previous period, we'd need to adjust the time window
        # This is simplified - in production would calculate actual previous period
        previous_stats = await NotificationAnalytics.get_delivery_stats(previous_enum, tenant_id)

        # Calculate changes
        def calc_change(current: float, previous: float) -> float:
            if previous == 0:
                return 100 if current > 0 else 0
            return round(((current - previous) / previous) * 100, 2)

        return {
            "current_period": {
                "range": current_range,
                "stats": current_stats,
            },
            "previous_period": {
                "range": previous_range,
                "stats": previous_stats,
            },
            "changes": {
                "total_notifications": calc_change(
                    current_stats.get("total_notifications", 0),
                    previous_stats.get("total_notifications", 0),
                ),
                "delivery_rate": calc_change(
                    current_stats.get("delivery_rate", 0), previous_stats.get("delivery_rate", 0)
                ),
                "read_rate": calc_change(current_stats.get("read_rate", 0), previous_stats.get("read_rate", 0)),
            },
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error comparing time periods: {e}")
        raise HTTPException(status_code=500, detail=str(e))
