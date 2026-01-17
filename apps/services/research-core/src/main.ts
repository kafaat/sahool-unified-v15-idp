import "reflect-metadata";
import { NestFactory } from "@nestjs/core";
import { ValidationPipe, Logger } from "@nestjs/common";
import { SwaggerModule, DocumentBuilder } from "@nestjs/swagger";
import { AppModule } from "./app.module";
import { HttpExceptionFilter } from "./utils/http-exception.filter";
import { RequestLoggingInterceptor } from "./utils/request-logging.interceptor";

async function bootstrap() {
  const logger = new Logger("Bootstrap");
  const app = await NestFactory.create(AppModule);

  // Global exception filter for unified error handling
  app.useGlobalFilters(new HttpExceptionFilter());

  // Global prefix
  app.setGlobalPrefix("api/v1");

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

  // Swagger documentation
  const config = new DocumentBuilder()
    .setTitle("SAHOOL Research Core API")
    .setDescription(
      "نواة البحث العلمي الزراعي - Agricultural Research Core API",
    )
    .setVersion("15.3.0")
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

  const port = process.env.PORT || 3015;
  await app.listen(port);

  logger.log(`Research Core service running on port ${port}`);
  logger.log(`Swagger docs available at http://localhost:${port}/api/docs`);
}

bootstrap();
