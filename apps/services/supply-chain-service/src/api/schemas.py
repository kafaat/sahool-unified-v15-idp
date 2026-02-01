"""Pydantic schemas for Supply Chain Service."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProductCategory(str, Enum):
    """Product category enumeration."""

    SEEDS = "seeds"
    FERTILIZERS = "fertilizers"
    PESTICIDES = "pesticides"
    HERBICIDES = "herbicides"
    EQUIPMENT = "equipment"
    IRRIGATION = "irrigation"
    TOOLS = "tools"
    OTHER = "other"


class OrderStatus(str, Enum):
    """Order status enumeration."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class DeliveryStatusEnum(str, Enum):
    """Delivery status enumeration."""

    PREPARING = "preparing"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    FAILED = "failed"


class PaymentMethod(str, Enum):
    """Payment method enumeration."""

    CASH_ON_DELIVERY = "cash_on_delivery"
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"


# Base schemas
class Product(BaseModel):
    """Product schema."""

    id: UUID
    name: str = Field(..., min_length=1, max_length=200)
    name_ar: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    description_ar: str | None = None
    category: ProductCategory
    unit: str = Field(..., description="Unit of measurement (kg, L, pcs)")
    unit_ar: str = Field(..., description="وحدة القياس")
    price_min: float = Field(..., ge=0, description="Minimum price in SAR")
    price_max: float = Field(..., ge=0, description="Maximum price in SAR")
    image_url: str | None = None
    is_available: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    """Product creation schema."""

    name: str = Field(..., min_length=1, max_length=200)
    name_ar: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    description_ar: str | None = None
    category: ProductCategory
    unit: str
    unit_ar: str
    price_min: float = Field(..., ge=0)
    price_max: float = Field(..., ge=0)


class Supplier(BaseModel):
    """Supplier schema."""

    id: UUID
    name: str = Field(..., min_length=1, max_length=200)
    name_ar: str = Field(..., min_length=1, max_length=200)
    location: str
    location_ar: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    rating: float = Field(..., ge=0, le=5, description="Supplier rating (0-5)")
    total_reviews: int = Field(default=0, ge=0)
    delivery_time_days: int = Field(..., ge=1, description="Average delivery time in days")
    products: list[UUID] = Field(default_factory=list)
    phone: str | None = None
    email: str | None = None
    is_verified: bool = False
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"from_attributes": True}


class SupplierSummary(BaseModel):
    """Supplier summary for listings."""

    id: UUID
    name: str
    name_ar: str
    location: str
    rating: float
    delivery_time_days: int
    is_verified: bool


class PurchaseRecommendation(BaseModel):
    """Purchase recommendation from advisory service."""

    id: UUID
    product_id: UUID
    product_name: str
    product_name_ar: str
    quantity: float = Field(..., gt=0)
    unit: str
    field_id: UUID
    reason: str = Field(..., description="Reason for recommendation")
    reason_ar: str = Field(..., description="سبب التوصية")
    priority: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    recommended_by: str = Field(default="advisory-service")
    valid_until: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"from_attributes": True}


class SupplierQuote(BaseModel):
    """Quote from a supplier for a product."""

    id: UUID
    supplier_id: UUID
    supplier_name: str
    supplier_name_ar: str
    product_id: UUID
    product_name: str
    product_name_ar: str
    quantity: float
    unit_price: float = Field(..., ge=0, description="Price per unit in SAR")
    total_price: float = Field(..., ge=0, description="Total price in SAR")
    delivery_days: int = Field(..., ge=1)
    availability: str = Field(..., pattern="^(in_stock|limited|out_of_stock|pre_order)$")
    valid_until: datetime
    notes: str | None = None
    notes_ar: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"from_attributes": True}


class QuoteRequest(BaseModel):
    """Request for quote from supplier."""

    product_id: UUID
    quantity: float = Field(..., gt=0)
    delivery_address: str | None = None


class OrderItem(BaseModel):
    """Order item schema."""

    product_id: UUID
    product_name: str
    product_name_ar: str
    quantity: float = Field(..., gt=0)
    unit: str
    unit_price: float = Field(..., ge=0)
    total_price: float = Field(..., ge=0)

    model_config = {"from_attributes": True}


class OrderItemCreate(BaseModel):
    """Order item creation schema."""

    product_id: UUID
    quantity: float = Field(..., gt=0)


class Order(BaseModel):
    """Order schema."""

    id: UUID
    farmer_id: UUID
    supplier_id: UUID
    supplier_name: str
    supplier_name_ar: str
    status: OrderStatus = OrderStatus.PENDING
    items: list[OrderItem]
    subtotal: float = Field(..., ge=0)
    delivery_fee: float = Field(default=0, ge=0)
    tax: float = Field(default=0, ge=0)
    total: float = Field(..., ge=0)
    delivery_address: str
    delivery_address_ar: str | None = None
    payment_method: PaymentMethod
    payment_status: str = Field(default="pending")
    notes: str | None = None
    notes_ar: str | None = None
    estimated_delivery: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    """Order creation schema."""

    supplier_id: UUID
    items: list[OrderItemCreate] = Field(..., min_length=1)
    delivery_address: str = Field(..., min_length=5)
    delivery_address_ar: str | None = None
    payment_method: PaymentMethod = PaymentMethod.CASH_ON_DELIVERY
    notes: str | None = None
    notes_ar: str | None = None


class DeliveryStatus(BaseModel):
    """Delivery status schema."""

    order_id: UUID
    status: DeliveryStatusEnum
    status_ar: str
    eta: datetime | None = None
    tracking_url: str | None = None
    current_location: str | None = None
    current_location_ar: str | None = None
    driver_name: str | None = None
    driver_phone: str | None = None
    last_update: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"from_attributes": True}


class FarmerProfile(BaseModel):
    """Farmer profile for supply chain."""

    id: UUID
    name: str
    name_ar: str
    phone: str
    email: str | None = None
    address: str
    address_ar: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    preferred_suppliers: list[UUID] = Field(default_factory=list)
    payment_methods: list[PaymentMethod] = Field(default_factory=list)
    total_orders: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"from_attributes": True}


# Auto-purchase schemas
class AutoPurchaseRequest(BaseModel):
    """Auto-purchase request from recommendation."""

    recommendation_id: UUID
    supplier_id: UUID | None = None  # If None, select best supplier
    delivery_address: str | None = None
    payment_method: PaymentMethod = PaymentMethod.CASH_ON_DELIVERY


class SupplierComparison(BaseModel):
    """Supplier comparison for a product."""

    product_id: UUID
    product_name: str
    product_name_ar: str
    quantity: float
    quotes: list[SupplierQuote]
    best_price_supplier_id: UUID | None = None
    fastest_delivery_supplier_id: UUID | None = None
    best_rated_supplier_id: UUID | None = None


class BulkPurchaseItem(BaseModel):
    """Bulk purchase item."""

    product_id: UUID
    quantity: float = Field(..., gt=0)
    supplier_id: UUID | None = None


class BulkPurchaseRequest(BaseModel):
    """Bulk purchase request."""

    items: list[BulkPurchaseItem] = Field(..., min_length=1)
    delivery_address: str
    payment_method: PaymentMethod = PaymentMethod.CASH_ON_DELIVERY
    optimize_for: str = Field(default="price", pattern="^(price|delivery|rating)$")


class BulkPurchaseResult(BaseModel):
    """Bulk purchase result."""

    orders: list[Order]
    total_cost: float
    estimated_savings: float
    optimization_applied: str


# Response schemas
class ProductListResponse(BaseModel):
    """Product list response."""

    items: list[Product]
    total: int
    page: int
    page_size: int


class SupplierListResponse(BaseModel):
    """Supplier list response."""

    items: list[Supplier]
    total: int
    page: int
    page_size: int


class OrderListResponse(BaseModel):
    """Order list response."""

    items: list[Order]
    total: int
    page: int
    page_size: int
