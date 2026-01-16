import { Module } from "@nestjs/common";
import { TreatmentsController } from "./treatments.controller";
import { TreatmentsService } from "./treatments.service";
import { PrismaService } from "@/config/prisma.service";

@Module({
  controllers: [TreatmentsController],
  providers: [TreatmentsService, PrismaService],
  exports: [TreatmentsService],
})
export class TreatmentsModule {}
