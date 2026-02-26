import { Module } from "@nestjs/common";
import { APP_GUARD } from "@nestjs/core";
import { TenantGuard } from "@sahool/nestjs-auth";
import { HealthController } from "./health.controller";
import { YieldController } from "./yield/yield.controller";
import { YieldService } from "./yield/yield.service";

@Module({
  controllers: [HealthController, YieldController],
  providers: [
    YieldService,
    // Global tenant isolation guard
    {
      provide: APP_GUARD,
      useClass: TenantGuard,
    },
  ],
})
export class AppModule {}
