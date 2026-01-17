import { Controller, Get } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { PrismaService } from "./config/prisma.service";

@ApiTags("health")
@Controller()
export class HealthController {
  constructor(private readonly prisma: PrismaService) {}

  @Get("healthz")
  @ApiOperation({ summary: "Health check endpoint" })
  async healthCheck() {
    const dbStatus = await this.checkDatabase();

    return {
      status: "ok",
      service: "research-core",
      version: "15.3.0",
      timestamp: new Date().toISOString(),
      database: dbStatus,
    };
  }

  private async checkDatabase(): Promise<string> {
    try {
      await this.prisma.$queryRaw`SELECT 1`;
      return "connected";
    } catch {
      return "disconnected";
    }
  }
}
