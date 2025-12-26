"""
SAHOOL Inventory Alert Manager - مدير تنبيهات المخزون
Manages low stock alerts, expiring items, and reorder notifications
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime, date, timedelta
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)


class AlertType(Enum):
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    EXPIRING_SOON = "expiring_soon"
    EXPIRED = "expired"
    REORDER_POINT = "reorder_point"
    OVERSTOCK = "overstock"
    STORAGE_CONDITION = "storage_condition"


class AlertPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SNOOZED = "snoozed"


@dataclass
class InventoryAlert:
    """Inventory alert data structure"""
    id: str
    alert_type: AlertType
    priority: AlertPriority
    status: AlertStatus

    # Item info
    item_id: str
    item_name: str
    item_name_ar: str

    # Alert details
    title_en: str
    title_ar: str
    message_en: str
    message_ar: str

    # Thresholds
    current_value: float
    threshold_value: float

    # Actions
    recommended_action_en: str
    recommended_action_ar: str
    action_url: Optional[str] = None

    # Timing
    created_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    snooze_until: Optional[datetime] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "alert_type": self.alert_type.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "item_id": self.item_id,
            "item_name": self.item_name,
            "item_name_ar": self.item_name_ar,
            "title_en": self.title_en,
            "title_ar": self.title_ar,
            "message_en": self.message_en,
            "message_ar": self.message_ar,
            "current_value": self.current_value,
            "threshold_value": self.threshold_value,
            "recommended_action_en": self.recommended_action_en,
            "recommended_action_ar": self.recommended_action_ar,
            "action_url": self.action_url,
            "created_at": self.created_at.isoformat(),
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "acknowledged_by": self.acknowledged_by,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "resolved_by": self.resolved_by,
            "resolution_notes": self.resolution_notes,
            "snooze_until": self.snooze_until.isoformat() if self.snooze_until else None,
        }


class AlertManager:
    """Manage inventory alerts and notifications"""

    def __init__(self, inventory_db: Dict = None, alerts_db: Dict = None):
        """
        Initialize alert manager

        Args:
            inventory_db: Reference to inventory database (in-memory dict for now)
            alerts_db: Reference to alerts database (in-memory dict for now)
        """
        self.inventory_db = inventory_db or {}
        self.alerts_db = alerts_db or {}

    async def check_all_alerts(self) -> List[InventoryAlert]:
        """
        Run all alert checks and create/update alerts.
        Called by scheduler every hour.
        """
        logger.info("Running all alert checks...")
        alerts = []

        try:
            alerts.extend(await self.check_low_stock())
            alerts.extend(await self.check_out_of_stock())
            alerts.extend(await self.check_expiring_items())
            alerts.extend(await self.check_reorder_points())

            logger.info(f"Alert check completed. Found {len(alerts)} alerts.")
        except Exception as e:
            logger.error(f"Error during alert check: {e}")

        return alerts

    async def check_low_stock(self) -> List[InventoryAlert]:
        """
        Check items below reorder level.
        Priority based on how far below:
        - 50-100% of reorder: MEDIUM
        - 25-50% of reorder: HIGH
        - <25% of reorder: CRITICAL
        """
        alerts = []

        for item_id, item in self.inventory_db.items():
            quantity = item.get("quantity", 0)
            reorder_level = item.get("reorder_level", 0)

            if reorder_level <= 0:
                continue

            if 0 < quantity <= reorder_level:
                # Calculate percentage of reorder level
                percentage = (quantity / reorder_level) * 100

                # Determine priority
                if percentage >= 50:
                    priority = AlertPriority.MEDIUM
                    priority_ar = "متوسط"
                elif percentage >= 25:
                    priority = AlertPriority.HIGH
                    priority_ar = "عالي"
                else:
                    priority = AlertPriority.CRITICAL
                    priority_ar = "حرج"

                # Check if alert already exists
                existing_alert = self._find_existing_alert(
                    item_id,
                    AlertType.LOW_STOCK
                )

                if existing_alert and existing_alert.status == AlertStatus.ACTIVE:
                    # Update priority if changed
                    if existing_alert.priority != priority:
                        existing_alert.priority = priority
                        alerts.append(existing_alert)
                    continue

                # Create new alert
                alert = InventoryAlert(
                    id=f"alert_{uuid.uuid4().hex[:12]}",
                    alert_type=AlertType.LOW_STOCK,
                    priority=priority,
                    status=AlertStatus.ACTIVE,
                    item_id=item_id,
                    item_name=item.get("name", "Unknown"),
                    item_name_ar=item.get("name_ar", "غير معروف"),
                    title_en=f"Low Stock Alert: {item.get('name', 'Unknown')}",
                    title_ar=f"تنبيه مخزون منخفض: {item.get('name_ar', 'غير معروف')}",
                    message_en=f"Current stock ({quantity} {item.get('unit', 'units')}) is below reorder level ({reorder_level} {item.get('unit', 'units')}). Priority: {priority.value.upper()}",
                    message_ar=f"المخزون الحالي ({quantity} {item.get('unit', 'وحدة')}) أقل من مستوى إعادة الطلب ({reorder_level} {item.get('unit', 'وحدة')}). الأولوية: {priority_ar}",
                    current_value=quantity,
                    threshold_value=reorder_level,
                    recommended_action_en=f"Order at least {int(reorder_level - quantity)} {item.get('unit', 'units')} to reach minimum stock level",
                    recommended_action_ar=f"اطلب على الأقل {int(reorder_level - quantity)} {item.get('unit', 'وحدة')} للوصول إلى الحد الأدنى للمخزون",
                    action_url=f"/inventory/{item_id}/reorder"
                )

                self.alerts_db[alert.id] = alert
                alerts.append(alert)

        logger.info(f"Low stock check: Found {len(alerts)} alerts")
        return alerts

    async def check_out_of_stock(self) -> List[InventoryAlert]:
        """Check items with zero available quantity"""
        alerts = []

        for item_id, item in self.inventory_db.items():
            quantity = item.get("quantity", 0)

            if quantity <= 0:
                # Check if alert already exists
                existing_alert = self._find_existing_alert(
                    item_id,
                    AlertType.OUT_OF_STOCK
                )

                if existing_alert and existing_alert.status == AlertStatus.ACTIVE:
                    continue

                # Create new alert
                alert = InventoryAlert(
                    id=f"alert_{uuid.uuid4().hex[:12]}",
                    alert_type=AlertType.OUT_OF_STOCK,
                    priority=AlertPriority.CRITICAL,
                    status=AlertStatus.ACTIVE,
                    item_id=item_id,
                    item_name=item.get("name", "Unknown"),
                    item_name_ar=item.get("name_ar", "غير معروف"),
                    title_en=f"Out of Stock: {item.get('name', 'Unknown')}",
                    title_ar=f"نفاد المخزون: {item.get('name_ar', 'غير معروف')}",
                    message_en=f"{item.get('name', 'Unknown')} is completely out of stock. Immediate restocking required.",
                    message_ar=f"{item.get('name_ar', 'غير معروف')} نفد من المخزون بالكامل. يتطلب إعادة التخزين فورا.",
                    current_value=0,
                    threshold_value=item.get("reorder_level", 0),
                    recommended_action_en="Place urgent order to restock this item",
                    recommended_action_ar="قم بطلب عاجل لإعادة تخزين هذا الصنف",
                    action_url=f"/inventory/{item_id}/reorder"
                )

                self.alerts_db[alert.id] = alert
                alerts.append(alert)

        logger.info(f"Out of stock check: Found {len(alerts)} alerts")
        return alerts

    async def check_expiring_items(
        self,
        warning_days: int = 30,
        critical_days: int = 7
    ) -> List[InventoryAlert]:
        """
        Check items expiring soon.
        - 7-30 days: MEDIUM (warning)
        - <7 days: HIGH (critical)
        - Expired: CRITICAL
        """
        alerts = []
        now = datetime.utcnow()
        today = now.date()

        for item_id, item in self.inventory_db.items():
            expiry_date_str = item.get("expiry_date")
            if not expiry_date_str:
                continue

            # Parse expiry date
            if isinstance(expiry_date_str, str):
                expiry_date = datetime.fromisoformat(expiry_date_str.replace('Z', '+00:00')).date()
            elif isinstance(expiry_date_str, datetime):
                expiry_date = expiry_date_str.date()
            elif isinstance(expiry_date_str, date):
                expiry_date = expiry_date_str
            else:
                continue

            days_until_expiry = (expiry_date - today).days

            # Determine alert type and priority
            if days_until_expiry < 0:
                # Expired
                alert_type = AlertType.EXPIRED
                priority = AlertPriority.CRITICAL
                title_en = f"Expired: {item.get('name', 'Unknown')}"
                title_ar = f"منتهي الصلاحية: {item.get('name_ar', 'غير معروف')}"
                message_en = f"This item expired {abs(days_until_expiry)} day(s) ago. Remove from inventory immediately."
                message_ar = f"انتهت صلاحية هذا الصنف منذ {abs(days_until_expiry)} يوم. قم بإزالته من المخزون فوراً."
                action_en = "Remove expired item from inventory and dispose safely"
                action_ar = "قم بإزالة الصنف المنتهي الصلاحية من المخزون والتخلص منه بشكل آمن"
            elif days_until_expiry <= critical_days:
                # Critical warning
                alert_type = AlertType.EXPIRING_SOON
                priority = AlertPriority.HIGH
                title_en = f"Expiring Soon: {item.get('name', 'Unknown')}"
                title_ar = f"ينتهي قريبا: {item.get('name_ar', 'غير معروف')}"
                message_en = f"This item expires in {days_until_expiry} day(s). Use or discount immediately."
                message_ar = f"ينتهي هذا الصنف خلال {days_until_expiry} يوم. استخدمه أو قدم خصم فوراً."
                action_en = f"Use item within {days_until_expiry} days or offer discount"
                action_ar = f"استخدم الصنف خلال {days_until_expiry} يوم أو قدم خصم"
            elif days_until_expiry <= warning_days:
                # Warning
                alert_type = AlertType.EXPIRING_SOON
                priority = AlertPriority.MEDIUM
                title_en = f"Expiring in {days_until_expiry} Days: {item.get('name', 'Unknown')}"
                title_ar = f"ينتهي خلال {days_until_expiry} يوم: {item.get('name_ar', 'غير معروف')}"
                message_en = f"This item expires in {days_until_expiry} day(s). Plan usage accordingly."
                message_ar = f"ينتهي هذا الصنف خلال {days_until_expiry} يوم. خطط للاستخدام وفقاً لذلك."
                action_en = f"Plan to use item within {days_until_expiry} days"
                action_ar = f"خطط لاستخدام الصنف خلال {days_until_expiry} يوم"
            else:
                # No alert needed
                continue

            # Check if alert already exists
            existing_alert = self._find_existing_alert(
                item_id,
                alert_type
            )

            if existing_alert and existing_alert.status == AlertStatus.ACTIVE:
                # Update priority if changed
                if existing_alert.priority != priority:
                    existing_alert.priority = priority
                    existing_alert.message_en = message_en
                    existing_alert.message_ar = message_ar
                    alerts.append(existing_alert)
                continue

            # Create new alert
            alert = InventoryAlert(
                id=f"alert_{uuid.uuid4().hex[:12]}",
                alert_type=alert_type,
                priority=priority,
                status=AlertStatus.ACTIVE,
                item_id=item_id,
                item_name=item.get("name", "Unknown"),
                item_name_ar=item.get("name_ar", "غير معروف"),
                title_en=title_en,
                title_ar=title_ar,
                message_en=message_en,
                message_ar=message_ar,
                current_value=float(days_until_expiry),
                threshold_value=float(critical_days),
                recommended_action_en=action_en,
                recommended_action_ar=action_ar,
                action_url=f"/inventory/{item_id}"
            )

            self.alerts_db[alert.id] = alert
            alerts.append(alert)

        logger.info(f"Expiring items check: Found {len(alerts)} alerts")
        return alerts

    async def check_reorder_points(self) -> List[InventoryAlert]:
        """Check items that need reordering based on forecast"""
        alerts = []

        for item_id, item in self.inventory_db.items():
            quantity = item.get("quantity", 0)
            reorder_point = item.get("reorder_point", item.get("reorder_level", 0))
            max_stock = item.get("max_stock", reorder_point * 2)

            if reorder_point <= 0:
                continue

            # Check if at or below reorder point
            if quantity <= reorder_point:
                # Calculate optimal order quantity
                order_quantity = max_stock - quantity

                # Check if alert already exists
                existing_alert = self._find_existing_alert(
                    item_id,
                    AlertType.REORDER_POINT
                )

                if existing_alert and existing_alert.status == AlertStatus.ACTIVE:
                    continue

                # Create new alert
                alert = InventoryAlert(
                    id=f"alert_{uuid.uuid4().hex[:12]}",
                    alert_type=AlertType.REORDER_POINT,
                    priority=AlertPriority.MEDIUM,
                    status=AlertStatus.ACTIVE,
                    item_id=item_id,
                    item_name=item.get("name", "Unknown"),
                    item_name_ar=item.get("name_ar", "غير معروف"),
                    title_en=f"Reorder Point Reached: {item.get('name', 'Unknown')}",
                    title_ar=f"تم الوصول لنقطة إعادة الطلب: {item.get('name_ar', 'غير معروف')}",
                    message_en=f"Stock level ({quantity} {item.get('unit', 'units')}) has reached reorder point ({reorder_point} {item.get('unit', 'units')})",
                    message_ar=f"مستوى المخزون ({quantity} {item.get('unit', 'وحدة')}) وصل لنقطة إعادة الطلب ({reorder_point} {item.get('unit', 'وحدة')})",
                    current_value=quantity,
                    threshold_value=reorder_point,
                    recommended_action_en=f"Order {int(order_quantity)} {item.get('unit', 'units')} to reach optimal stock level",
                    recommended_action_ar=f"اطلب {int(order_quantity)} {item.get('unit', 'وحدة')} للوصول للمستوى الأمثل للمخزون",
                    action_url=f"/inventory/{item_id}/reorder"
                )

                self.alerts_db[alert.id] = alert
                alerts.append(alert)

        logger.info(f"Reorder point check: Found {len(alerts)} alerts")
        return alerts

    async def check_storage_conditions(self) -> List[InventoryAlert]:
        """Check if storage conditions are out of range"""
        alerts = []

        for item_id, item in self.inventory_db.items():
            storage = item.get("storage_conditions", {})
            current_temp = storage.get("current_temperature")
            current_humidity = storage.get("current_humidity")

            if current_temp is None and current_humidity is None:
                continue

            # Temperature check
            if current_temp is not None:
                min_temp = storage.get("min_temperature")
                max_temp = storage.get("max_temperature")

                if min_temp is not None and current_temp < min_temp:
                    alert = self._create_storage_alert(
                        item_id, item,
                        "Temperature Too Low",
                        "درجة الحرارة منخفضة جدا",
                        f"Current temperature ({current_temp}°C) is below minimum ({min_temp}°C)",
                        f"درجة الحرارة الحالية ({current_temp}°م) أقل من الحد الأدنى ({min_temp}°م)",
                        current_temp, min_temp
                    )
                    self.alerts_db[alert.id] = alert
                    alerts.append(alert)

                elif max_temp is not None and current_temp > max_temp:
                    alert = self._create_storage_alert(
                        item_id, item,
                        "Temperature Too High",
                        "درجة الحرارة مرتفعة جدا",
                        f"Current temperature ({current_temp}°C) exceeds maximum ({max_temp}°C)",
                        f"درجة الحرارة الحالية ({current_temp}°م) تتجاوز الحد الأقصى ({max_temp}°م)",
                        current_temp, max_temp
                    )
                    self.alerts_db[alert.id] = alert
                    alerts.append(alert)

            # Humidity check
            if current_humidity is not None:
                min_humidity = storage.get("min_humidity")
                max_humidity = storage.get("max_humidity")

                if min_humidity is not None and current_humidity < min_humidity:
                    alert = self._create_storage_alert(
                        item_id, item,
                        "Humidity Too Low",
                        "الرطوبة منخفضة جدا",
                        f"Current humidity ({current_humidity}%) is below minimum ({min_humidity}%)",
                        f"الرطوبة الحالية ({current_humidity}%) أقل من الحد الأدنى ({min_humidity}%)",
                        current_humidity, min_humidity
                    )
                    self.alerts_db[alert.id] = alert
                    alerts.append(alert)

                elif max_humidity is not None and current_humidity > max_humidity:
                    alert = self._create_storage_alert(
                        item_id, item,
                        "Humidity Too High",
                        "الرطوبة مرتفعة جدا",
                        f"Current humidity ({current_humidity}%) exceeds maximum ({max_humidity}%)",
                        f"الرطوبة الحالية ({current_humidity}%) تتجاوز الحد الأقصى ({max_humidity}%)",
                        current_humidity, max_humidity
                    )
                    self.alerts_db[alert.id] = alert
                    alerts.append(alert)

        logger.info(f"Storage conditions check: Found {len(alerts)} alerts")
        return alerts

    def _create_storage_alert(
        self,
        item_id: str,
        item: Dict,
        title_en: str,
        title_ar: str,
        message_en: str,
        message_ar: str,
        current_value: float,
        threshold_value: float
    ) -> InventoryAlert:
        """Helper to create storage condition alert"""
        return InventoryAlert(
            id=f"alert_{uuid.uuid4().hex[:12]}",
            alert_type=AlertType.STORAGE_CONDITION,
            priority=AlertPriority.HIGH,
            status=AlertStatus.ACTIVE,
            item_id=item_id,
            item_name=item.get("name", "Unknown"),
            item_name_ar=item.get("name_ar", "غير معروف"),
            title_en=f"{title_en}: {item.get('name', 'Unknown')}",
            title_ar=f"{title_ar}: {item.get('name_ar', 'غير معروف')}",
            message_en=message_en,
            message_ar=message_ar,
            current_value=current_value,
            threshold_value=threshold_value,
            recommended_action_en="Adjust storage conditions immediately to prevent spoilage",
            recommended_action_ar="اضبط ظروف التخزين فورا لمنع التلف",
            action_url=f"/inventory/{item_id}/storage"
        )

    async def get_active_alerts(
        self,
        priority: Optional[AlertPriority] = None,
        alert_type: Optional[AlertType] = None
    ) -> List[InventoryAlert]:
        """Get all active alerts"""
        now = datetime.utcnow()
        alerts = []

        for alert in self.alerts_db.values():
            # Skip non-active alerts
            if alert.status != AlertStatus.ACTIVE:
                continue

            # Skip snoozed alerts that are still snoozed
            if alert.snooze_until and alert.snooze_until > now:
                continue

            # Filter by priority if specified
            if priority and alert.priority != priority:
                continue

            # Filter by type if specified
            if alert_type and alert.alert_type != alert_type:
                continue

            alerts.append(alert)

        # Sort by priority (critical first), then by created_at
        priority_order = {
            AlertPriority.CRITICAL: 0,
            AlertPriority.HIGH: 1,
            AlertPriority.MEDIUM: 2,
            AlertPriority.LOW: 3
        }
        alerts.sort(key=lambda a: (priority_order.get(a.priority, 99), a.created_at))

        return alerts

    async def acknowledge_alert(
        self,
        alert_id: str,
        acknowledged_by: str
    ) -> Optional[InventoryAlert]:
        """Acknowledge an alert"""
        alert = self.alerts_db.get(alert_id)
        if not alert:
            return None

        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = acknowledged_by

        logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
        return alert

    async def resolve_alert(
        self,
        alert_id: str,
        resolved_by: str,
        resolution_notes: Optional[str] = None
    ) -> Optional[InventoryAlert]:
        """Mark alert as resolved"""
        alert = self.alerts_db.get(alert_id)
        if not alert:
            return None

        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = resolved_by
        alert.resolution_notes = resolution_notes

        logger.info(f"Alert {alert_id} resolved by {resolved_by}")
        return alert

    async def snooze_alert(
        self,
        alert_id: str,
        snooze_hours: int = 24
    ) -> Optional[InventoryAlert]:
        """Snooze alert for N hours"""
        alert = self.alerts_db.get(alert_id)
        if not alert:
            return None

        alert.status = AlertStatus.SNOOZED
        alert.snooze_until = datetime.utcnow() + timedelta(hours=snooze_hours)

        logger.info(f"Alert {alert_id} snoozed for {snooze_hours} hours")
        return alert

    async def get_alert_summary(self) -> Dict:
        """
        Get summary counts:
        - Total active
        - By priority
        - By type
        """
        active_alerts = await self.get_active_alerts()

        # Count by priority
        by_priority = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }

        # Count by type
        by_type = {
            "low_stock": 0,
            "out_of_stock": 0,
            "expiring_soon": 0,
            "expired": 0,
            "reorder_point": 0,
            "overstock": 0,
            "storage_condition": 0
        }

        for alert in active_alerts:
            by_priority[alert.priority.value] += 1
            by_type[alert.alert_type.value] += 1

        return {
            "total_active": len(active_alerts),
            "by_priority": by_priority,
            "by_type": by_type,
            "recent_alerts": [alert.to_dict() for alert in active_alerts[:5]]
        }

    async def send_notifications(
        self,
        alerts: List[InventoryAlert],
        nats_client = None
    ) -> Dict:
        """
        Send notifications via NATS to notification service.
        Groups by user/farm for batch sending.
        """
        if not nats_client:
            logger.warning("NATS client not available. Skipping notifications.")
            return {"sent": 0, "failed": 0}

        sent = 0
        failed = 0

        for alert in alerts:
            try:
                notification_data = {
                    "event_type": "inventory_alert",
                    "event_id": alert.id,
                    "source_service": "inventory-service",
                    "timestamp": datetime.utcnow().isoformat(),
                    "alert": alert.to_dict(),
                    "recipients": ["farm_manager", "owner"],
                    "notification_priority": alert.priority.value,
                    "notification_channels": ["in_app", "push"],
                    "action_template": {
                        "title_en": alert.title_en,
                        "title_ar": alert.title_ar,
                        "description_en": alert.message_en,
                        "description_ar": alert.message_ar,
                        "urgency": alert.priority.value,
                        "action_url": alert.action_url
                    }
                }

                # Publish to NATS
                await nats_client.publish(
                    "sahool.alerts.inventory",
                    notification_data
                )

                sent += 1
                logger.info(f"Notification sent for alert {alert.id}")

            except Exception as e:
                failed += 1
                logger.error(f"Failed to send notification for alert {alert.id}: {e}")

        return {"sent": sent, "failed": failed}

    def _find_existing_alert(
        self,
        item_id: str,
        alert_type: AlertType
    ) -> Optional[InventoryAlert]:
        """Find existing active alert for item and type"""
        for alert in self.alerts_db.values():
            if (alert.item_id == item_id and
                alert.alert_type == alert_type and
                alert.status == AlertStatus.ACTIVE):
                return alert
        return None
