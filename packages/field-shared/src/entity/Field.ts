import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  VersionColumn,
  Index,
  ManyToOne,
  JoinColumn,
} from 'typeorm';

/**
 * Field Entity - Geospatial Agricultural Field Model
 *
 * Stores field boundaries as PostGIS POLYGON geometry
 * with SRID 4326 (WGS84 - GPS coordinate system)
 *
 * Supports optimistic locking via version column for ETag-based conflict resolution
 *
 * IMPORTANT: Source of truth is the Prisma schema in field-management-service.
 * This TypeORM entity is kept aligned for services using TypeORM.
 * Any schema changes should be made in Prisma first, then reflected here.
 *
 * @see apps/services/field-management-service/prisma/schema.prisma
 * @see packages/shared-types/src/field.ts
 */
@Entity('fields')
export class Field {
  @PrimaryGeneratedColumn('uuid')
  id!: string;

  /**
   * Version for optimistic locking (auto-incremented on each update)
   * Used to generate ETag for conflict resolution
   */
  @VersionColumn()
  version!: number;

  @Column({ length: 255 })
  name!: string;

  @Column({ name: 'tenant_id', length: 100 })
  tenantId!: string;

  @Column({ name: 'crop_type', length: 100, nullable: true })
  cropType?: string;

  @Column({ name: 'owner_id', type: 'uuid', nullable: true })
  ownerId?: string;

  @Column({ name: 'farm_id', type: 'uuid', nullable: true })
  farmId?: string;

  /**
   * Geospatial boundary stored as PostGIS POLYGON
   * SRID 4326 = WGS84 (standard GPS coordinates)
   */
  @Index({ spatial: true })
  @Column({
    type: 'geometry',
    spatialFeatureType: 'Polygon',
    srid: 4326,
    nullable: true,
  })
  boundary?: object;

  /**
   * Field centroid for quick map display
   */
  @Column({
    type: 'geometry',
    spatialFeatureType: 'Point',
    srid: 4326,
    nullable: true,
  })
  centroid?: object;

  /**
   * Area in hectares (calculated from boundary)
   */
  @Column({
    name: 'area_hectares',
    type: 'decimal',
    precision: 10,
    scale: 4,
    nullable: true,
  })
  areaHectares?: number;

  /**
   * Current health score (0.0 - 1.0)
   * Updated by NDVI Engine
   */
  @Column({
    name: 'health_score',
    type: 'decimal',
    precision: 3,
    scale: 2,
    nullable: true,
  })
  healthScore?: number;

  /**
   * Latest NDVI value (-1.0 to 1.0)
   */
  @Column({
    name: 'ndvi_value',
    type: 'decimal',
    precision: 4,
    scale: 3,
    nullable: true,
  })
  ndviValue?: number;

  /**
   * Field status
   */
  @Column({
    type: 'enum',
    enum: ['active', 'fallow', 'harvested', 'preparing', 'inactive'],
    default: 'active',
  })
  status!: string;

  /**
   * Planting date for current crop
   */
  @Column({ name: 'planting_date', type: 'date', nullable: true })
  plantingDate?: Date;

  /**
   * Expected harvest date
   */
  @Column({ name: 'expected_harvest', type: 'date', nullable: true })
  expectedHarvest?: Date;

  /**
   * Irrigation type
   */
  @Column({ name: 'irrigation_type', length: 50, nullable: true })
  irrigationType?: string;

  /**
   * Soil type classification
   */
  @Column({ name: 'soil_type', length: 100, nullable: true })
  soilType?: string;

  /**
   * Additional metadata as JSON
   */
  @Column({ type: 'jsonb', nullable: true })
  metadata?: object;

  // ─── Sync Metadata (offline-first support) ─────────────────────────────────

  /**
   * Soft delete flag
   */
  @Column({ name: 'is_deleted', default: false })
  isDeleted!: boolean;

  /**
   * Server-side last update timestamp for sync
   */
  @Column({
    name: 'server_updated_at',
    type: 'timestamptz',
    default: () => 'now()',
  })
  serverUpdatedAt!: Date;

  /**
   * ETag for conflict resolution (auto-generated UUID)
   */
  @Column({ length: 64, nullable: true })
  etag?: string;

  // ─── Timestamps ────────────────────────────────────────────────────────────

  @CreateDateColumn({ name: 'created_at', type: 'timestamptz' })
  createdAt!: Date;

  @UpdateDateColumn({ name: 'updated_at', type: 'timestamptz' })
  updatedAt!: Date;
}
