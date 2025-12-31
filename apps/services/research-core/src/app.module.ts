import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { APP_GUARD } from '@nestjs/core';
import { ThrottlerModule, ThrottlerGuard } from '@nestjs/throttler';
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
    // Rate limiting configuration
    ThrottlerModule.forRoot([
      {
        name: 'short',
        ttl: 1000, // 1 second
        limit: 10, // 10 requests per second
      },
      {
        name: 'medium',
        ttl: 60000, // 1 minute
        limit: 100, // 100 requests per minute
      },
      {
        name: 'long',
        ttl: 3600000, // 1 hour
        limit: 1000, // 1000 requests per hour
      },
    ]),
    ExperimentsModule,
    ProtocolsModule,
    PlotsModule,
    TreatmentsModule,
    LogsModule,
    SamplesModule,
    SignaturesModule,
  ],
  controllers: [HealthController],
  providers: [
    PrismaService,
    SignatureService,
    ScientificLockGuard,
    // Global rate limiting guard
    {
      provide: APP_GUARD,
      useClass: ThrottlerGuard,
    },
  ],
  exports: [PrismaService, SignatureService, ScientificLockGuard],
})
export class AppModule {}
