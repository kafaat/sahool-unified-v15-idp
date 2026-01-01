/**
 * Reviews Module
 * وحدة تقييمات المنتجات
 */

import { Module } from '@nestjs/common';
import { ReviewsService } from './reviews.service';
import { ReviewsController } from './reviews.controller';
import { PrismaService } from '../prisma/prisma.service';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';

@Module({
  controllers: [ReviewsController],
  providers: [ReviewsService, PrismaService, JwtAuthGuard],
  exports: [ReviewsService],
})
export class ReviewsModule {}
