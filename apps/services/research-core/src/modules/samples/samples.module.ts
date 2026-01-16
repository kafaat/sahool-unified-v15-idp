import { Module } from "@nestjs/common";
import { SamplesController } from "./samples.controller";
import { SamplesService } from "./samples.service";
import { PrismaService } from "@/config/prisma.service";

@Module({
  controllers: [SamplesController],
  providers: [SamplesService, PrismaService],
  exports: [SamplesService],
})
export class SamplesModule {}
