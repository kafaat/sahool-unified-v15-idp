/**
 * Field KPI Snapshot Service
 * خدمة لقطات KPI للحقول — Sentinel Hub + OpenWeather
 */

import { Injectable, NotFoundException } from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import { IsNumber, IsOptional, IsString } from "class-validator";
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

  @ApiProperty({ required: false })
  @IsOptional()
  @IsString()
  weatherCondition?: string;

  @ApiProperty({ required: false })
  @IsOptional()
  @IsString()
  weatherConditionAr?: string;

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
  constructor(private readonly prisma: PrismaService) {}

  /**
   * Get the latest KPI snapshot for a field
   * جلب أحدث لقطة KPI للحقل
   */
  async getLatest(fieldId: string, tenantId: string) {
    // Verify field belongs to tenant
    const field = await this.prisma.field.findFirst({
      where: { id: fieldId, tenantId, deletedAt: null },
      select: { id: true },
    });
    if (!field) {
      throw new NotFoundException(`Field ${fieldId} not found`);
    }

    const snapshot = await (this.prisma as any).fieldKpiSnapshot.findFirst({
      where: { fieldId },
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
      where: { id: fieldId, tenantId, deletedAt: null },
      select: { id: true },
    });
    if (!field) {
      throw new NotFoundException(`Field ${fieldId} not found`);
    }

    // Create snapshot
    const snapshot = await (this.prisma as any).fieldKpiSnapshot.create({
      data: {
        fieldId,
        tenantId,
        ndvi: dto.ndvi != null ? dto.ndvi : undefined,
        evi: dto.evi != null ? dto.evi : undefined,
        ndwi: dto.ndwi != null ? dto.ndwi : undefined,
        savi: dto.savi != null ? dto.savi : undefined,
        lai: dto.lai != null ? dto.lai : undefined,
        ndmi: dto.ndmi != null ? dto.ndmi : undefined,
        temperature: dto.temperature != null ? dto.temperature : undefined,
        humidity: dto.humidity != null ? dto.humidity : undefined,
        windSpeed: dto.windSpeed != null ? dto.windSpeed : undefined,
        precipitation: dto.precipitation != null ? dto.precipitation : undefined,
        uvIndex: dto.uvIndex != null ? dto.uvIndex : undefined,
        weatherCondition: dto.weatherCondition,
        weatherConditionAr: dto.weatherConditionAr,
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
    }

    return snapshot;
  }
}
