"""
Soft Delete Usage Examples for Billing Core
============================================

This module demonstrates how to use the soft delete pattern with SQLAlchemy
in the billing service.

Author: SAHOOL Team
"""

# Import the soft delete utilities
import sys
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

sys.path.append("/home/user/sahool-unified-v15-idp/packages/shared-db/src")
from soft_delete_sqlalchemy import (
    count_active_records,
    count_deleted_records,
    get_active_records,
    get_deleted_records,
    get_deletion_metadata,
    restore_many,
    restore_record,
    soft_delete_many,
    soft_delete_record,
)

# Import your models (these would be your actual billing models)
from src.models import Invoice, Payment, Subscription


class SoftDeleteExamplesService:
    """
    Service class demonstrating soft delete operations in billing core.
    """

    def __init__(self, session: Session):
        self.session = session

    # ════════════════════════════════════════════════════════════════════════
    # Basic Operations - العمليات الأساسية
    # ════════════════════════════════════════════════════════════════════════

    def soft_delete_subscription(
        self, subscription_id: str, deleted_by: str
    ) -> Subscription | None:
        """
        Example 1: Soft delete a subscription
        مثال 1: حذف ناعم لاشتراك

        Args:
            subscription_id: ID of the subscription to delete
            deleted_by: User ID performing the deletion

        Returns:
            The soft-deleted subscription or None if not found
        """
        subscription = soft_delete_record(
            self.session, Subscription, subscription_id, deleted_by=deleted_by
        )

        if subscription:
            print(f"Subscription {subscription_id} soft-deleted by {deleted_by}")

        self.session.commit()
        return subscription

    def get_active_subscriptions(
        self, tenant_id: str | None = None
    ) -> list[Subscription]:
        """
        Example 2: Get all active subscriptions
        مثال 2: الحصول على جميع الاشتراكات النشطة

        Args:
            tenant_id: Optional tenant ID to filter by

        Returns:
            List of active subscriptions
        """
        filters = {}
        if tenant_id:
            filters["tenant_id"] = tenant_id

        subscriptions = get_active_records(self.session, Subscription, **filters)

        print(f"Found {len(subscriptions)} active subscriptions")
        return subscriptions

    def get_deleted_subscriptions(self) -> list[Subscription]:
        """
        Example 3: Get all deleted subscriptions
        مثال 3: الحصول على جميع الاشتراكات المحذوفة

        Returns:
            List of soft-deleted subscriptions
        """
        subscriptions = get_deleted_records(self.session, Subscription)

        print(f"Found {len(subscriptions)} deleted subscriptions")
        return subscriptions

    def restore_subscription(self, subscription_id: str) -> Subscription | None:
        """
        Example 4: Restore a soft-deleted subscription
        مثال 4: استعادة اشتراك محذوف

        Args:
            subscription_id: ID of the subscription to restore

        Returns:
            The restored subscription or None if not found
        """
        subscription = restore_record(self.session, Subscription, subscription_id)

        if subscription:
            print(f"Subscription {subscription_id} restored successfully")

        self.session.commit()
        return subscription

    # ════════════════════════════════════════════════════════════════════════
    # Advanced Operations - عمليات متقدمة
    # ════════════════════════════════════════════════════════════════════════

    def soft_delete_expired_trials(self, deleted_by: str) -> int:
        """
        Example 5: Soft delete all expired trial subscriptions
        مثال 5: حذف ناعم لجميع الاشتراكات التجريبية المنتهية

        Args:
            deleted_by: User ID performing the deletion

        Returns:
            Number of subscriptions deleted
        """
        # Find expired trials
        today = datetime.utcnow().date()

        # First, get the subscriptions to delete
        expired_trials = (
            self.session.query(Subscription)
            .filter(
                Subscription.status == "trial",
                Subscription.trial_end_date < today,
                Subscription.deleted_at.is_(None),
            )
            .all()
        )

        # Soft delete each one
        for subscription in expired_trials:
            subscription.soft_delete(deleted_by=deleted_by)

        count = len(expired_trials)
        self.session.commit()

        print(f"Soft-deleted {count} expired trial subscriptions")
        return count

    def cascade_delete_tenant_data(self, tenant_id: str, deleted_by: str) -> dict:
        """
        Example 6: Cascade soft delete all data for a tenant
        مثال 6: حذف ناعم متتالي لجميع بيانات مستأجر

        Args:
            tenant_id: Tenant ID
            deleted_by: User ID performing the deletion

        Returns:
            Dictionary with counts of deleted records
        """
        counts = {}

        # Delete subscriptions
        counts["subscriptions"] = soft_delete_many(
            self.session, Subscription, deleted_by=deleted_by, tenant_id=tenant_id
        )

        # Delete invoices
        counts["invoices"] = soft_delete_many(
            self.session, Invoice, deleted_by=deleted_by, tenant_id=tenant_id
        )

        # Delete payments
        counts["payments"] = soft_delete_many(
            self.session, Payment, deleted_by=deleted_by, tenant_id=tenant_id
        )

        self.session.commit()

        print(f"Cascade deleted data for tenant {tenant_id}")
        print(f"  - Subscriptions: {counts['subscriptions']}")
        print(f"  - Invoices: {counts['invoices']}")
        print(f"  - Payments: {counts['payments']}")

        return counts

    def get_subscription_stats(self) -> dict:
        """
        Example 7: Get subscription statistics
        مثال 7: الحصول على إحصائيات الاشتراكات

        Returns:
            Dictionary with subscription counts
        """
        active_count = count_active_records(self.session, Subscription)
        deleted_count = count_deleted_records(self.session, Subscription)
        total_count = active_count + deleted_count

        stats = {
            "active": active_count,
            "deleted": deleted_count,
            "total": total_count,
            "deletion_rate": (
                (deleted_count / total_count * 100) if total_count > 0 else 0
            ),
        }

        print("Subscription Statistics:")
        print(f"  Active: {stats['active']}")
        print(f"  Deleted: {stats['deleted']}")
        print(f"  Total: {stats['total']}")
        print(f"  Deletion Rate: {stats['deletion_rate']:.2f}%")

        return stats

    def check_subscription_deletion_status(self, subscription_id: str) -> dict:
        """
        Example 8: Check if a subscription is deleted and get metadata
        مثال 8: التحقق من حذف اشتراك والحصول على البيانات الوصفية

        Args:
            subscription_id: Subscription ID to check

        Returns:
            Dictionary with deletion status and metadata
        """
        # Get subscription including deleted ones
        subscription = (
            self.session.query(Subscription)
            .filter(Subscription.id == subscription_id)
            .first()
        )

        if not subscription:
            return {"found": False, "deleted": False, "metadata": None}

        is_deleted = subscription.is_deleted()
        metadata = get_deletion_metadata(subscription)

        result = {"found": True, "deleted": is_deleted, "metadata": metadata}

        if is_deleted:
            print(f"Subscription {subscription_id} is deleted")
            print(f"  Deleted at: {metadata['deleted_at']}")
            print(f"  Deleted by: {metadata['deleted_by']}")
        else:
            print(f"Subscription {subscription_id} is active")

        return result

    def get_deletion_audit_trail(
        self, start_date: datetime, end_date: datetime
    ) -> list[dict]:
        """
        Example 9: Get deletion audit trail for a date range
        مثال 9: الحصول على سجل تدقيق الحذف لنطاق تاريخ

        Args:
            start_date: Start of date range
            end_date: End of date range

        Returns:
            List of deletion records
        """
        # Find all subscriptions deleted in the date range
        deleted_subscriptions = (
            self.session.query(Subscription)
            .filter(
                Subscription.deleted_at >= start_date,
                Subscription.deleted_at <= end_date,
            )
            .all()
        )

        audit_trail = []
        for subscription in deleted_subscriptions:
            metadata = get_deletion_metadata(subscription)
            audit_trail.append(
                {
                    "subscription_id": str(subscription.id),
                    "tenant_id": subscription.tenant_id,
                    "plan_id": subscription.plan_id,
                    "deleted_at": metadata["deleted_at"],
                    "deleted_by": metadata["deleted_by"],
                }
            )

        print(f"Found {len(audit_trail)} deletions between {start_date} and {end_date}")
        return audit_trail

    def restore_recent_deletions(self, hours: int = 24) -> int:
        """
        Example 10: Restore all subscriptions deleted in the last N hours
        مثال 10: استعادة جميع الاشتراكات المحذوفة في آخر N ساعة

        Args:
            hours: Number of hours to look back

        Returns:
            Number of subscriptions restored
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Find recently deleted subscriptions
        recent_deleted = (
            self.session.query(Subscription)
            .filter(Subscription.deleted_at >= cutoff_time)
            .all()
        )

        count = 0
        for subscription in recent_deleted:
            subscription.restore()
            count += 1

        self.session.commit()

        print(f"Restored {count} subscriptions deleted in the last {hours} hours")
        return count

    # ════════════════════════════════════════════════════════════════════════
    # Query Examples - أمثلة الاستعلامات
    # ════════════════════════════════════════════════════════════════════════

    def find_active_subscriptions_with_filters(
        self, plan_id: str | None = None, status: str | None = None
    ) -> list[Subscription]:
        """
        Example 11: Complex query with soft delete filtering
        مثال 11: استعلام معقد مع تصفية الحذف الناعم

        Args:
            plan_id: Optional plan ID to filter by
            status: Optional status to filter by

        Returns:
            List of matching active subscriptions
        """
        # Build query
        query = self.session.query(Subscription)

        # Add soft delete filter
        query = Subscription.filter_active(query)

        # Add optional filters
        if plan_id:
            query = query.filter(Subscription.plan_id == plan_id)

        if status:
            query = query.filter(Subscription.status == status)

        # Order by created date
        query = query.order_by(Subscription.created_at.desc())

        subscriptions = query.all()

        print(f"Found {len(subscriptions)} active subscriptions matching filters")
        return subscriptions

    def bulk_restore_by_tenant(self, tenant_id: str) -> int:
        """
        Example 12: Bulk restore all deleted subscriptions for a tenant
        مثال 12: استعادة جماعية لجميع الاشتراكات المحذوفة لمستأجر

        Args:
            tenant_id: Tenant ID

        Returns:
            Number of subscriptions restored
        """
        count = restore_many(self.session, Subscription, tenant_id=tenant_id)

        self.session.commit()

        print(f"Restored {count} subscriptions for tenant {tenant_id}")
        return count

    def cleanup_old_deleted_records(self, days: int = 180) -> int:
        """
        Example 13: Permanently delete old soft-deleted records
        مثال 13: حذف دائم للسجلات المحذوفة القديمة

        CAUTION: This permanently deletes records. Use with care!

        Args:
            days: Number of days after which to permanently delete

        Returns:
            Number of records permanently deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Find old deleted subscriptions
        old_deleted = (
            self.session.query(Subscription)
            .filter(Subscription.deleted_at < cutoff_date)
            .all()
        )

        count = len(old_deleted)

        # Permanently delete them
        for subscription in old_deleted:
            self.session.delete(subscription)  # Hard delete

        self.session.commit()

        print(f"Permanently deleted {count} subscriptions older than {days} days")
        return count


# ════════════════════════════════════════════════════════════════════════════
# Usage Example
# ════════════════════════════════════════════════════════════════════════════


def main():
    """
    Main function demonstrating usage of the soft delete examples.
    """
    from src.database import SessionLocal

    # Create a database session
    session = SessionLocal()

    try:
        # Create the examples service
        SoftDeleteExamplesService(session)

        # Example 1: Soft delete a subscription
        # service.soft_delete_subscription('sub-123', deleted_by='admin-456')

        # Example 2: Get active subscriptions
        # active_subs = service.get_active_subscriptions(tenant_id='tenant-789')

        # Example 3: Get subscription stats
        # stats = service.get_subscription_stats()

        # Example 4: Restore a subscription
        # service.restore_subscription('sub-123')

        # Example 5: Get deletion audit trail
        # from datetime import datetime, timedelta
        # start = datetime.utcnow() - timedelta(days=7)
        # end = datetime.utcnow()
        # audit_trail = service.get_deletion_audit_trail(start, end)

        print("Soft delete examples completed successfully!")

    finally:
        session.close()


if __name__ == "__main__":
    main()
