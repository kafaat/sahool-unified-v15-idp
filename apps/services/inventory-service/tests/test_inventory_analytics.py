"""
Unit Tests for Inventory Analytics
اختبارات الوحدة لتحليلات المخزون
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest


class TestConsumptionForecast:
    """Test consumption forecasting"""

    @pytest.mark.asyncio
    async def test_forecast_to_dict(self, sample_consumption_forecast):
        """Test forecast serialization to dict"""
        forecast_dict = sample_consumption_forecast.to_dict()

        assert forecast_dict["item_id"] == "item-123"
        assert forecast_dict["current_stock"] == 500.0
        assert forecast_dict["avg_daily_consumption"] == 5.0
        assert "reorder_date" in forecast_dict
        assert isinstance(forecast_dict["reorder_date"], str)


class TestInventoryAnalytics:
    """Test InventoryAnalytics class"""

    @pytest.mark.asyncio
    async def test_analytics_initialization(self, async_session, sample_tenant_id):
        """Test analytics service initialization"""
        from src.inventory_analytics import InventoryAnalytics

        analytics = InventoryAnalytics(async_session, sample_tenant_id)

        assert analytics.db == async_session
        assert analytics.tenant_id == sample_tenant_id

    @pytest.mark.asyncio
    async def test_get_consumption_forecast_no_data(self, async_session, sample_tenant_id):
        """Test forecast when item has no consumption history"""
        from src.inventory_analytics import InventoryAnalytics
        from src.models.inventory import InventoryItem

        # Create test item
        item = InventoryItem(
            id="test-item-1",
            sku="TEST-001",
            name_en="Test Item",
            name_ar="عنصر اختبار",
            unit="kg",
            current_stock=Decimal("100.0"),
            available_stock=Decimal("100.0"),
            reorder_level=Decimal("20.0"),
            reorder_quantity=Decimal("50.0"),
            average_cost=Decimal("10.0"),
            tenant_id=sample_tenant_id,
        )
        async_session.add(item)
        await async_session.flush()

        analytics = InventoryAnalytics(async_session, sample_tenant_id)
        forecast = await analytics.get_consumption_forecast("test-item-1")

        assert forecast is not None
        assert forecast.item_id == "test-item-1"
        assert forecast.avg_daily_consumption == 0.0
        assert forecast.days_until_stockout == 999
        assert forecast.confidence == 0.0

    @pytest.mark.asyncio
    async def test_get_inventory_valuation(self, async_session, sample_tenant_id):
        """Test inventory valuation calculation"""
        from src.inventory_analytics import InventoryAnalytics
        from src.models.inventory import InventoryItem, ItemCategory

        # Create category
        category = ItemCategory(
            id="cat-1",
            name_en="Test Category",
            name_ar="فئة الاختبار",
            code="TEST",
            tenant_id=sample_tenant_id,
        )
        async_session.add(category)
        await async_session.flush()

        # Create items
        item1 = InventoryItem(
            id="item-1",
            sku="TEST-001",
            name_en="Item 1",
            name_ar="عنصر 1",
            unit="kg",
            current_stock=Decimal("100.0"),
            available_stock=Decimal("100.0"),
            average_cost=Decimal("10.0"),
            category_id="cat-1",
            tenant_id=sample_tenant_id,
        )
        item2 = InventoryItem(
            id="item-2",
            sku="TEST-002",
            name_en="Item 2",
            name_ar="عنصر 2",
            unit="liter",
            current_stock=Decimal("50.0"),
            available_stock=Decimal("50.0"),
            average_cost=Decimal("20.0"),
            category_id="cat-1",
            tenant_id=sample_tenant_id,
        )
        async_session.add_all([item1, item2])
        await async_session.flush()

        analytics = InventoryAnalytics(async_session, sample_tenant_id)
        valuation = await analytics.get_inventory_valuation()

        assert valuation.total_value == 2000.0  # (100*10) + (50*20)
        assert valuation.currency == "YER"
        assert "Test Category" in valuation.by_category
        assert len(valuation.top_items) > 0

    @pytest.mark.asyncio
    async def test_get_turnover_analysis(self, async_session, sample_tenant_id):
        """Test inventory turnover analysis"""
        from src.inventory_analytics import InventoryAnalytics
        from src.models.inventory import InventoryItem, ItemCategory

        # Create category
        category = ItemCategory(
            id="cat-1",
            name_en="Test Category",
            name_ar="فئة",
            code="TEST",
            tenant_id=sample_tenant_id,
        )
        async_session.add(category)
        await async_session.flush()

        # Create item
        item = InventoryItem(
            id="item-1",
            sku="TEST-001",
            name_en="Fast Moving Item",
            name_ar="عنصر سريع الحركة",
            unit="kg",
            current_stock=Decimal("100.0"),
            available_stock=Decimal("100.0"),
            average_cost=Decimal("10.0"),
            category_id="cat-1",
            tenant_id=sample_tenant_id,
        )
        async_session.add(item)
        await async_session.flush()

        analytics = InventoryAnalytics(async_session, sample_tenant_id)
        metrics = await analytics.get_turnover_analysis()

        assert len(metrics) > 0
        assert metrics[0].item_id == "item-1"
        assert metrics[0].velocity in ["fast", "medium", "slow", "dead"]

    @pytest.mark.asyncio
    async def test_identify_slow_moving_items(self, async_session, sample_tenant_id):
        """Test identification of slow-moving items"""
        from src.inventory_analytics import InventoryAnalytics
        from src.models.inventory import InventoryItem, ItemCategory

        # Create category
        category = ItemCategory(
            id="cat-1",
            name_en="Category",
            name_ar="فئة",
            code="TEST",
            tenant_id=sample_tenant_id,
        )
        async_session.add(category)

        # Create slow-moving item
        item = InventoryItem(
            id="item-1",
            sku="SLOW-001",
            name_en="Slow Item",
            name_ar="عنصر بطيء",
            unit="kg",
            current_stock=Decimal("200.0"),
            available_stock=Decimal("200.0"),
            average_cost=Decimal("15.0"),
            category_id="cat-1",
            tenant_id=sample_tenant_id,
        )
        async_session.add(item)
        await async_session.flush()

        analytics = InventoryAnalytics(async_session, sample_tenant_id)
        slow_items = await analytics.identify_slow_moving(days_threshold=90)

        assert len(slow_items) > 0
        assert slow_items[0]["sku"] == "SLOW-001"
        assert "total_value" in slow_items[0]

    @pytest.mark.asyncio
    async def test_identify_dead_stock(self, async_session, sample_tenant_id):
        """Test identification of dead stock"""
        from src.inventory_analytics import InventoryAnalytics
        from src.models.inventory import InventoryItem, ItemCategory

        # Create category
        category = ItemCategory(
            id="cat-1",
            name_en="Category",
            name_ar="فئة",
            code="TEST",
            tenant_id=sample_tenant_id,
        )
        async_session.add(category)

        # Create dead stock item with near expiry
        expiry_date = date.today() + timedelta(days=30)
        item = InventoryItem(
            id="item-1",
            sku="DEAD-001",
            name_en="Dead Stock",
            name_ar="مخزون ميت",
            unit="kg",
            current_stock=Decimal("50.0"),
            available_stock=Decimal("50.0"),
            average_cost=Decimal("10.0"),
            has_expiry=True,
            expiry_date=expiry_date,
            category_id="cat-1",
            tenant_id=sample_tenant_id,
        )
        async_session.add(item)
        await async_session.flush()

        analytics = InventoryAnalytics(async_session, sample_tenant_id)
        dead_items = await analytics.identify_dead_stock(days_threshold=180)

        assert len(dead_items) > 0
        assert "reason" in dead_items[0]

    @pytest.mark.asyncio
    async def test_get_abc_analysis(self, async_session, sample_tenant_id):
        """Test ABC (Pareto) analysis"""
        from src.inventory_analytics import InventoryAnalytics
        from src.models.inventory import InventoryItem, ItemCategory

        # Create category
        category = ItemCategory(
            id="cat-1",
            name_en="Category",
            name_ar="فئة",
            code="TEST",
            tenant_id=sample_tenant_id,
        )
        async_session.add(category)

        # Create items with different values (A, B, C classes)
        items = [
            InventoryItem(
                id=f"item-{i}",
                sku=f"TEST-{i:03d}",
                name_en=f"Item {i}",
                name_ar=f"عنصر {i}",
                unit="kg",
                current_stock=Decimal(str(1000 - (i * 50))),  # Decreasing stock
                available_stock=Decimal(str(1000 - (i * 50))),
                average_cost=Decimal(str(10 + i)),  # Increasing cost
                category_id="cat-1",
                tenant_id=sample_tenant_id,
            )
            for i in range(1, 11)
        ]
        async_session.add_all(items)
        await async_session.flush()

        analytics = InventoryAnalytics(async_session, sample_tenant_id)
        abc_analysis = await analytics.get_abc_analysis()

        assert "a_class" in abc_analysis
        assert "b_class" in abc_analysis
        assert "c_class" in abc_analysis
        assert abc_analysis["total_items"] == 10

    @pytest.mark.asyncio
    async def test_get_reorder_recommendations(self, async_session, sample_tenant_id):
        """Test reorder recommendations"""
        from src.inventory_analytics import InventoryAnalytics
        from src.models.inventory import InventoryItem, ItemCategory, Supplier

        # Create category and supplier
        category = ItemCategory(
            id="cat-1",
            name_en="Category",
            name_ar="فئة",
            code="TEST",
            tenant_id=sample_tenant_id,
        )
        supplier = Supplier(
            id="sup-1",
            name="Test Supplier",
            lead_time_days=7,
            tenant_id=sample_tenant_id,
        )
        async_session.add_all([category, supplier])
        await async_session.flush()

        # Create item below reorder level
        item = InventoryItem(
            id="item-1",
            sku="LOW-001",
            name_en="Low Stock Item",
            name_ar="عنصر منخفض المخزون",
            unit="kg",
            current_stock=Decimal("15.0"),
            available_stock=Decimal("15.0"),
            reorder_level=Decimal("20.0"),
            reorder_quantity=Decimal("100.0"),
            average_cost=Decimal("10.0"),
            category_id="cat-1",
            supplier_id="sup-1",
            tenant_id=sample_tenant_id,
        )
        async_session.add(item)
        await async_session.flush()

        analytics = InventoryAnalytics(async_session, sample_tenant_id)
        recommendations = await analytics.get_reorder_recommendations()

        assert len(recommendations) > 0
        assert recommendations[0]["sku"] == "LOW-001"
        assert "urgency" in recommendations[0]

    @pytest.mark.asyncio
    async def test_generate_dashboard_metrics(self, async_session, sample_tenant_id):
        """Test dashboard metrics generation"""
        from src.inventory_analytics import InventoryAnalytics
        from src.models.inventory import InventoryItem, ItemCategory

        # Create category and items
        category = ItemCategory(
            id="cat-1",
            name_en="Category",
            name_ar="فئة",
            code="TEST",
            tenant_id=sample_tenant_id,
        )
        async_session.add(category)

        item = InventoryItem(
            id="item-1",
            sku="TEST-001",
            name_en="Test Item",
            name_ar="عنصر",
            unit="kg",
            current_stock=Decimal("100.0"),
            available_stock=Decimal("100.0"),
            average_cost=Decimal("10.0"),
            category_id="cat-1",
            tenant_id=sample_tenant_id,
        )
        async_session.add(item)
        await async_session.flush()

        analytics = InventoryAnalytics(async_session, sample_tenant_id)
        metrics = await analytics.generate_dashboard_metrics()

        assert "total_skus" in metrics
        assert "total_value" in metrics
        assert "low_stock_count" in metrics
        assert "average_turnover_ratio" in metrics
        assert metrics["total_skus"] >= 0
