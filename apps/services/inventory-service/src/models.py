"""
Pydantic models for Inventory Service
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


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
    barcode: Optional[str] = None
    name_ar: str
    name_en: str
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    category: ItemCategory
    subcategory: Optional[str] = None
    unit: Unit
    unitSize: float = 1.0
    reorderLevel: Optional[float] = None
    reorderQuantity: Optional[float] = None
    unitCost: Optional[float] = None
    sellingPrice: Optional[float] = None
    currency: str = "YER"
    supplierId: Optional[str] = None
    warehouseId: Optional[str] = None
    storageLocation: Optional[str] = None
    expiryDate: Optional[datetime] = None


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    sku: Optional[str] = None
    barcode: Optional[str] = None
    name_ar: Optional[str] = None
    name_en: Optional[str] = None
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    category: Optional[ItemCategory] = None
    subcategory: Optional[str] = None
    unit: Optional[Unit] = None
    unitSize: Optional[float] = None
    reorderLevel: Optional[float] = None
    reorderQuantity: Optional[float] = None
    unitCost: Optional[float] = None
    sellingPrice: Optional[float] = None
    currency: Optional[str] = None
    supplierId: Optional[str] = None
    warehouseId: Optional[str] = None
    storageLocation: Optional[str] = None
    expiryDate: Optional[datetime] = None


class InventoryItemResponse(InventoryItemBase):
    id: str
    currentQuantity: float
    reservedQuantity: float
    availableQuantity: float
    lastRestocked: Optional[datetime]
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True


# Stock Movement Models
class StockMovementBase(BaseModel):
    itemId: str
    movementType: MovementType
    quantity: float
    unitCost: Optional[float] = None
    referenceType: Optional[str] = None
    referenceId: Optional[str] = None
    fieldId: Optional[str] = None
    cropSeasonId: Optional[str] = None
    performedBy: Optional[str] = None
    notes: Optional[str] = None


class StockInRequest(BaseModel):
    """Request for receiving stock (purchase)"""
    itemId: str
    quantity: float
    unitCost: Optional[float] = None
    batchNumber: Optional[str] = None
    lotNumber: Optional[str] = None
    expiryDate: Optional[datetime] = None
    productionDate: Optional[datetime] = None
    invoiceNumber: Optional[str] = None
    supplierId: Optional[str] = None
    qualityGrade: Optional[str] = None
    certifications: Optional[List[str]] = None
    referenceId: Optional[str] = None
    performedBy: Optional[str] = None
    notes: Optional[str] = None


class StockOutRequest(BaseModel):
    """Request for stock usage (sale, damage, etc.)"""
    itemId: str
    quantity: float
    movementType: MovementType = MovementType.SALE
    referenceType: Optional[str] = None
    referenceId: Optional[str] = None
    performedBy: Optional[str] = None
    notes: Optional[str] = None


class StockApplyRequest(BaseModel):
    """Request for field application"""
    itemId: str
    quantity: float
    fieldId: str
    cropSeasonId: Optional[str] = None
    performedBy: Optional[str] = None
    notes: Optional[str] = None


class StockAdjustRequest(BaseModel):
    """Request for manual stock adjustment"""
    itemId: str
    newQuantity: float
    reason: str
    performedBy: Optional[str] = None


class StockMovementResponse(BaseModel):
    id: str
    itemId: str
    movementType: MovementType
    quantity: float
    previousQty: float
    newQty: float
    unitCost: Optional[float]
    totalCost: Optional[float]
    referenceType: Optional[str]
    referenceId: Optional[str]
    fieldId: Optional[str]
    cropSeasonId: Optional[str]
    performedBy: Optional[str]
    notes: Optional[str]
    createdAt: datetime

    class Config:
        from_attributes = True


# Batch/Lot Models
class BatchLotBase(BaseModel):
    itemId: str
    lotNumber: str
    batchNumber: Optional[str] = None
    quantity: float
    productionDate: Optional[datetime] = None
    expiryDate: Optional[datetime] = None
    qualityGrade: Optional[str] = None
    certifications: Optional[List[str]] = []
    supplierId: Optional[str] = None
    invoiceNumber: Optional[str] = None
    unitCost: Optional[float] = None


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
    nameAr: Optional[str] = None
    contactName: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    governorate: Optional[str] = None
    country: str = "Yemen"
    rating: Optional[float] = None
    leadTimeDays: Optional[int] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    nameAr: Optional[str] = None
    contactName: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    governorate: Optional[str] = None
    country: Optional[str] = None
    rating: Optional[float] = None
    leadTimeDays: Optional[int] = None


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
    movements: List[StockMovementResponse]


# List Responses
class InventoryItemListResponse(BaseModel):
    items: List[InventoryItemResponse]
    total: int
    page: int
    pageSize: int


class SupplierListResponse(BaseModel):
    suppliers: List[SupplierResponse]
    total: int
    page: int
    pageSize: int
