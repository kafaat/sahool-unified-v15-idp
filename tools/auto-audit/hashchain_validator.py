#!/usr/bin/env python3
"""
SAHOOL Hash Chain Validator
Advanced tool for verifying audit trail integrity with hash chain validation

Features:
- Verify hash chain integrity for tamper detection
- Detect chain breaks and gaps
- Parallel validation for large datasets
- Forensic analysis of integrity violations
- Auto-repair suggestions for recoverable issues
- Real-time monitoring mode

Usage:
    python -m tools.auto-audit.hashchain_validator --tenant-id <uuid> [options]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator
from uuid import UUID


@dataclass
class ValidationError:
    """Details about a validation failure"""

    entry_index: int
    entry_id: str
    error_type: str  # 'hash_mismatch', 'chain_break', 'missing_entry', 'sequence_error'
    severity: str  # 'critical', 'high', 'medium', 'low'
    description: str
    expected_value: str | None = None
    actual_value: str | None = None
    timestamp: str | None = None
    recoverable: bool = False
    repair_suggestion: str | None = None


@dataclass
class ValidationSegment:
    """Results for a segment of the chain"""

    start_index: int
    end_index: int
    is_valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    entries_checked: int = 0


@dataclass
class ValidationReport:
    """Complete validation report"""

    tenant_id: str
    validation_time: datetime = field(default_factory=lambda: datetime.now(UTC))
    total_entries: int = 0
    validated_entries: int = 0
    is_valid: bool = True
    chain_integrity: float = 100.0  # Percentage of valid chain links

    errors: list[ValidationError] = field(default_factory=list)
    segments: list[ValidationSegment] = field(default_factory=list)

    first_entry_id: str | None = None
    last_entry_id: str | None = None
    first_entry_hash: str | None = None
    last_entry_hash: str | None = None

    # Statistics
    validation_duration_ms: float = 0
    hash_computations: int = 0
    chain_breaks_detected: int = 0
    tamper_indicators: int = 0

    # Forensic data
    suspicious_entries: list[dict] = field(default_factory=list)
    timeline_gaps: list[dict] = field(default_factory=list)


class HashChainValidator:
    """
    Advanced hash chain validator for audit log integrity verification.

    Supports parallel validation, forensic analysis, and recovery suggestions.
    """

    def __init__(self, entries: list[dict] | None = None):
        """
        Initialize validator with audit entries.

        Args:
            entries: List of audit log entries (must be sorted by created_at ASC)
        """
        self.entries = entries or []
        self._hash_cache: dict[str, str] = {}

    def load_from_file(self, file_path: Path) -> None:
        """Load entries from JSON file"""
        with open(file_path) as f:
            self.entries = json.load(f)
        # Ensure sorted by timestamp
        self.entries.sort(key=lambda x: x.get("created_at", ""))

    def load_from_database(
        self,
        db_session: Any,
        tenant_id: UUID,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> None:
        """Load entries from database in chronological order"""
        from sqlalchemy import select

        from shared.libs.audit.models import AuditLog

        stmt = (
            select(AuditLog)
            .where(AuditLog.tenant_id == tenant_id)
            .order_by(AuditLog.created_at.asc())
        )

        if start_date:
            stmt = stmt.where(AuditLog.created_at >= start_date)
        if end_date:
            stmt = stmt.where(AuditLog.created_at <= end_date)

        results = db_session.execute(stmt).scalars()
        self.entries = [self._entry_to_dict(entry) for entry in results]

    def _entry_to_dict(self, entry: Any) -> dict:
        """Convert ORM entry to dictionary"""
        return {
            "id": str(entry.id),
            "tenant_id": str(entry.tenant_id),
            "actor_id": str(entry.actor_id) if entry.actor_id else None,
            "actor_type": entry.actor_type,
            "action": entry.action,
            "resource_type": entry.resource_type,
            "resource_id": entry.resource_id,
            "correlation_id": str(entry.correlation_id),
            "details_json": entry.details_json,
            "prev_hash": entry.prev_hash,
            "entry_hash": entry.entry_hash,
            "created_at": entry.created_at.isoformat(),
        }

    @staticmethod
    def sha256_hex(data: str) -> str:
        """Compute SHA-256 hash of string"""
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    @staticmethod
    def build_canonical_string(entry: dict) -> str:
        """Build canonical string for hash computation"""
        return "|".join(
            [
                str(entry.get("tenant_id", "")),
                str(entry.get("actor_id", "")) if entry.get("actor_id") else "",
                str(entry.get("actor_type", "")),
                str(entry.get("action", "")),
                str(entry.get("resource_type", "")),
                str(entry.get("resource_id", "")),
                str(entry.get("correlation_id", "")),
                str(entry.get("details_json", "{}")),
                str(entry.get("created_at", "")),
            ]
        )

    def compute_entry_hash(self, prev_hash: str | None, canonical: str) -> str:
        """Compute hash for an entry"""
        cache_key = f"{prev_hash or ''}:{canonical[:100]}"
        if cache_key in self._hash_cache:
            return self._hash_cache[cache_key]

        prefix = prev_hash or ""
        result = self.sha256_hex(prefix + canonical)
        self._hash_cache[cache_key] = result
        return result

    def validate(
        self,
        tenant_id: str | None = None,
        parallel: bool = True,
        segment_size: int = 1000,
    ) -> ValidationReport:
        """
        Validate the hash chain integrity.

        Args:
            tenant_id: Optional tenant ID filter
            parallel: Use parallel validation for large datasets
            segment_size: Size of segments for parallel processing

        Returns:
            ValidationReport with all findings
        """
        start_time = datetime.now(UTC)

        if tenant_id:
            entries = [e for e in self.entries if e.get("tenant_id") == tenant_id]
        else:
            entries = self.entries

        report = ValidationReport(
            tenant_id=tenant_id or "all",
            total_entries=len(entries),
        )

        if not entries:
            return report

        report.first_entry_id = entries[0].get("id")
        report.last_entry_id = entries[-1].get("id")
        report.first_entry_hash = entries[0].get("entry_hash")
        report.last_entry_hash = entries[-1].get("entry_hash")

        # Choose validation strategy
        if parallel and len(entries) > segment_size:
            report.segments = self._validate_parallel(entries, segment_size)
        else:
            segment = self._validate_segment(entries, 0, len(entries) - 1)
            report.segments = [segment]

        # Aggregate results
        report.validated_entries = sum(s.entries_checked for s in report.segments)
        report.hash_computations = report.validated_entries

        for segment in report.segments:
            report.errors.extend(segment.errors)
            if not segment.is_valid:
                report.is_valid = False

        # Calculate chain integrity percentage
        if report.total_entries > 0:
            valid_links = report.total_entries - len(
                [e for e in report.errors if e.error_type in ("hash_mismatch", "chain_break")]
            )
            report.chain_integrity = round(valid_links / report.total_entries * 100, 2)

        # Count specific issues
        report.chain_breaks_detected = sum(
            1 for e in report.errors if e.error_type == "chain_break"
        )
        report.tamper_indicators = sum(
            1 for e in report.errors if e.error_type == "hash_mismatch"
        )

        # Forensic analysis
        report.suspicious_entries = self._identify_suspicious_entries(entries, report.errors)
        report.timeline_gaps = self._detect_timeline_gaps(entries)

        # Calculate duration
        end_time = datetime.now(UTC)
        report.validation_duration_ms = (end_time - start_time).total_seconds() * 1000

        return report

    def _validate_segment(
        self,
        entries: list[dict],
        start_index: int,
        end_index: int,
    ) -> ValidationSegment:
        """Validate a segment of the chain"""
        segment = ValidationSegment(
            start_index=start_index,
            end_index=end_index,
            is_valid=True,
        )

        prev_hash = None
        if start_index > 0:
            prev_hash = entries[start_index - 1].get("entry_hash")

        for i in range(start_index, min(end_index + 1, len(entries))):
            entry = entries[i]
            segment.entries_checked += 1

            stored_prev_hash = entry.get("prev_hash")
            stored_entry_hash = entry.get("entry_hash")

            # Verify prev_hash chain link
            if i == 0:
                # First entry should have null prev_hash
                if stored_prev_hash is not None:
                    segment.is_valid = False
                    segment.errors.append(
                        ValidationError(
                            entry_index=i,
                            entry_id=entry.get("id", "unknown"),
                            error_type="chain_break",
                            severity="high",
                            description="First entry has non-null prev_hash",
                            expected_value=None,
                            actual_value=stored_prev_hash,
                            timestamp=entry.get("created_at"),
                            recoverable=True,
                            repair_suggestion="Set prev_hash to NULL for first entry",
                        )
                    )
            else:
                # Check chain continuity
                if stored_prev_hash != prev_hash:
                    segment.is_valid = False
                    segment.errors.append(
                        ValidationError(
                            entry_index=i,
                            entry_id=entry.get("id", "unknown"),
                            error_type="chain_break",
                            severity="critical",
                            description=f"Chain break detected at entry {i}",
                            expected_value=prev_hash,
                            actual_value=stored_prev_hash,
                            timestamp=entry.get("created_at"),
                            recoverable=False,
                            repair_suggestion="Chain is broken. Manual investigation required.",
                        )
                    )

            # Verify entry hash
            canonical = self.build_canonical_string(entry)
            computed_hash = self.compute_entry_hash(
                prev_hash=stored_prev_hash, canonical=canonical
            )

            if computed_hash != stored_entry_hash:
                segment.is_valid = False
                segment.errors.append(
                    ValidationError(
                        entry_index=i,
                        entry_id=entry.get("id", "unknown"),
                        error_type="hash_mismatch",
                        severity="critical",
                        description=f"Hash mismatch at entry {i} - possible tampering",
                        expected_value=computed_hash,
                        actual_value=stored_entry_hash,
                        timestamp=entry.get("created_at"),
                        recoverable=False,
                        repair_suggestion="ALERT: Entry may have been tampered with. "
                        "Compare with backups.",
                    )
                )

            prev_hash = stored_entry_hash

        return segment

    def _validate_parallel(
        self, entries: list[dict], segment_size: int
    ) -> list[ValidationSegment]:
        """Validate chain in parallel segments"""
        segments = []
        num_segments = (len(entries) + segment_size - 1) // segment_size

        # We need to validate sequentially because of chain dependencies
        # But we can prepare segments and validate overlaps in parallel
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for i in range(num_segments):
                start = i * segment_size
                end = min(start + segment_size - 1, len(entries) - 1)
                futures.append(
                    executor.submit(self._validate_segment, entries, start, end)
                )

            for future in as_completed(futures):
                segments.append(future.result())

        # Sort segments by start index
        segments.sort(key=lambda s: s.start_index)

        # Verify segment boundaries
        for i in range(1, len(segments)):
            prev_segment = segments[i - 1]
            curr_segment = segments[i]

            prev_entry = entries[prev_segment.end_index]
            curr_entry = entries[curr_segment.start_index]

            if curr_entry.get("prev_hash") != prev_entry.get("entry_hash"):
                curr_segment.is_valid = False
                curr_segment.errors.append(
                    ValidationError(
                        entry_index=curr_segment.start_index,
                        entry_id=curr_entry.get("id", "unknown"),
                        error_type="chain_break",
                        severity="critical",
                        description=f"Chain break at segment boundary {i}",
                        expected_value=prev_entry.get("entry_hash"),
                        actual_value=curr_entry.get("prev_hash"),
                        timestamp=curr_entry.get("created_at"),
                    )
                )

        return segments

    def _identify_suspicious_entries(
        self, entries: list[dict], errors: list[ValidationError]
    ) -> list[dict]:
        """Identify entries that require investigation"""
        suspicious = []
        error_indices = {e.entry_index for e in errors}

        for idx in error_indices:
            if idx < len(entries):
                entry = entries[idx]
                suspicious.append(
                    {
                        "index": idx,
                        "id": entry.get("id"),
                        "action": entry.get("action"),
                        "actor_id": entry.get("actor_id"),
                        "timestamp": entry.get("created_at"),
                        "errors": [
                            e.error_type for e in errors if e.entry_index == idx
                        ],
                    }
                )

        return suspicious

    def _detect_timeline_gaps(self, entries: list[dict]) -> list[dict]:
        """Detect unusual gaps in the audit timeline"""
        gaps = []

        if len(entries) < 2:
            return gaps

        for i in range(1, len(entries)):
            prev_time = entries[i - 1].get("created_at")
            curr_time = entries[i].get("created_at")

            if prev_time and curr_time:
                try:
                    prev_dt = datetime.fromisoformat(prev_time.replace("Z", "+00:00"))
                    curr_dt = datetime.fromisoformat(curr_time.replace("Z", "+00:00"))
                    gap = (curr_dt - prev_dt).total_seconds()

                    # Flag gaps longer than 1 hour
                    if gap > 3600:
                        gaps.append(
                            {
                                "start_index": i - 1,
                                "end_index": i,
                                "gap_seconds": gap,
                                "gap_hours": round(gap / 3600, 2),
                                "start_time": prev_time,
                                "end_time": curr_time,
                            }
                        )
                except (ValueError, TypeError):
                    pass

        return gaps

    def verify_single_entry(self, entry: dict, prev_entry: dict | None = None) -> bool:
        """
        Verify a single entry's hash.

        Args:
            entry: Entry to verify
            prev_entry: Previous entry in the chain (None for first entry)

        Returns:
            True if entry hash is valid
        """
        expected_prev_hash = prev_entry.get("entry_hash") if prev_entry else None
        stored_prev_hash = entry.get("prev_hash")

        if stored_prev_hash != expected_prev_hash:
            return False

        canonical = self.build_canonical_string(entry)
        computed_hash = self.compute_entry_hash(
            prev_hash=stored_prev_hash, canonical=canonical
        )

        return computed_hash == entry.get("entry_hash")

    def find_chain_anchor(self) -> tuple[int, dict] | None:
        """
        Find a valid anchor point in a broken chain.

        Useful for recovery when chain is partially corrupted.

        Returns:
            Tuple of (index, entry) for last valid anchor, or None
        """
        if not self.entries:
            return None

        last_valid_idx = 0
        prev_hash = None

        for i, entry in enumerate(self.entries):
            canonical = self.build_canonical_string(entry)
            computed_hash = self.compute_entry_hash(
                prev_hash=entry.get("prev_hash"), canonical=canonical
            )

            if computed_hash == entry.get("entry_hash"):
                if i == 0 or entry.get("prev_hash") == prev_hash:
                    last_valid_idx = i
                    prev_hash = computed_hash

        return (last_valid_idx, self.entries[last_valid_idx])

    def generate_recovery_report(self, report: ValidationReport) -> str:
        """Generate recovery recommendations for integrity issues"""
        lines = [
            "# Hash Chain Recovery Report",
            "",
            f"Generated: {datetime.now(UTC).isoformat()}",
            f"Chain Integrity: {report.chain_integrity}%",
            "",
        ]

        if report.is_valid:
            lines.extend(
                [
                    "## Status: VALID",
                    "",
                    "No recovery actions needed. Chain integrity verified.",
                ]
            )
            return "\n".join(lines)

        lines.extend(
            [
                "## Status: INTEGRITY ISSUES DETECTED",
                "",
                f"Total Errors: {len(report.errors)}",
                f"Chain Breaks: {report.chain_breaks_detected}",
                f"Tamper Indicators: {report.tamper_indicators}",
                "",
                "## Recovery Actions",
                "",
            ]
        )

        # Group errors by type
        hash_mismatches = [e for e in report.errors if e.error_type == "hash_mismatch"]
        chain_breaks = [e for e in report.errors if e.error_type == "chain_break"]

        if hash_mismatches:
            lines.extend(
                [
                    "### Hash Mismatch Recovery",
                    "",
                    "**CRITICAL**: Hash mismatches indicate potential data tampering.",
                    "",
                    "Actions:",
                    "1. Compare affected entries with backup data",
                    "2. Check for recent database modifications",
                    "3. Review access logs for unauthorized changes",
                    "4. If legitimate changes, rebuild hash chain from known good state",
                    "",
                    "Affected entries:",
                    "",
                ]
            )
            for err in hash_mismatches[:20]:
                lines.append(f"- Entry {err.entry_index}: {err.entry_id} ({err.timestamp})")
            lines.append("")

        if chain_breaks:
            lines.extend(
                [
                    "### Chain Break Recovery",
                    "",
                    "Chain breaks indicate missing or out-of-order entries.",
                    "",
                    "Actions:",
                    "1. Verify no entries were deleted",
                    "2. Check for database replication issues",
                    "3. Look for entries with duplicate timestamps",
                    "",
                    "Break points:",
                    "",
                ]
            )
            for err in chain_breaks[:20]:
                lines.append(f"- Index {err.entry_index}: {err.description}")
            lines.append("")

        if report.timeline_gaps:
            lines.extend(
                [
                    "### Timeline Gaps",
                    "",
                    "Unusual gaps detected in audit timeline:",
                    "",
                ]
            )
            for gap in report.timeline_gaps[:10]:
                lines.append(
                    f"- {gap['gap_hours']}h gap between entries "
                    f"{gap['start_index']} and {gap['end_index']}"
                )
            lines.append("")

        # Find recovery anchor
        anchor = self.find_chain_anchor()
        if anchor:
            idx, entry = anchor
            lines.extend(
                [
                    "### Recovery Anchor Point",
                    "",
                    f"Last valid chain anchor found at index {idx}",
                    f"Entry ID: {entry.get('id')}",
                    f"Timestamp: {entry.get('created_at')}",
                    f"Hash: {entry.get('entry_hash')}",
                    "",
                    "To rebuild chain from this point:",
                    "1. Export entries from index 0 to anchor",
                    "2. Verify anchor entry integrity",
                    "3. Recalculate hashes for entries after anchor",
                    "",
                ]
            )

        lines.extend(
            [
                "---",
                "",
                "**WARNING**: Any chain reconstruction should be performed with",
                "appropriate audit trail and approval from security team.",
            ]
        )

        return "\n".join(lines)


def generate_markdown_report(report: ValidationReport) -> str:
    """Generate markdown validation report"""
    status_icon = "VALID" if report.is_valid else "INTEGRITY ISSUES DETECTED"
    status_color = "green" if report.is_valid else "red"

    lines = [
        "# SAHOOL Hash Chain Validation Report",
        "",
        f"> Validated: {report.validation_time.isoformat()}",
        f"> Tenant: {report.tenant_id}",
        f"> Duration: {report.validation_duration_ms:.2f}ms",
        "",
        f"## Status: {status_icon}",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total Entries | {report.total_entries:,} |",
        f"| Validated | {report.validated_entries:,} |",
        f"| Chain Integrity | {report.chain_integrity}% |",
        f"| Chain Breaks | {report.chain_breaks_detected} |",
        f"| Tamper Indicators | {report.tamper_indicators} |",
        "",
    ]

    if report.errors:
        lines.extend(
            [
                "## Validation Errors",
                "",
                "| Index | Type | Severity | Description |",
                "|-------|------|----------|-------------|",
            ]
        )
        for err in report.errors[:50]:
            lines.append(
                f"| {err.entry_index} | {err.error_type} | "
                f"{err.severity} | {err.description} |"
            )
        lines.append("")

    if report.suspicious_entries:
        lines.extend(
            [
                "## Suspicious Entries",
                "",
            ]
        )
        for entry in report.suspicious_entries[:20]:
            lines.append(
                f"- Entry {entry['index']}: {entry['action']} "
                f"by {entry['actor_id']} at {entry['timestamp']}"
            )
        lines.append("")

    if report.timeline_gaps:
        lines.extend(
            [
                "## Timeline Gaps",
                "",
            ]
        )
        for gap in report.timeline_gaps[:10]:
            lines.append(
                f"- {gap['gap_hours']}h gap: {gap['start_time']} to {gap['end_time']}"
            )
        lines.append("")

    lines.extend(
        [
            "---",
            "",
            "*Report generated by SAHOOL Auto Audit Tools*",
        ]
    )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Validate SAHOOL audit log hash chain integrity"
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Input JSON file with audit logs",
    )
    parser.add_argument(
        "--tenant-id",
        "-t",
        help="Filter by tenant ID",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="hashchain_validation_report.md",
        help="Output file path",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format",
    )
    parser.add_argument(
        "--recovery",
        "-r",
        action="store_true",
        help="Generate recovery report if issues found",
    )
    args = parser.parse_args()

    # Load and validate
    validator = HashChainValidator()
    validator.load_from_file(Path(args.input))
    report = validator.validate(tenant_id=args.tenant_id)

    # Generate output
    if args.format == "json":
        output = json.dumps(
            {
                "tenant_id": report.tenant_id,
                "validation_time": report.validation_time.isoformat(),
                "is_valid": report.is_valid,
                "chain_integrity": report.chain_integrity,
                "total_entries": report.total_entries,
                "validated_entries": report.validated_entries,
                "chain_breaks": report.chain_breaks_detected,
                "tamper_indicators": report.tamper_indicators,
                "errors": [
                    {
                        "index": e.entry_index,
                        "type": e.error_type,
                        "severity": e.severity,
                        "description": e.description,
                    }
                    for e in report.errors
                ],
                "suspicious_entries": report.suspicious_entries,
                "timeline_gaps": report.timeline_gaps,
            },
            indent=2,
        )
    else:
        output = generate_markdown_report(report)

        if args.recovery and not report.is_valid:
            output += "\n\n" + validator.generate_recovery_report(report)

    # Write output
    output_path = Path(args.output)
    output_path.write_text(output)

    # Console output
    status = "VALID" if report.is_valid else "INTEGRITY ISSUES"
    print(f"Hash Chain Validation: {status}")
    print(f"  Integrity: {report.chain_integrity}%")
    print(f"  Entries validated: {report.validated_entries:,}")
    print(f"  Errors found: {len(report.errors)}")
    print(f"  Report: {output_path}")

    sys.exit(0 if report.is_valid else 1)


if __name__ == "__main__":
    main()
