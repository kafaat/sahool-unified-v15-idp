"""
SAHOOL Agent Registry Service
خدمة سجل وكلاء سهول

Core registry service for agent registration, discovery, and health monitoring.
خدمة السجل الأساسية لتسجيل الوكلاء واكتشافهم ومراقبة الصحة.
"""

import asyncio
from datetime import datetime
from enum import Enum
from typing import Any

import httpx
import structlog
from pydantic import BaseModel, Field

from .agent_card import AgentCard

logger = structlog.get_logger()


class HealthStatus(str, Enum):
    """Agent health status / حالة صحة الوكيل"""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class HealthCheckResult(BaseModel):
    """Health check result / نتيجة فحص الصحة"""

    agent_id: str
    status: HealthStatus
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    response_time_ms: float | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class RegistryConfig(BaseModel):
    """
    Registry configuration
    تكوين السجل
    """

    health_check_interval_seconds: int = Field(
        default=60, description="How often to check agent health", ge=10, le=3600
    )
    health_check_timeout_seconds: int = Field(
        default=5, description="Health check request timeout", ge=1, le=60
    )
    max_retries: int = Field(
        default=3, description="Max health check retries", ge=0, le=10
    )
    enable_auto_discovery: bool = Field(
        default=False, description="Enable automatic agent discovery"
    )
    ttl_seconds: int = Field(default=3600, description="Agent registration TTL", ge=60)


class AgentRegistry:
    """
    Agent Registry Service
    خدمة سجل الوكلاء

    Manages agent registration, discovery, and health monitoring.
    يدير تسجيل الوكلاء واكتشافهم ومراقبة الصحة.

    Features:
    - Agent registration and deregistration
    - Capability-based discovery
    - Health monitoring
    - Version management
    - Dependency tracking
    """

    def __init__(self, config: RegistryConfig | None = None):
        """Initialize registry / تهيئة السجل"""
        self.config = config or RegistryConfig()
        self._agents: dict[str, AgentCard] = {}
        self._health_status: dict[str, HealthCheckResult] = {}
        self._capability_index: dict[str, set[str]] = {}
        self._skill_index: dict[str, set[str]] = {}
        self._tag_index: dict[str, set[str]] = {}
        self._health_check_task: asyncio.Task | None = None
        self._logger = logger.bind(component="agent_registry")

    async def start(self):
        """
        Start the registry service
        بدء خدمة السجل
        """
        self._logger.info("agent_registry_starting")

        # Start background health check task
        if self.config.health_check_interval_seconds > 0:
            self._health_check_task = asyncio.create_task(self._health_check_loop())

        self._logger.info(
            "agent_registry_started",
            health_check_enabled=self._health_check_task is not None,
        )

    async def stop(self):
        """
        Stop the registry service
        إيقاف خدمة السجل
        """
        self._logger.info("agent_registry_stopping")

        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        self._logger.info("agent_registry_stopped")

    async def register_agent(self, agent_card: AgentCard) -> bool:
        """
        Register an agent
        تسجيل وكيل

        Args:
            agent_card: Agent card to register

        Returns:
            True if registered successfully, False if already exists
        """
        try:
            # Validate agent card
            agent_card.metadata.updated_at = datetime.utcnow()

            # Store agent
            self._agents[agent_card.agent_id] = agent_card

            # Index capabilities
            for capability in agent_card.capabilities:
                cap_name = capability.name.lower()
                if cap_name not in self._capability_index:
                    self._capability_index[cap_name] = set()
                self._capability_index[cap_name].add(agent_card.agent_id)

            # Index skills
            for skill in agent_card.skills:
                skill_id = skill.skill_id.lower()
                if skill_id not in self._skill_index:
                    self._skill_index[skill_id] = set()
                self._skill_index[skill_id].add(agent_card.agent_id)

                # Index skill keywords
                for keyword in skill.keywords:
                    keyword_lower = keyword.lower()
                    if keyword_lower not in self._tag_index:
                        self._tag_index[keyword_lower] = set()
                    self._tag_index[keyword_lower].add(agent_card.agent_id)

            # Index metadata tags
            for tag in agent_card.metadata.tags:
                tag_lower = tag.lower()
                if tag_lower not in self._tag_index:
                    self._tag_index[tag_lower] = set()
                self._tag_index[tag_lower].add(agent_card.agent_id)

            self._logger.info(
                "agent_registered",
                agent_id=agent_card.agent_id,
                version=agent_card.version,
                capabilities=len(agent_card.capabilities),
            )

            return True

        except Exception as e:
            self._logger.error(
                "agent_registration_failed", agent_id=agent_card.agent_id, error=str(e)
            )
            raise

    async def deregister_agent(self, agent_id: str) -> bool:
        """
        Deregister an agent
        إلغاء تسجيل وكيل

        Args:
            agent_id: Agent ID to deregister

        Returns:
            True if deregistered, False if not found
        """
        if agent_id not in self._agents:
            return False

        agent_card = self._agents[agent_id]

        # Remove from capability index
        for capability in agent_card.capabilities:
            cap_name = capability.name.lower()
            if cap_name in self._capability_index:
                self._capability_index[cap_name].discard(agent_id)

        # Remove from skill index
        for skill in agent_card.skills:
            skill_id = skill.skill_id.lower()
            if skill_id in self._skill_index:
                self._skill_index[skill_id].discard(agent_id)

        # Remove from tag index
        for tag in agent_card.metadata.tags:
            tag_lower = tag.lower()
            if tag_lower in self._tag_index:
                self._tag_index[tag_lower].discard(agent_id)

        # Remove agent
        del self._agents[agent_id]

        # Remove health status
        if agent_id in self._health_status:
            del self._health_status[agent_id]

        self._logger.info("agent_deregistered", agent_id=agent_id)
        return True

    def get_agent(self, agent_id: str) -> AgentCard | None:
        """
        Get agent by ID
        الحصول على وكيل بواسطة المعرف

        Args:
            agent_id: Agent ID

        Returns:
            AgentCard if found, None otherwise
        """
        return self._agents.get(agent_id)

    def list_agents(
        self,
        status: str | None = None,
        category: str | None = None,
    ) -> list[AgentCard]:
        """
        List all agents with optional filters
        قائمة بجميع الوكلاء مع مرشحات اختيارية

        Args:
            status: Filter by status (active, inactive, etc.)
            category: Filter by category

        Returns:
            List of matching agent cards
        """
        agents = list(self._agents.values())

        if status:
            agents = [a for a in agents if a.status == status]

        if category:
            agents = [a for a in agents if a.metadata.category == category]

        return agents

    def discover_by_capability(self, capability_name: str) -> list[AgentCard]:
        """
        Discover agents by capability
        اكتشاف الوكلاء حسب القدرة

        Args:
            capability_name: Name of the capability to search for

        Returns:
            List of agents with the specified capability
        """
        cap_name = capability_name.lower()
        agent_ids = self._capability_index.get(cap_name, set())
        return [self._agents[aid] for aid in agent_ids if aid in self._agents]

    def discover_by_skill(self, skill_id: str) -> list[AgentCard]:
        """
        Discover agents by skill
        اكتشاف الوكلاء حسب المهارة

        Args:
            skill_id: Skill identifier

        Returns:
            List of agents with the specified skill
        """
        skill_lower = skill_id.lower()
        agent_ids = self._skill_index.get(skill_lower, set())
        return [self._agents[aid] for aid in agent_ids if aid in self._agents]

    def discover_by_tags(self, tags: list[str]) -> list[AgentCard]:
        """
        Discover agents by tags/keywords
        اكتشاف الوكلاء حسب العلامات/الكلمات المفتاحية

        Args:
            tags: List of tags to search for

        Returns:
            List of agents matching any of the tags
        """
        matching_agents: set[str] = set()

        for tag in tags:
            tag_lower = tag.lower()
            agent_ids = self._tag_index.get(tag_lower, set())
            matching_agents.update(agent_ids)

        return [self._agents[aid] for aid in matching_agents if aid in self._agents]

    async def check_agent_health(self, agent_id: str) -> HealthCheckResult:
        """
        Check health of a specific agent
        فحص صحة وكيل محدد

        Args:
            agent_id: Agent ID to check

        Returns:
            Health check result
        """
        agent_card = self._agents.get(agent_id)

        if not agent_card:
            return HealthCheckResult(
                agent_id=agent_id,
                status=HealthStatus.UNKNOWN,
                error="Agent not found in registry",
            )

        if not agent_card.health_endpoint:
            return HealthCheckResult(
                agent_id=agent_id,
                status=HealthStatus.UNKNOWN,
                error="No health endpoint configured",
            )

        start_time = datetime.utcnow()

        try:
            async with httpx.AsyncClient(
                timeout=self.config.health_check_timeout_seconds
            ) as client:
                response = await client.get(str(agent_card.health_endpoint))

                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

                if response.status_code == 200:
                    status = HealthStatus.HEALTHY
                elif response.status_code >= 500:
                    status = HealthStatus.UNHEALTHY
                else:
                    status = HealthStatus.DEGRADED

                result = HealthCheckResult(
                    agent_id=agent_id,
                    status=status,
                    response_time_ms=response_time,
                    metadata=(
                        response.json()
                        if response.headers.get("content-type", "").startswith(
                            "application/json"
                        )
                        else {}
                    ),
                )

        except Exception as e:
            result = HealthCheckResult(
                agent_id=agent_id, status=HealthStatus.UNHEALTHY, error=str(e)
            )

        # Cache result
        self._health_status[agent_id] = result

        return result

    def get_health_status(self, agent_id: str) -> HealthCheckResult | None:
        """
        Get cached health status
        الحصول على حالة الصحة المخزنة مؤقتًا

        Args:
            agent_id: Agent ID

        Returns:
            Last health check result, or None if not checked yet
        """
        return self._health_status.get(agent_id)

    def get_all_health_statuses(self) -> dict[str, HealthCheckResult]:
        """
        Get all cached health statuses
        الحصول على جميع حالات الصحة المخزنة مؤقتًا

        Returns:
            Dictionary of agent_id -> health status
        """
        return dict(self._health_status)

    def get_registry_stats(self) -> dict[str, Any]:
        """
        Get registry statistics
        الحصول على إحصائيات السجل

        Returns:
            Dictionary with registry statistics
        """
        healthy_count = sum(
            1
            for status in self._health_status.values()
            if status.status == HealthStatus.HEALTHY
        )

        return {
            "total_agents": len(self._agents),
            "active_agents": len(
                [a for a in self._agents.values() if a.status == "active"]
            ),
            "inactive_agents": len(
                [a for a in self._agents.values() if a.status == "inactive"]
            ),
            "healthy_agents": healthy_count,
            "capabilities": len(self._capability_index),
            "skills": len(self._skill_index),
            "tags": len(self._tag_index),
        }

    async def _health_check_loop(self):
        """
        Background health check loop
        حلقة فحص الصحة في الخلفية
        """
        self._logger.info(
            "health_check_loop_started",
            interval_seconds=self.config.health_check_interval_seconds,
        )

        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval_seconds)

                # Check health of all active agents
                active_agents = [
                    a
                    for a in self._agents.values()
                    if a.status == "active" and a.health_endpoint
                ]

                self._logger.debug("running_health_checks", count=len(active_agents))

                # Check all agents concurrently
                tasks = [
                    self.check_agent_health(agent.agent_id) for agent in active_agents
                ]

                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)

            except asyncio.CancelledError:
                self._logger.info("health_check_loop_cancelled")
                break
            except Exception as e:
                self._logger.error("health_check_loop_error", error=str(e))
                # Continue loop even on error
