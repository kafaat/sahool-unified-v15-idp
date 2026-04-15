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
  UnauthorizedException,
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

// -------- Actuator command DTO (IOT_ENDPOINTS.ACTUATORS POST /{id}/command) --------

class ActuatorCommandDto {
  @IsString()
  command: string; // "open" | "close" | "set_position" | "start" | "stop" | custom

  @IsOptional()
  parameters?: Record<string, unknown>;

  @IsOptional()
  @IsNumber()
  @Min(0)
  @Max(3600)
  durationSeconds?: number;
}

// =============================================================================
// Controller
// =============================================================================

@ApiTags("iot")
@Controller("iot")
export class IotController {
  constructor(private readonly iotService: IotService) {}

  /**
   * Extract tenantId from authenticated request (JWT `tid` / `tenant_id` claim).
   * استخراج معرف المستأجر من الرمز المصادق عليه
   *
   * SECURITY: Never trust the `x-tenant-id` header. The tenant id must
   * come from the JWT claim set by JwtAuthGuard; otherwise a client
   * could impersonate another tenant by setting the header.
   */
  private getTenantId(req: Request): string {
    const tid = (req as any).user?.tenantId || (req as any).user?.tid;
    if (!tid || typeof tid !== "string") {
      throw new UnauthorizedException({
        error: "missing_tenant",
        message: "JWT missing tenant id (tid)",
        message_ar: "الرمز لا يحتوي على معرف المستأجر",
      });
    }
    return tid;
  }

  // ==========================================================================
  // Health Check
  // ==========================================================================

  @Get("health")
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

  // ==========================================================================
  // Actuators (IOT_ENDPOINTS.ACTUATORS)
  // ==========================================================================

  /**
   * List actuators for the current tenant.
   *
   * Aligned with ``IOT_ENDPOINTS.ACTUATORS`` in the shared contracts
   * package. Returns actuator devices (pumps, valves, motors) scoped to
   * the tenant extracted from the JWT.
   */
  @Get("actuators")
  @UseGuards(JwtAuthGuard)
  @ApiOperation({ summary: "List actuators for the current tenant" })
  @ApiResponse({ status: 200, description: "Actuator list retrieved" })
  async listActuators(
    @Req() req: Request,
    @Query("fieldId") fieldId?: string,
    @Query("type") type?: string,
    @Query("limit") limit?: string,
    @Query("offset") offset?: string,
  ) {
    const tenantId = this.getTenantId(req);
    const parsedLimit = limit ? Math.min(parseInt(limit, 10) || 50, 200) : 50;
    const parsedOffset = offset ? Math.max(parseInt(offset, 10) || 0, 0) : 0;
    return this.iotService.listActuators(tenantId, {
      fieldId,
      actuatorType: type,
      limit: parsedLimit,
      offset: parsedOffset,
    });
  }

  /**
   * Send a command to a specific actuator.
   *
   * Returns HTTP 202 Accepted since commands are dispatched to the
   * device asynchronously via MQTT. The returned ``commandId`` can be
   * used to poll command status.
   */
  @Post("actuators/:id/command")
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.ACCEPTED)
  @ApiOperation({ summary: "Send a command to an actuator" })
  @ApiParam({ name: "id", description: "Actuator identifier" })
  @ApiBody({ type: ActuatorCommandDto })
  @ApiResponse({ status: 202, description: "Command accepted and queued" })
  async sendActuatorCommand(
    @Param("id") actuatorId: string,
    @Body() dto: ActuatorCommandDto,
    @Req() req: Request,
  ) {
    const tenantId = this.getTenantId(req);
    return this.iotService.dispatchActuatorCommand(tenantId, actuatorId, {
      command: dto.command,
      parameters: dto.parameters,
      durationSeconds: dto.durationSeconds,
    });
  }

  // ==========================================================================
  // Alert Rules (IOT_ENDPOINTS.ALERT_RULES)
  // ==========================================================================

  /**
   * List alert rules for the current tenant.
   *
   * Aligned with ``IOT_ENDPOINTS.ALERT_RULES`` in the shared contracts
   * package. Returns threshold-based alerting rules (sensor, metric,
   * operator, threshold, severity).
   */
  @Get("alert-rules")
  @UseGuards(JwtAuthGuard)
  @ApiOperation({ summary: "List IoT alert rules for the current tenant" })
  @ApiResponse({ status: 200, description: "Alert rules retrieved" })
  async listAlertRules(
    @Req() req: Request,
    @Query("enabled") enabled?: string,
    @Query("sensorId") sensorId?: string,
    @Query("fieldId") fieldId?: string,
  ) {
    const tenantId = this.getTenantId(req);
    const enabledFilter =
      typeof enabled === "string" ? enabled.toLowerCase() === "true" : undefined;
    return this.iotService.listAlertRules(tenantId, {
      enabled: enabledFilter,
      sensorId,
      fieldId,
    });
  }
}
