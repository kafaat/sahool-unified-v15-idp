"""
SAHOOL Notification Analytics Service
خدمة تحليلات الإشعارات

Provides comprehensive analytics for notification system performance,
delivery metrics, and user engagement tracking.
"""

import logging
from collections import defaultdict
from datetime import UTC, datetime, timedelta, timezone
from enum import Enum, StrEnum
from typing import Any

from tortoise.functions import Count

from .models import (
    FarmerProfile,
    Notification,
    NotificationChannel,
    NotificationLog,
    NotificationPreference,
)

logger = logging.getLogger("sahool-notifications.analytics")


class TimeRange(StrEnum):
    """فترة زمنية للتحليلات"""

    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"


class NotificationAnalytics:
    """
    خدمة تحليلات الإشعارات

    Features:
    - Delivery success/failure rates
    - Channel performance metrics
    - User engagement tracking
    - Time-based analytics
    - Regional distribution
    - Notification type breakdown
    """

    @staticmethod
    async def get_delivery_stats(
        time_range: TimeRange = TimeRange.DAY,
        tenant_id: str | None = None,
    ) -> dict[str, Any]:
        """
        إحصائيات التسليم
        Get delivery statistics for notifications

        Args:
            time_range: Time range for analytics
            tenant_id: Optional tenant filter

        Returns:
            Dict with delivery statistics
        """
        try:
            # Calculate time window
            now = datetime.now(UTC)
            start_time = NotificationAnalytics._get_start_time(now, time_range)

            # Build query
            query = Notification.filter(created_at__gte=start_time)
            if tenant_id:
                query = query.filter(tenant_id=tenant_id)

            # Get counts by status
            total = await query.count()
            sent = await query.filter(status="sent").count()
            failed = await query.filter(status="failed").count()
            pending = await query.filter(status="pending").count()
            read = await query.filter(status="read").count()

            # Calculate rates
            delivery_rate = (sent / total * 100) if total > 0 else 0
            failure_rate = (failed / total * 100) if total > 0 else 0
            read_rate = (read / sent * 100) if sent > 0 else 0

            return {
                "time_range": time_range.value,
                "start_time": start_time.isoformat(),
                "end_time": now.isoformat(),
                "total_notifications": total,
                "sent": sent,
                "failed": failed,
                "pending": pending,
                "read": read,
                "delivery_rate": round(delivery_rate, 2),
                "failure_rate": round(failure_rate, 2),
                "read_rate": round(read_rate, 2),
            }

        except Exception as e:
            logger.error(f"Error getting delivery stats: {e}")
            raise

    @staticmethod
    async def get_channel_performance(
        time_range: TimeRange = TimeRange.DAY,
        tenant_id: str | None = None,
    ) -> dict[str, Any]:
        """
        أداء القنوات
        Get performance metrics by notification channel

        Args:
            time_range: Time range for analytics
            tenant_id: Optional tenant filter

        Returns:
            Dict with channel performance data
        """
        try:
            now = datetime.now(UTC)
            start_time = NotificationAnalytics._get_start_time(now, time_range)

            # Get logs grouped by channel
            query = NotificationLog.filter(attempted_at__gte=start_time)

            channels = ["push", "sms", "email", "whatsapp", "in_app"]
            channel_stats = {}

            for channel in channels:
                channel_query = query.filter(channel=channel)

                total = await channel_query.count()
                success = await channel_query.filter(status="sent").count()
                failed = await channel_query.filter(status="failed").count()

                # Calculate average latency from logs
                # Simplified - in production would use actual timing data

                channel_stats[channel] = {
                    "total": total,
                    "success": success,
                    "failed": failed,
                    "success_rate": round((success / total * 100) if total > 0 else 0, 2),
                    "failure_rate": round((failed / total * 100) if total > 0 else 0, 2),
                }

            # Calculate overall best performing channel
            best_channel = max(
                channel_stats.items(),
                key=lambda x: x[1]["success_rate"],
                default=(None, {"success_rate": 0}),
            )

            return {
                "time_range": time_range.value,
                "channels": channel_stats,
                "best_performing_channel": best_channel[0],
                "best_success_rate": best_channel[1]["success_rate"],
            }

        except Exception as e:
            logger.error(f"Error getting channel performance: {e}")
            raise

    @staticmethod
    async def get_notification_type_breakdown(
        time_range: TimeRange = TimeRange.WEEK,
        tenant_id: str | None = None,
    ) -> dict[str, Any]:
        """
        تفصيل أنواع الإشعارات
        Get breakdown of notifications by type

        Args:
            time_range: Time range for analytics
            tenant_id: Optional tenant filter

        Returns:
            Dict with notification type breakdown
        """
        try:
            now = datetime.now(UTC)
            start_time = NotificationAnalytics._get_start_time(now, time_range)

            query = Notification.filter(created_at__gte=start_time)
            if tenant_id:
                query = query.filter(tenant_id=tenant_id)

            # Notification types
            types = [
                "weather_alert",
                "pest_outbreak",
                "irrigation_reminder",
                "crop_health",
                "market_price",
                "system",
                "task_reminder",
            ]

            type_stats = {}
            total = await query.count()

            for ntype in types:
                type_count = await query.filter(type=ntype).count()
                sent = await query.filter(type=ntype, status="sent").count()
                read = await query.filter(type=ntype, read_at__isnull=False).count()

                type_stats[ntype] = {
                    "count": type_count,
                    "percentage": round((type_count / total * 100) if total > 0 else 0, 2),
                    "sent": sent,
                    "read": read,
                    "read_rate": round((read / sent * 100) if sent > 0 else 0, 2),
                }

            # Find most common type
            most_common = max(type_stats.items(), key=lambda x: x[1]["count"], default=(None, {"count": 0}))

            return {
                "time_range": time_range.value,
                "total_notifications": total,
                "types": type_stats,
                "most_common_type": most_common[0],
                "most_common_count": most_common[1]["count"],
            }

        except Exception as e:
            logger.error(f"Error getting type breakdown: {e}")
            raise

    @staticmethod
    async def get_regional_distribution(
        time_range: TimeRange = TimeRange.WEEK,
        tenant_id: str | None = None,
    ) -> dict[str, Any]:
        """
        التوزيع الجغرافي
        Get notification distribution by governorate/region

        Args:
            time_range: Time range for analytics
            tenant_id: Optional tenant filter

        Returns:
            Dict with regional distribution data
        """
        try:
            now = datetime.now(UTC)
            start_time = NotificationAnalytics._get_start_time(now, time_range)

            # Get farmers grouped by governorate
            governorates = [
                "sanaa",
                "aden",
                "taiz",
                "hodeidah",
                "ibb",
                "dhamar",
                "hadramaut",
                "marib",
                "hajjah",
                "saada",
                "lahj",
                "abyan",
            ]

            governorate_stats = {}

            for gov in governorates:
                # Count farmers in this governorate
                farmers = await FarmerProfile.filter(governorate=gov, is_active=True).values_list(
                    "farmer_id", flat=True
                )

                farmer_count = len(farmers)

                if farmer_count > 0:
                    # Count notifications to these farmers
                    notif_count = await Notification.filter(user_id__in=farmers, created_at__gte=start_time).count()

                    governorate_stats[gov] = {
                        "farmer_count": farmer_count,
                        "notification_count": notif_count,
                        "notifications_per_farmer": round(notif_count / farmer_count, 2) if farmer_count > 0 else 0,
                    }

            # Calculate totals
            total_farmers = sum(s["farmer_count"] for s in governorate_stats.values())
            total_notifications = sum(s["notification_count"] for s in governorate_stats.values())

            return {
                "time_range": time_range.value,
                "governorates": governorate_stats,
                "total_farmers": total_farmers,
                "total_notifications": total_notifications,
                "average_per_farmer": round(total_notifications / total_farmers, 2) if total_farmers > 0 else 0,
            }

        except Exception as e:
            logger.error(f"Error getting regional distribution: {e}")
            raise

    @staticmethod
    async def get_hourly_trends(
        days: int = 7,
        tenant_id: str | None = None,
    ) -> dict[str, Any]:
        """
        الاتجاهات بالساعة
        Get notification trends by hour of day

        Args:
            days: Number of days to analyze
            tenant_id: Optional tenant filter

        Returns:
            Dict with hourly trend data
        """
        try:
            now = datetime.now(UTC)
            start_time = now - timedelta(days=days)

            query = Notification.filter(created_at__gte=start_time)
            if tenant_id:
                query = query.filter(tenant_id=tenant_id)

            # Get all notifications in range
            notifications = await query.all()

            # Group by hour
            hourly_counts: dict[int, int] = defaultdict(int)
            hourly_sent: dict[int, int] = defaultdict(int)
            hourly_read: dict[int, int] = defaultdict(int)

            for notif in notifications:
                hour = notif.created_at.hour
                hourly_counts[hour] += 1
                if notif.status == "sent":
                    hourly_sent[hour] += 1
                if notif.read_at:
                    hourly_read[hour] += 1

            # Build hourly data
            hourly_data = []
            for hour in range(24):
                hourly_data.append(
                    {
                        "hour": hour,
                        "hour_label": f"{hour:02d}:00",
                        "total": hourly_counts[hour],
                        "sent": hourly_sent[hour],
                        "read": hourly_read[hour],
                    }
                )

            # Find peak hours
            peak_hour = max(hourly_data, key=lambda x: x["total"])

            return {
                "days_analyzed": days,
                "hourly_data": hourly_data,
                "peak_hour": peak_hour["hour"],
                "peak_hour_label": peak_hour["hour_label"],
                "peak_hour_count": peak_hour["total"],
            }

        except Exception as e:
            logger.error(f"Error getting hourly trends: {e}")
            raise

    @staticmethod
    async def get_user_engagement(
        user_id: str | None = None,
        time_range: TimeRange = TimeRange.WEEK,
        tenant_id: str | None = None,
    ) -> dict[str, Any]:
        """
        تفاعل المستخدم
        Get user engagement metrics

        Args:
            user_id: Optional specific user ID
            time_range: Time range for analytics
            tenant_id: Optional tenant filter

        Returns:
            Dict with user engagement data
        """
        try:
            now = datetime.now(UTC)
            start_time = NotificationAnalytics._get_start_time(now, time_range)

            query = Notification.filter(created_at__gte=start_time)
            if tenant_id:
                query = query.filter(tenant_id=tenant_id)
            if user_id:
                query = query.filter(user_id=user_id)

            # Get notifications
            notifications = await query.all()

            # Calculate engagement metrics
            total = len(notifications)
            read_count = sum(1 for n in notifications if n.read_at)

            # Calculate average time to read
            read_times = []
            for notif in notifications:
                if notif.read_at and notif.sent_at:
                    time_diff = (notif.read_at - notif.sent_at).total_seconds()
                    if time_diff > 0:
                        read_times.append(time_diff)

            avg_read_time = sum(read_times) / len(read_times) if read_times else 0

            # Get most engaged users (top 10)
            if not user_id:
                user_reads: dict[str, int] = defaultdict(int)
                for notif in notifications:
                    if notif.read_at:
                        user_reads[notif.user_id] += 1

                top_users = sorted(user_reads.items(), key=lambda x: x[1], reverse=True)[:10]
            else:
                top_users = []

            return {
                "time_range": time_range.value,
                "user_id": user_id,
                "total_notifications": total,
                "read_notifications": read_count,
                "engagement_rate": round((read_count / total * 100) if total > 0 else 0, 2),
                "average_read_time_seconds": round(avg_read_time, 2),
                "average_read_time_minutes": round(avg_read_time / 60, 2),
                "top_engaged_users": [{"user_id": uid, "read_count": count} for uid, count in top_users]
                if top_users
                else None,
            }

        except Exception as e:
            logger.error(f"Error getting user engagement: {e}")
            raise

    @staticmethod
    async def get_priority_distribution(
        time_range: TimeRange = TimeRange.WEEK,
        tenant_id: str | None = None,
    ) -> dict[str, Any]:
        """
        توزيع الأولويات
        Get distribution of notifications by priority

        Args:
            time_range: Time range for analytics
            tenant_id: Optional tenant filter

        Returns:
            Dict with priority distribution data
        """
        try:
            now = datetime.now(UTC)
            start_time = NotificationAnalytics._get_start_time(now, time_range)

            query = Notification.filter(created_at__gte=start_time)
            if tenant_id:
                query = query.filter(tenant_id=tenant_id)

            priorities = ["low", "medium", "high", "critical"]
            priority_stats = {}
            total = await query.count()

            for priority in priorities:
                count = await query.filter(priority=priority).count()
                sent = await query.filter(priority=priority, status="sent").count()
                read = await query.filter(priority=priority, read_at__isnull=False).count()

                priority_stats[priority] = {
                    "count": count,
                    "percentage": round((count / total * 100) if total > 0 else 0, 2),
                    "sent": sent,
                    "read": read,
                    "read_rate": round((read / sent * 100) if sent > 0 else 0, 2),
                }

            return {
                "time_range": time_range.value,
                "total_notifications": total,
                "priorities": priority_stats,
            }

        except Exception as e:
            logger.error(f"Error getting priority distribution: {e}")
            raise

    @staticmethod
    async def get_dashboard_summary(
        tenant_id: str | None = None,
    ) -> dict[str, Any]:
        """
        ملخص لوحة القيادة
        Get comprehensive dashboard summary

        Args:
            tenant_id: Optional tenant filter

        Returns:
            Dict with complete dashboard data
        """
        try:
            # Get multiple analytics in parallel
            delivery_stats = await NotificationAnalytics.get_delivery_stats(TimeRange.DAY, tenant_id)
            channel_perf = await NotificationAnalytics.get_channel_performance(TimeRange.DAY, tenant_id)
            type_breakdown = await NotificationAnalytics.get_notification_type_breakdown(TimeRange.WEEK, tenant_id)
            user_engagement = await NotificationAnalytics.get_user_engagement(
                time_range=TimeRange.WEEK, tenant_id=tenant_id
            )

            # Get farmer count
            farmer_count = await FarmerProfile.filter(is_active=True).count()

            # Get preference statistics
            preference_count = await NotificationPreference.all().count()

            return {
                "generated_at": datetime.now(UTC).isoformat(),
                "summary": {
                    "total_farmers": farmer_count,
                    "total_preferences": preference_count,
                    "today_notifications": delivery_stats["total_notifications"],
                    "today_delivery_rate": delivery_stats["delivery_rate"],
                    "weekly_engagement_rate": user_engagement["engagement_rate"],
                },
                "delivery": delivery_stats,
                "channels": channel_perf,
                "types": type_breakdown,
                "engagement": user_engagement,
            }

        except Exception as e:
            logger.error(f"Error getting dashboard summary: {e}")
            raise

    @staticmethod
    def _get_start_time(now: datetime, time_range: TimeRange) -> datetime:
        """Helper to calculate start time based on time range"""
        if time_range == TimeRange.HOUR:
            return now - timedelta(hours=1)
        elif time_range == TimeRange.DAY:
            return now - timedelta(days=1)
        elif time_range == TimeRange.WEEK:
            return now - timedelta(weeks=1)
        elif time_range == TimeRange.MONTH:
            return now - timedelta(days=30)
        elif time_range == TimeRange.QUARTER:
            return now - timedelta(days=90)
        elif time_range == TimeRange.YEAR:
            return now - timedelta(days=365)
        else:
            return now - timedelta(days=1)
