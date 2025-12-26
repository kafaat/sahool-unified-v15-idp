/**
 * Health Controller
 * Root-level health check endpoint
 */

import { Controller, Get } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse } from '@nestjs/swagger';
import { PrismaService } from '../prisma/prisma.service';

@ApiTags('Health')
@Controller()
export class HealthController {
  constructor(private readonly prisma: PrismaService) {}

  @Get('health')
  @ApiOperation({ summary: 'Health check endpoint' })
  @ApiResponse({ status: 200, description: 'Service is healthy' })
  async health() {
    // Check database connection
    let databaseHealthy = false;
    try {
      await this.prisma.$queryRaw`SELECT 1`;
      databaseHealthy = true;
    } catch (error) {
      console.error('Database health check failed:', error);
    }

    return {
      status: 'healthy',
      service: 'chat-service',
      version: '16.0.0',
      timestamp: new Date().toISOString(),
      dependencies: {
        database: databaseHealthy ? 'connected' : 'disconnected',
      },
    };
  }

  @Get('healthz')
  @ApiOperation({ summary: 'Kubernetes health check' })
  @ApiResponse({ status: 200, description: 'Service is healthy' })
  healthz() {
    return {
      status: 'healthy',
      service: 'chat-service',
    };
  }

  @Get('readyz')
  @ApiOperation({ summary: 'Kubernetes readiness check' })
  @ApiResponse({ status: 200, description: 'Service is ready' })
  async readyz() {
    // Check if service is ready to accept traffic
    let ready = true;

    try {
      await this.prisma.$queryRaw`SELECT 1`;
    } catch (error) {
      ready = false;
    }

    return {
      status: ready ? 'ready' : 'not_ready',
      service: 'chat-service',
      database: ready,
    };
  }
}
