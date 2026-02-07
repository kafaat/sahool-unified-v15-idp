/**
 * NDVI Module - Vegetation Index Analysis
 */

import { Module } from "@nestjs/common";
import { NdviController } from "./ndvi.controller";
import { NdviService } from "./ndvi.service";

@Module({
  controllers: [NdviController],
  providers: [NdviService],
  exports: [NdviService],
})
export class NdviModule {}
