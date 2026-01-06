// ═══════════════════════════════════════════════════════════════════════════════
// Disaster Assessment App Module
// ═══════════════════════════════════════════════════════════════════════════════

import { Module } from '@nestjs/common';
import { ThrottlerModule } from '@nestjs/throttler';
import { DisasterController } from './disaster/disaster.controller';
import { DisasterService } from './disaster/disaster.service';
import { AlertController } from './alert/alert.controller';
import { AlertService } from './alert/alert.service';

@Module({
  imports: [
    // Rate limiting configuration
    ThrottlerModule.forRoot([
      {
        name: 'default',
        ttl: 60000, // 1 minute
        limit: 100, // 100 requests per minute
      },
    ]),
  ],
  controllers: [DisasterController, AlertController],
  providers: [DisasterService, AlertService],
})
export class AppModule {}
