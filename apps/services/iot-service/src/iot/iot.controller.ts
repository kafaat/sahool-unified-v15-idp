/**
 * SAHOOL IoT Controller
 * واجهة برمجة التطبيقات لإنترنت الأشياء
 */

import {
  Controller,
  Get,
  Post,
  Body,
  Param,
  Query,
  Req,
  HttpCode,
  HttpStatus,
  UseGuards,
  BadRequestException,
} from "@nestjs/common";
import { Request } from "express";
import {
  ApiTags,
  ApiOperation,
  ApiResponse,
  ApiParam,
  ApiBody,
} from "@nestjs/swagger";
import {
  IsIn,
  IsNumber,
  IsOptional,
  IsPositive,
  IsString,
  IsArray,
  IsBoolean,
  IsEnum,
  Min,
  Max,
} from "class-validator";
import { Type } from "class-transformer";
import { Throttle } from "@nestjs/throttler";
import { IotService, SensorType, SensorReading } from "./iot.service";
import { JwtAuthGuard } from "../auth/jwt-auth.guard";
import { SkipTenantCheck } from "@sahool/nestjs-auth";

// =============================================================================
// Sensor Value Bounds - حدود قيم المستشعرات
// =============================================================================

const SENSOR_BOUNDS: Record<string, { min: number; max: number; unit: string }> = {
  [SensorType.SOIL_MOISTURE]: { min: 0, max: 100, unit: "%" },
  [SensorType.SOIL_TEMPERATURE]: { min: -10, max: 60, unit: "°C" },
  [SensorType.AIR_TEMPERATURE]: { min: -20, max: 60, unit: "°C" },
  [SensorType.AIR_HUMIDITY]: { min: 0, max: 100, unit: "%" },
  [SensorType.LIGHT_INTENSITY]: { min: 0, max: 150000, unit: "lux" },
  [SensorType.WATER_LEVEL]: { min: 0, max: 1000, unit: "cm" },
  [SensorType.WATER_FLOW]: { min: 0, max: 1000, unit: "L/min" },
  [SensorType.PH_LEVEL]: { min: 0, max: 14, unit: "pH" },
  [SensorType.EC_LEVEL]: { min: 0, max: 10, unit: "mS/cm" },
  [SensorType.WIND_SPEED]: { min: 0, max: 200, unit: "km/h" },
  [SensorType.RAIN_GAUGE]: { min: 0, max: 500, unit: "mm" },
};

// =============================================================================
// DTOs
// =============================================================================

class TogglePumpDto {
  @IsIn(["ON", "OFF"])
  status: "ON" | "OFF";

  @IsNumber()
  @IsOptional()
  @IsPositive()
  duration?: number;
}

class ToggleValveDto {
  @IsIn(["ON", "OFF"])
  status: "ON" | "OFF";
}

class IrrigationScheduleDto {
  @IsString()
  startTime: string;

  @IsNumber()
  @IsPositive()
  duration: number;

  @IsArray()
  @IsString({ each: true })
  days: string[];

  @IsBoolean()
  enabled: boolean;
}

class IngestSensorReadingDto {
  @IsString()
  deviceId: string;

  @IsEnum(SensorType)
  sensorType: SensorType;

  @IsNumber()
  @Type(() => Number)
  value: number;

  @IsOptional()
  @IsString()
  timestamp?: string;
}

// =============================================================================
// Controller
// =============================================================================

@ApiTags("iot")
@Controller("iot")
export class IotController {
  constructor(private readonly iotService: IotService) {}

  /**
   * Extract tenantId from authenticated request
   * استخراج معرف المستأجر من الطلب المصادق عليه
   */
  private getTenantId(req: Request): string {
    return (req as any).user?.tenantId || req.headers['x-tenant-id'] as string || 'default';
  }

  // ==========================================================================
  // Health Check
  // ==========================================================================

  @Get("health")
  @SkipTenantCheck()
  @Throttle({ default: { limit: 10, ttl: 60000 } })
  @ApiOperation({ summary: "Health check" })
  healthCheck() {
    return {
      status: "ok",
      service: "iot-service",
      timestamp: new Date().toISOString(),
    };
  }

  // ==========================================================================
  // Sensor Data
  // ==========================================================================

  @Get("field/:fieldId/sensors")
  @UseGuards(JwtAuthGuard)
  @ApiOperation({ summary: "Get all sensor readings for a field" })
  @ApiParam({ name: "fieldId", description: "Field identifier" })
  @ApiResponse({ status: 200, description: "Sensor readings retrieved" })
  async getFieldSensors(
    @Param("fieldId") fieldId: string,
    @Req() req: Request,
  ): Promise<SensorReading[]> {
    return this.iotService.getFieldSensorData(fieldId, this.getTenantId(req));
  }

  @Get("field/:fieldId/sensor/:sensorType")
  @UseGuards(JwtAuthGuard)
  @ApiOperation({ summary: "Get specific sensor reading" })
  @ApiParam({ name: "fieldId", description: "Field identifier" })
  @ApiParam({
    name: "sensorType",
    description: "Type of sensor",
    enum: SensorType,
  })
  @ApiResponse({ status: 200, description: "Sensor reading retrieved" })
  async getSensorReading(
    @Param("fieldId") fieldId: string,
    @Param("sensorType") sensorType: SensorType,
    @Req() req: Request,
  ): Promise<SensorReading | null> {
    return this.iotService.getSensorReading(fieldId, sensorType, this.getTenantId(req));
  }

  // ==========================================================================
  // Sensor Data Ingestion (REST API)
  // ==========================================================================

  @Post("field/:fieldId/sensor/reading")
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: "Ingest a sensor reading via REST API" })
  @ApiParam({ name: "fieldId", description: "Field identifier" })
  @ApiBody({ type: IngestSensorReadingDto })
  @ApiResponse({ status: 200, description: "Sensor reading accepted" })
  @ApiResponse({ status: 400, description: "Invalid sensor value or out of bounds" })
  async ingestSensorReading(
    @Param("fieldId") fieldId: string,
    @Body() dto: IngestSensorReadingDto,
    @Req() req: Request,
  ): Promise<{ success: boolean; quality: string; message: string }> {
    const bounds = SENSOR_BOUNDS[dto.sensorType];
    if (bounds && (dto.value < bounds.min || dto.value > bounds.max)) {
      throw new BadRequestException({
        statusCode: 400,
        error: "Bad Request",
        message: `Value ${dto.value} out of bounds for ${dto.sensorType} [${bounds.min}, ${bounds.max}] ${bounds.unit}`,
        message_ar: `القيمة ${dto.value} خارج النطاق المسموح لـ ${dto.sensorType} [${bounds.min}, ${bounds.max}] ${bounds.unit}`,
      });
    }
    return this.iotService.ingestReading(fieldId, dto, this.getTenantId(req));
  }

  @Get("sensor-bounds")
  @ApiOperation({ summary: "Get sensor value bounds for all sensor types" })
  @ApiResponse({ status: 200, description: "Sensor bounds retrieved" })
  getSensorBounds() {
    return { bounds: SENSOR_BOUNDS };
  }

  // ==========================================================================
  // Actuator Control
  // ==========================================================================

  @Post("field/:fieldId/pump")
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: "Toggle pump on/off" })
  @ApiParam({ name: "fieldId", description: "Field identifier" })
  @ApiBody({ type: TogglePumpDto })
  @ApiResponse({ status: 200, description: "Pump command sent" })
  async togglePump(
    @Param("fieldId") fieldId: string,
    @Body() dto: TogglePumpDto,
    @Req() req: Request,
  ): Promise<{ success: boolean; message: string }> {
    return this.iotService.togglePump(fieldId, dto.status, {
      duration: dto.duration,
      tenantId: this.getTenantId(req),
    });
  }

  @Post("field/:fieldId/valve/:valveId")
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: "Toggle valve on/off" })
  @ApiParam({ name: "fieldId", description: "Field identifier" })
  @ApiParam({ name: "valveId", description: "Valve identifier" })
  @ApiBody({ type: ToggleValveDto })
  @ApiResponse({ status: 200, description: "Valve command sent" })
  async toggleValve(
    @Param("fieldId") fieldId: string,
    @Param("valveId") valveId: string,
    @Body() dto: ToggleValveDto,
    @Req() req: Request,
  ): Promise<{ success: boolean; message: string }> {
    return this.iotService.toggleValve(fieldId, valveId, dto.status, {
      tenantId: this.getTenantId(req),
    });
  }

  @Post("field/:fieldId/irrigation/schedule")
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: "Set irrigation schedule" })
  @ApiParam({ name: "fieldId", description: "Field identifier" })
  @ApiBody({ type: IrrigationScheduleDto })
  @ApiResponse({ status: 200, description: "Schedule saved" })
  setIrrigationSchedule(
    @Param("fieldId") fieldId: string,
    @Body() dto: IrrigationScheduleDto,
    @Req() req: Request,
  ): { success: boolean; message: string } {
    return this.iotService.setIrrigationSchedule(fieldId, {
      ...dto,
      tenantId: this.getTenantId(req),
    });
  }

  // ==========================================================================
  // Actuator States
  // ==========================================================================

  @Get("field/:fieldId/actuators")
  @UseGuards(JwtAuthGuard)
  @ApiOperation({ summary: "Get actuator states for a field" })
  @ApiParam({ name: "fieldId", description: "Field identifier" })
  @ApiResponse({ status: 200, description: "Actuator states retrieved" })
  async getFieldActuators(
    @Param("fieldId") fieldId: string,
    @Req() req: Request,
  ): Promise<Record<string, boolean>> {
    return this.iotService.getFieldActuatorStates(fieldId, this.getTenantId(req));
  }

  // ==========================================================================
  // Device Management
  // ==========================================================================

  @Get("devices")
  @UseGuards(JwtAuthGuard)
  @ApiOperation({ summary: "Get all connected devices" })
  @ApiResponse({ status: 200, description: "Device list retrieved" })
  async getDevices(@Req() req: Request) {
    const tenantId = this.getTenantId(req);
    return {
      devices: await this.iotService.getConnectedDevices(tenantId),
      stats: await this.iotService.getDeviceStats(tenantId),
    };
  }

  // ==========================================================================
  // Dashboard Data
  // ==========================================================================

  @Get("dashboard/:fieldId")
  @UseGuards(JwtAuthGuard)
  @ApiOperation({ summary: "Get IoT dashboard data for a field" })
  @ApiParam({ name: "fieldId", description: "Field identifier" })
  @ApiResponse({ status: 200, description: "Dashboard data retrieved" })
  async getDashboard(@Param("fieldId") fieldId: string, @Req() req: Request) {
    const tenantId = this.getTenantId(req);
    const sensors = await this.iotService.getFieldSensorData(fieldId, tenantId);
    const actuators = await this.iotService.getFieldActuatorStates(fieldId, tenantId);

    // Transform to dashboard format
    const sensorData: Record<string, any> = {};
    sensors.forEach((sensor) => {
      sensorData[sensor.sensorType] = {
        value: sensor.value,
        unit: sensor.unit,
        quality: sensor.quality,
        timestamp: sensor.timestamp,
      };
    });

    return {
      fieldId,
      sensors: sensorData,
      actuators,
      timestamp: new Date().toISOString(),
    };
  }

  // ==========================================================================
  // Historical Data
  // ==========================================================================

  @Get("field/:fieldId/history")
  @UseGuards(JwtAuthGuard)
  @ApiOperation({ summary: "Get historical sensor readings from database" })
  @ApiParam({ name: "fieldId", description: "Field identifier" })
  @ApiResponse({ status: 200, description: "Historical readings retrieved" })
  async getHistoricalReadings(
    @Param("fieldId") fieldId: string,
    @Req() req: Request,
    @Query("sensorType") sensorType?: string,
    @Query("hours") hours?: string,
  ) {
    return this.iotService.getHistoricalReadings(
      fieldId,
      this.getTenantId(req),
      sensorType,
      hours ? parseInt(hours, 10) : 24,
    );
  }
}
