import {
  IsString,
  IsNumber,
  IsOptional,
  IsArray,
  IsBoolean,
  IsEnum,
  IsObject,
  ValidateNested,
  Min,
  Max,
  IsNotEmpty,
  ArrayMinSize,
} from 'class-validator';
import { Type } from 'class-transformer';
import { GeoJSONGeometry } from './gis-integration.service';

// ═══════════════════════════════════════════════════════════════════════════════
// Nested DTOs for complex objects
// ═══════════════════════════════════════════════════════════════════════════════

export class BBoxDto {
  @IsNumber()
  @Min(-180)
  @Max(180)
  minX: number;

  @IsNumber()
  @Min(-90)
  @Max(90)
  minY: number;

  @IsNumber()
  @Min(-180)
  @Max(180)
  maxX: number;

  @IsNumber()
  @Min(-90)
  @Max(90)
  maxY: number;
}

export class PointDto {
  @IsNumber()
  @Min(-180)
  @Max(180)
  x: number;

  @IsNumber()
  @Min(-90)
  @Max(90)
  y: number;
}

export class LatLngDto {
  @IsNumber()
  @Min(-90)
  @Max(90)
  lat: number;

  @IsNumber()
  @Min(-180)
  @Max(180)
  lng: number;
}

// ═══════════════════════════════════════════════════════════════════════════════
// WMS DTOs
// ═══════════════════════════════════════════════════════════════════════════════

export class GetMapDto {
  @IsArray()
  @ArrayMinSize(1)
  @IsString({ each: true })
  layers: string[];

  @ValidateNested()
  @Type(() => BBoxDto)
  bbox: BBoxDto;

  @IsNumber()
  @Min(1)
  @Max(4096)
  width: number;

  @IsNumber()
  @Min(1)
  @Max(4096)
  height: number;

  @IsOptional()
  @IsString()
  format?: string;

  @IsOptional()
  @IsString()
  srs?: string;

  @IsOptional()
  @IsBoolean()
  transparent?: boolean;
}

export class GetFeatureInfoDto {
  @IsArray()
  @ArrayMinSize(1)
  @IsString({ each: true })
  layers: string[];

  @ValidateNested()
  @Type(() => PointDto)
  point: PointDto;

  @ValidateNested()
  @Type(() => BBoxDto)
  bbox: BBoxDto;

  @IsNumber()
  @Min(1)
  @Max(4096)
  width: number;

  @IsNumber()
  @Min(1)
  @Max(4096)
  height: number;

  @IsOptional()
  @IsString()
  srs?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// WFS DTOs
// ═══════════════════════════════════════════════════════════════════════════════

export class GetFeaturesDto {
  @IsString()
  @IsNotEmpty()
  typeName: string;

  @IsOptional()
  @ValidateNested()
  @Type(() => BBoxDto)
  bbox?: BBoxDto;

  @IsOptional()
  @IsString()
  filter?: string;

  @IsOptional()
  @IsNumber()
  @Min(1)
  @Max(10000)
  maxFeatures?: number;

  @IsOptional()
  @IsNumber()
  @Min(0)
  startIndex?: number;

  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  propertyName?: string[];

  @IsOptional()
  @IsString()
  sortBy?: string;

  @IsOptional()
  @IsString()
  outputFormat?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Spatial Query DTOs
// ═══════════════════════════════════════════════════════════════════════════════

export class SpatialQueryDto {
  @IsEnum(['intersects', 'contains', 'within', 'overlaps', 'touches', 'buffer', 'union'])
  operation: 'intersects' | 'contains' | 'within' | 'overlaps' | 'touches' | 'buffer' | 'union';

  @IsOptional()
  @IsObject()
  geometry?: GeoJSONGeometry;

  @IsOptional()
  @IsNumber()
  @Min(0)
  distance?: number;

  @IsOptional()
  @IsEnum(['meters', 'kilometers', 'miles'])
  unit?: 'meters' | 'kilometers' | 'miles';

  @IsOptional()
  @IsString()
  targetLayer?: string;

  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  properties?: string[];
}

export class BufferDto {
  @IsObject()
  @IsNotEmpty()
  geometry: GeoJSONGeometry;

  @IsNumber()
  @Min(0)
  @Max(1000000)
  distance: number;

  @IsOptional()
  @IsEnum(['meters', 'kilometers', 'miles'])
  unit?: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Field Management DTOs
// ═══════════════════════════════════════════════════════════════════════════════

export class CreateFieldDto {
  @IsString()
  @IsNotEmpty()
  farmId: string;

  @IsString()
  @IsNotEmpty()
  name: string;

  @IsString()
  @IsNotEmpty()
  nameAr: string;

  @IsObject()
  @IsNotEmpty()
  geometry: GeoJSONGeometry;

  @IsOptional()
  @IsString()
  soilType?: string;

  @IsOptional()
  @IsString()
  irrigationType?: string;

  @IsOptional()
  @IsString()
  currentCrop?: string;
}

export class CalculateAreaDto {
  @IsObject()
  @IsNotEmpty()
  geometry: GeoJSONGeometry;
}

export class CalculateCentroidDto {
  @IsObject()
  @IsNotEmpty()
  geometry: GeoJSONGeometry;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Analysis DTOs
// ═══════════════════════════════════════════════════════════════════════════════

export class ZonalStatsDto {
  @IsObject()
  @IsNotEmpty()
  zones: any; // GeoJSONFeatureCollection

  @IsString()
  @IsNotEmpty()
  rasterLayer: string;

  @IsArray()
  @ArrayMinSize(1)
  @IsEnum(['count', 'sum', 'mean', 'min', 'max', 'std'], { each: true })
  statistics: ('count' | 'sum' | 'mean' | 'min' | 'max' | 'std')[];
}

// ═══════════════════════════════════════════════════════════════════════════════
// Routing DTOs
// ═══════════════════════════════════════════════════════════════════════════════

export class RouteRequestDto {
  @ValidateNested()
  @Type(() => LatLngDto)
  origin: LatLngDto;

  @ValidateNested()
  @Type(() => LatLngDto)
  destination: LatLngDto;

  @IsOptional()
  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => LatLngDto)
  waypoints?: LatLngDto[];

  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  avoid?: string[];

  @IsOptional()
  @IsBoolean()
  optimize?: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Map Project DTOs
// ═══════════════════════════════════════════════════════════════════════════════

export class CreateProjectDto {
  @IsString()
  @IsNotEmpty()
  name: string;

  @IsString()
  @IsNotEmpty()
  nameAr: string;

  @IsString()
  @IsNotEmpty()
  description: string;

  @IsArray()
  @ArrayMinSize(1)
  @IsString({ each: true })
  layers: string[];

  @IsOptional()
  @IsString()
  basemap?: string;

  @IsOptional()
  @ValidateNested()
  @Type(() => LatLngDto)
  center?: LatLngDto;

  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(22)
  zoom?: number;

  @IsString()
  @IsNotEmpty()
  owner: string;
}

// ═══════════════════════════════════════════════════════════════════════════════
// Utility DTOs
// ═══════════════════════════════════════════════════════════════════════════════

export class TransformDto {
  @IsArray()
  @ArrayMinSize(2)
  @IsNumber({}, { each: true })
  coordinates: number[];

  @IsString()
  @IsNotEmpty()
  fromSRS: string;

  @IsString()
  @IsNotEmpty()
  toSRS: string;
}

export class ValidateGeoJSONDto {
  @IsObject()
  @IsNotEmpty()
  geojson: any;
}
