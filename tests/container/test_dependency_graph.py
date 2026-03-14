"""
SAHOOL Container Dependency Graph Tests
========================================
اختبارات رسم بياني لتبعيات حاويات سهول

Validates the dependency graph of all Docker containers defined in
docker-compose.yml. Tests ensure acyclic ordering, correct startup
sequencing, completeness, proper health-check conditions, bounded depth,
and infrastructure isolation.

Coverage:
1. Acyclic graph            - No circular dependency chains
2. Dependency ordering      - Infra before app, correct env-based deps
3. Completeness             - All referenced services exist, no deprecated deps
4. Health-check conditions  - depends_on uses service_healthy
5. Depth limits             - No chain deeper than 5 levels
6. Infrastructure isolation - Infra never depends on application services

Run:
    pytest tests/container/test_dependency_graph.py -v --tb=short
    pytest tests/container/test_dependency_graph.py -v -n auto   # parallel
"""

from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.container.service_registry import (
    ALL_BUILT_SERVICES,
    ALL_HTTP_SERVICES,
    INFRA_SERVICES,
    NODE_SERVICES,
    PORTLESS_SERVICES,
    PYTHON_SERVICES,
)

pytestmark = [pytest.mark.container, pytest.mark.smoke]

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
MAIN_COMPOSE = REPO_ROOT / "docker-compose.yml"

# ---------------------------------------------------------------------------
# Deprecated services that must not appear as dependencies
# الخدمات المهملة التي لا يجب أن تظهر كتبعيات
# ---------------------------------------------------------------------------

DEPRECATED_SERVICES: set[str] = {
    "satellite-service",
    "weather-advanced",
    "crop-health-ai",
    "crop-health",
    "fertilizer-advisor",
    "field-ops",
    "field-core",
    "field-service",
    "agro-advisor",
    "ndvi-engine",
    "weather-core",
    "community-chat",
    "field-chat",
    "yield-engine",
}

# Core infrastructure services that application services commonly depend on
# خدمات البنية التحتية الأساسية
CORE_INFRA: set[str] = {"postgres", "pgbouncer", "redis", "nats"}

# Maximum allowed dependency chain depth
# أقصى عمق مسموح به لسلسلة التبعيات
MAX_DEPENDENCY_DEPTH = 5


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def compose_data() -> dict[str, Any]:
    """Load and return the parsed docker-compose.yml.
    # تحميل وتحليل ملف docker-compose.yml
    """
    assert MAIN_COMPOSE.exists(), f"docker-compose.yml not found at {MAIN_COMPOSE}"
    with MAIN_COMPOSE.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@pytest.fixture(scope="module")
def compose_services(compose_data: dict[str, Any]) -> dict[str, Any]:
    """Return the services dict from docker-compose.yml.
    # إرجاع قاموس الخدمات من docker-compose.yml
    """
    services = compose_data.get("services", {})
    assert services, "No services found in docker-compose.yml"
    return services


@pytest.fixture(scope="module")
def dependency_graph(compose_services: dict[str, Any]) -> dict[str, list[str]]:
    """Build a directed adjacency list: service -> [dependencies].
    # بناء قائمة جوار موجهة: خدمة -> [تبعيات]
    """
    graph: dict[str, list[str]] = {}
    for svc_name, svc_def in compose_services.items():
        deps: list[str] = []
        depends_on = svc_def.get("depends_on")
        if depends_on is None:
            graph[svc_name] = []
        elif isinstance(depends_on, list):
            # Bare list format: depends_on: [postgres, redis]
            deps = list(depends_on)
            graph[svc_name] = deps
        elif isinstance(depends_on, dict):
            # Dict format: depends_on: {postgres: {condition: service_healthy}}
            deps = list(depends_on.keys())
            graph[svc_name] = deps
        else:
            graph[svc_name] = []
    return graph


@pytest.fixture(scope="module")
def application_services(compose_services: dict[str, Any]) -> set[str]:
    """Return the set of application service names (non-infrastructure).
    # إرجاع مجموعة أسماء خدمات التطبيق (غير البنية التحتية)
    """
    return {
        name
        for name in compose_services
        if name not in INFRA_SERVICES
    }


@pytest.fixture(scope="module")
def infra_services_in_compose(compose_services: dict[str, Any]) -> set[str]:
    """Return infrastructure services that are defined in docker-compose.yml.
    # إرجاع خدمات البنية التحتية المعرّفة في docker-compose.yml
    """
    return {name for name in compose_services if name in INFRA_SERVICES}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _find_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    """Detect all cycles in the directed graph using iterative DFS.
    # كشف جميع الحلقات في الرسم البياني الموجه باستخدام بحث العمق أولاً

    Returns a list of cycles, where each cycle is a list of service names.
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {node: WHITE for node in graph}
    parent: dict[str, str | None] = {node: None for node in graph}
    cycles: list[list[str]] = []

    for start in graph:
        if color[start] != WHITE:
            continue
        stack: list[tuple[str, int]] = [(start, 0)]
        color[start] = GRAY

        while stack:
            node, idx = stack[-1]
            neighbors = graph.get(node, [])
            if idx < len(neighbors):
                stack[-1] = (node, idx + 1)
                neighbor = neighbors[idx]
                if neighbor not in color:
                    # Neighbor not in graph keys; skip
                    continue
                if color[neighbor] == GRAY:
                    # Found a cycle - reconstruct it
                    cycle = [neighbor]
                    for sn, _ in reversed(stack):
                        cycle.append(sn)
                        if sn == neighbor:
                            break
                    cycle.reverse()
                    cycles.append(cycle)
                elif color[neighbor] == WHITE:
                    color[neighbor] = GRAY
                    parent[neighbor] = node
                    stack.append((neighbor, 0))
            else:
                color[node] = BLACK
                stack.pop()

    return cycles


def _compute_depth(
    service: str,
    graph: dict[str, list[str]],
    memo: dict[str, int],
) -> int:
    """Compute the maximum dependency chain depth for a service (memoized).
    # حساب أقصى عمق لسلسلة التبعيات لخدمة معينة (مع الحفظ)

    Depth 0 means no dependencies. Depth 1 means depends on leaf services, etc.
    """
    if service in memo:
        return memo[service]
    # Guard against cycles by temporarily marking as visited
    memo[service] = 0
    deps = graph.get(service, [])
    if not deps:
        memo[service] = 0
        return 0
    max_child = max(
        _compute_depth(dep, graph, memo) for dep in deps if dep in graph
    )
    depth = 1 + max_child
    memo[service] = depth
    return depth


def _get_env_vars(svc_def: dict[str, Any]) -> set[str]:
    """Extract environment variable names from a service definition.
    # استخراج أسماء متغيرات البيئة من تعريف الخدمة
    """
    env = svc_def.get("environment")
    if env is None:
        return set()
    if isinstance(env, list):
        # Format: ["KEY=value", "KEY2=value2"]
        return {item.split("=", 1)[0] for item in env if "=" in item}
    if isinstance(env, dict):
        return set(env.keys())
    return set()


def _get_env_values(svc_def: dict[str, Any]) -> dict[str, str]:
    """Extract environment variables as key-value pairs from a service definition.
    # استخراج متغيرات البيئة كأزواج مفتاح-قيمة من تعريف الخدمة
    """
    env = svc_def.get("environment")
    if env is None:
        return {}
    if isinstance(env, list):
        result = {}
        for item in env:
            if "=" in item:
                k, v = item.split("=", 1)
                result[k] = v
        return result
    if isinstance(env, dict):
        return {k: str(v) if v is not None else "" for k, v in env.items()}
    return {}


# ===========================================================================
# Test Class 1: Acyclic Graph Validation
# فئة الاختبار 1: التحقق من الرسم البياني اللاحلقي
# ===========================================================================


class TestDependencyGraphAcyclic:
    """Verify the dependency graph contains no circular dependencies.
    # التحقق من أن رسم التبعيات لا يحتوي على تبعيات دائرية
    """

    def test_no_circular_dependencies(
        self,
        dependency_graph: dict[str, list[str]],
    ) -> None:
        """The dependency graph must be a DAG (no cycles).
        # يجب أن يكون رسم التبعيات رسمًا بيانيًا موجهًا بدون حلقات
        """
        cycles = _find_cycles(dependency_graph)
        if cycles:
            formatted = []
            for cycle in cycles:
                formatted.append(" -> ".join(cycle))
            msg = (
                f"Circular dependencies detected ({len(cycles)} cycle(s)):\n"
                + "\n".join(f"  - {c}" for c in formatted)
            )
            pytest.fail(msg)

    def test_topological_sort_possible(
        self,
        dependency_graph: dict[str, list[str]],
    ) -> None:
        """A valid topological ordering must exist (Kahn's algorithm).
        # يجب أن يوجد ترتيب طوبولوجي صالح (خوارزمية كان)
        """
        # Build in-degree map
        in_degree: dict[str, int] = defaultdict(int)
        all_nodes: set[str] = set(dependency_graph.keys())
        for deps in dependency_graph.values():
            for dep in deps:
                if dep in all_nodes:
                    in_degree[dep] += 0  # ensure key exists
        for node in all_nodes:
            in_degree.setdefault(node, 0)
        for node, deps in dependency_graph.items():
            for dep in deps:
                if dep in all_nodes:
                    in_degree[dep] += 1

        # Kahn's: note direction is reversed (edge from service TO dependency)
        # We need: for each service, it depends_on deps.
        # Topological order: deps come before the service.
        # In-degree: count how many services list this node as a dependency.
        # Actually we want reverse: edges go FROM dependency TO dependent.
        reverse_in_degree: dict[str, int] = {node: 0 for node in all_nodes}
        for node, deps in dependency_graph.items():
            # node depends on deps, so node has in_degree = len(deps)
            for dep in deps:
                if dep in all_nodes:
                    reverse_in_degree[node] = reverse_in_degree.get(node, 0)

        # Simpler: just count deps as in-degree for each node
        node_in_degree: dict[str, int] = {node: 0 for node in all_nodes}
        for node, deps in dependency_graph.items():
            for dep in deps:
                if dep in all_nodes:
                    node_in_degree[node] += 1

        # BFS from nodes with 0 in-degree (no dependencies)
        # Actually, standard topo: edge u->v means u must come before v.
        # Here: if service A depends_on B, then B must start before A.
        # Edge: B -> A. In-degree of A = number of its dependencies.
        queue: deque[str] = deque()
        in_deg: dict[str, int] = {node: 0 for node in all_nodes}
        adj: dict[str, list[str]] = {node: [] for node in all_nodes}

        for node, deps in dependency_graph.items():
            count = 0
            for dep in deps:
                if dep in all_nodes:
                    adj[dep].append(node)
                    count += 1
            in_deg[node] = count

        for node, deg in in_deg.items():
            if deg == 0:
                queue.append(node)

        sorted_count = 0
        while queue:
            current = queue.popleft()
            sorted_count += 1
            for neighbor in adj[current]:
                in_deg[neighbor] -= 1
                if in_deg[neighbor] == 0:
                    queue.append(neighbor)

        assert sorted_count == len(all_nodes), (
            f"Topological sort processed {sorted_count}/{len(all_nodes)} nodes. "
            f"Remaining nodes are part of a cycle."
        )


# ===========================================================================
# Test Class 2: Dependency Ordering
# فئة الاختبار 2: ترتيب التبعيات
# ===========================================================================


class TestDependencyOrdering:
    """Validate that startup ordering follows infrastructure-first rules.
    # التحقق من أن ترتيب بدء التشغيل يتبع قواعد البنية التحتية أولاً
    """

    @pytest.mark.parametrize("infra_svc", sorted(CORE_INFRA))
    def test_infra_does_not_depend_on_app_services(
        self,
        infra_svc: str,
        dependency_graph: dict[str, list[str]],
        application_services: set[str],
    ) -> None:
        """Infrastructure services must NOT depend on application services.
        # يجب ألا تعتمد خدمات البنية التحتية على خدمات التطبيق
        """
        deps = set(dependency_graph.get(infra_svc, []))
        app_deps = deps & application_services
        assert not app_deps, (
            f"Infrastructure service '{infra_svc}' depends on application "
            f"service(s): {sorted(app_deps)}"
        )

    def test_pgbouncer_depends_on_postgres(
        self,
        dependency_graph: dict[str, list[str]],
    ) -> None:
        """pgbouncer must depend on postgres for connection pooling.
        # يجب أن يعتمد pgbouncer على postgres لتجميع الاتصالات
        """
        pgbouncer_deps = dependency_graph.get("pgbouncer", [])
        assert "postgres" in pgbouncer_deps, (
            f"pgbouncer must depend on postgres. "
            f"Current deps: {pgbouncer_deps}"
        )

    def test_database_services_depend_on_db(
        self,
        compose_services: dict[str, Any],
        dependency_graph: dict[str, list[str]],
        application_services: set[str],
    ) -> None:
        """Services using DATABASE_URL must depend on pgbouncer or postgres.
        # الخدمات التي تستخدم DATABASE_URL يجب أن تعتمد على pgbouncer أو postgres
        """
        failures: list[str] = []
        for svc_name in sorted(application_services):
            svc_def = compose_services[svc_name]
            env_vars = _get_env_vars(svc_def)
            env_values = _get_env_values(svc_def)
            # Check if DATABASE_URL is declared or if DB_HOST / POSTGRES_ vars exist
            has_db = (
                "DATABASE_URL" in env_vars
                or "DB_HOST" in env_vars
                or any(k.startswith("POSTGRES_") for k in env_vars)
            )
            # Also check if the value references pgbouncer or postgres
            for val in env_values.values():
                if isinstance(val, str) and ("pgbouncer" in val or "postgres" in val):
                    has_db = True
                    break

            if has_db:
                deps = set(dependency_graph.get(svc_name, []))
                if "pgbouncer" not in deps and "postgres" not in deps:
                    failures.append(
                        f"  {svc_name}: uses DATABASE_URL but depends on {sorted(deps)}"
                    )

        if failures:
            pytest.fail(
                f"Services with DATABASE_URL must depend on pgbouncer or postgres:\n"
                + "\n".join(failures)
            )

    def test_nats_services_depend_on_nats(
        self,
        compose_services: dict[str, Any],
        dependency_graph: dict[str, list[str]],
        application_services: set[str],
    ) -> None:
        """Services using NATS_URL must depend on nats.
        # الخدمات التي تستخدم NATS_URL يجب أن تعتمد على nats
        """
        failures: list[str] = []
        for svc_name in sorted(application_services):
            svc_def = compose_services[svc_name]
            env_vars = _get_env_vars(svc_def)
            env_values = _get_env_values(svc_def)
            has_nats = "NATS_URL" in env_vars
            # Also check values referencing nats://
            for val in env_values.values():
                if isinstance(val, str) and "nats://" in val:
                    has_nats = True
                    break

            if has_nats:
                deps = set(dependency_graph.get(svc_name, []))
                if "nats" not in deps:
                    failures.append(
                        f"  {svc_name}: uses NATS_URL but depends on {sorted(deps)}"
                    )

        if failures:
            pytest.fail(
                f"Services with NATS_URL must depend on nats:\n"
                + "\n".join(failures)
            )

    def test_redis_services_depend_on_redis(
        self,
        compose_services: dict[str, Any],
        dependency_graph: dict[str, list[str]],
        application_services: set[str],
    ) -> None:
        """Services using REDIS_URL must depend on redis.
        # الخدمات التي تستخدم REDIS_URL يجب أن تعتمد على redis
        """
        failures: list[str] = []
        for svc_name in sorted(application_services):
            svc_def = compose_services[svc_name]
            env_vars = _get_env_vars(svc_def)
            env_values = _get_env_values(svc_def)
            has_redis = "REDIS_URL" in env_vars or "REDIS_HOST" in env_vars
            for val in env_values.values():
                if isinstance(val, str) and "redis://" in val:
                    has_redis = True
                    break

            if has_redis:
                deps = set(dependency_graph.get(svc_name, []))
                if "redis" not in deps:
                    failures.append(
                        f"  {svc_name}: uses REDIS_URL but depends on {sorted(deps)}"
                    )

        if failures:
            pytest.fail(
                f"Services with REDIS_URL must depend on redis:\n"
                + "\n".join(failures)
            )


# ===========================================================================
# Test Class 3: Dependency Completeness
# فئة الاختبار 3: اكتمال التبعيات
# ===========================================================================


class TestDependencyCompleteness:
    """Ensure all dependency references are valid and complete.
    # التأكد من أن جميع مراجع التبعيات صالحة وكاملة
    """

    def test_all_depends_on_targets_exist(
        self,
        compose_services: dict[str, Any],
        dependency_graph: dict[str, list[str]],
    ) -> None:
        """Every service referenced in depends_on must be defined in docker-compose.yml.
        # كل خدمة مذكورة في depends_on يجب أن تكون معرّفة في docker-compose.yml
        """
        all_defined = set(compose_services.keys())
        missing: list[str] = []
        for svc_name, deps in sorted(dependency_graph.items()):
            for dep in deps:
                if dep not in all_defined:
                    missing.append(f"  {svc_name} -> {dep} (not defined)")

        assert not missing, (
            f"depends_on references undefined services:\n" + "\n".join(missing)
        )

    def test_app_services_have_infra_dependency(
        self,
        compose_services: dict[str, Any],
        dependency_graph: dict[str, list[str]],
        application_services: set[str],
    ) -> None:
        """All application services must have at least 1 infrastructure dependency
        (direct or transitive through other services).
        # يجب أن يكون لكل خدمة تطبيق تبعية واحدة على الأقل للبنية التحتية
        # (مباشرة أو عبر خدمات أخرى)
        """
        # Services that are init containers, model loaders, or one-shot jobs
        # may legitimately have no infra deps. We detect them by restart: "no"
        # or by having no ports and no healthcheck.
        exempt: set[str] = set()
        for svc_name in application_services:
            svc_def = compose_services[svc_name]
            restart = svc_def.get("restart", "")
            # One-shot / init containers are exempt
            if restart == "no" or restart == '"no"':
                exempt.add(svc_name)
            # Services with profiles (optional) are exempt from this check
            if svc_def.get("profiles"):
                exempt.add(svc_name)

        def _has_transitive_infra_dep(
            service: str,
            visited: set[str],
        ) -> bool:
            """Check if a service transitively depends on any infra service.
            # التحقق مما إذا كانت الخدمة تعتمد بشكل عابر على أي خدمة بنية تحتية
            """
            if service in visited:
                return False
            visited.add(service)
            for dep in dependency_graph.get(service, []):
                if dep in INFRA_SERVICES:
                    return True
                if _has_transitive_infra_dep(dep, visited):
                    return True
            return False

        failures: list[str] = []
        for svc_name in sorted(application_services - exempt):
            deps = set(dependency_graph.get(svc_name, []))
            if not deps:
                failures.append(
                    f"  {svc_name}: no dependencies at all"
                )
            elif not _has_transitive_infra_dep(svc_name, set()):
                failures.append(
                    f"  {svc_name}: no infrastructure dependency "
                    f"(direct or transitive, deps: {sorted(deps)})"
                )

        if failures:
            pytest.fail(
                f"Application services without infrastructure dependencies:\n"
                + "\n".join(failures)
            )

    def test_no_dependency_on_deprecated_services(
        self,
        dependency_graph: dict[str, list[str]],
    ) -> None:
        """No service should depend on a deprecated/archived service.
        # لا يجب أن تعتمد أي خدمة على خدمة مهملة أو مؤرشفة
        """
        violations: list[str] = []
        for svc_name, deps in sorted(dependency_graph.items()):
            deprecated_deps = set(deps) & DEPRECATED_SERVICES
            if deprecated_deps:
                violations.append(
                    f"  {svc_name} depends on deprecated: {sorted(deprecated_deps)}"
                )

        assert not violations, (
            f"Services depend on deprecated services:\n" + "\n".join(violations)
        )


# ===========================================================================
# Test Class 4: Dependency Conditions
# فئة الاختبار 4: شروط التبعيات
# ===========================================================================


class TestDependencyConditions:
    """Validate that depends_on entries use proper health conditions.
    # التحقق من أن إدخالات depends_on تستخدم شروط صحة مناسبة
    """

    def test_depends_on_uses_condition_format(
        self,
        compose_services: dict[str, Any],
    ) -> None:
        """All depends_on entries should use dict format with condition, not bare list.
        # يجب أن تستخدم جميع إدخالات depends_on صيغة القاموس مع شرط، وليس قائمة مجردة
        """
        bare_list_services: list[str] = []
        for svc_name, svc_def in sorted(compose_services.items()):
            depends_on = svc_def.get("depends_on")
            if depends_on is not None and isinstance(depends_on, list):
                bare_list_services.append(
                    f"  {svc_name}: depends_on is a bare list {depends_on}"
                )

        assert not bare_list_services, (
            f"Services using bare-list depends_on (should use condition format):\n"
            + "\n".join(bare_list_services)
        )

    def test_depends_on_uses_service_healthy(
        self,
        compose_services: dict[str, Any],
    ) -> None:
        """depends_on entries for services with healthchecks should use service_healthy.
        # يجب أن تستخدم إدخالات depends_on شرط service_healthy للخدمات التي لديها فحص صحة
        """
        # First, identify all services that have healthchecks
        services_with_healthcheck: set[str] = set()
        for svc_name, svc_def in compose_services.items():
            if svc_def.get("healthcheck"):
                services_with_healthcheck.add(svc_name)

        # Check that when depending on a service with a healthcheck,
        # the condition is service_healthy
        violations: list[str] = []
        for svc_name, svc_def in sorted(compose_services.items()):
            depends_on = svc_def.get("depends_on")
            if not isinstance(depends_on, dict):
                continue
            for dep_name, dep_config in depends_on.items():
                if dep_name not in services_with_healthcheck:
                    continue
                if not isinstance(dep_config, dict):
                    violations.append(
                        f"  {svc_name} -> {dep_name}: no condition specified"
                    )
                    continue
                condition = dep_config.get("condition")
                if condition != "service_healthy":
                    violations.append(
                        f"  {svc_name} -> {dep_name}: "
                        f"condition is '{condition}', expected 'service_healthy'"
                    )

        assert not violations, (
            f"depends_on entries should use service_healthy for services "
            f"with healthchecks:\n" + "\n".join(violations)
        )

    def test_infra_healthcheck_deps_use_service_healthy(
        self,
        compose_services: dict[str, Any],
    ) -> None:
        """Infrastructure services with healthchecks must be depended on via service_healthy.
        # خدمات البنية التحتية التي لديها فحص صحة يجب الاعتماد عليها عبر service_healthy
        """
        # Identify infra services with healthchecks
        infra_with_hc: set[str] = set()
        for svc_name in INFRA_SERVICES:
            svc_def = compose_services.get(svc_name)
            if svc_def and svc_def.get("healthcheck"):
                infra_with_hc.add(svc_name)

        violations: list[str] = []
        for svc_name, svc_def in sorted(compose_services.items()):
            depends_on = svc_def.get("depends_on")
            if not depends_on:
                continue
            if isinstance(depends_on, list):
                # Bare list: cannot specify condition
                for dep in depends_on:
                    if dep in infra_with_hc:
                        violations.append(
                            f"  {svc_name} -> {dep}: bare list (needs "
                            f"condition: service_healthy)"
                        )
            elif isinstance(depends_on, dict):
                for dep_name, dep_config in depends_on.items():
                    if dep_name not in infra_with_hc:
                        continue
                    if not isinstance(dep_config, dict):
                        violations.append(
                            f"  {svc_name} -> {dep_name}: missing condition"
                        )
                    elif dep_config.get("condition") != "service_healthy":
                        violations.append(
                            f"  {svc_name} -> {dep_name}: condition is "
                            f"'{dep_config.get('condition')}', "
                            f"expected 'service_healthy'"
                        )

        assert not violations, (
            f"Infrastructure services with healthchecks must be depended on "
            f"via service_healthy:\n" + "\n".join(violations)
        )


# ===========================================================================
# Test Class 5: Dependency Depth
# فئة الاختبار 5: عمق التبعيات
# ===========================================================================


class TestDependencyDepth:
    """Validate that dependency chains do not exceed the maximum allowed depth.
    # التحقق من أن سلاسل التبعيات لا تتجاوز الحد الأقصى المسموح به
    """

    def test_no_service_exceeds_max_depth(
        self,
        dependency_graph: dict[str, list[str]],
        compose_services: dict[str, Any],
    ) -> None:
        """No service should have a dependency chain deeper than MAX_DEPENDENCY_DEPTH.
        # لا يجب أن تمتلك أي خدمة سلسلة تبعيات أعمق من الحد الأقصى
        """
        memo: dict[str, int] = {}
        violations: list[str] = []

        for svc_name in sorted(compose_services.keys()):
            depth = _compute_depth(svc_name, dependency_graph, memo)
            if depth > MAX_DEPENDENCY_DEPTH:
                violations.append(
                    f"  {svc_name}: depth={depth} (max={MAX_DEPENDENCY_DEPTH})"
                )

        assert not violations, (
            f"Services exceeding maximum dependency depth "
            f"({MAX_DEPENDENCY_DEPTH}):\n" + "\n".join(violations)
        )

    def test_maximum_depth_is_reasonable(
        self,
        dependency_graph: dict[str, list[str]],
        compose_services: dict[str, Any],
    ) -> None:
        """Calculate and validate the overall maximum depth of the dependency tree.
        # حساب والتحقق من أقصى عمق إجمالي لشجرة التبعيات
        """
        memo: dict[str, int] = {}
        max_depth = 0
        deepest_service = ""

        for svc_name in compose_services:
            depth = _compute_depth(svc_name, dependency_graph, memo)
            if depth > max_depth:
                max_depth = depth
                deepest_service = svc_name

        assert max_depth <= MAX_DEPENDENCY_DEPTH, (
            f"Maximum dependency depth is {max_depth} "
            f"(service: '{deepest_service}'), exceeds limit of "
            f"{MAX_DEPENDENCY_DEPTH}"
        )

    @pytest.mark.parametrize(
        "svc_name",
        sorted(ALL_HTTP_SERVICES.keys()),
    )
    def test_individual_service_depth(
        self,
        svc_name: str,
        dependency_graph: dict[str, list[str]],
    ) -> None:
        """Each HTTP service must have a dependency depth within limits.
        # يجب أن يكون عمق تبعية كل خدمة HTTP ضمن الحدود
        """
        if svc_name not in dependency_graph:
            pytest.skip(f"{svc_name} not in docker-compose.yml")
        memo: dict[str, int] = {}
        depth = _compute_depth(svc_name, dependency_graph, memo)
        assert depth <= MAX_DEPENDENCY_DEPTH, (
            f"Service '{svc_name}' has dependency depth {depth}, "
            f"exceeding limit of {MAX_DEPENDENCY_DEPTH}"
        )


# ===========================================================================
# Test Class 6: Infrastructure Dependency Isolation
# فئة الاختبار 6: عزل تبعيات البنية التحتية
# ===========================================================================


class TestInfrastructureDependencyIsolation:
    """Ensure infrastructure services are isolated from application services.
    # التأكد من عزل خدمات البنية التحتية عن خدمات التطبيق
    """

    @pytest.mark.parametrize("infra_svc", sorted(INFRA_SERVICES))
    def test_infra_only_depends_on_infra(
        self,
        infra_svc: str,
        dependency_graph: dict[str, list[str]],
        compose_services: dict[str, Any],
    ) -> None:
        """Infrastructure services should only depend on other infrastructure services.
        # يجب أن تعتمد خدمات البنية التحتية فقط على خدمات بنية تحتية أخرى
        """
        if infra_svc not in dependency_graph:
            pytest.skip(f"{infra_svc} not defined in docker-compose.yml")

        deps = set(dependency_graph.get(infra_svc, []))
        non_infra_deps = deps - INFRA_SERVICES
        assert not non_infra_deps, (
            f"Infrastructure service '{infra_svc}' depends on "
            f"non-infrastructure service(s): {sorted(non_infra_deps)}. "
            f"Infra services must only depend on other infra services."
        )

    def test_no_infra_depends_on_any_app(
        self,
        dependency_graph: dict[str, list[str]],
        compose_services: dict[str, Any],
        application_services: set[str],
    ) -> None:
        """No infrastructure service should depend on any application service.
        # لا يجب أن تعتمد أي خدمة بنية تحتية على أي خدمة تطبيق
        """
        violations: list[str] = []
        for infra_svc in sorted(INFRA_SERVICES):
            if infra_svc not in dependency_graph:
                continue
            deps = set(dependency_graph.get(infra_svc, []))
            app_deps = deps & application_services
            if app_deps:
                violations.append(
                    f"  {infra_svc} -> {sorted(app_deps)}"
                )

        assert not violations, (
            f"Infrastructure services depending on application services:\n"
            + "\n".join(violations)
        )

    def test_infra_dependency_graph_is_self_contained(
        self,
        dependency_graph: dict[str, list[str]],
        compose_services: dict[str, Any],
    ) -> None:
        """The infrastructure subgraph must be entirely self-contained.
        # يجب أن يكون الرسم البياني الفرعي للبنية التحتية مكتفيًا ذاتيًا بالكامل
        """
        infra_in_compose = {
            name for name in compose_services if name in INFRA_SERVICES
        }
        external_refs: list[str] = []
        for infra_svc in sorted(infra_in_compose):
            for dep in dependency_graph.get(infra_svc, []):
                if dep not in INFRA_SERVICES:
                    external_refs.append(f"  {infra_svc} -> {dep}")

        assert not external_refs, (
            f"Infrastructure subgraph references non-infra services:\n"
            + "\n".join(external_refs)
        )
