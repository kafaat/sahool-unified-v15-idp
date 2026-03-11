// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL Crop Growth Model Service
// خدمة نموذج نمو المحاصيل
// Based on: WOFOST, DSSAT, APSIM mechanistic crop growth models
// Reference: Mechanistic, Intelligent and Integrated Development of Crop Models
// ═══════════════════════════════════════════════════════════════════════════════

// CRITICAL: reflect-metadata must be imported FIRST before any NestJS imports
// Required for decorators and dependency injection to work
import "reflect-metadata";

import { NestFactory } from "@nestjs/core";
import { ValidationPipe } from "@nestjs/common";
import { SwaggerModule, DocumentBuilder } from "@nestjs/swagger";
import helmet from "helmet";
import { AppModule } from "./app.module";
import { HttpExceptionFilter } from "./utils/http-exception.filter";
import { RequestLoggingInterceptor } from "./utils/request-logging.interceptor";

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Security headers
  app.use(helmet());

  // Global exception filter for unified error handling
  app.useGlobalFilters(new HttpExceptionFilter());

  app.useGlobalPipes(new ValidationPipe({ whitelist: true, forbidNonWhitelisted: true, transform: true }));

  // ============== Middleware Setup ==============
  // Global request logging interceptor with correlation IDs
  app.useGlobalInterceptors(new RequestLoggingInterceptor("crop-growth-model"));

  // CORS
  const allowedOrigins = process.env.CORS_ALLOWED_ORIGINS?.split(",") || [
    "https://sahool.com",
    "http://localhost:3000",
  ];
  app.enableCors({ origin: allowedOrigins, credentials: true });

  // Swagger (non-production only)
  if (process.env.NODE_ENV !== 'production') {
    const config = new DocumentBuilder()
      .setTitle("SAHOOL Crop Growth Model API")
      .setDescription(
        `
      خدمة نموذج نمو المحاصيل الآلي والذكي والمتكامل

      Mechanistic Crop Growth Model Service providing:

      🌱 Phenology Simulation (محاكاة مراحل النمو)
      - Development Stage (DVS) tracking
      - Thermal time accumulation (GDD)
      - Growth stage transitions

      ☀️ Photosynthesis Modeling (نمذجة التمثيل الضوئي)
      - Farquhar biochemical model concepts
      - Light Use Efficiency (LUE)
      - CO2 assimilation rates

      🌿 Biomass & Assimilate Distribution (توزيع الكتلة الحيوية)
      - Source-Sink-Flow partitioning
      - Organ-specific allocation (root, stem, leaf, storage)
      - Dynamic redistribution

      🌡️ Environmental Response (الاستجابة البيئية)
      - Temperature stress factors
      - Water stress simulation
      - Nutrient limitation effects

      📊 Model Integration
      - WOFOST-inspired crop parameters
      - DSSAT crop module concepts
      - APSIM soil-crop coupling

      Based on scientific literature with Impact Factor 12.4+
    `,
      )
      .setVersion("16.0.0")
      .addBearerAuth()
      .build();

    const document = SwaggerModule.createDocument(app, config);
    SwaggerModule.setup("docs", app, document);
  }

  const port = process.env.PORT || 3023;
  await app.listen(port);

  console.log(`🌱 Crop Growth Model Service running on port ${port}`);
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
