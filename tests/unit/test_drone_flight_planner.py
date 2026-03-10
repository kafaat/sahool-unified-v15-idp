"""Tests for drone flight planner."""

import pytest
from shared.drone_integration.advanced_flight_planner import (
    DroneFlightPlanner,
    DroneType,
    MissionType,
    FlightStatus,
    DRONE_SPECS,
)


class TestDroneFlightPlanner:
    def setup_method(self):
        self.planner = DroneFlightPlanner()

    def test_gsd_calculation(self):
        gsd = self.planner.calculate_gsd(50)
        assert gsd > 0
        assert gsd < 5  # Should be reasonable for 50m

    def test_plan_mapping_flight(self):
        plan = self.planner.plan_mapping_flight(
            field_id="F-001",
            tenant_id="T-001",
            center_lat=15.3,
            center_lon=44.2,
            area_hectares=10,
        )
        assert plan.status == FlightStatus.PLANNED
        assert plan.total_images > 0
        assert plan.estimated_flight_time_min > 0
        assert plan.message_ar != ""

    def test_plan_spray_mission(self):
        plan = self.planner.plan_spray_mission(
            field_id="F-001",
            area_hectares=5,
            spray_rate_l_ha=10,
            product="Pesticide A",
            product_ar="مبيد أ",
        )
        assert plan.total_volume_liters == 50
        assert plan.estimated_time_min > 0

    def test_all_drone_types_have_specs(self):
        for drone_type in [DroneType.DJI_MAVIC, DroneType.DJI_PHANTOM, DroneType.DJI_MATRICE]:
            assert drone_type in DRONE_SPECS

    def test_flight_lines_calculation(self):
        lines = self.planner.calculate_flight_lines(200, 65, 50)
        assert lines > 0
