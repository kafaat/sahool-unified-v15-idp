# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Agent Executor for LLM Orchestrator Service.

This module handles parallel execution of agent calls,
timeouts, retries, and result aggregation.

منفذ الوكلاء لخدمة تنسيق نماذج اللغة الكبيرة.
تتعامل هذه الوحدة مع التنفيذ المتوازي لاستدعاءات الوكلاء،
والمهل، وإعادة المحاولات، وتجميع النتائج.
"""

import asyncio
import hashlib
import json
import time
from typing import Any

import httpx
import structlog

from ..api.schemas import AgentCall, AgentResult, ExecutionMode, ExecutionPlan
from ..core.config import settings

logger = structlog.get_logger(__name__)


class AgentExecutor:
    """
    Executor for calling AI agents in parallel or sequentially.
    منفذ لاستدعاء وكلاء الذكاء الاصطناعي بشكل متوازٍ أو متسلسل.
    """

    def __init__(
        self,
        redis_client: Any | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        """
        Initialize the agent executor.

        Args:
            redis_client: Optional Redis client for caching
            http_client: Optional HTTP client (created if not provided)
        """
        self._redis = redis_client
        self._http_client = http_client
        self._owned_client = False

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(settings.agent_timeout),
                follow_redirects=True,
            )
            self._owned_client = True
        return self._http_client

    async def close(self) -> None:
        """Close the HTTP client if owned."""
        if self._owned_client and self._http_client:
            await self._http_client.aclose()
            self._http_client = None
            self._owned_client = False

    def _get_cache_key(self, agent_call: AgentCall) -> str:
        """Generate a cache key for an agent call, scoped by tenant_id for isolation."""
        tenant_id = (agent_call.params or {}).get("tenant_id", "unknown")
        data = json.dumps(
            {
                "tenant_id": tenant_id,
                "agent": agent_call.agent_name,
                "endpoint": agent_call.endpoint,
                "params": agent_call.params,
            },
            sort_keys=True,
        )
        return f"llm-orchestrator:cache:{tenant_id}:{hashlib.sha256(data.encode()).hexdigest()[:32]}"

    async def _get_cached_result(self, cache_key: str) -> dict[str, Any] | None:
        """Get cached result if available."""
        if not self._redis:
            return None

        try:
            cached = await self._redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning("cache_get_failed", error=str(e))

        return None

    async def _set_cached_result(self, cache_key: str, result: dict[str, Any], ttl: int | None = None) -> None:
        """Cache a result."""
        if not self._redis:
            return

        try:
            await self._redis.set(
                cache_key,
                json.dumps(result),
                ex=ttl or settings.redis_cache_ttl,
            )
        except Exception as e:
            logger.warning("cache_set_failed", error=str(e))

    async def _call_agent(
        self,
        agent_call: AgentCall,
        use_cache: bool = True,
    ) -> AgentResult:
        """
        Call a single agent with retry logic.
        استدعاء وكيل واحد مع منطق إعادة المحاولة.
        """
        start_time = time.time()
        cache_key = self._get_cache_key(agent_call)

        # Check cache first
        if use_cache:
            cached_result = await self._get_cached_result(cache_key)
            if cached_result:
                latency_ms = int((time.time() - start_time) * 1000)
                logger.info(
                    "agent_cache_hit",
                    agent=agent_call.agent_name,
                    latency_ms=latency_ms,
                )
                return AgentResult(
                    agent_name=agent_call.agent_name,
                    success=True,
                    result=cached_result,
                    latency_ms=latency_ms,
                    cached=True,
                )

        # Make HTTP request with retries
        last_error: str | None = None
        http_client = await self._get_http_client()

        for attempt in range(settings.agent_max_retries):
            try:
                if agent_call.method == "GET":
                    response = await http_client.get(
                        agent_call.endpoint,
                        params=agent_call.params,
                        headers=agent_call.headers,
                        timeout=agent_call.timeout,
                    )
                elif agent_call.method == "POST":
                    response = await http_client.post(
                        agent_call.endpoint,
                        json=agent_call.params,
                        headers=agent_call.headers,
                        timeout=agent_call.timeout,
                    )
                elif agent_call.method == "PUT":
                    response = await http_client.put(
                        agent_call.endpoint,
                        json=agent_call.params,
                        headers=agent_call.headers,
                        timeout=agent_call.timeout,
                    )
                else:
                    response = await http_client.delete(
                        agent_call.endpoint,
                        headers=agent_call.headers,
                        timeout=agent_call.timeout,
                    )

                latency_ms = int((time.time() - start_time) * 1000)

                if response.status_code >= 200 and response.status_code < 300:
                    result_data = response.json()

                    # Cache successful result
                    if use_cache:
                        await self._set_cached_result(cache_key, result_data)

                    logger.info(
                        "agent_call_success",
                        agent=agent_call.agent_name,
                        status=response.status_code,
                        latency_ms=latency_ms,
                        attempt=attempt + 1,
                    )

                    return AgentResult(
                        agent_name=agent_call.agent_name,
                        success=True,
                        result=result_data,
                        latency_ms=latency_ms,
                        cached=False,
                        metadata={"status_code": response.status_code},
                    )
                else:
                    last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                    logger.warning(
                        "agent_call_failed",
                        agent=agent_call.agent_name,
                        status=response.status_code,
                        attempt=attempt + 1,
                    )

            except httpx.TimeoutException:
                last_error = f"Timeout after {agent_call.timeout}s"
                logger.warning(
                    "agent_call_timeout",
                    agent=agent_call.agent_name,
                    timeout=agent_call.timeout,
                    attempt=attempt + 1,
                )

            except httpx.ConnectError as e:
                last_error = f"Connection error: {str(e)}"
                logger.warning(
                    "agent_call_connect_error",
                    agent=agent_call.agent_name,
                    error=str(e),
                    attempt=attempt + 1,
                )

            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                logger.error(
                    "agent_call_error",
                    agent=agent_call.agent_name,
                    error=str(e),
                    attempt=attempt + 1,
                )

            # Wait before retry (exponential backoff)
            if attempt < settings.agent_max_retries - 1:
                await asyncio.sleep(2**attempt * 0.5)

        # All retries failed
        latency_ms = int((time.time() - start_time) * 1000)
        return AgentResult(
            agent_name=agent_call.agent_name,
            success=False,
            error=last_error,
            latency_ms=latency_ms,
            cached=False,
        )

    async def execute_plan(
        self,
        plan: ExecutionPlan,
        use_cache: bool = True,
    ) -> list[AgentResult]:
        """
        Execute an execution plan.
        تنفيذ خطة التنفيذ.

        Args:
            plan: The execution plan to run
            use_cache: Whether to use caching

        Returns:
            List of agent results
        """
        if plan.execution_mode == ExecutionMode.PARALLEL:
            return await self._execute_parallel(plan.agents, use_cache)
        elif plan.execution_mode == ExecutionMode.SEQUENTIAL:
            return await self._execute_sequential(plan.agents, use_cache)
        else:
            # Conditional execution - handle dependencies
            return await self._execute_conditional(plan.agents, use_cache)

    async def _execute_parallel(
        self,
        agent_calls: list[AgentCall],
        use_cache: bool = True,
    ) -> list[AgentResult]:
        """
        Execute agent calls in parallel with concurrency limit.
        تنفيذ استدعاءات الوكلاء بالتوازي مع حد التزامن.
        """
        semaphore = asyncio.Semaphore(settings.agent_parallel_limit)

        async def limited_call(agent_call: AgentCall) -> AgentResult:
            async with semaphore:
                return await self._call_agent(agent_call, use_cache)

        tasks = [limited_call(call) for call in agent_calls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to failed results
        processed_results: list[AgentResult] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    AgentResult(
                        agent_name=agent_calls[i].agent_name,
                        success=False,
                        error=str(result),
                        latency_ms=0,
                    )
                )
            else:
                processed_results.append(result)

        return processed_results

    async def _execute_sequential(
        self,
        agent_calls: list[AgentCall],
        use_cache: bool = True,
    ) -> list[AgentResult]:
        """
        Execute agent calls sequentially.
        تنفيذ استدعاءات الوكلاء بشكل متسلسل.
        """
        results: list[AgentResult] = []

        for agent_call in agent_calls:
            result = await self._call_agent(agent_call, use_cache)
            results.append(result)

            # Stop if a required agent fails
            if not result.success and agent_call.required:
                logger.warning(
                    "sequential_execution_stopped",
                    failed_agent=agent_call.agent_name,
                    remaining=len(agent_calls) - len(results),
                )
                break

        return results

    async def _execute_conditional(
        self,
        agent_calls: list[AgentCall],
        use_cache: bool = True,
    ) -> list[AgentResult]:
        """
        Execute agent calls conditionally based on previous results.
        تنفيذ استدعاءات الوكلاء بشكل شرطي بناءً على النتائج السابقة.
        """
        results: list[AgentResult] = []
        previous_results: dict[str, AgentResult] = {}

        # Sort by priority
        sorted_calls = sorted(agent_calls, key=lambda x: x.priority)

        for agent_call in sorted_calls:
            # Check if we should skip based on previous results
            should_skip = False

            # Example: Skip yield prediction if crop intelligence failed
            if agent_call.agent_name == "yield-engine":
                crop_result = previous_results.get("crop-intelligence")
                if crop_result and not crop_result.success:
                    should_skip = True
                    logger.info(
                        "conditional_skip",
                        skipped_agent=agent_call.agent_name,
                        reason="dependency failed",
                    )

            if should_skip:
                results.append(
                    AgentResult(
                        agent_name=agent_call.agent_name,
                        success=False,
                        error="Skipped due to dependency failure",
                        latency_ms=0,
                        metadata={"skipped": True},
                    )
                )
                continue

            result = await self._call_agent(agent_call, use_cache)
            results.append(result)
            previous_results[agent_call.agent_name] = result

        return results

    async def call_single_agent(
        self,
        agent_call: AgentCall,
        use_cache: bool = True,
    ) -> AgentResult:
        """
        Call a single agent directly.
        استدعاء وكيل واحد مباشرة.
        """
        return await self._call_agent(agent_call, use_cache)

    async def health_check(self, agent_name: str, base_url: str) -> dict[str, Any]:
        """
        Check health of a specific agent.
        فحص صحة وكيل محدد.
        """
        start_time = time.time()
        http_client = await self._get_http_client()

        try:
            response = await http_client.get(
                f"{base_url}/healthz",
                timeout=5.0,
            )
            latency_ms = int((time.time() - start_time) * 1000)

            return {
                "agent": agent_name,
                "healthy": response.status_code == 200,
                "status_code": response.status_code,
                "latency_ms": latency_ms,
                "response": response.json() if response.status_code == 200 else None,
            }

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            return {
                "agent": agent_name,
                "healthy": False,
                "error": str(e),
                "latency_ms": latency_ms,
            }

    async def health_check_all(self, agents: list[tuple[str, str]]) -> list[dict[str, Any]]:
        """
        Check health of all agents in parallel.
        فحص صحة جميع الوكلاء بالتوازي.

        Args:
            agents: List of (name, base_url) tuples
        """
        tasks = [self.health_check(name, url) for name, url in agents]
        return await asyncio.gather(*tasks)
