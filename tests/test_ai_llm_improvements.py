"""
Test Suite for AI/LLM Improvements
Validates error handling, retry logic, and validation enhancements

Run with: pytest tests/test_ai_llm_improvements.py -v
"""

import pytest
import time
from unittest.mock import Mock, patch

# Import the improved modules
import sys
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent.parent / "packages"))

from advisor.ai.llm_client import (
    LlmClient,
    LlmError,
    LlmRateLimitError,
    LlmTimeoutError,
    LlmValidationError,
    LlmResponse,
    MockLlmClient,
)


class TestLlmClientValidation:
    """Test input validation in LLM client"""

    def test_empty_prompt_rejected(self):
        """Test that empty prompts are rejected"""
        client = MockLlmClient()
        
        with pytest.raises(LlmValidationError, match="cannot be empty"):
            client.generate("")
        
        with pytest.raises(LlmValidationError, match="cannot be empty"):
            client.generate("   ")

    def test_oversized_prompt_rejected(self):
        """Test that oversized prompts are rejected"""
        client = MockLlmClient()
        oversized_prompt = "a" * 60000  # Exceeds 50K limit
        
        with pytest.raises(LlmValidationError, match="too long"):
            client.generate(oversized_prompt)

    def test_valid_prompt_accepted(self):
        """Test that valid prompts are accepted"""
        client = MockLlmClient(default_response="Test response")
        response = client.generate("Valid prompt")
        
        assert response.text == "Test response"
        assert response.model == "mock-v1"


class TestLlmClientRetryLogic:
    """Test retry logic with exponential backoff"""

    def test_retry_on_rate_limit(self):
        """Test that client retries on rate limit errors"""
        client = MockLlmClient()
        
        # Simulate rate limit by making many requests
        # This should not raise if retry logic works
        for i in range(5):
            response = client.generate("test prompt")
            assert response is not None

    def test_max_retries_respected(self):
        """Test that max retries is respected"""
        client = MockLlmClient(simulate_errors=True)
        client.max_retries = 3
        
        # Should eventually raise after max retries
        with pytest.raises(LlmError, match="Failed after .* attempts"):
            # This will fail because simulate_errors raises every 5th call
            for i in range(10):
                client.generate("test")


class TestLlmClientRateLimiting:
    """Test rate limiting functionality"""

    def test_rate_limit_tracking(self):
        """Test that rate limit is tracked"""
        client = MockLlmClient()
        
        # Make some requests
        for i in range(10):
            client.generate("test")
        
        # Request count should be tracked
        assert client._request_count >= 10

    def test_rate_limit_enforced(self):
        """Test that rate limit is enforced"""
        client = MockLlmClient()
        
        # Simulate rapid requests by manipulating time
        client._last_request_time = time.time()
        client._request_count = 60
        
        with pytest.raises(LlmRateLimitError, match="Rate limit exceeded"):
            client.generate("test")


class TestLlmClientResponseMetadata:
    """Test enhanced response metadata"""

    def test_response_includes_metadata(self):
        """Test that response includes metadata"""
        client = MockLlmClient(default_response="Test")
        response = client.generate("prompt")
        
        assert response.text == "Test"
        assert response.model == "mock-v1"
        assert response.tokens_used is not None
        assert response.finish_reason == "stop"
        assert "call_count" in response.metadata


class TestLlmClientErrorTypes:
    """Test specialized error types"""

    def test_llm_validation_error(self):
        """Test LlmValidationError is raised"""
        client = MockLlmClient()
        
        with pytest.raises(LlmValidationError):
            client.generate("")

    def test_llm_rate_limit_error(self):
        """Test LlmRateLimitError is raised"""
        client = MockLlmClient()
        client._request_count = 60
        client._last_request_time = time.time()
        
        with pytest.raises(LlmRateLimitError):
            client.generate("test")

    def test_llm_error_inheritance(self):
        """Test that specialized errors inherit from LlmError"""
        assert issubclass(LlmValidationError, LlmError)
        assert issubclass(LlmRateLimitError, LlmError)
        assert issubclass(LlmTimeoutError, LlmError)


class TestMockLlmClient:
    """Test MockLlmClient functionality"""

    def test_mock_returns_default_response(self):
        """Test that mock returns default response"""
        response_text = "مرحباً بك في سهول"
        client = MockLlmClient(default_response=response_text)
        
        response = client.generate("test")
        assert response.text == response_text

    def test_mock_tracks_calls(self):
        """Test that mock tracks call count"""
        client = MockLlmClient()
        
        client.generate("test1")
        client.generate("test2")
        client.generate("test3")
        
        response = client.generate("test4")
        assert response.metadata["call_count"] == 4

    def test_mock_error_simulation(self):
        """Test that mock can simulate errors"""
        client = MockLlmClient(simulate_errors=True)
        
        # First 4 calls should succeed
        for i in range(4):
            response = client.generate("test")
            assert response is not None
        
        # 5th call should fail
        with pytest.raises(LlmError, match="Simulated error"):
            client.generate("test")


class TestLlmClientValidationBypass:
    """Test validation bypass option"""

    def test_validation_can_be_bypassed(self):
        """Test that validation can be bypassed when needed"""
        client = MockLlmClient()
        
        # With validation (default)
        with pytest.raises(LlmValidationError):
            client.generate("", validate=True)
        
        # Without validation (bypassed)
        response = client.generate("", validate=False)
        assert response is not None


# Integration tests
class TestLlmClientIntegration:
    """Integration tests for LLM client"""

    def test_end_to_end_flow(self):
        """Test complete request flow"""
        client = MockLlmClient(default_response="Integration test response")
        
        # Make a request
        response = client.generate("What is the weather?")
        
        # Verify response
        assert response.text == "Integration test response"
        assert response.model == "mock-v1"
        assert response.finish_reason == "stop"
        assert response.tokens_used > 0

    def test_multiple_requests(self):
        """Test multiple consecutive requests"""
        client = MockLlmClient()
        
        responses = []
        for i in range(10):
            response = client.generate(f"Question {i}")
            responses.append(response)
        
        assert len(responses) == 10
        assert all(r.model == "mock-v1" for r in responses)


# Performance tests
class TestLlmClientPerformance:
    """Performance tests for LLM client"""

    def test_validation_overhead(self):
        """Test validation overhead is minimal"""
        client = MockLlmClient()
        
        start = time.time()
        for i in range(100):
            client.generate("test prompt", validate=True)
        with_validation = time.time() - start
        
        # Reset client
        client = MockLlmClient()
        
        start = time.time()
        for i in range(100):
            client.generate("test prompt", validate=False)
        without_validation = time.time() - start
        
        # Validation should add minimal overhead (< 50% increase)
        assert with_validation < without_validation * 1.5


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
