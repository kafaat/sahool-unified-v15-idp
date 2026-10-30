# JWT Guards Integration Examples

# أمثلة على تكامل JWT Guards

## Table of Contents / جدول المحتويات

1. [Python FastAPI Examples](#python-fastapi-examples)
2. [TypeScript NestJS Examples](#typescript-nestjs-examples)
3. [Database Implementation](#database-implementation)
4. [Cache Management](#cache-management)
5. [Rate Limiting](#rate-limiting)

---

## Python FastAPI Examples

### Complete FastAPI Application

```python
# main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from shared.auth.user_cache import init_user_cache, close_user_cache
from shared.auth.user_repository import set_user_repository, UserRepository, UserValidationData
from shared.auth.dependencies import get_current_user, rate_limit_dependency
from shared.auth.models import User
from shared.libs.database import init_db, close_db, get_db_session

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


# ============================================================
# Database Model Example
# ============================================================
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Boolean, ARRAY
from datetime import datetime

class Base(DeclarativeBase):
    pass

class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    tenant_id: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    is_suspended: Mapped[bool] = mapped_column(Boolean, default=False)
    roles: Mapped[list[str]] = mapped_column(ARRAY(String))
    last_login: Mapped[datetime] = mapped_column(nullable=True)


# ============================================================
# User Repository Implementation
# ============================================================
class PostgresUserRepository(UserRepository):
    """PostgreSQL implementation of user repository"""

    def __init__(self, session_factory):
        super().__init__()
        self.session_factory = session_factory

    async def get_user_validation_data(
        self, user_id: str
    ) -> UserValidationData | None:
        """Get user from PostgreSQL"""
        async with self.session_factory() as session:
            stmt = select(UserModel).where(UserModel.id == user_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                return None

            return UserValidationData(
                user_id=user.id,
                email=user.email,
                is_active=user.is_active,
                is_verified=user.is_verified,
                roles=user.roles,
                tenant_id=user.tenant_id,
                is_deleted=user.is_deleted,
                is_suspended=user.is_suspended,
            )

    async def update_last_login(self, user_id: str) -> bool:
        """Update last login timestamp"""
        async with self.session_factory() as session:
            from sqlalchemy import update
            from datetime import datetime, timezone

            stmt = (
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(last_login=datetime.now(timezone.utc))
            )
            await session.execute(stmt)
            await session.commit()
            return True


# ============================================================
# Application Lifespan
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown"""

    # Startup
    print("🚀 Starting application...")

    # Initialize database
    from shared.libs.database import DatabaseConfig, DatabaseManager

    db_config = DatabaseConfig()
    db_manager = DatabaseManager(db_config)
    await db_manager.initialize()

    # Initialize user repository
    repository = PostgresUserRepository(db_manager.session)
    set_user_repository(repository)
    print("✅ User repository initialized")

    # Initialize Redis cache
    cache = await init_user_cache(ttl_seconds=300)
    if cache:
        print("✅ Redis cache initialized")
    else:
        print("⚠️  Redis cache not available - running without cache")

    yield

    # Shutdown
    print("🛑 Shutting down application...")
    await close_user_cache()
    await db_manager.close()
    print("✅ Cleanup completed")


# ============================================================
# FastAPI Application
# ============================================================
app = FastAPI(
    title="SAHOOL API",
    description="Enhanced JWT Authentication",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Routes
# ============================================================

@app.get("/")
async def root():
    """Public endpoint"""
    return {"message": "SAHOOL API - JWT Authentication Enhanced"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/api/profile")
async def get_profile(user: User = Depends(get_current_user)):
    """
    Get user profile
    - Validates user in database
    - Uses cache for performance
    - Checks user status
    """
    return {
        "user_id": user.id,
        "email": user.email,
        "roles": user.roles,
        "tenant_id": user.tenant_id,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
    }


@app.get("/api/farms")
async def list_farms(user: User = Depends(get_current_user)):
    """List farms for authenticated user"""
    return {
        "farms": [],
        "user_id": user.id,
    }


@app.post("/api/heavy-operation")
async def heavy_operation(user: User = Depends(rate_limit_dependency)):
    """
    Protected endpoint with rate limiting
    - Max 100 requests per minute
    - Logs violations
    """
    return {
        "message": "Operation completed",
        "user_id": user.id,
    }


@app.get("/api/admin/settings")
async def admin_settings(
    user: User = Depends(get_current_user),
):
    """Admin-only endpoint"""
    from shared.auth.dependencies import require_roles

    # Check admin role
    if not user.has_role("admin"):
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return {"settings": {}}


# ============================================================
# Cache Management Routes
# ============================================================
from shared.auth.user_cache import get_user_cache

@app.post("/api/admin/cache/invalidate/{user_id}")
async def invalidate_user_cache(
    user_id: str,
    admin: User = Depends(get_current_user),
):
    """Invalidate user cache (admin only)"""
    if not admin.has_role("admin"):
        from fastapi import HTTPException, status
        raise HTTPException(status_code=403, detail="Admin only")

    cache = get_user_cache()
    if cache:
        await cache.invalidate_user(user_id)
        return {"message": f"Cache invalidated for user {user_id}"}

    return {"message": "Cache not available"}


@app.delete("/api/admin/cache/clear")
async def clear_all_cache(admin: User = Depends(get_current_user)):
    """Clear all user cache (admin only)"""
    if not admin.has_role("admin"):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin only")

    cache = get_user_cache()
    if cache:
        count = await cache.clear_all()
        return {"message": f"Cleared {count} cached users"}

    return {"message": "Cache not available"}


# ============================================================
# Error Handlers
# ============================================================
from fastapi import Request
from fastapi.responses import JSONResponse
from shared.auth.models import AuthException

@app.exception_handler(AuthException)
async def auth_exception_handler(request: Request, exc: AuthException):
    """Handle authentication exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(lang="en"),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
```

---

## TypeScript NestJS Examples

### Complete NestJS Application

```typescript
// app.module.ts
import { Module } from "@nestjs/common";
import { TypeOrmModule } from "@nestjs/typeorm";
import { RedisModule } from "@liaoliaots/nestjs-redis";
import { AuthModule } from "./auth/auth.module";
import { FarmsModule } from "./farms/farms.module";

@Module({
  imports: [
    // Database
    TypeOrmModule.forRoot({
      type: "postgres",
      host: process.env.DB_HOST || "localhost",
      port: parseInt(process.env.DB_PORT || "5432"),
      username: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      database: process.env.DB_NAME,
      autoLoadEntities: true,
      synchronize: false,
    }),

    // Redis
    RedisModule.forRoot({
      config: {
        host: process.env.REDIS_HOST || "localhost",
        port: parseInt(process.env.REDIS_PORT || "6379"),
        password: process.env.REDIS_PASSWORD,
      },
    }),

    AuthModule,
    FarmsModule,
  ],
})
export class AppModule {}
```

```typescript
// auth/auth.module.ts
import { Module } from "@nestjs/common";
import { PassportModule } from "@nestjs/passport";
import { JwtModule } from "@nestjs/jwt";
import { TypeOrmModule } from "@nestjs/typeorm";
import { JwtStrategy } from "@shared/auth/jwt.strategy";
import { UserValidationService } from "@shared/auth/user-validation.service";
import { JWTConfig } from "@shared/auth/config";
import { User } from "./entities/user.entity";
import { UserRepository } from "./repositories/user.repository";

@Module({
  imports: [
    TypeOrmModule.forFeature([User]),
    PassportModule.register({ defaultStrategy: "jwt" }),
    JwtModule.register({
      secret: JWTConfig.JWT_SECRET,
      signOptions: {
        expiresIn: "30m",
        issuer: JWTConfig.ISSUER,
        audience: JWTConfig.AUDIENCE,
      },
    }),
  ],
  providers: [JwtStrategy, UserValidationService, UserRepository],
  exports: [JwtStrategy, UserValidationService],
})
export class AuthModule {}
```

```typescript
// auth/entities/user.entity.ts
import {
  Entity,
  Column,
  PrimaryColumn,
  UpdateDateColumn,
  CreateDateColumn,
} from "typeorm";

@Entity("users")
export class User {
  @PrimaryColumn("uuid")
  id: string;

  @Column({ unique: true })
  email: string;

  @Column()
  tenantId: string;

  @Column({ default: true })
  isActive: boolean;

  @Column({ default: false })
  isVerified: boolean;

  @Column({ default: false })
  isDeleted: boolean;

  @Column({ default: false })
  isSuspended: boolean;

  @Column("simple-array")
  roles: string[];

  @Column({ nullable: true })
  lastLogin: Date;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;
}
```

```typescript
// auth/repositories/user.repository.ts
import { Injectable } from "@nestjs/common";
import { InjectRepository } from "@nestjs/typeorm";
import { Repository } from "typeorm";
import { User } from "../entities/user.entity";
import {
  IUserRepository,
  UserValidationData,
} from "@shared/auth/user-validation.service";

@Injectable()
export class UserRepository implements IUserRepository {
  constructor(
    @InjectRepository(User)
    private readonly userRepo: Repository<User>,
  ) {}

  async getUserValidationData(
    userId: string,
  ): Promise<UserValidationData | null> {
    const user = await this.userRepo.findOne({
      where: { id: userId },
      select: [
        "id",
        "email",
        "isActive",
        "isVerified",
        "isDeleted",
        "isSuspended",
        "roles",
        "tenantId",
      ],
    });

    if (!user) {
      return null;
    }

    return {
      userId: user.id,
      email: user.email,
      isActive: user.isActive,
      isVerified: user.isVerified,
      roles: user.roles,
      tenantId: user.tenantId,
      isDeleted: user.isDeleted,
      isSuspended: user.isSuspended,
    };
  }

  async updateLastLogin(userId: string): Promise<void> {
    await this.userRepo.update({ id: userId }, { lastLogin: new Date() });
  }
}
```

```typescript
// farms/farms.controller.ts
import { Controller, Get, Post, UseGuards, Body } from "@nestjs/common";
import { JwtAuthGuard, RolesGuard } from "@shared/auth/jwt.guard";
import { CurrentUser } from "@shared/auth/decorators";
import { Roles } from "@shared/auth/decorators";

@Controller("farms")
@UseGuards(JwtAuthGuard)
export class FarmsController {
  @Get()
  async findAll(@CurrentUser() user: any) {
    // User is validated from database with caching
    return {
      farms: [],
      userId: user.id,
    };
  }

  @Get("profile")
  async getProfile(@CurrentUser() user: any) {
    return {
      userId: user.id,
      email: user.email,
      roles: user.roles,
    };
  }

  @Post()
  @UseGuards(RolesGuard)
  @Roles("admin", "manager")
  async create(@CurrentUser() user: any, @Body() createDto: any) {
    // Only admin or manager can create farms
    return {
      message: "Farm created",
      userId: user.id,
    };
  }
}
```

```typescript
// admin/cache.controller.ts
import { Controller, Delete, Param, Post, UseGuards } from "@nestjs/common";
import { JwtAuthGuard, RolesGuard } from "@shared/auth/jwt.guard";
import { Roles } from "@shared/auth/decorators";
import { UserValidationService } from "@shared/auth/user-validation.service";

@Controller("admin/cache")
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles("admin")
export class CacheController {
  constructor(private readonly validationService: UserValidationService) {}

  @Post("invalidate/:userId")
  async invalidateUser(@Param("userId") userId: string) {
    await this.validationService.invalidateUser(userId);
    return { message: `Cache invalidated for user ${userId}` };
  }

  @Delete("clear")
  async clearAll() {
    const count = await this.validationService.clearAll();
    return { message: `Cleared ${count} cached users` };
  }
}
```

---

## Database Implementation

### PostgreSQL Schema

```sql
-- users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    tenant_id UUID NOT NULL,
    password_hash VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    is_suspended BOOLEAN DEFAULT FALSE,
    roles TEXT[] DEFAULT ARRAY['user'],
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = TRUE;

-- Trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE
    ON users FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

## Cache Management

### Invalidate Cache on User Update

**Python:**

```python
from shared.auth.user_cache import get_user_cache

async def update_user_status(user_id: str, is_active: bool):
    # Update database
    # ...

    # Invalidate cache
    cache = get_user_cache()
    if cache:
        await cache.invalidate_user(user_id)
```

**TypeScript:**

```typescript
@Injectable()
class UserService {
  constructor(
    private userRepo: Repository<User>,
    private validationService: UserValidationService,
  ) {}

  async updateUserStatus(userId: string, isActive: boolean) {
    // Update database
    await this.userRepo.update({ id: userId }, { isActive });

    // Invalidate cache
    await this.validationService.invalidateUser(userId);
  }
}
```

---

## Rate Limiting

### Custom Rate Limits per Endpoint

```python
from shared.auth.dependencies import RateLimiter

# Create custom rate limiter
strict_limiter = RateLimiter(requests=10, window_seconds=60)

@app.post("/api/sensitive-operation")
async def sensitive_op(user: User = Depends(get_current_user)):
    key = f"strict:{user.id}"
    allowed, remaining = strict_limiter.is_allowed(key)

    if not allowed:
        raise HTTPException(status_code=429, detail="Too many requests")

    return {"message": "Success"}
```

---

## Testing

### Python Test Example

```python
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_protected_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Without token
        response = await client.get("/api/profile")
        assert response.status_code == 401

        # With valid token
        token = "valid_jwt_token"
        response = await client.get(
            "/api/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
```

### TypeScript Test Example

```typescript
describe("FarmsController", () => {
  let app: INestApplication;

  beforeAll(async () => {
    const module = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = module.createNestApplication();
    await app.init();
  });

  it("/farms (GET) - unauthorized", () => {
    return request(app.getHttpServer()).get("/farms").expect(401);
  });

  it("/farms (GET) - authorized", () => {
    const token = "valid_jwt_token";
    return request(app.getHttpServer())
      .get("/farms")
      .set("Authorization", `Bearer ${token}`)
      .expect(200);
  });
});
```

---

## Summary / الخلاصة

These examples show how to:

- ✅ Implement user repository with database
- ✅ Initialize caching service
- ✅ Use enhanced authentication guards
- ✅ Manage cache invalidation
- ✅ Implement custom rate limiting
- ✅ Handle authentication errors
- ✅ Test protected endpoints

For more details, see [JWT_GUARDS_ENHANCEMENT.md](./JWT_GUARDS_ENHANCEMENT.md)
