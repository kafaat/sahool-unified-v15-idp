// ═══════════════════════════════════════════════════════════════════════════════
// Disaster DTOs - أنواع بيانات الكوارث
// ═══════════════════════════════════════════════════════════════════════════════

import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import {
  IsString,
  IsNumber,
  IsEnum,
  IsOptional,
  IsArray,
  IsDateString,
  Min,
  Max,
  ValidateNested,
} from 'class-validator';
import { Type } from 'class-transformer';

// ─────────────────────────────────────────────────────────────────────────────
// Enums
// ─────────────────────────────────────────────────────────────────────────────

export enum DisasterType {
  FLOOD = 'flood',           // فيضان
  DROUGHT = 'drought',       // جفاف
  FROST = 'frost',           // صقيع
  HAIL = 'hail',             // بَرَد
  STORM = 'storm',           // عاصفة
  PEST = 'pest',             // آفات
  DISEASE = 'disease',       // أمراض
  LOCUST = 'locust',         // جراد
  WILDFIRE = 'wildfire',     // حرائق
}

export enum Severity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

export enum DisasterStatus {
  ACTIVE = 'active',
  MONITORING = 'monitoring',
  RESOLVED = 'resolved',
  ARCHIVED = 'archived',
}

// ─────────────────────────────────────────────────────────────────────────────
// Location DTO
// ─────────────────────────────────────────────────────────────────────────────

export class LocationDto {
  @ApiProperty({ description: 'Latitude', example: 15.3694 })
  @IsNumber()
  @Min(-90)
  @Max(90)
  lat: number;

  @ApiProperty({ description: 'Longitude', example: 44.191 })
  @IsNumber()
  @Min(-180)
  @Max(180)
  lng: number;
}

// ─────────────────────────────────────────────────────────────────────────────
// Create Disaster Report DTO
// ─────────────────────────────────────────────────────────────────────────────

export class CreateDisasterReportDto {
  @ApiProperty({ enum: DisasterType, description: 'نوع الكارثة' })
  @IsEnum(DisasterType)
  type: DisasterType;

  @ApiProperty({ description: 'عنوان الكارثة', example: 'فيضان وادي حضرموت' })
  @IsString()
  title: string;

  @ApiPropertyOptional({ description: 'وصف تفصيلي' })
  @IsOptional()
  @IsString()
  description?: string;

  @ApiProperty({ description: 'المحافظة', example: 'hadramaut' })
  @IsString()
  governorate: string;

  @ApiPropertyOptional({ description: 'المديرية' })
  @IsOptional()
  @IsString()
  district?: string;

  @ApiProperty({ type: LocationDto, description: 'موقع الكارثة' })
  @ValidateNested()
  @Type(() => LocationDto)
  location: LocationDto;

  @ApiPropertyOptional({ description: 'نصف قطر التأثير بالكيلومتر', example: 10 })
  @IsOptional()
  @IsNumber()
  @Min(0)
  affectedRadiusKm?: number;

  @ApiProperty({ enum: Severity, description: 'شدة الكارثة' })
  @IsEnum(Severity)
  severity: Severity;

  @ApiPropertyOptional({ description: 'تاريخ بدء الكارثة' })
  @IsOptional()
  @IsDateString()
  startDate?: string;

  @ApiPropertyOptional({ description: 'صور موثقة', type: [String] })
  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  images?: string[];

  @ApiPropertyOptional({ description: 'معرف المُبلّغ' })
  @IsOptional()
  @IsString()
  reportedBy?: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// Disaster Assessment DTO
// ─────────────────────────────────────────────────────────────────────────────

export class DisasterAssessmentDto {
  @ApiProperty({ description: 'معرف الكارثة' })
  @IsString()
  disasterId: string;

  @ApiPropertyOptional({ description: 'نسبة الضرر المقدرة (0-100)', example: 45 })
  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(100)
  damagePercentage?: number;

  @ApiPropertyOptional({ description: 'المساحة المتضررة بالهكتار', example: 25.5 })
  @IsOptional()
  @IsNumber()
  @Min(0)
  affectedAreaHectares?: number;

  @ApiPropertyOptional({ description: 'الخسائر المقدرة بالريال', example: 500000 })
  @IsOptional()
  @IsNumber()
  @Min(0)
  estimatedLossYER?: number;

  @ApiPropertyOptional({ description: 'نوع المحصول المتضرر' })
  @IsOptional()
  @IsString()
  affectedCropType?: string;

  @ApiPropertyOptional({ description: 'ملاحظات التقييم' })
  @IsOptional()
  @IsString()
  assessmentNotes?: string;

  @ApiPropertyOptional({ description: 'صور التقييم', type: [String] })
  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  assessmentImages?: string[];
}

// ─────────────────────────────────────────────────────────────────────────────
// Response DTOs
// ─────────────────────────────────────────────────────────────────────────────

export class DisasterResponseDto {
  @ApiProperty()
  id: string;

  @ApiProperty({ enum: DisasterType })
  type: DisasterType;

  @ApiProperty()
  title: string;

  @ApiProperty()
  titleAr: string;

  @ApiPropertyOptional()
  description?: string;

  @ApiProperty()
  governorate: string;

  @ApiProperty()
  governorateAr: string;

  @ApiProperty({ type: LocationDto })
  location: LocationDto;

  @ApiProperty({ enum: Severity })
  severity: Severity;

  @ApiProperty({ enum: DisasterStatus })
  status: DisasterStatus;

  @ApiProperty()
  affectedFieldsCount: number;

  @ApiProperty()
  totalAffectedAreaHectares: number;

  @ApiProperty()
  totalEstimatedLossYER: number;

  @ApiProperty()
  startDate: string;

  @ApiPropertyOptional()
  endDate?: string;

  @ApiProperty()
  createdAt: string;

  @ApiProperty()
  updatedAt: string;
}

export class DamageAssessmentResultDto {
  @ApiProperty()
  fieldId: string;

  @ApiProperty()
  disasterId: string;

  @ApiProperty()
  damagePercentage: number;

  @ApiProperty()
  damageLevel: string;

  @ApiProperty()
  damageLevelAr: string;

  @ApiProperty()
  affectedAreaHectares: number;

  @ApiProperty()
  estimatedLossYER: number;

  @ApiProperty()
  recommendedActions: string[];

  @ApiProperty()
  recommendedActionsAr: string[];

  @ApiProperty()
  insuranceEligible: boolean;

  @ApiProperty()
  assessedAt: string;
}
