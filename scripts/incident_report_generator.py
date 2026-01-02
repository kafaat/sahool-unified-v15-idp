#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════════════
SAHOOL IDP - Automated Incident Report Generator
مولد تقارير الحوادث التلقائي
═══════════════════════════════════════════════════════════════════════════════════════

Generates comprehensive incident reports after system events:
- Database migrations
- Outages and recoveries
- Data integrity issues
- Performance incidents

Usage:
    python incident_report_generator.py --type migration --title "Orphaned Data Cleanup"

═══════════════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import argparse
import asyncio
import aiohttp
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("incident-report")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

REPORTS_DIR = Path("incident_reports")
REPORTS_DIR.mkdir(exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════

class IncidentSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class IncidentStatus(Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MONITORING = "monitoring"
    RESOLVED = "resolved"

class IncidentType(Enum):
    OUTAGE = "outage"
    DEGRADATION = "degradation"
    MIGRATION = "migration"
    DATA_INTEGRITY = "data_integrity"
    SECURITY = "security"
    PERFORMANCE = "performance"
    SCHEDULED = "scheduled_maintenance"

# ═══════════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class TimelineEvent:
    timestamp: str
    description: str
    description_ar: str
    actor: str = "system"

@dataclass
class AffectedService:
    name: str
    impact: str
    recovery_time: Optional[str] = None

@dataclass
class ActionTaken:
    description: str
    description_ar: str
    outcome: str
    timestamp: str

@dataclass
class IncidentReport:
    # Identification
    id: str
    title: str
    title_ar: str
    incident_type: str
    severity: str
    status: str

    # Timing
    detected_at: str
    resolved_at: Optional[str] = None
    duration_minutes: Optional[int] = None

    # Description
    summary: str = ""
    summary_ar: str = ""
    root_cause: str = ""
    root_cause_ar: str = ""

    # Impact
    affected_services: List[Dict] = field(default_factory=list)
    affected_users_count: int = 0
    data_loss: bool = False
    data_loss_details: str = ""

    # Response
    timeline: List[Dict] = field(default_factory=list)
    actions_taken: List[Dict] = field(default_factory=list)

    # Prevention
    lessons_learned: List[str] = field(default_factory=list)
    preventive_measures: List[str] = field(default_factory=list)

    # Metadata
    created_by: str = "AI Technical Orchestrator"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_markdown(self) -> str:
        """Generate a Markdown incident report."""
        resolved_status = "✅ Resolved" if self.status == "resolved" else f"🔄 {self.status.title()}"

        services_table = "\n".join([
            f"| {s.get('name', 'N/A')} | {s.get('impact', 'N/A')} | {s.get('recovery_time', 'N/A')} |"
            for s in self.affected_services
        ]) or "| No services affected | - | - |"

        timeline_list = "\n".join([
            f"- **{e.get('timestamp', '')}**: {e.get('description', '')} _{e.get('description_ar', '')}_"
            for e in self.timeline
        ]) or "- No timeline events recorded"

        actions_list = "\n".join([
            f"- {a.get('description', '')} → _{a.get('outcome', '')}_"
            for a in self.actions_taken
        ]) or "- No actions recorded"

        lessons_list = "\n".join([f"- {l}" for l in self.lessons_learned]) or "- None identified"
        prevention_list = "\n".join([f"- {p}" for p in self.preventive_measures]) or "- None planned"

        return f'''# Incident Report: {self.title}
# تقرير الحادث: {self.title_ar}

---

## Overview | نظرة عامة

| Field | Value |
|-------|-------|
| **Incident ID** | `{self.id}` |
| **Status** | {resolved_status} |
| **Severity** | {self.severity.upper()} |
| **Type** | {self.incident_type} |
| **Detected** | {self.detected_at} |
| **Resolved** | {self.resolved_at or "Ongoing"} |
| **Duration** | {self.duration_minutes or "N/A"} minutes |

---

## Summary | الملخص

**English:**
{self.summary}

**العربية:**
{self.summary_ar}

---

## Root Cause | السبب الجذري

**English:**
{self.root_cause}

**العربية:**
{self.root_cause_ar}

---

## Impact | التأثير

| Affected Users | Data Loss |
|----------------|-----------|
| {self.affected_users_count} | {"Yes ⚠️" if self.data_loss else "No ✅"} |

{f"**Data Loss Details:** {self.data_loss_details}" if self.data_loss else ""}

### Affected Services | الخدمات المتأثرة

| Service | Impact | Recovery Time |
|---------|--------|---------------|
{services_table}

---

## Timeline | الجدول الزمني

{timeline_list}

---

## Actions Taken | الإجراءات المتخذة

{actions_list}

---

## Lessons Learned | الدروس المستفادة

{lessons_list}

---

## Preventive Measures | الإجراءات الوقائية

{prevention_list}

---

## Metadata | البيانات الوصفية

- **Report Generated By:** {self.created_by}
- **Report Created:** {self.created_at}
- **Last Updated:** {self.last_updated}

---

*This report was automatically generated by SAHOOL IDP Incident Management System.*
*تم إنشاء هذا التقرير تلقائياً بواسطة نظام إدارة الحوادث في منصة سهول.*
'''

    def to_json(self) -> str:
        """Generate JSON representation."""
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)

    def save(self):
        """Save report to files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"incident_{self.id}_{timestamp}"

        # Save Markdown
        md_path = REPORTS_DIR / f"{base_name}.md"
        md_path.write_text(self.to_markdown(), encoding="utf-8")
        logger.info(f"📝 Saved Markdown report: {md_path}")

        # Save JSON
        json_path = REPORTS_DIR / f"{base_name}.json"
        json_path.write_text(self.to_json(), encoding="utf-8")
        logger.info(f"📄 Saved JSON report: {json_path}")

        return md_path, json_path

# ═══════════════════════════════════════════════════════════════════════════════
# REPORT TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════════

class IncidentReportTemplates:
    """Pre-built templates for common incident types."""

    @staticmethod
    def orphaned_data_cleanup(
        orphaned_fields: int = 0,
        orphaned_sensors: int = 0,
        orphaned_tasks: int = 0,
        duration_minutes: int = 0,
        deadlock_occurred: bool = False,
    ) -> IncidentReport:
        """Template for orphaned data cleanup incidents."""
        now = datetime.now(timezone.utc)
        detected = now - timedelta(minutes=duration_minutes)

        timeline = [
            TimelineEvent(
                timestamp=detected.isoformat(),
                description="Orphaned data detected in database",
                description_ar="تم اكتشاف بيانات يتيمة في قاعدة البيانات",
                actor="DataGuardian-Agent"
            ),
            TimelineEvent(
                timestamp=(detected + timedelta(minutes=1)).isoformat(),
                description="Maintenance mode enabled",
                description_ar="تم تفعيل وضع الصيانة",
                actor="MaintenanceController"
            ),
        ]

        if deadlock_occurred:
            timeline.append(TimelineEvent(
                timestamp=(detected + timedelta(minutes=2)).isoformat(),
                description="Deadlock detected - automatic rollback initiated",
                description_ar="تم اكتشاف تضارب - بدء التراجع التلقائي",
                actor="PostgreSQL"
            ))
            timeline.append(TimelineEvent(
                timestamp=(detected + timedelta(minutes=3)).isoformat(),
                description="Retry with maintenance mode - successful",
                description_ar="إعادة المحاولة في وضع الصيانة - ناجح",
                actor="MigrationController"
            ))

        timeline.append(TimelineEvent(
            timestamp=now.isoformat(),
            description="Migration completed - maintenance mode disabled",
            description_ar="اكتمل التهجير - تم تعطيل وضع الصيانة",
            actor="MaintenanceController"
        ))

        total_cleaned = orphaned_fields + orphaned_sensors + orphaned_tasks

        return IncidentReport(
            id=f"INC-{now.strftime('%Y%m%d%H%M')}",
            title="Orphaned Data Cleanup Migration",
            title_ar="تهجير تنظيف البيانات اليتيمة",
            incident_type=IncidentType.DATA_INTEGRITY.value,
            severity=IncidentSeverity.MEDIUM.value,
            status=IncidentStatus.RESOLVED.value,
            detected_at=detected.isoformat(),
            resolved_at=now.isoformat(),
            duration_minutes=duration_minutes,
            summary=f"Cleaned {total_cleaned} orphaned records ({orphaned_fields} fields, {orphaned_sensors} sensor readings, {orphaned_tasks} tasks) and added foreign key constraints to prevent future occurrences.",
            summary_ar=f"تم تنظيف {total_cleaned} سجل يتيم ({orphaned_fields} حقل، {orphaned_sensors} قراءة حساس، {orphaned_tasks} مهمة) وإضافة قيود المفاتيح الأجنبية لمنع التكرار.",
            root_cause="Missing foreign key constraints allowed creation of records referencing non-existent parent records (users, tenants, fields).",
            root_cause_ar="سمح غياب قيود المفاتيح الأجنبية بإنشاء سجلات تشير إلى سجلات أب غير موجودة (مستخدمين، مستأجرين، حقول).",
            affected_services=[
                {"name": "field-service", "impact": "Fields not visible to users", "recovery_time": f"{duration_minutes} min"},
                {"name": "sensor-service", "impact": "Orphaned sensor data", "recovery_time": f"{duration_minutes} min"},
                {"name": "task-service", "impact": "Orphaned tasks", "recovery_time": f"{duration_minutes} min"},
            ],
            affected_users_count=orphaned_fields,  # Approximate
            data_loss=False,
            data_loss_details="All orphaned data was backed up before deletion. No valid user data was lost.",
            timeline=[asdict(e) for e in timeline],
            actions_taken=[
                {
                    "description": "Backed up orphaned records to recovery tables",
                    "description_ar": "نسخ احتياطي للسجلات اليتيمة في جداول الاسترداد",
                    "outcome": "Success",
                    "timestamp": (detected + timedelta(minutes=1)).isoformat(),
                },
                {
                    "description": f"Deleted {total_cleaned} orphaned records",
                    "description_ar": f"حذف {total_cleaned} سجل يتيم",
                    "outcome": "Success",
                    "timestamp": (now - timedelta(minutes=1)).isoformat(),
                },
                {
                    "description": "Added ON DELETE CASCADE foreign key constraints",
                    "description_ar": "إضافة قيود المفاتيح الأجنبية مع الحذف المتتالي",
                    "outcome": "Success",
                    "timestamp": now.isoformat(),
                },
            ],
            lessons_learned=[
                "Foreign key constraints should be added during initial schema design",
                "يجب إضافة قيود المفاتيح الأجنبية أثناء التصميم الأولي للمخطط",
                "Orphaned data accumulates silently and causes user-facing issues",
                "البيانات اليتيمة تتراكم بصمت وتسبب مشاكل للمستخدمين",
            ],
            preventive_measures=[
                "Add foreign key constraint checks to CI/CD pipeline",
                "إضافة فحوصات قيود المفاتيح الأجنبية إلى خط أنابيب CI/CD",
                "Implement weekly orphaned data detection job",
                "تنفيذ مهمة أسبوعية لاكتشاف البيانات اليتيمة",
                "Add database schema linting to pre-commit hooks",
                "إضافة فحص مخطط قاعدة البيانات إلى pre-commit hooks",
            ],
        )

    @staticmethod
    def database_migration_failure(
        migration_name: str,
        error_message: str,
        rollback_successful: bool,
        duration_minutes: int = 0,
    ) -> IncidentReport:
        """Template for failed database migration incidents."""
        now = datetime.now(timezone.utc)
        detected = now - timedelta(minutes=duration_minutes)

        return IncidentReport(
            id=f"INC-{now.strftime('%Y%m%d%H%M')}",
            title=f"Database Migration Failure: {migration_name}",
            title_ar=f"فشل تهجير قاعدة البيانات: {migration_name}",
            incident_type=IncidentType.MIGRATION.value,
            severity=IncidentSeverity.HIGH.value,
            status=IncidentStatus.RESOLVED.value if rollback_successful else IncidentStatus.INVESTIGATING.value,
            detected_at=detected.isoformat(),
            resolved_at=now.isoformat() if rollback_successful else None,
            duration_minutes=duration_minutes,
            summary=f"Migration '{migration_name}' failed with error: {error_message}. {'Rollback was successful.' if rollback_successful else 'Manual intervention required.'}",
            summary_ar=f"فشل التهجير '{migration_name}' مع الخطأ: {error_message}. {'كان التراجع ناجحاً.' if rollback_successful else 'مطلوب تدخل يدوي.'}",
            root_cause=error_message,
            root_cause_ar=error_message,
            affected_services=[
                {"name": "database", "impact": "Schema change failed", "recovery_time": f"{duration_minutes} min" if rollback_successful else "Unknown"},
            ],
            data_loss=not rollback_successful,
            timeline=[
                {"timestamp": detected.isoformat(), "description": f"Migration {migration_name} started", "description_ar": f"بدء التهجير {migration_name}", "actor": "MigrationController"},
                {"timestamp": (detected + timedelta(minutes=1)).isoformat(), "description": f"Error occurred: {error_message[:50]}...", "description_ar": f"حدث خطأ", "actor": "PostgreSQL"},
                {"timestamp": now.isoformat(), "description": "Rollback executed" if rollback_successful else "Manual intervention required", "description_ar": "تم تنفيذ التراجع" if rollback_successful else "مطلوب تدخل يدوي", "actor": "MigrationController"},
            ],
            actions_taken=[
                {
                    "description": "Automatic rollback initiated",
                    "description_ar": "بدء التراجع التلقائي",
                    "outcome": "Success" if rollback_successful else "Failed",
                    "timestamp": now.isoformat(),
                },
            ],
            lessons_learned=[
                "Always test migrations on a replica first",
                "Run migrations during low-traffic periods",
            ],
            preventive_measures=[
                "Add migration dry-run to CI/CD pipeline",
                "Implement shadow database for testing",
            ],
        )

# ═══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="SAHOOL Incident Report Generator - مولد تقارير الحوادث"
    )

    parser.add_argument("--type", "-t", choices=["migration", "outage", "data", "custom"],
                       default="custom", help="Incident type")
    parser.add_argument("--title", required=True, help="Incident title")
    parser.add_argument("--title-ar", help="Incident title (Arabic)")
    parser.add_argument("--severity", choices=["critical", "high", "medium", "low", "info"],
                       default="medium", help="Severity level")
    parser.add_argument("--duration", type=int, default=0, help="Duration in minutes")

    # For orphaned data template
    parser.add_argument("--orphaned-fields", type=int, default=0)
    parser.add_argument("--orphaned-sensors", type=int, default=0)
    parser.add_argument("--orphaned-tasks", type=int, default=0)
    parser.add_argument("--deadlock", action="store_true")

    args = parser.parse_args()

    if args.type == "data":
        report = IncidentReportTemplates.orphaned_data_cleanup(
            orphaned_fields=args.orphaned_fields,
            orphaned_sensors=args.orphaned_sensors,
            orphaned_tasks=args.orphaned_tasks,
            duration_minutes=args.duration,
            deadlock_occurred=args.deadlock,
        )
    else:
        # Custom report
        report = IncidentReport(
            id=f"INC-{datetime.now().strftime('%Y%m%d%H%M')}",
            title=args.title,
            title_ar=args.title_ar or args.title,
            incident_type=args.type,
            severity=args.severity,
            status="resolved",
            detected_at=datetime.now(timezone.utc).isoformat(),
            duration_minutes=args.duration,
        )

    # Save the report
    md_path, json_path = report.save()

    # Print summary
    print("\n" + "=" * 70)
    print("  📋 INCIDENT REPORT GENERATED")
    print("=" * 70)
    print(f"  ID:       {report.id}")
    print(f"  Title:    {report.title}")
    print(f"  Severity: {report.severity.upper()}")
    print(f"  Status:   {report.status}")
    print(f"  Files:")
    print(f"    - {md_path}")
    print(f"    - {json_path}")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
