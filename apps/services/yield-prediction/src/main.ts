// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL Yield Prediction Service
// خدمة التنبؤ بالإنتاجية الزراعية
// Based on: Agricultural Remote Sensing On-Demand Service Model
// ═══════════════════════════════════════════════════════════════════════════════

// CRITICAL: reflect-metadata must be imported FIRST before any NestJS imports
// Required for decorators and dependency injection to work
import "reflect-metadata";

import { NestFactory } from "@nestjs/core";
import { ValidationPipe } from "@nestjs/common";
import { SwaggerModule, DocumentBuilder } from "@nestjs/swagger";
import { AppModule } from "./app.module";
import { HttpExceptionFilter } from "./utils/http-exception.filter";
import { RequestLoggingInterceptor } from "./utils/request-logging.interceptor";

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Global exception filter for unified error handling
  app.useGlobalFilters(new HttpExceptionFilter());

  app.useGlobalPipes(new ValidationPipe({ whitelist: true, forbidNonWhitelisted: true, transform: true }));

  // ============== Middleware Setup ==============
  // Global request logging interceptor with correlation IDs
  app.useGlobalInterceptors(new RequestLoggingInterceptor("yield-prediction"));

  // CORS
  const allowedOrigins = process.env.CORS_ALLOWED_ORIGINS?.split(",") || [
    "https://sahool.com",
    "http://localhost:3000",
  ];
  app.enableCors({ origin: allowedOrigins, credentials: true });

  // Swagger
  const config = new DocumentBuilder()
    .setTitle("SAHOOL Yield Prediction API")
    .setDescription(
      `
      خدمة التنبؤ بالإنتاجية الزراعية

      Agricultural Yield Prediction Service providing:
      - Crop yield forecasting (التنبؤ بإنتاجية المحاصيل)
      - Growth stage monitoring (مراقبة مراحل النمو)
      - Harvest timing prediction (التنبؤ بموعد الحصاد)
      - Historical yield analysis (تحليل الإنتاجية التاريخية)
      - Comparison with regional averages (المقارنة مع المعدلات الإقليمية)
    `,
    )
    .setVersion("16.0.0")
    .addBearerAuth()
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup("docs", app, document);

  // Health endpoints (/healthz, /readyz) are registered at root level
  // via AppController, outside any global prefix

  const port = process.env.PORT || 3021;
  await app.listen(port);

  console.log(`🌾 Yield Prediction Service running on port ${port}`);
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
