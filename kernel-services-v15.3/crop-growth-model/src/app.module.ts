import { Module } from '@nestjs/common';
import { PhenologyController } from './phenology/phenology.controller';
import { PhenologyService } from './phenology/phenology.service';
import { PhotosynthesisController } from './photosynthesis/photosynthesis.controller';
import { PhotosynthesisService } from './photosynthesis/photosynthesis.service';
import { BiomassController } from './biomass/biomass.controller';
import { BiomassService } from './biomass/biomass.service';
import { GrowthSimulationController } from './simulation/simulation.controller';
import { GrowthSimulationService } from './simulation/simulation.service';

@Module({
  controllers: [
    PhenologyController,
    PhotosynthesisController,
    BiomassController,
    GrowthSimulationController,
  ],
  providers: [
    PhenologyService,
    PhotosynthesisService,
    BiomassService,
    GrowthSimulationService,
  ],
})
export class AppModule {}
