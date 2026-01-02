"""
SAHOOL Drone Edge Agent
وكيل الطائرة بدون طيار الطرفي

On-board drone processing for:
- Real-time NDVI calculation
- Field boundary detection
- Crop health assessment
- Irrigation mapping
- Pest/Disease hotspot detection

Target response time: < 100ms for decisions
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import asyncio
import logging
import math

from ..base_agent import (
    BaseAgent, AgentType, AgentLayer, AgentStatus,
    AgentContext, AgentAction, AgentPercept
)

logger = logging.getLogger(__name__)


@dataclass
class DronePosition:
    """موقع الطائرة"""
    latitude: float
    longitude: float
    altitude: float  # meters
    heading: float   # degrees
    speed: float     # m/s


@dataclass
class ImageTile:
    """قطعة صورة"""
    tile_id: str
    center_lat: float
    center_lon: float
    ndvi_value: Optional[float] = None
    health_status: str = "unknown"
    anomaly_detected: bool = False


class DroneAgent(BaseAgent):
    """
    وكيل الطائرة بدون طيار الطرفي
    Drone Edge Agent for aerial field analysis
    """

    # NDVI interpretation thresholds
    NDVI_THRESHOLDS = {
        "bare_soil": (-1.0, 0.1),
        "stressed": (0.1, 0.2),
        "moderate_stress": (0.2, 0.3),
        "moderate_health": (0.3, 0.5),
        "healthy": (0.5, 0.7),
        "very_healthy": (0.7, 1.0)
    }

    # Mission types
    MISSION_TYPES = {
        "survey": "مسح شامل",
        "health_check": "فحص صحة المحصول",
        "irrigation_map": "خريطة الري",
        "pest_detection": "كشف الآفات",
        "boundary_map": "رسم الحدود"
    }

    def __init__(self, agent_id: str = "drone_edge_001", drone_id: str = ""):
        super().__init__(
            agent_id=agent_id,
            name="Drone Edge Agent",
            name_ar="وكيل الطائرة بدون طيار الطرفي",
            agent_type=AgentType.GOAL_BASED,  # Works towards mission goals
            layer=AgentLayer.EDGE,
            description="On-board drone processing for aerial field analysis",
            description_ar="معالجة على متن الطائرة لتحليل الحقل الجوي"
        )

        self.drone_id = drone_id

        # Current mission
        self.current_mission: Optional[Dict[str, Any]] = None
        self.mission_progress: float = 0.0

        # Position tracking
        self.current_position: Optional[DronePosition] = None
        self.flight_path: List[DronePosition] = []

        # Image tiles collected
        self.tiles: List[ImageTile] = []

        # Analysis results
        self.field_analysis: Dict[str, Any] = {
            "ndvi_map": [],
            "health_zones": [],
            "stress_hotspots": [],
            "irrigation_zones": [],
            "boundaries": []
        }

        # Battery and safety
        self.battery_level: float = 100.0
        self.min_battery_for_return: float = 20.0

        # Goals for Goal-Based Agent
        self.state.goals = []

    async def perceive(self, percept: AgentPercept) -> None:
        """استقبال بيانات الطائرة"""
        if percept.percept_type == "position_update":
            self.current_position = DronePosition(**percept.data)
            self.flight_path.append(self.current_position)

        elif percept.percept_type == "image_capture":
            # Process captured image
            tile = await self._process_image(percept.data)
            self.tiles.append(tile)

            # Update context
            if self.context:
                self.context.satellite_data["latest_tile"] = tile.__dict__

        elif percept.percept_type == "battery_status":
            self.battery_level = percept.data.get("level", self.battery_level)

        elif percept.percept_type == "mission_start":
            self.current_mission = percept.data
            self.mission_progress = 0.0
            self._set_mission_goals(percept.data)

        elif percept.percept_type == "multispectral_data":
            # Direct NDVI from multispectral camera
            ndvi = self._calculate_ndvi(
                percept.data.get("red"),
                percept.data.get("nir")
            )
            if self.context:
                self.context.satellite_data["live_ndvi"] = ndvi

    async def _process_image(self, image_data: Dict[str, Any]) -> ImageTile:
        """معالجة الصورة الملتقطة"""
        tile_id = f"tile_{len(self.tiles):04d}"

        # Quick NDVI calculation if multispectral data available
        ndvi = None
        if "red_band" in image_data and "nir_band" in image_data:
            ndvi = self._calculate_ndvi(
                image_data["red_band"],
                image_data["nir_band"]
            )

        # Determine health status
        health_status = self._classify_ndvi(ndvi) if ndvi else "unknown"

        # Check for anomalies
        anomaly = await self._quick_anomaly_check(image_data)

        return ImageTile(
            tile_id=tile_id,
            center_lat=image_data.get("lat", 0),
            center_lon=image_data.get("lon", 0),
            ndvi_value=ndvi,
            health_status=health_status,
            anomaly_detected=anomaly
        )

    def _calculate_ndvi(self, red: float, nir: float) -> float:
        """حساب NDVI"""
        if nir + red == 0:
            return 0
        return (nir - red) / (nir + red)

    def _classify_ndvi(self, ndvi: float) -> str:
        """تصنيف قيمة NDVI"""
        for status, (min_val, max_val) in self.NDVI_THRESHOLDS.items():
            if min_val <= ndvi < max_val:
                return status
        return "unknown"

    async def _quick_anomaly_check(self, image_data: Dict[str, Any]) -> bool:
        """فحص سريع للشذوذ"""
        # Quick check for obvious anomalies
        # In production, this would use a lightweight CNN
        return False

    def _set_mission_goals(self, mission: Dict[str, Any]) -> None:
        """تعيين أهداف المهمة"""
        mission_type = mission.get("type", "survey")

        if mission_type == "survey":
            self.state.goals = [
                "cover_entire_field",
                "capture_all_tiles",
                "calculate_ndvi_map",
                "return_safely"
            ]
        elif mission_type == "health_check":
            self.state.goals = [
                "scan_problem_areas",
                "identify_stress_zones",
                "capture_detailed_images",
                "return_safely"
            ]
        elif mission_type == "pest_detection":
            self.state.goals = [
                "low_altitude_scan",
                "detect_pest_patterns",
                "mark_hotspots",
                "return_safely"
            ]

    async def think(self) -> Optional[AgentAction]:
        """التفكير واتخاذ القرار بناءً على الهدف"""
        # Safety check first
        if self.battery_level < self.min_battery_for_return:
            return AgentAction(
                action_type="emergency_return",
                parameters={"reason": "low_battery"},
                confidence=1.0,
                priority=1,
                reasoning="مستوى البطارية منخفض - العودة للقاعدة",
                source_agent=self.agent_id
            )

        # No mission - idle
        if not self.current_mission:
            return None

        # Check goals
        if "return_safely" in self.state.goals and self._mission_complete():
            return AgentAction(
                action_type="return_to_base",
                parameters={"mission_complete": True},
                confidence=0.95,
                priority=2,
                reasoning="اكتملت المهمة - العودة للقاعدة",
                source_agent=self.agent_id
            )

        # Check for urgent findings
        urgent_finding = await self._check_urgent_findings()
        if urgent_finding:
            return urgent_finding

        # Continue mission
        next_waypoint = self._calculate_next_waypoint()
        if next_waypoint:
            return AgentAction(
                action_type="navigate_to",
                parameters={"waypoint": next_waypoint},
                confidence=0.9,
                priority=3,
                reasoning="متابعة مسار المهمة",
                source_agent=self.agent_id
            )

        return None

    def _mission_complete(self) -> bool:
        """التحقق من اكتمال المهمة"""
        if not self.current_mission:
            return True

        target_coverage = self.current_mission.get("target_coverage", 100)
        return self.mission_progress >= target_coverage

    async def _check_urgent_findings(self) -> Optional[AgentAction]:
        """فحص النتائج العاجلة"""
        # Check latest tiles for critical issues
        recent_tiles = self.tiles[-5:] if len(self.tiles) >= 5 else self.tiles

        stress_count = sum(1 for t in recent_tiles if t.health_status in ["stressed", "moderate_stress"])
        anomaly_count = sum(1 for t in recent_tiles if t.anomaly_detected)

        if anomaly_count >= 2:
            return AgentAction(
                action_type="anomaly_cluster_alert",
                parameters={
                    "location": self.current_position.__dict__ if self.current_position else {},
                    "anomaly_count": anomaly_count,
                    "tiles": [t.tile_id for t in recent_tiles if t.anomaly_detected]
                },
                confidence=0.85,
                priority=1,
                reasoning=f"تم اكتشاف {anomaly_count} شذوذ في المنطقة الحالية",
                source_agent=self.agent_id
            )

        if stress_count >= 3:
            return AgentAction(
                action_type="stress_zone_detected",
                parameters={
                    "location": self.current_position.__dict__ if self.current_position else {},
                    "stress_level": "high",
                    "affected_tiles": stress_count
                },
                confidence=0.8,
                priority=2,
                reasoning=f"منطقة إجهاد مرتفع - {stress_count} قطع متأثرة",
                source_agent=self.agent_id
            )

        return None

    def _calculate_next_waypoint(self) -> Optional[Dict[str, float]]:
        """حساب نقطة الطريق التالية"""
        if not self.current_mission:
            return None

        waypoints = self.current_mission.get("waypoints", [])
        completed = len(self.tiles)

        if completed < len(waypoints):
            wp = waypoints[completed]
            self.mission_progress = (completed / len(waypoints)) * 100
            return {"lat": wp["lat"], "lon": wp["lon"], "alt": wp.get("alt", 50)}

        return None

    async def act(self, action: AgentAction) -> Dict[str, Any]:
        """تنفيذ الإجراء"""
        result = {
            "action_type": action.action_type,
            "executed_at": datetime.now().isoformat(),
            "success": True
        }

        if action.action_type == "navigate_to":
            result["flight_command"] = {
                "type": "goto",
                "waypoint": action.parameters.get("waypoint"),
                "speed": "normal"
            }

        elif action.action_type == "return_to_base":
            result["flight_command"] = {
                "type": "rtl",  # Return to Launch
                "reason": "mission_complete" if action.parameters.get("mission_complete") else "manual"
            }
            # Generate mission report
            result["mission_report"] = await self._generate_mission_report()

        elif action.action_type == "emergency_return":
            result["flight_command"] = {
                "type": "rtl",
                "speed": "fast",
                "reason": action.parameters.get("reason")
            }
            result["notification"] = {
                "type": "warning",
                "title": "عودة طارئة",
                "body": action.reasoning
            }

        elif action.action_type in ["anomaly_cluster_alert", "stress_zone_detected"]:
            result["notification"] = {
                "type": "alert",
                "title": "اكتشاف مهم",
                "body": action.reasoning,
                "data": action.parameters
            }
            # Mark location for detailed inspection
            result["marked_location"] = action.parameters.get("location")

        return result

    async def _generate_mission_report(self) -> Dict[str, Any]:
        """إنشاء تقرير المهمة"""
        if not self.tiles:
            return {"status": "no_data"}

        # Calculate statistics
        ndvi_values = [t.ndvi_value for t in self.tiles if t.ndvi_value is not None]
        health_counts = {}
        for t in self.tiles:
            health_counts[t.health_status] = health_counts.get(t.health_status, 0) + 1

        anomalies = [t for t in self.tiles if t.anomaly_detected]

        return {
            "mission_id": self.current_mission.get("id") if self.current_mission else "unknown",
            "tiles_captured": len(self.tiles),
            "coverage_percent": self.mission_progress,
            "ndvi_stats": {
                "mean": sum(ndvi_values) / len(ndvi_values) if ndvi_values else 0,
                "min": min(ndvi_values) if ndvi_values else 0,
                "max": max(ndvi_values) if ndvi_values else 0
            },
            "health_distribution": health_counts,
            "anomalies_detected": len(anomalies),
            "anomaly_locations": [
                {"tile_id": t.tile_id, "lat": t.center_lat, "lon": t.center_lon}
                for t in anomalies
            ],
            "flight_duration_minutes": len(self.flight_path) * 0.5,  # Approximate
            "battery_remaining": self.battery_level,
            "timestamp": datetime.now().isoformat()
        }

    def get_live_status(self) -> Dict[str, Any]:
        """الحصول على الحالة المباشرة"""
        return {
            "position": self.current_position.__dict__ if self.current_position else None,
            "battery": self.battery_level,
            "mission_progress": self.mission_progress,
            "tiles_captured": len(self.tiles),
            "current_goals": self.state.goals,
            "status": self.status.value
        }
