/**
 * SAHOOL Marketplace & FinTech Service v15.3
 * سوق سهول والخدمات المالية
 *
 * Features:
 * - Agricultural marketplace (B2B/B2C)
 * - Digital wallet for farmers
 * - Credit scoring based on farm data
 * - Agricultural loans (Islamic finance compatible)
 */

import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Global validation pipe
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      transform: true,
    }),
  );

  // CORS
  app.enableCors({
    origin: '*',
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Tenant-ID'],
  });

  // Global prefix
  app.setGlobalPrefix('api/v1');

  const port = process.env.PORT || 3010;
  await app.listen(port);

  console.log(`
  ╔═══════════════════════════════════════════════════════════════╗
  ║   🛒 SAHOOL Marketplace & FinTech Service v15.3               ║
  ║   سوق سهول والخدمات المالية                                   ║
  ╠═══════════════════════════════════════════════════════════════╣
  ║   Server running on: http://localhost:${port}                   ║
  ║   API Documentation: http://localhost:${port}/api/v1            ║
  ╚═══════════════════════════════════════════════════════════════╝
  `);
}

bootstrap();
