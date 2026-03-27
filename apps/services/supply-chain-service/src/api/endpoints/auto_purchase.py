"""Auto-purchase endpoints for Supply Chain Service."""

from datetime import datetime, timedelta
from uuid import UUID, uuid4

import structlog
from fastapi import APIRouter, Depends, HTTPException

from ...core.config import settings
from ...suppliers.finder import SupplierFinder
from ..schemas import (
    AutoPurchaseRequest,
    BulkPurchaseRequest,
    BulkPurchaseResult,
    Order,
    OrderItem,
    OrderStatus,
    PaymentMethod,
    SupplierComparison,
    SupplierQuote,
)

logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/auto-purchase", tags=["auto-purchase"])

# Mock storage
MOCK_ORDERS: dict[UUID, Order] = {}
MOCK_RECOMMENDATIONS: dict[UUID, dict] = {}


def _get_current_farmer_id() -> UUID:
    """Get current farmer ID (mock)."""
    return UUID("12345678-1234-1234-1234-123456789abc")


def _init_mock_recommendations() -> None:
    """Initialize mock recommendations."""
    if MOCK_RECOMMENDATIONS:
        return

    rec_id = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    MOCK_RECOMMENDATIONS[rec_id] = {
        "id": rec_id,
        "product_id": UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        "product_name": "Urea Fertilizer 46%",
        "product_name_ar": "سماد يوريا 46%",
        "quantity": 100.0,
        "unit": "kg",
        "field_id": UUID("cccccccc-cccc-cccc-cccc-cccccccccccc"),
        "reason": "Nitrogen deficiency detected in wheat field",
        "reason_ar": "تم اكتشاف نقص النيتروجين في حقل القمح",
        "priority": "high",
        "valid_until": datetime.utcnow() + timedelta(days=7),
    }


@router.post(
    "",
    response_model=Order,
    status_code=201,
    summary="Auto-Purchase from Recommendation | الشراء التلقائي من التوصية",
    description="Automatically create an order based on an advisory recommendation. "
    "إنشاء طلب تلقائياً بناءً على توصية استشارية.",
)
async def auto_purchase(
    request: AutoPurchaseRequest,
    farmer_id: UUID = Depends(_get_current_farmer_id),
) -> Order:
    """Create order from recommendation."""
    _init_mock_recommendations()

    if not settings.AUTO_PURCHASE_ENABLED:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "Auto-purchase is currently disabled",
                "message_ar": "الشراء التلقائي معطل حالياً",
            },
        )

    logger.info(
        "auto_purchase_request",
        recommendation_id=str(request.recommendation_id),
        supplier_id=str(request.supplier_id) if request.supplier_id else None,
    )

    # Get recommendation
    recommendation = MOCK_RECOMMENDATIONS.get(request.recommendation_id)
    if not recommendation:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Recommendation not found",
                "message_ar": "التوصية غير موجودة",
            },
        )

    # Check validity
    if recommendation["valid_until"] < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Recommendation has expired",
                "message_ar": "انتهت صلاحية التوصية",
            },
        )

    # Find best supplier if not specified
    supplier_id = request.supplier_id
    if not supplier_id:
        finder = SupplierFinder()
        best_supplier = await finder.find_best_supplier(
            product_id=recommendation["product_id"],
            quantity=recommendation["quantity"],
            optimize_for="price",
        )
        if best_supplier:
            supplier_id = best_supplier["supplier_id"]
        else:
            raise HTTPException(
                status_code=404,
                detail={
                    "message": "No suitable supplier found",
                    "message_ar": "لم يتم العثور على مورد مناسب",
                },
            )

    # Calculate prices
    import random

    unit_price = round(random.uniform(2.5, 4.0), 2)
    quantity = recommendation["quantity"]
    total_price = round(unit_price * quantity, 2)

    order_item = OrderItem(
        product_id=recommendation["product_id"],
        product_name=recommendation["product_name"],
        product_name_ar=recommendation["product_name_ar"],
        quantity=quantity,
        unit=recommendation["unit"],
        unit_price=unit_price,
        total_price=total_price,
    )

    # Calculate totals
    subtotal = total_price
    delivery_fee = 50.0 if subtotal < 500 else 0.0
    tax = round(subtotal * 0.15, 2)
    total = round(subtotal + delivery_fee + tax, 2)

    order = Order(
        id=uuid4(),
        farmer_id=farmer_id,
        supplier_id=supplier_id,
        supplier_name="Auto-selected Supplier",
        supplier_name_ar="مورد محدد تلقائياً",
        status=OrderStatus.CONFIRMED,
        items=[order_item],
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        tax=tax,
        total=total,
        delivery_address=request.delivery_address or "Default Farm Address",
        payment_method=request.payment_method,
        payment_status="pending",
        notes=f"Auto-purchase from recommendation {request.recommendation_id}",
        notes_ar=f"شراء تلقائي من التوصية {request.recommendation_id}",
        estimated_delivery=datetime.utcnow() + timedelta(days=2),
    )

    MOCK_ORDERS[order.id] = order

    logger.info(
        "auto_purchase_completed",
        order_id=str(order.id),
        recommendation_id=str(request.recommendation_id),
        total=total,
    )

    return order


@router.post(
    "/compare",
    response_model=SupplierComparison,
    summary="Compare Suppliers | مقارنة الموردين",
    description="Compare quotes from multiple suppliers for a product. مقارنة عروض الأسعار من موردين متعددين لمنتج.",
)
async def compare_suppliers(
    product_id: UUID,
    quantity: float,
) -> SupplierComparison:
    """Compare suppliers for a product."""
    logger.info(
        "comparing_suppliers",
        product_id=str(product_id),
        quantity=quantity,
    )

    finder = SupplierFinder()
    quotes = await finder.get_quotes(product_id, quantity)

    if not quotes:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "No suppliers found for this product",
                "message_ar": "لم يتم العثور على موردين لهذا المنتج",
            },
        )

    # Convert to SupplierQuote objects
    quote_objects = []
    for q in quotes:
        quote_objects.append(
            SupplierQuote(
                id=uuid4(),
                supplier_id=q["supplier_id"],
                supplier_name=q["supplier_name"],
                supplier_name_ar=q["supplier_name_ar"],
                product_id=product_id,
                product_name="Product Name",
                product_name_ar="اسم المنتج",
                quantity=quantity,
                unit_price=q["unit_price"],
                total_price=q["total_price"],
                delivery_days=q["delivery_days"],
                availability=q["availability"],
                valid_until=datetime.utcnow() + timedelta(hours=24),
            )
        )

    # Find best options
    best_price = min(quote_objects, key=lambda q: q.total_price)
    fastest = min(quote_objects, key=lambda q: q.delivery_days)

    return SupplierComparison(
        product_id=product_id,
        product_name="Product Name",
        product_name_ar="اسم المنتج",
        quantity=quantity,
        quotes=quote_objects,
        best_price_supplier_id=best_price.supplier_id,
        fastest_delivery_supplier_id=fastest.supplier_id,
    )


@router.post(
    "/bulk",
    response_model=BulkPurchaseResult,
    status_code=201,
    summary="Bulk Purchase | شراء بالجملة",
    description="Purchase multiple items at once with optimization. شراء عناصر متعددة مرة واحدة مع التحسين.",
)
async def bulk_purchase(
    request: BulkPurchaseRequest,
    farmer_id: UUID = Depends(_get_current_farmer_id),
) -> BulkPurchaseResult:
    """Create bulk purchase orders."""
    if not settings.AUTO_PURCHASE_ENABLED:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "Auto-purchase is currently disabled",
                "message_ar": "الشراء التلقائي معطل حالياً",
            },
        )

    logger.info(
        "bulk_purchase_request",
        items_count=len(request.items),
        optimize_for=request.optimize_for,
    )

    finder = SupplierFinder()
    orders = []
    total_cost = 0.0
    regular_cost = 0.0

    # Group items by supplier for optimization
    supplier_items: dict[UUID, list] = {}

    for item in request.items:
        if item.supplier_id:
            supplier_id = item.supplier_id
        else:
            # Find best supplier based on optimization preference
            best = await finder.find_best_supplier(
                product_id=item.product_id,
                quantity=item.quantity,
                optimize_for=request.optimize_for,
            )
            supplier_id = best["supplier_id"] if best else uuid4()

        if supplier_id not in supplier_items:
            supplier_items[supplier_id] = []
        supplier_items[supplier_id].append(item)

    # Create order for each supplier
    for supplier_id, items in supplier_items.items():
        import random

        order_items = []
        subtotal = 0.0

        for item in items:
            unit_price = round(random.uniform(10, 100), 2)
            item_total = round(unit_price * item.quantity, 2)
            subtotal += item_total
            regular_cost += item_total * 1.1  # 10% higher for comparison

            order_items.append(
                OrderItem(
                    product_id=item.product_id,
                    product_name="Bulk Item",
                    product_name_ar="عنصر بالجملة",
                    quantity=item.quantity,
                    unit="kg",
                    unit_price=unit_price,
                    total_price=item_total,
                )
            )

        delivery_fee = 0.0  # Free delivery for bulk
        tax = round(subtotal * 0.15, 2)
        total = round(subtotal + tax, 2)
        total_cost += total

        order = Order(
            id=uuid4(),
            farmer_id=farmer_id,
            supplier_id=supplier_id,
            supplier_name="Bulk Supplier",
            supplier_name_ar="مورد الجملة",
            status=OrderStatus.CONFIRMED,
            items=order_items,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            tax=tax,
            total=total,
            delivery_address=request.delivery_address,
            payment_method=request.payment_method,
            payment_status="pending",
            notes="Bulk purchase order",
            notes_ar="طلب شراء بالجملة",
            estimated_delivery=datetime.utcnow() + timedelta(days=3),
        )

        MOCK_ORDERS[order.id] = order
        orders.append(order)

    estimated_savings = round(regular_cost - total_cost, 2)

    logger.info(
        "bulk_purchase_completed",
        orders_count=len(orders),
        total_cost=total_cost,
        estimated_savings=estimated_savings,
    )

    return BulkPurchaseResult(
        orders=orders,
        total_cost=total_cost,
        estimated_savings=max(0, estimated_savings),
        optimization_applied=request.optimize_for,
    )
