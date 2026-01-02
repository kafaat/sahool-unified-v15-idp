"""
SAHOOL Master Coordinator Agent
وكيل المنسق الرئيسي

Central coordination agent for:
- Conflict resolution between specialist agents
- Priority-based decision making
- Resource allocation
- Unified recommendation generation
- Multi-agent orchestration

This agent implements a Goal-Based + Utility-Based hybrid approach.
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging

from ..base_agent import (
    BaseAgent, AgentType, AgentLayer, AgentStatus,
    AgentContext, AgentAction, AgentPercept
)
from ..specialist.disease_expert_agent import DiseaseExpertAgent
from ..specialist.yield_predictor_agent import YieldPredictorAgent
from ..specialist.irrigation_advisor_agent import IrrigationAdvisorAgent
from ..specialist.weather_analyst_agent import WeatherAnalystAgent

logger = logging.getLogger(__name__)


class ConflictType(Enum):
    """أنواع التعارض"""
    RESOURCE_CONFLICT = "resource"      # Same resource, different actions
    TIMING_CONFLICT = "timing"          # Conflicting schedules
    PRIORITY_CONFLICT = "priority"      # Different priorities
    GOAL_CONFLICT = "goal"              # Conflicting goals


@dataclass
class AgentRecommendation:
    """توصية من وكيل"""
    agent_id: str
    agent_name: str
    action: AgentAction
    timestamp: datetime


@dataclass
class ConflictResolution:
    """حل التعارض"""
    conflict_type: ConflictType
    conflicting_actions: List[AgentAction]
    resolution: str
    selected_action: AgentAction
    reasoning: str


@dataclass
class UnifiedRecommendation:
    """التوصية الموحدة"""
    primary_action: AgentAction
    supporting_actions: List[AgentAction]
    conflicts_resolved: List[ConflictResolution]
    priority_score: float
    confidence: float
    summary_ar: str
    details: Dict[str, Any]


class MasterCoordinatorAgent(BaseAgent):
    """
    وكيل المنسق الرئيسي
    Master Coordinator for multi-agent orchestration
    """

    # Priority weights for different action types
    ACTION_PRIORITIES = {
        "emergency": 100,
        "critical_alert": 90,
        "disease_treatment": 80,
        "frost_emergency": 95,
        "heat_emergency": 95,
        "irrigation_immediate": 70,
        "yield_optimization": 50,
        "prevention_measures": 40,
        "scheduled_maintenance": 30,
        "report": 10
    }

    # Resource constraints
    RESOURCES = {
        "water": {"daily_limit_liters": 10000, "used": 0},
        "labor": {"hours_available": 8, "used": 0},
        "budget": {"daily_yer": 50000, "used": 0},
        "equipment": {"available": True}
    }

    def __init__(self, agent_id: str = "master_coordinator_001"):
        super().__init__(
            agent_id=agent_id,
            name="Master Coordinator Agent",
            name_ar="وكيل المنسق الرئيسي",
            agent_type=AgentType.UTILITY_BASED,
            layer=AgentLayer.COORDINATOR,
            description="Central coordinator for all specialist agents",
            description_ar="المنسق المركزي لجميع الوكلاء المتخصصين"
        )

        # Initialize specialist agents
        self.specialists: Dict[str, BaseAgent] = {}
        self._init_specialists()

        # Collected recommendations
        self.pending_recommendations: List[AgentRecommendation] = []

        # Resolution history
        self.resolution_history: List[ConflictResolution] = []

        # Goals
        self.state.goals = [
            "maximize_yield",
            "minimize_resource_waste",
            "protect_crop_health",
            "optimize_costs"
        ]

        # Set utility function
        self.set_utility_function(self._unified_utility)

    def _init_specialists(self) -> None:
        """تهيئة الوكلاء المتخصصين"""
        self.specialists = {
            "disease": DiseaseExpertAgent("disease_expert_001"),
            "yield": YieldPredictorAgent("yield_predictor_001"),
            "irrigation": IrrigationAdvisorAgent("irrigation_advisor_001"),
            "weather": WeatherAnalystAgent("weather_analyst_001")
        }

    def _unified_utility(self, action: AgentAction, context: AgentContext) -> float:
        """
        دالة المنفعة الموحدة
        Unified utility function considering all factors
        """
        # Base priority
        action_type = action.action_type.lower()
        base_priority = 0
        for key, priority in self.ACTION_PRIORITIES.items():
            if key in action_type:
                base_priority = priority
                break

        if base_priority == 0:
            base_priority = 20  # Default

        # Normalize to 0-1
        priority_score = base_priority / 100

        # Confidence factor
        confidence_factor = action.confidence

        # Resource availability factor
        resource_factor = self._check_resource_availability(action)

        # Urgency factor
        urgency_factor = 1.0 if action.priority == 1 else (0.8 if action.priority == 2 else 0.6)

        # Combined utility
        utility = (
            0.35 * priority_score +
            0.25 * confidence_factor +
            0.20 * resource_factor +
            0.20 * urgency_factor
        )

        return utility

    def _check_resource_availability(self, action: AgentAction) -> float:
        """التحقق من توفر الموارد"""
        params = action.parameters

        # Check water
        if "water" in action.action_type.lower() or "irrigation" in action.action_type.lower():
            water_needed = params.get("amount_mm", 0) * 100  # Approximate liters
            water_available = self.RESOURCES["water"]["daily_limit_liters"] - self.RESOURCES["water"]["used"]
            if water_needed > water_available:
                return 0.3
            return 1.0

        # Check budget
        cost = params.get("cost_yer", 0)
        if cost > 0:
            budget_available = self.RESOURCES["budget"]["daily_yer"] - self.RESOURCES["budget"]["used"]
            if cost > budget_available:
                return 0.4
            return 1.0

        return 1.0

    async def perceive(self, percept: AgentPercept) -> None:
        """
        استقبال المدخلات وتوزيعها على الوكلاء
        Receive inputs and distribute to specialists
        """
        # Distribute to relevant specialists
        if percept.percept_type in ["image_analysis", "symptoms_report"]:
            await self.specialists["disease"].perceive(percept)

        if percept.percept_type in ["ndvi_data", "crop_info"]:
            await self.specialists["yield"].perceive(percept)

        if percept.percept_type in ["soil_moisture", "et0_data"]:
            await self.specialists["irrigation"].perceive(percept)

        if percept.percept_type in ["current_weather", "forecast"]:
            await self.specialists["weather"].perceive(percept)

        # Update shared context
        if not self.context:
            self.context = AgentContext()

        self.context.metadata[percept.percept_type] = percept.data

    async def think(self) -> Optional[AgentAction]:
        """
        جمع التوصيات وحل التعارضات
        Collect recommendations and resolve conflicts
        """
        # Step 1: Collect recommendations from all specialists
        recommendations = await self._collect_all_recommendations()

        if not recommendations:
            return AgentAction(
                action_type="no_action_needed",
                parameters={},
                confidence=0.7,
                priority=5,
                reasoning="لا توجد إجراءات مطلوبة حالياً",
                source_agent=self.agent_id
            )

        # Step 2: Detect conflicts
        conflicts = self._detect_conflicts(recommendations)

        # Step 3: Resolve conflicts
        resolutions = []
        for conflict in conflicts:
            resolution = await self._resolve_conflict(conflict)
            resolutions.append(resolution)
            self.resolution_history.append(resolution)

        # Step 4: Prioritize and select actions
        unified = await self._create_unified_recommendation(recommendations, resolutions)

        # Step 5: Return coordinated action
        return AgentAction(
            action_type="coordinated_recommendation",
            parameters={
                "unified_recommendation": {
                    "primary": unified.primary_action.to_dict() if hasattr(unified.primary_action, 'to_dict') else str(unified.primary_action),
                    "supporting": len(unified.supporting_actions),
                    "conflicts_resolved": len(unified.conflicts_resolved),
                    "summary_ar": unified.summary_ar,
                    "details": unified.details
                }
            },
            confidence=unified.confidence,
            priority=unified.primary_action.priority,
            reasoning=unified.summary_ar,
            source_agent=self.agent_id
        )

    async def _collect_all_recommendations(self) -> List[AgentRecommendation]:
        """جمع التوصيات من جميع الوكلاء"""
        recommendations = []

        for name, agent in self.specialists.items():
            try:
                action = await agent.think()
                if action and action.action_type not in ["no_action_needed", "insufficient_data"]:
                    recommendations.append(AgentRecommendation(
                        agent_id=agent.agent_id,
                        agent_name=agent.name_ar,
                        action=action,
                        timestamp=datetime.now()
                    ))
            except Exception as e:
                logger.error(f"Error collecting from {name}: {e}")

        return recommendations

    def _detect_conflicts(self, recommendations: List[AgentRecommendation]) -> List[Dict[str, Any]]:
        """اكتشاف التعارضات"""
        conflicts = []

        for i, rec1 in enumerate(recommendations):
            for rec2 in recommendations[i+1:]:
                conflict = self._check_conflict(rec1.action, rec2.action)
                if conflict:
                    conflicts.append({
                        "type": conflict,
                        "action1": rec1,
                        "action2": rec2
                    })

        return conflicts

    def _check_conflict(self, action1: AgentAction, action2: AgentAction) -> Optional[ConflictType]:
        """التحقق من وجود تعارض"""
        # Resource conflict
        if ("irrigation" in action1.action_type.lower() and
            "irrigation" in action2.action_type.lower()):
            return ConflictType.RESOURCE_CONFLICT

        # Timing conflict
        if (action1.priority == 1 and action2.priority == 1 and
            action1.action_type != action2.action_type):
            return ConflictType.TIMING_CONFLICT

        # Priority conflict
        if abs(action1.priority - action2.priority) >= 2:
            return ConflictType.PRIORITY_CONFLICT

        return None

    async def _resolve_conflict(self, conflict: Dict[str, Any]) -> ConflictResolution:
        """حل التعارض"""
        conflict_type = conflict["type"]
        action1 = conflict["action1"].action
        action2 = conflict["action2"].action

        # Calculate utilities
        utility1 = self.calculate_utility(action1, self.context)
        utility2 = self.calculate_utility(action2, self.context)

        if utility1 >= utility2:
            selected = action1
            reasoning = f"تم اختيار {action1.action_type} لأن منفعته أعلى ({utility1:.2f} > {utility2:.2f})"
        else:
            selected = action2
            reasoning = f"تم اختيار {action2.action_type} لأن منفعته أعلى ({utility2:.2f} > {utility1:.2f})"

        resolution_method = {
            ConflictType.RESOURCE_CONFLICT: "تم حل تعارض الموارد باختيار الإجراء الأكثر كفاءة",
            ConflictType.TIMING_CONFLICT: "تم حل تعارض التوقيت باختيار الإجراء الأكثر إلحاحاً",
            ConflictType.PRIORITY_CONFLICT: "تم حل تعارض الأولوية باختيار الإجراء ذو الأولوية الأعلى",
            ConflictType.GOAL_CONFLICT: "تم حل تعارض الأهداف بموازنة المنافع"
        }

        return ConflictResolution(
            conflict_type=conflict_type,
            conflicting_actions=[action1, action2],
            resolution=resolution_method.get(conflict_type, "تم الحل بناءً على المنفعة"),
            selected_action=selected,
            reasoning=reasoning
        )

    async def _create_unified_recommendation(
        self,
        recommendations: List[AgentRecommendation],
        resolutions: List[ConflictResolution]
    ) -> UnifiedRecommendation:
        """إنشاء التوصية الموحدة"""
        # Get resolved actions
        resolved_actions = {r.selected_action for r in resolutions}
        excluded_actions = set()
        for r in resolutions:
            for a in r.conflicting_actions:
                if a != r.selected_action:
                    excluded_actions.add(id(a))

        # Filter valid recommendations
        valid_actions = [
            rec.action for rec in recommendations
            if id(rec.action) not in excluded_actions
        ]

        if not valid_actions:
            # Use first recommendation as fallback
            valid_actions = [recommendations[0].action] if recommendations else []

        # Sort by priority and utility
        sorted_actions = sorted(
            valid_actions,
            key=lambda a: (a.priority, -self.calculate_utility(a, self.context))
        )

        primary = sorted_actions[0] if sorted_actions else None
        supporting = sorted_actions[1:4] if len(sorted_actions) > 1 else []

        # Calculate overall confidence
        confidences = [a.confidence for a in sorted_actions]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5

        # Generate summary
        summary_parts = []
        if primary:
            summary_parts.append(primary.reasoning)
        if supporting:
            summary_parts.append(f"بالإضافة إلى {len(supporting)} توصيات داعمة")
        if resolutions:
            summary_parts.append(f"تم حل {len(resolutions)} تعارض")

        summary_ar = " | ".join(summary_parts)

        return UnifiedRecommendation(
            primary_action=primary,
            supporting_actions=supporting,
            conflicts_resolved=resolutions,
            priority_score=1 - (primary.priority / 5) if primary else 0,
            confidence=avg_confidence,
            summary_ar=summary_ar,
            details={
                "total_recommendations": len(recommendations),
                "conflicts_detected": len(resolutions),
                "actions_selected": len(sorted_actions),
                "specialist_agents": list(self.specialists.keys())
            }
        )

    async def act(self, action: AgentAction) -> Dict[str, Any]:
        """تنفيذ التوصية المنسقة"""
        result = {
            "action_type": action.action_type,
            "executed_at": datetime.now().isoformat(),
            "success": True
        }

        if action.action_type == "coordinated_recommendation":
            unified = action.parameters.get("unified_recommendation", {})
            result["coordination"] = {
                "primary_action": unified.get("primary"),
                "supporting_count": unified.get("supporting"),
                "conflicts_resolved": unified.get("conflicts_resolved"),
                "summary_ar": unified.get("summary_ar")
            }

            # Execute primary action through appropriate specialist
            # This would integrate with actual service execution

        return result

    async def run_full_analysis(self, context: AgentContext) -> Dict[str, Any]:
        """تشغيل تحليل كامل"""
        self.context = context

        # Distribute context to all specialists
        for name, agent in self.specialists.items():
            agent.update_context(context)

        # Run coordination
        result = await self.run(AgentPercept(
            percept_type="full_analysis_request",
            data={"context": "full"},
            source="user"
        ))

        return result

    def get_system_status(self) -> Dict[str, Any]:
        """الحصول على حالة النظام"""
        return {
            "coordinator": self.get_metrics(),
            "specialists": {
                name: agent.get_metrics()
                for name, agent in self.specialists.items()
            },
            "resources": self.RESOURCES,
            "conflicts_resolved_total": len(self.resolution_history),
            "active_goals": self.state.goals
        }
