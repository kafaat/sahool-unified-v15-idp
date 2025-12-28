"""
SAHOOL LLM Client Interface
Sprint 9: Abstract LLM interface to prevent vendor lock-in

This is an interface-only module. Concrete implementations (OpenAI, Claude, etc.)
will be added as adapters without modifying this contract.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from enum import Enum


logger = logging.getLogger(__name__)


class LlmError(Exception):
    """Base exception for LLM-related errors"""
    pass


class LlmRateLimitError(LlmError):
    """Raised when rate limit is exceeded"""
    pass


class LlmTimeoutError(LlmError):
    """Raised when LLM request times out"""
    pass


class LlmValidationError(LlmError):
    """Raised when input validation fails"""
    pass


@dataclass(frozen=True)
class LlmResponse:
    """Response from LLM generation"""

    text: str
    model: Optional[str] = None
    tokens_used: Optional[int] = None
    finish_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class LlmClient(ABC):
    """Abstract LLM client interface.

    Implementations should handle:
    - Rate limiting
    - Retry logic
    - Token counting
    - Error handling
    """

    def __init__(
        self,
        max_retries: int = 3,
        timeout: int = 30,
        max_tokens: int = 2000,
    ):
        """Initialize LLM client with safety parameters.
        
        Args:
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
            max_tokens: Maximum tokens in response
        """
        self.max_retries = max_retries
        self.timeout = timeout
        self.max_tokens = max_tokens
        self._request_count = 0
        self._window_start_time = None  # Will be set on first request

    @abstractmethod
    def _generate_impl(self, prompt: str) -> LlmResponse:
        """Internal generation method to be implemented by subclasses.
        
        Args:
            prompt: The formatted prompt to send to the LLM

        Returns:
            LlmResponse with generated text
        """
        pass

    def generate(self, prompt: str, validate: bool = True) -> LlmResponse:
        """Generate a response from the LLM with error handling and retries.

        Args:
            prompt: The formatted prompt to send to the LLM
            validate: Whether to validate input before sending

        Returns:
            LlmResponse with generated text

        Raises:
            LlmValidationError: If input validation fails
            LlmRateLimitError: If rate limit is exceeded
            LlmTimeoutError: If request times out
            LlmError: For other LLM-related errors
        """
        if validate:
            self._validate_prompt(prompt)

        for attempt in range(self.max_retries):
            try:
                # Check rate limit FIRST, before tracking request
                self._check_rate_limit()
                
                # Track request AFTER rate limit check passes
                if self._request_count == 0 and self._window_start_time is None:
                    self._window_start_time = time.time()
                self._request_count += 1
                
                # Call implementation
                logger.info(f"LLM request attempt {attempt + 1}/{self.max_retries}")
                response = self._generate_impl(prompt)
                
                # Validate response
                self._validate_response(response)
                
                return response
                
            except LlmRateLimitError:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Rate limit hit, waiting {wait_time}s before retry")
                    time.sleep(wait_time)
                else:
                    raise
                    
            except LlmTimeoutError:
                if attempt < self.max_retries - 1:
                    logger.warning(f"Timeout on attempt {attempt + 1}, retrying...")
                    time.sleep(1)
                else:
                    raise
                    
            except Exception as e:
                logger.error(f"LLM generation error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                else:
                    raise LlmError(f"Failed after {self.max_retries} attempts") from e

        raise LlmError(f"Failed to generate response after {self.max_retries} attempts")

    def _validate_prompt(self, prompt: str) -> None:
        """Validate prompt before sending to LLM.
        
        Args:
            prompt: Prompt to validate
            
        Raises:
            LlmValidationError: If validation fails
        """
        if not prompt or not prompt.strip():
            raise LlmValidationError("Prompt cannot be empty")
            
        if len(prompt) > 50000:  # ~12k tokens
            raise LlmValidationError(
                f"Prompt too long: {len(prompt)} characters (max 50000)"
            )

    def _validate_response(self, response: LlmResponse) -> None:
        """Validate response from LLM.
        
        Args:
            response: Response to validate
            
        Raises:
            LlmValidationError: If validation fails
        """
        if not response.text or not response.text.strip():
            raise LlmValidationError("LLM returned empty response")

    def _check_rate_limit(self) -> None:
        """Check if rate limit would be exceeded.
        
        Raises:
            LlmRateLimitError: If rate limit exceeded
        """
        current_time = time.time()
        
        # Initialize window on first request
        if self._window_start_time is None:
            self._window_start_time = current_time
            return  # First request always passes
        
        time_since_window_start = current_time - self._window_start_time
        
        # Check if we've hit the limit within the current window FIRST
        # Note: _request_count hasn't been incremented yet, so we check >= 60
        # which means we've already made 60 requests
        if self._request_count >= 60:
            # If we're still within the window, raise error
            if time_since_window_start < 60:
                raise LlmRateLimitError(
                    f"Rate limit exceeded: {self._request_count} requests in {time_since_window_start:.1f}s"
                )
            # If window has expired, reset and allow
            self._request_count = 0
            self._window_start_time = current_time


class MockLlmClient(LlmClient):
    """Mock LLM client for testing.

    Returns a predefined response or echo of the prompt.
    """

    def __init__(
        self,
        default_response: str = "مرحبًا، هذه إجابة تجريبية.",
        simulate_errors: bool = False,
    ):
        super().__init__()
        self._default_response = default_response
        self._simulate_errors = simulate_errors
        self._call_count = 0

    def _generate_impl(self, prompt: str) -> LlmResponse:
        """Generate mock response."""
        self._call_count += 1
        
        # Simulate occasional errors for testing
        if self._simulate_errors and self._call_count % 5 == 0:
            raise LlmError("Simulated error for testing")
        
        return LlmResponse(
            text=self._default_response,
            model="mock-v1",
            tokens_used=len(self._default_response.split()),
            finish_reason="stop",
            metadata={"call_count": self._call_count},
        )
