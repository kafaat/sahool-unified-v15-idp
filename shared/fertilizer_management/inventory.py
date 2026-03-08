"""
Fertilizer Inventory Management - إدارة مخزون الأسمدة

Track fertilizer inventory, consumption, and reorder alerts.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from .models import (
    Fertilizer,
    FertilizerApplication,
    InventoryItem,
    InventoryStatus,
)


@dataclass
class InventoryTransaction:
    """
    Inventory transaction record - سجل حركة المخزون
    """

    id: str
    tenant_id: str
    inventory_item_id: str
    transaction_type: str  # receipt, issue, adjustment, transfer, return
    transaction_type_ar: str

    # Quantity
    quantity_kg: float
    quantity_before_kg: float
    quantity_after_kg: float

    # Reference
    reference_type: str = ""  # purchase_order, application, adjustment
    reference_id: str = ""

    # Cost
    unit_cost: Decimal = Decimal("0.00")
    total_cost: Decimal = Decimal("0.00")
    currency: str = "SAR"

    # User info
    created_by: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Notes
    reason: str = ""
    reason_ar: str = ""
    notes: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "inventory_item_id": self.inventory_item_id,
            "transaction_type": self.transaction_type,
            "quantity_kg": self.quantity_kg,
            "quantity_before_kg": self.quantity_before_kg,
            "quantity_after_kg": self.quantity_after_kg,
            "unit_cost": float(self.unit_cost),
            "total_cost": float(self.total_cost),
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class InventoryAlert:
    """
    Inventory alert - تنبيه المخزون
    """

    id: str
    tenant_id: str
    inventory_item_id: str
    fertilizer_name: str
    fertilizer_name_ar: str

    # Alert type
    alert_type: str  # low_stock, out_of_stock, expiring_soon, expired
    alert_type_ar: str
    severity: str  # info, warning, critical

    # Details
    current_quantity_kg: float
    threshold_kg: float
    expiry_date: datetime | None = None
    days_until_expiry: int | None = None

    # Messages
    title_en: str = ""
    title_ar: str = ""
    message_en: str = ""
    message_ar: str = ""

    # Recommendations
    recommended_action_en: str = ""
    recommended_action_ar: str = ""
    recommended_order_quantity_kg: float = 0.0

    # Status
    acknowledged: bool = False
    acknowledged_by: str | None = None
    acknowledged_at: datetime | None = None
    resolved: bool = False
    resolved_at: datetime | None = None

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict:
        """Convert to dictionary for NATS publishing"""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "inventory_item_id": self.inventory_item_id,
            "fertilizer_name": self.fertilizer_name,
            "fertilizer_name_ar": self.fertilizer_name_ar,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "current_quantity_kg": self.current_quantity_kg,
            "title_en": self.title_en,
            "title_ar": self.title_ar,
            "message_en": self.message_en,
            "message_ar": self.message_ar,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class InventorySummary:
    """
    Inventory summary report - تقرير ملخص المخزون
    """

    tenant_id: str
    report_date: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Totals
    total_items: int = 0
    total_quantity_kg: float = 0.0
    total_value: Decimal = Decimal("0.00")
    currency: str = "SAR"

    # Status breakdown
    in_stock_count: int = 0
    low_stock_count: int = 0
    out_of_stock_count: int = 0
    expired_count: int = 0
    expiring_soon_count: int = 0

    # By type
    by_fertilizer_type: dict = field(default_factory=dict)

    # Top items
    top_items_by_value: list[dict] = field(default_factory=list)
    items_needing_reorder: list[dict] = field(default_factory=list)

    # Alerts
    active_alerts_count: int = 0
    critical_alerts: list[InventoryAlert] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "tenant_id": self.tenant_id,
            "report_date": self.report_date.isoformat(),
            "total_items": self.total_items,
            "total_quantity_kg": self.total_quantity_kg,
            "total_value": float(self.total_value),
            "status_breakdown": {
                "in_stock": self.in_stock_count,
                "low_stock": self.low_stock_count,
                "out_of_stock": self.out_of_stock_count,
                "expired": self.expired_count,
                "expiring_soon": self.expiring_soon_count,
            },
            "by_type": self.by_fertilizer_type,
            "active_alerts": self.active_alerts_count,
        }


class FertilizerInventoryManager:
    """
    Manager for fertilizer inventory operations
    مدير عمليات مخزون الأسمدة
    """

    TRANSACTION_TYPES = {
        "receipt": "استلام",
        "issue": "صرف",
        "adjustment": "تعديل",
        "transfer": "تحويل",
        "return": "إرجاع",
        "write_off": "شطب",
    }

    ALERT_TYPES = {
        "low_stock": "مخزون منخفض",
        "out_of_stock": "نفد المخزون",
        "expiring_soon": "قارب انتهاء الصلاحية",
        "expired": "منتهي الصلاحية",
        "overstock": "مخزون زائد",
    }

    def __init__(
        self,
        inventory_items: list[InventoryItem] | None = None,
        expiry_warning_days: int = 30,
    ):
        """
        Initialize inventory manager.

        Args:
            inventory_items: Initial inventory items (in-memory storage)
            expiry_warning_days: Days before expiry to generate warning
        """
        self._inventory: dict[str, InventoryItem] = {}
        self._transactions: list[InventoryTransaction] = []
        self._alerts: list[InventoryAlert] = []
        self.expiry_warning_days = expiry_warning_days

        # Load initial inventory
        if inventory_items:
            for item in inventory_items:
                self._inventory[item.id] = item

    def add_item(self, item: InventoryItem) -> InventoryItem:
        """
        Add new inventory item.

        Args:
            item: Inventory item to add

        Returns:
            Added inventory item
        """
        self._inventory[item.id] = item
        self._update_item_status(item)
        return item

    def get_item(self, item_id: str) -> InventoryItem | None:
        """Get inventory item by ID."""
        return self._inventory.get(item_id)

    def get_all_items(self, tenant_id: str) -> list[InventoryItem]:
        """Get all inventory items for a tenant."""
        return [item for item in self._inventory.values() if item.tenant_id == tenant_id]

    def get_items_by_fertilizer(self, tenant_id: str, fertilizer_id: str) -> list[InventoryItem]:
        """Get inventory items for a specific fertilizer."""
        return [
            item
            for item in self._inventory.values()
            if item.tenant_id == tenant_id and item.fertilizer_id == fertilizer_id
        ]

    def receive_stock(
        self,
        item_id: str,
        quantity_kg: float,
        unit_cost: Decimal,
        batch_number: str = "",
        expiry_date: datetime | None = None,
        supplier: str = "",
        supplier_ar: str = "",
        created_by: str = "",
        reference_id: str = "",
        notes: str = "",
    ) -> tuple[InventoryItem, InventoryTransaction]:
        """
        Receive stock into inventory.

        Args:
            item_id: Inventory item ID
            quantity_kg: Quantity received in kg
            unit_cost: Cost per kg
            batch_number: Batch/lot number
            expiry_date: Expiration date
            supplier: Supplier name
            supplier_ar: Supplier name in Arabic
            created_by: User ID
            reference_id: Purchase order reference
            notes: Additional notes

        Returns:
            Tuple of (updated item, transaction record)
        """
        item = self._inventory.get(item_id)
        if not item:
            raise ValueError(f"Inventory item not found: {item_id}")

        quantity_before = item.quantity_kg
        item.quantity_kg += quantity_kg
        item.purchase_price_per_kg = unit_cost

        if batch_number:
            item.batch_number = batch_number
        if expiry_date:
            item.expiry_date = expiry_date
        if supplier:
            item.supplier = supplier
            item.supplier_ar = supplier_ar

        item.updated_at = datetime.now(UTC)
        self._update_item_status(item)

        # Create transaction
        transaction = InventoryTransaction(
            id=str(uuid.uuid4()),
            tenant_id=item.tenant_id,
            inventory_item_id=item_id,
            transaction_type="receipt",
            transaction_type_ar=self.TRANSACTION_TYPES["receipt"],
            quantity_kg=quantity_kg,
            quantity_before_kg=quantity_before,
            quantity_after_kg=item.quantity_kg,
            unit_cost=unit_cost,
            total_cost=unit_cost * Decimal(str(quantity_kg)),
            reference_type="purchase_order",
            reference_id=reference_id,
            created_by=created_by,
            reason="Stock receipt",
            reason_ar="استلام مخزون",
            notes=notes,
        )
        self._transactions.append(transaction)

        return item, transaction

    def issue_stock(
        self,
        item_id: str,
        quantity_kg: float,
        application: FertilizerApplication | None = None,
        created_by: str = "",
        reason: str = "",
        reason_ar: str = "",
    ) -> tuple[InventoryItem, InventoryTransaction]:
        """
        Issue stock from inventory (for field application).

        Args:
            item_id: Inventory item ID
            quantity_kg: Quantity to issue in kg
            application: Related fertilizer application record
            created_by: User ID
            reason: Reason for issue
            reason_ar: Reason in Arabic

        Returns:
            Tuple of (updated item, transaction record)

        Raises:
            ValueError: If insufficient stock
        """
        item = self._inventory.get(item_id)
        if not item:
            raise ValueError(f"Inventory item not found: {item_id}")

        if item.available_kg < quantity_kg:
            raise ValueError(f"Insufficient stock. Available: {item.available_kg} kg, Requested: {quantity_kg} kg")

        quantity_before = item.quantity_kg
        item.quantity_kg -= quantity_kg
        item.updated_at = datetime.now(UTC)
        self._update_item_status(item)

        # Create transaction
        transaction = InventoryTransaction(
            id=str(uuid.uuid4()),
            tenant_id=item.tenant_id,
            inventory_item_id=item_id,
            transaction_type="issue",
            transaction_type_ar=self.TRANSACTION_TYPES["issue"],
            quantity_kg=-quantity_kg,
            quantity_before_kg=quantity_before,
            quantity_after_kg=item.quantity_kg,
            unit_cost=item.purchase_price_per_kg,
            total_cost=item.purchase_price_per_kg * Decimal(str(quantity_kg)),
            reference_type="application" if application else "",
            reference_id=application.id if application else "",
            created_by=created_by,
            reason=reason or "Field application",
            reason_ar=reason_ar or "تطبيق حقلي",
        )
        self._transactions.append(transaction)

        return item, transaction

    def adjust_stock(
        self,
        item_id: str,
        new_quantity_kg: float,
        created_by: str = "",
        reason: str = "",
        reason_ar: str = "",
    ) -> tuple[InventoryItem, InventoryTransaction]:
        """
        Adjust inventory quantity (physical count adjustment).

        Args:
            item_id: Inventory item ID
            new_quantity_kg: New quantity after adjustment
            created_by: User ID
            reason: Reason for adjustment
            reason_ar: Reason in Arabic

        Returns:
            Tuple of (updated item, transaction record)
        """
        item = self._inventory.get(item_id)
        if not item:
            raise ValueError(f"Inventory item not found: {item_id}")

        quantity_before = item.quantity_kg
        quantity_change = new_quantity_kg - quantity_before
        item.quantity_kg = new_quantity_kg
        item.updated_at = datetime.now(UTC)
        self._update_item_status(item)

        # Create transaction
        transaction = InventoryTransaction(
            id=str(uuid.uuid4()),
            tenant_id=item.tenant_id,
            inventory_item_id=item_id,
            transaction_type="adjustment",
            transaction_type_ar=self.TRANSACTION_TYPES["adjustment"],
            quantity_kg=quantity_change,
            quantity_before_kg=quantity_before,
            quantity_after_kg=item.quantity_kg,
            unit_cost=item.purchase_price_per_kg,
            total_cost=item.purchase_price_per_kg * Decimal(str(abs(quantity_change))),
            reference_type="stock_count",
            created_by=created_by,
            reason=reason or "Physical count adjustment",
            reason_ar=reason_ar or "تعديل جرد فعلي",
        )
        self._transactions.append(transaction)

        return item, transaction

    def reserve_stock(
        self,
        item_id: str,
        quantity_kg: float,
    ) -> InventoryItem:
        """
        Reserve stock for planned application.

        Args:
            item_id: Inventory item ID
            quantity_kg: Quantity to reserve

        Returns:
            Updated inventory item

        Raises:
            ValueError: If insufficient available stock
        """
        item = self._inventory.get(item_id)
        if not item:
            raise ValueError(f"Inventory item not found: {item_id}")

        if item.available_kg < quantity_kg:
            raise ValueError(f"Insufficient available stock. Available: {item.available_kg} kg")

        item.reserved_kg += quantity_kg
        item.updated_at = datetime.now(UTC)
        self._update_item_status(item)

        return item

    def release_reservation(
        self,
        item_id: str,
        quantity_kg: float,
    ) -> InventoryItem:
        """
        Release reserved stock.

        Args:
            item_id: Inventory item ID
            quantity_kg: Quantity to release

        Returns:
            Updated inventory item
        """
        item = self._inventory.get(item_id)
        if not item:
            raise ValueError(f"Inventory item not found: {item_id}")

        item.reserved_kg = max(0, item.reserved_kg - quantity_kg)
        item.updated_at = datetime.now(UTC)
        self._update_item_status(item)

        return item

    def _update_item_status(self, item: InventoryItem) -> None:
        """Update inventory item status based on current state."""
        now = datetime.now(UTC)

        # Check expiry
        if item.expiry_date and item.expiry_date < now:
            item.status = InventoryStatus.EXPIRED
            return

        # Check stock level
        if item.quantity_kg <= 0:
            item.status = InventoryStatus.OUT_OF_STOCK
        elif item.is_low_stock:
            item.status = InventoryStatus.LOW_STOCK
        else:
            item.status = InventoryStatus.IN_STOCK

    def check_alerts(self, tenant_id: str) -> list[InventoryAlert]:
        """
        Check inventory and generate alerts.

        Args:
            tenant_id: Tenant ID to check

        Returns:
            List of new alerts
        """
        alerts = []
        now = datetime.now(UTC)

        for item in self.get_all_items(tenant_id):
            # Check for low stock
            if item.is_low_stock and item.quantity_kg > 0:
                alerts.append(
                    InventoryAlert(
                        id=str(uuid.uuid4()),
                        tenant_id=tenant_id,
                        inventory_item_id=item.id,
                        fertilizer_name=item.fertilizer_name,
                        fertilizer_name_ar=item.fertilizer_name_ar,
                        alert_type="low_stock",
                        alert_type_ar=self.ALERT_TYPES["low_stock"],
                        severity="warning",
                        current_quantity_kg=item.quantity_kg,
                        threshold_kg=item.minimum_stock_kg,
                        title_en=f"Low Stock Alert: {item.fertilizer_name}",
                        title_ar=f"تنبيه مخزون منخفض: {item.fertilizer_name_ar}",
                        message_en=f"Current stock ({item.quantity_kg:.1f} kg) is below minimum threshold ({item.minimum_stock_kg:.1f} kg)",
                        message_ar=f"المخزون الحالي ({item.quantity_kg:.1f} كجم) أقل من الحد الأدنى ({item.minimum_stock_kg:.1f} كجم)",
                        recommended_action_en="Place order to replenish stock",
                        recommended_action_ar="قم بطلب لتجديد المخزون",
                        recommended_order_quantity_kg=item.reorder_point_kg - item.quantity_kg,
                    )
                )

            # Check for out of stock
            if item.quantity_kg <= 0:
                alerts.append(
                    InventoryAlert(
                        id=str(uuid.uuid4()),
                        tenant_id=tenant_id,
                        inventory_item_id=item.id,
                        fertilizer_name=item.fertilizer_name,
                        fertilizer_name_ar=item.fertilizer_name_ar,
                        alert_type="out_of_stock",
                        alert_type_ar=self.ALERT_TYPES["out_of_stock"],
                        severity="critical",
                        current_quantity_kg=0,
                        threshold_kg=item.minimum_stock_kg,
                        title_en=f"Out of Stock: {item.fertilizer_name}",
                        title_ar=f"نفد المخزون: {item.fertilizer_name_ar}",
                        message_en=f"{item.fertilizer_name} is out of stock",
                        message_ar=f"{item.fertilizer_name_ar} نفد من المخزون",
                        recommended_action_en="Urgent order required",
                        recommended_action_ar="مطلوب طلب عاجل",
                        recommended_order_quantity_kg=item.reorder_point_kg,
                    )
                )

            # Check for expiring soon
            if item.expiry_date:
                days_until_expiry = (item.expiry_date - now).days
                if 0 < days_until_expiry <= self.expiry_warning_days:
                    alerts.append(
                        InventoryAlert(
                            id=str(uuid.uuid4()),
                            tenant_id=tenant_id,
                            inventory_item_id=item.id,
                            fertilizer_name=item.fertilizer_name,
                            fertilizer_name_ar=item.fertilizer_name_ar,
                            alert_type="expiring_soon",
                            alert_type_ar=self.ALERT_TYPES["expiring_soon"],
                            severity="warning",
                            current_quantity_kg=item.quantity_kg,
                            threshold_kg=0,
                            expiry_date=item.expiry_date,
                            days_until_expiry=days_until_expiry,
                            title_en=f"Expiring Soon: {item.fertilizer_name}",
                            title_ar=f"قارب انتهاء الصلاحية: {item.fertilizer_name_ar}",
                            message_en=f"{item.fertilizer_name} expires in {days_until_expiry} days ({item.quantity_kg:.1f} kg remaining)",
                            message_ar=f"{item.fertilizer_name_ar} ينتهي خلال {days_until_expiry} يوم ({item.quantity_kg:.1f} كجم متبقي)",
                            recommended_action_en="Plan to use before expiry or consider disposal",
                            recommended_action_ar="خطط للاستخدام قبل انتهاء الصلاحية أو النظر في التخلص",
                        )
                    )

                # Check for expired
                if days_until_expiry <= 0:
                    alerts.append(
                        InventoryAlert(
                            id=str(uuid.uuid4()),
                            tenant_id=tenant_id,
                            inventory_item_id=item.id,
                            fertilizer_name=item.fertilizer_name,
                            fertilizer_name_ar=item.fertilizer_name_ar,
                            alert_type="expired",
                            alert_type_ar=self.ALERT_TYPES["expired"],
                            severity="critical",
                            current_quantity_kg=item.quantity_kg,
                            threshold_kg=0,
                            expiry_date=item.expiry_date,
                            days_until_expiry=0,
                            title_en=f"Expired: {item.fertilizer_name}",
                            title_ar=f"منتهي الصلاحية: {item.fertilizer_name_ar}",
                            message_en=f"{item.fertilizer_name} has expired. {item.quantity_kg:.1f} kg needs disposal",
                            message_ar=f"{item.fertilizer_name_ar} انتهت صلاحيته. {item.quantity_kg:.1f} كجم يحتاج للتخلص",
                            recommended_action_en="Remove from inventory and dispose properly",
                            recommended_action_ar="أزل من المخزون وتخلص منه بشكل صحيح",
                        )
                    )

        self._alerts.extend(alerts)
        return alerts

    def get_inventory_summary(self, tenant_id: str) -> InventorySummary:
        """
        Generate inventory summary report.

        Args:
            tenant_id: Tenant ID

        Returns:
            Inventory summary
        """
        items = self.get_all_items(tenant_id)
        now = datetime.now(UTC)

        summary = InventorySummary(tenant_id=tenant_id)
        summary.total_items = len(items)

        by_type: dict[str, dict] = {}

        for item in items:
            summary.total_quantity_kg += item.quantity_kg
            summary.total_value += item.total_value

            # Count by status
            if item.status == InventoryStatus.IN_STOCK:
                summary.in_stock_count += 1
            elif item.status == InventoryStatus.LOW_STOCK:
                summary.low_stock_count += 1
            elif item.status == InventoryStatus.OUT_OF_STOCK:
                summary.out_of_stock_count += 1
            elif item.status == InventoryStatus.EXPIRED:
                summary.expired_count += 1

            # Check expiring soon
            if item.expiry_date:
                days_until_expiry = (item.expiry_date - now).days
                if 0 < days_until_expiry <= self.expiry_warning_days:
                    summary.expiring_soon_count += 1

            # Track items needing reorder
            if item.is_low_stock or item.status == InventoryStatus.OUT_OF_STOCK:
                summary.items_needing_reorder.append(
                    {
                        "id": item.id,
                        "name": item.fertilizer_name,
                        "name_ar": item.fertilizer_name_ar,
                        "current_kg": item.quantity_kg,
                        "reorder_point_kg": item.reorder_point_kg,
                        "suggested_order_kg": max(0, item.reorder_point_kg - item.quantity_kg),
                    }
                )

        # Sort items needing reorder by urgency
        summary.items_needing_reorder.sort(key=lambda x: x["current_kg"] - x["reorder_point_kg"])

        # Get top items by value
        items_by_value = sorted(items, key=lambda x: x.total_value, reverse=True)[:5]
        summary.top_items_by_value = [
            {
                "name": item.fertilizer_name,
                "name_ar": item.fertilizer_name_ar,
                "quantity_kg": item.quantity_kg,
                "value": float(item.total_value),
            }
            for item in items_by_value
        ]

        summary.by_fertilizer_type = by_type

        # Get active alerts
        alerts = self.check_alerts(tenant_id)
        summary.active_alerts_count = len(alerts)
        summary.critical_alerts = [a for a in alerts if a.severity == "critical"]

        return summary

    def get_transactions(
        self,
        tenant_id: str,
        item_id: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        transaction_type: str | None = None,
    ) -> list[InventoryTransaction]:
        """
        Get inventory transactions with filters.

        Args:
            tenant_id: Tenant ID
            item_id: Filter by inventory item
            start_date: Filter by start date
            end_date: Filter by end date
            transaction_type: Filter by transaction type

        Returns:
            List of transactions
        """
        transactions = [t for t in self._transactions if t.tenant_id == tenant_id]

        if item_id:
            transactions = [t for t in transactions if t.inventory_item_id == item_id]

        if start_date:
            transactions = [t for t in transactions if t.created_at >= start_date]

        if end_date:
            transactions = [t for t in transactions if t.created_at <= end_date]

        if transaction_type:
            transactions = [t for t in transactions if t.transaction_type == transaction_type]

        return sorted(transactions, key=lambda t: t.created_at, reverse=True)

    def calculate_consumption_rate(
        self,
        item_id: str,
        days: int = 30,
    ) -> dict:
        """
        Calculate consumption rate for an inventory item.

        Args:
            item_id: Inventory item ID
            days: Number of days to analyze

        Returns:
            Dictionary with consumption statistics
        """
        item = self._inventory.get(item_id)
        if not item:
            return {"error": "Item not found"}

        start_date = datetime.now(UTC) - timedelta(days=days)
        transactions = self.get_transactions(
            tenant_id=item.tenant_id,
            item_id=item_id,
            start_date=start_date,
            transaction_type="issue",
        )

        total_issued = sum(abs(t.quantity_kg) for t in transactions)
        daily_rate = total_issued / days if days > 0 else 0

        days_of_stock = item.available_kg / daily_rate if daily_rate > 0 else float("inf")

        return {
            "item_id": item_id,
            "fertilizer_name": item.fertilizer_name,
            "fertilizer_name_ar": item.fertilizer_name_ar,
            "period_days": days,
            "total_consumed_kg": total_issued,
            "daily_consumption_kg": round(daily_rate, 2),
            "current_stock_kg": item.available_kg,
            "days_of_stock_remaining": round(days_of_stock, 1) if days_of_stock != float("inf") else None,
            "projected_stockout_date": (datetime.now(UTC) + timedelta(days=days_of_stock)).isoformat()
            if days_of_stock != float("inf") and days_of_stock > 0
            else None,
        }


def create_inventory_item(
    tenant_id: str,
    fertilizer: Fertilizer,
    initial_quantity_kg: float = 0.0,
    warehouse_id: str = "",
    warehouse_name: str = "",
    minimum_stock_kg: float = 100.0,
    reorder_point_kg: float = 200.0,
) -> InventoryItem:
    """
    Create a new inventory item for a fertilizer product.

    Args:
        tenant_id: Tenant ID
        fertilizer: Fertilizer product
        initial_quantity_kg: Initial quantity
        warehouse_id: Warehouse ID
        warehouse_name: Warehouse name
        minimum_stock_kg: Minimum stock alert threshold
        reorder_point_kg: Reorder point threshold

    Returns:
        New inventory item
    """
    return InventoryItem(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        fertilizer_id=fertilizer.id,
        fertilizer_name=fertilizer.name,
        fertilizer_name_ar=fertilizer.name_ar,
        quantity_kg=initial_quantity_kg,
        warehouse_id=warehouse_id,
        warehouse_name=warehouse_name,
        minimum_stock_kg=minimum_stock_kg,
        reorder_point_kg=reorder_point_kg,
        status=InventoryStatus.IN_STOCK if initial_quantity_kg > 0 else InventoryStatus.OUT_OF_STOCK,
    )
