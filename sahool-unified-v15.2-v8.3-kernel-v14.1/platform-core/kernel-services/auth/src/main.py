"""
SAHOOL Auth Service - JWT RS256 Authentication & Authorization
===============================================================
Layer: Platform Core (Layer 1)
Purpose: Centralized authentication, authorization, and token management
"""

import os
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
import secrets
import hashlib
import base64

from fastapi import FastAPI, HTTPException, Depends, status, Security, Request, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field, validator
import jwt
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import bcrypt
import redis.asyncio as redis
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, ForeignKey, Table, Integer, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import structlog
import uuid
import enum

# Shared imports
import sys
sys.path.insert(0, '/app/shared')
from database import Database, BaseModel as DBBaseModel
from events.base_event import BaseEvent, EventBus
from utils.logging import setup_logging
from metrics import MetricsManager

# ============================================================================
# Configuration
# ============================================================================

class Settings:
    """Auth service configuration"""
    SERVICE_NAME = "auth-service"
    SERVICE_PORT = int(os.getenv("AUTH_SERVICE_PORT", "8080"))
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://sahool:sahool@postgres:5432/sahool_auth")
    
    # Redis for token blacklist and sessions
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # JWT Configuration
    JWT_ALGORITHM = "RS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_EXPIRE", "15"))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_EXPIRE", "7"))
    JWT_ISSUER = os.getenv("JWT_ISSUER", "sahool-platform")
    JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "sahool-api")
    
    # RSA Keys
    PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH", "/app/keys/private.pem")
    PUBLIC_KEY_PATH = os.getenv("PUBLIC_KEY_PATH", "/app/keys/public.pem")
    
    # NATS
    NATS_URL = os.getenv("NATS_URL", "nats://nats:4222")
    
    # Security
    PASSWORD_MIN_LENGTH = 8
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30
    
    # MFA
    MFA_ENABLED = os.getenv("MFA_ENABLED", "true").lower() == "true"
    TOTP_ISSUER = "SAHOOL"

settings = Settings()

# ============================================================================
# Logging & Metrics
# ============================================================================

setup_logging(settings.SERVICE_NAME)
logger = structlog.get_logger()

# Prometheus Metrics
auth_requests = Counter('auth_requests_total', 'Total authentication requests', ['method', 'status'])
token_operations = Counter('token_operations_total', 'Token operations', ['operation', 'status'])
login_latency = Histogram('login_latency_seconds', 'Login request latency')

# ============================================================================
# Database Models
# ============================================================================

class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    TENANT_ADMIN = "tenant_admin"
    FARM_MANAGER = "farm_manager"
    AGRONOMIST = "agronomist"
    FIELD_WORKER = "field_worker"
    VIEWER = "viewer"

# Association table for user-role many-to-many
user_roles = Table(
    'user_roles',
    DBBaseModel.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True)
)

# Association table for role-permission many-to-many
role_permissions = Table(
    'role_permissions',
    DBBaseModel.metadata,
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('permissions.id'), primary_key=True)
)

class User(DBBaseModel):
    """User model with authentication data"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile
    full_name = Column(String(255), nullable=False)
    full_name_ar = Column(String(255), nullable=True)  # Arabic name
    preferred_language = Column(String(10), default="ar")
    timezone = Column(String(50), default="Asia/Aden")
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    locked_until = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    
    # MFA
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)
    mfa_backup_codes = Column(JSON, nullable=True)
    
    # Metadata
    last_login = Column(DateTime, nullable=True)
    last_password_change = Column(DateTime, nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    verification_token = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")

class Role(DBBaseModel):
    """Role model for RBAC"""
    __tablename__ = "roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    name_ar = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True)
    is_system = Column(Boolean, default=False)  # System roles cannot be deleted
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")

class Permission(DBBaseModel):
    """Permission model for fine-grained access control"""
    __tablename__ = "permissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource = Column(String(100), nullable=False)  # e.g., "fields", "tasks", "reports"
    action = Column(String(50), nullable=False)  # e.g., "read", "write", "delete", "admin"
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
    
    @property
    def code(self) -> str:
        return f"{self.resource}:{self.action}"

class UserSession(DBBaseModel):
    """Active user sessions for tracking and revocation"""
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    refresh_token_hash = Column(String(255), nullable=False, unique=True)
    device_info = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")

class APIKey(DBBaseModel):
    """API Keys for service-to-service and programmatic access"""
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    name = Column(String(100), nullable=False)
    key_prefix = Column(String(10), nullable=False)  # First 8 chars for identification
    key_hash = Column(String(255), nullable=False)
    
    scopes = Column(ARRAY(String), default=[])  # Allowed permissions
    rate_limit = Column(Integer, default=1000)  # Requests per hour
    
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")

class AuditLog(DBBaseModel):
    """Audit log for security events"""
    __tablename__ = "auth_audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=True)
    
    event_type = Column(String(50), nullable=False)  # login, logout, password_change, etc.
    event_status = Column(String(20), nullable=False)  # success, failure
    
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    details = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# ============================================================================
# Pydantic Schemas
# ============================================================================

class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    phone: Optional[str] = None
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=255)
    full_name_ar: Optional[str] = None
    tenant_id: uuid.UUID
    preferred_language: str = "ar"
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain a digit')
        return v

class UserResponse(BaseModel):
    """User response schema"""
    id: uuid.UUID
    email: str
    phone: Optional[str]
    full_name: str
    full_name_ar: Optional[str]
    tenant_id: uuid.UUID
    preferred_language: str
    is_active: bool
    is_verified: bool
    mfa_enabled: bool
    roles: List[str]
    last_login: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str
    mfa_code: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None

class LoginResponse(BaseModel):
    """Login response with tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    user: UserResponse
    requires_mfa: bool = False

class TokenRefreshRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str

class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int

class PasswordChangeRequest(BaseModel):
    """Password change request"""
    current_password: str
    new_password: str = Field(..., min_length=8)

class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8)

class MFASetupResponse(BaseModel):
    """MFA setup response"""
    secret: str
    qr_code_uri: str
    backup_codes: List[str]

class MFAVerifyRequest(BaseModel):
    """MFA verification request"""
    code: str

class APIKeyCreate(BaseModel):
    """API key creation request"""
    name: str = Field(..., min_length=3, max_length=100)
    scopes: List[str] = []
    expires_in_days: Optional[int] = None

class APIKeyResponse(BaseModel):
    """API key response"""
    id: uuid.UUID
    name: str
    key_prefix: str
    scopes: List[str]
    is_active: bool
    last_used: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime

class APIKeyCreated(APIKeyResponse):
    """API key creation response with full key"""
    api_key: str  # Only shown once on creation

class TokenPayload(BaseModel):
    """JWT token payload"""
    sub: str  # User ID
    tenant_id: str
    email: str
    roles: List[str]
    permissions: List[str]
    exp: datetime
    iat: datetime
    iss: str
    aud: str
    jti: str  # Token ID for revocation
    token_type: str  # access or refresh

# ============================================================================
# JWT Manager
# ============================================================================

class JWTManager:
    """Manages JWT token operations with RS256"""
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
        self._load_keys()
    
    def _load_keys(self):
        """Load RSA keys from files or generate new ones"""
        try:
            # Try to load existing keys
            with open(settings.PRIVATE_KEY_PATH, 'rb') as f:
                self.private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
            with open(settings.PUBLIC_KEY_PATH, 'rb') as f:
                self.public_key = serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend()
                )
            logger.info("RSA keys loaded successfully")
        except FileNotFoundError:
            # Generate new keys
            self._generate_keys()
    
    def _generate_keys(self):
        """Generate new RSA key pair"""
        logger.info("Generating new RSA key pair...")
        
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        
        # Save keys
        os.makedirs(os.path.dirname(settings.PRIVATE_KEY_PATH), exist_ok=True)
        
        with open(settings.PRIVATE_KEY_PATH, 'wb') as f:
            f.write(self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        with open(settings.PUBLIC_KEY_PATH, 'wb') as f:
            f.write(self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))
        
        logger.info("RSA keys generated and saved")
    
    def create_access_token(
        self,
        user: User,
        roles: List[str],
        permissions: List[str]
    ) -> str:
        """Create JWT access token"""
        now = datetime.utcnow()
        expires = now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            "sub": str(user.id),
            "tenant_id": str(user.tenant_id),
            "email": user.email,
            "roles": roles,
            "permissions": permissions,
            "exp": expires,
            "iat": now,
            "iss": settings.JWT_ISSUER,
            "aud": settings.JWT_AUDIENCE,
            "jti": str(uuid.uuid4()),
            "token_type": "access"
        }
        
        token = jwt.encode(
            payload,
            self.private_key,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return token
    
    def create_refresh_token(self, user: User, session_id: uuid.UUID) -> str:
        """Create JWT refresh token"""
        now = datetime.utcnow()
        expires = now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        
        payload = {
            "sub": str(user.id),
            "tenant_id": str(user.tenant_id),
            "session_id": str(session_id),
            "exp": expires,
            "iat": now,
            "iss": settings.JWT_ISSUER,
            "aud": settings.JWT_AUDIENCE,
            "jti": str(uuid.uuid4()),
            "token_type": "refresh"
        }
        
        token = jwt.encode(
            payload,
            self.private_key,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return token
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.public_key,
                algorithms=[settings.JWT_ALGORITHM],
                issuer=settings.JWT_ISSUER,
                audience=settings.JWT_AUDIENCE
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
    
    def get_public_key_pem(self) -> str:
        """Get public key in PEM format for other services"""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
    
    def get_jwks(self) -> Dict:
        """Get JWKS (JSON Web Key Set) for public key distribution"""
        from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
        
        numbers = self.public_key.public_numbers()
        
        # Convert integers to base64url encoded strings
        def int_to_base64url(n: int) -> str:
            byte_length = (n.bit_length() + 7) // 8
            return base64.urlsafe_b64encode(n.to_bytes(byte_length, 'big')).rstrip(b'=').decode('ascii')
        
        return {
            "keys": [{
                "kty": "RSA",
                "alg": "RS256",
                "use": "sig",
                "kid": "sahool-auth-key-1",
                "n": int_to_base64url(numbers.n),
                "e": int_to_base64url(numbers.e)
            }]
        }

# ============================================================================
# Password Manager
# ============================================================================

class PasswordManager:
    """Handles password hashing and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def generate_reset_token() -> str:
        """Generate secure password reset token"""
        return secrets.token_urlsafe(32)

# ============================================================================
# MFA Manager
# ============================================================================

class MFAManager:
    """Handles TOTP-based MFA"""
    
    @staticmethod
    def generate_secret() -> str:
        """Generate TOTP secret"""
        import pyotp
        return pyotp.random_base32()
    
    @staticmethod
    def get_totp_uri(secret: str, email: str) -> str:
        """Get TOTP provisioning URI for QR code"""
        import pyotp
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=email,
            issuer_name=settings.TOTP_ISSUER
        )
    
    @staticmethod
    def verify_totp(secret: str, code: str) -> bool:
        """Verify TOTP code"""
        import pyotp
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)
    
    @staticmethod
    def generate_backup_codes(count: int = 10) -> List[str]:
        """Generate backup codes"""
        return [secrets.token_hex(4).upper() for _ in range(count)]

# ============================================================================
# Auth Service
# ============================================================================

class AuthService:
    """Core authentication service"""
    
    def __init__(self, db: Database, redis_client: redis.Redis, jwt_manager: JWTManager, event_bus: EventBus):
        self.db = db
        self.redis = redis_client
        self.jwt = jwt_manager
        self.event_bus = event_bus
        self.password_manager = PasswordManager()
        self.mfa_manager = MFAManager()
    
    async def register_user(self, data: UserCreate) -> User:
        """Register a new user"""
        async with self.db.session() as session:
            # Check if email exists
            existing = await session.execute(
                select(User).where(User.email == data.email)
            )
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Create user
            user = User(
                tenant_id=data.tenant_id,
                email=data.email,
                phone=data.phone,
                password_hash=self.password_manager.hash_password(data.password),
                full_name=data.full_name,
                full_name_ar=data.full_name_ar,
                preferred_language=data.preferred_language,
                verification_token=secrets.token_urlsafe(32)
            )
            
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            # Emit event
            await self.event_bus.publish(
                "auth.user.registered",
                {
                    "user_id": str(user.id),
                    "tenant_id": str(user.tenant_id),
                    "email": user.email
                }
            )
            
            logger.info("User registered", user_id=str(user.id), email=user.email)
            return user
    
    async def authenticate(
        self,
        email: str,
        password: str,
        ip_address: str,
        user_agent: str,
        device_info: Optional[Dict] = None
    ) -> tuple[User, str, str]:
        """Authenticate user and return tokens"""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        async with self.db.session() as session:
            # Get user with roles
            result = await session.execute(
                select(User)
                .options(selectinload(User.roles).selectinload(Role.permissions))
                .where(User.email == email)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                await self._log_audit(
                    session, None, None, "login", "failure",
                    ip_address, user_agent, {"reason": "user_not_found", "email": email}
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            # Check if account is locked
            if user.is_locked and user.locked_until and user.locked_until > datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=f"Account locked until {user.locked_until.isoformat()}"
                )
            
            # Verify password
            if not self.password_manager.verify_password(password, user.password_hash):
                user.failed_login_attempts += 1
                
                # Lock account after max attempts
                if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                    user.is_locked = True
                    user.locked_until = datetime.utcnow() + timedelta(minutes=settings.LOCKOUT_DURATION_MINUTES)
                
                await session.commit()
                
                await self._log_audit(
                    session, user.id, user.tenant_id, "login", "failure",
                    ip_address, user_agent, {"reason": "invalid_password"}
                )
                
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            # Check if user is active
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Account is deactivated"
                )
            
            # Reset failed attempts on successful login
            user.failed_login_attempts = 0
            user.is_locked = False
            user.locked_until = None
            user.last_login = datetime.utcnow()
            
            # Get roles and permissions
            roles = [role.name for role in user.roles]
            permissions = set()
            for role in user.roles:
                for perm in role.permissions:
                    permissions.add(perm.code)
            
            # Create session
            session_obj = UserSession(
                user_id=user.id,
                refresh_token_hash="",  # Will be updated
                device_info=device_info,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
            )
            session.add(session_obj)
            await session.flush()
            
            # Generate tokens
            access_token = self.jwt.create_access_token(user, roles, list(permissions))
            refresh_token = self.jwt.create_refresh_token(user, session_obj.id)
            
            # Update session with refresh token hash
            session_obj.refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
            
            await session.commit()
            
            # Log successful login
            await self._log_audit(
                session, user.id, user.tenant_id, "login", "success",
                ip_address, user_agent, {"session_id": str(session_obj.id)}
            )
            
            # Emit event
            await self.event_bus.publish(
                "auth.user.logged_in",
                {
                    "user_id": str(user.id),
                    "tenant_id": str(user.tenant_id),
                    "session_id": str(session_obj.id)
                }
            )
            
            logger.info("User logged in", user_id=str(user.id))
            return user, access_token, refresh_token
    
    async def refresh_tokens(self, refresh_token: str) -> tuple[str, str]:
        """Refresh access and refresh tokens"""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        # Verify refresh token
        payload = self.jwt.verify_token(refresh_token)
        
        if payload.get("token_type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        async with self.db.session() as session:
            # Find session
            result = await session.execute(
                select(UserSession)
                .where(
                    UserSession.refresh_token_hash == token_hash,
                    UserSession.is_active == True
                )
            )
            user_session = result.scalar_one_or_none()
            
            if not user_session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Session not found or expired"
                )
            
            # Get user with roles
            result = await session.execute(
                select(User)
                .options(selectinload(User.roles).selectinload(Role.permissions))
                .where(User.id == user_session.user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive"
                )
            
            # Get roles and permissions
            roles = [role.name for role in user.roles]
            permissions = set()
            for role in user.roles:
                for perm in role.permissions:
                    permissions.add(perm.code)
            
            # Generate new tokens
            access_token = self.jwt.create_access_token(user, roles, list(permissions))
            new_refresh_token = self.jwt.create_refresh_token(user, user_session.id)
            
            # Update session
            user_session.refresh_token_hash = hashlib.sha256(new_refresh_token.encode()).hexdigest()
            user_session.last_used = datetime.utcnow()
            user_session.expires_at = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
            
            await session.commit()
            
            return access_token, new_refresh_token
    
    async def logout(self, user_id: uuid.UUID, refresh_token: str):
        """Logout user and invalidate session"""
        from sqlalchemy import select
        
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        async with self.db.session() as session:
            result = await session.execute(
                select(UserSession)
                .where(
                    UserSession.user_id == user_id,
                    UserSession.refresh_token_hash == token_hash
                )
            )
            user_session = result.scalar_one_or_none()
            
            if user_session:
                user_session.is_active = False
                await session.commit()
            
            # Add refresh token to blacklist in Redis
            payload = self.jwt.verify_token(refresh_token)
            ttl = int((datetime.fromtimestamp(payload["exp"]) - datetime.utcnow()).total_seconds())
            if ttl > 0:
                await self.redis.setex(f"blacklist:{payload['jti']}", ttl, "1")
        
        logger.info("User logged out", user_id=str(user_id))
    
    async def _log_audit(
        self,
        session,
        user_id: Optional[uuid.UUID],
        tenant_id: Optional[uuid.UUID],
        event_type: str,
        event_status: str,
        ip_address: str,
        user_agent: str,
        details: Dict
    ):
        """Log audit event"""
        audit = AuditLog(
            user_id=user_id,
            tenant_id=tenant_id,
            event_type=event_type,
            event_status=event_status,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )
        session.add(audit)
        await session.commit()

# ============================================================================
# Dependencies
# ============================================================================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
http_bearer = HTTPBearer(auto_error=False)

# Global instances
db: Database = None
redis_client: redis.Redis = None
jwt_manager: JWTManager = None
event_bus: EventBus = None
auth_service: AuthService = None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(http_bearer),
    authorization: Optional[str] = Header(None)
) -> TokenPayload:
    """Get current authenticated user from token"""
    token = None
    
    if credentials:
        token = credentials.credentials
    elif authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check if token is blacklisted
    payload = jwt_manager.verify_token(token)
    
    is_blacklisted = await redis_client.exists(f"blacklist:{payload['jti']}")
    if is_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )
    
    return TokenPayload(**payload)

def require_permissions(*permissions: str):
    """Dependency to require specific permissions"""
    async def check_permissions(current_user: TokenPayload = Depends(get_current_user)):
        for perm in permissions:
            if perm not in current_user.permissions and "admin:*" not in current_user.permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied: {perm}"
                )
        return current_user
    return check_permissions

def require_roles(*roles: str):
    """Dependency to require specific roles"""
    async def check_roles(current_user: TokenPayload = Depends(get_current_user)):
        if not any(role in current_user.roles for role in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Role not authorized"
            )
        return current_user
    return check_roles

# ============================================================================
# FastAPI Application
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global db, redis_client, jwt_manager, event_bus, auth_service
    
    logger.info("Starting Auth Service...")
    
    # Initialize database
    db = Database(settings.DATABASE_URL)
    await db.connect()
    
    # Initialize Redis
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    # Initialize JWT Manager
    jwt_manager = JWTManager()
    
    # Initialize Event Bus
    event_bus = EventBus(settings.NATS_URL)
    await event_bus.connect()
    
    # Initialize Auth Service
    auth_service = AuthService(db, redis_client, jwt_manager, event_bus)
    
    logger.info("Auth Service started successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Auth Service...")
    await event_bus.close()
    await redis_client.close()
    await db.disconnect()

app = FastAPI(
    title="SAHOOL Auth Service",
    description="Authentication and Authorization Service",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": settings.SERVICE_NAME}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/.well-known/jwks.json")
async def jwks():
    """JWKS endpoint for public key distribution"""
    return jwt_manager.get_jwks()

@app.get("/api/v1/auth/public-key")
async def get_public_key():
    """Get public key in PEM format"""
    return {"public_key": jwt_manager.get_public_key_pem()}

# Authentication Endpoints
@app.post("/api/v1/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    request: Request
):
    """Register a new user"""
    user = await auth_service.register_user(data)
    auth_requests.labels(method="register", status="success").inc()
    return user

@app.post("/api/v1/auth/login", response_model=LoginResponse)
@login_latency.time()
async def login(
    data: LoginRequest,
    request: Request
):
    """Authenticate user and get tokens"""
    user, access_token, refresh_token = await auth_service.authenticate(
        email=data.email,
        password=data.password,
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "unknown"),
        device_info=data.device_info
    )
    
    # Check if MFA is required
    if user.mfa_enabled and not data.mfa_code:
        return LoginResponse(
            access_token="",
            refresh_token="",
            expires_in=0,
            user=UserResponse(
                id=user.id,
                email=user.email,
                phone=user.phone,
                full_name=user.full_name,
                full_name_ar=user.full_name_ar,
                tenant_id=user.tenant_id,
                preferred_language=user.preferred_language,
                is_active=user.is_active,
                is_verified=user.is_verified,
                mfa_enabled=user.mfa_enabled,
                roles=[r.name for r in user.roles],
                last_login=user.last_login,
                created_at=user.created_at
            ),
            requires_mfa=True
        )
    
    auth_requests.labels(method="login", status="success").inc()
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(
            id=user.id,
            email=user.email,
            phone=user.phone,
            full_name=user.full_name,
            full_name_ar=user.full_name_ar,
            tenant_id=user.tenant_id,
            preferred_language=user.preferred_language,
            is_active=user.is_active,
            is_verified=user.is_verified,
            mfa_enabled=user.mfa_enabled,
            roles=[r.name for r in user.roles],
            last_login=user.last_login,
            created_at=user.created_at
        )
    )

@app.post("/api/v1/auth/refresh", response_model=TokenResponse)
async def refresh_tokens(data: TokenRefreshRequest):
    """Refresh access token"""
    access_token, refresh_token = await auth_service.refresh_tokens(data.refresh_token)
    token_operations.labels(operation="refresh", status="success").inc()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@app.post("/api/v1/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    data: TokenRefreshRequest,
    current_user: TokenPayload = Depends(get_current_user)
):
    """Logout and invalidate session"""
    await auth_service.logout(uuid.UUID(current_user.sub), data.refresh_token)
    auth_requests.labels(method="logout", status="success").inc()

@app.get("/api/v1/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: TokenPayload = Depends(get_current_user)
):
    """Get current user information"""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    
    async with db.session() as session:
        result = await session.execute(
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == uuid.UUID(current_user.sub))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            id=user.id,
            email=user.email,
            phone=user.phone,
            full_name=user.full_name,
            full_name_ar=user.full_name_ar,
            tenant_id=user.tenant_id,
            preferred_language=user.preferred_language,
            is_active=user.is_active,
            is_verified=user.is_verified,
            mfa_enabled=user.mfa_enabled,
            roles=[r.name for r in user.roles],
            last_login=user.last_login,
            created_at=user.created_at
        )

@app.post("/api/v1/auth/verify-token")
async def verify_token(
    current_user: TokenPayload = Depends(get_current_user)
):
    """Verify token and return user info"""
    return {
        "valid": True,
        "user_id": current_user.sub,
        "tenant_id": current_user.tenant_id,
        "roles": current_user.roles,
        "permissions": current_user.permissions
    }

# Password Management
@app.post("/api/v1/auth/password/change", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    data: PasswordChangeRequest,
    current_user: TokenPayload = Depends(get_current_user)
):
    """Change user password"""
    from sqlalchemy import select
    
    async with db.session() as session:
        result = await session.execute(
            select(User).where(User.id == uuid.UUID(current_user.sub))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not PasswordManager.verify_password(data.current_password, user.password_hash):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        user.password_hash = PasswordManager.hash_password(data.new_password)
        user.last_password_change = datetime.utcnow()
        
        await session.commit()
    
    # Emit event
    await event_bus.publish(
        "auth.user.password_changed",
        {"user_id": current_user.sub, "tenant_id": current_user.tenant_id}
    )

@app.post("/api/v1/auth/password/reset-request", status_code=status.HTTP_204_NO_CONTENT)
async def request_password_reset(data: PasswordResetRequest):
    """Request password reset"""
    from sqlalchemy import select
    
    async with db.session() as session:
        result = await session.execute(
            select(User).where(User.email == data.email)
        )
        user = result.scalar_one_or_none()
        
        if user:
            user.password_reset_token = PasswordManager.generate_reset_token()
            user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
            await session.commit()
            
            # Emit event for notification service
            await event_bus.publish(
                "auth.password_reset.requested",
                {
                    "user_id": str(user.id),
                    "email": user.email,
                    "token": user.password_reset_token,
                    "expires": user.password_reset_expires.isoformat()
                }
            )

@app.post("/api/v1/auth/password/reset-confirm", status_code=status.HTTP_204_NO_CONTENT)
async def confirm_password_reset(data: PasswordResetConfirm):
    """Confirm password reset with token"""
    from sqlalchemy import select
    
    async with db.session() as session:
        result = await session.execute(
            select(User).where(
                User.password_reset_token == data.token,
                User.password_reset_expires > datetime.utcnow()
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        
        user.password_hash = PasswordManager.hash_password(data.new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        user.last_password_change = datetime.utcnow()
        
        await session.commit()

# MFA Endpoints
@app.post("/api/v1/auth/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(
    current_user: TokenPayload = Depends(get_current_user)
):
    """Setup MFA for user"""
    from sqlalchemy import select
    
    async with db.session() as session:
        result = await session.execute(
            select(User).where(User.id == uuid.UUID(current_user.sub))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        secret = MFAManager.generate_secret()
        backup_codes = MFAManager.generate_backup_codes()
        
        # Store temporarily in Redis until verified
        await redis_client.setex(
            f"mfa_setup:{current_user.sub}",
            300,  # 5 minutes
            f"{secret}:{','.join(backup_codes)}"
        )
        
        return MFASetupResponse(
            secret=secret,
            qr_code_uri=MFAManager.get_totp_uri(secret, user.email),
            backup_codes=backup_codes
        )

@app.post("/api/v1/auth/mfa/verify", status_code=status.HTTP_204_NO_CONTENT)
async def verify_mfa_setup(
    data: MFAVerifyRequest,
    current_user: TokenPayload = Depends(get_current_user)
):
    """Verify MFA setup with code"""
    from sqlalchemy import select
    
    setup_data = await redis_client.get(f"mfa_setup:{current_user.sub}")
    if not setup_data:
        raise HTTPException(status_code=400, detail="MFA setup expired")
    
    secret, backup_codes_str = setup_data.split(":", 1)
    backup_codes = backup_codes_str.split(",")
    
    if not MFAManager.verify_totp(secret, data.code):
        raise HTTPException(status_code=400, detail="Invalid MFA code")
    
    async with db.session() as session:
        result = await session.execute(
            select(User).where(User.id == uuid.UUID(current_user.sub))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.mfa_enabled = True
        user.mfa_secret = secret
        user.mfa_backup_codes = [PasswordManager.hash_password(c) for c in backup_codes]
        
        await session.commit()
    
    await redis_client.delete(f"mfa_setup:{current_user.sub}")

@app.delete("/api/v1/auth/mfa", status_code=status.HTTP_204_NO_CONTENT)
async def disable_mfa(
    data: MFAVerifyRequest,
    current_user: TokenPayload = Depends(get_current_user)
):
    """Disable MFA"""
    from sqlalchemy import select
    
    async with db.session() as session:
        result = await session.execute(
            select(User).where(User.id == uuid.UUID(current_user.sub))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not user.mfa_enabled:
            raise HTTPException(status_code=400, detail="MFA not enabled")
        
        if not MFAManager.verify_totp(user.mfa_secret, data.code):
            raise HTTPException(status_code=400, detail="Invalid MFA code")
        
        user.mfa_enabled = False
        user.mfa_secret = None
        user.mfa_backup_codes = None
        
        await session.commit()

# API Key Management
@app.post("/api/v1/auth/api-keys", response_model=APIKeyCreated, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    data: APIKeyCreate,
    current_user: TokenPayload = Depends(get_current_user)
):
    """Create new API key"""
    # Generate API key
    key = f"sk_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    
    async with db.session() as session:
        api_key = APIKey(
            user_id=uuid.UUID(current_user.sub),
            tenant_id=uuid.UUID(current_user.tenant_id),
            name=data.name,
            key_prefix=key[:10],
            key_hash=key_hash,
            scopes=data.scopes,
            expires_at=datetime.utcnow() + timedelta(days=data.expires_in_days) if data.expires_in_days else None
        )
        
        session.add(api_key)
        await session.commit()
        await session.refresh(api_key)
        
        return APIKeyCreated(
            id=api_key.id,
            name=api_key.name,
            key_prefix=api_key.key_prefix,
            scopes=api_key.scopes,
            is_active=api_key.is_active,
            last_used=api_key.last_used,
            expires_at=api_key.expires_at,
            created_at=api_key.created_at,
            api_key=key  # Only shown once
        )

@app.get("/api/v1/auth/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    current_user: TokenPayload = Depends(get_current_user)
):
    """List user's API keys"""
    from sqlalchemy import select
    
    async with db.session() as session:
        result = await session.execute(
            select(APIKey).where(APIKey.user_id == uuid.UUID(current_user.sub))
        )
        keys = result.scalars().all()
        
        return [
            APIKeyResponse(
                id=k.id,
                name=k.name,
                key_prefix=k.key_prefix,
                scopes=k.scopes,
                is_active=k.is_active,
                last_used=k.last_used,
                expires_at=k.expires_at,
                created_at=k.created_at
            )
            for k in keys
        ]

@app.delete("/api/v1/auth/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: uuid.UUID,
    current_user: TokenPayload = Depends(get_current_user)
):
    """Delete API key"""
    from sqlalchemy import select
    
    async with db.session() as session:
        result = await session.execute(
            select(APIKey).where(
                APIKey.id == key_id,
                APIKey.user_id == uuid.UUID(current_user.sub)
            )
        )
        api_key = result.scalar_one_or_none()
        
        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found")
        
        await session.delete(api_key)
        await session.commit()

# Session Management
@app.get("/api/v1/auth/sessions")
async def list_sessions(
    current_user: TokenPayload = Depends(get_current_user)
):
    """List active sessions"""
    from sqlalchemy import select
    
    async with db.session() as session:
        result = await session.execute(
            select(UserSession)
            .where(
                UserSession.user_id == uuid.UUID(current_user.sub),
                UserSession.is_active == True
            )
            .order_by(UserSession.last_used.desc())
        )
        sessions = result.scalars().all()
        
        return [
            {
                "id": str(s.id),
                "device_info": s.device_info,
                "ip_address": s.ip_address,
                "user_agent": s.user_agent,
                "last_used": s.last_used.isoformat() if s.last_used else None,
                "created_at": s.created_at.isoformat()
            }
            for s in sessions
        ]

@app.delete("/api/v1/auth/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_session(
    session_id: uuid.UUID,
    current_user: TokenPayload = Depends(get_current_user)
):
    """Revoke a specific session"""
    from sqlalchemy import select
    
    async with db.session() as session:
        result = await session.execute(
            select(UserSession).where(
                UserSession.id == session_id,
                UserSession.user_id == uuid.UUID(current_user.sub)
            )
        )
        user_session = result.scalar_one_or_none()
        
        if not user_session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        user_session.is_active = False
        await session.commit()

@app.delete("/api/v1/auth/sessions", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_all_sessions(
    current_user: TokenPayload = Depends(get_current_user)
):
    """Revoke all sessions except current"""
    from sqlalchemy import update
    
    async with db.session() as session:
        await session.execute(
            update(UserSession)
            .where(UserSession.user_id == uuid.UUID(current_user.sub))
            .values(is_active=False)
        )
        await session.commit()

# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.SERVICE_PORT)
