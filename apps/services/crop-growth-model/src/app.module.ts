import { Module } from '@nestjs/common';
import { APP_GUARD } from '@nestjs/core';
import { ThrottlerModule, ThrottlerGuard } from '@nestjs/throttler';
import { PhenologyController } from './phenology/phenology.controller';
import { PhenologyService } from './phenology/phenology.service';
import { PhotosynthesisController } from './photosynthesis/photosynthesis.controller';
import { PhotosynthesisService } from './photosynthesis/photosynthesis.service';
import { BiomassController } from './biomass/biomass.controller';
import { BiomassService } from './biomass/biomass.service';
import { GrowthSimulationController } from './simulation/simulation.controller';
import { GrowthSimulationService } from './simulation/simulation.service';
import { RootGrowthController } from './root-growth/root-growth.controller';
import { RootGrowthService } from './root-growth/root-growth.service';
import { WaterBalanceController } from './water-balance/water-balance.controller';
import { WaterBalanceService } from './water-balance/water-balance.service';
import { SatelliteDataController } from './satellite-data/satellite-data.controller';
import { SatelliteDataService } from './satellite-data/satellite-data.service';
import { IrrigationDecisionController } from './irrigation-decision/irrigation-decision.controller';
import { IrrigationDecisionService } from './irrigation-decision/irrigation-decision.service';
import { MultiAgentAdvisorController } from './multi-agent-advisor/multi-agent-advisor.controller';
import { MultiAgentAdvisorService } from './multi-agent-advisor/multi-agent-advisor.service';
import { VoiceGuidanceController } from './voice-guidance/voice-guidance.controller';
import { VoiceGuidanceService } from './voice-guidance/voice-guidance.service';
import { WebDataCollectorController } from './web-data-collector/web-data-collector.controller';
import { WebDataCollectorService } from './web-data-collector/web-data-collector.service';
import { DigitalTwinCoreController } from './digital-twin-core/digital-twin-core.controller';
import { DigitalTwinCoreService } from './digital-twin-core/digital-twin-core.service';
import { RSWorldModelController } from './rs-world-model/rs-world-model.controller';
import { RSWorldModelService } from './rs-world-model/rs-world-model.service';
import { PlantingStrategyController } from './planting-strategy/planting-strategy.controller';
import { PlantingStrategyService } from './planting-strategy/planting-strategy.service';
import { GISIntegrationController } from './gis-integration/gis-integration.controller';
import { GISIntegrationService } from './gis-integration/gis-integration.service';

@Module({
  imports: [
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
  ],
  controllers: [
    PhenologyController,
    PhotosynthesisController,
    BiomassController,
    GrowthSimulationController,
    RootGrowthController,
    WaterBalanceController,
    SatelliteDataController,
    IrrigationDecisionController,
    MultiAgentAdvisorController,
    VoiceGuidanceController,
    WebDataCollectorController,
    DigitalTwinCoreController,
    RSWorldModelController,
    PlantingStrategyController,
    GISIntegrationController,
  ],
  providers: [
    PhenologyService,
    PhotosynthesisService,
    BiomassService,
    GrowthSimulationService,
    RootGrowthService,
    WaterBalanceService,
    SatelliteDataService,
    IrrigationDecisionService,
    MultiAgentAdvisorService,
    VoiceGuidanceService,
    WebDataCollectorService,
    DigitalTwinCoreService,
    RSWorldModelService,
    PlantingStrategyService,
    GISIntegrationService,
    // Global rate limiting guard
    {
      provide: APP_GUARD,
      useClass: ThrottlerGuard,
    },
  ],
})
export class AppModule {}
