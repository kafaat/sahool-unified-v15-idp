# ═══════════════════════════════════════════════════════════════════════════════
# UltraRAG Workflow Engine - YAML-based Low-Code Workflows
# محرك سير العمل - تكوين منخفض الكود بـ YAML
# ═══════════════════════════════════════════════════════════════════════════════

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import structlog
import yaml

from .models import (
    RAGRequest,
    WorkflowConfig,
    WorkflowStep,
)
from ..knowledge.corrective_retrieval import (
    CorrectiveRetrievalEngine,
    CRAGResult,
    RetrievalAction,
)

logger = structlog.get_logger(__name__)


@dataclass
class WorkflowExecutionContext:
    """Context for workflow execution | سياق تنفيذ سير العمل"""

    workflow_id: str
    variables: dict[str, Any] = field(default_factory=dict)
    step_results: dict[str, Any] = field(default_factory=dict)
    current_step: str | None = None
    execution_path: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    start_time: float = 0.0


@dataclass
class StepExecutionResult:
    """Result from step execution | نتيجة تنفيذ الخطوة"""

    step_id: str
    success: bool
    output: Any = None
    error: str | None = None
    execution_time_ms: float = 0.0
    next_step: str | None = None


class WorkflowEngine:
    """
    YAML-based workflow engine for RAG pipelines
    محرك سير العمل المبني على YAML لخطوط أنابيب RAG
    """

    def __init__(self, rag_pipeline: Any = None):
        self.rag_pipeline = rag_pipeline
        self._workflows: dict[str, WorkflowConfig] = {}
        self._step_handlers: dict[str, Callable] = {}
        self._condition_evaluators: dict[str, Callable] = {}

        # Register built-in step handlers
        self._register_builtin_handlers()

    def _register_builtin_handlers(self):
        """Register built-in step handlers"""
        self._step_handlers = {
            "retrieve": self._handle_retrieve,
            "rerank": self._handle_rerank,
            "generate": self._handle_generate,
            "condition": self._handle_condition,
            "loop": self._handle_loop,
            "transform": self._handle_transform,
            "filter": self._handle_filter,
            "parallel": self._handle_parallel,
            "aggregate": self._handle_aggregate,
            "call_rag": self._handle_call_rag,
            "crag": self._handle_crag,
        }

        # Register built-in condition evaluators
        self._condition_evaluators = {
            "has_results": lambda ctx, params: len(ctx.variables.get("results", [])) > 0,
            "confidence_above": lambda ctx, params: ctx.variables.get("confidence", 0) > params.get("threshold", 0.5),
            "result_count_above": lambda ctx, params: len(ctx.variables.get("results", [])) > params.get("count", 0),
            "language_is": lambda ctx, params: ctx.variables.get("language") == params.get("lang"),
            "crag_action_is": lambda ctx, params: (
                ctx.variables.get("crag_action", "") == params.get("action", "correct")
            ),
            "needs_fallback": lambda ctx, params: ctx.variables.get("crag_fallback_used", False),
            "relevance_above": lambda ctx, params: (
                ctx.variables.get("crag_overall_score", 0) > params.get("threshold", 0.5)
            ),
        }

    def register_workflow(self, config: WorkflowConfig):
        """Register a workflow configuration"""
        self._workflows[config.id] = config
        logger.info("workflow_registered", workflow_id=config.id, name=config.name)

    def register_step_handler(self, step_type: str, handler: Callable):
        """Register a custom step handler"""
        self._step_handlers[step_type] = handler

    def register_condition(self, name: str, evaluator: Callable):
        """Register a custom condition evaluator"""
        self._condition_evaluators[name] = evaluator

    async def execute(
        self,
        workflow_id: str,
        initial_variables: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """
        Execute a workflow by ID
        تنفيذ سير العمل بواسطة المعرف
        """
        if workflow_id not in self._workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")

        workflow = self._workflows[workflow_id]
        return await self.execute_workflow(workflow, initial_variables)

    async def execute_workflow(
        self,
        workflow: WorkflowConfig,
        initial_variables: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """
        Execute a workflow configuration
        تنفيذ تكوين سير العمل
        """
        start_time = time.time()

        # Initialize context
        ctx = WorkflowExecutionContext(
            workflow_id=workflow.id,
            variables={**workflow.variables, **(initial_variables or {})},
            start_time=start_time,
        )

        logger.info(
            "workflow_execution_start",
            workflow_id=workflow.id,
            name=workflow.name,
            num_steps=len(workflow.steps),
        )

        try:
            # Build step map
            step_map = {step.id: step for step in workflow.steps}

            # Start from entry point
            current_step_id = workflow.entry_point

            # Execute steps until we reach the end
            max_iterations = 1000  # Safety limit
            iterations = 0

            while current_step_id and iterations < max_iterations:
                iterations += 1

                if current_step_id not in step_map:
                    raise ValueError(f"Step not found: {current_step_id}")

                step = step_map[current_step_id]
                ctx.current_step = current_step_id
                ctx.execution_path.append(current_step_id)

                # Execute step
                result = await self._execute_step(step, ctx)
                ctx.step_results[current_step_id] = result

                if not result.success:
                    # Handle failure
                    if step.on_failure:
                        current_step_id = step.on_failure
                    else:
                        ctx.errors.append(f"Step {current_step_id} failed: {result.error}")
                        break
                else:
                    # Determine next step
                    current_step_id = result.next_step or step.next_step or step.on_success

            if iterations >= max_iterations:
                ctx.errors.append("Workflow exceeded maximum iterations")

            total_time = (time.time() - start_time) * 1000

            logger.info(
                "workflow_execution_complete",
                workflow_id=workflow.id,
                steps_executed=len(ctx.execution_path),
                total_time_ms=total_time,
                success=len(ctx.errors) == 0,
            )

            return {
                "workflow_id": workflow.id,
                "success": len(ctx.errors) == 0,
                "variables": ctx.variables,
                "step_results": ctx.step_results,
                "execution_path": ctx.execution_path,
                "errors": ctx.errors,
                "total_time_ms": total_time,
            }

        except Exception as e:
            logger.error("workflow_execution_error", workflow_id=workflow.id, error=str(e))
            return {
                "workflow_id": workflow.id,
                "success": False,
                "variables": ctx.variables,
                "step_results": ctx.step_results,
                "execution_path": ctx.execution_path,
                "errors": [str(e)],
                "total_time_ms": (time.time() - start_time) * 1000,
            }

    async def _execute_step(
        self,
        step: WorkflowStep,
        ctx: WorkflowExecutionContext,
    ) -> StepExecutionResult:
        """Execute a single workflow step"""
        start_time = time.time()

        try:
            # Get handler
            handler = self._step_handlers.get(step.type)
            if handler is None:
                raise ValueError(f"Unknown step type: {step.type}")

            # Check condition if present
            if step.condition:
                if not await self._evaluate_condition(step.condition, ctx):
                    logger.debug("step_skipped_condition", step_id=step.id)
                    return StepExecutionResult(
                        step_id=step.id,
                        success=True,
                        output=None,
                        execution_time_ms=0.0,
                        next_step=step.next_step,  # Skip to next
                    )

            # Execute handler
            output, next_step = await handler(step, ctx)

            elapsed = (time.time() - start_time) * 1000

            logger.debug(
                "step_executed",
                step_id=step.id,
                step_type=step.type,
                elapsed_ms=elapsed,
            )

            return StepExecutionResult(
                step_id=step.id,
                success=True,
                output=output,
                execution_time_ms=elapsed,
                next_step=next_step,
            )

        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            logger.error("step_execution_error", step_id=step.id, error=str(e))

            return StepExecutionResult(
                step_id=step.id,
                success=False,
                error=str(e),
                execution_time_ms=elapsed,
            )

    async def _evaluate_condition(
        self,
        condition: str,
        ctx: WorkflowExecutionContext,
    ) -> bool:
        """Evaluate a condition expression"""
        # Parse condition: "evaluator_name:param1=value1,param2=value2"
        parts = condition.split(":", 1)
        evaluator_name = parts[0]
        params = {}

        if len(parts) > 1:
            param_str = parts[1]
            for param in param_str.split(","):
                if "=" in param:
                    key, value = param.split("=", 1)
                    # Try to convert to number
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                    params[key.strip()] = value

        # Get evaluator
        evaluator = self._condition_evaluators.get(evaluator_name)
        if evaluator is None:
            logger.warning("unknown_condition", condition=evaluator_name)
            return True  # Default to true if unknown

        return evaluator(ctx, params)

    # ═══════════════════════════════════════════════════════════════════════════
    # Built-in Step Handlers
    # ═══════════════════════════════════════════════════════════════════════════

    async def _handle_retrieve(
        self,
        step: WorkflowStep,
        ctx: WorkflowExecutionContext,
    ) -> tuple[Any, str | None]:
        """Handle retrieve step"""
        if self.rag_pipeline is None:
            raise ValueError("RAG pipeline not configured")

        query = step.config.get("query") or ctx.variables.get("query", "")
        collection = step.config.get("collection", "default")
        top_k = step.config.get("top_k", 10)

        # Use retriever directly
        from .retriever import RetrievalConfig

        config = RetrievalConfig(
            top_k=top_k,
            collection=collection,
        )

        results = await self.rag_pipeline.retriever.retrieve(query, config)

        # Store in context
        ctx.variables["results"] = results
        ctx.variables["result_count"] = len(results)

        return results, None

    async def _handle_rerank(
        self,
        step: WorkflowStep,
        ctx: WorkflowExecutionContext,
    ) -> tuple[Any, str | None]:
        """Handle rerank step"""
        if self.rag_pipeline is None:
            raise ValueError("RAG pipeline not configured")

        results = ctx.variables.get("results", [])
        query = ctx.variables.get("query", "")
        top_k = step.config.get("top_k", 5)

        from .reranker import RerankConfig

        config = RerankConfig(top_k=top_k)

        rerank_result = await self.rag_pipeline.reranker.rerank(query, results, config)

        ctx.variables["results"] = rerank_result.results
        ctx.variables["rerank_result"] = rerank_result

        return rerank_result, None

    async def _handle_generate(
        self,
        step: WorkflowStep,
        ctx: WorkflowExecutionContext,
    ) -> tuple[Any, str | None]:
        """Handle generate step"""
        query = ctx.variables.get("query", "")
        context = ctx.variables.get("context", "")
        language = step.config.get("language", "en")
        max_tokens = step.config.get("max_tokens", 1024)

        # Build context from results if not provided
        if not context and ctx.variables.get("results"):
            context_parts = []
            for r in ctx.variables["results"][:5]:
                context_parts.append(r.chunk.text)
            context = "\n\n".join(context_parts)

        if self.rag_pipeline and self.rag_pipeline._generator:
            from .models import GenerationMode

            mode = GenerationMode(step.config.get("mode", "standard"))

            result = await self.rag_pipeline._generator.generate(
                query=query,
                context=context,
                mode=mode,
                language=language,
                max_tokens=max_tokens,
            )

            ctx.variables["answer"] = result.answer
            ctx.variables["confidence"] = result.confidence
            ctx.variables["generation_result"] = result

            return result, None

        return None, None

    async def _handle_condition(
        self,
        step: WorkflowStep,
        ctx: WorkflowExecutionContext,
    ) -> tuple[Any, str | None]:
        """Handle conditional branching"""
        condition = step.config.get("condition", "")
        true_branch = step.config.get("true_branch")
        false_branch = step.config.get("false_branch")

        result = await self._evaluate_condition(condition, ctx)

        next_step = true_branch if result else false_branch

        return {"condition_result": result}, next_step

    async def _handle_loop(
        self,
        step: WorkflowStep,
        ctx: WorkflowExecutionContext,
    ) -> tuple[Any, str | None]:
        """Handle loop step"""
        loop_config = step.loop_config or {}
        items = loop_config.get("items") or ctx.variables.get(loop_config.get("items_var", "items"), [])
        loop_config.get("body_step")
        max_iterations = loop_config.get("max_iterations", 100)

        results = []

        for i, item in enumerate(items[:max_iterations]):
            # Set loop variable
            ctx.variables["_loop_item"] = item
            ctx.variables["_loop_index"] = i

            # Execute body step (simplified - would need full step execution)
            results.append({"item": item, "index": i})

        ctx.variables["loop_results"] = results

        return results, None

    async def _handle_transform(
        self,
        step: WorkflowStep,
        ctx: WorkflowExecutionContext,
    ) -> tuple[Any, str | None]:
        """Handle data transformation"""
        input_var = step.config.get("input", "results")
        output_var = step.config.get("output", "transformed")
        transform_type = step.config.get("type", "identity")

        data = ctx.variables.get(input_var, [])

        if transform_type == "extract_text":
            # Extract text from retrieval results
            transformed = [r.chunk.text for r in data if hasattr(r, "chunk")]
        elif transform_type == "join":
            separator = step.config.get("separator", "\n")
            transformed = separator.join(str(item) for item in data)
        elif transform_type == "limit":
            limit = step.config.get("limit", 5)
            transformed = data[:limit]
        elif transform_type == "sort":
            key = step.config.get("key", "score")
            reverse = step.config.get("reverse", True)
            transformed = sorted(data, key=lambda x: getattr(x, key, 0), reverse=reverse)
        else:
            transformed = data

        ctx.variables[output_var] = transformed

        return transformed, None

    async def _handle_filter(
        self,
        step: WorkflowStep,
        ctx: WorkflowExecutionContext,
    ) -> tuple[Any, str | None]:
        """Handle filtering"""
        input_var = step.config.get("input", "results")
        output_var = step.config.get("output", "filtered")
        min_score = step.config.get("min_score", 0.0)

        data = ctx.variables.get(input_var, [])

        # Filter by score
        filtered = [r for r in data if hasattr(r, "score") and r.score >= min_score]

        ctx.variables[output_var] = filtered

        return filtered, None

    async def _handle_parallel(
        self,
        step: WorkflowStep,
        ctx: WorkflowExecutionContext,
    ) -> tuple[Any, str | None]:
        """Handle parallel execution of steps"""
        parallel_steps = step.config.get("steps", [])

        # This is a simplified version - full implementation would execute
        # multiple steps in parallel
        results = {}
        for step_id in parallel_steps:
            results[step_id] = {"status": "parallel_placeholder"}

        return results, None

    async def _handle_aggregate(
        self,
        step: WorkflowStep,
        ctx: WorkflowExecutionContext,
    ) -> tuple[Any, str | None]:
        """Handle aggregation of results"""
        sources = step.config.get("sources", [])
        output_var = step.config.get("output", "aggregated")
        method = step.config.get("method", "merge")

        aggregated = []

        for source in sources:
            data = ctx.variables.get(source, [])
            if isinstance(data, list):
                aggregated.extend(data)
            else:
                aggregated.append(data)

        # Remove duplicates by ID if results have IDs
        if method == "dedupe" and aggregated:
            seen = set()
            deduped = []
            for item in aggregated:
                item_id = getattr(item, "id", None) or (item.chunk.id if hasattr(item, "chunk") else str(item))
                if item_id not in seen:
                    seen.add(item_id)
                    deduped.append(item)
            aggregated = deduped

        ctx.variables[output_var] = aggregated

        return aggregated, None

    async def _handle_crag(
        self,
        step: WorkflowStep,
        ctx: WorkflowExecutionContext,
    ) -> tuple[Any, str | None]:
        """Handle CRAG (Corrective Retrieval Augmented Generation) evaluation.

        Evaluates retrieval quality and refines chunks using the 3-action pattern:
        - CORRECT: high quality → keep chunks, proceed to generate
        - AMBIGUOUS: mixed quality → refine chunks at sentence level
        - INCORRECT: poor quality → mark for fallback collection search

        Config:
            domain: query domain for relevance scoring (crops, irrigation, pest_disease, etc.)
            region: target region for region-aware scoring
            correct_threshold: score threshold for CORRECT action (default 0.7)
            ambiguous_threshold: score threshold for AMBIGUOUS action (default 0.4)
            max_refined_chunks: max chunks to keep after refinement (default 10)
            on_correct: next step when action is CORRECT
            on_ambiguous: next step when action is AMBIGUOUS
            on_incorrect: next step when action is INCORRECT (fallback)

        مرحلة CRAG - الاسترجاع التصحيحي المعزز للتوليد
        """
        # Get config
        domain = step.config.get("domain", ctx.variables.get("query_domain", ""))
        region = step.config.get("region", ctx.variables.get("region", ""))
        correct_threshold = step.config.get("correct_threshold", 0.7)
        ambiguous_threshold = step.config.get("ambiguous_threshold", 0.4)
        max_refined = step.config.get("max_refined_chunks", 10)

        # Build CRAG engine
        engine = CorrectiveRetrievalEngine(
            correct_threshold=correct_threshold,
            ambiguous_threshold=ambiguous_threshold,
            max_refined_chunks=max_refined,
        )

        # Convert retrieval results to chunk dicts for CRAG engine
        results = ctx.variables.get("results", [])
        query = ctx.variables.get("query", "")

        chunks_for_crag: list[dict] = []
        for r in results:
            if hasattr(r, "chunk"):
                chunks_for_crag.append(
                    {
                        "content": r.chunk.text,
                        "content_ar": r.chunk.text_ar or "",
                        "metadata": {
                            **r.chunk.metadata,
                            "collection": r.chunk.collection,
                            "source": r.chunk.document_id,
                        },
                    }
                )
            elif isinstance(r, dict):
                chunks_for_crag.append(r)

        # Run CRAG evaluation and refinement
        crag_result: CRAGResult = engine.evaluate_and_refine(
            query=query,
            retrieved_chunks=chunks_for_crag,
            query_domain=domain,
            target_region=region,
        )

        # Store CRAG results in context
        ctx.variables["crag_result"] = crag_result.to_dict()
        ctx.variables["crag_action"] = crag_result.action_taken.value
        ctx.variables["crag_confidence"] = crag_result.evaluation.confidence.value
        ctx.variables["crag_overall_score"] = crag_result.evaluation.overall_score
        ctx.variables["crag_fallback_used"] = crag_result.fallback_used
        ctx.variables["crag_fallback_source"] = crag_result.fallback_source
        ctx.variables["crag_chunks_in"] = crag_result.total_chunks_input
        ctx.variables["crag_chunks_out"] = crag_result.total_chunks_output
        ctx.variables["crag_refinement_ratio"] = crag_result.refinement_ratio

        # Store refined chunks as context for generation
        if crag_result.refined_chunks:
            ctx.variables["crag_refined_context"] = "\n\n---\n\n".join(
                chunk.content for chunk in crag_result.refined_chunks
            )
            ctx.variables["crag_refined_context_ar"] = "\n\n---\n\n".join(
                chunk.content_ar for chunk in crag_result.refined_chunks if chunk.content_ar
            )

        # If fallback needed, suggest alternative collections
        if crag_result.fallback_used:
            current_collection = ctx.variables.get("collection", "default")
            fallback_collections = engine.suggest_fallback_collections(domain, current_collection)
            ctx.variables["crag_fallback_collections"] = fallback_collections

        # Determine next step based on CRAG action
        on_correct = step.config.get("on_correct")
        on_ambiguous = step.config.get("on_ambiguous")
        on_incorrect = step.config.get("on_incorrect")

        next_step = None
        if crag_result.action_taken == RetrievalAction.CORRECT and on_correct:
            next_step = on_correct
        elif crag_result.action_taken == RetrievalAction.AMBIGUOUS and on_ambiguous:
            next_step = on_ambiguous
        elif crag_result.action_taken == RetrievalAction.INCORRECT and on_incorrect:
            next_step = on_incorrect

        logger.info(
            "crag_step_complete",
            action=crag_result.action_taken.value,
            score=round(crag_result.evaluation.overall_score, 3),
            chunks_in=crag_result.total_chunks_input,
            chunks_out=crag_result.total_chunks_output,
            fallback=crag_result.fallback_used,
            next_step=next_step,
        )

        return crag_result.to_dict(), next_step

    async def _handle_call_rag(
        self,
        step: WorkflowStep,
        ctx: WorkflowExecutionContext,
    ) -> tuple[Any, str | None]:
        """Handle full RAG pipeline call"""
        if self.rag_pipeline is None:
            raise ValueError("RAG pipeline not configured")

        query = step.config.get("query") or ctx.variables.get("query", "")
        collection = step.config.get("collection", "default")

        request = RAGRequest(
            query=query,
            collection=collection,
            top_k=step.config.get("top_k", 10),
            rerank_top_k=step.config.get("rerank_top_k", 5),
            language=step.config.get("language", "en"),
        )

        result = await self.rag_pipeline.run(request)

        ctx.variables["rag_result"] = result
        ctx.variables["answer"] = result.generation_result.answer if result.generation_result else None
        ctx.variables["results"] = result.retrieval_results

        return result, None


def load_workflow_from_yaml(path: str | Path) -> WorkflowConfig:
    """
    Load workflow configuration from YAML file
    تحميل تكوين سير العمل من ملف YAML
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Workflow file not found: {path}")

    with open(path, encoding="utf-8") as f:
        yaml_dict = yaml.safe_load(f)

    return WorkflowConfig.from_yaml(yaml_dict)


def load_workflows_from_directory(directory: str | Path) -> list[WorkflowConfig]:
    """
    Load all workflow configurations from a directory
    تحميل جميع تكوينات سير العمل من مجلد
    """
    directory = Path(directory)
    workflows = []

    if not directory.exists():
        return workflows

    for yaml_file in directory.glob("*.yaml"):
        try:
            workflow = load_workflow_from_yaml(yaml_file)
            workflows.append(workflow)
            logger.info("workflow_loaded", file=str(yaml_file), workflow_id=workflow.id)
        except Exception as e:
            logger.error("workflow_load_error", file=str(yaml_file), error=str(e))

    return workflows


# Export classes
__all__ = [
    "WorkflowEngine",
    "WorkflowExecutionContext",
    "StepExecutionResult",
    "load_workflow_from_yaml",
    "load_workflows_from_directory",
]
