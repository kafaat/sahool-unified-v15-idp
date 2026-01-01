"""
GlobalGAP Supply Chain Portal API Client
عميل واجهة برمجة بوابة سلسلة التوريد GlobalGAP

Client for interacting with GlobalGAP's Supply Chain Portal API to verify
certificates and search producer information.

عميل للتفاعل مع واجهة برمجة بوابة سلسلة التوريد GlobalGAP للتحقق من
الشهادات والبحث عن معلومات المنتجين.

Author: SAHOOL Platform Team
Version: 1.0.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
import asyncio
from contextlib import asynccontextmanager

import httpx
import structlog
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

logger = structlog.get_logger()


# ═══════════════════════════════════════════════════════════════════════════
# Data Models / نماذج البيانات
# ═══════════════════════════════════════════════════════════════════════════


class CertificateStatus(str, Enum):
    """
    Certificate status enumeration
    تعداد حالات الشهادة

    Possible values:
    - VALID: الشهادة صالحة
    - EXPIRED: الشهادة منتهية الصلاحية
    - SUSPENDED: الشهادة معلقة
    - WITHDRAWN: الشهادة مسحوبة
    """

    VALID = "valid"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    WITHDRAWN = "withdrawn"


@dataclass
class CertificateInfo:
    """
    GlobalGAP certificate information
    معلومات شهادة GlobalGAP

    Attributes:
        ggn: GlobalGAP Number (رقم GlobalGAP)
        status: Certificate status (حالة الشهادة)
        valid_from: Start date of validity (تاريخ بداية الصلاحية)
        valid_to: End date of validity (تاريخ نهاية الصلاحية)
        scope: Certification scope (نطاق الشهادة)
        cb_name: Certification body name (اسم جهة الشهادة)
        product_categories: Product categories (فئات المنتجات)
        producer_name: Producer/farm name (اسم المنتج/المزرعة)
        country: Country code (رمز البلد)
        sub_scopes: Sub-scopes covered (النطاقات الفرعية المشمولة)
    """

    ggn: str
    status: CertificateStatus
    valid_from: datetime
    valid_to: datetime
    scope: str
    cb_name: str
    product_categories: List[str] = field(default_factory=list)
    producer_name: Optional[str] = None
    country: Optional[str] = None
    sub_scopes: List[str] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        """
        Check if certificate is currently valid
        التحقق من صحة الشهادة حالياً

        Returns:
            True if certificate is valid and not expired
        """
        now = datetime.now()
        return (
            self.status == CertificateStatus.VALID
            and self.valid_from <= now <= self.valid_to
        )

    def days_until_expiry(self) -> int:
        """
        Calculate days until certificate expires
        حساب الأيام حتى انتهاء صلاحية الشهادة

        Returns:
            Number of days (negative if already expired)
        """
        delta = self.valid_to - datetime.now()
        return delta.days


@dataclass
class Producer:
    """
    Producer/farm information
    معلومات المنتج/المزرعة

    Attributes:
        name: Producer name (اسم المنتج)
        country: Country name or code (اسم البلد أو الرمز)
        products: List of products (قائمة المنتجات)
        certification_status: Current certification status (حالة الشهادة الحالية)
        ggn: GlobalGAP Number if available (رقم GlobalGAP إذا كان متوفراً)
        location: Geographic location (الموقع الجغرافي)
        certification_date: Date of certification (تاريخ الشهادة)
    """

    name: str
    country: str
    products: List[str]
    certification_status: CertificateStatus
    ggn: Optional[str] = None
    location: Optional[str] = None
    certification_date: Optional[datetime] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════
# Exceptions / الاستثناءات
# ═══════════════════════════════════════════════════════════════════════════


class GlobalGAPAPIError(Exception):
    """
    Base exception for GlobalGAP API errors
    الاستثناء الأساسي لأخطاء واجهة برمجة GlobalGAP

    Attributes:
        message: Error message in English (رسالة الخطأ بالإنجليزية)
        message_ar: Error message in Arabic (رسالة الخطأ بالعربية)
        status_code: HTTP status code if applicable (رمز حالة HTTP إن وجد)
        details: Additional error details (تفاصيل إضافية للخطأ)
    """

    def __init__(
        self,
        message: str,
        message_ar: str,
        status_code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.message_ar = message_ar
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

    def to_dict(self, lang: str = "en") -> Dict[str, Any]:
        """
        Convert exception to dictionary for API response
        تحويل الاستثناء إلى قاموس لاستجابة واجهة البرمجة

        Args:
            lang: Language code ('en' or 'ar')

        Returns:
            Dictionary representation
        """
        message = self.message_ar if lang == "ar" else self.message
        return {
            "error": self.__class__.__name__,
            "message": message,
            "status_code": self.status_code,
            "details": self.details,
        }


class CertificateNotFound(GlobalGAPAPIError):
    """
    Exception raised when certificate is not found
    استثناء يُثار عندما لا يتم العثور على الشهادة
    """

    def __init__(self, ggn: str):
        super().__init__(
            message=f"Certificate not found for GGN: {ggn}",
            message_ar=f"لم يتم العثور على شهادة لرقم GGN: {ggn}",
            status_code=404,
            details={"ggn": ggn},
        )


class InvalidGGN(GlobalGAPAPIError):
    """
    Exception raised when GGN format is invalid
    استثناء يُثار عندما يكون تنسيق GGN غير صالح
    """

    def __init__(self, ggn: str):
        super().__init__(
            message=f"Invalid GGN format: {ggn}",
            message_ar=f"تنسيق GGN غير صالح: {ggn}",
            status_code=400,
            details={"ggn": ggn},
        )


class RateLimitExceeded(GlobalGAPAPIError):
    """
    Exception raised when rate limit is exceeded
    استثناء يُثار عند تجاوز حد المعدل
    """

    def __init__(self, retry_after: Optional[int] = None):
        super().__init__(
            message="Rate limit exceeded. Please try again later.",
            message_ar="تم تجاوز حد المعدل. يرجى المحاولة مرة أخرى لاحقاً.",
            status_code=429,
            details={"retry_after": retry_after},
        )


class AuthenticationError(GlobalGAPAPIError):
    """
    Exception raised when authentication fails
    استثناء يُثار عند فشل المصادقة
    """

    def __init__(self):
        super().__init__(
            message="Authentication failed. Invalid or missing API key.",
            message_ar="فشلت المصادقة. مفتاح واجهة البرمجة غير صالح أو مفقود.",
            status_code=401,
        )


# ═══════════════════════════════════════════════════════════════════════════
# Rate Limiter / محدد المعدل
# ═══════════════════════════════════════════════════════════════════════════


class RateLimiter:
    """
    Token bucket rate limiter
    محدد معدل دلو الرموز

    Implements token bucket algorithm for rate limiting API requests.
    ينفذ خوارزمية دلو الرموز لتحديد معدل طلبات واجهة البرمجة.
    """

    def __init__(self, rate: int = 10, per: int = 60):
        """
        Initialize rate limiter
        تهيئة محدد المعدل

        Args:
            rate: Number of requests allowed (عدد الطلبات المسموح بها)
            per: Time period in seconds (الفترة الزمنية بالثواني)
        """
        self.rate = rate
        self.per = per
        self.tokens = rate
        self.last_update = datetime.now()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """
        Acquire token for making a request
        الحصول على رمز لإجراء طلب

        Blocks if no tokens are available until tokens are replenished.
        يحظر إذا لم تكن هناك رموز متاحة حتى يتم تجديد الرموز.
        """
        async with self._lock:
            now = datetime.now()
            elapsed = (now - self.last_update).total_seconds()

            # Replenish tokens based on elapsed time
            # تجديد الرموز بناءً على الوقت المنقضي
            self.tokens = min(self.rate, self.tokens + (elapsed * self.rate / self.per))
            self.last_update = now

            # Wait if no tokens available
            # الانتظار إذا لم تكن هناك رموز متاحة
            if self.tokens < 1:
                wait_time = (1 - self.tokens) * self.per / self.rate
                logger.warning(
                    "rate_limit_waiting",
                    wait_time=wait_time,
                )
                await asyncio.sleep(wait_time)
                self.tokens = 1

            self.tokens -= 1


# ═══════════════════════════════════════════════════════════════════════════
# GlobalGAP Client / عميل GlobalGAP
# ═══════════════════════════════════════════════════════════════════════════


class GlobalGAPClient:
    """
    Async HTTP client for GlobalGAP Supply Chain Portal API
    عميل HTTP غير متزامن لواجهة برمجة بوابة سلسلة التوريد GlobalGAP

    Provides methods to verify certificates, search producers, and retrieve
    certificate status from GlobalGAP's public API.

    يوفر طرقاً للتحقق من الشهادات والبحث عن المنتجين واسترجاع حالة الشهادة
    من واجهة برمجة GlobalGAP العامة.

    Example:
        client = GlobalGAPClient(api_key="your-api-key")
        cert_info = await client.verify_certificate("4063061891234")
        print(f"Status: {cert_info.status}")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://www.globalgap.org/api/v1",
        timeout: int = 30,
        max_retries: int = 3,
        rate_limit: int = 10,
        rate_limit_period: int = 60,
        mock_mode: bool = False,
    ):
        """
        Initialize GlobalGAP client
        تهيئة عميل GlobalGAP

        Args:
            api_key: GlobalGAP API key (مفتاح واجهة برمجة GlobalGAP)
            base_url: Base URL for API (عنوان URL الأساسي لواجهة البرمجة)
            timeout: Request timeout in seconds (مهلة الطلب بالثواني)
            max_retries: Maximum retry attempts (الحد الأقصى لمحاولات إعادة المحاولة)
            rate_limit: Requests per period (الطلبات في الفترة)
            rate_limit_period: Period in seconds (الفترة بالثواني)
            mock_mode: Enable mock mode for testing (تمكين وضع المحاكاة للاختبار)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.mock_mode = mock_mode

        # Initialize rate limiter
        # تهيئة محدد المعدل
        self.rate_limiter = RateLimiter(rate=rate_limit, per=rate_limit_period)

        # HTTP client will be created in context manager
        # سيتم إنشاء عميل HTTP في مدير السياق
        self._client: Optional[httpx.AsyncClient] = None

        logger.info(
            "globalgap_client_initialized",
            base_url=base_url,
            mock_mode=mock_mode,
            rate_limit=f"{rate_limit}/{rate_limit_period}s",
        )

    @asynccontextmanager
    async def _get_client(self):
        """
        Get or create HTTP client
        الحصول على عميل HTTP أو إنشاؤه

        Context manager for HTTP client lifecycle.
        مدير السياق لدورة حياة عميل HTTP.
        """
        if self._client is None:
            headers = {
                "User-Agent": "SAHOOL-Platform/1.0",
                "Accept": "application/json",
            }
            if self.api_key and not self.mock_mode:
                headers["Authorization"] = f"Bearer {self.api_key}"

            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=headers,
                follow_redirects=True,
            )

        try:
            yield self._client
        finally:
            pass  # Keep client alive for reuse

    async def close(self):
        """
        Close HTTP client and cleanup resources
        إغلاق عميل HTTP وتنظيف الموارد
        """
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("globalgap_client_closed")

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    def _validate_ggn(self, ggn: str) -> None:
        """
        Validate GGN format
        التحقق من صحة تنسيق GGN

        GGN should be 13 digits starting with 4.
        يجب أن يكون GGN 13 رقماً يبدأ بـ 4.

        Args:
            ggn: GlobalGAP Number

        Raises:
            InvalidGGN: If GGN format is invalid
        """
        if not ggn:
            raise InvalidGGN(ggn)

        # Remove any spaces or hyphens
        # إزالة أي مسافات أو شرطات
        clean_ggn = ggn.replace(" ", "").replace("-", "")

        # Check if it's 13 digits and starts with 4
        # التحقق من أنه 13 رقماً ويبدأ بـ 4
        if (
            not clean_ggn.isdigit()
            or len(clean_ggn) != 13
            or not clean_ggn.startswith("4")
        ):
            raise InvalidGGN(ggn)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPStatusError),
    )
    async def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic
        إجراء طلب HTTP مع منطق إعادة المحاولة

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional arguments for httpx

        Returns:
            Response data as dictionary

        Raises:
            GlobalGAPAPIError: On API errors
        """
        # Apply rate limiting
        # تطبيق تحديد المعدل
        await self.rate_limiter.acquire()

        try:
            async with self._get_client() as client:
                response = await client.request(method, endpoint, **kwargs)

                # Handle rate limiting
                # معالجة تحديد المعدل
                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    raise RateLimitExceeded(
                        retry_after=int(retry_after) if retry_after else None
                    )

                # Handle authentication errors
                # معالجة أخطاء المصادقة
                if response.status_code == 401:
                    raise AuthenticationError()

                response.raise_for_status()
                return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(
                "globalgap_api_http_error",
                status_code=e.response.status_code,
                endpoint=endpoint,
                error=str(e),
            )
            raise GlobalGAPAPIError(
                message=f"HTTP error {e.response.status_code}: {str(e)}",
                message_ar=f"خطأ HTTP {e.response.status_code}: {str(e)}",
                status_code=e.response.status_code,
            )

        except httpx.RequestError as e:
            logger.error(
                "globalgap_api_request_error",
                endpoint=endpoint,
                error=str(e),
            )
            raise GlobalGAPAPIError(
                message=f"Request error: {str(e)}",
                message_ar=f"خطأ في الطلب: {str(e)}",
            )

    def _get_mock_certificate(self, ggn: str) -> CertificateInfo:
        """
        Generate mock certificate data for testing
        إنشاء بيانات شهادة وهمية للاختبار

        Args:
            ggn: GlobalGAP Number

        Returns:
            Mock certificate information
        """
        logger.info("globalgap_mock_certificate", ggn=ggn)

        # Generate mock data based on GGN
        # إنشاء بيانات وهمية بناءً على GGN
        valid_from = datetime(2024, 1, 1)
        valid_to = datetime(2025, 12, 31)

        return CertificateInfo(
            ggn=ggn,
            status=CertificateStatus.VALID,
            valid_from=valid_from,
            valid_to=valid_to,
            scope="IFA - Integrated Farm Assurance",
            cb_name="Mock Certification Body",
            product_categories=["Fruits and Vegetables", "Crops"],
            producer_name="Mock Farm Ltd.",
            country="SA",
            sub_scopes=["Crops Base", "Fruit and Vegetables"],
            raw_data={"mock": True},
        )

    def _get_mock_producers(self, query: str) -> List[Producer]:
        """
        Generate mock producer data for testing
        إنشاء بيانات منتج وهمية للاختبار

        Args:
            query: Search query

        Returns:
            List of mock producers
        """
        logger.info("globalgap_mock_producers", query=query)

        return [
            Producer(
                name=f"Mock Producer 1 - {query}",
                country="SA",
                products=["Dates", "Vegetables"],
                certification_status=CertificateStatus.VALID,
                ggn="4063061891234",
                location="Riyadh Region",
                certification_date=datetime(2024, 1, 15),
                raw_data={"mock": True},
            ),
            Producer(
                name=f"Mock Producer 2 - {query}",
                country="AE",
                products=["Fruits", "Herbs"],
                certification_status=CertificateStatus.VALID,
                ggn="4063061891235",
                location="Abu Dhabi",
                certification_date=datetime(2024, 3, 20),
                raw_data={"mock": True},
            ),
        ]

    async def verify_certificate(self, ggn: str) -> CertificateInfo:
        """
        Verify GlobalGAP certificate by GGN
        التحقق من شهادة GlobalGAP بواسطة GGN

        Args:
            ggn: GlobalGAP Number (13 digits starting with 4)

        Returns:
            Certificate information

        Raises:
            InvalidGGN: If GGN format is invalid
            CertificateNotFound: If certificate doesn't exist
            GlobalGAPAPIError: On API errors

        Example:
            cert = await client.verify_certificate("4063061891234")
            if cert.is_valid():
                print(f"Valid until: {cert.valid_to}")
        """
        self._validate_ggn(ggn)

        logger.info("globalgap_verify_certificate", ggn=ggn)

        # Return mock data if in mock mode
        # إرجاع بيانات وهمية إذا كان في وضع المحاكاة
        if self.mock_mode:
            return self._get_mock_certificate(ggn)

        # Make API request
        # إجراء طلب واجهة البرمجة
        try:
            data = await self._make_request("GET", f"/certificates/{ggn}")

            # Parse response
            # تحليل الاستجابة
            if not data:
                raise CertificateNotFound(ggn)

            cert_info = CertificateInfo(
                ggn=data.get("ggn", ggn),
                status=CertificateStatus(data.get("status", "valid").lower()),
                valid_from=datetime.fromisoformat(data.get("valid_from")),
                valid_to=datetime.fromisoformat(data.get("valid_to")),
                scope=data.get("scope", ""),
                cb_name=data.get("certification_body", ""),
                product_categories=data.get("product_categories", []),
                producer_name=data.get("producer_name"),
                country=data.get("country"),
                sub_scopes=data.get("sub_scopes", []),
                raw_data=data,
            )

            logger.info(
                "globalgap_certificate_verified",
                ggn=ggn,
                status=cert_info.status.value,
                is_valid=cert_info.is_valid(),
            )

            return cert_info

        except KeyError as e:
            logger.error(
                "globalgap_certificate_parse_error",
                ggn=ggn,
                error=str(e),
            )
            raise GlobalGAPAPIError(
                message=f"Failed to parse certificate data: {str(e)}",
                message_ar=f"فشل تحليل بيانات الشهادة: {str(e)}",
            )

    async def get_certificate_status(self, ggn: str) -> CertificateStatus:
        """
        Get certificate status only (lightweight operation)
        الحصول على حالة الشهادة فقط (عملية خفيفة)

        Args:
            ggn: GlobalGAP Number

        Returns:
            Certificate status

        Raises:
            InvalidGGN: If GGN format is invalid
            CertificateNotFound: If certificate doesn't exist
            GlobalGAPAPIError: On API errors

        Example:
            status = await client.get_certificate_status("4063061891234")
            if status == CertificateStatus.VALID:
                print("Certificate is valid")
        """
        self._validate_ggn(ggn)

        logger.info("globalgap_get_certificate_status", ggn=ggn)

        # Return mock data if in mock mode
        # إرجاع بيانات وهمية إذا كان في وضع المحاكاة
        if self.mock_mode:
            return CertificateStatus.VALID

        # Make API request
        # إجراء طلب واجهة البرمجة
        try:
            data = await self._make_request("GET", f"/certificates/{ggn}/status")

            if not data:
                raise CertificateNotFound(ggn)

            status = CertificateStatus(data.get("status", "valid").lower())

            logger.info(
                "globalgap_certificate_status_retrieved",
                ggn=ggn,
                status=status.value,
            )

            return status

        except ValueError as e:
            logger.error(
                "globalgap_invalid_status",
                ggn=ggn,
                error=str(e),
            )
            raise GlobalGAPAPIError(
                message=f"Invalid certificate status: {str(e)}",
                message_ar=f"حالة شهادة غير صالحة: {str(e)}",
            )

    async def search_producers(
        self,
        query: str,
        country: Optional[str] = None,
        product_category: Optional[str] = None,
        limit: int = 20,
    ) -> List[Producer]:
        """
        Search for certified producers
        البحث عن المنتجين المعتمدين

        Args:
            query: Search query (name, location, etc.)
            country: Filter by country code (ISO 2-letter)
            product_category: Filter by product category
            limit: Maximum number of results

        Returns:
            List of matching producers

        Raises:
            GlobalGAPAPIError: On API errors

        Example:
            producers = await client.search_producers(
                query="organic farm",
                country="SA",
                product_category="vegetables"
            )
            for producer in producers:
                print(f"{producer.name} - {producer.country}")
        """
        logger.info(
            "globalgap_search_producers",
            query=query,
            country=country,
            product_category=product_category,
            limit=limit,
        )

        # Return mock data if in mock mode
        # إرجاع بيانات وهمية إذا كان في وضع المحاكاة
        if self.mock_mode:
            return self._get_mock_producers(query)

        # Build query parameters
        # بناء معاملات الاستعلام
        params = {
            "q": query,
            "limit": limit,
        }

        if country:
            params["country"] = country

        if product_category:
            params["product_category"] = product_category

        # Make API request
        # إجراء طلب واجهة البرمجة
        try:
            data = await self._make_request("GET", "/producers/search", params=params)

            producers = []
            for item in data.get("results", []):
                producer = Producer(
                    name=item.get("name", ""),
                    country=item.get("country", ""),
                    products=item.get("products", []),
                    certification_status=CertificateStatus(
                        item.get("certification_status", "valid").lower()
                    ),
                    ggn=item.get("ggn"),
                    location=item.get("location"),
                    certification_date=(
                        datetime.fromisoformat(item.get("certification_date"))
                        if item.get("certification_date")
                        else None
                    ),
                    raw_data=item,
                )
                producers.append(producer)

            logger.info(
                "globalgap_producers_found",
                query=query,
                count=len(producers),
            )

            return producers

        except (KeyError, ValueError) as e:
            logger.error(
                "globalgap_producers_parse_error",
                query=query,
                error=str(e),
            )
            raise GlobalGAPAPIError(
                message=f"Failed to parse producer data: {str(e)}",
                message_ar=f"فشل تحليل بيانات المنتج: {str(e)}",
            )

    async def batch_verify_certificates(
        self, ggns: List[str]
    ) -> Dict[str, CertificateInfo]:
        """
        Verify multiple certificates concurrently
        التحقق من شهادات متعددة بشكل متزامن

        Args:
            ggns: List of GlobalGAP Numbers

        Returns:
            Dictionary mapping GGN to certificate info

        Example:
            results = await client.batch_verify_certificates([
                "4063061891234",
                "4063061891235",
            ])
            for ggn, cert in results.items():
                print(f"{ggn}: {cert.status}")
        """
        logger.info("globalgap_batch_verify", count=len(ggns))

        # Create concurrent tasks
        # إنشاء مهام متزامنة
        tasks = {ggn: self.verify_certificate(ggn) for ggn in ggns}

        # Execute all tasks
        # تنفيذ جميع المهام
        results = {}
        for ggn, task in tasks.items():
            try:
                cert_info = await task
                results[ggn] = cert_info
            except Exception as e:
                logger.error(
                    "globalgap_batch_verify_failed",
                    ggn=ggn,
                    error=str(e),
                )
                # Continue with other certificates
                # الاستمرار مع الشهادات الأخرى

        logger.info(
            "globalgap_batch_verify_completed",
            requested=len(ggns),
            successful=len(results),
        )

        return results
