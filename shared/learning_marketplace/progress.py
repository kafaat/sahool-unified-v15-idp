"""
Learning Progress Tracking
==========================
تتبع تقدم التعلم

Tracks and manages farmer learning progress including:
- Course enrollment and completion
- Lesson progress and time tracking
- Quiz attempts and scores
- Skill advancement
- Certification eligibility

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio
import json
import os
import tempfile
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Any

from .models import (
    BilingualText,
    Certification,
    Course,
    DifficultyLevel,
    EnrollmentStatus,
    FarmerCertification,
    FarmerProfile,
    FarmerSkill,
    Lesson,
    SkillCategory,
)


class ProgressEventType(StrEnum):
    """Progress event type | نوع حدث التقدم"""

    ENROLLMENT = "enrollment"  # التسجيل
    LESSON_STARTED = "lesson_started"  # بدأ الدرس
    LESSON_COMPLETED = "lesson_completed"  # أكمل الدرس
    QUIZ_STARTED = "quiz_started"  # بدأ الاختبار
    QUIZ_COMPLETED = "quiz_completed"  # أكمل الاختبار
    COURSE_COMPLETED = "course_completed"  # أكمل الدورة
    SKILL_LEVELED_UP = "skill_leveled_up"  # ارتقى المهارة
    CERTIFICATION_EARNED = "certification_earned"  # حصل على الشهادة
    STREAK_ACHIEVED = "streak_achieved"  # حقق سلسلة


@dataclass
class LessonProgress:
    """
    Progress for a single lesson
    تقدم لدرس واحد
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    farmer_id: str = ""
    lesson_id: str = ""
    course_id: str = ""

    # Progress
    started_at: datetime | None = None
    completed_at: datetime | None = None
    is_completed: bool = False

    # Time tracking
    time_spent_minutes: int = 0
    last_position_seconds: int = 0  # For video content

    # Content interaction
    content_viewed: bool = False
    downloads_completed: list[str] = field(default_factory=list)

    # Notes
    notes: str | None = None

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage"""
        if self.is_completed:
            return 100.0
        # Estimate based on time spent vs expected duration
        return 0.0  # Will be calculated based on lesson duration

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "farmer_id": self.farmer_id,
            "lesson_id": self.lesson_id,
            "course_id": self.course_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "is_completed": self.is_completed,
            "time_spent_minutes": self.time_spent_minutes,
            "last_position_seconds": self.last_position_seconds,
            "content_viewed": self.content_viewed,
            "downloads_completed": self.downloads_completed,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LessonProgress:
        """Create from dictionary"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            farmer_id=data.get("farmer_id", ""),
            lesson_id=data.get("lesson_id", ""),
            course_id=data.get("course_id", ""),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            is_completed=data.get("is_completed", False),
            time_spent_minutes=data.get("time_spent_minutes", 0),
            last_position_seconds=data.get("last_position_seconds", 0),
            content_viewed=data.get("content_viewed", False),
            downloads_completed=data.get("downloads_completed", []),
            notes=data.get("notes"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(UTC),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(UTC),
        )


@dataclass
class QuizAttempt:
    """
    Quiz attempt record
    سجل محاولة الاختبار
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    farmer_id: str = ""
    quiz_id: str = ""
    lesson_id: str = ""
    course_id: str = ""

    # Attempt info
    attempt_number: int = 1
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None

    # Results
    score: int = 0
    max_score: int = 0
    percentage: float = 0.0
    passed: bool = False

    # Answers
    answers: dict[str, Any] = field(default_factory=dict)  # question_id -> answer
    correct_count: int = 0
    incorrect_count: int = 0

    # Time
    time_taken_seconds: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "farmer_id": self.farmer_id,
            "quiz_id": self.quiz_id,
            "lesson_id": self.lesson_id,
            "course_id": self.course_id,
            "attempt_number": self.attempt_number,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "score": self.score,
            "max_score": self.max_score,
            "percentage": self.percentage,
            "passed": self.passed,
            "answers": self.answers,
            "correct_count": self.correct_count,
            "incorrect_count": self.incorrect_count,
            "time_taken_seconds": self.time_taken_seconds,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QuizAttempt:
        """Create from dictionary"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            farmer_id=data.get("farmer_id", ""),
            quiz_id=data.get("quiz_id", ""),
            lesson_id=data.get("lesson_id", ""),
            course_id=data.get("course_id", ""),
            attempt_number=data.get("attempt_number", 1),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else datetime.now(UTC),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            score=data.get("score", 0),
            max_score=data.get("max_score", 0),
            percentage=data.get("percentage", 0.0),
            passed=data.get("passed", False),
            answers=data.get("answers", {}),
            correct_count=data.get("correct_count", 0),
            incorrect_count=data.get("incorrect_count", 0),
            time_taken_seconds=data.get("time_taken_seconds", 0),
        )


@dataclass
class CourseEnrollment:
    """
    Course enrollment record
    سجل التسجيل في الدورة
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    farmer_id: str = ""
    course_id: str = ""

    # Status
    status: EnrollmentStatus = EnrollmentStatus.ENROLLED

    # Dates
    enrolled_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    expires_at: datetime | None = None

    # Progress
    lessons_completed: int = 0
    total_lessons: int = 0
    quizzes_passed: int = 0
    total_quizzes: int = 0

    # Time
    total_time_spent_minutes: int = 0

    # Scores
    average_quiz_score: float = 0.0

    # Last activity
    last_activity_at: datetime | None = None
    last_lesson_id: str | None = None

    # Lesson progress
    lesson_progress: list[LessonProgress] = field(default_factory=list)

    # Quiz attempts
    quiz_attempts: list[QuizAttempt] = field(default_factory=list)

    # Certificate
    certificate_id: str | None = None
    certificate_issued_at: datetime | None = None

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def progress_percentage(self) -> float:
        """Calculate overall progress percentage"""
        if self.total_lessons == 0:
            return 0.0
        return (self.lessons_completed / self.total_lessons) * 100

    @property
    def is_completed(self) -> bool:
        """Check if course is completed"""
        return self.status == EnrollmentStatus.COMPLETED

    def get_lesson_progress(self, lesson_id: str) -> LessonProgress | None:
        """Get progress for a specific lesson"""
        for progress in self.lesson_progress:
            if progress.lesson_id == lesson_id:
                return progress
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "farmer_id": self.farmer_id,
            "course_id": self.course_id,
            "status": self.status.value,
            "enrolled_at": self.enrolled_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "lessons_completed": self.lessons_completed,
            "total_lessons": self.total_lessons,
            "quizzes_passed": self.quizzes_passed,
            "total_quizzes": self.total_quizzes,
            "progress_percentage": self.progress_percentage,
            "total_time_spent_minutes": self.total_time_spent_minutes,
            "average_quiz_score": self.average_quiz_score,
            "last_activity_at": self.last_activity_at.isoformat() if self.last_activity_at else None,
            "last_lesson_id": self.last_lesson_id,
            "lesson_progress": [lp.to_dict() for lp in self.lesson_progress],
            "quiz_attempts": [qa.to_dict() for qa in self.quiz_attempts],
            "certificate_id": self.certificate_id,
            "certificate_issued_at": self.certificate_issued_at.isoformat() if self.certificate_issued_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CourseEnrollment:
        """Create from dictionary"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            farmer_id=data.get("farmer_id", ""),
            course_id=data.get("course_id", ""),
            status=EnrollmentStatus(data.get("status", "enrolled")),
            enrolled_at=datetime.fromisoformat(data["enrolled_at"]) if data.get("enrolled_at") else datetime.now(UTC),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            lessons_completed=data.get("lessons_completed", 0),
            total_lessons=data.get("total_lessons", 0),
            quizzes_passed=data.get("quizzes_passed", 0),
            total_quizzes=data.get("total_quizzes", 0),
            total_time_spent_minutes=data.get("total_time_spent_minutes", 0),
            average_quiz_score=data.get("average_quiz_score", 0.0),
            last_activity_at=datetime.fromisoformat(data["last_activity_at"]) if data.get("last_activity_at") else None,
            last_lesson_id=data.get("last_lesson_id"),
            lesson_progress=[LessonProgress.from_dict(lp) for lp in data.get("lesson_progress", [])],
            quiz_attempts=[QuizAttempt.from_dict(qa) for qa in data.get("quiz_attempts", [])],
            certificate_id=data.get("certificate_id"),
            certificate_issued_at=datetime.fromisoformat(data["certificate_issued_at"])
            if data.get("certificate_issued_at")
            else None,
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(UTC),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.now(UTC),
        )


@dataclass
class ProgressEvent:
    """
    Progress event for tracking and notifications
    حدث التقدم للتتبع والإشعارات
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    farmer_id: str = ""
    tenant_id: str = ""

    # Event info
    event_type: ProgressEventType = ProgressEventType.LESSON_STARTED

    # Context
    course_id: str | None = None
    lesson_id: str | None = None
    quiz_id: str | None = None
    skill_category: SkillCategory | None = None
    certification_id: str | None = None

    # Data
    data: dict[str, Any] = field(default_factory=dict)

    # Messages
    message: BilingualText = field(default_factory=BilingualText)

    # XP earned
    xp_earned: int = 0

    # Timestamp
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "farmer_id": self.farmer_id,
            "tenant_id": self.tenant_id,
            "event_type": self.event_type.value,
            "course_id": self.course_id,
            "lesson_id": self.lesson_id,
            "quiz_id": self.quiz_id,
            "skill_category": self.skill_category.value if self.skill_category else None,
            "certification_id": self.certification_id,
            "data": self.data,
            "message": self.message.to_dict(),
            "xp_earned": self.xp_earned,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProgressEvent:
        """Create from dictionary"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            farmer_id=data.get("farmer_id", ""),
            tenant_id=data.get("tenant_id", ""),
            event_type=ProgressEventType(data.get("event_type", "lesson_started")),
            course_id=data.get("course_id"),
            lesson_id=data.get("lesson_id"),
            quiz_id=data.get("quiz_id"),
            skill_category=SkillCategory(data["skill_category"]) if data.get("skill_category") else None,
            certification_id=data.get("certification_id"),
            data=data.get("data", {}),
            message=BilingualText.from_dict(data.get("message", {})),
            xp_earned=data.get("xp_earned", 0),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.now(UTC),
        )


class ProgressStorage:
    """
    Storage backend for progress data
    التخزين الخلفي لبيانات التقدم
    """

    def __init__(self, storage_path: str | None = None):
        """Initialize storage"""
        # Default to /var/lib/sahool in production, tempdir for development only
        default_path = (
            "/var/lib/sahool/learning_progress"
            if os.getenv("ENVIRONMENT") == "production"
            else os.path.join(tempfile.gettempdir(), "sahool_learning_progress")
        )
        self.storage_path = Path(storage_path or os.getenv("LEARNING_PROGRESS_PATH", default_path))
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._lock = asyncio.Lock()

    async def save_enrollment(self, enrollment: CourseEnrollment) -> None:
        """Save enrollment record"""
        async with self._lock:
            file_path = self.storage_path / f"{enrollment.farmer_id}_enrollments.jsonl"
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(enrollment.to_dict(), ensure_ascii=False) + "\n")

    async def load_enrollments(self, farmer_id: str) -> list[CourseEnrollment]:
        """Load all enrollments for a farmer"""
        file_path = self.storage_path / f"{farmer_id}_enrollments.jsonl"
        if not file_path.exists():
            return []

        enrollments = []
        async with self._lock:
            with open(file_path, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        enrollments.append(CourseEnrollment.from_dict(data))

        # Return most recent version of each enrollment (by course_id)
        latest: dict[str, CourseEnrollment] = {}
        for enrollment in enrollments:
            key = f"{enrollment.farmer_id}_{enrollment.course_id}"
            if key not in latest or enrollment.updated_at > latest[key].updated_at:
                latest[key] = enrollment

        return list(latest.values())

    async def save_event(self, event: ProgressEvent) -> None:
        """Save progress event"""
        async with self._lock:
            file_path = self.storage_path / f"{event.farmer_id}_events.jsonl"
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")

    async def load_events(
        self,
        farmer_id: str,
        event_type: ProgressEventType | None = None,
        since: datetime | None = None,
    ) -> list[ProgressEvent]:
        """Load progress events"""
        file_path = self.storage_path / f"{farmer_id}_events.jsonl"
        if not file_path.exists():
            return []

        events = []
        async with self._lock:
            with open(file_path, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        event = ProgressEvent.from_dict(data)

                        # Apply filters
                        if event_type and event.event_type != event_type:
                            continue
                        if since and event.timestamp < since:
                            continue

                        events.append(event)

        return sorted(events, key=lambda e: e.timestamp, reverse=True)

    async def save_profile(self, profile: FarmerProfile) -> None:
        """Save farmer profile"""
        async with self._lock:
            file_path = self.storage_path / f"{profile.farmer_id}_profile.json"
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(profile.to_dict(), f, ensure_ascii=False, indent=2)

    async def load_profile(self, farmer_id: str) -> FarmerProfile | None:
        """Load farmer profile"""
        file_path = self.storage_path / f"{farmer_id}_profile.json"
        if not file_path.exists():
            return None

        async with self._lock:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
                return FarmerProfile.from_dict(data)


# XP rewards for different actions
XP_REWARDS = {
    "lesson_completed": 25,
    "quiz_passed": 50,
    "quiz_perfect_score": 100,
    "course_completed": 200,
    "certification_earned": 500,
    "streak_7_days": 100,
    "streak_30_days": 300,
    "first_course_completed": 150,
}


class ProgressTracker:
    """
    Progress tracker for farmer learning
    متتبع تقدم تعلم المزارع

    Features:
    - Course enrollment management
    - Lesson progress tracking
    - Quiz attempt recording
    - Skill advancement
    - Certification eligibility checking
    - XP and streak management

    Usage:
        tracker = ProgressTracker(tenant_id="farm_001")

        # Enroll in course
        enrollment = await tracker.enroll_course(farmer_id, course)

        # Track lesson progress
        progress = await tracker.start_lesson(farmer_id, lesson)
        progress = await tracker.complete_lesson(farmer_id, lesson)

        # Submit quiz
        result = await tracker.submit_quiz(farmer_id, quiz, answers)

        # Check eligibility
        eligible = await tracker.check_certification_eligibility(
            farmer_id, certification
        )
    """

    def __init__(
        self,
        tenant_id: str,
        storage: ProgressStorage | None = None,
        on_event: Callable[[ProgressEvent], None] | None = None,
    ):
        """
        Initialize the progress tracker

        Args:
            tenant_id: Tenant identifier
            storage: Storage backend (default: file-based)
            on_event: Callback when progress event occurs
        """
        self.tenant_id = tenant_id
        self.storage = storage or ProgressStorage()
        self.on_event = on_event

        # In-memory cache
        self._profiles: dict[str, FarmerProfile] = {}
        self._enrollments: dict[str, list[CourseEnrollment]] = {}

    async def get_or_create_profile(self, farmer_id: str) -> FarmerProfile:
        """Get or create farmer profile"""
        if farmer_id in self._profiles:
            return self._profiles[farmer_id]

        profile = await self.storage.load_profile(farmer_id)
        if not profile:
            profile = FarmerProfile(
                farmer_id=farmer_id,
                tenant_id=self.tenant_id,
            )
            await self.storage.save_profile(profile)

        self._profiles[farmer_id] = profile
        return profile

    async def enroll_course(
        self,
        farmer_id: str,
        course: Course,
    ) -> CourseEnrollment:
        """
        Enroll farmer in a course
        تسجيل المزارع في دورة

        Args:
            farmer_id: Farmer identifier
            course: Course to enroll in

        Returns:
            CourseEnrollment record
        """
        profile = await self.get_or_create_profile(farmer_id)

        # Check if already enrolled
        enrollments = await self.get_enrollments(farmer_id)
        for enrollment in enrollments:
            if enrollment.course_id == course.id and enrollment.status != EnrollmentStatus.DROPPED:
                return enrollment

        # Create enrollment
        enrollment = CourseEnrollment(
            farmer_id=farmer_id,
            course_id=course.id,
            status=EnrollmentStatus.ENROLLED,
            total_lessons=len(course.lessons),
            total_quizzes=sum(1 for l in course.lessons if l.quiz),
        )

        # Update profile
        profile.total_courses_enrolled += 1
        profile.updated_at = datetime.now(UTC)

        await self.storage.save_enrollment(enrollment)
        await self.storage.save_profile(profile)

        # Emit event
        await self._emit_event(
            farmer_id=farmer_id,
            event_type=ProgressEventType.ENROLLMENT,
            course_id=course.id,
            message=BilingualText(
                en=f"Enrolled in: {course.title.en}",
                ar=f"تم التسجيل في: {course.title.ar}",
            ),
        )

        self._enrollments[farmer_id] = enrollments + [enrollment]
        return enrollment

    async def get_enrollments(
        self,
        farmer_id: str,
        status: EnrollmentStatus | None = None,
    ) -> list[CourseEnrollment]:
        """Get all enrollments for a farmer"""
        if farmer_id not in self._enrollments:
            self._enrollments[farmer_id] = await self.storage.load_enrollments(farmer_id)

        enrollments = self._enrollments[farmer_id]

        if status:
            enrollments = [e for e in enrollments if e.status == status]

        return enrollments

    async def get_enrollment(
        self,
        farmer_id: str,
        course_id: str,
    ) -> CourseEnrollment | None:
        """Get enrollment for a specific course"""
        enrollments = await self.get_enrollments(farmer_id)
        for enrollment in enrollments:
            if enrollment.course_id == course_id:
                return enrollment
        return None

    async def start_lesson(
        self,
        farmer_id: str,
        lesson: Lesson,
    ) -> LessonProgress:
        """
        Start a lesson
        بدء درس

        Args:
            farmer_id: Farmer identifier
            lesson: Lesson to start

        Returns:
            LessonProgress record
        """
        enrollment = await self.get_enrollment(farmer_id, lesson.course_id)
        if not enrollment:
            raise ValueError(f"Farmer {farmer_id} is not enrolled in course {lesson.course_id}")

        # Check if already started
        progress = enrollment.get_lesson_progress(lesson.id)
        if progress:
            # Update last activity
            progress.updated_at = datetime.now(UTC)
            enrollment.last_activity_at = datetime.now(UTC)
            enrollment.last_lesson_id = lesson.id
            return progress

        # Create new progress
        progress = LessonProgress(
            farmer_id=farmer_id,
            lesson_id=lesson.id,
            course_id=lesson.course_id,
            started_at=datetime.now(UTC),
        )

        enrollment.lesson_progress.append(progress)
        enrollment.last_activity_at = datetime.now(UTC)
        enrollment.last_lesson_id = lesson.id

        if enrollment.status == EnrollmentStatus.ENROLLED:
            enrollment.status = EnrollmentStatus.IN_PROGRESS
            enrollment.started_at = datetime.now(UTC)

        await self.storage.save_enrollment(enrollment)

        # Emit event
        await self._emit_event(
            farmer_id=farmer_id,
            event_type=ProgressEventType.LESSON_STARTED,
            course_id=lesson.course_id,
            lesson_id=lesson.id,
            message=BilingualText(
                en=f"Started lesson: {lesson.title.en}",
                ar=f"بدأ الدرس: {lesson.title.ar}",
            ),
        )

        return progress

    async def complete_lesson(
        self,
        farmer_id: str,
        lesson: Lesson,
        time_spent_minutes: int = 0,
    ) -> LessonProgress:
        """
        Complete a lesson
        إكمال درس

        Args:
            farmer_id: Farmer identifier
            lesson: Lesson completed
            time_spent_minutes: Time spent on lesson

        Returns:
            Updated LessonProgress record
        """
        enrollment = await self.get_enrollment(farmer_id, lesson.course_id)
        if not enrollment:
            raise ValueError(f"Farmer {farmer_id} is not enrolled in course {lesson.course_id}")

        progress = enrollment.get_lesson_progress(lesson.id)
        if not progress:
            # Start lesson first
            progress = await self.start_lesson(farmer_id, lesson)

        if progress.is_completed:
            return progress

        # Mark as completed
        progress.is_completed = True
        progress.completed_at = datetime.now(UTC)
        progress.content_viewed = True
        progress.time_spent_minutes = time_spent_minutes or lesson.estimated_duration_minutes

        # Update enrollment
        enrollment.lessons_completed += 1
        enrollment.total_time_spent_minutes += progress.time_spent_minutes
        enrollment.last_activity_at = datetime.now(UTC)
        enrollment.updated_at = datetime.now(UTC)

        # Update profile
        profile = await self.get_or_create_profile(farmer_id)
        profile.total_learning_minutes += progress.time_spent_minutes
        profile.updated_at = datetime.now(UTC)

        # Award XP
        xp_earned = XP_REWARDS["lesson_completed"]
        profile.total_xp += xp_earned

        # Update skills
        for skill_category in lesson.skills:
            await self._update_skill(
                profile,
                skill_category,
                xp_earned=xp_earned // len(lesson.skills) if lesson.skills else 0,
                learning_minutes=progress.time_spent_minutes // len(lesson.skills) if lesson.skills else 0,
            )

        # Update streak
        await self._update_streak(profile)

        # Check course completion
        if enrollment.lessons_completed >= enrollment.total_lessons:
            await self._complete_course(enrollment, profile)

        await self.storage.save_enrollment(enrollment)
        await self.storage.save_profile(profile)

        # Emit event
        await self._emit_event(
            farmer_id=farmer_id,
            event_type=ProgressEventType.LESSON_COMPLETED,
            course_id=lesson.course_id,
            lesson_id=lesson.id,
            xp_earned=xp_earned,
            data={"time_spent_minutes": progress.time_spent_minutes},
            message=BilingualText(
                en=f"Completed lesson: {lesson.title.en}",
                ar=f"أكمل الدرس: {lesson.title.ar}",
            ),
        )

        return progress

    async def start_quiz(
        self,
        farmer_id: str,
        lesson: Lesson,
    ) -> QuizAttempt:
        """
        Start a quiz attempt
        بدء محاولة اختبار

        Args:
            farmer_id: Farmer identifier
            lesson: Lesson containing the quiz

        Returns:
            QuizAttempt record
        """
        if not lesson.quiz:
            raise ValueError(f"Lesson {lesson.id} does not have a quiz")

        enrollment = await self.get_enrollment(farmer_id, lesson.course_id)
        if not enrollment:
            raise ValueError(f"Farmer {farmer_id} is not enrolled in course {lesson.course_id}")

        # Count existing attempts
        existing_attempts = [qa for qa in enrollment.quiz_attempts if qa.quiz_id == lesson.quiz.id]

        if len(existing_attempts) >= lesson.quiz.attempts_allowed:
            raise ValueError("Maximum quiz attempts reached")

        # Create new attempt
        attempt = QuizAttempt(
            farmer_id=farmer_id,
            quiz_id=lesson.quiz.id,
            lesson_id=lesson.id,
            course_id=lesson.course_id,
            attempt_number=len(existing_attempts) + 1,
            max_score=lesson.quiz.total_points,
        )

        enrollment.quiz_attempts.append(attempt)
        await self.storage.save_enrollment(enrollment)

        # Emit event
        await self._emit_event(
            farmer_id=farmer_id,
            event_type=ProgressEventType.QUIZ_STARTED,
            course_id=lesson.course_id,
            lesson_id=lesson.id,
            quiz_id=lesson.quiz.id,
            data={"attempt_number": attempt.attempt_number},
            message=BilingualText(
                en=f"Started quiz: {lesson.quiz.title.en}",
                ar=f"بدأ الاختبار: {lesson.quiz.title.ar}",
            ),
        )

        return attempt

    async def submit_quiz(
        self,
        farmer_id: str,
        lesson: Lesson,
        answers: dict[str, Any],
    ) -> QuizAttempt:
        """
        Submit quiz answers
        تقديم إجابات الاختبار

        Args:
            farmer_id: Farmer identifier
            lesson: Lesson containing the quiz
            answers: Dictionary of question_id -> answer

        Returns:
            Completed QuizAttempt with results
        """
        if not lesson.quiz:
            raise ValueError(f"Lesson {lesson.id} does not have a quiz")

        enrollment = await self.get_enrollment(farmer_id, lesson.course_id)
        if not enrollment:
            raise ValueError(f"Farmer {farmer_id} is not enrolled in course {lesson.course_id}")

        # Find active attempt
        active_attempt = None
        for qa in enrollment.quiz_attempts:
            if qa.quiz_id == lesson.quiz.id and not qa.completed_at:
                active_attempt = qa
                break

        if not active_attempt:
            # Start new attempt
            active_attempt = await self.start_quiz(farmer_id, lesson)

        # Grade quiz
        score = 0
        correct_count = 0
        incorrect_count = 0

        for question in lesson.quiz.questions:
            answer = answers.get(question.id)
            if answer == question.correct_answer:
                score += question.points
                correct_count += 1
            else:
                incorrect_count += 1

        # Update attempt
        active_attempt.completed_at = datetime.now(UTC)
        active_attempt.answers = answers
        active_attempt.score = score
        active_attempt.percentage = (score / active_attempt.max_score * 100) if active_attempt.max_score > 0 else 0
        active_attempt.passed = active_attempt.percentage >= lesson.quiz.passing_score
        active_attempt.correct_count = correct_count
        active_attempt.incorrect_count = incorrect_count
        active_attempt.time_taken_seconds = int(
            (active_attempt.completed_at - active_attempt.started_at).total_seconds()
        )

        # Update enrollment
        if active_attempt.passed:
            # Check if first pass
            previous_passes = sum(
                1
                for qa in enrollment.quiz_attempts
                if qa.quiz_id == lesson.quiz.id and qa.passed and qa.id != active_attempt.id
            )
            if previous_passes == 0:
                enrollment.quizzes_passed += 1

        # Calculate average score
        all_scores = [qa.percentage for qa in enrollment.quiz_attempts if qa.completed_at]
        enrollment.average_quiz_score = sum(all_scores) / len(all_scores) if all_scores else 0
        enrollment.updated_at = datetime.now(UTC)

        # Update profile
        profile = await self.get_or_create_profile(farmer_id)

        # Award XP
        xp_earned = 0
        if active_attempt.passed:
            xp_earned = XP_REWARDS["quiz_passed"]
            if active_attempt.percentage == 100:
                xp_earned += XP_REWARDS["quiz_perfect_score"]

            profile.total_xp += xp_earned

            # Update skills
            for skill_category in lesson.skills:
                skill = profile.get_skill(skill_category)
                if skill:
                    skill.quizzes_passed += 1
                    # Update average score
                    total_score = skill.average_quiz_score * (skill.quizzes_passed - 1) + active_attempt.percentage
                    skill.average_quiz_score = total_score / skill.quizzes_passed
                    if active_attempt.percentage > skill.best_quiz_score:
                        skill.best_quiz_score = active_attempt.percentage

        await self.storage.save_enrollment(enrollment)
        await self.storage.save_profile(profile)

        # Emit event
        await self._emit_event(
            farmer_id=farmer_id,
            event_type=ProgressEventType.QUIZ_COMPLETED,
            course_id=lesson.course_id,
            lesson_id=lesson.id,
            quiz_id=lesson.quiz.id,
            xp_earned=xp_earned,
            data={
                "score": active_attempt.score,
                "percentage": active_attempt.percentage,
                "passed": active_attempt.passed,
            },
            message=BilingualText(
                en=f"Completed quiz with {active_attempt.percentage:.0f}%",
                ar=f"أكمل الاختبار بنسبة {active_attempt.percentage:.0f}%",
            ),
        )

        return active_attempt

    async def _complete_course(
        self,
        enrollment: CourseEnrollment,
        profile: FarmerProfile,
    ) -> None:
        """Complete a course"""
        if enrollment.status == EnrollmentStatus.COMPLETED:
            return

        enrollment.status = EnrollmentStatus.COMPLETED
        enrollment.completed_at = datetime.now(UTC)

        # Update profile
        profile.total_courses_completed += 1

        # Award XP
        xp_earned = XP_REWARDS["course_completed"]
        if profile.total_courses_completed == 1:
            xp_earned += XP_REWARDS["first_course_completed"]

        profile.total_xp += xp_earned

        # Emit event
        await self._emit_event(
            farmer_id=enrollment.farmer_id,
            event_type=ProgressEventType.COURSE_COMPLETED,
            course_id=enrollment.course_id,
            xp_earned=xp_earned,
            message=BilingualText(
                en="Congratulations! Course completed!",
                ar="تهانينا! تم إكمال الدورة!",
            ),
        )

    async def _update_skill(
        self,
        profile: FarmerProfile,
        category: SkillCategory,
        xp_earned: int = 0,
        learning_minutes: int = 0,
    ) -> FarmerSkill:
        """Update or create a skill"""
        skill = profile.get_skill(category)
        if not skill:
            skill = FarmerSkill(
                farmer_id=profile.farmer_id,
                category=category,
            )
            profile.skills.append(skill)

        # Update skill
        skill.experience_points += xp_earned
        skill.total_learning_minutes += learning_minutes
        skill.last_activity_at = datetime.now(UTC)
        skill.updated_at = datetime.now(UTC)

        # Check level up
        old_level = skill.level
        new_level = self._calculate_skill_level(skill.experience_points)

        if new_level != old_level:
            skill.level = new_level

            # Emit level up event
            await self._emit_event(
                farmer_id=profile.farmer_id,
                event_type=ProgressEventType.SKILL_LEVELED_UP,
                skill_category=category,
                data={
                    "old_level": old_level.value,
                    "new_level": new_level.value,
                    "experience_points": skill.experience_points,
                },
                message=BilingualText(
                    en=f"Skill leveled up to {new_level.value}!",
                    ar=f"ارتقت المهارة إلى {new_level.value}!",
                ),
            )

        return skill

    def _calculate_skill_level(self, xp: int) -> DifficultyLevel:
        """Calculate skill level from XP"""
        if xp >= 3500:
            return DifficultyLevel.EXPERT
        elif xp >= 1500:
            return DifficultyLevel.ADVANCED
        elif xp >= 500:
            return DifficultyLevel.INTERMEDIATE
        return DifficultyLevel.BEGINNER

    async def _update_streak(self, profile: FarmerProfile) -> None:
        """Update learning streak"""
        today = datetime.now(UTC).date()

        if profile.last_learning_date:
            last_date = profile.last_learning_date.date()
            days_diff = (today - last_date).days

            if days_diff == 0:
                # Same day, no change
                return
            elif days_diff == 1:
                # Consecutive day
                profile.current_streak_days += 1
            else:
                # Streak broken
                profile.current_streak_days = 1
        else:
            profile.current_streak_days = 1

        profile.last_learning_date = datetime.now(UTC)

        # Update longest streak
        if profile.current_streak_days > profile.longest_streak_days:
            profile.longest_streak_days = profile.current_streak_days

        # Check streak milestones
        if profile.current_streak_days == 7:
            profile.total_xp += XP_REWARDS["streak_7_days"]
            await self._emit_event(
                farmer_id=profile.farmer_id,
                event_type=ProgressEventType.STREAK_ACHIEVED,
                xp_earned=XP_REWARDS["streak_7_days"],
                data={"streak_days": 7},
                message=BilingualText(
                    en="7-day learning streak achieved!",
                    ar="تم تحقيق سلسلة تعلم 7 أيام!",
                ),
            )
        elif profile.current_streak_days == 30:
            profile.total_xp += XP_REWARDS["streak_30_days"]
            await self._emit_event(
                farmer_id=profile.farmer_id,
                event_type=ProgressEventType.STREAK_ACHIEVED,
                xp_earned=XP_REWARDS["streak_30_days"],
                data={"streak_days": 30},
                message=BilingualText(
                    en="30-day learning streak achieved!",
                    ar="تم تحقيق سلسلة تعلم 30 يوم!",
                ),
            )

    async def check_certification_eligibility(
        self,
        farmer_id: str,
        certification: Certification,
    ) -> tuple[bool, list[str]]:
        """
        Check if farmer is eligible for certification
        التحقق من أهلية المزارع للشهادة

        Args:
            farmer_id: Farmer identifier
            certification: Certification to check

        Returns:
            Tuple of (is_eligible, list of missing requirements)
        """
        profile = await self.get_or_create_profile(farmer_id)
        missing = []

        # Check required courses
        for course_id in certification.required_course_ids:
            enrollment = await self.get_enrollment(farmer_id, course_id)
            if not enrollment or not enrollment.is_completed:
                missing.append(f"Complete course: {course_id}")

            # Check score if completed
            if enrollment and enrollment.is_completed:
                if enrollment.average_quiz_score < certification.minimum_score:
                    missing.append(f"Minimum score {certification.minimum_score}% required for {course_id}")

        # Check required skills
        for skill_category in certification.required_skills:
            skill = profile.get_skill(skill_category)
            if not skill or skill.level == DifficultyLevel.BEGINNER:
                missing.append(f"Develop skill: {skill_category.value}")

        is_eligible = len(missing) == 0
        return is_eligible, missing

    async def award_certification(
        self,
        farmer_id: str,
        certification: Certification,
        score: int = 0,
    ) -> FarmerCertification:
        """
        Award certification to farmer
        منح الشهادة للمزارع

        Args:
            farmer_id: Farmer identifier
            certification: Certification to award
            score: Score achieved

        Returns:
            FarmerCertification record
        """
        profile = await self.get_or_create_profile(farmer_id)

        # Calculate expiry date
        expires_at = None
        if certification.validity_days:
            expires_at = datetime.now(UTC) + timedelta(days=certification.validity_days)

        # Create certification record
        farmer_cert = FarmerCertification(
            farmer_id=farmer_id,
            certification_id=certification.id,
            score=score,
            expires_at=expires_at,
        )

        profile.certifications.append(farmer_cert)

        # Award XP
        profile.total_xp += XP_REWARDS["certification_earned"]

        await self.storage.save_profile(profile)

        # Emit event
        await self._emit_event(
            farmer_id=farmer_id,
            event_type=ProgressEventType.CERTIFICATION_EARNED,
            certification_id=certification.id,
            xp_earned=XP_REWARDS["certification_earned"],
            data={
                "certificate_number": farmer_cert.certificate_number,
                "score": score,
            },
            message=BilingualText(
                en=f"Certification earned: {certification.name.en}",
                ar=f"تم الحصول على الشهادة: {certification.name.ar}",
            ),
        )

        return farmer_cert

    async def get_progress_summary(
        self,
        farmer_id: str,
    ) -> dict[str, Any]:
        """
        Get learning progress summary
        الحصول على ملخص تقدم التعلم

        Args:
            farmer_id: Farmer identifier

        Returns:
            Summary dictionary with all progress stats
        """
        profile = await self.get_or_create_profile(farmer_id)
        enrollments = await self.get_enrollments(farmer_id)

        # Calculate stats
        in_progress = [e for e in enrollments if e.status == EnrollmentStatus.IN_PROGRESS]
        completed = [e for e in enrollments if e.status == EnrollmentStatus.COMPLETED]

        return {
            "farmer_id": farmer_id,
            "total_xp": profile.total_xp,
            "overall_level": profile.overall_level.value,
            "current_streak_days": profile.current_streak_days,
            "longest_streak_days": profile.longest_streak_days,
            "total_learning_minutes": profile.total_learning_minutes,
            "total_courses_enrolled": len(enrollments),
            "courses_in_progress": len(in_progress),
            "courses_completed": len(completed),
            "total_certifications": len(profile.certifications),
            "valid_certifications": sum(1 for c in profile.certifications if c.is_valid and not c.is_expired),
            "skills_summary": {
                skill.category.value: {
                    "level": skill.level.value,
                    "xp": skill.experience_points,
                    "progress": skill.level_progress,
                }
                for skill in profile.skills
            },
            "weekly_goal_progress": (
                min(
                    100,
                    (profile.total_learning_minutes / profile.weekly_learning_goal_minutes) * 100,
                )
                if profile.weekly_learning_goal_minutes > 0
                else 0
            ),
            "last_activity_at": profile.last_learning_date.isoformat() if profile.last_learning_date else None,
        }

    async def get_events(
        self,
        farmer_id: str,
        event_type: ProgressEventType | None = None,
        limit: int = 50,
    ) -> list[ProgressEvent]:
        """Get progress events for farmer"""
        events = await self.storage.load_events(farmer_id, event_type)
        return events[:limit]

    async def _emit_event(
        self,
        farmer_id: str,
        event_type: ProgressEventType,
        message: BilingualText,
        course_id: str | None = None,
        lesson_id: str | None = None,
        quiz_id: str | None = None,
        skill_category: SkillCategory | None = None,
        certification_id: str | None = None,
        xp_earned: int = 0,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Emit and store a progress event"""
        event = ProgressEvent(
            farmer_id=farmer_id,
            tenant_id=self.tenant_id,
            event_type=event_type,
            course_id=course_id,
            lesson_id=lesson_id,
            quiz_id=quiz_id,
            skill_category=skill_category,
            certification_id=certification_id,
            data=data or {},
            message=message,
            xp_earned=xp_earned,
        )

        await self.storage.save_event(event)

        if self.on_event:
            self.on_event(event)


# Convenience functions
_trackers: dict[str, ProgressTracker] = {}


def get_progress_tracker(tenant_id: str) -> ProgressTracker:
    """Get or create a progress tracker for a tenant"""
    if tenant_id not in _trackers:
        _trackers[tenant_id] = ProgressTracker(tenant_id)
    return _trackers[tenant_id]


async def enroll_course(
    tenant_id: str,
    farmer_id: str,
    course: Course,
) -> CourseEnrollment:
    """Enroll a farmer in a course"""
    tracker = get_progress_tracker(tenant_id)
    return await tracker.enroll_course(farmer_id, course)


async def complete_lesson(
    tenant_id: str,
    farmer_id: str,
    lesson: Lesson,
    time_spent_minutes: int = 0,
) -> LessonProgress:
    """Complete a lesson"""
    tracker = get_progress_tracker(tenant_id)
    return await tracker.complete_lesson(farmer_id, lesson, time_spent_minutes)


async def submit_quiz(
    tenant_id: str,
    farmer_id: str,
    lesson: Lesson,
    answers: dict[str, Any],
) -> QuizAttempt:
    """Submit quiz answers"""
    tracker = get_progress_tracker(tenant_id)
    return await tracker.submit_quiz(farmer_id, lesson, answers)


async def get_progress_summary(
    tenant_id: str,
    farmer_id: str,
) -> dict[str, Any]:
    """Get progress summary for a farmer"""
    tracker = get_progress_tracker(tenant_id)
    return await tracker.get_progress_summary(farmer_id)
