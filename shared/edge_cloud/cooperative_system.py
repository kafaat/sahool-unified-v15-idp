"""
Edge-Cloud Cooperative System - Smart Agriculture
=================================================
نظام التعاون بين الحافة والسحابة - الزراعة الذكية

The cooperative system integrates all three layers (perception, edge, cloud)
to provide a comprehensive smart agriculture solution with:
- Real-time data collection from 200+ device types
- Edge processing with 300ms latency and offline autonomy
- Cloud AI for high-accuracy inference
- Seamless edge-cloud synchronization

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any, Callable
from uuid import uuid4

import structlog

from .cloud_layer import get_cloud_layer
from .edge_layer import get_edge_layer
from .models import (
    CloudInference,
    DeviceConfig,
    DeviceProtocol,
    EdgeDecision,
    IFTTTRule,
    Recommendation,
    SamplingConfig,
    SensorReading,
    SensorType,
    SystemMetrics,
)
from .perception_layer import get_perception_layer

# Configure structured logging
logger = structlog.get_logger(__name__)


# =============================================================================
# Sync Manager - مدير المزامنة
# =============================================================================


class SyncManager:
    """
    Manages synchronization between edge and cloud layers.
    يدير المزامنة بين طبقتي الحافة والسحابة

    Handles bidirectional sync of:
    - Sensor data (edge -> cloud)
    - Decisions and inferences (edge <-> cloud)
    - Model updates (cloud -> edge)
    - Rule updates (cloud -> edge)
    """

    def __init__(self):
        """Initialize sync manager."""
        self._pending_uploads: list[dict[str, Any]] = []
        self._pending_downloads: list[dict[str, Any]] = []
        self._sync_history: list[dict[str, Any]] = []
        self._last_sync: datetime | None = None
        self._sync_failures = 0
        self._logger = structlog.get_logger(__name__).bind(component="sync_manager")

    async def sync_edge_to_cloud(self, readings: list[SensorReading], decisions: list[EdgeDecision]) -> dict[str, Any]:
        """
        Sync edge data to cloud.
        مزامنة بيانات الحافة إلى السحابة

        Args:
            readings: Sensor readings to upload | قراءات المستشعرات للرفع
            decisions: Edge decisions to upload | قرارات الحافة للرفع

        Returns:
            Sync result with counts
        """
        try:
            # Simulate cloud upload
            await asyncio.sleep(0.05)

            sync_result = {
                "direction": "edge_to_cloud",
                "readings_synced": len(readings),
                "decisions_synced": len(decisions),
                "timestamp": datetime.now(UTC).isoformat(),
                "success": True,
            }

            self._record_sync(sync_result)
            self._last_sync = datetime.now(UTC)

            self._logger.info(
                "edge_to_cloud_sync_completed",
                readings=len(readings),
                decisions=len(decisions),
                message_ar="اكتملت مزامنة الحافة إلى السحابة",
            )

            return sync_result

        except Exception as e:
            self._sync_failures += 1
            self._logger.error("edge_to_cloud_sync_failed", error=str(e))
            return {
                "direction": "edge_to_cloud",
                "success": False,
                "error": str(e),
            }

    async def sync_cloud_to_edge(
        self, models: list[dict[str, Any]] | None = None, rules: list[IFTTTRule] | None = None
    ) -> dict[str, Any]:
        """
        Sync cloud updates to edge.
        مزامنة تحديثات السحابة إلى الحافة

        Args:
            models: Model updates to download | تحديثات النماذج للتنزيل
            rules: Rule updates to download | تحديثات القواعد للتنزيل

        Returns:
            Sync result
        """
        try:
            # Simulate cloud download
            await asyncio.sleep(0.03)

            models = models or []
            rules = rules or []

            sync_result = {
                "direction": "cloud_to_edge",
                "models_synced": len(models),
                "rules_synced": len(rules),
                "timestamp": datetime.now(UTC).isoformat(),
                "success": True,
            }

            self._record_sync(sync_result)
            self._last_sync = datetime.now(UTC)

            self._logger.info(
                "cloud_to_edge_sync_completed",
                models=len(models),
                rules=len(rules),
                message_ar="اكتملت مزامنة السحابة إلى الحافة",
            )

            return sync_result

        except Exception as e:
            self._sync_failures += 1
            self._logger.error("cloud_to_edge_sync_failed", error=str(e))
            return {
                "direction": "cloud_to_edge",
                "success": False,
                "error": str(e),
            }

    def _record_sync(self, result: dict[str, Any]) -> None:
        """Record sync operation in history."""
        self._sync_history.append(result)
        if len(self._sync_history) > 1000:
            self._sync_history = self._sync_history[-1000:]

    def get_sync_status(self) -> dict[str, Any]:
        """Get current sync status."""
        return {
            "last_sync": self._last_sync.isoformat() if self._last_sync else None,
            "pending_uploads": len(self._pending_uploads),
            "pending_downloads": len(self._pending_downloads),
            "sync_failures": self._sync_failures,
            "total_syncs": len(self._sync_history),
        }


# =============================================================================
# Edge-Cloud Cooperative System - نظام التعاون بين الحافة والسحابة
# =============================================================================


class EdgeCloudCooperativeSystem:
    """
    Edge-Cloud Cooperative System for smart agriculture.
    نظام التعاون بين الحافة والسحابة للزراعة الذكية

    Integrates perception, edge, and cloud layers to provide:
    - Data collection from 200+ IoT device types
    - Edge processing with 300ms latency
    - Cloud AI inference (YOLOv5 pest detection, 3% error moisture prediction)
    - Seamless offline operation and synchronization
    - Real-time and batch processing modes

    Example:
        system = EdgeCloudCooperativeSystem(farm_id="farm_001")

        # Register devices
        await system.register_device(
            "sensor_001",
            DeviceProtocol.MQTT,
            {"sensor_types": [SensorType.SOIL_MOISTURE]}
        )

        # Start data collection
        await system.start_data_collection()

        # Process in real-time with edge fallback
        await system.process_realtime(use_edge=True, fallback_to_cloud=True)

        # Sync with cloud
        await system.sync_edge_cloud()

        # Get system metrics
        metrics = system.get_system_metrics()
    """

    def __init__(
        self,
        farm_id: str,
        gateway_id: str | None = None,
        location: str = "",
        sampling_interval_minutes: int = 15,
        offline_autonomy: bool = True,
        enable_cloud_training: bool = True,
    ):
        """
        Initialize the Edge-Cloud Cooperative System.
        تهيئة نظام التعاون بين الحافة والسحابة

        Args:
            farm_id: Farm identifier | معرف المزرعة
            gateway_id: Edge gateway ID (auto-generated if None) | معرف البوابة
            location: Physical location | الموقع الفيزيائي
            sampling_interval_minutes: Data collection interval | فترة جمع البيانات
            offline_autonomy: Enable offline operation | تمكين التشغيل بدون اتصال
            enable_cloud_training: Enable cloud model training | تمكين تدريب نماذج السحابة
        """
        self.farm_id = farm_id
        self.gateway_id = gateway_id or f"gateway_{farm_id}_{uuid4().hex[:8]}"
        self.location = location

        # Initialize layers
        self._perception_layer = get_perception_layer(
            farm_id=farm_id,
            sampling_config=SamplingConfig(
                interval_minutes=sampling_interval_minutes,
                min_interval=10,
            ),
        )

        self._edge_layer = get_edge_layer(
            gateway_id=self.gateway_id,
            location=location,
            offline_autonomy=offline_autonomy,
        )

        self._cloud_layer = get_cloud_layer(
            farm_id=farm_id,
            enable_training=enable_cloud_training,
        )

        # Sync manager
        self._sync_manager = SyncManager()

        # State
        self._is_running = False
        self._collection_task: asyncio.Task | None = None
        self._processing_mode = "hybrid"  # edge, cloud, hybrid
        self._cloud_available = True

        # Data buffers
        self._readings_buffer: list[SensorReading] = []
        self._decisions_buffer: list[EdgeDecision] = []
        self._inferences_buffer: list[CloudInference] = []
        self._recommendations_buffer: list[Recommendation] = []

        # Statistics
        self._start_time: datetime | None = None
        self._total_readings = 0
        self._total_edge_decisions = 0
        self._total_cloud_inferences = 0
        self._processing_errors = 0

        # Callbacks
        self._on_reading_callbacks: list[Callable[[SensorReading], None]] = []
        self._on_decision_callbacks: list[Callable[[EdgeDecision], None]] = []
        self._on_recommendation_callbacks: list[Callable[[Recommendation], None]] = []

        # Logger
        self._logger = structlog.get_logger(__name__).bind(
            farm_id=farm_id, gateway_id=self.gateway_id, system="edge_cloud_cooperative"
        )

        self._logger.info(
            "cooperative_system_initialized",
            farm_id=farm_id,
            gateway_id=self.gateway_id,
            location=location,
            offline_autonomy=offline_autonomy,
            message_ar="تم تهيئة نظام التعاون",
        )

    # =========================================================================
    # Device Management - إدارة الأجهزة
    # =========================================================================

    async def register_device(
        self, device_id: str, protocol: DeviceProtocol, config: DeviceConfig | dict[str, Any]
    ) -> bool:
        """
        Register an IoT device with the system.
        تسجيل جهاز إنترنت الأشياء مع النظام

        Supports 200+ device types including Hikvision cameras and DJI drones.

        Args:
            device_id: Unique device identifier | معرف الجهاز
            protocol: Communication protocol | بروتوكول الاتصال
            config: Device configuration | تكوين الجهاز

        Returns:
            True if registration successful

        Example:
            success = await system.register_device(
                "soil_sensor_001",
                DeviceProtocol.MQTT,
                {
                    "host": "192.168.1.100",
                    "sensor_types": [SensorType.SOIL_MOISTURE, SensorType.SOIL_TEMPERATURE]
                }
            )
        """
        return await self._perception_layer.register_device(device_id=device_id, protocol=protocol, config=config)

    async def unregister_device(self, device_id: str) -> bool:
        """
        Unregister a device from the system.
        إلغاء تسجيل جهاز من النظام

        Args:
            device_id: Device to unregister | الجهاز لإلغاء تسجيله

        Returns:
            True if successful
        """
        return await self._perception_layer.unregister_device(device_id)

    def get_registered_devices(self) -> dict[str, DeviceConfig]:
        """
        Get all registered devices.
        الحصول على جميع الأجهزة المسجلة

        Returns:
            Dictionary of device_id -> DeviceConfig
        """
        return self._perception_layer.get_all_devices()

    # =========================================================================
    # Data Collection - جمع البيانات
    # =========================================================================

    async def start_data_collection(self, interval_seconds: int | None = None, continuous: bool = True) -> None:
        """
        Start continuous data collection from devices.
        بدء جمع البيانات المستمر من الأجهزة

        Args:
            interval_seconds: Collection interval (default: from config) | فترة الجمع
            continuous: Run continuously or single collection | تشغيل مستمر

        Example:
            # Start continuous collection every 60 seconds
            await system.start_data_collection(interval_seconds=60)

            # Single collection
            await system.start_data_collection(continuous=False)
        """
        self._is_running = True
        self._start_time = datetime.now(UTC)

        if interval_seconds is None:
            interval_seconds = self._perception_layer.default_sampling_config.interval_minutes * 60

        self._logger.info(
            "data_collection_starting",
            interval_seconds=interval_seconds,
            continuous=continuous,
            message_ar="بدء جمع البيانات",
        )

        if continuous:
            self._collection_task = asyncio.create_task(self._continuous_collection(interval_seconds))
        else:
            await self._collect_once()

    async def stop_data_collection(self) -> None:
        """
        Stop data collection.
        إيقاف جمع البيانات
        """
        self._is_running = False

        if self._collection_task:
            self._collection_task.cancel()
            try:
                await self._collection_task
            except asyncio.CancelledError:
                pass
            self._collection_task = None

        self._logger.info(
            "data_collection_stopped",
            total_readings=self._total_readings,
            message_ar="تم إيقاف جمع البيانات",
        )

    async def _continuous_collection(self, interval_seconds: int) -> None:
        """Run continuous data collection loop."""
        while self._is_running:
            try:
                await self._collect_once()
                await asyncio.sleep(interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error("collection_error", error=str(e))
                self._processing_errors += 1
                await asyncio.sleep(interval_seconds)

    async def _collect_once(self) -> list[SensorReading]:
        """Perform single data collection."""
        # Collect raw readings
        raw_readings = await self._perception_layer.collect_sensor_data()

        # Clean data at edge
        cleaned_readings = self._edge_layer.clean_data(raw_readings)

        # Update buffers and stats
        self._readings_buffer.extend(cleaned_readings)
        self._total_readings += len(cleaned_readings)

        # Trim buffer
        max_buffer = 10000
        if len(self._readings_buffer) > max_buffer:
            self._readings_buffer = self._readings_buffer[-max_buffer:]

        # Notify callbacks
        for reading in cleaned_readings:
            for callback in self._on_reading_callbacks:
                try:
                    callback(reading)
                except Exception:
                    pass

        return cleaned_readings

    # =========================================================================
    # Real-time Processing - المعالجة الآنية
    # =========================================================================

    async def process_realtime(self, use_edge: bool = True, fallback_to_cloud: bool = True) -> dict[str, Any]:
        """
        Process data in real-time with edge-first strategy.
        معالجة البيانات في الوقت الحقيقي باستراتيجية الحافة أولاً

        Processing flow:
        1. Edge layer processes locally (300ms target latency)
        2. If edge cannot decide or cloud is requested, escalate to cloud
        3. Return combined results

        Args:
            use_edge: Use edge processing | استخدام معالجة الحافة
            fallback_to_cloud: Fall back to cloud if needed | الرجوع للسحابة إذا لزم

        Returns:
            Processing results including decisions and recommendations

        Example:
            result = await system.process_realtime(use_edge=True, fallback_to_cloud=True)
            for decision in result["edge_decisions"]:
                if decision.decision_type == DecisionType.IRRIGATION_TRIGGER:
                    # Execute irrigation
                    pass
        """
        start_time = datetime.now(UTC)
        results: dict[str, Any] = {
            "timestamp": start_time.isoformat(),
            "processing_mode": "hybrid" if use_edge and fallback_to_cloud else ("edge" if use_edge else "cloud"),
            "edge_decisions": [],
            "cloud_inferences": [],
            "recommendations": [],
            "latency_ms": 0,
            "used_edge": False,
            "used_cloud": False,
        }

        # Get recent readings
        recent_readings = self._readings_buffer[-100:] if self._readings_buffer else []

        if not recent_readings:
            self._logger.warning("no_readings_for_processing", message_ar="لا توجد قراءات للمعالجة")
            return results

        # Edge processing
        if use_edge:
            try:
                # Run local inference
                edge_decision = await self._edge_layer.run_local_inference(recent_readings)
                results["edge_decisions"].append(edge_decision)
                results["used_edge"] = True
                self._total_edge_decisions += 1

                # Evaluate IFTTT rules
                rule_decisions = await self._edge_layer.evaluate_rules(recent_readings)
                results["edge_decisions"].extend(rule_decisions)
                self._total_edge_decisions += len(rule_decisions)

                # Store decisions
                self._decisions_buffer.extend(results["edge_decisions"])

                # Notify callbacks
                for decision in results["edge_decisions"]:
                    for callback in self._on_decision_callbacks:
                        try:
                            callback(decision)
                        except Exception:
                            pass

            except Exception as e:
                self._logger.error("edge_processing_error", error=str(e))
                self._processing_errors += 1

        # Cloud processing
        if fallback_to_cloud and self._cloud_available:
            try:
                # Prepare context from readings
                context = self._prepare_context(recent_readings)

                # Get cloud recommendations
                recommendations = await self._cloud_layer.get_decision_recommendations(context)
                results["recommendations"] = recommendations
                results["used_cloud"] = True

                # Store recommendations
                self._recommendations_buffer.extend(recommendations)

                # Notify callbacks
                for rec in recommendations:
                    for callback in self._on_recommendation_callbacks:
                        try:
                            callback(rec)
                        except Exception:
                            pass

                self._total_cloud_inferences += 1

            except Exception as e:
                self._logger.error("cloud_processing_error", error=str(e))
                self._processing_errors += 1
                # Continue with edge-only results
                self._cloud_available = False

        # Calculate latency
        end_time = datetime.now(UTC)
        results["latency_ms"] = (end_time - start_time).total_seconds() * 1000

        self._logger.info(
            "realtime_processing_completed",
            edge_decisions=len(results["edge_decisions"]),
            recommendations=len(results["recommendations"]),
            latency_ms=results["latency_ms"],
            used_edge=results["used_edge"],
            used_cloud=results["used_cloud"],
            message_ar="اكتملت المعالجة الآنية",
        )

        return results

    def _prepare_context(self, readings: list[SensorReading]) -> dict[str, Any]:
        """Prepare context dictionary from readings."""
        context: dict[str, Any] = {}

        # Group by sensor type
        by_type: dict[SensorType, list[float]] = defaultdict(list)
        for reading in readings:
            by_type[reading.sensor_type].append(reading.value)

        # Calculate averages
        for sensor_type, values in by_type.items():
            avg_value = sum(values) / len(values)
            key = sensor_type.value
            context[key] = avg_value

        return context

    # =========================================================================
    # Edge-Cloud Synchronization - مزامنة الحافة والسحابة
    # =========================================================================

    async def sync_edge_cloud(self) -> dict[str, Any]:
        """
        Synchronize data between edge and cloud layers.
        مزامنة البيانات بين طبقتي الحافة والسحابة

        Performs bidirectional sync:
        - Edge -> Cloud: Sensor readings, decisions
        - Cloud -> Edge: Model updates, rules

        Returns:
            Sync results for both directions

        Example:
            sync_result = await system.sync_edge_cloud()
            print(f"Synced {sync_result['edge_to_cloud']['readings_synced']} readings")
        """
        results: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "edge_to_cloud": {},
            "cloud_to_edge": {},
            "success": True,
        }

        # Get pending edge data
        pending_decisions = self._edge_layer.get_pending_sync_data()

        # Sync edge to cloud
        edge_result = await self._sync_manager.sync_edge_to_cloud(
            readings=self._readings_buffer[-1000:],  # Last 1000 readings
            decisions=pending_decisions,
        )
        results["edge_to_cloud"] = edge_result

        if edge_result.get("success"):
            # Mark decisions as synced
            decision_ids = [d.id for d in pending_decisions]
            self._edge_layer.mark_synced(decision_ids)

        # Sync cloud to edge (model/rule updates)
        cloud_result = await self._sync_manager.sync_cloud_to_edge(
            models=[],  # Would contain actual model updates
            rules=[],  # Would contain rule updates
        )
        results["cloud_to_edge"] = cloud_result

        results["success"] = edge_result.get("success", False) and cloud_result.get("success", False)

        self._logger.info(
            "edge_cloud_sync_completed",
            success=results["success"],
            readings_synced=edge_result.get("readings_synced", 0),
            decisions_synced=edge_result.get("decisions_synced", 0),
            message_ar="اكتملت المزامنة بين الحافة والسحابة",
        )

        return results

    # =========================================================================
    # Cloud AI Features - ميزات الذكاء الاصطناعي السحابي
    # =========================================================================

    async def detect_pests(self, image: bytes | str, confidence_threshold: float = 0.5) -> tuple[str, float]:
        """
        Detect pests in crop image using cloud AI.
        كشف الآفات في صورة المحصول باستخدام الذكاء الاصطناعي السحابي

        Uses YOLOv5-style model for high-accuracy detection.

        Args:
            image: Image data or path | بيانات الصورة أو المسار
            confidence_threshold: Minimum confidence | الحد الأدنى للثقة

        Returns:
            Tuple of (pest_type, confidence)

        Example:
            pest_type, confidence = await system.detect_pests(image_bytes)
            if confidence > 0.8:
                print(f"Detected: {pest_type}")
        """
        return await self._cloud_layer.pest_detection(image, confidence_threshold)

    async def predict_moisture(self, days: int = 3, weather_forecast: dict[str, Any] | None = None) -> list[float]:
        """
        Predict soil moisture for upcoming days.
        التنبؤ برطوبة التربة للأيام القادمة

        Error rate: ~3%

        Args:
            days: Number of days to predict | عدد الأيام للتنبؤ
            weather_forecast: Optional weather data | بيانات الطقس

        Returns:
            List of predicted moisture values

        Example:
            predictions = await system.predict_moisture(days=3)
            print(f"Tomorrow's moisture: {predictions[0]}%")
        """
        # Get moisture history from readings
        moisture_readings = [r.value for r in self._readings_buffer if r.sensor_type == SensorType.SOIL_MOISTURE][
            -100:
        ]  # Last 100 readings

        if not moisture_readings:
            moisture_readings = [50.0]  # Default

        return await self._cloud_layer.moisture_prediction(
            history=moisture_readings,
            days=days,
            weather_factors=weather_forecast,
        )

    async def estimate_yield(
        self,
        field_data: dict[str, Any],
        weather_forecast: dict[str, Any] | None = None,
        days: int = 15,
    ) -> list[float]:
        """
        Estimate crop yield with 15-day yield curve.
        تقدير إنتاجية المحصول مع منحنى 15 يوم

        Args:
            field_data: Field and crop information | معلومات الحقل والمحصول
            weather_forecast: Weather data | بيانات الطقس
            days: Forecast horizon | أفق التنبؤ

        Returns:
            List of daily yield estimates

        Example:
            field_data = {
                "crop_type": "wheat",
                "area_ha": 10.0,
                "growth_stage": "vegetative"
            }
            yield_curve = await system.estimate_yield(field_data, days=15)
        """
        return await self._cloud_layer.yield_estimation(
            field_data=field_data,
            weather_forecast=weather_forecast,
            days=days,
        )

    # =========================================================================
    # System Metrics - مقاييس النظام
    # =========================================================================

    def get_system_metrics(self) -> SystemMetrics:
        """
        Get comprehensive system metrics.
        الحصول على مقاييس النظام الشاملة

        Returns:
            SystemMetrics with latency, accuracy, and uptime data

        Example:
            metrics = system.get_system_metrics()
            print(f"Edge latency: {metrics.edge_latency_ms}ms")
            print(f"Uptime: {metrics.uptime_percent}%")
        """
        # Calculate uptime
        if self._start_time:
            uptime_seconds = (datetime.now(UTC) - self._start_time).total_seconds()
            uptime_percent = min(100.0, (uptime_seconds / (uptime_seconds + 1)) * 100)
        else:
            uptime_percent = 0.0

        # Get layer statistics
        perception_stats = self._perception_layer.get_statistics()
        edge_stats = self._edge_layer.get_statistics()
        cloud_stats = self._cloud_layer.get_statistics()
        sync_status = self._sync_manager.get_sync_status()

        # Calculate sync success rate
        total_syncs = sync_status.get("total_syncs", 0)
        sync_failures = sync_status.get("sync_failures", 0)
        sync_success_rate = (total_syncs - sync_failures) / total_syncs if total_syncs > 0 else 1.0

        metrics = SystemMetrics(
            # Latency
            edge_latency_ms=edge_stats.get("average_latency_ms", 0.0),
            cloud_latency_ms=cloud_stats.get("average_processing_time_ms", 0.0),
            total_latency_ms=(
                edge_stats.get("average_latency_ms", 0.0) + cloud_stats.get("average_processing_time_ms", 0.0)
            ),
            # Accuracy (estimated based on model specs)
            edge_accuracy=0.88,  # Local inference accuracy
            cloud_accuracy=0.95,  # Cloud model accuracy
            moisture_prediction_error=0.03,  # 3% error rate
            # Availability
            uptime_percent=uptime_percent,
            edge_uptime_percent=100.0 if self._edge_layer.offline_autonomy else uptime_percent,
            cloud_uptime_percent=100.0 if self._cloud_available else 0.0,
            # Throughput
            readings_per_minute=(self._total_readings / max(1, uptime_seconds / 60) if self._start_time else 0.0),
            decisions_per_minute=(
                self._total_edge_decisions / max(1, uptime_seconds / 60) if self._start_time else 0.0
            ),
            inferences_per_minute=(
                self._total_cloud_inferences / max(1, uptime_seconds / 60) if self._start_time else 0.0
            ),
            # Devices
            total_devices=perception_stats.get("total_devices", 0),
            active_devices=perception_stats.get("online_devices", 0),
            offline_devices=perception_stats.get("offline_devices", 0),
            # Sync
            sync_success_rate=sync_success_rate,
            pending_sync_count=edge_stats.get("pending_sync_count", 0),
            last_sync_at=(datetime.fromisoformat(sync_status["last_sync"]) if sync_status.get("last_sync") else None),
        )

        return metrics

    def get_statistics(self) -> dict[str, Any]:
        """
        Get detailed system statistics.
        الحصول على إحصائيات النظام التفصيلية

        Returns:
            Dictionary with comprehensive statistics
        """
        return {
            "farm_id": self.farm_id,
            "gateway_id": self.gateway_id,
            "is_running": self._is_running,
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "cloud_available": self._cloud_available,
            "processing_mode": self._processing_mode,
            "totals": {
                "readings": self._total_readings,
                "edge_decisions": self._total_edge_decisions,
                "cloud_inferences": self._total_cloud_inferences,
                "processing_errors": self._processing_errors,
            },
            "buffers": {
                "readings": len(self._readings_buffer),
                "decisions": len(self._decisions_buffer),
                "recommendations": len(self._recommendations_buffer),
            },
            "perception_layer": self._perception_layer.get_statistics(),
            "edge_layer": self._edge_layer.get_statistics(),
            "cloud_layer": self._cloud_layer.get_statistics(),
            "sync_status": self._sync_manager.get_sync_status(),
        }

    # =========================================================================
    # Rule Management - إدارة القواعد
    # =========================================================================

    def add_automation_rule(self, rule: IFTTTRule) -> bool:
        """
        Add an IFTTT-style automation rule.
        إضافة قاعدة أتمتة نمط IFTTT

        Args:
            rule: Rule to add | القاعدة للإضافة

        Returns:
            True if successful
        """
        loaded_rules = self._edge_layer.execute_preloaded_logic([rule])
        return len(loaded_rules) > 0

    def setup_auto_irrigation(self, soil_moisture_threshold: float = 30.0, zone_id: str | None = None) -> IFTTTRule:
        """
        Set up automatic irrigation based on soil moisture.
        إعداد الري التلقائي بناءً على رطوبة التربة

        Args:
            soil_moisture_threshold: Trigger threshold (%) | عتبة التشغيل
            zone_id: Specific zone | المنطقة المحددة

        Returns:
            Created IFTTT rule

        Example:
            rule = system.setup_auto_irrigation(soil_moisture_threshold=30)
        """
        return self._edge_layer.auto_irrigation_trigger(
            soil_moisture_threshold=soil_moisture_threshold, zone_id=zone_id
        )

    # =========================================================================
    # Callbacks - ردود الاتصال
    # =========================================================================

    def on_reading(self, callback: Callable[[SensorReading], None]) -> None:
        """Register callback for new sensor readings."""
        self._on_reading_callbacks.append(callback)

    def on_decision(self, callback: Callable[[EdgeDecision], None]) -> None:
        """Register callback for edge decisions."""
        self._on_decision_callbacks.append(callback)

    def on_recommendation(self, callback: Callable[[Recommendation], None]) -> None:
        """Register callback for cloud recommendations."""
        self._on_recommendation_callbacks.append(callback)

    # =========================================================================
    # Lifecycle - دورة الحياة
    # =========================================================================

    def set_cloud_availability(self, available: bool) -> None:
        """
        Set cloud availability status.
        تعيين حالة توفر السحابة

        When cloud is unavailable, system operates in edge-only mode.

        Args:
            available: Whether cloud is reachable | هل السحابة متاحة
        """
        previous = self._cloud_available
        self._cloud_available = available
        self._edge_layer.set_cloud_connection_status(available)

        if previous != available:
            self._logger.info(
                "cloud_availability_changed",
                available=available,
                message_ar="تغيرت حالة توفر السحابة",
            )

    async def shutdown(self) -> None:
        """
        Shutdown the cooperative system.
        إيقاف النظام التعاوني

        Performs graceful shutdown:
        1. Stop data collection
        2. Sync pending data to cloud
        3. Shutdown all layers
        """
        self._logger.info("cooperative_system_shutting_down", message_ar="جاري إيقاف النظام التعاوني")

        # Stop data collection
        await self.stop_data_collection()

        # Final sync
        try:
            await self.sync_edge_cloud()
        except Exception as e:
            self._logger.error("final_sync_failed", error=str(e))

        # Shutdown layers
        await self._perception_layer.shutdown()
        await self._edge_layer.shutdown()

        self._logger.info(
            "cooperative_system_shutdown_complete",
            total_readings=self._total_readings,
            total_decisions=self._total_edge_decisions,
            message_ar="اكتمل إيقاف النظام",
        )


# =============================================================================
# Factory Function - وظيفة المصنع
# =============================================================================


def get_cooperative_system(
    farm_id: str, gateway_id: str | None = None, location: str = "", **kwargs
) -> EdgeCloudCooperativeSystem:
    """
    Get an Edge-Cloud Cooperative System instance.
    الحصول على مثيل نظام التعاون بين الحافة والسحابة

    Args:
        farm_id: Farm identifier | معرف المزرعة
        gateway_id: Gateway ID (optional) | معرف البوابة
        location: Physical location | الموقع الفيزيائي
        **kwargs: Additional configuration | تكوين إضافي

    Returns:
        EdgeCloudCooperativeSystem instance

    Example:
        system = get_cooperative_system(
            farm_id="farm_001",
            location="Field A",
            offline_autonomy=True
        )
    """
    return EdgeCloudCooperativeSystem(farm_id=farm_id, gateway_id=gateway_id, location=location, **kwargs)
