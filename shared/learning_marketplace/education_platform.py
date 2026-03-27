"""
Farmer Education Platform | منصة تعليم المزارعين

Provides personalized learning paths, digital certificates,
community features, and gamification for farmer education.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

logger = logging.getLogger(__name__)


class ContentType(StrEnum):
    VIDEO = "video"
    ARTICLE = "article"
    AUDIO = "audio"
    QUIZ = "quiz"
    PRACTICAL = "practical"
    INFOGRAPHIC = "infographic"


class DifficultyLevel(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class CertificateType(StrEnum):
    COMPLETION = "completion"
    COMPETENCY = "competency"
    PROFESSIONAL = "professional"


CONTENT_TYPE_AR = {
    ContentType.VIDEO: "فيديو",
    ContentType.ARTICLE: "مقالة",
    ContentType.AUDIO: "صوتي",
    ContentType.QUIZ: "اختبار",
    ContentType.PRACTICAL: "تطبيق عملي",
    ContentType.INFOGRAPHIC: "إنفوجرافيك",
}

DIFFICULTY_AR = {
    DifficultyLevel.BEGINNER: "مبتدئ",
    DifficultyLevel.INTERMEDIATE: "متوسط",
    DifficultyLevel.ADVANCED: "متقدم",
    DifficultyLevel.EXPERT: "خبير",
}


@dataclass
class LearningModule:
    """A learning module | وحدة تعليمية"""

    module_id: str = ""
    title: str = ""
    title_ar: str = ""
    description: str = ""
    description_ar: str = ""
    content_type: ContentType = ContentType.ARTICLE
    content_type_ar: str = ""
    difficulty: DifficultyLevel = DifficultyLevel.BEGINNER
    difficulty_ar: str = ""
    duration_minutes: int = 0
    crop_type: str = ""
    crop_type_ar: str = ""
    region: str = ""
    tags: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    points: int = 10


@dataclass
class LearningPath:
    """A structured learning path | مسار تعليمي"""

    path_id: str = ""
    title: str = ""
    title_ar: str = ""
    description: str = ""
    description_ar: str = ""
    modules: list[LearningModule] = field(default_factory=list)
    total_duration_hours: float = 0.0
    total_points: int = 0
    certificate_type: CertificateType = CertificateType.COMPLETION
    crop_type: str = ""
    region: str = ""


@dataclass
class FarmerProgress:
    """Farmer's learning progress | تقدم المزارع التعليمي"""

    farmer_id: str = ""
    tenant_id: str = ""
    total_points: int = 0
    level: int = 1
    level_title: str = "Seedling"
    level_title_ar: str = "بذرة"
    completed_modules: int = 0
    total_modules: int = 0
    certificates_earned: int = 0
    badges: list[str] = field(default_factory=list)
    current_streak_days: int = 0
    rank_in_community: int = 0


@dataclass
class DigitalCertificate:
    """Digital certificate | شهادة رقمية"""

    certificate_id: str = ""
    farmer_id: str = ""
    path_id: str = ""
    title: str = ""
    title_ar: str = ""
    certificate_type: CertificateType = CertificateType.COMPLETION
    issued_date: str = ""
    score_percent: float = 0.0
    skills: list[str] = field(default_factory=list)
    verification_code: str = ""


# Predefined learning paths
LEARNING_PATHS = [
    {
        "path_id": "LP-WHEAT-BASIC",
        "title": "Wheat Farming Basics",
        "title_ar": "أساسيات زراعة القمح",
        "crop_type": "wheat",
        "modules": [
            {
                "id": "M01",
                "title": "Wheat Varieties",
                "title_ar": "أصناف القمح",
                "type": ContentType.VIDEO,
                "duration": 15,
                "points": 10,
            },
            {
                "id": "M02",
                "title": "Soil Preparation",
                "title_ar": "تجهيز التربة",
                "type": ContentType.VIDEO,
                "duration": 20,
                "points": 15,
            },
            {
                "id": "M03",
                "title": "Planting Guide",
                "title_ar": "دليل الزراعة",
                "type": ContentType.ARTICLE,
                "duration": 10,
                "points": 10,
            },
            {
                "id": "M04",
                "title": "Irrigation Scheduling",
                "title_ar": "جدولة الري",
                "type": ContentType.PRACTICAL,
                "duration": 30,
                "points": 25,
            },
            {
                "id": "M05",
                "title": "Fertilizer Application",
                "title_ar": "تطبيق الأسمدة",
                "type": ContentType.VIDEO,
                "duration": 20,
                "points": 15,
            },
            {
                "id": "M06",
                "title": "Disease Recognition",
                "title_ar": "التعرف على الأمراض",
                "type": ContentType.QUIZ,
                "duration": 15,
                "points": 20,
            },
            {
                "id": "M07",
                "title": "Harvest Timing",
                "title_ar": "توقيت الحصاد",
                "type": ContentType.ARTICLE,
                "duration": 10,
                "points": 10,
            },
        ],
    },
    {
        "path_id": "LP-DATE-PALM",
        "title": "Date Palm Management",
        "title_ar": "إدارة النخيل",
        "crop_type": "date_palm",
        "modules": [
            {
                "id": "D01",
                "title": "Palm Varieties",
                "title_ar": "أصناف النخيل",
                "type": ContentType.VIDEO,
                "duration": 20,
                "points": 10,
            },
            {
                "id": "D02",
                "title": "Pollination",
                "title_ar": "التلقيح",
                "type": ContentType.VIDEO,
                "duration": 25,
                "points": 20,
            },
            {
                "id": "D03",
                "title": "RPW Prevention",
                "title_ar": "الوقاية من سوسة النخيل",
                "type": ContentType.PRACTICAL,
                "duration": 30,
                "points": 30,
            },
            {
                "id": "D04",
                "title": "Irrigation & Fertilization",
                "title_ar": "الري والتسميد",
                "type": ContentType.ARTICLE,
                "duration": 15,
                "points": 15,
            },
            {
                "id": "D05",
                "title": "Harvest & Post-Harvest",
                "title_ar": "الحصاد وما بعده",
                "type": ContentType.VIDEO,
                "duration": 20,
                "points": 15,
            },
        ],
    },
    {
        "path_id": "LP-IPM",
        "title": "Integrated Pest Management",
        "title_ar": "الإدارة المتكاملة للآفات",
        "crop_type": "general",
        "modules": [
            {
                "id": "I01",
                "title": "IPM Principles",
                "title_ar": "مبادئ الإدارة المتكاملة",
                "type": ContentType.VIDEO,
                "duration": 20,
                "points": 15,
            },
            {
                "id": "I02",
                "title": "Pest Identification",
                "title_ar": "تحديد الآفات",
                "type": ContentType.PRACTICAL,
                "duration": 30,
                "points": 25,
            },
            {
                "id": "I03",
                "title": "Biological Control",
                "title_ar": "المكافحة الحيوية",
                "type": ContentType.ARTICLE,
                "duration": 15,
                "points": 15,
            },
            {
                "id": "I04",
                "title": "Safe Pesticide Use",
                "title_ar": "الاستخدام الآمن للمبيدات",
                "type": ContentType.VIDEO,
                "duration": 25,
                "points": 20,
            },
            {
                "id": "I05",
                "title": "IPM Assessment",
                "title_ar": "تقييم الإدارة المتكاملة",
                "type": ContentType.QUIZ,
                "duration": 20,
                "points": 30,
            },
        ],
    },
    {
        "path_id": "LP-SMART-IRRIGATION",
        "title": "Smart Irrigation Techniques",
        "title_ar": "تقنيات الري الذكي",
        "crop_type": "general",
        "modules": [
            {
                "id": "S01",
                "title": "Water Requirements",
                "title_ar": "الاحتياجات المائية",
                "type": ContentType.ARTICLE,
                "duration": 15,
                "points": 10,
            },
            {
                "id": "S02",
                "title": "Drip vs Sprinkler",
                "title_ar": "التنقيط مقابل الرشاش",
                "type": ContentType.VIDEO,
                "duration": 20,
                "points": 15,
            },
            {
                "id": "S03",
                "title": "Soil Moisture Monitoring",
                "title_ar": "مراقبة رطوبة التربة",
                "type": ContentType.PRACTICAL,
                "duration": 25,
                "points": 20,
            },
            {
                "id": "S04",
                "title": "Scheduling with ET",
                "title_ar": "الجدولة باستخدام التبخر-نتح",
                "type": ContentType.VIDEO,
                "duration": 20,
                "points": 20,
            },
            {
                "id": "S05",
                "title": "Water Conservation",
                "title_ar": "الحفاظ على المياه",
                "type": ContentType.QUIZ,
                "duration": 15,
                "points": 25,
            },
        ],
    },
]

# Farmer level titles (gamification)
FARMER_LEVELS = {
    1: ("Seedling", "بذرة", 0),
    2: ("Sprout", "نبتة", 100),
    3: ("Sapling", "شتلة", 300),
    4: ("Cultivator", "مزارع", 600),
    5: ("Expert Farmer", "مزارع خبير", 1000),
    6: ("Master Farmer", "مزارع محترف", 1500),
    7: ("Agricultural Sage", "حكيم زراعي", 2500),
}


class EducationPlatform:
    """Farmer education and training platform.

    منصة تعليم وتدريب المزارعين.
    """

    def __init__(self):
        self._paths = self._load_paths()
        self._progress: dict[str, FarmerProgress] = {}

    def _load_paths(self) -> list[LearningPath]:
        paths = []
        for p in LEARNING_PATHS:
            modules = []
            for m in p.get("modules", []):
                modules.append(
                    LearningModule(
                        module_id=m["id"],
                        title=m["title"],
                        title_ar=m["title_ar"],
                        content_type=m.get("type", ContentType.ARTICLE),
                        content_type_ar=CONTENT_TYPE_AR.get(m.get("type", ContentType.ARTICLE), ""),
                        duration_minutes=m.get("duration", 15),
                        points=m.get("points", 10),
                        crop_type=p.get("crop_type", ""),
                    )
                )

            total_hrs = sum(m.duration_minutes for m in modules) / 60
            total_pts = sum(m.points for m in modules)

            paths.append(
                LearningPath(
                    path_id=p["path_id"],
                    title=p["title"],
                    title_ar=p["title_ar"],
                    modules=modules,
                    total_duration_hours=round(total_hrs, 1),
                    total_points=total_pts,
                    crop_type=p.get("crop_type", ""),
                )
            )
        return paths

    def get_paths(self, crop_type: str | None = None) -> list[LearningPath]:
        """Get available learning paths."""
        if crop_type:
            return [p for p in self._paths if p.crop_type in (crop_type, "general")]
        return self._paths

    def get_path(self, path_id: str) -> LearningPath | None:
        for p in self._paths:
            if p.path_id == path_id:
                return p
        return None

    def get_farmer_level(self, total_points: int) -> tuple[int, str, str]:
        """Get farmer level from points."""
        level = 1
        title = "Seedling"
        title_ar = "بذرة"
        for lvl, (t, t_ar, threshold) in FARMER_LEVELS.items():
            if total_points >= threshold:
                level = lvl
                title = t
                title_ar = t_ar
        return level, title, title_ar

    def complete_module(self, farmer_id: str, module_id: str, score_percent: float = 100.0) -> FarmerProgress:
        """Record module completion."""
        if farmer_id not in self._progress:
            self._progress[farmer_id] = FarmerProgress(farmer_id=farmer_id)

        progress = self._progress[farmer_id]

        # Find module points
        points = 10
        for path in self._paths:
            for module in path.modules:
                if module.module_id == module_id:
                    points = int(module.points * (score_percent / 100))
                    break

        progress.total_points += points
        progress.completed_modules += 1

        level, title, title_ar = self.get_farmer_level(progress.total_points)
        progress.level = level
        progress.level_title = title
        progress.level_title_ar = title_ar

        return progress

    def issue_certificate(self, farmer_id: str, path_id: str, score_percent: float = 100.0) -> DigitalCertificate:
        """Issue a digital certificate."""
        path = self.get_path(path_id)
        return DigitalCertificate(
            certificate_id=f"CERT-{farmer_id}-{path_id}-{datetime.now().strftime('%Y%m%d')}",
            farmer_id=farmer_id,
            path_id=path_id,
            title=path.title if path else "",
            title_ar=path.title_ar if path else "",
            certificate_type=CertificateType.COMPLETION,
            issued_date=datetime.now(UTC).isoformat(),
            score_percent=score_percent,
            verification_code=f"SAHOOL-{farmer_id[:8]}-{datetime.now().strftime('%Y%m%d%H%M')}",
        )
