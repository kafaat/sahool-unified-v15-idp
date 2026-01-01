"""
SAHOOL Agent Registry Client
عميل سجل وكلاء سهول

Client for querying the agent registry and invoking remote agents.
عميل للاستعلام عن سجل الوكلاء واستدعاء الوكلاء عن بعد.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, HttpUrl
import httpx
import structlog
from datetime import datetime

from .agent_card import AgentCard, SecurityScheme
from .registry import HealthCheckResult, HealthStatus

logger = structlog.get_logger()


class AgentInvocationRequest(BaseModel):
    """
    Request to invoke an agent
    طلب لاستدعاء وكيل
    """

    capability: str = Field(..., description="Capability to invoke")
    input_data: Dict[str, Any] = Field(..., description="Input data for the agent")
    context: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional context"
    )
    timeout_seconds: int = Field(
        default=30, description="Request timeout", ge=1, le=300
    )

    class Config:
        json_schema_extra = {
            "example": {
                "capability": "diagnose_disease",
                "input_data": {
                    "crop_type": "wheat",
                    "symptoms": {"leaf_spots": True, "wilting": False},
                },
                "context": {"tenant_id": "tenant_123", "field_id": "field_456"},
                "timeout_seconds": 30,
            }
        }


class AgentInvocationResponse(BaseModel):
    """
    Response from agent invocation
    استجابة من استدعاء الوكيل
    """

    status: str = Field(..., description="Response status (success/error)")
    agent_id: str = Field(..., description="ID of the agent that processed the request")
    capability: str = Field(..., description="Capability that was invoked")
    output_data: Optional[Dict[str, Any]] = Field(
        None, description="Output data from the agent"
    )
    error: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Response metadata"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )
    response_time_ms: Optional[float] = Field(
        None, description="Response time in milliseconds"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "agent_id": "disease-expert-agent",
                "capability": "diagnose_disease",
                "output_data": {
                    "disease": "leaf_rust",
                    "confidence": 0.92,
                    "recommendations": ["Apply fungicide", "Monitor moisture levels"],
                },
                "response_time_ms": 234.5,
            }
        }


class RegistryClient:
    """
    Agent Registry Client
    عميل سجل الوكلاء

    Provides methods to:
    - Query the agent registry
    - Discover agents by capabilities
    - Invoke remote agents
    - Check agent health

    يوفر طرقًا لـ:
    - الاستعلام عن سجل الوكلاء
    - اكتشاف الوكلاء حسب القدرات
    - استدعاء الوكلاء عن بعد
    - فحص صحة الوكيل
    """

    def __init__(
        self,
        registry_url: str,
        api_key: Optional[str] = None,
        timeout_seconds: int = 30,
    ):
        """
        Initialize registry client
        تهيئة عميل السجل

        Args:
            registry_url: Base URL of the registry service
            api_key: Optional API key for authentication
            timeout_seconds: Default request timeout
        """
        self.registry_url = registry_url.rstrip("/")
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self._logger = logger.bind(component="registry_client")

        # Setup HTTP client
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        self._client = httpx.AsyncClient(
            base_url=self.registry_url,
            headers=headers,
            timeout=timeout_seconds,
        )

    async def close(self):
        """Close the HTTP client / إغلاق عميل HTTP"""
        await self._client.aclose()

    async def __aenter__(self):
        """Context manager entry / دخول مدير السياق"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit / خروج مدير السياق"""
        await self.close()

    async def get_agent(self, agent_id: str) -> Optional[AgentCard]:
        """
        Get agent card by ID
        الحصول على بطاقة الوكيل بواسطة المعرف

        Args:
            agent_id: Agent ID

        Returns:
            AgentCard if found, None otherwise
        """
        try:
            response = await self._client.get(f"/v1/registry/agents/{agent_id}")
            response.raise_for_status()

            data = response.json()
            return AgentCard.from_dict(data)

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            self._logger.error(
                "get_agent_failed",
                agent_id=agent_id,
                status_code=e.response.status_code,
            )
            raise
        except Exception as e:
            self._logger.error("get_agent_error", agent_id=agent_id, error=str(e))
            raise

    async def list_agents(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[AgentCard]:
        """
        List all agents with optional filters
        قائمة بجميع الوكلاء مع مرشحات اختيارية

        Args:
            status: Filter by status
            category: Filter by category

        Returns:
            List of agent cards
        """
        try:
            params = {}
            if status:
                params["status"] = status
            if category:
                params["category"] = category

            response = await self._client.get("/v1/registry/agents", params=params)
            response.raise_for_status()

            data = response.json()
            return [AgentCard.from_dict(agent) for agent in data.get("agents", [])]

        except Exception as e:
            self._logger.error("list_agents_error", error=str(e))
            raise

    async def discover_by_capability(self, capability_name: str) -> List[AgentCard]:
        """
        Discover agents by capability
        اكتشاف الوكلاء حسب القدرة

        Args:
            capability_name: Name of the capability

        Returns:
            List of agents with the specified capability
        """
        try:
            response = await self._client.get(
                "/v1/registry/discover/capability",
                params={"capability": capability_name},
            )
            response.raise_for_status()

            data = response.json()
            return [AgentCard.from_dict(agent) for agent in data.get("agents", [])]

        except Exception as e:
            self._logger.error(
                "discover_by_capability_error", capability=capability_name, error=str(e)
            )
            raise

    async def discover_by_skill(self, skill_id: str) -> List[AgentCard]:
        """
        Discover agents by skill
        اكتشاف الوكلاء حسب المهارة

        Args:
            skill_id: Skill identifier

        Returns:
            List of agents with the specified skill
        """
        try:
            response = await self._client.get(
                "/v1/registry/discover/skill", params={"skill": skill_id}
            )
            response.raise_for_status()

            data = response.json()
            return [AgentCard.from_dict(agent) for agent in data.get("agents", [])]

        except Exception as e:
            self._logger.error("discover_by_skill_error", skill=skill_id, error=str(e))
            raise

    async def discover_by_tags(self, tags: List[str]) -> List[AgentCard]:
        """
        Discover agents by tags
        اكتشاف الوكلاء حسب العلامات

        Args:
            tags: List of tags to search for

        Returns:
            List of matching agents
        """
        try:
            response = await self._client.post(
                "/v1/registry/discover/tags", json={"tags": tags}
            )
            response.raise_for_status()

            data = response.json()
            return [AgentCard.from_dict(agent) for agent in data.get("agents", [])]

        except Exception as e:
            self._logger.error("discover_by_tags_error", tags=tags, error=str(e))
            raise

    async def check_agent_health(self, agent_id: str) -> HealthCheckResult:
        """
        Check health of an agent
        فحص صحة وكيل

        Args:
            agent_id: Agent ID

        Returns:
            Health check result
        """
        try:
            response = await self._client.get(f"/v1/registry/agents/{agent_id}/health")
            response.raise_for_status()

            data = response.json()
            return HealthCheckResult(**data)

        except Exception as e:
            self._logger.error(
                "check_agent_health_error", agent_id=agent_id, error=str(e)
            )
            raise

    async def invoke_agent(
        self,
        agent_id: str,
        request: AgentInvocationRequest,
        auth_token: Optional[str] = None,
    ) -> AgentInvocationResponse:
        """
        Invoke an agent capability
        استدعاء قدرة وكيل

        Args:
            agent_id: Agent to invoke
            request: Invocation request
            auth_token: Optional authentication token for the agent

        Returns:
            Agent invocation response
        """
        start_time = datetime.utcnow()

        try:
            # Get agent card to get endpoint
            agent_card = await self.get_agent(agent_id)
            if not agent_card:
                raise ValueError(f"Agent not found: {agent_id}")

            # Verify capability exists
            capability_names = [c.name for c in agent_card.capabilities]
            if request.capability not in capability_names:
                raise ValueError(
                    f"Agent {agent_id} does not have capability: {request.capability}"
                )

            # Prepare headers
            headers = {"Content-Type": "application/json"}

            # Add authentication if required
            if agent_card.requires_authentication:
                if not auth_token and not self.api_key:
                    raise ValueError(
                        f"Agent {agent_id} requires authentication but no token provided"
                    )

                token = auth_token or self.api_key
                if agent_card.security_scheme == SecurityScheme.BEARER:
                    headers["Authorization"] = f"Bearer {token}"
                elif agent_card.security_scheme == SecurityScheme.API_KEY:
                    headers["X-API-Key"] = token

            # Add any custom headers from endpoint
            if agent_card.endpoint.headers:
                headers.update(agent_card.endpoint.headers)

            # Prepare request body
            body = {
                "capability": request.capability,
                "input": request.input_data,
                "context": request.context or {},
            }

            # Invoke agent
            async with httpx.AsyncClient(timeout=request.timeout_seconds) as client:
                if agent_card.endpoint.method == "POST":
                    response = await client.post(
                        str(agent_card.endpoint.url),
                        json=body,
                        headers=headers,
                    )
                else:
                    # For GET requests, encode as query params (less common)
                    response = await client.get(
                        str(agent_card.endpoint.url),
                        params=body,
                        headers=headers,
                    )

                response.raise_for_status()
                result_data = response.json()

            # Calculate response time
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return AgentInvocationResponse(
                status="success",
                agent_id=agent_id,
                capability=request.capability,
                output_data=result_data,
                response_time_ms=response_time,
            )

        except Exception as e:
            self._logger.error(
                "invoke_agent_error",
                agent_id=agent_id,
                capability=request.capability,
                error=str(e),
            )

            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return AgentInvocationResponse(
                status="error",
                agent_id=agent_id,
                capability=request.capability,
                error=str(e),
                response_time_ms=response_time,
            )

    async def get_registry_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics
        الحصول على إحصائيات السجل

        Returns:
            Registry statistics
        """
        try:
            response = await self._client.get("/v1/registry/stats")
            response.raise_for_status()
            return response.json()

        except Exception as e:
            self._logger.error("get_registry_stats_error", error=str(e))
            raise
