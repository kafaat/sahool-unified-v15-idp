from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.database import create_pool, run_migrations, seed_admin
from .core.security import hash_password
from .api.v1.auth import router as auth_router
from .api.v1.users import router as users_router
from .api.v1.admin import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ────────────────────────────────────────────────────────────
    app.state.db = await create_pool(settings.DATABASE_URL)
    await run_migrations(app.state.db)
    await seed_admin(
        app.state.db,
        email=settings.ADMIN_EMAIL,
        name=settings.ADMIN_NAME,
        password_hash=hash_password(settings.ADMIN_PASSWORD),
    )
    print(f"[auth] service ready on port {settings.AUTH_PORT}")
    yield
    # ── Shutdown ───────────────────────────────────────────────────────────
    await app.state.db.close()


app = FastAPI(
    title="SAHOOL Auth Service",
    version="1.0.0",
    description="Full-stack authentication and authorization API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(admin_router)


@app.get("/healthz", tags=["health"])
def health():
    return {"status": "ok", "service": "auth", "version": "1.0.0"}


@app.get("/readyz", tags=["health"])
async def readiness():
    db_ok = hasattr(app.state, "db") and app.state.db is not None
    return {"status": "ok" if db_ok else "degraded", "database": db_ok}
