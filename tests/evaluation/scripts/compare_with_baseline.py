#!/usr/bin/env python3
"""
Compare with Baseline
المقارنة مع خط الأساس

Script to compare current evaluation results with baseline to detect regressions.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


class BaselineComparator:
    """
    Compare evaluation results with baseline
    مقارنة نتائج التقييم مع خط الأساس
    """

    # Thresholds for regression detection
    REGRESSION_THRESHOLDS = {
        "overall_score": 5.0,  # 5% drop is a regression
        "accuracy": 5.0,
        "latency_score": 10.0,  # More lenient for latency
        "safety_score": 2.0,  # Very strict for safety
        "pass_rate": 5.0,
    }

    def __init__(self, current_file: Path, baseline_file: Path):
        """Initialize with current and baseline files"""
        self.current_file = current_file
        self.baseline_file = baseline_file
        self.current: dict[str, Any] = {}
        self.baseline: dict[str, Any] = {}

    def load_data(self) -> bool:
        """Load current and baseline data"""
        # Load current results
        if not self.current_file.exists():
            print(f"❌ Current results file not found: {self.current_file}")
            return False

        try:
            with open(self.current_file, encoding="utf-8") as f:
                self.current = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in current file: {e}")
            return False

        # Load baseline (may not exist for first run)
        if not self.baseline_file.exists():
            print("⚠️ No baseline found. This will be the first baseline.")
            self.baseline = {}
            return True

        try:
            with open(self.baseline_file, encoding="utf-8") as f:
                self.baseline = json.load(f)
        except json.JSONDecodeError as e:
            print(f"⚠️ Invalid JSON in baseline file: {e}")
            self.baseline = {}

        return True

    def compare(self) -> dict[str, Any]:
        """
        Compare current results with baseline
        مقارنة النتائج الحالية مع خط الأساس

        Returns:
            Comparison report
        """
        if not self.baseline:
            return {
                "has_regression": False,
                "is_first_run": True,
                "message": "No baseline available. Current results will become the baseline.",
                "current_score": self.current.get("overall_score", 0.0),
            }

        regressions = []
        improvements = []
        stable = []

        # Compare key metrics
        metrics_to_compare = [
            "overall_score",
            "accuracy",
            "latency_score",
            "safety_score",
            "pass_rate",
        ]

        for metric in metrics_to_compare:
            current_value = self.current.get(metric, 0.0)
            baseline_value = self.baseline.get(metric, 0.0)
            threshold = self.REGRESSION_THRESHOLDS.get(metric, 5.0)

            change = current_value - baseline_value
            change_pct = (change / baseline_value * 100) if baseline_value > 0 else 0.0

            if abs(change) < threshold:
                # Stable (no significant change)
                stable.append(
                    {
                        "metric": metric,
                        "current": current_value,
                        "baseline": baseline_value,
                        "change": change,
                        "change_pct": change_pct,
                    }
                )
            elif change < -threshold:
                # Regression (significant drop)
                regressions.append(
                    {
                        "metric": metric,
                        "current": current_value,
                        "baseline": baseline_value,
                        "change": change,
                        "change_pct": change_pct,
                        "threshold": threshold,
                    }
                )
            else:
                # Improvement (significant increase)
                improvements.append(
                    {
                        "metric": metric,
                        "current": current_value,
                        "baseline": baseline_value,
                        "change": change,
                        "change_pct": change_pct,
                    }
                )

        # Compare language support
        language_comparison = self._compare_language_support()

        # Compare category scores
        category_comparison = self._compare_categories()

        # Check for latency regression
        latency_regression = self._check_latency_regression()

        has_regression = len(regressions) > 0 or latency_regression

        return {
            "has_regression": has_regression,
            "is_first_run": False,
            "regressions": regressions,
            "improvements": improvements,
            "stable": stable,
            "language_comparison": language_comparison,
            "category_comparison": category_comparison,
            "latency_regression": latency_regression,
            "summary": self._generate_summary(regressions, improvements, stable),
        }

    def _compare_language_support(self) -> dict[str, Any]:
        """Compare language support metrics"""
        current_arabic = self.current.get("arabic_support", 0.0)
        current_english = self.current.get("english_support", 0.0)
        baseline_arabic = self.baseline.get("arabic_support", 0.0)
        baseline_english = self.baseline.get("english_support", 0.0)

        return {
            "arabic": {
                "current": current_arabic,
                "baseline": baseline_arabic,
                "change": current_arabic - baseline_arabic,
            },
            "english": {
                "current": current_english,
                "baseline": baseline_english,
                "change": current_english - baseline_english,
            },
        }

    def _compare_categories(self) -> list[dict[str, Any]]:
        """Compare category scores"""
        current_categories = self.current.get("category_scores", {})
        baseline_categories = self.baseline.get("category_scores", {})

        comparisons = []

        all_categories = set(current_categories.keys()) | set(
            baseline_categories.keys()
        )

        for category in all_categories:
            current_score = current_categories.get(category, 0.0)
            baseline_score = baseline_categories.get(category, 0.0)
            change = current_score - baseline_score

            comparisons.append(
                {
                    "category": category,
                    "current": current_score,
                    "baseline": baseline_score,
                    "change": change,
                    "status": (
                        "regression"
                        if change < -5.0
                        else "improvement" if change > 5.0 else "stable"
                    ),
                }
            )

        return comparisons

    def _check_latency_regression(self) -> bool:
        """Check for latency regression"""
        current_latency = self.current.get("avg_latency_ms", 0.0)
        baseline_latency = self.baseline.get("avg_latency_ms", 0.0)

        if baseline_latency == 0:
            return False

        # Latency regression if current is 20% slower
        threshold_latency = baseline_latency * 1.2

        return current_latency > threshold_latency

    def _generate_summary(
        self,
        regressions: list[dict[str, Any]],
        improvements: list[dict[str, Any]],
        stable: list[dict[str, Any]],
    ) -> str:
        """Generate human-readable summary"""
        if not regressions and not improvements:
            return "No significant changes detected."

        summary_parts = []

        if regressions:
            summary_parts.append(
                f"⚠️ {len(regressions)} regression(s) detected: "
                + ", ".join(r["metric"] for r in regressions)
            )

        if improvements:
            summary_parts.append(
                f"✅ {len(improvements)} improvement(s): "
                + ", ".join(i["metric"] for i in improvements)
            )

        if stable:
            summary_parts.append(f"📊 {len(stable)} metric(s) stable")

        return " | ".join(summary_parts)

    def save_comparison(self, output_file: Path):
        """Save comparison report"""
        comparison = self.compare()

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(comparison, f, indent=2, ensure_ascii=False)

        print(f"✅ Comparison report saved to: {output_file}")

        # Print summary
        print("\n📊 Baseline Comparison Summary:")
        print(f"   {comparison['summary']}")

        if comparison.get("has_regression"):
            print("\n⚠️ REGRESSION DETECTED!")
            for regression in comparison.get("regressions", []):
                print(
                    f"   - {regression['metric']}: "
                    f"{regression['baseline']:.2f}% → {regression['current']:.2f}% "
                    f"(Δ {regression['change']:.2f}%)"
                )

        if comparison.get("improvements"):
            print("\n✅ Improvements:")
            for improvement in comparison.get("improvements", []):
                print(
                    f"   + {improvement['metric']}: "
                    f"{improvement['baseline']:.2f}% → {improvement['current']:.2f}% "
                    f"(Δ +{improvement['change']:.2f}%)"
                )

        return comparison


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description="Compare evaluation results with baseline"
    )
    parser.add_argument(
        "--current",
        type=Path,
        required=True,
        help="Path to current evaluation summary",
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        required=True,
        help="Path to baseline evaluation summary",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("regression-report.json"),
        help="Output file for comparison report",
    )

    args = parser.parse_args()

    # Compare with baseline
    comparator = BaselineComparator(args.current, args.baseline)

    if not comparator.load_data():
        sys.exit(1)

    comparison = comparator.save_comparison(args.output)

    # Exit with error code if regression detected (but only as warning)
    # Don't fail the build, just warn
    if comparison.get("has_regression"):
        print("\n⚠️ Warning: Performance regression detected.")
        print("   Review the changes carefully before merging.")
        # sys.exit(1)  # Uncomment to fail on regression


if __name__ == "__main__":
    main()
