"""
Agent Registry Storage Layer
طبقة تخزين سجل الوكلاء

Implements both in-memory and Redis-backed storage for agent cards.
ينفذ التخزين في الذاكرة والمدعوم بـ Redis لبطاقات الوكلاء.
"""

import json
import os
import sys

import structlog
from redis import asyncio as aioredis

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))
from registry.agent_card import AgentCard
from registry.registry import HealthCheckResult

logger = structlog.get_logger()


class RegistryStorage:
    """
    Base storage interface
    واجهة التخزين الأساسية
    """

    async def save_agent(self, agent_card: AgentCard) -> bool:
        """Save agent card / حفظ بطاقة الوكيل"""
        raise NotImplementedError

    async def get_agent(self, agent_id: str) -> AgentCard | None:
        """Get agent card / الحصول على بطاقة الوكيل"""
        raise NotImplementedError

    async def delete_agent(self, agent_id: str) -> bool:
        """Delete agent card / حذف بطاقة الوكيل"""
        raise NotImplementedError

    async def list_agents(self) -> list[AgentCard]:
        """List all agents / قائمة بجميع الوكلاء"""
        raise NotImplementedError

    async def save_health_status(self, agent_id: str, status: HealthCheckResult) -> bool:
        """Save health status / حفظ حالة الصحة"""
        raise NotImplementedError

    async def get_health_status(self, agent_id: str) -> HealthCheckResult | None:
        """Get health status / الحصول على حالة الصحة"""
        raise NotImplementedError


class InMemoryStorage(RegistryStorage):
    """
    In-memory storage implementation
    تطبيق التخزين في الذاكرة

    Fast but non-persistent. Useful for development and testing.
    سريع ولكنه غير دائم. مفيد للتطوير والاختبار.
    """

    def __init__(self):
        self._agents: dict[str, AgentCard] = {}
        self._health_status: dict[str, HealthCheckResult] = {}
        self._logger = logger.bind(storage="in_memory")

    async def save_agent(self, agent_card: AgentCard) -> bool:
        """Save agent card in memory"""
        self._agents[agent_card.agent_id] = agent_card
        self._logger.debug("agent_saved", agent_id=agent_card.agent_id)
        return True

    async def get_agent(self, agent_id: str) -> AgentCard | None:
        """Get agent card from memory"""
        return self._agents.get(agent_id)

    async def delete_agent(self, agent_id: str) -> bool:
        """Delete agent card from memory"""
        if agent_id in self._agents:
            del self._agents[agent_id]
            if agent_id in self._health_status:
                del self._health_status[agent_id]
            self._logger.debug("agent_deleted", agent_id=agent_id)
            return True
        return False

    async def list_agents(self) -> list[AgentCard]:
        """List all agents from memory"""
        return list(self._agents.values())

    async def save_health_status(self, agent_id: str, status: HealthCheckResult) -> bool:
        """Save health status in memory"""
        self._health_status[agent_id] = status
        return True

    async def get_health_status(self, agent_id: str) -> HealthCheckResult | None:
        """Get health status from memory"""
        return self._health_status.get(agent_id)


class RedisStorage(RegistryStorage):
    """
    Redis-backed storage implementation
    تطبيق التخزين المدعوم بـ Redis

    Persistent and distributed. Recommended for production.
    دائم وموزع. موصى به للإنتاج.
    """

    def __init__(
        self,
        redis_url: str,
        key_prefix: str = "sahool:registry:",
        ttl_seconds: int = 3600,
    ):
        """
        Initialize Redis storage

        Args:
            redis_url: Redis connection URL
            key_prefix: Prefix for all keys
            ttl_seconds: Time-to-live for agent cards
        """
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self.ttl_seconds = ttl_seconds
        self._redis: aioredis.Redis | None = None
        self._logger = logger.bind(storage="redis")

    async def connect(self):
        """Connect to Redis / الاتصال بـ Redis"""
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
        """Close Redis connection / إغلاق اتصال Redis"""
        if self._redis:
            await self._redis.close()
            self._logger.info("redis_disconnected")

    def _agent_key(self, agent_id: str) -> str:
        """Get Redis key for agent / الحصول على مفتاح Redis للوكيل"""
        return f"{self.key_prefix}agent:{agent_id}"

    def _health_key(self, agent_id: str) -> str:
        """Get Redis key for health status / الحصول على مفتاح Redis لحالة الصحة"""
        return f"{self.key_prefix}health:{agent_id}"

    def _agents_set_key(self) -> str:
        """Get Redis key for agents set / الحصول على مفتاح Redis لمجموعة الوكلاء"""
        return f"{self.key_prefix}agents"

    async def save_agent(self, agent_card: AgentCard) -> bool:
        """Save agent card to Redis"""
        if not self._redis:
            raise RuntimeError("Redis not connected")

        try:
            # Serialize agent card
            agent_json = agent_card.to_json()

            # Save to Redis with TTL
            key = self._agent_key(agent_card.agent_id)
            await self._redis.setex(key, self.ttl_seconds, agent_json)

            # Add to agents set
            await self._redis.sadd(self._agents_set_key(), agent_card.agent_id)

            self._logger.debug("agent_saved_to_redis", agent_id=agent_card.agent_id)
            return True

        except Exception as e:
            self._logger.error("save_agent_failed", agent_id=agent_card.agent_id, error=str(e))
            raise

    async def get_agent(self, agent_id: str) -> AgentCard | None:
        """Get agent card from Redis"""
        if not self._redis:
            raise RuntimeError("Redis not connected")

        try:
            key = self._agent_key(agent_id)
            agent_json = await self._redis.get(key)

            if not agent_json:
                return None

            agent_data = json.loads(agent_json)
            return AgentCard.from_dict(agent_data)

        except Exception as e:
            self._logger.error("get_agent_failed", agent_id=agent_id, error=str(e))
            raise

    async def delete_agent(self, agent_id: str) -> bool:
        """Delete agent card from Redis"""
        if not self._redis:
            raise RuntimeError("Redis not connected")

        try:
            # Delete agent key
            agent_key = self._agent_key(agent_id)
            deleted = await self._redis.delete(agent_key)

            # Delete health status
            health_key = self._health_key(agent_id)
            await self._redis.delete(health_key)

            # Remove from agents set
            await self._redis.srem(self._agents_set_key(), agent_id)

            self._logger.debug("agent_deleted_from_redis", agent_id=agent_id)
            return deleted > 0

        except Exception as e:
            self._logger.error("delete_agent_failed", agent_id=agent_id, error=str(e))
            raise

    async def list_agents(self) -> list[AgentCard]:
        """List all agents from Redis"""
        if not self._redis:
            raise RuntimeError("Redis not connected")

        try:
            # Get all agent IDs from set
            agent_ids = await self._redis.smembers(self._agents_set_key())

            # Get all agent cards
            agents = []
            for agent_id in agent_ids:
                agent = await self.get_agent(agent_id)
                if agent:
                    agents.append(agent)

            return agents

        except Exception as e:
            self._logger.error("list_agents_failed", error=str(e))
            raise

    async def save_health_status(self, agent_id: str, status: HealthCheckResult) -> bool:
        """Save health status to Redis"""
        if not self._redis:
            raise RuntimeError("Redis not connected")

        try:
            key = self._health_key(agent_id)
            status_json = status.model_dump_json()

            # Save with shorter TTL (health status expires faster)
            await self._redis.setex(key, 300, status_json)  # 5 minutes TTL

            return True

        except Exception as e:
            self._logger.error("save_health_status_failed", agent_id=agent_id, error=str(e))
            raise

    async def get_health_status(self, agent_id: str) -> HealthCheckResult | None:
        """Get health status from Redis"""
        if not self._redis:
            raise RuntimeError("Redis not connected")

        try:
            key = self._health_key(agent_id)
            status_json = await self._redis.get(key)

            if not status_json:
                return None

            status_data = json.loads(status_json)
            return HealthCheckResult(**status_data)

        except Exception as e:
            self._logger.error("get_health_status_failed", agent_id=agent_id, error=str(e))
            raise
