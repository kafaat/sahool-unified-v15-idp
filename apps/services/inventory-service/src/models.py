"""
Pydantic models for Inventory Service
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


# Enums
class ItemCategory(str, Enum):
    SEED = "SEED"
    FERTILIZER = "FERTILIZER"
    PESTICIDE = "PESTICIDE"
    HERBICIDE = "HERBICIDE"
    FUNGICIDE = "FUNGICIDE"
    TOOL = "TOOL"
    EQUIPMENT_PART = "EQUIPMENT_PART"
    PACKAGING = "PACKAGING"
    FUEL = "FUEL"
    IRRIGATION_SUPPLY = "IRRIGATION_SUPPLY"
    OTHER = "OTHER"


class Unit(str, Enum):
    KG = "KG"
    GRAM = "GRAM"
    TON = "TON"
    LITER = "LITER"
    ML = "ML"
    PIECE = "PIECE"
    BAG = "BAG"
    BOX = "BOX"
    ROLL = "ROLL"
    METER = "METER"
    HECTARE_DOSE = "HECTARE_DOSE"


class MovementType(str, Enum):
    PURCHASE = "PURCHASE"
    SALE = "SALE"
    FIELD_APPLICATION = "FIELD_APPLICATION"
    TRANSFER = "TRANSFER"
    ADJUSTMENT = "ADJUSTMENT"
    RETURN = "RETURN"
    DAMAGE = "DAMAGE"
    EXPIRED = "EXPIRED"


# Inventory Item Models
class InventoryItemBase(BaseModel):
    sku: str
    barcode: str | None = None
    name_ar: str
    name_en: str
    description_ar: str | None = None
    description_en: str | None = None
    category: ItemCategory
    subcategory: str | None = None
    unit: Unit
    unitSize: float = 1.0
    reorderLevel: float | None = None
    reorderQuantity: float | None = None
    unitCost: float | None = None
    sellingPrice: float | None = None
    currency: str = "YER"
    supplierId: str | None = None
    warehouseId: str | None = None
    storageLocation: str | None = None
    expiryDate: datetime | None = None


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    sku: str | None = None
    barcode: str | None = None
    name_ar: str | None = None
    name_en: str | None = None
    description_ar: str | None = None
    description_en: str | None = None
    category: ItemCategory | None = None
    subcategory: str | None = None
    unit: Unit | None = None
    unitSize: float | None = None
    reorderLevel: float | None = None
    reorderQuantity: float | None = None
    unitCost: float | None = None
    sellingPrice: float | None = None
    currency: str | None = None
    supplierId: str | None = None
    warehouseId: str | None = None
    storageLocation: str | None = None
    expiryDate: datetime | None = None


class InventoryItemResponse(InventoryItemBase):
    id: str
    currentQuantity: float
    reservedQuantity: float
    availableQuantity: float
    lastRestocked: datetime | None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


# Stock Movement Models
class StockMovementBase(BaseModel):
    itemId: str
    movementType: MovementType
    quantity: float
    unitCost: float | None = None
    referenceType: str | None = None
    referenceId: str | None = None
    fieldId: str | None = None
    cropSeasonId: str | None = None
    performedBy: str | None = None
    notes: str | None = None


class StockInRequest(BaseModel):
    """Request for receiving stock (purchase)"""

    itemId: str
    quantity: float
    unitCost: float | None = None
    batchNumber: str | None = None
    lotNumber: str | None = None
    expiryDate: datetime | None = None
    productionDate: datetime | None = None
    invoiceNumber: str | None = None
    supplierId: str | None = None
    qualityGrade: str | None = None
    certifications: list[str] | None = None
    referenceId: str | None = None
    performedBy: str | None = None
    notes: str | None = None


class StockOutRequest(BaseModel):
    """Request for stock usage (sale, damage, etc.)"""

    itemId: str
    quantity: float
    movementType: MovementType = MovementType.SALE
    referenceType: str | None = None
    referenceId: str | None = None
    performedBy: str | None = None
    notes: str | None = None


class StockApplyRequest(BaseModel):
    """Request for field application"""

    itemId: str
    quantity: float
    fieldId: str
    cropSeasonId: str | None = None
    performedBy: str | None = None
    notes: str | None = None


class StockAdjustRequest(BaseModel):
    """Request for manual stock adjustment"""

    itemId: str
    newQuantity: float
    reason: str
    performedBy: str | None = None


class StockMovementResponse(BaseModel):
    id: str
    itemId: str
    movementType: MovementType
    quantity: float
    previousQty: float
    newQty: float
    unitCost: float | None
    totalCost: float | None
    referenceType: str | None
    referenceId: str | None
    fieldId: str | None
    cropSeasonId: str | None
    performedBy: str | None
    notes: str | None
    createdAt: datetime

    class Config:
        from_attributes = True


# Batch/Lot Models
class BatchLotBase(BaseModel):
    itemId: str
    lotNumber: str
    batchNumber: str | None = None
    quantity: float
    productionDate: datetime | None = None
    expiryDate: datetime | None = None
    qualityGrade: str | None = None
    certifications: list[str] | None = []
    supplierId: str | None = None
    invoiceNumber: str | None = None
    unitCost: float | None = None


class BatchLotCreate(BatchLotBase):
    pass


class BatchLotResponse(BatchLotBase):
    id: str
    remainingQty: float
    receivedDate: datetime

    class Config:
        from_attributes = True


# Supplier Models
class SupplierBase(BaseModel):
    name: str
    nameAr: str | None = None
    contactName: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    governorate: str | None = None
    country: str = "Yemen"
    rating: float | None = None
    leadTimeDays: int | None = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: str | None = None
    nameAr: str | None = None
    contactName: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    governorate: str | None = None
    country: str | None = None
    rating: float | None = None
    leadTimeDays: int | None = None


class SupplierResponse(SupplierBase):
    id: str
    createdAt: datetime

    class Config:
        from_attributes = True


# Report Models
class InventorySummary(BaseModel):
    totalItems: int
    totalValue: float
    lowStockItems: int
    expiringItems: int
    outOfStockItems: int


class InventoryValuation(BaseModel):
    totalValue: float
    currency: str
    itemCount: int
    byCategory: dict


class ConsumptionReport(BaseModel):
    itemId: str
    itemName: str
    period: str
    totalConsumed: float
    averageDaily: float
    movements: list[StockMovementResponse]


# List Responses
class InventoryItemListResponse(BaseModel):
    items: list[InventoryItemResponse]
    total: int
    page: int
    pageSize: int


class SupplierListResponse(BaseModel):
    suppliers: list[SupplierResponse]
    total: int
    page: int
    pageSize: int
