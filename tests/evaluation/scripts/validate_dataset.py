#!/usr/bin/env python3
"""
Validate Evaluation Dataset
التحقق من صحة مجموعة بيانات التقييم

Script to validate the structure and content of golden datasets.
"""

import json
import sys
from pathlib import Path
from typing import Any


class DatasetValidator:
    """
    Validator for evaluation datasets
    مدقق لمجموعات بيانات التقييم
    """

    REQUIRED_FIELDS = {
        "id": str,
        "category": str,
        "language": str,
        "input": dict,
        "expected_output": dict,
        "evaluation_criteria": dict,
    }

    REQUIRED_INPUT_FIELDS = {
        "query": str,
    }

    REQUIRED_OUTPUT_FIELDS = {
        "response": str,
        "agents": list,
    }

    REQUIRED_CRITERIA_FIELDS = {
        "min_similarity": (int, float),
        "max_latency_ms": (int, float),
    }

    VALID_CATEGORIES = {
        "disease_diagnosis",
        "irrigation",
        "field_analysis",
        "yield_prediction",
        "multi_agent",
    }

    VALID_LANGUAGES = {"en", "ar"}

    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate_dataset(self, dataset: list[dict[str, Any]]) -> bool:
        """
        Validate entire dataset
        التحقق من صحة مجموعة البيانات بالكامل

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(dataset, list):
            self.errors.append("Dataset must be a list")
            return False

        if len(dataset) == 0:
            self.errors.append("Dataset is empty")
            return False

        # Track IDs for uniqueness
        ids: set[str] = set()

        for idx, test_case in enumerate(dataset):
            if not self._validate_test_case(test_case, idx):
                return False

            # Check ID uniqueness
            test_id = test_case.get("id")
            if test_id in ids:
                self.errors.append(f"Duplicate test ID: {test_id}")
                return False
            ids.add(test_id)

        # Check coverage
        self._check_coverage(dataset)

        return len(self.errors) == 0

    def _validate_test_case(self, test_case: dict[str, Any], idx: int) -> bool:
        """Validate individual test case"""
        # Check required fields
        for field, field_type in self.REQUIRED_FIELDS.items():
            if field not in test_case:
                self.errors.append(f"Test case {idx}: Missing required field '{field}'")
                return False

            if not isinstance(test_case[field], field_type):
                self.errors.append(
                    f"Test case {idx}: Field '{field}' must be of type {field_type.__name__}"
                )
                return False

        # Validate category
        if test_case["category"] not in self.VALID_CATEGORIES:
            self.errors.append(
                f"Test case {idx}: Invalid category '{test_case['category']}'. "
                f"Valid categories: {self.VALID_CATEGORIES}"
            )
            return False

        # Validate language
        if test_case["language"] not in self.VALID_LANGUAGES:
            self.errors.append(
                f"Test case {idx}: Invalid language '{test_case['language']}'. "
                f"Valid languages: {self.VALID_LANGUAGES}"
            )
            return False

        # Validate input section
        if not self._validate_input(test_case["input"], idx):
            return False

        # Validate expected output section
        if not self._validate_expected_output(test_case["expected_output"], idx):
            return False

        # Validate evaluation criteria
        if not self._validate_criteria(test_case["evaluation_criteria"], idx):
            return False

        return True

    def _validate_input(self, input_data: dict[str, Any], idx: int) -> bool:
        """Validate input section"""
        for field, field_type in self.REQUIRED_INPUT_FIELDS.items():
            if field not in input_data:
                self.errors.append(
                    f"Test case {idx}: Missing required input field '{field}'"
                )
                return False

            if not isinstance(input_data[field], field_type):
                self.errors.append(
                    f"Test case {idx}: Input field '{field}' must be of type {field_type.__name__}"
                )
                return False

        # Check query is not empty
        if not input_data["query"].strip():
            self.errors.append(f"Test case {idx}: Query cannot be empty")
            return False

        return True

    def _validate_expected_output(self, output: dict[str, Any], idx: int) -> bool:
        """Validate expected output section"""
        for field, field_type in self.REQUIRED_OUTPUT_FIELDS.items():
            if field not in output:
                self.errors.append(
                    f"Test case {idx}: Missing required output field '{field}'"
                )
                return False

            if not isinstance(output[field], field_type):
                self.errors.append(
                    f"Test case {idx}: Output field '{field}' must be of type {field_type.__name__}"
                )
                return False

        # Check response is not empty
        if not output["response"].strip():
            self.errors.append(f"Test case {idx}: Expected response cannot be empty")
            return False

        # Check agents list is not empty
        if len(output["agents"]) == 0:
            self.warnings.append(f"Test case {idx}: No agents specified")

        return True

    def _validate_criteria(self, criteria: dict[str, Any], idx: int) -> bool:
        """Validate evaluation criteria"""
        for field, field_types in self.REQUIRED_CRITERIA_FIELDS.items():
            if field not in criteria:
                self.errors.append(
                    f"Test case {idx}: Missing required criteria field '{field}'"
                )
                return False

            if not isinstance(criteria[field], field_types):
                self.errors.append(
                    f"Test case {idx}: Criteria field '{field}' must be numeric"
                )
                return False

        # Validate ranges
        min_sim = criteria["min_similarity"]
        if not (0.0 <= min_sim <= 1.0):
            self.errors.append(
                f"Test case {idx}: min_similarity must be between 0 and 1"
            )
            return False

        max_latency = criteria["max_latency_ms"]
        if max_latency <= 0:
            self.errors.append(f"Test case {idx}: max_latency_ms must be positive")
            return False

        if max_latency > 30000:
            self.warnings.append(
                f"Test case {idx}: max_latency_ms of {max_latency}ms seems very high"
            )

        return True

    def _check_coverage(self, dataset: list[dict[str, Any]]):
        """Check dataset coverage"""
        categories = set(tc["category"] for tc in dataset)
        languages = set(tc["language"] for tc in dataset)

        # Check category coverage
        missing_categories = self.VALID_CATEGORIES - categories
        if missing_categories:
            self.warnings.append(
                f"Dataset missing test cases for categories: {missing_categories}"
            )

        # Check language coverage
        missing_languages = self.VALID_LANGUAGES - languages
        if missing_languages:
            self.warnings.append(
                f"Dataset missing test cases for languages: {missing_languages}"
            )

        # Check each category has tests in each language
        for category in categories:
            category_cases = [tc for tc in dataset if tc["category"] == category]
            category_langs = set(tc["language"] for tc in category_cases)

            missing_langs = self.VALID_LANGUAGES - category_langs
            if missing_langs:
                self.warnings.append(
                    f"Category '{category}' missing tests for languages: {missing_langs}"
                )

    def print_results(self):
        """Print validation results"""
        if self.errors:
            print("❌ Validation FAILED")
            print("\nErrors:")
            for error in self.errors:
                print(f"  - {error}")
        else:
            print("✅ Validation PASSED")

        if self.warnings:
            print("\nWarnings:")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")


def main():
    """Main execution"""
    # Find dataset file
    script_dir = Path(__file__).parent
    dataset_file = script_dir.parent / "datasets" / "golden_dataset.json"

    if not dataset_file.exists():
        print(f"❌ Dataset file not found: {dataset_file}")
        sys.exit(1)

    # Load dataset
    try:
        with open(dataset_file, encoding="utf-8") as f:
            dataset = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in dataset file: {e}")
        sys.exit(1)

    # Validate
    validator = DatasetValidator()
    is_valid = validator.validate_dataset(dataset)

    # Print results
    print(f"\n📊 Validating dataset: {dataset_file}")
    print(f"   Total test cases: {len(dataset)}")
    validator.print_results()

    # Exit with appropriate code
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
