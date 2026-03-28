"""Order endpoints for Supply Chain Service."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query

from ...core.config import settings
from ..schemas import (
    DeliveryStatus,
    DeliveryStatusEnum,
    Order,
    OrderCreate,
    OrderItem,
    OrderListResponse,
    OrderStatus,
)

# Authentication dependency
try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

    _bearer_scheme = HTTPBearer(auto_error=False)

    async def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    ):
        """Lightweight auth - validates Authorization header presence."""
        if not credentials:
            raise HTTPException(status_code=401, detail="Authentication required")
        return {"token": credentials.credentials, "id": None}


logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])

# Mock order storage
MOCK_ORDERS: dict[UUID, Order] = {}


def _get_current_farmer_id(user=Depends(get_current_user)) -> UUID:
    """Get current farmer ID from authenticated user."""
    user_id = getattr(user, "id", None) or (user.get("id") if isinstance(user, dict) else None)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail={
                "message": "Authentication required",
                "message_ar": "المصادقة مطلوبة",
            },
        )
    return UUID(str(user_id)) if not isinstance(user_id, UUID) else user_id


@router.post(
    "",
    response_model=Order,
    status_code=201,
    summary="Create Order | إنشاء طلب",
    description="Create a new order from a supplier. إنشاء طلب جديد من مورد.",
)
async def create_order(
    order_data: OrderCreate,
    farmer_id: UUID = Depends(_get_current_farmer_id),
) -> Order:
    """Create a new order."""
    logger.info(
        "creating_order",
        farmer_id=str(farmer_id),
        supplier_id=str(order_data.supplier_id),
        items_count=len(order_data.items),
    )

    # Validate item count
    if len(order_data.items) > settings.MAX_ORDER_ITEMS:
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"Maximum {settings.MAX_ORDER_ITEMS} items per order",
                "message_ar": f"الحد الأقصى {settings.MAX_ORDER_ITEMS} عنصر لكل طلب",
            },
        )

    # Build order items with mock prices
    import random

    order_items = []
    subtotal = 0.0

    for item in order_data.items:
        unit_price = round(random.uniform(10, 200), 2)
        total_price = round(unit_price * item.quantity, 2)
        subtotal += total_price

        order_items.append(
            OrderItem(
                product_id=item.product_id,
                product_name="Product Name",
                product_name_ar="اسم المنتج",
                quantity=item.quantity,
                unit="kg",
                unit_price=unit_price,
                total_price=total_price,
            )
        )

    # Calculate totals
    delivery_fee = 50.0 if subtotal < 500 else 0.0  # Free delivery over 500 SAR
    tax = round(subtotal * 0.15, 2)  # 15% VAT
    total = round(subtotal + delivery_fee + tax, 2)

    order = Order(
        id=uuid4(),
        farmer_id=farmer_id,
        supplier_id=order_data.supplier_id,
        supplier_name="Supplier Name",
        supplier_name_ar="اسم المورد",
        status=OrderStatus.PENDING,
        items=order_items,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        tax=tax,
        total=total,
        delivery_address=order_data.delivery_address,
        delivery_address_ar=order_data.delivery_address_ar,
        payment_method=order_data.payment_method,
        payment_status="pending",
        notes=order_data.notes,
        notes_ar=order_data.notes_ar,
        estimated_delivery=datetime.utcnow() + timedelta(days=3),
    )

    MOCK_ORDERS[order.id] = order

    logger.info(
        "order_created",
        order_id=str(order.id),
        total=total,
        items_count=len(order_items),
    )

    return order


@router.get(
    "",
    response_model=OrderListResponse,
    summary="List Orders | قائمة الطلبات",
    description="Get a list of the farmer's orders. الحصول على قائمة طلبات المزارع.",
)
async def list_orders(
    status: OrderStatus | None = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    farmer_id: UUID = Depends(_get_current_farmer_id),
) -> OrderListResponse:
    """List farmer's orders."""
    logger.info(
        "listing_orders",
        farmer_id=str(farmer_id),
        status=status,
    )

    orders = [o for o in MOCK_ORDERS.values() if o.farmer_id == farmer_id]

    # Filter by status
    if status:
        orders = [o for o in orders if o.status == status]

    # Sort by created_at (newest first)
    orders.sort(key=lambda o: o.created_at, reverse=True)

    # Pagination
    total = len(orders)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = orders[start:end]

    return OrderListResponse(
        items=paginated,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{order_id}",
    response_model=Order,
    summary="Get Order | الحصول على طلب",
    description="Get details of a specific order. الحصول على تفاصيل طلب محدد.",
)
async def get_order(
    order_id: UUID,
    farmer_id: UUID = Depends(_get_current_farmer_id),
) -> Order:
    """Get order by ID."""
    logger.info("getting_order", order_id=str(order_id))

    order = MOCK_ORDERS.get(order_id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Order not found",
                "message_ar": "الطلب غير موجود",
            },
        )

    if order.farmer_id != farmer_id:
        raise HTTPException(
            status_code=403,
            detail={
                "message": "Access denied",
                "message_ar": "الوصول مرفوض",
            },
        )

    return order


@router.post(
    "/{order_id}/cancel",
    response_model=Order,
    summary="Cancel Order | إلغاء الطلب",
    description="Cancel a pending order. إلغاء طلب قيد الانتظار.",
)
async def cancel_order(
    order_id: UUID,
    farmer_id: UUID = Depends(_get_current_farmer_id),
) -> Order:
    """Cancel an order."""
    logger.info("cancelling_order", order_id=str(order_id))

    order = MOCK_ORDERS.get(order_id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Order not found",
                "message_ar": "الطلب غير موجود",
            },
        )

    if order.farmer_id != farmer_id:
        raise HTTPException(
            status_code=403,
            detail={
                "message": "Access denied",
                "message_ar": "الوصول مرفوض",
            },
        )

    # Check if order can be cancelled
    if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"Cannot cancel order with status: {order.status.value}",
                "message_ar": f"لا يمكن إلغاء طلب بحالة: {order.status.value}",
            },
        )

    # Update order status
    order.status = OrderStatus.CANCELLED
    order.updated_at = datetime.utcnow()

    logger.info("order_cancelled", order_id=str(order_id))

    return order


@router.get(
    "/{order_id}/track",
    response_model=DeliveryStatus,
    summary="Track Delivery | تتبع التوصيل",
    description="Track the delivery status of an order. تتبع حالة توصيل الطلب.",
)
async def track_order(
    order_id: UUID,
    farmer_id: UUID = Depends(_get_current_farmer_id),
) -> DeliveryStatus:
    """Track order delivery."""
    logger.info("tracking_order", order_id=str(order_id))

    order = MOCK_ORDERS.get(order_id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Order not found",
                "message_ar": "الطلب غير موجود",
            },
        )

    if order.farmer_id != farmer_id:
        raise HTTPException(
            status_code=403,
            detail={
                "message": "Access denied",
                "message_ar": "الوصول مرفوض",
            },
        )

    # Map order status to delivery status
    status_mapping = {
        OrderStatus.PENDING: DeliveryStatusEnum.PREPARING,
        OrderStatus.CONFIRMED: DeliveryStatusEnum.PREPARING,
        OrderStatus.PROCESSING: DeliveryStatusEnum.PICKED_UP,
        OrderStatus.SHIPPED: DeliveryStatusEnum.IN_TRANSIT,
        OrderStatus.DELIVERED: DeliveryStatusEnum.DELIVERED,
        OrderStatus.CANCELLED: DeliveryStatusEnum.FAILED,
    }

    status_ar_mapping = {
        DeliveryStatusEnum.PREPARING: "جاري التحضير",
        DeliveryStatusEnum.PICKED_UP: "تم الاستلام",
        DeliveryStatusEnum.IN_TRANSIT: "في الطريق",
        DeliveryStatusEnum.OUT_FOR_DELIVERY: "خارج للتوصيل",
        DeliveryStatusEnum.DELIVERED: "تم التوصيل",
        DeliveryStatusEnum.FAILED: "فشل التوصيل",
    }

    delivery_status = status_mapping.get(order.status, DeliveryStatusEnum.PREPARING)

    return DeliveryStatus(
        order_id=order_id,
        status=delivery_status,
        status_ar=status_ar_mapping.get(delivery_status, "غير معروف"),
        eta=order.estimated_delivery,
        tracking_url=f"https://delivery.sahool.local/track/{order_id}",
        current_location="Warehouse" if delivery_status == DeliveryStatusEnum.PREPARING else "In Transit",
        current_location_ar="المستودع" if delivery_status == DeliveryStatusEnum.PREPARING else "في الطريق",
    )
