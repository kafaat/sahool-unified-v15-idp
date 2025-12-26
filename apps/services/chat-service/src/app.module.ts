/**
 * SAHOOL Chat Service App Module
 * وحدة التطبيق الرئيسية
 */

import { Module } from '@nestjs/common';
import { PrismaService } from './prisma/prisma.service';
import { ChatGateway } from './chat/chat.gateway';
import { ChatService } from './chat/chat.service';
import { ChatController } from './chat/chat.controller';

@Module({
  imports: [],
  controllers: [ChatController],
  providers: [PrismaService, ChatService, ChatGateway],
})
export class AppModule {}
