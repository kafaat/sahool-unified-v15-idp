"""
SAHOOL AI Agents - Base Agent Class
قاعدة الوكلاء الذكية

Implements the foundation for all agent types:
- Simple Reflex Agent
- Model-Based Agent
- Goal-Based Agent
- Utility-Based Agent
- Learning Agent
"""

import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """أنواع الوكلاء"""

    SIMPLE_REFLEX = "simple_reflex"  # If condition → Action
    MODEL_BASED = "model_based"  # Internal model of environment
    GOAL_BASED = "goal_based"  # Decision based on goal
    UTILITY_BASED = "utility_based"  # Best outcome selection
    LEARNING = "learning"  # Learns from experience


class AgentLayer(Enum):
    """طبقات الوكلاء"""

    EDGE = "edge"  # < 100ms response
    SPECIALIST = "specialist"  # Domain expert
    COORDINATOR = "coordinator"  # Integration & decisions
    LEARNING = "learning"  # Continuous improvement


class AgentStatus(Enum):
    """حالة الوكيل"""

    IDLE = "idle"
    PROCESSING = "processing"
    WAITING = "waiting"
    ERROR = "error"
    LEARNING = "learning"


@dataclass
class AgentContext:
    """سياق الوكيل - البيئة والمعلومات"""

    field_id: str | None = None
    crop_type: str | None = None
    location: dict[str, float] | None = None  # lat, lon
    timestamp: datetime = field(default_factory=datetime.now)
    sensor_data: dict[str, Any] = field(default_factory=dict)
    weather_data: dict[str, Any] = field(default_factory=dict)
    satellite_data: dict[str, Any] = field(default_factory=dict)
    history: list[dict[str, Any]] = field(default_factory=list)
    user_preferences: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentAction:
    """إجراء الوكيل"""

    action_type: str
    parameters: dict[str, Any]
    confidence: float  # 0.0 - 1.0
    priority: int  # 1 (highest) - 5 (lowest)
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.now)
    source_agent: str = ""
    requires_confirmation: bool = False


@dataclass
class AgentPercept:
    """إدراك الوكيل - المدخلات"""

    percept_type: str
    data: Any
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    reliability: float = 1.0  # 0.0 - 1.0


@dataclass
class AgentState:
    """حالة الوكيل الداخلية"""

    beliefs: dict[str, Any] = field(default_factory=dict)
    goals: list[str] = field(default_factory=list)
    intentions: list[str] = field(default_factory=list)
    knowledge: dict[str, Any] = field(default_factory=dict)
    memory: list[dict[str, Any]] = field(default_factory=list)


class BaseAgent(ABC):
    """
    الوكيل الأساسي - Base Agent

    كل الوكلاء يرثون من هذه الفئة الأساسية
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        name_ar: str,
        agent_type: AgentType,
        layer: AgentLayer,
        description: str = "",
        description_ar: str = "",
    ):
        self.agent_id = agent_id
        self.name = name
        self.name_ar = name_ar
        self.agent_type = agent_type
        self.layer = layer
        self.description = description
        self.description_ar = description_ar

        self.status = AgentStatus.IDLE
        self.state = AgentState()
        self.context: AgentContext | None = None

        # Performance metrics
        self.total_requests = 0
        self.successful_requests = 0
        self.total_response_time_ms = 0
        self.last_action_time: datetime | None = None

        # Learning metrics
        self.feedback_history: list[dict[str, Any]] = []
        self.reward_history: list[float] = []

        # Rules for Simple Reflex Agent
        self.rules: list[dict[str, Any]] = []

        # Utility function for Utility-Based Agent
        self.utility_function: Callable | None = None

        logger.info(f"Agent initialized: {self.name} ({self.agent_id})")

    @abstractmethod
    async def perceive(self, percept: AgentPercept) -> None:
        """
        استقبال المدخلات من البيئة
        Receive inputs from environment
        """
        pass

    @abstractmethod
    async def think(self) -> AgentAction | None:
        """
        معالجة المعلومات واتخاذ القرار
        Process information and make decision
        """
        pass

    @abstractmethod
    async def act(self, action: AgentAction) -> dict[str, Any]:
        """
        تنفيذ الإجراء
        Execute the action
        """
        pass

    async def run(self, percept: AgentPercept) -> dict[str, Any]:
        """
        دورة الوكيل الكاملة: إدراك → تفكير → فعل
        Full agent cycle: Perceive → Think → Act
        """
        start_time = datetime.now()
        self.status = AgentStatus.PROCESSING
        self.total_requests += 1

        try:
            # 1. Perceive - استقبال
            await self.perceive(percept)

            # 2. Think - تفكير
            action = await self.think()

            if action is None:
                self.status = AgentStatus.IDLE
                return {
                    "success": False,
                    "message": "No action determined",
                    "agent_id": self.agent_id,
                }

            # 3. Act - فعل
            result = await self.act(action)

            # Update metrics
            self.successful_requests += 1
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            self.total_response_time_ms += response_time
            self.last_action_time = datetime.now()

            self.status = AgentStatus.IDLE

            return {
                "success": True,
                "action": action,
                "result": result,
                "agent_id": self.agent_id,
                "response_time_ms": response_time,
            }

        except Exception as e:
            self.status = AgentStatus.ERROR
            logger.error(f"Agent {self.agent_id} error: {e}")
            return {"success": False, "error": str(e), "agent_id": self.agent_id}

    def add_rule(self, condition: Callable, action: AgentAction) -> None:
        """
        إضافة قاعدة للوكيل البسيط
        Add rule for Simple Reflex Agent
        """
        self.rules.append({"condition": condition, "action": action})

    def evaluate_rules(self, context: AgentContext) -> AgentAction | None:
        """
        تقييم القواعد للوكيل البسيط
        Evaluate rules for Simple Reflex Agent
        """
        for rule in self.rules:
            if rule["condition"](context):
                return rule["action"]
        return None

    def set_utility_function(self, func: Callable[[AgentAction, AgentContext], float]) -> None:
        """
        تعيين دالة المنفعة للوكيل القائم على المنفعة
        Set utility function for Utility-Based Agent
        """
        self.utility_function = func

    def calculate_utility(self, action: AgentAction, context: AgentContext) -> float:
        """
        حساب المنفعة
        Calculate utility
        """
        if self.utility_function:
            return self.utility_function(action, context)
        return 0.0

    def select_best_action(self, actions: list[AgentAction], context: AgentContext) -> AgentAction:
        """
        اختيار أفضل إجراء بناءً على المنفعة
        Select best action based on utility
        """
        if not actions:
            raise ValueError("No actions to select from")

        best_action = actions[0]
        best_utility = self.calculate_utility(best_action, context)

        for action in actions[1:]:
            utility = self.calculate_utility(action, context)
            if utility > best_utility:
                best_utility = utility
                best_action = action

        return best_action

    async def learn(self, feedback: dict[str, Any]) -> None:
        """
        التعلم من التجربة
        Learn from experience (for Learning Agent)
        """
        self.status = AgentStatus.LEARNING

        # Store feedback
        self.feedback_history.append(
            {"feedback": feedback, "timestamp": datetime.now().isoformat()}
        )

        # Calculate reward
        reward = feedback.get("reward", 0.0)
        self.reward_history.append(reward)

        # Update beliefs based on feedback
        if feedback.get("correct", True):
            # Reinforce current beliefs
            pass
        else:
            # Adjust beliefs
            correction = feedback.get("correction", {})
            for key, value in correction.items():
                self.state.beliefs[key] = value

        self.status = AgentStatus.IDLE
        logger.info(f"Agent {self.agent_id} learned from feedback: reward={reward}")

    def update_context(self, context: AgentContext) -> None:
        """تحديث سياق الوكيل"""
        self.context = context

    def get_metrics(self) -> dict[str, Any]:
        """الحصول على مقاييس الأداء"""
        avg_response_time = (
            self.total_response_time_ms / self.total_requests if self.total_requests > 0 else 0
        )
        success_rate = (
            self.successful_requests / self.total_requests * 100 if self.total_requests > 0 else 0
        )
        avg_reward = (
            sum(self.reward_history) / len(self.reward_history) if self.reward_history else 0
        )

        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.agent_type.value,
            "layer": self.layer.value,
            "status": self.status.value,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "success_rate_percent": round(success_rate, 2),
            "avg_response_time_ms": round(avg_response_time, 2),
            "avg_reward": round(avg_reward, 4),
            "last_action_time": self.last_action_time.isoformat()
            if self.last_action_time
            else None,
        }

    def to_dict(self) -> dict[str, Any]:
        """تحويل الوكيل إلى قاموس"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "type": self.agent_type.value,
            "layer": self.layer.value,
            "description": self.description,
            "description_ar": self.description_ar,
            "status": self.status.value,
            "metrics": self.get_metrics(),
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.agent_id}, name={self.name}, layer={self.layer.value})>"
