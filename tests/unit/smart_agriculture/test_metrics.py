"""
SAHOOL Smart Agriculture - Metrics Tests
اختبارات المقاييس للزراعة الذكية

Tests for metrics including:
- Management radius
- Labor cost reduction
- Failure response time
- Detection accuracy

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

# ==============================================================================
# Metrics Components (Test Target Mocks)
# ==============================================================================


class MetricsCollector:
    """Collects and calculates smart agriculture metrics"""

    def __init__(self, farm_id: str):
        self.farm_id = farm_id
        self._incidents: list[dict[str, Any]] = []
        self._detections: list[dict[str, Any]] = []
        self._operations: list[dict[str, Any]] = []

    def record_incident(self, incident: dict[str, Any]) -> None:
        """Record a system incident"""
        incident["recorded_at"] = datetime.now(UTC).isoformat()
        self._incidents.append(incident)

    def record_detection(self, detection: dict[str, Any]) -> None:
        """Record a detection event"""
        detection["recorded_at"] = datetime.now(UTC).isoformat()
        self._detections.append(detection)

    def record_operation(self, operation: dict[str, Any]) -> None:
        """Record a farm operation"""
        operation["recorded_at"] = datetime.now(UTC).isoformat()
        self._operations.append(operation)

    def calculate_management_radius(
        self,
        field_locations: list[dict[str, float]],
        base_location: dict[str, float],
    ) -> dict[str, Any]:
        """
        Calculate management radius from base location
        حساب نصف قطر الإدارة من الموقع الأساسي
        """
        if not field_locations:
            return {
                "radius_km": 0.0,
                "fields_count": 0,
                "coverage_area_km2": 0.0,
            }

        import math

        max_distance = 0.0
        distances = []

        for field in field_locations:
            # Haversine formula for distance calculation
            lat1 = math.radians(base_location["latitude"])
            lat2 = math.radians(field["latitude"])
            lon1 = math.radians(base_location["longitude"])
            lon2 = math.radians(field["longitude"])

            dlat = lat2 - lat1
            dlon = lon2 - lon1

            a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
            c = 2 * math.asin(math.sqrt(a))
            r = 6371  # Earth radius in km

            distance = r * c
            distances.append(distance)
            max_distance = max(max_distance, distance)

        return {
            "radius_km": round(max_distance, 2),
            "fields_count": len(field_locations),
            "average_distance_km": round(sum(distances) / len(distances), 2),
            "coverage_area_km2": round(math.pi * max_distance**2, 2),
        }

    def calculate_labor_cost_reduction(
        self,
        traditional_hours: float,
        automated_hours: float,
        hourly_rate: float,
    ) -> dict[str, Any]:
        """
        Calculate labor cost reduction
        حساب تخفيض تكلفة العمالة
        """
        if traditional_hours <= 0:
            raise ValueError("Traditional hours must be positive")

        hours_saved = traditional_hours - automated_hours
        cost_saved = hours_saved * hourly_rate
        reduction_percent = (hours_saved / traditional_hours) * 100

        return {
            "traditional_hours": traditional_hours,
            "automated_hours": automated_hours,
            "hours_saved": round(hours_saved, 1),
            "cost_saved": round(cost_saved, 2),
            "reduction_percent": round(reduction_percent, 1),
            "hourly_rate": hourly_rate,
        }

    def calculate_failure_response_time(self) -> dict[str, Any]:
        """
        Calculate average failure response time
        حساب متوسط وقت الاستجابة للفشل
        """
        if not self._incidents:
            return {
                "total_incidents": 0,
                "average_response_minutes": 0.0,
                "max_response_minutes": 0.0,
                "min_response_minutes": 0.0,
            }

        response_times = []
        for incident in self._incidents:
            detected_at = datetime.fromisoformat(incident["detected_at"].replace("Z", "+00:00"))
            resolved_at = incident.get("resolved_at")
            if resolved_at:
                resolved = datetime.fromisoformat(resolved_at.replace("Z", "+00:00"))
                response_time = (resolved - detected_at).total_seconds() / 60
                response_times.append(response_time)

        if not response_times:
            return {
                "total_incidents": len(self._incidents),
                "resolved_incidents": 0,
                "average_response_minutes": None,
            }

        return {
            "total_incidents": len(self._incidents),
            "resolved_incidents": len(response_times),
            "average_response_minutes": round(sum(response_times) / len(response_times), 1),
            "max_response_minutes": round(max(response_times), 1),
            "min_response_minutes": round(min(response_times), 1),
            "within_sla_count": sum(1 for t in response_times if t <= 15),  # 15 min SLA
        }

    def calculate_detection_accuracy(self) -> dict[str, Any]:
        """
        Calculate detection accuracy metrics
        حساب مقاييس دقة الكشف
        """
        if not self._detections:
            return {
                "total_detections": 0,
                "accuracy_percent": None,
            }

        true_positives = sum(1 for d in self._detections if d.get("predicted") and d.get("actual"))
        false_positives = sum(1 for d in self._detections if d.get("predicted") and not d.get("actual"))
        true_negatives = sum(1 for d in self._detections if not d.get("predicted") and not d.get("actual"))
        false_negatives = sum(1 for d in self._detections if not d.get("predicted") and d.get("actual"))

        total = true_positives + false_positives + true_negatives + false_negatives

        if total == 0:
            return {"total_detections": 0, "accuracy_percent": None}

        accuracy = (true_positives + true_negatives) / total * 100

        # Calculate precision and recall
        precision = true_positives / max(true_positives + false_positives, 1) * 100
        recall = true_positives / max(true_positives + false_negatives, 1) * 100

        # F1 score
        if precision + recall > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
        else:
            f1 = 0

        return {
            "total_detections": total,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "true_negatives": true_negatives,
            "false_negatives": false_negatives,
            "accuracy_percent": round(accuracy, 1),
            "precision_percent": round(precision, 1),
            "recall_percent": round(recall, 1),
            "f1_score": round(f1, 1),
        }

    def get_comprehensive_metrics(self) -> dict[str, Any]:
        """Get comprehensive metrics summary"""
        return {
            "farm_id": self.farm_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "failure_response": self.calculate_failure_response_time(),
            "detection_accuracy": self.calculate_detection_accuracy(),
            "total_operations": len(self._operations),
            "total_incidents": len(self._incidents),
        }


class EfficiencyMetrics:
    """Calculate efficiency metrics for smart agriculture"""

    @staticmethod
    def calculate_water_efficiency(
        water_used_m3: float,
        water_needed_m3: float,
    ) -> dict[str, Any]:
        """
        Calculate water use efficiency
        حساب كفاءة استخدام المياه
        """
        if water_needed_m3 <= 0:
            raise ValueError("Water needed must be positive")

        efficiency = min(100, (water_needed_m3 / water_used_m3) * 100) if water_used_m3 > 0 else 0
        waste = max(0, water_used_m3 - water_needed_m3)
        waste_percent = (waste / water_used_m3) * 100 if water_used_m3 > 0 else 0

        return {
            "water_used_m3": water_used_m3,
            "water_needed_m3": water_needed_m3,
            "efficiency_percent": round(efficiency, 1),
            "waste_m3": round(waste, 2),
            "waste_percent": round(waste_percent, 1),
        }

    @staticmethod
    def calculate_fertilizer_efficiency(
        applied_kg: float,
        absorbed_kg: float,
    ) -> dict[str, Any]:
        """
        Calculate fertilizer use efficiency
        حساب كفاءة استخدام الأسمدة
        """
        if applied_kg <= 0:
            raise ValueError("Applied fertilizer must be positive")

        efficiency = min(100, (absorbed_kg / applied_kg) * 100)
        loss = max(0, applied_kg - absorbed_kg)
        loss_percent = (loss / applied_kg) * 100

        return {
            "applied_kg": applied_kg,
            "absorbed_kg": absorbed_kg,
            "efficiency_percent": round(efficiency, 1),
            "loss_kg": round(loss, 2),
            "loss_percent": round(loss_percent, 1),
        }

    @staticmethod
    def calculate_energy_efficiency(
        energy_consumed_kwh: float,
        productive_output: float,
        output_unit: str = "kg",
    ) -> dict[str, Any]:
        """
        Calculate energy efficiency
        حساب كفاءة الطاقة
        """
        if energy_consumed_kwh <= 0:
            raise ValueError("Energy consumed must be positive")

        efficiency = productive_output / energy_consumed_kwh

        return {
            "energy_consumed_kwh": energy_consumed_kwh,
            "productive_output": productive_output,
            "output_unit": output_unit,
            "efficiency_ratio": round(efficiency, 2),
            "unit": f"{output_unit}/kWh",
        }


# ==============================================================================
# Test Classes
# ==============================================================================


class TestManagementRadius:
    """Tests for management radius calculation"""

    @pytest.fixture
    def collector(self) -> MetricsCollector:
        return MetricsCollector(farm_id=str(uuid.uuid4()))

    def test_calculate_management_radius_single_field(self, collector: MetricsCollector):
        """Test management radius with single field"""
        base = {"latitude": 24.7136, "longitude": 46.6753}
        fields = [{"latitude": 24.7236, "longitude": 46.6853}]

        result = collector.calculate_management_radius(fields, base)

        assert result["fields_count"] == 1
        assert result["radius_km"] > 0
        assert result["radius_km"] < 2  # Should be close

    def test_calculate_management_radius_multiple_fields(self, collector: MetricsCollector):
        """Test management radius with multiple fields"""
        base = {"latitude": 24.7136, "longitude": 46.6753}
        fields = [
            {"latitude": 24.7236, "longitude": 46.6853},  # Close
            {"latitude": 24.8136, "longitude": 46.7753},  # Far
            {"latitude": 24.6136, "longitude": 46.5753},  # Another direction
        ]

        result = collector.calculate_management_radius(fields, base)

        assert result["fields_count"] == 3
        assert result["average_distance_km"] > 0
        assert result["coverage_area_km2"] > 0

    def test_calculate_management_radius_empty_fields(self, collector: MetricsCollector):
        """Test management radius with no fields"""
        base = {"latitude": 24.7136, "longitude": 46.6753}

        result = collector.calculate_management_radius([], base)

        assert result["radius_km"] == 0.0
        assert result["fields_count"] == 0

    def test_management_radius_real_distance(self, collector: MetricsCollector):
        """Test management radius calculates reasonable real-world distance"""
        # Riyadh center to 50km away (approximately 0.45 degrees)
        base = {"latitude": 24.7136, "longitude": 46.6753}
        fields = [{"latitude": 25.1636, "longitude": 46.6753}]  # ~50km north

        result = collector.calculate_management_radius(fields, base)

        # Should be approximately 50km (within 10% margin)
        assert 45 < result["radius_km"] < 55


class TestLaborCostReduction:
    """Tests for labor cost reduction calculation"""

    @pytest.fixture
    def collector(self) -> MetricsCollector:
        return MetricsCollector(farm_id=str(uuid.uuid4()))

    def test_calculate_labor_cost_reduction(self, collector: MetricsCollector):
        """Test labor cost reduction calculation"""
        result = collector.calculate_labor_cost_reduction(
            traditional_hours=100,
            automated_hours=60,
            hourly_rate=50,
        )

        assert result["hours_saved"] == 40
        assert result["cost_saved"] == 2000
        assert result["reduction_percent"] == 40.0

    def test_labor_cost_zero_automated_hours(self, collector: MetricsCollector):
        """Test labor cost reduction with full automation"""
        result = collector.calculate_labor_cost_reduction(
            traditional_hours=100,
            automated_hours=0,
            hourly_rate=50,
        )

        assert result["hours_saved"] == 100
        assert result["reduction_percent"] == 100.0

    def test_labor_cost_no_reduction(self, collector: MetricsCollector):
        """Test labor cost with no reduction"""
        result = collector.calculate_labor_cost_reduction(
            traditional_hours=100,
            automated_hours=100,
            hourly_rate=50,
        )

        assert result["hours_saved"] == 0
        assert result["reduction_percent"] == 0.0

    def test_labor_cost_zero_traditional_fails(self, collector: MetricsCollector):
        """Test labor cost calculation fails with zero traditional hours"""
        with pytest.raises(ValueError, match="must be positive"):
            collector.calculate_labor_cost_reduction(
                traditional_hours=0,
                automated_hours=50,
                hourly_rate=50,
            )


class TestFailureResponse:
    """Tests for failure response time calculation"""

    @pytest.fixture
    def collector(self) -> MetricsCollector:
        return MetricsCollector(farm_id=str(uuid.uuid4()))

    def test_calculate_failure_response_no_incidents(self, collector: MetricsCollector):
        """Test failure response with no incidents"""
        result = collector.calculate_failure_response_time()

        assert result["total_incidents"] == 0
        assert result["average_response_minutes"] == 0.0

    def test_calculate_failure_response_single_incident(self, collector: MetricsCollector):
        """Test failure response with single incident"""
        now = datetime.now(UTC)
        collector.record_incident(
            {
                "incident_id": str(uuid.uuid4()),
                "type": "sensor_failure",
                "detected_at": now.isoformat(),
                "resolved_at": (now + timedelta(minutes=10)).isoformat(),
            }
        )

        result = collector.calculate_failure_response_time()

        assert result["total_incidents"] == 1
        assert result["resolved_incidents"] == 1
        assert 9 < result["average_response_minutes"] < 11

    def test_calculate_failure_response_multiple_incidents(self, collector: MetricsCollector):
        """Test failure response with multiple incidents"""
        now = datetime.now(UTC)

        # 5 minute response
        collector.record_incident(
            {
                "incident_id": str(uuid.uuid4()),
                "detected_at": now.isoformat(),
                "resolved_at": (now + timedelta(minutes=5)).isoformat(),
            }
        )

        # 15 minute response
        collector.record_incident(
            {
                "incident_id": str(uuid.uuid4()),
                "detected_at": now.isoformat(),
                "resolved_at": (now + timedelta(minutes=15)).isoformat(),
            }
        )

        result = collector.calculate_failure_response_time()

        assert result["total_incidents"] == 2
        assert result["average_response_minutes"] == 10.0
        assert result["max_response_minutes"] == 15.0
        assert result["min_response_minutes"] == 5.0

    def test_failure_response_within_sla(self, collector: MetricsCollector):
        """Test SLA compliance tracking"""
        now = datetime.now(UTC)

        # Within SLA (15 min)
        for _ in range(3):
            collector.record_incident(
                {
                    "detected_at": now.isoformat(),
                    "resolved_at": (now + timedelta(minutes=10)).isoformat(),
                }
            )

        # Outside SLA
        for _ in range(2):
            collector.record_incident(
                {
                    "detected_at": now.isoformat(),
                    "resolved_at": (now + timedelta(minutes=20)).isoformat(),
                }
            )

        result = collector.calculate_failure_response_time()

        assert result["within_sla_count"] == 3


class TestDetectionAccuracy:
    """Tests for detection accuracy calculation"""

    @pytest.fixture
    def collector(self) -> MetricsCollector:
        return MetricsCollector(farm_id=str(uuid.uuid4()))

    def test_calculate_detection_accuracy_no_detections(self, collector: MetricsCollector):
        """Test detection accuracy with no detections"""
        result = collector.calculate_detection_accuracy()

        assert result["total_detections"] == 0
        assert result["accuracy_percent"] is None

    def test_calculate_detection_accuracy_perfect(self, collector: MetricsCollector):
        """Test detection accuracy with perfect predictions"""
        # All true positives and true negatives
        for _ in range(5):
            collector.record_detection({"predicted": True, "actual": True})
            collector.record_detection({"predicted": False, "actual": False})

        result = collector.calculate_detection_accuracy()

        assert result["accuracy_percent"] == 100.0
        assert result["precision_percent"] == 100.0
        assert result["recall_percent"] == 100.0

    def test_calculate_detection_accuracy_with_errors(self, collector: MetricsCollector):
        """Test detection accuracy with some errors"""
        # 80 true positives
        for _ in range(80):
            collector.record_detection({"predicted": True, "actual": True})

        # 10 false positives
        for _ in range(10):
            collector.record_detection({"predicted": True, "actual": False})

        # 5 false negatives
        for _ in range(5):
            collector.record_detection({"predicted": False, "actual": True})

        # 5 true negatives
        for _ in range(5):
            collector.record_detection({"predicted": False, "actual": False})

        result = collector.calculate_detection_accuracy()

        assert result["total_detections"] == 100
        assert result["true_positives"] == 80
        assert result["false_positives"] == 10
        assert result["accuracy_percent"] == 85.0

    def test_detection_precision_recall(self, collector: MetricsCollector):
        """Test precision and recall calculation"""
        # 90 TP, 10 FP, 10 FN, 90 TN
        for _ in range(90):
            collector.record_detection({"predicted": True, "actual": True})
        for _ in range(10):
            collector.record_detection({"predicted": True, "actual": False})
        for _ in range(10):
            collector.record_detection({"predicted": False, "actual": True})
        for _ in range(90):
            collector.record_detection({"predicted": False, "actual": False})

        result = collector.calculate_detection_accuracy()

        # Precision = 90 / (90 + 10) = 90%
        assert result["precision_percent"] == 90.0

        # Recall = 90 / (90 + 10) = 90%
        assert result["recall_percent"] == 90.0

        # F1 = 2 * (0.9 * 0.9) / (0.9 + 0.9) = 90%
        assert result["f1_score"] == 90.0

    def test_comprehensive_metrics(self, collector: MetricsCollector):
        """Test comprehensive metrics summary"""
        # Add some data
        collector.record_detection({"predicted": True, "actual": True})
        collector.record_operation({"type": "irrigation"})

        now = datetime.now(UTC)
        collector.record_incident(
            {
                "detected_at": now.isoformat(),
                "resolved_at": (now + timedelta(minutes=5)).isoformat(),
            }
        )

        result = collector.get_comprehensive_metrics()

        assert result["farm_id"] == collector.farm_id
        assert "failure_response" in result
        assert "detection_accuracy" in result
        assert result["total_operations"] == 1


class TestEfficiencyMetrics:
    """Tests for efficiency metrics calculations"""

    def test_water_efficiency_calculation(self):
        """Test water efficiency calculation"""
        result = EfficiencyMetrics.calculate_water_efficiency(
            water_used_m3=1000,
            water_needed_m3=800,
        )

        assert result["efficiency_percent"] == 80.0
        assert result["waste_m3"] == 200
        assert result["waste_percent"] == 20.0

    def test_water_efficiency_perfect(self):
        """Test water efficiency with perfect usage"""
        result = EfficiencyMetrics.calculate_water_efficiency(
            water_used_m3=800,
            water_needed_m3=800,
        )

        assert result["efficiency_percent"] == 100.0
        assert result["waste_m3"] == 0

    def test_water_efficiency_zero_needed_fails(self):
        """Test water efficiency fails with zero needed"""
        with pytest.raises(ValueError, match="must be positive"):
            EfficiencyMetrics.calculate_water_efficiency(
                water_used_m3=100,
                water_needed_m3=0,
            )

    def test_fertilizer_efficiency_calculation(self):
        """Test fertilizer efficiency calculation"""
        result = EfficiencyMetrics.calculate_fertilizer_efficiency(
            applied_kg=100,
            absorbed_kg=70,
        )

        assert result["efficiency_percent"] == 70.0
        assert result["loss_kg"] == 30
        assert result["loss_percent"] == 30.0

    def test_fertilizer_efficiency_zero_applied_fails(self):
        """Test fertilizer efficiency fails with zero applied"""
        with pytest.raises(ValueError, match="must be positive"):
            EfficiencyMetrics.calculate_fertilizer_efficiency(
                applied_kg=0,
                absorbed_kg=50,
            )

    def test_energy_efficiency_calculation(self):
        """Test energy efficiency calculation"""
        result = EfficiencyMetrics.calculate_energy_efficiency(
            energy_consumed_kwh=500,
            productive_output=2500,
            output_unit="kg",
        )

        assert result["efficiency_ratio"] == 5.0
        assert result["unit"] == "kg/kWh"

    def test_energy_efficiency_zero_energy_fails(self):
        """Test energy efficiency fails with zero energy"""
        with pytest.raises(ValueError, match="must be positive"):
            EfficiencyMetrics.calculate_energy_efficiency(
                energy_consumed_kwh=0,
                productive_output=1000,
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
