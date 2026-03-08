"""Product endpoints for Supply Chain Service."""

from typing import Optional
from uuid import UUID, uuid4

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query

from ..schemas import Product, ProductCategory, ProductListResponse

# Authentication dependency
try:
    from shared.auth.dependencies import get_current_user
except ImportError:
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

    _bearer_scheme = HTTPBearer(auto_error=False)

    async def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    ):
        """Lightweight auth - validates Authorization header presence."""
        if not credentials:
            raise HTTPException(status_code=401, detail="Authentication required")
        return {"token": credentials.credentials}


logger = structlog.get_logger()

router = APIRouter(prefix="/api/v1/products", tags=["products"])

# Mock product data
MOCK_PRODUCTS: dict[UUID, Product] = {}


def _init_mock_products() -> None:
    """Initialize mock products."""
    if MOCK_PRODUCTS:
        return

    products_data = [
        {
            "name": "Wheat Seeds (Sakha 95)",
            "name_ar": "بذور القمح (سخا 95)",
            "description": "High-yield winter wheat variety",
            "description_ar": "صنف قمح شتوي عالي الإنتاجية",
            "category": ProductCategory.SEEDS,
            "unit": "kg",
            "unit_ar": "كجم",
            "price_min": 25.0,
            "price_max": 35.0,
        },
        {
            "name": "Urea Fertilizer 46%",
            "name_ar": "سماد يوريا 46%",
            "description": "Nitrogen fertilizer for top dressing",
            "description_ar": "سماد نيتروجيني للتسميد السطحي",
            "category": ProductCategory.FERTILIZERS,
            "unit": "kg",
            "unit_ar": "كجم",
            "price_min": 2.5,
            "price_max": 4.0,
        },
        {
            "name": "DAP Fertilizer 18-46-0",
            "name_ar": "سماد DAP 18-46-0",
            "description": "Diammonium phosphate fertilizer",
            "description_ar": "سماد فوسفات ثنائي الأمونيوم",
            "category": ProductCategory.FERTILIZERS,
            "unit": "kg",
            "unit_ar": "كجم",
            "price_min": 3.5,
            "price_max": 5.5,
        },
        {
            "name": "Lambda-cyhalothrin 5%",
            "name_ar": "لامبدا سيهالوثرين 5%",
            "description": "Broad-spectrum insecticide",
            "description_ar": "مبيد حشري واسع الطيف",
            "category": ProductCategory.PESTICIDES,
            "unit": "L",
            "unit_ar": "لتر",
            "price_min": 85.0,
            "price_max": 120.0,
        },
        {
            "name": "Glyphosate 48%",
            "name_ar": "جليفوسات 48%",
            "description": "Non-selective herbicide",
            "description_ar": "مبيد أعشاب غير انتقائي",
            "category": ProductCategory.HERBICIDES,
            "unit": "L",
            "unit_ar": "لتر",
            "price_min": 45.0,
            "price_max": 65.0,
        },
        {
            "name": "Drip Irrigation Kit",
            "name_ar": "طقم الري بالتنقيط",
            "description": "Complete drip irrigation system for 1 hectare",
            "description_ar": "نظام ري بالتنقيط كامل لمساحة هكتار واحد",
            "category": ProductCategory.IRRIGATION,
            "unit": "set",
            "unit_ar": "طقم",
            "price_min": 2500.0,
            "price_max": 4500.0,
        },
        {
            "name": "Sprayer Backpack 16L",
            "name_ar": "رشاشة ظهر 16 لتر",
            "description": "Manual backpack sprayer",
            "description_ar": "رشاشة ظهر يدوية",
            "category": ProductCategory.EQUIPMENT,
            "unit": "pcs",
            "unit_ar": "قطعة",
            "price_min": 150.0,
            "price_max": 250.0,
        },
        {
            "name": "Pruning Shears",
            "name_ar": "مقص تقليم",
            "description": "Professional pruning shears for fruit trees",
            "description_ar": "مقص تقليم احترافي لأشجار الفاكهة",
            "category": ProductCategory.TOOLS,
            "unit": "pcs",
            "unit_ar": "قطعة",
            "price_min": 45.0,
            "price_max": 85.0,
        },
    ]

    for data in products_data:
        product_id = uuid4()
        MOCK_PRODUCTS[product_id] = Product(id=product_id, **data)


@router.get(
    "",
    response_model=ProductListResponse,
    summary="List Products | قائمة المنتجات",
    description="Get a paginated list of available agricultural products. "
    "احصل على قائمة مُرقمة بالمنتجات الزراعية المتاحة.",
)
async def list_products(
    category: ProductCategory | None = Query(None, description="Filter by category"),
    search: str | None = Query(None, description="Search in name"),
    is_available: bool = Query(True, description="Filter by availability"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    _user=Depends(get_current_user),
) -> ProductListResponse:
    """List available products with optional filtering."""
    _init_mock_products()

    logger.info(
        "listing_products",
        category=category,
        search=search,
        page=page,
        page_size=page_size,
    )

    products = list(MOCK_PRODUCTS.values())

    # Apply filters
    if category:
        products = [p for p in products if p.category == category]

    if search:
        search_lower = search.lower()
        products = [p for p in products if search_lower in p.name.lower() or search_lower in p.name_ar]

    if is_available:
        products = [p for p in products if p.is_available]

    # Pagination
    total = len(products)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = products[start:end]

    return ProductListResponse(
        items=paginated,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/search",
    response_model=ProductListResponse,
    summary="Search Products | البحث عن المنتجات",
    description="Search products by name, category, or description. البحث عن المنتجات بالاسم أو الفئة أو الوصف.",
)
async def search_products(
    q: str = Query(..., min_length=2, description="Search query"),
    category: ProductCategory | None = Query(None, description="Filter by category"),
    price_min: float | None = Query(None, ge=0, description="Minimum price"),
    price_max: float | None = Query(None, ge=0, description="Maximum price"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> ProductListResponse:
    """Search products with advanced filters."""
    _init_mock_products()

    logger.info("searching_products", query=q, category=category)

    search_lower = q.lower()
    products = [
        p
        for p in MOCK_PRODUCTS.values()
        if search_lower in p.name.lower()
        or search_lower in p.name_ar
        or (p.description and search_lower in p.description.lower())
        or (p.description_ar and search_lower in p.description_ar)
    ]

    # Apply filters
    if category:
        products = [p for p in products if p.category == category]

    if price_min is not None:
        products = [p for p in products if p.price_max >= price_min]

    if price_max is not None:
        products = [p for p in products if p.price_min <= price_max]

    # Pagination
    total = len(products)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = products[start:end]

    return ProductListResponse(
        items=paginated,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{product_id}",
    response_model=Product,
    summary="Get Product | الحصول على منتج",
    description="Get detailed information about a specific product. الحصول على معلومات تفصيلية عن منتج محدد.",
)
async def get_product(product_id: UUID) -> Product:
    """Get product by ID."""
    _init_mock_products()

    logger.info("getting_product", product_id=str(product_id))

    product = MOCK_PRODUCTS.get(product_id)
    if not product:
        logger.warning("product_not_found", product_id=str(product_id))
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Product not found",
                "message_ar": "المنتج غير موجود",
                "product_id": str(product_id),
            },
        )

    return product
