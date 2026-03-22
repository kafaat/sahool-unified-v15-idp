"""Tests for SupplierFinder in Supply Chain Service."""

import os

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NATS_URL", "")
os.environ.setdefault("REDIS_URL", "")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
from uuid import UUID, uuid4

import pytest


@pytest.fixture
def finder():
    from src.suppliers.finder import SupplierFinder

    return SupplierFinder()
class TestSupplierFinderInit:
    """Tests for SupplierFinder initialization."""

    def test_init_creates_mock_suppliers(self, finder):
        assert len(finder._mock_suppliers) == 4

    def test_mock_suppliers_have_required_fields(self, finder):
        for s in finder._mock_suppliers:
            assert "id" in s
            assert "name" in s
            assert "name_ar" in s
            assert "latitude" in s
            assert "longitude" in s
            assert "rating" in s
            assert "delivery_days" in s
            assert "price_modifier" in s

    def test_mock_suppliers_have_uuid_ids(self, finder):
        for s in finder._mock_suppliers:
            assert isinstance(s["id"], UUID)
class TestHaversineDistance:
    """Tests for haversine distance calculation."""

    def test_same_point_zero_distance(self):
        from src.suppliers.finder import SupplierFinder

        d = SupplierFinder._haversine_distance(24.7, 46.7, 24.7, 46.7)
        assert d == pytest.approx(0.0, abs=0.01)

    def test_known_distance_riyadh_jeddah(self):
        from src.suppliers.finder import SupplierFinder

        # Riyadh to Jeddah is approximately 850 km
        d = SupplierFinder._haversine_distance(24.7136, 46.6753, 21.4858, 39.1925)
        assert 800 < d < 950

    def test_symmetry(self):
        from src.suppliers.finder import SupplierFinder

        d1 = SupplierFinder._haversine_distance(24.7, 46.7, 21.5, 39.2)
        d2 = SupplierFinder._haversine_distance(21.5, 39.2, 24.7, 46.7)
        assert d1 == pytest.approx(d2, abs=0.01)

    def test_antipodal_points(self):
        from src.suppliers.finder import SupplierFinder

        # North pole to south pole is about half earth circumference (~20015 km)
        d = SupplierFinder._haversine_distance(90, 0, -90, 0)
        assert 20000 < d < 20100
class TestFindSuppliersByProduct:
    """Tests for find_suppliers_by_product."""

    @pytest.mark.asyncio
    async def test_returns_suppliers(self, finder):
        result = await finder.find_suppliers_by_product(uuid4())
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_max_results_limit(self, finder):
        result = await finder.find_suppliers_by_product(uuid4(), max_results=2)
        assert len(result) <= 2

    @pytest.mark.asyncio
    async def test_with_location_sorts_by_distance(self, finder):
        result = await finder.find_suppliers_by_product(
            uuid4(), latitude=24.7, longitude=46.7
        )
        assert len(result) > 0
        # Check that distance_km is set
        assert "distance_km" in result[0]

    @pytest.mark.asyncio
    async def test_without_location_no_distance(self, finder):
        result = await finder.find_suppliers_by_product(uuid4())
        assert "distance_km" not in result[0]
class TestFindSuppliersNearby:
    """Tests for find_suppliers_nearby."""

    @pytest.mark.asyncio
    async def test_finds_nearby_with_large_radius(self, finder):
        # Using a huge radius to find all mock suppliers
        result = await finder.find_suppliers_nearby(24.7, 46.7, radius_km=5000)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_no_results_with_tiny_radius(self, finder):
        # Using a tiny radius at a remote location
        result = await finder.find_suppliers_nearby(0.0, 0.0, radius_km=1)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_results_sorted_by_distance(self, finder):
        result = await finder.find_suppliers_nearby(24.7, 46.7, radius_km=5000)
        if len(result) >= 2:
            for i in range(len(result) - 1):
                assert result[i]["distance_km"] <= result[i + 1]["distance_km"]

    @pytest.mark.asyncio
    async def test_distance_km_is_rounded(self, finder):
        result = await finder.find_suppliers_nearby(24.7, 46.7, radius_km=5000)
        for s in result:
            # distance_km should be rounded to 2 decimal places
            assert s["distance_km"] == round(s["distance_km"], 2)
class TestComparePrices:
    """Tests for compare_prices."""

    @pytest.mark.asyncio
    async def test_returns_comparisons(self, finder):
        result = await finder.compare_prices(uuid4(), 100.0)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_sorted_by_total_price(self, finder):
        result = await finder.compare_prices(uuid4(), 100.0)
        if len(result) >= 2:
            for i in range(len(result) - 1):
                assert result[i]["total_price"] <= result[i + 1]["total_price"]

    @pytest.mark.asyncio
    async def test_filter_by_supplier_ids(self, finder):
        # Get the IDs of first two suppliers
        ids = [finder._mock_suppliers[0]["id"], finder._mock_suppliers[1]["id"]]
        result = await finder.compare_prices(uuid4(), 50.0, supplier_ids=ids)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_comparison_has_required_fields(self, finder):
        result = await finder.compare_prices(uuid4(), 100.0)
        for comp in result:
            assert "supplier_id" in comp
            assert "supplier_name" in comp
            assert "supplier_name_ar" in comp
            assert "unit_price" in comp
            assert "total_price" in comp
            assert "delivery_days" in comp
            assert "rating" in comp
class TestCheckAvailability:
    """Tests for check_availability."""

    @pytest.mark.asyncio
    async def test_returns_availability_info(self, finder):
        result = await finder.check_availability(uuid4(), 100.0, uuid4())
        assert "product_id" in result
        assert "supplier_id" in result
        assert "requested_quantity" in result
        assert "available_quantity" in result
        assert "is_available" in result
        assert "status" in result

    @pytest.mark.asyncio
    async def test_status_values(self, finder):
        result = await finder.check_availability(uuid4(), 100.0, uuid4())
        assert result["status"] in ("in_stock", "limited")

    @pytest.mark.asyncio
    async def test_requested_quantity_matches(self, finder):
        qty = 75.5
        result = await finder.check_availability(uuid4(), qty, uuid4())
        assert result["requested_quantity"] == qty
class TestGetQuotes:
    """Tests for get_quotes."""

    @pytest.mark.asyncio
    async def test_returns_quotes_for_all_suppliers(self, finder):
        result = await finder.get_quotes(uuid4(), 100.0)
        assert len(result) == 4  # 4 mock suppliers

    @pytest.mark.asyncio
    async def test_quotes_have_required_fields(self, finder):
        result = await finder.get_quotes(uuid4(), 100.0)
        for q in result:
            assert "supplier_id" in q
            assert "supplier_name" in q
            assert "unit_price" in q
            assert "total_price" in q
            assert "delivery_days" in q
            assert "availability" in q

    @pytest.mark.asyncio
    async def test_total_price_calculation(self, finder):
        result = await finder.get_quotes(uuid4(), 100.0)
        for q in result:
            expected = round(q["unit_price"] * 100.0, 2)
            assert q["total_price"] == expected
class TestFindBestSupplier:
    """Tests for find_best_supplier."""

    @pytest.mark.asyncio
    async def test_optimize_price(self, finder):
        result = await finder.find_best_supplier(uuid4(), 100.0, optimize_for="price")
        assert result is not None
        assert "total_price" in result

    @pytest.mark.asyncio
    async def test_optimize_delivery(self, finder):
        result = await finder.find_best_supplier(uuid4(), 100.0, optimize_for="delivery")
        assert result is not None
        assert "delivery_days" in result

    @pytest.mark.asyncio
    async def test_optimize_rating(self, finder):
        result = await finder.find_best_supplier(uuid4(), 100.0, optimize_for="rating")
        assert result is not None
        assert "rating" in result

    @pytest.mark.asyncio
    async def test_unknown_optimize_defaults_to_price(self, finder):
        result = await finder.find_best_supplier(uuid4(), 100.0, optimize_for="unknown")
        assert result is not None
class TestGetSupplierRating:
    """Tests for get_supplier_rating."""

    @pytest.mark.asyncio
    async def test_existing_supplier(self, finder):
        supplier_id = finder._mock_suppliers[0]["id"]
        result = await finder.get_supplier_rating(supplier_id)
        assert result is not None
        assert result["supplier_id"] == supplier_id
        assert "rating" in result
        assert "total_reviews" in result
        assert "rating_breakdown" in result

    @pytest.mark.asyncio
    async def test_nonexistent_supplier(self, finder):
        result = await finder.get_supplier_rating(uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_rating_breakdown_sums(self, finder):
        supplier_id = finder._mock_suppliers[0]["id"]
        result = await finder.get_supplier_rating(supplier_id)
        breakdown = result["rating_breakdown"]
        total = sum(int(v) for v in breakdown.values())
        assert total == result["total_reviews"]
