# SAHOOL Platform - OpenAPI Schema Documentation

**Version:** 16.0.0  
**Generated:** 2026-02-11  
**Platform:** SAHOOL Agricultural Intelligence Platform  
**Organization:** KAFAAT

---

## Table of Contents

1. [Introduction](#introduction)
2. [API Gateway Configuration](#api-gateway-configuration)
3. [Authentication & Security](#authentication--security)
4. [Infrastructure Services](#infrastructure-services)
5. [Node.js Services (NestJS)](#nodejs-services-nestjs)
6. [Python Services (FastAPI)](#python-services-fastapi)
7. [AI/ML Services](#aiml-services)
8. [Common Patterns](#common-patterns)
9. [Error Handling](#error-handling)
10. [Rate Limiting](#rate-limiting)

---

## Introduction

This document provides comprehensive OpenAPI schema definitions for all active services in the SAHOOL platform. All services are accessible through the Kong API Gateway and follow standardized patterns for authentication, error handling, and response formats.

### Base URLs

- **Development:** `http://localhost:8000` (Kong Gateway)
- **Staging:** `https://api-staging.sahool.io`
- **Production:** `https://api.sahool.io`

### Technology Stack

| Category | Technologies |
|----------|--------------|
| **API Gateway** | Kong 3.4 |
| **Node.js Services** | NestJS, Express, Prisma ORM |
| **Python Services** | FastAPI, Uvicorn, Tortoise ORM |
| **Database** | PostgreSQL 16 with PostGIS 3.4 |
| **Cache** | Redis 7.4 |
| **Message Queue** | NATS 2.10 |
| **Authentication** | JWT (HS256/RS256) |

---

## API Gateway Configuration

### Global Plugins (Applied to All Routes)

```yaml
# Kong Global Plugins
plugins:
  - cors                    # Cross-Origin Resource Sharing
  - prometheus             # Metrics collection
  - correlation-id         # Distributed tracing
  - request-size-limiting  # Max 10MB payload
  - response-transformer   # Security headers
  - bot-detection         # Block malicious bots
```

### Security Headers (Auto-Applied)

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Referrer-Policy: strict-origin-when-cross-origin
X-Correlation-Id: {uuid}
```

### CORS Configuration

**Development:**
```yaml
origins: ["*"]
credentials: false
```

**Production:**
```yaml
origins: 
  - "https://app.sahool.com"
  - "https://admin.sahool.com"
  - "https://mobile.sahool.com"
credentials: true
```

---

## Authentication & Security

### Security Schemes

```yaml
securitySchemes:
  BearerAuth:
    type: http
    scheme: bearer
    bearerFormat: JWT
    description: |
      JWT token obtained from /api/v1/auth/login
      Include in Authorization header: "Bearer {token}"
  
  ApiKeyAuth:
    type: apiKey
    in: header
    name: X-API-Key
    description: API key for machine-to-machine authentication
```

### JWT Token Structure

```json
{
  "sub": "user_id",
  "tenant_id": "tenant_001",
  "role": "farmer|admin|agronomist|operator",
  "permissions": ["field:read", "field:write"],
  "iat": 1707674400,
  "exp": 1707760800
}
```

### Public Endpoints (No Authentication Required)

```
/api/v1/auth/login
/api/v1/auth/register
/api/v1/auth/forgot-password
/api/v1/auth/reset-password
/api/v1/auth/send-otp
/api/v1/auth/verify-otp
/api/v1/auth/refresh
/healthz
/readyz
/metrics
```

---

## Infrastructure Services

### PostgreSQL Database

**Service:** `postgres`  
**Port:** `5432` (internal), `127.0.0.1:5432` (host)  
**Image:** `postgis/postgis:16-3.4`

**Extensions:**
- PostGIS 3.4 (Geospatial)
- pgcrypto (Encryption)
- pg_stat_statements (Performance)

**No API Endpoints** - Accessed via connection pooler (PgBouncer)

---

### PgBouncer Connection Pooler

**Service:** `pgbouncer`  
**Port:** `6432` (internal), `127.0.0.1:6432` (host)  
**Image:** `edoburu/pgbouncer:v1.23.1-p3`

**Configuration:**
- Pool Mode: Transaction
- Max DB Connections: 250
- Default Pool Size: 30
- Max Client Connections: 800

**No API Endpoints** - Database proxy service

---

### Redis Cache & Session Store

**Service:** `redis`  
**Port:** `6379` (internal), `127.0.0.1:6379` (host)  
**Image:** `redis:7.4-alpine`

**Features:**
- Session management
- Rate limiting
- Cache layer
- Pub/Sub messaging

**No API Endpoints** - Client library access only

---

### NATS Message Broker

**Service:** `nats`  
**Port:** `4222` (client), `8222` (monitoring)  
**Image:** `nats:2.10.24-alpine`

**Event Subjects:**
```
sahool.{tenant_id}.fields.created
sahool.{tenant_id}.fields.updated
sahool.{tenant_id}.irrigation.scheduled
sahool.{tenant_id}.alerts.generated
```

**Monitoring Endpoint:**
```http
GET http://localhost:8222/varz
```

---

### HashiCorp Vault (Secrets Management)

**Service:** `vault`  
**Port:** `8200`  
**Image:** `hashicorp/vault:1.17`

```yaml
openapi: 3.0.3
info:
  title: HashiCorp Vault API
  version: 1.17.0

paths:
  /v1/sys/health:
    get:
      summary: Health check
      responses:
        '200':
          description: Vault is healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  initialized:
                    type: boolean
                  sealed:
                    type: boolean
                  standby:
                    type: boolean
                  version:
                    type: string

  /v1/secret/data/{path}:
    get:
      summary: Read secret
      security:
        - VaultToken: []
      parameters:
        - name: path
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Secret data
```

---

### Kong API Gateway

**Service:** `kong`  
**Port:** `8000` (HTTP), `8443` (HTTPS), `8001` (Admin)  
**Image:** `kong:3.4`

**Admin API:**

```yaml
openapi: 3.0.3
info:
  title: Kong Admin API
  version: 3.4.0

paths:
  /services:
    get:
      summary: List all services
      responses:
        '200':
          description: List of Kong services
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/Service'

  /routes:
    get:
      summary: List all routes
      responses:
        '200':
          description: List of Kong routes

components:
  schemas:
    Service:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        protocol:
          type: string
          enum: [http, https]
        host:
          type: string
        port:
          type: integer
```

---

### MinIO Object Storage

**Service:** `minio`  
**Port:** `9000` (API), `9001` (Console)  
**Image:** `minio/minio:RELEASE.2024-01`

```yaml
openapi: 3.0.3
info:
  title: MinIO S3 API
  version: RELEASE.2024-01

paths:
  /{bucket}:
    put:
      summary: Create bucket
      parameters:
        - name: bucket
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Bucket created

  /{bucket}/{object}:
    put:
      summary: Upload object
      parameters:
        - name: bucket
          in: path
          required: true
          schema:
            type: string
        - name: object
          in: path
          required: true
          schema:
            type: string
      requestBody:
        content:
          application/octet-stream:
            schema:
              type: string
              format: binary
      responses:
        '200':
          description: Object uploaded
```

---

## Node.js Services (NestJS)

### User Service (Authentication & Authorization)

**Service:** `user-service`  
**Port:** `3025`  
**Kong Routes:** `/api/v1/auth/*`, `/api/v1/users/*`

```yaml
openapi: 3.0.3
info:
  title: SAHOOL User Service API
  description: Authentication, authorization, and user management
  version: 16.0.0
  contact:
    name: SAHOOL Platform
    email: support@sahool.io

servers:
  - url: http://localhost:8000
    description: Kong Gateway (Development)
  - url: https://api.sahool.io
    description: Production

tags:
  - name: Authentication
    description: Login, registration, password management
  - name: Users
    description: User profile management
  - name: Health
    description: Service health endpoints

paths:
  /api/v1/auth/register:
    post:
      tags: [Authentication]
      summary: Register new user
      description: Create a new farmer or agronomist account
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RegisterRequest'
            example:
              email: farmer@example.com
              password: SecurePass123!
              full_name: محمد أحمد
              phone: "+967771234567"
              role: farmer
              language: ar
      responses:
        '201':
          description: User registered successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RegisterResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '409':
          description: Email already exists

  /api/v1/auth/login:
    post:
      tags: [Authentication]
      summary: User login
      description: Authenticate user and return JWT token
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LoginRequest'
            example:
              email: farmer@example.com
              password: SecurePass123!
      responses:
        '200':
          description: Login successful
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LoginResponse'
        '401':
          description: Invalid credentials

  /api/v1/auth/refresh:
    post:
      tags: [Authentication]
      summary: Refresh access token
      description: Get new access token using refresh token
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                refresh_token:
                  type: string
              required: [refresh_token]
      responses:
        '200':
          description: Token refreshed
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/LoginResponse'

  /api/v1/auth/logout:
    post:
      tags: [Authentication]
      summary: Logout user
      description: Revoke current access token
      security:
        - BearerAuth: []
      responses:
        '200':
          description: Logout successful
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                    example: "Logged out successfully"

  /api/v1/auth/forgot-password:
    post:
      tags: [Authentication]
      summary: Request password reset
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                  format: email
              required: [email]
      responses:
        '200':
          description: Reset email sent

  /api/v1/auth/reset-password:
    post:
      tags: [Authentication]
      summary: Reset password with token
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                token:
                  type: string
                new_password:
                  type: string
                  minLength: 8
              required: [token, new_password]
      responses:
        '200':
          description: Password reset successful

  /api/v1/auth/send-otp:
    post:
      tags: [Authentication]
      summary: Send OTP for phone verification
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                phone:
                  type: string
                  pattern: '^\+967[0-9]{9}$'
              required: [phone]
      responses:
        '200':
          description: OTP sent

  /api/v1/auth/verify-otp:
    post:
      tags: [Authentication]
      summary: Verify OTP code
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                phone:
                  type: string
                otp:
                  type: string
                  pattern: '^[0-9]{6}$'
              required: [phone, otp]
      responses:
        '200':
          description: OTP verified

  /api/v1/auth/me:
    get:
      tags: [Users]
      summary: Get current user profile
      security:
        - BearerAuth: []
      responses:
        '200':
          description: User profile
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserProfile'

  /api/v1/users:
    get:
      tags: [Users]
      summary: List users (Admin only)
      security:
        - BearerAuth: []
      parameters:
        - $ref: '#/components/parameters/Page'
        - $ref: '#/components/parameters/Limit'
        - name: role
          in: query
          schema:
            type: string
            enum: [farmer, agronomist, admin, operator]
      responses:
        '200':
          description: List of users
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/UserProfile'
                  pagination:
                    $ref: '#/components/schemas/Pagination'

  /api/v1/users/{userId}:
    get:
      tags: [Users]
      summary: Get user by ID
      security:
        - BearerAuth: []
      parameters:
        - name: userId
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: User details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserProfile'
    
    patch:
      tags: [Users]
      summary: Update user profile
      security:
        - BearerAuth: []
      parameters:
        - name: userId
          in: path
          required: true
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserUpdateRequest'
      responses:
        '200':
          description: User updated

  /api/v1/healthz:
    get:
      tags: [Health]
      summary: Health check
      responses:
        '200':
          description: Service is healthy
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HealthResponse'

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    RegisterRequest:
      type: object
      required: [email, password, full_name, phone, role]
      properties:
        email:
          type: string
          format: email
        password:
          type: string
          minLength: 8
        full_name:
          type: string
        phone:
          type: string
          pattern: '^\+967[0-9]{9}$'
        role:
          type: string
          enum: [farmer, agronomist, admin, operator]
        language:
          type: string
          enum: [ar, en]
          default: ar

    RegisterResponse:
      type: object
      properties:
        user_id:
          type: string
        message:
          type: string

    LoginRequest:
      type: object
      required: [email, password]
      properties:
        email:
          type: string
        password:
          type: string

    LoginResponse:
      type: object
      properties:
        access_token:
          type: string
        refresh_token:
          type: string
        token_type:
          type: string
          enum: [Bearer]
        expires_in:
          type: integer
          description: Token expiration in seconds
        user:
          $ref: '#/components/schemas/UserProfile'

    UserProfile:
      type: object
      properties:
        id:
          type: string
        email:
          type: string
        full_name:
          type: string
        phone:
          type: string
        role:
          type: string
          enum: [farmer, agronomist, admin, operator]
        language:
          type: string
          enum: [ar, en]
        tenant_id:
          type: string
        created_at:
          type: string
          format: date-time
        last_login:
          type: string
          format: date-time

    UserUpdateRequest:
      type: object
      properties:
        full_name:
          type: string
        phone:
          type: string
        language:
          type: string
          enum: [ar, en]

    HealthResponse:
      type: object
      properties:
        status:
          type: string
          enum: [ok, degraded, error]
        service:
          type: string
        version:
          type: string
        timestamp:
          type: string
          format: date-time

    Pagination:
      type: object
      properties:
        page:
          type: integer
        limit:
          type: integer
        total:
          type: integer
        total_pages:
          type: integer

  parameters:
    Page:
      name: page
      in: query
      schema:
        type: integer
        default: 1
        minimum: 1

    Limit:
      name: limit
      in: query
      schema:
        type: integer
        default: 20
        minimum: 1
        maximum: 100

  responses:
    BadRequest:
      description: Invalid request
      content:
        application/json:
          schema:
            type: object
            properties:
              error:
                type: string
              message:
                type: string
```

**Rate Limiting:**
- Public auth endpoints: 30/min, 500/hour
- Protected endpoints: 100/min, 2000/hour

---

### Field Management Service

**Service:** `field-management-service`  
**Port:** `3000`  
**Kong Routes:** `/api/v1/fields/*`, `/api/v1/field/*`

```yaml
openapi: 3.0.3
info:
  title: SAHOOL Field Management API
  description: |
    خدمة إدارة الحقول - Field operations, boundaries, crops, rotations
    
    Features:
    - Field registration and boundary management (GeoJSON/WKT)
    - Crop rotation planning
    - Soil profile management
    - Field zoning for variable rate applications
  version: 16.0.0

servers:
  - url: http://localhost:8000
    description: Kong Gateway

tags:
  - name: Fields
  - name: Crops
  - name: Zones
  - name: Rotations

paths:
  /api/v1/fields:
    get:
      tags: [Fields]
      summary: List farmer's fields
      security:
        - BearerAuth: []
      parameters:
        - $ref: '#/components/parameters/Page'
        - $ref: '#/components/parameters/Limit'
        - name: crop_type
          in: query
          schema:
            type: string
        - name: status
          in: query
          schema:
            type: string
            enum: [active, fallow, harvested]
      responses:
        '200':
          description: List of fields
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/Field'
                  pagination:
                    $ref: '#/components/schemas/Pagination'

    post:
      tags: [Fields]
      summary: Register new field
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/FieldCreate'
            example:
              name: "حقل القمح الشمالي"
              name_en: "North Wheat Field"
              area_hectares: 5.2
              boundary:
                type: "Polygon"
                coordinates: [[[44.191, 15.369], [44.192, 15.369], [44.192, 15.370], [44.191, 15.370], [44.191, 15.369]]]
              crop_type: "wheat"
              irrigation_type: "pivot"
              soil_type: "clay_loam"
      responses:
        '201':
          description: Field created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Field'

  /api/v1/fields/{fieldId}:
    get:
      tags: [Fields]
      summary: Get field details
      security:
        - BearerAuth: []
      parameters:
        - name: fieldId
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Field details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Field'

    patch:
      tags: [Fields]
      summary: Update field
      security:
        - BearerAuth: []
      parameters:
        - name: fieldId
          in: path
          required: true
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/FieldUpdate'
      responses:
        '200':
          description: Field updated

    delete:
      tags: [Fields]
      summary: Delete field
      security:
        - BearerAuth: []
      parameters:
        - name: fieldId
          in: path
          required: true
          schema:
            type: string
      responses:
        '204':
          description: Field deleted

  /api/v1/fields/{fieldId}/zones:
    get:
      tags: [Zones]
      summary: List field zones
      security:
        - BearerAuth: []
      parameters:
        - name: fieldId
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Field zones
          content:
            application/json:
              schema:
                type: object
                properties:
                  zones:
                    type: array
                    items:
                      $ref: '#/components/schemas/Zone'

    post:
      tags: [Zones]
      summary: Create field zone
      security:
        - BearerAuth: []
      parameters:
        - name: fieldId
          in: path
          required: true
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ZoneCreate'
      responses:
        '201':
          description: Zone created

  /api/v1/fields/{fieldId}/crops:
    get:
      tags: [Crops]
      summary: Get crop history
      security:
        - BearerAuth: []
      parameters:
        - name: fieldId
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Crop history

    post:
      tags: [Crops]
      summary: Register new crop season
      security:
        - BearerAuth: []
      parameters:
        - name: fieldId
          in: path
          required: true
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CropSeasonCreate'
      responses:
        '201':
          description: Crop season registered

components:
  schemas:
    Field:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        name_en:
          type: string
        area_hectares:
          type: number
        boundary:
          $ref: '#/components/schemas/GeoJSONPolygon'
        crop_type:
          type: string
        irrigation_type:
          type: string
          enum: [drip, sprinkler, pivot, flood, rain_fed]
        soil_type:
          type: string
        status:
          type: string
          enum: [active, fallow, harvested]
        tenant_id:
          type: string
        created_at:
          type: string
          format: date-time

    FieldCreate:
      type: object
      required: [name, area_hectares, boundary, crop_type]
      properties:
        name:
          type: string
        name_en:
          type: string
        area_hectares:
          type: number
          minimum: 0.01
        boundary:
          $ref: '#/components/schemas/GeoJSONPolygon'
        crop_type:
          type: string
        irrigation_type:
          type: string
        soil_type:
          type: string

    FieldUpdate:
      type: object
      properties:
        name:
          type: string
        name_en:
          type: string
        status:
          type: string
        crop_type:
          type: string

    Zone:
      type: object
      properties:
        id:
          type: string
        field_id:
          type: string
        name:
          type: string
        boundary:
          $ref: '#/components/schemas/GeoJSONPolygon'
        area_hectares:
          type: number
        zone_type:
          type: string
          enum: [management, irrigation, fertility]

    ZoneCreate:
      type: object
      required: [name, boundary]
      properties:
        name:
          type: string
        boundary:
          $ref: '#/components/schemas/GeoJSONPolygon'
        zone_type:
          type: string

    CropSeasonCreate:
      type: object
      required: [crop_type, variety, planting_date]
      properties:
        crop_type:
          type: string
        variety:
          type: string
        planting_date:
          type: string
          format: date
        expected_harvest_date:
          type: string
          format: date
        target_yield:
          type: number

    GeoJSONPolygon:
      type: object
      properties:
        type:
          type: string
          enum: [Polygon]
        coordinates:
          type: array
          items:
            type: array
            items:
              type: array
              items:
                type: number
              minItems: 2
              maxItems: 3

    Pagination:
      $ref: '#/components/schemas/Pagination'
```

---

### Marketplace Service

**Service:** `marketplace-service`  
**Port:** `3010`  
**Kong Routes:** `/api/v1/marketplace/*`

```yaml
openapi: 3.0.3
info:
  title: SAHOOL Marketplace API
  description: |
    سوق سهول الزراعي - Agricultural marketplace for seeds, fertilizers, equipment
  version: 16.0.0

paths:
  /api/v1/marketplace/products:
    get:
      summary: List marketplace products
      security:
        - BearerAuth: []
      parameters:
        - name: category
          in: query
          schema:
            type: string
            enum: [seeds, fertilizers, pesticides, equipment, services]
        - name: search
          in: query
          schema:
            type: string
        - $ref: '#/components/parameters/Page'
      responses:
        '200':
          description: Product list
          content:
            application/json:
              schema:
                type: object
                properties:
                  products:
                    type: array
                    items:
                      $ref: '#/components/schemas/Product'

  /api/v1/marketplace/orders:
    post:
      summary: Create order
      security:
        - BearerAuth: []
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/OrderCreate'
      responses:
        '201':
          description: Order created

components:
  schemas:
    Product:
      type: object
      properties:
        id:
          type: string
        name:
          type: string
        name_ar:
          type: string
        category:
          type: string
        price:
          type: number
        unit:
          type: string
        vendor_id:
          type: string

    OrderCreate:
      type: object
      required: [items]
      properties:
        items:
          type: array
          items:
            type: object
            properties:
              product_id:
                type: string
              quantity:
                type: number
```

**Rate Limiting:** 60/min, 1000/hour

---

### IoT Service

**Service:** `iot-service`  
**Port:** `8117`  
**Kong Routes:** `/api/v1/iot/*`

```yaml
openapi: 3.0.3
info:
  title: SAHOOL IoT Service API
  description: IoT sensors and actuators management
  version: 16.0.0

paths:
  /api/v1/iot/fields/{fieldId}/sensors:
    get:
      summary: List field sensors
      security:
        - BearerAuth: []
      parameters:
        - name: fieldId
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Sensor list
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Sensor'

  /api/v1/iot/sensors/{sensorId}/readings:
    get:
      summary: Get sensor readings
      security:
        - BearerAuth: []
      parameters:
        - name: sensorId
          in: path
          required: true
          schema:
            type: string
        - name: start_date
          in: query
          schema:
            type: string
            format: date-time
        - name: end_date
          in: query
          schema:
            type: string
            format: date-time
        - name: interval
          in: query
          schema:
            type: string
            enum: [1m, 5m, 15m, 1h, 1d]
            default: 1h
      responses:
        '200':
          description: Sensor readings
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/SensorReading'

  /api/v1/iot/actuators/{actuatorId}/control:
    post:
      summary: Control actuator (pump, valve, etc.)
      security:
        - BearerAuth: []
      parameters:
        - name: actuatorId
          in: path
          required: true
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required: [action]
              properties:
                action:
                  type: string
                  enum: [on, off]
                duration_minutes:
                  type: integer
                reason:
                  type: string
      responses:
        '200':
          description: Command sent

components:
  schemas:
    Sensor:
      type: object
      properties:
        id:
          type: string
        field_id:
          type: string
        name:
          type: string
        type:
          type: string
          enum: [soil_moisture, temperature, humidity, ph, ec, light]
        status:
          type: string
          enum: [online, offline]
        latitude:
          type: number
        longitude:
          type: number
        last_reading:
          type: string
          format: date-time

    SensorReading:
      type: object
      properties:
        sensor_id:
          type: string
        value:
          type: number
        unit:
          type: string
        timestamp:
          type: string
          format: date-time
        quality:
          type: string
          enum: [good, fair, poor]
```

---

## Python Services (FastAPI)

### Advisory Service

**Service:** `advisory-service`  
**Port:** `8093`  
**Kong Routes:** `/api/v1/advisory/*`, `/api/v1/fertilizer/*`

```yaml
openapi: 3.0.3
info:
  title: SAHOOL Advisory Service API
  description: |
    خدمة الاستشارات الزراعية - Agricultural advisory and fertilizer recommendations
  version: 16.0.0

paths:
  /api/v1/advisory/{field_id}:
    get:
      summary: Get field advisory recommendations
      security:
        - BearerAuth: []
      parameters:
        - name: field_id
          in: path
          required: true
          schema:
            type: string
        - name: date
          in: query
          schema:
            type: string
            format: date
      responses:
        '200':
          description: Advisory recommendations
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/AdvisoryResponse'
              example:
                field_id: "field_001"
                date: "2026-02-11"
                recommendations:
                  - type: "fertilizer"
                    priority: "high"
                    title: "تسميد نيتروجيني عاجل"
                    title_en: "Urgent nitrogen fertilization"
                    description: "نقص النيتروجين واضح من اصفرار الأوراق"
                    action:
                      product: "Urea 46%"
                      rate_kg_per_ha: 46
                      application_method: "broadcast"
                      timing: "early_morning"
                    expected_benefit:
                      yield_improvement_pct: 15
                      cost_sar: 850
                      roi_pct: 1025

  /api/v1/fertilizer/recommendation:
    post:
      summary: Get fertilizer recommendation
      security:
        - BearerAuth: []
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/FertilizerRequest'
            example:
              field_id: "field_001"
              crop_type: "wheat"
              crop_stage: "tillering"
              soil_test:
                nitrogen_ppm: 18
                phosphorus_ppm: 25
                potassium_ppm: 150
                ph: 7.2
              target_yield_ton_per_ha: 5.0
      responses:
        '200':
          description: Fertilizer recommendation
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/FertilizerRecommendation'

components:
  schemas:
    AdvisoryResponse:
      type: object
      properties:
        field_id:
          type: string
        date:
          type: string
          format: date
        recommendations:
          type: array
          items:
            $ref: '#/components/schemas/Recommendation'

    Recommendation:
      type: object
      properties:
        type:
          type: string
          enum: [irrigation, fertilizer, pest_control, disease_management]
        priority:
          type: string
          enum: [critical, high, medium, low]
        title:
          type: string
        title_en:
          type: string
        description:
          type: string
        action:
          type: object
        expected_benefit:
          type: object

    FertilizerRequest:
      type: object
      required: [field_id, crop_type, crop_stage, soil_test]
      properties:
        field_id:
          type: string
        crop_type:
          type: string
        crop_stage:
          type: string
        soil_test:
          type: object
          properties:
            nitrogen_ppm:
              type: number
            phosphorus_ppm:
              type: number
            potassium_ppm:
              type: number
            ph:
              type: number
        target_yield_ton_per_ha:
          type: number

    FertilizerRecommendation:
      type: object
      properties:
        product:
          type: string
        rate_kg_per_ha:
          type: number
        application_method:
          type: string
        timing:
          type: string
        cost_estimate_sar:
          type: number
```

---

### Irrigation Smart Service

**Service:** `irrigation-smart`  
**Port:** `8094`  
**Kong Routes:** `/api/v1/irrigation/*`

```yaml
openapi: 3.0.3
info:
  title: SAHOOL Irrigation Smart API
  description: Smart irrigation scheduling and management
  version: 16.0.0

paths:
  /api/v1/irrigation/{field_id}/schedule:
    get:
      summary: Get irrigation schedule
      security:
        - BearerAuth: []
      parameters:
        - name: field_id
          in: path
          required: true
          schema:
            type: string
        - name: days
          in: query
          schema:
            type: integer
            default: 7
      responses:
        '200':
          description: Irrigation schedule
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/IrrigationSchedule'

    post:
      summary: Create/update irrigation schedule
      security:
        - BearerAuth: []
      parameters:
        - name: field_id
          in: path
          required: true
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/IrrigationRequest'
      responses:
        '200':
          description: Schedule created

  /api/v1/irrigation/{field_id}/recommendation:
    get:
      summary: Get irrigation recommendation
      security:
        - BearerAuth: []
      parameters:
        - name: field_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Irrigation recommendation
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/IrrigationRecommendation'
              example:
                field_id: "field_001"
                recommendation:
                  action: "irrigate"
                  amount_mm: 25
                  timing: "within_24_hours"
                  reason: "رطوبة التربة منخفضة (35%) + لا أمطار متوقعة"
                  reason_en: "Low soil moisture (35%) + no rain forecast"
                factors:
                  soil_moisture_pct: 35
                  et_mm_per_day: 5.5
                  rain_forecast_mm: 0
                  crop_stage: "tillering"

components:
  schemas:
    IrrigationSchedule:
      type: object
      properties:
        field_id:
          type: string
        events:
          type: array
          items:
            type: object
            properties:
              date:
                type: string
                format: date-time
              amount_mm:
                type: number
              duration_minutes:
                type: integer
              status:
                type: string
                enum: [scheduled, completed, skipped]

    IrrigationRequest:
      type: object
      properties:
        start_date:
          type: string
          format: date
        irrigation_type:
          type: string
        frequency_days:
          type: integer
        amount_mm:
          type: number

    IrrigationRecommendation:
      type: object
      properties:
        field_id:
          type: string
        recommendation:
          type: object
        factors:
          type: object
```

---

### Crop Intelligence Service

**Service:** `crop-intelligence-service`  
**Port:** `8095`  
**Kong Routes:** `/api/v1/crop-health/*`, `/api/v1/crop/*`

```yaml
openapi: 3.0.3
info:
  title: SAHOOL Crop Intelligence API
  description: |
    Crop health diagnostics with AI-powered recommendations
    Includes OpenAPI spec from existing file
  version: 16.0.0

# Reference the existing detailed OpenAPI spec
# (Content from apps/services/crop-intelligence-service/openapi.yaml)
# See full specification in the service directory
```

---

### Weather Service

**Service:** `weather-service`  
**Port:** `8092`  
**Kong Routes:** `/api/v1/weather/*`

```yaml
openapi: 3.0.3
info:
  title: SAHOOL Weather Service API
  description: Weather data aggregation and forecasting
  version: 16.0.0

paths:
  /api/v1/weather/current:
    get:
      summary: Get current weather
      parameters:
        - name: latitude
          in: query
          required: true
          schema:
            type: number
        - name: longitude
          in: query
          required: true
          schema:
            type: number
      responses:
        '200':
          description: Current weather data
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/CurrentWeather'

  /api/v1/weather/forecast:
    get:
      summary: Get weather forecast
      parameters:
        - name: latitude
          in: query
          required: true
          schema:
            type: number
        - name: longitude
          in: query
          required: true
          schema:
            type: number
        - name: days
          in: query
          schema:
            type: integer
            default: 7
            maximum: 14
      responses:
        '200':
          description: Weather forecast
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/WeatherForecast'

  /api/v1/weather/field/{field_id}:
    get:
      summary: Get weather for specific field
      security:
        - BearerAuth: []
      parameters:
        - name: field_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Field weather

components:
  schemas:
    CurrentWeather:
      type: object
      properties:
        temperature_c:
          type: number
        humidity_pct:
          type: number
        wind_speed_kmh:
          type: number
        wind_direction:
          type: string
        precipitation_mm:
          type: number
        pressure_mb:
          type: number
        timestamp:
          type: string
          format: date-time

    WeatherForecast:
      type: object
      properties:
        location:
          type: object
        forecast:
          type: array
          items:
            type: object
            properties:
              date:
                type: string
                format: date
              temp_max_c:
                type: number
              temp_min_c:
                type: number
              precipitation_mm:
                type: number
              precipitation_probability_pct:
                type: number
```

**Caching:** 15 minutes (Kong proxy-cache plugin)

---

### Vegetation Analysis Service

**Service:** `vegetation-analysis-service`  
**Port:** `8090`  
**Kong Routes:** `/api/v1/vegetation/*`, `/api/v1/satellite/*`, `/api/v1/ndvi/*`

```yaml
openapi: 3.0.3
info:
  title: SAHOOL Vegetation Analysis API
  description: |
    تحليل الأقمار الصناعية - Satellite imagery and NDVI analysis
  version: 16.0.0

paths:
  /api/v1/vegetation/{field_id}/ndvi:
    get:
      summary: Get NDVI analysis for field
      security:
        - BearerAuth: []
      parameters:
        - name: field_id
          in: path
          required: true
          schema:
            type: string
        - name: date
          in: query
          required: true
          schema:
            type: string
            format: date
        - name: source
          in: query
          schema:
            type: string
            enum: [sentinel-2, landsat-8, planet]
            default: sentinel-2
      responses:
        '200':
          description: NDVI analysis
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/NDVIAnalysis'

  /api/v1/vegetation/{field_id}/timeseries:
    get:
      summary: Get NDVI time series
      security:
        - BearerAuth: []
      parameters:
        - name: field_id
          in: path
          required: true
          schema:
            type: string
        - name: start_date
          in: query
          required: true
          schema:
            type: string
            format: date
        - name: end_date
          in: query
          required: true
          schema:
            type: string
            format: date
      responses:
        '200':
          description: NDVI time series

components:
  schemas:
    NDVIAnalysis:
      type: object
      properties:
        field_id:
          type: string
        date:
          type: string
          format: date
        source:
          type: string
        ndvi_mean:
          type: number
          minimum: -1
          maximum: 1
        ndvi_min:
          type: number
        ndvi_max:
          type: number
        ndvi_std:
          type: number
        health_status:
          type: string
          enum: [excellent, good, moderate, poor, critical]
        cloud_coverage_pct:
          type: number
        raster_url:
          type: string
          description: URL to NDVI raster image
```

**Caching:** 30 minutes

---

## AI/ML Services

### YOLO26 Vision Service

**Service:** `yolo26-vision-service`  
**Port:** `8150`  
**Kong Routes:** `/api/v1/vision/*`

```yaml
openapi: 3.0.3
info:
  title: SAHOOL YOLO26 Vision Service API
  description: |
    Computer vision for pest/disease/weed detection using YOLOv26
  version: 16.0.0

paths:
  /api/v1/vision/detect:
    post:
      summary: Detect pests, diseases, or weeds in image
      security:
        - BearerAuth: []
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              required: [image, detection_type]
              properties:
                image:
                  type: string
                  format: binary
                detection_type:
                  type: string
                  enum: [pest, disease, weed]
                crop_type:
                  type: string
                confidence_threshold:
                  type: number
                  default: 0.5
      responses:
        '200':
          description: Detection results
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DetectionResult'

  /api/v1/vision/batch:
    post:
      summary: Batch image processing
      security:
        - BearerAuth: []
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                images:
                  type: array
                  items:
                    type: string
                    format: binary
      responses:
        '200':
          description: Batch results

components:
  schemas:
    DetectionResult:
      type: object
      properties:
        image_id:
          type: string
        detections:
          type: array
          items:
            type: object
            properties:
              class:
                type: string
              confidence:
                type: number
              bounding_box:
                type: object
                properties:
                  x:
                    type: integer
                  y:
                    type: integer
                  width:
                    type: integer
                  height:
                    type: integer
              severity:
                type: string
                enum: [low, medium, high, critical]
        processing_time_ms:
          type: number
```

---

### LLM Orchestrator Service

**Service:** `llm-orchestrator-service`  
**Port:** `8127`  
**Kong Routes:** `/api/v1/llm/*`

```yaml
openapi: 3.0.3
info:
  title: SAHOOL LLM Orchestrator API
  description: |
    LLM orchestration for agricultural advisory using local Ollama models
  version: 16.0.0

paths:
  /api/v1/llm/chat:
    post:
      summary: Chat with agricultural LLM assistant
      security:
        - BearerAuth: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              required: [message]
              properties:
                message:
                  type: string
                  description: User message in Arabic or English
                context:
                  type: object
                  description: Optional context (field_id, crop_type, etc.)
                model:
                  type: string
                  enum: [llama3.1, mistral, codellama]
                  default: llama3.1
      responses:
        '200':
          description: LLM response
          content:
            application/json:
              schema:
                type: object
                properties:
                  response:
                    type: string
                  model:
                    type: string
                  tokens_used:
                    type: integer

  /api/v1/llm/advisory:
    post:
      summary: Generate agricultural advisory
      security:
        - BearerAuth: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                field_id:
                  type: string
                question:
                  type: string
      responses:
        '200':
          description: Generated advisory
```

---

### Terrain Core Service

**Service:** `terrain-core-service`  
**Port:** `8106`  
**Kong Routes:** `/api/v1/terrain/*`

```yaml
openapi: 3.0.3
info:
  title: SAHOOL Terrain Core API
  description: DEM processing and terrain analysis
  version: 16.0.0

paths:
  /api/v1/terrain/{field_id}/slope:
    get:
      summary: Get slope analysis
      security:
        - BearerAuth: []
      parameters:
        - name: field_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Slope analysis

  /api/v1/terrain/{field_id}/aspect:
    get:
      summary: Get aspect analysis
      security:
        - BearerAuth: []
      parameters:
        - name: field_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Aspect analysis
```

---

### Hydrology Service

**Service:** `hydrology-service`  
**Port:** `8170`  
**Kong Routes:** `/api/v1/hydrology/*`

```yaml
openapi: 3.0.3
info:
  title: SAHOOL Hydrology Service API
  description: Water management and drainage analysis
  version: 16.0.0

paths:
  /api/v1/hydrology/{field_id}/drainage:
    get:
      summary: Get drainage analysis
      security:
        - BearerAuth: []
      parameters:
        - name: field_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Drainage analysis
```

---

### Edge Orchestrator Service

**Service:** `edge-orchestrator-service`  
**Port:** `8150`  
**Kong Routes:** `/api/v1/edge/*`

```yaml
openapi: 3.0.3
info:
  title: SAHOOL Edge Orchestrator API
  description: Edge device management (Jetson Orin)
  version: 16.0.0

paths:
  /api/v1/edge/devices:
    get:
      summary: List edge devices
      security:
        - BearerAuth: []
      responses:
        '200':
          description: Edge device list

  /api/v1/edge/deploy:
    post:
      summary: Deploy model to edge device
      security:
        - BearerAuth: []
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                device_id:
                  type: string
                model_id:
                  type: string
      responses:
        '200':
          description: Deployment initiated
```

---

## Common Patterns

### Standard Response Format

All services follow this response format:

```json
{
  "data": { },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2026-02-11T19:51:45Z",
    "version": "16.0.0"
  }
}
```

### Pagination

```json
{
  "data": [],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

### GeoJSON Format

All geospatial data uses GeoJSON RFC 7946:

```json
{
  "type": "Feature",
  "geometry": {
    "type": "Polygon",
    "coordinates": [[[44.191, 15.369], [44.192, 15.369]]]
  },
  "properties": {
    "field_id": "field_001",
    "name": "حقل القمح"
  }
}
```

---

## Error Handling

### Standard Error Response

```json
{
  "error": {
    "code": "FIELD_NOT_FOUND",
    "message": "Field with ID 'field_001' not found",
    "message_ar": "لم يتم العثور على الحقل",
    "request_id": "uuid",
    "timestamp": "2026-02-11T19:51:45Z"
  }
}
```

### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful request |
| 201 | Created | Resource created |
| 204 | No Content | Successful deletion |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Duplicate resource |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service down |

### Error Codes

| Code | Description |
|------|-------------|
| `INVALID_TOKEN` | JWT token invalid or expired |
| `FIELD_NOT_FOUND` | Field does not exist |
| `UNAUTHORIZED_ACCESS` | User cannot access resource |
| `VALIDATION_ERROR` | Input validation failed |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `SERVICE_UNAVAILABLE` | Backend service down |

---

## Rate Limiting

### Rate Limit Headers

```http
X-RateLimit-Limit-Minute: 100
X-RateLimit-Remaining-Minute: 95
X-RateLimit-Reset: 1707674460
```

### Service-Specific Limits

| Service | Rate Limit (per minute) | Rate Limit (per hour) |
|---------|-------------------------|----------------------|
| **user-service** (public auth) | 30 | 500 |
| **user-service** (protected) | 100 | 2000 |
| **marketplace-service** | 60 | 1000 |
| **billing-core** | 20 | 200 |
| **Default** | 100 | 2000 |

### Rate Limit Exceeded Response

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 45 seconds.",
    "retry_after": 45
  }
}
```

---

## Health Check Endpoints

All services implement standard health endpoints:

### Liveness Probe

```http
GET /healthz
GET /health/live

Response:
{
  "status": "ok",
  "service": "advisory-service",
  "version": "16.0.0"
}
```

### Readiness Probe

```http
GET /readyz
GET /health/ready

Response:
{
  "status": "ok",
  "checks": {
    "database": "connected",
    "nats": "connected",
    "redis": "connected"
  }
}
```

### Metrics (Prometheus)

```http
GET /metrics

Response (Prometheus format):
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/api/v1/fields",status="200"} 1523
```

---

## Appendix: Service Registry

### Complete Service List (80+ Services)

#### Infrastructure (13)
- postgres, pgbouncer, redis, nats, vault, mqtt, etcd, kong, minio, qdrant, milvus, ollama, mlflow

#### Node.js/NestJS (23)
- field-management-service, user-service, marketplace-service, community-chat, chat-service, field-chat, ws-gateway, billing-core, equipment-service, task-service, provider-config, crm-service, inventory-service, wechat-service, agent-registry, llm-orchestrator-service, ai-agents-service, ai-agents-core, knowledge-graph, ai-advisor, code-review-service, code-fix-agent, copilot-api

#### Python/FastAPI (45+)
- advisory-service, irrigation-smart, crop-intelligence-service, yield-prediction-service, yield-engine, vegetation-analysis-service, ndvi-engine, ndvi-processor, ground-vision-service, terrain-core-service, weather-service, weather-core, soil-analysis-service, pest-detection-service, field-intelligence, indicators-service, yolo26-vision-service, lai-estimation, crop-growth-model, disaster-assessment, research-core, virtual-sensors, agro-advisor, agro-rules, alert-service, notification-service, astronomical-calendar, iot-service, iot-gateway, iot-sensor-hub, audit-service, traceability-service, globalgap-compliance, supply-chain-service, logistics-service, cooperative-service, drone-service, hydrology-service, leveling-optimizer-service, lowcode-engine, mcp-server, skills-service, edge-orchestrator-service, irrigation-cycle-engine, fertigation-engine, digital-twin-engine

---

## Document Metadata

- **Generated:** 2026-02-11
- **Generator:** Claude Code (Anthropic)
- **Source:** docker-compose.yml + infrastructure/gateway/kong/kong.yml
- **Purpose:** Enable dynamic admin web app development
- **Maintainer:** KAFAAT DevOps Team

---

**End of OpenAPI Schema Documentation**
