import { Controller, Get } from "@nestjs/common";
import { ApiTags, ApiOperation } from "@nestjs/swagger";
import { Public } from "./guards/jwt-auth.guard";
import { SkipTenantCheck } from "./guards/tenant.guard";
import { PrismaService } from "./config/prisma.service";

@ApiTags("health")
@Public()
@SkipTenantCheck()
@Controller()
export class HealthController {
  constructor(private readonly prisma: PrismaService) {}

  @Get("healthz")
  @ApiOperation({ summary: "Liveness probe | فحص الحياة" })
  async healthCheck() {
    return {
      status: "ok",
      service: "research-core",
      version: "16.0.0",
      timestamp: new Date().toISOString(),
    };
  }

  @Get("readyz")
  @ApiOperation({ summary: "Readiness probe | فحص الجاهزية" })
  async readinessCheck() {
    const dbStatus = await this.checkDatabase();

    return {
      status: dbStatus === "connected" ? "ready" : "not_ready",
      service: "research-core",
      version: "16.0.0",
      checks: {
        database: dbStatus,
      },
      timestamp: new Date().toISOString(),
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
