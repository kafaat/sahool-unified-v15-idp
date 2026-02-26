# shared/learning_marketplace

Educational content marketplace for the SAHOOL platform. Provides structured learning
management for farmers: course browsing, enrollment, lesson progress tracking, quiz
assessment, gamification (XP and streaks), certifications, and personalized recommendations.

## File Structure

```
shared/learning_marketplace/
├── __init__.py          # Public API exports
├── models.py            # Course, lesson, farmer profile, certification data classes
├── progress.py          # Enrollment, lesson tracking, quiz attempts, XP rewards
└── recommendations.py   # Personalized course and learning path recommendations
```

## Key Components

### models.py

Domain entities for the learning system.

**Content types (`ContentType`):**
VIDEO, PDF, INTERACTIVE, QUIZ, ARTICLE, INFOGRAPHIC, AUDIO, SIMULATION.

**Skill categories (`SkillCategory`):**
IRRIGATION, PEST_MANAGEMENT, DISEASE_CONTROL, SOIL_HEALTH, FERTILIZATION,
CROP_MANAGEMENT, MACHINERY, SAFETY, BUSINESS, DIGITAL_TOOLS, WATER_CONSERVATION.

**Course difficulty levels (`DifficultyLevel`):**
BEGINNER, INTERMEDIATE, ADVANCED, EXPERT.

**Core data classes:**

| Class | Purpose |
|-------|---------|
| `Course` | Full course with modules, estimated duration, language, XP value |
| `CourseModule` | Ordered section within a course |
| `Lesson` | Individual lesson with content resource references |
| `ContentResource` | URL/path to video, PDF, or interactive content |
| `Quiz` | Quiz with passing score, max attempts, XP on pass |
| `QuizQuestion` | MCQ, true/false, or open-text question with bilingual text |
| `Expert` | Content author with specialization tags |
| `Certification` | Certification offered upon course completion |
| `FarmerCertification` | Earned certification linked to a farmer and enrollment |
| `FarmerSkill` | Skill record with level (0-100) and XP for a category |
| `FarmerProfile` | Farmer learning profile: skills, crops, language, learning goals |
| `BilingualText` | Arabic/English text pair used throughout the module |

Enumerations: `CourseStatus` (DRAFT, REVIEW, PUBLISHED, ARCHIVED, SUSPENDED),
`EnrollmentStatus` (ENROLLED, IN_PROGRESS, COMPLETED, DROPPED, EXPIRED),
`ContentLanguage` (ARABIC, ENGLISH, BILINGUAL).

### progress.py

Tracks farmer progress through courses and manages gamification rewards.

**XP reward table (`XP_REWARDS`):**

| Event | XP |
|-------|----|
| Lesson completed | 10 |
| Quiz passed | 25 |
| Course completed | 100 |
| Perfect quiz score | 50 |
| Streak (7 days) | 75 |
| Certification earned | 200 |

**Core classes:**

| Class | Purpose |
|-------|---------|
| `LessonProgress` | Per-lesson tracking: completion, time spent, video position |
| `QuizAttempt` | Quiz result with score, pass/fail, XP earned |
| `CourseEnrollment` | Enrollment record with completion percentage and streak tracking |
| `ProgressEvent` | Audit event for any progress action |
| `ProgressStorage` | Persistence layer (file-based; swap for DB adapter) |
| `ProgressTracker` | Main service: enroll, complete lessons, submit quizzes, summary |

**Convenience functions:**

| Function | Description |
|----------|-------------|
| `get_progress_tracker(tenant_id)` | Returns tenant-scoped tracker |
| `enroll_course(farmer_id, course_id)` | Creates enrollment, fires ENROLLMENT event |
| `complete_lesson(farmer_id, lesson_id, course_id)` | Marks lesson done, awards XP |
| `submit_quiz(farmer_id, quiz_id, answers)` | Grades quiz, updates skill levels |
| `get_progress_summary(farmer_id, tenant_id)` | Returns aggregated stats |

### recommendations.py

Personalized content recommendations using multi-factor scoring.

**Recommendation reasons (`RecommendationReason`):**
SKILL_GAP, NEXT_LEVEL, POPULAR, TRENDING, SIMILAR_FARMERS, CROP_RELEVANT,
SEASONAL, PREREQUISITE, CONTINUATION, CERTIFICATION_PATH, PERSONALIZED, BEGINNER_FRIENDLY.

**Scoring dimensions (`RecommendationScore`):**
relevance, difficulty_match, skill_gap, popularity, freshness, completion_likelihood.

**Constants:**
- `CROP_SKILL_MAPPING` - maps crop types to relevant skill categories
- `SEASONAL_TOPICS` - maps months to recommended topic areas

| Class | Description |
|-------|-------------|
| `CourseRecommendation` | Recommended course with score and primary reason |
| `LearningPath` | Ordered sequence of courses toward a skill goal |
| `ContentRecommender` | Generates ranked recommendations for a farmer profile |

**Convenience functions:**

| Function | Description |
|----------|-------------|
| `get_recommendations(tenant_id, profile, catalog, limit)` | Ranked course list |
| `get_learning_path(tenant_id, profile, target_skill, catalog)` | Ordered learning path |
| `get_content_recommender(tenant_id)` | Returns tenant-scoped recommender |

## Usage Example

```python
from shared.learning_marketplace import (
    Course,
    BilingualText,
    DifficultyLevel,
    SkillCategory,
    FarmerProfile,
    FarmerSkill,
    get_progress_tracker,
    get_recommendations,
    get_learning_path,
)

# Farmer learning profile
profile = FarmerProfile(
    farmer_id="farmer_001",
    tenant_id="tenant_001",
    primary_crops=["wheat", "barley"],
    preferred_language="ar",
    skills=[
        FarmerSkill(category=SkillCategory.IRRIGATION, level=35, xp=350),
        FarmerSkill(category=SkillCategory.SOIL_HEALTH, level=20, xp=200),
    ],
)

# Enroll and track progress
tracker = get_progress_tracker("tenant_001")
enrollment = await tracker.enroll_course("farmer_001", course_id="COURSE-IRR-101")

await tracker.complete_lesson(
    farmer_id="farmer_001",
    lesson_id="LES-001",
    course_id="COURSE-IRR-101",
    time_spent_minutes=12,
)

attempt = await tracker.submit_quiz(
    farmer_id="farmer_001",
    quiz_id="QUIZ-IRR-001",
    answers={"q1": "b", "q2": "true", "q3": "drip"},
)
print(f"Score: {attempt.score}%, Passed: {attempt.passed}, XP: {attempt.xp_earned}")

# Personalized recommendations
courses_catalog = [...]  # list of published Course objects
recommendations = await get_recommendations(
    tenant_id="tenant_001",
    farmer_profile=profile,
    courses_catalog=courses_catalog,
    limit=5,
)
for rec in recommendations:
    print(f"{rec.course.title.ar} - {rec.reason}")

# Build a learning path toward advanced irrigation
path = await get_learning_path(
    tenant_id="tenant_001",
    farmer_profile=profile,
    target_skill=SkillCategory.IRRIGATION,
    courses_catalog=courses_catalog,
)
print(f"Path: {[c.title.en for c in path.courses]}")
```
