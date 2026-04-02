#!/usr/bin/env python3
"""
SAHOOL CLI — Complete DevOps Tool
Platform deployment, load testing, performance analysis, and auto-scaling.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Optional

import click

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

logger = logging.getLogger(__name__)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def cli(verbose: bool) -> None:
    """SAHOOL Platform DevOps CLI"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Deploy command
# ─────────────────────────────────────────────────────────────────────────────


@cli.command()
@click.option("--service", required=True, help="Service name to deploy")
@click.option("--version", required=True, help="Version tag")
@click.option("--environment", default="staging", help="Target environment")
@click.option("--replicas", default=3, type=int, help="Number of replicas")
@click.option(
    "--verify-isolation",
    is_flag=True,
    help="Verify tenant isolation after deploy",
)
def deploy(
    service: str,
    version: str,
    environment: str,
    replicas: int,
    verify_isolation: bool,
) -> None:
    """Deploy service with tenant isolation verification."""

    async def _deploy() -> None:
        from shared.devops import DeploymentConfig, KubernetesDeployer

        deployer = KubernetesDeployer(namespace=f"sahool-{environment}")
        cfg = DeploymentConfig(
            service_name=service,
            version=version,
            replicas=replicas,
        )

        result = await deployer.deploy_service(cfg)
        click.echo(f"✅ Deployed: {json.dumps(result, indent=2)}")

        if verify_isolation:
            verification = await deployer.verify_tenant_isolation(service)
            click.echo(
                f"🔒 Isolation check: {json.dumps(verification, indent=2)}"
            )

            if not verification["all_pods_compliant"]:
                click.echo(
                    "❌ Tenant isolation not verified! Consider rolling back."
                )
                raise SystemExit(1)

    asyncio.run(_deploy())


# ─────────────────────────────────────────────────────────────────────────────
# Rollback command
# ─────────────────────────────────────────────────────────────────────────────


@cli.command()
@click.option("--service", required=True, help="Service name")
@click.option("--to-version", required=True, help="Version to rollback to")
@click.option("--environment", default="production", help="Target environment")
def rollback(service: str, to_version: str, environment: str) -> None:
    """Rollback a service to a previous version."""

    async def _rollback() -> None:
        from shared.devops import KubernetesDeployer

        deployer = KubernetesDeployer(namespace=f"sahool-{environment}")
        result = await deployer.rollback(service, to_version)
        click.echo(f"✅ Rollback complete: {json.dumps(result, indent=2)}")

    asyncio.run(_rollback())


# ─────────────────────────────────────────────────────────────────────────────
# Load-test command
# ─────────────────────────────────────────────────────────────────────────────


@cli.command("load-test")
@click.option("--environment", required=True, help="Target environment")
@click.option("--duration", default=60, type=int, help="Test duration in seconds")
@click.option("--tenants", default=10, type=int, help="Number of simulated tenants")
@click.option(
    "--requests-per-tenant",
    default=100,
    type=int,
    help="Requests per tenant",
)
@click.option(
    "--verify-isolation",
    is_flag=True,
    help="Verify tenant isolation under load",
)
def load_test(
    environment: str,
    duration: int,
    tenants: int,
    requests_per_tenant: int,
    verify_isolation: bool,
) -> None:
    """Run load test with tenant isolation verification."""

    async def _test() -> None:
        from shared.devops import LoadTestScenario, TenantAwareLoadTester

        base_url = f"https://api-{environment}.sahool.app"

        async with TenantAwareLoadTester(base_url) as tester:
            scenario = LoadTestScenario(
                name="list_fields",
                endpoint="/fields",
                method="GET",
            )

            test_tenants = [f"test-tenant-{i}" for i in range(tenants)]

            result = await tester.run_scenario(
                scenario,
                test_tenants,
                duration_seconds=duration,
                requests_per_tenant=requests_per_tenant,
            )

            click.echo("📊 Load test result:")
            click.echo(f"   Total requests:  {result.total_requests}")
            click.echo(f"   Successful:      {result.successful_requests}")
            click.echo(f"   Failed:          {result.failed_requests}")
            click.echo(f"   Avg response:    {result.avg_response_time_ms:.1f} ms")
            click.echo(f"   P95 response:    {result.p95_response_time_ms:.1f} ms")
            click.echo(f"   P99 response:    {result.p99_response_time_ms:.1f} ms")
            click.echo(f"   Requests/sec:    {result.requests_per_second:.1f}")

            if verify_isolation:
                isolation = await tester.verify_tenant_isolation_under_load()
                click.echo(
                    f"\n🔒 Isolation verification: {json.dumps(isolation, indent=2)}"
                )

                if not isolation["isolation_intact"]:
                    click.echo("❌ CRITICAL: Tenant isolation breach detected!")
                    raise SystemExit(1)

    asyncio.run(_test())


# ─────────────────────────────────────────────────────────────────────────────
# Analyze-performance command
# ─────────────────────────────────────────────────────────────────────────────


@cli.command("analyze-performance")
@click.option("--environment", required=True, help="Target environment")
@click.option("--output", default=None, help="Output file path (JSON)")
def analyze_performance(environment: str, output: str | None) -> None:
    """Analyze and optimize performance."""

    async def _analyze() -> None:
        from shared.devops import PerformanceAnalyzer

        # PerformanceAnalyzer requires redis/metrics for cache analysis;
        # when invoked via CLI without live connections, database and
        # resource analysis still work.  Cache-related methods return
        # empty results gracefully.
        analyzer = PerformanceAnalyzer(redis=None, metrics=None)  # type: ignore[arg-type]
        report = await analyzer.generate_optimization_report()

        formatted = json.dumps(report, indent=2, default=str)
        click.echo(formatted)

        if output:
            with open(output, "w") as f:
                f.write(formatted)
            click.echo(f"\n📄 Report saved to {output}")

    asyncio.run(_analyze())


# ─────────────────────────────────────────────────────────────────────────────
# Auto-scale command
# ─────────────────────────────────────────────────────────────────────────────


@cli.command("auto-scale")
@click.option("--environment", required=True, help="Target environment")
@click.option("--dry-run", is_flag=True, help="Evaluate without applying changes")
def auto_scale(environment: str, dry_run: bool) -> None:
    """Evaluate and apply auto-scaling decisions."""

    async def _scale() -> None:
        from shared.devops import AutoScaler, KubernetesDeployer

        deployer = KubernetesDeployer(namespace=f"sahool-{environment}")
        scaler = AutoScaler(deployer)

        decisions = await scaler.evaluate_scaling_needs()
        click.echo(f"📊 Scaling decisions: {json.dumps(decisions, indent=2)}")

        if decisions["decisions"] and not dry_run:
            applied = await scaler.apply_scaling(decisions["decisions"])
            click.echo(f"✅ Applied: {json.dumps(applied, indent=2)}")
        elif dry_run:
            click.echo("ℹ️  Dry-run mode — no changes applied.")

    asyncio.run(_scale())


# ─────────────────────────────────────────────────────────────────────────────
# Verify command
# ─────────────────────────────────────────────────────────────────────────────


@cli.command()
@click.option("--environment", required=True, help="Target environment")
@click.option("--service", default=None, help="Service name (all if omitted)")
@click.option(
    "--check-tenant-isolation",
    is_flag=True,
    help="Verify tenant isolation",
)
def verify(
    environment: str, service: str | None, check_tenant_isolation: bool
) -> None:
    """Verify deployment and tenant isolation."""

    async def _verify() -> None:
        from shared.devops import KubernetesDeployer

        deployer = KubernetesDeployer(namespace=f"sahool-{environment}")

        if service and check_tenant_isolation:
            result = await deployer.verify_tenant_isolation(service)
            click.echo(json.dumps(result, indent=2))

            if not result["all_pods_compliant"]:
                click.echo("❌ Tenant isolation verification FAILED")
                raise SystemExit(1)
            click.echo("✅ Tenant isolation verified")
        else:
            click.echo(
                "ℹ️  Provide --service and --check-tenant-isolation to verify."
            )

    asyncio.run(_verify())


if __name__ == "__main__":
    cli()
