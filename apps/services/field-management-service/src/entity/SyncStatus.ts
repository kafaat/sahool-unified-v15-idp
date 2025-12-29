import {
    Entity,
    PrimaryGeneratedColumn,
    Column,
    CreateDateColumn,
    UpdateDateColumn,
    Index
} from "typeorm";

/**
 * Sync Status Entity
 *
 * Tracks sync status per device/user for mobile offline-first support
 * Used to determine what data needs to be synced on reconnection
 */
@Entity("sync_status")
@Index("idx_sync_user_tenant", ["userId", "tenantId"])
@Index("idx_sync_device_tenant", ["deviceId", "tenantId"])
@Index("idx_sync_tenant_updated", ["tenantId", "updatedAt"])
export class SyncStatus {

    @PrimaryGeneratedColumn("uuid")
    id!: string;

    /**
     * Device unique identifier
     */
    @Column({ name: "device_id" })
    @Index()
    deviceId!: string;

    /**
     * User ID associated with the device
     */
    @Column({ name: "user_id" })
    @Index()
    userId!: string;

    /**
     * Tenant ID for multi-tenancy
     */
    @Column({ name: "tenant_id" })
    @Index()
    tenantId!: string;

    /**
     * Last successful sync timestamp
     * Used for delta sync calculations
     */
    @Column({ name: "last_sync_at", type: "timestamp with time zone", nullable: true })
    lastSyncAt?: Date;

    /**
     * Last sync version marker
     */
    @Column({ name: "last_sync_version", type: "bigint", default: 0 })
    lastSyncVersion!: number;

    /**
     * Number of pending uploads from device
     */
    @Column({ name: "pending_uploads", default: 0 })
    pendingUploads!: number;

    /**
     * Number of pending downloads to device
     */
    @Column({ name: "pending_downloads", default: 0 })
    pendingDownloads!: number;

    /**
     * Number of conflicts requiring resolution
     */
    @Column({ name: "conflicts_count", default: 0 })
    conflictsCount!: number;

    /**
     * Sync status: idle, syncing, error, conflict
     */
    @Column({
        type: "enum",
        enum: ["idle", "syncing", "error", "conflict"],
        default: "idle"
    })
    status!: string;

    /**
     * Last error message if any
     */
    @Column({ name: "last_error", type: "text", nullable: true })
    lastError?: string;

    /**
     * Device info for debugging
     */
    @Column({ name: "device_info", type: "jsonb", nullable: true })
    deviceInfo?: object;

    @CreateDateColumn({ name: "created_at" })
    createdAt!: Date;

    @Index("idx_sync_updated_at")
    @UpdateDateColumn({ name: "updated_at" })
    updatedAt!: Date;
}
