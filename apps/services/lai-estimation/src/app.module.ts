import { Module } from "@nestjs/common";
import { HealthController } from "./health/health.controller";
import { LAIController } from "./lai/lai.controller";
import { LAIService } from "./lai/lai.service";
import { VegetationIndicesController } from "./indices/indices.controller";
import { VegetationIndicesService } from "./indices/indices.service";

@Module({
  controllers: [HealthController, LAIController, VegetationIndicesController],
  providers: [LAIService, VegetationIndicesService],
})
export class AppModule {}
