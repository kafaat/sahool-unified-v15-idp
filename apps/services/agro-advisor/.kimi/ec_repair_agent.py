"""
Kimi Agro Advisor EC Repair Agent
==================================
وكيل إصلاح EC للمستشار الزراعي - Kimi

Specialized agent for detecting and fixing EC (Electrical Conductivity) misuse
in agricultural advisory services.

This agent focuses on the critical issue identified in Research Paper 2:
EC ≠ NPK correlation - EC should NOT be used as a nutrient indicator.

Usage:
    python -m apps.services.agro-advisor..kimi.ec_repair_agent [--scan|--fix]

Author: SAHOOL Platform Team
Version: 16.0.0
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class ECIssue:
    """Represents an EC misuse issue."""

    file_path: str
    line_number: int
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    issue_type: str
    message: str
    message_ar: str
    pattern_matched: str
    suggested_fix: Optional[str] = None
    code_snippet: Optional[str] = None


class AgroAdvisorECRepairAgent:
    """
    Specialized agent for detecting EC misuse in Agro Advisor service.
    وكيل متخصص في اكتشاف سوء استخدام EC في خدمة المستشار الزراعي.

    Research Background:
    - EC (Electrical Conductivity) measures soil salinity, NOT nutrient content
    - Common mistake: Using EC values to calculate NPK fertilizer recommendations
    - Correct approach: Use actual lab nutrient analysis (mg/kg or ppm)
    """

    # Patterns that indicate EC misuse
    EC_MISUSE_PATTERNS = [
        # Direct EC to nutrient calculation
        (
            r"ec_value\s*[*+\-/]\s*\w*nutrient",
            "CRITICAL",
            "Using EC value in nutrient calculation",
            "استخدام قيمة EC في حساب المغذيات",
        ),
        (
            r"ec\s*.*\s*fertilizer.*calculat",
            "CRITICAL",
            "Using EC for fertilizer calculation",
            "استخدام EC لحساب الأسمدة",
        ),
        # EC used for NPK determination
        (
            r"soil_ec\s*.*\s*(nitrogen|phosphorus|potassium)",
            "CRITICAL",
            "Using soil EC to determine NPK levels",
            "استخدام EC التربة لتحديد مستويات NPK",
        ),
        (
            r"if\s+ec\s*[<>=!]+.*return.*[\"']?[NPK]",
            "CRITICAL",
            "Conditional NPK based on EC value",
            "NPK مشروط بناءً على قيمة EC",
        ),
        # EC in nutrient-related functions
        (
            r"def\s+\w*nutrient\w*.*ec",
            "HIGH",
            "Function name suggests EC-nutrient correlation",
            "اسم الدالة يشير إلى ارتباط EC-المغذيات",
        ),
        (
            r"def\s+calculate_\w+.*\(.*ec",
            "HIGH",
            "EC parameter in calculation function",
            "معامل EC في دالة الحساب",
        ),
    ]

    def __init__(self, service_path: str = "apps/services/agro-advisor"):
        """
        Initialize the EC repair agent.

        Args:
            service_path: Path to the agro-advisor service
        """
        self.service_path = Path(service_path)
        self.issues: List[ECIssue] = []

    def scan(self) -> List[ECIssue]:
        """
        Scan the service for EC misuse patterns.

        Returns:
            List of detected issues
        """
        print(f"🔍 Scanning {self.service_path} for EC misuse...")
        print(f"   فحص {self.service_path} لسوء استخدام EC...")

        self.issues = []

        # Find all Python files
        python_files = list(self.service_path.rglob("*.py"))

        for file_path in python_files:
            self._scan_file(file_path)

        print(f"\n✅ Scan complete. Found {len(self.issues)} issues.")
        print(f"   اكتمل الفحص. تم العثور على {len(self.issues)} مشكلة.")

        return self.issues

    def _scan_file(self, file_path: Path):
        """Scan a single file for EC misuse."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            for pattern, severity, message, message_ar in self.EC_MISUSE_PATTERNS:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    # Find line number
                    line_num = content[: match.start()].count("\n") + 1

                    # Get code snippet (3 lines context)
                    start_line = max(0, line_num - 2)
                    end_line = min(len(lines), line_num + 1)
                    snippet = "\n".join(lines[start_line:end_line])

                    # Create issue
                    issue = ECIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        severity=severity,
                        issue_type="ec_as_nutrient",
                        message=message,
                        message_ar=message_ar,
                        pattern_matched=match.group(0),
                        code_snippet=snippet,
                        suggested_fix=self._generate_fix(match.group(0)),
                    )

                    self.issues.append(issue)

        except Exception as e:
            print(f"⚠️  Error scanning {file_path}: {e}")

    def _generate_fix(self, matched_code: str) -> str:
        """
        Generate suggested fix for EC misuse.

        Args:
            matched_code: The code that matched the pattern

        Returns:
            Suggested fix code
        """
        # Generic fix suggestion
        return """
# ❌ INCORRECT - Using EC as nutrient indicator
# def calculate_fertilizer(ec_value):
#     if ec_value < 0.5:
#         return {"N": 100, "P": 50, "K": 80}

# ✅ CORRECT - Using actual lab nutrient results
def calculate_fertilizer(lab_results: dict):
    '''
    Calculate fertilizer based on actual lab nutrient analysis.
    
    Args:
        lab_results: Dictionary with nutrient levels in mg/kg or ppm
            Required keys: nitrogen_mg_kg, phosphorus_mg_kg, potassium_mg_kg
    
    Returns:
        Dictionary with fertilizer recommendations
    '''
    # Check nitrogen levels (mg/kg)
    if lab_results.get('nitrogen_mg_kg', 0) < 60:
        n_recommendation = 100
    elif lab_results.get('nitrogen_mg_kg', 0) < 90:
        n_recommendation = 75
    else:
        n_recommendation = 50
    
    # Check phosphorus levels (mg/kg)
    if lab_results.get('phosphorus_mg_kg', 0) < 15:
        p_recommendation = 50
    elif lab_results.get('phosphorus_mg_kg', 0) < 25:
        p_recommendation = 30
    else:
        p_recommendation = 20
    
    # Check potassium levels (mg/kg)
    if lab_results.get('potassium_mg_kg', 0) < 150:
        k_recommendation = 80
    elif lab_results.get('potassium_mg_kg', 0) < 250:
        k_recommendation = 60
    else:
        k_recommendation = 40
    
    return {
        "N": n_recommendation,
        "P": p_recommendation,
        "K": k_recommendation
    }

# Note: EC can still be used for salinity assessment, just not for NPK calculation
# ملاحظة: يمكن استخدام EC لتقييم الملوحة، ولكن ليس لحساب NPK
"""

    def print_report(self):
        """Print a human-readable report of issues."""
        if not self.issues:
            print("\n✅ No EC misuse issues found!")
            print("   لم يتم العثور على مشاكل سوء استخدام EC!")
            return

        print("\n" + "=" * 80)
        print("🔍 EC Misuse Detection Report | تقرير اكتشاف سوء استخدام EC")
        print("=" * 80)

        # Group by severity
        by_severity = {}
        for issue in self.issues:
            by_severity.setdefault(issue.severity, []).append(issue)

        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            if severity not in by_severity:
                continue

            issues = by_severity[severity]
            print(f"\n{severity}: {len(issues)} issue(s)")

            for i, issue in enumerate(issues, 1):
                print(f"\n  {i}. {issue.file_path}:{issue.line_number}")
                print(f"     {issue.message}")
                print(f"     {issue.message_ar}")
                print(f"     Pattern: {issue.pattern_matched}")

                if issue.code_snippet:
                    print(f"\n     Code:")
                    for line in issue.code_snippet.split("\n"):
                        print(f"       {line}")

        print("\n" + "=" * 80)
        print(f"Total: {len(self.issues)} issues found")
        print("=" * 80)

    def export_json(self, output_path: str = "/tmp/ec-issues.json"):
        """Export issues to JSON format."""
        import json

        data = {
            "agent": "AgroAdvisorECRepairAgent",
            "version": "16.0.0",
            "service": str(self.service_path),
            "total_issues": len(self.issues),
            "issues": [
                {
                    "file": issue.file_path,
                    "line": issue.line_number,
                    "severity": issue.severity,
                    "type": issue.issue_type,
                    "message": issue.message,
                    "message_ar": issue.message_ar,
                    "pattern": issue.pattern_matched,
                    "snippet": issue.code_snippet,
                }
                for issue in self.issues
            ],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Issues exported to: {output_path}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Kimi EC Repair Agent for Agro Advisor"
    )
    parser.add_argument(
        "--service-path",
        default="apps/services/agro-advisor",
        help="Path to agro-advisor service",
    )
    parser.add_argument("--scan", action="store_true", help="Scan for EC misuse")
    parser.add_argument(
        "--export-json", help="Export issues to JSON file"
    )

    args = parser.parse_args()

    agent = AgroAdvisorECRepairAgent(service_path=args.service_path)

    if args.scan:
        agent.scan()
        agent.print_report()

        if args.export_json:
            agent.export_json(args.export_json)


if __name__ == "__main__":
    main()
