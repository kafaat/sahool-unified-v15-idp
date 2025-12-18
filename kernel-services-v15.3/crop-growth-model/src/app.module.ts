import { Module } from '@nestjs/common';
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

@Module({
  controllers: [
    PhenologyController,
    PhotosynthesisController,
    BiomassController,
    GrowthSimulationController,
    RootGrowthController,
    WaterBalanceController,
  ],
  providers: [
    PhenologyService,
    PhotosynthesisService,
    BiomassService,
    GrowthSimulationService,
    RootGrowthService,
    WaterBalanceService,
  ],
})
export class AppModule {}
