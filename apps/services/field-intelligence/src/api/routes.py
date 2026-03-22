"""
مسارات API لخدمة ذكاء الحقول
Field Intelligence API Routes

Storage: PostgreSQL with asyncpg (with in-memory fallback for testing)
التخزين: PostgreSQL مع asyncpg (مع احتياطي في الذاكرة للاختبار)
"""

import json
import logging
from datetime import UTC, datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query, Request

from ..models.events import EventCreate, EventResponse, EventStatus, EventType
from ..models.rules import (
    Rule,
    RuleConditionGroup,
    RuleCreate,
    RuleResponse,
    RuleStatus,
    RuleUpdate,
)
from ..services.event_processor import EventProcessor
from ..services.rules_engine import RulesEngine


def _sanitize_log_input(value: str, max_length: int = 100) -> str:
    """Sanitize user input for safe logging to prevent log injection."""
    if value is None:
        return ""
    return str(value).replace("\n", "").replace("\r", "").replace("\t", "")[:max_length]


# Database imports
try:
    from ..database import events_repo, get_pool, rules_repo

    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

logger = logging.getLogger(__name__)

# إنشاء الموجّه
router = APIRouter()

# In-memory fallback storage (used when PostgreSQL is not available)
# التخزين الاحتياطي في الذاكرة (يستخدم عندما لا تتوفر PostgreSQL)
_events_fallback: dict[str, EventResponse] = {}
_rules_fallback: dict[str, Rule] = {}


async def is_db_connected() -> bool:
    """Check if database is connected"""
    if not DB_AVAILABLE:
        return False
    try:
        pool = await get_pool()
        return pool is not None
    except Exception:
        return False


# محركات المعالجة
rules_engine = RulesEngine()
event_processor = EventProcessor(rules_engine)


# ═══════════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════════


def get_tenant_id(x_tenant_id: str | None = Header(None, alias="X-Tenant-Id")) -> str:
    """استخراج معرف المستأجر من الرأس"""
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-Id header is required")
    return x_tenant_id


# ═══════════════════════════════════════════════════════════════════════════════
# Event Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@router.post("/events", response_model=EventResponse, tags=["Events"])
async def create_event(
    event_data: EventCreate,
    request: Request,
    tenant_id: str = Depends(get_tenant_id),
):
    """
    إنشاء حدث حقلي جديد
    Create a new field event

    يقوم بـ:
    - إنشاء الحدث
    - تقييم القواعد المطابقة
    - تنفيذ الإجراءات (مهام، إشعارات، تنبيهات)
    """
    try:
        # التحقق من تطابق المستأجر
        if event_data.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="Tenant ID mismatch")

        # Check if database is available
        db_connected = await is_db_connected()

        # جلب القواعد النشطة للمستأجر
        if db_connected:
            # Fetch from PostgreSQL
            rules_data = await rules_repo.get_active_rules_for_tenant(tenant_id)
            tenant_rules = [
                Rule(
                    rule_id=r["rule_id"],
                    tenant_id=r["tenant_id"],
                    name=r["name"],
                    name_ar=r.get("name_ar"),
                    description=r.get("description"),
                    description_ar=r.get("description_ar"),
                    status=RuleStatus(r["status"]),
                    field_ids=r.get("field_ids", []),
                    event_types=r.get("event_types", []),
                    conditions=RuleConditionGroup(**r["conditions"]),
                    actions=r.get("actions", []),
                    cooldown_minutes=r.get("cooldown_minutes", 60),
                    priority=r.get("priority", 100),
                    created_at=r["created_at"],
                    updated_at=r["updated_at"],
                    last_triggered_at=r.get("last_triggered_at"),
                    trigger_count=r.get("trigger_count", 0),
                    metadata=r.get("metadata", {}),
                )
                for r in rules_data
            ]
        else:
            # Fallback to in-memory
            tenant_rules = [
                r for r in _rules_fallback.values() if r.tenant_id == tenant_id and r.status == RuleStatus.ACTIVE
            ]

        # معالجة الحدث
        event_response = await event_processor.process_event(event_data, tenant_rules)

        # حفظ الحدث
        if db_connected:
            # Save to PostgreSQL
            await events_repo.create(
                event_id=event_response.event_id,
                tenant_id=event_response.tenant_id,
                field_id=event_response.field_id,
                event_type=event_response.event_type.value,
                severity=event_response.severity.value,
                status=event_response.status.value,
                title=event_response.title,
                title_ar=event_response.title_ar,
                description=event_response.description,
                description_ar=event_response.description_ar,
                source_service=event_response.source_service,
                metadata=event_response.metadata,
                location=event_response.location,
                correlation_id=event_response.correlation_id,
                triggered_rules=event_response.triggered_rules,
                created_tasks=event_response.created_tasks,
                notifications_sent=event_response.notifications_sent,
            )
        else:
            # Fallback to in-memory
            _events_fallback[event_response.event_id] = event_response

        logger.info(
            "✓ تم إنشاء حدث %s للحقل %s",
            _sanitize_log_input(event_response.event_id),
            _sanitize_log_input(event_data.field_id),
        )

        # Publish processed event to NATS for downstream services
        nc = getattr(request.app.state, "nc", None)
        if nc:
            try:
                nats_payload = json.dumps(
                    {
                        "event_id": event_response.event_id,
                        "tenant_id": event_response.tenant_id,
                        "field_id": event_response.field_id,
                        "event_type": event_response.event_type.value,
                        "severity": event_response.severity.value
                        if hasattr(event_response.severity, "value")
                        else str(event_response.severity),
                        "status": event_response.status.value,
                        "title": event_response.title,
                        "source_service": event_response.source_service,
                        "triggered_rules": event_response.triggered_rules,
                        "created_tasks": event_response.created_tasks,
                        "notifications_sent": event_response.notifications_sent,
                        "timestamp": datetime.now(UTC).isoformat(),
                    },
                    default=str,
                ).encode()
                subject = "sahool.field_intelligence.event_processed"
                await nc.publish(subject, nats_payload)
                logger.info("NATS event published: %s for %s", subject, _sanitize_log_input(event_response.event_id))
            except Exception as pub_err:
                logger.warning("Failed to publish NATS event: %s", str(pub_err))

        return event_response

    except HTTPException:
        raise
    except Exception:
        logger.error("خطأ في إنشاء الحدث", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create event")


@router.get("/events/{event_id}", response_model=EventResponse, tags=["Events"])
async def get_event(
    event_id: str = Path(..., description="معرف الحدث"),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    جلب حدث محدد
    Get a specific event
    """
    db_connected = await is_db_connected()

    if db_connected:
        # Fetch from PostgreSQL
        event_data = await events_repo.get_by_id(event_id, tenant_id)
        if not event_data:
            raise HTTPException(status_code=404, detail="Event not found")

        return EventResponse(
            event_id=event_data["event_id"],
            tenant_id=event_data["tenant_id"],
            field_id=event_data["field_id"],
            event_type=EventType(event_data["event_type"]),
            severity=event_data["severity"],
            status=EventStatus(event_data["status"]),
            title=event_data["title"],
            title_ar=event_data.get("title_ar"),
            description=event_data["description"],
            description_ar=event_data.get("description_ar"),
            source_service=event_data["source_service"],
            metadata=event_data.get("metadata", {}),
            location=event_data.get("location"),
            created_at=event_data["created_at"],
            acknowledged_at=event_data.get("acknowledged_at"),
            resolved_at=event_data.get("resolved_at"),
            correlation_id=event_data.get("correlation_id"),
            triggered_rules=event_data.get("triggered_rules", []),
            created_tasks=event_data.get("created_tasks", []),
            notifications_sent=event_data.get("notifications_sent", 0),
        )
    else:
        # Fallback to in-memory
        if event_id not in _events_fallback:
            raise HTTPException(status_code=404, detail="Event not found")

        event = _events_fallback[event_id]

        # التحقق من صلاحية الوصول
        if event.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")

        return event


@router.get("/events", response_model=dict[str, Any], tags=["Events"])
async def list_events(
    field_id: str | None = Query(None, description="تصفية حسب الحقل"),
    event_type: EventType | None = Query(None, description="تصفية حسب نوع الحدث"),
    status: EventStatus | None = Query(None, description="تصفية حسب الحالة"),
    start_date: datetime | None = Query(None, description="من تاريخ"),
    end_date: datetime | None = Query(None, description="إلى تاريخ"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    قائمة الأحداث مع الفلترة
    List events with filters
    """
    db_connected = await is_db_connected()

    if db_connected:
        # Fetch from PostgreSQL
        items_data, total = await events_repo.list_events(
            tenant_id=tenant_id,
            field_id=field_id,
            event_type=event_type.value if event_type else None,
            status=status.value if status else None,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit,
        )

        items = [
            EventResponse(
                event_id=e["event_id"],
                tenant_id=e["tenant_id"],
                field_id=e["field_id"],
                event_type=EventType(e["event_type"]),
                severity=e["severity"],
                status=EventStatus(e["status"]),
                title=e["title"],
                title_ar=e.get("title_ar"),
                description=e["description"],
                description_ar=e.get("description_ar"),
                source_service=e["source_service"],
                metadata=e.get("metadata", {}),
                location=e.get("location"),
                created_at=e["created_at"],
                acknowledged_at=e.get("acknowledged_at"),
                resolved_at=e.get("resolved_at"),
                correlation_id=e.get("correlation_id"),
                triggered_rules=e.get("triggered_rules", []),
                created_tasks=e.get("created_tasks", []),
                notifications_sent=e.get("notifications_sent", 0),
            )
            for e in items_data
        ]
    else:
        # Fallback to in-memory
        # فلترة الأحداث
        filtered = [e for e in _events_fallback.values() if e.tenant_id == tenant_id]

        if field_id:
            filtered = [e for e in filtered if e.field_id == field_id]
        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]
        if status:
            filtered = [e for e in filtered if e.status == status]
        if start_date:
            filtered = [e for e in filtered if e.created_at >= start_date]
        if end_date:
            filtered = [e for e in filtered if e.created_at <= end_date]

        # الترتيب (الأحدث أولاً)
        filtered.sort(key=lambda e: e.created_at, reverse=True)

        # التقسيم
        total = len(filtered)
        items = filtered[skip : skip + limit]

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": skip + limit < total,
    }


@router.patch("/events/{event_id}/status", response_model=EventResponse, tags=["Events"])
async def update_event_status(
    event_id: str = Path(..., description="معرف الحدث"),
    new_status: EventStatus = Query(..., description="الحالة الجديدة"),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    تحديث حالة الحدث
    Update event status
    """
    db_connected = await is_db_connected()

    acknowledged_at = None
    resolved_at = None

    if new_status == EventStatus.ACKNOWLEDGED:
        acknowledged_at = datetime.now(UTC)
    elif new_status == EventStatus.RESOLVED:
        resolved_at = datetime.now(UTC)

    if db_connected:
        # Update in PostgreSQL
        event_data = await events_repo.update_status(
            event_id=event_id,
            tenant_id=tenant_id,
            new_status=new_status.value,
            acknowledged_at=acknowledged_at,
            resolved_at=resolved_at,
        )

        if not event_data:
            raise HTTPException(status_code=404, detail="Event not found")

        logger.info("✓ تم تحديث حالة الحدث %s إلى %s", _sanitize_log_input(event_id), new_status.value)

        return EventResponse(
            event_id=event_data["event_id"],
            tenant_id=event_data["tenant_id"],
            field_id=event_data["field_id"],
            event_type=EventType(event_data["event_type"]),
            severity=event_data["severity"],
            status=EventStatus(event_data["status"]),
            title=event_data["title"],
            title_ar=event_data.get("title_ar"),
            description=event_data["description"],
            description_ar=event_data.get("description_ar"),
            source_service=event_data["source_service"],
            metadata=event_data.get("metadata", {}),
            location=event_data.get("location"),
            created_at=event_data["created_at"],
            acknowledged_at=event_data.get("acknowledged_at"),
            resolved_at=event_data.get("resolved_at"),
            correlation_id=event_data.get("correlation_id"),
            triggered_rules=event_data.get("triggered_rules", []),
            created_tasks=event_data.get("created_tasks", []),
            notifications_sent=event_data.get("notifications_sent", 0),
        )
    else:
        # Fallback to in-memory
        if event_id not in _events_fallback:
            raise HTTPException(status_code=404, detail="Event not found")

        event = _events_fallback[event_id]

        # التحقق من صلاحية الوصول
        if event.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # تحديث الحالة
        event.status = new_status

        if acknowledged_at:
            event.acknowledged_at = acknowledged_at
        if resolved_at:
            event.resolved_at = resolved_at

        _events_fallback[event_id] = event

        logger.info("✓ تم تحديث حالة الحدث %s إلى %s", _sanitize_log_input(event_id), new_status.value)

        return event


@router.get("/events/field/{field_id}/stats", response_model=dict[str, Any], tags=["Events"])
async def get_field_event_stats(
    field_id: str = Path(..., description="معرف الحقل"),
    days: int = Query(30, ge=1, le=90, description="عدد الأيام للإحصائيات"),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    إحصائيات الأحداث للحقل
    Event statistics for a field
    """
    from datetime import timedelta

    cutoff = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    cutoff = cutoff - timedelta(days=days)

    db_connected = await is_db_connected()

    if db_connected:
        # Fetch from PostgreSQL
        events_data = await events_repo.get_field_stats(tenant_id, field_id, cutoff)
        recent_events = events_data
    else:
        # Fallback to in-memory
        # فلترة أحداث الحقل
        field_events = [e for e in _events_fallback.values() if e.tenant_id == tenant_id and e.field_id == field_id]
        recent_events = [e for e in field_events if e.created_at >= cutoff]

    # إحصائيات
    total = len(recent_events)
    by_type: dict[str, int] = {}
    by_severity: dict[str, int] = {}
    by_status: dict[str, int] = {}

    for event in recent_events:
        if db_connected:
            event_type = event["event_type"]
            severity = event["severity"]
            status = event["status"]
        else:
            event_type = event.event_type.value
            severity = event.severity.value
            status = event.status.value

        by_type[event_type] = by_type.get(event_type, 0) + 1
        by_severity[severity] = by_severity.get(severity, 0) + 1
        by_status[status] = by_status.get(status, 0) + 1

    return {
        "field_id": field_id,
        "period_days": days,
        "total_events": total,
        "by_type": by_type,
        "by_severity": by_severity,
        "by_status": by_status,
        "most_common_type": max(by_type.items(), key=lambda x: x[1])[0] if by_type else None,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Rules Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@router.post("/rules", response_model=RuleResponse, tags=["Rules"])
async def create_rule(
    rule_data: RuleCreate,
    tenant_id: str = Depends(get_tenant_id),
):
    """
    إنشاء قاعدة أتمتة جديدة
    Create a new automation rule
    """
    try:
        # التحقق من تطابق المستأجر
        if rule_data.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="Tenant ID mismatch")

        rule_id = str(uuid4())
        now = datetime.now(UTC)

        db_connected = await is_db_connected()

        if db_connected:
            # Save to PostgreSQL
            # Convert actions to list of dicts for JSON storage
            actions_data = [a.model_dump() for a in rule_data.actions]

            rule_row = await rules_repo.create(
                rule_id=rule_id,
                tenant_id=rule_data.tenant_id,
                name=rule_data.name,
                name_ar=rule_data.name_ar,
                description=rule_data.description,
                description_ar=rule_data.description_ar,
                status=rule_data.status.value,
                field_ids=rule_data.field_ids,
                event_types=rule_data.event_types,
                conditions=rule_data.conditions.model_dump(),
                actions=actions_data,
                cooldown_minutes=rule_data.cooldown_minutes,
                priority=rule_data.priority,
                metadata=rule_data.metadata,
            )

            if not rule_row:
                raise HTTPException(status_code=500, detail="Failed to create rule in database")

            logger.info(
                "✓ تم إنشاء قاعدة %s: %s",
                _sanitize_log_input(rule_id),
                _sanitize_log_input(rule_data.name),
            )

            return RuleResponse(
                rule_id=rule_row["rule_id"],
                tenant_id=rule_row["tenant_id"],
                name=rule_row["name"],
                name_ar=rule_row.get("name_ar"),
                description=rule_row.get("description"),
                description_ar=rule_row.get("description_ar"),
                status=RuleStatus(rule_row["status"]),
                field_ids=rule_row.get("field_ids", []),
                event_types=rule_row.get("event_types", []),
                conditions=RuleConditionGroup(**rule_row["conditions"]),
                actions=rule_row.get("actions", []),
                cooldown_minutes=rule_row.get("cooldown_minutes", 60),
                priority=rule_row.get("priority", 100),
                created_at=rule_row["created_at"],
                updated_at=rule_row["updated_at"],
                last_triggered_at=rule_row.get("last_triggered_at"),
                trigger_count=rule_row.get("trigger_count", 0),
                metadata=rule_row.get("metadata", {}),
            )
        else:
            # Fallback to in-memory
            rule = Rule(
                rule_id=rule_id,
                tenant_id=rule_data.tenant_id,
                name=rule_data.name,
                name_ar=rule_data.name_ar,
                description=rule_data.description,
                description_ar=rule_data.description_ar,
                status=rule_data.status,
                field_ids=rule_data.field_ids,
                event_types=rule_data.event_types,
                conditions=rule_data.conditions,
                actions=rule_data.actions,
                cooldown_minutes=rule_data.cooldown_minutes,
                priority=rule_data.priority,
                created_at=now,
                updated_at=now,
                metadata=rule_data.metadata,
            )

            _rules_fallback[rule_id] = rule

            logger.info(
                "✓ تم إنشاء قاعدة %s: %s",
                _sanitize_log_input(rule_id),
                _sanitize_log_input(rule.name),
            )

            return RuleResponse(**rule.model_dump())

    except HTTPException:
        raise
    except Exception as e:
        logger.error("خطأ في إنشاء القاعدة", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create rule: {str(e)}")


@router.get("/rules/{rule_id}", response_model=RuleResponse, tags=["Rules"])
async def get_rule(
    rule_id: str = Path(..., description="معرف القاعدة"),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    جلب قاعدة محددة
    Get a specific rule
    """
    db_connected = await is_db_connected()

    if db_connected:
        # Fetch from PostgreSQL
        rule_data = await rules_repo.get_by_id(rule_id, tenant_id)
        if not rule_data:
            raise HTTPException(status_code=404, detail="Rule not found")

        return RuleResponse(
            rule_id=rule_data["rule_id"],
            tenant_id=rule_data["tenant_id"],
            name=rule_data["name"],
            name_ar=rule_data.get("name_ar"),
            description=rule_data.get("description"),
            description_ar=rule_data.get("description_ar"),
            status=RuleStatus(rule_data["status"]),
            field_ids=rule_data.get("field_ids", []),
            event_types=rule_data.get("event_types", []),
            conditions=RuleConditionGroup(**rule_data["conditions"]),
            actions=rule_data.get("actions", []),
            cooldown_minutes=rule_data.get("cooldown_minutes", 60),
            priority=rule_data.get("priority", 100),
            created_at=rule_data["created_at"],
            updated_at=rule_data["updated_at"],
            last_triggered_at=rule_data.get("last_triggered_at"),
            trigger_count=rule_data.get("trigger_count", 0),
            metadata=rule_data.get("metadata", {}),
        )
    else:
        # Fallback to in-memory
        if rule_id not in _rules_fallback:
            raise HTTPException(status_code=404, detail="Rule not found")

        rule = _rules_fallback[rule_id]

        # التحقق من صلاحية الوصول
        if rule.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")

        return RuleResponse(**rule.model_dump())


@router.get("/rules", response_model=dict[str, Any], tags=["Rules"])
async def list_rules(
    field_id: str | None = Query(None, description="تصفية حسب الحقل"),
    status: RuleStatus | None = Query(None, description="تصفية حسب الحالة"),
    event_type: str | None = Query(None, description="تصفية حسب نوع الحدث"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    قائمة القواعد مع الفلترة
    List rules with filters
    """
    db_connected = await is_db_connected()

    if db_connected:
        # Fetch from PostgreSQL
        rules_data, total = await rules_repo.list_rules(
            tenant_id=tenant_id,
            field_id=field_id,
            status=status.value if status else None,
            event_type=event_type,
            skip=skip,
            limit=limit,
        )

        items = [
            RuleResponse(
                rule_id=r["rule_id"],
                tenant_id=r["tenant_id"],
                name=r["name"],
                name_ar=r.get("name_ar"),
                description=r.get("description"),
                description_ar=r.get("description_ar"),
                status=RuleStatus(r["status"]),
                field_ids=r.get("field_ids", []),
                event_types=r.get("event_types", []),
                conditions=RuleConditionGroup(**r["conditions"]),
                actions=r.get("actions", []),
                cooldown_minutes=r.get("cooldown_minutes", 60),
                priority=r.get("priority", 100),
                created_at=r["created_at"],
                updated_at=r["updated_at"],
                last_triggered_at=r.get("last_triggered_at"),
                trigger_count=r.get("trigger_count", 0),
                metadata=r.get("metadata", {}),
            )
            for r in rules_data
        ]
    else:
        # Fallback to in-memory
        # فلترة القواعد
        filtered = [r for r in _rules_fallback.values() if r.tenant_id == tenant_id]

        if field_id:
            filtered = [r for r in filtered if not r.field_ids or field_id in r.field_ids]
        if status:
            filtered = [r for r in filtered if r.status == status]
        if event_type:
            filtered = [r for r in filtered if not r.event_types or event_type in r.event_types]

        # الترتيب (حسب الأولوية)
        filtered.sort(key=lambda r: r.priority)

        # التقسيم
        total = len(filtered)
        items = [RuleResponse(**r.model_dump()) for r in filtered[skip : skip + limit]]

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": skip + limit < total,
    }


@router.patch("/rules/{rule_id}", response_model=RuleResponse, tags=["Rules"])
async def update_rule(
    rule_id: str = Path(..., description="معرف القاعدة"),
    update_data: RuleUpdate = None,
    tenant_id: str = Depends(get_tenant_id),
):
    """
    تحديث قاعدة
    Update a rule
    """
    db_connected = await is_db_connected()

    if db_connected:
        # Prepare updates for PostgreSQL
        update_dict = update_data.model_dump(exclude_unset=True) if update_data else {}

        # Convert status enum to string
        if "status" in update_dict and update_dict["status"]:
            update_dict["status"] = update_dict["status"].value

        # Convert conditions to dict for JSON
        if "conditions" in update_dict and update_dict["conditions"]:
            update_dict["conditions"] = update_dict["conditions"].model_dump()

        # Convert actions to list of dicts for JSON
        if "actions" in update_dict and update_dict["actions"]:
            update_dict["actions"] = [a.model_dump() for a in update_dict["actions"]]

        rule_data = await rules_repo.update(rule_id, tenant_id, **update_dict)

        if not rule_data:
            raise HTTPException(status_code=404, detail="Rule not found")

        logger.info("✓ تم تحديث القاعدة %s", _sanitize_log_input(rule_id))

        return RuleResponse(
            rule_id=rule_data["rule_id"],
            tenant_id=rule_data["tenant_id"],
            name=rule_data["name"],
            name_ar=rule_data.get("name_ar"),
            description=rule_data.get("description"),
            description_ar=rule_data.get("description_ar"),
            status=RuleStatus(rule_data["status"]),
            field_ids=rule_data.get("field_ids", []),
            event_types=rule_data.get("event_types", []),
            conditions=RuleConditionGroup(**rule_data["conditions"]),
            actions=rule_data.get("actions", []),
            cooldown_minutes=rule_data.get("cooldown_minutes", 60),
            priority=rule_data.get("priority", 100),
            created_at=rule_data["created_at"],
            updated_at=rule_data["updated_at"],
            last_triggered_at=rule_data.get("last_triggered_at"),
            trigger_count=rule_data.get("trigger_count", 0),
            metadata=rule_data.get("metadata", {}),
        )
    else:
        # Fallback to in-memory
        if rule_id not in _rules_fallback:
            raise HTTPException(status_code=404, detail="Rule not found")

        rule = _rules_fallback[rule_id]

        # التحقق من صلاحية الوصول
        if rule.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # تحديث الحقول
        if update_data:
            update_dict = update_data.model_dump(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(rule, field, value)

        rule.updated_at = datetime.now(UTC)
        _rules_fallback[rule_id] = rule

        logger.info("✓ تم تحديث القاعدة %s", _sanitize_log_input(rule_id))

        return RuleResponse(**rule.model_dump())


@router.delete("/rules/{rule_id}", tags=["Rules"])
async def delete_rule(
    rule_id: str = Path(..., description="معرف القاعدة"),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    حذف قاعدة
    Delete a rule
    """
    db_connected = await is_db_connected()

    if db_connected:
        # Delete from PostgreSQL
        deleted = await rules_repo.delete(rule_id, tenant_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Rule not found")

        logger.info("✓ تم حذف القاعدة %s", _sanitize_log_input(rule_id))

        return {"status": "deleted", "rule_id": rule_id}
    else:
        # Fallback to in-memory
        if rule_id not in _rules_fallback:
            raise HTTPException(status_code=404, detail="Rule not found")

        rule = _rules_fallback[rule_id]

        # التحقق من صلاحية الوصول
        if rule.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")

        del _rules_fallback[rule_id]

        logger.info("✓ تم حذف القاعدة %s", _sanitize_log_input(rule_id))

        return {"status": "deleted", "rule_id": rule_id}


@router.post("/rules/{rule_id}/toggle", response_model=RuleResponse, tags=["Rules"])
async def toggle_rule_status(
    rule_id: str = Path(..., description="معرف القاعدة"),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    تبديل حالة القاعدة (نشط/غير نشط)
    Toggle rule status (active/inactive)
    """
    db_connected = await is_db_connected()

    if db_connected:
        # Get current rule from PostgreSQL
        rule_data = await rules_repo.get_by_id(rule_id, tenant_id)

        if not rule_data:
            raise HTTPException(status_code=404, detail="Rule not found")

        # Toggle status
        current_status = RuleStatus(rule_data["status"])
        new_status = RuleStatus.INACTIVE if current_status == RuleStatus.ACTIVE else RuleStatus.ACTIVE

        # Update in PostgreSQL
        updated_rule = await rules_repo.update(rule_id, tenant_id, status=new_status.value)

        if not updated_rule:
            raise HTTPException(status_code=500, detail="Failed to update rule")

        logger.info("✓ تم تبديل حالة القاعدة %s إلى %s", _sanitize_log_input(rule_id), new_status.value)

        return RuleResponse(
            rule_id=updated_rule["rule_id"],
            tenant_id=updated_rule["tenant_id"],
            name=updated_rule["name"],
            name_ar=updated_rule.get("name_ar"),
            description=updated_rule.get("description"),
            description_ar=updated_rule.get("description_ar"),
            status=RuleStatus(updated_rule["status"]),
            field_ids=updated_rule.get("field_ids", []),
            event_types=updated_rule.get("event_types", []),
            conditions=RuleConditionGroup(**updated_rule["conditions"]),
            actions=updated_rule.get("actions", []),
            cooldown_minutes=updated_rule.get("cooldown_minutes", 60),
            priority=updated_rule.get("priority", 100),
            created_at=updated_rule["created_at"],
            updated_at=updated_rule["updated_at"],
            last_triggered_at=updated_rule.get("last_triggered_at"),
            trigger_count=updated_rule.get("trigger_count", 0),
            metadata=updated_rule.get("metadata", {}),
        )
    else:
        # Fallback to in-memory
        if rule_id not in _rules_fallback:
            raise HTTPException(status_code=404, detail="Rule not found")

        rule = _rules_fallback[rule_id]

        # التحقق من صلاحية الوصول
        if rule.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # تبديل الحالة
        if rule.status == RuleStatus.ACTIVE:
            rule.status = RuleStatus.INACTIVE
        else:
            rule.status = RuleStatus.ACTIVE

        rule.updated_at = datetime.now(UTC)
        _rules_fallback[rule_id] = rule

        logger.info("✓ تم تبديل حالة القاعدة %s إلى %s", _sanitize_log_input(rule_id), rule.status.value)

        return RuleResponse(**rule.model_dump())


@router.get("/rules/{rule_id}/stats", response_model=dict[str, Any], tags=["Rules"])
async def get_rule_stats(
    rule_id: str = Path(..., description="معرف القاعدة"),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    إحصائيات تنفيذ القاعدة
    Rule execution statistics
    """
    db_connected = await is_db_connected()

    if db_connected:
        # Fetch from PostgreSQL
        rule_data = await rules_repo.get_by_id(rule_id, tenant_id)

        if not rule_data:
            raise HTTPException(status_code=404, detail="Rule not found")

        conditions = rule_data.get("conditions", {})
        actions = rule_data.get("actions", [])

        # إحصائيات
        stats = {
            "rule_id": rule_id,
            "rule_name": rule_data["name"],
            "status": rule_data["status"],
            "trigger_count": rule_data.get("trigger_count", 0),
            "last_triggered_at": rule_data["last_triggered_at"].isoformat()
            if rule_data.get("last_triggered_at")
            else None,
            "cooldown_minutes": rule_data.get("cooldown_minutes", 60),
            "actions_count": len(actions),
            "conditions_count": len(conditions.get("conditions", [])),
        }

        return stats
    else:
        # Fallback to in-memory
        if rule_id not in _rules_fallback:
            raise HTTPException(status_code=404, detail="Rule not found")

        rule = _rules_fallback[rule_id]

        # التحقق من صلاحية الوصول
        if rule.tenant_id != tenant_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # إحصائيات
        stats = {
            "rule_id": rule_id,
            "rule_name": rule.name,
            "status": rule.status.value,
            "trigger_count": rule.trigger_count,
            "last_triggered_at": rule.last_triggered_at.isoformat() if rule.last_triggered_at else None,
            "cooldown_minutes": rule.cooldown_minutes,
            "actions_count": len(rule.actions),
            "conditions_count": len(rule.conditions.conditions),
        }

        return stats
