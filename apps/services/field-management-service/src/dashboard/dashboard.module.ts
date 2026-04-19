import { Module } from "@nestjs/common";
import { DashboardController } from "./dashboard.controller";

// PrismaService is re-exported globally by PrismaModule, so we don't
// need to list it in `providers` here.
@Module({
  controllers: [DashboardController],
})
export class DashboardModule {}
