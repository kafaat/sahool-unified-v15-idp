#!/usr/bin/env python3
"""
SAHOOL Audit Data Exporter
Comprehensive export tool for audit logs in multiple formats

Features:
- Multiple export formats (JSON, CSV, Parquet, SIEM)
- Data transformation and normalization
- PII redaction for compliance
- Incremental export with checkpoints
- Compression support
- SIEM integration (Splunk, ELK, Azure Sentinel)

Usage:
    python -m tools.auto-audit.exporter --input logs.json --format csv [options]
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from io import StringIO
from pathlib import Path
from typing import Any


class ExportFormat(str, Enum):
    """Supported export formats"""

    JSON = "json"
    JSONL = "jsonl"  # JSON Lines
    CSV = "csv"
    PARQUET = "parquet"
    SPLUNK = "splunk"  # Splunk HEC format
    ELK = "elk"  # Elasticsearch bulk format
    CEF = "cef"  # Common Event Format
    SYSLOG = "syslog"


class RedactionLevel(str, Enum):
    """PII redaction levels"""

    NONE = "none"
    BASIC = "basic"  # Passwords, tokens
    STANDARD = "standard"  # + IPs, emails
    STRICT = "strict"  # + names, all identifiers


@dataclass
class ExportConfig:
    """Export configuration"""

    format: ExportFormat = ExportFormat.JSON
    redaction_level: RedactionLevel = RedactionLevel.STANDARD
    compress: bool = False
    include_hash_chain: bool = True
    flatten_json: bool = False
    timestamp_format: str = "iso"  # iso, unix, rfc2822
    batch_size: int = 10000
    checkpoint_enabled: bool = False
    checkpoint_file: str | None = None


@dataclass
class ExportCheckpoint:
    """Checkpoint for incremental exports"""

    last_export_time: datetime
    last_entry_id: str
    entries_exported: int
    checksum: str


@dataclass
class ExportResult:
    """Export operation result"""

    success: bool
    format: str
    output_path: str
    entries_exported: int
    file_size_bytes: int
    compressed: bool
    duration_ms: float
    checksum: str | None = None
    errors: list[str] = field(default_factory=list)


class AuditDataExporter:
    """
    Comprehensive audit data export tool.

    Supports multiple formats and SIEM integrations.
    """

    # PII field patterns for redaction
    PII_FIELDS_BASIC = {
        "password",
        "token",
        "secret",
        "api_key",
        "apikey",
        "auth",
        "credential",
    }

    PII_FIELDS_STANDARD = PII_FIELDS_BASIC | {
        "ip",
        "ip_address",
        "email",
        "phone",
        "ssn",
        "credit_card",
        "card_number",
    }

    PII_FIELDS_STRICT = PII_FIELDS_STANDARD | {
        "name",
        "first_name",
        "last_name",
        "username",
        "user_id",
        "actor_id",
        "address",
        "location",
    }

    # CEF severity mapping
    CEF_SEVERITY = {
        "info": 1,
        "low": 3,
        "medium": 5,
        "high": 7,
        "critical": 10,
    }

    def __init__(self, entries: list[dict] | None = None):
        """
        Initialize exporter.

        Args:
            entries: List of audit log entries
        """
        self.entries = entries or []
        self._checkpoints: dict[str, ExportCheckpoint] = {}

    def load_from_file(self, file_path: Path) -> None:
        """Load entries from JSON file"""
        with open(file_path) as f:
            self.entries = json.load(f)

    def load_checkpoint(self, checkpoint_file: Path) -> ExportCheckpoint | None:
        """Load export checkpoint"""
        if checkpoint_file.exists():
            with open(checkpoint_file) as f:
                data = json.load(f)
                return ExportCheckpoint(
                    last_export_time=datetime.fromisoformat(data["last_export_time"]),
                    last_entry_id=data["last_entry_id"],
                    entries_exported=data["entries_exported"],
                    checksum=data["checksum"],
                )
        return None

    def save_checkpoint(self, checkpoint_file: Path, checkpoint: ExportCheckpoint) -> None:
        """Save export checkpoint"""
        with open(checkpoint_file, "w") as f:
            json.dump(
                {
                    "last_export_time": checkpoint.last_export_time.isoformat(),
                    "last_entry_id": checkpoint.last_entry_id,
                    "entries_exported": checkpoint.entries_exported,
                    "checksum": checkpoint.checksum,
                },
                f,
                indent=2,
            )

    def export(
        self,
        output_path: Path,
        config: ExportConfig | None = None,
        tenant_id: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> ExportResult:
        """
        Export audit logs to specified format.

        Args:
            output_path: Output file path
            config: Export configuration
            tenant_id: Filter by tenant
            start_date: Filter by start date
            end_date: Filter by end date

        Returns:
            ExportResult with operation details
        """
        start_time = datetime.now(UTC)
        config = config or ExportConfig()

        # Filter entries
        entries = self._filter_entries(tenant_id, start_date, end_date)

        # Apply redaction
        if config.redaction_level != RedactionLevel.NONE:
            entries = [self._redact_entry(e, config.redaction_level) for e in entries]

        # Remove hash chain if not needed
        if not config.include_hash_chain:
            for entry in entries:
                entry.pop("prev_hash", None)
                entry.pop("entry_hash", None)

        # Flatten JSON if requested
        if config.flatten_json:
            entries = [self._flatten_entry(e) for e in entries]

        # Format timestamps
        if config.timestamp_format != "iso":
            entries = [self._format_timestamps(e, config.timestamp_format) for e in entries]

        # Export to format
        try:
            if config.format == ExportFormat.JSON:
                content = self._export_json(entries)
            elif config.format == ExportFormat.JSONL:
                content = self._export_jsonl(entries)
            elif config.format == ExportFormat.CSV:
                content = self._export_csv(entries)
            elif config.format == ExportFormat.SPLUNK:
                content = self._export_splunk(entries)
            elif config.format == ExportFormat.ELK:
                content = self._export_elk(entries)
            elif config.format == ExportFormat.CEF:
                content = self._export_cef(entries)
            elif config.format == ExportFormat.SYSLOG:
                content = self._export_syslog(entries)
            else:
                raise ValueError(f"Unsupported format: {config.format}")
        except Exception as e:
            return ExportResult(
                success=False,
                format=config.format.value,
                output_path=str(output_path),
                entries_exported=0,
                file_size_bytes=0,
                compressed=config.compress,
                duration_ms=0,
                errors=[str(e)],
            )

        # Calculate checksum
        checksum = hashlib.sha256(content.encode("utf-8")).hexdigest()

        # Write output
        if config.compress:
            output_path = Path(str(output_path) + ".gz")
            with gzip.open(output_path, "wt", encoding="utf-8") as f:
                f.write(content)
        else:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

        file_size = output_path.stat().st_size
        end_time = datetime.now(UTC)
        duration_ms = (end_time - start_time).total_seconds() * 1000

        # Save checkpoint if enabled
        if config.checkpoint_enabled and entries:
            checkpoint = ExportCheckpoint(
                last_export_time=datetime.now(UTC),
                last_entry_id=entries[-1].get("id", ""),
                entries_exported=len(entries),
                checksum=checksum,
            )
            if config.checkpoint_file:
                self.save_checkpoint(Path(config.checkpoint_file), checkpoint)

        return ExportResult(
            success=True,
            format=config.format.value,
            output_path=str(output_path),
            entries_exported=len(entries),
            file_size_bytes=file_size,
            compressed=config.compress,
            duration_ms=duration_ms,
            checksum=checksum,
        )

    def _filter_entries(
        self,
        tenant_id: str | None,
        start_date: datetime | None,
        end_date: datetime | None,
    ) -> list[dict]:
        """Filter entries by tenant and date range"""
        entries = self.entries

        if tenant_id:
            entries = [e for e in entries if e.get("tenant_id") == tenant_id]

        if start_date or end_date:
            filtered = []
            for entry in entries:
                ts_str = entry.get("created_at", "")
                if ts_str:
                    try:
                        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                        if start_date and ts < start_date:
                            continue
                        if end_date and ts > end_date:
                            continue
                        filtered.append(entry)
                    except ValueError:
                        pass
            entries = filtered

        return entries

    def _redact_entry(self, entry: dict, level: RedactionLevel) -> dict:
        """Redact PII from entry based on level"""
        if level == RedactionLevel.BASIC:
            pii_fields = self.PII_FIELDS_BASIC
        elif level == RedactionLevel.STANDARD:
            pii_fields = self.PII_FIELDS_STANDARD
        elif level == RedactionLevel.STRICT:
            pii_fields = self.PII_FIELDS_STRICT
        else:
            return entry

        redacted = entry.copy()

        def redact_value(key: str, value: Any) -> Any:
            if key.lower() in pii_fields:
                if isinstance(value, str):
                    return "[REDACTED]"
                return None
            if isinstance(value, dict):
                return {k: redact_value(k, v) for k, v in value.items()}
            if isinstance(value, list):
                return [redact_value("item", v) for v in value]
            return value

        for key, value in entry.items():
            redacted[key] = redact_value(key, value)

        # Redact details_json if present
        if "details_json" in redacted:
            try:
                details = json.loads(redacted["details_json"])
                redacted_details = {k: redact_value(k, v) for k, v in details.items()}
                redacted["details_json"] = json.dumps(redacted_details)
            except (json.JSONDecodeError, TypeError):
                pass

        return redacted

    def _flatten_entry(self, entry: dict, prefix: str = "") -> dict:
        """Flatten nested dictionary"""
        flat = {}

        for key, value in entry.items():
            new_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                flat.update(self._flatten_entry(value, new_key))
            elif isinstance(value, list):
                flat[new_key] = json.dumps(value)
            else:
                flat[new_key] = value

        return flat

    def _format_timestamps(self, entry: dict, format_type: str) -> dict:
        """Convert timestamps to specified format"""
        formatted = entry.copy()

        for key in ["created_at", "updated_at", "timestamp"]:
            if key in formatted and formatted[key]:
                try:
                    ts = datetime.fromisoformat(str(formatted[key]).replace("Z", "+00:00"))
                    if format_type == "unix":
                        formatted[key] = ts.timestamp()
                    elif format_type == "rfc2822":
                        formatted[key] = ts.strftime("%a, %d %b %Y %H:%M:%S %z")
                except ValueError:
                    pass

        return formatted

    def _export_json(self, entries: list[dict]) -> str:
        """Export as formatted JSON"""
        return json.dumps(entries, indent=2, ensure_ascii=False, default=str)

    def _export_jsonl(self, entries: list[dict]) -> str:
        """Export as JSON Lines (one JSON object per line)"""
        lines = [json.dumps(e, ensure_ascii=False, default=str) for e in entries]
        return "\n".join(lines)

    def _export_csv(self, entries: list[dict]) -> str:
        """Export as CSV"""
        if not entries:
            return ""

        # Get all unique keys
        all_keys = set()
        for entry in entries:
            all_keys.update(entry.keys())

        # Sort keys for consistent output
        fieldnames = sorted(all_keys)

        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()

        for entry in entries:
            # Convert non-string values to JSON strings
            row = {}
            for key, value in entry.items():
                if isinstance(value, (dict, list)):
                    row[key] = json.dumps(value)
                elif value is None:
                    row[key] = ""
                else:
                    row[key] = str(value)
            writer.writerow(row)

        return output.getvalue()

    def _export_splunk(self, entries: list[dict]) -> str:
        """Export in Splunk HEC (HTTP Event Collector) format"""
        events = []

        for entry in entries:
            # Parse timestamp
            ts_str = entry.get("created_at", "")
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                epoch_time = ts.timestamp()
            except (ValueError, TypeError):
                epoch_time = datetime.now(UTC).timestamp()

            splunk_event = {
                "time": epoch_time,
                "host": "sahool-audit",
                "source": "audit-log",
                "sourcetype": "sahool:audit:json",
                "index": "audit",
                "event": {
                    "action": entry.get("action"),
                    "actor_id": entry.get("actor_id"),
                    "actor_type": entry.get("actor_type"),
                    "resource_type": entry.get("resource_type"),
                    "resource_id": entry.get("resource_id"),
                    "tenant_id": entry.get("tenant_id"),
                    "correlation_id": entry.get("correlation_id"),
                    "ip": entry.get("ip"),
                    "user_agent": entry.get("user_agent"),
                    "details": entry.get("details_json"),
                },
            }
            events.append(json.dumps(splunk_event, default=str))

        return "\n".join(events)

    def _export_elk(self, entries: list[dict]) -> str:
        """Export in Elasticsearch bulk format"""
        lines = []

        for entry in entries:
            # Index action
            index_action = {
                "index": {
                    "_index": "sahool-audit",
                    "_id": entry.get("id"),
                }
            }
            lines.append(json.dumps(index_action))

            # Document
            doc = {
                "@timestamp": entry.get("created_at"),
                "action": entry.get("action"),
                "actor": {
                    "id": entry.get("actor_id"),
                    "type": entry.get("actor_type"),
                },
                "resource": {
                    "type": entry.get("resource_type"),
                    "id": entry.get("resource_id"),
                },
                "tenant_id": entry.get("tenant_id"),
                "correlation_id": entry.get("correlation_id"),
                "source": {
                    "ip": entry.get("ip"),
                    "user_agent": entry.get("user_agent"),
                },
                "hash_chain": {
                    "prev_hash": entry.get("prev_hash"),
                    "entry_hash": entry.get("entry_hash"),
                },
            }

            # Parse details
            if entry.get("details_json"):
                try:
                    doc["details"] = json.loads(entry["details_json"])
                except (json.JSONDecodeError, TypeError):
                    doc["details"] = entry.get("details_json")

            lines.append(json.dumps(doc, default=str))

        return "\n".join(lines)

    def _export_cef(self, entries: list[dict]) -> str:
        """Export in Common Event Format (CEF) for SIEM integration"""
        lines = []

        for entry in entries:
            # Determine severity based on action
            action = entry.get("action", "").lower()
            if "delete" in action or "admin" in action:
                severity = 7
            elif "create" in action or "update" in action:
                severity = 3
            else:
                severity = 1

            # Build CEF header
            # CEF:Version|Device Vendor|Device Product|Device Version|Signature ID|Name|Severity|Extension
            cef_header = (
                f"CEF:0|SAHOOL|AuditLog|1.0|"
                f"{entry.get('action', 'unknown')}|"
                f"{entry.get('action', 'Unknown Action')}|"
                f"{severity}|"
            )

            # Build extension (key=value pairs)
            extensions = [
                f"act={entry.get('action', '')}",
                f"src={entry.get('ip', '')}",
                f"suser={entry.get('actor_id', '')}",
                f"duser={entry.get('resource_id', '')}",
                f"cs1={entry.get('tenant_id', '')}",
                "cs1Label=TenantID",
                f"cs2={entry.get('correlation_id', '')}",
                "cs2Label=CorrelationID",
                f"cs3={entry.get('resource_type', '')}",
                "cs3Label=ResourceType",
                f"rt={entry.get('created_at', '')}",
            ]

            cef_line = cef_header + " ".join(extensions)
            lines.append(cef_line)

        return "\n".join(lines)

    def _export_syslog(self, entries: list[dict]) -> str:
        """Export in Syslog format (RFC 5424)"""
        lines = []

        for entry in entries:
            # Parse timestamp
            ts_str = entry.get("created_at", "")
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                timestamp = ts.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
            except (ValueError, TypeError):
                timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.%f%z")

            # Syslog priority (facility * 8 + severity)
            # Using facility 4 (security) and severity 6 (informational)
            priority = 4 * 8 + 6

            # Build structured data
            structured_data = (
                f'[audit@sahool action="{entry.get("action", "")}" '
                f'actor="{entry.get("actor_id", "")}" '
                f'resource="{entry.get("resource_type", "")}/{entry.get("resource_id", "")}" '
                f'tenant="{entry.get("tenant_id", "")}"]'
            )

            # Build message
            message = f"{entry.get('action', 'unknown')} by {entry.get('actor_id', 'unknown')}"

            # RFC 5424 format
            # <PRI>VERSION TIMESTAMP HOSTNAME APP-NAME PROCID MSGID STRUCTURED-DATA MSG
            syslog_line = (
                f"<{priority}>1 {timestamp} sahool-audit audit - "
                f"{entry.get('correlation_id', '-')} {structured_data} {message}"
            )

            lines.append(syslog_line)

        return "\n".join(lines)

    def export_incremental(
        self,
        output_dir: Path,
        config: ExportConfig | None = None,
        tenant_id: str | None = None,
    ) -> ExportResult:
        """
        Export only new entries since last checkpoint.

        Args:
            output_dir: Output directory for exports
            config: Export configuration
            tenant_id: Filter by tenant

        Returns:
            ExportResult
        """
        config = config or ExportConfig()
        config.checkpoint_enabled = True

        checkpoint_file = output_dir / "export_checkpoint.json"
        config.checkpoint_file = str(checkpoint_file)

        # Load checkpoint
        checkpoint = self.load_checkpoint(checkpoint_file)

        # Filter entries after checkpoint
        if checkpoint:
            entries = [
                e
                for e in self.entries
                if e.get("created_at", "") > checkpoint.last_export_time.isoformat()
            ]
            if tenant_id:
                entries = [e for e in entries if e.get("tenant_id") == tenant_id]
            self.entries = entries

        # Generate output filename with timestamp
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        extension = {
            ExportFormat.JSON: ".json",
            ExportFormat.JSONL: ".jsonl",
            ExportFormat.CSV: ".csv",
            ExportFormat.SPLUNK: ".splunk",
            ExportFormat.ELK: ".ndjson",
            ExportFormat.CEF: ".cef",
            ExportFormat.SYSLOG: ".log",
        }.get(config.format, ".json")

        output_path = output_dir / f"audit_export_{timestamp}{extension}"

        return self.export(output_path, config, tenant_id)


def main():
    parser = argparse.ArgumentParser(description="Export SAHOOL audit logs")
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Input JSON file with audit logs",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Output file path",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["json", "jsonl", "csv", "splunk", "elk", "cef", "syslog"],
        default="json",
        help="Export format",
    )
    parser.add_argument(
        "--tenant-id",
        "-t",
        help="Filter by tenant ID",
    )
    parser.add_argument(
        "--redact",
        "-r",
        choices=["none", "basic", "standard", "strict"],
        default="standard",
        help="PII redaction level",
    )
    parser.add_argument(
        "--compress",
        "-c",
        action="store_true",
        help="Compress output with gzip",
    )
    parser.add_argument(
        "--flatten",
        action="store_true",
        help="Flatten nested JSON",
    )
    parser.add_argument(
        "--no-hash-chain",
        action="store_true",
        help="Exclude hash chain fields",
    )
    args = parser.parse_args()

    # Build config
    format_map = {
        "json": ExportFormat.JSON,
        "jsonl": ExportFormat.JSONL,
        "csv": ExportFormat.CSV,
        "splunk": ExportFormat.SPLUNK,
        "elk": ExportFormat.ELK,
        "cef": ExportFormat.CEF,
        "syslog": ExportFormat.SYSLOG,
    }

    redact_map = {
        "none": RedactionLevel.NONE,
        "basic": RedactionLevel.BASIC,
        "standard": RedactionLevel.STANDARD,
        "strict": RedactionLevel.STRICT,
    }

    config = ExportConfig(
        format=format_map[args.format],
        redaction_level=redact_map[args.redact],
        compress=args.compress,
        flatten_json=args.flatten,
        include_hash_chain=not args.no_hash_chain,
    )

    # Export
    exporter = AuditDataExporter()
    exporter.load_from_file(Path(args.input))
    result = exporter.export(
        output_path=Path(args.output),
        config=config,
        tenant_id=args.tenant_id,
    )

    if result.success:
        print(f"Export Complete: {result.format.upper()}")
        print(f"  Entries: {result.entries_exported:,}")
        print(f"  Size: {result.file_size_bytes:,} bytes")
        print(f"  Compressed: {result.compressed}")
        print(f"  Duration: {result.duration_ms:.2f}ms")
        print(f"  Checksum: {result.checksum}")
        print(f"  Output: {result.output_path}")
    else:
        print(f"Export Failed: {', '.join(result.errors)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
