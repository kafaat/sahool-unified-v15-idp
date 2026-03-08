"""
Learning Marketplace Models
===========================
نماذج سوق التعلم التعليمي

Data models for the educational content marketplace including:
- Courses and curriculum structure
- Lessons and content types (video, PDF, interactive)
- Certifications and achievements
- Farmer skill levels and competencies
- Expert content authoring

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class ContentType(StrEnum):
    """Content type for lessons | نوع المحتوى للدروس"""

    VIDEO = "video"  # فيديو
    PDF = "pdf"  # مستند PDF
    INTERACTIVE = "interactive"  # تفاعلي
    QUIZ = "quiz"  # اختبار
    ARTICLE = "article"  # مقال
    INFOGRAPHIC = "infographic"  # إنفوجرافيك
    AUDIO = "audio"  # صوتي
    SIMULATION = "simulation"  # محاكاة


class DifficultyLevel(StrEnum):
    """Difficulty level | مستوى الصعوبة"""

    BEGINNER = "beginner"  # مبتدئ
    INTERMEDIATE = "intermediate"  # متوسط
    ADVANCED = "advanced"  # متقدم
    EXPERT = "expert"  # خبير


class CourseStatus(StrEnum):
    """Course status | حالة الدورة"""

    DRAFT = "draft"  # مسودة
    REVIEW = "review"  # قيد المراجعة
    PUBLISHED = "published"  # منشور
    ARCHIVED = "archived"  # مؤرشف
    SUSPENDED = "suspended"  # معلق


class CertificationType(StrEnum):
    """Certification type | نوع الشهادة"""

    COMPLETION = "completion"  # شهادة إتمام
    COMPETENCY = "competency"  # شهادة كفاءة
    PROFESSIONAL = "professional"  # شهادة مهنية
    MASTER = "master"  # شهادة إتقان
    SPECIALIST = "specialist"  # شهادة تخصص


class SkillCategory(StrEnum):
    """Skill category | فئة المهارة"""

    IRRIGATION = "irrigation"  # الري
    FERTILIZATION = "fertilization"  # التسميد
    PEST_MANAGEMENT = "pest_management"  # إدارة الآفات
    CROP_MANAGEMENT = "crop_management"  # إدارة المحاصيل
    SOIL_HEALTH = "soil_health"  # صحة التربة
    HARVESTING = "harvesting"  # الحصاد
    POST_HARVEST = "post_harvest"  # ما بعد الحصاد
    FARM_PLANNING = "farm_planning"  # تخطيط المزرعة
    TECHNOLOGY = "technology"  # التقنية
    BUSINESS = "business"  # الأعمال
    SUSTAINABILITY = "sustainability"  # الاستدامة
    SAFETY = "safety"  # السلامة
    GLOBALGAP = "globalgap"  # GlobalGAP


class ContentLanguage(StrEnum):
    """Content language | لغة المحتوى"""

    ARABIC = "ar"  # العربية
    ENGLISH = "en"  # الإنجليزية
    BILINGUAL = "bilingual"  # ثنائي اللغة


class EnrollmentStatus(StrEnum):
    """Enrollment status | حالة التسجيل"""

    ENROLLED = "enrolled"  # مسجل
    IN_PROGRESS = "in_progress"  # قيد التقدم
    COMPLETED = "completed"  # مكتمل
    DROPPED = "dropped"  # منسحب
    EXPIRED = "expired"  # منتهي الصلاحية


class QuizQuestionType(StrEnum):
    """Quiz question type | نوع سؤال الاختبار"""

    MULTIPLE_CHOICE = "multiple_choice"  # اختيار من متعدد
    TRUE_FALSE = "true_false"  # صح أو خطأ
    FILL_BLANK = "fill_blank"  # ملء الفراغ
    MATCHING = "matching"  # مطابقة
    IMAGE_BASED = "image_based"  # قائم على الصورة


@dataclass
class BilingualText:
    """Bilingual text container | حاوية النص ثنائي اللغة"""

    en: str = ""
    ar: str = ""

    def get(self, language: str = "en") -> str:
        """Get text in specified language"""
        return self.ar if language == "ar" else self.en

    def to_dict(self) -> dict[str, str]:
        """Convert to dictionary"""
        return {"en": self.en, "ar": self.ar}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BilingualText:
        """Create from dictionary"""
        if isinstance(data, str):
            return cls(en=data, ar=data)
        return cls(en=data.get("en", ""), ar=data.get("ar", ""))


@dataclass
class ContentResource:
    """
    Content resource (video, PDF, etc.)
    مورد المحتوى (فيديو، PDF، إلخ)
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_type: ContentType = ContentType.VIDEO

    # Resource location
    url: str = ""
    thumbnail_url: str | None = None

    # Metadata
    title: BilingualText = field(default_factory=BilingualText)
    description: BilingualText = field(default_factory=BilingualText)

    # Duration/size
    duration_minutes: int = 0  # For video/audio
    file_size_mb: float = 0.0
    page_count: int = 0  # For PDF

    # Quality
    quality: str = "720p"  # For video

    # Offline availability
    offline_available: bool = True
    download_url: str | None = None

    # Accessibility
    has_captions: bool = False
    caption_languages: list[str] = field(default_factory=list)
    has_transcript: bool = False

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "content_type": self.content_type.value,
            "url": self.url,
            "thumbnail_url": self.thumbnail_url,
            "title": self.title.to_dict(),
            "description": self.description.to_dict(),
            "duration_minutes": self.duration_minutes,
            "file_size_mb": self.file_size_mb,
            "page_count": self.page_count,
            "quality": self.quality,
            "offline_available": self.offline_available,
            "download_url": self.download_url,
            "has_captions": self.has_captions,
            "caption_languages": self.caption_languages,
            "has_transcript": self.has_transcript,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ContentResource:
        """Create from dictionary"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            content_type=ContentType(data.get("content_type", "video")),
            url=data.get("url", ""),
            thumbnail_url=data.get("thumbnail_url"),
            title=BilingualText.from_dict(data.get("title", {})),
            description=BilingualText.from_dict(data.get("description", {})),
            duration_minutes=data.get("duration_minutes", 0),
            file_size_mb=data.get("file_size_mb", 0.0),
            page_count=data.get("page_count", 0),
            quality=data.get("quality", "720p"),
            offline_available=data.get("offline_available", True),
            download_url=data.get("download_url"),
            has_captions=data.get("has_captions", False),
            caption_languages=data.get("caption_languages", []),
            has_transcript=data.get("has_transcript", False),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(UTC),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(UTC),
        )


@dataclass
class QuizQuestion:
    """
    Quiz question
    سؤال الاختبار
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    question_type: QuizQuestionType = QuizQuestionType.MULTIPLE_CHOICE

    # Question content
    question: BilingualText = field(default_factory=BilingualText)
    explanation: BilingualText = field(default_factory=BilingualText)

    # Options (for multiple choice)
    options: list[BilingualText] = field(default_factory=list)
    correct_answer: int | str | list[int] = 0  # Index or value

    # Points
    points: int = 10

    # Media
    image_url: str | None = None

    # Order
    order: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "question_type": self.question_type.value,
            "question": self.question.to_dict(),
            "explanation": self.explanation.to_dict(),
            "options": [opt.to_dict() for opt in self.options],
            "correct_answer": self.correct_answer,
            "points": self.points,
            "image_url": self.image_url,
            "order": self.order,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QuizQuestion:
        """Create from dictionary"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            question_type=QuizQuestionType(data.get("question_type", "multiple_choice")),
            question=BilingualText.from_dict(data.get("question", {})),
            explanation=BilingualText.from_dict(data.get("explanation", {})),
            options=[BilingualText.from_dict(opt) for opt in data.get("options", [])],
            correct_answer=data.get("correct_answer", 0),
            points=data.get("points", 10),
            image_url=data.get("image_url"),
            order=data.get("order", 0),
        )


@dataclass
class Quiz:
    """
    Quiz assessment
    اختبار التقييم
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Quiz content
    title: BilingualText = field(default_factory=BilingualText)
    description: BilingualText = field(default_factory=BilingualText)
    instructions: BilingualText = field(default_factory=BilingualText)

    # Questions
    questions: list[QuizQuestion] = field(default_factory=list)

    # Settings
    passing_score: int = 70  # Percentage
    time_limit_minutes: int | None = None
    attempts_allowed: int = 3
    shuffle_questions: bool = True
    shuffle_options: bool = True
    show_correct_answers: bool = True

    # Total points
    total_points: int = 0

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self):
        """Calculate total points"""
        self.total_points = sum(q.points for q in self.questions)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "title": self.title.to_dict(),
            "description": self.description.to_dict(),
            "instructions": self.instructions.to_dict(),
            "questions": [q.to_dict() for q in self.questions],
            "passing_score": self.passing_score,
            "time_limit_minutes": self.time_limit_minutes,
            "attempts_allowed": self.attempts_allowed,
            "shuffle_questions": self.shuffle_questions,
            "shuffle_options": self.shuffle_options,
            "show_correct_answers": self.show_correct_answers,
            "total_points": self.total_points,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Quiz:
        """Create from dictionary"""
        quiz = cls(
            id=data.get("id", str(uuid.uuid4())),
            title=BilingualText.from_dict(data.get("title", {})),
            description=BilingualText.from_dict(data.get("description", {})),
            instructions=BilingualText.from_dict(data.get("instructions", {})),
            questions=[QuizQuestion.from_dict(q) for q in data.get("questions", [])],
            passing_score=data.get("passing_score", 70),
            time_limit_minutes=data.get("time_limit_minutes"),
            attempts_allowed=data.get("attempts_allowed", 3),
            shuffle_questions=data.get("shuffle_questions", True),
            shuffle_options=data.get("shuffle_options", True),
            show_correct_answers=data.get("show_correct_answers", True),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(UTC),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(UTC),
        )
        return quiz


@dataclass
class Lesson:
    """
    Individual lesson within a course
    درس فردي ضمن دورة
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str = ""
    module_id: str | None = None  # Optional grouping

    # Content
    title: BilingualText = field(default_factory=BilingualText)
    description: BilingualText = field(default_factory=BilingualText)
    objectives: list[BilingualText] = field(default_factory=list)

    # Resources
    primary_content: ContentResource | None = None
    supplementary_content: list[ContentResource] = field(default_factory=list)

    # Assessment
    quiz: Quiz | None = None

    # Order and structure
    order: int = 0
    is_preview: bool = False  # Can be viewed without enrollment
    is_mandatory: bool = True

    # Duration
    estimated_duration_minutes: int = 30

    # Prerequisites
    prerequisite_lesson_ids: list[str] = field(default_factory=list)

    # Skills taught
    skills: list[SkillCategory] = field(default_factory=list)

    # Status
    status: CourseStatus = CourseStatus.DRAFT

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    published_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "course_id": self.course_id,
            "module_id": self.module_id,
            "title": self.title.to_dict(),
            "description": self.description.to_dict(),
            "objectives": [obj.to_dict() for obj in self.objectives],
            "primary_content": self.primary_content.to_dict() if self.primary_content else None,
            "supplementary_content": [c.to_dict() for c in self.supplementary_content],
            "quiz": self.quiz.to_dict() if self.quiz else None,
            "order": self.order,
            "is_preview": self.is_preview,
            "is_mandatory": self.is_mandatory,
            "estimated_duration_minutes": self.estimated_duration_minutes,
            "prerequisite_lesson_ids": self.prerequisite_lesson_ids,
            "skills": [s.value for s in self.skills],
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "published_at": self.published_at.isoformat() if self.published_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Lesson:
        """Create from dictionary"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            course_id=data.get("course_id", ""),
            module_id=data.get("module_id"),
            title=BilingualText.from_dict(data.get("title", {})),
            description=BilingualText.from_dict(data.get("description", {})),
            objectives=[BilingualText.from_dict(obj) for obj in data.get("objectives", [])],
            primary_content=ContentResource.from_dict(data["primary_content"]) if data.get("primary_content") else None,
            supplementary_content=[ContentResource.from_dict(c) for c in data.get("supplementary_content", [])],
            quiz=Quiz.from_dict(data["quiz"]) if data.get("quiz") else None,
            order=data.get("order", 0),
            is_preview=data.get("is_preview", False),
            is_mandatory=data.get("is_mandatory", True),
            estimated_duration_minutes=data.get("estimated_duration_minutes", 30),
            prerequisite_lesson_ids=data.get("prerequisite_lesson_ids", []),
            skills=[SkillCategory(s) for s in data.get("skills", [])],
            status=CourseStatus(data.get("status", "draft")),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(UTC),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(UTC),
            published_at=datetime.fromisoformat(data["published_at"]) if data.get("published_at") else None,
        )


@dataclass
class CourseModule:
    """
    Course module (grouping of lessons)
    وحدة الدورة (تجميع الدروس)
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str = ""

    # Content
    title: BilingualText = field(default_factory=BilingualText)
    description: BilingualText = field(default_factory=BilingualText)

    # Lessons
    lesson_ids: list[str] = field(default_factory=list)

    # Order
    order: int = 0

    # Duration
    estimated_duration_minutes: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "course_id": self.course_id,
            "title": self.title.to_dict(),
            "description": self.description.to_dict(),
            "lesson_ids": self.lesson_ids,
            "order": self.order,
            "estimated_duration_minutes": self.estimated_duration_minutes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CourseModule:
        """Create from dictionary"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            course_id=data.get("course_id", ""),
            title=BilingualText.from_dict(data.get("title", {})),
            description=BilingualText.from_dict(data.get("description", {})),
            lesson_ids=data.get("lesson_ids", []),
            order=data.get("order", 0),
            estimated_duration_minutes=data.get("estimated_duration_minutes", 0),
        )


@dataclass
class Expert:
    """
    Content expert/instructor
    خبير المحتوى/المدرب
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""

    # Profile
    name: BilingualText = field(default_factory=BilingualText)
    title: BilingualText = field(default_factory=BilingualText)
    bio: BilingualText = field(default_factory=BilingualText)

    # Contact
    email: str = ""

    # Media
    avatar_url: str | None = None

    # Expertise
    specializations: list[SkillCategory] = field(default_factory=list)
    credentials: list[BilingualText] = field(default_factory=list)
    years_of_experience: int = 0

    # Stats
    courses_created: int = 0
    total_students: int = 0
    average_rating: float = 0.0

    # Verification
    is_verified: bool = False
    verified_at: datetime | None = None

    # Status
    is_active: bool = True

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name.to_dict(),
            "title": self.title.to_dict(),
            "bio": self.bio.to_dict(),
            "email": self.email,
            "avatar_url": self.avatar_url,
            "specializations": [s.value for s in self.specializations],
            "credentials": [c.to_dict() for c in self.credentials],
            "years_of_experience": self.years_of_experience,
            "courses_created": self.courses_created,
            "total_students": self.total_students,
            "average_rating": self.average_rating,
            "is_verified": self.is_verified,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Expert:
        """Create from dictionary"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            user_id=data.get("user_id", ""),
            name=BilingualText.from_dict(data.get("name", {})),
            title=BilingualText.from_dict(data.get("title", {})),
            bio=BilingualText.from_dict(data.get("bio", {})),
            email=data.get("email", ""),
            avatar_url=data.get("avatar_url"),
            specializations=[SkillCategory(s) for s in data.get("specializations", [])],
            credentials=[BilingualText.from_dict(c) for c in data.get("credentials", [])],
            years_of_experience=data.get("years_of_experience", 0),
            courses_created=data.get("courses_created", 0),
            total_students=data.get("total_students", 0),
            average_rating=data.get("average_rating", 0.0),
            is_verified=data.get("is_verified", False),
            verified_at=datetime.fromisoformat(data["verified_at"]) if data.get("verified_at") else None,
            is_active=data.get("is_active", True),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(UTC),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(UTC),
        )


@dataclass
class Course:
    """
    Educational course
    دورة تعليمية
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Basic info
    title: BilingualText = field(default_factory=BilingualText)
    subtitle: BilingualText = field(default_factory=BilingualText)
    description: BilingualText = field(default_factory=BilingualText)

    # Learning outcomes
    objectives: list[BilingualText] = field(default_factory=list)
    prerequisites: list[BilingualText] = field(default_factory=list)
    target_audience: BilingualText = field(default_factory=BilingualText)

    # Categorization
    category: SkillCategory = SkillCategory.CROP_MANAGEMENT
    tags: list[str] = field(default_factory=list)
    difficulty: DifficultyLevel = DifficultyLevel.BEGINNER
    language: ContentLanguage = ContentLanguage.BILINGUAL

    # Structure
    modules: list[CourseModule] = field(default_factory=list)
    lessons: list[Lesson] = field(default_factory=list)

    # Experts
    expert_ids: list[str] = field(default_factory=list)

    # Media
    thumbnail_url: str | None = None
    trailer_url: str | None = None

    # Duration
    estimated_duration_minutes: int = 0

    # Pricing
    is_free: bool = True
    price: float = 0.0
    currency: str = "SAR"

    # Status
    status: CourseStatus = CourseStatus.DRAFT

    # Stats
    total_enrollments: int = 0
    total_completions: int = 0
    average_rating: float = 0.0
    rating_count: int = 0

    # Certification
    certification_id: str | None = None
    offers_certificate: bool = True

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    published_at: datetime | None = None

    # Tenant
    tenant_id: str = ""

    def __post_init__(self):
        """Calculate total duration"""
        if not self.estimated_duration_minutes:
            self.estimated_duration_minutes = sum(lesson.estimated_duration_minutes for lesson in self.lessons)

    @property
    def completion_rate(self) -> float:
        """Calculate completion rate"""
        if self.total_enrollments == 0:
            return 0.0
        return (self.total_completions / self.total_enrollments) * 100

    @property
    def lesson_count(self) -> int:
        """Get total lesson count"""
        return len(self.lessons)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "title": self.title.to_dict(),
            "subtitle": self.subtitle.to_dict(),
            "description": self.description.to_dict(),
            "objectives": [obj.to_dict() for obj in self.objectives],
            "prerequisites": [prereq.to_dict() for prereq in self.prerequisites],
            "target_audience": self.target_audience.to_dict(),
            "category": self.category.value,
            "tags": self.tags,
            "difficulty": self.difficulty.value,
            "language": self.language.value,
            "modules": [m.to_dict() for m in self.modules],
            "lessons": [l.to_dict() for l in self.lessons],
            "expert_ids": self.expert_ids,
            "thumbnail_url": self.thumbnail_url,
            "trailer_url": self.trailer_url,
            "estimated_duration_minutes": self.estimated_duration_minutes,
            "is_free": self.is_free,
            "price": self.price,
            "currency": self.currency,
            "status": self.status.value,
            "total_enrollments": self.total_enrollments,
            "total_completions": self.total_completions,
            "average_rating": self.average_rating,
            "rating_count": self.rating_count,
            "certification_id": self.certification_id,
            "offers_certificate": self.offers_certificate,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "tenant_id": self.tenant_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Course:
        """Create from dictionary"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=BilingualText.from_dict(data.get("title", {})),
            subtitle=BilingualText.from_dict(data.get("subtitle", {})),
            description=BilingualText.from_dict(data.get("description", {})),
            objectives=[BilingualText.from_dict(obj) for obj in data.get("objectives", [])],
            prerequisites=[BilingualText.from_dict(prereq) for prereq in data.get("prerequisites", [])],
            target_audience=BilingualText.from_dict(data.get("target_audience", {})),
            category=SkillCategory(data.get("category", "crop_management")),
            tags=data.get("tags", []),
            difficulty=DifficultyLevel(data.get("difficulty", "beginner")),
            language=ContentLanguage(data.get("language", "bilingual")),
            modules=[CourseModule.from_dict(m) for m in data.get("modules", [])],
            lessons=[Lesson.from_dict(l) for l in data.get("lessons", [])],
            expert_ids=data.get("expert_ids", []),
            thumbnail_url=data.get("thumbnail_url"),
            trailer_url=data.get("trailer_url"),
            estimated_duration_minutes=data.get("estimated_duration_minutes", 0),
            is_free=data.get("is_free", True),
            price=data.get("price", 0.0),
            currency=data.get("currency", "SAR"),
            status=CourseStatus(data.get("status", "draft")),
            total_enrollments=data.get("total_enrollments", 0),
            total_completions=data.get("total_completions", 0),
            average_rating=data.get("average_rating", 0.0),
            rating_count=data.get("rating_count", 0),
            certification_id=data.get("certification_id"),
            offers_certificate=data.get("offers_certificate", True),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(UTC),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(UTC),
            published_at=datetime.fromisoformat(data["published_at"]) if data.get("published_at") else None,
            tenant_id=data.get("tenant_id", ""),
        )


@dataclass
class Certification:
    """
    Certification/credential
    شهادة/اعتماد
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Basic info
    name: BilingualText = field(default_factory=BilingualText)
    description: BilingualText = field(default_factory=BilingualText)

    # Type
    certification_type: CertificationType = CertificationType.COMPLETION

    # Requirements
    required_course_ids: list[str] = field(default_factory=list)
    required_skills: list[SkillCategory] = field(default_factory=list)
    minimum_score: int = 70  # Percentage

    # Validity
    validity_days: int | None = 365  # None = lifetime

    # Badge
    badge_url: str | None = None
    badge_color: str = "#4CAF50"

    # Status
    is_active: bool = True

    # Stats
    total_issued: int = 0

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Tenant
    tenant_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name.to_dict(),
            "description": self.description.to_dict(),
            "certification_type": self.certification_type.value,
            "required_course_ids": self.required_course_ids,
            "required_skills": [s.value for s in self.required_skills],
            "minimum_score": self.minimum_score,
            "validity_days": self.validity_days,
            "badge_url": self.badge_url,
            "badge_color": self.badge_color,
            "is_active": self.is_active,
            "total_issued": self.total_issued,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tenant_id": self.tenant_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Certification:
        """Create from dictionary"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=BilingualText.from_dict(data.get("name", {})),
            description=BilingualText.from_dict(data.get("description", {})),
            certification_type=CertificationType(data.get("certification_type", "completion")),
            required_course_ids=data.get("required_course_ids", []),
            required_skills=[SkillCategory(s) for s in data.get("required_skills", [])],
            minimum_score=data.get("minimum_score", 70),
            validity_days=data.get("validity_days", 365),
            badge_url=data.get("badge_url"),
            badge_color=data.get("badge_color", "#4CAF50"),
            is_active=data.get("is_active", True),
            total_issued=data.get("total_issued", 0),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(UTC),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(UTC),
            tenant_id=data.get("tenant_id", ""),
        )


@dataclass
class FarmerCertification:
    """
    Issued certification for a farmer
    شهادة صادرة للمزارع
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    farmer_id: str = ""
    certification_id: str = ""

    # Certificate details
    certificate_number: str = ""

    # Issue info
    issued_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None

    # Score achieved
    score: int = 0

    # Status
    is_valid: bool = True
    revoked_at: datetime | None = None
    revocation_reason: str | None = None

    # Verification
    verification_url: str | None = None

    # Download
    certificate_pdf_url: str | None = None

    def __post_init__(self):
        """Generate certificate number if not provided"""
        if not self.certificate_number:
            self.certificate_number = f"SAHOOL-CERT-{self.id[:8].upper()}"

    @property
    def is_expired(self) -> bool:
        """Check if certification is expired"""
        if not self.expires_at:
            return False
        return datetime.now(UTC) > self.expires_at

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "farmer_id": self.farmer_id,
            "certification_id": self.certification_id,
            "certificate_number": self.certificate_number,
            "issued_at": self.issued_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "score": self.score,
            "is_valid": self.is_valid,
            "is_expired": self.is_expired,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "revocation_reason": self.revocation_reason,
            "verification_url": self.verification_url,
            "certificate_pdf_url": self.certificate_pdf_url,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FarmerCertification:
        """Create from dictionary"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            farmer_id=data.get("farmer_id", ""),
            certification_id=data.get("certification_id", ""),
            certificate_number=data.get("certificate_number", ""),
            issued_at=datetime.fromisoformat(data["issued_at"]) if data.get("issued_at") else datetime.now(UTC),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            score=data.get("score", 0),
            is_valid=data.get("is_valid", True),
            revoked_at=datetime.fromisoformat(data["revoked_at"]) if data.get("revoked_at") else None,
            revocation_reason=data.get("revocation_reason"),
            verification_url=data.get("verification_url"),
            certificate_pdf_url=data.get("certificate_pdf_url"),
        )


@dataclass
class FarmerSkill:
    """
    Farmer skill level
    مستوى مهارة المزارع
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    farmer_id: str = ""

    # Skill info
    category: SkillCategory = SkillCategory.CROP_MANAGEMENT
    level: DifficultyLevel = DifficultyLevel.BEGINNER

    # Progress
    experience_points: int = 0
    courses_completed: int = 0
    quizzes_passed: int = 0

    # Scores
    average_quiz_score: float = 0.0
    best_quiz_score: float = 0.0

    # Time spent
    total_learning_minutes: int = 0

    # Last activity
    last_activity_at: datetime | None = None

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def level_progress(self) -> float:
        """Calculate progress to next level (0-100)"""
        # XP thresholds for each level
        thresholds = {
            DifficultyLevel.BEGINNER: 0,
            DifficultyLevel.INTERMEDIATE: 500,
            DifficultyLevel.ADVANCED: 1500,
            DifficultyLevel.EXPERT: 3500,
        }

        current_threshold = thresholds[self.level]
        levels = list(DifficultyLevel)
        current_index = levels.index(self.level)

        if current_index >= len(levels) - 1:
            return 100.0  # Max level

        next_threshold = thresholds[levels[current_index + 1]]
        range_xp = next_threshold - current_threshold
        progress_xp = self.experience_points - current_threshold

        return min(100.0, (progress_xp / range_xp) * 100)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "farmer_id": self.farmer_id,
            "category": self.category.value,
            "level": self.level.value,
            "experience_points": self.experience_points,
            "courses_completed": self.courses_completed,
            "quizzes_passed": self.quizzes_passed,
            "average_quiz_score": self.average_quiz_score,
            "best_quiz_score": self.best_quiz_score,
            "total_learning_minutes": self.total_learning_minutes,
            "level_progress": self.level_progress,
            "last_activity_at": self.last_activity_at.isoformat() if self.last_activity_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FarmerSkill:
        """Create from dictionary"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            farmer_id=data.get("farmer_id", ""),
            category=SkillCategory(data.get("category", "crop_management")),
            level=DifficultyLevel(data.get("level", "beginner")),
            experience_points=data.get("experience_points", 0),
            courses_completed=data.get("courses_completed", 0),
            quizzes_passed=data.get("quizzes_passed", 0),
            average_quiz_score=data.get("average_quiz_score", 0.0),
            best_quiz_score=data.get("best_quiz_score", 0.0),
            total_learning_minutes=data.get("total_learning_minutes", 0),
            last_activity_at=datetime.fromisoformat(data["last_activity_at"]) if data.get("last_activity_at") else None,
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(UTC),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(UTC),
        )


@dataclass
class FarmerProfile:
    """
    Farmer learning profile
    ملف تعلم المزارع
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    farmer_id: str = ""
    tenant_id: str = ""

    # Preferences
    preferred_language: ContentLanguage = ContentLanguage.ARABIC
    preferred_content_types: list[ContentType] = field(default_factory=list)

    # Farming context
    crop_types: list[str] = field(default_factory=list)
    farm_size_hectares: float | None = None
    farming_experience_years: int = 0
    region: str | None = None

    # Skills
    skills: list[FarmerSkill] = field(default_factory=list)

    # Certifications
    certifications: list[FarmerCertification] = field(default_factory=list)

    # Learning stats
    total_courses_enrolled: int = 0
    total_courses_completed: int = 0
    total_learning_minutes: int = 0
    total_xp: int = 0

    # Streak
    current_streak_days: int = 0
    longest_streak_days: int = 0
    last_learning_date: datetime | None = None

    # Goals
    weekly_learning_goal_minutes: int = 60

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def overall_level(self) -> DifficultyLevel:
        """Calculate overall level based on skills"""
        if not self.skills:
            return DifficultyLevel.BEGINNER

        # Average XP across all skills
        total_xp = sum(s.experience_points for s in self.skills)
        avg_xp = total_xp / len(self.skills)

        if avg_xp >= 3500:
            return DifficultyLevel.EXPERT
        elif avg_xp >= 1500:
            return DifficultyLevel.ADVANCED
        elif avg_xp >= 500:
            return DifficultyLevel.INTERMEDIATE
        return DifficultyLevel.BEGINNER

    def get_skill(self, category: SkillCategory) -> FarmerSkill | None:
        """Get skill by category"""
        for skill in self.skills:
            if skill.category == category:
                return skill
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "farmer_id": self.farmer_id,
            "tenant_id": self.tenant_id,
            "preferred_language": self.preferred_language.value,
            "preferred_content_types": [ct.value for ct in self.preferred_content_types],
            "crop_types": self.crop_types,
            "farm_size_hectares": self.farm_size_hectares,
            "farming_experience_years": self.farming_experience_years,
            "region": self.region,
            "skills": [s.to_dict() for s in self.skills],
            "certifications": [c.to_dict() for c in self.certifications],
            "total_courses_enrolled": self.total_courses_enrolled,
            "total_courses_completed": self.total_courses_completed,
            "total_learning_minutes": self.total_learning_minutes,
            "total_xp": self.total_xp,
            "overall_level": self.overall_level.value,
            "current_streak_days": self.current_streak_days,
            "longest_streak_days": self.longest_streak_days,
            "last_learning_date": self.last_learning_date.isoformat() if self.last_learning_date else None,
            "weekly_learning_goal_minutes": self.weekly_learning_goal_minutes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FarmerProfile:
        """Create from dictionary"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            farmer_id=data.get("farmer_id", ""),
            tenant_id=data.get("tenant_id", ""),
            preferred_language=ContentLanguage(data.get("preferred_language", "ar")),
            preferred_content_types=[ContentType(ct) for ct in data.get("preferred_content_types", [])],
            crop_types=data.get("crop_types", []),
            farm_size_hectares=data.get("farm_size_hectares"),
            farming_experience_years=data.get("farming_experience_years", 0),
            region=data.get("region"),
            skills=[FarmerSkill.from_dict(s) for s in data.get("skills", [])],
            certifications=[FarmerCertification.from_dict(c) for c in data.get("certifications", [])],
            total_courses_enrolled=data.get("total_courses_enrolled", 0),
            total_courses_completed=data.get("total_courses_completed", 0),
            total_learning_minutes=data.get("total_learning_minutes", 0),
            total_xp=data.get("total_xp", 0),
            current_streak_days=data.get("current_streak_days", 0),
            longest_streak_days=data.get("longest_streak_days", 0),
            last_learning_date=datetime.fromisoformat(data["last_learning_date"])
            if data.get("last_learning_date")
            else None,
            weekly_learning_goal_minutes=data.get("weekly_learning_goal_minutes", 60),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(UTC),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(UTC),
        )
