/**
 * Health Check Controller
 * متحكم فحص الصحة
 */

import { Controller, Get } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';

@ApiTags('Health')
@Controller('health')
export class HealthController {
  @Get()
  @ApiOperation({
    summary: 'Health check endpoint',
    description: 'نقطة فحص صحة الخدمة',
  })
  @ApiResponse({
    status: 200,
    description: 'Service is healthy',
  })
  check() {
    return {
      success: true,
      service: 'user-service',
      version: '16.0.0',
      status: 'healthy',
      timestamp: new Date().toISOString(),
    };
  }
}
