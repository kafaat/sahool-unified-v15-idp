"""
Learning Content Recommendations
================================
توصيات محتوى التعلم

Provides personalized course and content recommendations based on:
- Farmer profile and preferences
- Current skill levels
- Learning history
- Farming context (crops, region, experience)
- Similar farmer patterns
- Seasonal relevance

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from .models import (
    BilingualText,
    ContentLanguage,
    Course,
    CourseStatus,
    DifficultyLevel,
    FarmerProfile,
    SkillCategory,
)
from .progress import (
    EnrollmentStatus,
    ProgressTracker,
)


class RecommendationReason(StrEnum):
    """Reason for recommendation | سبب التوصية"""

    SKILL_GAP = "skill_gap"  # فجوة في المهارات
    NEXT_LEVEL = "next_level"  # المستوى التالي
    POPULAR = "popular"  # شائع
    TRENDING = "trending"  # رائج
    SIMILAR_FARMERS = "similar_farmers"  # مزارعون مشابهون
    CROP_RELEVANT = "crop_relevant"  # متعلق بالمحصول
    SEASONAL = "seasonal"  # موسمي
    PREREQUISITE = "prerequisite"  # متطلب مسبق
    CONTINUATION = "continuation"  # استمرار
    CERTIFICATION_PATH = "certification_path"  # مسار الشهادة
    PERSONALIZED = "personalized"  # مخصص
    BEGINNER_FRIENDLY = "beginner_friendly"  # مناسب للمبتدئين


class RecommendationPriority(StrEnum):
    """Recommendation priority | أولوية التوصية"""

    HIGH = "high"  # عالية
    MEDIUM = "medium"  # متوسطة
    LOW = "low"  # منخفضة


@dataclass
class RecommendationScore:
    """
    Score breakdown for a recommendation
    تفصيل درجة التوصية
    """

    # Individual scores (0-100)
    relevance_score: float = 0.0  # How relevant to farmer
    difficulty_match: float = 0.0  # How well difficulty matches level
    skill_gap_score: float = 0.0  # How much it addresses skill gaps
    popularity_score: float = 0.0  # General popularity
    freshness_score: float = 0.0  # Recency of content
    completion_likelihood: float = 0.0  # Predicted completion rate

    # Weights (sum to 1.0)
    relevance_weight: float = 0.30
    difficulty_weight: float = 0.20
    skill_gap_weight: float = 0.25
    popularity_weight: float = 0.10
    freshness_weight: float = 0.05
    completion_weight: float = 0.10

    @property
    def total_score(self) -> float:
        """Calculate weighted total score"""
        return (
            self.relevance_score * self.relevance_weight
            + self.difficulty_match * self.difficulty_weight
            + self.skill_gap_score * self.skill_gap_weight
            + self.popularity_score * self.popularity_weight
            + self.freshness_score * self.freshness_weight
            + self.completion_likelihood * self.completion_weight
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "total_score": self.total_score,
            "breakdown": {
                "relevance": self.relevance_score,
                "difficulty_match": self.difficulty_match,
                "skill_gap": self.skill_gap_score,
                "popularity": self.popularity_score,
                "freshness": self.freshness_score,
                "completion_likelihood": self.completion_likelihood,
            },
        }


@dataclass
class CourseRecommendation:
    """
    A course recommendation
    توصية بدورة
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Course info
    course: Course = field(default_factory=Course)

    # Recommendation info
    reasons: list[RecommendationReason] = field(default_factory=list)
    priority: RecommendationPriority = RecommendationPriority.MEDIUM

    # Score
    score: RecommendationScore = field(default_factory=RecommendationScore)

    # Context
    reason_text: BilingualText = field(default_factory=BilingualText)

    # Metadata
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def primary_reason(self) -> RecommendationReason | None:
        """Get primary recommendation reason"""
        return self.reasons[0] if self.reasons else None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "course_id": self.course.id,
            "course_title": self.course.title.to_dict(),
            "course_thumbnail": self.course.thumbnail_url,
            "course_duration_minutes": self.course.estimated_duration_minutes,
            "course_difficulty": self.course.difficulty.value,
            "course_category": self.course.category.value,
            "reasons": [r.value for r in self.reasons],
            "primary_reason": self.primary_reason.value if self.primary_reason else None,
            "priority": self.priority.value,
            "score": self.score.to_dict(),
            "reason_text": self.reason_text.to_dict(),
            "generated_at": self.generated_at.isoformat(),
        }


@dataclass
class LearningPath:
    """
    A recommended learning path
    مسار تعلم موصى به
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Path info
    name: BilingualText = field(default_factory=BilingualText)
    description: BilingualText = field(default_factory=BilingualText)

    # Target
    target_skill: SkillCategory = SkillCategory.CROP_MANAGEMENT
    target_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE

    # Courses in path
    course_ids: list[str] = field(default_factory=list)
    courses: list[Course] = field(default_factory=list)

    # Duration
    total_duration_minutes: int = 0

    # Progress
    courses_completed: int = 0

    # Certification
    certification_id: str | None = None

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def progress_percentage(self) -> float:
        """Calculate path progress"""
        if not self.courses:
            return 0.0
        return (self.courses_completed / len(self.courses)) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name.to_dict(),
            "description": self.description.to_dict(),
            "target_skill": self.target_skill.value,
            "target_level": self.target_level.value,
            "course_ids": self.course_ids,
            "total_duration_minutes": self.total_duration_minutes,
            "courses_completed": self.courses_completed,
            "progress_percentage": self.progress_percentage,
            "certification_id": self.certification_id,
            "created_at": self.created_at.isoformat(),
        }


# Seasonal topic mapping (Northern Hemisphere - Middle East)
SEASONAL_TOPICS: dict[int, list[SkillCategory]] = {
    # Winter (Jan-Feb)
    1: [SkillCategory.FARM_PLANNING, SkillCategory.SOIL_HEALTH, SkillCategory.IRRIGATION],
    2: [SkillCategory.FARM_PLANNING, SkillCategory.SOIL_HEALTH, SkillCategory.FERTILIZATION],
    # Spring (Mar-May)
    3: [SkillCategory.CROP_MANAGEMENT, SkillCategory.PEST_MANAGEMENT, SkillCategory.IRRIGATION],
    4: [SkillCategory.CROP_MANAGEMENT, SkillCategory.PEST_MANAGEMENT, SkillCategory.FERTILIZATION],
    5: [SkillCategory.PEST_MANAGEMENT, SkillCategory.IRRIGATION, SkillCategory.CROP_MANAGEMENT],
    # Summer (Jun-Aug)
    6: [SkillCategory.IRRIGATION, SkillCategory.PEST_MANAGEMENT, SkillCategory.HARVESTING],
    7: [SkillCategory.IRRIGATION, SkillCategory.HARVESTING, SkillCategory.POST_HARVEST],
    8: [SkillCategory.HARVESTING, SkillCategory.POST_HARVEST, SkillCategory.IRRIGATION],
    # Fall (Sep-Nov)
    9: [SkillCategory.POST_HARVEST, SkillCategory.SOIL_HEALTH, SkillCategory.FARM_PLANNING],
    10: [SkillCategory.SOIL_HEALTH, SkillCategory.FARM_PLANNING, SkillCategory.SUSTAINABILITY],
    11: [SkillCategory.FARM_PLANNING, SkillCategory.TECHNOLOGY, SkillCategory.BUSINESS],
    # Winter (Dec)
    12: [SkillCategory.BUSINESS, SkillCategory.TECHNOLOGY, SkillCategory.FARM_PLANNING],
}

# Crop to skill category mapping
CROP_SKILL_MAPPING: dict[str, list[SkillCategory]] = {
    "wheat": [SkillCategory.CROP_MANAGEMENT, SkillCategory.IRRIGATION, SkillCategory.FERTILIZATION],
    "barley": [SkillCategory.CROP_MANAGEMENT, SkillCategory.IRRIGATION, SkillCategory.SOIL_HEALTH],
    "date_palm": [
        SkillCategory.PEST_MANAGEMENT,
        SkillCategory.IRRIGATION,
        SkillCategory.HARVESTING,
    ],
    "tomato": [
        SkillCategory.PEST_MANAGEMENT,
        SkillCategory.CROP_MANAGEMENT,
        SkillCategory.IRRIGATION,
    ],
    "cucumber": [
        SkillCategory.CROP_MANAGEMENT,
        SkillCategory.IRRIGATION,
        SkillCategory.PEST_MANAGEMENT,
    ],
    "citrus": [
        SkillCategory.IRRIGATION,
        SkillCategory.FERTILIZATION,
        SkillCategory.PEST_MANAGEMENT,
    ],
    "olives": [SkillCategory.HARVESTING, SkillCategory.POST_HARVEST, SkillCategory.IRRIGATION],
    "vegetables": [
        SkillCategory.CROP_MANAGEMENT,
        SkillCategory.PEST_MANAGEMENT,
        SkillCategory.IRRIGATION,
    ],
}


class ContentRecommender:
    """
    Content recommendation engine
    محرك توصيات المحتوى

    Provides personalized course recommendations based on:
    - Farmer profile and preferences
    - Current skill levels and gaps
    - Learning history
    - Farming context
    - Seasonal relevance
    - Popularity and trends

    Usage:
        recommender = ContentRecommender(tenant_id="farm_001")

        # Get personalized recommendations
        recommendations = await recommender.get_recommendations(
            farmer_profile,
            courses_catalog,
            limit=10
        )

        # Get learning path
        path = await recommender.suggest_learning_path(
            farmer_profile,
            target_skill=SkillCategory.IRRIGATION,
            courses_catalog
        )

        # Get next best course
        next_course = await recommender.get_next_course(
            farmer_profile,
            courses_catalog
        )
    """

    def __init__(
        self,
        tenant_id: str,
        progress_tracker: ProgressTracker | None = None,
    ):
        """
        Initialize the recommender

        Args:
            tenant_id: Tenant identifier
            progress_tracker: Progress tracker for enrollment data
        """
        self.tenant_id = tenant_id
        self.progress_tracker = progress_tracker

    async def get_recommendations(
        self,
        profile: FarmerProfile,
        courses: list[Course],
        limit: int = 10,
        include_enrolled: bool = False,
    ) -> list[CourseRecommendation]:
        """
        Get personalized course recommendations
        الحصول على توصيات الدورات المخصصة

        Args:
            profile: Farmer profile
            courses: Available courses catalog
            limit: Maximum recommendations to return
            include_enrolled: Include already enrolled courses

        Returns:
            List of CourseRecommendation sorted by score
        """
        # Get enrolled courses
        enrolled_course_ids: set[str] = set()
        if not include_enrolled and self.progress_tracker:
            enrollments = await self.progress_tracker.get_enrollments(profile.farmer_id)
            enrolled_course_ids = {
                e.course_id for e in enrollments if e.status not in [EnrollmentStatus.DROPPED, EnrollmentStatus.EXPIRED]
            }

        # Filter publishedcourses
        available_courses = [
            c for c in courses if c.status == CourseStatus.PUBLISHED and c.id not in enrolled_course_ids
        ]

        # Score each course
        recommendations: list[CourseRecommendation] = []
        for course in available_courses:
            rec = await self._score_course(profile, course)
            recommendations.append(rec)

        # Sort by total score
        recommendations.sort(key=lambda r: r.score.total_score, reverse=True)

        # Return top recommendations
        return recommendations[:limit]

    async def _score_course(
        self,
        profile: FarmerProfile,
        course: Course,
    ) -> CourseRecommendation:
        """Score a course for a farmer"""
        score = RecommendationScore()
        reasons: list[RecommendationReason] = []

        # 1. Relevance score (language, content type preferences)
        score.relevance_score = self._calculate_relevance(profile, course)

        # 2. Difficulty match
        score.difficulty_match = self._calculate_difficulty_match(profile, course)
        if score.difficulty_match > 70:
            reasons.append(RecommendationReason.NEXT_LEVEL)

        # 3. Skill gap score
        score.skill_gap_score = self._calculate_skill_gap_score(profile, course)
        if score.skill_gap_score > 60:
            reasons.append(RecommendationReason.SKILL_GAP)

        # 4. Popularity score
        score.popularity_score = self._calculate_popularity_score(course)
        if score.popularity_score > 80:
            reasons.append(RecommendationReason.POPULAR)

        # 5. Freshness score
        score.freshness_score = self._calculate_freshness_score(course)
        if score.freshness_score > 80:
            reasons.append(RecommendationReason.TRENDING)

        # 6. Completion likelihood
        score.completion_likelihood = self._calculate_completion_likelihood(profile, course)

        # Check crop relevance
        crop_score = self._calculate_crop_relevance(profile, course)
        if crop_score > 70:
            reasons.append(RecommendationReason.CROP_RELEVANT)

        # Check seasonal relevance
        if self._is_seasonally_relevant(course):
            reasons.append(RecommendationReason.SEASONAL)

        # Check beginner friendliness
        if course.difficulty == DifficultyLevel.BEGINNER and profile.overall_level == DifficultyLevel.BEGINNER:
            reasons.append(RecommendationReason.BEGINNER_FRIENDLY)

        # Determine priority
        total = score.total_score
        if total >= 70:
            priority = RecommendationPriority.HIGH
        elif total >= 50:
            priority = RecommendationPriority.MEDIUM
        else:
            priority = RecommendationPriority.LOW

        # Generate reason text
        reason_text = self._generate_reason_text(reasons, course, profile)

        return CourseRecommendation(
            course=course,
            reasons=reasons or [RecommendationReason.PERSONALIZED],
            priority=priority,
            score=score,
            reason_text=reason_text,
        )

    def _calculate_relevance(self, profile: FarmerProfile, course: Course) -> float:
        """Calculate relevance score based on preferences"""
        score = 50.0  # Base score

        # Language match
        if course.language == ContentLanguage.BILINGUAL:
            score += 20
        elif course.language == profile.preferred_language:
            score += 30

        # Content type preferences
        if profile.preferred_content_types and course.lessons:
            preferred_types = set(profile.preferred_content_types)
            course_types = set()
            for lesson in course.lessons:
                if lesson.primary_content:
                    course_types.add(lesson.primary_content.content_type)

            overlap = len(preferred_types & course_types)
            if overlap > 0:
                score += min(20, overlap * 10)

        return min(100, score)

    def _calculate_difficulty_match(self, profile: FarmerProfile, course: Course) -> float:
        """Calculate how well difficulty matches farmer level"""
        level_order = [
            DifficultyLevel.BEGINNER,
            DifficultyLevel.INTERMEDIATE,
            DifficultyLevel.ADVANCED,
            DifficultyLevel.EXPERT,
        ]

        farmer_idx = level_order.index(profile.overall_level)
        course_idx = level_order.index(course.difficulty)

        diff = course_idx - farmer_idx

        # Ideal: course is same level or one level up
        if diff == 0:
            return 100.0
        elif diff == 1:
            return 90.0  # Slightly challenging
        elif diff == -1:
            return 70.0  # Slightly easy (review)
        elif diff == 2:
            return 50.0  # Too challenging
        elif diff < -1:
            return 40.0  # Too easy
        else:
            return 30.0  # Much too challenging

    def _calculate_skill_gap_score(self, profile: FarmerProfile, course: Course) -> float:
        """Calculate how much course addresses skill gaps"""
        if not course.lessons:
            return 50.0

        # Collect skills taught by course
        course_skills: set[SkillCategory] = {course.category}
        for lesson in course.lessons:
            course_skills.update(lesson.skills)

        # Find farmer's weakest skills
        skill_levels: dict[SkillCategory, int] = {}
        level_values = {
            DifficultyLevel.BEGINNER: 1,
            DifficultyLevel.INTERMEDIATE: 2,
            DifficultyLevel.ADVANCED: 3,
            DifficultyLevel.EXPERT: 4,
        }

        for skill in profile.skills:
            skill_levels[skill.category] = level_values[skill.level]

        # Score based on addressing weak skills
        weak_skills = [
            cat
            for cat, level in skill_levels.items()
            if level < 2  # Below intermediate
        ]

        # Also consider skills not yet learned
        all_categories = set(SkillCategory)
        unlearned = all_categories - set(skill_levels.keys())

        gap_skills = set(weak_skills) | unlearned
        overlap = course_skills & gap_skills

        if not gap_skills:
            return 50.0  # No gaps, neutral score

        return min(100, (len(overlap) / len(course_skills)) * 100 + 30)

    def _calculate_popularity_score(self, course: Course) -> float:
        """Calculate popularity score based on enrollments and ratings"""
        score = 0.0

        # Enrollment-based score
        if course.total_enrollments > 1000:
            score += 40
        elif course.total_enrollments > 500:
            score += 30
        elif course.total_enrollments > 100:
            score += 20
        elif course.total_enrollments > 10:
            score += 10

        # Rating-based score
        if course.rating_count > 0:
            if course.average_rating >= 4.5:
                score += 40
            elif course.average_rating >= 4.0:
                score += 30
            elif course.average_rating >= 3.5:
                score += 20
            else:
                score += 10

        # Completion rate
        if course.total_enrollments > 0:
            completion_rate = course.completion_rate
            if completion_rate > 70:
                score += 20
            elif completion_rate > 50:
                score += 10

        return min(100, score)

    def _calculate_freshness_score(self, course: Course) -> float:
        """Calculate freshness score based on update date"""
        if not course.updated_at:
            return 50.0

        days_since_update = (datetime.now(UTC) - course.updated_at).days

        if days_since_update < 30:
            return 100.0
        elif days_since_update < 90:
            return 80.0
        elif days_since_update < 180:
            return 60.0
        elif days_since_update < 365:
            return 40.0
        else:
            return 20.0

    def _calculate_completion_likelihood(self, profile: FarmerProfile, course: Course) -> float:
        """Predict likelihood of completion based on profile"""
        score = 50.0  # Base

        # Time availability (based on weekly goal)
        weekly_minutes = profile.weekly_learning_goal_minutes
        max(1, course.estimated_duration_minutes / 60)  # Assume 1 hour/week

        if weekly_minutes >= 120:  # 2+ hours/week
            score += 20
        elif weekly_minutes >= 60:  # 1+ hour/week
            score += 10

        # Past completion rate
        if profile.total_courses_enrolled > 0:
            completion_rate = profile.total_courses_completed / profile.total_courses_enrolled
            score += completion_rate * 30

        # Streak indicates consistency
        if profile.current_streak_days >= 7:
            score += 10
        elif profile.current_streak_days >= 3:
            score += 5

        return min(100, score)

    def _calculate_crop_relevance(self, profile: FarmerProfile, course: Course) -> float:
        """Calculate relevance to farmer's crops"""
        if not profile.crop_types:
            return 50.0  # Neutral if no crop info

        # Get relevant skills for farmer's crops
        relevant_skills: set[SkillCategory] = set()
        for crop in profile.crop_types:
            crop_lower = crop.lower()
            if crop_lower in CROP_SKILL_MAPPING:
                relevant_skills.update(CROP_SKILL_MAPPING[crop_lower])

        if not relevant_skills:
            return 50.0

        # Check if course category or lessons match
        if course.category in relevant_skills:
            return 90.0

        # Check lesson skills
        lesson_skills: set[SkillCategory] = set()
        for lesson in course.lessons:
            lesson_skills.update(lesson.skills)

        overlap = relevant_skills & lesson_skills
        if overlap:
            return 70.0 + (len(overlap) * 5)

        return 40.0

    def _is_seasonally_relevant(self, course: Course) -> bool:
        """Check if course is seasonally relevant"""
        current_month = datetime.now(UTC).month
        seasonal_skills = SEASONAL_TOPICS.get(current_month, [])

        if course.category in seasonal_skills:
            return True

        return any(any(skill in seasonal_skills for skill in lesson.skills) for lesson in course.lessons)

    def _generate_reason_text(
        self,
        reasons: list[RecommendationReason],
        course: Course,
        profile: FarmerProfile,
    ) -> BilingualText:
        """Generate human-readable reason text"""
        if not reasons:
            return BilingualText(
                en="Recommended for you",
                ar="موصى به لك",
            )

        primary = reasons[0]

        reason_templates = {
            RecommendationReason.SKILL_GAP: BilingualText(
                en=f"Build your {course.category.value.replace('_', ' ')} skills",
                ar=f"طور مهاراتك في {course.category.value}",
            ),
            RecommendationReason.NEXT_LEVEL: BilingualText(
                en="Perfect for your current level",
                ar="مثالي لمستواك الحالي",
            ),
            RecommendationReason.POPULAR: BilingualText(
                en="Popular among farmers like you",
                ar="شائع بين المزارعين مثلك",
            ),
            RecommendationReason.TRENDING: BilingualText(
                en="Trending this month",
                ar="رائج هذا الشهر",
            ),
            RecommendationReason.CROP_RELEVANT: BilingualText(
                en="Relevant to your crops",
                ar="متعلق بمحاصيلك",
            ),
            RecommendationReason.SEASONAL: BilingualText(
                en="Perfect timing for this season",
                ar="توقيت مثالي لهذا الموسم",
            ),
            RecommendationReason.BEGINNER_FRIENDLY: BilingualText(
                en="Great for getting started",
                ar="رائع للبدء",
            ),
            RecommendationReason.CERTIFICATION_PATH: BilingualText(
                en="Part of certification path",
                ar="جزء من مسار الشهادة",
            ),
            RecommendationReason.CONTINUATION: BilingualText(
                en="Continue your learning journey",
                ar="واصل رحلة تعلمك",
            ),
        }

        return reason_templates.get(
            primary,
            BilingualText(
                en="Recommended for you",
                ar="موصى به لك",
            ),
        )

    async def get_next_course(
        self,
        profile: FarmerProfile,
        courses: list[Course],
    ) -> CourseRecommendation | None:
        """
        Get the single best next course
        الحصول على أفضل دورة تالية

        Args:
            profile: Farmer profile
            courses: Available courses

        Returns:
            Best CourseRecommendation or None
        """
        recommendations = await self.get_recommendations(profile, courses, limit=1)
        return recommendations[0] if recommendations else None

    async def suggest_learning_path(
        self,
        profile: FarmerProfile,
        target_skill: SkillCategory,
        courses: list[Course],
        target_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE,
    ) -> LearningPath:
        """
        Suggest a learning path for a skill
        اقتراح مسار تعلم لمهارة

        Args:
            profile: Farmer profile
            target_skill: Skill to develop
            courses: Available courses
            target_level: Target skill level

        Returns:
            LearningPath with recommended courses
        """
        # Filter courses for this skill
        skill_courses = [
            c
            for c in courses
            if c.status == CourseStatus.PUBLISHED
            and (c.category == target_skill or any(target_skill in lesson.skills for lesson in c.lessons))
        ]

        # Sort by difficulty
        level_order = {
            DifficultyLevel.BEGINNER: 1,
            DifficultyLevel.INTERMEDIATE: 2,
            DifficultyLevel.ADVANCED: 3,
            DifficultyLevel.EXPERT: 4,
        }

        skill_courses.sort(key=lambda c: level_order[c.difficulty])

        # Build path up to target level
        path_courses: list[Course] = []
        current_level = profile.get_skill(target_skill)
        start_level = current_level.level if current_level else DifficultyLevel.BEGINNER

        for course in skill_courses:
            if level_order[course.difficulty] > level_order[target_level]:
                break

            if level_order[course.difficulty] >= level_order[start_level]:
                path_courses.append(course)

        # Calculate total duration
        total_duration = sum(c.estimated_duration_minutes for c in path_courses)

        # Skill name translations
        skill_names_ar = {
            SkillCategory.IRRIGATION: "الري",
            SkillCategory.FERTILIZATION: "التسميد",
            SkillCategory.PEST_MANAGEMENT: "إدارة الآفات",
            SkillCategory.CROP_MANAGEMENT: "إدارة المحاصيل",
            SkillCategory.SOIL_HEALTH: "صحة التربة",
            SkillCategory.HARVESTING: "الحصاد",
            SkillCategory.POST_HARVEST: "ما بعد الحصاد",
            SkillCategory.FARM_PLANNING: "تخطيط المزرعة",
            SkillCategory.TECHNOLOGY: "التقنية",
            SkillCategory.BUSINESS: "الأعمال",
            SkillCategory.SUSTAINABILITY: "الاستدامة",
            SkillCategory.SAFETY: "السلامة",
            SkillCategory.GLOBALGAP: "GlobalGAP",
        }

        return LearningPath(
            name=BilingualText(
                en=f"{target_skill.value.replace('_', ' ').title()} Mastery Path",
                ar=f"مسار إتقان {skill_names_ar.get(target_skill, target_skill.value)}",
            ),
            description=BilingualText(
                en=f"Complete path to reach {target_level.value} level in {target_skill.value.replace('_', ' ')}",
                ar=f"مسار كامل للوصول إلى مستوى {target_level.value} في {skill_names_ar.get(target_skill, target_skill.value)}",
            ),
            target_skill=target_skill,
            target_level=target_level,
            course_ids=[c.id for c in path_courses],
            courses=path_courses,
            total_duration_minutes=total_duration,
        )

    async def get_similar_courses(
        self,
        course: Course,
        courses: list[Course],
        limit: int = 5,
    ) -> list[Course]:
        """
        Get similar courses
        الحصول على دورات مشابهة

        Args:
            course: Reference course
            courses: Available courses
            limit: Maximum results

        Returns:
            List of similar courses
        """
        similar: list[tuple[Course, float]] = []

        for c in courses:
            if c.id == course.id or c.status != CourseStatus.PUBLISHED:
                continue

            score = 0.0

            # Same category
            if c.category == course.category:
                score += 40

            # Overlapping tags
            common_tags = set(c.tags) & set(course.tags)
            score += len(common_tags) * 10

            # Same difficulty
            if c.difficulty == course.difficulty:
                score += 20

            # Same expert
            common_experts = set(c.expert_ids) & set(course.expert_ids)
            score += len(common_experts) * 15

            if score > 0:
                similar.append((c, score))

        # Sort by score
        similar.sort(key=lambda x: x[1], reverse=True)

        return [c for c, _ in similar[:limit]]

    async def get_seasonal_recommendations(
        self,
        profile: FarmerProfile,
        courses: list[Course],
        limit: int = 5,
    ) -> list[CourseRecommendation]:
        """
        Get seasonally relevant recommendations
        الحصول على توصيات موسمية

        Args:
            profile: Farmer profile
            courses: Available courses
            limit: Maximum results

        Returns:
            List of seasonal CourseRecommendation
        """
        current_month = datetime.now(UTC).month
        seasonal_skills = set(SEASONAL_TOPICS.get(current_month, []))

        # Filter for seasonal courses
        seasonal_courses = [
            c
            for c in courses
            if c.status == CourseStatus.PUBLISHED
            and (
                c.category in seasonal_skills
                or any(skill in seasonal_skills for lesson in c.lessons for skill in lesson.skills)
            )
        ]

        # Get recommendations from seasonal courses
        recommendations = await self.get_recommendations(profile, seasonal_courses, limit)

        # Ensure seasonal reason is included
        for rec in recommendations:
            if RecommendationReason.SEASONAL not in rec.reasons:
                rec.reasons.insert(0, RecommendationReason.SEASONAL)

        return recommendations

    async def get_quick_wins(
        self,
        profile: FarmerProfile,
        courses: list[Course],
        max_duration_minutes: int = 30,
        limit: int = 5,
    ) -> list[CourseRecommendation]:
        """
        Get quick, easy courses for motivation
        الحصول على دورات سريعة وسهلة للتحفيز

        Args:
            profile: Farmer profile
            courses: Available courses
            max_duration_minutes: Maximum course duration
            limit: Maximum results

        Returns:
            List of quick CourseRecommendation
        """
        # Filter short courses
        quick_courses = [
            c
            for c in courses
            if c.status == CourseStatus.PUBLISHED and c.estimated_duration_minutes <= max_duration_minutes
        ]

        return await self.get_recommendations(profile, quick_courses, limit)


# Convenience functions
_recommenders: dict[str, ContentRecommender] = {}


def get_content_recommender(
    tenant_id: str,
    progress_tracker: ProgressTracker | None = None,
) -> ContentRecommender:
    """Get or create a content recommender for a tenant"""
    if tenant_id not in _recommenders:
        _recommenders[tenant_id] = ContentRecommender(tenant_id, progress_tracker)
    return _recommenders[tenant_id]


async def get_recommendations(
    tenant_id: str,
    profile: FarmerProfile,
    courses: list[Course],
    limit: int = 10,
) -> list[CourseRecommendation]:
    """Get course recommendations for a farmer"""
    recommender = get_content_recommender(tenant_id)
    return await recommender.get_recommendations(profile, courses, limit)


async def get_learning_path(
    tenant_id: str,
    profile: FarmerProfile,
    target_skill: SkillCategory,
    courses: list[Course],
) -> LearningPath:
    """Get a learning path for a skill"""
    recommender = get_content_recommender(tenant_id)
    return await recommender.suggest_learning_path(profile, target_skill, courses)
