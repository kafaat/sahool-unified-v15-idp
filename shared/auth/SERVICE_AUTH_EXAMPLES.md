# Service-to-Service Authentication Examples

This document provides comprehensive examples for using the service-to-service authentication system in the SAHOOL platform.

## Table of Contents

- [Python (FastAPI) Examples](#python-fastapi-examples)
- [TypeScript (NestJS) Examples](#typescript-nestjs-examples)
- [Configuration](#configuration)
- [Service Communication Matrix](#service-communication-matrix)

---

## Python (FastAPI) Examples

### 1. Creating Service Tokens

```python
from shared.auth import create_service_token

# Create a service token for farm-service to call field-service
token = create_service_token(
    service_name="farm-service",
    target_service="field-service",
    ttl=300  # 5 minutes
)

# Use the token in HTTP requests
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get(
        "http://field-service/api/fields",
        headers={
            "X-Service-Token": token
        }
    )
```

### 2. Using ServiceToken Class

```python
from shared.auth import ServiceToken

# Create a token
token = ServiceToken.create(
    service_name="farm-service",
    target_service="field-service",
    ttl=600,
    extra_claims={"request_id": "req-123"}
)

# Verify a token
try:
    payload = ServiceToken.verify(token)
    print(f"Service: {payload['service_name']}")
    print(f"Target: {payload['target_service']}")
    print(f"Expires: {payload['exp']}")
except Exception as e:
    print(f"Invalid token: {e}")
```

### 3. Adding Service Auth Middleware to FastAPI App

```python
from fastapi import FastAPI
from shared.auth import ServiceAuthMiddleware

app = FastAPI()

# Add service authentication middleware
app.add_middleware(
    ServiceAuthMiddleware,
    current_service="field-service",  # Name of this service
    exclude_paths=["/health", "/docs", "/metrics"],
    require_service_auth=False  # Set to True to require service auth for all routes
)

@app.get("/internal/data")
async def get_internal_data(request: Request):
    # Access calling service if authenticated
    calling_service = request.state.calling_service
    if calling_service:
        return {"message": f"Called by {calling_service}"}
    return {"message": "Not a service request"}
```

### 4. Using Dependency Injection for Service Authentication

```python
from fastapi import APIRouter, Depends
from shared.auth import verify_service_request, require_service_auth

router = APIRouter(prefix="/internal")

# Require any valid service token
@router.get("/data")
async def get_data(
    service_info: dict = Depends(verify_service_request)
):
    calling_service = service_info["service_name"]
    return {
        "message": f"Called by {calling_service}",
        "data": [...]
    }

# Require specific services
@router.post("/process")
async def process_data(
    service_info: dict = Depends(
        require_service_auth(["farm-service", "crop-service"])
    )
):
    return {"status": "processed"}
```

### 5. Checking Service Authorization

```python
from shared.auth import is_service_authorized, get_allowed_targets

# Check if farm-service can call field-service
if is_service_authorized("farm-service", "field-service"):
    print("Authorized!")

# Get all services that farm-service can call
targets = get_allowed_targets("farm-service")
print(f"Farm service can call: {targets}")
```

### 6. Complete FastAPI Service Example

```python
from fastapi import FastAPI, Request, Depends
from shared.auth import (
    ServiceAuthMiddleware,
    verify_service_request,
    require_service_auth,
    create_service_token,
)
import httpx

app = FastAPI(title="Field Service")

# Add middleware
app.add_middleware(
    ServiceAuthMiddleware,
    current_service="field-service",
    exclude_paths=["/health"]
)

# Public endpoint
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Internal endpoint - any service can call
@app.get("/internal/fields")
async def get_fields(
    service_info: dict = Depends(verify_service_request)
):
    calling_service = service_info["service_name"]
    return {
        "fields": [...],
        "called_by": calling_service
    }

# Internal endpoint - only specific services
@app.post("/internal/update")
async def update_field(
    service_info: dict = Depends(
        require_service_auth(["farm-service"])
    )
):
    return {"status": "updated"}

# Making calls to other services
@app.get("/call-weather-service")
async def call_weather():
    # Create token to call weather service
    token = create_service_token(
        service_name="field-service",
        target_service="weather-service",
        ttl=300
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://weather-service/api/weather",
            headers={"X-Service-Token": token}
        )
        return response.json()
```

---

## TypeScript (NestJS) Examples

### 1. Creating Service Tokens

```typescript
import { createServiceToken } from "./shared/auth/service_auth";
import axios from "axios";

// Create a service token
const token = createServiceToken(
  "farm-service",
  "field-service",
  300, // 5 minutes
);

// Use the token in HTTP requests
const response = await axios.get("http://field-service/api/fields", {
  headers: {
    "X-Service-Token": token,
  },
});
```

### 2. Using ServiceToken Class

```typescript
import { ServiceToken } from "./shared/auth/service_auth";

// Create a token
const token = ServiceToken.create("farm-service", "field-service", 600, {
  request_id: "req-123",
});

// Verify a token
try {
  const payload = ServiceToken.verify(token);
  console.log(`Service: ${payload.service_name}`);
  console.log(`Target: ${payload.target_service}`);
  console.log(`Expires: ${payload.exp}`);
} catch (error) {
  console.error("Invalid token:", error);
}
```

### 3. Using ServiceAuthGuard in Controllers

```typescript
import { Controller, Get, UseGuards } from '@nestjs/common';
import {
  ServiceAuthGuard,
  AllowedServices,
  ServiceInfo,
  CallingService,
} from './shared/auth/service-auth.guard';
import { ServiceTokenPayload } from './shared/auth/service_auth';

@Controller('internal')
export class InternalController {
  // Any valid service can call
  @Get('data')
  @UseGuards(ServiceAuthGuard)
  async getData(@ServiceInfo() serviceInfo: ServiceTokenPayload) {
    return {
      message: `Called by ${serviceInfo.service_name}`,
      data: [...],
    };
  }

  // Only specific services can call
  @Get('fields')
  @UseGuards(ServiceAuthGuard)
  @AllowedServices('farm-service', 'crop-service')
  async getFields(@CallingService() callingService: string) {
    return {
      fields: [...],
      called_by: callingService,
    };
  }

  // Use simplified decorator
  @Post('update')
  @UseGuards(ServiceAuthGuard)
  @AllowedServices('farm-service')
  async updateField() {
    return { status: 'updated' };
  }
}
```

### 4. Using Guard at Controller Level

```typescript
import { Controller, Get, UseGuards } from '@nestjs/common';
import {
  ServiceAuthGuard,
  CurrentService,
  AllowedServices,
  ServiceInfo,
} from './shared/auth/service-auth.guard';

// Apply guard and configuration to entire controller
@Controller('internal')
@UseGuards(ServiceAuthGuard)
@CurrentService('field-service')
@AllowedServices('farm-service', 'crop-service')
export class InternalController {
  @Get('data')
  async getData(@ServiceInfo() serviceInfo) {
    return { data: [...] };
  }

  @Get('fields')
  async getFields() {
    return { fields: [...] };
  }
}
```

### 5. Global Service Guard

```typescript
// main.ts
import { NestFactory, Reflector } from "@nestjs/core";
import { AppModule } from "./app.module";
import { ServiceAuthGuard } from "./shared/auth/service-auth.guard";

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Add global service auth guard
  const reflector = app.get(Reflector);
  app.useGlobalGuards(new ServiceAuthGuard(reflector, "field-service"));

  await app.listen(3000);
}
bootstrap();
```

### 6. Optional Service Authentication

```typescript
import { Controller, Get, UseGuards } from '@nestjs/common';
import {
  OptionalServiceAuthGuard,
  ServiceInfo,
} from './shared/auth/service-auth.guard';
import { ServiceTokenPayload } from './shared/auth/service_auth';

@Controller('data')
export class DataController {
  // Can be called by both users and services
  @Get('items')
  @UseGuards(OptionalServiceAuthGuard)
  async getItems(@ServiceInfo() serviceInfo?: ServiceTokenPayload) {
    if (serviceInfo) {
      // Called by a service
      console.log(`Service call from ${serviceInfo.service_name}`);
      return { items: [...], source: 'service' };
    } else {
      // Called by a user
      console.log('User call');
      return { items: [...], source: 'user' };
    }
  }
}
```

### 7. Complete NestJS Service Example

```typescript
// app.module.ts
import { Module } from '@nestjs/common';
import { InternalController } from './internal.controller';
import { WeatherService } from './weather.service';

@Module({
  controllers: [InternalController],
  providers: [WeatherService],
})
export class AppModule {}

// internal.controller.ts
import { Controller, Get, Post, UseGuards } from '@nestjs/common';
import {
  ServiceAuthGuard,
  AllowedServices,
  ServiceInfo,
  CurrentService,
} from './shared/auth/service-auth.guard';
import { WeatherService } from './weather.service';

@Controller('internal')
@UseGuards(ServiceAuthGuard)
@CurrentService('field-service')
export class InternalController {
  constructor(private weatherService: WeatherService) {}

  @Get('fields')
  @AllowedServices('farm-service', 'crop-service')
  async getFields(@ServiceInfo() serviceInfo) {
    return {
      fields: [...],
      called_by: serviceInfo.service_name,
    };
  }

  @Post('update')
  @AllowedServices('farm-service')
  async updateField() {
    return { status: 'updated' };
  }

  // Call another service
  @Get('weather-data')
  async getWeatherData() {
    return this.weatherService.fetchWeather();
  }
}

// weather.service.ts
import { Injectable } from '@nestjs/common';
import { createServiceToken } from './shared/auth/service_auth';
import axios from 'axios';

@Injectable()
export class WeatherService {
  async fetchWeather() {
    // Create token to call weather service
    const token = createServiceToken(
      'field-service',
      'weather-service',
      300
    );

    const response = await axios.get(
      'http://weather-service/api/weather',
      {
        headers: { 'X-Service-Token': token },
      }
    );

    return response.data;
  }
}
```

---

## Configuration

### Environment Variables

```bash
# JWT Configuration (shared with user authentication)
JWT_SECRET=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_ISSUER=sahool-platform
JWT_AUDIENCE=sahool-api

# Service Name (for automatic service identification)
SERVICE_NAME=farm-service
```

### Updating Service Communication Matrix

To allow a new service or modify communication rules, edit the `SERVICE_COMMUNICATION_MATRIX` in both:

1. `/shared/auth/service_auth.py` (Python)
2. `/shared/auth/service_auth.ts` (TypeScript)

```python
# Python example
SERVICE_COMMUNICATION_MATRIX = {
    "farm-service": [
        "field-service",
        "crop-service",
        "new-service",  # Add new service
    ],
}
```

```typescript
// TypeScript example
export const SERVICE_COMMUNICATION_MATRIX: Record<string, string[]> = {
  "farm-service": [
    "field-service",
    "crop-service",
    "new-service", // Add new service
  ],
};
```

---

## Service Communication Matrix

Current allowed service communications:

```
idp-service → ALL SERVICES
farm-service → field-service, crop-service, equipment-service, user-service, tenant-service
field-service → crop-service, weather-service, precision-ag-service
crop-service → weather-service, advisory-service, precision-ag-service
weather-service → advisory-service, analytics-service
advisory-service → notification-service, analytics-service
analytics-service → notification-service
equipment-service → inventory-service, farm-service
precision-ag-service → weather-service, field-service, crop-service
payment-service → user-service, tenant-service, notification-service
user-service → tenant-service, notification-service
tenant-service → notification-service
inventory-service → notification-service
notification-service → (receives calls only)
```

---

## Error Handling

### Python Error Handling

```python
from shared.auth import ServiceToken, AuthException

try:
    token = ServiceToken.create("farm-service", "field-service")
except AuthException as e:
    print(f"Error: {e.error.code}")
    print(f"Message: {e.error.en}")
    print(f"Status: {e.status_code}")
```

### TypeScript Error Handling

```typescript
import { ServiceToken, ServiceAuthException } from "./shared/auth/service_auth";

try {
  const token = ServiceToken.create("farm-service", "field-service");
} catch (error) {
  if (error instanceof ServiceAuthException) {
    console.error(`Error: ${error.error.code}`);
    console.error(`Message: ${error.error.en}`);
    console.error(`Status: ${error.statusCode}`);
  }
}
```

---

## Best Practices

1. **Use Short TTL**: Service tokens should have short TTL (5-10 minutes)
2. **Create Tokens on Demand**: Create a new token for each service call
3. **Validate Target Service**: Always verify the target service matches your service
4. **Use Middleware**: Apply middleware globally and use dependencies for specific routes
5. **Log Service Calls**: Log all inter-service communications for debugging
6. **Update Matrix**: Keep the communication matrix updated with actual service dependencies
7. **Environment Variables**: Use `SERVICE_NAME` environment variable for automatic configuration

---

## Testing

### Python Testing Example

```python
import pytest
from shared.auth import create_service_token, verify_service_token

def test_service_token_creation():
    token = create_service_token("farm-service", "field-service")
    assert token is not None

    payload = verify_service_token(token)
    assert payload["service_name"] == "farm-service"
    assert payload["target_service"] == "field-service"

def test_unauthorized_service():
    with pytest.raises(Exception):
        # notification-service cannot call farm-service
        create_service_token("notification-service", "farm-service")
```

### TypeScript Testing Example

```typescript
import {
  createServiceToken,
  verifyServiceToken,
} from "./shared/auth/service_auth";

describe("Service Authentication", () => {
  it("should create and verify service token", () => {
    const token = createServiceToken("farm-service", "field-service");
    expect(token).toBeDefined();

    const payload = verifyServiceToken(token);
    expect(payload.service_name).toBe("farm-service");
    expect(payload.target_service).toBe("field-service");
  });

  it("should reject unauthorized service", () => {
    expect(() => {
      // notification-service cannot call farm-service
      createServiceToken("notification-service", "farm-service");
    }).toThrow();
  });
});
```

---

## Migration Guide

### Migrating Existing Service Calls

1. **Add service authentication to receiving service:**

```python
# Before
@app.get("/internal/data")
async def get_data():
    return {"data": [...]}

# After
from shared.auth import verify_service_request

@app.get("/internal/data")
async def get_data(
    service_info: dict = Depends(verify_service_request)
):
    return {"data": [...]}
```

2. **Update calling service to include token:**

```python
# Before
response = await client.get("http://other-service/internal/data")

# After
from shared.auth import create_service_token

token = create_service_token("my-service", "other-service")
response = await client.get(
    "http://other-service/internal/data",
    headers={"X-Service-Token": token}
)
```

---

For more information, refer to the main authentication module documentation.
