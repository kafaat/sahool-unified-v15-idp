import { Module } from "@nestjs/common";
import { PrismaService } from "@/config/prisma.service";

@Module({
  providers: [PrismaService],
  exports: [],
})
export class PlotsModule {}
