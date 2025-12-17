"""
SAHOOL RAG Evaluation
Sprint 9: Evaluation hooks for RAG quality measurement

Provides metrics for measuring RAG quality using:
- Pass@K: Whether expected documents appear in top-k results
- Recall: Proportion of expected documents retrieved
- Precision: Proportion of retrieved documents that are relevant
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvalCase:
    """A single evaluation case for RAG testing.

    Attributes:
        question: The test question
        expected_doc_ids: Documents that should appear in sources
        expected_keywords: Keywords that should appear in the answer (optional)
    """

    question: str
    expected_doc_ids: list[str]
    expected_keywords: list[str] | None = None


@dataclass(frozen=True)
class EvalResult:
    """Result of evaluating a single case.

    Attributes:
        case: The evaluation case
        passed: Whether the case passed
        pass_at_k: Pass@K score (1.0 if any expected doc found, else 0.0)
        recall: Recall score (proportion of expected docs found)
        returned_sources: Sources returned by RAG
        answer: Generated answer
    """

    case: EvalCase
    passed: bool
    pass_at_k: float
    recall: float
    returned_sources: list[str]
    answer: str


def pass_at_k(
    *,
    returned_sources: list[str],
    expected_doc_ids: list[str],
) -> float:
    """Calculate Pass@K metric.

    Pass@K = 1.0 if any expected document appears in returned sources.
    This is a lenient metric suitable for knowledge retrieval.

    Args:
        returned_sources: Documents returned by RAG
        expected_doc_ids: Documents expected to be relevant

    Returns:
        1.0 if pass, 0.0 if fail
    """
    if not expected_doc_ids:
        return 1.0  # No expected docs means trivially passing

    returned = set(returned_sources)
    expected = set(expected_doc_ids)

    return 1.0 if expected.intersection(returned) else 0.0


def recall(
    *,
    returned_sources: list[str],
    expected_doc_ids: list[str],
) -> float:
    """Calculate recall metric.

    Recall = (relevant retrieved) / (total relevant)

    Args:
        returned_sources: Documents returned by RAG
        expected_doc_ids: Documents expected to be relevant

    Returns:
        Recall score between 0.0 and 1.0
    """
    if not expected_doc_ids:
        return 1.0

    returned = set(returned_sources)
    expected = set(expected_doc_ids)
    found = expected.intersection(returned)

    return len(found) / len(expected)


def precision(
    *,
    returned_sources: list[str],
    expected_doc_ids: list[str],
) -> float:
    """Calculate precision metric.

    Precision = (relevant retrieved) / (total retrieved)

    Args:
        returned_sources: Documents returned by RAG
        expected_doc_ids: Documents expected to be relevant

    Returns:
        Precision score between 0.0 and 1.0
    """
    if not returned_sources:
        return 0.0 if expected_doc_ids else 1.0

    returned = set(returned_sources)
    expected = set(expected_doc_ids)
    found = expected.intersection(returned)

    return len(found) / len(returned)


def f1_score(
    *,
    returned_sources: list[str],
    expected_doc_ids: list[str],
) -> float:
    """Calculate F1 score.

    F1 = 2 * (precision * recall) / (precision + recall)

    Args:
        returned_sources: Documents returned by RAG
        expected_doc_ids: Documents expected to be relevant

    Returns:
        F1 score between 0.0 and 1.0
    """
    p = precision(returned_sources=returned_sources, expected_doc_ids=expected_doc_ids)
    r = recall(returned_sources=returned_sources, expected_doc_ids=expected_doc_ids)

    if p + r == 0:
        return 0.0

    return 2 * (p * r) / (p + r)


def keyword_coverage(
    *,
    answer: str,
    expected_keywords: list[str],
) -> float:
    """Calculate keyword coverage in the answer.

    Args:
        answer: Generated answer
        expected_keywords: Keywords expected in the answer

    Returns:
        Proportion of keywords found in answer
    """
    if not expected_keywords:
        return 1.0

    answer_lower = answer.lower()
    found = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)

    return found / len(expected_keywords)


def evaluate_case(
    case: EvalCase,
    returned_sources: list[str],
    answer: str,
) -> EvalResult:
    """Evaluate a single case.

    Args:
        case: Evaluation case
        returned_sources: Sources returned by RAG
        answer: Generated answer

    Returns:
        Evaluation result
    """
    pak = pass_at_k(
        returned_sources=returned_sources,
        expected_doc_ids=case.expected_doc_ids,
    )
    rec = recall(
        returned_sources=returned_sources,
        expected_doc_ids=case.expected_doc_ids,
    )

    # Consider passed if Pass@K is 1.0
    passed = pak == 1.0

    return EvalResult(
        case=case,
        passed=passed,
        pass_at_k=pak,
        recall=rec,
        returned_sources=returned_sources,
        answer=answer,
    )


def aggregate_results(results: list[EvalResult]) -> dict:
    """Aggregate multiple evaluation results.

    Args:
        results: List of evaluation results

    Returns:
        Aggregated metrics dict
    """
    if not results:
        return {
            "total": 0,
            "passed": 0,
            "pass_rate": 0.0,
            "avg_pass_at_k": 0.0,
            "avg_recall": 0.0,
        }

    total = len(results)
    passed = sum(1 for r in results if r.passed)
    avg_pak = sum(r.pass_at_k for r in results) / total
    avg_recall = sum(r.recall for r in results) / total

    return {
        "total": total,
        "passed": passed,
        "pass_rate": passed / total,
        "avg_pass_at_k": avg_pak,
        "avg_recall": avg_recall,
    }
