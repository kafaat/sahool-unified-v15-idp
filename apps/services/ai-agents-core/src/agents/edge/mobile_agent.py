"""
SAHOOL Mobile Edge Agent
وكيل الجوال الطرفي

Fast on-device processing for:
- Quick disease detection from camera
- Instant weather alerts
- Offline field recommendations
- Voice command processing

Target response time: < 100ms
"""

import logging
from datetime import datetime
from typing import Any

from ..base_agent import (
    AgentAction,
    AgentContext,
    AgentLayer,
    AgentPercept,
    AgentType,
    BaseAgent,
)

logger = logging.getLogger(__name__)


class MobileAgent(BaseAgent):
    """
    وكيل الجوال الطرفي
    Mobile Edge Agent for instant on-device processing
    """

    # Quick response rules (condition → action)
    QUICK_RULES = {
        "high_temperature": {
            "threshold": 40,  # Celsius
            "action": "irrigation_alert",
            "priority": 1,
            "message_ar": "تنبيه: درجة الحرارة مرتفعة جداً، يُنصح بالري الفوري",
        },
        "low_soil_moisture": {
            "threshold": 0.2,  # 20%
            "action": "irrigation_needed",
            "priority": 2,
            "message_ar": "رطوبة التربة منخفضة، يُنصح بالري",
        },
        "pest_detected": {
            "confidence_threshold": 0.7,
            "action": "pest_alert",
            "priority": 1,
            "message_ar": "تم اكتشاف آفة، يُرجى اتخاذ إجراء فوري",
        },
        "disease_detected": {
            "confidence_threshold": 0.6,
            "action": "disease_alert",
            "priority": 1,
            "message_ar": "تم اكتشاف مرض محتمل، يُنصح بالفحص",
        },
        "harvest_ready": {
            "maturity_threshold": 0.9,
            "action": "harvest_notification",
            "priority": 3,
            "message_ar": "المحصول جاهز للحصاد",
        },
    }

    def __init__(self, agent_id: str = "mobile_edge_001"):
        super().__init__(
            agent_id=agent_id,
            name="Mobile Edge Agent",
            name_ar="وكيل الجوال الطرفي",
            agent_type=AgentType.SIMPLE_REFLEX,
            layer=AgentLayer.EDGE,
            description="Fast on-device processing for instant responses",
            description_ar="معالجة سريعة على الجهاز للاستجابات الفورية",
        )

        # Local cache for offline operation
        self.local_cache: dict[str, Any] = {}
        self.offline_queue: list[dict[str, Any]] = []

        # Image processing state
        self.last_image_analysis: dict[str, Any] | None = None

        # Initialize rules
        self._init_rules()

    def _init_rules(self) -> None:
        """تهيئة قواعد الاستجابة السريعة"""
        # High temperature rule
        self.add_rule(
            condition=lambda ctx: ctx.sensor_data.get("temperature", 0) > 40,
            action=AgentAction(
                action_type="irrigation_alert",
                parameters={"urgency": "high", "reason": "high_temperature"},
                confidence=0.95,
                priority=1,
                reasoning="درجة الحرارة تجاوزت 40 درجة مئوية",
            ),
        )

        # Low moisture rule
        self.add_rule(
            condition=lambda ctx: ctx.sensor_data.get("soil_moisture", 1.0) < 0.2,
            action=AgentAction(
                action_type="irrigation_needed",
                parameters={"urgency": "medium", "reason": "low_moisture"},
                confidence=0.9,
                priority=2,
                reasoning="رطوبة التربة أقل من 20%",
            ),
        )

        # Frost alert rule
        self.add_rule(
            condition=lambda ctx: ctx.sensor_data.get("temperature", 20) < 2,
            action=AgentAction(
                action_type="frost_alert",
                parameters={"urgency": "critical", "reason": "frost_risk"},
                confidence=0.98,
                priority=1,
                reasoning="خطر الصقيع - درجة الحرارة أقل من 2 درجة",
            ),
        )

    async def perceive(self, percept: AgentPercept) -> None:
        """استقبال المدخلات"""
        # Update context based on percept type
        if percept.percept_type == "sensor_reading":
            if self.context:
                self.context.sensor_data.update(percept.data)
            else:
                self.context = AgentContext(sensor_data=percept.data)

        elif percept.percept_type == "image":
            # Quick image classification
            self.last_image_analysis = await self._quick_image_analysis(percept.data)

        elif percept.percept_type == "voice_command":
            # Parse voice command
            command = await self._parse_voice_command(percept.data)
            self.state.intentions.append(command)

        elif percept.percept_type == "location":
            if self.context:
                self.context.location = percept.data
            else:
                self.context = AgentContext(location=percept.data)

        # Store in memory for learning
        self.state.memory.append(
            {
                "percept": percept.percept_type,
                "timestamp": datetime.now().isoformat(),
                "data_summary": str(percept.data)[:100],
            }
        )

        # Keep memory limited
        if len(self.state.memory) > 100:
            self.state.memory = self.state.memory[-100:]

    async def think(self) -> AgentAction | None:
        """
        التفكير السريع - Simple Reflex
        Quick thinking using predefined rules
        """
        if not self.context:
            return None

        # 1. Check rules first (fastest)
        action = self.evaluate_rules(self.context)
        if action:
            action.source_agent = self.agent_id
            return action

        # 2. Check image analysis results
        if self.last_image_analysis:
            img_action = await self._process_image_result(self.last_image_analysis)
            if img_action:
                return img_action

        # 3. Check voice command intentions
        if self.state.intentions:
            intention = self.state.intentions.pop(0)
            return await self._intention_to_action(intention)

        # 4. Proactive checks
        proactive_action = await self._proactive_check()
        if proactive_action:
            return proactive_action

        return None

    async def act(self, action: AgentAction) -> dict[str, Any]:
        """تنفيذ الإجراء"""
        result = {
            "action_type": action.action_type,
            "executed_at": datetime.now().isoformat(),
            "parameters": action.parameters,
            "success": True,
        }

        # Execute based on action type
        if action.action_type == "irrigation_alert":
            result["notification"] = {
                "title": "تنبيه الري",
                "body": action.reasoning,
                "priority": "high",
                "sound": "alert",
            }

        elif action.action_type == "disease_alert":
            result["notification"] = {
                "title": "تنبيه مرض",
                "body": action.reasoning,
                "priority": "high",
                "action_button": "عرض التفاصيل",
            }
            # Queue for specialist agent
            self.offline_queue.append(
                {
                    "type": "disease_analysis_request",
                    "data": self.last_image_analysis,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        elif action.action_type == "harvest_notification":
            result["notification"] = {
                "title": "إشعار الحصاد",
                "body": action.reasoning,
                "priority": "normal",
            }

        elif action.action_type == "frost_alert":
            result["notification"] = {
                "title": "⚠️ تحذير صقيع",
                "body": action.reasoning,
                "priority": "critical",
                "sound": "emergency",
            }

        # Cache result for offline access
        self.local_cache[f"last_action_{action.action_type}"] = result

        return result

    async def _quick_image_analysis(self, image_data: Any) -> dict[str, Any]:
        """
        تحليل سريع للصورة
        Quick on-device image analysis using TFLite
        """
        # Simulated quick analysis (would use TFLite in production)
        return {
            "analyzed": True,
            "quick_classification": "healthy",
            "confidence": 0.85,
            "needs_detailed_analysis": False,
            "timestamp": datetime.now().isoformat(),
        }

    async def _parse_voice_command(self, audio_data: Any) -> str:
        """تحليل الأمر الصوتي"""
        # Simulated voice parsing
        return "check_field_status"

    async def _process_image_result(self, analysis: dict[str, Any]) -> AgentAction | None:
        """معالجة نتيجة تحليل الصورة"""
        if analysis.get("quick_classification") == "disease":
            return AgentAction(
                action_type="disease_alert",
                parameters={
                    "confidence": analysis.get("confidence", 0),
                    "image_id": analysis.get("image_id"),
                },
                confidence=analysis.get("confidence", 0.5),
                priority=1,
                reasoning="تم اكتشاف أعراض مرضية في الصورة",
                source_agent=self.agent_id,
            )
        return None

    async def _intention_to_action(self, intention: str) -> AgentAction:
        """تحويل النية إلى إجراء"""
        intention_map = {
            "check_field_status": AgentAction(
                action_type="field_status_query",
                parameters={},
                confidence=0.9,
                priority=3,
                reasoning="طلب المستخدم حالة الحقل",
                source_agent=self.agent_id,
            ),
            "start_irrigation": AgentAction(
                action_type="irrigation_command",
                parameters={"action": "start"},
                confidence=0.95,
                priority=2,
                reasoning="أمر المستخدم ببدء الري",
                source_agent=self.agent_id,
                requires_confirmation=True,
            ),
        }
        return intention_map.get(
            intention,
            AgentAction(
                action_type="unknown_command",
                parameters={"raw_intention": intention},
                confidence=0.5,
                priority=4,
                reasoning="أمر غير معروف",
                source_agent=self.agent_id,
            ),
        )

    async def _proactive_check(self) -> AgentAction | None:
        """فحص استباقي"""
        if not self.context:
            return None

        # Check if it's prayer time (example of proactive feature)
        # Check if weather is changing
        # etc.
        return None

    def get_offline_queue(self) -> list[dict[str, Any]]:
        """الحصول على قائمة المهام المؤجلة"""
        return self.offline_queue

    def clear_offline_queue(self) -> None:
        """مسح قائمة المهام المؤجلة"""
        self.offline_queue = []

    def sync_with_cloud(self, cloud_data: dict[str, Any]) -> None:
        """مزامنة مع السحابة"""
        # Update local cache with cloud data
        self.local_cache.update(cloud_data.get("cache_updates", {}))

        # Send offline queue to cloud
        # This would be handled by the actual sync mechanism

        # Clear synced items
        self.clear_offline_queue()
