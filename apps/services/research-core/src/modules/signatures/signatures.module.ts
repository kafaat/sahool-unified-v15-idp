import { Module } from "@nestjs/common";
import { SignaturesController } from "./signatures.controller";
import { SignaturesService } from "./signatures.service";
import { PrismaService } from "@/config/prisma.service";
import { SignatureService } from "@/core/services/signature.service";

@Module({
  controllers: [SignaturesController],
  providers: [SignaturesService, PrismaService, SignatureService],
  exports: [SignaturesService],
})
export class SignaturesModule {}
