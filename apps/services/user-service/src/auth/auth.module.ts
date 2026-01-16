/**
 * Authentication Module for SAHOOL User Service
 * وحدة المصادقة لخدمة المستخدمين
 *
 * Integrates:
 * - JWT authentication
 * - Token revocation with Redis
 * - Password hashing
 * - User validation
 */

import { Module } from "@nestjs/common";
import { JwtModule } from "@nestjs/jwt";
import { PassportModule } from "@nestjs/passport";
import { AuthController } from "./auth.controller";
import { AuthService } from "./auth.service";
import { JwtStrategy } from "./jwt.strategy";
import { JwtAuthGuard } from "./jwt-auth.guard";
import { PrismaModule } from "../prisma/prisma.module";

// Import token revocation services from local utils
import { RedisTokenRevocationStore } from "../utils/token-revocation";
import { TokenRevocationGuard } from "../utils/token-revocation.guard";
import { JWTConfig } from "../utils/jwt.config";

@Module({
  imports: [
    PrismaModule,
    PassportModule.register({ defaultStrategy: "jwt" }),
    JwtModule.register({
      secret: JWTConfig.getSigningKey(),
      signOptions: {
        algorithm: JWTConfig.getEffectiveAlgorithm() as any,
        issuer: JWTConfig.ISSUER,
        audience: JWTConfig.AUDIENCE,
      },
    }),
  ],
  controllers: [AuthController],
  providers: [
    AuthService,
    JwtStrategy,
    JwtAuthGuard,
    // Token revocation services
    {
      provide: RedisTokenRevocationStore,
      useFactory: () => {
        // Create instance with Redis URL from environment
        const redisUrl =
          process.env.REDIS_URL ||
          `redis://${process.env.REDIS_HOST || "localhost"}:${process.env.REDIS_PORT || 6379}`;

        return new RedisTokenRevocationStore(redisUrl);
      },
    },
    TokenRevocationGuard,
  ],
  exports: [AuthService, JwtAuthGuard, RedisTokenRevocationStore],
})
export class AuthModule {}
