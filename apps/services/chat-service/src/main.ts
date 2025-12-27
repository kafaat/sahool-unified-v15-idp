/**
 * SAHOOL Chat Service v16.0.0
 * خدمة المحادثات للسوق الزراعي
 *
 * Features:
 * - Real-time buyer-seller messaging using Socket.IO
 * - Message history and pagination
 * - Typing indicators and read receipts
 * - Online/offline status tracking
 * - Product and order-linked conversations
 * - Support for text, images, and price offers
 */

import { NestFactory, Reflector } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';
import { ThrottlerGuard } from '@nestjs/throttler';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Global validation pipe
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      transform: true,
      forbidNonWhitelisted: true,
    }),
  );

  // Global rate limiting guard
  const reflector = app.get(Reflector);
  app.useGlobalGuards(new ThrottlerGuard({ reflector }));

  // CORS - Secure configuration using environment variable
  const allowedOrigins = process.env.CORS_ALLOWED_ORIGINS?.split(',') || [
    'https://sahool.com',
    'https://app.sahool.com',
    'https://admin.sahool.com',
    'http://localhost:3000',
    'http://localhost:8080',
  ];

  app.enableCors({
    origin: allowedOrigins,
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Tenant-ID', 'X-Request-ID'],
    credentials: true,
  });

  // Global prefix
  app.setGlobalPrefix('api/v1');

  // Swagger/OpenAPI Documentation
  const config = new DocumentBuilder()
    .setTitle('SAHOOL Chat Service API')
    .setDescription(`
      خدمة المحادثات للسوق الزراعي

      ## Features
      - **Real-time Messaging**: Socket.IO WebSocket for instant communication
      - **Buyer-Seller Chat**: Direct messaging between buyers and sellers
      - **Product Context**: Link conversations to specific products
      - **Order Integration**: Associate chats with marketplace orders
      - **Rich Messages**: Support text, images, and price offers
      - **Read Receipts**: Track message delivery and read status
      - **Typing Indicators**: Real-time typing notifications
      - **Online Status**: Track user presence

      ## WebSocket Events
      - \`join_conversation\` - Join a conversation room
      - \`send_message\` - Send a message to conversation
      - \`message_received\` - Receive new messages
      - \`typing\` - Send/receive typing indicators
      - \`read_receipt\` - Mark messages as read
      - \`user_online\` - User online status
      - \`user_offline\` - User offline status
    `)
    .setVersion('16.0.0')
    .addTag('Chat', 'Chat conversation management')
    .addTag('Messages', 'Message operations')
    .addBearerAuth()
    .addApiKey({ type: 'apiKey', name: 'X-Tenant-ID', in: 'header' }, 'tenant-id')
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('docs', app, document);

  const port = process.env.PORT || 8114;
  await app.listen(port);

  console.log(`
  ╔═══════════════════════════════════════════════════════════════╗
  ║   💬 SAHOOL Chat Service v16.0.0                              ║
  ║   خدمة المحادثات للسوق الزراعي                                ║
  ╠═══════════════════════════════════════════════════════════════╣
  ║   Server running on: http://localhost:${port}                   ║
  ║   API Documentation: http://localhost:${port}/docs             ║
  ║   WebSocket Gateway: ws://localhost:${port}                    ║
  ╚═══════════════════════════════════════════════════════════════╝
  `);
}

bootstrap();
