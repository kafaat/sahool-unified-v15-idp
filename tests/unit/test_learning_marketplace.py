"""
Unit Tests for Learning Marketplace Module
==========================================
Tests for courses, progress tracking, quiz scoring, certifications, and recommendations

Author: SAHOOL Platform Team
Updated: January 2026
"""

import uuid
from datetime import datetime, timedelta, UTC
from unittest.mock import AsyncMock, MagicMock, patch
import tempfile
import os

import pytest

from shared.learning_marketplace.models import (
    BilingualText,
    Certification,
    CertificationType,
    ContentLanguage,
    ContentResource,
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
from shared.learning_marketplace.progress import (
    CourseEnrollment,
    LessonProgress,
    ProgressEvent,
    ProgressEventType,
    ProgressStorage,
    ProgressTracker,
    QuizAttempt,
    XP_REWARDS,
    get_progress_tracker,
)
from shared.learning_marketplace.recommendations import (
    ContentRecommender,
    CourseRecommendation,
    LearningPath,
    RecommendationPriority,
    RecommendationReason,
    RecommendationScore,
    CROP_SKILL_MAPPING,
    SEASONAL_TOPICS,
    get_content_recommender,
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def bilingual_text():
    """Create a sample bilingual text"""
    return BilingualText(en="Irrigation Basics", ar="أساسيات الري")


@pytest.fixture
def sample_quiz_question():
    """Create a sample quiz question"""
    return QuizQuestion(
        id="q1",
        question_type=QuizQuestionType.MULTIPLE_CHOICE,
        question=BilingualText(en="How often should wheat be irrigated?", ar="كم مرة يجب ري القمح؟"),
        options=[
            BilingualText(en="Every day", ar="كل يوم"),
            BilingualText(en="Every 7-10 days", ar="كل 7-10 أيام"),
            BilingualText(en="Every month", ar="كل شهر"),
        ],
        correct_answer=1,
        points=10,
        explanation=BilingualText(
            en="Wheat typically needs irrigation every 7-10 days",
            ar="يحتاج القمح عادة للري كل 7-10 أيام",
        ),
    )


@pytest.fixture
def sample_quiz(sample_quiz_question):
    """Create a sample quiz"""
    return Quiz(
        id="quiz1",
        title=BilingualText(en="Irrigation Quiz", ar="اختبار الري"),
        description=BilingualText(en="Test your knowledge", ar="اختبر معلوماتك"),
        questions=[sample_quiz_question],
        passing_score=70,
        attempts_allowed=3,
    )


@pytest.fixture
def sample_content_resource():
    """Create a sample content resource"""
    return ContentResource(
        id="res1",
        content_type=ContentType.VIDEO,
        url="https://example.com/video.mp4",
        title=BilingualText(en="Irrigation Video", ar="فيديو الري"),
        duration_minutes=15,
        offline_available=True,
    )


@pytest.fixture
def sample_lesson(sample_content_resource, sample_quiz):
    """Create a sample lesson"""
    return Lesson(
        id="lesson1",
        course_id="course1",
        title=BilingualText(en="Introduction to Irrigation", ar="مقدمة في الري"),
        description=BilingualText(en="Learn the basics", ar="تعلم الأساسيات"),
        primary_content=sample_content_resource,
        quiz=sample_quiz,
        estimated_duration_minutes=30,
        skills=[SkillCategory.IRRIGATION],
        status=CourseStatus.PUBLISHED,
    )


@pytest.fixture
def sample_course(sample_lesson):
    """Create a sample course"""
    return Course(
        id="course1",
        title=BilingualText(en="Irrigation Fundamentals", ar="أساسيات الري"),
        description=BilingualText(en="Complete irrigation guide", ar="دليل الري الكامل"),
        category=SkillCategory.IRRIGATION,
        difficulty=DifficultyLevel.BEGINNER,
        language=ContentLanguage.BILINGUAL,
        lessons=[sample_lesson],
        status=CourseStatus.PUBLISHED,
        total_enrollments=100,
        average_rating=4.5,
        rating_count=50,
        offers_certificate=True,
    )


@pytest.fixture
def sample_farmer_profile():
    """Create a sample farmer profile"""
    return FarmerProfile(
        id="profile1",
        farmer_id="farmer1",
        tenant_id="tenant1",
        preferred_language=ContentLanguage.ARABIC,
        preferred_content_types=[ContentType.VIDEO],
        crop_types=["wheat", "barley"],
        farming_experience_years=5,
        skills=[
            FarmerSkill(
                farmer_id="farmer1",
                category=SkillCategory.IRRIGATION,
                level=DifficultyLevel.BEGINNER,
                experience_points=200,
            )
        ],
        total_courses_enrolled=2,
        total_courses_completed=1,
        weekly_learning_goal_minutes=60,
    )


@pytest.fixture
def sample_certification():
    """Create a sample certification"""
    return Certification(
        id="cert1",
        name=BilingualText(en="Irrigation Expert", ar="خبير الري"),
        description=BilingualText(en="Certified irrigation expert", ar="خبير ري معتمد"),
        certification_type=CertificationType.COMPETENCY,
        required_course_ids=["course1"],
        required_skills=[SkillCategory.IRRIGATION],
        minimum_score=70,
        validity_days=365,
    )


@pytest.fixture
def temp_storage_path():
    """Create a temporary storage path for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


# =============================================================================
# BilingualText Tests
# =============================================================================


@pytest.mark.unit
class TestBilingualText:
    """Test BilingualText model"""

    def test_bilingual_text_creation(self, bilingual_text):
        """Test creating bilingual text"""
        assert bilingual_text.en == "Irrigation Basics"
        assert bilingual_text.ar == "أساسيات الري"

    def test_get_english(self, bilingual_text):
        """Test getting English text"""
        assert bilingual_text.get("en") == "Irrigation Basics"

    def test_get_arabic(self, bilingual_text):
        """Test getting Arabic text"""
        assert bilingual_text.get("ar") == "أساسيات الري"

    def test_get_default_language(self, bilingual_text):
        """Test default language is English"""
        assert bilingual_text.get() == "Irrigation Basics"

    def test_to_dict(self, bilingual_text):
        """Test conversion to dictionary"""
        result = bilingual_text.to_dict()
        assert result == {"en": "Irrigation Basics", "ar": "أساسيات الري"}

    def test_from_dict(self):
        """Test creation from dictionary"""
        data = {"en": "Test", "ar": "اختبار"}
        text = BilingualText.from_dict(data)
        assert text.en == "Test"
        assert text.ar == "اختبار"

    def test_from_dict_string(self):
        """Test creation from string (fallback)"""
        text = BilingualText.from_dict("Simple text")
        assert text.en == "Simple text"
        assert text.ar == "Simple text"

    def test_empty_bilingual_text(self):
        """Test empty bilingual text"""
        text = BilingualText()
        assert text.en == ""
        assert text.ar == ""


# =============================================================================
# Course and Module Creation Tests
# =============================================================================


@pytest.mark.unit
class TestCourseCreation:
    """Test Course model creation and properties"""

    def test_course_creation(self, sample_course):
        """Test creating a course"""
        assert sample_course.id == "course1"
        assert sample_course.title.en == "Irrigation Fundamentals"
        assert sample_course.category == SkillCategory.IRRIGATION
        assert sample_course.difficulty == DifficultyLevel.BEGINNER

    def test_course_lesson_count(self, sample_course):
        """Test course lesson count property"""
        assert sample_course.lesson_count == 1

    def test_course_completion_rate(self, sample_course):
        """Test course completion rate calculation"""
        sample_course.total_completions = 50
        assert sample_course.completion_rate == 50.0

    def test_course_completion_rate_zero_enrollments(self):
        """Test completion rate with zero enrollments"""
        course = Course(total_enrollments=0)
        assert course.completion_rate == 0.0

    def test_course_auto_duration_calculation(self):
        """Test automatic duration calculation from lessons"""
        lessons = [
            Lesson(estimated_duration_minutes=30),
            Lesson(estimated_duration_minutes=45),
        ]
        course = Course(lessons=lessons)
        assert course.estimated_duration_minutes == 75

    def test_course_to_dict(self, sample_course):
        """Test course serialization"""
        result = sample_course.to_dict()
        assert result["id"] == "course1"
        assert result["title"]["en"] == "Irrigation Fundamentals"
        assert result["category"] == "irrigation"
        assert result["difficulty"] == "beginner"

    def test_course_from_dict(self):
        """Test course deserialization"""
        data = {
            "id": "course2",
            "title": {"en": "Test Course", "ar": "دورة اختبار"},
            "category": "irrigation",
            "difficulty": "intermediate",
            "status": "published",
        }
        course = Course.from_dict(data)
        assert course.id == "course2"
        assert course.category == SkillCategory.IRRIGATION
        assert course.difficulty == DifficultyLevel.INTERMEDIATE


@pytest.mark.unit
class TestCourseModuleCreation:
    """Test CourseModule model"""

    def test_module_creation(self):
        """Test creating a course module"""
        module = CourseModule(
            id="mod1",
            course_id="course1",
            title=BilingualText(en="Module 1", ar="الوحدة 1"),
            lesson_ids=["lesson1", "lesson2"],
            order=1,
        )
        assert module.id == "mod1"
        assert len(module.lesson_ids) == 2

    def test_module_to_dict(self):
        """Test module serialization"""
        module = CourseModule(
            id="mod1",
            title=BilingualText(en="Module 1", ar="الوحدة 1"),
        )
        result = module.to_dict()
        assert result["id"] == "mod1"
        assert result["title"]["en"] == "Module 1"


@pytest.mark.unit
class TestLessonCreation:
    """Test Lesson model"""

    def test_lesson_creation(self, sample_lesson):
        """Test creating a lesson"""
        assert sample_lesson.id == "lesson1"
        assert sample_lesson.course_id == "course1"
        assert sample_lesson.estimated_duration_minutes == 30

    def test_lesson_with_prerequisites(self):
        """Test lesson with prerequisites"""
        lesson = Lesson(
            id="lesson2",
            prerequisite_lesson_ids=["lesson1"],
        )
        assert "lesson1" in lesson.prerequisite_lesson_ids

    def test_lesson_preview_flag(self):
        """Test lesson preview flag"""
        lesson = Lesson(is_preview=True)
        assert lesson.is_preview is True

    def test_lesson_mandatory_flag(self):
        """Test lesson mandatory flag"""
        lesson = Lesson(is_mandatory=False)
        assert lesson.is_mandatory is False


# =============================================================================
# Quiz Scoring Tests
# =============================================================================


@pytest.mark.unit
class TestQuizCreation:
    """Test Quiz and QuizQuestion models"""

    def test_quiz_creation(self, sample_quiz):
        """Test creating a quiz"""
        assert sample_quiz.id == "quiz1"
        assert sample_quiz.passing_score == 70
        assert sample_quiz.attempts_allowed == 3

    def test_quiz_total_points_calculation(self, sample_quiz):
        """Test quiz total points calculation"""
        assert sample_quiz.total_points == 10  # One question with 10 points

    def test_quiz_multiple_questions(self):
        """Test quiz with multiple questions"""
        questions = [
            QuizQuestion(points=10),
            QuizQuestion(points=20),
            QuizQuestion(points=15),
        ]
        quiz = Quiz(questions=questions)
        assert quiz.total_points == 45

    def test_quiz_question_types(self):
        """Test different quiz question types"""
        mc_question = QuizQuestion(question_type=QuizQuestionType.MULTIPLE_CHOICE)
        tf_question = QuizQuestion(question_type=QuizQuestionType.TRUE_FALSE)
        fb_question = QuizQuestion(question_type=QuizQuestionType.FILL_BLANK)

        assert mc_question.question_type == QuizQuestionType.MULTIPLE_CHOICE
        assert tf_question.question_type == QuizQuestionType.TRUE_FALSE
        assert fb_question.question_type == QuizQuestionType.FILL_BLANK


@pytest.mark.unit
class TestQuizAttempt:
    """Test QuizAttempt model"""

    def test_quiz_attempt_creation(self):
        """Test creating a quiz attempt"""
        attempt = QuizAttempt(
            farmer_id="farmer1",
            quiz_id="quiz1",
            attempt_number=1,
            max_score=100,
        )
        assert attempt.farmer_id == "farmer1"
        assert attempt.attempt_number == 1

    def test_quiz_attempt_scoring(self):
        """Test quiz attempt scoring"""
        attempt = QuizAttempt(
            score=75,
            max_score=100,
            percentage=75.0,
            passed=True,
            correct_count=3,
            incorrect_count=1,
        )
        assert attempt.score == 75
        assert attempt.percentage == 75.0
        assert attempt.passed is True

    def test_quiz_attempt_to_dict(self):
        """Test quiz attempt serialization"""
        attempt = QuizAttempt(
            farmer_id="farmer1",
            score=80,
            passed=True,
        )
        result = attempt.to_dict()
        assert result["farmer_id"] == "farmer1"
        assert result["score"] == 80
        assert result["passed"] is True


# =============================================================================
# Progress Tracking Tests
# =============================================================================


@pytest.mark.unit
class TestLessonProgress:
    """Test LessonProgress model"""

    def test_lesson_progress_creation(self):
        """Test creating lesson progress"""
        progress = LessonProgress(
            farmer_id="farmer1",
            lesson_id="lesson1",
            course_id="course1",
        )
        assert progress.farmer_id == "farmer1"
        assert progress.is_completed is False

    def test_lesson_progress_completion(self):
        """Test marking lesson as completed"""
        progress = LessonProgress(
            is_completed=True,
            completed_at=datetime.now(UTC),
            time_spent_minutes=30,
        )
        assert progress.is_completed is True
        assert progress.completion_percentage == 100.0

    def test_lesson_progress_with_notes(self):
        """Test lesson progress with notes"""
        progress = LessonProgress(
            notes="Important points about irrigation timing",
        )
        assert progress.notes is not None


@pytest.mark.unit
class TestCourseEnrollment:
    """Test CourseEnrollment model"""

    def test_enrollment_creation(self):
        """Test creating course enrollment"""
        enrollment = CourseEnrollment(
            farmer_id="farmer1",
            course_id="course1",
            total_lessons=5,
            total_quizzes=2,
        )
        assert enrollment.status == EnrollmentStatus.ENROLLED
        assert enrollment.total_lessons == 5

    def test_enrollment_progress_percentage(self):
        """Test enrollment progress calculation"""
        enrollment = CourseEnrollment(
            lessons_completed=3,
            total_lessons=10,
        )
        assert enrollment.progress_percentage == 30.0

    def test_enrollment_progress_zero_lessons(self):
        """Test progress with zero lessons"""
        enrollment = CourseEnrollment(total_lessons=0)
        assert enrollment.progress_percentage == 0.0

    def test_enrollment_is_completed(self):
        """Test enrollment completion status"""
        enrollment = CourseEnrollment(status=EnrollmentStatus.COMPLETED)
        assert enrollment.is_completed is True

    def test_get_lesson_progress(self):
        """Test getting lesson progress from enrollment"""
        progress = LessonProgress(lesson_id="lesson1")
        enrollment = CourseEnrollment(
            lesson_progress=[progress],
        )
        result = enrollment.get_lesson_progress("lesson1")
        assert result is not None
        assert result.lesson_id == "lesson1"

    def test_get_lesson_progress_not_found(self):
        """Test getting non-existent lesson progress"""
        enrollment = CourseEnrollment()
        result = enrollment.get_lesson_progress("nonexistent")
        assert result is None


@pytest.mark.unit
class TestProgressEvent:
    """Test ProgressEvent model"""

    def test_progress_event_creation(self):
        """Test creating progress event"""
        event = ProgressEvent(
            farmer_id="farmer1",
            tenant_id="tenant1",
            event_type=ProgressEventType.LESSON_COMPLETED,
            xp_earned=25,
        )
        assert event.event_type == ProgressEventType.LESSON_COMPLETED
        assert event.xp_earned == 25

    def test_progress_event_with_context(self):
        """Test progress event with full context"""
        event = ProgressEvent(
            farmer_id="farmer1",
            event_type=ProgressEventType.QUIZ_COMPLETED,
            course_id="course1",
            lesson_id="lesson1",
            quiz_id="quiz1",
            data={"score": 85, "passed": True},
        )
        assert event.course_id == "course1"
        assert event.data["score"] == 85


# =============================================================================
# Progress Tracker Tests
# =============================================================================


@pytest.mark.unit
class TestProgressTracker:
    """Test ProgressTracker class"""

    @pytest.fixture
    def tracker(self, temp_storage_path):
        """Create a progress tracker with temp storage"""
        storage = ProgressStorage(temp_storage_path)
        return ProgressTracker(
            tenant_id="tenant1",
            storage=storage,
        )

    @pytest.mark.asyncio
    async def test_get_or_create_profile(self, tracker):
        """Test getting or creating farmer profile"""
        profile = await tracker.get_or_create_profile("farmer1")
        assert profile.farmer_id == "farmer1"
        assert profile.tenant_id == "tenant1"

    @pytest.mark.asyncio
    async def test_enroll_course(self, tracker, sample_course):
        """Test enrolling in a course"""
        enrollment = await tracker.enroll_course("farmer1", sample_course)
        assert enrollment.farmer_id == "farmer1"
        assert enrollment.course_id == "course1"
        assert enrollment.status == EnrollmentStatus.ENROLLED
        assert enrollment.total_lessons == 1

    @pytest.mark.asyncio
    async def test_enroll_course_already_enrolled(self, tracker, sample_course):
        """Test re-enrolling returns existing enrollment"""
        enrollment1 = await tracker.enroll_course("farmer1", sample_course)
        enrollment2 = await tracker.enroll_course("farmer1", sample_course)
        assert enrollment1.id == enrollment2.id

    @pytest.mark.asyncio
    async def test_start_lesson(self, tracker, sample_course, sample_lesson):
        """Test starting a lesson"""
        await tracker.enroll_course("farmer1", sample_course)
        progress = await tracker.start_lesson("farmer1", sample_lesson)
        assert progress.lesson_id == "lesson1"
        assert progress.started_at is not None

    @pytest.mark.asyncio
    async def test_start_lesson_not_enrolled(self, tracker, sample_lesson):
        """Test starting lesson without enrollment raises error"""
        with pytest.raises(ValueError, match="not enrolled"):
            await tracker.start_lesson("farmer1", sample_lesson)

    @pytest.mark.asyncio
    async def test_complete_lesson(self, tracker, sample_course, sample_lesson):
        """Test completing a lesson"""
        await tracker.enroll_course("farmer1", sample_course)
        progress = await tracker.complete_lesson("farmer1", sample_lesson, time_spent_minutes=25)

        assert progress.is_completed is True
        assert progress.completed_at is not None
        assert progress.time_spent_minutes == 25

    @pytest.mark.asyncio
    async def test_complete_lesson_awards_xp(self, tracker, sample_course, sample_lesson):
        """Test completing lesson awards XP"""
        await tracker.enroll_course("farmer1", sample_course)
        await tracker.complete_lesson("farmer1", sample_lesson)

        profile = await tracker.get_or_create_profile("farmer1")
        assert profile.total_xp >= XP_REWARDS["lesson_completed"]

    @pytest.mark.asyncio
    async def test_complete_lesson_already_completed(self, tracker, sample_course, sample_lesson):
        """Test completing already completed lesson returns same progress"""
        await tracker.enroll_course("farmer1", sample_course)
        progress1 = await tracker.complete_lesson("farmer1", sample_lesson)
        progress2 = await tracker.complete_lesson("farmer1", sample_lesson)
        assert progress1.is_completed
        assert progress2.is_completed

    @pytest.mark.asyncio
    async def test_start_quiz(self, tracker, sample_course, sample_lesson):
        """Test starting a quiz"""
        await tracker.enroll_course("farmer1", sample_course)
        attempt = await tracker.start_quiz("farmer1", sample_lesson)

        assert attempt.quiz_id == "quiz1"
        assert attempt.attempt_number == 1

    @pytest.mark.asyncio
    async def test_start_quiz_no_quiz(self, tracker, sample_course):
        """Test starting quiz for lesson without quiz"""
        await tracker.enroll_course("farmer1", sample_course)
        lesson_no_quiz = Lesson(
            id="lesson2",
            course_id="course1",
            quiz=None,
        )
        with pytest.raises(ValueError, match="does not have a quiz"):
            await tracker.start_quiz("farmer1", lesson_no_quiz)

    @pytest.mark.asyncio
    async def test_submit_quiz_passing(self, tracker, sample_course, sample_lesson):
        """Test submitting quiz with passing score"""
        await tracker.enroll_course("farmer1", sample_course)

        # Answer correctly (question has correct_answer=1)
        answers = {"q1": 1}
        result = await tracker.submit_quiz("farmer1", sample_lesson, answers)

        assert result.passed is True
        assert result.score == 10
        assert result.percentage == 100.0

    @pytest.mark.asyncio
    async def test_submit_quiz_failing(self, tracker, sample_course, sample_lesson):
        """Test submitting quiz with failing score"""
        await tracker.enroll_course("farmer1", sample_course)

        # Answer incorrectly
        answers = {"q1": 0}
        result = await tracker.submit_quiz("farmer1", sample_lesson, answers)

        assert result.passed is False
        assert result.score == 0

    @pytest.mark.asyncio
    async def test_quiz_max_attempts(self, tracker, sample_course, sample_lesson):
        """Test quiz maximum attempts limit"""
        await tracker.enroll_course("farmer1", sample_course)

        # Use all 3 attempts
        for _ in range(3):
            await tracker.submit_quiz("farmer1", sample_lesson, {"q1": 0})

        # 4th attempt should fail
        with pytest.raises(ValueError, match="Maximum quiz attempts"):
            await tracker.start_quiz("farmer1", sample_lesson)


@pytest.mark.unit
class TestProgressTrackerSkills:
    """Test skill progression in ProgressTracker"""

    @pytest.fixture
    def tracker(self, temp_storage_path):
        """Create a progress tracker with temp storage"""
        storage = ProgressStorage(temp_storage_path)
        return ProgressTracker(tenant_id="tenant1", storage=storage)

    def test_calculate_skill_level_beginner(self, tracker):
        """Test skill level calculation for beginner"""
        level = tracker._calculate_skill_level(100)
        assert level == DifficultyLevel.BEGINNER

    def test_calculate_skill_level_intermediate(self, tracker):
        """Test skill level calculation for intermediate"""
        level = tracker._calculate_skill_level(500)
        assert level == DifficultyLevel.INTERMEDIATE

    def test_calculate_skill_level_advanced(self, tracker):
        """Test skill level calculation for advanced"""
        level = tracker._calculate_skill_level(1500)
        assert level == DifficultyLevel.ADVANCED

    def test_calculate_skill_level_expert(self, tracker):
        """Test skill level calculation for expert"""
        level = tracker._calculate_skill_level(3500)
        assert level == DifficultyLevel.EXPERT


# =============================================================================
# Certificate Generation Tests
# =============================================================================


@pytest.mark.unit
class TestCertification:
    """Test Certification model"""

    def test_certification_creation(self, sample_certification):
        """Test creating certification"""
        assert sample_certification.name.en == "Irrigation Expert"
        assert sample_certification.minimum_score == 70
        assert sample_certification.validity_days == 365

    def test_certification_lifetime_validity(self):
        """Test certification with lifetime validity"""
        cert = Certification(validity_days=None)
        assert cert.validity_days is None


@pytest.mark.unit
class TestFarmerCertification:
    """Test FarmerCertification model"""

    def test_farmer_certification_creation(self):
        """Test creating farmer certification"""
        cert = FarmerCertification(
            farmer_id="farmer1",
            certification_id="cert1",
            score=85,
        )
        assert cert.farmer_id == "farmer1"
        assert cert.score == 85
        assert cert.is_valid is True

    def test_farmer_certification_auto_number(self):
        """Test automatic certificate number generation"""
        cert = FarmerCertification()
        assert cert.certificate_number.startswith("SAHOOL-CERT-")

    def test_farmer_certification_is_expired(self):
        """Test certification expiration check"""
        past = datetime.now(UTC) - timedelta(days=1)
        cert = FarmerCertification(expires_at=past)
        assert cert.is_expired is True

    def test_farmer_certification_not_expired(self):
        """Test certification not expired"""
        future = datetime.now(UTC) + timedelta(days=30)
        cert = FarmerCertification(expires_at=future)
        assert cert.is_expired is False

    def test_farmer_certification_no_expiry(self):
        """Test certification with no expiry"""
        cert = FarmerCertification(expires_at=None)
        assert cert.is_expired is False


@pytest.mark.unit
class TestCertificationEligibility:
    """Test certification eligibility checking"""

    @pytest.fixture
    def tracker(self, temp_storage_path):
        """Create a progress tracker with temp storage"""
        storage = ProgressStorage(temp_storage_path)
        return ProgressTracker(tenant_id="tenant1", storage=storage)

    @pytest.mark.asyncio
    async def test_check_eligibility_missing_course(self, tracker, sample_certification):
        """Test eligibility check with missing required course"""
        is_eligible, missing = await tracker.check_certification_eligibility("farmer1", sample_certification)
        assert is_eligible is False
        assert any("Complete course" in m for m in missing)

    @pytest.mark.asyncio
    async def test_award_certification(self, tracker, sample_certification):
        """Test awarding certification"""
        farmer_cert = await tracker.award_certification("farmer1", sample_certification, score=85)

        assert farmer_cert.farmer_id == "farmer1"
        assert farmer_cert.certification_id == "cert1"
        assert farmer_cert.score == 85

    @pytest.mark.asyncio
    async def test_award_certification_sets_expiry(self, tracker, sample_certification):
        """Test certification expiry is set correctly"""
        farmer_cert = await tracker.award_certification("farmer1", sample_certification, score=80)

        assert farmer_cert.expires_at is not None
        # Should be about 365 days from now
        delta = farmer_cert.expires_at - datetime.now(UTC)
        assert 364 <= delta.days <= 365


# =============================================================================
# Skill Assessment Tests
# =============================================================================


@pytest.mark.unit
class TestFarmerSkill:
    """Test FarmerSkill model"""

    def test_farmer_skill_creation(self):
        """Test creating farmer skill"""
        skill = FarmerSkill(
            farmer_id="farmer1",
            category=SkillCategory.IRRIGATION,
            level=DifficultyLevel.INTERMEDIATE,
            experience_points=750,
        )
        assert skill.category == SkillCategory.IRRIGATION
        assert skill.level == DifficultyLevel.INTERMEDIATE

    def test_level_progress_beginner(self):
        """Test level progress calculation for beginner"""
        skill = FarmerSkill(
            level=DifficultyLevel.BEGINNER,
            experience_points=250,
        )
        # Progress from 0 to 500 XP, at 250 = 50%
        assert skill.level_progress == 50.0

    def test_level_progress_intermediate(self):
        """Test level progress calculation for intermediate"""
        skill = FarmerSkill(
            level=DifficultyLevel.INTERMEDIATE,
            experience_points=1000,
        )
        # Progress from 500 to 1500 XP, at 1000 = 50%
        assert skill.level_progress == 50.0

    def test_level_progress_expert_max(self):
        """Test level progress at max level"""
        skill = FarmerSkill(
            level=DifficultyLevel.EXPERT,
            experience_points=5000,
        )
        assert skill.level_progress == 100.0


@pytest.mark.unit
class TestFarmerProfile:
    """Test FarmerProfile model"""

    def test_farmer_profile_creation(self, sample_farmer_profile):
        """Test creating farmer profile"""
        assert sample_farmer_profile.farmer_id == "farmer1"
        assert sample_farmer_profile.preferred_language == ContentLanguage.ARABIC

    def test_overall_level_beginner(self):
        """Test overall level calculation - beginner"""
        profile = FarmerProfile(
            skills=[
                FarmerSkill(experience_points=100),
            ]
        )
        assert profile.overall_level == DifficultyLevel.BEGINNER

    def test_overall_level_intermediate(self):
        """Test overall level calculation - intermediate"""
        profile = FarmerProfile(
            skills=[
                FarmerSkill(experience_points=500),
                FarmerSkill(experience_points=600),
            ]
        )
        assert profile.overall_level == DifficultyLevel.INTERMEDIATE

    def test_overall_level_no_skills(self):
        """Test overall level with no skills"""
        profile = FarmerProfile()
        assert profile.overall_level == DifficultyLevel.BEGINNER

    def test_get_skill(self, sample_farmer_profile):
        """Test getting skill by category"""
        skill = sample_farmer_profile.get_skill(SkillCategory.IRRIGATION)
        assert skill is not None
        assert skill.category == SkillCategory.IRRIGATION

    def test_get_skill_not_found(self, sample_farmer_profile):
        """Test getting non-existent skill"""
        skill = sample_farmer_profile.get_skill(SkillCategory.HARVESTING)
        assert skill is None


# =============================================================================
# Content Recommendations Tests
# =============================================================================


@pytest.mark.unit
class TestRecommendationScore:
    """Test RecommendationScore model"""

    def test_score_creation(self):
        """Test creating recommendation score"""
        score = RecommendationScore(
            relevance_score=80,
            difficulty_match=90,
            skill_gap_score=70,
            popularity_score=60,
            freshness_score=80,
            completion_likelihood=75,
        )
        assert score.relevance_score == 80

    def test_total_score_calculation(self):
        """Test weighted total score calculation"""
        score = RecommendationScore(
            relevance_score=100,
            difficulty_match=100,
            skill_gap_score=100,
            popularity_score=100,
            freshness_score=100,
            completion_likelihood=100,
        )
        # All 100s should give total of 100
        assert score.total_score == 100.0

    def test_total_score_partial(self):
        """Test partial score calculation"""
        score = RecommendationScore(
            relevance_score=50,
            difficulty_match=50,
            skill_gap_score=50,
            popularity_score=50,
            freshness_score=50,
            completion_likelihood=50,
        )
        assert score.total_score == 50.0


@pytest.mark.unit
class TestContentRecommender:
    """Test ContentRecommender class"""

    @pytest.fixture
    def recommender(self):
        """Create a content recommender"""
        return ContentRecommender(tenant_id="tenant1")

    @pytest.fixture
    def course_catalog(self):
        """Create a catalog of courses"""
        return [
            Course(
                id=f"course{i}",
                title=BilingualText(en=f"Course {i}", ar=f"دورة {i}"),
                category=list(SkillCategory)[i % len(SkillCategory)],
                difficulty=list(DifficultyLevel)[i % 4],
                status=CourseStatus.PUBLISHED,
                language=ContentLanguage.BILINGUAL,
                total_enrollments=100 * (i + 1),
                average_rating=4.0 + (i * 0.1),
                rating_count=50,
                updated_at=datetime.now(UTC) - timedelta(days=i * 10),
            )
            for i in range(5)
        ]

    @pytest.mark.asyncio
    async def test_get_recommendations(self, recommender, sample_farmer_profile, course_catalog):
        """Test getting recommendations"""
        recommendations = await recommender.get_recommendations(
            sample_farmer_profile,
            course_catalog,
            limit=3,
        )

        assert len(recommendations) <= 3
        assert all(isinstance(r, CourseRecommendation) for r in recommendations)

    @pytest.mark.asyncio
    async def test_recommendations_sorted_by_score(self, recommender, sample_farmer_profile, course_catalog):
        """Test recommendations are sorted by score"""
        recommendations = await recommender.get_recommendations(
            sample_farmer_profile,
            course_catalog,
            limit=5,
        )

        scores = [r.score.total_score for r in recommendations]
        assert scores == sorted(scores, reverse=True)

    @pytest.mark.asyncio
    async def test_get_next_course(self, recommender, sample_farmer_profile, course_catalog):
        """Test getting single best next course"""
        recommendation = await recommender.get_next_course(
            sample_farmer_profile,
            course_catalog,
        )

        assert recommendation is None or isinstance(recommendation, CourseRecommendation)

    @pytest.mark.asyncio
    async def test_recommendations_exclude_draft_courses(self, recommender, sample_farmer_profile):
        """Test draft courses are excluded"""
        courses = [
            Course(id="c1", status=CourseStatus.DRAFT),
            Course(id="c2", status=CourseStatus.PUBLISHED),
        ]

        recommendations = await recommender.get_recommendations(
            sample_farmer_profile,
            courses,
        )

        course_ids = [r.course.id for r in recommendations]
        assert "c1" not in course_ids

    def test_calculate_relevance_language_match(self, recommender, sample_farmer_profile):
        """Test relevance score with language match"""
        course_bilingual = Course(language=ContentLanguage.BILINGUAL)
        course_arabic = Course(language=ContentLanguage.ARABIC)

        score_bilingual = recommender._calculate_relevance(sample_farmer_profile, course_bilingual)
        score_arabic = recommender._calculate_relevance(sample_farmer_profile, course_arabic)

        # Both should have decent scores, Arabic should be higher for Arabic-preferring user
        assert score_bilingual > 0
        assert score_arabic >= score_bilingual

    def test_calculate_difficulty_match_same_level(self, recommender, sample_farmer_profile):
        """Test difficulty match when levels match"""
        course = Course(difficulty=DifficultyLevel.BEGINNER)
        score = recommender._calculate_difficulty_match(sample_farmer_profile, course)
        assert score == 100.0

    def test_calculate_difficulty_match_one_level_up(self, recommender, sample_farmer_profile):
        """Test difficulty match one level up"""
        course = Course(difficulty=DifficultyLevel.INTERMEDIATE)
        score = recommender._calculate_difficulty_match(sample_farmer_profile, course)
        assert score == 90.0

    def test_calculate_popularity_score_high_enrollment(self, recommender):
        """Test popularity score with high enrollment"""
        course = Course(
            total_enrollments=1500,
            average_rating=4.8,
            rating_count=100,
        )
        score = recommender._calculate_popularity_score(course)
        assert score >= 80

    def test_calculate_freshness_score_recent(self, recommender):
        """Test freshness score for recently updated course"""
        course = Course(updated_at=datetime.now(UTC) - timedelta(days=10))
        score = recommender._calculate_freshness_score(course)
        assert score == 100.0

    def test_calculate_freshness_score_old(self, recommender):
        """Test freshness score for old course"""
        course = Course(updated_at=datetime.now(UTC) - timedelta(days=400))
        score = recommender._calculate_freshness_score(course)
        assert score == 20.0

    def test_is_seasonally_relevant(self, recommender):
        """Test seasonal relevance detection"""
        current_month = datetime.now(UTC).month
        seasonal_skills = SEASONAL_TOPICS.get(current_month, [])

        if seasonal_skills:
            course = Course(category=seasonal_skills[0])
            assert recommender._is_seasonally_relevant(course) is True

    def test_calculate_crop_relevance_matching(self, recommender, sample_farmer_profile):
        """Test crop relevance with matching skills"""
        # wheat maps to IRRIGATION, CROP_MANAGEMENT, FERTILIZATION
        course = Course(category=SkillCategory.IRRIGATION)
        score = recommender._calculate_crop_relevance(sample_farmer_profile, course)
        assert score >= 70


# =============================================================================
# Learning Path Tests
# =============================================================================


@pytest.mark.unit
class TestLearningPath:
    """Test LearningPath model"""

    def test_learning_path_creation(self):
        """Test creating learning path"""
        path = LearningPath(
            name=BilingualText(en="Irrigation Path", ar="مسار الري"),
            target_skill=SkillCategory.IRRIGATION,
            target_level=DifficultyLevel.ADVANCED,
            course_ids=["c1", "c2", "c3"],
            total_duration_minutes=180,
        )
        assert path.target_skill == SkillCategory.IRRIGATION
        assert len(path.course_ids) == 3

    def test_learning_path_progress(self):
        """Test learning path progress calculation"""
        path = LearningPath(
            courses=[Course(), Course(), Course()],
            courses_completed=1,
        )
        assert path.progress_percentage == pytest.approx(33.33, rel=0.1)

    def test_learning_path_empty_progress(self):
        """Test learning path with no courses"""
        path = LearningPath()
        assert path.progress_percentage == 0.0


@pytest.mark.unit
class TestLearningPathSuggestion:
    """Test learning path suggestion"""

    @pytest.fixture
    def recommender(self):
        """Create a content recommender"""
        return ContentRecommender(tenant_id="tenant1")

    @pytest.fixture
    def skill_courses(self):
        """Create courses for different skill levels"""
        return [
            Course(
                id="c1",
                title=BilingualText(en="Irrigation Basics", ar="أساسيات الري"),
                category=SkillCategory.IRRIGATION,
                difficulty=DifficultyLevel.BEGINNER,
                status=CourseStatus.PUBLISHED,
                estimated_duration_minutes=60,
            ),
            Course(
                id="c2",
                title=BilingualText(en="Irrigation Intermediate", ar="الري المتوسط"),
                category=SkillCategory.IRRIGATION,
                difficulty=DifficultyLevel.INTERMEDIATE,
                status=CourseStatus.PUBLISHED,
                estimated_duration_minutes=90,
            ),
            Course(
                id="c3",
                title=BilingualText(en="Irrigation Advanced", ar="الري المتقدم"),
                category=SkillCategory.IRRIGATION,
                difficulty=DifficultyLevel.ADVANCED,
                status=CourseStatus.PUBLISHED,
                estimated_duration_minutes=120,
            ),
        ]

    @pytest.mark.asyncio
    async def test_suggest_learning_path(self, recommender, sample_farmer_profile, skill_courses):
        """Test suggesting a learning path"""
        path = await recommender.suggest_learning_path(
            sample_farmer_profile,
            target_skill=SkillCategory.IRRIGATION,
            courses=skill_courses,
            target_level=DifficultyLevel.INTERMEDIATE,
        )

        assert path.target_skill == SkillCategory.IRRIGATION
        assert path.target_level == DifficultyLevel.INTERMEDIATE
        # Should include beginner and intermediate courses
        assert len(path.courses) >= 1

    @pytest.mark.asyncio
    async def test_learning_path_duration(self, recommender, sample_farmer_profile, skill_courses):
        """Test learning path total duration"""
        path = await recommender.suggest_learning_path(
            sample_farmer_profile,
            target_skill=SkillCategory.IRRIGATION,
            courses=skill_courses,
            target_level=DifficultyLevel.INTERMEDIATE,
        )

        expected_duration = sum(c.estimated_duration_minutes for c in path.courses)
        assert path.total_duration_minutes == expected_duration


# =============================================================================
# Bilingual Content Handling Tests
# =============================================================================


@pytest.mark.unit
class TestBilingualContentHandling:
    """Test bilingual content handling throughout the module"""

    def test_course_title_bilingual(self):
        """Test course with bilingual title"""
        course = Course(
            title=BilingualText(en="Irrigation", ar="الري"),
        )
        assert course.title.get("en") == "Irrigation"
        assert course.title.get("ar") == "الري"

    def test_lesson_objectives_bilingual(self):
        """Test lesson with bilingual objectives"""
        lesson = Lesson(
            objectives=[
                BilingualText(en="Understand basics", ar="فهم الأساسيات"),
                BilingualText(en="Apply techniques", ar="تطبيق التقنيات"),
            ]
        )
        assert len(lesson.objectives) == 2
        assert lesson.objectives[0].get("ar") == "فهم الأساسيات"

    def test_expert_credentials_bilingual(self):
        """Test expert with bilingual credentials"""
        expert = Expert(
            name=BilingualText(en="Dr. Ahmed", ar="د. أحمد"),
            credentials=[
                BilingualText(en="PhD in Agriculture", ar="دكتوراه في الزراعة"),
            ],
        )
        assert expert.name.get("ar") == "د. أحمد"
        assert expert.credentials[0].get("en") == "PhD in Agriculture"

    def test_progress_event_message_bilingual(self):
        """Test progress event with bilingual message"""
        event = ProgressEvent(
            message=BilingualText(
                en="Completed lesson",
                ar="أكمل الدرس",
            )
        )
        assert event.message.get("en") == "Completed lesson"
        assert event.message.get("ar") == "أكمل الدرس"

    def test_recommendation_reason_text_bilingual(self):
        """Test recommendation with bilingual reason"""
        rec = CourseRecommendation(
            reason_text=BilingualText(
                en="Relevant to your crops",
                ar="متعلق بمحاصيلك",
            )
        )
        assert rec.reason_text.get("ar") == "متعلق بمحاصيلك"


# =============================================================================
# Edge Cases Tests
# =============================================================================


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_quiz_with_no_questions(self):
        """Test quiz with no questions"""
        quiz = Quiz()
        assert quiz.total_points == 0

    def test_course_with_no_lessons(self):
        """Test course with no lessons"""
        course = Course()
        assert course.lesson_count == 0
        assert course.estimated_duration_minutes == 0

    def test_farmer_profile_empty_crops(self):
        """Test farmer profile with no crops"""
        profile = FarmerProfile(crop_types=[])
        assert profile.crop_types == []

    @pytest.mark.asyncio
    async def test_recommendations_empty_catalog(self):
        """Test recommendations with empty course catalog"""
        recommender = ContentRecommender(tenant_id="tenant1")
        profile = FarmerProfile()

        recommendations = await recommender.get_recommendations(profile, [])
        assert recommendations == []

    @pytest.mark.asyncio
    async def test_similar_courses_empty_catalog(self):
        """Test similar courses with empty catalog"""
        recommender = ContentRecommender(tenant_id="tenant1")
        course = Course()

        similar = await recommender.get_similar_courses(course, [])
        assert similar == []

    def test_enrollment_expired_status(self):
        """Test enrollment with expired status"""
        enrollment = CourseEnrollment(
            status=EnrollmentStatus.EXPIRED,
            expires_at=datetime.now(UTC) - timedelta(days=1),
        )
        assert enrollment.status == EnrollmentStatus.EXPIRED
        assert enrollment.is_completed is False

    def test_enrollment_dropped_status(self):
        """Test enrollment with dropped status"""
        enrollment = CourseEnrollment(
            status=EnrollmentStatus.DROPPED,
        )
        assert enrollment.is_completed is False


@pytest.mark.unit
class TestQuizRetakes:
    """Test quiz retake functionality"""

    @pytest.fixture
    def tracker(self, temp_storage_path):
        """Create a progress tracker with temp storage"""
        storage = ProgressStorage(temp_storage_path)
        return ProgressTracker(tenant_id="tenant1", storage=storage)

    @pytest.mark.asyncio
    async def test_quiz_retake_improves_score(self, tracker):
        """Test that quiz retakes can improve scores"""
        course = Course(
            id="course1",
            lessons=[
                Lesson(
                    id="lesson1",
                    course_id="course1",
                    quiz=Quiz(
                        id="quiz1",
                        questions=[
                            QuizQuestion(id="q1", correct_answer=1, points=50),
                            QuizQuestion(id="q2", correct_answer=2, points=50),
                        ],
                        passing_score=70,
                        attempts_allowed=3,
                    ),
                )
            ],
        )
        lesson = course.lessons[0]

        await tracker.enroll_course("farmer1", course)

        # First attempt - fail
        result1 = await tracker.submit_quiz("farmer1", lesson, {"q1": 0, "q2": 0})
        assert result1.passed is False
        assert result1.percentage == 0.0

        # Second attempt - partial
        result2 = await tracker.submit_quiz("farmer1", lesson, {"q1": 1, "q2": 0})
        assert result2.percentage == 50.0

        # Third attempt - pass
        result3 = await tracker.submit_quiz("farmer1", lesson, {"q1": 1, "q2": 2})
        assert result3.passed is True
        assert result3.percentage == 100.0


@pytest.mark.unit
class TestIncompleteCourses:
    """Test handling of incomplete courses"""

    @pytest.fixture
    def tracker(self, temp_storage_path):
        """Create a progress tracker with temp storage"""
        storage = ProgressStorage(temp_storage_path)
        return ProgressTracker(tenant_id="tenant1", storage=storage)

    @pytest.mark.asyncio
    async def test_partial_course_completion(self, tracker):
        """Test partial course completion tracking"""
        course = Course(
            id="course1",
            lessons=[
                Lesson(id="lesson1", course_id="course1"),
                Lesson(id="lesson2", course_id="course1"),
                Lesson(id="lesson3", course_id="course1"),
            ],
        )

        await tracker.enroll_course("farmer1", course)

        # Complete only first lesson
        await tracker.complete_lesson("farmer1", course.lessons[0])

        enrollment = await tracker.get_enrollment("farmer1", "course1")
        assert enrollment.lessons_completed == 1
        assert enrollment.total_lessons == 3
        assert enrollment.progress_percentage == pytest.approx(33.33, rel=0.1)
        assert enrollment.status == EnrollmentStatus.IN_PROGRESS

    @pytest.mark.asyncio
    async def test_progress_summary_incomplete(self, tracker):
        """Test progress summary for incomplete courses"""
        course = Course(
            id="course1",
            lessons=[Lesson(id="lesson1", course_id="course1")],
        )

        await tracker.enroll_course("farmer1", course)

        summary = await tracker.get_progress_summary("farmer1")
        # Newly enrolled courses have ENROLLED status, not IN_PROGRESS
        assert summary["total_courses_enrolled"] == 1
        assert summary["courses_completed"] == 0


# =============================================================================
# Storage Tests
# =============================================================================


@pytest.mark.unit
class TestProgressStorage:
    """Test ProgressStorage class"""

    @pytest.fixture
    def storage(self, temp_storage_path):
        """Create a progress storage instance"""
        return ProgressStorage(temp_storage_path)

    @pytest.mark.asyncio
    async def test_save_and_load_enrollment(self, storage):
        """Test saving and loading enrollment"""
        enrollment = CourseEnrollment(
            farmer_id="farmer1",
            course_id="course1",
        )

        await storage.save_enrollment(enrollment)

        loaded = await storage.load_enrollments("farmer1")
        assert len(loaded) == 1
        assert loaded[0].farmer_id == "farmer1"

    @pytest.mark.asyncio
    async def test_save_and_load_event(self, storage):
        """Test saving and loading events"""
        event = ProgressEvent(
            farmer_id="farmer1",
            event_type=ProgressEventType.LESSON_COMPLETED,
        )

        await storage.save_event(event)

        loaded = await storage.load_events("farmer1")
        assert len(loaded) == 1
        assert loaded[0].event_type == ProgressEventType.LESSON_COMPLETED

    @pytest.mark.asyncio
    async def test_load_events_with_filter(self, storage):
        """Test loading events with filter"""
        event1 = ProgressEvent(
            farmer_id="farmer1",
            event_type=ProgressEventType.LESSON_STARTED,
        )
        event2 = ProgressEvent(
            farmer_id="farmer1",
            event_type=ProgressEventType.LESSON_COMPLETED,
        )

        await storage.save_event(event1)
        await storage.save_event(event2)

        loaded = await storage.load_events(
            "farmer1",
            event_type=ProgressEventType.LESSON_COMPLETED,
        )
        assert len(loaded) == 1
        assert loaded[0].event_type == ProgressEventType.LESSON_COMPLETED

    @pytest.mark.asyncio
    async def test_save_and_load_profile(self, storage):
        """Test saving and loading farmer profile"""
        profile = FarmerProfile(
            farmer_id="farmer1",
            tenant_id="tenant1",
        )

        await storage.save_profile(profile)

        loaded = await storage.load_profile("farmer1")
        assert loaded is not None
        assert loaded.farmer_id == "farmer1"

    @pytest.mark.asyncio
    async def test_load_nonexistent_profile(self, storage):
        """Test loading non-existent profile returns None"""
        loaded = await storage.load_profile("nonexistent")
        assert loaded is None


# =============================================================================
# Convenience Function Tests
# =============================================================================


@pytest.mark.unit
class TestConvenienceFunctions:
    """Test module-level convenience functions"""

    def test_get_progress_tracker(self):
        """Test getting progress tracker"""
        tracker = get_progress_tracker("tenant1")
        assert tracker.tenant_id == "tenant1"

    def test_get_progress_tracker_cached(self):
        """Test tracker caching"""
        tracker1 = get_progress_tracker("tenant_cached")
        tracker2 = get_progress_tracker("tenant_cached")
        assert tracker1 is tracker2

    def test_get_content_recommender(self):
        """Test getting content recommender"""
        recommender = get_content_recommender("tenant1")
        assert recommender.tenant_id == "tenant1"


# =============================================================================
# Seasonal Topics and Crop Mapping Tests
# =============================================================================


@pytest.mark.unit
class TestSeasonalAndCropMapping:
    """Test seasonal topics and crop skill mapping"""

    def test_seasonal_topics_all_months(self):
        """Test seasonal topics defined for all months"""
        for month in range(1, 13):
            assert month in SEASONAL_TOPICS
            assert len(SEASONAL_TOPICS[month]) > 0

    def test_crop_skill_mapping(self):
        """Test crop skill mapping exists"""
        assert "wheat" in CROP_SKILL_MAPPING
        assert "date_palm" in CROP_SKILL_MAPPING
        assert len(CROP_SKILL_MAPPING["wheat"]) > 0

    def test_crop_skill_mapping_skills(self):
        """Test crop skill mapping contains valid skills"""
        for crop, skills in CROP_SKILL_MAPPING.items():
            for skill in skills:
                assert isinstance(skill, SkillCategory)


# =============================================================================
# XP Rewards Tests
# =============================================================================


@pytest.mark.unit
class TestXPRewards:
    """Test XP reward constants"""

    def test_xp_rewards_defined(self):
        """Test all XP rewards are defined"""
        assert "lesson_completed" in XP_REWARDS
        assert "quiz_passed" in XP_REWARDS
        assert "quiz_perfect_score" in XP_REWARDS
        assert "course_completed" in XP_REWARDS
        assert "certification_earned" in XP_REWARDS

    def test_xp_rewards_positive(self):
        """Test all XP rewards are positive"""
        for reward_type, xp in XP_REWARDS.items():
            assert xp > 0, f"{reward_type} should have positive XP"

    def test_xp_rewards_hierarchy(self):
        """Test XP rewards follow logical hierarchy"""
        assert XP_REWARDS["course_completed"] > XP_REWARDS["lesson_completed"]
        assert XP_REWARDS["certification_earned"] > XP_REWARDS["course_completed"]
        assert XP_REWARDS["quiz_perfect_score"] > XP_REWARDS["quiz_passed"]


# =============================================================================
# Streak Tests
# =============================================================================


@pytest.mark.unit
class TestStreakTracking:
    """Test learning streak functionality"""

    @pytest.fixture
    def tracker(self, temp_storage_path):
        """Create a progress tracker with temp storage"""
        storage = ProgressStorage(temp_storage_path)
        return ProgressTracker(tenant_id="tenant1", storage=storage)

    @pytest.mark.asyncio
    async def test_streak_starts_at_one(self, tracker, sample_course, sample_lesson):
        """Test streak starts at 1 on first learning activity"""
        await tracker.enroll_course("farmer1", sample_course)
        await tracker.complete_lesson("farmer1", sample_lesson)

        profile = await tracker.get_or_create_profile("farmer1")
        assert profile.current_streak_days == 1

    @pytest.mark.asyncio
    async def test_longest_streak_updated(self, tracker, sample_course, sample_lesson):
        """Test longest streak is updated"""
        await tracker.enroll_course("farmer1", sample_course)
        await tracker.complete_lesson("farmer1", sample_lesson)

        profile = await tracker.get_or_create_profile("farmer1")
        assert profile.longest_streak_days >= profile.current_streak_days
