"""
Ollama LLM Integration for Code Fix Agent
==========================================
تكامل Ollama للوكيل إصلاح الكود

Integrates Ollama with DeepSeek-Coder for intelligent code analysis and fixes.
"""

import json
from typing import Any

import httpx
import structlog

logger = structlog.get_logger(__name__)


class OllamaClient:
    """Client for Ollama API with DeepSeek-Coder"""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "deepseek-coder:latest",
        timeout: float = 120.0,
    ):
        """
        Initialize Ollama client

        Args:
            base_url: Ollama API base URL
            model: Model name (default: deepseek-coder:latest)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(timeout=timeout)

    async def generate(
        self,
        prompt: str,
        system: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 4000,
    ) -> dict[str, Any]:
        """
        Generate completion using Ollama

        Args:
            prompt: User prompt
            system: System prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Response dict with 'response' and 'metadata'
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            }

            if system:
                payload["system"] = system

            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload,
            )
            response.raise_for_status()

            result = response.json()
            return {
                "response": result.get("response", ""),
                "metadata": {
                    "model": result.get("model"),
                    "total_duration": result.get("total_duration"),
                    "load_duration": result.get("load_duration"),
                    "prompt_eval_count": result.get("prompt_eval_count"),
                    "eval_count": result.get("eval_count"),
                },
            }

        except Exception as e:
            logger.error("ollama_generate_failed", error=str(e))
            raise

    async def analyze_code(self, code: str, language: str) -> dict[str, Any]:
        """
        Analyze code for issues using DeepSeek-Coder

        Args:
            code: Code to analyze
            language: Programming language

        Returns:
            Analysis result with issues found
        """
        system_prompt = """You are an expert code analyzer. Analyze the provided code and identify:
1. Syntax errors
2. Logic errors
3. Security vulnerabilities
4. Performance issues
5. Style violations
6. Type errors
7. Import errors

Return your analysis as a JSON object with this structure:
{
  "issues": [
    {
      "type": "syntax_error|logic_error|security|performance|style|type_error|import_error",
      "severity": "critical|high|medium|low|info",
      "line": <line_number>,
      "column": <column_number>,
      "message": "Description of the issue",
      "suggestion": "How to fix it"
    }
  ],
  "summary": "Overall code quality assessment"
}

Be precise and actionable in your suggestions."""

        user_prompt = f"""Analyze this {language} code:

```{language}
{code}
```

Provide a detailed analysis in JSON format."""

        result = await self.generate(user_prompt, system=system_prompt, temperature=0.1)

        try:
            # Extract JSON from response
            response_text = result["response"]
            # Try to find JSON in the response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                analysis = json.loads(json_str)
                return analysis
            else:
                logger.warning("no_json_in_response", response=response_text[:200])
                return {"issues": [], "summary": "Could not parse analysis"}

        except json.JSONDecodeError as e:
            logger.error("json_parse_error", error=str(e), response=result["response"][:200])
            return {"issues": [], "summary": "JSON parse error"}

    async def fix_code(
        self,
        code: str,
        errors: list[dict[str, Any]],
        language: str,
        strategy: str = "minimal",
    ) -> dict[str, Any]:
        """
        Generate code fix using DeepSeek-Coder

        Args:
            code: Original code with errors
            errors: List of errors to fix
            language: Programming language
            strategy: Fix strategy (minimal, comprehensive, refactor)

        Returns:
            Fixed code and explanation
        """
        strategy_instructions = {
            "minimal": "Make the minimum changes necessary to fix the errors. Preserve the original code structure and style.",
            "comprehensive": "Fix the errors and improve code quality, readability, and best practices.",
            "refactor": "Fix the errors and refactor the code for better design, maintainability, and performance.",
        }

        system_prompt = f"""You are an expert code fixer. Fix the provided code according to the {strategy} strategy.

Strategy: {strategy_instructions.get(strategy, strategy_instructions['minimal'])}

Return your fix as a JSON object with this structure:
{{
  "fixed_code": "The complete fixed code",
  "changes": [
    {{
      "line": <line_number>,
      "type": "added|removed|modified",
      "description": "What was changed"
    }}
  ],
  "explanation": "Brief explanation of the fixes applied",
  "confidence": <0.0-1.0>,
  "breaking_changes": <true|false>
}}

IMPORTANT: Return ONLY valid JSON, no markdown formatting."""

        errors_desc = "\n".join(
            [
                f"- Line {e.get('line', '?')}: {e.get('type', 'Error')}: {e.get('message', 'Unknown error')}"
                for e in errors
            ]
        )

        user_prompt = f"""Fix this {language} code:

```{language}
{code}
```

Errors to fix:
{errors_desc}

Provide the fixed code in JSON format."""

        result = await self.generate(user_prompt, system=system_prompt, temperature=0.1)

        try:
            response_text = result["response"]
            # Extract JSON
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                fix_result = json.loads(json_str)
                return fix_result
            else:
                logger.warning("no_json_in_fix_response")
                return {
                    "fixed_code": code,
                    "changes": [],
                    "explanation": "Could not generate fix",
                    "confidence": 0.0,
                    "breaking_changes": False,
                }

        except json.JSONDecodeError as e:
            logger.error("fix_json_parse_error", error=str(e))
            return {
                "fixed_code": code,
                "changes": [],
                "explanation": f"JSON parse error: {e}",
                "confidence": 0.0,
                "breaking_changes": False,
            }

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
