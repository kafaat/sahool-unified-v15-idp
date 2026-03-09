#!/usr/bin/env python3
"""
SAHOOL Kong Service Connectivity Test
=====================================

Comprehensive testing for Kong routes, rate limiting, CORS, and JWT authentication.
اختبار شامل لمسارات Kong والحد من المعدل و CORS والمصادقة JWT.

Usage:
    python service-connectivity-test.py [options]

Options:
    --kong-url URL        Kong gateway URL (default: http://localhost:8000)
    --admin-url URL       Kong admin URL (default: http://localhost:8001)
    --verbose             Enable verbose output
    --json                Output as JSON
    --output FILE         Write report to file
    --test TYPE           Run specific test (routes, rate-limit, cors, jwt, all)
    --skip-deprecated     Skip deprecated services

Author: SAHOOL Platform Team
Version: 16.0.0
Last Updated: 2026-02-07
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, UTC
from enum import Enum
from pathlib import Path
from typing import Any

# Try importing aiohttp, fallback to requests if not available
try:
    import aiohttp

    ASYNC_MODE = True
except ImportError:
    ASYNC_MODE = False
    import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class TestStatus(Enum):
    """Test result status."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WARNING = "warning"


class TestType(Enum):
    """Types of connectivity tests."""

    ROUTES = "routes"
    RATE_LIMIT = "rate-limit"
    CORS = "cors"
    JWT = "jwt"
    ALL = "all"


@dataclass
class TestResult:
    """Individual test result."""

    test_name: str
    test_name_ar: str
    status: TestStatus
    message: str
    message_ar: str
    duration_ms: float
    details: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class ServiceTestResult:
    """Test results for a single service."""

    service_name: str
    service_name_ar: str
    category: str
    tests: list[TestResult] = field(default_factory=list)
    overall_status: TestStatus = TestStatus.PASSED

    def add_result(self, result: TestResult):
        self.tests.append(result)
        if result.status == TestStatus.FAILED:
            self.overall_status = TestStatus.FAILED
        elif result.status == TestStatus.WARNING and self.overall_status != TestStatus.FAILED:
            self.overall_status = TestStatus.WARNING


@dataclass
class TestReport:
    """Complete test report."""

    platform: str = "SAHOOL"
    version: str = "16.0.0"
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    kong_url: str = ""
    total_services: int = 0
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    skipped: int = 0
    services: list[ServiceTestResult] = field(default_factory=list)
    misconfigured_services: list[dict] = field(default_factory=list)


class KongConnectivityTester:
    """
    Kong service connectivity tester.
    مختبر اتصال خدمات Kong.
    """

    def __init__(
        self,
        kong_url: str = "http://localhost:8000",
        admin_url: str = "http://localhost:8001",
        verbose: bool = False,
        skip_deprecated: bool = False,
    ):
        self.kong_url = kong_url.rstrip("/")
        self.admin_url = admin_url.rstrip("/")
        self.verbose = verbose
        self.skip_deprecated = skip_deprecated
        self.script_dir = Path(__file__).parent
        self.services_json_path = self.script_dir / "kong-services.json"
        self.services: list[dict] = []
        self.report = TestReport(kong_url=kong_url)

    def load_services(self) -> bool:
        """Load services from JSON registry."""
        if not self.services_json_path.exists():
            logger.error(f"Service registry not found: {self.services_json_path}")
            return False

        with open(self.services_json_path) as f:
            data = json.load(f)
            self.services = data.get("services", [])

        logger.info(f"Loaded {len(self.services)} services from registry")
        return True

    def _log(self, message: str, level: str = "info"):
        """Log message based on verbosity."""
        if level == "debug" and not self.verbose:
            return
        getattr(logger, level)(message)

    async def _async_request(
        self, method: str, url: str, headers: dict | None = None, timeout: int = 10, **kwargs
    ) -> tuple[int, dict, float]:
        """Make async HTTP request."""
        start_time = time.time()
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method,
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=timeout),
                    **kwargs,
                ) as response:
                    duration = (time.time() - start_time) * 1000
                    try:
                        body = await response.json()
                    except Exception:
                        body = {"raw": await response.text()}
                    return response.status, dict(response.headers), body, duration
            except TimeoutError:
                duration = (time.time() - start_time) * 1000
                return 0, {}, {"error": "timeout"}, duration
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                return 0, {}, {"error": str(e)}, duration

    def _sync_request(
        self, method: str, url: str, headers: dict | None = None, timeout: int = 10, **kwargs
    ) -> tuple[int, dict, dict, float]:
        """Make sync HTTP request."""
        start_time = time.time()
        try:
            response = requests.request(method, url, headers=headers, timeout=timeout, **kwargs)
            duration = (time.time() - start_time) * 1000
            try:
                body = response.json()
            except Exception:
                body = {"raw": response.text}
            return response.status_code, dict(response.headers), body, duration
        except requests.Timeout:
            duration = (time.time() - start_time) * 1000
            return 0, {}, {"error": "timeout"}, duration
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return 0, {}, {"error": str(e)}, duration

    async def test_route(self, service: dict) -> TestResult:
        """
        Test if route is accessible through Kong.
        اختبار إمكانية الوصول للمسار عبر Kong.
        """
        routes = service.get("routes", [])
        if not routes:
            return TestResult(
                test_name="Route Accessibility",
                test_name_ar="إمكانية الوصول للمسار",
                status=TestStatus.SKIPPED,
                message="No routes defined",
                message_ar="لا توجد مسارات محددة",
                duration_ms=0,
            )

        # Test first route
        route = routes[0]
        url = f"{self.kong_url}{route}"

        if ASYNC_MODE:
            status_code, headers, body, duration = await self._async_request("GET", url)
        else:
            status_code, headers, body, duration = self._sync_request("GET", url)

        if status_code == 0:
            return TestResult(
                test_name="Route Accessibility",
                test_name_ar="إمكانية الوصول للمسار",
                status=TestStatus.FAILED,
                message=f"Failed to reach route: {route}",
                message_ar=f"فشل الوصول للمسار: {route}",
                duration_ms=duration,
                details={"route": route, "error": body.get("error", "Unknown")},
            )

        # 4xx/5xx might be expected (auth required, etc.)
        if status_code in (401, 403):
            return TestResult(
                test_name="Route Accessibility",
                test_name_ar="إمكانية الوصول للمسار",
                status=TestStatus.PASSED,
                message=f"Route requires authentication (expected): {route}",
                message_ar=f"المسار يتطلب مصادقة (متوقع): {route}",
                duration_ms=duration,
                details={"route": route, "status_code": status_code},
            )
        elif status_code < 500:
            return TestResult(
                test_name="Route Accessibility",
                test_name_ar="إمكانية الوصول للمسار",
                status=TestStatus.PASSED,
                message=f"Route accessible: {route}",
                message_ar=f"المسار متاح: {route}",
                duration_ms=duration,
                details={"route": route, "status_code": status_code},
            )
        else:
            return TestResult(
                test_name="Route Accessibility",
                test_name_ar="إمكانية الوصول للمسار",
                status=TestStatus.WARNING,
                message=f"Route returned server error: {route} ({status_code})",
                message_ar=f"المسار أعاد خطأ في الخادم: {route} ({status_code})",
                duration_ms=duration,
                details={"route": route, "status_code": status_code},
            )

    async def test_rate_limiting(self, service: dict) -> TestResult:
        """
        Test rate limiting configuration.
        اختبار تكوين الحد من المعدل.
        """
        routes = service.get("routes", [])
        if not routes:
            return TestResult(
                test_name="Rate Limiting",
                test_name_ar="الحد من المعدل",
                status=TestStatus.SKIPPED,
                message="No routes to test",
                message_ar="لا توجد مسارات للاختبار",
                duration_ms=0,
            )

        route = routes[0]
        url = f"{self.kong_url}{route}"

        # Make a request and check for rate limit headers
        if ASYNC_MODE:
            status_code, headers, body, duration = await self._async_request("GET", url)
        else:
            status_code, headers, body, duration = self._sync_request("GET", url)

        # Check for rate limit headers
        rate_limit_headers = [
            "X-RateLimit-Limit-Minute",
            "X-RateLimit-Remaining-Minute",
            "RateLimit-Limit",
            "RateLimit-Remaining",
        ]

        found_headers = {h: headers.get(h) for h in rate_limit_headers if headers.get(h)}

        if found_headers:
            return TestResult(
                test_name="Rate Limiting",
                test_name_ar="الحد من المعدل",
                status=TestStatus.PASSED,
                message="Rate limiting is configured",
                message_ar="تم تكوين الحد من المعدل",
                duration_ms=duration,
                details={"headers": found_headers, "route": route},
            )
        else:
            # Rate limiting might be disabled for some routes (health checks, etc.)
            return TestResult(
                test_name="Rate Limiting",
                test_name_ar="الحد من المعدل",
                status=TestStatus.WARNING,
                message="No rate limit headers found (may be intentional)",
                message_ar="لم يتم العثور على رؤوس الحد من المعدل (قد يكون مقصوداً)",
                duration_ms=duration,
                details={"route": route},
            )

    async def test_cors(self, service: dict) -> TestResult:
        """
        Test CORS configuration.
        اختبار تكوين CORS.
        """
        routes = service.get("routes", [])
        if not routes:
            return TestResult(
                test_name="CORS Configuration",
                test_name_ar="تكوين CORS",
                status=TestStatus.SKIPPED,
                message="No routes to test",
                message_ar="لا توجد مسارات للاختبار",
                duration_ms=0,
            )

        route = routes[0]
        url = f"{self.kong_url}{route}"

        # Send preflight OPTIONS request
        preflight_headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Authorization, Content-Type",
        }

        if ASYNC_MODE:
            status_code, headers, body, duration = await self._async_request("OPTIONS", url, headers=preflight_headers)
        else:
            status_code, headers, body, duration = self._sync_request("OPTIONS", url, headers=preflight_headers)

        cors_headers = {
            "Access-Control-Allow-Origin": headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": headers.get("Access-Control-Allow-Headers"),
            "Access-Control-Max-Age": headers.get("Access-Control-Max-Age"),
        }

        if cors_headers["Access-Control-Allow-Origin"]:
            # Check for security issues
            if cors_headers["Access-Control-Allow-Origin"] == "*":
                return TestResult(
                    test_name="CORS Configuration",
                    test_name_ar="تكوين CORS",
                    status=TestStatus.WARNING,
                    message="CORS allows all origins (wildcard) - review for production",
                    message_ar="CORS يسمح بجميع المصادر (عام) - راجع للإنتاج",
                    duration_ms=duration,
                    details={"cors_headers": cors_headers, "route": route},
                )
            return TestResult(
                test_name="CORS Configuration",
                test_name_ar="تكوين CORS",
                status=TestStatus.PASSED,
                message="CORS is properly configured",
                message_ar="تم تكوين CORS بشكل صحيح",
                duration_ms=duration,
                details={"cors_headers": cors_headers, "route": route},
            )
        else:
            return TestResult(
                test_name="CORS Configuration",
                test_name_ar="تكوين CORS",
                status=TestStatus.WARNING,
                message="No CORS headers in response (may be configured differently)",
                message_ar="لا توجد رؤوس CORS في الاستجابة (قد تكون مكونة بشكل مختلف)",
                duration_ms=duration,
                details={"route": route},
            )

    async def test_jwt(self, service: dict) -> TestResult:
        """
        Test JWT authentication flow.
        اختبار تدفق مصادقة JWT.
        """
        routes = service.get("routes", [])
        if not routes:
            return TestResult(
                test_name="JWT Authentication",
                test_name_ar="مصادقة JWT",
                status=TestStatus.SKIPPED,
                message="No routes to test",
                message_ar="لا توجد مسارات للاختبار",
                duration_ms=0,
            )

        route = routes[0]
        url = f"{self.kong_url}{route}"

        # Test without JWT token
        if ASYNC_MODE:
            status_code_no_jwt, _, _, duration1 = await self._async_request("GET", url)
        else:
            status_code_no_jwt, _, _, duration1 = self._sync_request("GET", url)

        # Test with invalid JWT token
        headers_with_jwt = {"Authorization": "Bearer invalid.jwt.token"}
        if ASYNC_MODE:
            status_code_invalid_jwt, _, body, duration2 = await self._async_request(
                "GET", url, headers=headers_with_jwt
            )
        else:
            status_code_invalid_jwt, _, body, duration2 = self._sync_request("GET", url, headers=headers_with_jwt)

        total_duration = duration1 + duration2

        # Analyze responses
        jwt_protected = status_code_no_jwt in (401, 403)
        rejects_invalid = status_code_invalid_jwt in (401, 403)

        if jwt_protected and rejects_invalid:
            return TestResult(
                test_name="JWT Authentication",
                test_name_ar="مصادقة JWT",
                status=TestStatus.PASSED,
                message="JWT authentication is properly enforced",
                message_ar="تم تطبيق مصادقة JWT بشكل صحيح",
                duration_ms=total_duration,
                details={
                    "route": route,
                    "status_no_jwt": status_code_no_jwt,
                    "status_invalid_jwt": status_code_invalid_jwt,
                },
            )
        elif not jwt_protected:
            return TestResult(
                test_name="JWT Authentication",
                test_name_ar="مصادقة JWT",
                status=TestStatus.WARNING,
                message="Route does not require JWT (may be public endpoint)",
                message_ar="المسار لا يتطلب JWT (قد يكون نقطة نهاية عامة)",
                duration_ms=total_duration,
                details={"route": route, "status_no_jwt": status_code_no_jwt},
            )
        else:
            return TestResult(
                test_name="JWT Authentication",
                test_name_ar="مصادقة JWT",
                status=TestStatus.FAILED,
                message="JWT validation may have issues",
                message_ar="قد تكون هناك مشاكل في التحقق من JWT",
                duration_ms=total_duration,
                details={
                    "route": route,
                    "status_no_jwt": status_code_no_jwt,
                    "status_invalid_jwt": status_code_invalid_jwt,
                },
            )

    async def test_service(self, service: dict, test_types: list[TestType]) -> ServiceTestResult:
        """Run all specified tests for a service."""
        service_result = ServiceTestResult(
            service_name=service["name"],
            service_name_ar=service.get("name_ar", service["name"]),
            category=service.get("category", "unknown"),
        )

        test_mapping = {
            TestType.ROUTES: self.test_route,
            TestType.RATE_LIMIT: self.test_rate_limiting,
            TestType.CORS: self.test_cors,
            TestType.JWT: self.test_jwt,
        }

        for test_type in test_types:
            if test_type == TestType.ALL:
                continue
            test_func = test_mapping.get(test_type)
            if test_func:
                self._log(f"  Running {test_type.value} test for {service['name']}", "debug")
                result = await test_func(service)
                service_result.add_result(result)
                self.report.total_tests += 1

                if result.status == TestStatus.PASSED:
                    self.report.passed += 1
                elif result.status == TestStatus.FAILED:
                    self.report.failed += 1
                elif result.status == TestStatus.WARNING:
                    self.report.warnings += 1
                else:
                    self.report.skipped += 1

        return service_result

    async def run_tests(self, test_types: list[TestType]) -> TestReport:
        """Run connectivity tests on all services."""
        if not self.load_services():
            return self.report

        # Determine which tests to run
        if TestType.ALL in test_types:
            test_types = [TestType.ROUTES, TestType.RATE_LIMIT, TestType.CORS, TestType.JWT]

        logger.info(f"Running tests: {[t.value for t in test_types]}")
        logger.info(f"Testing against Kong: {self.kong_url}")
        print()

        for service in self.services:
            # Skip deprecated if requested
            if self.skip_deprecated and service.get("deprecated", False):
                self._log(f"Skipping deprecated service: {service['name']}", "debug")
                continue

            self.report.total_services += 1
            logger.info(f"Testing service: {service['name']} ({service.get('name_ar', '')})")

            service_result = await self.test_service(service, test_types)
            self.report.services.append(service_result)

            # Track misconfigured services
            if service_result.overall_status == TestStatus.FAILED:
                self.report.misconfigured_services.append(
                    {
                        "name": service["name"],
                        "name_ar": service.get("name_ar", ""),
                        "category": service.get("category", ""),
                        "issues": [
                            {"test": t.test_name, "message": t.message}
                            for t in service_result.tests
                            if t.status == TestStatus.FAILED
                        ],
                    }
                )

        return self.report

    def print_report(self, output_json: bool = False, output_file: str | None = None):
        """Print or save the test report."""

        def serialize_report(obj):
            """Custom serializer for report objects."""
            if isinstance(obj, TestStatus):
                return obj.value
            if isinstance(obj, (TestResult, ServiceTestResult)):
                return asdict(obj)
            if hasattr(obj, "__dict__"):
                return obj.__dict__
            return str(obj)

        if output_json:
            report_dict = asdict(self.report)
            # Fix enum serialization
            report_json = json.dumps(report_dict, default=serialize_report, indent=2, ensure_ascii=False)

            if output_file:
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(report_json)
                logger.info(f"Report saved to: {output_file}")
            else:
                print(report_json)
        else:
            # Text output
            print()
            print("=" * 78)
            print("  SAHOOL Kong Connectivity Test Report")
            print("  تقرير اختبار اتصال Kong لمنصة سهول")
            print("=" * 78)
            print()
            print(f"Timestamp: {self.report.timestamp}")
            print(f"Kong URL: {self.report.kong_url}")
            print()
            print("-" * 78)
            print("Summary | ملخص")
            print("-" * 78)
            print()
            print(f"  Total Services:  {self.report.total_services}")
            print(f"  Total Tests:     {self.report.total_tests}")
            print(f"  Passed:          {self.report.passed} (OK)")
            print(f"  Failed:          {self.report.failed} (FAIL)")
            print(f"  Warnings:        {self.report.warnings} (WARN)")
            print(f"  Skipped:         {self.report.skipped}")
            print()

            if self.report.misconfigured_services:
                print("-" * 78)
                print("Misconfigured Services | الخدمات ذات التكوين الخاطئ")
                print("-" * 78)
                print()
                for svc in self.report.misconfigured_services:
                    print(f"  {svc['name']} ({svc['name_ar']}) - {svc['category']}")
                    for issue in svc["issues"]:
                        print(f"    - {issue['test']}: {issue['message']}")
                    print()

            print("=" * 78)

            if output_file:
                # Save text report
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write("SAHOOL Kong Connectivity Test Report\n")
                    f.write(f"{'=' * 40}\n\n")
                    f.write(f"Timestamp: {self.report.timestamp}\n")
                    f.write(f"Total: {self.report.total_tests}, Passed: {self.report.passed}, ")
                    f.write(f"Failed: {self.report.failed}, Warnings: {self.report.warnings}\n\n")

                    for svc in self.report.services:
                        f.write(f"\n{svc.service_name}: {svc.overall_status.value}\n")
                        for test in svc.tests:
                            f.write(f"  - {test.test_name}: {test.status.value}\n")

                logger.info(f"Report saved to: {output_file}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="SAHOOL Kong Service Connectivity Test",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python service-connectivity-test.py
  python service-connectivity-test.py --test routes
  python service-connectivity-test.py --json --output report.json
  python service-connectivity-test.py --verbose --skip-deprecated
        """,
    )

    parser.add_argument(
        "--kong-url",
        default=os.environ.get("KONG_GATEWAY_URL", "http://localhost:8000"),
        help="Kong gateway URL (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--admin-url",
        default=os.environ.get("KONG_ADMIN_URL", "http://localhost:8001"),
        help="Kong admin URL (default: http://localhost:8001)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("-j", "--json", action="store_true", help="Output as JSON")
    parser.add_argument("-o", "--output", help="Write report to file")
    parser.add_argument(
        "--test",
        choices=["routes", "rate-limit", "cors", "jwt", "all"],
        default="all",
        help="Run specific test type (default: all)",
    )
    parser.add_argument("--skip-deprecated", action="store_true", help="Skip deprecated services")

    return parser.parse_args()


async def main_async(args):
    """Async main function."""
    tester = KongConnectivityTester(
        kong_url=args.kong_url,
        admin_url=args.admin_url,
        verbose=args.verbose,
        skip_deprecated=args.skip_deprecated,
    )

    # Map test argument to TestType
    test_type_map = {
        "routes": [TestType.ROUTES],
        "rate-limit": [TestType.RATE_LIMIT],
        "cors": [TestType.CORS],
        "jwt": [TestType.JWT],
        "all": [TestType.ALL],
    }
    test_types = test_type_map.get(args.test, [TestType.ALL])

    await tester.run_tests(test_types)
    tester.print_report(output_json=args.json, output_file=args.output)

    # Exit with appropriate code
    if tester.report.failed > 0:
        sys.exit(1)
    sys.exit(0)


def main():
    """Main entry point."""
    args = parse_args()

    print()
    print("=" * 78)
    print("  SAHOOL Kong Service Connectivity Test")
    print("  اختبار اتصال خدمات Kong لمنصة سهول")
    print("=" * 78)
    print()

    if ASYNC_MODE:
        asyncio.run(main_async(args))
    else:
        logger.warning("aiohttp not installed, using synchronous requests")
        # Fallback to sync mode (simplified)
        tester = KongConnectivityTester(
            kong_url=args.kong_url,
            admin_url=args.admin_url,
            verbose=args.verbose,
            skip_deprecated=args.skip_deprecated,
        )
        asyncio.run(tester.run_tests([TestType.ALL]))
        tester.print_report(output_json=args.json, output_file=args.output)


if __name__ == "__main__":
    main()
