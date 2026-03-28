/**
 * SAHOOL User Service v16.0.0
 * خدمة إدارة المستخدمين
 *
 * Features:
 * - User registration and authentication
 * - User profile management
 * - Role-based access control
 * - Session management
 * - Multi-tenant user isolation
 * - Email and phone verification
 */

// CRITICAL: reflect-metadata must be imported FIRST before any NestJS imports
// Required for decorators and dependency injection to work
import "reflect-metadata";

import { NestFactory } from "@nestjs/core";
import { ValidationPipe, RequestMethod, Logger } from "@nestjs/common";
import { SwaggerModule, DocumentBuilder } from "@nestjs/swagger";
import helmet from 'helmet';
import { AppModule } from "./app.module";
import { HttpExceptionFilter } from "./utils/http-exception.filter";
import { RequestLoggingInterceptor } from "./utils/request-logging.interceptor";

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  const logger = new Logger('Bootstrap');

  // Security headers
  app.use(helmet());

  // Global exception filter for unified error handling
  app.useGlobalFilters(new HttpExceptionFilter());

  // Global validation pipe
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      transform: true,
      forbidNonWhitelisted: true,
    }),
  );

  // ============== Middleware Setup ==============
  // Global request logging interceptor with correlation IDs
  app.useGlobalInterceptors(new RequestLoggingInterceptor("user-service"));

  // CORS - Secure configuration using environment variable
  const allowedOrigins = process.env.CORS_ALLOWED_ORIGINS?.split(",") || [
    "https://sahool.com",
    "https://app.sahool.com",
    "https://admin.sahool.com",
    "http://localhost:3000",
    "http://localhost:8080",
  ];

  app.enableCors({
    origin: allowedOrigins,
    methods: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allowedHeaders: [
      "Content-Type",
      "Authorization",
      "X-Tenant-ID",
      "X-Request-ID",
    ],
    credentials: true,
  });

  // Global prefix - exclude health and metrics endpoints for K8s probes & Prometheus
  app.setGlobalPrefix("api/v1", {
    exclude: [
      { path: "healthz", method: RequestMethod.GET },
      { path: "readyz", method: RequestMethod.GET },
      { path: "health", method: RequestMethod.GET },
      { path: "metrics", method: RequestMethod.GET },
    ],
  });

  // Swagger/OpenAPI Documentation - disabled in production
  if (process.env.NODE_ENV !== 'production') {
    const config = new DocumentBuilder()
      .setTitle("SAHOOL User Service API")
      .setDescription(
        `
      خدمة إدارة المستخدمين

      ## Features
      - **User Management**: Complete CRUD operations for users
      - **Multi-tenant**: Isolated user data per tenant
      - **Authentication**: Secure password hashing with bcrypt
      - **User Roles**: ADMIN, MANAGER, FARMER, WORKER, VIEWER
      - **User Status**: ACTIVE, INACTIVE, SUSPENDED, PENDING
      - **Profile Management**: Extended user profile information
      - **Session Management**: Track user sessions and login history
      - **Verification**: Email and phone number verification
      - **Refresh Tokens**: Secure token refresh mechanism

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
    `,
      )
      .setVersion("16.0.0")
      .addTag("Users", "User management operations")
      .addBearerAuth()
      .addApiKey(
        { type: "apiKey", name: "X-Tenant-ID", in: "header" },
        "tenant-id",
      )
      .build();

    const document = SwaggerModule.createDocument(app, config);
    SwaggerModule.setup("docs", app, document);
  }

  const port = process.env.PORT || 3025;
  await app.listen(port);

  logger.log(`SAHOOL User Service v16.0.0 running on http://localhost:${port}`);

  // Graceful shutdown handlers
  let isShuttingDown = false;

  async function gracefulShutdown(signal: string) {
    if (isShuttingDown) return;
    isShuttingDown = true;

    logger.log(`Received ${signal}, starting graceful shutdown...`);

    try {
      // Close NestJS application
      // This will:
      // - Stop accepting new requests
      // - Wait for existing requests to complete
      // - Trigger OnModuleDestroy hooks (including Prisma $disconnect)
      // - Close all connections
      await app.close();

      logger.log("User Service shutdown complete");
      process.exit(0);
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      logger.error(`Error during graceful shutdown: ${message}`);
      process.exit(1);
    }
  }

  process.on("SIGTERM", () => gracefulShutdown("SIGTERM"));
  process.on("SIGINT", () => gracefulShutdown("SIGINT"));
}

bootstrap();
