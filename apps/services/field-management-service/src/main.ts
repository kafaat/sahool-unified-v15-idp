/**
 * SAHOOL Field Management Service v16.0.0
 * خدمة إدارة الحقول الزراعية
 *
 * Features:
 * - PostGIS geospatial operations
 * - Offline-first mobile sync
 * - Redis caching layer
 * - Optimistic locking with ETags
 */

import "reflect-metadata";
import { NestFactory } from "@nestjs/core";
import { ValidationPipe, Logger } from "@nestjs/common";
import { SwaggerModule, DocumentBuilder } from "@nestjs/swagger";
import helmet from "helmet";
import { AppModule } from "./app.module";

const logger = new Logger("Bootstrap");

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Security headers
  app.use(helmet());

  // Global validation pipe with transformation
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      transform: true,
      transformOptions: {
        enableImplicitConversion: true,
      },
    }),
  );

  // CORS configuration
  const allowedOrigins = process.env.CORS_ALLOWED_ORIGINS?.split(",") || [
    "https://sahool.app",
    "https://admin.sahool.app",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
  ];

  app.enableCors({
    origin: allowedOrigins,
    methods: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allowedHeaders: [
      "Content-Type",
      "Authorization",
      "If-Match",
      "X-Request-ID",
      "X-Tenant-ID",
    ],
    credentials: true,
    exposedHeaders: ["ETag", "X-Cache", "X-Cache-Key"],
  });

  // Swagger/OpenAPI Documentation (non-production only)
  if (process.env.NODE_ENV !== 'production') {
    const config = new DocumentBuilder()
      .setTitle("SAHOOL Field Management API")
      .setDescription(
        `
        خدمة إدارة الحقول الزراعية

        ## Features
        - **Field CRUD**: Full field management with PostGIS
        - **Mobile Sync**: Delta sync for offline-first apps
        - **NDVI Analysis**: Vegetation index tracking
        - **Task Management**: Agricultural operations
        - **Boundary History**: Version tracking with rollback
      `,
      )
      .setVersion("16.0.0")
      .addTag("Fields - الحقول", "Field management")
      .addTag("Tasks - المهام", "Task management")
      .addTag("NDVI - مؤشر الغطاء النباتي", "Vegetation index")
      .addTag("Sync - المزامنة", "Mobile sync")
      .addTag("Health - الصحة", "Service health")
      .addBearerAuth()
      .addApiKey(
        { type: "apiKey", name: "X-Tenant-ID", in: "header" },
        "tenant-id",
      )
      .build();

    const document = SwaggerModule.createDocument(app, config);
    SwaggerModule.setup("docs", app, document);
  }

  // Start server
  const port = process.env.PORT || 3000;
  await app.listen(port, "0.0.0.0");

  logger.log(`
  ╔═══════════════════════════════════════════════════════════════╗
  ║   🌾 SAHOOL Field Management Service v16.0.0                  ║
  ║   خدمة إدارة الحقول الزراعية                                   ║
  ╠═══════════════════════════════════════════════════════════════╣
  ║   Server: http://localhost:${port}                              ║
  ║   Docs:   http://localhost:${port}/docs                         ║
  ╚═══════════════════════════════════════════════════════════════╝

  📡 API Endpoints:
    GET  /healthz              - Liveness probe
    GET  /readyz               - Readiness probe
    GET  /health               - Detailed health status
    GET  /metrics              - Prometheus metrics

  🌿 Field Management:
    GET    /api/v1/fields           - List fields
    POST   /api/v1/fields           - Create field
    GET    /api/v1/fields/:id       - Get field
    PUT    /api/v1/fields/:id       - Update field
    DELETE /api/v1/fields/:id       - Delete field
    GET    /api/v1/fields/nearby    - Find nearby fields
    GET    /api/v1/fields/stats/:id - Get field stats

  📱 Mobile Sync:
    GET  /api/v1/fields/sync        - Delta sync
    POST /api/v1/fields/sync/batch  - Batch upload
    GET  /api/v1/sync/status        - Sync status
    PUT  /api/v1/sync/status        - Update status

  📊 NDVI Analysis:
    GET /api/v1/fields/:id/ndvi     - Field NDVI
    PUT /api/v1/fields/:id/ndvi     - Update NDVI
    GET /api/v1/ndvi/summary        - Tenant summary

  ✅ Tasks:
    GET   /api/v1/tasks/field/:id   - Field tasks
    POST  /api/v1/tasks             - Create task
    PATCH /api/v1/tasks/:id/status  - Update status
    GET   /api/v1/tasks/overdue     - Overdue tasks
  `);

  // Graceful shutdown
  let isShuttingDown = false;

  async function gracefulShutdown(signal: string) {
    if (isShuttingDown) return;
    isShuttingDown = true;

    logger.log(`Received ${signal}, starting graceful shutdown...`);

    try {
      await app.close();
      logger.log("Field Management Service shutdown complete");
      process.exit(0);
    } catch (error) {
      logger.error("Error during graceful shutdown:", error);
      process.exit(1);
    }
  }

  process.on("SIGTERM", () => gracefulShutdown("SIGTERM"));
  process.on("SIGINT", () => gracefulShutdown("SIGINT"));
}

bootstrap().catch((error) => {
  logger.error("Failed to start Field Management Service:", error);
  process.exit(1);
});
