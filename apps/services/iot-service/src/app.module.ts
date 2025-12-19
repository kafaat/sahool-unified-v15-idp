/**
 * SAHOOL IoT Service - App Module
 */

import { Module } from '@nestjs/common';
import { IotModule } from './iot/iot.module';

@Module({
  imports: [IotModule],
})
export class AppModule {}
