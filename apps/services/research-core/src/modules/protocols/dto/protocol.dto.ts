import { ApiProperty, ApiPropertyOptional, PartialType } from '@nestjs/swagger';
import {
  IsString,
  IsOptional,
  IsArray,
  IsObject,
  IsUUID,
  IsInt,
  Min,
  IsDateString,
} from 'class-validator';

export class CreateProtocolDto {
  @ApiProperty({ description: 'Experiment ID' })
  @IsUUID()
  experimentId: string;

  @ApiProperty({ description: 'Protocol name' })
  @IsString()
  name: string;

  @ApiPropertyOptional({ description: 'Arabic name' })
  @IsString()
  @IsOptional()
  nameAr?: string;

  @ApiPropertyOptional({ description: 'Description' })
  @IsString()
  @IsOptional()
  description?: string;

  @ApiPropertyOptional({ description: 'Arabic description' })
  @IsString()
  @IsOptional()
  descriptionAr?: string;

  @ApiProperty({ description: 'Methodology details' })
  @IsString()
  methodology: string;

  @ApiPropertyOptional({ description: 'Arabic methodology' })
  @IsString()
  @IsOptional()
  methodologyAr?: string;

  @ApiPropertyOptional({ description: 'Variables as JSON object' })
  @IsObject()
  @IsOptional()
  variables?: Record<string, unknown>;

  @ApiPropertyOptional({ description: 'Measurement schedule as JSON object' })
  @IsObject()
  @IsOptional()
  measurementSchedule?: Record<string, unknown>;

  @ApiPropertyOptional({ description: 'Required equipment list' })
  @IsArray()
  @IsString({ each: true })
  @IsOptional()
  equipmentRequired?: string[];

  @ApiPropertyOptional({ description: 'Safety guidelines' })
  @IsString()
  @IsOptional()
  safetyGuidelines?: string;

  @ApiPropertyOptional({ description: 'Version number' })
  @IsInt()
  @Min(1)
  @IsOptional()
  version?: number;

  @ApiPropertyOptional({ description: 'Approved by user ID' })
  @IsString()
  @IsOptional()
  approvedBy?: string;

  @ApiPropertyOptional({ description: 'Approval date' })
  @IsDateString()
  @IsOptional()
  approvedAt?: string;
}

export class UpdateProtocolDto extends PartialType(CreateProtocolDto) {
  @ApiPropertyOptional({ description: 'Experiment ID' })
  @IsUUID()
  @IsOptional()
  experimentId?: string;
}
