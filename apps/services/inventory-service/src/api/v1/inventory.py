"""
Inventory CRUD endpoints - Wave 2.
نقاط نهاية المخزون CRUD - الموجة الثانية.

Implements the core inventory item lifecycle used by the admin portal:
- CRUD with soft delete
- Optimistic locking (version field)
- Stock adjustments with transactional ledger
- Paginated list with filters
- Summary stats

All endpoints derive ``tenant_id`` from the authenticated JWT user (``tid``
claim via ``shared.auth.dependencies.get_current_user``) and NEVER from a
header or query param. Bilingual (AR/EN) error messages are returned on
conflicts.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import and_, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.inventory_v2 import InventoryItemV2, InventoryTransactionV2

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/inventory", tags=["inventory"])


# ---------------------------------------------------------------------------
# Allowed transaction types - أنواع المعاملات المسموح بها
# ---------------------------------------------------------------------------
ALLOWED_TRANSACTION_TYPES = {
    "purchase",
    "sale",
    "adjustment",
    "transfer",
    "consumption",
}

MAX_PAGE_LIMIT = 200


# ---------------------------------------------------------------------------
# Pydantic schemas - مخططات التحقق
# ---------------------------------------------------------------------------
class InventoryItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    name_ar: str | None = Field(None, max_length=200)
    sku: str | None = Field(None, max_length=120)
    category: str | None = Field(None, max_length=120)
    quantity: Decimal = Field(Decimal("0"), ge=Decimal("0"))
    unit: str = Field(..., min_length=1, max_length=32)
    unit_price: Decimal | None = Field(None, ge=Decimal("0"))
    currency: str = Field("SAR", max_length=8)
    low_stock_threshold: Decimal | None = Field(None, ge=Decimal("0"))
    supplier_id: str | None = None
    location: str | None = Field(None, max_length=200)


class InventoryItemUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    name_ar: str | None = Field(None, max_length=200)
    sku: str | None = Field(None, max_length=120)
    category: str | None = Field(None, max_length=120)
    unit: str | None = Field(None, min_length=1, max_length=32)
    unit_price: Decimal | None = Field(None, ge=Decimal("0"))
    currency: str | None = Field(None, max_length=8)
    low_stock_threshold: Decimal | None = Field(None, ge=Decimal("0"))
    supplier_id: str | None = None
    location: str | None = Field(None, max_length=200)

    # Optimistic concurrency control: caller asserts the version they hold.
    if_match_version: int | None = Field(None, ge=1)


class InventoryItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    name: str
    name_ar: str | None
    sku: str | None
    category: str | None
    quantity: Decimal
    unit: str
    unit_price: Decimal | None
    currency: str
    low_stock_threshold: Decimal | None
    supplier_id: str | None
    location: str | None
    created_at: datetime
    updated_at: datetime
    version: int


class PaginationMeta(BaseModel):
    total: int
    page: int
    limit: int


class InventoryItemList(BaseModel):
    items: list[InventoryItemResponse]
    pagination: PaginationMeta


class InventoryAdjustRequest(BaseModel):
    delta: Decimal = Field(..., description="Signed quantity change. Positive = add, negative = remove.")
    reason: str = Field(..., min_length=1, max_length=500)
    transaction_type: str = Field("adjustment")
    if_match_version: int | None = Field(None, ge=1)

    @field_validator("transaction_type")
    @classmethod
    def _validate_tx_type(cls, value: str) -> str:
        normalized = value.lower().strip()
        if normalized not in ALLOWED_TRANSACTION_TYPES:
            raise ValueError(f"transaction_type must be one of {sorted(ALLOWED_TRANSACTION_TYPES)}")
        return normalized


class InventoryTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    tenant_id: str
    item_id: str
    transaction_type: str
    quantity_delta: Decimal
    quantity_after: Decimal
    reason: str | None
    performed_by: str | None
    created_at: datetime


class InventoryTransactionList(BaseModel):
    transactions: list[InventoryTransactionResponse]
    pagination: PaginationMeta


class InventoryStats(BaseModel):
    total_items: int
    total_quantity: Decimal
    total_value: Decimal
    low_stock_count: int
    out_of_stock_count: int
    categories: int


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _bilingual_detail(en: str, ar: str, code: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"message": en, "message_ar": ar}
    if code:
        payload["code"] = code
    return payload


def _require_tenant_id(user: Any) -> str:
    """Extract tenant_id strictly from the authenticated user (JWT ``tid``)."""
    tenant_id = getattr(user, "tenant_id", None) if user is not None else None
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_bilingual_detail(
                "Tenant context missing from credentials",
                "سياق المستأجر مفقود من بيانات الاعتماد",
                code="E8001",
            ),
        )
    return str(tenant_id)


def _require_user_id(user: Any) -> str | None:
    if user is None:
        return None
    uid = getattr(user, "id", None)
    return str(uid) if uid is not None else None


def _parse_item_id(raw_id: str) -> str:
    try:
        return str(uuid.UUID(str(raw_id)))
    except (ValueError, AttributeError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_bilingual_detail(
                "Invalid item id format (expected UUID)",
                "تنسيق معرف الصنف غير صالح (مطلوب UUID)",
                code="E1002",
            ),
        ) from exc


def _item_to_response(item: InventoryItemV2) -> InventoryItemResponse:
    return InventoryItemResponse(
        id=str(item.id),
        tenant_id=str(item.tenant_id),
        name=item.name,
        name_ar=item.name_ar,
        sku=item.sku,
        category=item.category,
        quantity=Decimal(str(item.quantity)),
        unit=item.unit,
        unit_price=Decimal(str(item.unit_price)) if item.unit_price is not None else None,
        currency=item.currency or "SAR",
        low_stock_threshold=(Decimal(str(item.low_stock_threshold)) if item.low_stock_threshold is not None else None),
        supplier_id=item.supplier_id,
        location=item.location,
        created_at=item.created_at,
        updated_at=item.updated_at,
        version=item.version,
    )


def _txn_to_response(txn: InventoryTransactionV2) -> InventoryTransactionResponse:
    return InventoryTransactionResponse(
        id=str(txn.id),
        tenant_id=str(txn.tenant_id),
        item_id=str(txn.item_id),
        transaction_type=txn.transaction_type,
        quantity_delta=Decimal(str(txn.quantity_delta)),
        quantity_after=Decimal(str(txn.quantity_after)),
        reason=txn.reason,
        performed_by=txn.performed_by,
        created_at=txn.created_at,
    )


async def _load_item_for_tenant(db: AsyncSession, item_id: str, tenant_id: str) -> InventoryItemV2:
    stmt = select(InventoryItemV2).where(
        InventoryItemV2.id == item_id,
        InventoryItemV2.tenant_id == tenant_id,
        InventoryItemV2.is_deleted.is_(False),
    )
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_bilingual_detail(
                "Inventory item not found",
                "الصنف غير موجود",
                code="E1004",
            ),
        )
    return item


# ---------------------------------------------------------------------------
# Dependency wiring - lazy import of get_db / get_current_user via
# importlib so this module can be imported before the main application
# defines them, AND so static analyzers (CodeQL) don't see a textual
# circular import between `src.main` and `src.api.v1.inventory`.
# ---------------------------------------------------------------------------
def _get_db_dependency():
    import importlib

    return importlib.import_module("src.main").get_db


def _get_user_dependency():
    import importlib

    return importlib.import_module("src.main").get_current_user


async def get_db_session() -> AsyncSession:  # pragma: no cover - thin wrapper
    dep = _get_db_dependency()
    async for session in dep():
        yield session


async def get_user():  # pragma: no cover - thin wrapper
    dep = _get_user_dependency()
    result = dep()
    if hasattr(result, "__await__"):
        return await result
    return result


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@router.post(
    "",
    response_model=InventoryItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_inventory_item(
    payload: InventoryItemCreate,
    db: AsyncSession = Depends(get_db_session),
    user: Any = Depends(get_user),
) -> InventoryItemResponse:
    """Create a new inventory item scoped to the caller's tenant."""
    tenant_id = _require_tenant_id(user)

    item = InventoryItemV2(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        name=payload.name,
        name_ar=payload.name_ar,
        sku=payload.sku,
        category=payload.category,
        quantity=payload.quantity,
        unit=payload.unit,
        unit_price=payload.unit_price,
        currency=payload.currency or "SAR",
        low_stock_threshold=payload.low_stock_threshold,
        supplier_id=payload.supplier_id,
        location=payload.location,
        is_deleted=False,
        version=1,
    )
    db.add(item)
    try:
        await db.flush()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_bilingual_detail(
                "SKU already exists for this tenant",
                "رمز SKU موجود بالفعل لهذا المستأجر",
                code="E1003",
            ),
        ) from exc
    await db.refresh(item)
    return _item_to_response(item)


@router.get("/stats", response_model=InventoryStats)
async def get_inventory_stats(
    db: AsyncSession = Depends(get_db_session),
    user: Any = Depends(get_user),
) -> InventoryStats:
    """Return summary statistics for the caller's tenant."""
    tenant_id = _require_tenant_id(user)

    base = and_(
        InventoryItemV2.tenant_id == tenant_id,
        InventoryItemV2.is_deleted.is_(False),
    )

    total_items_result = await db.execute(select(func.count(InventoryItemV2.id)).where(base))
    total_items = int(total_items_result.scalar() or 0)

    total_qty_result = await db.execute(select(func.coalesce(func.sum(InventoryItemV2.quantity), 0)).where(base))
    total_quantity = Decimal(str(total_qty_result.scalar() or 0))

    total_value_result = await db.execute(
        select(func.coalesce(func.sum(InventoryItemV2.quantity * InventoryItemV2.unit_price), 0)).where(base)
    )
    try:
        total_value = Decimal(str(total_value_result.scalar() or 0))
    except (InvalidOperation, TypeError):  # pragma: no cover - defensive
        total_value = Decimal("0")

    low_stock_result = await db.execute(
        select(func.count(InventoryItemV2.id)).where(
            base,
            InventoryItemV2.low_stock_threshold.isnot(None),
            InventoryItemV2.quantity <= InventoryItemV2.low_stock_threshold,
            InventoryItemV2.quantity > 0,
        )
    )
    low_stock_count = int(low_stock_result.scalar() or 0)

    out_of_stock_result = await db.execute(
        select(func.count(InventoryItemV2.id)).where(base, InventoryItemV2.quantity <= 0)
    )
    out_of_stock_count = int(out_of_stock_result.scalar() or 0)

    categories_result = await db.execute(
        select(func.count(func.distinct(InventoryItemV2.category))).where(base, InventoryItemV2.category.isnot(None))
    )
    categories = int(categories_result.scalar() or 0)

    return InventoryStats(
        total_items=total_items,
        total_quantity=total_quantity,
        total_value=total_value,
        low_stock_count=low_stock_count,
        out_of_stock_count=out_of_stock_count,
        categories=categories,
    )


@router.get("/transactions", response_model=InventoryTransactionList)
async def list_inventory_transactions(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=MAX_PAGE_LIMIT),
    item_id: str | None = Query(None),
    transaction_type: str | None = Query(None),
    db: AsyncSession = Depends(get_db_session),
    user: Any = Depends(get_user),
) -> InventoryTransactionList:
    """Return the inventory transaction history for the caller's tenant."""
    tenant_id = _require_tenant_id(user)

    filters = [InventoryTransactionV2.tenant_id == tenant_id]
    if item_id:
        filters.append(InventoryTransactionV2.item_id == _parse_item_id(item_id))
    if transaction_type:
        normalized = transaction_type.lower().strip()
        if normalized not in ALLOWED_TRANSACTION_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=_bilingual_detail(
                    f"transaction_type must be one of {sorted(ALLOWED_TRANSACTION_TYPES)}",
                    "نوع المعاملة يجب أن يكون أحد القيم المسموح بها",
                    code="E1002",
                ),
            )
        filters.append(InventoryTransactionV2.transaction_type == normalized)

    count_stmt = select(func.count(InventoryTransactionV2.id)).where(*filters)
    total = int((await db.execute(count_stmt)).scalar() or 0)

    offset = (page - 1) * limit
    rows_stmt = (
        select(InventoryTransactionV2)
        .where(*filters)
        .order_by(InventoryTransactionV2.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(rows_stmt)
    transactions = [_txn_to_response(t) for t in result.scalars().all()]

    return InventoryTransactionList(
        transactions=transactions,
        pagination=PaginationMeta(total=total, page=page, limit=limit),
    )


@router.get("", response_model=InventoryItemList)
async def list_inventory_items(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=MAX_PAGE_LIMIT),
    category: str | None = Query(None),
    search: str | None = Query(None, max_length=200),
    db: AsyncSession = Depends(get_db_session),
    user: Any = Depends(get_user),
) -> InventoryItemList:
    """List inventory items with pagination and basic filters."""
    tenant_id = _require_tenant_id(user)

    filters = [
        InventoryItemV2.tenant_id == tenant_id,
        InventoryItemV2.is_deleted.is_(False),
    ]
    if category:
        filters.append(InventoryItemV2.category == category)
    if search:
        like = f"%{search.strip()}%"
        filters.append(
            (InventoryItemV2.name.ilike(like))
            | (InventoryItemV2.name_ar.ilike(like))
            | (InventoryItemV2.sku.ilike(like))
        )

    total_stmt = select(func.count(InventoryItemV2.id)).where(*filters)
    total = int((await db.execute(total_stmt)).scalar() or 0)

    offset = (page - 1) * limit
    items_stmt = (
        select(InventoryItemV2).where(*filters).order_by(InventoryItemV2.created_at.desc()).offset(offset).limit(limit)
    )
    result = await db.execute(items_stmt)
    items = [_item_to_response(i) for i in result.scalars().all()]

    return InventoryItemList(
        items=items,
        pagination=PaginationMeta(total=total, page=page, limit=limit),
    )


@router.get("/{item_id}", response_model=InventoryItemResponse)
async def get_inventory_item(
    item_id: str,
    db: AsyncSession = Depends(get_db_session),
    user: Any = Depends(get_user),
) -> InventoryItemResponse:
    """Fetch a single inventory item by id."""
    tenant_id = _require_tenant_id(user)
    parsed_id = _parse_item_id(item_id)
    item = await _load_item_for_tenant(db, parsed_id, tenant_id)
    return _item_to_response(item)


@router.put("/{item_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    item_id: str,
    payload: InventoryItemUpdate,
    db: AsyncSession = Depends(get_db_session),
    user: Any = Depends(get_user),
) -> InventoryItemResponse:
    """
    Update an inventory item with optimistic locking.

    The caller MUST supply ``if_match_version`` matching the currently stored
    ``version`` field. On mismatch the server returns 409 Conflict and the
    client is expected to refetch + retry.
    """
    tenant_id = _require_tenant_id(user)
    parsed_id = _parse_item_id(item_id)

    item = await _load_item_for_tenant(db, parsed_id, tenant_id)

    if payload.if_match_version is not None and payload.if_match_version != item.version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_bilingual_detail(
                f"Version conflict: expected {payload.if_match_version}, current {item.version}",
                f"تعارض في الإصدار: متوقع {payload.if_match_version}, الحالي {item.version}",
                code="E1005",
            ),
        )

    update_data = payload.model_dump(exclude_unset=True, exclude={"if_match_version"})
    for key, value in update_data.items():
        setattr(item, key, value)
    item.version = item.version + 1
    item.updated_at = datetime.utcnow()

    try:
        await db.flush()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_bilingual_detail(
                "SKU already exists for this tenant",
                "رمز SKU موجود بالفعل لهذا المستأجر",
                code="E1003",
            ),
        ) from exc

    await db.refresh(item)
    return _item_to_response(item)


@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
async def delete_inventory_item(
    item_id: str,
    db: AsyncSession = Depends(get_db_session),
    user: Any = Depends(get_user),
) -> dict[str, Any]:
    """Soft-delete an inventory item (sets ``is_deleted = TRUE``)."""
    tenant_id = _require_tenant_id(user)
    parsed_id = _parse_item_id(item_id)
    item = await _load_item_for_tenant(db, parsed_id, tenant_id)

    item.is_deleted = True
    item.version = item.version + 1
    item.updated_at = datetime.utcnow()
    await db.flush()

    return {
        "id": str(item.id),
        "deleted": True,
        "message": "Inventory item soft-deleted",
        "message_ar": "تم حذف الصنف بشكل ناعم",
    }


@router.post("/{item_id}/adjust", response_model=InventoryItemResponse)
async def adjust_inventory_item(
    item_id: str,
    payload: InventoryAdjustRequest,
    db: AsyncSession = Depends(get_db_session),
    user: Any = Depends(get_user),
) -> InventoryItemResponse:
    """
    Adjust stock for an item and append a transaction ledger row.

    The whole operation runs inside a single DB transaction:

    1. Load + lock the item (``SELECT ... FOR UPDATE`` on PostgreSQL; a
       no-op on SQLite used by tests, which is single-writer anyway).
    2. Check optimistic lock if ``if_match_version`` is provided.
    3. Validate ``quantity + delta >= 0``.
    4. Update item and insert a row into ``inventory_transactions_v2``.
    """
    tenant_id = _require_tenant_id(user)
    parsed_id = _parse_item_id(item_id)

    # Step 1: load & lock the row. with_for_update is ignored on sqlite.
    stmt = (
        select(InventoryItemV2)
        .where(
            InventoryItemV2.id == parsed_id,
            InventoryItemV2.tenant_id == tenant_id,
            InventoryItemV2.is_deleted.is_(False),
        )
        .with_for_update()
    )
    try:
        result = await db.execute(stmt)
    except Exception:  # pragma: no cover - sqlite lacks FOR UPDATE
        stmt_no_lock = select(InventoryItemV2).where(
            InventoryItemV2.id == parsed_id,
            InventoryItemV2.tenant_id == tenant_id,
            InventoryItemV2.is_deleted.is_(False),
        )
        result = await db.execute(stmt_no_lock)

    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_bilingual_detail(
                "Inventory item not found",
                "الصنف غير موجود",
                code="E1004",
            ),
        )

    # Step 2: optimistic lock check
    if payload.if_match_version is not None and payload.if_match_version != item.version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_bilingual_detail(
                f"Version conflict: expected {payload.if_match_version}, current {item.version}",
                f"تعارض في الإصدار: متوقع {payload.if_match_version}, الحالي {item.version}",
                code="E1005",
            ),
        )

    # Step 3: arithmetic & validation
    current_qty = Decimal(str(item.quantity))
    delta = Decimal(str(payload.delta))
    new_qty = current_qty + delta
    if new_qty < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_bilingual_detail(
                f"Adjustment would result in negative stock: {new_qty}",
                f"التعديل سيؤدي إلى مخزون سالب: {new_qty}",
                code="E1006",
            ),
        )

    item.quantity = new_qty
    item.version = item.version + 1
    item.updated_at = datetime.utcnow()

    txn = InventoryTransactionV2(
        id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        item_id=str(item.id),
        transaction_type=payload.transaction_type,
        quantity_delta=delta,
        quantity_after=new_qty,
        reason=payload.reason,
        performed_by=_require_user_id(user),
    )
    db.add(txn)

    await db.flush()
    await db.refresh(item)
    return _item_to_response(item)
