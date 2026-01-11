#!/usr/bin/env python3
"""
SAHOOL Project Analyzer
فاحص مشروع سهول

Scans the entire project using Code Fix Agent API.
يفحص المشروع بالكامل باستخدام وكيل إصلاح الكود.

Usage:
    python scripts/analyze_project.py [--path PATH] [--output OUTPUT]
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import httpx

# Configuration
AGENT_URL = os.getenv("CODE_FIX_AGENT_URL", "http://localhost:8090")
SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "typescript",
    ".dart": "dart",
}

# Directories to skip
SKIP_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "dist",
    "build",
    ".next",
    "coverage",
    ".pytest_cache",
    ".mypy_cache",
    "eggs",
    "*.egg-info",
    "archive",  # Skip archived/legacy code
    "vendor",
    "migrations",
}

# Files to skip
SKIP_FILES = {
    "*.min.js",
    "*.bundle.js",
    "package-lock.json",
    "yarn.lock",
}


class ProjectAnalyzer:
    """فاحص المشروع"""

    def __init__(self, base_url: str = AGENT_URL):
        self.base_url = base_url
        self.results = {
            "scan_time": datetime.utcnow().isoformat(),
            "total_files": 0,
            "files_analyzed": 0,
            "files_with_issues": 0,
            "total_issues": 0,
            "issues_by_severity": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "issues_by_type": {},
            "files": [],
        }

    def should_skip(self, path: Path) -> bool:
        """Check if path should be skipped"""
        # Skip directories
        for skip_dir in SKIP_DIRS:
            if skip_dir in path.parts:
                return True

        # Skip files
        for skip_file in SKIP_FILES:
            if path.match(skip_file):
                return True

        return False

    def get_language(self, path: Path) -> str | None:
        """Get language from file extension"""
        return SUPPORTED_EXTENSIONS.get(path.suffix.lower())

    async def analyze_file(self, file_path: Path, client: httpx.AsyncClient) -> dict:
        """Analyze a single file"""
        language = self.get_language(file_path)
        if not language:
            return None

        try:
            code = file_path.read_text(encoding="utf-8", errors="ignore")

            # Skip empty or very large files
            if not code.strip():
                return {"skipped": True, "reason": "empty"}
            if len(code) > 100000:
                return {"skipped": True, "reason": "too_large"}

            response = await client.post(
                f"{self.base_url}/api/v1/analyze",
                json={
                    "code": code,
                    "language": language,
                    "file_path": str(file_path),
                },
                timeout=30.0,
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    async def scan_directory(self, root_path: Path, max_files: int = 500) -> dict:
        """Scan entire directory"""
        print(f"\n🔍 فحص المشروع: {root_path}")
        print(f"   Scanning project: {root_path}\n")

        files_to_analyze = []

        # Collect files
        for ext in SUPPORTED_EXTENSIONS.keys():
            for file_path in root_path.rglob(f"*{ext}"):
                if not self.should_skip(file_path):
                    files_to_analyze.append(file_path)

        self.results["total_files"] = len(files_to_analyze)

        if len(files_to_analyze) > max_files:
            print(f"⚠️  تم العثور على {len(files_to_analyze)} ملف، سيتم فحص أول {max_files}")
            files_to_analyze = files_to_analyze[:max_files]

        print(f"📁 الملفات للفحص: {len(files_to_analyze)}")
        print("-" * 50)

        async with httpx.AsyncClient() as client:
            # Check if agent is running
            try:
                health = await client.get(f"{self.base_url}/healthz", timeout=5.0)
                if health.status_code != 200:
                    print("❌ وكيل إصلاح الكود غير متاح!")
                    print("   Code Fix Agent is not available!")
                    print(f"   تأكد من تشغيله على: {self.base_url}")
                    return self.results
            except Exception:
                print("❌ لا يمكن الاتصال بوكيل إصلاح الكود!")
                print(f"   Cannot connect to Code Fix Agent at {self.base_url}")
                return self.results

            # Analyze files with progress
            for i, file_path in enumerate(files_to_analyze, 1):
                relative_path = file_path.relative_to(root_path)
                print(f"[{i}/{len(files_to_analyze)}] {relative_path}...", end=" ")

                result = await self.analyze_file(file_path, client)

                if result and result.get("skipped"):
                    print(f"⏭️  {result.get('reason', 'skipped')}")
                    continue

                if result and result.get("success"):
                    self.results["files_analyzed"] += 1

                    data = result.get("data", {})
                    issues = data.get("issues", [])
                    issues_count = data.get("issues_count", len(issues))

                    if issues_count > 0:
                        self.results["files_with_issues"] += 1
                        self.results["total_issues"] += issues_count

                        # Count by type
                        for issue in issues:
                            issue_type = issue.get("type", "unknown")
                            self.results["issues_by_type"][issue_type] = (
                                self.results["issues_by_type"].get(issue_type, 0) + 1
                            )

                            # Count by severity
                            severity = issue.get("severity", "medium").lower()
                            if severity in self.results["issues_by_severity"]:
                                self.results["issues_by_severity"][severity] += 1

                        print(f"⚠️  {issues_count} مشكلة")

                        self.results["files"].append(
                            {
                                "path": str(relative_path),
                                "language": self.get_language(file_path),
                                "issues_count": issues_count,
                                "issues": issues[:10],  # Limit stored issues
                                "metrics": data.get("metrics", {}),
                            }
                        )
                    else:
                        print("✅")
                elif result and result.get("error"):
                    print(f"❌ {str(result.get('error', ''))[:50]}")
                else:
                    print("⏭️  تخطي")

        return self.results

    def generate_report(self, output_path: str = None) -> str:
        """Generate analysis report"""
        report = []
        report.append("=" * 60)
        report.append("📊 تقرير فحص مشروع سهول")
        report.append("   SAHOOL Project Analysis Report")
        report.append("=" * 60)
        report.append(f"\n⏰ وقت الفحص: {self.results['scan_time']}")
        report.append(f"\n📁 إحصائيات الملفات:")
        report.append(f"   - إجمالي الملفات: {self.results['total_files']}")
        report.append(f"   - الملفات المفحوصة: {self.results['files_analyzed']}")
        report.append(f"   - ملفات بها مشاكل: {self.results['files_with_issues']}")
        report.append(f"\n🐛 إحصائيات المشاكل:")
        report.append(f"   - إجمالي المشاكل: {self.results['total_issues']}")
        report.append(f"\n📈 المشاكل حسب الخطورة:")
        for severity, count in self.results["issues_by_severity"].items():
            if count > 0:
                emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(
                    severity, "⚪"
                )
                report.append(f"   {emoji} {severity}: {count}")

        if self.results["issues_by_type"]:
            report.append(f"\n📋 المشاكل حسب النوع:")
            for issue_type, count in sorted(
                self.results["issues_by_type"].items(), key=lambda x: -x[1]
            )[:10]:
                report.append(f"   - {issue_type}: {count}")

        if self.results["files_with_issues"] > 0:
            report.append(f"\n📄 الملفات التي تحتاج مراجعة:")
            for file_info in sorted(
                self.results["files"], key=lambda x: -x["issues_count"]
            )[:20]:
                report.append(f"   - {file_info['path']} ({file_info['issues_count']} مشكلة)")

        report.append("\n" + "=" * 60)

        report_text = "\n".join(report)

        if output_path:
            # Save JSON results
            json_path = output_path.replace(".txt", ".json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)

            # Save text report
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report_text)

            print(f"\n💾 تم حفظ التقرير: {output_path}")
            print(f"💾 تم حفظ النتائج: {json_path}")

        return report_text


async def main():
    parser = argparse.ArgumentParser(description="SAHOOL Project Analyzer")
    parser.add_argument(
        "--path",
        default=".",
        help="Path to project root (default: current directory)",
    )
    parser.add_argument(
        "--output",
        default="analysis_report.txt",
        help="Output file path (default: analysis_report.txt)",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=500,
        help="Maximum files to analyze (default: 500)",
    )
    parser.add_argument(
        "--agent-url",
        default=AGENT_URL,
        help=f"Code Fix Agent URL (default: {AGENT_URL})",
    )

    args = parser.parse_args()

    analyzer = ProjectAnalyzer(base_url=args.agent_url)
    root_path = Path(args.path).resolve()

    if not root_path.exists():
        print(f"❌ المسار غير موجود: {root_path}")
        sys.exit(1)

    results = await analyzer.scan_directory(root_path, max_files=args.max_files)
    report = analyzer.generate_report(args.output)

    print(report)


if __name__ == "__main__":
    asyncio.run(main())
