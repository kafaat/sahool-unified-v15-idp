"""
Unit Tests for Agent Registry Client
اختبارات الوحدة لعميل سجل الوكلاء

Tests the AgentRegistryClient functionality including registration,
discovery, and performance tracking.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from src.multi_agent.infrastructure.registry_client import (
    AgentCard,
    AgentCapability,
    AgentStatus,
    AgentRegistryClient,
)


@pytest.fixture
def sample_agent_card():
    """Create a sample agent card for testing"""
    return AgentCard(
        agent_id="test-agent",
        name="Test Agent",
        description="Test agent for unit testing",
        description_ar="وكيل اختبار",
        capabilities=[AgentCapability.DIAGNOSIS, AgentCapability.TREATMENT],
        skills=["test_skill"],
        model="claude-3-5-sonnet-20241022",
        endpoint="http://localhost:8112/test",
        status=AgentStatus.ACTIVE,
        performance_score=0.85,
        tags=["test"],
    )


@pytest.fixture
def registry_client():
    """Create a registry client for testing"""
    return AgentRegistryClient(
        redis_url="redis://localhost:6379/0",
        key_prefix="test:agents:",
        cache_ttl=60,
        agent_ttl=300,
    )


class TestAgentCard:
    """Test AgentCard data model"""

    def test_agent_card_creation(self, sample_agent_card):
        """Test creating an agent card"""
        assert sample_agent_card.agent_id == "test-agent"
        assert sample_agent_card.name == "Test Agent"
        assert AgentCapability.DIAGNOSIS in sample_agent_card.capabilities
        assert sample_agent_card.status == AgentStatus.ACTIVE

    def test_agent_card_to_dict(self, sample_agent_card):
        """Test converting agent card to dictionary"""
        data = sample_agent_card.to_dict()

        assert data["agent_id"] == "test-agent"
        assert data["name"] == "Test Agent"
        assert "diagnosis" in data["capabilities"]
        assert data["status"] == "active"
        assert isinstance(data["last_heartbeat"], str)

    def test_agent_card_from_dict(self, sample_agent_card):
        """Test creating agent card from dictionary"""
        data = sample_agent_card.to_dict()
        restored = AgentCard.from_dict(data)

        assert restored.agent_id == sample_agent_card.agent_id
        assert restored.name == sample_agent_card.name
        assert restored.capabilities == sample_agent_card.capabilities
        assert restored.status == sample_agent_card.status

    def test_agent_card_to_json(self, sample_agent_card):
        """Test converting agent card to JSON"""
        json_str = sample_agent_card.to_json()

        assert isinstance(json_str, str)
        assert "test-agent" in json_str
        assert "Test Agent" in json_str

    def test_agent_card_from_json(self, sample_agent_card):
        """Test creating agent card from JSON"""
        json_str = sample_agent_card.to_json()
        restored = AgentCard.from_json(json_str)

        assert restored.agent_id == sample_agent_card.agent_id
        assert restored.name == sample_agent_card.name


class TestAgentRegistryClient:
    """Test AgentRegistryClient functionality"""

    @pytest.mark.asyncio
    async def test_connect(self, registry_client):
        """Test connecting to Redis"""
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_redis_instance = AsyncMock()
            mock_redis_instance.ping = AsyncMock()
            mock_redis.return_value = mock_redis_instance

            await registry_client.connect()

            assert registry_client._redis is not None
            mock_redis.assert_called_once()
            mock_redis_instance.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_close(self, registry_client):
        """Test closing Redis connection"""
        registry_client._redis = AsyncMock()

        await registry_client.close()

        registry_client._redis.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_agent(self, registry_client, sample_agent_card):
        """Test registering an agent"""
        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock()
        mock_redis.sadd = AsyncMock()
        mock_redis.expire = AsyncMock()
        registry_client._redis = mock_redis

        result = await registry_client.register_agent(sample_agent_card)

        assert result is True
        assert mock_redis.setex.called
        assert mock_redis.sadd.called

    @pytest.mark.asyncio
    async def test_get_agent(self, registry_client, sample_agent_card):
        """Test getting an agent by ID"""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=sample_agent_card.to_json())
        registry_client._redis = mock_redis

        agent = await registry_client.get_agent("test-agent")

        assert agent is not None
        assert agent.agent_id == "test-agent"
        assert agent.name == "Test Agent"

    @pytest.mark.asyncio
    async def test_get_agent_not_found(self, registry_client):
        """Test getting non-existent agent"""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)
        registry_client._redis = mock_redis

        agent = await registry_client.get_agent("non-existent")

        assert agent is None

    @pytest.mark.asyncio
    async def test_deregister_agent(self, registry_client, sample_agent_card):
        """Test deregistering an agent"""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=sample_agent_card.to_json())
        mock_redis.delete = AsyncMock()
        mock_redis.srem = AsyncMock()
        registry_client._redis = mock_redis

        result = await registry_client.deregister_agent("test-agent")

        assert result is True
        assert mock_redis.delete.called
        assert mock_redis.srem.called

    @pytest.mark.asyncio
    async def test_update_status(self, registry_client, sample_agent_card):
        """Test updating agent status"""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=sample_agent_card.to_json())
        mock_redis.setex = AsyncMock()
        mock_redis.sadd = AsyncMock()
        mock_redis.expire = AsyncMock()
        registry_client._redis = mock_redis

        result = await registry_client.update_status(
            "test-agent",
            AgentStatus.BUSY
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_heartbeat(self, registry_client, sample_agent_card):
        """Test sending heartbeat"""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=sample_agent_card.to_json())
        mock_redis.setex = AsyncMock()
        mock_redis.sadd = AsyncMock()
        mock_redis.expire = AsyncMock()
        registry_client._redis = mock_redis

        result = await registry_client.heartbeat("test-agent")

        assert result is True

    @pytest.mark.asyncio
    async def test_discover_agents(self, registry_client, sample_agent_card):
        """Test discovering agents by capability"""
        mock_redis = AsyncMock()
        mock_redis.smembers = AsyncMock(return_value={"test-agent"})
        mock_redis.get = AsyncMock(return_value=sample_agent_card.to_json())
        registry_client._redis = mock_redis

        agents = await registry_client.discover_agents([AgentCapability.DIAGNOSIS])

        assert len(agents) == 1
        assert agents[0].agent_id == "test-agent"

    @pytest.mark.asyncio
    async def test_get_best_agent(self, registry_client, sample_agent_card):
        """Test getting best performing agent"""
        mock_redis = AsyncMock()
        mock_redis.smembers = AsyncMock(return_value={"test-agent"})
        mock_redis.get = AsyncMock(return_value=sample_agent_card.to_json())
        registry_client._redis = mock_redis

        best_agent = await registry_client.get_best_agent(AgentCapability.DIAGNOSIS)

        assert best_agent is not None
        assert best_agent.agent_id == "test-agent"
        assert best_agent.performance_score == 0.85

    @pytest.mark.asyncio
    async def test_update_performance(self, registry_client, sample_agent_card):
        """Test updating performance score"""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=sample_agent_card.to_json())
        mock_redis.setex = AsyncMock()
        mock_redis.sadd = AsyncMock()
        mock_redis.expire = AsyncMock()
        registry_client._redis = mock_redis

        result = await registry_client.update_performance("test-agent", 0.95)

        assert result is True

    @pytest.mark.asyncio
    async def test_performance_score_bounds(self, registry_client, sample_agent_card):
        """Test that performance score is bounded between 0 and 1"""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=sample_agent_card.to_json())
        mock_redis.setex = AsyncMock()
        mock_redis.sadd = AsyncMock()
        mock_redis.expire = AsyncMock()
        registry_client._redis = mock_redis

        # Test upper bound
        await registry_client.update_performance("test-agent", 1.5)
        # Test lower bound
        await registry_client.update_performance("test-agent", -0.5)

        # Should not raise error (scores are clamped)

    @pytest.mark.asyncio
    async def test_get_registry_stats(self, registry_client, sample_agent_card):
        """Test getting registry statistics"""
        mock_redis = AsyncMock()
        mock_redis.smembers = AsyncMock(return_value={"test-agent"})
        mock_redis.get = AsyncMock(return_value=sample_agent_card.to_json())
        registry_client._redis = mock_redis

        stats = await registry_client.get_registry_stats()

        assert "total_agents" in stats
        assert "status_distribution" in stats
        assert "capability_distribution" in stats
        assert "average_performance" in stats

    def test_cache_get_set(self, registry_client):
        """Test cache operations"""
        # Set cache
        registry_client._set_cache("test_key", "test_value")

        # Get from cache
        value = registry_client._get_cache("test_key")
        assert value == "test_value"

        # Get expired cache (none should be expired immediately)
        value = registry_client._get_cache("test_key")
        assert value == "test_value"

    def test_cache_invalidation(self, registry_client):
        """Test cache invalidation"""
        # Set cache
        registry_client._set_cache("test_key_1", "value_1")
        registry_client._set_cache("test_key_2", "value_2")

        # Invalidate all
        registry_client._invalidate_cache()

        # Cache should be empty
        assert registry_client._get_cache("test_key_1") is None
        assert registry_client._get_cache("test_key_2") is None

    def test_cache_invalidation_pattern(self, registry_client):
        """Test cache invalidation with pattern"""
        # Set cache
        registry_client._set_cache("discover:diagnosis", "value_1")
        registry_client._set_cache("discover:treatment", "value_2")
        registry_client._set_cache("agent:test", "value_3")

        # Invalidate discover pattern
        registry_client._invalidate_cache("discover:")

        # Only discover keys should be invalidated
        assert registry_client._get_cache("discover:diagnosis") is None
        assert registry_client._get_cache("discover:treatment") is None
        assert registry_client._get_cache("agent:test") == "value_3"

    @pytest.mark.asyncio
    async def test_context_manager(self, registry_client):
        """Test using registry client as context manager"""
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_redis_instance = AsyncMock()
            mock_redis_instance.ping = AsyncMock()
            mock_redis_instance.close = AsyncMock()
            mock_redis.return_value = mock_redis_instance

            async with registry_client as client:
                assert client._redis is not None

            mock_redis_instance.close.assert_called_once()


class TestAgentCapability:
    """Test AgentCapability enum"""

    def test_all_capabilities_exist(self):
        """Test that all required capabilities are defined"""
        required = [
            "DIAGNOSIS",
            "TREATMENT",
            "IRRIGATION",
            "FERTILIZATION",
            "PEST_MANAGEMENT",
            "YIELD_PREDICTION",
            "MARKET_ANALYSIS",
            "SOIL_SCIENCE",
            "ECOLOGICAL",
            "WEATHER_ANALYSIS",
            "IMAGE_ANALYSIS",
            "SATELLITE_ANALYSIS",
        ]

        for cap_name in required:
            assert hasattr(AgentCapability, cap_name)

    def test_capability_values(self):
        """Test capability enum values"""
        assert AgentCapability.DIAGNOSIS.value == "diagnosis"
        assert AgentCapability.TREATMENT.value == "treatment"
        assert AgentCapability.IRRIGATION.value == "irrigation"


class TestAgentStatus:
    """Test AgentStatus enum"""

    def test_all_statuses_exist(self):
        """Test that all required statuses are defined"""
        required = ["ACTIVE", "INACTIVE", "BUSY", "MAINTENANCE"]

        for status_name in required:
            assert hasattr(AgentStatus, status_name)

    def test_status_values(self):
        """Test status enum values"""
        assert AgentStatus.ACTIVE.value == "active"
        assert AgentStatus.INACTIVE.value == "inactive"
        assert AgentStatus.BUSY.value == "busy"
        assert AgentStatus.MAINTENANCE.value == "maintenance"
