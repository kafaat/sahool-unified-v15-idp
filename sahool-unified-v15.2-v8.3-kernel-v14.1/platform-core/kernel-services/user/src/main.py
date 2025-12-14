"""
SAHOOL User Service - User Management
=====================================
Layer: Platform Core (Layer 1)
Purpose: User profile management, preferences, and user-related operations
"""

import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import uuid

from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, ForeignKey, select, update, delete, func
from sqlalchemy.orm import relationship, selectinload
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import structlog
import enum

# Shared imports
import sys
sys.path.insert(0, '/app/shared')
from database import Database, BaseModel as DBBaseModel  # noqa: E402
from events.base_event import EventBus  # noqa: E402
from utils.logging import setup_logging  # noqa: E402


# ============================================================================
# Configuration
# ============================================================================

class Settings:
    """User service configuration"""
    SERVICE_NAME = "user-service"
    SERVICE_PORT = int(os.getenv("USER_SERVICE_PORT", "8083"))
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://sahool:sahool@postgres:5432/sahool_users")
    NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")
    
    # File Storage
    AVATAR_UPLOAD_PATH = os.getenv("AVATAR_UPLOAD_PATH", "/app/uploads/avatars")
    MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5MB
    
    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

settings = Settings()

# ============================================================================
# Logging & Metrics
# ============================================================================

setup_logging(settings.SERVICE_NAME)
logger = structlog.get_logger()

user_operations = Counter('user_operations_total', 'User operations', ['operation', 'status'])
user_latency = Histogram('user_operation_latency_seconds', 'User operation latency')

# ============================================================================
# Database Models
# ============================================================================

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"

class User(DBBaseModel):
    """Extended user profile"""
    __tablename__ = "user_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auth_user_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)  # Link to auth service
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Profile Info
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True, index=True)
    full_name = Column(String(255), nullable=False)
    full_name_ar = Column(String(255), nullable=True)
    
    # Extended Profile
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    bio_ar = Column(Text, nullable=True)
    job_title = Column(String(100), nullable=True)
    job_title_ar = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    
    # Location
    country = Column(String(100), default="Yemen")
    region = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    
    # Preferences
    preferred_language = Column(String(10), default="ar")
    timezone = Column(String(50), default="Asia/Aden")
    date_format = Column(String(20), default="DD/MM/YYYY")
    time_format = Column(String(10), default="24h")
    
    # Notification Preferences
    notification_channels = Column(ARRAY(String), default=["push", "in_app"])
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    push_notifications = Column(Boolean, default=True)
    
    # App Preferences
    app_settings = Column(JSON, default={})
    dashboard_layout = Column(JSON, nullable=True)
    
    # Status
    status = Column(String(20), default=UserStatus.ACTIVE.value)
    
    # Metadata
    last_activity = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assigned_fields = relationship("UserFieldAssignment", back_populates="user", cascade="all, delete-orphan")

class UserFieldAssignment(DBBaseModel):
    """User-Field assignment for access control"""
    __tablename__ = "user_field_assignments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user_profiles.id', ondelete='CASCADE'), nullable=False)
    field_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Access level
    access_level = Column(String(20), default="read")  # read, write, manage
    
    # Metadata
    assigned_by = Column(UUID(as_uuid=True), nullable=True)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="assigned_fields")

class UserActivity(DBBaseModel):
    """User activity log"""
    __tablename__ = "user_activities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    activity_type = Column(String(50), nullable=False)  # login, task_completed, field_viewed, etc.
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

class UserNotificationPreference(DBBaseModel):
    """Detailed notification preferences per event type"""
    __tablename__ = "user_notification_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    event_type = Column(String(100), nullable=False)  # task.assigned, alert.created, etc.
    
    # Channels enabled for this event type
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    push_enabled = Column(Boolean, default=True)
    in_app_enabled = Column(Boolean, default=True)
    
    # Quiet hours
    quiet_start = Column(String(5), nullable=True)  # HH:MM
    quiet_end = Column(String(5), nullable=True)    # HH:MM
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ============================================================================
# Pydantic Schemas
# ============================================================================

class UserProfileBase(BaseModel):
    """Base user profile schema"""
    full_name: str = Field(..., min_length=2, max_length=255)
    full_name_ar: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    bio_ar: Optional[str] = None
    job_title: Optional[str] = None
    job_title_ar: Optional[str] = None
    department: Optional[str] = None
    country: str = "Yemen"
    region: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None

class UserProfileCreate(UserProfileBase):
    """Create user profile"""
    auth_user_id: uuid.UUID
    tenant_id: uuid.UUID
    email: EmailStr

class UserProfileUpdate(BaseModel):
    """Update user profile"""
    full_name: Optional[str] = None
    full_name_ar: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    bio_ar: Optional[str] = None
    job_title: Optional[str] = None
    job_title_ar: Optional[str] = None
    department: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    avatar_url: Optional[str] = None

class UserPreferencesUpdate(BaseModel):
    """Update user preferences"""
    preferred_language: Optional[str] = None
    timezone: Optional[str] = None
    date_format: Optional[str] = None
    time_format: Optional[str] = None
    notification_channels: Optional[List[str]] = None
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    app_settings: Optional[Dict[str, Any]] = None
    dashboard_layout: Optional[Dict[str, Any]] = None

class UserProfileResponse(BaseModel):
    """User profile response"""
    id: uuid.UUID
    auth_user_id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    phone: Optional[str]
    full_name: str
    full_name_ar: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    bio_ar: Optional[str]
    job_title: Optional[str]
    job_title_ar: Optional[str]
    department: Optional[str]
    country: str
    region: Optional[str]
    city: Optional[str]
    address: Optional[str]
    preferred_language: str
    timezone: str
    date_format: str
    time_format: str
    notification_channels: List[str]
    email_notifications: bool
    sms_notifications: bool
    push_notifications: bool
    status: str
    last_activity: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    """Paginated user list"""
    items: List[UserProfileResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class FieldAssignmentCreate(BaseModel):
    """Create field assignment"""
    field_id: uuid.UUID
    access_level: str = "read"

class FieldAssignmentResponse(BaseModel):
    """Field assignment response"""
    id: uuid.UUID
    field_id: uuid.UUID
    access_level: str
    assigned_by: Optional[uuid.UUID]
    assigned_at: datetime
    
    class Config:
        from_attributes = True

class NotificationPreferenceCreate(BaseModel):
    """Create notification preference"""
    event_type: str
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = True
    in_app_enabled: bool = True
    quiet_start: Optional[str] = None
    quiet_end: Optional[str] = None

class NotificationPreferenceResponse(BaseModel):
    """Notification preference response"""
    id: uuid.UUID
    event_type: str
    email_enabled: bool
    sms_enabled: bool
    push_enabled: bool
    in_app_enabled: bool
    quiet_start: Optional[str]
    quiet_end: Optional[str]
    
    class Config:
        from_attributes = True

class ActivityLogResponse(BaseModel):
    """Activity log response"""
    id: uuid.UUID
    activity_type: str
    resource_type: Optional[str]
    resource_id: Optional[uuid.UUID]
    details: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============================================================================
# User Service
# ============================================================================

class UserService:
    """Core user management service"""
    
    def __init__(self, db: Database, event_bus: EventBus):
        self.db = db
        self.event_bus = event_bus
    
    async def create_profile(self, data: UserProfileCreate) -> User:
        """Create user profile"""
        async with self.db.session() as session:
            # Check if profile exists
            existing = await session.execute(
                select(User).where(User.auth_user_id == data.auth_user_id)
            )
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Profile already exists for this user"
                )
            
            profile = User(
                auth_user_id=data.auth_user_id,
                tenant_id=data.tenant_id,
                email=data.email,
                full_name=data.full_name,
                full_name_ar=data.full_name_ar,
                phone=data.phone,
                bio=data.bio,
                bio_ar=data.bio_ar,
                job_title=data.job_title,
                job_title_ar=data.job_title_ar,
                department=data.department,
                country=data.country,
                region=data.region,
                city=data.city,
                address=data.address
            )
            
            session.add(profile)
            await session.commit()
            await session.refresh(profile)
            
            # Emit event
            await self.event_bus.publish(
                "user.profile.created",
                {
                    "user_id": str(profile.id),
                    "auth_user_id": str(profile.auth_user_id),
                    "tenant_id": str(profile.tenant_id)
                }
            )
            
            logger.info("User profile created", user_id=str(profile.id))
            return profile
    
    async def get_profile(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user profile by ID"""
        async with self.db.session() as session:
            result = await session.execute(
                select(User)
                .options(selectinload(User.assigned_fields))
                .where(User.id == user_id)
            )
            return result.scalar_one_or_none()
    
    async def get_profile_by_auth_id(self, auth_user_id: uuid.UUID) -> Optional[User]:
        """Get user profile by auth user ID"""
        async with self.db.session() as session:
            result = await session.execute(
                select(User)
                .options(selectinload(User.assigned_fields))
                .where(User.auth_user_id == auth_user_id)
            )
            return result.scalar_one_or_none()
    
    async def update_profile(self, user_id: uuid.UUID, data: UserProfileUpdate) -> User:
        """Update user profile"""
        async with self.db.session() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            profile = result.scalar_one_or_none()
            
            if not profile:
                raise HTTPException(status_code=404, detail="User not found")
            
            update_data = data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(profile, key, value)
            
            profile.updated_at = datetime.utcnow()
            
            await session.commit()
            await session.refresh(profile)
            
            # Emit event
            await self.event_bus.publish(
                "user.profile.updated",
                {
                    "user_id": str(profile.id),
                    "updated_fields": list(update_data.keys())
                }
            )
            
            return profile
    
    async def update_preferences(self, user_id: uuid.UUID, data: UserPreferencesUpdate) -> User:
        """Update user preferences"""
        async with self.db.session() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            profile = result.scalar_one_or_none()
            
            if not profile:
                raise HTTPException(status_code=404, detail="User not found")
            
            update_data = data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(profile, key, value)
            
            profile.updated_at = datetime.utcnow()
            
            await session.commit()
            await session.refresh(profile)
            
            return profile
    
    async def list_users(
        self,
        tenant_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        status_filter: Optional[str] = None,
        department: Optional[str] = None
    ) -> tuple[List[User], int]:
        """List users with pagination and filters"""
        async with self.db.session() as session:
            query = select(User).where(User.tenant_id == tenant_id)
            count_query = select(func.count(User.id)).where(User.tenant_id == tenant_id)
            
            if search:
                search_filter = f"%{search}%"
                query = query.where(
                    (User.full_name.ilike(search_filter)) |
                    (User.full_name_ar.ilike(search_filter)) |
                    (User.email.ilike(search_filter)) |
                    (User.phone.ilike(search_filter))
                )
                count_query = count_query.where(
                    (User.full_name.ilike(search_filter)) |
                    (User.full_name_ar.ilike(search_filter)) |
                    (User.email.ilike(search_filter)) |
                    (User.phone.ilike(search_filter))
                )
            
            if status_filter:
                query = query.where(User.status == status_filter)
                count_query = count_query.where(User.status == status_filter)
            
            if department:
                query = query.where(User.department == department)
                count_query = count_query.where(User.department == department)
            
            # Get total count
            total_result = await session.execute(count_query)
            total = total_result.scalar()
            
            # Apply pagination
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size).order_by(User.created_at.desc())
            
            result = await session.execute(query)
            users = result.scalars().all()
            
            return users, total
    
    async def assign_field(
        self,
        user_id: uuid.UUID,
        field_id: uuid.UUID,
        access_level: str,
        assigned_by: uuid.UUID
    ) -> UserFieldAssignment:
        """Assign field to user"""
        async with self.db.session() as session:
            # Check if assignment exists
            existing = await session.execute(
                select(UserFieldAssignment).where(
                    UserFieldAssignment.user_id == user_id,
                    UserFieldAssignment.field_id == field_id
                )
            )
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Field already assigned to user"
                )
            
            assignment = UserFieldAssignment(
                user_id=user_id,
                field_id=field_id,
                access_level=access_level,
                assigned_by=assigned_by
            )
            
            session.add(assignment)
            await session.commit()
            await session.refresh(assignment)
            
            # Emit event
            await self.event_bus.publish(
                "user.field.assigned",
                {
                    "user_id": str(user_id),
                    "field_id": str(field_id),
                    "access_level": access_level
                }
            )
            
            return assignment
    
    async def remove_field_assignment(self, user_id: uuid.UUID, field_id: uuid.UUID):
        """Remove field assignment"""
        async with self.db.session() as session:
            result = await session.execute(
                select(UserFieldAssignment).where(
                    UserFieldAssignment.user_id == user_id,
                    UserFieldAssignment.field_id == field_id
                )
            )
            assignment = result.scalar_one_or_none()
            
            if not assignment:
                raise HTTPException(status_code=404, detail="Assignment not found")
            
            await session.delete(assignment)
            await session.commit()
            
            # Emit event
            await self.event_bus.publish(
                "user.field.unassigned",
                {
                    "user_id": str(user_id),
                    "field_id": str(field_id)
                }
            )
    
    async def log_activity(
        self,
        user_id: uuid.UUID,
        tenant_id: uuid.UUID,
        activity_type: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[uuid.UUID] = None,
        details: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log user activity"""
        async with self.db.session() as session:
            activity = UserActivity(
                user_id=user_id,
                tenant_id=tenant_id,
                activity_type=activity_type,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            session.add(activity)
            
            # Update last activity
            await session.execute(
                update(User)
                .where(User.id == user_id)
                .values(last_activity=datetime.utcnow())
            )
            
            await session.commit()
    
    async def get_activities(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
        activity_type: Optional[str] = None
    ) -> List[UserActivity]:
        """Get user activities"""
        async with self.db.session() as session:
            query = select(UserActivity).where(UserActivity.user_id == user_id)
            
            if activity_type:
                query = query.where(UserActivity.activity_type == activity_type)
            
            query = query.order_by(UserActivity.created_at.desc()).limit(limit)
            
            result = await session.execute(query)
            return result.scalars().all()
    
    async def set_notification_preferences(
        self,
        user_id: uuid.UUID,
        preferences: List[NotificationPreferenceCreate]
    ):
        """Set notification preferences for user"""
        async with self.db.session() as session:
            # Delete existing preferences
            await session.execute(
                delete(UserNotificationPreference).where(
                    UserNotificationPreference.user_id == user_id
                )
            )
            
            # Create new preferences
            for pref in preferences:
                np = UserNotificationPreference(
                    user_id=user_id,
                    event_type=pref.event_type,
                    email_enabled=pref.email_enabled,
                    sms_enabled=pref.sms_enabled,
                    push_enabled=pref.push_enabled,
                    in_app_enabled=pref.in_app_enabled,
                    quiet_start=pref.quiet_start,
                    quiet_end=pref.quiet_end
                )
                session.add(np)
            
            await session.commit()
    
    async def get_notification_preferences(
        self,
        user_id: uuid.UUID
    ) -> List[UserNotificationPreference]:
        """Get user notification preferences"""
        async with self.db.session() as session:
            result = await session.execute(
                select(UserNotificationPreference).where(
                    UserNotificationPreference.user_id == user_id
                )
            )
            return result.scalars().all()
    
    async def deactivate_user(self, user_id: uuid.UUID, reason: Optional[str] = None):
        """Deactivate user"""
        async with self.db.session() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            user.status = UserStatus.INACTIVE.value
            await session.commit()
            
            # Emit event
            await self.event_bus.publish(
                "user.deactivated",
                {
                    "user_id": str(user_id),
                    "tenant_id": str(user.tenant_id),
                    "reason": reason
                }
            )

# ============================================================================
# Event Handlers
# ============================================================================

async def handle_user_registered(event: Dict[str, Any], service: UserService):
    """Handle user registered event from auth service"""
    try:
        await service.create_profile(UserProfileCreate(
            auth_user_id=uuid.UUID(event["user_id"]),
            tenant_id=uuid.UUID(event["tenant_id"]),
            email=event["email"],
            full_name=event.get("full_name", "New User")
        ))
    except Exception as e:
        logger.error("Failed to create profile for registered user", error=str(e))

# ============================================================================
# Dependencies
# ============================================================================

db: Database = None
event_bus: EventBus = None
user_service: UserService = None

# ============================================================================
# FastAPI Application
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global db, event_bus, user_service
    
    logger.info("Starting User Service...")
    
    # Initialize database
    db = Database(settings.DATABASE_URL)
    await db.connect()
    
    # Initialize Event Bus
    event_bus = EventBus(settings.NATS_URL)
    await event_bus.connect()
    
    # Initialize User Service
    user_service = UserService(db, event_bus)
    
    # Subscribe to events
    await event_bus.subscribe(
        "auth.user.registered",
        lambda e: handle_user_registered(e, user_service)
    )
    
    logger.info("User Service started successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down User Service...")
    await event_bus.close()
    await db.disconnect()

app = FastAPI(
    title="SAHOOL User Service",
    description="User Profile and Management Service",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.SERVICE_NAME}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Profile Endpoints
@app.post("/api/v1/users", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_user_profile(data: UserProfileCreate):
    """Create user profile"""
    profile = await user_service.create_profile(data)
    user_operations.labels(operation="create", status="success").inc()
    return profile

@app.get("/api/v1/users/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(user_id: uuid.UUID):
    """Get user profile by ID"""
    profile = await user_service.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return profile

@app.get("/api/v1/users/by-auth/{auth_user_id}", response_model=UserProfileResponse)
async def get_user_by_auth_id(auth_user_id: uuid.UUID):
    """Get user profile by auth user ID"""
    profile = await user_service.get_profile_by_auth_id(auth_user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return profile

@app.patch("/api/v1/users/{user_id}", response_model=UserProfileResponse)
async def update_user_profile(user_id: uuid.UUID, data: UserProfileUpdate):
    """Update user profile"""
    profile = await user_service.update_profile(user_id, data)
    user_operations.labels(operation="update", status="success").inc()
    return profile

@app.patch("/api/v1/users/{user_id}/preferences", response_model=UserProfileResponse)
async def update_user_preferences(user_id: uuid.UUID, data: UserPreferencesUpdate):
    """Update user preferences"""
    profile = await user_service.update_preferences(user_id, data)
    return profile

@app.get("/api/v1/users", response_model=UserListResponse)
async def list_users(
    tenant_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status_filter: Optional[str] = None,
    department: Optional[str] = None
):
    """List users with pagination and filters"""
    users, total = await user_service.list_users(
        tenant_id=tenant_id,
        page=page,
        page_size=page_size,
        search=search,
        status_filter=status_filter,
        department=department
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return UserListResponse(
        items=users,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

# Field Assignment Endpoints
@app.post("/api/v1/users/{user_id}/fields", response_model=FieldAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def assign_field_to_user(
    user_id: uuid.UUID,
    data: FieldAssignmentCreate,
    assigned_by: uuid.UUID = Query(...)
):
    """Assign field to user"""
    assignment = await user_service.assign_field(
        user_id=user_id,
        field_id=data.field_id,
        access_level=data.access_level,
        assigned_by=assigned_by
    )
    return assignment

@app.get("/api/v1/users/{user_id}/fields", response_model=List[FieldAssignmentResponse])
async def get_user_fields(user_id: uuid.UUID):
    """Get user's assigned fields"""
    profile = await user_service.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return profile.assigned_fields

@app.delete("/api/v1/users/{user_id}/fields/{field_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_field_from_user(user_id: uuid.UUID, field_id: uuid.UUID):
    """Remove field assignment from user"""
    await user_service.remove_field_assignment(user_id, field_id)

# Activity Endpoints
@app.post("/api/v1/users/{user_id}/activities", status_code=status.HTTP_201_CREATED)
async def log_user_activity(
    user_id: uuid.UUID,
    activity_type: str,
    tenant_id: uuid.UUID,
    resource_type: Optional[str] = None,
    resource_id: Optional[uuid.UUID] = None,
    details: Optional[Dict] = None
):
    """Log user activity"""
    await user_service.log_activity(
        user_id=user_id,
        tenant_id=tenant_id,
        activity_type=activity_type,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details
    )
    return {"status": "logged"}

@app.get("/api/v1/users/{user_id}/activities", response_model=List[ActivityLogResponse])
async def get_user_activities(
    user_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=200),
    activity_type: Optional[str] = None
):
    """Get user activities"""
    activities = await user_service.get_activities(user_id, limit, activity_type)
    return activities

# Notification Preference Endpoints
@app.put("/api/v1/users/{user_id}/notification-preferences")
async def set_user_notification_preferences(
    user_id: uuid.UUID,
    preferences: List[NotificationPreferenceCreate]
):
    """Set user notification preferences"""
    await user_service.set_notification_preferences(user_id, preferences)
    return {"status": "updated"}

@app.get("/api/v1/users/{user_id}/notification-preferences", response_model=List[NotificationPreferenceResponse])
async def get_user_notification_preferences(user_id: uuid.UUID):
    """Get user notification preferences"""
    preferences = await user_service.get_notification_preferences(user_id)
    return preferences

# Status Management
@app.post("/api/v1/users/{user_id}/deactivate", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(user_id: uuid.UUID, reason: Optional[str] = None):
    """Deactivate user"""
    await user_service.deactivate_user(user_id, reason)

# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.SERVICE_PORT)
