"""
SAHOOL AI Monitoring API Routes
نقاط API للمراقبة
"""

from __future__ import annotations

from fastapi import APIRouter

from .metrics import metrics

router = APIRouter(prefix="/ai/metrics", tags=["ai-metrics"])


@router.get("")
def get_metrics():
    """الحصول على مقاييس نظام الذكاء الاصطناعي."""
    return metrics.get_stats()


@router.get("/health")
def health():
    """فحص الصحة مع المقاييس الأساسية."""
    stats = metrics.get_stats()

    return {
        "status": "ok",
        "total_queries": stats["counters"].get("rag_queries_total", 0),
        "total_errors": stats["counters"].get("rag_errors_total", 0),
    }


@router.post("/reset")
def reset_metrics():
    """إعادة تعيين جميع المقاييس (للاختبار فقط)."""
    metrics.reset()
    return {"status": "ok", "message": "Metrics reset successfully"}
