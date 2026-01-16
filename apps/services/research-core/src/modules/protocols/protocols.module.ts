import { Module } from "@nestjs/common";
import { ProtocolsController } from "./protocols.controller";
import { ProtocolsService } from "./protocols.service";
import { PrismaService } from "@/config/prisma.service";

@Module({
  controllers: [ProtocolsController],
  providers: [ProtocolsService, PrismaService],
  exports: [ProtocolsService],
})
export class ProtocolsModule {}
