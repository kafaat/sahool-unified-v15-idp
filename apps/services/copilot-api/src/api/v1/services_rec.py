"""
Services Recommender — محرك توصية الخدمات
Recommends relevant platform services based on farmer query context.
Phase 4 of Component Unification Plan (PR #1344)
"""

import structlog
from fastapi import APIRouter, Body, Depends
from pydantic import BaseModel, Field

from ..deps import get_current_user

logger = structlog.get_logger()
router = APIRouter(prefix="/services", tags=["services"])


class ServiceRecommendRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    field_id: str | None = None
    location: dict | None = None
    crop_type: str | None = None
    language: str = "ar"


class ServiceRecommendation(BaseModel):
    category: str
    category_ar: str
    services: list[dict]
    relevance: float  # 0.0 - 1.0


# Service catalog with relevance keywords
SERVICE_CATALOG = {
    "equipment": {
        "category_ar": "المعدات والطائرات",
        "keywords_ar": ["مضخة", "طائرة", "رش", "معدة", "جرار", "حصاد"],
        "keywords_en": ["pump", "drone", "sprayer", "equipment", "tractor", "harvester"],
        "services": [
            {
                "name": "drone-service",
                "name_ar": "خدمة الطائرات المسيّرة",
                "port": 8126,
                "description_ar": "تخطيط رحلات الطائرات + رش متغير المعدل",
            },
            {
                "name": "equipment-service",
                "name_ar": "خدمة إدارة المعدات",
                "port": 8101,
                "description_ar": "تتبع المعدات + صيانة وقائية",
            },
        ],
    },
    "financing": {
        "category_ar": "التمويل والتأمين",
        "keywords_ar": ["تمويل", "قرض", "تأمين", "دعم", "إعانة"],
        "keywords_en": ["finance", "loan", "insurance", "subsidy", "grant"],
        "services": [
            {
                "name": "billing-core",
                "name_ar": "خدمة الفوترة",
                "port": 8089,
                "description_ar": "إدارة الاشتراكات والمدفوعات",
            },
            {
                "name": "crop-insurance",
                "name_ar": "تأمين المحاصيل",
                "port": None,
                "description_ar": "تقييم المخاطر + حسابات التعويض",
            },
        ],
    },
    "training": {
        "category_ar": "التدريب والتعلم",
        "keywords_ar": ["تعلم", "تدريب", "دورة", "شرح", "كيف"],
        "keywords_en": ["learn", "train", "course", "how to", "tutorial"],
        "services": [
            {
                "name": "skills-service",
                "name_ar": "خدمة المهارات",
                "port": 8121,
                "description_ar": "تقييم المهارات الزراعية + مسارات التعلم",
            },
            {
                "name": "learning-marketplace",
                "name_ar": "سوق التعلم",
                "port": None,
                "description_ar": "دورات تدريبية + تتبع التقدم",
            },
        ],
    },
    "market": {
        "category_ar": "السوق والتجارة",
        "keywords_ar": ["سعر", "بيع", "شراء", "سوق", "تجار"],
        "keywords_en": ["price", "sell", "buy", "market", "trade"],
        "services": [
            {
                "name": "marketplace-service",
                "name_ar": "خدمة السوق",
                "port": 3010,
                "description_ar": "أسعار المحاصيل + البيع والشراء",
            },
            {
                "name": "logistics-service",
                "name_ar": "خدمة اللوجستيات",
                "port": 8167,
                "description_ar": "النقل والتوصيل",
            },
        ],
    },
    "cooperative": {
        "category_ar": "التعاونيات والمجتمع",
        "keywords_ar": ["تعاون", "جمعية", "مشترك", "مزارعين", "مجموعة"],
        "keywords_en": ["cooperative", "association", "community", "group", "farmers"],
        "services": [
            {
                "name": "cooperative-service",
                "name_ar": "خدمة التعاونيات",
                "port": 8127,
                "description_ar": "إدارة التعاونيات الزراعية",
            },
            {
                "name": "chat-service",
                "name_ar": "خدمة المحادثة",
                "port": 8115,
                "description_ar": "التواصل بين المزارعين",
            },
        ],
    },
}


def _calculate_relevance(query: str, keywords_ar: list, keywords_en: list) -> float:
    query_lower = query.lower()
    matches = sum(1 for k in keywords_ar if k in query_lower) + sum(1 for k in keywords_en if k in query_lower)
    total = len(keywords_ar) + len(keywords_en)
    return min(matches / max(total * 0.3, 1), 1.0)


@router.post("/recommend")
async def recommend_services(req: ServiceRecommendRequest = Body(...), user: dict = Depends(get_current_user)):
    tenant_id = user.get("tenant_id", "")
    logger.info("service_recommendation_request", tenant_id=tenant_id, query=req.query[:100])
    recommendations = []
    for cat_key, cat_data in SERVICE_CATALOG.items():
        relevance = _calculate_relevance(req.query, cat_data["keywords_ar"], cat_data["keywords_en"])
        if relevance > 0:
            recommendations.append(
                ServiceRecommendation(
                    category=cat_key,
                    category_ar=cat_data["category_ar"],
                    services=cat_data["services"],
                    relevance=relevance,
                )
            )
    recommendations.sort(key=lambda r: r.relevance, reverse=True)
    return {
        "query": req.query,
        "recommendations": [r.model_dump() for r in recommendations[:5]],
        "count": len(recommendations),
    }
