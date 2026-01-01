# SAHOOL User Service
# خدمة إدارة المستخدمين

Version: 16.0.0

## Overview

The User Service is a critical NestJS-based microservice that provides centralized user management for the SAHOOL platform. It handles user registration, authentication, authorization, profile management, and session tracking.

## Features

- **User Management**: Complete CRUD operations for user accounts
- **Multi-tenant Support**: Isolated user data per tenant
- **Authentication**: Secure password hashing with bcryptjs
- **Role-Based Access Control (RBAC)**: Five user roles (ADMIN, MANAGER, FARMER, WORKER, VIEWER)
- **User Status Management**: ACTIVE, INACTIVE, SUSPENDED, PENDING
- **Profile Management**: Extended user profile information
- **Session Management**: Track user sessions and login history
- **Email & Phone Verification**: Verification status tracking
- **Refresh Tokens**: Secure token refresh mechanism
- **API Documentation**: Auto-generated Swagger/OpenAPI docs

## Technology Stack

- **Framework**: NestJS 10.4.15
- **Database**: PostgreSQL with Prisma ORM 5.22.0
- **Validation**: class-validator, class-transformer
- **Security**: bcryptjs for password hashing
- **Documentation**: Swagger/OpenAPI
- **Rate Limiting**: @nestjs/throttler

## Prerequisites

- Node.js >= 20.0.0
- PostgreSQL database
- npm or yarn

## Installation

```bash
# Install dependencies
npm install

# Generate Prisma client
npm run prisma:generate

# Run database migrations
npm run prisma:migrate
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Key variables:
- `PORT`: Service port (default: 3020)
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET`: Secret key for JWT tokens
- `CORS_ALLOWED_ORIGINS`: Allowed CORS origins

## Running the Service

```bash
# Development mode
npm run start:dev

# Production mode
npm run build
npm run start:prod

# Docker
docker build -t sahool-user-service .
docker run -p 3020:3020 sahool-user-service
```

## API Documentation

Once running, access the Swagger documentation at:
- Local: http://localhost:3020/docs
- Health Check: http://localhost:3020/api/v1/health

## Database Schema

### User Model
- id, tenantId, email (unique), phone, passwordHash
- firstName, lastName, role, status
- emailVerified, phoneVerified, lastLoginAt
- timestamps (createdAt, updatedAt)

### UserProfile Model
- id, userId (unique), nationalId
- dateOfBirth, address, city, region, country
- avatarUrl, timestamps

### UserRole Model
- id, name (unique), permissions (JSON), isSystem
- timestamps

### UserSession Model
- id, userId, token, ipAddress, userAgent
- expiresAt, timestamps

### RefreshToken Model
- id, userId, token, expiresAt, revoked
- createdAt

## API Endpoints

### Users
- `POST /api/v1/users` - Create a new user
- `GET /api/v1/users` - Get all users (with filters)
- `GET /api/v1/users/:id` - Get user by ID
- `GET /api/v1/users/email/:email` - Get user by email
- `PUT /api/v1/users/:id` - Update user
- `DELETE /api/v1/users/:id` - Soft delete user
- `DELETE /api/v1/users/:id/hard` - Hard delete user

### Statistics
- `GET /api/v1/users/stats/count/:tenantId` - Get user count by tenant
- `GET /api/v1/users/stats/active` - Get active users count

## User Roles

- **ADMIN**: Full system access
- **MANAGER**: Manage users and operations
- **FARMER**: Farm owner access
- **WORKER**: Farm worker access
- **VIEWER**: Read-only access

## User Status

- **ACTIVE**: User is active and can access the system
- **INACTIVE**: User is deactivated
- **SUSPENDED**: User is temporarily suspended
- **PENDING**: User registration pending approval

## Testing

```bash
# Run tests
npm run test

# Run tests with coverage
npm run test:cov

# Watch mode
npm run test:watch
```

## Security Features

- Password hashing with bcryptjs (10 rounds)
- Rate limiting (10 req/s, 100 req/min, 1000 req/hour)
- Input validation with class-validator
- CORS protection
- SQL injection protection via Prisma

## Development

```bash
# Format code
npm run format

# Lint code
npm run lint

# Generate Prisma client
npm run prisma:generate

# Push schema changes to DB (dev)
npm run prisma:push

# Create migration
npm run prisma:migrate
```

## License

MIT - SAHOOL Team

## Support

For issues and questions, contact the SAHOOL development team.
