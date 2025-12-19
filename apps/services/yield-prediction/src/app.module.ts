import { Module } from '@nestjs/common';
import { YieldController } from './yield/yield.controller';
import { YieldService } from './yield/yield.service';

@Module({
  controllers: [YieldController],
  providers: [YieldService],
})
export class AppModule {}
