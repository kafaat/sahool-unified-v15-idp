"""
Tests for shared/libs/pagination.py module
اختبارات وحدة أدوات التقسيم
"""

import base64
import json
from dataclasses import dataclass

import pytest


class TestSortOrder:
    """Tests for SortOrder enum"""

    def test_sort_order_values(self):
        """Test sort order values"""
        from shared.libs.pagination import SortOrder

        assert SortOrder.ASC == "asc"
        assert SortOrder.DESC == "desc"

    def test_sort_order_is_string(self):
        """Test SortOrder is string enum"""
        from shared.libs.pagination import SortOrder

        assert isinstance(SortOrder.ASC, str)
        assert isinstance(SortOrder.DESC, str)


class TestPageInfo:
    """Tests for PageInfo dataclass"""

    def test_page_info_minimal(self):
        """Test PageInfo with required fields only"""
        from shared.libs.pagination import PageInfo

        info = PageInfo(has_next_page=True, has_previous_page=False)

        assert info.has_next_page is True
        assert info.has_previous_page is False
        assert info.start_cursor is None
        assert info.end_cursor is None
        assert info.total_count is None

    def test_page_info_full(self):
        """Test PageInfo with all fields"""
        from shared.libs.pagination import PageInfo

        info = PageInfo(
            has_next_page=True,
            has_previous_page=True,
            start_cursor="cursor1",
            end_cursor="cursor2",
            total_count=100,
        )

        assert info.start_cursor == "cursor1"
        assert info.end_cursor == "cursor2"
        assert info.total_count == 100


class TestPage:
    """Tests for Page generic dataclass"""

    def test_page_with_items(self):
        """Test Page with items"""
        from shared.libs.pagination import Page, PageInfo

        page_info = PageInfo(has_next_page=False, has_previous_page=False)
        page = Page(items=[1, 2, 3], page_info=page_info)

        assert page.items == [1, 2, 3]
        assert page.page_info.has_next_page is False

    def test_page_empty(self):
        """Test Page with no items"""
        from shared.libs.pagination import Page, PageInfo

        page_info = PageInfo(has_next_page=False, has_previous_page=False)
        page = Page(items=[], page_info=page_info)

        assert page.items == []

    def test_page_to_dict_simple_items(self):
        """Test Page to_dict with simple items"""
        from shared.libs.pagination import Page, PageInfo

        page_info = PageInfo(
            has_next_page=True,
            has_previous_page=False,
            start_cursor="start",
            end_cursor="end",
            total_count=50,
        )
        page = Page(items=["a", "b", "c"], page_info=page_info)

        result = page.to_dict()

        assert result["items"] == ["a", "b", "c"]
        assert result["page_info"]["has_next_page"] is True
        assert result["page_info"]["has_previous_page"] is False
        assert result["page_info"]["start_cursor"] == "start"
        assert result["page_info"]["end_cursor"] == "end"
        assert result["page_info"]["total_count"] == 50


class TestOffsetPage:
    """Tests for OffsetPage dataclass"""

    def test_offset_page_creation(self):
        """Test OffsetPage creation"""
        from shared.libs.pagination import OffsetPage

        page = OffsetPage(items=[1, 2, 3], total=100, page=1, page_size=10, total_pages=10)

        assert page.items == [1, 2, 3]
        assert page.total == 100
        assert page.page == 1
        assert page.page_size == 10
        assert page.total_pages == 10

    def test_offset_page_to_dict(self):
        """Test OffsetPage to_dict"""
        from shared.libs.pagination import OffsetPage

        page = OffsetPage(items=["item1", "item2"], total=50, page=2, page_size=10, total_pages=5)

        result = page.to_dict()

        assert result["items"] == ["item1", "item2"]
        assert result["pagination"]["total"] == 50
        assert result["pagination"]["page"] == 2
        assert result["pagination"]["page_size"] == 10
        assert result["pagination"]["total_pages"] == 5
        assert result["pagination"]["has_next"] is True
        assert result["pagination"]["has_previous"] is True

    def test_offset_page_first_page(self):
        """Test OffsetPage on first page"""
        from shared.libs.pagination import OffsetPage

        page = OffsetPage(items=[], total=50, page=1, page_size=10, total_pages=5)

        result = page.to_dict()

        assert result["pagination"]["has_previous"] is False
        assert result["pagination"]["has_next"] is True

    def test_offset_page_last_page(self):
        """Test OffsetPage on last page"""
        from shared.libs.pagination import OffsetPage

        page = OffsetPage(items=[], total=50, page=5, page_size=10, total_pages=5)

        result = page.to_dict()

        assert result["pagination"]["has_previous"] is True
        assert result["pagination"]["has_next"] is False


class TestCursor:
    """Tests for Cursor class"""

    def test_cursor_encode_string(self):
        """Test encoding string as cursor"""
        from shared.libs.pagination import Cursor

        result = Cursor.encode("test-id")

        assert isinstance(result, str)
        # Verify it's base64
        decoded = base64.b64decode(result.encode()).decode()
        assert json.loads(decoded) == "test-id"

    def test_cursor_encode_number(self):
        """Test encoding number as cursor"""
        from shared.libs.pagination import Cursor

        result = Cursor.encode(12345)

        decoded = base64.b64decode(result.encode()).decode()
        assert json.loads(decoded) == 12345

    def test_cursor_encode_dict(self):
        """Test encoding dict as cursor"""
        from shared.libs.pagination import Cursor

        value = {"id": 1, "timestamp": "2024-01-01"}
        result = Cursor.encode(value)

        decoded = base64.b64decode(result.encode()).decode()
        assert json.loads(decoded) == value

    def test_cursor_decode_string(self):
        """Test decoding cursor to string"""
        from shared.libs.pagination import Cursor

        encoded = Cursor.encode("my-value")
        decoded = Cursor.decode(encoded)

        assert decoded == "my-value"

    def test_cursor_decode_number(self):
        """Test decoding cursor to number"""
        from shared.libs.pagination import Cursor

        encoded = Cursor.encode(42)
        decoded = Cursor.decode(encoded)

        assert decoded == 42

    def test_cursor_decode_invalid(self):
        """Test decoding invalid cursor returns None"""
        from shared.libs.pagination import Cursor

        result = Cursor.decode("not-valid-base64!!!")

        assert result is None

    def test_cursor_roundtrip(self):
        """Test cursor encode-decode roundtrip"""
        from shared.libs.pagination import Cursor

        values = [
            "string-value",
            12345,
            {"complex": "value", "num": 42},
            ["list", "of", "items"],
            None,
            True,
            False,
        ]

        for value in values:
            encoded = Cursor.encode(value)
            decoded = Cursor.decode(encoded)
            assert decoded == value


class TestPaginationHelper:
    """Tests for PaginationHelper class"""

    def test_get_page_size_default(self):
        """Test get_page_size with None returns default"""
        from shared.libs.pagination import PaginationHelper

        result = PaginationHelper.get_page_size(None)

        assert result == 50  # default

    def test_get_page_size_custom_default(self):
        """Test get_page_size with custom default"""
        from shared.libs.pagination import PaginationHelper

        result = PaginationHelper.get_page_size(None, default=25)

        assert result == 25

    def test_get_page_size_valid(self):
        """Test get_page_size with valid size"""
        from shared.libs.pagination import PaginationHelper

        result = PaginationHelper.get_page_size(100)

        assert result == 100

    def test_get_page_size_exceeds_max(self):
        """Test get_page_size caps at max"""
        from shared.libs.pagination import PaginationHelper

        result = PaginationHelper.get_page_size(5000, max_size=1000)

        assert result == 1000

    def test_get_page_size_below_min(self):
        """Test get_page_size enforces minimum of 1"""
        from shared.libs.pagination import PaginationHelper

        result = PaginationHelper.get_page_size(0)

        assert result == 1

    def test_get_page_size_negative(self):
        """Test get_page_size handles negative values"""
        from shared.libs.pagination import PaginationHelper

        result = PaginationHelper.get_page_size(-10)

        assert result == 1

    def test_calculate_offset_page_1(self):
        """Test calculate_offset for page 1"""
        from shared.libs.pagination import PaginationHelper

        result = PaginationHelper.calculate_offset(1, 10)

        assert result == 0

    def test_calculate_offset_page_2(self):
        """Test calculate_offset for page 2"""
        from shared.libs.pagination import PaginationHelper

        result = PaginationHelper.calculate_offset(2, 10)

        assert result == 10

    def test_calculate_offset_page_5(self):
        """Test calculate_offset for page 5"""
        from shared.libs.pagination import PaginationHelper

        result = PaginationHelper.calculate_offset(5, 20)

        assert result == 80

    def test_calculate_offset_page_zero(self):
        """Test calculate_offset treats page 0 as page 1"""
        from shared.libs.pagination import PaginationHelper

        result = PaginationHelper.calculate_offset(0, 10)

        assert result == 0

    def test_calculate_offset_negative_page(self):
        """Test calculate_offset treats negative page as page 1"""
        from shared.libs.pagination import PaginationHelper

        result = PaginationHelper.calculate_offset(-5, 10)

        assert result == 0

    def test_calculate_total_pages(self):
        """Test calculate_total_pages"""
        from shared.libs.pagination import PaginationHelper

        # Exact fit
        assert PaginationHelper.calculate_total_pages(100, 10) == 10

        # With remainder
        assert PaginationHelper.calculate_total_pages(101, 10) == 11

        # Less than page size
        assert PaginationHelper.calculate_total_pages(5, 10) == 1

    def test_calculate_total_pages_zero_items(self):
        """Test calculate_total_pages with zero items"""
        from shared.libs.pagination import PaginationHelper

        result = PaginationHelper.calculate_total_pages(0, 10)

        assert result == 0

    def test_calculate_total_pages_zero_page_size(self):
        """Test calculate_total_pages with zero page size"""
        from shared.libs.pagination import PaginationHelper

        result = PaginationHelper.calculate_total_pages(100, 0)

        assert result == 0

    def test_calculate_total_pages_one_item(self):
        """Test calculate_total_pages with one item"""
        from shared.libs.pagination import PaginationHelper

        result = PaginationHelper.calculate_total_pages(1, 10)

        assert result == 1


class TestCreatePaginationParams:
    """Tests for create_pagination_params function"""

    def test_create_pagination_params_defaults(self):
        """Test create_pagination_params with defaults"""
        from shared.libs.pagination import create_pagination_params

        result = create_pagination_params()

        assert result["page"] == 1
        assert result["page_size"] == 50

    def test_create_pagination_params_custom(self):
        """Test create_pagination_params with custom values"""
        from shared.libs.pagination import create_pagination_params

        result = create_pagination_params(page=3, page_size=25)

        assert result["page"] == 3
        assert result["page_size"] == 25

    def test_create_pagination_params_zero_page(self):
        """Test create_pagination_params with zero page becomes 1"""
        from shared.libs.pagination import create_pagination_params

        result = create_pagination_params(page=0)

        assert result["page"] == 1

    def test_create_pagination_params_negative_page(self):
        """Test create_pagination_params with negative page becomes 1"""
        from shared.libs.pagination import create_pagination_params

        result = create_pagination_params(page=-5)

        assert result["page"] == 1

    def test_create_pagination_params_exceeds_max(self):
        """Test create_pagination_params caps at max_page_size"""
        from shared.libs.pagination import create_pagination_params

        result = create_pagination_params(page_size=5000, max_page_size=100)

        assert result["page_size"] == 100


class TestCreateCursorPaginationParams:
    """Tests for create_cursor_pagination_params function"""

    def test_create_cursor_params_empty(self):
        """Test create_cursor_pagination_params with no args"""
        from shared.libs.pagination import create_cursor_pagination_params

        result = create_cursor_pagination_params()

        assert result["first"] is None
        assert result["after"] is None
        assert result["last"] is None
        assert result["before"] is None

    def test_create_cursor_params_first(self):
        """Test create_cursor_pagination_params with first"""
        from shared.libs.pagination import create_cursor_pagination_params

        result = create_cursor_pagination_params(first=10)

        assert result["first"] == 10
        assert result["after"] is None

    def test_create_cursor_params_after(self):
        """Test create_cursor_pagination_params with after cursor"""
        from shared.libs.pagination import create_cursor_pagination_params

        result = create_cursor_pagination_params(first=10, after="cursor123")

        assert result["first"] == 10
        assert result["after"] == "cursor123"

    def test_create_cursor_params_backward(self):
        """Test create_cursor_pagination_params for backward pagination"""
        from shared.libs.pagination import create_cursor_pagination_params

        result = create_cursor_pagination_params(last=5, before="cursorXYZ")

        assert result["last"] == 5
        assert result["before"] == "cursorXYZ"


class TestPageWithDictItems:
    """Tests for Page with items that have dict() method"""

    def test_page_to_dict_with_dataclass_items(self):
        """Test Page to_dict with dataclass items"""
        from shared.libs.pagination import Page, PageInfo

        @dataclass
        class Item:
            id: int
            name: str

            def dict(self):
                return {"id": self.id, "name": self.name}

        items = [Item(id=1, name="First"), Item(id=2, name="Second")]
        page_info = PageInfo(has_next_page=False, has_previous_page=False)
        page = Page(items=items, page_info=page_info)

        result = page.to_dict()

        assert len(result["items"]) == 2
        assert result["items"][0] == {"id": 1, "name": "First"}
        assert result["items"][1] == {"id": 2, "name": "Second"}
