"""
مسارات API لخدمة ذكاء الحقول
Field Intelligence API Routes
"""

import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Path, Query

from ..models.events import EventCreate, EventResponse, EventStatus, EventType
from ..models.rules import (
    Rule,
    RuleCreate,
    RuleResponse,
    RuleStatus,
    RuleUpdate,
)
from ..services.event_processor import EventProcessor
from ..services.rules_engine import RulesEngine

logger = logging.getLogger(__name__)

# إنشاء الموجّه
router = APIRouter()

# In-memory storage (في الإنتاج: استخدام PostgreSQL)
# TODO: MIGRATE TO POSTGRESQL
# Current: events_db and rules_db stored in-memory (lost on restart)
# Migration Priority: HIGH - Event history and rules are critical
events_db: dict[str, EventResponse] = {}
rules_db: dict[str, Rule] = {}

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

        # جلب القواعد النشطة للمستأجر
        tenant_rules = [
            r
            for r in rules_db.values()
            if r.tenant_id == tenant_id and r.status == RuleStatus.ACTIVE
        ]

        # معالجة الحدث
        event_response = await event_processor.process_event(event_data, tenant_rules)

        # حفظ الحدث
        events_db[event_response.event_id] = event_response

        logger.info(f"✓ تم إنشاء حدث {event_response.event_id} للحقل {event_data.field_id}")

        return event_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"خطأ في إنشاء الحدث: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")


@router.get("/events/{event_id}", response_model=EventResponse, tags=["Events"])
async def get_event(
    event_id: str = Path(..., description="معرف الحدث"),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    جلب حدث محدد
    Get a specific event
    """
    if event_id not in events_db:
        raise HTTPException(status_code=404, detail="Event not found")

    event = events_db[event_id]

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
    # فلترة الأحداث
    filtered = [e for e in events_db.values() if e.tenant_id == tenant_id]

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
    if event_id not in events_db:
        raise HTTPException(status_code=404, detail="Event not found")

    event = events_db[event_id]

    # التحقق من صلاحية الوصول
    if event.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # تحديث الحالة
    event.status = new_status

    if new_status == EventStatus.ACKNOWLEDGED:
        event.acknowledged_at = datetime.utcnow()
    elif new_status == EventStatus.RESOLVED:
        event.resolved_at = datetime.utcnow()

    events_db[event_id] = event

    logger.info(f"✓ تم تحديث حالة الحدث {event_id} إلى {new_status.value}")

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
    # فلترة أحداث الحقل
    field_events = [
        e for e in events_db.values() if e.tenant_id == tenant_id and e.field_id == field_id
    ]

    # فلترة حسب الفترة الزمنية
    cutoff = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    from datetime import timedelta

    cutoff = cutoff - timedelta(days=days)

    recent_events = [e for e in field_events if e.created_at >= cutoff]

    # إحصائيات
    total = len(recent_events)
    by_type = {}
    by_severity = {}
    by_status = {}

    for event in recent_events:
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
        now = datetime.utcnow()

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

        rules_db[rule_id] = rule

        logger.info(f"✓ تم إنشاء قاعدة {rule_id}: {rule.name}")

        return RuleResponse(**rule.model_dump())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"خطأ في إنشاء القاعدة: {str(e)}", exc_info=True)
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
    if rule_id not in rules_db:
        raise HTTPException(status_code=404, detail="Rule not found")

    rule = rules_db[rule_id]

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
    # فلترة القواعد
    filtered = [r for r in rules_db.values() if r.tenant_id == tenant_id]

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
    items = filtered[skip : skip + limit]

    return {
        "items": [RuleResponse(**r.model_dump()) for r in items],
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
    if rule_id not in rules_db:
        raise HTTPException(status_code=404, detail="Rule not found")

    rule = rules_db[rule_id]

    # التحقق من صلاحية الوصول
    if rule.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # تحديث الحقول
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(rule, field, value)

    rule.updated_at = datetime.utcnow()
    rules_db[rule_id] = rule

    logger.info(f"✓ تم تحديث القاعدة {rule_id}")

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
    if rule_id not in rules_db:
        raise HTTPException(status_code=404, detail="Rule not found")

    rule = rules_db[rule_id]

    # التحقق من صلاحية الوصول
    if rule.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    del rules_db[rule_id]

    logger.info(f"✓ تم حذف القاعدة {rule_id}")

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
    if rule_id not in rules_db:
        raise HTTPException(status_code=404, detail="Rule not found")

    rule = rules_db[rule_id]

    # التحقق من صلاحية الوصول
    if rule.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # تبديل الحالة
    if rule.status == RuleStatus.ACTIVE:
        rule.status = RuleStatus.INACTIVE
    else:
        rule.status = RuleStatus.ACTIVE

    rule.updated_at = datetime.utcnow()
    rules_db[rule_id] = rule

    logger.info(f"✓ تم تبديل حالة القاعدة {rule_id} إلى {rule.status.value}")

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
    if rule_id not in rules_db:
        raise HTTPException(status_code=404, detail="Rule not found")

    rule = rules_db[rule_id]

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
