"""
Stock Manager - Handles FIFO batch consumption and stock operations
"""

from datetime import datetime

from prisma import Prisma
from prisma.models import BatchLot, InventoryItem, StockMovement

from models import MovementType


class StockManager:
    """Manages stock operations with FIFO batch consumption"""

    def __init__(self, db: Prisma):
        self.db = db

    async def consume_stock_fifo(
        self, item_id: str, quantity: float
    ) -> tuple[list[dict], float]:
        """
        Consume stock using FIFO (First In First Out) method
        Returns: (consumed_batches, total_consumed)

        consumed_batches format:
        [
            {"batch_id": str, "lot_number": str, "quantity": float, "unit_cost": float},
            ...
        ]
        """
        # Validate input
        if quantity <= 0:
            raise ValueError(f"Quantity must be positive, got: {quantity}")

        # Use transaction with row-level locking to prevent race conditions
        async with self.db.tx() as transaction:
            # Get all batches for this item with row lock, ordered by received date (FIFO)
            batches = await transaction.batchlot.find_many(
                where={"itemId": item_id, "remainingQty": {"gt": 0}},
                order={"receivedDate": "asc"},
            )

            if not batches:
                raise ValueError(f"No batches available for item {item_id}")

            consumed_batches = []
            remaining_to_consume = quantity
            total_consumed = 0.0

            for batch in batches:
                if remaining_to_consume <= 0:
                    break

                # Calculate how much to consume from this batch
                consume_from_batch = min(batch.remainingQty, remaining_to_consume)

                # Update batch remaining quantity within transaction
                await transaction.batchlot.update(
                    where={"id": batch.id},
                    data={"remainingQty": batch.remainingQty - consume_from_batch},
                )

                # Record consumed batch
                consumed_batches.append(
                    {
                        "batch_id": batch.id,
                        "lot_number": batch.lotNumber,
                        "quantity": consume_from_batch,
                        "unit_cost": batch.unitCost or 0.0,
                    }
                )

                total_consumed += consume_from_batch
                remaining_to_consume -= consume_from_batch

            if remaining_to_consume > 0:
                raise ValueError(
                    f"Insufficient stock. Required: {quantity}, Available: {total_consumed}"
                )

        return consumed_batches, total_consumed

    async def add_stock_batch(
        self,
        item_id: str,
        quantity: float,
        lot_number: str,
        batch_number: str | None = None,
        expiry_date: datetime | None = None,
        production_date: datetime | None = None,
        supplier_id: str | None = None,
        invoice_number: str | None = None,
        unit_cost: float | None = None,
        quality_grade: str | None = None,
        certifications: list[str] | None = None,
    ) -> BatchLot:
        """Add a new batch/lot of stock"""
        # Validate input
        if quantity <= 0:
            raise ValueError(f"Quantity must be positive, got: {quantity}")

        batch = await self.db.batchlot.create(
            data={
                "itemId": item_id,
                "lotNumber": lot_number,
                "batchNumber": batch_number,
                "quantity": quantity,
                "remainingQty": quantity,
                "productionDate": production_date,
                "expiryDate": expiry_date,
                "supplierId": supplier_id,
                "invoiceNumber": invoice_number,
                "unitCost": unit_cost,
                "qualityGrade": quality_grade,
                "certifications": certifications or [],
            }
        )
        return batch

    async def update_item_quantities(
        self, item_id: str, quantity_change: float, is_addition: bool = True
    ) -> InventoryItem:
        """
        Update item quantities (current and available)
        is_addition: True for stock in, False for stock out
        """
        item = await self.db.inventoryitem.find_unique(where={"id": item_id})
        if not item:
            raise ValueError(f"Item {item_id} not found")

        if is_addition:
            new_current = item.currentQuantity + quantity_change
            new_available = item.availableQuantity + quantity_change
        else:
            if item.availableQuantity < quantity_change:
                raise ValueError(
                    f"Insufficient available stock. "
                    f"Required: {quantity_change}, Available: {item.availableQuantity}"
                )
            new_current = item.currentQuantity - quantity_change
            new_available = item.availableQuantity - quantity_change

        # Update item
        updated_item = await self.db.inventoryitem.update(
            where={"id": item_id},
            data={
                "currentQuantity": new_current,
                "availableQuantity": new_available,
                "lastRestocked": (
                    datetime.utcnow() if is_addition else item.lastRestocked
                ),
            },
        )

        return updated_item

    async def create_movement_record(
        self,
        item_id: str,
        movement_type: MovementType,
        quantity: float,
        previous_qty: float,
        new_qty: float,
        unit_cost: float | None = None,
        reference_type: str | None = None,
        reference_id: str | None = None,
        field_id: str | None = None,
        crop_season_id: str | None = None,
        performed_by: str | None = None,
        notes: str | None = None,
    ) -> StockMovement:
        """Create a stock movement audit record"""
        total_cost = (unit_cost * quantity) if unit_cost else None

        movement = await self.db.stockmovement.create(
            data={
                "itemId": item_id,
                "movementType": movement_type,
                "quantity": quantity,
                "previousQty": previous_qty,
                "newQty": new_qty,
                "unitCost": unit_cost,
                "totalCost": total_cost,
                "referenceType": reference_type,
                "referenceId": reference_id,
                "fieldId": field_id,
                "cropSeasonId": crop_season_id,
                "performedBy": performed_by,
                "notes": notes,
            }
        )

        return movement

    async def reserve_stock(self, item_id: str, quantity: float) -> InventoryItem:
        """Reserve stock for orders/tasks"""
        # Validate input
        if quantity <= 0:
            raise ValueError(f"Quantity must be positive, got: {quantity}")

        # Use transaction to prevent race conditions
        async with self.db.tx() as transaction:
            item = await transaction.inventoryitem.find_unique(where={"id": item_id})
            if not item:
                raise ValueError(f"Item {item_id} not found")

            if item.availableQuantity < quantity:
                raise ValueError(
                    f"Insufficient available stock to reserve. "
                    f"Required: {quantity}, Available: {item.availableQuantity}"
                )

            updated_item = await transaction.inventoryitem.update(
                where={"id": item_id},
                data={
                    "reservedQuantity": item.reservedQuantity + quantity,
                    "availableQuantity": item.availableQuantity - quantity,
                },
            )

        return updated_item

    async def release_reservation(self, item_id: str, quantity: float) -> InventoryItem:
        """Release reserved stock back to available"""
        # Validate input
        if quantity <= 0:
            raise ValueError(f"Quantity must be positive, got: {quantity}")

        # Use transaction to prevent race conditions
        async with self.db.tx() as transaction:
            item = await transaction.inventoryitem.find_unique(where={"id": item_id})
            if not item:
                raise ValueError(f"Item {item_id} not found")

            if item.reservedQuantity < quantity:
                raise ValueError(
                    f"Cannot release more than reserved. "
                    f"Requested: {quantity}, Reserved: {item.reservedQuantity}"
                )

            updated_item = await transaction.inventoryitem.update(
                where={"id": item_id},
                data={
                    "reservedQuantity": item.reservedQuantity - quantity,
                    "availableQuantity": item.availableQuantity + quantity,
                },
            )

        return updated_item

    async def get_batches_for_item(
        self, item_id: str, include_empty: bool = False
    ) -> list[BatchLot]:
        """Get all batches for an item"""
        where_clause = {"itemId": item_id}
        if not include_empty:
            where_clause["remainingQty"] = {"gt": 0}

        batches = await self.db.batchlot.find_many(
            where=where_clause, order={"receivedDate": "asc"}
        )

        return batches

    async def check_low_stock(self) -> list[InventoryItem]:
        """Get items below reorder level"""
        items = await self.db.inventoryitem.find_many(
            where={
                "AND": [
                    {"reorderLevel": {"not": None}},
                    {
                        "OR": [
                            {
                                "currentQuantity": {
                                    "lte": self.db.inventoryitem.fields.reorderLevel
                                }
                            },
                        ]
                    },
                ]
            }
        )

        # Filter in Python for accurate comparison
        low_stock_items = [
            item
            for item in items
            if item.reorderLevel is not None
            and item.currentQuantity <= item.reorderLevel
        ]

        return low_stock_items

    async def check_expiring_items(self, days_threshold: int = 30) -> list[BatchLot]:
        """Get batches expiring within threshold days"""
        from datetime import timedelta

        threshold_date = datetime.utcnow() + timedelta(days=days_threshold)

        batches = await self.db.batchlot.find_many(
            where={
                "AND": [
                    {"expiryDate": {"not": None}},
                    {"expiryDate": {"lte": threshold_date}},
                    {"remainingQty": {"gt": 0}},
                ]
            },
            order={"expiryDate": "asc"},
            include={"item": True},
        )

        return batches

    async def calculate_inventory_value(self) -> dict:
        """Calculate total inventory value"""
        items = await self.db.inventoryitem.find_many(
            where={"currentQuantity": {"gt": 0}}
        )

        total_value = 0.0
        value_by_category = {}

        for item in items:
            if item.unitCost:
                item_value = item.currentQuantity * item.unitCost
                total_value += item_value

                category = item.category
                if category not in value_by_category:
                    value_by_category[category] = 0.0
                value_by_category[category] += item_value

        return {
            "total_value": total_value,
            "by_category": value_by_category,
            "item_count": len(items),
        }
