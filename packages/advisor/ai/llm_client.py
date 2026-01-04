"""
SAHOOL LLM Client Interface
Sprint 9: Abstract LLM interface to prevent vendor lock-in

This is an interface-only module. Concrete implementations (OpenAI, Claude, etc.)
will be added as adapters without modifying this contract.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class LlmResponse:
    """Response from LLM generation"""

    text: str


class LlmClient(ABC):
    """Abstract LLM client interface.

    Implementations should handle:
    - Rate limiting
    - Retry logic
    - Token counting
    - Error handling
    """

    @abstractmethod
    def generate(self, prompt: str) -> LlmResponse:
        """Generate a response from the LLM.

        Args:
            prompt: The formatted prompt to send to the LLM

        Returns:
            LlmResponse with generated text
        """
        pass


class MockLlmClient(LlmClient):
    """Mock LLM client for testing.

    Returns a predefined response or echo of the prompt.
    """

    def __init__(self, default_response: str = "مرحبًا، هذه إجابة تجريبية."):
        self._default_response = default_response

    def generate(self, prompt: str) -> LlmResponse:
        return LlmResponse(text=self._default_response)
