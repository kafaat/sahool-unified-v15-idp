"""
Expert Support System - نظام دعم الخبراء
Real-time expert consultation for farmers

Features:
- Expert registration and profiles
- Support request management
- Real-time expert matching
- Consultation tracking and ratings
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from .models import (
    ExpertProfile,
    ExpertRequestStatus,
    ExpertSpecialty,
    ExpertSupportRequest,
    OnlineExpert,
)

router = APIRouter(prefix="/experts", tags=["Expert System"])


# ═══════════════════════════════════════════════════════════════════════════════
# Request/Response Models
# ═══════════════════════════════════════════════════════════════════════════════


class CreateExpertProfileRequest(BaseModel):
    """Request to create expert profile"""

    tenant_id: str
    user_id: str
    name: str
    name_ar: Optional[str] = None
    specialties: list[str] = Field(default_factory=lambda: ["general"])
    bio: Optional[str] = None
    bio_ar: Optional[str] = None
    governorates: list[str] = Field(default_factory=list)


class ExpertProfileResponse(BaseModel):
    """Expert profile response"""

    expert_id: str
    user_id: str
    name: str
    name_ar: Optional[str]
    specialties: list[str]
    specialties_ar: list[str]
    bio: Optional[str]
    bio_ar: Optional[str]
    governorates: list[str]
    is_available: bool
    is_verified: bool
    total_consultations: int
    avg_rating: float
    rating_count: int


class CreateSupportRequestRequest(BaseModel):
    """Farmer request for expert support"""

    tenant_id: str
    farmer_id: str
    farmer_name: str
    governorate: Optional[str] = None
    topic: str
    topic_ar: Optional[str] = None
    description: Optional[str] = None
    specialty_needed: str = "general"
    field_id: Optional[str] = None
    diagnosis_id: Optional[str] = None
    priority: str = "normal"


class SupportRequestResponse(BaseModel):
    """Support request response"""

    request_id: str
    farmer_id: str
    farmer_name: str
    topic: str
    topic_ar: Optional[str]
    specialty_needed: str
    status: str
    status_ar: str
    priority: str
    expert_id: Optional[str]
    expert_name: Optional[str]
    thread_id: Optional[str]
    created_at: str
    accepted_at: Optional[str]
    resolved_at: Optional[str]


class AcceptRequestRequest(BaseModel):
    """Expert accepts a support request"""

    tenant_id: str
    expert_id: str
    expert_name: str


class ResolveRequestRequest(BaseModel):
    """Resolve/close a support request"""

    tenant_id: str
    expert_id: str
    resolution_notes: Optional[str] = None
    resolution_notes_ar: Optional[str] = None


class RateSupportRequest(BaseModel):
    """Farmer rates expert support"""

    tenant_id: str
    farmer_id: str
    rating: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = None


class OnlineExpertsResponse(BaseModel):
    """Online experts count and availability"""

    count: int
    available_count: int
    by_specialty: dict[str, int]


# ═══════════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════════

STATUS_AR = {
    "pending": "في انتظار خبير",
    "accepted": "تم القبول",
    "in_progress": "جاري التنفيذ",
    "resolved": "تم الحل",
    "cancelled": "ملغي",
}

SPECIALTY_AR = {
    "crop_diseases": "أمراض المحاصيل",
    "irrigation": "الري",
    "soil": "التربة",
    "pest_control": "مكافحة الآفات",
    "fertilization": "التسميد",
    "general": "استشارة عامة",
}


def get_specialty_ar(specialties: list[str]) -> list[str]:
    """Get Arabic names for specialties"""
    return [SPECIALTY_AR.get(s, s) for s in specialties]


# ═══════════════════════════════════════════════════════════════════════════════
# Expert Profile Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@router.post("/profiles", response_model=ExpertProfileResponse)
async def create_expert_profile(req: CreateExpertProfileRequest):
    """
    Create a new expert profile
    إنشاء ملف تعريف خبير جديد
    """
    # Check if profile already exists
    existing = await ExpertProfile.filter(user_id=req.user_id).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "profile_exists",
                "message_ar": "ملف الخبير موجود مسبقاً",
                "message_en": "Expert profile already exists for this user",
            },
        )

    # Validate specialties
    valid_specialties = [s.value for s in ExpertSpecialty]
    for spec in req.specialties:
        if spec not in valid_specialties:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_specialty",
                    "message_ar": f"التخصص غير صالح: {spec}",
                    "valid_values": valid_specialties,
                },
            )

    profile = await ExpertProfile.create(
        id=uuid4(),
        tenant_id=req.tenant_id,
        user_id=req.user_id,
        name=req.name,
        name_ar=req.name_ar,
        specialties=req.specialties,
        bio=req.bio,
        bio_ar=req.bio_ar,
        governorates=req.governorates,
    )

    return ExpertProfileResponse(
        expert_id=str(profile.id),
        user_id=profile.user_id,
        name=profile.name,
        name_ar=profile.name_ar,
        specialties=profile.specialties,
        specialties_ar=get_specialty_ar(profile.specialties),
        bio=profile.bio,
        bio_ar=profile.bio_ar,
        governorates=profile.governorates,
        is_available=profile.is_available,
        is_verified=profile.is_verified,
        total_consultations=profile.total_consultations,
        avg_rating=profile.avg_rating,
        rating_count=profile.rating_count,
    )


@router.get("/profiles", response_model=list[ExpertProfileResponse])
async def list_experts(
    tenant_id: str = Query(...),
    specialty: Optional[str] = Query(None, description="Filter by specialty"),
    governorate: Optional[str] = Query(None, description="Filter by governorate"),
    available_only: bool = Query(False, description="Only show available experts"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    List expert profiles with filters
    عرض قائمة الخبراء
    """
    query = ExpertProfile.filter(tenant_id=tenant_id, is_active=True)

    if available_only:
        query = query.filter(is_available=True)

    experts = await query.offset(offset).limit(limit)

    # Filter in Python for JSON fields (specialties, governorates)
    results = []
    for expert in experts:
        if specialty and specialty not in expert.specialties:
            continue
        if governorate and governorate not in expert.governorates:
            continue
        results.append(
            ExpertProfileResponse(
                expert_id=str(expert.id),
                user_id=expert.user_id,
                name=expert.name,
                name_ar=expert.name_ar,
                specialties=expert.specialties,
                specialties_ar=get_specialty_ar(expert.specialties),
                bio=expert.bio,
                bio_ar=expert.bio_ar,
                governorates=expert.governorates,
                is_available=expert.is_available,
                is_verified=expert.is_verified,
                total_consultations=expert.total_consultations,
                avg_rating=expert.avg_rating,
                rating_count=expert.rating_count,
            )
        )

    return results


@router.get("/profiles/{expert_id}", response_model=ExpertProfileResponse)
async def get_expert_profile(
    expert_id: UUID,
    tenant_id: str = Query(...),
):
    """Get expert profile by ID"""
    expert = await ExpertProfile.filter(id=expert_id, tenant_id=tenant_id).first()
    if not expert:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "expert_not_found",
                "message_ar": "الخبير غير موجود",
            },
        )

    return ExpertProfileResponse(
        expert_id=str(expert.id),
        user_id=expert.user_id,
        name=expert.name,
        name_ar=expert.name_ar,
        specialties=expert.specialties,
        specialties_ar=get_specialty_ar(expert.specialties),
        bio=expert.bio,
        bio_ar=expert.bio_ar,
        governorates=expert.governorates,
        is_available=expert.is_available,
        is_verified=expert.is_verified,
        total_consultations=expert.total_consultations,
        avg_rating=expert.avg_rating,
        rating_count=expert.rating_count,
    )


@router.patch("/profiles/{expert_id}/availability")
async def toggle_availability(
    expert_id: UUID,
    tenant_id: str = Query(...),
    is_available: bool = Query(...),
):
    """
    Toggle expert availability
    تغيير حالة توفر الخبير
    """
    updated = await ExpertProfile.filter(id=expert_id, tenant_id=tenant_id).update(
        is_available=is_available,
        last_online_at=datetime.utcnow() if is_available else None,
    )

    if not updated:
        raise HTTPException(status_code=404, detail="expert_not_found")

    status_ar = "متاح الآن" if is_available else "غير متاح"
    return {
        "expert_id": str(expert_id),
        "is_available": is_available,
        "status_ar": status_ar,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Support Request Endpoints
# ═══════════════════════════════════════════════════════════════════════════════


@router.post("/requests", response_model=SupportRequestResponse)
async def create_support_request(req: CreateSupportRequestRequest):
    """
    Create a support request (farmer asks for expert help)
    إنشاء طلب دعم (مزارع يطلب مساعدة خبير)
    """
    # Validate priority
    if req.priority not in ("low", "normal", "high", "urgent"):
        req.priority = "normal"

    # Create request
    support_request = await ExpertSupportRequest.create(
        id=uuid4(),
        tenant_id=req.tenant_id,
        farmer_id=req.farmer_id,
        farmer_name=req.farmer_name,
        governorate=req.governorate,
        topic=req.topic,
        topic_ar=req.topic_ar,
        description=req.description,
        specialty_needed=req.specialty_needed,
        field_id=req.field_id,
        diagnosis_id=req.diagnosis_id,
        priority=req.priority,
        status="pending",
    )

    return SupportRequestResponse(
        request_id=str(support_request.id),
        farmer_id=support_request.farmer_id,
        farmer_name=support_request.farmer_name,
        topic=support_request.topic,
        topic_ar=support_request.topic_ar,
        specialty_needed=support_request.specialty_needed,
        status=support_request.status,
        status_ar=STATUS_AR.get(support_request.status, support_request.status),
        priority=support_request.priority,
        expert_id=support_request.expert_id,
        expert_name=support_request.expert_name,
        thread_id=str(support_request.thread_id) if support_request.thread_id else None,
        created_at=support_request.created_at.isoformat(),
        accepted_at=None,
        resolved_at=None,
    )


@router.get("/requests", response_model=list[SupportRequestResponse])
async def list_support_requests(
    tenant_id: str = Query(...),
    status: Optional[str] = Query(None, description="Filter by status"),
    specialty: Optional[str] = Query(None),
    farmer_id: Optional[str] = Query(None),
    expert_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    List support requests with filters
    عرض طلبات الدعم
    """
    query = ExpertSupportRequest.filter(tenant_id=tenant_id)

    if status:
        query = query.filter(status=status)
    if specialty:
        query = query.filter(specialty_needed=specialty)
    if farmer_id:
        query = query.filter(farmer_id=farmer_id)
    if expert_id:
        query = query.filter(expert_id=expert_id)

    requests = await query.order_by("-created_at").offset(offset).limit(limit)

    return [
        SupportRequestResponse(
            request_id=str(r.id),
            farmer_id=r.farmer_id,
            farmer_name=r.farmer_name,
            topic=r.topic,
            topic_ar=r.topic_ar,
            specialty_needed=r.specialty_needed,
            status=r.status,
            status_ar=STATUS_AR.get(r.status, r.status),
            priority=r.priority,
            expert_id=r.expert_id,
            expert_name=r.expert_name,
            thread_id=str(r.thread_id) if r.thread_id else None,
            created_at=r.created_at.isoformat(),
            accepted_at=r.accepted_at.isoformat() if r.accepted_at else None,
            resolved_at=r.resolved_at.isoformat() if r.resolved_at else None,
        )
        for r in requests
    ]


@router.get("/requests/pending", response_model=list[SupportRequestResponse])
async def list_pending_requests(
    tenant_id: str = Query(...),
    specialty: Optional[str] = Query(None),
    governorate: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=50),
):
    """
    List pending requests for experts to accept
    عرض الطلبات المعلقة للخبراء
    """
    query = ExpertSupportRequest.filter(tenant_id=tenant_id, status="pending")

    if specialty:
        query = query.filter(specialty_needed=specialty)
    if governorate:
        query = query.filter(governorate=governorate)

    requests = await query.order_by("-priority", "created_at").limit(limit)

    return [
        SupportRequestResponse(
            request_id=str(r.id),
            farmer_id=r.farmer_id,
            farmer_name=r.farmer_name,
            topic=r.topic,
            topic_ar=r.topic_ar,
            specialty_needed=r.specialty_needed,
            status=r.status,
            status_ar=STATUS_AR.get(r.status, r.status),
            priority=r.priority,
            expert_id=None,
            expert_name=None,
            thread_id=None,
            created_at=r.created_at.isoformat(),
            accepted_at=None,
            resolved_at=None,
        )
        for r in requests
    ]


@router.post("/requests/{request_id}/accept", response_model=SupportRequestResponse)
async def accept_support_request(
    request_id: UUID,
    req: AcceptRequestRequest,
):
    """
    Expert accepts a support request
    الخبير يقبل طلب الدعم
    """
    support_request = await ExpertSupportRequest.filter(
        id=request_id, tenant_id=req.tenant_id
    ).first()

    if not support_request:
        raise HTTPException(status_code=404, detail="request_not_found")

    if support_request.status != "pending":
        raise HTTPException(
            status_code=400,
            detail={
                "error": "already_accepted",
                "message_ar": "تم قبول هذا الطلب مسبقاً",
                "current_status": support_request.status,
            },
        )

    # Create chat thread for this support session
    from .models import ChatThread

    thread = await ChatThread.create(
        id=uuid4(),
        tenant_id=req.tenant_id,
        scope_type="support",
        scope_id=str(request_id),
        created_by=req.expert_id,
        title=f"استشارة: {support_request.topic}",
    )

    # Update request
    now = datetime.utcnow()
    support_request.status = "accepted"
    support_request.expert_id = req.expert_id
    support_request.expert_name = req.expert_name
    support_request.accepted_at = now
    support_request.thread_id = thread.id
    await support_request.save()

    # Update expert stats
    await ExpertProfile.filter(user_id=req.expert_id).update(
        total_consultations=ExpertProfile.total_consultations + 1
    )

    return SupportRequestResponse(
        request_id=str(support_request.id),
        farmer_id=support_request.farmer_id,
        farmer_name=support_request.farmer_name,
        topic=support_request.topic,
        topic_ar=support_request.topic_ar,
        specialty_needed=support_request.specialty_needed,
        status=support_request.status,
        status_ar=STATUS_AR.get(support_request.status, support_request.status),
        priority=support_request.priority,
        expert_id=support_request.expert_id,
        expert_name=support_request.expert_name,
        thread_id=str(support_request.thread_id),
        created_at=support_request.created_at.isoformat(),
        accepted_at=support_request.accepted_at.isoformat(),
        resolved_at=None,
    )


@router.post("/requests/{request_id}/resolve")
async def resolve_support_request(
    request_id: UUID,
    req: ResolveRequestRequest,
):
    """
    Expert resolves/closes a support request
    الخبير يحل طلب الدعم
    """
    support_request = await ExpertSupportRequest.filter(
        id=request_id, tenant_id=req.tenant_id, expert_id=req.expert_id
    ).first()

    if not support_request:
        raise HTTPException(status_code=404, detail="request_not_found")

    if support_request.status not in ("accepted", "in_progress"):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "cannot_resolve",
                "message_ar": "لا يمكن حل هذا الطلب في حالته الحالية",
            },
        )

    support_request.status = "resolved"
    support_request.resolved_at = datetime.utcnow()
    support_request.resolution_notes = req.resolution_notes
    support_request.resolution_notes_ar = req.resolution_notes_ar
    await support_request.save()

    return {
        "request_id": str(request_id),
        "status": "resolved",
        "status_ar": "تم الحل",
        "resolved_at": support_request.resolved_at.isoformat(),
    }


@router.post("/requests/{request_id}/rate")
async def rate_support(
    request_id: UUID,
    req: RateSupportRequest,
):
    """
    Farmer rates the expert support
    تقييم المزارع للخبير
    """
    support_request = await ExpertSupportRequest.filter(
        id=request_id, tenant_id=req.tenant_id, farmer_id=req.farmer_id
    ).first()

    if not support_request:
        raise HTTPException(status_code=404, detail="request_not_found")

    if support_request.status != "resolved":
        raise HTTPException(
            status_code=400,
            detail={
                "error": "not_resolved",
                "message_ar": "يجب حل الطلب قبل التقييم",
            },
        )

    if support_request.farmer_rating:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "already_rated",
                "message_ar": "تم تقييم هذا الطلب مسبقاً",
            },
        )

    # Update request with rating
    support_request.farmer_rating = req.rating
    support_request.farmer_feedback = req.feedback
    await support_request.save()

    # Update expert average rating
    if support_request.expert_id:
        expert = await ExpertProfile.filter(user_id=support_request.expert_id).first()
        if expert:
            # Calculate new average
            total_ratings = expert.rating_count * expert.avg_rating + req.rating
            new_count = expert.rating_count + 1
            new_avg = total_ratings / new_count

            expert.avg_rating = round(new_avg, 2)
            expert.rating_count = new_count
            await expert.save()

    return {
        "request_id": str(request_id),
        "rating": req.rating,
        "message_ar": "شكراً لتقييمك!",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Online Experts Tracking
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/online", response_model=OnlineExpertsResponse)
async def get_online_experts(tenant_id: str = Query(...)):
    """
    Get online experts count and availability
    عدد الخبراء المتصلين
    """
    online = await OnlineExpert.filter(tenant_id=tenant_id)
    available = [e for e in online if not e.is_busy]

    # Count by specialty (requires joining with profiles)
    by_specialty: dict[str, int] = {}
    for expert in online:
        profile = await ExpertProfile.filter(user_id=expert.expert_id).first()
        if profile:
            for spec in profile.specialties:
                by_specialty[spec] = by_specialty.get(spec, 0) + 1

    return OnlineExpertsResponse(
        count=len(online),
        available_count=len(available),
        by_specialty=by_specialty,
    )


@router.post("/online/register")
async def register_online(
    tenant_id: str = Query(...),
    expert_id: str = Query(...),
    connection_id: str = Query(...),
):
    """
    Register expert as online (called by WebSocket gateway)
    تسجيل الخبير كمتصل
    """
    # Remove any existing connections for this expert
    await OnlineExpert.filter(expert_id=expert_id).delete()

    # Create new online record
    await OnlineExpert.create(
        id=uuid4(),
        tenant_id=tenant_id,
        expert_id=expert_id,
        connection_id=connection_id,
    )

    # Update profile last online
    await ExpertProfile.filter(user_id=expert_id).update(
        last_online_at=datetime.utcnow(),
        is_available=True,
    )

    return {"status": "online", "expert_id": expert_id}


@router.delete("/online/{connection_id}")
async def unregister_online(connection_id: str):
    """
    Remove expert from online list (called when WebSocket disconnects)
    إزالة الخبير من قائمة المتصلين
    """
    record = await OnlineExpert.filter(connection_id=connection_id).first()
    if record:
        await record.delete()
        return {"status": "offline", "expert_id": record.expert_id}

    return {"status": "not_found"}


# ═══════════════════════════════════════════════════════════════════════════════
# Statistics
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/stats")
async def get_expert_stats(tenant_id: str = Query(...)):
    """
    Get expert system statistics
    إحصائيات نظام الخبراء
    """
    total_experts = await ExpertProfile.filter(tenant_id=tenant_id, is_active=True).count()
    verified_experts = await ExpertProfile.filter(
        tenant_id=tenant_id, is_active=True, is_verified=True
    ).count()
    available_experts = await ExpertProfile.filter(
        tenant_id=tenant_id, is_active=True, is_available=True
    ).count()
    online_experts = await OnlineExpert.filter(tenant_id=tenant_id).count()

    total_requests = await ExpertSupportRequest.filter(tenant_id=tenant_id).count()
    pending_requests = await ExpertSupportRequest.filter(
        tenant_id=tenant_id, status="pending"
    ).count()
    resolved_requests = await ExpertSupportRequest.filter(
        tenant_id=tenant_id, status="resolved"
    ).count()

    return {
        "experts": {
            "total": total_experts,
            "verified": verified_experts,
            "available": available_experts,
            "online": online_experts,
        },
        "requests": {
            "total": total_requests,
            "pending": pending_requests,
            "resolved": resolved_requests,
            "resolution_rate": (
                round(resolved_requests / total_requests * 100, 1)
                if total_requests > 0
                else 0
            ),
        },
        "labels_ar": {
            "experts": "الخبراء",
            "total": "الإجمالي",
            "verified": "الموثقون",
            "available": "المتاحون",
            "online": "المتصلون",
            "requests": "الطلبات",
            "pending": "قيد الانتظار",
            "resolved": "تم حلها",
        },
    }
