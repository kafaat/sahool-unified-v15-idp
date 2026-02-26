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
} from "class-validator";
import { Throttle } from "@nestjs/throttler";
import { IotService, SensorType, SensorReading } from "./iot.service";
import { JwtAuthGuard } from "../auth/jwt-auth.guard";
import { SkipTenantCheck } from "@sahool/nestjs-auth";

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
