# ═══════════════════════════════════════════════════════════════════════════════
# UltraRAG Generator - LLM-based Response Generation
# توليد الاستجابات باستخدام نماذج اللغة الكبيرة
# ═══════════════════════════════════════════════════════════════════════════════

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import structlog

from .models import (
    GenerationMode,
    GenerationResult,
)

logger = structlog.get_logger(__name__)


@dataclass
class GeneratorConfig:
    """Configuration for generation | تكوين التوليد"""

    model: str = "codellama:7b"
    provider: str = "ollama"
    max_tokens: int = 1024
    temperature: float = 0.1
    top_p: float = 0.9
    mode: GenerationMode = GenerationMode.STANDARD
    system_prompt: str = ""
    system_prompt_ar: str = ""
    include_sources: bool = True
    bilingual_output: bool = False


class Generator(ABC):
    """Abstract base class for generators | فئة أساسية مجردة للمولدات"""

    @abstractmethod
    async def generate(
        self,
        query: str,
        context: str,
        mode: GenerationMode = GenerationMode.STANDARD,
        language: str = "en",
        max_tokens: int = 1024,
    ) -> GenerationResult:
        """Generate a response based on query and context"""
        pass


class OllamaGenerator(Generator):
    """Generator using local Ollama LLM | مولد يستخدم Ollama محلياً"""

    def __init__(
        self,
        llm_client: Any,
        config: GeneratorConfig | None = None,
    ):
        self.llm_client = llm_client
        self.config = config or GeneratorConfig()

        # Mode-specific prompts
        self._mode_prompts = {
            GenerationMode.STANDARD: self._standard_prompt,
            GenerationMode.CHAIN_OF_THOUGHT: self._cot_prompt,
            GenerationMode.SELF_REFLECTIVE: self._self_reflective_prompt,
            GenerationMode.ITERATIVE: self._iterative_prompt,
        }

    async def generate(
        self,
        query: str,
        context: str,
        mode: GenerationMode = GenerationMode.STANDARD,
        language: str = "en",
        max_tokens: int = 1024,
    ) -> GenerationResult:
        """Generate response using Ollama"""
        start_time = time.time()

        try:
            # Get prompt generator for mode
            prompt_fn = self._mode_prompts.get(mode, self._standard_prompt)
            prompt = prompt_fn(query, context, language)

            # Generate response
            response = await self.llm_client.generate(
                prompt=prompt,
                model=self.config.model,
                max_tokens=max_tokens,
                temperature=self.config.temperature,
            )

            # Parse response based on mode
            answer, reasoning, confidence = self._parse_response(response, mode)

            elapsed = (time.time() - start_time) * 1000

            # Generate Arabic translation if needed
            answer_ar = None
            if self.config.bilingual_output and language == "en":
                answer_ar = await self._translate_to_arabic(answer)

            result = GenerationResult(
                answer=answer,
                answer_ar=answer_ar,
                confidence=confidence,
                reasoning=reasoning,
                mode=mode,
                processing_time_ms=elapsed,
            )

            logger.info(
                "generation_complete",
                mode=mode.value,
                language=language,
                answer_length=len(answer),
                elapsed_ms=elapsed,
            )

            return result

        except Exception as e:
            logger.error("generation_error", error=str(e))
            return GenerationResult(
                answer=f"Error: {str(e)}",
                confidence=0.0,
                mode=mode,
                processing_time_ms=(time.time() - start_time) * 1000,
            )

    def _standard_prompt(self, query: str, context: str, language: str) -> str:
        """Standard RAG prompt"""
        if language == "ar":
            return f"""أنت مساعد زراعي متخصص. استخدم السياق التالي للإجابة على السؤال.
إذا لم تجد المعلومة في السياق، قل ذلك بوضوح.

السياق:
{context}

السؤال: {query}

الإجابة:"""
        else:
            return f"""You are a specialized agricultural assistant. Use the following context to answer the question.
If the information is not in the context, clearly state that.

Context:
{context}

Question: {query}

Answer:"""

    def _cot_prompt(self, query: str, context: str, language: str) -> str:
        """Chain-of-thought prompt for step-by-step reasoning"""
        if language == "ar":
            return f"""أنت مساعد زراعي متخصص. استخدم التفكير خطوة بخطوة للإجابة.

السياق:
{context}

السؤال: {query}

فكر بصوت عالٍ:
1. ما هي المعلومات الرئيسية في السياق؟
2. كيف ترتبط بالسؤال؟
3. ما هو الاستنتاج المنطقي؟

التفكير:
[اكتب خطوات تفكيرك هنا]

الإجابة النهائية:
[اكتب الإجابة النهائية هنا]"""
        else:
            return f"""You are a specialized agricultural assistant. Use step-by-step reasoning to answer.

Context:
{context}

Question: {query}

Think aloud:
1. What are the key pieces of information in the context?
2. How do they relate to the question?
3. What is the logical conclusion?

Reasoning:
[Write your reasoning steps here]

Final Answer:
[Write your final answer here]"""

    def _self_reflective_prompt(self, query: str, context: str, language: str) -> str:
        """Self-reflective RAG prompt with verification"""
        if language == "ar":
            return f"""أنت مساعد زراعي متخصص. أجب ثم راجع إجابتك.

السياق:
{context}

السؤال: {query}

الإجابة الأولية:
[اكتب إجابتك الأولية]

المراجعة:
- هل الإجابة مدعومة بالسياق؟
- هل هناك معلومات ناقصة؟
- ما مدى ثقتك في الإجابة (0-100%)؟

الإجابة النهائية المعدلة:
[اكتب الإجابة المحسنة]

مستوى الثقة: [رقم من 0 إلى 100]%"""
        else:
            return f"""You are a specialized agricultural assistant. Answer then review your response.

Context:
{context}

Question: {query}

Initial Answer:
[Write your initial answer]

Review:
- Is the answer supported by the context?
- Is there missing information?
- How confident are you in the answer (0-100%)?

Final Refined Answer:
[Write improved answer]

Confidence Level: [number from 0 to 100]%"""

    def _iterative_prompt(self, query: str, context: str, language: str) -> str:
        """Iterative refinement prompt"""
        if language == "ar":
            return f"""أنت مساعد زراعي متخصص. قم ببناء إجابتك بشكل تدريجي.

السياق:
{context}

السؤال: {query}

المحاولة 1 (إجابة موجزة):
[جملة واحدة]

المحاولة 2 (إضافة تفاصيل):
[2-3 جمل]

المحاولة 3 (إجابة شاملة):
[إجابة كاملة مع أمثلة إن وجدت]

الإجابة النهائية:
[أفضل نسخة من الإجابة]"""
        else:
            return f"""You are a specialized agricultural assistant. Build your answer iteratively.

Context:
{context}

Question: {query}

Attempt 1 (brief answer):
[one sentence]

Attempt 2 (add details):
[2-3 sentences]

Attempt 3 (comprehensive):
[full answer with examples if available]

Final Answer:
[best version of the answer]"""

    def _parse_response(
        self,
        response: str,
        mode: GenerationMode,
    ) -> tuple[str, str | None, float]:
        """Parse LLM response based on generation mode"""
        answer = response.strip()
        reasoning = None
        confidence = 0.7  # Default confidence

        if mode == GenerationMode.CHAIN_OF_THOUGHT:
            # Extract reasoning and final answer
            if "Final Answer:" in response:
                parts = response.split("Final Answer:")
                reasoning = parts[0].replace("Reasoning:", "").strip()
                answer = parts[1].strip()
            elif "الإجابة النهائية:" in response:
                parts = response.split("الإجابة النهائية:")
                reasoning = parts[0].replace("التفكير:", "").strip()
                answer = parts[1].strip()

        elif mode == GenerationMode.SELF_REFLECTIVE:
            # Extract confidence and refined answer
            import re

            # Try to extract confidence
            confidence_match = re.search(r"(\d+)\s*%", response)
            if confidence_match:
                confidence = float(confidence_match.group(1)) / 100.0

            # Extract final answer
            if "Final Refined Answer:" in response:
                parts = response.split("Final Refined Answer:")
                answer = parts[1].split("Confidence")[0].strip()
            elif "الإجابة النهائية المعدلة:" in response:
                parts = response.split("الإجابة النهائية المعدلة:")
                answer = parts[1].split("مستوى الثقة")[0].strip()

        elif mode == GenerationMode.ITERATIVE:
            # Extract final answer
            if "Final Answer:" in response:
                parts = response.split("Final Answer:")
                answer = parts[-1].strip()
            elif "الإجابة النهائية:" in response:
                parts = response.split("الإجابة النهائية:")
                answer = parts[-1].strip()

        return answer, reasoning, confidence

    async def _translate_to_arabic(self, text: str) -> str | None:
        """Translate text to Arabic"""
        try:
            prompt = f"""Translate the following English text to Arabic. Only provide the translation, nothing else.

Text: {text}

Arabic translation:"""

            response = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=len(text) * 2,
                temperature=0.1,
            )

            return response.strip()

        except Exception as e:
            logger.warning("translation_error", error=str(e))
            return None


class TemplateGenerator(Generator):
    """Template-based generator for simple responses | مولد قائم على القوالب"""

    def __init__(self, templates: dict[str, str] = None):
        self.templates = templates or {}
        self._default_template = "Based on the available information: {context}\n\nAnswer: {answer}"
        self._default_template_ar = "بناءً على المعلومات المتاحة: {context}\n\nالإجابة: {answer}"

    async def generate(
        self,
        query: str,
        context: str,
        mode: GenerationMode = GenerationMode.STANDARD,
        language: str = "en",
        max_tokens: int = 1024,
    ) -> GenerationResult:
        """Generate using templates"""
        start_time = time.time()

        # Select template
        template_key = f"{mode.value}_{language}"
        template = self.templates.get(template_key)

        if template is None:
            template = self._default_template_ar if language == "ar" else self._default_template

        # Simple extraction from context
        answer = self._extract_answer(context, query)

        # Format response
        formatted = template.format(
            context=context[:500],  # Truncate context
            answer=answer,
            query=query,
        )

        elapsed = (time.time() - start_time) * 1000

        return GenerationResult(
            answer=formatted,
            confidence=0.5,
            mode=mode,
            processing_time_ms=elapsed,
        )

    def _extract_answer(self, context: str, query: str) -> str:
        """Extract relevant text from context"""
        # Simple extraction - return first 200 chars
        if context:
            return context[:200] + "..."
        return "No relevant information found."


class CompositeGenerator(Generator):
    """Generator that combines multiple generators | مولد يجمع بين عدة مولدات"""

    def __init__(self, generators: list[Generator]):
        self.generators = generators

    async def generate(
        self,
        query: str,
        context: str,
        mode: GenerationMode = GenerationMode.STANDARD,
        language: str = "en",
        max_tokens: int = 1024,
    ) -> GenerationResult:
        """Try generators in order until one succeeds"""
        start_time = time.time()
        last_error = None

        for generator in self.generators:
            try:
                result = await generator.generate(
                    query=query,
                    context=context,
                    mode=mode,
                    language=language,
                    max_tokens=max_tokens,
                )

                if result.confidence > 0.3:  # Acceptable confidence
                    return result

            except Exception as e:
                last_error = e
                logger.warning("generator_fallback", error=str(e))
                continue

        # Return error result if all failed
        return GenerationResult(
            answer=f"Generation failed: {last_error}",
            confidence=0.0,
            mode=mode,
            processing_time_ms=(time.time() - start_time) * 1000,
        )


def create_generator(
    config: GeneratorConfig,
    llm_client: Any = None,
) -> Generator:
    """Factory function to create generator | دالة مصنع لإنشاء المولد"""
    if config.provider == "ollama" and llm_client:
        return OllamaGenerator(llm_client, config)
    elif config.provider == "template":
        return TemplateGenerator()
    else:
        # Default to template if no LLM available
        return TemplateGenerator()


# Export classes
__all__ = [
    "Generator",
    "GeneratorConfig",
    "OllamaGenerator",
    "TemplateGenerator",
    "CompositeGenerator",
    "create_generator",
]
