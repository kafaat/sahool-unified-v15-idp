"""
Learning Marketplace Module
===========================
وحدة سوق التعلم التعليمي

Educational content marketplace for the SAHOOL agricultural platform.
Provides comprehensive learning management including:
- Course and content management
- Farmer skill tracking
- Certification management
- Expert content creation
- Progress tracking
- Personalized recommendations

Features:
- Multi-content types: Video, PDF, interactive, quiz
- Bilingual support: Arabic and English
- Offline-first architecture compatible
- Gamification: XP, streaks, achievements
- Certification paths and credentialing

Usage:
    from shared.learning_marketplace import (
        # Models
        Course,
        Lesson,
        Certification,
        FarmerProfile,
        FarmerSkill,
        Quiz,

        # Progress tracking
        ProgressTracker,
        CourseEnrollment,
        LessonProgress,
        QuizAttempt,
        get_progress_tracker,
        enroll_course,
        complete_lesson,
        submit_quiz,

        # Recommendations
        ContentRecommender,
        CourseRecommendation,
        LearningPath,
        get_recommendations,
        get_learning_path,
    )

    # Create a course
    course = Course(
        title=BilingualText(
            en="Irrigation Management",
            ar="إدارة الري"
        ),
        category=SkillCategory.IRRIGATION,
        difficulty=DifficultyLevel.BEGINNER,
    )

    # Track progress
    tracker = get_progress_tracker("tenant_001")
    enrollment = await tracker.enroll_course("farmer_001", course)

    # Get recommendations
    recommendations = await get_recommendations(
        "tenant_001",
        farmer_profile,
        courses_catalog,
        limit=10
    )

Author: SAHOOL Platform Team
Updated: January 2026
"""

# Models
from .models import (
    # Data classes
    BilingualText,
    Certification,
    CertificationType,
    ContentLanguage,
    ContentResource,
    # Enums
    ContentType,
    Course,
    CourseModule,
    CourseStatus,
    DifficultyLevel,
    EnrollmentStatus,
    Expert,
    FarmerCertification,
    FarmerProfile,
    FarmerSkill,
    Lesson,
    Quiz,
    QuizQuestion,
    QuizQuestionType,
    SkillCategory,
)

# Progress tracking
from .progress import (
    # XP rewards
    XP_REWARDS,
    CourseEnrollment,
    # Data classes
    LessonProgress,
    ProgressEvent,
    # Enums
    ProgressEventType,
    # Storage
    ProgressStorage,
    # Tracker
    ProgressTracker,
    QuizAttempt,
    complete_lesson,
    enroll_course,
    get_progress_summary,
    # Convenience functions
    get_progress_tracker,
    submit_quiz,
)

# Recommendations
from .recommendations import (
    CROP_SKILL_MAPPING,
    # Constants
    SEASONAL_TOPICS,
    # Recommender
    ContentRecommender,
    CourseRecommendation,
    LearningPath,
    RecommendationPriority,
    # Enums
    RecommendationReason,
    # Data classes
    RecommendationScore,
    # Convenience functions
    get_content_recommender,
    get_learning_path,
    get_recommendations,
)

__version__ = "1.0.0"

__all__ = [
    # Version
    "__version__",
    # === Models ===
    # Enums
    "ContentType",
    "DifficultyLevel",
    "CourseStatus",
    "CertificationType",
    "SkillCategory",
    "ContentLanguage",
    "EnrollmentStatus",
    "QuizQuestionType",
    # Data classes
    "BilingualText",
    "ContentResource",
    "QuizQuestion",
    "Quiz",
    "Lesson",
    "CourseModule",
    "Expert",
    "Course",
    "Certification",
    "FarmerCertification",
    "FarmerSkill",
    "FarmerProfile",
    # === Progress Tracking ===
    # Enums
    "ProgressEventType",
    # Data classes
    "LessonProgress",
    "QuizAttempt",
    "CourseEnrollment",
    "ProgressEvent",
    # Storage
    "ProgressStorage",
    # Tracker
    "ProgressTracker",
    # XP rewards
    "XP_REWARDS",
    # Convenience functions
    "get_progress_tracker",
    "enroll_course",
    "complete_lesson",
    "submit_quiz",
    "get_progress_summary",
    # === Recommendations ===
    # Enums
    "RecommendationReason",
    "RecommendationPriority",
    # Data classes
    "RecommendationScore",
    "CourseRecommendation",
    "LearningPath",
    # Constants
    "SEASONAL_TOPICS",
    "CROP_SKILL_MAPPING",
    # Recommender
    "ContentRecommender",
    # Convenience functions
    "get_content_recommender",
    "get_recommendations",
    "get_learning_path",
]
