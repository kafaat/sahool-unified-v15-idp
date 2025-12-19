/**
 * SAHOOL Marketplace App Module
 * وحدة التطبيق الرئيسية
 */

import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { PrismaService } from './prisma/prisma.service';
import { MarketService } from './market/market.service';
import { FintechService } from './fintech/fintech.service';

@Module({
  imports: [],
  controllers: [AppController],
  providers: [PrismaService, MarketService, FintechService],
})
export class AppModule {}
