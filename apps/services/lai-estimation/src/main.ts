// ═══════════════════════════════════════════════════════════════════════════════
// SAHOOL LAI Estimation Service
// خدمة تقدير مؤشر مساحة الأوراق
// Based on: LAI-TransNet Two-Stage Transfer Learning Framework
// Reference: Artificial Intelligence in Agriculture Journal (2025)
// ═══════════════════════════════════════════════════════════════════════════════

import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  app.useGlobalPipes(new ValidationPipe({ whitelist: true, transform: true }));

  // CORS
  const allowedOrigins = process.env.CORS_ALLOWED_ORIGINS?.split(',') || [
    'https://sahool.com',
    'http://localhost:3000',
  ];
  app.enableCors({ origin: allowedOrigins, credentials: true });

  // Swagger
  const config = new DocumentBuilder()
    .setTitle('SAHOOL LAI Estimation API')
    .setDescription(`
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
    `)
    .setVersion('16.0.0')
    .addBearerAuth()
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('docs', app, document);

  const port = process.env.PORT || 3022;
  await app.listen(port);

  console.log(`🌿 LAI Estimation Service running on port ${port}`);
  console.log(`📚 API Documentation: http://localhost:${port}/docs`);
}

bootstrap();
