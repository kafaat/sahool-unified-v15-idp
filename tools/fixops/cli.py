#!/usr/bin/env python3
"""
SAHOOL FixOps CLI - Kimi Repair Agent
أداة سطر الأوامر لـ FixOps - وكيل Kimi للإصلاح

Usage:
    python -m tools.fixops.cli [options]

    # Or via script:
    ./scripts/fixops.sh [options]

Examples:
    # Preview mode (dry-run)
    python -m tools.fixops.cli --dry-run

    # Run with safe strategy
    python -m tools.fixops.cli --strategy safe

    # Run on specific path
    python -m tools.fixops.cli --path apps/services/

    # Full repair with comprehensive strategy
    python -m tools.fixops.cli --strategy comprehensive --no-dry-run
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from tools.fixops.orchestrator import FixOpsOrchestrator, FixOpsConfig


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="SAHOOL FixOps CLI - Kimi Repair Agent | وكيل Kimi للإصلاح",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples | أمثلة:
  %(prog)s --dry-run                    # Preview mode | وضع المعاينة
  %(prog)s --strategy safe              # Safe fixes | إصلاحات آمنة
  %(prog)s --strategy comprehensive     # All fixes | جميع الإصلاحات
  %(prog)s --path apps/services/        # Specific path | مسار محدد
  %(prog)s --output ./reports           # Custom output | مخرجات مخصصة
        """,
    )

    parser.add_argument(
        "--path",
        "-p",
        type=Path,
        default=REPO_ROOT,
        help="Repository root path (default: current repo) | مسار المستودع",
    )

    parser.add_argument(
        "--strategy",
        "-s",
        choices=["minimal", "safe", "comprehensive", "refactor"],
        default="safe",
        help="Fix strategy: minimal, safe, comprehensive, refactor (default: safe) | استراتيجية الإصلاح",
    )

    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        default=True,
        help="Preview mode - don't apply fixes (default: True) | وضع المعاينة",
    )

    parser.add_argument(
        "--no-dry-run",
        "-n",
        action="store_true",
        help="Apply fixes (disable dry-run) | تطبيق الإصلاحات",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Output directory for reports (default: .fixops/) | مجلد المخرجات",
    )

    parser.add_argument(
        "--max-files",
        "-m",
        type=int,
        default=20,
        help="Maximum files to change (default: 20) | أقصى عدد ملفات",
    )

    parser.add_argument(
        "--python",
        action="store_true",
        default=True,
        help="Analyze Python files (default: True) | تحليل ملفات Python",
    )

    parser.add_argument(
        "--typescript",
        action="store_true",
        default=True,
        help="Analyze TypeScript files (default: True) | تحليل ملفات TypeScript",
    )

    parser.add_argument(
        "--dart",
        action="store_true",
        default=False,
        help="Analyze Dart/Flutter files (default: False) | تحليل ملفات Dart",
    )

    parser.add_argument(
        "--no-auto-fix",
        action="store_true",
        help="Disable auto-fix engine | تعطيل محرك الإصلاح التلقائي",
    )

    parser.add_argument(
        "--no-audit",
        action="store_true",
        help="Disable audit logging | تعطيل سجل التدقيق",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output | مخرجات تفصيلية",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON | المخرجات بصيغة JSON",
    )

    return parser.parse_args()


def print_banner():
    """Print CLI banner."""
    banner = """
╔════════════════════════════════════════════════════════════╗
║   🔧 SAHOOL FixOps - Kimi Repair Agent                    ║
║   وكيل Kimi للإصلاح التلقائي                               ║
╚════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_summary(summary, verbose: bool = False, as_json: bool = False):
    """Print fix summary."""
    import json

    if as_json:
        output = {
            "id": summary.id,
            "status": summary.status,
            "total_issues": summary.analysis.total_issues if summary.analysis else 0,
            "by_severity": summary.analysis.by_severity if summary.analysis else {},
            "by_category": summary.analysis.by_category if summary.analysis else {},
            "fixes_applied": len(summary.actions.get("fixes_applied", [])) if summary.actions else 0,
            "files_modified": summary.actions.get("files_modified", []) if summary.actions else [],
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return

    print("\n" + "=" * 60)
    print("📊 FixOps Summary | ملخص FixOps")
    print("=" * 60)

    print(f"\n🆔 Run ID: {summary.id}")
    print(f"📁 Status: {summary.status}")

    if summary.analysis:
        print(f"\n📈 Total Issues | إجمالي المشاكل: {summary.analysis.total_issues}")

        print("\n🔴 By Severity | حسب الخطورة:")
        for severity, count in summary.analysis.by_severity.items():
            emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(severity, "⚪")
            print(f"   {emoji} {severity}: {count}")

        print("\n📂 By Category | حسب الفئة:")
        for category, count in summary.analysis.by_category.items():
            emoji = {"security": "🔒", "bug": "🐛", "style": "🎨", "performance": "⚡"}.get(category, "📁")
            print(f"   {emoji} {category}: {count}")

    if summary.actions:
        fixes_applied = len(summary.actions.get("fixes_applied", []))
        files_modified = summary.actions.get("files_modified", [])

        print(f"\n✅ Fixes Applied | الإصلاحات المطبقة: {fixes_applied}")

        if files_modified and verbose:
            print("\n📝 Files Modified | الملفات المعدلة:")
            for f in files_modified[:10]:
                print(f"   • {f}")
            if len(files_modified) > 10:
                print(f"   ... and {len(files_modified) - 10} more")

    print("\n" + "=" * 60)


async def main():
    """Main entry point."""
    args = parse_args()

    if not args.json:
        print_banner()

    # Determine dry_run setting
    dry_run = not args.no_dry_run

    if not args.json:
        mode = "🔍 Preview Mode (dry-run)" if dry_run else "🔧 Apply Mode"
        print(f"\n{mode}")
        print(f"📂 Path: {args.path}")
        print(f"📋 Strategy: {args.strategy}")
        print(f"📊 Max Files: {args.max_files}")
        print()

    # Create config
    config = FixOpsConfig(
        repo_root=args.path,
        output_dir=args.output or args.path / ".fixops",
        dry_run=dry_run,
        max_files_changed=args.max_files,
        fix_strategy=args.strategy,
        enable_auto_fix=not args.no_auto_fix,
        enable_audit=not args.no_audit,
        analyze_python=args.python,
        analyze_typescript=args.typescript,
        analyze_dart=args.dart,
        use_auto_fix_engine=not args.no_auto_fix,
        use_audit_logger=not args.no_audit,
    )

    if not args.json:
        print("🚀 Starting FixOps analysis... | بدء تحليل FixOps...")
        print()

    try:
        # Run orchestrator
        orchestrator = FixOpsOrchestrator(config)
        summary = await orchestrator.run()

        # Print results
        print_summary(summary, verbose=args.verbose, as_json=args.json)

        if not args.json:
            output_file = config.output_dir / f"fixops_summary_{summary.id}.json"
            print(f"\n💾 Report saved to: {output_file}")

            if dry_run:
                print("\n💡 Tip: Use --no-dry-run to apply fixes | نصيحة: استخدم --no-dry-run لتطبيق الإصلاحات")

        return 0

    except Exception as e:
        if args.json:
            import json

            print(json.dumps({"error": str(e)}, ensure_ascii=False))
        else:
            print(f"\n❌ Error | خطأ: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
