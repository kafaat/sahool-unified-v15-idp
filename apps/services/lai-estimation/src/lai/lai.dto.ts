// ═══════════════════════════════════════════════════════════════════════════════
// LAI DTOs - أنماط البيانات لمؤشر مساحة الأوراق
// ═══════════════════════════════════════════════════════════════════════════════

import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";
import {
  IsString,
  IsNumber,
  IsOptional,
  IsEnum,
  IsArray,
  Min,
  Max,
} from "class-validator";

// ─────────────────────────────────────────────────────────────────────────────
// Enums
// ─────────────────────────────────────────────────────────────────────────────

export enum DataSource {
  UAV = "UAV", // الطائرات بدون طيار
  PLANETSCOPE = "PLANETSCOPE", // PlanetScope (3m)
  SENTINEL2 = "SENTINEL2", // Sentinel-2 (10m)
  LANDSAT = "LANDSAT", // Landsat (30m)
  FUSION = "FUSION", // Multi-source fusion
}

export enum CropType {
  SOYBEAN = "SOYBEAN", // فول الصويا
  WHEAT = "WHEAT", // القمح
  CORN = "CORN", // الذرة
  RICE = "RICE", // الأرز
  COTTON = "COTTON", // القطن
  COFFEE = "COFFEE", // البن
  SORGHUM = "SORGHUM", // الذرة الرفيعة
}

export enum GrowthStage {
  EMERGENCE = "EMERGENCE", // الإنبات
  VEGETATIVE = "VEGETATIVE", // النمو الخضري
  FLOWERING = "FLOWERING", // الإزهار
  POD_DEVELOPMENT = "POD_DEVELOPMENT", // تطور القرون
  MATURITY = "MATURITY", // النضج
}

// ─────────────────────────────────────────────────────────────────────────────
// Request DTOs
// ─────────────────────────────────────────────────────────────────────────────

export class EstimateLAIDto {
  @ApiProperty({ description: "Field ID" })
  @IsString()
  fieldId: string;

  @ApiPropertyOptional({ enum: DataSource, default: DataSource.FUSION })
  @IsEnum(DataSource)
  @IsOptional()
  dataSource?: DataSource;

  @ApiPropertyOptional({ enum: CropType })
  @IsEnum(CropType)
  @IsOptional()
  cropType?: CropType;

  @ApiPropertyOptional({ description: "Date for LAI estimation (ISO format)" })
  @IsString()
  @IsOptional()
  date?: string;
}

export class SpectralBandsDto {
  @ApiProperty({ description: "Green band reflectance (0-1)" })
  @IsNumber()
  @Min(0)
  @Max(1)
  green: number;

  @ApiProperty({ description: "Red band reflectance (0-1)" })
  @IsNumber()
  @Min(0)
  @Max(1)
  red: number;

  @ApiProperty({ description: "Red Edge band reflectance (0-1)" })
  @IsNumber()
  @Min(0)
  @Max(1)
  redEdge: number;

  @ApiProperty({ description: "Near-Infrared band reflectance (0-1)" })
  @IsNumber()
  @Min(0)
  @Max(1)
  nir: number;
}

export class CalculateLAIFromBandsDto {
  @ApiProperty({ type: SpectralBandsDto })
  bands: SpectralBandsDto;

  @ApiPropertyOptional({ enum: CropType })
  @IsEnum(CropType)
  @IsOptional()
  cropType?: CropType;

  @ApiPropertyOptional({ enum: GrowthStage })
  @IsEnum(GrowthStage)
  @IsOptional()
  growthStage?: GrowthStage;
}

export class TimeSeriesLAIDto {
  @ApiProperty({ description: "Field ID" })
  @IsString()
  fieldId: string;

  @ApiPropertyOptional({ description: "Start date (ISO format)" })
  @IsString()
  @IsOptional()
  startDate?: string;

  @ApiPropertyOptional({ description: "End date (ISO format)" })
  @IsString()
  @IsOptional()
  endDate?: string;

  @ApiPropertyOptional({ enum: DataSource })
  @IsEnum(DataSource)
  @IsOptional()
  dataSource?: DataSource;
}

// ─────────────────────────────────────────────────────────────────────────────
// Response DTOs
// ─────────────────────────────────────────────────────────────────────────────

export class LAIEstimationResult {
  @ApiProperty({ description: "Leaf Area Index value (m²/m²)" })
  lai: number;

  @ApiProperty({ description: "LAI Arabic label" })
  laiAr: string;

  @ApiProperty({ description: "Confidence score (0-1)" })
  confidence: number;

  @ApiProperty({ description: "Model used for estimation" })
  model: string;

  @ApiProperty({ description: "Data source used" })
  dataSource: DataSource;

  @ApiProperty({ description: "Estimation date" })
  date: string;

  @ApiProperty({ description: "Vegetation indices used" })
  indices: {
    ndvi: number;
    evi2: number;
    gndvi: number;
    savi: number;
  };

  @ApiProperty({ description: "Quality metrics" })
  quality: {
    cloudCover: number;
    pixelPurity: number;
    r2: number;
    rmse: number;
  };
}

export class LAITimeSeriesPoint {
  @ApiProperty()
  date: string;

  @ApiProperty()
  lai: number;

  @ApiProperty()
  confidence: number;

  @ApiProperty()
  dataSource: string;
}

export class LAIComparisonResult {
  @ApiProperty()
  fieldId: string;

  @ApiProperty()
  currentLAI: number;

  @ApiProperty()
  optimalLAI: number;

  @ApiProperty()
  deviation: number;

  @ApiProperty()
  recommendation: string;

  @ApiProperty()
  recommendationAr: string;
}
