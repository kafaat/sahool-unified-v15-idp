"""
Database Pagination and Streaming Utilities
أدوات التقسيم والبث لقاعدة البيانات

Provides utilities for:
1. Cursor-based pagination (for large datasets)
2. Offset-based pagination (for smaller datasets)
3. Response streaming (for very large results)
4. Query optimization helpers
"""

import base64
import json
from collections.abc import AsyncIterator
from dataclasses import dataclass
from enum import Enum
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class SortOrder(str, Enum):
    """Sort order options"""

    ASC = "asc"
    DESC = "desc"


@dataclass
class PageInfo:
    """Page information for cursor-based pagination"""

    has_next_page: bool
    has_previous_page: bool
    start_cursor: str | None = None
    end_cursor: str | None = None
    total_count: int | None = None


@dataclass
class Page(Generic[T]):
    """Generic paginated response"""

    items: list[T]
    page_info: PageInfo

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "items": [item.dict() if hasattr(item, "dict") else item for item in self.items],
            "page_info": {
                "has_next_page": self.page_info.has_next_page,
                "has_previous_page": self.page_info.has_previous_page,
                "start_cursor": self.page_info.start_cursor,
                "end_cursor": self.page_info.end_cursor,
                "total_count": self.page_info.total_count,
            },
        }


@dataclass
class OffsetPage(Generic[T]):
    """Offset-based paginated response"""

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "items": [item.dict() if hasattr(item, "dict") else item for item in self.items],
            "pagination": {
                "total": self.total,
                "page": self.page,
                "page_size": self.page_size,
                "total_pages": self.total_pages,
                "has_next": self.page < self.total_pages,
                "has_previous": self.page > 1,
            },
        }


class Cursor:
    """Cursor for cursor-based pagination"""

    @staticmethod
    def encode(value: Any) -> str:
        """
        Encode a value as a cursor.
        تشفير قيمة كمؤشر.

        Args:
            value: Value to encode (typically an ID or timestamp)

        Returns:
            Base64-encoded cursor string
        """
        json_str = json.dumps(value)
        return base64.b64encode(json_str.encode()).decode()

    @staticmethod
    def decode(cursor: str) -> Any:
        """
        Decode a cursor value.
        فك تشفير قيمة المؤشر.

        Args:
            cursor: Base64-encoded cursor string

        Returns:
            Decoded value
        """
        try:
            json_str = base64.b64decode(cursor.encode()).decode()
            return json.loads(json_str)
        except Exception:
            return None


class PaginationHelper:
    """
    Helper for implementing pagination in queries.
    مساعد لتنفيذ التقسيم في الاستعلامات.
    """

    @staticmethod
    def get_page_size(requested_size: int | None, default: int = 50, max_size: int = 1000) -> int:
        """
        Get validated page size.
        الحصول على حجم الصفحة المتحقق منه.

        Args:
            requested_size: Requested page size
            default: Default page size
            max_size: Maximum allowed page size

        Returns:
            Validated page size
        """
        if requested_size is None:
            return default

        return min(max(1, requested_size), max_size)

    @staticmethod
    def calculate_offset(page: int, page_size: int) -> int:
        """
        Calculate offset from page number.
        حساب الإزاحة من رقم الصفحة.

        Args:
            page: Page number (1-indexed)
            page_size: Items per page

        Returns:
            Offset value
        """
        return (max(1, page) - 1) * page_size

    @staticmethod
    def calculate_total_pages(total_items: int, page_size: int) -> int:
        """
        Calculate total number of pages.
        حساب العدد الإجمالي للصفحات.

        Args:
            total_items: Total number of items
            page_size: Items per page

        Returns:
            Total number of pages
        """
        if page_size <= 0:
            return 0
        return (total_items + page_size - 1) // page_size


# SQLAlchemy pagination helpers
class SQLAlchemyPagination:
    """
    SQLAlchemy-specific pagination helpers.
    مساعدو التقسيم الخاصة بـ SQLAlchemy.
    """

    @staticmethod
    async def paginate_query(
        query,
        page: int = 1,
        page_size: int = 50,
        max_page_size: int = 1000,
    ) -> OffsetPage:
        """
        Paginate a SQLAlchemy query with offset-based pagination.
        تقسيم استعلام SQLAlchemy بتقسيم قائم على الإزاحة.

        Args:
            query: SQLAlchemy query object
            page: Page number (1-indexed)
            page_size: Items per page
            max_page_size: Maximum allowed page size

        Returns:
            OffsetPage with results
        """
        # Validate page size
        page_size = PaginationHelper.get_page_size(page_size, max_size=max_page_size)

        # Calculate offset
        offset = PaginationHelper.calculate_offset(page, page_size)

        # Get total count
        total = await query.count()

        # Get items
        items = await query.offset(offset).limit(page_size).all()

        # Calculate total pages
        total_pages = PaginationHelper.calculate_total_pages(total, page_size)

        return OffsetPage(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    @staticmethod
    async def cursor_paginate_query(
        query,
        cursor_field: str,
        first: int | None = None,
        after: str | None = None,
        last: int | None = None,
        before: str | None = None,
        order_by: SortOrder = SortOrder.ASC,
        max_page_size: int = 1000,
    ) -> Page:
        """
        Paginate a SQLAlchemy query with cursor-based pagination.
        تقسيم استعلام SQLAlchemy بتقسيم قائم على المؤشر.

        Args:
            query: SQLAlchemy query object
            cursor_field: Field to use for cursor (e.g., 'id', 'created_at')
            first: Get first N items (forward pagination)
            after: Get items after this cursor
            last: Get last N items (backward pagination)
            before: Get items before this cursor
            order_by: Sort order
            max_page_size: Maximum allowed page size

        Returns:
            Page with results and page info
        """
        # Validate page size
        if first is not None:
            limit = PaginationHelper.get_page_size(first, max_size=max_page_size)
        elif last is not None:
            limit = PaginationHelper.get_page_size(last, max_size=max_page_size)
        else:
            limit = PaginationHelper.get_page_size(None, max_size=max_page_size)

        # Validate cursor_field exists on model
        if not hasattr(query.model, cursor_field):
            raise ValueError(f"Field '{cursor_field}' not found on model {query.model.__name__}")

        # Apply cursor filters
        cursor_value = None
        if after:
            cursor_value = Cursor.decode(after)
            if cursor_value is not None:
                if order_by == SortOrder.ASC:
                    query = query.filter(getattr(query.model, cursor_field) > cursor_value)
                else:
                    query = query.filter(getattr(query.model, cursor_field) < cursor_value)

        if before:
            cursor_value = Cursor.decode(before)
            if cursor_value is not None:
                if order_by == SortOrder.ASC:
                    query = query.filter(getattr(query.model, cursor_field) < cursor_value)
                else:
                    query = query.filter(getattr(query.model, cursor_field) > cursor_value)

        # Apply ordering
        if order_by == SortOrder.ASC:
            query = query.order_by(getattr(query.model, cursor_field).asc())
        else:
            query = query.order_by(getattr(query.model, cursor_field).desc())

        # Fetch one extra item to determine if there are more pages
        items = await query.limit(limit + 1).all()

        # Check if there are more items
        has_next_page = len(items) > limit
        if has_next_page:
            items = items[:limit]

        # Generate cursors
        start_cursor = None
        end_cursor = None
        if items:
            start_cursor = Cursor.encode(getattr(items[0], cursor_field))
            end_cursor = Cursor.encode(getattr(items[-1], cursor_field))

        return Page(
            items=items,
            page_info=PageInfo(
                has_next_page=has_next_page,
                has_previous_page=after is not None or before is not None,
                start_cursor=start_cursor,
                end_cursor=end_cursor,
            ),
        )


# Streaming response helpers
class StreamingResponse:
    """
    Helpers for streaming large responses.
    مساعدون لبث الاستجابات الكبيرة.
    """

    @staticmethod
    async def stream_json_array(
        items: AsyncIterator[Any],
        chunk_size: int = 100,
    ) -> AsyncIterator[str]:
        """
        Stream items as a JSON array.
        بث العناصر كمصفوفة JSON.

        Args:
            items: Async iterator of items
            chunk_size: Number of items to buffer before yielding

        Yields:
            JSON chunks
        """
        yield '{"items": ['

        first = True
        buffer = []

        async for item in items:
            if not first:
                buffer.append(",")
            first = False

            # Serialize item
            if hasattr(item, "dict"):
                item_json = json.dumps(item.dict())
            elif hasattr(item, "__dict__"):
                item_json = json.dumps(item.__dict__)
            else:
                item_json = json.dumps(item)

            buffer.append(item_json)

            # Yield chunk if buffer is full
            if len(buffer) >= chunk_size:
                yield "".join(buffer)
                buffer = []

        # Yield remaining items
        if buffer:
            yield "".join(buffer)

        yield "]}"

    @staticmethod
    async def stream_ndjson(
        items: AsyncIterator[Any],
    ) -> AsyncIterator[str]:
        """
        Stream items as newline-delimited JSON (NDJSON).
        بث العناصر كـ JSON محدد بسطر جديد.

        Args:
            items: Async iterator of items

        Yields:
            NDJSON lines
        """
        async for item in items:
            # Serialize item
            if hasattr(item, "dict"):
                item_json = json.dumps(item.dict())
            elif hasattr(item, "__dict__"):
                item_json = json.dumps(item.__dict__)
            else:
                item_json = json.dumps(item)

            yield item_json + "\n"


# FastAPI integration helpers
def create_pagination_params(
    page: int = 1,
    page_size: int = 50,
    max_page_size: int = 1000,
):
    """
    FastAPI dependency for pagination parameters.
    تبعية FastAPI لمعاملات التقسيم.

    Usage:
        @app.get("/items")
        async def list_items(pagination: dict = Depends(create_pagination_params)):
            page = pagination["page"]
            page_size = pagination["page_size"]
            ...
    """
    return {
        "page": max(1, page),
        "page_size": PaginationHelper.get_page_size(page_size, max_size=max_page_size),
    }


def create_cursor_pagination_params(
    first: int | None = None,
    after: str | None = None,
    last: int | None = None,
    before: str | None = None,
):
    """
    FastAPI dependency for cursor-based pagination parameters.
    تبعية FastAPI لمعاملات التقسيم القائم على المؤشر.

    Usage:
        @app.get("/items")
        async def list_items(pagination: dict = Depends(create_cursor_pagination_params)):
            ...
    """
    return {
        "first": first,
        "after": after,
        "last": last,
        "before": before,
    }
