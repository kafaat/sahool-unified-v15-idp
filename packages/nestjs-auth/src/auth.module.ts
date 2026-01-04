/**
 * SAHOOL Shared Authentication Module
 * وحدة المصادقة المشتركة لمنصة سهول
 *
 * A comprehensive authentication module for NestJS services providing:
 * - JWT authentication with RS256/HS256 support
 * - Role-based access control (RBAC)
 * - Permission-based access control
 * - Token revocation support
 * - User validation with Redis caching
 * - Multiple authentication guards
 * - Custom decorators for easy usage
 *
 * @module AuthModule
 */

import { Module, DynamicModule, Global } from '@nestjs/common';
import { JwtModule, JwtModuleOptions } from '@nestjs/jwt';
import { PassportModule } from '@nestjs/passport';

// Import all guards
import {
  JwtAuthGuard,
  RolesGuard,
  PermissionsGuard,
  FarmAccessGuard,
  OptionalAuthGuard,
  ActiveAccountGuard,
} from './guards/jwt.guard';

import {
  TokenRevocationGuard,
  TokenRevocationInterceptor,
} from './guards/token-revocation.guard';

// Import strategy
import { JwtStrategy } from './strategies/jwt.strategy';

// Import services
import { UserValidationService, IUserRepository } from './services/user-validation.service';

// Import config
import { JWTConfig } from './config/jwt.config';

/**
 * Configuration options for AuthModule
 */
export interface AuthModuleOptions {
  /**
   * JWT configuration options
   * If not provided, will use JWTConfig defaults from environment
   */
  jwtOptions?: JwtModuleOptions;

  /**
   * Enable user validation service (requires Redis and UserRepository)
   * @default true
   */
  enableUserValidation?: boolean;

  /**
   * Enable token revocation checking (requires Redis)
   * @default true
   */
  enableTokenRevocation?: boolean;

  /**
   * User repository implementation for database lookups
   * Required if enableUserValidation is true
   */
  userRepository?: IUserRepository;

  /**
   * Enable global authentication guard
   * If true, all routes will require authentication unless marked with @Public()
   * @default false
   */
  enableGlobalGuard?: boolean;

  /**
   * Validate JWT configuration on module initialization
   * @default true
   */
  validateConfig?: boolean;
}

/**
 * Shared Authentication Module for SAHOOL Platform
 *
 * @example
 * Basic usage:
 * ```typescript
 * import { Module } from '@nestjs/common';
 * import { AuthModule } from '@sahool/nestjs-auth';
 *
 * @Module({
 *   imports: [
 *     AuthModule.forRoot({
 *       enableUserValidation: true,
 *       userRepository: myUserRepository,
 *     }),
 *   ],
 * })
 * export class AppModule {}
 * ```
 *
 * @example
 * With custom JWT options:
 * ```typescript
 * AuthModule.forRoot({
 *   jwtOptions: {
 *     secret: 'custom-secret',
 *     signOptions: {
 *       expiresIn: '1h',
 *     },
 *   },
 * })
 * ```
 */
@Global()
@Module({})
export class AuthModule {
  /**
   * Create a dynamic AuthModule with custom configuration
   *
   * @param options - Configuration options
   * @returns Dynamic module
   */
  static forRoot(options: AuthModuleOptions = {}): DynamicModule {
    const {
      jwtOptions,
      enableUserValidation = true,
      enableTokenRevocation = true,
      userRepository,
      enableGlobalGuard = false,
      validateConfig = true,
    } = options;

    // Validate JWT configuration if enabled
    if (validateConfig) {
      try {
        JWTConfig.validate();
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        console.error('[AuthModule] Configuration validation failed:', errorMessage);
        throw error;
      }
    }

    // Use provided JWT options or defaults from JWTConfig
    const jwtModuleOptions: JwtModuleOptions = jwtOptions || {
      secret: JWTConfig.getVerificationKey(),
      signOptions: {
        expiresIn: `${JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES}m`,
        issuer: JWTConfig.ISSUER,
        audience: JWTConfig.AUDIENCE,
        algorithm: JWTConfig.ALGORITHM as any,
      },
    };

    // Build providers array
    const providers: any[] = [
      // Guards
      JwtAuthGuard,
      RolesGuard,
      PermissionsGuard,
      FarmAccessGuard,
      OptionalAuthGuard,
      ActiveAccountGuard,

      // Strategy
      {
        provide: JwtStrategy,
        useFactory: (userValidationService?: UserValidationService) => {
          return new JwtStrategy(
            enableUserValidation ? userValidationService : undefined
          );
        },
        inject: enableUserValidation ? [UserValidationService] : [],
      },
    ];

    // Add user validation service if enabled
    if (enableUserValidation) {
      providers.push({
        provide: UserValidationService,
        useFactory: (redis: any) => {
          return new UserValidationService(redis, userRepository);
        },
        inject: ['REDIS_CLIENT'],
      });
    }

    // Add token revocation providers if enabled
    if (enableTokenRevocation) {
      providers.push(
        TokenRevocationGuard,
        TokenRevocationInterceptor,
      );
    }

    // Add global guard if enabled
    if (enableGlobalGuard) {
      providers.push({
        provide: 'APP_GUARD',
        useClass: JwtAuthGuard,
      });
    }

    return {
      module: AuthModule,
      imports: [
        PassportModule.register({ defaultStrategy: 'jwt' }),
        JwtModule.register(jwtModuleOptions),
      ],
      providers,
      exports: [
        JwtModule,
        PassportModule,
        JwtAuthGuard,
        RolesGuard,
        PermissionsGuard,
        FarmAccessGuard,
        OptionalAuthGuard,
        ActiveAccountGuard,
        JwtStrategy,
        ...(enableUserValidation ? [UserValidationService] : []),
        ...(enableTokenRevocation ? [TokenRevocationGuard, TokenRevocationInterceptor] : []),
      ],
    };
  }

  /**
   * Create AuthModule for async configuration
   * Useful when configuration depends on other modules
   *
   * @example
   * ```typescript
   * import { ConfigModule, ConfigService } from '@nestjs/config';
   *
   * AuthModule.forRootAsync({
   *   imports: [ConfigModule],
   *   useFactory: (configService: ConfigService) => ({
   *     jwtOptions: {
   *       secret: configService.get('JWT_SECRET'),
   *     },
   *     enableUserValidation: true,
   *   }),
   *   inject: [ConfigService],
   * })
   * ```
   */
  static forRootAsync(options: {
    imports?: any[];
    useFactory: (...args: any[]) => Promise<AuthModuleOptions> | AuthModuleOptions;
    inject?: any[];
  }): DynamicModule {
    return {
      module: AuthModule,
      imports: [
        PassportModule.register({ defaultStrategy: 'jwt' }),
        JwtModule.registerAsync({
          imports: options.imports,
          useFactory: async (...args: any[]) => {
            const config = await options.useFactory(...args);
            return config.jwtOptions || {
              secret: JWTConfig.getVerificationKey(),
              signOptions: {
                expiresIn: `${JWTConfig.ACCESS_TOKEN_EXPIRE_MINUTES}m`,
                issuer: JWTConfig.ISSUER,
                audience: JWTConfig.AUDIENCE,
              },
            };
          },
          inject: options.inject,
        }),
      ],
      providers: [
        JwtAuthGuard,
        RolesGuard,
        PermissionsGuard,
        FarmAccessGuard,
        OptionalAuthGuard,
        ActiveAccountGuard,
        JwtStrategy,
      ],
      exports: [
        JwtModule,
        PassportModule,
        JwtAuthGuard,
        RolesGuard,
        PermissionsGuard,
        FarmAccessGuard,
        OptionalAuthGuard,
        ActiveAccountGuard,
        JwtStrategy,
      ],
    };
  }
}
