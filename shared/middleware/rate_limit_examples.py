"""
Rate Limiting Examples for SAHOOL Platform
أمثلة استخدام تحديد المعدل لمنصة سهول

This file contains practical examples of how to use rate limiting
in your FastAPI applications.
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse

# Import rate limiting components
from shared.middleware import (
    rate_limit,
    rate_limit_by_user,
    rate_limit_by_api_key,
    rate_limit_by_tenant,
    rate_limit_middleware,
    RateLimiter,
    RateLimitConfig,
)
from shared.auth.middleware import RateLimitMiddleware


# ═══════════════════════════════════════════════════════════════════════════════
# Example 1: Basic FastAPI Application with Global Rate Limiting
# ═══════════════════════════════════════════════════════════════════════════════


def example_1_basic_global_rate_limiting():
    """
    مثال 1: تطبيق بسيط مع تحديد معدل عام

    This example shows how to add rate limiting to all endpoints
    in your FastAPI application.
    """
    app = FastAPI(title="Example 1: Global Rate Limiting")

    # Add global rate limiting middleware
    app.middleware("http")(rate_limit_middleware)

    @app.get("/")
    async def root():
        return {"message": "Welcome to SAHOOL API"}

    @app.get("/data")
    async def get_data():
        """All endpoints automatically have rate limiting"""
        return {"data": "Some data"}

    return app


# ═══════════════════════════════════════════════════════════════════════════════
# Example 2: Custom Rate Limiting with Different Limits
# ═══════════════════════════════════════════════════════════════════════════════


def example_2_custom_rate_limits():
    """
    مثال 2: endpoints مختلفة مع حدود مخصصة

    This example shows how to use decorators to apply different
    rate limits to different endpoints.
    """
    app = FastAPI(title="Example 2: Custom Rate Limits")

    @app.get("/public")
    @rate_limit(requests_per_minute=100, requests_per_hour=5000)
    async def public_endpoint(request: Request):
        """Public endpoint with higher limits"""
        return {"message": "Public data", "tier": "public"}

    @app.get("/expensive")
    @rate_limit(requests_per_minute=5, requests_per_hour=50, burst_limit=2)
    async def expensive_endpoint(request: Request):
        """Expensive operation with strict limits"""
        # Simulate expensive operation
        import asyncio

        await asyncio.sleep(0.1)
        return {"message": "Expensive operation completed"}

    @app.post("/write")
    @rate_limit(requests_per_minute=20, requests_per_hour=200)
    async def write_endpoint(request: Request):
        """Write operation with moderate limits"""
        return {"message": "Data written successfully"}

    return app


# ═══════════════════════════════════════════════════════════════════════════════
# Example 3: User-Based Rate Limiting (Requires Authentication)
# ═══════════════════════════════════════════════════════════════════════════════


def example_3_user_based_rate_limiting():
    """
    مثال 3: تحديد معدل بناءً على المستخدم

    This example shows how to apply rate limits per authenticated user.
    Requires JWT authentication middleware.
    """
    from shared.auth.middleware import JWTAuthMiddleware

    app = FastAPI(title="Example 3: User-Based Rate Limiting")

    # Add authentication first
    app.add_middleware(JWTAuthMiddleware, require_auth=False)

    @app.get("/user/profile")
    @rate_limit_by_user(requests_per_minute=30, requests_per_hour=500)
    async def get_user_profile(request: Request):
        """Rate limited per user ID"""
        user = request.state.user if hasattr(request.state, "user") else None
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")

        return {
            "user_id": user.id,
            "email": user.email,
            "roles": user.roles,
        }

    @app.post("/user/update")
    @rate_limit_by_user(requests_per_minute=10, requests_per_hour=100)
    async def update_user_profile(request: Request):
        """Stricter limits for write operations"""
        user = request.state.user if hasattr(request.state, "user") else None
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")

        return {"message": "Profile updated successfully"}

    return app


# ═══════════════════════════════════════════════════════════════════════════════
# Example 4: API Key Based Rate Limiting
# ═══════════════════════════════════════════════════════════════════════════════


def example_4_api_key_rate_limiting():
    """
    مثال 4: تحديد معدل بناءً على API key

    This example shows how to apply rate limits based on API keys.
    Useful for public APIs with API key authentication.
    """
    app = FastAPI(title="Example 4: API Key Rate Limiting")

    @app.get("/api/v1/data")
    @rate_limit_by_api_key(
        requests_per_minute=100, requests_per_hour=5000, header_name="X-API-Key"
    )
    async def get_api_data(request: Request):
        """Rate limited per API key"""
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            raise HTTPException(status_code=401, detail="API key required")

        return {
            "data": "API response",
            "api_key": api_key[:8] + "...",  # Show partial key
        }

    @app.post("/api/v1/process")
    @rate_limit_by_api_key(
        requests_per_minute=50, requests_per_hour=1000, header_name="X-API-Key"
    )
    async def process_api_request(request: Request):
        """Processing endpoint with lower limits"""
        return {"status": "processing"}

    return app


# ═══════════════════════════════════════════════════════════════════════════════
# Example 5: Tenant-Based Rate Limiting (Multi-Tenancy)
# ═══════════════════════════════════════════════════════════════════════════════


def example_5_tenant_rate_limiting():
    """
    مثال 5: تحديد معدل بناءً على المستأجر (Multi-tenant)

    This example shows how to apply rate limits per tenant in a
    multi-tenant application.
    """
    app = FastAPI(title="Example 5: Tenant Rate Limiting")

    @app.get("/tenant/data")
    @rate_limit_by_tenant(requests_per_minute=200, requests_per_hour=10000)
    async def get_tenant_data(request: Request):
        """Rate limited per tenant"""
        tenant_id = request.headers.get("X-Tenant-ID")
        if not tenant_id:
            raise HTTPException(status_code=400, detail="Tenant ID required")

        return {
            "tenant_id": tenant_id,
            "data": "Tenant-specific data",
        }

    return app


# ═══════════════════════════════════════════════════════════════════════════════
# Example 6: Custom Key Function
# ═══════════════════════════════════════════════════════════════════════════════


def example_6_custom_key_function():
    """
    مثال 6: دالة مفتاح مخصصة

    This example shows how to create custom rate limit keys based on
    any request property.
    """
    app = FastAPI(title="Example 6: Custom Key Function")

    def organization_key(request: Request) -> str:
        """Rate limit by organization ID"""
        org_id = request.headers.get("X-Organization-ID", "default")
        # nosemgrep
        return f"org:{org_id}"

    def combined_key(request: Request) -> str:
        """Rate limit by combination of user and organization"""
        user_id = getattr(request.state, "user_id", "anonymous")
        org_id = request.headers.get("X-Organization-ID", "default")
        # nosemgrep
        return f"user:{user_id}:org:{org_id}"

    @app.get("/org/resources")
    @rate_limit(
        requests_per_minute=50, requests_per_hour=2000, key_func=organization_key
    )
    async def get_org_resources(request: Request):
        """Rate limited by organization"""
        return {"message": "Organization resources"}

    @app.post("/org/action")
    @rate_limit(requests_per_minute=20, requests_per_hour=500, key_func=combined_key)
    async def org_action(request: Request):
        """Rate limited by user + organization combination"""
        return {"status": "action completed"}

    return app


# ═══════════════════════════════════════════════════════════════════════════════
# Example 7: Using RateLimitMiddleware Directly
# ═══════════════════════════════════════════════════════════════════════════════


def example_7_middleware_configuration():
    """
    مثال 7: تكوين Middleware مباشرة

    This example shows how to configure the RateLimitMiddleware
    with custom settings.
    """
    app = FastAPI(title="Example 7: Middleware Configuration")

    # Configure rate limiting middleware with custom settings
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=100,
        requests_per_hour=2000,
        burst_limit=20,
        exclude_paths=[
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/metrics",
        ],
        redis_url="redis://localhost:6379/0",  # Optional
    )

    @app.get("/")
    async def root():
        return {"message": "Rate limited by middleware"}

    @app.get("/health")
    async def health():
        """This endpoint is excluded from rate limiting"""
        return {"status": "healthy"}

    return app


# ═══════════════════════════════════════════════════════════════════════════════
# Example 8: Manual Rate Limit Checking
# ═══════════════════════════════════════════════════════════════════════════════


def example_8_manual_rate_limit_check():
    """
    مثال 8: فحص يدوي لتحديد المعدل

    This example shows how to manually check rate limits in your code.
    """
    app = FastAPI(title="Example 8: Manual Rate Limit Check")

    # Create custom limiter
    limiter = RateLimiter()

    @app.get("/manual-check")
    async def manual_rate_limit_check(request: Request):
        """Manually check rate limit"""

        # Check rate limit
        allowed, headers = limiter.check_rate_limit(request)

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "rate_limit_exceeded",
                    "error_ar": "تم تجاوز حد الطلبات",
                    "message": "Too many requests",
                },
                headers=headers,
            )

        # Process request
        return {
            "message": "Request allowed",
            "rate_limit_info": headers,
        }

    return app


# ═══════════════════════════════════════════════════════════════════════════════
# Example 9: Dynamic Rate Limits Based on User Tier
# ═══════════════════════════════════════════════════════════════════════════════


def example_9_dynamic_rate_limits():
    """
    مثال 9: حدود ديناميكية بناءً على مستوى المستخدم

    This example shows how to apply different rate limits based on
    user subscription tier.
    """
    app = FastAPI(title="Example 9: Dynamic Rate Limits")

    async def get_user_tier(request: Request) -> str:
        """Get user tier from token or database"""
        # In real application, get from JWT token or database
        return request.headers.get("X-User-Tier", "free")

    @app.get("/dynamic")
    async def dynamic_rate_limit(request: Request):
        """Apply rate limit based on user tier"""
        tier = await get_user_tier(request)

        # Define tier-specific limits
        tier_limits = {
            "free": RateLimitConfig(
                requests_per_minute=30, requests_per_hour=500, burst_limit=5
            ),
            "standard": RateLimitConfig(
                requests_per_minute=60, requests_per_hour=2000, burst_limit=10
            ),
            "premium": RateLimitConfig(
                requests_per_minute=120, requests_per_hour=5000, burst_limit=20
            ),
        }

        config = tier_limits.get(tier, tier_limits["free"])

        # Check rate limit with custom config
        limiter = RateLimiter()
        # Note: You'd need to customize the limiter to use this config
        # This is a simplified example

        return {
            "message": "Request allowed",
            "tier": tier,
            "limits": {
                "requests_per_minute": config.requests_per_minute,
                "requests_per_hour": config.requests_per_hour,
            },
        }

    return app


# ═══════════════════════════════════════════════════════════════════════════════
# Example 10: Complete Production Application
# ═══════════════════════════════════════════════════════════════════════════════


def example_10_complete_production_app():
    """
    مثال 10: تطبيق إنتاج كامل

    This example shows a complete production-ready application with
    authentication, rate limiting, and proper error handling.
    """
    from shared.auth.middleware import JWTAuthMiddleware, SecurityHeadersMiddleware

    app = FastAPI(
        title="SAHOOL Production API",
        version="1.0.0",
        description="Complete production API with rate limiting",
    )

    # 1. Security headers
    app.add_middleware(SecurityHeadersMiddleware)

    # 2. JWT Authentication
    app.add_middleware(
        JWTAuthMiddleware,
        exclude_paths=["/", "/health", "/docs", "/redoc"],
        require_auth=False,
    )

    # 3. Rate limiting
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=60,
        requests_per_hour=2000,
        burst_limit=10,
        exclude_paths=["/health", "/docs", "/redoc"],
    )

    # Exception handler for rate limits
    @app.exception_handler(HTTPException)
    async def rate_limit_exception_handler(request: Request, exc: HTTPException):
        if exc.status_code == 429:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "error_ar": "تم تجاوز حد الطلبات",
                    "message": "Too many requests. Please try again later.",
                    "message_ar": "طلبات كثيرة جداً. يرجى المحاولة لاحقاً.",
                    "retry_after": exc.headers.get("Retry-After", 60),
                },
                headers=exc.headers,
            )
        raise exc

    # Public endpoints
    @app.get("/")
    async def root():
        return {
            "name": "SAHOOL API",
            "version": "1.0.0",
            "docs": "/docs",
        }

    @app.get("/health")
    async def health():
        """Health check - no rate limiting"""
        return {"status": "healthy"}

    # Protected endpoints
    @app.get("/user/profile")
    @rate_limit_by_user(requests_per_minute=30)
    async def get_profile(request: Request):
        """Get user profile"""
        user = request.state.user
        return {"user_id": user.id, "email": user.email}

    @app.get("/data/export")
    @rate_limit(requests_per_minute=5, burst_limit=1)
    async def export_data(request: Request):
        """Expensive export operation"""
        return {"message": "Export started", "status": "processing"}

    @app.post("/data/import")
    @rate_limit_by_user(requests_per_minute=10)
    async def import_data(request: Request):
        """Import data"""
        return {"message": "Import completed"}

    return app


# ═══════════════════════════════════════════════════════════════════════════════
# Main: Run Examples
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    # Choose which example to run
    # app = example_1_basic_global_rate_limiting()
    # app = example_2_custom_rate_limits()
    # app = example_3_user_based_rate_limiting()
    # app = example_4_api_key_rate_limiting()
    # app = example_5_tenant_rate_limiting()
    # app = example_6_custom_key_function()
    # app = example_7_middleware_configuration()
    # app = example_8_manual_rate_limit_check()
    # app = example_9_dynamic_rate_limits()
    app = example_10_complete_production_app()

    # Run the application
    uvicorn.run(app, host="0.0.0.0", port=8000)

    print("\n" + "=" * 80)
    print("Rate Limiting Examples - SAHOOL Platform")
    print("=" * 80)
    print("\nServer running at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("\nTest with curl:")
    print("  curl http://localhost:8000/")
    print("\nTo test rate limiting:")
    print("  for i in {1..100}; do curl http://localhost:8000/; done")
    print("=" * 80 + "\n")
