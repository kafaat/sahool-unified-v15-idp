# ═══════════════════════════════════════════════════════════════════════════════
# Knowledge Base CLI (GAP-15)
# واجهة سطر الأوامر لإدارة قاعدة المعرفة الزراعية
# ═══════════════════════════════════════════════════════════════════════════════
#
# Dependency-free CLI using only stdlib (argparse) + project imports.
#
# Usage:
#   python -m shared.ai.knowledge.cli ingest docs/knowledge-base/crops/
#   python -m shared.ai.knowledge.cli ingest docs/knowledge-base/crops/wheat.md
#   python -m shared.ai.knowledge.cli ingest docs/knowledge-base/ -r
#   python -m shared.ai.knowledge.cli validate docs/knowledge-base/crops/wheat.md
#   python -m shared.ai.knowledge.cli collections
#   python -m shared.ai.knowledge.cli status
#   python -m shared.ai.knowledge.cli freshness --warning-days 60
#   python -m shared.ai.knowledge.cli stats
#
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)


class KnowledgeCLI:
    """Command-line interface for knowledge base management.
    واجهة سطر الأوامر لإدارة قاعدة المعرفة"""

    def __init__(self) -> None:
        self._parser = self._build_parser()

    def _build_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog="sahool-knowledge",
            description="SAHOOL Agricultural Knowledge Base Manager | مدير قاعدة المعرفة الزراعية",
        )
        subparsers = parser.add_subparsers(dest="command", help="Available commands | الأوامر المتاحة")

        # ingest - Ingest files or directories
        ingest_parser = subparsers.add_parser(
            "ingest",
            help="Ingest knowledge files | استيعاب ملفات المعرفة",
        )
        ingest_parser.add_argument("path", help="File or directory path | مسار الملف أو المجلد")
        ingest_parser.add_argument(
            "--collection",
            "-c",
            default=None,
            help="Target collection name | اسم المجموعة المستهدفة",
        )
        ingest_parser.add_argument(
            "--source-url",
            "-s",
            default="",
            help="Source URL for provenance | رابط المصدر",
        )
        ingest_parser.add_argument(
            "--recursive",
            "-r",
            action="store_true",
            help="Recursive directory scan | فحص المجلدات الفرعية",
        )
        ingest_parser.add_argument(
            "--patterns",
            "-p",
            nargs="+",
            default=["*.md", "*.txt"],
            help="File glob patterns (default: *.md *.txt) | أنماط الملفات",
        )

        # validate - Validate knowledge files
        validate_parser = subparsers.add_parser(
            "validate",
            help="Validate knowledge files | التحقق من ملفات المعرفة",
        )
        validate_parser.add_argument("path", help="File or directory path | مسار الملف أو المجلد")

        # status - Show knowledge base status
        subparsers.add_parser(
            "status",
            help="Show knowledge base status | عرض حالة قاعدة المعرفة",
        )

        # collections - List collections
        subparsers.add_parser(
            "collections",
            help="List all collections | قائمة المجموعات",
        )

        # freshness - Check document freshness
        freshness_parser = subparsers.add_parser(
            "freshness",
            help="Check document freshness | فحص حداثة الوثائق",
        )
        freshness_parser.add_argument(
            "--warning-days",
            "-w",
            type=int,
            default=30,
            help="Days before expiry to warn (default: 30) | أيام التحذير قبل انتهاء الصلاحية",
        )

        # stats - Show statistics
        subparsers.add_parser(
            "stats",
            help="Show statistics | عرض الإحصائيات",
        )

        return parser

    def run(self, args: list[str] | None = None) -> int:
        """Run CLI with given args. Returns exit code (0=success).
        تشغيل واجهة سطر الأوامر. يعيد رمز الخروج (0=نجاح)"""
        parsed = self._parser.parse_args(args)
        if not parsed.command:
            self._parser.print_help()
            return 1

        handler = getattr(self, f"_cmd_{parsed.command}", None)
        if handler is None:
            print(f"Error: Unknown command '{parsed.command}'")
            return 1

        try:
            return handler(parsed)
        except KeyboardInterrupt:
            print("\nOperation cancelled. | تم إلغاء العملية.")
            return 130
        except Exception as exc:
            logger.error("cli_error", command=parsed.command, error=str(exc))
            print(f"Error: {exc}")
            return 1

    # ─── Command Handlers ──────────────────────────────────────────────────────

    def _cmd_ingest(self, args: argparse.Namespace) -> int:
        """Handle ingest command.
        معالجة أمر الاستيعاب"""
        from .ingestion.pipeline import KnowledgeIngestionPipeline

        path = Path(args.path)
        if not path.exists():
            print(f"Error: Path not found: {path}")
            print(f"خطأ: المسار غير موجود: {path}")
            return 1

        pipeline = KnowledgeIngestionPipeline()
        start_time = time.monotonic()

        if path.is_file():
            print(f"Ingesting file: {path}")
            print(f"استيعاب ملف: {path}")
            result = pipeline.ingest_file(
                file_path=path,
                source_url=args.source_url,
                target_collection=args.collection,
            )
            elapsed = time.monotonic() - start_time

            print()
            print("=" * 60)
            print("Ingestion Result | نتيجة الاستيعاب")
            print("=" * 60)
            print(f"  Document ID : {result.document_id}")
            print(f"  Success     : {'Yes' if result.success else 'No'}")
            print(f"  Collection  : {result.collection}")
            print(f"  Credibility : {result.source_credibility}/5")
            print(f"  Domains     : {', '.join(result.domains_detected) or 'none'}")
            print(f"  Regions     : {', '.join(result.regions_detected) or 'none'}")
            print(f"  Tags        : {', '.join(result.tags) or 'none'}")
            print(f"  Time        : {elapsed:.2f}s")

            if result.errors:
                print()
                print("Errors | أخطاء:")
                for err in result.errors:
                    print(f"  [!] {err}")

            if result.warnings:
                print()
                print("Warnings | تحذيرات:")
                for warn in result.warnings:
                    print(f"  [~] {warn}")

            return 0 if result.success else 1

        elif path.is_dir():
            if args.recursive:
                print(f"Ingesting directory (recursive): {path}")
                print(f"استيعاب مجلد (بشكل متكرر): {path}")
                # Collect files recursively using rglob
                all_files: list[Path] = []
                for pattern in args.patterns:
                    all_files.extend(path.rglob(pattern))
                # Deduplicate and sort
                all_files = sorted(set(all_files))

                total = len(all_files)
                succeeded = 0
                failed = 0
                skipped = 0
                by_collection: dict[str, int] = {}
                by_domain: dict[str, int] = {}

                for file_path in all_files:
                    if file_path.name.startswith(".") or file_path.name == "README.md":
                        skipped += 1
                        continue
                    result = pipeline.ingest_file(
                        file_path=file_path,
                        source_url=args.source_url,
                        target_collection=args.collection,
                    )
                    if result.success:
                        succeeded += 1
                        by_collection[result.collection] = by_collection.get(result.collection, 0) + 1
                        for d in result.domains_detected:
                            by_domain[d] = by_domain.get(d, 0) + 1
                    else:
                        failed += 1
                        for err in result.errors:
                            print(f"  [!] {file_path.name}: {err}")

                elapsed = time.monotonic() - start_time
                self._print_batch_report(total, succeeded, failed, skipped, by_collection, by_domain, elapsed)
                return 0 if failed == 0 else 1

            else:
                print(f"Ingesting directory: {path}")
                print(f"استيعاب مجلد: {path}")
                report = pipeline.ingest_directory(
                    directory=path,
                    patterns=args.patterns,
                    target_collection=args.collection,
                )
                elapsed = time.monotonic() - start_time

                self._print_batch_report(
                    report.total,
                    report.succeeded,
                    report.failed,
                    report.skipped,
                    report.by_collection,
                    report.by_domain,
                    elapsed,
                )

                if report.failed > 0:
                    print()
                    print("Failed files | الملفات الفاشلة:")
                    for r in report.results:
                        if not r.success:
                            for err in r.errors:
                                print(f"  [!] {r.document_id}: {err}")

                return 0 if report.failed == 0 else 1

        else:
            print(f"Error: Path is neither a file nor a directory: {path}")
            return 1

    def _cmd_validate(self, args: argparse.Namespace) -> int:
        """Handle validate command.
        معالجة أمر التحقق"""
        from .ingestion.pipeline import KnowledgeIngestionPipeline

        path = Path(args.path)
        if not path.exists():
            print(f"Error: Path not found: {path}")
            print(f"خطأ: المسار غير موجود: {path}")
            return 1

        pipeline = KnowledgeIngestionPipeline()

        files: list[Path] = []
        if path.is_file():
            files = [path]
        elif path.is_dir():
            for pattern in ["*.md", "*.txt", "*.pdf", "*.html"]:
                files.extend(path.glob(pattern))
            files = sorted(files)
        else:
            print(f"Error: Path is neither a file nor a directory: {path}")
            return 1

        if not files:
            print(f"No knowledge files found at: {path}")
            print(f"لم يتم العثور على ملفات معرفة في: {path}")
            return 0

        print(f"Validating {len(files)} file(s)...")
        print(f"التحقق من {len(files)} ملف(ات)...")
        print()

        total_errors = 0
        total_warnings = 0
        valid_count = 0

        for file_path in files:
            result = pipeline.ingest_file(file_path=file_path)

            file_errors = len(result.errors)
            file_warnings = len(result.warnings)
            total_errors += file_errors
            total_warnings += file_warnings

            if result.success:
                valid_count += 1
                status_icon = "[OK]"
            else:
                status_icon = "[FAIL]"

            print(f"  {status_icon} {file_path.name}")

            if result.validation:
                for issue in result.validation.issues:
                    severity_tag = issue.severity.upper()
                    print(f"        [{severity_tag}] {issue.field}: {issue.message}")
            for err in result.errors:
                if not (result.validation and any(err in str(i.message) for i in result.validation.issues)):
                    print(f"        [ERROR] {err}")
            for warn in result.warnings:
                if not (result.validation and any(warn in str(i.message) for i in result.validation.issues)):
                    print(f"        [WARNING] {warn}")

        print()
        print("=" * 60)
        print("Validation Summary | ملخص التحقق")
        print("=" * 60)
        headers = ["Metric | المقياس", "Count | العدد"]
        rows = [
            ["Total files | إجمالي الملفات", str(len(files))],
            ["Valid | صالح", str(valid_count)],
            ["Invalid | غير صالح", str(len(files) - valid_count)],
            ["Total errors | إجمالي الأخطاء", str(total_errors)],
            ["Total warnings | إجمالي التحذيرات", str(total_warnings)],
        ]
        self._print_table(headers, rows)

        return 0 if valid_count == len(files) else 1

    def _cmd_status(self, args: argparse.Namespace) -> int:
        """Handle status command - show collections and their directory mappings.
        معالجة أمر الحالة - عرض المجموعات وتعييناتها"""
        from .collections import ALL_COLLECTIONS, COLLECTION_DIRECTORY_MAP

        print("=" * 70)
        print("SAHOOL Knowledge Base Status | حالة قاعدة المعرفة")
        print("=" * 70)
        print()

        headers = ["Collection | المجموعة", "Directories | المجلدات", "Files | الملفات"]
        rows = []
        total_files = 0

        for collection in ALL_COLLECTIONS:
            dirs = COLLECTION_DIRECTORY_MAP.get(collection, [])
            dir_str = ", ".join(dirs) if dirs else "(metadata-routed)"

            file_count = 0
            for d in dirs:
                dir_path = Path(d)
                if dir_path.is_dir():
                    for pattern in ["*.md", "*.txt"]:
                        file_count += len(list(dir_path.glob(pattern)))

            total_files += file_count
            rows.append([collection, dir_str, str(file_count)])

        self._print_table(headers, rows)

        print()
        print(f"Total collections: {len(ALL_COLLECTIONS)} | إجمالي المجموعات: {len(ALL_COLLECTIONS)}")
        print(f"Total files found: {total_files} | إجمالي الملفات: {total_files}")

        return 0

    def _cmd_collections(self, args: argparse.Namespace) -> int:
        """Handle collections command.
        معالجة أمر قائمة المجموعات"""
        from .collections import ALL_COLLECTIONS, COLLECTION_DIRECTORY_MAP

        print("=" * 60)
        print("Knowledge Collections | مجموعات المعرفة")
        print("=" * 60)
        print()

        for i, collection in enumerate(ALL_COLLECTIONS, start=1):
            dirs = COLLECTION_DIRECTORY_MAP.get(collection, [])
            dir_display = ", ".join(dirs) if dirs else "(metadata-routed)"
            print(f"  {i:2d}. {collection}")
            print(f"      Directories: {dir_display}")
            print()

        print(f"Total: {len(ALL_COLLECTIONS)} collections | المجموع: {len(ALL_COLLECTIONS)} مجموعة")

        return 0

    def _cmd_freshness(self, args: argparse.Namespace) -> int:
        """Handle freshness command.
        معالجة أمر فحص الحداثة"""
        from .collections import COLLECTION_DIRECTORY_MAP
        from .freshness_monitor import KnowledgeFreshnessMonitor
        from .ingestion.pipeline import KnowledgeIngestionPipeline
        from .models import BaseKnowledgeDocument, KnowledgeDomain

        warning_days = args.warning_days
        monitor = KnowledgeFreshnessMonitor(warning_days=warning_days)
        pipeline = KnowledgeIngestionPipeline()

        print(f"Scanning knowledge base directories (warning window: {warning_days} days)...")
        print(f"فحص مجلدات قاعدة المعرفة (نافذة التحذير: {warning_days} يوم)...")
        print()

        # Collect documents from all mapped directories
        documents: list[BaseKnowledgeDocument] = []
        files_scanned = 0

        for _collection, dirs in COLLECTION_DIRECTORY_MAP.items():
            for d in dirs:
                dir_path = Path(d)
                if not dir_path.is_dir():
                    continue
                for pattern in ["*.md", "*.txt"]:
                    for file_path in sorted(dir_path.glob(pattern)):
                        if file_path.name.startswith(".") or file_path.name == "README.md":
                            continue
                        files_scanned += 1
                        result = pipeline.ingest_file(file_path=file_path)
                        if result.success and result.document_id:
                            primary_domain = (
                                KnowledgeDomain(result.domains_detected[0])
                                if result.domains_detected
                                else KnowledgeDomain.GENERAL
                            )
                            doc = BaseKnowledgeDocument(
                                id=result.document_id,
                                title=file_path.stem,
                                domain=primary_domain,
                                content="placeholder",
                            )
                            documents.append(doc)

        if not documents:
            print("No documents found for freshness check.")
            print("لم يتم العثور على وثائق لفحص الحداثة.")
            print(f"Files scanned: {files_scanned}")
            return 0

        report = monitor.check_documents(documents)

        print("=" * 60)
        print("Freshness Report | تقرير الحداثة")
        print("=" * 60)
        print()

        headers = ["Metric | المقياس", "Count | العدد"]
        rows = [
            ["Total documents | إجمالي الوثائق", str(report.total_documents)],
            ["Fresh | حديثة", str(report.fresh_count)],
            ["Expiring soon | تنتهي قريبا", str(report.expiring_soon_count)],
            ["Expired | منتهية", str(report.expired_count)],
            ["No expiration set | بدون تاريخ انتهاء", str(report.no_expiration_count)],
            ["Health score | درجة الصحة", f"{report.health_score:.1%}"],
        ]
        self._print_table(headers, rows)

        if report.alerts:
            print()
            print("Alerts | تنبيهات:")
            print("-" * 60)
            for alert in report.alerts:
                severity_icon = "[!!]" if alert.severity == "expired" else "[!]"
                print(f"  {severity_icon} {alert.title}")
                print(f"       {alert.message}")
                print(f"       {alert.message_ar}")
                print(f"       Domain: {alert.domain}, Expires: {alert.expiration_date}")
                print()

        if report.by_domain:
            print()
            print("By Domain | حسب المجال:")
            domain_headers = ["Domain | المجال", "Fresh", "Expiring", "Expired", "No Expiry"]
            domain_rows = []
            for domain, counts in sorted(report.by_domain.items()):
                domain_rows.append(
                    [
                        domain,
                        str(counts.get("fresh", 0)),
                        str(counts.get("expiring_soon", 0)),
                        str(counts.get("expired", 0)),
                        str(counts.get("no_expiration", 0)),
                    ]
                )
            self._print_table(domain_headers, domain_rows)

        return 0

    def _cmd_stats(self, args: argparse.Namespace) -> int:
        """Handle stats command.
        معالجة أمر الإحصائيات"""
        from .collections import ALL_COLLECTIONS, COLLECTION_DIRECTORY_MAP
        from .models import KnowledgeDomain

        print("=" * 60)
        print("Knowledge Base Statistics | إحصائيات قاعدة المعرفة")
        print("=" * 60)
        print()

        # Count files per collection directory
        total_files = 0
        total_size_bytes = 0
        files_by_extension: dict[str, int] = {}
        files_per_collection: dict[str, int] = {}

        for collection in ALL_COLLECTIONS:
            dirs = COLLECTION_DIRECTORY_MAP.get(collection, [])
            collection_count = 0

            for d in dirs:
                dir_path = Path(d)
                if not dir_path.is_dir():
                    continue
                for file_path in dir_path.iterdir():
                    if file_path.is_file() and not file_path.name.startswith("."):
                        total_files += 1
                        collection_count += 1
                        total_size_bytes += file_path.stat().st_size
                        ext = file_path.suffix.lower() or "(no ext)"
                        files_by_extension[ext] = files_by_extension.get(ext, 0) + 1

            files_per_collection[collection] = collection_count

        # General stats
        print("General | عام:")
        general_headers = ["Metric | المقياس", "Value | القيمة"]
        general_rows = [
            ["Total collections | إجمالي المجموعات", str(len(ALL_COLLECTIONS))],
            ["Total files | إجمالي الملفات", str(total_files)],
            ["Total size | الحجم الإجمالي", self._format_size(total_size_bytes)],
            ["Knowledge domains | مجالات المعرفة", str(len(KnowledgeDomain))],
        ]
        self._print_table(general_headers, general_rows)

        # Knowledge domains listing
        print()
        print("Domains | المجالات:")
        for domain in KnowledgeDomain:
            print(f"  - {domain.value}")

        # Files by extension
        if files_by_extension:
            print()
            print("Files by Extension | الملفات حسب الامتداد:")
            ext_headers = ["Extension | الامتداد", "Count | العدد"]
            ext_rows = [[ext, str(count)] for ext, count in sorted(files_by_extension.items(), key=lambda x: -x[1])]
            self._print_table(ext_headers, ext_rows)

        # Files per collection (non-empty only)
        non_empty = {c: n for c, n in files_per_collection.items() if n > 0}
        if non_empty:
            print()
            print("Files per Collection | الملفات حسب المجموعة:")
            coll_headers = ["Collection | المجموعة", "Files | الملفات"]
            coll_rows = [[coll, str(count)] for coll, count in sorted(non_empty.items(), key=lambda x: -x[1])]
            self._print_table(coll_headers, coll_rows)

        # Empty collections
        empty_collections = [c for c, n in files_per_collection.items() if n == 0]
        if empty_collections:
            print()
            print(f"Empty collections ({len(empty_collections)}) | مجموعات فارغة:")
            for c in empty_collections:
                dirs = COLLECTION_DIRECTORY_MAP.get(c, [])
                reason = "(metadata-routed)" if not dirs else "(directory not found)"
                print(f"  - {c} {reason}")

        return 0

    # ─── Output Helpers ────────────────────────────────────────────────────────

    def _print_batch_report(
        self,
        total: int,
        succeeded: int,
        failed: int,
        skipped: int,
        by_collection: dict[str, int],
        by_domain: dict[str, int],
        elapsed: float,
    ) -> None:
        """Print a formatted batch ingestion report.
        طباعة تقرير استيعاب مجمع منسق"""
        print()
        print("=" * 60)
        print("Batch Ingestion Report | تقرير الاستيعاب المجمع")
        print("=" * 60)

        headers = ["Metric | المقياس", "Count | العدد"]
        rows = [
            ["Total files | إجمالي الملفات", str(total)],
            ["Succeeded | نجح", str(succeeded)],
            ["Failed | فشل", str(failed)],
            ["Skipped | تم تخطيه", str(skipped)],
            ["Time | الوقت", f"{elapsed:.2f}s"],
        ]
        self._print_table(headers, rows)

        if by_collection:
            print()
            print("By Collection | حسب المجموعة:")
            coll_headers = ["Collection | المجموعة", "Documents | الوثائق"]
            coll_rows = [[coll, str(count)] for coll, count in sorted(by_collection.items(), key=lambda x: -x[1])]
            self._print_table(coll_headers, coll_rows)

        if by_domain:
            print()
            print("By Domain | حسب المجال:")
            domain_headers = ["Domain | المجال", "Documents | الوثائق"]
            domain_rows = [[domain, str(count)] for domain, count in sorted(by_domain.items(), key=lambda x: -x[1])]
            self._print_table(domain_headers, domain_rows)

    def _print_table(self, headers: list[str], rows: list[list[str]]) -> None:
        """Print a formatted ASCII table.
        طباعة جدول ASCII منسق"""
        if not headers or not rows:
            return

        # Calculate column widths
        col_count = len(headers)
        widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < col_count:
                    widths[i] = max(widths[i], len(cell))

        # Build format string
        sep = "+-" + "-+-".join("-" * w for w in widths) + "-+"
        fmt = "| " + " | ".join(f"{{:<{w}}}" for w in widths) + " |"

        # Print table
        print(sep)
        print(fmt.format(*headers))
        print(sep)
        for row in rows:
            # Pad row to match header count
            padded = list(row) + [""] * (col_count - len(row))
            print(fmt.format(*padded[:col_count]))
        print(sep)

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format byte size to human-readable string.
        تنسيق الحجم بالبايت لنص مقروء"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def main() -> None:
    """Entry point for CLI.
    نقطة الدخول لواجهة سطر الأوامر"""
    cli = KnowledgeCLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
