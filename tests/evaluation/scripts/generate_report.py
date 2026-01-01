#!/usr/bin/env python3
"""
Generate Evaluation Report
إنشاء تقرير التقييم

Script to generate detailed markdown evaluation report.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class ReportGenerator:
    """
    Generate detailed evaluation reports
    إنشاء تقارير تقييم مفصلة
    """

    def __init__(self, metrics_file: Path):
        """Initialize with metrics file"""
        self.metrics_file = metrics_file
        self.metrics: Dict[str, Any] = {}

    def load_metrics(self) -> bool:
        """Load metrics from file"""
        if not self.metrics_file.exists():
            print(f"❌ Metrics file not found: {self.metrics_file}")
            return False

        try:
            with open(self.metrics_file, "r", encoding="utf-8") as f:
                self.metrics = json.load(f)
            return True
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in metrics file: {e}")
            return False

    def generate_report(self) -> str:
        """
        Generate comprehensive markdown report
        إنشاء تقرير ماركداون شامل

        Returns:
            Markdown report string
        """
        report_lines = []

        # Header
        report_lines.extend(self._generate_header())

        # Executive Summary
        report_lines.extend(self._generate_executive_summary())

        # Detailed Metrics
        report_lines.extend(self._generate_detailed_metrics())

        # Category Breakdown
        report_lines.extend(self._generate_category_breakdown())

        # Language Support
        report_lines.extend(self._generate_language_support())

        # Performance Metrics
        report_lines.extend(self._generate_performance_metrics())

        # Recommendations
        report_lines.extend(self._generate_recommendations())

        # Footer
        report_lines.extend(self._generate_footer())

        return "\n".join(report_lines)

    def _generate_header(self) -> list:
        """Generate report header"""
        timestamp = self.metrics.get("timestamp", datetime.utcnow().isoformat())
        return [
            "# Agent Evaluation Report",
            "# تقرير تقييم الوكلاء",
            "",
            f"**Generated:** {timestamp}",
            "",
            "---",
            "",
        ]

    def _generate_executive_summary(self) -> list:
        """Generate executive summary"""
        overall_score = self.metrics.get("overall_score", 0.0)
        pass_rate = self.metrics.get("pass_rate", 0.0)
        total_tests = self.metrics.get("total_tests", 0)
        passed_tests = self.metrics.get("passed_tests", 0)
        failed_tests = self.metrics.get("failed_tests", 0)

        status_emoji = (
            "✅" if overall_score >= 85 else "⚠️" if overall_score >= 70 else "❌"
        )
        status_text = (
            "PASS"
            if overall_score >= 85
            else "WARNING" if overall_score >= 70 else "FAIL"
        )

        return [
            "## Executive Summary",
            "## الملخص التنفيذي",
            "",
            f"### {status_emoji} Overall Status: **{status_text}**",
            "",
            f"**Overall Evaluation Score:** {overall_score}%",
            "",
            "| Metric | Score | Status |",
            "|--------|-------|--------|",
            f"| Overall Score | {overall_score}% | {self._get_status_badge(overall_score)} |",
            f"| Pass Rate | {pass_rate}% | {self._get_status_badge(pass_rate)} |",
            f"| Tests Passed | {passed_tests}/{total_tests} | - |",
            "",
        ]

    def _generate_detailed_metrics(self) -> list:
        """Generate detailed metrics section"""
        accuracy = self.metrics.get("accuracy", 0.0)
        latency_score = self.metrics.get("latency_score", 0.0)
        safety_score = self.metrics.get("safety_score", 0.0)

        return [
            "## Detailed Metrics",
            "## المقاييس التفصيلية",
            "",
            "### Component Scores",
            "",
            "| Component | Score | Weight | Status |",
            "|-----------|-------|--------|--------|",
            f"| **Accuracy** | {accuracy}% | 50% | {self._get_status_badge(accuracy)} |",
            f"| **Latency** | {latency_score}% | 25% | {self._get_status_badge(latency_score)} |",
            f"| **Safety** | {safety_score}% | 25% | {self._get_status_badge(safety_score)} |",
            "",
            "#### Accuracy (استجابة دقيقة)",
            f"- Measures semantic similarity between agent responses and expected outputs",
            f"- Current Score: **{accuracy}%**",
            f"- Target: ≥75%",
            "",
            "#### Latency (زمن الاستجابة)",
            f"- Measures response time performance",
            f"- Current Score: **{latency_score}%**",
            f"- Target: <5000ms per query",
            "",
            "#### Safety (السلامة)",
            f"- Checks for harmful content, bias, and misinformation",
            f"- Current Score: **{safety_score}%**",
            f"- Target: ≥95%",
            "",
        ]

    def _generate_category_breakdown(self) -> list:
        """Generate category breakdown"""
        category_scores = self.metrics.get("category_scores", {})

        if not category_scores:
            return ["## Category Breakdown", "", "_No category data available_", ""]

        lines = [
            "## Category Breakdown",
            "## تفصيل حسب الفئة",
            "",
            "| Category | Pass Rate | Status |",
            "|----------|-----------|--------|",
        ]

        for category, score in category_scores.items():
            category_name = self._format_category_name(category)
            lines.append(
                f"| {category_name} | {score}% | {self._get_status_badge(score)} |"
            )

        lines.append("")
        return lines

    def _generate_language_support(self) -> list:
        """Generate language support section"""
        arabic_support = self.metrics.get("arabic_support", 0.0)
        english_support = self.metrics.get("english_support", 0.0)

        return [
            "## Language Support",
            "## دعم اللغات",
            "",
            "| Language | Pass Rate | Status |",
            "|----------|-----------|--------|",
            f"| Arabic (العربية) | {arabic_support}% | {self._get_status_badge(arabic_support)} |",
            f"| English | {english_support}% | {self._get_status_badge(english_support)} |",
            "",
            "### Multi-language Support Analysis",
            "",
            self._get_language_analysis(arabic_support, english_support),
            "",
        ]

    def _generate_performance_metrics(self) -> list:
        """Generate performance metrics"""
        avg_latency = self.metrics.get("avg_latency_ms", 0.0)
        max_latency = self.metrics.get("max_latency_ms", 0.0)
        min_latency = self.metrics.get("min_latency_ms", 0.0)

        latency_status = (
            "✅ Excellent"
            if avg_latency < 2000
            else "⚠️ Acceptable" if avg_latency < 5000 else "❌ Poor"
        )

        return [
            "## Performance Metrics",
            "## مقاييس الأداء",
            "",
            "### Response Latency",
            "",
            "| Metric | Value | Status |",
            "|--------|-------|--------|",
            f"| Average Latency | {avg_latency:.0f}ms | {latency_status} |",
            f"| Minimum Latency | {min_latency:.0f}ms | - |",
            f"| Maximum Latency | {max_latency:.0f}ms | - |",
            "",
            "**Latency Targets:**",
            "- Excellent: <2000ms",
            "- Acceptable: <5000ms",
            "- Poor: ≥5000ms",
            "",
        ]

    def _generate_recommendations(self) -> list:
        """Generate recommendations based on metrics"""
        recommendations = []
        overall_score = self.metrics.get("overall_score", 0.0)
        accuracy = self.metrics.get("accuracy", 0.0)
        latency_score = self.metrics.get("latency_score", 0.0)
        safety_score = self.metrics.get("safety_score", 0.0)
        avg_latency = self.metrics.get("avg_latency_ms", 0.0)

        lines = [
            "## Recommendations",
            "## التوصيات",
            "",
        ]

        if overall_score >= 85:
            recommendations.append(
                "✅ Excellent performance! Agent is ready for production."
            )
        elif overall_score >= 70:
            recommendations.append("⚠️ Good performance with room for improvement.")
        else:
            recommendations.append(
                "❌ Performance below threshold. Review and improve before deploying."
            )

        if accuracy < 75:
            recommendations.append(
                "- **Accuracy**: Improve response quality. Consider:\n"
                "  - Fine-tuning prompts\n"
                "  - Enhancing RAG knowledge base\n"
                "  - Adding more training examples"
            )

        if latency_score < 75 or avg_latency > 5000:
            recommendations.append(
                "- **Latency**: Optimize response time. Consider:\n"
                "  - Caching frequent queries\n"
                "  - Optimizing RAG retrieval\n"
                "  - Using smaller model variants for simple queries"
            )

        if safety_score < 95:
            recommendations.append(
                "- **Safety**: Enhance safety checks. Consider:\n"
                "  - Adding more safety constraints\n"
                "  - Improving content filtering\n"
                "  - Adding human review for critical decisions"
            )

        arabic_support = self.metrics.get("arabic_support", 0.0)
        english_support = self.metrics.get("english_support", 0.0)

        if arabic_support < english_support - 10:
            recommendations.append(
                "- **Arabic Support**: Improve Arabic language handling:\n"
                "  - Add more Arabic training examples\n"
                "  - Verify Arabic-specific prompts\n"
                "  - Test with native speakers"
            )

        if not recommendations:
            recommendations.append("No specific recommendations at this time.")

        lines.extend(recommendations)
        lines.append("")

        return lines

    def _generate_footer(self) -> list:
        """Generate report footer"""
        return [
            "---",
            "",
            "## About This Report",
            "",
            "This evaluation report was automatically generated by the SAHOOL Agent Evaluation Pipeline.",
            "The pipeline follows Google AgentOps best practices for AI agent evaluation.",
            "",
            "**Evaluation Components:**",
            "- Golden Dataset Testing",
            "- Semantic Similarity Analysis",
            "- Latency Performance Monitoring",
            "- Safety Compliance Checking",
            "- Multi-language Support Validation",
            "",
            "For questions or issues, please contact the AI team.",
            "",
        ]

    def _get_status_badge(self, score: float) -> str:
        """Get status badge emoji based on score"""
        if score >= 85:
            return "✅ Excellent"
        elif score >= 70:
            return "⚠️ Good"
        else:
            return "❌ Needs Improvement"

    def _format_category_name(self, category: str) -> str:
        """Format category name for display"""
        return category.replace("_", " ").title()

    def _get_language_analysis(self, arabic: float, english: float) -> str:
        """Get language support analysis"""
        diff = abs(arabic - english)

        if diff < 5:
            return "✅ **Excellent**: Both languages are well-supported with balanced performance."
        elif diff < 15:
            return "⚠️ **Good**: Minor difference in language support. Monitor for consistency."
        else:
            lower_lang = "Arabic" if arabic < english else "English"
            return f"❌ **Attention Needed**: {lower_lang} support significantly lower. Requires improvement."

    def save_report(self, output_file: Path):
        """Save report to file"""
        report = self.generate_report()

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"✅ Evaluation report saved to: {output_file}")


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description="Generate detailed evaluation report")
    parser.add_argument(
        "--metrics",
        type=Path,
        required=True,
        help="Path to evaluation summary JSON",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("evaluation-detailed-report.md"),
        help="Output markdown file",
    )

    args = parser.parse_args()

    # Generate report
    generator = ReportGenerator(args.metrics)

    if not generator.load_metrics():
        sys.exit(1)

    generator.save_report(args.output)

    print("\n✅ Report generation complete!")


if __name__ == "__main__":
    main()
