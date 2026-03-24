"""
Edge Computing Layer - Smart Agriculture
=========================================
طبقة الحوسبة الطرفية - الزراعة الذكية

The edge computing layer provides local processing capabilities
with 300ms target latency and offline autonomy. Enables real-time
decision making without cloud connectivity using preloaded IFTTT-style rules.

Key Features:
- Local inference with 300ms target latency
- Offline autonomy mode
- IFTTT-style rule execution
- Data cleaning and noise filtering
- Automatic irrigation triggering

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import statistics
from collections import defaultdict
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import structlog

from .models import (
    DataQuality,
    DecisionType,
    EdgeDecision,
    IFTTTRule,
    RuleAction,
    RuleCondition,
    SensorReading,
    SensorType,
    SystemStatus,
)

# Configure structured logging
logger = structlog.get_logger(__name__)


# =============================================================================
# Data Cleaning - تنظيف البيانات
# =============================================================================


class DataCleaner:
    """
    Data cleaning and noise filtering for sensor readings.
    تنظيف البيانات وفلترة الضوضاء لقراءات المستشعرات

    Implements various cleaning strategies including outlier detection,
    smoothing, and quality assessment.
    """

    def __init__(self, window_size: int = 10, outlier_threshold: float = 3.0):
        """
        Initialize data cleaner.
        تهيئة منظف البيانات

        Args:
            window_size: Size of the moving window for statistics | حجم النافذة المتحركة
            outlier_threshold: Z-score threshold for outliers | عتبة القيم المتطرفة
        """
        self.window_size = window_size
        self.outlier_threshold = outlier_threshold
        self._history: dict[str, list[float]] = defaultdict(list)
        self._logger = structlog.get_logger(__name__).bind(component="data_cleaner")

    def clean(self, readings: list[SensorReading]) -> list[SensorReading]:
        """
        Clean a batch of sensor readings.
        تنظيف مجموعة من قراءات المستشعرات

        Applies the following cleaning steps:
        1. Remove invalid readings
        2. Detect and handle outliers
        3. Apply smoothing filter
        4. Update quality scores

        Args:
            readings: Raw sensor readings | قراءات المستشعرات الخام

        Returns:
            Cleaned sensor readings | قراءات المستشعرات المنظفة
        """
        cleaned: list[SensorReading] = []

        for reading in readings:
            # Skip invalid readings
            if reading.quality == DataQuality.INVALID:
                continue

            # Create key for history tracking
            history_key = f"{reading.device_id}_{reading.sensor_type.value}"

            # Add to history
            self._history[history_key].append(reading.value)

            # Keep only recent values
            if len(self._history[history_key]) > self.window_size:
                self._history[history_key] = self._history[history_key][-self.window_size :]

            # Skip if not enough history
            if len(self._history[history_key]) < 3:
                cleaned.append(reading)
                continue

            # Check for outliers
            is_outlier = self._is_outlier(
                reading.value,
                self._history[history_key][:-1],  # Exclude current value
            )

            if is_outlier:
                # Use smoothed value instead
                smoothed_value = self._smooth_value(self._history[history_key])
                reading.value = smoothed_value
                reading.quality = DataQuality.FAIR
                reading.calibration_applied = True
                self._logger.debug(
                    "outlier_smoothed",
                    device_id=reading.device_id,
                    sensor_type=reading.sensor_type.value,
                    original_value=reading.raw_value,
                    smoothed_value=smoothed_value,
                )
            else:
                # Apply light smoothing
                if len(self._history[history_key]) >= 3:
                    smoothed = self._smooth_value(self._history[history_key][-3:])
                    reading.value = round(smoothed, 2)

            cleaned.append(reading)

        return cleaned

    def _is_outlier(self, value: float, history: list[float]) -> bool:
        """
        Check if a value is an outlier using Z-score.
        التحقق مما إذا كانت القيمة متطرفة باستخدام Z-score
        """
        if len(history) < 2:
            return False

        mean = statistics.mean(history)
        try:
            stdev = statistics.stdev(history)
        except statistics.StatisticsError:
            return False

        if stdev == 0:
            return False

        z_score = abs(value - mean) / stdev
        return z_score > self.outlier_threshold

    def _smooth_value(self, values: list[float]) -> float:
        """
        Apply exponential moving average smoothing.
        تطبيق التنعيم بالمتوسط المتحرك الأسي
        """
        if not values:
            return 0.0

        alpha = 0.3  # Smoothing factor
        smoothed = values[0]
        for value in values[1:]:
            smoothed = alpha * value + (1 - alpha) * smoothed

        return round(smoothed, 2)

    def get_sensor_stats(self, device_id: str, sensor_type: SensorType) -> dict[str, float]:
        """
        Get statistics for a sensor.
        الحصول على إحصائيات المستشعر

        Returns:
            Dictionary with mean, stdev, min, max
        """
        history_key = f"{device_id}_{sensor_type.value}"
        history = self._history.get(history_key, [])

        if not history:
            return {"mean": 0.0, "stdev": 0.0, "min": 0.0, "max": 0.0, "count": 0}

        return {
            "mean": round(statistics.mean(history), 2),
            "stdev": round(statistics.stdev(history), 2) if len(history) > 1 else 0.0,
            "min": round(min(history), 2),
            "max": round(max(history), 2),
            "count": len(history),
        }

    def clear_history(self, device_id: str | None = None) -> None:
        """
        Clear sensor history.
        مسح سجل المستشعر
        """
        if device_id:
            keys_to_remove = [k for k in self._history if k.startswith(device_id)]
            for key in keys_to_remove:
                del self._history[key]
        else:
            self._history.clear()


# =============================================================================
# Rule Engine - محرك القواعد
# =============================================================================


class RuleEngine:
    """
    IFTTT-style rule engine for edge computing.
    محرك قواعد نمط IFTTT للحوسبة الطرفية

    Evaluates conditions and triggers actions based on
    preloaded rules for offline autonomous operation.
    """

    def __init__(self):
        """Initialize rule engine."""
        self._rules: dict[UUID, IFTTTRule] = {}
        self._rule_triggers: dict[UUID, int] = defaultdict(int)
        self._rule_last_trigger: dict[UUID, datetime] = {}
        self._logger = structlog.get_logger(__name__).bind(component="rule_engine")

    def add_rule(self, rule: IFTTTRule) -> bool:
        """
        Add a rule to the engine.
        إضافة قاعدة إلى المحرك

        Args:
            rule: IFTTT rule to add | قاعدة IFTTT للإضافة

        Returns:
            True if rule was added successfully
        """
        self._rules[rule.id] = rule
        self._logger.info(
            "rule_added",
            rule_id=str(rule.id),
            rule_name=rule.name,
            conditions_count=len(rule.conditions),
            actions_count=len(rule.actions),
            message_ar="تمت إضافة القاعدة",
        )
        return True

    def remove_rule(self, rule_id: UUID) -> bool:
        """
        Remove a rule from the engine.
        إزالة قاعدة من المحرك

        Args:
            rule_id: Rule ID to remove | معرف القاعدة للإزالة

        Returns:
            True if rule was removed
        """
        if rule_id in self._rules:
            del self._rules[rule_id]
            self._logger.info("rule_removed", rule_id=str(rule_id))
            return True
        return False

    def evaluate(
        self, readings: list[SensorReading], current_time: datetime | None = None
    ) -> list[tuple[IFTTTRule, list[RuleAction]]]:
        """
        Evaluate all rules against current readings.
        تقييم جميع القواعد مقابل القراءات الحالية

        Args:
            readings: Current sensor readings | القراءات الحالية
            current_time: Current time (default: now) | الوقت الحالي

        Returns:
            List of (rule, actions) tuples for triggered rules
        """
        current_time = current_time or datetime.now(UTC)
        triggered: list[tuple[IFTTTRule, list[RuleAction]]] = []

        # Index readings by sensor type for fast lookup
        readings_by_type: dict[SensorType, list[SensorReading]] = defaultdict(list)
        for reading in readings:
            readings_by_type[reading.sensor_type].append(reading)

        # Evaluate each active rule
        for rule in self._rules.values():
            if not rule.is_active:
                continue

            # Check time constraints
            if not self._is_within_active_hours(rule, current_time):
                continue

            # Check cooldown
            if not self._check_cooldown(rule, current_time):
                continue

            # Check daily trigger limit
            if not self._check_daily_limit(rule, current_time):
                continue

            # Evaluate conditions
            if self._evaluate_conditions(rule, readings_by_type):
                triggered.append((rule, rule.actions))
                self._record_trigger(rule, current_time)
                self._logger.info(
                    "rule_triggered",
                    rule_id=str(rule.id),
                    rule_name=rule.name,
                    message_ar="تم تفعيل القاعدة",
                )

        return triggered

    def _evaluate_conditions(self, rule: IFTTTRule, readings_by_type: dict[SensorType, list[SensorReading]]) -> bool:
        """
        Evaluate rule conditions.
        تقييم شروط القاعدة
        """
        results = []

        for condition in rule.conditions:
            readings = readings_by_type.get(condition.sensor_type, [])

            # Filter by zone if specified
            if condition.zone_id:
                readings = [r for r in readings if r.zone_id == condition.zone_id]

            if not readings:
                results.append(False)
                continue

            # Use average value if multiple readings
            avg_value = statistics.mean(r.value for r in readings)

            # Evaluate condition
            condition_met = self._evaluate_condition(avg_value, condition.operator, condition.threshold)
            results.append(condition_met)

        # Apply logic (AND/OR)
        if rule.condition_logic.upper() == "AND":
            return all(results) if results else False
        else:  # OR
            return any(results) if results else False

    def _evaluate_condition(self, value: float, operator: str, threshold: float) -> bool:
        """
        Evaluate a single condition.
        تقييم شرط واحد
        """
        operators = {
            "<": lambda v, t: v < t,
            ">": lambda v, t: v > t,
            "<=": lambda v, t: v <= t,
            ">=": lambda v, t: v >= t,
            "==": lambda v, t: abs(v - t) < 0.001,
            "!=": lambda v, t: abs(v - t) >= 0.001,
        }
        op_func = operators.get(operator, lambda v, t: False)
        return op_func(value, threshold)

    def _is_within_active_hours(self, rule: IFTTTRule, current_time: datetime) -> bool:
        """Check if current time is within rule's active hours."""
        if rule.active_hours_start is None or rule.active_hours_end is None:
            return True

        current_hour = current_time.hour

        if rule.active_hours_start <= rule.active_hours_end:
            return rule.active_hours_start <= current_hour <= rule.active_hours_end
        else:
            # Spans midnight
            return current_hour >= rule.active_hours_start or current_hour <= rule.active_hours_end

    def _check_cooldown(self, rule: IFTTTRule, current_time: datetime) -> bool:
        """Check if rule has passed its cooldown period."""
        last_trigger = self._rule_last_trigger.get(rule.id)
        if not last_trigger:
            return True

        cooldown = timedelta(minutes=rule.cooldown_minutes)
        return current_time >= last_trigger + cooldown

    def _check_daily_limit(self, rule: IFTTTRule, current_time: datetime) -> bool:
        """Check if rule has reached its daily trigger limit."""
        # Reset counter at midnight
        last_trigger = self._rule_last_trigger.get(rule.id)
        if last_trigger and last_trigger.date() != current_time.date():
            self._rule_triggers[rule.id] = 0

        return self._rule_triggers[rule.id] < rule.max_daily_triggers

    def _record_trigger(self, rule: IFTTTRule, trigger_time: datetime) -> None:
        """Record a rule trigger."""
        self._rule_triggers[rule.id] += 1
        self._rule_last_trigger[rule.id] = trigger_time
        rule.trigger_count += 1
        rule.last_triggered_at = trigger_time

    def get_rules(self, active_only: bool = False) -> list[IFTTTRule]:
        """
        Get all rules.
        الحصول على جميع القواعد

        Args:
            active_only: Return only active rules | إرجاع القواعد النشطة فقط

        Returns:
            List of rules
        """
        if active_only:
            return [r for r in self._rules.values() if r.is_active]
        return list(self._rules.values())


# =============================================================================
# Local Inference - الاستدلال المحلي
# =============================================================================


class LocalInferenceEngine:
    """
    Local inference engine for edge computing.
    محرك الاستدلال المحلي للحوسبة الطرفية

    Provides lightweight ML inference with 300ms target latency.
    يوفر استدلال تعلم آلي خفيف الوزن بزمن استجابة مستهدف 300 مللي ثانية
    """

    TARGET_LATENCY_MS = 300

    def __init__(self):
        """Initialize inference engine."""
        self._models: dict[str, Any] = {}
        self._inference_count = 0
        self._total_latency_ms = 0.0
        self._logger = structlog.get_logger(__name__).bind(component="inference_engine")

    async def run_inference(self, model_name: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        Run local inference.
        تشغيل الاستدلال المحلي

        Args:
            model_name: Name of the model | اسم النموذج
            data: Input data | بيانات الإدخال

        Returns:
            Inference result with latency
        """
        start_time = datetime.now(UTC)

        # Placeholder for actual inference
        # In production, this would use TFLite, ONNX, or similar
        result = await self._simple_inference(model_name, data)

        end_time = datetime.now(UTC)
        latency_ms = (end_time - start_time).total_seconds() * 1000

        self._inference_count += 1
        self._total_latency_ms += latency_ms

        self._logger.debug(
            "inference_completed",
            model_name=model_name,
            latency_ms=latency_ms,
            within_target=latency_ms <= self.TARGET_LATENCY_MS,
        )

        return {
            "result": result,
            "latency_ms": latency_ms,
            "model_name": model_name,
            "timestamp": end_time.isoformat(),
        }

    async def _simple_inference(self, model_name: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        Simple rule-based inference for common agricultural scenarios.
        استدلال بسيط قائم على القواعد للسيناريوهات الزراعية الشائعة
        """
        if model_name == "irrigation_decision":
            return self._irrigation_decision(data)
        elif model_name == "stress_detection":
            return self._stress_detection(data)
        elif model_name == "anomaly_detection":
            return self._anomaly_detection(data)
        else:
            return {"status": "unknown_model"}

    def _irrigation_decision(self, data: dict[str, Any]) -> dict[str, Any]:
        """Simple irrigation decision model."""
        soil_moisture = data.get("soil_moisture", 50.0)
        temperature = data.get("temperature", 25.0)
        humidity = data.get("humidity", 60.0)

        # Simple decision logic
        if soil_moisture < 30:
            decision = "irrigate"
            confidence = 0.9
        elif soil_moisture < 40 and temperature > 35:
            decision = "irrigate"
            confidence = 0.7
        elif soil_moisture > 70:
            decision = "skip"
            confidence = 0.85
        else:
            decision = "monitor"
            confidence = 0.6

        return {
            "decision": decision,
            "confidence": confidence,
            "factors": {
                "soil_moisture": soil_moisture,
                "temperature": temperature,
                "humidity": humidity,
            },
        }

    def _stress_detection(self, data: dict[str, Any]) -> dict[str, Any]:
        """Simple stress detection model."""
        soil_moisture = data.get("soil_moisture", 50.0)
        temperature = data.get("temperature", 25.0)

        stress_indicators = []

        if soil_moisture < 25:
            stress_indicators.append("water_stress")
        if temperature > 40:
            stress_indicators.append("heat_stress")
        if soil_moisture > 85:
            stress_indicators.append("waterlogging_risk")

        return {
            "stress_detected": len(stress_indicators) > 0,
            "stress_indicators": stress_indicators,
            "severity": "high" if len(stress_indicators) > 1 else "low",
        }

    def _anomaly_detection(self, data: dict[str, Any]) -> dict[str, Any]:
        """Simple anomaly detection model."""
        values = data.get("values", [])

        if not values:
            return {"anomaly_detected": False}

        mean = statistics.mean(values)
        try:
            stdev = statistics.stdev(values)
        except statistics.StatisticsError:
            stdev = 0

        anomalies = []
        for i, v in enumerate(values):
            if stdev > 0 and abs(v - mean) > 3 * stdev:
                anomalies.append({"index": i, "value": v})

        return {
            "anomaly_detected": len(anomalies) > 0,
            "anomalies": anomalies,
            "statistics": {"mean": mean, "stdev": stdev},
        }

    def get_average_latency(self) -> float:
        """Get average inference latency in ms."""
        if self._inference_count == 0:
            return 0.0
        return self._total_latency_ms / self._inference_count


# =============================================================================
# Edge Computing Layer - طبقة الحوسبة الطرفية
# =============================================================================


class EdgeComputingLayer:
    """
    Edge Computing Layer for smart agriculture.
    طبقة الحوسبة الطرفية للزراعة الذكية

    Provides local processing with 300ms target latency and
    offline autonomy using preloaded IFTTT-style rules.

    Features:
    - Data cleaning and noise filtering
    - Local inference engine
    - IFTTT-style rule execution
    - Automatic irrigation triggering
    - Offline autonomy mode

    Example:
        layer = EdgeComputingLayer(
            gateway_id="gateway_001",
            location="Field A, Zone 1"
        )

        # Clean sensor data
        cleaned = layer.clean_data(raw_readings)

        # Run local inference
        decision = await layer.run_local_inference(cleaned)

        # Check irrigation trigger
        layer.auto_irrigation_trigger(soil_moisture_threshold=30)
    """

    # Target response latency: 300ms
    TARGET_LATENCY_MS = 300

    def __init__(self, gateway_id: str, location: str, offline_autonomy: bool = True):
        """
        Initialize Edge Computing Layer.
        تهيئة طبقة الحوسبة الطرفية

        Args:
            gateway_id: Unique gateway identifier | معرف البوابة الفريد
            location: Physical location description | وصف الموقع الفيزيائي
            offline_autonomy: Enable offline autonomous operation | تمكين التشغيل الذاتي بدون اتصال
        """
        self.gateway_id = gateway_id
        self.location = location
        self.offline_autonomy = offline_autonomy

        # Components
        self._data_cleaner = DataCleaner()
        self._rule_engine = RuleEngine()
        self._inference_engine = LocalInferenceEngine()

        # State
        self._status = SystemStatus.ONLINE
        self._cloud_connected = True
        self._last_cloud_sync: datetime | None = None

        # Decision history
        self._decisions: list[EdgeDecision] = []
        self._max_decision_history = 1000

        # Irrigation state
        self._irrigation_active: dict[str, bool] = {}
        self._last_irrigation: dict[str, datetime] = {}

        # Callbacks
        self._on_decision_callbacks: list[Callable[[EdgeDecision], None]] = []

        # Statistics
        self._total_decisions = 0
        self._offline_decisions = 0

        # Logger
        self._logger = structlog.get_logger(__name__).bind(gateway_id=gateway_id, layer="edge")

        self._logger.info(
            "edge_layer_initialized",
            gateway_id=gateway_id,
            location=location,
            offline_autonomy=offline_autonomy,
            message_ar="تم تهيئة طبقة الحوسبة الطرفية",
        )

    def clean_data(self, readings: list[SensorReading]) -> list[SensorReading]:
        """
        Clean sensor data by removing noise and outliers.
        تنظيف بيانات المستشعرات بإزالة الضوضاء والقيم المتطرفة

        Applies the following cleaning steps:
        - Remove invalid readings
        - Detect and smooth outliers
        - Apply moving average filtering
        - Update quality scores

        Args:
            readings: Raw sensor readings | قراءات المستشعرات الخام

        Returns:
            Cleaned sensor readings | قراءات المستشعرات المنظفة

        Example:
            raw_readings = await perception_layer.collect_sensor_data()
            cleaned = edge_layer.clean_data(raw_readings)
        """
        cleaned = self._data_cleaner.clean(readings)

        self._logger.debug(
            "data_cleaned",
            input_count=len(readings),
            output_count=len(cleaned),
            message_ar="تم تنظيف البيانات",
        )

        return cleaned

    async def run_local_inference(
        self, data: list[SensorReading] | dict[str, Any], model_name: str = "irrigation_decision"
    ) -> EdgeDecision:
        """
        Run local inference on sensor data.
        تشغيل الاستدلال المحلي على بيانات المستشعرات

        Target latency: 300ms
        زمن الاستجابة المستهدف: 300 مللي ثانية

        Args:
            data: Sensor readings or preprocessed data | قراءات المستشعرات أو البيانات المعالجة
            model_name: Name of inference model | اسم نموذج الاستدلال

        Returns:
            EdgeDecision with inference result

        Example:
            decision = await edge_layer.run_local_inference(cleaned_readings)
            if decision.decision_type == DecisionType.IRRIGATION_TRIGGER:
                # Execute irrigation
                pass
        """
        datetime.now(UTC)

        # Convert readings to dict format
        if isinstance(data, list):
            input_data = self._readings_to_dict(data)
        else:
            input_data = data

        # Run inference
        result = await self._inference_engine.run_inference(model_name, input_data)

        # Calculate latency
        latency_ms = result.get("latency_ms", 0.0)

        # Determine decision type and action
        decision_result = result.get("result", {})
        decision_type, action, action_ar = self._interpret_inference_result(model_name, decision_result)

        # Create decision
        decision = EdgeDecision(
            gateway_id=self.gateway_id,
            decision_type=decision_type,
            action=action,
            action_ar=action_ar,
            latency_ms=latency_ms,
            offline_mode=not self._cloud_connected,
            confidence=decision_result.get("confidence", 0.5),
            metadata={
                "model_name": model_name,
                "inference_result": decision_result,
                "input_summary": str(input_data)[:200],
            },
        )

        # Record decision
        self._record_decision(decision)

        self._logger.info(
            "local_inference_completed",
            decision_type=decision_type.value,
            action=action,
            latency_ms=latency_ms,
            within_target=latency_ms <= self.TARGET_LATENCY_MS,
            message_ar="اكتمل الاستدلال المحلي",
        )

        return decision

    def _readings_to_dict(self, readings: list[SensorReading]) -> dict[str, Any]:
        """Convert sensor readings to dictionary format."""
        result: dict[str, Any] = {}

        for reading in readings:
            key = reading.sensor_type.value
            if key not in result:
                result[key] = reading.value
            else:
                # Average multiple readings of same type
                if isinstance(result[key], list):
                    result[key].append(reading.value)
                else:
                    result[key] = [result[key], reading.value]

        # Convert lists to averages
        for key, value in result.items():
            if isinstance(value, list):
                result[key] = statistics.mean(value)

        return result

    def _interpret_inference_result(self, model_name: str, result: dict[str, Any]) -> tuple[DecisionType, str, str]:
        """Interpret inference result into decision type and action."""
        if model_name == "irrigation_decision":
            decision = result.get("decision", "monitor")
            if decision == "irrigate":
                return (DecisionType.IRRIGATION_TRIGGER, "start_irrigation", "بدء الري")
            elif decision == "skip":
                return (DecisionType.IRRIGATION_STOP, "skip_irrigation", "تجاوز الري")
            else:
                return (DecisionType.DATA_AGGREGATION, "continue_monitoring", "استمرار المراقبة")

        elif model_name == "stress_detection":
            if result.get("stress_detected"):
                return (
                    DecisionType.ALERT_WARNING,
                    f"stress_alert: {result.get('stress_indicators', [])}",
                    "تنبيه إجهاد",
                )
            return (DecisionType.DATA_AGGREGATION, "no_stress", "لا يوجد إجهاد")

        elif model_name == "anomaly_detection":
            if result.get("anomaly_detected"):
                return (
                    DecisionType.ALERT_WARNING,
                    f"anomaly_detected: {len(result.get('anomalies', []))} anomalies",
                    "تم اكتشاف شذوذ",
                )
            return (DecisionType.DATA_AGGREGATION, "normal", "طبيعي")

        return (DecisionType.LOCAL_INFERENCE, str(result), "نتيجة الاستدلال")

    def execute_preloaded_logic(self, rules: list[IFTTTRule] | None = None) -> list[IFTTTRule]:
        """
        Load and prepare IFTTT-style rules for execution.
        تحميل وإعداد قواعد نمط IFTTT للتنفيذ

        These rules enable autonomous operation without cloud connectivity.
        هذه القواعد تمكن التشغيل الذاتي بدون اتصال بالسحابة

        Args:
            rules: List of rules to load (optional) | قائمة القواعد للتحميل

        Returns:
            List of loaded rules

        Example:
            rules = [
                IFTTTRule(
                    name="Low Moisture Alert",
                    conditions=[RuleCondition(
                        sensor_type=SensorType.SOIL_MOISTURE,
                        operator="<",
                        threshold=30.0
                    )],
                    actions=[RuleAction(
                        action_type="start_irrigation",
                        parameters={"duration_minutes": 30}
                    )]
                )
            ]
            edge_layer.execute_preloaded_logic(rules)
        """
        if rules:
            for rule in rules:
                self._rule_engine.add_rule(rule)

        loaded_rules = self._rule_engine.get_rules()

        self._logger.info("rules_loaded", rule_count=len(loaded_rules), message_ar="تم تحميل القواعد")

        return loaded_rules

    async def evaluate_rules(self, readings: list[SensorReading]) -> list[EdgeDecision]:
        """
        Evaluate IFTTT rules against current readings.
        تقييم قواعد IFTTT مقابل القراءات الحالية

        Args:
            readings: Current sensor readings | القراءات الحالية

        Returns:
            List of decisions from triggered rules
        """
        triggered = self._rule_engine.evaluate(readings)
        decisions: list[EdgeDecision] = []

        for rule, actions in triggered:
            for action in actions:
                decision = EdgeDecision(
                    gateway_id=self.gateway_id,
                    decision_type=self._action_to_decision_type(action),
                    action=action.action_type,
                    action_ar=action.action_type_ar,
                    latency_ms=0.0,  # Rule evaluation is fast
                    offline_mode=not self._cloud_connected,
                    rule_id=str(rule.id),
                    confidence=0.9,
                    metadata={
                        "rule_name": rule.name,
                        "action_parameters": action.parameters,
                    },
                )

                # Execute action after delay
                if action.delay_seconds > 0:
                    decision.executed = False
                else:
                    decision.executed = await self._execute_action(action)
                    if decision.executed:
                        decision.executed_at = datetime.now(UTC)

                self._record_decision(decision)
                decisions.append(decision)

        return decisions

    def _action_to_decision_type(self, action: RuleAction) -> DecisionType:
        """Map action type to decision type."""
        mapping = {
            "start_irrigation": DecisionType.IRRIGATION_TRIGGER,
            "stop_irrigation": DecisionType.IRRIGATION_STOP,
            "alert_critical": DecisionType.ALERT_CRITICAL,
            "alert_warning": DecisionType.ALERT_WARNING,
        }
        return mapping.get(action.action_type, DecisionType.DEVICE_CONTROL)

    async def _execute_action(self, action: RuleAction) -> bool:
        """Execute an action. Returns True if successful."""
        self._logger.info(
            "action_executed",
            action_type=action.action_type,
            parameters=action.parameters,
            message_ar="تم تنفيذ الإجراء",
        )
        return True

    def auto_irrigation_trigger(self, soil_moisture_threshold: float = 30.0, zone_id: str | None = None) -> IFTTTRule:
        """
        Set up automatic irrigation triggering based on soil moisture.
        إعداد تشغيل الري التلقائي بناءً على رطوبة التربة

        Creates an IFTTT rule that triggers irrigation when
        soil moisture falls below the threshold.

        Args:
            soil_moisture_threshold: Moisture threshold (%) | عتبة الرطوبة (%)
            zone_id: Specific zone (optional) | المنطقة المحددة

        Returns:
            The created IFTTT rule

        Example:
            rule = edge_layer.auto_irrigation_trigger(soil_moisture_threshold=30)
        """
        condition = RuleCondition(
            sensor_type=SensorType.SOIL_MOISTURE,
            operator="<",
            threshold=soil_moisture_threshold,
            unit="%",
            zone_id=zone_id,
        )

        action = RuleAction(
            action_type="start_irrigation",
            action_type_ar="بدء الري",
            parameters={
                "zone_id": zone_id,
                "trigger_reason": f"soil_moisture < {soil_moisture_threshold}%",
                "auto_triggered": True,
            },
        )

        rule = IFTTTRule(
            name=f"Auto Irrigation (moisture < {soil_moisture_threshold}%)",
            name_ar=f"الري التلقائي (الرطوبة < {soil_moisture_threshold}%)",
            description=f"Automatically trigger irrigation when soil moisture drops below {soil_moisture_threshold}%",
            description_ar=f"تشغيل الري تلقائياً عندما تنخفض رطوبة التربة عن {soil_moisture_threshold}%",
            conditions=[condition],
            actions=[action],
            is_active=True,
            priority=2,
            cooldown_minutes=120,  # 2 hour cooldown
            max_daily_triggers=4,
        )

        self._rule_engine.add_rule(rule)

        self._logger.info(
            "auto_irrigation_configured",
            threshold=soil_moisture_threshold,
            zone_id=zone_id,
            message_ar="تم إعداد الري التلقائي",
        )

        return rule

    def _record_decision(self, decision: EdgeDecision) -> None:
        """Record a decision in history."""
        self._decisions.append(decision)
        self._total_decisions += 1

        if decision.offline_mode:
            self._offline_decisions += 1

        # Trim history
        if len(self._decisions) > self._max_decision_history:
            self._decisions = self._decisions[-self._max_decision_history :]

        # Notify callbacks
        for callback in self._on_decision_callbacks:
            callback(decision)

    @property
    def response_latency(self) -> float:
        """
        Get average response latency in milliseconds.
        الحصول على متوسط زمن الاستجابة بالمللي ثانية

        Target: 300ms
        الهدف: 300 مللي ثانية
        """
        return self._inference_engine.get_average_latency()

    def set_cloud_connection_status(self, connected: bool) -> None:
        """
        Update cloud connection status.
        تحديث حالة الاتصال بالسحابة

        When offline, the edge layer operates autonomously
        using preloaded rules and local inference.

        Args:
            connected: Whether cloud is reachable | هل السحابة متاحة
        """
        previous = self._cloud_connected
        self._cloud_connected = connected

        if previous != connected:
            self._logger.info(
                "cloud_connection_changed",
                connected=connected,
                offline_autonomy=self.offline_autonomy,
                message_ar="تغيرت حالة الاتصال بالسحابة",
            )

    def get_pending_sync_data(self) -> list[EdgeDecision]:
        """
        Get decisions pending sync to cloud.
        الحصول على القرارات المعلقة للمزامنة مع السحابة

        Returns:
            List of unsynced decisions
        """
        return [d for d in self._decisions if not d.synced_to_cloud]

    def mark_synced(self, decision_ids: list[UUID]) -> int:
        """
        Mark decisions as synced to cloud.
        تحديد القرارات على أنها تمت مزامنتها

        Args:
            decision_ids: Decision IDs to mark | معرفات القرارات

        Returns:
            Number of decisions marked
        """
        count = 0
        sync_time = datetime.now(UTC)

        for decision in self._decisions:
            if decision.id in decision_ids:
                decision.synced_to_cloud = True
                decision.synced_at = sync_time
                count += 1

        if count > 0:
            self._last_cloud_sync = sync_time

        return count

    def get_statistics(self) -> dict[str, Any]:
        """
        Get edge layer statistics.
        الحصول على إحصائيات طبقة الحافة

        Returns:
            Dictionary of statistics
        """
        pending_sync = len(self.get_pending_sync_data())

        return {
            "gateway_id": self.gateway_id,
            "location": self.location,
            "status": self._status.value,
            "cloud_connected": self._cloud_connected,
            "offline_autonomy": self.offline_autonomy,
            "total_decisions": self._total_decisions,
            "offline_decisions": self._offline_decisions,
            "offline_ratio": (self._offline_decisions / self._total_decisions if self._total_decisions > 0 else 0.0),
            "average_latency_ms": self.response_latency,
            "target_latency_ms": self.TARGET_LATENCY_MS,
            "latency_within_target": self.response_latency <= self.TARGET_LATENCY_MS,
            "active_rules": len(self._rule_engine.get_rules(active_only=True)),
            "pending_sync_count": pending_sync,
            "last_cloud_sync": (self._last_cloud_sync.isoformat() if self._last_cloud_sync else None),
        }

    def on_decision(self, callback: Callable[[EdgeDecision], None]) -> None:
        """
        Register callback for new decisions.
        تسجيل رد اتصال للقرارات الجديدة

        Args:
            callback: Function to call with each decision
        """
        self._on_decision_callbacks.append(callback)

    async def shutdown(self) -> None:
        """
        Shutdown the edge layer.
        إيقاف طبقة الحافة
        """
        self._logger.info(
            "edge_layer_shutting_down",
            pending_decisions=len(self.get_pending_sync_data()),
            message_ar="جاري إيقاف طبقة الحافة",
        )

        self._status = SystemStatus.OFFLINE


# =============================================================================
# Factory Function - وظيفة المصنع
# =============================================================================


def get_edge_layer(gateway_id: str, location: str, offline_autonomy: bool = True) -> EdgeComputingLayer:
    """
    Get an edge computing layer instance.
    الحصول على مثيل طبقة الحوسبة الطرفية

    Args:
        gateway_id: Gateway identifier | معرف البوابة
        location: Physical location | الموقع الفيزيائي
        offline_autonomy: Enable offline mode | تمكين وضع عدم الاتصال

    Returns:
        EdgeComputingLayer instance

    Example:
        layer = get_edge_layer("gateway_001", "Field A, Zone 1")
    """
    return EdgeComputingLayer(gateway_id, location, offline_autonomy)
