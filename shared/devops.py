"""
SAHOOL DevOps & Performance Layer v16.0.0
Deployment automation, load testing, and performance optimization
"""

import asyncio
import hashlib
import json
import logging
import os
import re
import statistics
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

import aiohttp
import asyncpg
import jwt
from kubernetes import client, config as k8s_config

from shared.platform import (
    TenantMetrics,
    TenantRedis,
    tenant_db,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: Deployment Automation
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class DeploymentConfig:
    """Configuration for service deployment"""

    service_name: str
    version: str
    replicas: int = 3
    cpu_request: str = "100m"
    cpu_limit: str = "500m"
    memory_request: str = "256Mi"
    memory_limit: str = "512Mi"
    env_vars: dict[str, str] = field(default_factory=dict)
    health_check_path: str = "/health"
    readiness_timeout: int = 30
    rolling_update_max_surge: str = "25%"
    rolling_update_max_unavailable: str = "0"


class KubernetesDeployer:
    """Automated Kubernetes deployment with tenant-aware configuration"""

    def __init__(self, namespace: str = "sahool"):
        try:
            k8s_config.load_incluster_config()
        except Exception:
            k8s_config.load_kube_config()

        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()
        self.namespace = namespace

    async def deploy_service(self, deploy_cfg: DeploymentConfig) -> dict[str, Any]:
        """Deploy service with automatic tenant isolation configuration."""
        deployment_name = f"{deploy_cfg.service_name}-{deploy_cfg.version.replace('.', '-')}"

        # Create deployment with tenant-aware labels
        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(
                name=deployment_name,
                labels={
                    "app": deploy_cfg.service_name,
                    "version": deploy_cfg.version,
                    "tenant-isolation": "enabled",
                    "managed-by": "sahool-platform",
                },
            ),
            spec=client.V1DeploymentSpec(
                replicas=deploy_cfg.replicas,
                selector={"matchLabels": {"app": deploy_cfg.service_name}},
                strategy=client.V1DeploymentStrategy(
                    type="RollingUpdate",
                    rolling_update=client.V1RollingUpdateDeployment(
                        max_surge=deploy_cfg.rolling_update_max_surge,
                        max_unavailable=deploy_cfg.rolling_update_max_unavailable,
                    ),
                ),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(
                        labels={
                            "app": deploy_cfg.service_name,
                            "version": deploy_cfg.version,
                        }
                    ),
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name=deploy_cfg.service_name,
                                image=f"sahool/{deploy_cfg.service_name}:{deploy_cfg.version}",
                                ports=[client.V1ContainerPort(container_port=8000)],
                                resources=client.V1ResourceRequirements(
                                    requests={
                                        "cpu": deploy_cfg.cpu_request,
                                        "memory": deploy_cfg.memory_request,
                                    },
                                    limits={
                                        "cpu": deploy_cfg.cpu_limit,
                                        "memory": deploy_cfg.memory_limit,
                                    },
                                ),
                                env=[
                                    client.V1EnvVar(name=k, value=v)
                                    for k, v in {
                                        **deploy_cfg.env_vars,
                                        "SAHOOL_TENANT_ISOLATION": "enabled",
                                        "SAHOOL_RLS_ENFORCED": "true",
                                        "SAHOOL_SERVICE_NAME": deploy_cfg.service_name,
                                    }.items()
                                ],
                                liveness_probe=client.V1Probe(
                                    http_get=client.V1HTTPGetAction(
                                        path=deploy_cfg.health_check_path,
                                        port=8000,
                                    ),
                                    initial_delay_seconds=10,
                                    period_seconds=10,
                                ),
                                readiness_probe=client.V1Probe(
                                    http_get=client.V1HTTPGetAction(
                                        path=deploy_cfg.health_check_path,
                                        port=8000,
                                    ),
                                    initial_delay_seconds=5,
                                    period_seconds=5,
                                    timeout_seconds=deploy_cfg.readiness_timeout,
                                ),
                            )
                        ],
                        # Ensure tenant isolation at pod level
                        security_context=client.V1PodSecurityContext(
                            run_as_non_root=True,
                            seccomp_profile=client.V1SeccompProfile(type="RuntimeDefault"),
                        ),
                    ),
                ),
            ),
        )

        try:
            # Check if deployment already exists
            self.apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=self.namespace,
            )
            # Rolling update
            self.apps_v1.replace_namespaced_deployment(
                name=deployment_name,
                namespace=self.namespace,
                body=deployment,
            )
            action = "updated"
        except client.exceptions.ApiException as e:
            if e.status == 404:
                self.apps_v1.create_namespaced_deployment(
                    namespace=self.namespace,
                    body=deployment,
                )
                action = "created"
            else:
                raise

        # Ensure service exists
        service = client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=client.V1ObjectMeta(
                name=deploy_cfg.service_name,
                labels={"app": deploy_cfg.service_name},
            ),
            spec=client.V1ServiceSpec(
                selector={"app": deploy_cfg.service_name},
                ports=[client.V1ServicePort(port=80, target_port=8000)],
            ),
        )

        try:
            self.core_v1.read_namespaced_service(
                name=deploy_cfg.service_name,
                namespace=self.namespace,
            )
        except client.exceptions.ApiException as e:
            if e.status == 404:
                self.core_v1.create_namespaced_service(
                    namespace=self.namespace,
                    body=service,
                )
            else:
                raise

        return {
            "service": deploy_cfg.service_name,
            "version": deploy_cfg.version,
            "action": action,
            "replicas": deploy_cfg.replicas,
            "deployment_name": deployment_name,
            "status": "deployed",
        }

    async def verify_tenant_isolation(self, service_name: str) -> dict[str, Any]:
        """Verify deployed service has tenant isolation enabled."""
        pods = self.core_v1.list_namespaced_pod(
            namespace=self.namespace,
            label_selector=f"app={service_name}",
        )

        results = []
        for pod in pods.items:
            env_vars = {e.name: e.value for e in pod.spec.containers[0].env}

            has_isolation = (
                env_vars.get("SAHOOL_TENANT_ISOLATION") == "enabled"
                and env_vars.get("SAHOOL_RLS_ENFORCED") == "true"
            )

            results.append({
                "pod": pod.metadata.name,
                "tenant_isolation_enabled": has_isolation,
                "env_check": {
                    "isolation": env_vars.get("SAHOOL_TENANT_ISOLATION"),
                    "rls": env_vars.get("SAHOOL_RLS_ENFORCED"),
                },
            })

        all_enabled = all(r["tenant_isolation_enabled"] for r in results)

        return {
            "service": service_name,
            "total_pods": len(results),
            "isolation_enabled_pods": sum(1 for r in results if r["tenant_isolation_enabled"]),
            "all_pods_compliant": all_enabled,
            "details": results,
        }

    async def rollback(self, service_name: str, previous_version: str) -> dict[str, Any]:
        """Rollback to previous version."""
        deployment_name = f"{service_name}-{previous_version.replace('.', '-')}"

        # Scale down current
        current_deployments = self.apps_v1.list_namespaced_deployment(
            namespace=self.namespace,
            label_selector=f"app={service_name}",
        )

        for dep in current_deployments.items:
            if previous_version.replace(".", "-") not in dep.metadata.name:
                dep.spec.replicas = 0
                self.apps_v1.replace_namespaced_deployment(
                    name=dep.metadata.name,
                    namespace=self.namespace,
                    body=dep,
                )

        # Scale up previous
        previous = self.apps_v1.read_namespaced_deployment(
            name=deployment_name,
            namespace=self.namespace,
        )
        previous.spec.replicas = 3

        self.apps_v1.replace_namespaced_deployment(
            name=deployment_name,
            namespace=self.namespace,
            body=previous,
        )

        return {
            "service": service_name,
            "rolled_back_to": previous_version,
            "status": "rollback_complete",
        }


class DatabaseMigrationRunner:
    """Run database migrations with tenant safety checks"""

    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def run_migration(self, migration_file: str) -> dict[str, Any]:
        """Run migration with automatic tenant isolation verification."""
        with open(migration_file) as f:
            sql = f.read()

        # Check for tenant safety
        safety_issues = self._check_tenant_safety(sql)

        if safety_issues:
            return {
                "status": "blocked",
                "migration": migration_file,
                "safety_issues": safety_issues,
                "message": "Migration blocked due to tenant safety concerns",
            }

        # Run migration
        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(sql)

                await conn.execute(
                    """
                    INSERT INTO schema_migrations (filename, applied_at, hash)
                    VALUES ($1, NOW(), $2)
                    """,
                    migration_file,
                    hashlib.sha256(sql.encode()).hexdigest()[:16],
                )

        return {
            "status": "success",
            "migration": migration_file,
            "safety_check": "passed",
            "applied_at": datetime.utcnow().isoformat(),
        }

    def _check_tenant_safety(self, sql: str) -> list[str]:
        """Check SQL for tenant safety issues."""
        issues = []

        if "CREATE TABLE" in sql.upper():
            if "tenant_id" not in sql.lower():
                issues.append("Table created without tenant_id column")

        if "CREATE TABLE" in sql.upper() and "ENABLE ROW LEVEL SECURITY" not in sql.upper():
            issues.append("Table created without RLS enabled")

        dangerous_patterns = [
            "DROP TABLE",
            "TRUNCATE TABLE",
            r"ALTER TABLE.*DROP COLUMN",
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, sql, re.IGNORECASE):
                issues.append(f"Dangerous operation detected: {pattern}")

        return issues


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2: Load Testing
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class LoadTestScenario:
    """Definition of a load test scenario"""

    name: str
    endpoint: str
    method: str = "GET"
    payload: dict | None = None
    headers: dict[str, str] = field(default_factory=dict)
    weight: int = 1
    expected_status: int = 200


@dataclass
class LoadTestResult:
    """Results from a load test run"""

    scenario_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float
    p50_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    requests_per_second: float
    errors: list[str] = field(default_factory=list)
    tenant_distribution: dict[str, int] = field(default_factory=dict)


class TenantAwareLoadTester:
    """Load testing with tenant isolation verification."""

    def __init__(self, base_url: str, max_concurrent: int = 100):
        self.base_url = base_url
        self.max_concurrent = max_concurrent
        self.results: list[LoadTestResult] = []
        self._session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()

    async def run_scenario(
        self,
        scenario: LoadTestScenario,
        tenants: list[str],
        duration_seconds: int = 60,
        requests_per_tenant: int = 100,
    ) -> LoadTestResult:
        """Run load test scenario across multiple tenants."""
        response_times: list[float] = []
        errors: list[str] = []
        tenant_counts: dict[str, int] = dict.fromkeys(tenants, 0)
        # Use a mutable container so the inner closure can modify these counters
        counters = {"successful": 0, "failed": 0}

        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def make_request(tenant_id: str):
            async with semaphore:
                token = self._generate_test_token(tenant_id)

                headers = {
                    **scenario.headers,
                    "Authorization": f"Bearer {token}",
                    "X-Test-Tenant": tenant_id,
                }

                start = time.time()

                try:
                    async with self._session.request(
                        method=scenario.method,
                        url=f"{self.base_url}{scenario.endpoint}",
                        headers=headers,
                        json=scenario.payload,
                        timeout=aiohttp.ClientTimeout(total=30),
                    ) as response:
                        elapsed = (time.time() - start) * 1000
                        response_times.append(elapsed)
                        tenant_counts[tenant_id] += 1

                        if response.status == scenario.expected_status:
                            counters["successful"] += 1

                            # Verify tenant isolation in response
                            try:
                                body = await response.json()
                                if "tenant_id" in body and body["tenant_id"] != tenant_id:
                                    errors.append(
                                        f"Tenant isolation breach: {tenant_id} "
                                        f"saw data from {body['tenant_id']}"
                                    )
                            except (json.JSONDecodeError, aiohttp.ContentTypeError):
                                pass  # Non-JSON response, skip isolation check
                        else:
                            counters["failed"] += 1
                            errors.append(
                                f"Unexpected status {response.status} for tenant {tenant_id}"
                            )

                except Exception as e:
                    counters["failed"] += 1
                    errors.append(f"Request failed for tenant {tenant_id}: {e}")

        # Generate all requests
        tasks = []
        for tenant in tenants:
            for _ in range(requests_per_tenant):
                tasks.append(make_request(tenant))

        # Run with progress tracking
        start_time = time.time()
        await asyncio.gather(*tasks, return_exceptions=True)
        total_duration = time.time() - start_time

        # Calculate statistics
        if response_times:
            sorted_times = sorted(response_times)
            n = len(sorted_times)

            result = LoadTestResult(
                scenario_name=scenario.name,
                total_requests=len(tasks),
                successful_requests=counters["successful"],
                failed_requests=counters["failed"],
                avg_response_time_ms=statistics.mean(response_times),
                p50_response_time_ms=sorted_times[n // 2],
                p95_response_time_ms=sorted_times[int(n * 0.95)],
                p99_response_time_ms=sorted_times[int(n * 0.99)],
                requests_per_second=len(response_times) / total_duration if total_duration > 0 else 0,
                errors=list(set(errors))[:10],
                tenant_distribution=tenant_counts,
            )
        else:
            result = LoadTestResult(
                scenario_name=scenario.name,
                total_requests=len(tasks),
                successful_requests=0,
                failed_requests=counters["failed"],
                avg_response_time_ms=0,
                p50_response_time_ms=0,
                p95_response_time_ms=0,
                p99_response_time_ms=0,
                requests_per_second=0,
                errors=errors,
                tenant_distribution=tenant_counts,
            )

        self.results.append(result)
        return result

    def _generate_test_token(self, tenant_id: str) -> str:
        """Generate test JWT for load testing (test environments only)."""
        secret = os.getenv("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
        payload = {
            "tid": tenant_id,
            "sub": f"test-user-{tenant_id[:8]}",
            "role": "user",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        return jwt.encode(payload, secret, algorithm="HS256")

    async def verify_tenant_isolation_under_load(self) -> dict[str, Any]:
        """Critical test: Verify no cross-tenant data leakage under high load."""
        test_tenants = [f"test-tenant-{i}" for i in range(10)]

        # Create data for each tenant
        for tenant in test_tenants:
            await self._create_test_data(tenant)

        # Run concurrent queries across all tenants
        isolation_breaches: list[dict[str, Any]] = []

        async def query_and_verify(tenant_id: str):
            token = self._generate_test_token(tenant_id)

            async with self._session.get(
                f"{self.base_url}/fields",
                headers={"Authorization": f"Bearer {token}"},
            ) as response:
                data = await response.json()

                for item in data:
                    if item.get("tenant_id") != tenant_id:
                        isolation_breaches.append({
                            "expected_tenant": tenant_id,
                            "actual_tenant": item.get("tenant_id"),
                            "item_id": item.get("id"),
                        })

        # High concurrency test
        await asyncio.gather(*[query_and_verify(t) for t in test_tenants])

        return {
            "test_tenants": len(test_tenants),
            "isolation_breaches": len(isolation_breaches),
            "breach_details": isolation_breaches[:5],
            "isolation_intact": len(isolation_breaches) == 0,
        }

    async def _create_test_data(self, tenant_id: str):
        """Create test data for load testing."""
        token = self._generate_test_token(tenant_id)

        for i in range(5):
            await self._session.post(
                f"{self.base_url}/fields",
                headers={"Authorization": f"Bearer {token}"},
                json={"name": f"Field {i}", "area": 100.0 + i},
            )


class K6Integration:
    """Integration with k6 for advanced load testing."""

    def __init__(self, base_url: str):
        self.base_url = base_url

    def generate_k6_script(self, scenarios: list[LoadTestScenario], tenants: list[str]) -> str:
        """Generate k6 JavaScript script for load testing."""
        script = f"""
import http from 'k6/http';
import {{ check, sleep }} from 'k6';

// Test configuration
export const options = {{
    stages: [
        {{ duration: '2m', target: 100 }},  // Ramp up
        {{ duration: '5m', target: 100 }},  // Steady state
        {{ duration: '2m', target: 200 }},  // Spike
        {{ duration: '2m', target: 0 }},    // Ramp down
    ],
    thresholds: {{
        http_req_duration: ['p(95)<500'],  // 95% under 500ms
        http_req_failed: ['rate<0.01'],     // Error rate under 1%
    }},
}};

// Test tenants
const tenants = {json.dumps(tenants)};

// Generate JWT for tenant
function generateToken(tenantId) {{
    // Simplified — use proper JWT in production
    return `test-token-${{tenantId}}`;
}}

export default function() {{
    const tenant = tenants[Math.floor(Math.random() * tenants.length)];
    const token = generateToken(tenant);

    const params = {{
        headers: {{
            'Authorization': `Bearer ${{token}}`,
            'X-Tenant-ID': tenant,
            'Content-Type': 'application/json',
        }},
    }};

    // Test scenarios
"""

        for scenario in scenarios:
            payload_js = json.dumps(scenario.payload) if scenario.payload else "null"
            script += f"""
    // {scenario.name}
    {{
        const response = http.{scenario.method.lower()}(
            '{self.base_url}{scenario.endpoint}',
            {payload_js},
            params
        );

        check(response, {{
            '{scenario.name} status is {scenario.expected_status}': (r) => r.status === {scenario.expected_status},
            '{scenario.name} response time < 500ms': (r) => r.timings.duration < 500,
            '{scenario.name} tenant isolation': (r) => {{
                try {{
                    const body = JSON.parse(r.body);
                    return !body.tenant_id || body.tenant_id === tenant;
                }} catch(e) {{ return true; }}
            }},
        }});
    }}
"""

        script += """
    sleep(1);
}
"""
        return script

    async def run_k6_test(self, script: str, output_file: str = "k6-results.json") -> dict[str, Any]:
        """Execute k6 test and parse results."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
            f.write(script)
            script_file = f.name

        try:
            result = subprocess.run(
                ["k6", "run", "--out", f"json={output_file}", script_file],
                capture_output=True,
                text=True,
                check=False,
            )

            try:
                with open(output_file) as f:
                    results = [json.loads(line) for line in f if line.strip()]
            except FileNotFoundError:
                return {"status": "failed", "error": "k6 output file not found"}

            # Calculate metrics
            http_reqs = [
                r
                for r in results
                if r.get("type") == "Point" and "http_req_duration" in r.get("metric", "")
            ]

            if http_reqs:
                durations = [r["data"]["value"] for r in http_reqs]
                return {
                    "status": "completed",
                    "total_requests": len(http_reqs),
                    "avg_duration_ms": statistics.mean(durations),
                    "p95_duration_ms": sorted(durations)[int(len(durations) * 0.95)],
                    "errors": result.stderr if result.returncode != 0 else None,
                }

            return {"status": "failed", "error": "No metrics collected"}
        finally:
            os.unlink(script_file)


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3: Performance Tuning
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class PerformanceMetrics:
    """Collected performance metrics"""

    timestamp: datetime
    tenant_id: str
    service_name: str
    endpoint: str
    response_time_ms: float
    db_query_time_ms: float
    cache_hit: bool
    cache_time_ms: float | None
    serialization_time_ms: float
    memory_usage_mb: float


class PerformanceAnalyzer:
    """Analyze and optimize performance per tenant."""

    def __init__(self, tenant_redis: TenantRedis, metrics: TenantMetrics):
        self.redis = tenant_redis
        self.metrics = metrics
        self._slow_query_threshold_ms = 100
        self._cache_hit_threshold = 0.8

    async def analyze_endpoint_performance(
        self,
        endpoint: str,
        time_range_hours: int = 24,
    ) -> dict[str, Any]:
        """Analyze performance patterns for an endpoint."""
        async with tenant_db() as conn:
            stats = await conn.fetch(
                """
                SELECT
                    tenant_id,
                    COUNT(*) AS request_count,
                    AVG(duration_ms) AS avg_duration,
                    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration_ms) AS p95,
                    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY duration_ms) AS p99,
                    MAX(duration_ms) AS max_duration
                FROM request_metrics
                WHERE endpoint = $1
                AND recorded_at > NOW() - make_interval(hours => $2)
                GROUP BY tenant_id
                """,
                endpoint,
                time_range_hours,
            )

        analysis: dict[str, Any] = {
            "endpoint": endpoint,
            "time_range_hours": time_range_hours,
            "tenant_breakdown": [],
            "recommendations": [],
        }

        for row in stats:
            tenant_analysis = {
                "tenant_id": row["tenant_id"][:8],
                "request_count": row["request_count"],
                "avg_duration_ms": round(row["avg_duration"], 2),
                "p95_duration_ms": round(row["p95"], 2),
                "p99_duration_ms": round(row["p99"], 2),
                "max_duration_ms": round(row["max_duration"], 2),
                "performance_grade": self._grade_performance(row["avg_duration"]),
            }

            analysis["tenant_breakdown"].append(tenant_analysis)

            if row["avg_duration"] > self._slow_query_threshold_ms:
                analysis["recommendations"].append({
                    "tenant": row["tenant_id"][:8],
                    "issue": "Slow average response time",
                    "suggestion": "Consider adding database index or cache layer",
                    "priority": "high" if row["avg_duration"] > 500 else "medium",
                })

        return analysis

    def _grade_performance(self, avg_duration_ms: float) -> str:
        """Grade performance based on response time."""
        if avg_duration_ms < 50:
            return "A+"
        elif avg_duration_ms < 100:
            return "A"
        elif avg_duration_ms < 200:
            return "B"
        elif avg_duration_ms < 500:
            return "C"
        return "D"

    async def optimize_cache_strategy(self, tenant_id: str) -> dict[str, Any]:
        """Analyze and optimize cache strategy for a tenant."""
        cache_hits = await self.redis.get("metrics", f"cache_hits:{tenant_id}")
        cache_misses = await self.redis.get("metrics", f"cache_misses:{tenant_id}")

        total = (cache_hits or 0) + (cache_misses or 0)
        hit_rate = (cache_hits or 0) / total if total > 0 else 0

        recommendations = []

        if hit_rate < self._cache_hit_threshold:
            recommendations.append({
                "issue": f"Low cache hit rate: {hit_rate:.1%}",
                "suggestions": [
                    "Increase cache TTL for stable data",
                    "Implement cache warming for hot data",
                    "Review cache key patterns for efficiency",
                ],
            })

        keys = await self.redis.scan("cache", "*")

        return {
            "tenant_id": tenant_id[:8],
            "cache_hit_rate": hit_rate,
            "total_cache_keys": len(keys),
            "recommendations": recommendations,
        }

    async def generate_optimization_report(self) -> dict[str, Any]:
        """Generate comprehensive optimization report."""
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "database_optimizations": await self._analyze_database(),
            "cache_optimizations": await self._analyze_cache(),
            "query_optimizations": await self._analyze_slow_queries(),
            "resource_scaling": await self._analyze_resource_usage(),
        }

    async def _analyze_database(self) -> list[dict]:
        """Analyze database performance."""
        async with tenant_db() as conn:
            missing_indexes = await conn.fetch("""
                SELECT
                    schemaname,
                    tablename,
                    attname AS column_name,
                    n_tup_read,
                    n_tup_fetch
                FROM pg_stats
                WHERE schemaname = 'public'
                AND n_tup_read > 10000
                AND NOT EXISTS (
                    SELECT 1 FROM pg_indexes
                    WHERE tablename = pg_stats.tablename
                    AND indexdef LIKE '%' || attname || '%'
                )
            """)

            return [
                {
                    "table": row["tablename"],
                    "column": row["column_name"],
                    "reads": row["n_tup_read"],
                    "recommendation": f"Consider index on {row['tablename']}({row['column_name']})",
                }
                for row in missing_indexes
            ]

    async def _analyze_cache(self) -> list[dict]:
        """Analyze cache efficiency."""
        return []

    async def _analyze_slow_queries(self) -> list[dict]:
        """Identify and analyze slow queries."""
        async with tenant_db() as conn:
            slow_queries = await conn.fetch("""
                SELECT
                    query,
                    calls,
                    total_time,
                    mean_time,
                    rows
                FROM pg_stat_statements
                WHERE mean_time > 100
                ORDER BY mean_time DESC
                LIMIT 10
            """)

            return [
                {
                    "query": row["query"][:100],
                    "calls": row["calls"],
                    "avg_time_ms": round(row["mean_time"], 2),
                    "total_time_ms": round(row["total_time"], 2),
                }
                for row in slow_queries
            ]

    async def _analyze_resource_usage(self) -> dict[str, Any]:
        """Analyze resource usage patterns."""
        return {
            "cpu_recommendations": "Implement HPA based on tenant load",
            "memory_recommendations": "Review memory limits per service",
            "scaling_strategy": "Consider tenant-based sharding for high-load tenants",
        }


class AutoScaler:
    """Automatic scaling based on tenant load."""

    def __init__(self, k8s_deployer: KubernetesDeployer):
        self.k8s = k8s_deployer

    async def evaluate_scaling_needs(self) -> dict[str, Any]:
        """Evaluate if scaling is needed based on metrics."""
        metrics = await self._get_cluster_metrics()

        scaling_decisions = []

        for service, metric in metrics.items():
            current_replicas = metric["replicas"]
            cpu_util = metric["cpu_utilization"]
            request_rate = metric["requests_per_second"]

            # Scale up if CPU > 70% or requests > 1000/s per pod
            if cpu_util > 70 or request_rate > 1000:
                desired = min(current_replicas + 2, 20)
                if desired > current_replicas:
                    scaling_decisions.append({
                        "service": service,
                        "action": "scale_up",
                        "from": current_replicas,
                        "to": desired,
                        "reason": f"CPU {cpu_util}%, RPS {request_rate}",
                    })

            # Scale down if CPU < 30% and replicas > 3
            elif cpu_util < 30 and current_replicas > 3:
                desired = max(current_replicas - 1, 3)
                scaling_decisions.append({
                    "service": service,
                    "action": "scale_down",
                    "from": current_replicas,
                    "to": desired,
                    "reason": f"Low CPU utilization {cpu_util}%",
                })

        return {
            "evaluated_at": datetime.utcnow().isoformat(),
            "decisions": scaling_decisions,
            "total_services_evaluated": len(metrics),
        }

    async def apply_scaling(self, decisions: list[dict]) -> dict[str, Any]:
        """Apply scaling decisions."""
        applied = []

        for decision in decisions:
            try:
                self.k8s.apps_v1.patch_namespaced_deployment_scale(
                    name=decision["service"],
                    namespace=self.k8s.namespace,
                    body={"spec": {"replicas": decision["to"]}},
                )

                applied.append({
                    "service": decision["service"],
                    "action": decision["action"],
                    "new_replicas": decision["to"],
                    "status": "applied",
                })
            except Exception as e:
                logger.error("Failed to scale %s: %s", decision["service"], e)
                applied.append({
                    "service": decision["service"],
                    "action": decision["action"],
                    "status": "failed",
                    "error": str(e),
                })

        return {"applied": applied}

    async def _get_cluster_metrics(self) -> dict[str, dict]:
        """Get current cluster metrics (via metrics-server or Prometheus)."""
        return {}


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Deployment
    "DeploymentConfig",
    "KubernetesDeployer",
    "DatabaseMigrationRunner",
    # Load Testing
    "LoadTestScenario",
    "LoadTestResult",
    "TenantAwareLoadTester",
    "K6Integration",
    # Performance
    "PerformanceMetrics",
    "PerformanceAnalyzer",
    "AutoScaler",
]
