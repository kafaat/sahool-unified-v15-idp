// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL Disaster Assessment Service
// خدمة تقييم الكوارث الزراعية
// Based on: Agricultural Remote Sensing On-Demand Service Model
// ═══════════════════════════════════════════════════════════════════════════════

import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { AppModule } from './app.module';
import { HttpExceptionFilter } from '../../shared/errors';
import { RequestLoggingInterceptor } from '../../shared/middleware/request-logging';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

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

  // CORS configuration
  const allowedOrigins = process.env.CORS_ALLOWED_ORIGINS?.split(',') || [
    'https://sahool.com',
    'https://app.sahool.com',
    'http://localhost:3000',
  ];
  app.enableCors({
    origin: allowedOrigins,
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
    credentials: true,
  });

  // Swagger/OpenAPI Documentation
  const config = new DocumentBuilder()
    .setTitle('SAHOOL Disaster Assessment API')
    .setDescription(`
      خدمة تقييم الكوارث الزراعية

      Agricultural Disaster Assessment Service providing:
      - Flood damage assessment (تقييم أضرار الفيضانات)
      - Drought monitoring (مراقبة الجفاف)
      - Frost damage evaluation (تقييم أضرار الصقيع)
      - Hail damage assessment (تقييم أضرار البَرَد)
      - Pest & disease outbreak tracking (تتبع تفشي الآفات والأمراض)
      - Storm damage evaluation (تقييم أضرار العواصف)
    `)
    .setVersion('16.0.0')
    .addTag('disasters', 'Disaster monitoring and assessment')
    .addTag('alerts', 'Early warning alerts')
    .addTag('reports', 'Damage reports and statistics')
    .addBearerAuth()
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('docs', app, document);

  const port = process.env.PORT || 3020;
  await app.listen(port);

  console.log(`🚨 Disaster Assessment Service running on port ${port}`);
  console.log(`📚 API Documentation: http://localhost:${port}/docs`);
}

bootstrap();
