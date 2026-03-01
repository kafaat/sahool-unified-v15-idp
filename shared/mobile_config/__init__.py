"""
Mobile Improvement Configuration | تكوين تحسينات تطبيق الهاتف

Defines 20 mobile improvements organized by category:
- UI/UX (8 improvements)
- Performance (6 improvements)
- New Features (6 improvements)
"""
from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, field


class ImprovementCategory(str, Enum):
    UI_UX = "ui_ux"
    PERFORMANCE = "performance"
    NEW_FEATURES = "new_features"


class Priority(str, Enum):
    P0 = "P0"  # Highest
    P1 = "P1"
    P2 = "P2"


CATEGORY_AR = {
    ImprovementCategory.UI_UX: "واجهة المستخدم",
    ImprovementCategory.PERFORMANCE: "الأداء",
    ImprovementCategory.NEW_FEATURES: "ميزات جديدة",
}

PRIORITY_AR = {
    Priority.P0: "أولوية قصوى",
    Priority.P1: "أولوية عالية",
    Priority.P2: "أولوية متوسطة",
}


@dataclass
class MobileImprovement:
    """A single mobile improvement | تحسين واحد للهاتف"""
    improvement_id: str = ""
    title: str = ""
    title_ar: str = ""
    description: str = ""
    description_ar: str = ""
    category: ImprovementCategory = ImprovementCategory.UI_UX
    category_ar: str = ""
    priority: Priority = Priority.P1
    priority_ar: str = ""
    effort_weeks: float = 1.0
    status: str = "planned"
    reference_platform: str = ""
    implementation_notes: str = ""


# 20 Mobile improvements
MOBILE_IMPROVEMENTS: list[dict] = [
    # === UI/UX (8) ===
    {
        "id": "MOB-01", "title": "Simplified Home Screen", "title_ar": "واجهة مبسطة للصفحة الرئيسية",
        "description": "Large cards with clear icons instead of complex menus",
        "description_ar": "بطاقات كبيرة بأيقونات واضحة بدلاً من القوائم المعقدة",
        "category": ImprovementCategory.UI_UX, "priority": Priority.P0,
        "effort_weeks": 2, "reference": "Plantix",
    },
    {
        "id": "MOB-02", "title": "Sunlight Mode", "title_ar": "وضع الشمس",
        "description": "High contrast colors for outdoor field use",
        "description_ar": "ألوان عالية التباين للاستخدام في الحقل تحت الشمس",
        "category": ImprovementCategory.UI_UX, "priority": Priority.P0,
        "effort_weeks": 1, "reference": "AgTech best practices",
    },
    {
        "id": "MOB-03", "title": "Agricultural Icons", "title_ar": "أيقونات زراعية محلية",
        "description": "Custom icons: wheat, palm, plow instead of generic ones",
        "description_ar": "أيقونات مخصصة: سنبلة قمح، نخلة، محراث",
        "category": ImprovementCategory.UI_UX, "priority": Priority.P1,
        "effort_weeks": 1, "reference": "Custom",
    },
    {
        "id": "MOB-04", "title": "Gesture Navigation", "title_ar": "تنقل بإيماءات",
        "description": "Swipe left/right between fields, pull to refresh",
        "description_ar": "سحب يمين/يسار بين الحقول، سحب لأسفل للتحديث",
        "category": ImprovementCategory.UI_UX, "priority": Priority.P1,
        "effort_weeks": 1, "reference": "Standard UX",
    },
    {
        "id": "MOB-05", "title": "Map-First Home", "title_ar": "خريطة الحقول كصفحة رئيسية",
        "description": "Interactive map showing all fields with NDVI colors",
        "description_ar": "خريطة تفاعلية تعرض جميع الحقول مع ألوان NDVI",
        "category": ImprovementCategory.UI_UX, "priority": Priority.P0,
        "effort_weeks": 3, "reference": "OneSoil",
    },
    {
        "id": "MOB-06", "title": "Agricultural Dark Mode", "title_ar": "وضع ليلي زراعي",
        "description": "Night theme with green/earthy tones",
        "description_ar": "ثيم ليلي بألوان خضراء/ترابية مريحة",
        "category": ImprovementCategory.UI_UX, "priority": Priority.P2,
        "effort_weeks": 0.5, "reference": "Material Design",
    },
    {
        "id": "MOB-07", "title": "Interactive Onboarding", "title_ar": "تعليمات أولى تفاعلية",
        "description": "Arabic animated onboarding for new farmers",
        "description_ar": "تعليمات أولى بالعربية مع رسوم متحركة للمزارع الجديد",
        "category": ImprovementCategory.UI_UX, "priority": Priority.P1,
        "effort_weeks": 1, "reference": "Plantix",
    },
    {
        "id": "MOB-08", "title": "Home Screen Widget", "title_ar": "ويدجت الشاشة الرئيسية",
        "description": "Widget showing weather + next task on phone home screen",
        "description_ar": "ويدجت تعرض الطقس + المهمة القادمة",
        "category": ImprovementCategory.UI_UX, "priority": Priority.P2,
        "effort_weeks": 1, "reference": "Android/iOS native",
    },
    # === PERFORMANCE (6) ===
    {
        "id": "MOB-09", "title": "Delta Sync", "title_ar": "مزامنة Delta ذكية",
        "description": "Sync only changes instead of full data",
        "description_ar": "مزامنة التغييرات فقط بدل البيانات الكاملة",
        "category": ImprovementCategory.PERFORMANCE, "priority": Priority.P0,
        "effort_weeks": 2, "reference": "AgriWebb",
    },
    {
        "id": "MOB-10", "title": "Auto Image Compression", "title_ar": "ضغط الصور التلقائي",
        "description": "Compress field images before upload (80% size reduction)",
        "description_ar": "ضغط صور الحقل قبل الرفع (80% تقليل حجم)",
        "category": ImprovementCategory.PERFORMANCE, "priority": Priority.P0,
        "effort_weeks": 0.5, "reference": "Standard",
    },
    {
        "id": "MOB-11", "title": "Lazy Loading", "title_ar": "تحميل كسول",
        "description": "Load pages on demand to speed up app start",
        "description_ar": "تحميل الصفحات عند الحاجة فقط لتسريع بدء التطبيق",
        "category": ImprovementCategory.PERFORMANCE, "priority": Priority.P1,
        "effort_weeks": 1, "reference": "Flutter best practices",
    },
    {
        "id": "MOB-12", "title": "Optimized Local DB", "title_ar": "قاعدة بيانات محلية محسّنة",
        "description": "Optimize Drift queries + SQLite indexes",
        "description_ar": "تحسين استعلامات Drift + فهارس SQLite",
        "category": ImprovementCategory.PERFORMANCE, "priority": Priority.P1,
        "effort_weeks": 1, "reference": "SQLite optimization",
    },
    {
        "id": "MOB-13", "title": "Offline Map Tiles", "title_ar": "تخزين مؤقت للخرائط",
        "description": "Cache map tiles for offline use",
        "description_ar": "حفظ tiles الخرائط للعمل بدون إنترنت",
        "category": ImprovementCategory.PERFORMANCE, "priority": Priority.P0,
        "effort_weeks": 1, "reference": "AgriWebb",
    },
    {
        "id": "MOB-14", "title": "Battery Optimization", "title_ar": "تقليل استهلاك البطارية",
        "description": "Optimize GPS polling + reduce background tasks",
        "description_ar": "تحسين GPS polling + تقليل المهام الخلفية",
        "category": ImprovementCategory.PERFORMANCE, "priority": Priority.P1,
        "effort_weeks": 1, "reference": "Android/iOS guidelines",
    },
    # === NEW FEATURES (6) ===
    {
        "id": "MOB-15", "title": "AI Camera Scan", "title_ar": "كاميرا ذكية (AI Scan)",
        "description": "Point camera at plant to detect diseases instantly",
        "description_ar": "تصوير النبات \u2192 كشف المرض فور\u0627\u064b",
        "category": ImprovementCategory.NEW_FEATURES, "priority": Priority.P0,
        "effort_weeks": 3, "reference": "Plantix, YOLO26",
    },
    {
        "id": "MOB-16", "title": "Voice Field Notes", "title_ar": "مذكرة حقلية صوتية",
        "description": "Record voice notes saved with GPS coordinates",
        "description_ar": "تسجيل ملاحظات صوتية تُحفظ مع إحداثيات GPS",
        "category": ImprovementCategory.NEW_FEATURES, "priority": Priority.P1,
        "effort_weeks": 1, "reference": "Custom",
    },
    {
        "id": "MOB-17", "title": "Field Sharing", "title_ar": "مشاركة الحقل مع فريق",
        "description": "Invite workers/engineers to access specific field data",
        "description_ar": "دعوة عمال/مهندسين للوصول لبيانات حقل محدد",
        "category": ImprovementCategory.NEW_FEATURES, "priority": Priority.P1,
        "effort_weeks": 2, "reference": "Agworld",
    },
    {
        "id": "MOB-18", "title": "Production Cost Calculator", "title_ar": "حاسبة تكلفة الإنتاج",
        "description": "Quick calculator: area + crop + inputs = expected cost",
        "description_ar": "حاسبة سريعة: مساحة + محصول + مدخلات = تكلفة متوقعة",
        "category": ImprovementCategory.NEW_FEATURES, "priority": Priority.P1,
        "effort_weeks": 1, "reference": "FarmLogs",
    },
    {
        "id": "MOB-19", "title": "Smart Weather Alerts", "title_ar": "تنبيهات طقس ذكية",
        "description": "Proactive alerts: 'Rain in 6h - don't fertilize today'",
        "description_ar": "إشعارات استباقية: 'مطر خلال 6 ساعات - لا تسمّد اليوم'",
        "category": ImprovementCategory.NEW_FEATURES, "priority": Priority.P0,
        "effort_weeks": 1, "reference": "Custom",
    },
    {
        "id": "MOB-20", "title": "Harvest Photo Report", "title_ar": "تقرير حصاد مصوّر",
        "description": "End-of-season report with photos, stats and recommendations",
        "description_ar": "تقرير نهاية الموسم بالصور والإحصائيات والتوصيات",
        "category": ImprovementCategory.NEW_FEATURES, "priority": Priority.P2,
        "effort_weeks": 2, "reference": "Custom",
    },
]


class MobileImprovementTracker:
    """Tracks mobile improvement implementation progress.

    يتتبع تقدم تنفيذ تحسينات الهاتف.
    """

    def __init__(self):
        self._improvements = [
            MobileImprovement(
                improvement_id=imp["id"],
                title=imp["title"],
                title_ar=imp["title_ar"],
                description=imp.get("description", ""),
                description_ar=imp.get("description_ar", ""),
                category=imp["category"],
                category_ar=CATEGORY_AR.get(imp["category"], ""),
                priority=imp["priority"],
                priority_ar=PRIORITY_AR.get(imp["priority"], ""),
                effort_weeks=imp.get("effort_weeks", 1),
                reference_platform=imp.get("reference", ""),
            )
            for imp in MOBILE_IMPROVEMENTS
        ]

    def list_improvements(self, category: ImprovementCategory | None = None, priority: Priority | None = None) -> list[MobileImprovement]:
        """List improvements, optionally filtered."""
        result = self._improvements
        if category:
            result = [i for i in result if i.category == category]
        if priority:
            result = [i for i in result if i.priority == priority]
        return result

    def get_summary(self) -> dict:
        """Get improvement summary."""
        by_cat = {}
        for cat in ImprovementCategory:
            items = [i for i in self._improvements if i.category == cat]
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
