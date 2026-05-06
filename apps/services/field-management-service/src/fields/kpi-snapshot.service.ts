/**
 * Field KPI Snapshot Service
 * خدمة لقطات KPI للحقول — Sentinel Hub + OpenWeather
 */

import { Injectable, NotFoundException } from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import { CacheService, CACHE_KEYS } from "../cache/cache.service";
import { IsInt, IsNumber, IsOptional, IsString } from "class-validator";
import { ApiProperty } from "@nestjs/swagger";

export class CreateKpiSnapshotDto {
  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  ndvi?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  evi?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  ndwi?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  savi?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  lai?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  ndmi?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  temperature?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  humidity?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  windSpeed?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  precipitation?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  uvIndex?: number;

  // ── Vegetation extras
  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  gndvi?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  ndre?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  msavi?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  osavi?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  evi2?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  cvi?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  mcari?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  tcari?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  wdrvi?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  vari?: number;

  // ── Water indices
  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  mndwi?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  turbidity?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  chlorophyll?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  phycocyanin?: number;

  // ── Soil / Bare land
  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  bsi?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  nbsi?: number;

  // ── Fire / Burn
  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  nbr?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  nbr2?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  bais2?: number;

  // ── Urban / Built-up
  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  ndbi?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  ibi?: number;

  // ── Snow / Ice
  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  ndsi?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  ndgi?: number;

  // ── Atmosphere
  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  lst?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  cloudProbability?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  arvi?: number;

  // ── Weather extras
  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  windDirection?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  pressure?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  cloudCover?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  visibility?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsString()
  weatherCondition?: string;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsString()
  weatherConditionAr?: string;

  // ── Air quality
  @ApiProperty({ required: false })
  @IsOptional()
  @IsInt()
  aqi?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  co?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  no?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  no2?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  o3?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  so2?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  nh3?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  pm25?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  pm10?: number;

  // ── Solar irradiance
  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  ghiClearSky?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  dniClearSky?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  dhiClearSky?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  ghiCloudy?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  dniCloudy?: number;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsNumber()
  dhiCloudy?: number;

  // ── Metadata
  @ApiProperty({ required: false })
  @IsOptional()
  @IsString()
  satelliteSource?: string;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsString()
  weatherSource?: string;
}

@Injectable()
export class KpiSnapshotService {
  constructor(
    private readonly prisma: PrismaService,
    private readonly cacheService: CacheService,
  ) {}

  /**
   * Get the latest KPI snapshot for a field
   * جلب أحدث لقطة KPI للحقل
   */
  async getLatest(fieldId: string, tenantId: string) {
    // Verify field belongs to tenant
    const field = await this.prisma.field.findFirst({
      where: { id: fieldId, tenantId, isDeleted: false },
      select: { id: true },
    });
    if (!field) {
      throw new NotFoundException(`Field ${fieldId} not found`);
    }

    const snapshot = await this.prisma.fieldKpiSnapshot.findFirst({
      where: { fieldId, tenantId },
      orderBy: { fetchedAt: "desc" },
    });

    return snapshot ?? null;
  }

  /**
   * Save a new KPI snapshot and update field ndvi/health
   * حفظ لقطة KPI جديدة وتحديث NDVI وصحة الحقل
   */
  async save(
    fieldId: string,
    tenantId: string,
    dto: CreateKpiSnapshotDto,
  ) {
    // Verify field belongs to tenant
    const field = await this.prisma.field.findFirst({
      where: { id: fieldId, tenantId, isDeleted: false },
      select: { id: true },
    });
    if (!field) {
      throw new NotFoundException(`Field ${fieldId} not found`);
    }

    // Create snapshot
    const snapshot = await this.prisma.fieldKpiSnapshot.create({
      data: {
        fieldId,
        tenantId,
        // Vegetation
        ndvi: dto.ndvi != null ? dto.ndvi : undefined,
        evi: dto.evi != null ? dto.evi : undefined,
        lai: dto.lai != null ? dto.lai : undefined,
        savi: dto.savi != null ? dto.savi : undefined,
        ndmi: dto.ndmi != null ? dto.ndmi : undefined,
        gndvi: dto.gndvi != null ? dto.gndvi : undefined,
        ndre: dto.ndre != null ? dto.ndre : undefined,
        msavi: dto.msavi != null ? dto.msavi : undefined,
        osavi: dto.osavi != null ? dto.osavi : undefined,
        evi2: dto.evi2 != null ? dto.evi2 : undefined,
        cvi: dto.cvi != null ? dto.cvi : undefined,
        mcari: dto.mcari != null ? dto.mcari : undefined,
        tcari: dto.tcari != null ? dto.tcari : undefined,
        wdrvi: dto.wdrvi != null ? dto.wdrvi : undefined,
        vari: dto.vari != null ? dto.vari : undefined,
        // Water
        ndwi: dto.ndwi != null ? dto.ndwi : undefined,
        mndwi: dto.mndwi != null ? dto.mndwi : undefined,
        turbidity: dto.turbidity != null ? dto.turbidity : undefined,
        chlorophyll: dto.chlorophyll != null ? dto.chlorophyll : undefined,
        phycocyanin: dto.phycocyanin != null ? dto.phycocyanin : undefined,
        // Soil
        bsi: dto.bsi != null ? dto.bsi : undefined,
        nbsi: dto.nbsi != null ? dto.nbsi : undefined,
        // Fire / Burn
        nbr: dto.nbr != null ? dto.nbr : undefined,
        nbr2: dto.nbr2 != null ? dto.nbr2 : undefined,
        bais2: dto.bais2 != null ? dto.bais2 : undefined,
        // Urban
        ndbi: dto.ndbi != null ? dto.ndbi : undefined,
        ibi: dto.ibi != null ? dto.ibi : undefined,
        // Snow / Ice
        ndsi: dto.ndsi != null ? dto.ndsi : undefined,
        ndgi: dto.ndgi != null ? dto.ndgi : undefined,
        // Atmosphere
        lst: dto.lst != null ? dto.lst : undefined,
        cloudProbability: dto.cloudProbability != null ? dto.cloudProbability : undefined,
        arvi: dto.arvi != null ? dto.arvi : undefined,
        // Weather
        temperature: dto.temperature != null ? dto.temperature : undefined,
        humidity: dto.humidity != null ? dto.humidity : undefined,
        windSpeed: dto.windSpeed != null ? dto.windSpeed : undefined,
        windDirection: dto.windDirection != null ? dto.windDirection : undefined,
        precipitation: dto.precipitation != null ? dto.precipitation : undefined,
        pressure: dto.pressure != null ? dto.pressure : undefined,
        cloudCover: dto.cloudCover != null ? dto.cloudCover : undefined,
        visibility: dto.visibility != null ? dto.visibility : undefined,
        uvIndex: dto.uvIndex != null ? dto.uvIndex : undefined,
        weatherCondition: dto.weatherCondition,
        weatherConditionAr: dto.weatherConditionAr,
        // Air quality
        aqi: dto.aqi != null ? dto.aqi : undefined,
        co: dto.co != null ? dto.co : undefined,
        no: dto.no != null ? dto.no : undefined,
        no2: dto.no2 != null ? dto.no2 : undefined,
        o3: dto.o3 != null ? dto.o3 : undefined,
        so2: dto.so2 != null ? dto.so2 : undefined,
        nh3: dto.nh3 != null ? dto.nh3 : undefined,
        pm25: dto.pm25 != null ? dto.pm25 : undefined,
        pm10: dto.pm10 != null ? dto.pm10 : undefined,
        // Solar
        ghiClearSky: dto.ghiClearSky != null ? dto.ghiClearSky : undefined,
        dniClearSky: dto.dniClearSky != null ? dto.dniClearSky : undefined,
        dhiClearSky: dto.dhiClearSky != null ? dto.dhiClearSky : undefined,
        ghiCloudy: dto.ghiCloudy != null ? dto.ghiCloudy : undefined,
        dniCloudy: dto.dniCloudy != null ? dto.dniCloudy : undefined,
        dhiCloudy: dto.dhiCloudy != null ? dto.dhiCloudy : undefined,
        // Metadata
        satelliteSource: dto.satelliteSource,
        weatherSource: dto.weatherSource,
      },
    });

    // Update field ndvi_value and health_score from ndvi
    if (dto.ndvi != null) {
      await this.prisma.field.update({
        where: { id: fieldId },
        data: {
          ndviValue: dto.ndvi,
          healthScore: dto.ndvi, // Use NDVI as health proxy
          updatedAt: new Date(),
        },
      });
      // Invalidate service-level cache and HTTP interceptor cache keys
      await this.cacheService.del(CACHE_KEYS.FIELD(fieldId));
      // HTTP interceptor key format: {tenantId}:{path}:{hash("{}") = "31e"}
      await this.cacheService.del(`${tenantId}:/api/v1/fields/${fieldId}:31e`);
      await this.cacheService.del(`${tenantId}:/api/v1/fields/${fieldId}/kpi-snapshot:31e`);
    }

    return snapshot;
  }
}
