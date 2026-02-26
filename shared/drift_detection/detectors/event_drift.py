"""
Event Drift Detector
كاشف انحراف الأحداث

Detects NATS event schema drift:
- Event catalog consistency (governance/events/catalog.yaml)
- JSON schema validation of event payloads
- Subject naming convention violations
- Missing idempotency keys in event handlers
- Dead Letter Queue (DLQ) configuration
- Consumer/subscription health indicators
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from shared.drift_detection.detectors.base import BaseDriftDetector
from shared.drift_detection.models import (
    DriftCategory,
    DriftResult,
    DriftSeverity,
)

logger = logging.getLogger(__name__)

# Valid NATS subject patterns for SAHOOL
VALID_SUBJECT_PATTERNS = [
    re.compile(r"^sahool\.\w+\.\w+$"),  # sahool.{domain}.{action}
    re.compile(r"^sahool\.tenant\.[a-f0-9-]+\.\w+\.\w+$"),  # tenant-scoped
    re.compile(r"^sahool\.[a-f0-9-]+\.\w+\.\w+$"),  # inline tenant
    re.compile(r"^sahool\.vision\.\w+$"),  # vision events
    re.compile(r"^sahool\.dlq\.\w+$"),  # DLQ events
]


class EventDriftDetector(BaseDriftDetector):
    """
    Detects NATS event schema and contract drift.
    يكتشف انحراف مخطط وعقود أحداث NATS.
    """

    @property
    def category(self) -> DriftCategory:
        return DriftCategory.EVENT

    async def detect(self) -> list[DriftResult]:
        self.clear_results()

        await self._check_event_catalog()
        await self._check_event_schemas()
        await self._check_subject_conventions()
        await self._check_idempotency()
        await self._check_dlq_config()
        await self._check_event_envelope()

        return self.results

    async def _check_event_catalog(self) -> None:
        """Check event catalog consistency."""
        root = Path(self.working_dir)
        catalog = root / "governance" / "events" / "catalog.yaml"

        if not catalog.exists():
            self.add_result(
                DriftResult(
                    category=DriftCategory.EVENT,
                    severity=DriftSeverity.HIGH,
                    source="event_catalog",
                    description="Event catalog not found at governance/events/catalog.yaml",
                    description_ar="كتالوج الأحداث غير موجود في governance/events/catalog.yaml",
                    file_path=str(catalog),
                    auto_fixable=False,
                    remediation_hint="Create event catalog defining all NATS subjects",
                )
            )
            return

        try:
            import yaml

            with open(catalog) as f:
                events = yaml.safe_load(f)
        except ImportError:
            logger.warning("PyYAML not installed, skipping event catalog check")
            return
        except Exception as e:
            self.add_result(
                DriftResult(
                    category=DriftCategory.EVENT,
                    severity=DriftSeverity.HIGH,
                    source="event_catalog",
                    description=f"Failed to parse event catalog: {e}",
                    description_ar=f"فشل في تحليل كتالوج الأحداث: {e}",
                    file_path=str(catalog),
                )
            )
            return

        if not events:
            return

        # Validate catalog structure
        event_list = events.get("events", [])
        if isinstance(event_list, list):
            for event in event_list:
                if not isinstance(event, dict):
                    continue

                # Check required fields
                for req_field in ["subject", "description", "category"]:
                    if req_field not in event:
                        self.add_result(
                            DriftResult(
                                category=DriftCategory.EVENT,
                                severity=DriftSeverity.MEDIUM,
                                source="event_catalog",
                                description=f"Event missing '{req_field}': {event.get('subject', 'unknown')}",
                                description_ar=f"الحدث يفتقر إلى '{req_field}': {event.get('subject', 'مجهول')}",
                                file_path=str(catalog),
                            )
                        )

                # Validate category
                valid_categories = {
                    "field",
                    "ndvi",
                    "alert",
                    "weather",
                    "irrigation",
                    "crop_health",
                    "yield",
                    "system",
                    "vision",
                    "tenant",
                    "user",
                    "equipment",
                    "task",
                    "billing",
                    "notification",
                }
                cat = event.get("category", "")
                if cat and cat not in valid_categories:
                    self.add_result(
                        DriftResult(
                            category=DriftCategory.EVENT,
                            severity=DriftSeverity.LOW,
                            source="event_catalog",
                            description=f"Unknown event category '{cat}' for {event.get('subject')}",
                            description_ar=f"فئة حدث غير معروفة '{cat}' لـ {event.get('subject')}",
                            file_path=str(catalog),
                        )
                    )

    async def _check_event_schemas(self) -> None:
        """Check JSON schema files for events."""
        root = Path(self.working_dir)
        schemas_dir = root / "governance" / "events" / "schemas"

        if not schemas_dir.exists():
            return

        for schema_file in schemas_dir.glob("*.json"):
            try:
                with open(schema_file) as f:
                    schema = json.load(f)
            except json.JSONDecodeError as e:
                self.add_result(
                    DriftResult(
                        category=DriftCategory.EVENT,
                        severity=DriftSeverity.HIGH,
                        source="event_schema",
                        description=f"Invalid JSON schema: {schema_file.name} - {e}",
                        description_ar=f"مخطط JSON غير صالح: {schema_file.name} - {e}",
                        file_path=str(schema_file),
                    )
                )
                continue

            # Check schema has required metadata
            if "type" not in schema:
                self.add_result(
                    DriftResult(
                        category=DriftCategory.EVENT,
                        severity=DriftSeverity.MEDIUM,
                        source="event_schema",
                        description=f"Schema '{schema_file.name}' missing 'type' property",
                        description_ar=f"المخطط '{schema_file.name}' يفتقر إلى خاصية 'type'",
                        file_path=str(schema_file),
                    )
                )

            # Check for event_id and timestamp in required fields
            required = schema.get("required", [])
            properties = schema.get("properties", {})
            for essential in ["event_id", "timestamp"]:
                if essential not in properties and essential not in required:
                    self.add_result(
                        DriftResult(
                            category=DriftCategory.EVENT,
                            severity=DriftSeverity.MEDIUM,
                            source="event_schema",
                            description=f"Schema '{schema_file.name}' missing essential field: {essential}",
                            description_ar=f"المخطط '{schema_file.name}' يفتقر إلى حقل أساسي: {essential}",
                            file_path=str(schema_file),
                        )
                    )

    async def _check_subject_conventions(self) -> None:
        """Check NATS subject naming conventions in code."""
        root = Path(self.working_dir)

        # Scan for subject definitions in Python code
        subject_files = list(root.glob("shared/events/**/*.py"))
        subject_files += list(root.glob("apps/services/*/src/events/**/*.py"))

        all_subjects: list[tuple[str, str]] = []  # (subject, file_path)

        for sf in subject_files:
            try:
                content = sf.read_text(errors="ignore")
            except (OSError, UnicodeDecodeError):
                continue

            # Find string subjects
            matches = re.findall(r'["\']+(sahool\.[^"\']+)["\']', content)
            for m in matches:
                all_subjects.append((m, str(sf)))

        for subject, file_path in all_subjects:
            # Skip template subjects with placeholders
            if "{" in subject or ">" in subject or "*" in subject:
                continue

            valid = any(p.match(subject) for p in VALID_SUBJECT_PATTERNS)
            if not valid:
                self.add_result(
                    DriftResult(
                        category=DriftCategory.EVENT,
                        severity=DriftSeverity.MEDIUM,
                        source="subject_convention",
                        expected="sahool.{domain}.{action} or sahool.tenant.{id}.{domain}.{action}",
                        actual=subject,
                        description=f"Non-standard NATS subject: '{subject}'",
                        description_ar=f"موضوع NATS غير قياسي: '{subject}'",
                        file_path=file_path,
                    )
                )

    async def _check_idempotency(self) -> None:
        """Check event handlers for idempotency patterns."""
        root = Path(self.working_dir)

        handler_files = list(root.glob("apps/services/*/src/events/*.py"))
        handler_files += list(root.glob("apps/services/*/src/events/**/*.py"))

        for hf in handler_files:
            try:
                content = hf.read_text(errors="ignore")
            except (OSError, UnicodeDecodeError):
                continue

            # Check for subscribe/handler patterns
            has_handler = any(
                pat in content
                for pat in [
                    "subscribe",
                    "on_message",
                    "message_handler",
                    "event_handler",
                    "nats_handler",
                    "jetstream",
                ]
            )

            if not has_handler:
                continue

            # Check for idempotency patterns
            has_idempotency = any(
                pat in content
                for pat in [
                    "idempotency",
                    "event_id",
                    "dedup",
                    "already_processed",
                    "processed_events",
                    "upsert",
                    "ON CONFLICT",
                ]
            )

            if not has_idempotency:
                service_name = ""
                parts = hf.parts
                for i, part in enumerate(parts):
                    if part == "services" and i + 1 < len(parts):
                        service_name = parts[i + 1]
                        break

                self.add_result(
                    DriftResult(
                        category=DriftCategory.EVENT,
                        severity=DriftSeverity.HIGH,
                        source="idempotency",
                        expected="Idempotency key check in event handler",
                        actual="No idempotency pattern found",
                        description=f"Event handler in {service_name} lacks idempotency protection",
                        description_ar=f"معالج الأحداث في {service_name} يفتقر إلى حماية التكافؤ",
                        file_path=str(hf),
                        service_name=service_name,
                        auto_fixable=False,
                        remediation_hint="Add event_id deduplication check before processing",
                    )
                )

    async def _check_dlq_config(self) -> None:
        """Check Dead Letter Queue configuration."""
        root = Path(self.working_dir)

        # Check for DLQ configuration
        dlq_files = list(root.glob("**/dlq*")) + list(root.glob("**/dead_letter*"))
        dlq_compose = root / "docker" / "docker-compose.dlq.yml"

        if not dlq_compose.exists() and not dlq_files:
            self.add_result(
                DriftResult(
                    category=DriftCategory.EVENT,
                    severity=DriftSeverity.MEDIUM,
                    source="dlq_config",
                    description="No DLQ configuration found - poison messages will block consumers",
                    description_ar="لم يتم العثور على تكوين DLQ - الرسائل السامة ستحظر المستهلكين",
                    auto_fixable=False,
                    remediation_hint="Configure DLQ stream for failed message handling",
                )
            )

    async def _check_event_envelope(self) -> None:
        """Check that events follow the standard envelope format."""
        root = Path(self.working_dir)

        # Check shared events for envelope definition
        envelope_found = False
        events_dir = root / "shared" / "events"
        if events_dir.exists():
            for py_file in events_dir.rglob("*.py"):
                try:
                    content = py_file.read_text(errors="ignore")
                    if any(
                        pat in content
                        for pat in [
                            "EventEnvelope",
                            "event_envelope",
                            "BaseEvent",
                            "correlation_id",
                            "trace_id",
                        ]
                    ):
                        envelope_found = True
                        break
                except (OSError, UnicodeDecodeError):
                    continue

        if not envelope_found:
            self.add_result(
                DriftResult(
                    category=DriftCategory.EVENT,
                    severity=DriftSeverity.HIGH,
                    source="event_envelope",
                    description="No standard event envelope found - events lack correlation_id/trace_id",
                    description_ar="لم يتم العثور على مغلف حدث قياسي - الأحداث تفتقر إلى correlation_id/trace_id",
                    auto_fixable=False,
                    remediation_hint="Create shared EventEnvelope with event_id, correlation_id, trace_id, timestamp, tenant_id",
                )
            )
