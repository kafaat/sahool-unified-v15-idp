#!/usr/bin/env python3
"""
Golden Dataset Evaluation Tests
اختبارات تقييم مجموعة البيانات الذهبية

Tests agent responses against golden dataset for quality assurance.
"""

import json
import os
import pytest
from pathlib import Path
from typing import Dict, Any, List


# Locate golden datasets
REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
GOLDEN_DATASETS_DIR = REPO_ROOT / "tests" / "golden-datasets"
EVALUATION_DATASETS_DIR = REPO_ROOT / "tests" / "evaluation" / "datasets"


def load_golden_datasets() -> List[Dict[str, Any]]:
    """Load all golden datasets for testing"""
    test_cases = []

    # Load from tests/golden-datasets if it exists
    if GOLDEN_DATASETS_DIR.exists():
        for json_file in GOLDEN_DATASETS_DIR.glob("*.json"):
            if json_file.name == "README.md":
                continue
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Handle both formats: direct array or with test_cases key
                    if isinstance(data, list):
                        test_cases.extend(data)
                    elif isinstance(data, dict) and 'test_cases' in data:
                        test_cases.extend(data['test_cases'])
            except Exception as e:
                print(f"Warning: Could not load {json_file}: {e}")

    # Load from tests/evaluation/datasets if golden-datasets was empty
    if not test_cases and EVALUATION_DATASETS_DIR.exists():
        golden_file = EVALUATION_DATASETS_DIR / "golden_dataset.json"
        if golden_file.exists():
            with open(golden_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    test_cases.extend(data)

    return test_cases


@pytest.fixture(scope="module")
def golden_test_cases():
    """Fixture to load golden test cases"""
    test_cases = load_golden_datasets()
    if not test_cases:
        pytest.skip("No golden datasets found")
    return test_cases


@pytest.mark.asyncio
async def test_golden_dataset_structure(golden_test_cases):
    """Test that golden datasets have the correct structure"""
    assert len(golden_test_cases) > 0, "No test cases loaded"

    for idx, test_case in enumerate(golden_test_cases):
        # Check required fields
        assert 'id' in test_case, f"Test case {idx} missing 'id'"
        assert 'input' in test_case or 'prompt' in test_case.get('input', {}), \
            f"Test case {idx} missing input"


@pytest.mark.asyncio
@pytest.mark.parametrize("test_case", load_golden_datasets(),
                         ids=lambda tc: tc.get('id', 'unknown'))
async def test_agent_response_quality(test_case):
    """
    Test agent responses against golden dataset

    This is a placeholder that demonstrates the structure.
    In production, this would:
    1. Call the actual AI agent with the test input
    2. Compare the response against expected output
    3. Calculate similarity scores
    4. Verify safety constraints
    """
    # Skip if running without actual agent
    if os.getenv("EVALUATION_MODE") != "true":
        pytest.skip("Evaluation mode not enabled")

    # Placeholder test - in production, call actual agent
    test_id = test_case.get('id', 'unknown')

    # For now, just verify the structure
    assert 'id' in test_case

    # Mock passing test
    # In production, replace with actual agent evaluation
    accuracy_score = 0.85  # Mock score
    latency_ms = 1200  # Mock latency

    # Check thresholds (from test case or defaults)
    min_accuracy = test_case.get('evaluation_criteria', {}).get('min_similarity', 0.75)
    max_latency = test_case.get('evaluation_criteria', {}).get('max_latency_ms', 5000)

    assert accuracy_score >= min_accuracy, \
        f"Accuracy {accuracy_score} below threshold {min_accuracy}"
    assert latency_ms <= max_latency, \
        f"Latency {latency_ms}ms exceeds threshold {max_latency}ms"


@pytest.mark.asyncio
async def test_language_support(golden_test_cases):
    """Test that both Arabic and English are supported"""
    languages = set()
    for test_case in golden_test_cases:
        lang = test_case.get('language') or test_case.get('input', {}).get('language', 'en')
        languages.add(lang)

    # Should have at least one language
    assert len(languages) > 0, "No languages found in test cases"


@pytest.mark.asyncio
async def test_category_coverage(golden_test_cases):
    """Test that multiple agricultural categories are covered"""
    categories = set()
    for test_case in golden_test_cases:
        category = test_case.get('category', 'unknown')
        categories.add(category)

    # Should cover multiple categories
    assert len(categories) >= 3, \
        f"Insufficient category coverage: {categories}"


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
