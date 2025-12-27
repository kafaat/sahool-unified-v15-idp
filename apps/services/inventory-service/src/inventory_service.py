"""
Inventory Service - Main business logic layer
"""
from datetime import datetime, timedelta
from typing import List, Optional
from prisma import Prisma
from prisma.models import InventoryItem, Supplier, BatchLot, StockMovement

from models import (
    InventoryItemCreate,
    InventoryItemUpdate,
    StockInRequest,
    StockOutRequest,
    StockApplyRequest,
    StockAdjustRequest,
    SupplierCreate,
    SupplierUpdate,
    MovementType,
    InventorySummary,
    ConsumptionReport,
)
from stock_manager import StockManager


class InventoryService:
    """Main service class for inventory operations"""

    def __init__(self, db: Prisma):
        self.db = db
        self.stock_manager = StockManager(db)

    # ========== Inventory Item Operations ==========

    async def create_item(self, item_data: InventoryItemCreate) -> InventoryItem:
        """Create a new inventory item"""
        # Use transaction to prevent race condition on SKU uniqueness
        async with self.db.tx() as transaction:
            # Check if SKU already exists with SELECT FOR UPDATE
            existing = await transaction.inventoryitem.find_unique(
                where={"sku": item_data.sku}
            )
            if existing:
                raise ValueError(f"Item with SKU {item_data.sku} already exists")

            # Create item within transaction
            item = await transaction.inventoryitem.create(
                data={
                    **item_data.model_dump(),
                    "currentQuantity": 0,
                    "reservedQuantity": 0,
                    "availableQuantity": 0
                }
            )

        return item

    async def get_item(self, item_id: str) -> Optional[InventoryItem]:
        """Get item by ID"""
        item = await self.db.inventoryitem.find_unique(
            where={"id": item_id},
            include={"supplier": True}
        )
        return item

    async def list_items(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        search: Optional[str] = None
    ) -> tuple[List[InventoryItem], int]:
        """List items with pagination and filters"""
        where_clause = {}

        if category:
            where_clause["category"] = category

        if search:
            where_clause["OR"] = [
                {"name_en": {"contains": search, "mode": "insensitive"}},
                {"name_ar": {"contains": search}},
                {"sku": {"contains": search, "mode": "insensitive"}},
            ]

        items = await self.db.inventoryitem.find_many(
            where=where_clause,
            skip=skip,
            take=limit,
            include={"supplier": True},
            order={"createdAt": "desc"}
        )

        total = await self.db.inventoryitem.count(where=where_clause)

        return items, total

    async def update_item(
        self,
        item_id: str,
        item_data: InventoryItemUpdate
    ) -> InventoryItem:
        """Update an inventory item"""
        # Get existing item
        existing = await self.db.inventoryitem.find_unique(where={"id": item_id})
        if not existing:
            raise ValueError(f"Item {item_id} not found")

        # Check SKU uniqueness if being updated
        if item_data.sku and item_data.sku != existing.sku:
            sku_exists = await self.db.inventoryitem.find_unique(
                where={"sku": item_data.sku}
            )
            if sku_exists:
                raise ValueError(f"Item with SKU {item_data.sku} already exists")

        # Update item
        update_data = item_data.model_dump(exclude_unset=True)
        item = await self.db.inventoryitem.update(
            where={"id": item_id},
            data=update_data
        )

        return item

    async def delete_item(self, item_id: str) -> bool:
        """Delete an inventory item"""
        item = await self.db.inventoryitem.find_unique(where={"id": item_id})
        if not item:
            raise ValueError(f"Item {item_id} not found")

        if item.currentQuantity > 0:
            raise ValueError("Cannot delete item with stock quantity > 0")

        await self.db.inventoryitem.delete(where={"id": item_id})
        return True

    async def get_low_stock_items(self) -> List[InventoryItem]:
        """Get items below reorder level"""
        return await self.stock_manager.check_low_stock()

    async def get_expiring_items(self, days: int = 30) -> List[BatchLot]:
        """Get items expiring within specified days"""
        return await self.stock_manager.check_expiring_items(days)

    # ========== Stock Movement Operations ==========

    async def stock_in(self, request: StockInRequest) -> dict:
        """
        Receive stock (purchase)
        Creates batch/lot and updates quantities
        """
        # Verify item exists
        item = await self.db.inventoryitem.find_unique(where={"id": request.itemId})
        if not item:
            raise ValueError(f"Item {request.itemId} not found")

        previous_qty = item.currentQuantity

        # Generate lot number if not provided
        lot_number = request.lotNumber
        if not lot_number:
            lot_number = f"LOT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        # Create batch/lot
        batch = await self.stock_manager.add_stock_batch(
            item_id=request.itemId,
            quantity=request.quantity,
            lot_number=lot_number,
            batch_number=request.batchNumber,
            expiry_date=request.expiryDate,
            production_date=request.productionDate,
            supplier_id=request.supplierId,
            invoice_number=request.invoiceNumber,
            unit_cost=request.unitCost,
            quality_grade=request.qualityGrade,
            certifications=request.certifications
        )

        # Update item quantities
        updated_item = await self.stock_manager.update_item_quantities(
            item_id=request.itemId,
            quantity_change=request.quantity,
            is_addition=True
        )

        # Create movement record
        movement = await self.stock_manager.create_movement_record(
            item_id=request.itemId,
            movement_type=MovementType.PURCHASE,
            quantity=request.quantity,
            previous_qty=previous_qty,
            new_qty=updated_item.currentQuantity,
            unit_cost=request.unitCost,
            reference_type="batch",
            reference_id=batch.id,
            performed_by=request.performedBy,
            notes=request.notes
        )

        return {
            "success": True,
            "batch": batch,
            "item": updated_item,
            "movement": movement
        }

    async def stock_out(self, request: StockOutRequest) -> dict:
        """
        Stock out (sale, damage, etc.)
        Uses FIFO to consume from batches
        """
        # Verify item exists
        item = await self.db.inventoryitem.find_unique(where={"id": request.itemId})
        if not item:
            raise ValueError(f"Item {request.itemId} not found")

        previous_qty = item.currentQuantity

        # Consume stock using FIFO
        consumed_batches, total_consumed = await self.stock_manager.consume_stock_fifo(
            item_id=request.itemId,
            quantity=request.quantity
        )

        # Calculate average cost
        total_cost = sum(b["quantity"] * b["unit_cost"] for b in consumed_batches)
        avg_unit_cost = total_cost / total_consumed if total_consumed > 0 else None

        # Update item quantities
        updated_item = await self.stock_manager.update_item_quantities(
            item_id=request.itemId,
            quantity_change=request.quantity,
            is_addition=False
        )

        # Create movement record
        movement = await self.stock_manager.create_movement_record(
            item_id=request.itemId,
            movement_type=request.movementType,
            quantity=request.quantity,
            previous_qty=previous_qty,
            new_qty=updated_item.currentQuantity,
            unit_cost=avg_unit_cost,
            reference_type=request.referenceType,
            reference_id=request.referenceId,
            performed_by=request.performedBy,
            notes=request.notes
        )

        return {
            "success": True,
            "consumed_batches": consumed_batches,
            "item": updated_item,
            "movement": movement
        }

    async def stock_apply(self, request: StockApplyRequest) -> dict:
        """
        Apply stock to field (field application)
        Uses FIFO and records field reference
        """
        # Verify item exists
        item = await self.db.inventoryitem.find_unique(where={"id": request.itemId})
        if not item:
            raise ValueError(f"Item {request.itemId} not found")

        previous_qty = item.currentQuantity

        # Consume stock using FIFO
        consumed_batches, total_consumed = await self.stock_manager.consume_stock_fifo(
            item_id=request.itemId,
            quantity=request.quantity
        )

        # Calculate average cost
        total_cost = sum(b["quantity"] * b["unit_cost"] for b in consumed_batches)
        avg_unit_cost = total_cost / total_consumed if total_consumed > 0 else None

        # Update item quantities
        updated_item = await self.stock_manager.update_item_quantities(
            item_id=request.itemId,
            quantity_change=request.quantity,
            is_addition=False
        )

        # Create movement record with field reference
        movement = await self.stock_manager.create_movement_record(
            item_id=request.itemId,
            movement_type=MovementType.FIELD_APPLICATION,
            quantity=request.quantity,
            previous_qty=previous_qty,
            new_qty=updated_item.currentQuantity,
            unit_cost=avg_unit_cost,
            reference_type="field_application",
            field_id=request.fieldId,
            crop_season_id=request.cropSeasonId,
            performed_by=request.performedBy,
            notes=request.notes
        )

        return {
            "success": True,
            "consumed_batches": consumed_batches,
            "item": updated_item,
            "movement": movement
        }

    async def stock_adjust(self, request: StockAdjustRequest) -> dict:
        """
        Manual stock adjustment
        Used for corrections, physical counts, etc.
        """
        # Verify item exists
        item = await self.db.inventoryitem.find_unique(where={"id": request.itemId})
        if not item:
            raise ValueError(f"Item {request.itemId} not found")

        previous_qty = item.currentQuantity
        quantity_diff = request.newQuantity - previous_qty

        # Update item quantities directly
        updated_item = await self.db.inventoryitem.update(
            where={"id": request.itemId},
            data={
                "currentQuantity": request.newQuantity,
                "availableQuantity": request.newQuantity - item.reservedQuantity
            }
        )

        # Create movement record
        movement = await self.stock_manager.create_movement_record(
            item_id=request.itemId,
            movement_type=MovementType.ADJUSTMENT,
            quantity=abs(quantity_diff),
            previous_qty=previous_qty,
            new_qty=updated_item.currentQuantity,
            performed_by=request.performedBy,
            notes=f"Adjustment: {request.reason}"
        )

        return {
            "success": True,
            "item": updated_item,
            "movement": movement,
            "adjustment": quantity_diff
        }

    async def get_item_movements(
        self,
        item_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[StockMovement], int]:
        """Get movement history for an item"""
        movements = await self.db.stockmovement.find_many(
            where={"itemId": item_id},
            skip=skip,
            take=limit,
            order={"createdAt": "desc"}
        )

        total = await self.db.stockmovement.count(where={"itemId": item_id})

        return movements, total

    # ========== Batch Operations ==========

    async def get_item_batches(
        self,
        item_id: str,
        include_empty: bool = False
    ) -> List[BatchLot]:
        """Get batches for an item"""
        return await self.stock_manager.get_batches_for_item(item_id, include_empty)

    # ========== Supplier Operations ==========

    async def create_supplier(self, supplier_data: SupplierCreate) -> Supplier:
        """Create a new supplier"""
        supplier = await self.db.supplier.create(
            data=supplier_data.model_dump()
        )
        return supplier

    async def get_supplier(self, supplier_id: str) -> Optional[Supplier]:
        """Get supplier by ID"""
        supplier = await self.db.supplier.find_unique(
            where={"id": supplier_id},
            include={"items": True}
        )
        return supplier

    async def list_suppliers(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Supplier], int]:
        """List suppliers with pagination"""
        suppliers = await self.db.supplier.find_many(
            skip=skip,
            take=limit,
            order={"createdAt": "desc"}
        )

        total = await self.db.supplier.count()

        return suppliers, total

    async def update_supplier(
        self,
        supplier_id: str,
        supplier_data: SupplierUpdate
    ) -> Supplier:
        """Update a supplier"""
        existing = await self.db.supplier.find_unique(where={"id": supplier_id})
        if not existing:
            raise ValueError(f"Supplier {supplier_id} not found")

        update_data = supplier_data.model_dump(exclude_unset=True)
        supplier = await self.db.supplier.update(
            where={"id": supplier_id},
            data=update_data
        )

        return supplier

    # ========== Reports ==========

    async def get_inventory_summary(self) -> InventorySummary:
        """Get inventory summary statistics"""
        # Total items
        total_items = await self.db.inventoryitem.count()

        # Low stock items
        low_stock = await self.stock_manager.check_low_stock()
        low_stock_count = len(low_stock)

        # Expiring items
        expiring = await self.stock_manager.check_expiring_items(30)
        expiring_count = len(expiring)

        # Out of stock items
        out_of_stock = await self.db.inventoryitem.count(
            where={"currentQuantity": {"lte": 0}}
        )

        # Total value
        valuation = await self.stock_manager.calculate_inventory_value()

        return InventorySummary(
            totalItems=total_items,
            totalValue=valuation["total_value"],
            lowStockItems=low_stock_count,
            expiringItems=expiring_count,
            outOfStockItems=out_of_stock
        )

    async def get_inventory_valuation(self) -> dict:
        """Get inventory valuation report"""
        valuation = await self.stock_manager.calculate_inventory_value()
        return {
            "totalValue": valuation["total_value"],
            "currency": "YER",
            "itemCount": valuation["item_count"],
            "byCategory": valuation["by_category"]
        }

    async def get_consumption_report(
        self,
        item_id: str,
        days: int = 30
    ) -> ConsumptionReport:
        """Get consumption report for an item"""
        item = await self.db.inventoryitem.find_unique(where={"id": item_id})
        if not item:
            raise ValueError(f"Item {item_id} not found")

        # Get movements for the period
        since_date = datetime.utcnow() - timedelta(days=days)
        movements = await self.db.stockmovement.find_many(
            where={
                "itemId": item_id,
                "createdAt": {"gte": since_date},
                "movementType": {
                    "in": [
                        MovementType.SALE,
                        MovementType.FIELD_APPLICATION,
                        MovementType.DAMAGE,
                        MovementType.EXPIRED
                    ]
                }
            },
            order={"createdAt": "desc"}
        )

        # Calculate total consumed
        total_consumed = sum(m.quantity for m in movements)
        average_daily = total_consumed / days if days > 0 else 0

        return ConsumptionReport(
            itemId=item_id,
            itemName=f"{item.name_en} ({item.name_ar})",
            period=f"Last {days} days",
            totalConsumed=total_consumed,
            averageDaily=average_daily,
            movements=[m for m in movements]
        )
