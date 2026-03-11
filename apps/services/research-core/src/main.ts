import "reflect-metadata";
import { NestFactory } from "@nestjs/core";
import { ValidationPipe, Logger, RequestMethod } from "@nestjs/common";
import { SwaggerModule, DocumentBuilder } from "@nestjs/swagger";
import helmet from "helmet";
import { AppModule } from "./app.module";
import { HttpExceptionFilter } from "./utils/http-exception.filter";
import { RequestLoggingInterceptor } from "./utils/request-logging.interceptor";

async function bootstrap() {
  const logger = new Logger("Bootstrap");
  const app = await NestFactory.create(AppModule);

  // Security headers
  app.use(helmet());

  // Global exception filter for unified error handling
  app.useGlobalFilters(new HttpExceptionFilter());

  // Global request logging interceptor for structured logging
  app.useGlobalInterceptors(
    new RequestLoggingInterceptor("research-core", false, false),
  );

  // Global prefix - exclude health endpoints for K8s probes
  app.setGlobalPrefix("api/v1", {
    exclude: [
      { path: "healthz", method: RequestMethod.GET },
      { path: "readyz", method: RequestMethod.GET },
      { path: "health", method: RequestMethod.GET },
    ],
  });

  // Validation pipe
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      transformOptions: {
        enableImplicitConversion: true,
      },
    }),
  );

  // CORS
  app.enableCors({
    origin: process.env.CORS_ALLOWED_ORIGINS?.split(",") || [
      "http://localhost:3000",
    ],
    credentials: true,
  });

  // Swagger documentation - disabled in production
  if (process.env.NODE_ENV !== "production") {
    const config = new DocumentBuilder()
      .setTitle("SAHOOL Research Core API")
      .setDescription(
        "نواة البحث العلمي الزراعي - Agricultural Research Core API",
      )
      .setVersion("16.0.0")
      .addBearerAuth()
      .addTag("experiments", "التجارب البحثية")
      .addTag("protocols", "البروتوكولات")
      .addTag("plots", "قطع الأرض")
      .addTag("treatments", "المعاملات")
      .addTag("logs", "السجلات اليومية")
      .addTag("samples", "العينات")
      .addTag("signatures", "التوقيعات الرقمية")
      .build();

    const document = SwaggerModule.createDocument(app, config);
    SwaggerModule.setup("api/docs", app, document);
  }

  const port = process.env.PORT || 3015;
  await app.listen(port);

  logger.log(`Research Core service running on port ${port}`);
  if (process.env.NODE_ENV !== "production") {
    logger.log(`Swagger docs available at http://localhost:${port}/api/docs`);
  }

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
