"""
Example FastAPI Service with Error Localization
مثال على خدمة FastAPI مع توطين الأخطاء

This demonstrates how to use the error localization system in a FastAPI service.
"""

from fastapi import FastAPI, Request, Depends, Header
from typing import Optional, List
from pydantic import BaseModel, Field

# Import error handling utilities
from exception_handler import (
    setup_exception_handlers,
    NotFoundError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    AppError,
)

# Create FastAPI app
app = FastAPI(
    title="SAHOOL Field Service Example",
    description="Example service demonstrating error localization",
    version="1.0.0",
)

# Setup exception handlers with localization support
setup_exception_handlers(app)


# Example models
class Field(BaseModel):
    id: str
    name: str
    crop_type: str
    area_hectares: float
    tenant_id: str


class FieldCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    crop_type: str = Field(..., min_length=1, max_length=50)
    area_hectares: float = Field(..., gt=0, le=10000)
    tenant_id: str


# Mock database
FIELDS_DB = {
    "field-123": Field(
        id="field-123",
        name="North Field",
        crop_type="Wheat",
        area_hectares=50.5,
        tenant_id="tenant-1",
    )
}


# ════════════════════════════════════════════════════════════════════════
# EXAMPLE 1: NOT FOUND ERROR
# ════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/fields/{field_id}")
async def get_field(field_id: str, accept_language: Optional[str] = Header(None)):
    """
    Get a field by ID.

    Example requests:
    - English: GET /api/v1/fields/invalid-id
    - Arabic: GET /api/v1/fields/invalid-id -H "Accept-Language: ar"

    Error response:
    {
        "success": false,
        "error": {
            "code": "NOT_FOUND",
            "message": "Field not found.",
            "message_ar": "الحقل غير موجود.",
            "error": "الحقل غير موجود.",  # Matches Accept-Language
            "error_id": "A3F2D891"
        }
    }
    """
    field = FIELDS_DB.get(field_id)

    if not field:
        # Raises 404 with bilingual message
        # The error handler will automatically use Accept-Language header
        raise NotFoundError("Field", "الحقل")

    return {"success": True, "data": field}


# ════════════════════════════════════════════════════════════════════════
# EXAMPLE 2: CONFLICT ERROR
# ════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/fields")
async def create_field(field_data: FieldCreate):
    """
    Create a new field.

    Example request:
    POST /api/v1/fields
    {
        "name": "North Field",  // Already exists!
        "crop_type": "Wheat",
        "area_hectares": 50.5,
        "tenant_id": "tenant-1"
    }

    Error response (409 Conflict):
    {
        "success": false,
        "error": {
            "code": "CONFLICT",
            "message": "A field with this name already exists",
            "message_ar": "حقل بهذا الاسم موجود بالفعل",
            "error_id": "B7E3C542",
            "details": {
                "field_name": "North Field"
            }
        }
    }
    """
    # Check if field already exists
    for field in FIELDS_DB.values():
        if field.name == field_data.name and field.tenant_id == field_data.tenant_id:
            raise ConflictError(
                "A field with this name already exists",
                "حقل بهذا الاسم موجود بالفعل",
                details={"field_name": field_data.name},
            )

    # Create new field
    field_id = f"field-{len(FIELDS_DB) + 1}"
    new_field = Field(id=field_id, **field_data.dict())
    FIELDS_DB[field_id] = new_field

    return {"success": True, "data": new_field}


# ════════════════════════════════════════════════════════════════════════
# EXAMPLE 3: VALIDATION ERROR
# ════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/fields/{field_id}/validate-boundary")
async def validate_boundary(field_id: str, coordinates: List[List[float]]):
    """
    Validate field boundary coordinates.

    Example request with invalid data:
    POST /api/v1/fields/field-123/validate-boundary
    {
        "coordinates": [[0, 0], [0, 1]]  // Less than 3 points!
    }

    Error response (400 Bad Request):
    {
        "success": false,
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Field boundary must have at least 3 points",
            "message_ar": "حدود الحقل يجب أن تحتوي على 3 نقاط على الأقل",
            "error_id": "C9D4E123",
            "details": {
                "points_provided": 2,
                "minimum_required": 3
            }
        }
    }
    """
    if len(coordinates) < 3:
        raise ValidationError(
            "Field boundary must have at least 3 points",
            "حدود الحقل يجب أن تحتوي على 3 نقاط على الأقل",
            details={
                "points_provided": len(coordinates),
                "minimum_required": 3,
            },
        )

    return {
        "success": True,
        "message": "Boundary is valid",
        "message_ar": "الحدود صالحة",
    }


# ════════════════════════════════════════════════════════════════════════
# EXAMPLE 4: AUTHENTICATION ERROR
# ════════════════════════════════════════════════════════════════════════

async def verify_token(authorization: Optional[str] = Header(None)) -> str:
    """Dependency to verify authentication token"""
    if not authorization:
        raise AuthenticationError(
            "Authentication token is required",
            "رمز المصادقة مطلوب",
        )

    if not authorization.startswith("Bearer "):
        raise AuthenticationError(
            "Invalid authentication token format",
            "تنسيق رمز المصادقة غير صالح",
        )

    # Mock token validation
    token = authorization[7:]
    if token != "valid-token":
        raise AuthenticationError(
            "Invalid authentication token",
            "رمز المصادقة غير صالح",
        )

    return token


@app.get("/api/v1/fields/{field_id}/protected")
async def protected_endpoint(
    field_id: str,
    token: str = Depends(verify_token),
):
    """
    Protected endpoint requiring authentication.

    Example request without token:
    GET /api/v1/fields/field-123/protected

    Error response (401 Unauthorized):
    {
        "success": false,
        "error": {
            "code": "AUTHENTICATION_ERROR",
            "message": "Authentication token is required",
            "message_ar": "رمز المصادقة مطلوب",
            "error_id": "D5F6A234"
        }
    }
    """
    field = FIELDS_DB.get(field_id)
    if not field:
        raise NotFoundError("Field", "الحقل")

    return {
        "success": True,
        "data": field,
        "message": "Access granted",
    }


# ════════════════════════════════════════════════════════════════════════
# EXAMPLE 5: CUSTOM ERROR WITH CUSTOM CODE
# ════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/fields/{field_id}/harvest")
async def harvest_field(field_id: str):
    """
    Harvest a field.

    Example with custom business logic error:
    POST /api/v1/fields/field-123/harvest

    Error response (400 Bad Request):
    {
        "success": false,
        "error": {
            "code": "CROP_NOT_READY",
            "message": "Crop is not ready for harvest",
            "message_ar": "المحصول ليس جاهزاً للحصاد",
            "error_id": "E7G8H345",
            "details": {
                "days_until_ready": 30,
                "current_growth_stage": "flowering"
            }
        }
    }
    """
    field = FIELDS_DB.get(field_id)
    if not field:
        raise NotFoundError("Field", "الحقل")

    # Custom business logic error
    raise AppError(
        status_code=400,
        error_code="CROP_NOT_READY",
        message="Crop is not ready for harvest",
        message_ar="المحصول ليس جاهزاً للحصاد",
        details={
            "days_until_ready": 30,
            "current_growth_stage": "flowering",
        },
    )


# ════════════════════════════════════════════════════════════════════════
# TESTING INSTRUCTIONS
# ════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 70)
    print("SAHOOL Error Localization Example Service")
    print("خدمة مثال توطين الأخطاء لنظام سهول")
    print("=" * 70)
    print("\nStarting server at http://localhost:8000")
    print("\nTry these endpoints:")
    print("\n1. Not Found Error (English):")
    print("   curl http://localhost:8000/api/v1/fields/invalid-id")
    print("\n2. Not Found Error (Arabic):")
    print('   curl -H "Accept-Language: ar" http://localhost:8000/api/v1/fields/invalid-id')
    print("\n3. Conflict Error:")
    print('   curl -X POST http://localhost:8000/api/v1/fields \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"name":"North Field","crop_type":"Wheat","area_hectares":50,"tenant_id":"tenant-1"}\'')
    print("\n4. Authentication Error:")
    print("   curl http://localhost:8000/api/v1/fields/field-123/protected")
    print("\n5. Documentation:")
    print("   http://localhost:8000/docs")
    print("=" * 70 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
