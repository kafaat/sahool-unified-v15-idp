/**
 * SAHOOL IoT Service - Main Entry Point
 * خدمة إنترنت الأشياء - نقطة البداية
 *
 * Features:
 * - MQTT broker connection
 * - Sensor data ingestion
 * - Actuator control (pumps, valves)
 * - Real-time data streaming
 */

import 'reflect-metadata';
import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { AppModule } from './app.module';
import { HttpExceptionFilter } from './utils/http-exception.filter';
import { RequestLoggingInterceptor } from './utils/request-logging.interceptor';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Global exception filter for unified error handling
  app.useGlobalFilters(new HttpExceptionFilter());

  // CORS configuration - restrict to allowed origins
  const allowedOrigins = process.env.CORS_ORIGINS
    ? process.env.CORS_ORIGINS.split(',')
    : [
        'https://sahool.io',
        'https://app.sahool.io',
        'https://admin.sahool.io',
        'http://localhost:3000',
        'http://localhost:3001',
      ];

  app.enableCors({
    origin: allowedOrigins,
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    credentials: true,
  });

  // Validation
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      transform: true,
    }),
  );

  // API prefix
  app.setGlobalPrefix('api/v1');

  // Swagger documentation
  const config = new DocumentBuilder()
    .setTitle('SAHOOL IoT Service')
    .setDescription('Smart Irrigation & Sensor Management API')
    .setVersion('1.0')
    .addTag('sensors', 'Sensor data endpoints')
    .addTag('actuators', 'Pump & valve control')
    .addTag('devices', 'Device management')
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('docs', app, document);

  const port = process.env.PORT || 8117;
  await app.listen(port);

  console.log(`
╔═══════════════════════════════════════════════════════════╗
║             SAHOOL IoT Service Started                   ║
╠═══════════════════════════════════════════════════════════╣
║  📡 Service: http://localhost:${port}                       ║
║  📚 Swagger: http://localhost:${port}/docs                  ║
║  🔌 MQTT: Connected to broker                            ║
╚═══════════════════════════════════════════════════════════╝
  `);
}

bootstrap();
