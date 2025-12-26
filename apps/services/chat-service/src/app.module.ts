/**
 * SAHOOL Chat Service App Module
 * وحدة التطبيق الرئيسية
 */

import { Module } from '@nestjs/common';
import { PrismaService } from './prisma/prisma.service';
import { ChatGateway } from './chat/chat.gateway';
import { ChatService } from './chat/chat.service';
import { ChatController } from './chat/chat.controller';
import { HealthController } from './health/health.controller';

@Module({
  imports: [],
  controllers: [ChatController, HealthController],
  providers: [PrismaService, ChatService, ChatGateway],
})
export class AppModule {}
