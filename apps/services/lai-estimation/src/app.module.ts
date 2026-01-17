import { Module } from "@nestjs/common";
import { LAIController } from "./lai/lai.controller";
import { LAIService } from "./lai/lai.service";
import { VegetationIndicesController } from "./indices/indices.controller";
import { VegetationIndicesService } from "./indices/indices.service";

@Module({
  controllers: [LAIController, VegetationIndicesController],
  providers: [LAIService, VegetationIndicesService],
})
export class AppModule {}
