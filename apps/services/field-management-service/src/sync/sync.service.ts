/**
 * Sync Service - Mobile Delta Sync Operations
 *
 * Features:
 * - Delta sync based on timestamps
 * - Batch upload with conflict detection
 * - Device sync status tracking
 */

import { Injectable, BadRequestException, Logger } from "@nestjs/common";
import { SyncState } from "../../prisma/generated/client";
import { PrismaService } from "../prisma/prisma.service";
import { CacheService, CACHE_KEYS, CACHE_TTL } from "../cache/cache.service";

// ETag generation
function generateETag(id: string, version: number): string {
  return `"${id}-v${version}"`;
}

export interface SyncResult {
  clientId: string;
  serverId?: string;
  status: "created" | "updated" | "conflict" | "error";
  server_version?: number;
  etag?: string;
  serverData?: any;
  error?: string;
}

@Injectable()
export class SyncService {
  private readonly logger = new Logger(SyncService.name);

  constructor(
    private prisma: PrismaService,
    private cacheService: CacheService,
  ) {}

  /**
   * Delta sync - get fields modified since timestamp
   */
  async deltaSync(params: {
    tenantId: string;
    since?: string;
    includeDeleted?: boolean;
    limit?: number;
  }) {
    const { tenantId, since, includeDeleted, limit = 100 } = params;

    const where: any = { tenantId };

    if (since) {
      const sinceDate = new Date(since);
      if (isNaN(sinceDate.getTime())) {
        throw new BadRequestException("Invalid 'since' timestamp format. Use ISO 8601.");
      }
      where.updatedAt = { gt: sinceDate };
    }

    if (!includeDeleted) {
      where.isDeleted = false;
    }

    const fields = await this.prisma.field.findMany({
      where,
      select: {
        id: true,
        name: true,
        tenantId: true,
        cropType: true,
        status: true,
        areaHectares: true,
        healthScore: true,
        ndviValue: true,
        irrigationType: true,
        soilType: true,
        plantingDate: true,
        expectedHarvest: true,
        metadata: true,
        isDeleted: true,
        version: true,
        serverUpdatedAt: true,
        createdAt: true,
        updatedAt: true,
      },
      orderBy: { updatedAt: "asc" },
      take: Math.min(limit, 100),
    });

    const actualLimit = Math.min(limit, 100);
    const hasMore = fields.length === actualLimit;
    const lastUpdated = fields.length > 0 ? fields[fields.length - 1].updatedAt : null;

    // Transform with sync metadata
    const syncData = fields.map((field: typeof fields[0]) => ({
      ...field,
      server_version: field.version,
      etag: generateETag(field.id, field.version),
      _syncMeta: {
        serverTime: new Date().toISOString(),
        action: field.isDeleted ? "delete" : "upsert",
      },
    }));

    return {
      data: syncData,
      sync: {
        serverTime: new Date().toISOString(),
        lastUpdated: lastUpdated?.toISOString() || null,
        count: fields.length,
        hasMore,
        nextSince: lastUpdated?.toISOString() || since,
      },
    };
  }

  /**
   * Batch sync - upload multiple fields with conflict detection
   */
  async batchSync(params: {
    deviceId: string;
    userId: string;
    tenantId: string;
    fields: any[];
  }): Promise<{
    results: SyncResult[];
    summary: any;
    serverTime: string;
  }> {
    const { deviceId, userId, tenantId, fields } = params;

    const results: SyncResult[] = [];

    for (const clientField of fields) {
      try {
        const { id, client_version, _isNew, ...fieldData } = clientField;

        // New field creation
        if (_isNew || !id) {
          const newField = await this.prisma.field.create({
            data: {
              name: fieldData.name,
              tenantId,
              cropType: fieldData.cropType,
              status: fieldData.status || "active",
              irrigationType: fieldData.irrigationType,
              soilType: fieldData.soilType,
              plantingDate: fieldData.plantingDate ? new Date(fieldData.plantingDate) : null,
              expectedHarvest: fieldData.expectedHarvest ? new Date(fieldData.expectedHarvest) : null,
              metadata: fieldData.metadata,
            },
          });

          results.push({
            clientId: id || "new",
            serverId: newField.id,
            status: "created",
            server_version: newField.version,
            etag: generateETag(newField.id, newField.version),
          });
          continue;
        }

        // Update existing field - validate tenant ownership
        const existingField = await this.prisma.field.findUnique({
          where: { id_tenantId: { id, tenantId } },
          select: { id: true, version: true, tenantId: true },
        });

        if (!existingField) {
          results.push({
            clientId: id,
            status: "error",
            error: "Field not found",
          });
          continue;
        }

        // Security: Verify field belongs to the same tenant
        if (existingField.tenantId !== tenantId) {
          results.push({
            clientId: id,
            status: "error",
            error: "Access denied: field belongs to another tenant",
          });
          continue;
        }

        // Version conflict check
        if (client_version !== undefined && client_version < existingField.version) {
          const serverData = await this.prisma.field.findUnique({
            where: { id_tenantId: { id, tenantId } },
          });

          results.push({
            clientId: id,
            serverId: id,
            status: "conflict",
            server_version: existingField.version,
            etag: generateETag(existingField.id, existingField.version),
            serverData,
          });
          continue;
        }

        // Apply update with version increment for optimistic locking
        const updated = await this.prisma.field.update({
          where: { id_tenantId: { id, tenantId }, version: existingField.version },
          data: {
            version: { increment: 1 },
            ...(fieldData.name && { name: fieldData.name }),
            ...(fieldData.cropType && { cropType: fieldData.cropType }),
            ...(fieldData.status && { status: fieldData.status }),
            ...(fieldData.irrigationType && { irrigationType: fieldData.irrigationType }),
            ...(fieldData.soilType && { soilType: fieldData.soilType }),
            ...(fieldData.metadata && { metadata: fieldData.metadata }),
          },
        });

        results.push({
          clientId: id,
          serverId: updated.id,
          status: "updated",
          server_version: updated.version,
          etag: generateETag(updated.id, updated.version),
        });

        // Invalidate cache (tenant-scoped key)
        await this.cacheService.del(CACHE_KEYS.FIELD(id, tenantId));
      } catch (error) {
        results.push({
          clientId: clientField.id || "unknown",
          status: "error",
          error: error instanceof Error ? error.message : "Unknown error",
        });
      }
    }

    // Update sync status
    await this.updateSyncStatus(deviceId, userId, tenantId, results);

    // Invalidate tenant cache
    await this.cacheService.invalidateTenant(tenantId);

    const successCount = results.filter(
      (r) => r.status === "created" || r.status === "updated",
    ).length;
    const conflictCount = results.filter((r) => r.status === "conflict").length;
    const errorCount = results.filter((r) => r.status === "error").length;

    return {
      results,
      summary: {
        total: results.length,
        created: results.filter((r) => r.status === "created").length,
        updated: results.filter((r) => r.status === "updated").length,
        conflicts: conflictCount,
        errors: errorCount,
        successRate: results.length > 0 ? `${Math.round((successCount / results.length) * 100)}%` : "N/A",
      },
      serverTime: new Date().toISOString(),
    };
  }

  /**
   * Get sync status for a device
   */
  async getSyncStatus(deviceId: string, tenantId: string, userId?: string) {
    const cacheKey = CACHE_KEYS.SYNC_STATUS(deviceId, tenantId);
    const cached = await this.cacheService.get<any>(cacheKey);
    if (cached) return cached;

    const where: any = { deviceId, tenantId };
    if (userId) where.userId = userId;

    const syncStatus = await this.prisma.syncStatus.findFirst({
      where,
    });

    if (!syncStatus) {
      return {
        deviceId,
        tenantId,
        status: "new",
        lastSyncAt: null,
        pendingDownloads: 0,
        conflictsCount: 0,
      };
    }

    // Calculate pending downloads
    let pendingDownloads = 0;
    if (syncStatus.lastSyncAt) {
      pendingDownloads = await this.prisma.field.count({
        where: {
          tenantId,
          updatedAt: { gt: syncStatus.lastSyncAt },
          isDeleted: false,
        },
      });
    } else {
      pendingDownloads = await this.prisma.field.count({
        where: { tenantId, isDeleted: false },
      });
    }

    const result = {
      ...syncStatus,
      pendingDownloads,
    };

    await this.cacheService.set(cacheKey, result, CACHE_TTL.SHORT);

    return result;
  }

  /**
   * Update sync status
   */
  private async updateSyncStatus(
    deviceId: string,
    userId: string,
    tenantId: string,
    results: SyncResult[],
  ) {
    const conflictCount = results.filter((r) => r.status === "conflict").length;

    await this.prisma.syncStatus.upsert({
      where: {
        idx_sync_device_user: { deviceId, userId },
      },
      create: {
        deviceId,
        userId,
        tenantId,
        lastSyncAt: new Date(),
        status: conflictCount > 0 ? SyncState.conflict : SyncState.idle,
        conflictsCount: conflictCount,
      },
      update: {
        lastSyncAt: new Date(),
        status: conflictCount > 0 ? SyncState.conflict : SyncState.idle,
        conflictsCount: conflictCount,
      },
    });

    // Invalidate cache
    await this.cacheService.del(CACHE_KEYS.SYNC_STATUS(deviceId, tenantId));
  }

  /**
   * Update device sync status
   */
  async updateDeviceSyncStatus(params: {
    deviceId: string;
    userId: string;
    tenantId: string;
    lastSyncVersion?: number;
    deviceInfo?: any;
    status?: SyncState | "idle" | "syncing" | "error" | "conflict";
  }) {
    const { deviceId, userId, tenantId, lastSyncVersion, deviceInfo, status } = params;

    const syncStatus = await this.prisma.syncStatus.upsert({
      where: {
        idx_sync_device_user: { deviceId, userId },
      },
      create: {
        deviceId,
        userId,
        tenantId,
        lastSyncAt: new Date(),
        lastSyncVersion: lastSyncVersion || 0,
        deviceInfo,
        status: status ?? SyncState.idle,
      },
      update: {
        lastSyncAt: new Date(),
        ...(lastSyncVersion && { lastSyncVersion }),
        ...(deviceInfo && { deviceInfo }),
        ...(status && { status }),
      },
    });

    // Invalidate cache
    await this.cacheService.del(CACHE_KEYS.SYNC_STATUS(deviceId, tenantId));

    return syncStatus;
  }
}
