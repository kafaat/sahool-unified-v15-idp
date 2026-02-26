import { Module } from "@nestjs/common";
import { APP_GUARD } from "@nestjs/core";
import { AuthModule, TenantGuard } from "@sahool/nestjs-auth";
import { HealthController } from "./health/health.controller";
import { LAIController } from "./lai/lai.controller";
import { LAIService } from "./lai/lai.service";
import { VegetationIndicesController } from "./indices/indices.controller";
import { VegetationIndicesService } from "./indices/indices.service";

@Module({
  imports: [
    // Shared JWT authentication (replaces local custom guard)
    AuthModule.forRoot({
      enableUserValidation: false,
      enableTokenRevocation: false,
    }),
  ],
  controllers: [HealthController, LAIController, VegetationIndicesController],
  providers: [
    LAIService,
    VegetationIndicesService,
    // Global tenant isolation guard
    {
      provide: APP_GUARD,
      useClass: TenantGuard,
    },
  ],
})
export class AppModule {}
