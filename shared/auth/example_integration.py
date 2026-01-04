"""
Example Integration: Two-Factor Authentication
مثال على التكامل: المصادقة الثنائية

This file demonstrates how to integrate 2FA into a FastAPI application.
"""

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import 2FA components
from shared.auth.auth_api import router as auth_router
from shared.auth.auth_api import set_user_service
from shared.auth.dependencies import get_current_user
from shared.auth.twofa_api import router as twofa_router
from shared.auth.twofa_config import (
    TwoFAEnforcementLevel,
    configure_twofa,
)
from shared.domain.users.service import UserService

# ══════════════════════════════════════════════════════════════════════════════
# Application Setup
# ══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="SAHOOL Platform API",
    description="Agricultural Platform with 2FA Security",
    version="16.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # Admin dashboard URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ══════════════════════════════════════════════════════════════════════════════
# Initialize Services
# ══════════════════════════════════════════════════════════════════════════════

# Initialize user service
# In production, this would connect to your database
user_service = UserService()

# Set user service for auth APIs
set_user_service(user_service)

# ══════════════════════════════════════════════════════════════════════════════
# Configure 2FA
# ══════════════════════════════════════════════════════════════════════════════

# Option 1: Use preset configuration
# configure_twofa_with_preset = get_production_config()
# set_twofa_config(configure_twofa_with_preset)

# Option 2: Custom configuration
configure_twofa(
    enforcement_level=TwoFAEnforcementLevel.REQUIRED_FOR_ADMIN,
    grace_period_days=7,
    max_2fa_attempts=3,
    lockout_duration_minutes=30,
    require_2fa_for_api_access=True,
    notify_on_2fa_setup=True,
    notify_on_2fa_disable=True,
    notify_on_backup_code_used=True,
)

# ══════════════════════════════════════════════════════════════════════════════
# Register Routes
# ══════════════════════════════════════════════════════════════════════════════

# Authentication routes (includes login with 2FA)
app.include_router(auth_router)

# 2FA management routes
app.include_router(twofa_router)

# ══════════════════════════════════════════════════════════════════════════════
# Example Protected Routes
# ══════════════════════════════════════════════════════════════════════════════


@app.get("/")
async def root():
    """Public endpoint"""
    return {
        "message": "SAHOOL Platform API",
        "version": "16.0.0",
        "security": "2FA Enabled",
    }


@app.get("/api/v1/dashboard")
async def dashboard(user=Depends(get_current_user)):
    """Protected dashboard endpoint requiring authentication"""
    return {
        "message": f"Welcome {user.email}",
        "user_id": user.id,
        "2fa_enabled": user.twofa_enabled if hasattr(user, "twofa_enabled") else False,
    }


@app.get("/api/v1/admin/settings")
async def admin_settings(user=Depends(get_current_user)):
    """Admin-only endpoint"""
    if not user.has_role("admin"):
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Admin access required")

    return {
        "message": "Admin settings",
        "user": user.email,
    }


# ══════════════════════════════════════════════════════════════════════════════
# Startup and Shutdown Events
# ══════════════════════════════════════════════════════════════════════════════


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("🚀 SAHOOL Platform API starting...")
    print("🔐 2FA Security: Enabled")
    print(
        f"📋 Enforcement: {configure_twofa.__defaults__[0] if configure_twofa.__defaults__ else 'REQUIRED_FOR_ADMIN'}"
    )

    # Create a test admin user for development
    if app.debug:
        try:
            test_user = user_service.create_user(
                tenant_id="sahool-001",
                email="admin@sahool.io",
                name="Test Admin",
                name_ar="مسؤول تجريبي",
                password="admin123",  # Change this in production!
                roles=["admin"],
            )
            print(f"✅ Test admin user created: {test_user.email}")
        except ValueError:
            print("ℹ️  Test admin user already exists")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("👋 SAHOOL Platform API shutting down...")


# ══════════════════════════════════════════════════════════════════════════════
# Run Application
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "example_integration:app",
        host="0.0.0.0",
        port=3000,
        reload=True,
        log_level="info",
    )

"""
To run this example:

1. Install dependencies:
   pip install fastapi uvicorn pyotp qrcode[pil]

2. Run the application:
   python example_integration.py

3. Access the API:
   - API Docs: http://localhost:3000/docs
   - Login: POST http://localhost:3000/api/v1/auth/login
   - 2FA Setup: POST http://localhost:3000/admin/2fa/setup

4. Test the flow:
   a. Login with test credentials (admin@sahool.io / admin123)
   b. Navigate to http://localhost:3001/settings/security
   c. Set up 2FA by scanning QR code
   d. Logout and test 2FA login

Environment variables (optional):
   - API_URL: Backend API URL (default: http://localhost:3000)
   - ADMIN_URL: Admin dashboard URL (default: http://localhost:3001)
   - JWT_SECRET: Secret key for JWT tokens
   - DATABASE_URL: Database connection string
"""
