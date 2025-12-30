"""
SAHOOL Multi-Agent Registry Client
عميل سجل الوكلاء المتعدد لسهول

Dynamic agent discovery and management for agricultural AI agents.
اكتشاف وإدارة ديناميكية للوكلاء الذكيين الزراعيين.

Features / الميزات:
- Redis-backed distributed registry / سجل موزع مدعوم بـ Redis
- A2A Protocol compatible agent cards / بطاقات وكلاء متوافقة مع بروتوكول A2A
- Capability-based discovery / اكتشاف قائم على القدرات
- Performance tracking / تتبع الأداء
- Health monitoring / مراقبة الصحة
- In-memory caching / تخزين مؤقت في الذاكرة
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
import json
import structlog
from redis import asyncio as aioredis

logger = structlog.get_logger()


# ═══════════════════════════════════════════════════════════════════════════════
# Enums / التعدادات
# ═══════════════════════════════════════════════════════════════════════════════

class AgentStatus(str, Enum):
    """
    Agent operational status
    حالة تشغيل الوكيل
    """
    ACTIVE = "active"  # نشط - Agent is active and ready
    INACTIVE = "inactive"  # غير نشط - Agent is not available
    BUSY = "busy"  # مشغول - Agent is processing requests
    MAINTENANCE = "maintenance"  # صيانة - Under maintenance


class AgentCapability(str, Enum):
    """
    Agricultural agent capabilities
    قدرات الوكيل الزراعي

    Defines specific agricultural domain capabilities that agents can provide.
    يحدد قدرات المجال الزراعي المحددة التي يمكن للوكلاء توفيرها.
    """
    # Crop Health / صحة المحاصيل
    DIAGNOSIS = "diagnosis"  # تشخيص الأمراض - Disease and pest diagnosis
    TREATMENT = "treatment"  # علاج - Treatment recommendations

    # Water Management / إدارة المياه
    IRRIGATION = "irrigation"  # ري - Irrigation planning and optimization

    # Soil & Nutrition / التربة والتغذية
    FERTILIZATION = "fertilization"  # تسميد - Fertilization recommendations
    SOIL_SCIENCE = "soil_science"  # علم التربة - Soil analysis and health

    # Pest & Disease / الآفات والأمراض
    PEST_MANAGEMENT = "pest_management"  # إدارة الآفات - Integrated pest management

    # Analytics & Prediction / التحليل والتنبؤ
    YIELD_PREDICTION = "yield_prediction"  # توقع المحصول - Crop yield forecasting
    MARKET_ANALYSIS = "market_analysis"  # تحليل السوق - Market trends and pricing

    # Environmental / البيئة
    ECOLOGICAL = "ecological"  # بيئي - Ecological and sustainability analysis
    WEATHER_ANALYSIS = "weather_analysis"  # تحليل الطقس - Weather pattern analysis

    # Remote Sensing / الاستشعار عن بعد
    IMAGE_ANALYSIS = "image_analysis"  # تحليل الصور - Image-based crop analysis
    SATELLITE_ANALYSIS = "satellite_analysis"  # تحليل الأقمار الصناعية - Satellite imagery analysis


# ═══════════════════════════════════════════════════════════════════════════════
# Data Models / نماذج البيانات
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class AgentCard:
    """
    A2A Protocol-Compatible Agent Card
    بطاقة الوكيل المتوافقة مع بروتوكول A2A

    Comprehensive agent specification for registration and discovery.
    مواصفات شاملة للوكيل للتسجيل والاكتشاف.
    """
    # Core Identity / الهوية الأساسية
    agent_id: str  # معرف الوكيل الفريد
    name: str  # اسم الوكيل
    description: str  # وصف بالإنجليزية
    description_ar: str  # وصف بالعربية

    # Capabilities & Skills / القدرات والمهارات
    capabilities: List[AgentCapability] = field(default_factory=list)  # القدرات
    skills: List[str] = field(default_factory=list)  # المهارات المحددة

    # Model & Configuration / النموذج والإعدادات
    model: str = "claude-3-5-sonnet-20241022"  # نموذج اللغة المستخدم
    endpoint: str = ""  # نقطة نهاية الاستدعاء

    # Status & Performance / الحالة والأداء
    status: AgentStatus = AgentStatus.ACTIVE  # حالة الوكيل
    performance_score: float = 0.0  # درجة الأداء (0.0-1.0)
    last_heartbeat: datetime = field(default_factory=datetime.utcnow)  # آخر نبضة

    # Metadata / البيانات الوصفية
    version: str = "1.0.0"  # إصدار الوكيل
    tags: List[str] = field(default_factory=list)  # علامات للبحث
    created_at: datetime = field(default_factory=datetime.utcnow)  # تاريخ الإنشاء
    updated_at: datetime = field(default_factory=datetime.utcnow)  # تاريخ التحديث

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary
        تحويل إلى قاموس
        """
        data = asdict(self)
        # Convert enums and datetime to serializable formats
        data['capabilities'] = [c.value if isinstance(c, Enum) else c for c in self.capabilities]
        data['status'] = self.status.value if isinstance(self.status, Enum) else self.status
        data['last_heartbeat'] = self.last_heartbeat.isoformat()
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentCard':
        """
        Create from dictionary
        إنشاء من قاموس
        """
        # Convert string capabilities back to enum
        if 'capabilities' in data:
            data['capabilities'] = [
                AgentCapability(c) if isinstance(c, str) else c
                for c in data['capabilities']
            ]

        # Convert string status back to enum
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = AgentStatus(data['status'])

        # Convert ISO datetime strings back to datetime objects
        for field_name in ['last_heartbeat', 'created_at', 'updated_at']:
            if field_name in data and isinstance(data[field_name], str):
                data[field_name] = datetime.fromisoformat(data[field_name])

        return cls(**data)

    def to_json(self) -> str:
        """
        Convert to JSON string
        تحويل إلى نص JSON
        """
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'AgentCard':
        """
        Create from JSON string
        إنشاء من نص JSON
        """
        data = json.loads(json_str)
        return cls.from_dict(data)


# ═══════════════════════════════════════════════════════════════════════════════
# Agent Registry Client / عميل سجل الوكلاء
# ═══════════════════════════════════════════════════════════════════════════════

class AgentRegistryClient:
    """
    Redis-backed Agent Registry Client
    عميل سجل الوكلاء المدعوم بـ Redis

    Provides dynamic agent discovery, registration, and management with
    performance tracking and health monitoring.

    يوفر اكتشاف وتسجيل وإدارة ديناميكية للوكلاء مع تتبع الأداء ومراقبة الصحة.

    Features:
    - Agent registration and deregistration / تسجيل وإلغاء تسجيل الوكلاء
    - Capability-based discovery / اكتشاف قائم على القدرات
    - Performance scoring / تسجيل الأداء
    - Health monitoring / مراقبة الصحة
    - In-memory caching / تخزين مؤقت

    Example / مثال:
        ```python
        # Initialize client
        client = AgentRegistryClient(
            redis_url="redis://localhost:6379/0",
            key_prefix="sahool:agents:"
        )
        await client.connect()

        # Register an agent
        agent = AgentCard(
            agent_id="disease-expert",
            name="Disease Expert Agent",
            description="Expert in diagnosing crop diseases",
            description_ar="خبير في تشخيص أمراض المحاصيل",
            capabilities=[AgentCapability.DIAGNOSIS, AgentCapability.TREATMENT],
            model="claude-3-5-sonnet-20241022",
            endpoint="http://localhost:8112/agents/disease-expert"
        )
        await client.register_agent(agent)

        # Discover agents by capability
        agents = await client.discover_agents([AgentCapability.DIAGNOSIS])

        # Get best performing agent
        best_agent = await client.get_best_agent(AgentCapability.DIAGNOSIS)
        ```
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        key_prefix: str = "sahool:agents:",
        cache_ttl: int = 300,  # 5 minutes
        agent_ttl: int = 3600,  # 1 hour
    ):
        """
        Initialize registry client
        تهيئة عميل السجل

        Args:
            redis_url: Redis connection URL / رابط اتصال Redis
            key_prefix: Key prefix for Redis / بادئة المفاتيح في Redis
            cache_ttl: Cache TTL in seconds / مدة التخزين المؤقت بالثواني
            agent_ttl: Agent registration TTL / مدة تسجيل الوكيل
        """
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self.cache_ttl = cache_ttl
        self.agent_ttl = agent_ttl

        self._redis: Optional[aioredis.Redis] = None
        self._cache: Dict[str, tuple[Any, datetime]] = {}  # (value, expiry)
        self._logger = logger.bind(component="agent_registry_client")

    # ─── Connection Management ────────────────────────────────────────────

    async def connect(self):
        """
        Connect to Redis
        الاتصال بـ Redis
        """
        try:
            self._redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            await self._redis.ping()
            self._logger.info("redis_connected", url=self.redis_url)
        except Exception as e:
            self._logger.error("redis_connection_failed", error=str(e))
            raise

    async def close(self):
        """
        Close Redis connection
        إغلاق اتصال Redis
        """
        if self._redis:
            await self._redis.close()
            self._logger.info("redis_disconnected")

    async def __aenter__(self):
        """Context manager entry / دخول مدير السياق"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit / خروج مدير السياق"""
        await self.close()

    # ─── Cache Management ─────────────────────────────────────────────────

    def _get_cache(self, key: str) -> Optional[Any]:
        """Get value from cache / الحصول على قيمة من التخزين المؤقت"""
        if key in self._cache:
            value, expiry = self._cache[key]
            if datetime.utcnow() < expiry:
                return value
            else:
                del self._cache[key]
        return None

    def _set_cache(self, key: str, value: Any):
        """Set value in cache / تعيين قيمة في التخزين المؤقت"""
        expiry = datetime.utcnow() + timedelta(seconds=self.cache_ttl)
        self._cache[key] = (value, expiry)

    def _invalidate_cache(self, pattern: Optional[str] = None):
        """Invalidate cache / إبطال التخزين المؤقت"""
        if pattern:
            keys_to_delete = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self._cache[key]
        else:
            self._cache.clear()

    # ─── Redis Key Management ─────────────────────────────────────────────

    def _agent_key(self, agent_id: str) -> str:
        """Get Redis key for agent / الحصول على مفتاح Redis للوكيل"""
        return f"{self.key_prefix}agent:{agent_id}"

    def _capability_key(self, capability: AgentCapability) -> str:
        """Get Redis key for capability index / مفتاح فهرس القدرة"""
        return f"{self.key_prefix}capability:{capability.value}"

    def _performance_key(self, agent_id: str) -> str:
        """Get Redis key for performance / مفتاح الأداء"""
        return f"{self.key_prefix}performance:{agent_id}"

    def _agents_set_key(self) -> str:
        """Get Redis key for agents set / مفتاح مجموعة الوكلاء"""
        return f"{self.key_prefix}agents"

    # ─── Agent Registration ───────────────────────────────────────────────

    async def register_agent(self, agent_card: AgentCard) -> bool:
        """
        Register an agent in the registry
        تسجيل وكيل في السجل

        Args:
            agent_card: Agent card to register / بطاقة الوكيل للتسجيل

        Returns:
            True if successful / صحيح إذا نجح
        """
        if not self._redis:
            raise RuntimeError("Redis not connected. Call connect() first.")

        try:
            agent_card.updated_at = datetime.utcnow()

            # Save agent card
            agent_key = self._agent_key(agent_card.agent_id)
            agent_json = agent_card.to_json()
            await self._redis.setex(agent_key, self.agent_ttl, agent_json)

            # Add to agents set
            await self._redis.sadd(self._agents_set_key(), agent_card.agent_id)

            # Index by capabilities
            for capability in agent_card.capabilities:
                cap_key = self._capability_key(capability)
                await self._redis.sadd(cap_key, agent_card.agent_id)
                # Set expiry on capability index
                await self._redis.expire(cap_key, self.agent_ttl)

            # Initialize performance score if not set
            if agent_card.performance_score > 0:
                await self.update_performance(
                    agent_card.agent_id,
                    agent_card.performance_score
                )

            self._invalidate_cache()

            self._logger.info(
                "agent_registered",
                agent_id=agent_card.agent_id,
                capabilities=[c.value for c in agent_card.capabilities]
            )

            return True

        except Exception as e:
            self._logger.error(
                "agent_registration_failed",
                agent_id=agent_card.agent_id,
                error=str(e)
            )
            raise

    async def deregister_agent(self, agent_id: str) -> bool:
        """
        Remove an agent from the registry
        إزالة وكيل من السجل

        Args:
            agent_id: Agent ID to deregister / معرف الوكيل لإلغاء التسجيل

        Returns:
            True if successful / صحيح إذا نجح
        """
        if not self._redis:
            raise RuntimeError("Redis not connected. Call connect() first.")

        try:
            # Get agent to find capabilities
            agent = await self.get_agent(agent_id)

            # Delete agent key
            agent_key = self._agent_key(agent_id)
            await self._redis.delete(agent_key)

            # Remove from agents set
            await self._redis.srem(self._agents_set_key(), agent_id)

            # Remove from capability indexes
            if agent:
                for capability in agent.capabilities:
                    cap_key = self._capability_key(capability)
                    await self._redis.srem(cap_key, agent_id)

            # Delete performance score
            perf_key = self._performance_key(agent_id)
            await self._redis.delete(perf_key)

            self._invalidate_cache()

            self._logger.info("agent_deregistered", agent_id=agent_id)

            return True

        except Exception as e:
            self._logger.error(
                "agent_deregistration_failed",
                agent_id=agent_id,
                error=str(e)
            )
            raise

    # ─── Agent Status Management ──────────────────────────────────────────

    async def update_status(self, agent_id: str, status: AgentStatus) -> bool:
        """
        Update agent status
        تحديث حالة الوكيل

        Args:
            agent_id: Agent ID / معرف الوكيل
            status: New status / الحالة الجديدة

        Returns:
            True if successful / صحيح إذا نجح
        """
        if not self._redis:
            raise RuntimeError("Redis not connected. Call connect() first.")

        try:
            agent = await self.get_agent(agent_id)
            if not agent:
                return False

            agent.status = status
            agent.updated_at = datetime.utcnow()

            await self.register_agent(agent)  # Re-register with updated status

            self._logger.info(
                "agent_status_updated",
                agent_id=agent_id,
                status=status.value
            )

            return True

        except Exception as e:
            self._logger.error(
                "agent_status_update_failed",
                agent_id=agent_id,
                error=str(e)
            )
            raise

    async def heartbeat(self, agent_id: str) -> bool:
        """
        Send heartbeat to update last_heartbeat timestamp
        إرسال نبضة لتحديث الطابع الزمني للنبضة الأخيرة

        Args:
            agent_id: Agent ID / معرف الوكيل

        Returns:
            True if successful / صحيح إذا نجح
        """
        if not self._redis:
            raise RuntimeError("Redis not connected. Call connect() first.")

        try:
            agent = await self.get_agent(agent_id)
            if not agent:
                return False

            agent.last_heartbeat = datetime.utcnow()
            agent.updated_at = datetime.utcnow()

            await self.register_agent(agent)

            self._logger.debug("agent_heartbeat", agent_id=agent_id)

            return True

        except Exception as e:
            self._logger.error(
                "agent_heartbeat_failed",
                agent_id=agent_id,
                error=str(e)
            )
            raise

    # ─── Agent Discovery ──────────────────────────────────────────────────

    async def discover_agents(
        self,
        capabilities: List[AgentCapability]
    ) -> List[AgentCard]:
        """
        Discover agents by capabilities
        اكتشاف الوكلاء حسب القدرات

        Args:
            capabilities: List of required capabilities / قائمة القدرات المطلوبة

        Returns:
            List of matching agent cards / قائمة بطاقات الوكلاء المطابقة
        """
        if not self._redis:
            raise RuntimeError("Redis not connected. Call connect() first.")

        # Check cache
        cache_key = f"discover:{','.join(sorted([c.value for c in capabilities]))}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        try:
            # Get agent IDs for each capability
            agent_id_sets = []
            for capability in capabilities:
                cap_key = self._capability_key(capability)
                agent_ids = await self._redis.smembers(cap_key)
                agent_id_sets.append(set(agent_ids))

            # Find intersection (agents with ALL capabilities)
            if agent_id_sets:
                matching_ids = set.intersection(*agent_id_sets)
            else:
                matching_ids = set()

            # Get agent cards
            agents = []
            for agent_id in matching_ids:
                agent = await self.get_agent(agent_id)
                if agent and agent.status == AgentStatus.ACTIVE:
                    agents.append(agent)

            # Sort by performance score
            agents.sort(key=lambda a: a.performance_score, reverse=True)

            # Cache results
            self._set_cache(cache_key, agents)

            self._logger.info(
                "agents_discovered",
                capabilities=[c.value for c in capabilities],
                count=len(agents)
            )

            return agents

        except Exception as e:
            self._logger.error(
                "agent_discovery_failed",
                capabilities=[c.value for c in capabilities],
                error=str(e)
            )
            raise

    async def get_agent(self, agent_id: str) -> Optional[AgentCard]:
        """
        Get agent by ID
        الحصول على وكيل بالمعرف

        Args:
            agent_id: Agent ID / معرف الوكيل

        Returns:
            Agent card or None / بطاقة الوكيل أو لا شيء
        """
        if not self._redis:
            raise RuntimeError("Redis not connected. Call connect() first.")

        # Check cache
        cache_key = f"agent:{agent_id}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        try:
            agent_key = self._agent_key(agent_id)
            agent_json = await self._redis.get(agent_key)

            if not agent_json:
                return None

            agent = AgentCard.from_json(agent_json)

            # Cache result
            self._set_cache(cache_key, agent)

            return agent

        except Exception as e:
            self._logger.error(
                "get_agent_failed",
                agent_id=agent_id,
                error=str(e)
            )
            raise

    async def get_best_agent(
        self,
        capability: AgentCapability
    ) -> Optional[AgentCard]:
        """
        Get the best performing agent for a capability
        الحصول على أفضل وكيل أداءً لقدرة معينة

        Args:
            capability: Required capability / القدرة المطلوبة

        Returns:
            Best agent or None / أفضل وكيل أو لا شيء
        """
        agents = await self.discover_agents([capability])

        if not agents:
            return None

        # Already sorted by performance score in discover_agents
        best_agent = agents[0]

        self._logger.info(
            "best_agent_selected",
            capability=capability.value,
            agent_id=best_agent.agent_id,
            performance_score=best_agent.performance_score
        )

        return best_agent

    # ─── Performance Management ───────────────────────────────────────────

    async def update_performance(self, agent_id: str, score: float) -> bool:
        """
        Update agent performance score
        تحديث درجة أداء الوكيل

        Args:
            agent_id: Agent ID / معرف الوكيل
            score: Performance score (0.0-1.0) / درجة الأداء

        Returns:
            True if successful / صحيح إذا نجح
        """
        if not self._redis:
            raise RuntimeError("Redis not connected. Call connect() first.")

        try:
            # Validate score
            score = max(0.0, min(1.0, score))

            # Update agent card
            agent = await self.get_agent(agent_id)
            if not agent:
                return False

            agent.performance_score = score
            agent.updated_at = datetime.utcnow()

            await self.register_agent(agent)

            # Also store in sorted set for quick lookups
            perf_key = self._performance_key(agent_id)
            await self._redis.setex(perf_key, self.agent_ttl, str(score))

            self._invalidate_cache(f"discover:")

            self._logger.info(
                "agent_performance_updated",
                agent_id=agent_id,
                score=score
            )

            return True

        except Exception as e:
            self._logger.error(
                "agent_performance_update_failed",
                agent_id=agent_id,
                error=str(e)
            )
            raise

    # ─── Registry Statistics ──────────────────────────────────────────────

    async def get_registry_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics
        الحصول على إحصائيات السجل

        Returns:
            Statistics dictionary / قاموس الإحصائيات
        """
        if not self._redis:
            raise RuntimeError("Redis not connected. Call connect() first.")

        try:
            # Get all agent IDs
            agent_ids = await self._redis.smembers(self._agents_set_key())

            # Count by status
            status_counts = {status.value: 0 for status in AgentStatus}
            capability_counts: Dict[str, int] = {}
            total_performance = 0.0
            active_count = 0

            for agent_id in agent_ids:
                agent = await self.get_agent(agent_id)
                if agent:
                    status_counts[agent.status.value] += 1

                    for cap in agent.capabilities:
                        cap_value = cap.value
                        capability_counts[cap_value] = capability_counts.get(cap_value, 0) + 1

                    if agent.status == AgentStatus.ACTIVE:
                        total_performance += agent.performance_score
                        active_count += 1

            avg_performance = total_performance / active_count if active_count > 0 else 0.0

            stats = {
                "total_agents": len(agent_ids),
                "status_distribution": status_counts,
                "capability_distribution": capability_counts,
                "average_performance": round(avg_performance, 3),
                "cache_size": len(self._cache),
            }

            self._logger.info("registry_stats_retrieved", **stats)

            return stats

        except Exception as e:
            self._logger.error("get_registry_stats_failed", error=str(e))
            raise
