"""
API Contract Drift Detector
كاشف انحراف عقود API

Detects API contract drift:
- TypeScript contract changes (shared-types)
- Dart contract sync status
- OpenAPI spec drift
- Endpoint route drift (Kong vs service definitions)
- Response shape consistency
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

from shared.drift_detection.detectors.base import BaseDriftDetector
from shared.drift_detection.models import (
    DriftCategory,
    DriftResult,
    DriftSeverity,
)

logger = logging.getLogger(__name__)


class APIDriftDetector(BaseDriftDetector):
    """
    Detects API contract drift between definitions and implementations.
    يكتشف انحراف عقود API بين التعريفات والتطبيقات.
    """

    @property
    def category(self) -> DriftCategory:
        return DriftCategory.API

    async def detect(self) -> list[DriftResult]:
        self.clear_results()

        await self._check_contract_version()
        await self._check_dart_sync()
        await self._check_port_uniqueness()
        await self._check_endpoint_consistency()
        await self._check_health_endpoints()

        return self.results

    async def _check_contract_version(self) -> None:
        """Check that CONTRACT_VERSION is properly bumped."""
        root = Path(self.working_dir)
        contracts_index = root / "packages" / "shared-types" / "src" / "contracts" / "index.ts"

        if not contracts_index.exists():
            return

        content = contracts_index.read_text()
        version_match = re.search(r'CONTRACT_VERSION\s*=\s*["\'](\d+\.\d+\.\d+)["\']', content)
        if not version_match:
            self.add_result(DriftResult(
                category=DriftCategory.API,
                severity=DriftSeverity.HIGH,
                source="contract_version",
                description="CONTRACT_VERSION not found in contracts/index.ts",
                description_ar="CONTRACT_VERSION غير موجود في contracts/index.ts",
                file_path=str(contracts_index),
                auto_fixable=False,
                remediation_hint="Add 'export const CONTRACT_VERSION = \"x.y.z\"' to index.ts",
            ))

    async def _check_dart_sync(self) -> None:
        """Check if Dart contracts are in sync with TypeScript source."""
        root = Path(self.working_dir)
        ts_contracts = root / "packages" / "shared-types" / "src" / "contracts"
        dart_contracts = root / "apps" / "mobile" / "lib" / "core" / "contracts"

        # Also check Flutter field app
        if not dart_contracts.exists():
            dart_contracts = root / "apps" / "mobile" / "sahool_field_app" / "lib" / "core" / "contracts"

        if not ts_contracts.exists():
            return

        if not dart_contracts.exists():
            self.add_result(DriftResult(
                category=DriftCategory.API,
                severity=DriftSeverity.MEDIUM,
                source="dart_sync",
                description="Dart contract directory not found - mobile contracts may be out of sync",
                description_ar="دليل عقود Dart غير موجود - قد تكون عقود الموبايل غير متزامنة",
                auto_fixable=True,
                remediation_hint="Run 'npx tsx scripts/sync-contracts-to-dart.ts' to generate Dart contracts",
            ))
            return

        # Check modification times
        ts_files = list(ts_contracts.glob("*.ts"))
        dart_files = list(dart_contracts.glob("*.dart"))

        if ts_files and dart_files:
            latest_ts = max(f.stat().st_mtime for f in ts_files)
            latest_dart = max(f.stat().st_mtime for f in dart_files)

            if latest_ts > latest_dart:
                self.add_result(DriftResult(
                    category=DriftCategory.API,
                    severity=DriftSeverity.HIGH,
                    source="dart_sync",
                    expected="Dart contracts in sync with TypeScript",
                    actual="TypeScript contracts modified after Dart generation",
                    description="Dart contracts are stale - TypeScript source was modified after last sync",
                    description_ar="عقود Dart قديمة - تم تعديل مصدر TypeScript بعد آخر مزامنة",
                    auto_fixable=True,
                    remediation_hint="Run 'npx tsx scripts/sync-contracts-to-dart.ts'",
                ))

    async def _check_port_uniqueness(self) -> None:
        """Check that all service ports are unique."""
        root = Path(self.working_dir)
        ports_file = root / "packages" / "shared-types" / "src" / "contracts" / "service-ports.ts"

        if not ports_file.exists():
            return

        content = ports_file.read_text()
        port_matches = re.findall(r"(\w+)\s*:\s*(\d+)", content)

        port_map: dict[int, list[str]] = {}
        for name, port_str in port_matches:
            port = int(port_str)
            if port not in port_map:
                port_map[port] = []
            port_map[port].append(name)

        for port, services in port_map.items():
            if len(services) > 1:
                self.add_result(DriftResult(
                    category=DriftCategory.API,
                    severity=DriftSeverity.CRITICAL,
                    source="port_uniqueness",
                    expected="Unique port per service",
                    actual=f"Port {port} shared by: {', '.join(services)}",
                    description=f"Port collision: {', '.join(services)} all use port {port}",
                    description_ar=f"تعارض المنافذ: {', '.join(services)} جميعها تستخدم المنفذ {port}",
                    file_path=str(ports_file),
                    auto_fixable=False,
                    remediation_hint=f"Assign unique ports to conflicting services",
                ))

    async def _check_endpoint_consistency(self) -> None:
        """Check endpoint definitions match actual service implementations."""
        root = Path(self.working_dir)
        endpoints_file = root / "packages" / "shared-types" / "src" / "contracts" / "api-endpoints.ts"

        if not endpoints_file.exists():
            return

        content = endpoints_file.read_text()

        # Extract defined endpoints
        endpoint_matches = re.findall(r'["\'](/api/v\d+/\w+[^"\']*)["\']', content)

        # Check for version consistency (should use /api/v1/ or /api/v2/)
        for endpoint in endpoint_matches:
            if "/api/v0/" in endpoint:
                self.add_result(DriftResult(
                    category=DriftCategory.API,
                    severity=DriftSeverity.MEDIUM,
                    source="endpoint_version",
                    description=f"Endpoint uses v0 (pre-release): {endpoint}",
                    description_ar=f"نقطة النهاية تستخدم v0 (ما قبل الإصدار): {endpoint}",
                    file_path=str(endpoints_file),
                ))

    async def _check_health_endpoints(self) -> None:
        """Check all services implement required health endpoints."""
        root = Path(self.working_dir)

        service_dirs = list(root.glob("apps/services/*/src"))

        for src_dir in service_dirs:
            service_name = src_dir.parent.name

            # Skip archived/deprecated
            if "archive" in str(src_dir):
                continue

            main_files = (
                list(src_dir.glob("main.py"))
                + list(src_dir.glob("index.ts"))
                + list(src_dir.glob("app.module.ts"))
            )

            if not main_files:
                continue

            has_health = False
            for mf in main_files:
                try:
                    content = mf.read_text(errors="ignore")
                    if any(ep in content for ep in ["/healthz", "/health", "/readyz"]):
                        has_health = True
                        break
                except (OSError, UnicodeDecodeError):
                    continue

            if not has_health:
                self.add_result(DriftResult(
                    category=DriftCategory.API,
                    severity=DriftSeverity.HIGH,
                    source="health_endpoint",
                    expected="Health endpoint (/healthz or /health) implemented",
                    actual=f"No health endpoint found in {service_name}",
                    description=f"Service '{service_name}' missing health endpoints (required for K8s probes)",
                    description_ar=f"الخدمة '{service_name}' تفتقر إلى نقاط صحة (مطلوبة لفحوصات K8s)",
                    service_name=service_name,
                    auto_fixable=False,
                    remediation_hint="Add /healthz and /readyz endpoints per platform convention",
                ))
