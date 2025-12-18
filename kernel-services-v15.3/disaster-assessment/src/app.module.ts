// ═══════════════════════════════════════════════════════════════════════════════
// Disaster Assessment App Module
// ═══════════════════════════════════════════════════════════════════════════════

import { Module } from '@nestjs/common';
import { DisasterController } from './disaster/disaster.controller';
import { DisasterService } from './disaster/disaster.service';
import { AlertController } from './alert/alert.controller';
import { AlertService } from './alert/alert.service';

@Module({
  imports: [],
  controllers: [DisasterController, AlertController],
  providers: [DisasterService, AlertService],
})
export class AppModule {}
