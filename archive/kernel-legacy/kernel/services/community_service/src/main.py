"""
SAHOOL Community Service - خدمة مجتمع المزارعين
Port: 8102

Provides farmer community features:
- Posts (questions, tips, discussions)
- Comments and replies
- Expert verification
- Search and categories
- Stories
"""

import os
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════

SERVICE_NAME = "sahool-community-service"
SERVICE_PORT = int(os.getenv("PORT", "8102"))

app = FastAPI(
    title="SAHOOL Community Service",
    description="Farmer community and Q&A platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS - Secure configuration
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
try:
    from shared.cors_config import CORS_SETTINGS
    app.add_middleware(CORSMiddleware, **CORS_SETTINGS)
except ImportError:
    ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "https://sahool.io,https://admin.sahool.io,http://localhost:3000").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "X-Tenant-Id"],
    )

# ═══════════════════════════════════════════════════════════════════════════
# Enums & Models
# ═══════════════════════════════════════════════════════════════════════════


class PostCategory(str, Enum):
    GENERAL = "general"
    DISEASES = "diseases"
    IRRIGATION = "irrigation"
    FERTILIZATION = "fertilization"
    MARKETING = "marketing"
    EQUIPMENT = "equipment"
    WEATHER = "weather"
    HARVEST = "harvest"


class UserRole(str, Enum):
    FARMER = "farmer"
    EXPERT = "expert"
    AGRONOMIST = "agronomist"
    VENDOR = "vendor"
    ADMIN = "admin"


class PostCreate(BaseModel):
    """Create a new post"""
    title: str = Field(..., min_length=1, max_length=300)
    title_ar: Optional[str] = None
    content: str = Field(..., min_length=1, max_length=5000)
    content_ar: Optional[str] = None
    category: PostCategory = PostCategory.GENERAL
    image_urls: Optional[list[str]] = None
    field_id: Optional[str] = None
    location: Optional[dict] = None  # {lat, lon}
    tags: Optional[list[str]] = None


class CommentCreate(BaseModel):
    """Create a comment"""
    content: str = Field(..., min_length=1, max_length=2000)
    content_ar: Optional[str] = None
    parent_comment_id: Optional[str] = None


class User(BaseModel):
    """User profile"""
    user_id: str
    name: str
    name_ar: Optional[str] = None
    role: UserRole
    is_verified_expert: bool = False
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    joined_at: datetime
    posts_count: int = 0
    answers_count: int = 0
    helpful_count: int = 0


class Comment(BaseModel):
    """Comment model"""
    comment_id: str
    post_id: str
    author: User
    content: str
    content_ar: Optional[str] = None
    parent_comment_id: Optional[str] = None
    likes_count: int = 0
    is_expert_reply: bool = False
    is_accepted_answer: bool = False
    created_at: datetime
    updated_at: datetime


class Post(BaseModel):
    """Full post model"""
    post_id: str
    tenant_id: str
    author: User
    title: str
    title_ar: Optional[str] = None
    content: str
    content_ar: Optional[str] = None
    category: PostCategory
    image_urls: Optional[list[str]] = None
    field_id: Optional[str] = None
    location: Optional[dict] = None
    tags: Optional[list[str]] = None
    likes_count: int = 0
    comments_count: int = 0
    views_count: int = 0
    has_expert_reply: bool = False
    has_accepted_answer: bool = False
    is_pinned: bool = False
    created_at: datetime
    updated_at: datetime


class Story(BaseModel):
    """Story model (24hr content)"""
    story_id: str
    author: User
    media_url: str
    media_type: str  # image, video
    caption: Optional[str] = None
    views_count: int = 0
    created_at: datetime
    expires_at: datetime


# ═══════════════════════════════════════════════════════════════════════════
# In-Memory Storage (Replace with PostgreSQL in production)
# ═══════════════════════════════════════════════════════════════════════════

users_db: dict[str, User] = {}
posts_db: dict[str, Post] = {}
comments_db: dict[str, Comment] = {}
stories_db: dict[str, Story] = {}
likes_db: dict[str, set] = {}  # post_id -> set of user_ids


def seed_demo_data():
    """Seed demo data for testing"""
    now = datetime.utcnow()

    # Demo users
    demo_users = [
        User(
            user_id="user_hassan",
            name="Hassan Al-Omari",
            name_ar="حسن العمري",
            role=UserRole.FARMER,
            is_verified_expert=False,
            location="صنعاء",
            joined_at=now - timedelta(days=180),
            posts_count=5,
            answers_count=2,
        ),
        User(
            user_id="user_salem",
            name="Eng. Salem",
            name_ar="المهندس سالم",
            role=UserRole.EXPERT,
            is_verified_expert=True,
            bio="خبير زراعي معتمد - متخصص في أمراض النبات",
            location="عدن",
            joined_at=now - timedelta(days=365),
            posts_count=45,
            answers_count=230,
            helpful_count=450,
        ),
        User(
            user_id="user_mohammed",
            name="Mohammed Al-Fallah",
            name_ar="محمد الفلاح",
            role=UserRole.FARMER,
            is_verified_expert=False,
            location="تعز",
            joined_at=now - timedelta(days=90),
            posts_count=3,
            answers_count=5,
        ),
        User(
            user_id="user_fatima",
            name="Eng. Fatima Ahmed",
            name_ar="م. فاطمة أحمد",
            role=UserRole.AGRONOMIST,
            is_verified_expert=True,
            bio="مهندسة زراعية - متخصصة في الري والتسميد",
            location="صنعاء",
            joined_at=now - timedelta(days=200),
            posts_count=28,
            answers_count=156,
            helpful_count=320,
        ),
    ]

    for user in demo_users:
        users_db[user.user_id] = user

    # Demo posts
    demo_posts = [
        Post(
            post_id="post_001",
            tenant_id="tenant_demo",
            author=users_db["user_hassan"],
            title="Yellow spots on tomato leaves",
            title_ar="ظهور بقع صفراء على أوراق الطماطم",
            content="I noticed these spots this morning in greenhouse #3. Is this nutrient deficiency or fungal disease?",
            content_ar="لاحظت هذه البقع اليوم صباحاً في البيت المحمي رقم 3. هل هذا نقص عناصر أم مرض فطري؟",
            category=PostCategory.DISEASES,
            image_urls=["https://example.com/tomato_spots.jpg"],
            tags=["tomato", "disease", "greenhouse"],
            likes_count=12,
            comments_count=5,
            views_count=89,
            has_expert_reply=True,
            created_at=now - timedelta(hours=2),
            updated_at=now - timedelta(hours=1),
        ),
        Post(
            post_id="post_002",
            tenant_id="tenant_demo",
            author=users_db["user_salem"],
            title="Important alert for wheat farmers",
            title_ar="تنبيه هام لمزارعي القمح",
            content="Due to expected temperature drop tonight, please delay morning irrigation until 9 AM to reduce frost impact. Expected temperature: 2°C",
            content_ar="بسبب انخفاض درجات الحرارة المتوقع الليلة، يرجى تأخير رية الصباح حتى الساعة 9 لتقليل أثر الصقيع. درجة الحرارة المتوقعة: 2°C",
            category=PostCategory.WEATHER,
            tags=["wheat", "frost", "irrigation", "alert"],
            likes_count=156,
            comments_count=24,
            views_count=1250,
            is_pinned=True,
            created_at=now - timedelta(hours=5),
            updated_at=now - timedelta(hours=5),
        ),
        Post(
            post_id="post_003",
            tenant_id="tenant_demo",
            author=users_db["user_mohammed"],
            title="Best fertilizer for potatoes",
            title_ar="أفضل سماد للبطاطس",
            content="What is the best NPK compound for tuber formation stage? I want to increase tuber size. Crop is 60 days old.",
            content_ar="ما هو أفضل مركب NPK لمرحلة التدرن؟ أريد زيادة حجم الدرنات. المحصول عمره 60 يوم.",
            category=PostCategory.FERTILIZATION,
            tags=["potato", "fertilizer", "NPK"],
            likes_count=3,
            comments_count=8,
            views_count=45,
            has_expert_reply=False,
            created_at=now - timedelta(days=1),
            updated_at=now - timedelta(hours=12),
        ),
        Post(
            post_id="post_004",
            tenant_id="tenant_demo",
            author=users_db["user_fatima"],
            title="Drip irrigation tips for summer",
            title_ar="نصائح للري بالتنقيط في الصيف",
            content="With rising temperatures, here are some tips to improve irrigation efficiency:\n• Increase irrigation frequency while reducing quantity\n• Irrigate early morning or evening\n• Check filters weekly",
            content_ar="مع ارتفاع درجات الحرارة، إليكم بعض النصائح لتحسين كفاءة الري:\n• زيادة عدد الريات مع تقليل الكمية\n• الري في الصباح الباكر أو المساء\n• فحص الفلاتر أسبوعياً",
            category=PostCategory.IRRIGATION,
            tags=["drip", "irrigation", "summer", "tips"],
            likes_count=231,
            comments_count=42,
            views_count=1890,
            created_at=now - timedelta(days=1),
            updated_at=now - timedelta(days=1),
        ),
    ]

    for post in demo_posts:
        posts_db[post.post_id] = post

    # Demo comments
    demo_comments = [
        Comment(
            comment_id="comment_001",
            post_id="post_001",
            author=users_db["user_salem"],
            content="These are symptoms of magnesium deficiency. I recommend spraying foliar fertilizer containing 2% magnesium.",
            content_ar="هذه أعراض نقص المغنيسيوم. أنصح برش سماد ورقي يحتوي على 2% مغنيسيوم.",
            likes_count=8,
            is_expert_reply=True,
            is_accepted_answer=True,
            created_at=now - timedelta(hours=1),
            updated_at=now - timedelta(hours=1),
        ),
        Comment(
            comment_id="comment_002",
            post_id="post_001",
            author=users_db["user_mohammed"],
            content="Same thing happened to me last season. The engineer's advice is correct.",
            content_ar="حصل معي نفس الشيء الموسم الماضي. نصيحة المهندس صحيحة.",
            likes_count=2,
            is_expert_reply=False,
            created_at=now - timedelta(minutes=30),
            updated_at=now - timedelta(minutes=30),
        ),
    ]

    for comment in demo_comments:
        comments_db[comment.comment_id] = comment

    # Demo stories
    demo_stories = [
        Story(
            story_id="story_001",
            author=users_db["user_salem"],
            media_url="https://example.com/story1.jpg",
            media_type="image",
            caption="Field inspection today",
            views_count=45,
            created_at=now - timedelta(hours=3),
            expires_at=now + timedelta(hours=21),
        ),
        Story(
            story_id="story_002",
            author=users_db["user_fatima"],
            media_url="https://example.com/story2.jpg",
            media_type="image",
            caption="New irrigation system installation",
            views_count=78,
            created_at=now - timedelta(hours=8),
            expires_at=now + timedelta(hours=16),
        ),
    ]

    for story in demo_stories:
        stories_db[story.story_id] = story


# Seed on startup
seed_demo_data()


# ═══════════════════════════════════════════════════════════════════════════
# Helper Functions
# ═══════════════════════════════════════════════════════════════════════════


def get_tenant_id(x_tenant_id: str = "tenant_demo") -> str:
    """Extract tenant ID from header (simplified)"""
    return x_tenant_id


def get_current_user_id(x_user_id: str = "user_hassan") -> str:
    """Get current user ID (simplified - would use auth in production)"""
    return x_user_id


# ═══════════════════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════════════════


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": SERVICE_NAME}


# ─────────────────────────────────────────────────────────────────
# Posts
# ─────────────────────────────────────────────────────────────────


@app.get("/api/v1/posts", response_model=dict)
async def list_posts(
    category: Optional[PostCategory] = Query(None, description="Filter by category"),
    author_id: Optional[str] = Query(None, description="Filter by author"),
    has_expert_reply: Optional[bool] = Query(None, description="Filter by expert reply"),
    search: Optional[str] = Query(None, description="Search in title and content"),
    sort_by: str = Query("recent", description="Sort: recent, popular, unanswered"),
    limit: int = Query(20, ge=1, le=50),
    offset: int = Query(0, ge=0),
    tenant_id: str = Depends(get_tenant_id),
):
    """List posts with filters"""
    filtered = [p for p in posts_db.values() if p.tenant_id == tenant_id]

    if category:
        filtered = [p for p in filtered if p.category == category]
    if author_id:
        filtered = [p for p in filtered if p.author.user_id == author_id]
    if has_expert_reply is not None:
        filtered = [p for p in filtered if p.has_expert_reply == has_expert_reply]
    if search:
        search_lower = search.lower()
        filtered = [
            p for p in filtered
            if search_lower in p.title.lower()
            or search_lower in p.content.lower()
            or (p.title_ar and search_lower in p.title_ar)
            or (p.content_ar and search_lower in p.content_ar)
        ]

    # Sort
    if sort_by == "popular":
        filtered.sort(key=lambda p: (p.likes_count + p.comments_count * 2), reverse=True)
    elif sort_by == "unanswered":
        filtered = [p for p in filtered if not p.has_expert_reply]
        filtered.sort(key=lambda p: p.created_at, reverse=True)
    else:  # recent
        # Pinned posts first, then by date
        filtered.sort(key=lambda p: (not p.is_pinned, p.created_at), reverse=True)

    total = len(filtered)
    paginated = filtered[offset:offset + limit]

    return {
        "posts": [p.model_dump() for p in paginated],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@app.get("/api/v1/posts/{post_id}", response_model=Post)
async def get_post(
    post_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Get a post by ID"""
    post = posts_db.get(post_id)
    if not post or post.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Post not found")

    # Increment views
    post.views_count += 1
    posts_db[post_id] = post

    return post


@app.post("/api/v1/posts", response_model=Post, status_code=201)
async def create_post(
    data: PostCreate,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user_id),
):
    """Create a new post"""
    now = datetime.utcnow()
    post_id = f"post_{uuid.uuid4().hex[:8]}"

    author = users_db.get(user_id)
    if not author:
        # Create a basic user if not found
        author = User(
            user_id=user_id,
            name="Unknown User",
            role=UserRole.FARMER,
            joined_at=now,
        )
        users_db[user_id] = author

    post = Post(
        post_id=post_id,
        tenant_id=tenant_id,
        author=author,
        title=data.title,
        title_ar=data.title_ar,
        content=data.content,
        content_ar=data.content_ar,
        category=data.category,
        image_urls=data.image_urls,
        field_id=data.field_id,
        location=data.location,
        tags=data.tags,
        created_at=now,
        updated_at=now,
    )

    posts_db[post_id] = post

    # Update author's post count
    author.posts_count += 1
    users_db[user_id] = author

    return post


@app.post("/api/v1/posts/{post_id}/like", response_model=dict)
async def like_post(
    post_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user_id),
):
    """Like/unlike a post"""
    post = posts_db.get(post_id)
    if not post or post.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Post not found")

    if post_id not in likes_db:
        likes_db[post_id] = set()

    if user_id in likes_db[post_id]:
        # Unlike
        likes_db[post_id].remove(user_id)
        post.likes_count = max(0, post.likes_count - 1)
        liked = False
    else:
        # Like
        likes_db[post_id].add(user_id)
        post.likes_count += 1
        liked = True

    posts_db[post_id] = post

    return {"liked": liked, "likes_count": post.likes_count}


@app.delete("/api/v1/posts/{post_id}", status_code=204)
async def delete_post(
    post_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user_id),
):
    """Delete a post (author only)"""
    post = posts_db.get(post_id)
    if not post or post.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.author.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    del posts_db[post_id]


# ─────────────────────────────────────────────────────────────────
# Comments
# ─────────────────────────────────────────────────────────────────


@app.get("/api/v1/posts/{post_id}/comments", response_model=dict)
async def get_comments(
    post_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tenant_id: str = Depends(get_tenant_id),
):
    """Get comments for a post"""
    post = posts_db.get(post_id)
    if not post or post.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Post not found")

    comments = [c for c in comments_db.values() if c.post_id == post_id]

    # Sort: accepted answer first, then expert replies, then by date
    comments.sort(key=lambda c: (
        not c.is_accepted_answer,
        not c.is_expert_reply,
        c.created_at
    ))

    total = len(comments)
    paginated = comments[offset:offset + limit]

    return {
        "comments": [c.model_dump() for c in paginated],
        "total": total,
    }


@app.post("/api/v1/posts/{post_id}/comments", response_model=Comment, status_code=201)
async def create_comment(
    post_id: str,
    data: CommentCreate,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user_id),
):
    """Add a comment to a post"""
    post = posts_db.get(post_id)
    if not post or post.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Post not found")

    now = datetime.utcnow()
    comment_id = f"comment_{uuid.uuid4().hex[:8]}"

    author = users_db.get(user_id)
    if not author:
        author = User(
            user_id=user_id,
            name="Unknown User",
            role=UserRole.FARMER,
            joined_at=now,
        )
        users_db[user_id] = author

    is_expert = author.is_verified_expert

    comment = Comment(
        comment_id=comment_id,
        post_id=post_id,
        author=author,
        content=data.content,
        content_ar=data.content_ar,
        parent_comment_id=data.parent_comment_id,
        is_expert_reply=is_expert,
        created_at=now,
        updated_at=now,
    )

    comments_db[comment_id] = comment

    # Update post
    post.comments_count += 1
    if is_expert:
        post.has_expert_reply = True
    post.updated_at = now
    posts_db[post_id] = post

    # Update author's answer count
    author.answers_count += 1
    users_db[user_id] = author

    return comment


@app.post("/api/v1/comments/{comment_id}/accept", response_model=Comment)
async def accept_answer(
    comment_id: str,
    tenant_id: str = Depends(get_tenant_id),
    user_id: str = Depends(get_current_user_id),
):
    """Accept a comment as the answer (post author only)"""
    comment = comments_db.get(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    post = posts_db.get(comment.post_id)
    if not post or post.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.author.user_id != user_id:
        raise HTTPException(status_code=403, detail="Only post author can accept answers")

    # Unaccept other answers
    for c in comments_db.values():
        if c.post_id == comment.post_id and c.is_accepted_answer:
            c.is_accepted_answer = False
            comments_db[c.comment_id] = c

    # Accept this answer
    comment.is_accepted_answer = True
    comment.updated_at = datetime.utcnow()
    comments_db[comment_id] = comment

    # Update post
    post.has_accepted_answer = True
    posts_db[post.post_id] = post

    # Give helpful points to comment author
    comment.author.helpful_count += 1
    users_db[comment.author.user_id] = comment.author

    return comment


@app.post("/api/v1/comments/{comment_id}/like", response_model=dict)
async def like_comment(
    comment_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Like a comment"""
    comment = comments_db.get(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment.likes_count += 1
    comments_db[comment_id] = comment

    return {"likes_count": comment.likes_count}


# ─────────────────────────────────────────────────────────────────
# Stories
# ─────────────────────────────────────────────────────────────────


@app.get("/api/v1/stories", response_model=dict)
async def get_stories(
    tenant_id: str = Depends(get_tenant_id),
):
    """Get active stories (not expired)"""
    now = datetime.utcnow()
    active_stories = [
        s for s in stories_db.values()
        if s.expires_at > now
    ]
    active_stories.sort(key=lambda s: s.created_at, reverse=True)

    return {
        "stories": [s.model_dump() for s in active_stories],
        "count": len(active_stories),
    }


@app.post("/api/v1/stories", response_model=Story, status_code=201)
async def create_story(
    media_url: str = Query(...),
    media_type: str = Query("image"),
    caption: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
):
    """Create a new story"""
    now = datetime.utcnow()
    story_id = f"story_{uuid.uuid4().hex[:8]}"

    author = users_db.get(user_id)
    if not author:
        author = User(
            user_id=user_id,
            name="Unknown User",
            role=UserRole.FARMER,
            joined_at=now,
        )
        users_db[user_id] = author

    story = Story(
        story_id=story_id,
        author=author,
        media_url=media_url,
        media_type=media_type,
        caption=caption,
        created_at=now,
        expires_at=now + timedelta(hours=24),
    )

    stories_db[story_id] = story
    return story


@app.post("/api/v1/stories/{story_id}/view", response_model=dict)
async def view_story(
    story_id: str,
):
    """Mark story as viewed"""
    story = stories_db.get(story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    story.views_count += 1
    stories_db[story_id] = story

    return {"views_count": story.views_count}


# ─────────────────────────────────────────────────────────────────
# Users/Experts
# ─────────────────────────────────────────────────────────────────


@app.get("/api/v1/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get user profile"""
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.get("/api/v1/experts", response_model=dict)
async def list_experts():
    """List verified experts"""
    experts = [u for u in users_db.values() if u.is_verified_expert]
    experts.sort(key=lambda u: u.helpful_count, reverse=True)

    return {
        "experts": [e.model_dump() for e in experts],
        "count": len(experts),
    }


@app.get("/api/v1/search", response_model=dict)
async def search(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=50),
    tenant_id: str = Depends(get_tenant_id),
):
    """Search posts, users, and tags"""
    q_lower = q.lower()

    # Search posts
    matching_posts = [
        p for p in posts_db.values()
        if p.tenant_id == tenant_id and (
            q_lower in p.title.lower()
            or q_lower in p.content.lower()
            or (p.title_ar and q_lower in p.title_ar)
            or any(q_lower in tag.lower() for tag in (p.tags or []))
        )
    ][:limit]

    # Search users
    matching_users = [
        u for u in users_db.values()
        if q_lower in u.name.lower()
        or (u.name_ar and q_lower in u.name_ar)
    ][:10]

    return {
        "posts": [p.model_dump() for p in matching_posts],
        "users": [u.model_dump() for u in matching_users],
        "query": q,
    }


# ═══════════════════════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SERVICE_PORT)
