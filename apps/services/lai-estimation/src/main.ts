// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL LAI Estimation Service
// خدمة تقدير مؤشر مساحة الأوراق
// Based on: LAI-TransNet Two-Stage Transfer Learning Framework
// Reference: Artificial Intelligence in Agriculture Journal (2025)
// ═══════════════════════════════════════════════════════════════════════════════

// CRITICAL: reflect-metadata must be imported FIRST before any NestJS imports
// Required for decorators and dependency injection to work
import "reflect-metadata";

import { NestFactory } from "@nestjs/core";
import { ValidationPipe } from "@nestjs/common";
import { SwaggerModule, DocumentBuilder } from "@nestjs/swagger";
import { AppModule } from "./app.module";
import helmet from 'helmet';
import { HttpExceptionFilter } from "./utils/http-exception.filter";
import { RequestLoggingInterceptor } from "./utils/request-logging.interceptor";

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Global exception filter for unified error handling
  app.useGlobalFilters(new HttpExceptionFilter());

  app.useGlobalPipes(new ValidationPipe({ whitelist: true, forbidNonWhitelisted: true, transform: true }));

  // ============== Middleware Setup ==============
  // Global request logging interceptor with correlation IDs
  app.useGlobalInterceptors(new RequestLoggingInterceptor("lai-estimation"));

  // Helmet security headers
  app.use(helmet());

  // CORS
  const allowedOrigins = process.env.CORS_ALLOWED_ORIGINS?.split(",") || [
    "https://sahool.com",
    "http://localhost:3000",
  ];
  app.enableCors({ origin: allowedOrigins, credentials: true });

  // Swagger - only in non-production environments
  if (process.env.NODE_ENV !== 'production') {
    const config = new DocumentBuilder()
      .setTitle("SAHOOL LAI Estimation API")
      .setDescription(
        `
      خدمة تقدير مؤشر مساحة الأوراق (LAI)

      Leaf Area Index Estimation Service based on LAI-TransNet research providing:

      🌿 LAI Estimation (تقدير مؤشر مساحة الأوراق)
      - Multi-platform data fusion (UAV + Satellite)
      - Two-stage transfer learning framework
      - Cross-scale predictions (R²=0.69-0.96)

      📊 Vegetation Indices (مؤشرات الغطاء النباتي)
      - NDVI: Normalized Difference Vegetation Index
      - EVI2: Enhanced Vegetation Index 2
      - GNDVI: Green NDVI
      - SAVI: Soil Adjusted Vegetation Index

      🛰️ Data Sources (مصادر البيانات)
      - UAV imagery (centimeter resolution)
      - PlanetScope satellite (3m resolution, daily revisit)
      - Sentinel-2 satellite (10m resolution)

      🔬 Scientific Basis
      - PROSAIL radiative transfer model
      - CNN-TL transfer learning (R²=0.81)
      - CycleGAN domain alignment
    `,
      )
      .setVersion("16.0.0")
      .addBearerAuth()
      .build();

    const document = SwaggerModule.createDocument(app, config);
    SwaggerModule.setup("docs", app, document);
  }

  const port = process.env.PORT || 3022;
  await app.listen(port);

  console.log(`🌿 LAI Estimation Service running on port ${port}`);
  console.log(`📚 API Documentation: http://localhost:${port}/docs`);

  // Graceful shutdown
  let isShuttingDown = false;
  async function gracefulShutdown(signal: string) {
    if (isShuttingDown) return;
    isShuttingDown = true;
    console.log(`\nReceived ${signal}, starting graceful shutdown...`);
    try {
      await app.close();
      console.log('Service shutdown complete');
      process.exit(0);
    } catch (error) {
      console.error('Error during graceful shutdown:', error);
      process.exit(1);
    }
  }

  process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
  process.on('SIGINT', () => gracefulShutdown('SIGINT'));
}

bootstrap();
