/**
 * SAHOOL Marketplace & FinTech Service v16.0.0
 * سوق سهول والخدمات المالية
 *
 * Features:
 * - Agricultural marketplace (B2B/B2C)
 * - Digital wallet for farmers
 * - Credit scoring based on farm data
 * - Agricultural loans (Islamic finance compatible)
 */

import "reflect-metadata";
import { NestFactory } from "@nestjs/core";
import { RequestMethod, ValidationPipe } from "@nestjs/common";
import { SwaggerModule, DocumentBuilder } from "@nestjs/swagger";
import helmet from "helmet";
import { AppModule } from "./app.module";
import { HttpExceptionFilter } from "./filters/http-exception.filter";
import { RequestLoggingInterceptor } from "./utils/request-logging.interceptor";

// Prevent unhandled Redis/NATS errors from crashing the process
process.on("unhandledRejection", (reason) => {
  const msg = reason instanceof Error ? reason.message : String(reason);
  if (msg.includes("SocketClosedUnexpectedly") || msg.includes("ECONNREFUSED")) {
    console.warn(`[marketplace-service] Suppressed connection error: ${msg}`);
    return;
  }
  console.error("[marketplace-service] Unhandled rejection:", reason);
});

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Security headers
  app.use(helmet());

  // Global exception filter for unified error handling
  app.useGlobalFilters(new HttpExceptionFilter());

  // Global validation pipe
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
    }),
  );

  // ============== Middleware Setup ==============
  // Global request logging interceptor with correlation IDs
  app.useGlobalInterceptors(
    new RequestLoggingInterceptor("marketplace-service"),
  );

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

  // Global prefix — exclude health endpoints for K8s probes and CI container tests
  app.setGlobalPrefix("api/v1", {
    exclude: [
      { path: "healthz", method: RequestMethod.GET },
      { path: "readyz", method: RequestMethod.GET },
    ],
  });

  // Swagger/OpenAPI Documentation (non-production only)
  if (process.env.NODE_ENV !== 'production') {
    const config = new DocumentBuilder()
      .setTitle("SAHOOL Marketplace & FinTech API")
      .setDescription(
        `
        سوق سهول والخدمات المالية

        ## Features
        - **Marketplace**: Agricultural products B2B/B2C trading
        - **Wallet**: Digital wallet management for farmers
        - **Credit Scoring**: Farm data-based credit scoring
        - **Loans**: Islamic finance compatible agricultural loans
      `,
      )
      .setVersion("16.0.0")
      .addTag("Market", "Marketplace operations")
      .addTag("Wallet", "Digital wallet management")
      .addTag("Loans", "Agricultural loan services")
      .addBearerAuth()
      .addApiKey(
        { type: "apiKey", name: "X-Tenant-ID", in: "header" },
        "tenant-id",
      )
      .build();

    const document = SwaggerModule.createDocument(app, config);
    SwaggerModule.setup("docs", app, document);
  }

  const port = process.env.PORT || 3010;
  await app.listen(port);

  console.log(`
  ╔═══════════════════════════════════════════════════════════════╗
  ║   🛒 SAHOOL Marketplace & FinTech Service v16.0.0              ║
  ║   سوق سهول والخدمات المالية                                   ║
  ╠═══════════════════════════════════════════════════════════════╣
  ║   Server running on: http://localhost:${port}                   ║
  ║   API Documentation: http://localhost:${port}/docs              ║
  ╚═══════════════════════════════════════════════════════════════╝
  `);

  // Graceful shutdown handlers
  let isShuttingDown = false;

  async function gracefulShutdown(signal: string) {
    if (isShuttingDown) return;
    isShuttingDown = true;

    console.log(`\nReceived ${signal}, starting graceful shutdown...`);

    try {
      // Close NestJS application
      // This will:
      // - Stop accepting new requests
      // - Wait for existing requests to complete
      // - Trigger OnModuleDestroy hooks (including Prisma $disconnect)
      // - Close all connections
      await app.close();

      console.log("Marketplace & FinTech Service shutdown complete");
      process.exit(0);
    } catch (error) {
      console.error("Error during graceful shutdown:", error);
      process.exit(1);
    }
  }

  process.on("SIGTERM", () => gracefulShutdown("SIGTERM"));
  process.on("SIGINT", () => gracefulShutdown("SIGINT"));
}

bootstrap();
