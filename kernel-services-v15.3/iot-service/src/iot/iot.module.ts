/**
 * SAHOOL IoT Module
 */

import { Module } from '@nestjs/common';
import { IotService } from './iot.service';
import { IotController } from './iot.controller';

@Module({
  providers: [IotService],
  controllers: [IotController],
  exports: [IotService],
})
export class IotModule {}
