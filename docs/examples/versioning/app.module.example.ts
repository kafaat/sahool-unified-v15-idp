/**
 * Example: app.module.ts with API Versioning
 * Demonstrates how to structure modules for multiple API versions
 */

import { Module } from "@nestjs/common";
import { APP_INTERCEPTOR } from "@nestjs/core";
import { DeprecationInterceptor } from "@sahool/versioning";

// V1 Controllers (Deprecated)
import { UsersV1Controller } from "./users/users.v1.controller";
import { FieldsV1Controller } from "./fields/fields.v1.controller";
import { WeatherV1Controller } from "./weather/weather.v1.controller";

// V2 Controllers (Current)
import { UsersV2Controller } from "./users/users.v2.controller";
import { FieldsV2Controller } from "./fields/fields.v2.controller";
import { WeatherV2Controller } from "./weather/weather.v2.controller";

// Services (Shared between versions)
import { UsersService } from "./users/users.service";
import { FieldsService } from "./fields/fields.service";
import { WeatherService } from "./weather/weather.service";

// Database modules
import { PrismaModule } from "./prisma/prisma.module";

/**
 * Main Application Module
 * Includes both v1 and v2 controllers
 */
@Module({
  imports: [
    PrismaModule,
    // Other shared modules
  ],
  controllers: [
    // V1 Controllers (Deprecated)
    UsersV1Controller,
    FieldsV1Controller,
    WeatherV1Controller,

    // V2 Controllers (Current)
    UsersV2Controller,
    FieldsV2Controller,
    WeatherV2Controller,
  ],
  providers: [
    // Services (shared between versions)
    UsersService,
    FieldsService,
    WeatherService,

    // Global interceptor for deprecation warnings
    {
      provide: APP_INTERCEPTOR,
      useClass: DeprecationInterceptor,
    },
  ],
})
export class AppModule {}

/**
 * Alternative: Separate modules for each version
 * This approach provides better separation and can be useful for larger applications
 */

// V1 Module (Deprecated)
@Module({
  imports: [PrismaModule],
  controllers: [UsersV1Controller, FieldsV1Controller, WeatherV1Controller],
  providers: [UsersService, FieldsService, WeatherService],
})
export class V1Module {}

// V2 Module (Current)
@Module({
  imports: [PrismaModule],
  controllers: [UsersV2Controller, FieldsV2Controller, WeatherV2Controller],
  providers: [UsersService, FieldsService, WeatherService],
})
export class V2Module {}

// Main module importing versioned modules
@Module({
  imports: [V1Module, V2Module, PrismaModule],
  providers: [
    {
      provide: APP_INTERCEPTOR,
      useClass: DeprecationInterceptor,
    },
  ],
})
export class AppModuleWithVersionedModules {}

/**
 * Migration Strategy:
 *
 * Phase 1: Add v2 controllers alongside v1
 * - Keep v1 controllers active
 * - Add v2 controllers with new features
 * - Services remain shared
 *
 * Phase 2: Add deprecation warnings (Current)
 * - Add deprecation interceptor
 * - Update v1 controllers to log warnings
 * - Update documentation
 *
 * Phase 3: Reduce v1 rate limits
 * - Reduce rate limits in Kong for v1 endpoints
 * - Monitor v1 usage
 * - Contact heavy v1 users
 *
 * Phase 4: Remove v1 (After sunset date)
 * - Remove v1 controllers
 * - Remove v1 routes from Kong
 * - Return 410 Gone for v1 requests
 */
