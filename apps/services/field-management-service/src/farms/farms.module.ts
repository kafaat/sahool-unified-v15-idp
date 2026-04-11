/**
 * Farms Module - Farm Management
 * وحدة المزارع
 */

import { Module } from "@nestjs/common";
import { FarmsController } from "./farms.controller";
import { FarmsService } from "./farms.service";

@Module({
  controllers: [FarmsController],
  providers: [FarmsService],
  exports: [FarmsService],
})
export class FarmsModule {}
