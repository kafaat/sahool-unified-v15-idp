"""
SAHOOL Retry Utilities with Exponential Backoff
أدوات إعادة المحاولة مع التراجع الأسي لمنصة سهول

Provides robust retry mechanisms for handling transient failures
in network calls, database operations, and external service interactions.

Features:
- Exponential backoff with jitter
- Configurable max retries and delays
- Exception filtering (retry only on specific exceptions)
- Async and sync support
- Decorator and context manager patterns

Author: SAHOOL Platform Team
License: MIT
"""

import asyncio
import functools
import logging
import random
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, ParamSpec, TypeVar

logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


@dataclass
class RetryConfig:
    """
    تكوين إعادة المحاولة
    Retry configuration parameters.

    Attributes:
        max_retries: الحد الأقصى للمحاولات - Maximum number of retry attempts
        base_delay: التأخير الأساسي بالثواني - Base delay in seconds
        max_delay: الحد الأقصى للتأخير - Maximum delay cap in seconds
        exponential_base: أساس التراجع الأسي - Base for exponential backoff
        jitter: إضافة عشوائية للتأخير - Add randomness to delay
        retry_exceptions: الاستثناءات القابلة للمحاولة - Exceptions to retry on
    """

    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    exponential_base: float = 2.0
    jitter: bool = True
    retry_exceptions: tuple[type[Exception], ...] = field(
        default_factory=lambda: (
            ConnectionError,
            TimeoutError,
            OSError,
        )
    )


def calculate_delay(
    attempt: int,
    base_delay: float,
    max_delay: float,
    exponential_base: float,
    jitter: bool,
) -> float:
    """
    حساب وقت التأخير للمحاولة
    Calculate delay for retry attempt using exponential backoff.

    Args:
        attempt: رقم المحاولة (0-indexed) - Attempt number (0-indexed)
        base_delay: التأخير الأساسي - Base delay in seconds
        max_delay: الحد الأقصى للتأخير - Maximum delay cap
        exponential_base: أساس الأس - Exponential base
        jitter: إضافة عشوائية - Add randomness

    Returns:
        float: وقت التأخير بالثواني - Delay time in seconds
    """
    # حساب التأخير الأسي: base_delay * (exponential_base ^ attempt)
    # Calculate exponential delay
    delay = base_delay * (exponential_base**attempt)

    # تطبيق الحد الأقصى
    # Apply max cap
    delay = min(delay, max_delay)

    # إضافة العشوائية لتجنب تزامن المحاولات
    # Add jitter to avoid thundering herd
    if jitter:
        delay = delay * (0.5 + random.random())

    return delay


async def async_retry(
    func: Callable[P, T],
    *args: P.args,
    config: RetryConfig | None = None,
    **kwargs: P.kwargs,
) -> T:
    """
    تنفيذ دالة async مع إعادة المحاولة
    Execute async function with retry logic.

    Args:
        func: الدالة المراد تنفيذها - Function to execute
        *args: معاملات الدالة - Function arguments
        config: تكوين إعادة المحاولة - Retry configuration
        **kwargs: معاملات الدالة الإضافية - Additional function arguments

    Returns:
        نتيجة الدالة - Function result

    Raises:
        آخر استثناء - Last exception if all retries fail
    """
    config = config or RetryConfig()
    last_exception: Exception | None = None

    for attempt in range(config.max_retries + 1):
        try:
            return await func(*args, **kwargs)

        except config.retry_exceptions as e:
            last_exception = e

            if attempt < config.max_retries:
                delay = calculate_delay(
                    attempt=attempt,
                    base_delay=config.base_delay,
                    max_delay=config.max_delay,
                    exponential_base=config.exponential_base,
                    jitter=config.jitter,
                )

                logger.warning(
                    f"محاولة {attempt + 1}/{config.max_retries + 1} فشلت: {e}. "
                    f"إعادة المحاولة بعد {delay:.2f}s - "
                    f"Attempt {attempt + 1}/{config.max_retries + 1} failed: {e}. "
                    f"Retrying in {delay:.2f}s"
                )

                await asyncio.sleep(delay)
            else:
                logger.error(
                    f"جميع المحاولات فشلت بعد {config.max_retries + 1} محاولات - "
                    f"All {config.max_retries + 1} attempts failed"
                )

    # إذا وصلنا هنا، فشلت جميع المحاولات
    # If we reach here, all retries failed
    if last_exception:
        raise last_exception

    # This should never happen, but satisfy type checker
    raise RuntimeError("Unexpected retry state")


def sync_retry(
    func: Callable[P, T],
    *args: P.args,
    config: RetryConfig | None = None,
    **kwargs: P.kwargs,
) -> T:
    """
    تنفيذ دالة sync مع إعادة المحاولة
    Execute sync function with retry logic.

    Args:
        func: الدالة المراد تنفيذها - Function to execute
        *args: معاملات الدالة - Function arguments
        config: تكوين إعادة المحاولة - Retry configuration
        **kwargs: معاملات الدالة الإضافية - Additional function arguments

    Returns:
        نتيجة الدالة - Function result

    Raises:
        آخر استثناء - Last exception if all retries fail
    """
    config = config or RetryConfig()
    last_exception: Exception | None = None

    for attempt in range(config.max_retries + 1):
        try:
            return func(*args, **kwargs)

        except config.retry_exceptions as e:
            last_exception = e

            if attempt < config.max_retries:
                delay = calculate_delay(
                    attempt=attempt,
                    base_delay=config.base_delay,
                    max_delay=config.max_delay,
                    exponential_base=config.exponential_base,
                    jitter=config.jitter,
                )

                logger.warning(
                    f"محاولة {attempt + 1}/{config.max_retries + 1} فشلت: {e}. "
                    f"إعادة المحاولة بعد {delay:.2f}s - "
                    f"Attempt {attempt + 1}/{config.max_retries + 1} failed: {e}. "
                    f"Retrying in {delay:.2f}s"
                )

                time.sleep(delay)
            else:
                logger.error(
                    f"جميع المحاولات فشلت بعد {config.max_retries + 1} محاولات - "
                    f"All {config.max_retries + 1} attempts failed"
                )

    if last_exception:
        raise last_exception

    raise RuntimeError("Unexpected retry state")


def retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retry_exceptions: Sequence[type[Exception]] | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    ديكوريتر إعادة المحاولة للدوال
    Retry decorator for functions.

    Supports both sync and async functions.

    Usage:
        @retry(max_retries=3, base_delay=1.0)
        async def fetch_data():
            ...

        @retry(max_retries=5, retry_exceptions=[ConnectionError])
        def connect_to_db():
            ...

    Args:
        max_retries: الحد الأقصى للمحاولات - Maximum retry attempts
        base_delay: التأخير الأساسي - Base delay in seconds
        max_delay: الحد الأقصى للتأخير - Maximum delay
        exponential_base: أساس التراجع الأسي - Exponential base
        jitter: إضافة عشوائية - Add jitter
        retry_exceptions: الاستثناءات للمحاولة - Exceptions to retry

    Returns:
        دالة مغلفة - Wrapped function
    """
    if retry_exceptions is None:
        retry_exceptions = [ConnectionError, TimeoutError, OSError]

    config = RetryConfig(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
        jitter=jitter,
        retry_exceptions=tuple(retry_exceptions),
    )

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            return await async_retry(func, *args, config=config, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            return sync_retry(func, *args, config=config, **kwargs)

        # تحديد ما إذا كانت الدالة async أو sync
        # Determine if function is async or sync
        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore[return-value]
        return sync_wrapper  # type: ignore[return-value]

    return decorator


class RetryContext:
    """
    مدير سياق لإعادة المحاولة
    Context manager for retry operations.

    Usage:
        async with RetryContext(max_retries=3) as ctx:
            for attempt in ctx:
                try:
                    result = await risky_operation()
                    break
                except ConnectionError:
                    ctx.record_failure()
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        self.config = RetryConfig(
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            exponential_base=exponential_base,
            jitter=jitter,
        )
        self._attempt = 0
        self._last_exception: Exception | None = None
        self._success = False

    def __iter__(self):
        return self

    def __next__(self) -> int:
        if self._success or self._attempt > self.config.max_retries:
            raise StopIteration
        current = self._attempt
        self._attempt += 1
        return current

    def record_failure(self, exception: Exception | None = None):
        """تسجيل فشل المحاولة - Record attempt failure"""
        self._last_exception = exception

    def mark_success(self):
        """تسجيل نجاح العملية - Mark operation as successful"""
        self._success = True

    async def wait(self) -> float:
        """
        انتظار قبل المحاولة التالية
        Wait before next attempt.

        Returns:
            float: وقت الانتظار - Wait time in seconds
        """
        delay = calculate_delay(
            attempt=self._attempt - 1,
            base_delay=self.config.base_delay,
            max_delay=self.config.max_delay,
            exponential_base=self.config.exponential_base,
            jitter=self.config.jitter,
        )
        await asyncio.sleep(delay)
        return delay

    @property
    def attempts_remaining(self) -> int:
        """عدد المحاولات المتبقية - Remaining attempts"""
        return max(0, self.config.max_retries - self._attempt + 1)

    @property
    def last_exception(self) -> Exception | None:
        """آخر استثناء - Last recorded exception"""
        return self._last_exception


# تكوينات شائعة مسبقة التعريف
# Pre-defined common configurations
RETRY_FAST = RetryConfig(max_retries=2, base_delay=0.5, max_delay=5.0)
RETRY_STANDARD = RetryConfig(max_retries=3, base_delay=1.0, max_delay=30.0)
RETRY_AGGRESSIVE = RetryConfig(max_retries=5, base_delay=2.0, max_delay=60.0)
RETRY_DATABASE = RetryConfig(
    max_retries=3,
    base_delay=0.5,
    max_delay=10.0,
    retry_exceptions=(ConnectionError, TimeoutError, OSError),
)
RETRY_HTTP = RetryConfig(
    max_retries=3,
    base_delay=1.0,
    max_delay=30.0,
    retry_exceptions=(ConnectionError, TimeoutError, OSError),
)


__all__ = [
    "RetryConfig",
    "calculate_delay",
    "async_retry",
    "sync_retry",
    "retry",
    "RetryContext",
    "RETRY_FAST",
    "RETRY_STANDARD",
    "RETRY_AGGRESSIVE",
    "RETRY_DATABASE",
    "RETRY_HTTP",
]
