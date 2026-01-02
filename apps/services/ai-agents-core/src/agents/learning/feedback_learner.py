"""
SAHOOL Feedback Learner Agent
وكيل التعلم من التغذية الراجعة

Learns from user feedback and outcomes:
- Reinforcement learning from rewards
- Policy adjustment
- Recommendation improvement
- Error correction

True Learning Agent implementation.
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
import asyncio
import logging
import json
import math

from ..base_agent import (
    BaseAgent, AgentType, AgentLayer, AgentStatus,
    AgentContext, AgentAction, AgentPercept
)

logger = logging.getLogger(__name__)


@dataclass
class FeedbackEntry:
    """إدخال التغذية الراجعة"""
    feedback_id: str
    recommendation_id: str
    agent_id: str
    action_type: str
    user_rating: float  # -1 to 1
    outcome_success: bool
    actual_result: Dict[str, Any]
    expected_result: Dict[str, Any]
    timestamp: datetime
    context_snapshot: Dict[str, Any]


@dataclass
class LearningPolicy:
    """سياسة التعلم"""
    action_type: str
    success_rate: float
    avg_reward: float
    adjustment_factor: float
    samples_count: int
    last_updated: datetime


class FeedbackLearnerAgent(BaseAgent):
    """
    وكيل التعلم من التغذية الراجعة
    Reinforcement Learning Agent
    """

    # Learning parameters
    LEARNING_RATE = 0.1
    DISCOUNT_FACTOR = 0.95
    EXPLORATION_RATE = 0.1
    MIN_SAMPLES_FOR_ADJUSTMENT = 5

    def __init__(self, agent_id: str = "feedback_learner_001"):
        super().__init__(
            agent_id=agent_id,
            name="Feedback Learner Agent",
            name_ar="وكيل التعلم من التغذية الراجعة",
            agent_type=AgentType.LEARNING,
            layer=AgentLayer.LEARNING,
            description="Learns from feedback to improve recommendations",
            description_ar="يتعلم من التغذية الراجعة لتحسين التوصيات"
        )

        # Feedback storage
        self.feedback_history: List[FeedbackEntry] = []

        # Learning policies per action type
        self.policies: Dict[str, LearningPolicy] = {}

        # Q-values for state-action pairs (simplified)
        self.q_table: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))

        # Reward history per agent
        self.agent_rewards: Dict[str, List[float]] = defaultdict(list)

        # Model adjustment queue
        self.adjustment_queue: List[Dict[str, Any]] = []

    async def perceive(self, percept: AgentPercept) -> None:
        """استقبال التغذية الراجعة"""
        if percept.percept_type == "user_feedback":
            feedback = self._create_feedback_entry(percept.data)
            self.feedback_history.append(feedback)
            await self._process_feedback(feedback)

        elif percept.percept_type == "outcome_report":
            # Actual outcome vs predicted
            await self._process_outcome(percept.data)

        elif percept.percept_type == "correction":
            # User correction of recommendation
            await self._process_correction(percept.data)

    def _create_feedback_entry(self, data: Dict[str, Any]) -> FeedbackEntry:
        """إنشاء إدخال التغذية الراجعة"""
        return FeedbackEntry(
            feedback_id=f"fb_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            recommendation_id=data.get("recommendation_id", ""),
            agent_id=data.get("agent_id", ""),
            action_type=data.get("action_type", ""),
            user_rating=data.get("rating", 0),  # -1 to 1
            outcome_success=data.get("success", False),
            actual_result=data.get("actual_result", {}),
            expected_result=data.get("expected_result", {}),
            timestamp=datetime.now(),
            context_snapshot=data.get("context", {})
        )

    async def _process_feedback(self, feedback: FeedbackEntry) -> None:
        """معالجة التغذية الراجعة"""
        # Calculate reward
        reward = self._calculate_reward(feedback)

        # Store reward for agent
        self.agent_rewards[feedback.agent_id].append(reward)

        # Update Q-value
        state = self._extract_state(feedback.context_snapshot)
        action = feedback.action_type

        old_q = self.q_table[state][action]
        new_q = old_q + self.LEARNING_RATE * (reward - old_q)
        self.q_table[state][action] = new_q

        # Update policy
        await self._update_policy(feedback.action_type, reward, feedback.outcome_success)

        logger.info(f"Processed feedback: reward={reward:.2f}, Q[{state}][{action}]={new_q:.2f}")

    def _calculate_reward(self, feedback: FeedbackEntry) -> float:
        """حساب المكافأة"""
        # Combine user rating and outcome
        user_component = feedback.user_rating * 0.4  # -0.4 to 0.4
        outcome_component = 0.6 if feedback.outcome_success else -0.3

        # Bonus for matching expected result
        match_bonus = 0
        if feedback.actual_result and feedback.expected_result:
            # Compare key metrics
            actual_yield = feedback.actual_result.get("yield", 0)
            expected_yield = feedback.expected_result.get("yield", 0)
            if expected_yield > 0:
                accuracy = 1 - abs(actual_yield - expected_yield) / expected_yield
                match_bonus = max(0, accuracy * 0.2)

        reward = user_component + outcome_component + match_bonus

        # Normalize to [-1, 1]
        return max(-1, min(1, reward))

    def _extract_state(self, context: Dict[str, Any]) -> str:
        """استخراج الحالة من السياق"""
        # Simplified state representation
        crop = context.get("crop_type", "unknown")
        season = context.get("season", "unknown")
        severity = context.get("severity", "normal")

        return f"{crop}_{season}_{severity}"

    async def _update_policy(self, action_type: str, reward: float, success: bool) -> None:
        """تحديث السياسة"""
        if action_type not in self.policies:
            self.policies[action_type] = LearningPolicy(
                action_type=action_type,
                success_rate=0.5,
                avg_reward=0.0,
                adjustment_factor=1.0,
                samples_count=0,
                last_updated=datetime.now()
            )

        policy = self.policies[action_type]

        # Update running averages
        n = policy.samples_count
        policy.success_rate = (policy.success_rate * n + (1 if success else 0)) / (n + 1)
        policy.avg_reward = (policy.avg_reward * n + reward) / (n + 1)
        policy.samples_count = n + 1
        policy.last_updated = datetime.now()

        # Calculate adjustment factor
        if policy.samples_count >= self.MIN_SAMPLES_FOR_ADJUSTMENT:
            # Increase confidence for high-performing actions
            if policy.success_rate > 0.7 and policy.avg_reward > 0.3:
                policy.adjustment_factor = min(1.5, policy.adjustment_factor + 0.05)
            # Decrease confidence for poor-performing actions
            elif policy.success_rate < 0.4 or policy.avg_reward < -0.2:
                policy.adjustment_factor = max(0.5, policy.adjustment_factor - 0.05)

            # Queue for model update if significant change
            if abs(policy.adjustment_factor - 1.0) > 0.2:
                self.adjustment_queue.append({
                    "action_type": action_type,
                    "adjustment": policy.adjustment_factor,
                    "reason": "policy_drift",
                    "timestamp": datetime.now().isoformat()
                })

    async def _process_outcome(self, data: Dict[str, Any]) -> None:
        """معالجة النتيجة الفعلية"""
        recommendation_id = data.get("recommendation_id")
        actual = data.get("actual")
        predicted = data.get("predicted")

        # Find original recommendation
        original_feedback = None
        for fb in reversed(self.feedback_history):
            if fb.recommendation_id == recommendation_id:
                original_feedback = fb
                break

        if original_feedback:
            # Calculate prediction error
            if isinstance(actual, (int, float)) and isinstance(predicted, (int, float)):
                error = abs(actual - predicted)
                error_rate = error / predicted if predicted != 0 else 1.0

                # Penalize large errors
                if error_rate > 0.3:
                    penalty_reward = -0.5 * error_rate
                    await self._update_policy(original_feedback.action_type, penalty_reward, False)

    async def _process_correction(self, data: Dict[str, Any]) -> None:
        """معالجة التصحيح"""
        original_action = data.get("original_action")
        corrected_action = data.get("corrected_action")
        reason = data.get("reason", "")

        # Learn from correction
        self.state.knowledge[f"correction_{original_action}"] = {
            "should_be": corrected_action,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }

        # Negative reward for original
        await self._update_policy(original_action, -0.5, False)

        # Positive reward for corrected
        await self._update_policy(corrected_action, 0.5, True)

    async def think(self) -> Optional[AgentAction]:
        """التفكير في التحسينات"""
        # Check if model updates are needed
        if self.adjustment_queue:
            adjustments = self.adjustment_queue[:5]  # Process up to 5
            self.adjustment_queue = self.adjustment_queue[5:]

            return AgentAction(
                action_type="model_adjustment_request",
                parameters={
                    "adjustments": adjustments,
                    "policies": {
                        k: {
                            "success_rate": v.success_rate,
                            "avg_reward": v.avg_reward,
                            "adjustment_factor": v.adjustment_factor
                        }
                        for k, v in self.policies.items()
                    }
                },
                confidence=0.8,
                priority=3,
                reasoning="تحديث النماذج بناءً على التغذية الراجعة",
                source_agent=self.agent_id
            )

        # Generate learning insights
        insights = await self._generate_insights()
        if insights:
            return AgentAction(
                action_type="learning_insights",
                parameters={"insights": insights},
                confidence=0.75,
                priority=4,
                reasoning="رؤى من التعلم المستمر",
                source_agent=self.agent_id
            )

        return None

    async def _generate_insights(self) -> List[Dict[str, Any]]:
        """توليد رؤى من التعلم"""
        insights = []

        # Best performing actions
        if self.policies:
            sorted_policies = sorted(
                self.policies.values(),
                key=lambda p: p.avg_reward,
                reverse=True
            )

            if sorted_policies and sorted_policies[0].avg_reward > 0.5:
                insights.append({
                    "type": "top_performer",
                    "action": sorted_policies[0].action_type,
                    "success_rate": sorted_policies[0].success_rate,
                    "message_ar": f"الإجراء الأفضل أداءً: {sorted_policies[0].action_type}"
                })

            # Worst performing
            if sorted_policies and sorted_policies[-1].avg_reward < -0.2:
                insights.append({
                    "type": "needs_improvement",
                    "action": sorted_policies[-1].action_type,
                    "success_rate": sorted_policies[-1].success_rate,
                    "message_ar": f"يحتاج تحسين: {sorted_policies[-1].action_type}"
                })

        return insights

    async def act(self, action: AgentAction) -> Dict[str, Any]:
        """تنفيذ الإجراء"""
        return {
            "action_type": action.action_type,
            "executed_at": datetime.now().isoformat(),
            "parameters": action.parameters,
            "success": True
        }

    def get_policy_adjustments(self, action_type: str) -> float:
        """الحصول على عامل التعديل للإجراء"""
        policy = self.policies.get(action_type)
        if policy:
            return policy.adjustment_factor
        return 1.0

    def get_best_action(self, state: str) -> Optional[str]:
        """الحصول على أفضل إجراء للحالة"""
        if state in self.q_table:
            actions = self.q_table[state]
            if actions:
                return max(actions, key=actions.get)
        return None

    def get_learning_stats(self) -> Dict[str, Any]:
        """إحصائيات التعلم"""
        return {
            "total_feedback": len(self.feedback_history),
            "policies_count": len(self.policies),
            "q_table_states": len(self.q_table),
            "pending_adjustments": len(self.adjustment_queue),
            "agent_performance": {
                agent_id: {
                    "avg_reward": sum(rewards) / len(rewards) if rewards else 0,
                    "samples": len(rewards)
                }
                for agent_id, rewards in self.agent_rewards.items()
            }
        }
