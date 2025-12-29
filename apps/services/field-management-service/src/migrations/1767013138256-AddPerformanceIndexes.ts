import { MigrationInterface, QueryRunner } from "typeorm";

/**
 * Migration: Add Performance Indexes
 *
 * Adds composite and temporal indexes to improve query performance across all entities
 *
 * Indexes Added:
 * - Fields: Composite indexes on [tenantId, status], [tenantId, createdAt], and temporal index on updatedAt
 * - FieldBoundaryHistory: Temporal index on createdAt
 * - SyncStatus: Composite indexes on [userId, tenantId], [deviceId, tenantId], [tenantId, updatedAt], and temporal index on updatedAt
 */
export class AddPerformanceIndexes1767013138256 implements MigrationInterface {
    name = 'AddPerformanceIndexes1767013138256'

    public async up(queryRunner: QueryRunner): Promise<void> {
        // =====================================================================
        // Fields Table Indexes
        // =====================================================================

        // Composite index for tenant-scoped status queries (e.g., active fields by tenant)
        await queryRunner.query(`
            CREATE INDEX IF NOT EXISTS "idx_field_tenant_status"
            ON "fields" ("tenant_id", "status")
        `);

        // Composite index for tenant-scoped creation date queries (e.g., recent fields by tenant)
        await queryRunner.query(`
            CREATE INDEX IF NOT EXISTS "idx_field_tenant_created"
            ON "fields" ("tenant_id", "created_at")
        `);

        // Temporal index for sync queries and general updated_at filtering
        await queryRunner.query(`
            CREATE INDEX IF NOT EXISTS "idx_field_updated_at"
            ON "fields" ("updated_at")
        `);

        // Single column index on tenant_id (if not already exists from entity definition)
        await queryRunner.query(`
            CREATE INDEX IF NOT EXISTS "idx_field_tenant"
            ON "fields" ("tenant_id")
        `);

        // =====================================================================
        // Field Boundary History Table Indexes
        // =====================================================================

        // Temporal index for audit queries and history lookups
        await queryRunner.query(`
            CREATE INDEX IF NOT EXISTS "idx_history_created_at"
            ON "field_boundary_history" ("created_at")
        `);

        // =====================================================================
        // Sync Status Table Indexes
        // =====================================================================

        // Composite index for user-tenant queries (e.g., get sync status for user in tenant)
        await queryRunner.query(`
            CREATE INDEX IF NOT EXISTS "idx_sync_user_tenant"
            ON "sync_status" ("user_id", "tenant_id")
        `);

        // Composite index for device-tenant queries (e.g., get sync status for device in tenant)
        await queryRunner.query(`
            CREATE INDEX IF NOT EXISTS "idx_sync_device_tenant"
            ON "sync_status" ("device_id", "tenant_id")
        `);

        // Composite index for tenant-scoped temporal queries (e.g., recently updated sync statuses by tenant)
        await queryRunner.query(`
            CREATE INDEX IF NOT EXISTS "idx_sync_tenant_updated"
            ON "sync_status" ("tenant_id", "updated_at")
        `);

        // Temporal index for general updated_at filtering
        await queryRunner.query(`
            CREATE INDEX IF NOT EXISTS "idx_sync_updated_at"
            ON "sync_status" ("updated_at")
        `);
    }

    public async down(queryRunner: QueryRunner): Promise<void> {
        // =====================================================================
        // Remove all indexes in reverse order
        // =====================================================================

        // Sync Status Indexes
        await queryRunner.query(`DROP INDEX IF EXISTS "idx_sync_updated_at"`);
        await queryRunner.query(`DROP INDEX IF EXISTS "idx_sync_tenant_updated"`);
        await queryRunner.query(`DROP INDEX IF EXISTS "idx_sync_device_tenant"`);
        await queryRunner.query(`DROP INDEX IF EXISTS "idx_sync_user_tenant"`);

        // Field Boundary History Indexes
        await queryRunner.query(`DROP INDEX IF EXISTS "idx_history_created_at"`);

        // Fields Indexes
        await queryRunner.query(`DROP INDEX IF EXISTS "idx_field_tenant"`);
        await queryRunner.query(`DROP INDEX IF EXISTS "idx_field_updated_at"`);
        await queryRunner.query(`DROP INDEX IF EXISTS "idx_field_tenant_created"`);
        await queryRunner.query(`DROP INDEX IF EXISTS "idx_field_tenant_status"`);
    }
}
