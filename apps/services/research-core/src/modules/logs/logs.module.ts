import { Module } from "@nestjs/common";
import { LogsController } from "./logs.controller";
import { LogsService } from "./logs.service";
import { PrismaService } from "@/config/prisma.service";
import { SignatureService } from "@/core/services/signature.service";

@Module({
  controllers: [LogsController],
  providers: [LogsService, PrismaService, SignatureService],
  exports: [LogsService],
})
export class LogsModule {}
