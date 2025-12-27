/**
 * SAHOOL IoT Service - App Module
 */

import { Module } from '@nestjs/common';
import { IotModule } from './iot/iot.module';
import { HealthController } from './health/health.controller';

@Module({
  imports: [IotModule],
  controllers: [HealthController],
})
export class AppModule {}
