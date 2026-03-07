"""
SAHOOL Notification History Controller
مراقب سجل الإشعارات

Provides comprehensive API endpoints for notification history,
delivery logs, and audit trail.
"""

import logging
from datetime import UTC, datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from .analytics_service import NotificationAnalytics, TimeRange
from .models import Notification, NotificationLog
from .repository import (
    NotificationLogRepository,
    NotificationRepository,
)

logger = logging.getLogger("sahool-notifications.history")

router = APIRouter(prefix="/history", tags=["Notification History | سجل الإشعارات"])


# =============================================================================
# Request/Response Models
# =============================================================================


class NotificationHistoryResponse(BaseModel):
    """استجابة سجل الإشعارات"""

    id: str
    user_id: str
    title: str
    title_ar: str | None
    body: str
    body_ar: str | None
    type: str
    priority: str
    channel: str
    status: str
    is_read: bool
    created_at: datetime
    sent_at: datetime | None
    read_at: datetime | None
    expires_at: datetime | None
    data: dict[str, Any] | None


class DeliveryLogResponse(BaseModel):
    """استجابة سجل التسليم"""

    id: str
    notification_id: str
    channel: str
    status: str
    error_message: str | None
    provider_message_id: str | None
    retry_count: int
    attempted_at: datetime
    completed_at: datetime | None


class HistoryStatsResponse(BaseModel):
    """استجابة إحصائيات السجل"""

    total_notifications: int
    sent: int
    failed: int
    pending: int
    read: int
    delivery_rate: float
    read_rate: float


class PaginatedHistoryResponse(BaseModel):
    """استجابة سجل مرقم"""

    total: int
    page: int
    page_size: int
    total_pages: int
    notifications: list[NotificationHistoryResponse]


# =============================================================================
# API Endpoints
# =============================================================================


@router.get("/user/{user_id}", response_model=PaginatedHistoryResponse)
async def get_user_notification_history(
    user_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None, description="Filter by status: pending, sent, failed, read"),
    type: str | None = Query(default=None, description="Filter by notification type"),
    channel: str | None = Query(default=None, description="Filter by channel"),
    start_date: datetime | None = Query(default=None, description="Filter from date"),
    end_date: datetime | None = Query(default=None, description="Filter to date"),
    include_expired: bool = Query(default=False, description="Include expired notifications"),
):
    """
    الحصول على سجل إشعارات المستخدم
    Get paginated notification history for a user

    Args:
        user_id: User ID
        page: Page number (1-indexed)
        page_size: Number of items per page
        status: Optional status filter
        type: Optional notification type filter
        channel: Optional channel filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        include_expired: Whether to include expired notifications

    Returns:
        Paginated list of notifications
    """
    try:
        # Build query
        offset = (page - 1) * page_size

        # Get notifications with filters
        query = Notification.filter(user_id=user_id)

        if status:
            query = query.filter(status=status)
        if type:
            query = query.filter(type=type)
        if channel:
            query = query.filter(channel=channel)
        if start_date:
            query = query.filter(created_at__gte=start_date)
        if end_date:
            query = query.filter(created_at__lte=end_date)
        if not include_expired:
            now = datetime.now(UTC)
            query = query.filter(expires_at__gt=now) | query.filter(expires_at__isnull=True)

        # Get total count
        total = await query.count()

        # Get paginated results
        notifications = await query.order_by("-created_at").offset(offset).limit(page_size).all()

        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size

        # Format response
        notification_list = [
            NotificationHistoryResponse(
                id=str(n.id),
                user_id=n.user_id,
                title=n.title,
                title_ar=n.title_ar,
                body=n.body,
                body_ar=n.body_ar,
                type=n.type,
                priority=n.priority,
                channel=n.channel,
                status=n.status,
                is_read=n.is_read,
                created_at=n.created_at,
                sent_at=n.sent_at,
                read_at=n.read_at,
                expires_at=n.expires_at,
                data=n.data,
            )
            for n in notifications
        ]

        return PaginatedHistoryResponse(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            notifications=notification_list,
        )

    except Exception as e:
        logger.error(f"Error getting user history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/notification/{notification_id}")
async def get_notification_details(
    notification_id: str,
):
    """
    الحصول على تفاصيل إشعار
    Get detailed information about a specific notification

    Args:
        notification_id: Notification UUID

    Returns:
        Notification details with delivery logs
    """
    try:
        notif_uuid = UUID(notification_id)

        # Get notification
        notification = await NotificationRepository.get_by_id(notif_uuid)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")

        # Get delivery logs
        logs = await NotificationLogRepository.get_notification_logs(notif_uuid)

        # Format logs
        log_list = [
            DeliveryLogResponse(
                id=str(log.id),
                notification_id=str(log.notification_id),
                channel=log.channel,
                status=log.status,
                error_message=log.error_message,
                provider_message_id=log.provider_message_id,
                retry_count=log.retry_count,
                attempted_at=log.attempted_at,
                completed_at=log.completed_at,
            )
            for log in logs
        ]

        return {
            "notification": NotificationHistoryResponse(
                id=str(notification.id),
                user_id=notification.user_id,
                title=notification.title,
                title_ar=notification.title_ar,
                body=notification.body,
                body_ar=notification.body_ar,
                type=notification.type,
                priority=notification.priority,
                channel=notification.channel,
                status=notification.status,
                is_read=notification.is_read,
                created_at=notification.created_at,
                sent_at=notification.sent_at,
                read_at=notification.read_at,
                expires_at=notification.expires_at,
                data=notification.data,
            ),
            "delivery_logs": log_list,
            "delivery_attempts": len(log_list),
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid notification ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notification details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/delivery-logs/{notification_id}")
async def get_delivery_logs(
    notification_id: str,
):
    """
    الحصول على سجلات التسليم
    Get delivery logs for a notification

    Args:
        notification_id: Notification UUID

    Returns:
        List of delivery log entries
    """
    try:
        notif_uuid = UUID(notification_id)
        logs = await NotificationLogRepository.get_notification_logs(notif_uuid)

        return {
            "notification_id": notification_id,
            "total_logs": len(logs),
            "logs": [
                DeliveryLogResponse(
                    id=str(log.id),
                    notification_id=str(log.notification_id),
                    channel=log.channel,
                    status=log.status,
                    error_message=log.error_message,
                    provider_message_id=log.provider_message_id,
                    retry_count=log.retry_count,
                    attempted_at=log.attempted_at,
                    completed_at=log.completed_at,
                )
                for log in logs
            ],
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid notification ID format")
    except Exception as e:
        logger.error(f"Error getting delivery logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/failed")
async def get_failed_notifications(
    limit: int = Query(default=50, ge=1, le=200),
    retry_pending: bool = Query(default=False, description="Only show notifications pending retry"),
):
    """
    الحصول على الإشعارات الفاشلة
    Get failed notifications for monitoring

    Args:
        limit: Maximum number of records
        retry_pending: Only show notifications pending retry

    Returns:
        List of failed notifications with details
    """
    try:
        # Get failed logs
        failed_logs = await NotificationLogRepository.get_failed_logs(limit=limit)

        if retry_pending:
            failed_logs = [log for log in failed_logs if log.retry_count < 3]

        results = []
        for log in failed_logs:
            # Get notification details
            notification = await NotificationRepository.get_by_id(log.notification_id)

            results.append(
                {
                    "log_id": str(log.id),
                    "notification_id": str(log.notification_id),
                    "user_id": notification.user_id if notification else None,
                    "channel": log.channel,
                    "status": log.status,
                    "error_message": log.error_message,
                    "retry_count": log.retry_count,
                    "next_retry_at": log.next_retry_at.isoformat() if log.next_retry_at else None,
                    "attempted_at": log.attempted_at.isoformat(),
                    "notification_type": notification.type if notification else None,
                    "notification_title": notification.title if notification else None,
                }
            )

        return {
            "total": len(results),
            "failed_notifications": results,
        }

    except Exception as e:
        logger.error(f"Error getting failed notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=HistoryStatsResponse)
async def get_notification_stats(
    user_id: str | None = Query(default=None, description="Filter by user ID"),
    days: int = Query(default=7, ge=1, le=365, description="Number of days to analyze"),
    tenant_id: str | None = Query(default=None, description="Tenant ID filter"),
):
    """
    إحصائيات الإشعارات
    Get notification statistics

    Args:
        user_id: Optional user ID filter
        days: Number of days to analyze
        tenant_id: Optional tenant filter

    Returns:
        Notification statistics
    """
    try:
        start_date = datetime.now(UTC) - timedelta(days=days)

        # Build query
        query = Notification.filter(created_at__gte=start_date)
        if user_id:
            query = query.filter(user_id=user_id)
        if tenant_id:
            query = query.filter(tenant_id=tenant_id)

        # Get counts
        total = await query.count()
        sent = await query.filter(status="sent").count()
        failed = await query.filter(status="failed").count()
        pending = await query.filter(status="pending").count()
        read = await query.filter(read_at__isnull=False).count()

        # Calculate rates
        delivery_rate = (sent / total * 100) if total > 0 else 0
        read_rate = (read / sent * 100) if sent > 0 else 0

        return HistoryStatsResponse(
            total_notifications=total,
            sent=sent,
            failed=failed,
            pending=pending,
            read=read,
            delivery_rate=round(delivery_rate, 2),
            read_rate=round(read_rate, 2),
        )

    except Exception as e:
        logger.error(f"Error getting notification stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/old")
async def cleanup_old_notifications(
    days: int = Query(default=30, ge=7, le=365, description="Delete notifications older than this many days"),
):
    """
    تنظيف الإشعارات القديمة
    Delete old notifications to free up database space

    Args:
        days: Number of days to keep

    Returns:
        Number of notifications deleted
    """
    try:
        deleted_count = await NotificationRepository.delete_old_notifications(days=days)

        logger.info(f"Deleted {deleted_count} notifications older than {days} days")

        return {
            "success": True,
            "deleted_count": deleted_count,
            "message": f"Deleted {deleted_count} notifications older than {days} days",
            "message_ar": f"تم حذف {deleted_count} إشعار أقدم من {days} يوم",
        }

    except Exception as e:
        logger.error(f"Error cleaning up old notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def export_notification_history(
    user_id: str | None = Query(default=None),
    start_date: datetime = Query(..., description="Export start date"),
    end_date: datetime = Query(..., description="Export end date"),
    format: str = Query(default="json", description="Export format: json, csv"),
    limit: int = Query(default=1000, ge=1, le=10000),
):
    """
    تصدير سجل الإشعارات
    Export notification history for a date range

    Args:
        user_id: Optional user ID filter
        start_date: Start date for export
        end_date: End date for export
        format: Export format (json or csv)
        limit: Maximum records to export

    Returns:
        Exported data in requested format
    """
    try:
        # Build query
        query = Notification.filter(created_at__gte=start_date, created_at__lte=end_date)

        if user_id:
            query = query.filter(user_id=user_id)

        # Get notifications
        notifications = await query.order_by("-created_at").limit(limit).all()

        # Format data
        data = [
            {
                "id": str(n.id),
                "user_id": n.user_id,
                "title": n.title,
                "title_ar": n.title_ar,
                "type": n.type,
                "priority": n.priority,
                "channel": n.channel,
                "status": n.status,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat(),
                "sent_at": n.sent_at.isoformat() if n.sent_at else None,
                "read_at": n.read_at.isoformat() if n.read_at else None,
            }
            for n in notifications
        ]

        if format == "csv":
            # Convert to CSV format
            if not data:
                csv_content = ""
            else:
                headers = list(data[0].keys())
                csv_lines = [",".join(headers)]
                for row in data:
                    csv_lines.append(",".join(str(row.get(h, "")) for h in headers))
                csv_content = "\n".join(csv_lines)

            return {
                "format": "csv",
                "total_records": len(data),
                "content": csv_content,
            }

        return {
            "format": "json",
            "total_records": len(data),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "data": data,
        }

    except Exception as e:
        logger.error(f"Error exporting notification history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retry/{notification_id}")
async def retry_failed_notification(
    notification_id: str,
):
    """
    إعادة محاولة إرسال إشعار فاشل
    Retry sending a failed notification

    Args:
        notification_id: Notification UUID

    Returns:
        Retry result
    """
    try:
        notif_uuid = UUID(notification_id)

        # Get notification
        notification = await NotificationRepository.get_by_id(notif_uuid)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")

        if notification.status != "failed":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot retry notification with status '{notification.status}'",
            )

        # Reset status to pending for retry
        await NotificationRepository.update_status(notif_uuid, status="pending")

        logger.info(f"Scheduled retry for notification {notification_id}")

        return {
            "success": True,
            "notification_id": notification_id,
            "message": "Notification queued for retry",
            "message_ar": "تم إضافة الإشعار لقائمة الإعادة",
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid notification ID format")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrying notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))
