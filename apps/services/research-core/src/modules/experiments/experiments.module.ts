import { Module } from '@nestjs/common';
import { ExperimentsController } from './experiments.controller';
import { ExperimentsService } from './experiments.service';
import { PrismaService } from '@/config/prisma.service';

@Module({
  controllers: [ExperimentsController],
  providers: [ExperimentsService, PrismaService],
  exports: [ExperimentsService],
})
export class ExperimentsModule {}
