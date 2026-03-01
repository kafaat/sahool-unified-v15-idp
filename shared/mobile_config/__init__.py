"""
Mobile Improvement Configuration | تكوين تحسينات تطبيق الهاتف

Tracks 20 mobile improvements organized by category:
- performance (الأداء)
- ux (واجهة المستخدم)
- offline (العمل بدون إنترنت)
- security (الأمان)
- features (ميزات جديدة)

يتتبع 20 تحسيناً لتطبيق الهاتف المحمول مقسمة حسب الفئة.
"""
from __future__ import annotations

import logging
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enumerations | التعدادات
# ---------------------------------------------------------------------------

class ImprovementCategory(str, Enum):
    """Improvement category | فئة التحسين"""
    PERFORMANCE = "performance"
    UX = "ux"
    OFFLINE = "offline"
    SECURITY = "security"
    FEATURES = "features"
    # Legacy aliases (mapped to the 5 primary categories above)
    UI_UX = "ui_ux"
    NEW_FEATURES = "new_features"


class ImprovementStatus(str, Enum):
    """Implementation status | حالة التنفيذ"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Priority(str, Enum):
    """Priority level | مستوى الأولوية"""
    P0 = "P0"  # Highest | أولوية قصوى
    P1 = "P1"  # High | أولوية عالية
    P2 = "P2"  # Medium | أولوية متوسطة


# Arabic translations | الترجمات العربية
CATEGORY_AR: dict[ImprovementCategory, str] = {
    ImprovementCategory.PERFORMANCE: "الأداء",
    ImprovementCategory.UX: "واجهة المستخدم",
    ImprovementCategory.OFFLINE: "العمل بدون إنترنت",
    ImprovementCategory.SECURITY: "الأمان",
    ImprovementCategory.FEATURES: "ميزات جديدة",
    ImprovementCategory.UI_UX: "واجهة المستخدم",
    ImprovementCategory.NEW_FEATURES: "ميزات جديدة",
}

PRIORITY_AR: dict[Priority, str] = {
    Priority.P0: "أولوية قصوى",
    Priority.P1: "أولوية عالية",
    Priority.P2: "أولوية متوسطة",
}

STATUS_AR: dict[ImprovementStatus, str] = {
    ImprovementStatus.PLANNED: "مخطط",
    ImprovementStatus.IN_PROGRESS: "قيد التنفيذ",
    ImprovementStatus.COMPLETED: "مكتمل",
}


# ---------------------------------------------------------------------------
# Data classes | فئات البيانات
# ---------------------------------------------------------------------------

@dataclass
class MobileImprovement:
    """A single mobile improvement item | تحسين واحد للهاتف المحمول"""
    id: str = ""
    title_en: str = ""
    title_ar: str = ""
    category: ImprovementCategory = ImprovementCategory.UX
    category_ar: str = ""
    status: ImprovementStatus = ImprovementStatus.PLANNED
    status_ar: str = ""
    priority: Priority = Priority.P1
    priority_ar: str = ""
    description: str = ""
    description_ar: str = ""
    effort_weeks: float = 1.0
    reference_platform: str = ""

    # Legacy compat aliases
    @property
    def improvement_id(self) -> str:
        return self.id

    @property
    def title(self) -> str:
        return self.title_en


# ---------------------------------------------------------------------------
# Improvement definitions (20 items) | تعريفات التحسينات (20 عنصراً)
# ---------------------------------------------------------------------------

MOBILE_IMPROVEMENTS: list[dict] = [
    # === performance (4) | الأداء ===
    {
        "id": "MOB-01", "title": "Delta Sync", "title_ar": "مزامنة Delta ذكية",
        "description": "Sync only changes instead of full data",
        "description_ar": "مزامنة التغييرات فقط بدل البيانات الكاملة",
        "category": ImprovementCategory.PERFORMANCE, "priority": Priority.P0,
        "effort_weeks": 2, "reference": "AgriWebb", "status": ImprovementStatus.PLANNED,
    },
    {
        "id": "MOB-02", "title": "Auto Image Compression", "title_ar": "ضغط الصور التلقائي",
        "description": "Compress field images before upload (80% size reduction)",
        "description_ar": "ضغط صور الحقل قبل الرفع (80% تقليل حجم)",
        "category": ImprovementCategory.PERFORMANCE, "priority": Priority.P0,
        "effort_weeks": 0.5, "reference": "Standard", "status": ImprovementStatus.PLANNED,
    },
    {
        "id": "MOB-03", "title": "Lazy Loading", "title_ar": "تحميل كسول",
        "description": "Load pages on demand to speed up app start",
        "description_ar": "تحميل الصفحات عند الحاجة فقط لتسريع بدء التطبيق",
        "category": ImprovementCategory.PERFORMANCE, "priority": Priority.P1,
        "effort_weeks": 1, "reference": "Flutter best practices", "status": ImprovementStatus.PLANNED,
    },
    {
        "id": "MOB-04", "title": "Battery Optimization", "title_ar": "تقليل استهلاك البطارية",
        "description": "Optimize GPS polling + reduce background tasks",
        "description_ar": "تحسين GPS polling + تقليل المهام الخلفية",
        "category": ImprovementCategory.PERFORMANCE, "priority": Priority.P1,
        "effort_weeks": 1, "reference": "Android/iOS guidelines", "status": ImprovementStatus.PLANNED,
    },
    # === ux (4) | واجهة المستخدم ===
    {
        "id": "MOB-05", "title": "Simplified Home Screen", "title_ar": "واجهة مبسطة للصفحة الرئيسية",
        "description": "Large cards with clear icons instead of complex menus",
        "description_ar": "بطاقات كبيرة بأيقونات واضحة بدلاً من القوائم المعقدة",
        "category": ImprovementCategory.UX, "priority": Priority.P0,
        "effort_weeks": 2, "reference": "Plantix", "status": ImprovementStatus.PLANNED,
    },
    {
        "id": "MOB-06", "title": "Sunlight Mode", "title_ar": "وضع الشمس",
        "description": "High contrast colors for outdoor field use",
        "description_ar": "ألوان عالية التباين للاستخدام في الحقل تحت الشمس",
        "category": ImprovementCategory.UX, "priority": Priority.P0,
        "effort_weeks": 1, "reference": "AgTech best practices", "status": ImprovementStatus.PLANNED,
    },
    {
        "id": "MOB-07", "title": "Agricultural Icons", "title_ar": "أيقونات زراعية محلية",
        "description": "Custom icons: wheat, palm, plow instead of generic ones",
        "description_ar": "أيقونات مخصصة: سنبلة قمح، نخلة، محراث",
        "category": ImprovementCategory.UX, "priority": Priority.P1,
        "effort_weeks": 1, "reference": "Custom", "status": ImprovementStatus.PLANNED,
    },
    {
        "id": "MOB-08", "title": "Interactive Onboarding", "title_ar": "تعليمات أولى تفاعلية",
        "description": "Arabic animated onboarding for new farmers",
        "description_ar": "تعليمات أولى بالعربية مع رسوم متحركة للمزارع الجديد",
        "category": ImprovementCategory.UX, "priority": Priority.P1,
        "effort_weeks": 1, "reference": "Plantix", "status": ImprovementStatus.PLANNED,
    },
    # === offline (4) | العمل بدون إنترنت ===
    {
        "id": "MOB-09", "title": "Offline Map Tiles", "title_ar": "تخزين مؤقت للخرائط",
        "description": "Cache map tiles for offline use",
        "description_ar": "حفظ tiles الخرائط للعمل بدون إنترنت",
        "category": ImprovementCategory.OFFLINE, "priority": Priority.P0,
        "effort_weeks": 1, "reference": "AgriWebb", "status": ImprovementStatus.PLANNED,
    },
    {
        "id": "MOB-10", "title": "Offline Advisory Cache", "title_ar": "تخزين مؤقت للنصائح",
        "description": "Pre-cache advisory content for offline access",
        "description_ar": "تحميل مسبق للنصائح الزراعية للعمل بدون إنترنت",
        "category": ImprovementCategory.OFFLINE, "priority": Priority.P0,
        "effort_weeks": 1.5, "reference": "Custom", "status": ImprovementStatus.PLANNED,
    },
    {
        "id": "MOB-11", "title": "Optimized Local DB", "title_ar": "قاعدة بيانات محلية محسّنة",
        "description": "Optimize Drift queries + SQLite indexes",
        "description_ar": "تحسين استعلامات Drift + فهارس SQLite",
        "category": ImprovementCategory.OFFLINE, "priority": Priority.P1,
        "effort_weeks": 1, "reference": "SQLite optimization", "status": ImprovementStatus.PLANNED,
    },
    {
        "id": "MOB-12", "title": "Conflict Resolution UI", "title_ar": "واجهة حل التعارضات",
        "description": "User-friendly UI for resolving offline sync conflicts",
        "description_ar": "واجهة سهلة لحل تعارضات المزامنة",
        "category": ImprovementCategory.OFFLINE, "priority": Priority.P1,
        "effort_weeks": 1.5, "reference": "Custom", "status": ImprovementStatus.PLANNED,
    },
    # === security (4) | الأمان ===
    {
        "id": "MOB-13", "title": "Biometric Login", "title_ar": "دخول بالبصمة",
        "description": "Fingerprint and face authentication for quick access",
        "description_ar": "مصادقة بالبصمة والوجه للوصول السريع",
        "category": ImprovementCategory.SECURITY, "priority": Priority.P0,
        "effort_weeks": 1, "reference": "local_auth", "status": ImprovementStatus.COMPLETED,
    },
    {
        "id": "MOB-14", "title": "Certificate Pinning", "title_ar": "تثبيت الشهادات",
        "description": "Pin TLS certificates to prevent MITM attacks",
        "description_ar": "تثبيت شهادات TLS لمنع هجمات الوسيط",
        "category": ImprovementCategory.SECURITY, "priority": Priority.P0,
        "effort_weeks": 0.5, "reference": "OWASP", "status": ImprovementStatus.COMPLETED,
    },
    {
        "id": "MOB-15", "title": "Encrypted Local Storage", "title_ar": "تخزين محلي مشفر",
        "description": "SQLCipher 256-bit AES for local database encryption",
        "description_ar": "تشفير قاعدة البيانات المحلية بـ SQLCipher AES 256",
        "category": ImprovementCategory.SECURITY, "priority": Priority.P0,
        "effort_weeks": 1, "reference": "SQLCipher", "status": ImprovementStatus.COMPLETED,
    },
    {
        "id": "MOB-16", "title": "Root Detection", "title_ar": "كشف الروت",
        "description": "Detect rooted/jailbroken devices and warn user",
        "description_ar": "كشف الأجهزة المعدلة (روت/جيلبريك) وتحذير المستخدم",
        "category": ImprovementCategory.SECURITY, "priority": Priority.P1,
        "effort_weeks": 0.5, "reference": "safe_device", "status": ImprovementStatus.COMPLETED,
    },
    # === features (4) | ميزات جديدة ===
    {
        "id": "MOB-17", "title": "AI Camera Scan", "title_ar": "كاميرا ذكية (AI Scan)",
        "description": "Point camera at plant to detect diseases instantly",
        "description_ar": "تصوير النبات لكشف المرض فوراً",
        "category": ImprovementCategory.FEATURES, "priority": Priority.P0,
        "effort_weeks": 3, "reference": "Plantix, YOLO26", "status": ImprovementStatus.IN_PROGRESS,
    },
    {
        "id": "MOB-18", "title": "Voice Field Notes", "title_ar": "مذكرة حقلية صوتية",
        "description": "Record voice notes saved with GPS coordinates",
        "description_ar": "تسجيل ملاحظات صوتية تُحفظ مع إحداثيات GPS",
        "category": ImprovementCategory.FEATURES, "priority": Priority.P1,
        "effort_weeks": 1, "reference": "Custom", "status": ImprovementStatus.PLANNED,
    },
    {
        "id": "MOB-19", "title": "Smart Weather Alerts", "title_ar": "تنبيهات طقس ذكية",
        "description": "Proactive alerts: 'Rain in 6h - don't fertilize today'",
        "description_ar": "إشعارات استباقية: 'مطر خلال 6 ساعات - لا تسمّد اليوم'",
        "category": ImprovementCategory.FEATURES, "priority": Priority.P0,
        "effort_weeks": 1, "reference": "Custom", "status": ImprovementStatus.PLANNED,
    },
    {
        "id": "MOB-20", "title": "Harvest Photo Report", "title_ar": "تقرير حصاد مصوّر",
        "description": "End-of-season report with photos, stats and recommendations",
        "description_ar": "تقرير نهاية الموسم بالصور والإحصائيات والتوصيات",
        "category": ImprovementCategory.FEATURES, "priority": Priority.P2,
        "effort_weeks": 2, "reference": "Custom", "status": ImprovementStatus.PLANNED,
    },
]


# ---------------------------------------------------------------------------
# Tracker class | فئة التتبع
# ---------------------------------------------------------------------------

class MobileImprovementTracker:
    """Tracks mobile improvement implementation progress.

    يتتبع تقدم تنفيذ تحسينات الهاتف المحمول.
    """

    def __init__(self) -> None:
        self._improvements: list[MobileImprovement] = []
        for imp in MOBILE_IMPROVEMENTS:
            cat = imp["category"]
            status = imp.get("status", ImprovementStatus.PLANNED)
            priority = imp["priority"]
            self._improvements.append(
                MobileImprovement(
                    id=imp["id"],
                    title_en=imp["title"],
                    title_ar=imp["title_ar"],
                    description=imp.get("description", ""),
                    description_ar=imp.get("description_ar", ""),
                    category=cat,
                    category_ar=CATEGORY_AR.get(cat, ""),
                    status=status,
                    status_ar=STATUS_AR.get(status, ""),
                    priority=priority,
                    priority_ar=PRIORITY_AR.get(priority, ""),
                    effort_weeks=imp.get("effort_weeks", 1.0),
                    reference_platform=imp.get("reference", ""),
                )
            )

    # ----- New API (required by specification) -------------------------

    def get_improvements(
        self,
        status: ImprovementStatus | None = None,
    ) -> list[MobileImprovement]:
        """Get all improvements, optionally filtered by status.

        الحصول على جميع التحسينات، مع تصفية اختيارية حسب الحالة.
        """
        result = list(self._improvements)
        if status is not None:
            result = [i for i in result if i.status == status]
        return result

    def get_by_category(
        self,
        category: ImprovementCategory,
    ) -> list[MobileImprovement]:
        """Get improvements filtered by category.

        الحصول على التحسينات حسب الفئة.
        """
        return [i for i in self._improvements if i.category == category]

    def get_completion_stats(self) -> dict:
        """Get completion statistics across all improvements.

        الحصول على إحصائيات الإنجاز لجميع التحسينات.

        Returns:
            Dict with total, planned, in_progress, completed counts and percentages.
        """
        total = len(self._improvements)
        planned = sum(1 for i in self._improvements if i.status == ImprovementStatus.PLANNED)
        in_progress = sum(1 for i in self._improvements if i.status == ImprovementStatus.IN_PROGRESS)
        completed = sum(1 for i in self._improvements if i.status == ImprovementStatus.COMPLETED)
        pct = (completed / total * 100) if total > 0 else 0.0

        by_category: dict[str, dict] = {}
        for cat in (
            ImprovementCategory.PERFORMANCE,
            ImprovementCategory.UX,
            ImprovementCategory.OFFLINE,
            ImprovementCategory.SECURITY,
            ImprovementCategory.FEATURES,
        ):
            items = self.get_by_category(cat)
            cat_completed = sum(1 for i in items if i.status == ImprovementStatus.COMPLETED)
            by_category[cat.value] = {
                "total": len(items),
                "completed": cat_completed,
                "total_weeks": sum(i.effort_weeks for i in items),
            }

        return {
            "total": total,
            "planned": planned,
            "in_progress": in_progress,
            "completed": completed,
            "completion_percent": round(pct, 1),
            "by_category": by_category,
            "message": f"{completed}/{total} improvements completed ({pct:.0f}%)",
            "message_ar": f"{completed}/{total} تحسين مكتمل ({pct:.0f}%)",
        }

    # ----- Legacy API (backward compatibility) -------------------------

    def list_improvements(
        self,
        category: ImprovementCategory | None = None,
        priority: Priority | None = None,
    ) -> list[MobileImprovement]:
        """Legacy: list improvements with optional filters."""
        result = list(self._improvements)
        if category is not None:
            result = [i for i in result if i.category == category]
        if priority is not None:
            result = [i for i in result if i.priority == priority]
        return result

    def get_summary(self) -> dict:
        """Legacy: get improvement summary."""
        by_cat: dict[str, dict] = {}
        for cat in (
            ImprovementCategory.PERFORMANCE,
            ImprovementCategory.UX,
            ImprovementCategory.OFFLINE,
            ImprovementCategory.SECURITY,
            ImprovementCategory.FEATURES,
        ):
            items = self.get_by_category(cat)
            by_cat[CATEGORY_AR[cat]] = {
                "count": len(items),
                "total_weeks": sum(i.effort_weeks for i in items),
            }

        p0 = [i for i in self._improvements if i.priority == Priority.P0]

        return {
            "total_improvements": len(self._improvements),
            "by_category": by_cat,
            "p0_count": len(p0),
            "total_effort_weeks": sum(i.effort_weeks for i in self._improvements),
            "message": f"20 mobile improvements: {len(p0)} P0 priority",
            "message_ar": f"20 تحسين للهاتف: {len(p0)} أولوية قصوى",
        }
