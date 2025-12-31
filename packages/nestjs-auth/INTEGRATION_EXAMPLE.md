# Integration Example: Marketplace Service

This is a complete, working example of integrating `@sahool/nestjs-auth` into the marketplace-service.

## File Structure After Integration

```
apps/services/marketplace-service/
├── src/
│   ├── app.module.ts          # Updated to use AuthModule
│   ├── app.controller.ts      # Updated to use decorators
│   ├── main.ts
│   ├── market/
│   │   ├── market.controller.ts  # Protected routes
│   │   └── market.service.ts
│   ├── fintech/
│   │   ├── fintech.controller.ts
│   │   └── fintech.service.ts
│   ├── prisma/
│   │   └── prisma.service.ts
│   └── users/                 # New: User repository
│       └── user.repository.ts
├── .env                       # Environment variables
└── package.json
```

## Complete Implementation

### 1. Environment Variables (.env)

```bash
# JWT Configuration
JWT_SECRET_KEY=sahool-marketplace-secret-key-min-32-characters-long
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
JWT_ISSUER=sahool-marketplace
JWT_AUDIENCE=sahool-api

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Features
TOKEN_REVOCATION_ENABLED=true
```

### 2. App Module (src/app.module.ts)

```typescript
/**
 * SAHOOL Marketplace App Module
 * وحدة التطبيق الرئيسية
 */

import { Module } from '@nestjs/common';
import { RedisModule } from '@liaoliaots/nestjs-redis';
import { AuthModule } from '@sahool/nestjs-auth';

import { AppController } from './app.controller';
import { PrismaService } from './prisma/prisma.service';
import { MarketService } from './market/market.service';
import { FintechService } from './fintech/fintech.service';
import { UserRepository } from './users/user.repository';

@Module({
  imports: [
    // Redis for caching and token revocation
    RedisModule.forRoot({
      config: {
        host: process.env.REDIS_HOST || 'localhost',
        port: parseInt(process.env.REDIS_PORT || '6379', 10),
        password: process.env.REDIS_PASSWORD,
        db: parseInt(process.env.REDIS_DB || '0', 10),
      },
    }),

    // Shared Authentication Module
    AuthModule.forRoot({
      enableUserValidation: true,
      enableTokenRevocation: true,
      userRepository: new UserRepository(new PrismaService()),
    }),
  ],
  controllers: [AppController],
  providers: [
    PrismaService,
    MarketService,
    FintechService,
    UserRepository,
  ],
})
export class AppModule {}
```

### 3. User Repository (src/users/user.repository.ts)

```typescript
/**
 * User Repository for Authentication
 * مستودع المستخدمين للمصادقة
 */

import { Injectable } from '@nestjs/common';
import { IUserRepository, UserValidationData } from '@sahool/nestjs-auth';
import { PrismaService } from '../prisma/prisma.service';

@Injectable()
export class UserRepository implements IUserRepository {
  constructor(private readonly prisma: PrismaService) {}

  /**
   * Get user validation data from database
   */
  async getUserValidationData(userId: string): Promise<UserValidationData | null> {
    try {
      // Adjust based on your actual Prisma schema
      const user = await this.prisma.user.findUnique({
        where: { id: userId },
        select: {
          id: true,
          email: true,
          isActive: true,
          isVerified: true,
          roles: true,
          tenantId: true,
          // Add these fields if they exist in your schema
          isDeleted: true,
          isSuspended: true,
        },
      });

      if (!user) {
        return null;
      }

      return {
        userId: user.id,
        email: user.email,
        isActive: user.isActive ?? true,
        isVerified: user.isVerified ?? true,
        roles: user.roles || [],
        tenantId: user.tenantId,
        isDeleted: user.isDeleted ?? false,
        isSuspended: user.isSuspended ?? false,
      };
    } catch (error) {
      console.error('Error fetching user validation data:', error);
      return null;
    }
  }

  /**
   * Update user's last login timestamp
   */
  async updateLastLogin(userId: string): Promise<void> {
    try {
      await this.prisma.user.update({
        where: { id: userId },
        data: { lastLoginAt: new Date() },
      });
    } catch (error) {
      console.error('Error updating last login:', error);
    }
  }
}
```

### 4. App Controller (src/app.controller.ts)

```typescript
/**
 * SAHOOL Marketplace App Controller
 * المتحكم الرئيسي
 */

import { Controller, Get, Post, Body, UseGuards, HttpCode } from '@nestjs/common';
import {
  JwtAuthGuard,
  RolesGuard,
  OptionalAuthGuard,
  Public,
  Roles,
  CurrentUser,
  UserId,
  UserRoles,
} from '@sahool/nestjs-auth';

import { MarketService } from './market/market.service';
import { FintechService } from './fintech/fintech.service';

@Controller()
export class AppController {
  constructor(
    private readonly marketService: MarketService,
    private readonly fintechService: FintechService,
  ) {}

  /**
   * Public health check endpoint
   */
  @Public()
  @Get('health')
  health() {
    return {
      status: 'ok',
      service: 'marketplace-service',
      timestamp: new Date().toISOString(),
    };
  }

  /**
   * Get marketplace listings (optional auth)
   * Returns more data if authenticated
   */
  @UseGuards(OptionalAuthGuard)
  @Get('marketplace')
  async getMarketplace(@CurrentUser() user?: any) {
    if (user) {
      return this.marketService.getPersonalizedListings(user.id);
    }
    return this.marketService.getPublicListings();
  }

  /**
   * Get user's marketplace activity (protected)
   */
  @UseGuards(JwtAuthGuard)
  @Get('marketplace/my-activity')
  async getMyActivity(@UserId() userId: string) {
    return this.marketService.getUserActivity(userId);
  }

  /**
   * Create marketplace listing (protected, farmers only)
   */
  @UseGuards(JwtAuthGuard, RolesGuard)
  @Roles('farmer', 'agricultural_business')
  @Post('marketplace/listings')
  @HttpCode(201)
  async createListing(
    @Body() listingData: any,
    @UserId() userId: string,
    @UserRoles() roles: string[],
  ) {
    return this.marketService.createListing({
      ...listingData,
      sellerId: userId,
      sellerType: roles[0],
    });
  }

  /**
   * Get credit score (protected)
   */
  @UseGuards(JwtAuthGuard)
  @Get('fintech/credit-score')
  async getCreditScore(@UserId() userId: string) {
    return this.fintechService.getCreditScore(userId);
  }

  /**
   * Admin: Get all credit scores (protected, admins only)
   */
  @UseGuards(JwtAuthGuard, RolesGuard)
  @Roles('admin', 'financial_manager')
  @Get('fintech/admin/credit-scores')
  async getAllCreditScores(@CurrentUser() user: any) {
    return {
      message: 'Admin access granted',
      user: {
        id: user.id,
        roles: user.roles,
      },
      data: await this.fintechService.getAllCreditScores(),
    };
  }

  /**
   * Process payment (protected)
   */
  @UseGuards(JwtAuthGuard)
  @Post('fintech/payments')
  async processPayment(
    @Body() paymentData: any,
    @UserId() userId: string,
  ) {
    return this.fintechService.processPayment({
      ...paymentData,
      userId,
    });
  }
}
```

### 5. Market Service (src/market/market.service.ts)

```typescript
/**
 * Market Service
 * خدمة السوق
 */

import { Injectable, ForbiddenException } from '@nestjs/common';
import { hasRole } from '@sahool/nestjs-auth';

@Injectable()
export class MarketService {
  async getPublicListings() {
    return {
      listings: [
        { id: '1', title: 'Fresh Tomatoes', price: 100 },
        { id: '2', title: 'Organic Wheat', price: 200 },
      ],
      count: 2,
      isAuthenticated: false,
    };
  }

  async getPersonalizedListings(userId: string) {
    return {
      listings: [
        { id: '1', title: 'Fresh Tomatoes', price: 100, recommended: true },
        { id: '2', title: 'Organic Wheat', price: 200 },
        { id: '3', title: 'Farm Equipment', price: 5000, featured: true },
      ],
      count: 3,
      isAuthenticated: true,
      userId,
    };
  }

  async getUserActivity(userId: string) {
    return {
      userId,
      purchases: [],
      sales: [],
      bids: [],
    };
  }

  async createListing(data: any) {
    return {
      id: 'listing-123',
      ...data,
      createdAt: new Date().toISOString(),
    };
  }

  async deleteListing(listingId: string, user: any) {
    // Business logic: Only admins or listing owners can delete
    const listing = await this.findOne(listingId);

    if (!hasRole(user, 'admin') && listing.sellerId !== user.id) {
      throw new ForbiddenException(
        'You can only delete your own listings'
      );
    }

    // Delete logic here
    return { deleted: true, listingId };
  }

  private async findOne(listingId: string) {
    // Mock implementation
    return {
      id: listingId,
      sellerId: 'user-123',
      title: 'Test Listing',
    };
  }
}
```

### 6. Fintech Service (src/fintech/fintech.service.ts)

```typescript
/**
 * Fintech Service
 * خدمة التكنولوجيا المالية
 */

import { Injectable } from '@nestjs/common';

@Injectable()
export class FintechService {
  async getCreditScore(userId: string) {
    return {
      userId,
      score: 750,
      rating: 'Good',
      lastUpdated: new Date().toISOString(),
    };
  }

  async getAllCreditScores() {
    return {
      scores: [
        { userId: 'user-1', score: 750, rating: 'Good' },
        { userId: 'user-2', score: 650, rating: 'Fair' },
        { userId: 'user-3', score: 850, rating: 'Excellent' },
      ],
      count: 3,
    };
  }

  async processPayment(paymentData: any) {
    return {
      transactionId: 'txn-123',
      status: 'success',
      ...paymentData,
      processedAt: new Date().toISOString(),
    };
  }
}
```

### 7. Package.json Updates

```json
{
  "name": "marketplace-service",
  "version": "1.0.0",
  "dependencies": {
    "@nestjs/common": "^10.0.0",
    "@nestjs/core": "^10.0.0",
    "@nestjs/platform-express": "^10.0.0",
    "@nestjs/jwt": "^10.0.0",
    "@nestjs/passport": "^10.0.0",
    "@prisma/client": "^5.0.0",
    "passport": "^0.7.0",
    "passport-jwt": "^4.0.0",
    "ioredis": "^5.0.0",
    "@liaoliaots/nestjs-redis": "^9.0.0",
    "@sahool/nestjs-auth": "workspace:*",
    "rxjs": "^7.0.0"
  }
}
```

## Testing the Integration

### 1. Start the service

```bash
cd apps/services/marketplace-service
npm install
npm run start:dev
```

### 2. Test endpoints

```bash
# Public endpoint (no auth)
curl http://localhost:3000/health

# Public marketplace (no auth)
curl http://localhost:3000/marketplace

# Protected endpoint (requires auth)
export TOKEN="your-jwt-token-here"
curl -H "Authorization: Bearer $TOKEN" http://localhost:3000/marketplace/my-activity

# Create listing (requires auth + farmer role)
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Fresh Apples","price":50}' \
  http://localhost:3000/marketplace/listings

# Admin endpoint (requires admin role)
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:3000/fintech/admin/credit-scores
```

### 3. Test with different roles

```javascript
// Generate test tokens with different roles

// Farmer token
{
  "sub": "user-123",
  "email": "farmer@example.com",
  "roles": ["farmer"],
  "iat": 1234567890,
  "exp": 9999999999
}

// Admin token
{
  "sub": "admin-123",
  "email": "admin@example.com",
  "roles": ["admin"],
  "iat": 1234567890,
  "exp": 9999999999
}
```

## What Changed from Original Implementation

### Removed Files
- ❌ `src/auth/jwt-auth.guard.ts` (replaced by shared module)

### Updated Files
- ✅ `src/app.module.ts` - Now imports AuthModule
- ✅ `src/app.controller.ts` - Uses decorators from shared module

### New Files
- ➕ `src/users/user.repository.ts` - User validation repository

### Benefits of Migration

1. **Less Code**: Removed ~100 lines of auth code
2. **More Features**: Added roles, permissions, revocation
3. **Better Security**: User validation, token revocation
4. **Consistency**: Same auth across all services
5. **Maintainability**: Auth bugs fixed in one place
6. **Type Safety**: Full TypeScript support
7. **Testing**: Easier to mock and test

## Troubleshooting

### Redis Connection Error

```bash
# Start Redis locally
docker run -d -p 6379:6379 redis:latest

# Or use Redis from docker-compose
docker-compose up -d redis
```

### JWT Secret Not Found

```bash
# Ensure .env file has JWT_SECRET_KEY
echo "JWT_SECRET_KEY=sahool-marketplace-secret-key-min-32-characters" >> .env
```

### User Repository Error

```typescript
// If your Prisma schema doesn't have all fields, adjust:
const user = await this.prisma.user.findUnique({
  where: { id: userId },
  select: {
    id: true,
    email: true,
    // Only select fields that exist in your schema
  },
});

return {
  userId: user.id,
  email: user.email,
  isActive: true, // Default if field doesn't exist
  isVerified: true,
  roles: [],
  // ...
};
```

## Next Steps

1. ✅ Test all endpoints
2. ✅ Update API documentation
3. ✅ Add E2E tests
4. ✅ Deploy to staging
5. ✅ Monitor authentication logs
6. ✅ Consider enabling global guard
7. ✅ Add more role-based routes
8. ✅ Implement token revocation on logout
