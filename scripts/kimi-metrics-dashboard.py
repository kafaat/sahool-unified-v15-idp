#!/usr/bin/env python3
"""
Kimi Repair Agent Metrics Dashboard
====================================
لوحة معلومات مقاييس وكيل إصلاح Kimi

Collects and visualizes metrics from Kimi Repair Agent operations.
جمع وتصور المقاييس من عمليات وكيل إصلاح Kimi.

Usage:
    python scripts/kimi-metrics-dashboard.py [--output-dir /path/to/output]

Author: SAHOOL Platform Team
Version: 16.0.0
"""

import argparse
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Try importing matplotlib for visualization
try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("⚠️  matplotlib not installed. Visualizations will be skipped.")
    print("   Install with: pip install matplotlib")


class KimiMetricsDashboard:
    """
    Kimi Repair Agent Metrics Dashboard
    لوحة معلومات مقاييس وكيل إصلاح Kimi
    """

    def __init__(self, db_path: str = "/tmp/kimi-metrics.db"):
        """
        Initialize metrics dashboard.

        Args:
            db_path: Path to metrics SQLite database
        """
        self.db_path = Path(db_path)
        self.ensure_database()

    def ensure_database(self):
        """Create database and tables if they don't exist."""
        if not self.db_path.exists():
            print(f"📊 Creating new metrics database: {self.db_path}")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Issues table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS issues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    file_path TEXT,
                    issue_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    tool TEXT,
                    auto_fixed INTEGER DEFAULT 0,
                    time_saved_hours REAL DEFAULT 0,
                    category TEXT,
                    service_name TEXT
                )
            """)

            # Scans table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_issues INTEGER DEFAULT 0,
                    auto_fixed INTEGER DEFAULT 0,
                    critical_prevented INTEGER DEFAULT 0,
                    duration_seconds REAL,
                    success INTEGER DEFAULT 1
                )
            """)

            # Fixes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fixes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    issue_id INTEGER,
                    strategy TEXT,
                    success INTEGER DEFAULT 1,
                    time_saved_hours REAL DEFAULT 0,
                    FOREIGN KEY (issue_id) REFERENCES issues(id)
                )
            """)

            conn.commit()
            print("✅ Database schema verified")

    def add_sample_data(self, days: int = 30):
        """
        Add sample data for demonstration.

        Args:
            days: Number of days of sample data to generate
        """
        import random

        print(f"📝 Adding {days} days of sample data...")

        issue_types = [
            "ec_as_nutrient",
            "unoptimized_ml_model",
            "security_vulnerability",
            "code_style_violation",
            "performance_bottleneck",
        ]

        severities = ["critical", "high", "medium", "low"]
        tools = ["ruff", "bandit", "mypy", "eslint"]
        categories = ["security", "performance", "style", "logic"]
        services = [
            "agro-advisor",
            "yield-prediction",
            "crop-intelligence-service",
        ]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            for day in range(days):
                date = datetime.now() - timedelta(days=days - day)
                date_str = date.isoformat()

                # Add scan record
                total_issues = random.randint(10, 50)
                auto_fixed = int(total_issues * random.uniform(0.6, 0.9))
                critical_prevented = random.randint(0, 5)

                cursor.execute(
                    """
                    INSERT INTO scans (timestamp, total_issues, auto_fixed, 
                                       critical_prevented, duration_seconds, success)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (date_str, total_issues, auto_fixed, critical_prevented,
                     random.uniform(60, 300), 1),
                )

                # Add issues
                for _ in range(total_issues):
                    issue_timestamp = (date + timedelta(minutes=random.randint(0, 1440))).isoformat()
                    cursor.execute(
                        """
                        INSERT INTO issues (timestamp, file_path, issue_type, severity,
                                            tool, auto_fixed, time_saved_hours, category,
                                            service_name)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            issue_timestamp,
                            f"apps/services/{random.choice(services)}/src/main.py",
                            random.choice(issue_types),
                            random.choice(severities),
                            random.choice(tools),
                            random.choice([0, 1]),
                            random.uniform(0.1, 2.0),
                            random.choice(categories),
                            random.choice(services),
                        ),
                    )

            conn.commit()
            print("✅ Sample data added successfully")

    def get_summary_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        Get summary statistics for the last N days.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with summary statistics
        """
        since_date = (datetime.now() - timedelta(days=days)).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Total issues
            cursor.execute(
                "SELECT COUNT(*) FROM issues WHERE timestamp >= ?", (since_date,)
            )
            total_issues = cursor.fetchone()[0]

            # Auto-fixed
            cursor.execute(
                "SELECT COUNT(*) FROM issues WHERE timestamp >= ? AND auto_fixed = 1",
                (since_date,),
            )
            auto_fixed = cursor.fetchone()[0]

            # Critical prevented
            cursor.execute(
                """SELECT COUNT(*) FROM issues 
                   WHERE timestamp >= ? AND severity = 'critical'""",
                (since_date,),
            )
            critical_prevented = cursor.fetchone()[0]

            # Time saved
            cursor.execute(
                """SELECT SUM(time_saved_hours) FROM issues 
                   WHERE timestamp >= ? AND auto_fixed = 1""",
                (since_date,),
            )
            time_saved = cursor.fetchone()[0] or 0

            # By severity
            cursor.execute(
                """SELECT severity, COUNT(*) FROM issues 
                   WHERE timestamp >= ? GROUP BY severity""",
                (since_date,),
            )
            by_severity = dict(cursor.fetchall())

            # By category
            cursor.execute(
                """SELECT category, COUNT(*) FROM issues 
                   WHERE timestamp >= ? GROUP BY category""",
                (since_date,),
            )
            by_category = dict(cursor.fetchall())

            # By service
            cursor.execute(
                """SELECT service_name, COUNT(*) FROM issues 
                   WHERE timestamp >= ? GROUP BY service_name""",
                (since_date,),
            )
            by_service = dict(cursor.fetchall())

            return {
                "total_issues": total_issues,
                "auto_fixed": auto_fixed,
                "auto_fix_rate": (auto_fixed / total_issues * 100) if total_issues > 0 else 0,
                "critical_prevented": critical_prevented,
                "time_saved_hours": round(time_saved, 1),
                "by_severity": by_severity,
                "by_category": by_category,
                "by_service": by_service,
            }

    def generate_monthly_report(self, output_dir: str = "/tmp") -> Dict[str, Any]:
        """
        Generate monthly report with statistics and visualizations.

        Args:
            output_dir: Directory to save report files

        Returns:
            Summary statistics dictionary
        """
        print("\n" + "=" * 80)
        print("📊 Kimi Repair Agent Performance - Last 30 Days")
        print("   أداء وكيل إصلاح Kimi - آخر 30 يوماً")
        print("=" * 80 + "\n")

        stats = self.get_summary_stats(days=30)

        # Print summary
        print(f"📈 Summary Statistics | إحصائيات ملخصة:")
        print(f"   Total Issues Found     | المشكلات المكتشفة:     {stats['total_issues']:>6}")
        print(f"   Auto-Fixed             | الإصلاح التلقائي:       {stats['auto_fixed']:>6} ({stats['auto_fix_rate']:.1f}%)")
        print(f"   Critical Prevented     | الحرجة الممنوعة:        {stats['critical_prevented']:>6}")
        print(f"   Time Saved (hours)     | الوقت الموفر (ساعات):   {stats['time_saved_hours']:>6.1f}")
        print()

        print(f"📊 By Severity | حسب الخطورة:")
        for severity, count in sorted(stats['by_severity'].items(), key=lambda x: -x[1]):
            print(f"   {severity:20} {count:>6}")
        print()

        print(f"📂 By Category | حسب الفئة:")
        for category, count in sorted(stats['by_category'].items(), key=lambda x: -x[1]):
            print(f"   {category:20} {count:>6}")
        print()

        print(f"🔧 By Service | حسب الخدمة:")
        for service, count in sorted(stats['by_service'].items(), key=lambda x: -x[1]):
            print(f"   {service:30} {count:>6}")
        print()

        # Generate visualizations if matplotlib is available
        if HAS_MATPLOTLIB:
            self._generate_visualizations(stats, output_dir)

        # Save JSON report
        report_path = Path(output_dir) / "kimi-metrics-report.json"
        with open(report_path, "w") as f:
            json.dump(stats, f, indent=2)
        print(f"💾 JSON report saved: {report_path}")

        return stats

    def _generate_visualizations(self, stats: Dict[str, Any], output_dir: str):
        """Generate visualization charts."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle("Kimi Repair Agent Metrics - Last 30 Days", fontsize=16)

        # 1. Summary bar chart
        ax1 = axes[0, 0]
        categories = ["Issues Found", "Auto-Fixed", "Critical Prevented"]
        values = [
            stats["total_issues"],
            stats["auto_fixed"],
            stats["critical_prevented"],
        ]
        colors = ["#3498db", "#2ecc71", "#e74c3c"]
        ax1.bar(categories, values, color=colors)
        ax1.set_title("Overall Summary")
        ax1.set_ylabel("Count")
        ax1.grid(axis="y", alpha=0.3)

        # Add value labels on bars
        for i, v in enumerate(values):
            ax1.text(i, v, str(v), ha="center", va="bottom")

        # 2. By severity pie chart
        ax2 = axes[0, 1]
        if stats["by_severity"]:
            severity_colors = {
                "critical": "#e74c3c",
                "high": "#f39c12",
                "medium": "#f1c40f",
                "low": "#3498db",
            }
            labels = list(stats["by_severity"].keys())
            sizes = list(stats["by_severity"].values())
            colors = [severity_colors.get(s, "#95a5a6") for s in labels]
            ax2.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors,
                    startangle=90)
            ax2.set_title("Issues by Severity")
        else:
            ax2.text(0.5, 0.5, "No data", ha="center", va="center")

        # 3. By category bar chart
        ax3 = axes[1, 0]
        if stats["by_category"]:
            categories = list(stats["by_category"].keys())
            counts = list(stats["by_category"].values())
            ax3.barh(categories, counts, color="#9b59b6")
            ax3.set_title("Issues by Category")
            ax3.set_xlabel("Count")
            ax3.grid(axis="x", alpha=0.3)
        else:
            ax3.text(0.5, 0.5, "No data", ha="center", va="center")

        # 4. Time saved metrics
        ax4 = axes[1, 1]
        metrics = [
            "Time Saved\n(hours)",
            "Auto-Fix Rate\n(%)",
        ]
        values = [stats["time_saved_hours"], stats["auto_fix_rate"]]
        colors = ["#1abc9c", "#3498db"]
        bars = ax4.bar(metrics, values, color=colors)
        ax4.set_title("Efficiency Metrics")
        ax4.set_ylabel("Value")
        ax4.grid(axis="y", alpha=0.3)

        # Add value labels
        for bar, val in zip(bars, values):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width() / 2, height,
                    f"{val:.1f}", ha="center", va="bottom")

        plt.tight_layout()

        # Save figure
        chart_path = output_path / "kimi-metrics.png"
        plt.savefig(chart_path, dpi=150, bbox_inches="tight")
        print(f"📊 Chart saved: {chart_path}")

        plt.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Kimi Repair Agent Metrics Dashboard"
    )
    parser.add_argument(
        "--db-path",
        default="/tmp/kimi-metrics.db",
        help="Path to metrics database",
    )
    parser.add_argument(
        "--output-dir", default="/tmp", help="Output directory for reports"
    )
    parser.add_argument(
        "--add-sample-data",
        action="store_true",
        help="Add sample data for demonstration",
    )
    parser.add_argument(
        "--days", type=int, default=30, help="Number of days to analyze"
    )

    args = parser.parse_args()

    dashboard = KimiMetricsDashboard(db_path=args.db_path)

    if args.add_sample_data:
        dashboard.add_sample_data(days=args.days)

    dashboard.generate_monthly_report(output_dir=args.output_dir)

    print("\n" + "=" * 80)
    print("✅ Metrics dashboard generation complete!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
