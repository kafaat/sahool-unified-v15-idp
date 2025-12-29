import {
    Entity,
    PrimaryGeneratedColumn,
    Column,
    CreateDateColumn,
    UpdateDateColumn,
    VersionColumn,
    Index
} from "typeorm";

/**
 * Field Entity - Geospatial Agricultural Field Model
 *
 * Stores field boundaries as PostGIS POLYGON geometry
 * with SRID 4326 (WGS84 - GPS coordinate system)
 *
 * Supports optimistic locking via version column for ETag-based conflict resolution
 */
@Entity("fields")
@Index("idx_field_tenant_status", ["tenantId", "status"])
@Index("idx_field_tenant_created", ["tenantId", "createdAt"])
export class Field {

    @PrimaryGeneratedColumn("uuid")
    id!: string;

    /**
     * Version for optimistic locking (auto-incremented on each update)
     * Used to generate ETag for conflict resolution
     */
    @VersionColumn()
    version!: number;

    @Column({ length: 255 })
    name!: string;

    @Index("idx_field_tenant")
    @Column({ name: "tenant_id" })
    tenantId!: string;

    @Column({ name: "crop_type", length: 100 })
    cropType!: string;

    @Column({ name: "owner_id", nullable: true })
    ownerId?: string;

    /**
     * Geospatial boundary stored as PostGIS POLYGON
     * SRID 4326 = WGS84 (standard GPS coordinates)
     */
    @Index({ spatial: true })
    @Column({
        type: "geometry",
        spatialFeatureType: "Polygon",
        srid: 4326,
        nullable: true
    })
    boundary?: object;

    /**
     * Field centroid for quick map display
     */
    @Column({
        type: "geometry",
        spatialFeatureType: "Point",
        srid: 4326,
        nullable: true
    })
    centroid?: object;

    /**
     * Area in hectares (calculated from boundary)
     */
    @Column({ name: "area_hectares", type: "decimal", precision: 10, scale: 4, default: 0 })
    areaHectares!: number;

    /**
     * Current health score (0.0 - 1.0)
     * Updated by NDVI Engine
     */
    @Column({ name: "health_score", type: "decimal", precision: 3, scale: 2, default: 0 })
    healthScore!: number;

    /**
     * Latest NDVI value (-1.0 to 1.0)
     */
    @Column({ name: "ndvi_value", type: "decimal", precision: 4, scale: 3, nullable: true })
    ndviValue?: number;

    /**
     * Field status
     */
    @Column({
        type: "enum",
        enum: ["active", "fallow", "harvested", "preparing"],
        default: "active"
    })
    status!: string;

    /**
     * Planting date for current crop
     */
    @Column({ name: "planting_date", type: "date", nullable: true })
    plantingDate?: Date;

    /**
     * Expected harvest date
     */
    @Column({ name: "expected_harvest", type: "date", nullable: true })
    expectedHarvest?: Date;

    /**
     * Irrigation type
     */
    @Column({ name: "irrigation_type", length: 50, nullable: true })
    irrigationType?: string;

    /**
     * Soil type classification
     */
    @Column({ name: "soil_type", length: 100, nullable: true })
    soilType?: string;

    /**
     * Additional metadata as JSON
     */
    @Column({ type: "jsonb", nullable: true })
    metadata?: object;

    @CreateDateColumn({ name: "created_at" })
    createdAt!: Date;

    @Index("idx_field_updated_at")
    @UpdateDateColumn({ name: "updated_at" })
    updatedAt!: Date;
}
