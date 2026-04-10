/**
 * NDVI Service - Vegetation Index Operations
 */

import { Injectable, NotFoundException, BadRequestException, Logger } from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";
import { CacheService, CACHE_KEYS, CACHE_TTL } from "../cache/cache.service";
import { assertTenantOwnership } from "../auth/tenant.utils";

export interface NdviCategory {
  name: string;
  nameAr: string;
  color: string;
}

@Injectable()
export class NdviService {
  private readonly logger = new Logger(NdviService.name);

  constructor(
    private prisma: PrismaService,
    private cacheService: CacheService,
  ) {}

  /**
   * Get NDVI analysis for a field with tenant isolation
   */
  async getFieldNdvi(fieldId: string, tenantId: string) {
    const cacheKey = CACHE_KEYS.NDVI(fieldId);
    const cached = await this.cacheService.get<any>(cacheKey);
    if (cached) return cached;

    const field = await this.prisma.field.findUnique({
      where: { id: fieldId },
      select: {
        id: true,
        name: true,
        tenantId: true,
        ndviValue: true,
        healthScore: true,
      },
    });

    if (!field) {
      throw new NotFoundException("Field not found - الحقل غير موجود");
    }

    // Enforce tenant isolation
    assertTenantOwnership(field.tenantId, tenantId, "field");

    // Get NDVI readings (tenant-scoped for defense-in-depth).
    //
    // Noisy readings are excluded from the statistics (average / min / max /
    // trend) to avoid poisoning the summary with cloudy pixels:
    //   * cloudCover > MAX_CLOUD_COVER_FOR_STATS  → skipped
    //   * quality === 'poor'                       → skipped
    // The full raw `readings` list is still shipped in `history` so the UI
    // can render everything and let the user see what was filtered.
    const readings = await this.prisma.ndviReading.findMany({
      where: { fieldId, tenantId: field.tenantId },
      orderBy: { capturedAt: "desc" },
      take: 30,
      select: {
        id: true,
        value: true,
        capturedAt: true,
        source: true,
        cloudCover: true,
        quality: true,
      },
    });

    const MAX_CLOUD_COVER_FOR_STATS = 30; // percent — matches save-time threshold
    const usable = readings.filter((r: { cloudCover: unknown; quality: string | null }) => {
      if (r.quality === "poor") return false;
      if (r.cloudCover == null) return true; // cloudCover unknown → assume ok
      return Number(r.cloudCover) <= MAX_CLOUD_COVER_FOR_STATS;
    });
    const values: number[] = usable.map((r) => Number((r as { value: unknown }).value));
    const current = field.ndviValue ? Number(field.ndviValue) : values[0] || 0;

    // Calculate statistics
    const average = values.length > 0
      ? values.reduce((a: number, b: number) => a + b, 0) / values.length
      : 0;
    const min = values.length > 0 ? Math.min(...values) : 0;
    const max = values.length > 0 ? Math.max(...values) : 0;

    // Calculate trend (compare first half vs second half of readings)
    let trend = 0;
    if (values.length >= 4) {
      const firstHalf = values.slice(0, Math.floor(values.length / 2));
      const secondHalf = values.slice(Math.floor(values.length / 2));
      const firstAvg = firstHalf.reduce((a: number, b: number) => a + b, 0) / firstHalf.length;
      const secondAvg = secondHalf.reduce((a: number, b: number) => a + b, 0) / secondHalf.length;
      trend = secondAvg - firstAvg;
    }

    const result = {
      fieldId: field.id,
      fieldName: field.name,
      current: {
        value: current,
        category: this.getNdviCategory(current),
        date: new Date().toISOString(),
      },
      statistics: {
        average: Math.round(average * 100) / 100,
        min: Math.round(min * 100) / 100,
        max: Math.round(max * 100) / 100,
        trend: Math.round(trend * 100) / 100,
        trendDirection:
          trend > 0.05 ? "improving" : trend < -0.05 ? "declining" : "stable",
      },
      history: readings.map((r: { capturedAt: Date; value: unknown; source: string; quality: string | null; cloudCover: unknown }) => ({
        date: r.capturedAt,
        value: Number(r.value),
        source: r.source,
        quality: r.quality,
        cloudCover: r.cloudCover ? Number(r.cloudCover) : null,
      })),
      lastUpdated: new Date().toISOString(),
    };

    await this.cacheService.set(cacheKey, result, CACHE_TTL.MEDIUM);

    return result;
  }

  /**
   * Update NDVI value for a field with tenant isolation
   */
  async updateFieldNdvi(
    fieldId: string,
    tenantId: string,
    value: number,
    source: string = "manual",
    cloudCover?: number,
  ) {
    if (value < -1 || value > 1) {
      throw new BadRequestException("NDVI value must be between -1 and 1 - قيمة NDVI يجب أن تكون بين -1 و 1");
    }

    const field = await this.prisma.field.findUnique({
      where: { id: fieldId },
      select: { id: true, tenantId: true },
    });

    if (!field) {
      throw new NotFoundException("Field not found - الحقل غير موجود");
    }

    // Enforce tenant isolation
    assertTenantOwnership(field.tenantId, tenantId, "field");

    // Create NDVI reading
    await this.prisma.ndviReading.create({
      data: {
        tenantId: field.tenantId,
        fieldId,
        value,
        capturedAt: new Date(),
        source,
        cloudCover: cloudCover ?? null,
        quality: cloudCover && cloudCover > 50 ? "poor" : "good",
      },
    });

    // Update field NDVI and health score
    const healthScore = this.calculateHealthScore(value);
    await this.prisma.field.update({
      where: { id: fieldId },
      data: {
        ndviValue: value,
        healthScore,
      },
    });

    // Invalidate caches
    await this.cacheService.del(CACHE_KEYS.NDVI(fieldId));
    await this.cacheService.del(CACHE_KEYS.FIELD(fieldId));
    await this.cacheService.del(CACHE_KEYS.NDVI_SUMMARY(field.tenantId));

    return {
      fieldId,
      ndviValue: value,
      healthScore,
      category: this.getNdviCategory(value),
      source,
      updatedAt: new Date().toISOString(),
    };
  }

  /**
   * Get NDVI summary for a tenant
   */
  async getTenantNdviSummary(tenantId: string) {
    const cacheKey = CACHE_KEYS.NDVI_SUMMARY(tenantId);
    const cached = await this.cacheService.get<any>(cacheKey);
    if (cached) return cached;

    const result = await this.prisma.$queryRaw<any[]>`
      SELECT
        COUNT(*) as total_fields,
        AVG(ndvi_value) as average_ndvi,
        AVG(health_score) as average_health,
        SUM(area_hectares) as total_area,
        COUNT(*) FILTER (WHERE ndvi_value >= 0.6) as healthy_count,
        COUNT(*) FILTER (WHERE ndvi_value >= 0.4 AND ndvi_value < 0.6) as moderate_count,
        COUNT(*) FILTER (WHERE ndvi_value >= 0.2 AND ndvi_value < 0.4) as stressed_count,
        COUNT(*) FILTER (WHERE ndvi_value < 0.2 OR ndvi_value IS NULL) as critical_count
      FROM fields
      WHERE tenant_id = ${tenantId} AND is_deleted = false AND ndvi_value IS NOT NULL
    `;

    const summary = result[0] || {};

    const data = {
      tenantId,
      totalFields: parseInt(summary.total_fields) || 0,
      averageNdvi: parseFloat(summary.average_ndvi) || 0,
      averageHealth: parseFloat(summary.average_health) || 0,
      totalAreaHectares: parseFloat(summary.total_area) || 0,
      distribution: {
        healthy: parseInt(summary.healthy_count) || 0,
        moderate: parseInt(summary.moderate_count) || 0,
        stressed: parseInt(summary.stressed_count) || 0,
        critical: parseInt(summary.critical_count) || 0,
      },
      timestamp: new Date().toISOString(),
    };

    await this.cacheService.set(cacheKey, data, CACHE_TTL.MEDIUM);

    return data;
  }

  /**
   * Get NDVI category based on value
   */
  private getNdviCategory(value: number): NdviCategory {
    if (value < 0) {
      return { name: "non-vegetation", nameAr: "غير نباتي", color: "#1565C0" };
    }
    if (value < 0.2) {
      return { name: "bare-soil", nameAr: "تربة جرداء", color: "#8D6E63" };
    }
    if (value < 0.4) {
      return { name: "stressed", nameAr: "إجهاد", color: "#FF5722" };
    }
    if (value < 0.6) {
      return { name: "moderate", nameAr: "متوسط", color: "#FFEB3B" };
    }
    if (value < 0.8) {
      return { name: "healthy", nameAr: "صحي", color: "#8BC34A" };
    }
    return { name: "very-healthy", nameAr: "ممتاز", color: "#2E7D32" };
  }

  /**
   * Calculate health score from NDVI
   */
  private calculateHealthScore(ndviValue: number): number {
    if (ndviValue < 0.2) return 0;
    if (ndviValue > 0.8) return 1;
    return (ndviValue - 0.2) / 0.6;
  }
}
