/**
 * Profiles Module
 * وحدة ملفات البائعين والمشترين
 */

import { Module } from '@nestjs/common';
import { ProfilesService } from './profiles.service';
import { SellerProfileController } from './seller-profile.controller';
import { BuyerProfileController } from './buyer-profile.controller';
import { PrismaService } from '../prisma/prisma.service';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';

@Module({
  controllers: [SellerProfileController, BuyerProfileController],
  providers: [ProfilesService, PrismaService, JwtAuthGuard],
  exports: [ProfilesService],
})
export class ProfilesModule {}
