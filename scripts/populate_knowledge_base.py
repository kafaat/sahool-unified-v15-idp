#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════════
# Knowledge Base Population Script
# سكريبت تعبئة قاعدة المعرفة الزراعية
# ═══════════════════════════════════════════════════════════════════════════════
#
# Usage:
#   python scripts/populate_knowledge_base.py --source docs
#   python scripts/populate_knowledge_base.py --source code
#   python scripts/populate_knowledge_base.py --source all
#   python scripts/populate_knowledge_base.py --source all --dry-run
#   python scripts/populate_knowledge_base.py --source all --verify
#   python scripts/populate_knowledge_base.py --status
#
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.ai.knowledge.collection_populator import KnowledgeBasePopulator, PopulationReport
from shared.ai.knowledge.ingestion.pipeline import KnowledgeIngestionPipeline
from shared.ai.knowledge.sources.registry import KnowledgeSourceRegistry
from shared.ai.knowledge.validators import KnowledgeValidator


def print_report(report: PopulationReport) -> None:
    """Print a formatted population report."""
    print("\n" + "=" * 60)
    print("  Knowledge Base Population Report")
    print("  تقرير تعبئة قاعدة المعرفة")
    print("=" * 60)
    print(f"\n  Total files:    {report.total_files}")
    print(f"  Ingested:       {report.total_ingested}")
    print(f"  Failed:         {report.total_failed}")
    print(f"  Skipped:        {report.total_skipped}")

    if report.by_collection:
        print("\n  By Collection:")
        print("  " + "-" * 40)
        for coll, count in sorted(report.by_collection.items()):
            print(f"    {coll:<35} {count:>3}")

    if report.by_domain:
        print("\n  By Domain:")
        print("  " + "-" * 40)
        for domain, count in sorted(report.by_domain.items()):
            print(f"    {domain:<35} {count:>3}")

    if report.errors:
        print(f"\n  Errors ({len(report.errors)}):")
        print("  " + "-" * 40)
        for err in report.errors[:10]:
            print(f"    - {err}")
        if len(report.errors) > 10:
            print(f"    ... and {len(report.errors) - 10} more")

    print("\n" + "=" * 60)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Populate SAHOOL agricultural knowledge base / تعبئة قاعدة المعرفة الزراعية"
    )
    parser.add_argument(
        "--source",
        choices=["docs", "code", "all"],
        default="all",
        help="Source to populate from (docs, code, or all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without actual ingestion",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run verification agent on content",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show current population status",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )
    parser.add_argument(
        "--docs-path",
        default="docs/knowledge-base",
        help="Path to knowledge base docs",
    )

    args = parser.parse_args()

    # Initialize components
    registry = KnowledgeSourceRegistry()
    validator = KnowledgeValidator()
    pipeline = KnowledgeIngestionPipeline(
        source_registry=registry,
        validator=validator,
        min_source_credibility=1,
        require_bilingual=args.verify,
    )
    populator = KnowledgeBasePopulator(
        pipeline=pipeline,
        base_docs_path=args.docs_path,
        verify=args.verify,
    )

    if args.status:
        status = populator.get_population_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print("\n  Knowledge Base Population Status")
            print("  " + "=" * 50)
            for coll, info in status["collections"].items():
                files = info["files_available"]
                dirs = ", ".join(info["directories"]) or "N/A"
                print(f"    {coll:<35} {files:>3} files  ({dirs})")
            print(f"\n    Total files available: {status['total_files']}")
        return 0

    # Run population
    if args.source == "docs":
        report = populator.populate_from_docs(dry_run=args.dry_run)
    elif args.source == "code":
        report = populator.populate_from_code_modules(dry_run=args.dry_run)
    else:
        report = populator.populate_all(dry_run=args.dry_run)

    if args.json:
        print(
            json.dumps(
                {
                    "total_files": report.total_files,
                    "total_ingested": report.total_ingested,
                    "total_failed": report.total_failed,
                    "total_skipped": report.total_skipped,
                    "by_collection": report.by_collection,
                    "by_domain": report.by_domain,
                    "errors": report.errors,
                },
                indent=2,
            )
        )
    else:
        if args.dry_run:
            print("\n  [DRY RUN] No actual ingestion performed")
        print_report(report)

    return 0 if report.total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
