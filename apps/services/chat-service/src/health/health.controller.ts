/**
 * Health Controller for Chat Service
 * نقاط فحص صحة الخدمة
 */

import { Controller, Get } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';

@ApiTags('Health')
@Controller()
export class HealthController {
  private readonly startTime: Date;

  constructor() {
    this.startTime = new Date();
  }

  @Get('healthz')
  @ApiOperation({ summary: 'Health check endpoint' })
  @ApiResponse({ status: 200, description: 'Service is healthy' })
  healthCheck() {
    return {
      status: 'ok',
      service: 'chat-service',
      timestamp: new Date().toISOString(),
      uptime: this.getUptime(),
    };
  }

  @Get('readyz')
  @ApiOperation({ summary: 'Readiness check endpoint' })
  @ApiResponse({ status: 200, description: 'Service is ready' })
  readinessCheck() {
    return {
      status: 'ready',
      service: 'chat-service',
      timestamp: new Date().toISOString(),
    };
  }

  @Get('livez')
  @ApiOperation({ summary: 'Liveness check endpoint' })
  @ApiResponse({ status: 200, description: 'Service is alive' })
  livenessCheck() {
    return {
      status: 'alive',
      service: 'chat-service',
      timestamp: new Date().toISOString(),
      uptime: this.getUptime(),
    };
  }

  private getUptime(): string {
    const uptime = Date.now() - this.startTime.getTime();
    const seconds = Math.floor(uptime / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ${hours % 24}h`;
    if (hours > 0) return `${hours}h ${minutes % 60}m`;
    if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
    return `${seconds}s`;
  }
}
