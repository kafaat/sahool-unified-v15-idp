"""
Warehouse and Storage Management Module
Handles warehouses, zones, locations, and stock transfers
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from enum import Enum


class WarehouseType(Enum):
    MAIN = "main"           # Main farm warehouse
    FIELD = "field"         # Field storage shed
    COLD = "cold"           # Cold storage
    CHEMICAL = "chemical"   # Chemical storage (pesticides)
    SEED = "seed"           # Seed bank
    FUEL = "fuel"           # Fuel storage


class StorageCondition(Enum):
    AMBIENT = "ambient"
    COOL = "cool"           # 10-15°C
    COLD = "cold"           # 2-8°C
    FROZEN = "frozen"       # Below 0°C
    DRY = "dry"             # Low humidity
    CONTROLLED = "controlled"  # Temperature + humidity controlled


class TransferStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TransferType(Enum):
    INTER_WAREHOUSE = "inter_warehouse"
    RECEIVING = "receiving"
    DISPATCH = "dispatch"


@dataclass
class Warehouse:
    id: str
    name: str
    name_ar: str
    warehouse_type: WarehouseType
    location: Dict  # {lat, lon, address, governorate}
    capacity: float
    capacity_unit: str  # "cubic_meter", "ton", "pallet"
    current_utilization: float
    storage_condition: StorageCondition
    temperature_range: Optional[Dict]  # {min, max}
    humidity_range: Optional[Dict]
    zones: List[Dict]  # [{zone_id, name, capacity}]
    is_active: bool
    manager_id: Optional[str] = None
    manager_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class StorageLocation:
    id: str
    warehouse_id: str
    zone: str
    aisle: str
    shelf: str
    bin: str
    location_code: str  # e.g., "A-01-03-B"
    capacity: float
    current_items: List[str]  # Item IDs
    storage_condition: StorageCondition
    is_occupied: bool = False
    current_qty: float = 0


class WarehouseManager:
    """Manage warehouses, zones, and storage locations"""

    def __init__(self, db):
        """
        Initialize with Prisma database client

        Args:
            db: Prisma client instance
        """
        self.db = db

    async def create_warehouse(self, data: dict) -> Warehouse:
        """
        Create a new warehouse

        Args:
            data: Warehouse data including name, type, location, capacity

        Returns:
            Created Warehouse object
        """
        warehouse = await self.db.warehouse.create(
            data={
                "name": data["name"],
                "nameAr": data["name_ar"],
                "warehouseType": data["warehouse_type"],
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "address": data.get("address"),
                "governorate": data.get("governorate"),
                "capacityValue": data["capacity_value"],
                "capacityUnit": data.get("capacity_unit", "cubic_meter"),
                "storageCondition": data.get("storage_condition", "AMBIENT"),
                "tempMin": data.get("temp_min"),
                "tempMax": data.get("temp_max"),
                "humidityMin": data.get("humidity_min"),
                "humidityMax": data.get("humidity_max"),
                "managerId": data.get("manager_id"),
                "managerName": data.get("manager_name"),
            }
        )

        return self._warehouse_to_dataclass(warehouse)

    async def get_warehouses(
        self,
        warehouse_type: Optional[str] = None,
        is_active: bool = True
    ) -> List[Warehouse]:
        """
        Get all warehouses, optionally filtered

        Args:
            warehouse_type: Filter by warehouse type
            is_active: Filter by active status

        Returns:
            List of Warehouse objects
        """
        where = {"isActive": is_active}
        if warehouse_type:
            where["warehouseType"] = warehouse_type

        warehouses = await self.db.warehouse.find_many(
            where=where,
            include={"zones": True}
        )

        return [self._warehouse_to_dataclass(w) for w in warehouses]

    async def get_warehouse(self, warehouse_id: str) -> Optional[Warehouse]:
        """
        Get a specific warehouse by ID

        Args:
            warehouse_id: Warehouse ID

        Returns:
            Warehouse object or None
        """
        warehouse = await self.db.warehouse.find_unique(
            where={"id": warehouse_id},
            include={"zones": True}
        )

        if not warehouse:
            return None

        return self._warehouse_to_dataclass(warehouse)

    async def get_warehouse_utilization(self, warehouse_id: str) -> Dict:
        """
        Get current capacity usage by zone

        Args:
            warehouse_id: Warehouse ID

        Returns:
            Dictionary with utilization metrics
        """
        warehouse = await self.db.warehouse.find_unique(
            where={"id": warehouse_id},
            include={"zones": True}
        )

        if not warehouse:
            return {"error": "Warehouse not found"}

        total_capacity = warehouse.capacityValue
        total_usage = warehouse.currentUsage

        zones_utilization = []
        for zone in warehouse.zones:
            zones_utilization.append({
                "zone_id": zone.id,
                "zone_name": zone.name,
                "capacity": zone.capacity,
                "usage": zone.currentUsage,
                "utilization_pct": (zone.currentUsage / zone.capacity * 100) if zone.capacity > 0 else 0,
                "available": zone.capacity - zone.currentUsage
            })

        return {
            "warehouse_id": warehouse_id,
            "warehouse_name": warehouse.name,
            "total_capacity": total_capacity,
            "total_usage": total_usage,
            "utilization_pct": (total_usage / total_capacity * 100) if total_capacity > 0 else 0,
            "available_capacity": total_capacity - total_usage,
            "capacity_unit": warehouse.capacityUnit,
            "zones": zones_utilization,
            "zone_count": len(zones_utilization)
        }

    async def find_storage_location(
        self,
        item_category: str,
        required_condition: str,
        quantity: float
    ) -> Optional[StorageLocation]:
        """
        Find suitable storage location for item

        Args:
            item_category: Item category (SEED, FERTILIZER, etc.)
            required_condition: Required storage condition
            quantity: Quantity to store

        Returns:
            StorageLocation object or None
        """
        # Map item categories to warehouse types
        category_warehouse_map = {
            "SEED": "SEED",
            "CHEMICAL": "CHEMICAL",
            "PESTICIDE": "CHEMICAL",
            "HERBICIDE": "CHEMICAL",
            "FUNGICIDE": "CHEMICAL",
            "FUEL": "FUEL",
            "COLD_STORAGE": "COLD"
        }

        preferred_type = category_warehouse_map.get(item_category, "MAIN")

        # Find warehouses with matching type and condition
        warehouses = await self.db.warehouse.find_many(
            where={
                "warehouseType": preferred_type,
                "storageCondition": required_condition,
                "isActive": True
            },
            include={"zones": {"include": {"locations": True}}}
        )

        # Find available location
        for warehouse in warehouses:
            for zone in warehouse.zones:
                for location in zone.locations:
                    if not location.isOccupied and location.capacity >= quantity:
                        return StorageLocation(
                            id=location.id,
                            warehouse_id=warehouse.id,
                            zone=zone.name,
                            aisle=location.aisle,
                            shelf=location.shelf,
                            bin=location.bin,
                            location_code=location.locationCode,
                            capacity=location.capacity,
                            current_items=[],
                            storage_condition=StorageCondition(warehouse.storageCondition.lower()),
                            is_occupied=location.isOccupied,
                            current_qty=location.currentQty
                        )

        return None

    async def transfer_stock(
        self,
        item_id: str,
        from_warehouse: Optional[str],
        to_warehouse: str,
        quantity: float,
        requested_by: str,
        transfer_type: str = "INTER_WAREHOUSE",
        notes: Optional[str] = None
    ) -> Dict:
        """
        Transfer stock between warehouses

        Args:
            item_id: Inventory item ID
            from_warehouse: Source warehouse ID (None for receiving)
            to_warehouse: Destination warehouse ID
            quantity: Quantity to transfer
            requested_by: User ID requesting transfer
            transfer_type: Type of transfer
            notes: Optional notes

        Returns:
            Transfer record
        """
        # Create transfer record
        transfer = await self.db.stocktransfer.create(
            data={
                "itemId": item_id,
                "fromWarehouseId": from_warehouse,
                "toWarehouseId": to_warehouse,
                "quantity": quantity,
                "transferType": transfer_type,
                "status": "PENDING",
                "requestedBy": requested_by,
                "notes": notes
            }
        )

        return {
            "transfer_id": transfer.id,
            "item_id": item_id,
            "from_warehouse": from_warehouse,
            "to_warehouse": to_warehouse,
            "quantity": quantity,
            "status": transfer.status,
            "requested_at": transfer.requestedAt.isoformat(),
            "requested_by": requested_by
        }

    async def approve_transfer(
        self,
        transfer_id: str,
        approved_by: str
    ) -> Dict:
        """
        Approve a pending transfer

        Args:
            transfer_id: Transfer ID
            approved_by: User ID approving transfer

        Returns:
            Updated transfer record
        """
        transfer = await self.db.stocktransfer.update(
            where={"id": transfer_id},
            data={
                "status": "APPROVED",
                "approvedBy": approved_by,
                "approvedAt": datetime.utcnow()
            }
        )

        return {
            "transfer_id": transfer.id,
            "status": transfer.status,
            "approved_by": approved_by,
            "approved_at": transfer.approvedAt.isoformat() if transfer.approvedAt else None
        }

    async def complete_transfer(
        self,
        transfer_id: str,
        performed_by: str
    ) -> Dict:
        """
        Mark transfer as completed

        Args:
            transfer_id: Transfer ID
            performed_by: User ID performing transfer

        Returns:
            Updated transfer record
        """
        transfer = await self.db.stocktransfer.update(
            where={"id": transfer_id},
            data={
                "status": "COMPLETED",
                "performedBy": performed_by,
                "completedAt": datetime.utcnow()
            }
        )

        return {
            "transfer_id": transfer.id,
            "status": transfer.status,
            "performed_by": performed_by,
            "completed_at": transfer.completedAt.isoformat() if transfer.completedAt else None
        }

    async def get_warehouse_inventory(
        self,
        warehouse_id: str,
        category: Optional[str] = None
    ) -> List[Dict]:
        """
        Get all inventory in a warehouse

        Args:
            warehouse_id: Warehouse ID
            category: Optional filter by item category

        Returns:
            List of inventory items
        """
        where = {"warehouseId": warehouse_id}
        if category:
            where["category"] = category

        items = await self.db.inventoryitem.find_many(
            where=where,
            include={"batchLots": True}
        )

        result = []
        for item in items:
            result.append({
                "item_id": item.id,
                "sku": item.sku,
                "name_ar": item.name_ar,
                "name_en": item.name_en,
                "category": item.category,
                "quantity": item.currentQuantity,
                "available": item.availableQuantity,
                "unit": item.unit,
                "storage_location": item.storageLocation,
                "expiry_date": item.expiryDate.isoformat() if item.expiryDate else None,
                "batch_count": len(item.batchLots) if item.batchLots else 0
            })

        return result

    async def check_storage_conditions(
        self,
        warehouse_id: str
    ) -> Dict:
        """
        Check if current conditions match required conditions

        Args:
            warehouse_id: Warehouse ID

        Returns:
            Condition check results
        """
        warehouse = await self.db.warehouse.find_unique(
            where={"id": warehouse_id}
        )

        if not warehouse:
            return {"error": "Warehouse not found"}

        # In a real system, this would check sensor data
        # For now, return the configured ranges
        return {
            "warehouse_id": warehouse_id,
            "warehouse_name": warehouse.name,
            "storage_condition": warehouse.storageCondition,
            "temperature_range": {
                "min": warehouse.tempMin,
                "max": warehouse.tempMax,
                "current": None  # Would come from IoT sensors
            },
            "humidity_range": {
                "min": warehouse.humidityMin,
                "max": warehouse.humidityMax,
                "current": None  # Would come from IoT sensors
            },
            "status": "OK",  # Would be calculated based on sensor data
            "alerts": []
        }

    async def get_expiring_items(
        self,
        warehouse_id: str,
        days: int = 30
    ) -> List[Dict]:
        """
        Get items expiring within N days in warehouse

        Args:
            warehouse_id: Warehouse ID
            days: Number of days threshold

        Returns:
            List of expiring items
        """
        cutoff_date = datetime.utcnow() + timedelta(days=days)

        items = await self.db.inventoryitem.find_many(
            where={
                "warehouseId": warehouse_id,
                "expiryDate": {
                    "lte": cutoff_date,
                    "gte": datetime.utcnow()
                }
            },
            order_by={"expiryDate": "asc"}
        )

        result = []
        for item in items:
            days_until_expiry = (item.expiryDate - datetime.utcnow()).days if item.expiryDate else None
            result.append({
                "item_id": item.id,
                "sku": item.sku,
                "name_ar": item.name_ar,
                "name_en": item.name_en,
                "category": item.category,
                "quantity": item.currentQuantity,
                "unit": item.unit,
                "expiry_date": item.expiryDate.isoformat() if item.expiryDate else None,
                "days_until_expiry": days_until_expiry,
                "storage_location": item.storageLocation
            })

        return result

    async def create_zone(
        self,
        warehouse_id: str,
        name: str,
        name_ar: str,
        capacity: float,
        condition: Optional[str] = None
    ) -> Dict:
        """
        Create a zone within a warehouse

        Args:
            warehouse_id: Warehouse ID
            name: Zone name (English)
            name_ar: Zone name (Arabic)
            capacity: Zone capacity
            condition: Storage condition

        Returns:
            Created zone
        """
        zone = await self.db.zone.create(
            data={
                "warehouseId": warehouse_id,
                "name": name,
                "nameAr": name_ar,
                "capacity": capacity,
                "condition": condition
            }
        )

        return {
            "zone_id": zone.id,
            "warehouse_id": warehouse_id,
            "name": zone.name,
            "name_ar": zone.nameAr,
            "capacity": zone.capacity,
            "current_usage": zone.currentUsage,
            "condition": zone.condition
        }

    async def create_storage_location(
        self,
        zone_id: str,
        aisle: str,
        shelf: str,
        bin: str,
        capacity: float
    ) -> Dict:
        """
        Create a storage location within a zone

        Args:
            zone_id: Zone ID
            aisle: Aisle identifier
            shelf: Shelf identifier
            bin: Bin identifier
            capacity: Location capacity

        Returns:
            Created storage location
        """
        location_code = f"{aisle}-{shelf}-{bin}"

        location = await self.db.storagelocation.create(
            data={
                "zoneId": zone_id,
                "aisle": aisle,
                "shelf": shelf,
                "bin": bin,
                "locationCode": location_code,
                "capacity": capacity
            }
        )

        return {
            "location_id": location.id,
            "zone_id": zone_id,
            "location_code": location_code,
            "aisle": aisle,
            "shelf": shelf,
            "bin": bin,
            "capacity": capacity,
            "is_occupied": location.isOccupied
        }

    async def get_transfers(
        self,
        warehouse_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get stock transfers

        Args:
            warehouse_id: Filter by warehouse (from or to)
            status: Filter by status
            limit: Maximum number of records

        Returns:
            List of transfers
        """
        where = {}
        if warehouse_id:
            where["OR"] = [
                {"fromWarehouseId": warehouse_id},
                {"toWarehouseId": warehouse_id}
            ]
        if status:
            where["status"] = status

        transfers = await self.db.stocktransfer.find_many(
            where=where,
            take=limit,
            order_by={"requestedAt": "desc"},
            include={
                "fromWarehouse": True,
                "toWarehouse": True
            }
        )

        result = []
        for t in transfers:
            result.append({
                "transfer_id": t.id,
                "item_id": t.itemId,
                "from_warehouse": {
                    "id": t.fromWarehouse.id if t.fromWarehouse else None,
                    "name": t.fromWarehouse.name if t.fromWarehouse else None
                },
                "to_warehouse": {
                    "id": t.toWarehouse.id,
                    "name": t.toWarehouse.name
                },
                "quantity": t.quantity,
                "transfer_type": t.transferType,
                "status": t.status,
                "requested_by": t.requestedBy,
                "requested_at": t.requestedAt.isoformat(),
                "approved_by": t.approvedBy,
                "completed_at": t.completedAt.isoformat() if t.completedAt else None,
                "notes": t.notes
            })

        return result

    def _warehouse_to_dataclass(self, warehouse) -> Warehouse:
        """Convert Prisma warehouse to dataclass"""
        return Warehouse(
            id=warehouse.id,
            name=warehouse.name,
            name_ar=warehouse.nameAr,
            warehouse_type=WarehouseType(warehouse.warehouseType.lower()),
            location={
                "lat": warehouse.latitude,
                "lon": warehouse.longitude,
                "address": warehouse.address,
                "governorate": warehouse.governorate
            },
            capacity=warehouse.capacityValue,
            capacity_unit=warehouse.capacityUnit,
            current_utilization=warehouse.currentUsage,
            storage_condition=StorageCondition(warehouse.storageCondition.lower()),
            temperature_range={
                "min": warehouse.tempMin,
                "max": warehouse.tempMax
            } if warehouse.tempMin or warehouse.tempMax else None,
            humidity_range={
                "min": warehouse.humidityMin,
                "max": warehouse.humidityMax
            } if warehouse.humidityMin or warehouse.humidityMax else None,
            zones=[{
                "zone_id": z.id,
                "name": z.name,
                "capacity": z.capacity,
                "usage": z.currentUsage
            } for z in (warehouse.zones or [])],
            is_active=warehouse.isActive,
            manager_id=warehouse.managerId,
            manager_name=warehouse.managerName,
            created_at=warehouse.createdAt,
            updated_at=warehouse.updatedAt
        )
