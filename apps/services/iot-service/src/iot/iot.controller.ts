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
  HttpCode,
  HttpStatus,
  UseGuards,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiParam, ApiBody } from '@nestjs/swagger';
import { IsIn, IsNumber, IsOptional, IsPositive, IsString, IsArray, IsBoolean } from 'class-validator';
import { Throttle } from '@nestjs/throttler';
import { IotService, SensorType, SensorReading } from './iot.service';
import { JwtAuthGuard } from '../auth/jwt-auth.guard';

// =============================================================================
// DTOs
// =============================================================================

class TogglePumpDto {
  @IsIn(['ON', 'OFF'])
  status: 'ON' | 'OFF';

  @IsNumber()
  @IsOptional()
  @IsPositive()
  duration?: number;
}

class ToggleValveDto {
  @IsIn(['ON', 'OFF'])
  status: 'ON' | 'OFF';
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

@ApiTags('iot')
@Controller('iot')
export class IotController {
  constructor(private readonly iotService: IotService) {}

  // ==========================================================================
  // Health Check
  // ==========================================================================

  @Get('health')
  @Throttle({ default: { limit: 10, ttl: 60000 } })
  @ApiOperation({ summary: 'Health check' })
  healthCheck() {
    return {
      status: 'ok',
      service: 'iot-service',
      timestamp: new Date().toISOString(),
    };
  }

  // ==========================================================================
  // Sensor Data
  // ==========================================================================

  @Get('field/:fieldId/sensors')
  @UseGuards(JwtAuthGuard)
  @ApiOperation({ summary: 'Get all sensor readings for a field' })
  @ApiParam({ name: 'fieldId', description: 'Field identifier' })
  @ApiResponse({ status: 200, description: 'Sensor readings retrieved' })
  async getFieldSensors(@Param('fieldId') fieldId: string): Promise<SensorReading[]> {
    return this.iotService.getFieldSensorData(fieldId);
  }

  @Get('field/:fieldId/sensor/:sensorType')
  @UseGuards(JwtAuthGuard)
  @ApiOperation({ summary: 'Get specific sensor reading' })
  @ApiParam({ name: 'fieldId', description: 'Field identifier' })
  @ApiParam({ name: 'sensorType', description: 'Type of sensor', enum: SensorType })
  @ApiResponse({ status: 200, description: 'Sensor reading retrieved' })
  async getSensorReading(
    @Param('fieldId') fieldId: string,
    @Param('sensorType') sensorType: SensorType,
  ): Promise<SensorReading | null> {
    return this.iotService.getSensorReading(fieldId, sensorType);
  }

  // ==========================================================================
  // Actuator Control
  // ==========================================================================

  @Post('field/:fieldId/pump')
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Toggle pump on/off' })
  @ApiParam({ name: 'fieldId', description: 'Field identifier' })
  @ApiBody({ type: TogglePumpDto })
  @ApiResponse({ status: 200, description: 'Pump command sent' })
  async togglePump(
    @Param('fieldId') fieldId: string,
    @Body() dto: TogglePumpDto,
  ): Promise<{ success: boolean; message: string }> {
    return this.iotService.togglePump(fieldId, dto.status, {
      duration: dto.duration,
    });
  }

  @Post('field/:fieldId/valve/:valveId')
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Toggle valve on/off' })
  @ApiParam({ name: 'fieldId', description: 'Field identifier' })
  @ApiParam({ name: 'valveId', description: 'Valve identifier' })
  @ApiBody({ type: ToggleValveDto })
  @ApiResponse({ status: 200, description: 'Valve command sent' })
  toggleValve(
    @Param('fieldId') fieldId: string,
    @Param('valveId') valveId: string,
    @Body() dto: ToggleValveDto,
  ): { success: boolean; message: string } {
    return this.iotService.toggleValve(fieldId, valveId, dto.status);
  }

  @Post('field/:fieldId/irrigation/schedule')
  @UseGuards(JwtAuthGuard)
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ summary: 'Set irrigation schedule' })
  @ApiParam({ name: 'fieldId', description: 'Field identifier' })
  @ApiBody({ type: IrrigationScheduleDto })
  @ApiResponse({ status: 200, description: 'Schedule saved' })
  setIrrigationSchedule(
    @Param('fieldId') fieldId: string,
    @Body() dto: IrrigationScheduleDto,
  ): { success: boolean; message: string } {
    return this.iotService.setIrrigationSchedule(fieldId, dto);
  }

  // ==========================================================================
  // Actuator States
  // ==========================================================================

  @Get('field/:fieldId/actuators')
  @UseGuards(JwtAuthGuard)
  @ApiOperation({ summary: 'Get actuator states for a field' })
  @ApiParam({ name: 'fieldId', description: 'Field identifier' })
  @ApiResponse({ status: 200, description: 'Actuator states retrieved' })
  async getFieldActuators(
    @Param('fieldId') fieldId: string,
  ): Promise<Record<string, boolean>> {
    return this.iotService.getFieldActuatorStates(fieldId);
  }

  // ==========================================================================
  // Device Management
  // ==========================================================================

  @Get('devices')
  @UseGuards(JwtAuthGuard)
  @ApiOperation({ summary: 'Get all connected devices' })
  @ApiResponse({ status: 200, description: 'Device list retrieved' })
  async getDevices() {
    return {
      devices: await this.iotService.getConnectedDevices(),
      stats: await this.iotService.getDeviceStats(),
    };
  }

  // ==========================================================================
  // Dashboard Data
  // ==========================================================================

  @Get('dashboard/:fieldId')
  @UseGuards(JwtAuthGuard)
  @ApiOperation({ summary: 'Get IoT dashboard data for a field' })
  @ApiParam({ name: 'fieldId', description: 'Field identifier' })
  @ApiResponse({ status: 200, description: 'Dashboard data retrieved' })
  async getDashboard(@Param('fieldId') fieldId: string) {
    const sensors = await this.iotService.getFieldSensorData(fieldId);
    const actuators = await this.iotService.getFieldActuatorStates(fieldId);

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
}
