from .auto_purchase import router as auto_purchase_router
from .orders import router as orders_router
from .products import router as products_router
from .suppliers import router as suppliers_router

__all__ = [
    "products_router",
    "suppliers_router",
    "orders_router",
    "auto_purchase_router",
]
