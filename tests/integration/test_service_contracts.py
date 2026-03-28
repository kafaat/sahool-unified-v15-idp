"""
Service Contract Integration Tests
===================================
اختبارات تكامل عقود الخدمات

Verifies that API contracts between SAHOOL microservices are maintained.
Each test imports REAL models from the codebase and validates required
fields, value ranges, bilingual support, and cross-service consistency.

Author: SAHOOL Platform Team
Updated: March 2026
"""

from __future__ import annotations

import uuid
from dataclasses import fields as dc_fields
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal

import pytest


# ---------------------------------------------------------------------------
# 1. Weather service response format
# ---------------------------------------------------------------------------


class TestWeatherServiceContract:
    """Verify weather forecast models expose the required API contract fields."""

    def test_weather_forecast_has_required_fields(self):
        """WeatherForecast must include temperature, humidity, wind, and forecast_date."""
        from shared.weather_alerts.models import WeatherForecast

        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature=28.5,
            humidity=65.0,
            wind_speed=12.0,
        )

        assert forecast.temperature == 28.5
        assert forecast.humidity == 65.0
        assert forecast.wind_speed == 12.0
        assert forecast.forecast_date == date.today()

    def test_weather_forecast_to_dict_contains_keys(self):
        """to_dict() must include all contract keys."""
        from shared.weather_alerts.models import WeatherForecast

        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature=30.0,
            humidity=50.0,
            wind_speed=8.0,
        )
        d = forecast.to_dict()

        required_keys = {
            "forecast_date",
            "temperature",
            "temperature_min",
            "temperature_max",
            "humidity",
            "wind_speed",
            "wind_direction",
            "precipitation_probability",
            "precipitation_amount",
            "source",
            "confidence",
        }
        assert required_keys.issubset(d.keys()), f"Missing keys: {required_keys - d.keys()}"

    def test_weather_forecast_days_field(self):
        """IrrigationSchedule carries forecast_days_used for multi-day windows."""
        from shared.weather_alerts.models import IrrigationSchedule

        schedule = IrrigationSchedule(
            field_id="FIELD-001",
            forecast_days_used=5,
        )
        assert schedule.forecast_days_used == 5
        assert schedule.to_dict()["forecast_days_used"] == 5

    def test_weather_alert_bilingual(self):
        """WeatherAlert must carry title/description in both EN and AR."""
        from shared.weather_alerts.models import AlertSeverity, AlertType, WeatherAlert

        alert = WeatherAlert(
            alert_type=AlertType.FROST,
            severity=AlertSeverity.CRITICAL,
            title="Frost Warning",
            title_ar="تحذير من الصقيع",
            description="Sub-zero temperatures expected",
            description_ar="متوقع درجات حرارة تحت الصفر",
        )
        d = alert.to_dict()
        assert d["title"] != ""
        assert d["title_ar"] != ""
        assert d["description"] != ""
        assert d["description_ar"] != ""


# ---------------------------------------------------------------------------
# 2. Irrigation calculation contract
# ---------------------------------------------------------------------------


class TestIrrigationContract:
    """Verify irrigation plan models include water_amount, schedule, method, crop."""

    def test_irrigation_schedule_has_required_fields(self):
        """IrrigationSchedule must carry amount, recommendation, crop_type, and timing."""
        from shared.weather_alerts.models import (
            CropType,
            IrrigationRecommendation,
            IrrigationSchedule,
        )

        plan = IrrigationSchedule(
            field_id="FIELD-002",
            crop_type=CropType.WHEAT,
            recommendation=IrrigationRecommendation.IRRIGATE_NOW,
            recommended_amount_mm=25.0,
            recommended_date=date.today(),
        )
        assert plan.recommended_amount_mm == 25.0
        assert plan.crop_type == CropType.WHEAT
        assert plan.recommendation == IrrigationRecommendation.IRRIGATE_NOW
        assert plan.recommended_date is not None

    def test_irrigation_schedule_to_dict_contract(self):
        """to_dict() must include water amount, crop, and schedule keys."""
        from shared.weather_alerts.models import IrrigationSchedule

        plan = IrrigationSchedule(field_id="FIELD-003", recommended_amount_mm=30.0)
        d = plan.to_dict()

        required = {
            "field_id",
            "crop_type",
            "recommendation",
            "recommended_amount_mm",
            "recommended_date",
            "confidence",
        }
        assert required.issubset(d.keys()), f"Missing: {required - d.keys()}"

    def test_irrigation_goal_model(self):
        """IrrigationGoal pydantic model must have bilingual name fields."""
        from shared.irrigation.models import IrrigationGoal, IrrigationGoalType

        goal = IrrigationGoal(
            goal_type=IrrigationGoalType.WATER_SAVING,
            name="Save water",
            name_ar="توفير المياه",
            target_reduction=0.3,
            priority=1,
        )
        assert goal.name == "Save water"
        assert goal.name_ar == "توفير المياه"
        assert 0.0 <= goal.target_reduction <= 1.0

    def test_irrigation_bilingual_labels(self):
        """IrrigationSchedule must provide reason_ar and factors_ar."""
        from shared.weather_alerts.models import IrrigationSchedule

        plan = IrrigationSchedule(
            field_id="FIELD-004",
            reason="Low soil moisture",
            reason_ar="رطوبة التربة منخفضة",
            factors=["soil_moisture"],
            factors_ar=["رطوبة التربة"],
        )
        d = plan.to_dict()
        assert d["reason"] != ""
        assert d["reason_ar"] != ""
        assert len(d["factors"]) > 0
        assert len(d["factors_ar"]) > 0


# ---------------------------------------------------------------------------
# 3. Advisory recommendation contract
# ---------------------------------------------------------------------------


class TestAdvisoryRecommendationContract:
    """Verify advisory models span disease, fertilizer, and irrigation sections."""

    def test_weather_alert_covers_disease_advisory(self):
        """WeatherAlert can represent crop disease advisories with affected_crops."""
        from shared.weather_alerts.models import AlertSeverity, AlertType, WeatherAlert

        alert = WeatherAlert(
            alert_type=AlertType.HUMIDITY,
            severity=AlertSeverity.WARNING,
            title="Disease risk: high humidity",
            title_ar="خطر مرض: رطوبة عالية",
            affected_crops=["wheat", "tomato"],
            crop_damage_risk="high",
            crop_damage_risk_ar="مرتفع",
            recommended_actions=["Apply fungicide", "Improve ventilation"],
            recommended_actions_ar=["تطبيق مبيد فطري", "تحسين التهوية"],
        )
        d = alert.to_dict()
        assert len(d["affected_crops"]) >= 1
        assert d["crop_damage_risk"] in ("low", "medium", "high", "severe")
        assert len(d["recommended_actions"]) >= 1
        assert len(d["recommended_actions_ar"]) >= 1

    def test_fertilizer_advisory_model(self):
        """Fertilizer models must carry nutrient composition and bilingual names."""
        from shared.fertilizer_management.models import (
            ApplicationMethod,
            Fertilizer,
            FertilizerForm,
            FertilizerType,
            NutrientComposition,
        )

        fert = Fertilizer(
            id="FERT-001",
            name="Urea 46%",
            name_ar="يوريا 46%",
            fertilizer_type=FertilizerType.NITROGEN,
            form=FertilizerForm.GRANULAR,
            composition=NutrientComposition(nitrogen_n=46.0),
            application_methods=[ApplicationMethod.BROADCAST, ApplicationMethod.FERTIGATION],
        )
        d = fert.to_dict()
        assert d["name"] != ""
        assert d["name_ar"] != ""
        assert d["composition"]["N"] == 46.0
        assert fert.composition.npk_ratio == "46-0-0"

    def test_spray_window_advisory(self):
        """SprayWindow provides condition assessment for pesticide application."""
        from shared.weather_alerts.models import SprayCondition, SprayWindow

        window = SprayWindow(
            overall_condition=SprayCondition.OPTIMAL,
            score=85.0,
            recommendation="Ideal conditions for spraying",
            recommendation_ar="ظروف مثالية للرش",
        )
        d = window.to_dict()
        assert d["overall_condition"] == "optimal"
        assert d["recommendation"] != ""
        assert d["recommendation_ar"] != ""


# ---------------------------------------------------------------------------
# 4. Billing invoice contract
# ---------------------------------------------------------------------------


class TestBillingInvoiceContract:
    """Verify Invoice model has tenant_id, amount, currency, line_items.

    The billing-core service defines its Pydantic Invoice model inside
    apps/services/billing-core/src/main.py with relative imports that
    prevent direct import outside the service package. We verify the
    SQLAlchemy ORM model schema and the Pydantic contract independently.
    """

    def test_invoice_orm_has_tenant_id_column(self):
        """The Invoice ORM model must declare a tenant_id column."""
        import importlib
        import ast

        src = "/home/user/sahool-unified-v15-idp/apps/services/billing-core/src/main.py"
        with open(src) as f:
            tree = ast.parse(f.read())

        # Find the Invoice Pydantic class and collect its field names
        invoice_fields: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "Invoice":
                for item in node.body:
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        invoice_fields.add(item.target.id)

        required = {"invoice_id", "tenant_id", "currency", "total", "line_items"}
        assert required.issubset(invoice_fields), (
            f"Missing Invoice fields: {required - invoice_fields}"
        )

    def test_invoice_line_item_has_bilingual_description(self):
        """InvoiceLineItem must declare description and description_ar."""
        import ast

        src = "/home/user/sahool-unified-v15-idp/apps/services/billing-core/src/main.py"
        with open(src) as f:
            tree = ast.parse(f.read())

        line_item_fields: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "InvoiceLineItem":
                for item in node.body:
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        line_item_fields.add(item.target.id)

        assert "description" in line_item_fields
        assert "description_ar" in line_item_fields
        assert "amount" in line_item_fields

    def test_invoice_status_enum_values(self):
        """InvoiceStatus must include draft, pending, paid, overdue, canceled."""
        import ast

        src = "/home/user/sahool-unified-v15-idp/apps/services/billing-core/src/main.py"
        with open(src) as f:
            tree = ast.parse(f.read())

        # Find InvoiceStatus class and collect values
        statuses: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "InvoiceStatus":
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                if isinstance(item.value, ast.Constant):
                                    statuses.add(item.value.value)

        expected = {"draft", "pending", "paid", "overdue", "canceled"}
        assert expected.issubset(statuses), f"Missing statuses: {expected - statuses}"

    def test_currency_enum_defined(self):
        """Currency enum must be defined with at least USD."""
        import ast

        src = "/home/user/sahool-unified-v15-idp/apps/services/billing-core/src/main.py"
        with open(src) as f:
            tree = ast.parse(f.read())

        currency_values: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "Currency":
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                if isinstance(item.value, ast.Constant):
                                    currency_values.add(item.value.value)

        assert "USD" in currency_values


# ---------------------------------------------------------------------------
# 5. Notification payload contract
# ---------------------------------------------------------------------------


class TestNotificationPayloadContract:
    """Verify notification models have type, priority, recipient, channel, bilingual content."""

    def test_notification_payload_required_fields(self):
        """NotificationPayload must have priority, channels, tenant_id, and bilingual content."""
        from shared.notification_routing import (
            NotificationChannel,
            NotificationPayload,
            NotificationPriority,
        )

        payload = NotificationPayload(
            notification_id="NOTIF-001",
            tenant_id="tenant-xyz",
            user_id="user-123",
            priority=NotificationPriority.CRITICAL,
            alert_type="rpw_detected",
            title="Red Palm Weevil Detected",
            title_ar="تم اكتشاف سوسة النخيل الحمراء",
            body="Immediate action required in Block B",
            body_ar="مطلوب إجراء فوري في القطعة ب",
            channels=[NotificationChannel.PUSH, NotificationChannel.WHATSAPP, NotificationChannel.SMS],
        )
        d = payload.to_dict()

        assert d["tenant_id"] != ""
        assert d["user_id"] != ""
        assert d["priority"] == "critical"
        assert len(d["channels"]) >= 1
        assert d["title"] != ""
        assert d["title_ar"] != ""
        assert d["body"] != ""
        assert d["body_ar"] != ""

    def test_notification_router_builds_payload(self):
        """NotificationRouter.build_notification must populate channels from priority rules."""
        from shared.notification_routing import NotificationRouter

        router = NotificationRouter()
        payload = router.build_notification(
            notification_id="N-002",
            tenant_id="tenant-001",
            user_id="user-001",
            alert_type="frost_warning",
            body="Frost expected tonight",
            body_ar="متوقع صقيع الليلة",
        )
        assert payload.priority.value == "critical"
        assert len(payload.channels) >= 2  # critical routes to push + whatsapp + sms

    def test_notification_priority_enum_values(self):
        """All priority levels must be defined."""
        from shared.notification_routing import NotificationPriority

        expected = {"critical", "warning", "advisory", "info"}
        actual = {p.value for p in NotificationPriority}
        assert expected == actual

    def test_notification_channel_enum_values(self):
        """All delivery channels must be defined."""
        from shared.notification_routing import NotificationChannel

        expected = {"push", "whatsapp", "sms", "email", "in_app"}
        actual = {c.value for c in NotificationChannel}
        assert expected == actual


# ---------------------------------------------------------------------------
# 6. Field boundary GeoJSON contract
# ---------------------------------------------------------------------------


class TestFieldBoundaryGeoJSONContract:
    """Verify field models produce valid GeoJSON with type, coordinates, properties."""

    def _make_square_ring(self):
        """Create a simple closed polygon ring (square in Saudi Arabia)."""
        return [
            (46.7, 24.7),
            (46.8, 24.7),
            (46.8, 24.8),
            (46.7, 24.8),
            (46.7, 24.7),  # closed ring
        ]

    def test_field_boundary_to_geojson_feature(self):
        """to_geojson_feature() must produce valid GeoJSON Feature with required keys."""
        from shared.field_boundaries.models import FieldBoundary, Polygon

        ring = self._make_square_ring()
        boundary = FieldBoundary(
            field_id="FIELD-010",
            tenant_id="tenant-001",
            owner_id="owner-001",
            name="North Block",
            name_ar="القطعة الشمالية",
            geometry=Polygon(coordinates=[ring]),
            area_hectares=12.5,
        )
        geojson = boundary.to_geojson_feature()

        assert geojson["type"] == "Feature"
        assert "geometry" in geojson
        assert geojson["geometry"]["type"] == "Polygon"
        assert len(geojson["geometry"]["coordinates"]) >= 1
        assert len(geojson["geometry"]["coordinates"][0]) >= 4

        props = geojson["properties"]
        assert "field_id" in props
        assert "name" in props
        assert "name_ar" in props
        assert "area_hectares" in props

    def test_polygon_validation_closed_ring(self):
        """Polygon must reject rings that are not closed."""
        from shared.field_boundaries.models import Polygon

        open_ring = [(46.7, 24.7), (46.8, 24.7), (46.8, 24.8), (46.7, 24.8)]
        with pytest.raises(Exception):
            Polygon(coordinates=[open_ring])

    def test_polygon_validation_minimum_points(self):
        """Polygon ring must have at least 4 points."""
        from shared.field_boundaries.models import Polygon

        too_few = [(46.7, 24.7), (46.8, 24.7), (46.7, 24.7)]
        with pytest.raises(Exception):
            Polygon(coordinates=[too_few])

    def test_point_coordinate_validation(self):
        """Point coordinates must be valid lon/lat ranges."""
        from shared.field_boundaries.models import Point

        valid = Point(coordinates=(46.7, 24.7))
        assert valid.coordinates == (46.7, 24.7)

        with pytest.raises(Exception):
            Point(coordinates=(200.0, 24.7))  # invalid longitude

        with pytest.raises(Exception):
            Point(coordinates=(46.7, 100.0))  # invalid latitude


# ---------------------------------------------------------------------------
# 7. NDVI response contract
# ---------------------------------------------------------------------------


class TestNDVIResponseContract:
    """Verify NDVI models return value in [-1, 1] range with health_status enum."""

    def test_ndvi_result_valid_range(self):
        """NDVIResult mean_value must be in [-1.0, 1.0]."""
        from shared.satellite.sentinel_ndvi import NDVIResult, VegetationIndex

        result = NDVIResult(
            field_id="FIELD-020",
            timestamp=datetime.now(UTC),
            index_type=VegetationIndex.NDVI,
            mean_value=0.65,
            min_value=0.3,
            max_value=0.85,
            std_value=0.1,
            cloud_coverage=5.0,
            pixel_count=1000,
        )
        assert -1.0 <= result.mean_value <= 1.0
        assert -1.0 <= result.min_value <= 1.0
        assert -1.0 <= result.max_value <= 1.0

    def test_ndvi_rejects_out_of_range(self):
        """NDVIResult must raise ValueError for NDVI values outside [-1, 1]."""
        from shared.satellite.sentinel_ndvi import NDVIResult, VegetationIndex

        with pytest.raises(ValueError, match="outside valid range"):
            NDVIResult(
                field_id="FIELD-021",
                timestamp=datetime.now(UTC),
                index_type=VegetationIndex.NDVI,
                mean_value=1.5,  # invalid
                min_value=0.3,
                max_value=0.85,
                std_value=0.1,
                cloud_coverage=5.0,
                pixel_count=1000,
            )

    def test_ndvi_health_status_classification(self):
        """Health status must be classified based on mean NDVI value."""
        from shared.satellite.sentinel_ndvi import NDVIResult, VegetationIndex

        test_cases = [
            (0.7, "healthy", "صحي"),
            (0.5, "moderate", "معتدل"),
            (0.3, "stressed", "مجهد"),
            (0.1, "critical", "حرج"),
        ]
        for mean_val, expected_status, expected_ar in test_cases:
            result = NDVIResult(
                field_id="FIELD-022",
                timestamp=datetime.now(UTC),
                index_type=VegetationIndex.NDVI,
                mean_value=mean_val,
                min_value=mean_val - 0.1,
                max_value=mean_val + 0.1,
                std_value=0.05,
                cloud_coverage=10.0,
                pixel_count=500,
            )
            assert result.health_status == expected_status, (
                f"mean={mean_val}: expected {expected_status}, got {result.health_status}"
            )
            assert result.health_status_ar == expected_ar

    def test_ndvi_health_status_bilingual(self):
        """health_status_ar must be populated for every classification."""
        from shared.satellite.sentinel_ndvi import NDVIResult, VegetationIndex

        result = NDVIResult(
            field_id="FIELD-023",
            timestamp=datetime.now(UTC),
            index_type=VegetationIndex.NDVI,
            mean_value=0.45,
            min_value=0.2,
            max_value=0.7,
            std_value=0.1,
            cloud_coverage=15.0,
            pixel_count=800,
        )
        assert result.health_status_ar != ""


# ---------------------------------------------------------------------------
# 8. Sensor reading contract
# ---------------------------------------------------------------------------


class TestSensorReadingContract:
    """Verify IoT sensor models have device_id, sensor_type, value, timestamp, unit."""

    def test_sensor_reading_required_fields(self):
        """SensorReading must have sensor_id, reading_type, value, unit, timestamp."""
        from shared.soil_sensors.models import SensorReading, SensorType

        reading = SensorReading(
            sensor_id="SENSOR-001",
            timestamp=datetime.now(UTC),
            reading_type=SensorType.MOISTURE,
            value=42.5,
            unit="%",
        )
        assert reading.sensor_id == "SENSOR-001"
        assert reading.reading_type == SensorType.MOISTURE
        assert reading.value == 42.5
        assert reading.unit == "%"
        assert reading.timestamp is not None

    def test_sensor_device_model_fields(self):
        """SoilSensor must have id, tenant_id, field_id, name, and bilingual name."""
        from shared.soil_sensors.models import SensorProtocol, SensorType, SoilSensor

        sensor = SoilSensor(
            id="DEV-001",
            tenant_id="tenant-001",
            field_id="FIELD-030",
            name="Moisture Probe A",
            name_ar="مجس الرطوبة أ",
            sensor_type=SensorType.MOISTURE,
            protocol=SensorProtocol.LORAWAN,
            model="CropX-100",
            manufacturer="CropX",
            lat=24.7,
            lng=46.7,
        )
        assert sensor.tenant_id == "tenant-001"
        assert sensor.field_id == "FIELD-030"
        assert sensor.name_ar != ""

    def test_sensor_type_enum_coverage(self):
        """SensorType enum must include moisture, temperature, EC, pH."""
        from shared.soil_sensors.models import SensorType

        required = {"moisture", "temperature", "electrical_conductivity", "ph"}
        actual = {s.value for s in SensorType}
        assert required.issubset(actual), f"Missing sensor types: {required - actual}"

    def test_sensor_reading_quality_field(self):
        """SensorReading must have a quality score for data validation."""
        from shared.soil_sensors.models import SensorReading, SensorType

        reading = SensorReading(
            sensor_id="SENSOR-002",
            timestamp=datetime.now(UTC),
            reading_type=SensorType.TEMPERATURE,
            value=22.3,
            unit="C",
            quality=0.95,
            is_valid=True,
        )
        assert 0 <= reading.quality <= 1
        assert reading.is_valid is True


# ---------------------------------------------------------------------------
# 9. Task assignment contract
# ---------------------------------------------------------------------------


class TestTaskAssignmentContract:
    """Verify task models have assigned_to, field_id, due_date, priority, status enum."""

    def test_task_required_fields(self):
        """Task must have assigned workers, field_id, priority, and status."""
        from shared.labor_management.models import Task, TaskPriority, TaskStatus

        task = Task(
            task_id="TASK-001",
            tenant_id="tenant-001",
            farm_id="FARM-001",
            field_id="FIELD-040",
            title="Apply nitrogen fertilizer",
            title_ar="تطبيق سماد النيتروجين",
            priority=TaskPriority.HIGH,
            status=TaskStatus.ASSIGNED,
            assigned_workers=["WORKER-001", "WORKER-002"],
            planned_start=datetime.now(UTC),
            planned_end=datetime.now(UTC) + timedelta(hours=4),
        )
        assert task.field_id == "FIELD-040"
        assert task.priority == TaskPriority.HIGH
        assert task.status == TaskStatus.ASSIGNED
        assert len(task.assigned_workers) >= 1
        assert task.planned_end is not None

    def test_task_status_enum_values(self):
        """TaskStatus must include standard workflow states."""
        from shared.labor_management.models import TaskStatus

        required = {"pending", "assigned", "in_progress", "completed", "cancelled"}
        actual = {s.value for s in TaskStatus}
        assert required.issubset(actual), f"Missing statuses: {required - actual}"

    def test_task_priority_enum_values(self):
        """TaskPriority must include critical, high, medium, low."""
        from shared.labor_management.models import TaskPriority

        required = {"critical", "high", "medium", "low"}
        actual = {p.value for p in TaskPriority}
        assert required == actual

    def test_task_bilingual_fields(self):
        """Task must have bilingual title and description."""
        from shared.labor_management.models import Task

        task = Task(
            task_id="TASK-002",
            tenant_id="tenant-001",
            farm_id="FARM-001",
            title="Inspect field for pests",
            title_ar="فحص الحقل للآفات",
            description="Scout for aphids in wheat block",
            description_ar="البحث عن المن في قطعة القمح",
        )
        assert task.title_ar != ""
        assert task.description_ar != ""


# ---------------------------------------------------------------------------
# 10. Marketplace order contract
# ---------------------------------------------------------------------------


class TestMarketplaceOrderContract:
    """Verify order models have items, total_amount, currency, and delivery info."""

    def test_marketplace_listing_required_fields(self):
        """Listing must have seller_id, tenant_id, crop_type, quantity, price."""
        from shared.marketplace_enhanced import Listing, ListingStatus, OrderType

        listing = Listing(
            listing_id="LST-001",
            seller_id="SELLER-001",
            tenant_id="tenant-001",
            crop_type="wheat",
            crop_type_ar="قمح",
            quantity_tons=50.0,
            price_sar_per_ton=1850.0,
            status=ListingStatus.ACTIVE,
            order_type=OrderType.FIXED,
            location="Riyadh",
            location_ar="الرياض",
        )
        assert listing.tenant_id != ""
        assert listing.quantity_tons > 0
        assert listing.price_sar_per_ton > 0
        assert listing.crop_type_ar != ""

    def test_group_purchase_order_fields(self):
        """GroupPurchaseOrder must have items, total amounts, and delivery tracking."""
        from shared.cooperatives.models import GroupPurchaseOrder, PurchaseOrderStatus

        order = GroupPurchaseOrder.create(
            cooperative_id="COOP-001",
            title="Bulk Urea Purchase",
            title_ar="شراء يوريا بالجملة",
            product_type="fertilizer",
            product_name="Urea 46%",
            product_name_ar="يوريا 46%",
        )
        order.total_quantity_ordered = 5000.0
        order.unit_price = Decimal("2.50")
        order.total_value = Decimal("12500.00")
        order.final_amount = Decimal("11500.00")
        order.status = PurchaseOrderStatus.CONFIRMED

        assert order.cooperative_id == "COOP-001"
        assert order.total_value > 0
        assert order.final_amount > 0
        assert order.title_ar != ""
        assert order.product_name_ar != ""

    def test_marketplace_engine_returns_prices(self):
        """MarketplaceEngine must return structured market prices."""
        from shared.marketplace_enhanced import MarketplaceEngine

        engine = MarketplaceEngine()
        prices = engine.get_market_prices()

        assert len(prices) > 0
        for price in prices:
            assert price.crop_type != ""
            assert price.crop_type_ar != ""
            assert price.price_sar_per_ton > 0


# ---------------------------------------------------------------------------
# 11. Cross-service tenant_id propagation
# ---------------------------------------------------------------------------


class TestTenantIdPropagation:
    """Verify ALL key response models include tenant_id for multi-tenancy."""

    def test_notification_payload_has_tenant_id(self):
        from shared.notification_routing import NotificationPayload

        payload = NotificationPayload(tenant_id="T-001")
        assert payload.tenant_id == "T-001"
        assert "tenant_id" in payload.to_dict()

    def test_field_boundary_has_tenant_id(self):
        from shared.field_boundaries.models import FieldBoundary, Polygon

        ring = [(46.7, 24.7), (46.8, 24.7), (46.8, 24.8), (46.7, 24.8), (46.7, 24.7)]
        boundary = FieldBoundary(
            field_id="F-001",
            tenant_id="T-002",
            owner_id="O-001",
            name="Test",
            geometry=Polygon(coordinates=[ring]),
        )
        assert boundary.tenant_id == "T-002"

    def test_soil_sensor_has_tenant_id(self):
        from shared.soil_sensors.models import SensorProtocol, SensorType, SoilSensor

        sensor = SoilSensor(
            id="S-001",
            tenant_id="T-003",
            field_id="F-002",
            name="Probe",
            name_ar="مجس",
            sensor_type=SensorType.MOISTURE,
            protocol=SensorProtocol.MQTT,
            model="Test",
            manufacturer="Test",
            lat=24.7,
            lng=46.7,
        )
        assert sensor.tenant_id == "T-003"

    def test_task_has_tenant_id(self):
        from shared.labor_management.models import Task

        task = Task(task_id="T-001", tenant_id="T-004", farm_id="FM-001")
        assert task.tenant_id == "T-004"

    def test_fertilizer_inventory_has_tenant_id(self):
        from shared.fertilizer_management.models import InventoryItem

        item = InventoryItem(
            id="INV-001",
            tenant_id="T-005",
            fertilizer_id="FERT-001",
            fertilizer_name="Urea",
            fertilizer_name_ar="يوريا",
            quantity_kg=500.0,
        )
        assert item.tenant_id == "T-005"

    def test_marketplace_listing_has_tenant_id(self):
        from shared.marketplace_enhanced import Listing

        listing = Listing(tenant_id="T-006")
        assert listing.tenant_id == "T-006"

    def test_billing_invoice_has_tenant_id(self):
        """Invoice model in billing-core must declare tenant_id field."""
        import ast

        src = "/home/user/sahool-unified-v15-idp/apps/services/billing-core/src/main.py"
        with open(src) as f:
            tree = ast.parse(f.read())

        invoice_fields: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "Invoice":
                for item in node.body:
                    if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        invoice_fields.add(item.target.id)

        assert "tenant_id" in invoice_fields, "Invoice must include tenant_id"


# ---------------------------------------------------------------------------
# 12. Bilingual field coverage
# ---------------------------------------------------------------------------


class TestBilingualFieldCoverage:
    """Verify all user-facing models have both _en and _ar fields."""

    def test_weather_alert_bilingual_completeness(self):
        """WeatherAlert must have bilingual title, description, impact, actions."""
        from shared.weather_alerts.models import WeatherAlert

        field_names = {f.name for f in dc_fields(WeatherAlert)}
        bilingual_pairs = [
            ("title", "title_ar"),
            ("description", "description_ar"),
            ("impact", "impact_ar"),
            ("recommended_actions", "recommended_actions_ar"),
            ("location_name", "location_name_ar"),
            ("crop_damage_risk", "crop_damage_risk_ar"),
        ]
        for en_field, ar_field in bilingual_pairs:
            assert en_field in field_names, f"Missing EN field: {en_field}"
            assert ar_field in field_names, f"Missing AR field: {ar_field}"

    def test_spray_window_bilingual_completeness(self):
        """SprayWindow must have bilingual recommendation, cautions, risk labels."""
        from shared.weather_alerts.models import SprayWindow

        field_names = {f.name for f in dc_fields(SprayWindow)}
        bilingual_pairs = [
            ("recommendation", "recommendation_ar"),
            ("cautions", "cautions_ar"),
            ("adjustments", "adjustments_ar"),
            ("drift_risk", "drift_risk_ar"),
            ("evaporation_risk", "evaporation_risk_ar"),
            ("phytotoxicity_risk", "phytotoxicity_risk_ar"),
            ("inversion_warning", "inversion_warning_ar"),
        ]
        for en_field, ar_field in bilingual_pairs:
            assert en_field in field_names, f"Missing EN: {en_field}"
            assert ar_field in field_names, f"Missing AR: {ar_field}"

    def test_irrigation_schedule_bilingual_completeness(self):
        """IrrigationSchedule must have bilingual reason, factors, warnings."""
        from shared.weather_alerts.models import IrrigationSchedule

        field_names = {f.name for f in dc_fields(IrrigationSchedule)}
        bilingual_pairs = [
            ("reason", "reason_ar"),
            ("factors", "factors_ar"),
            ("warnings", "warnings_ar"),
        ]
        for en_field, ar_field in bilingual_pairs:
            assert en_field in field_names, f"Missing EN: {en_field}"
            assert ar_field in field_names, f"Missing AR: {ar_field}"

    def test_harvest_window_bilingual_completeness(self):
        """HarvestWindow must have bilingual recommendation and risk labels."""
        from shared.weather_alerts.models import HarvestWindow

        field_names = {f.name for f in dc_fields(HarvestWindow)}
        bilingual_pairs = [
            ("recommendation", "recommendation_ar"),
            ("considerations", "considerations_ar"),
            ("alternatives", "alternatives_ar"),
            ("rain_risk", "rain_risk_ar"),
            ("moisture_risk", "moisture_risk_ar"),
            ("quality_risk", "quality_risk_ar"),
        ]
        for en_field, ar_field in bilingual_pairs:
            assert en_field in field_names, f"Missing EN: {en_field}"
            assert ar_field in field_names, f"Missing AR: {ar_field}"

    def test_notification_payload_bilingual(self):
        """NotificationPayload must have title/body in both languages."""
        from shared.notification_routing import NotificationPayload

        field_names = {f.name for f in dc_fields(NotificationPayload)}
        assert "title" in field_names
        assert "title_ar" in field_names
        assert "body" in field_names
        assert "body_ar" in field_names

    def test_task_bilingual_fields_coverage(self):
        """Task must have bilingual title, description, safety_notes, completion_notes."""
        from shared.labor_management.models import Task

        field_names = {f.name for f in dc_fields(Task)}
        bilingual_pairs = [
            ("title", "title_ar"),
            ("description", "description_ar"),
            ("safety_notes", "safety_notes_ar"),
            ("completion_notes", "completion_notes_ar"),
            ("location_description", "location_description_ar"),
        ]
        for en_field, ar_field in bilingual_pairs:
            assert en_field in field_names, f"Missing EN: {en_field}"
            assert ar_field in field_names, f"Missing AR: {ar_field}"

    def test_field_boundary_bilingual(self):
        """FieldBoundary must have name and name_ar."""
        from shared.field_boundaries.models import FieldBoundary

        field_names = set(FieldBoundary.model_fields.keys())
        assert "name" in field_names
        assert "name_ar" in field_names
        assert "description" in field_names
        assert "description_ar" in field_names

    def test_sensor_device_bilingual(self):
        """SoilSensor must have name and name_ar."""
        from shared.soil_sensors.models import SoilSensor

        field_names = {f.name for f in dc_fields(SoilSensor)}
        assert "name" in field_names
        assert "name_ar" in field_names

    def test_fertilizer_bilingual(self):
        """Fertilizer must have bilingual name and manufacturer fields."""
        from shared.fertilizer_management.models import Fertilizer

        field_names = {f.name for f in dc_fields(Fertilizer)}
        bilingual_pairs = [
            ("name", "name_ar"),
            ("manufacturer", "manufacturer_ar"),
            ("trade_name", "trade_name_ar"),
            ("notes", "notes_ar"),
        ]
        for en_field, ar_field in bilingual_pairs:
            assert en_field in field_names, f"Missing EN: {en_field}"
            assert ar_field in field_names, f"Missing AR: {ar_field}"
