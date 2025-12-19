import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { PrismaService } from './config/prisma.service';
import { SignatureService } from './core/services/signature.service';
import { ScientificLockGuard } from './core/guards/scientific-lock.guard';
import { ExperimentsModule } from './modules/experiments/experiments.module';
import { ProtocolsModule } from './modules/protocols/protocols.module';
import { PlotsModule } from './modules/plots/plots.module';
import { TreatmentsModule } from './modules/treatments/treatments.module';
import { LogsModule } from './modules/logs/logs.module';
import { SamplesModule } from './modules/samples/samples.module';
import { SignaturesModule } from './modules/signatures/signatures.module';
import { HealthController } from './health.controller';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: ['.env', '../.env'],
    }),
    ExperimentsModule,
    ProtocolsModule,
    PlotsModule,
    TreatmentsModule,
    LogsModule,
    SamplesModule,
    SignaturesModule,
  ],
  controllers: [HealthController],
  providers: [PrismaService, SignatureService, ScientificLockGuard],
  exports: [PrismaService, SignatureService, ScientificLockGuard],
})
export class AppModule {}
