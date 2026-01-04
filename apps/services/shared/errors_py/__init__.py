"""
Shared Error Handling Module for Python Services
وحدة معالجة الأخطاء المشتركة

@module shared/errors_py
@description Centralized error handling for all SAHOOL FastAPI services

@example
```python
from apps.services.shared.errors_py import (
    ErrorCode,
    AppException,
    NotFoundException,
    ValidationException,
    setup_exception_handlers,
)

# Throw a custom exception
raise NotFoundException(ErrorCode.FARM_NOT_FOUND, details={"farm_id": "farm-123"})

# Setup exception handlers in FastAPI app
setup_exception_handlers(app)
```
"""

# Export error codes and types
from .error_codes import (
    ERROR_REGISTRY,
    BilingualMessage,
    ErrorCategory,
    ErrorCode,
    ErrorCodeMetadata,
    get_error_codes_by_category,
    get_error_metadata,
)

# Export exception handlers
from .exception_handlers import (
    add_request_id_middleware,
    get_request_id,
    setup_exception_handlers,
)

# Export custom exceptions
from .exceptions import (
    AppException,
    AuthenticationException,
    AuthorizationException,
    BusinessLogicException,
    ConflictException,
    DatabaseException,
    ExternalServiceException,
    InternalServerException,
    NotFoundException,
    RateLimitException,
    ValidationException,
)

# Export response models
from .response_models import (
    ErrorDetailsModel,
    ErrorResponseModel,
    FieldErrorModel,
    PaginatedResponseModel,
    SuccessResponseModel,
    create_paginated_response,
    create_success_response,
)

__all__ = [
    # Error codes
    "ErrorCode",
    "ErrorCategory",
    "BilingualMessage",
    "ErrorCodeMetadata",
    "ERROR_REGISTRY",
    "get_error_metadata",
    "get_error_codes_by_category",
    # Exceptions
    "AppException",
    "ValidationException",
    "AuthenticationException",
    "AuthorizationException",
    "NotFoundException",
    "ConflictException",
    "BusinessLogicException",
    "ExternalServiceException",
    "DatabaseException",
    "InternalServerException",
    "RateLimitException",
    # Response models
    "FieldErrorModel",
    "ErrorDetailsModel",
    "ErrorResponseModel",
    "SuccessResponseModel",
    "PaginatedResponseModel",
    "create_success_response",
    "create_paginated_response",
    # Exception handlers
    "setup_exception_handlers",
    "get_request_id",
    "add_request_id_middleware",
]
