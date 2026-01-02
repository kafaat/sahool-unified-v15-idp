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
    ErrorCode,
    ErrorCategory,
    BilingualMessage,
    ErrorCodeMetadata,
    ERROR_REGISTRY,
    get_error_metadata,
    get_error_codes_by_category,
)

# Export custom exceptions
from .exceptions import (
    AppException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    NotFoundException,
    ConflictException,
    BusinessLogicException,
    ExternalServiceException,
    DatabaseException,
    InternalServerException,
    RateLimitException,
)

# Export response models
from .response_models import (
    FieldErrorModel,
    ErrorDetailsModel,
    ErrorResponseModel,
    SuccessResponseModel,
    PaginatedResponseModel,
    create_success_response,
    create_paginated_response,
)

# Export exception handlers
from .exception_handlers import (
    setup_exception_handlers,
    get_request_id,
    add_request_id_middleware,
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
