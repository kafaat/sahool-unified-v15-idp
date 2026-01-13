/**
 * Prisma Module - Database Module
 * وحدة قاعدة البيانات
 */

import { Module, Global } from "@nestjs/common";
import { PrismaService } from "./prisma.service";

@Global()
@Module({
  providers: [PrismaService],
  exports: [PrismaService],
})
export class PrismaModule {}
