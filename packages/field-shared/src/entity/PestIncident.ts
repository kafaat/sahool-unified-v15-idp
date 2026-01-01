import {
    Entity,
    PrimaryGeneratedColumn,
    Column,
    CreateDateColumn,
    UpdateDateColumn,
    Index,
    OneToMany
} from "typeorm";
import { PestTreatment } from "./PestTreatment";

/**
 * Pest Type Enumeration
 */
export enum PestType {
    INSECT = "INSECT",
    FUNGUS = "FUNGUS",
    BACTERIA = "BACTERIA",
    VIRUS = "VIRUS",
    WEED = "WEED",
    RODENT = "RODENT",
    BIRD = "BIRD",
    NEMATODE = "NEMATODE",
    OTHER = "OTHER"
}

/**
 * Incident Status Enumeration
 */
export enum IncidentStatus {
    DETECTED = "DETECTED",
    MONITORING = "MONITORING",
    TREATING = "TREATING",
    RESOLVED = "RESOLVED",
    RECURRING = "RECURRING"
}

/**
 * Pest Incident Entity - حوادث الآفات
 *
 * Tracks pest detection and monitoring in agricultural fields
 * Supports multi-tenant isolation and geospatial tracking
 */
@Entity("pest_incidents")
@Index("idx_pest_incident_field", ["fieldId"])
@Index("idx_pest_incident_tenant", ["tenantId"])
@Index("idx_pest_incident_status", ["status"])
@Index("idx_pest_incident_date", ["detectedAt"])
export class PestIncident {

    @PrimaryGeneratedColumn("uuid")
    id!: string;

    // ─────────────────────────────────────────────────────────────────────────
    // References
    // ─────────────────────────────────────────────────────────────────────────

    @Column({ name: "field_id", type: "uuid" })
    fieldId!: string;

    @Column({ name: "crop_season_id", type: "uuid", nullable: true })
    cropSeasonId?: string;

    @Column({ name: "tenant_id", length: 100 })
    tenantId!: string;

    // ─────────────────────────────────────────────────────────────────────────
    // Pest Information
    // ─────────────────────────────────────────────────────────────────────────

    @Column({
        name: "pest_type",
        type: "enum",
        enum: PestType
    })
    pestType!: PestType;

    @Column({ name: "pest_name", length: 255 })
    pestName!: string;

    @Column({ name: "severity_level", type: "int" })
    severityLevel!: number; // 1-5 scale

    @Column({ name: "affected_area", type: "decimal", precision: 10, scale: 4 })
    affectedArea!: number; // hectares

    @Column({
        type: "enum",
        enum: IncidentStatus,
        default: IncidentStatus.DETECTED
    })
    status!: IncidentStatus;

    // ─────────────────────────────────────────────────────────────────────────
    // Detection Details
    // ─────────────────────────────────────────────────────────────────────────

    @Column({ name: "detected_at", type: "timestamptz" })
    detectedAt!: Date;

    @Column({ name: "reported_by", length: 255 })
    reportedBy!: string;

    // ─────────────────────────────────────────────────────────────────────────
    // Location & Evidence
    // ─────────────────────────────────────────────────────────────────────────

    @Column({ type: "jsonb", nullable: true })
    location?: {
        lat: number;
        lng: number;
        coordinates?: number[][];
    };

    @Column({ type: "jsonb", nullable: true })
    photos?: string[];

    @Column({ type: "text", nullable: true })
    notes?: string;

    // ─────────────────────────────────────────────────────────────────────────
    // Relations
    // ─────────────────────────────────────────────────────────────────────────

    @OneToMany(() => PestTreatment, treatment => treatment.incident)
    treatments?: PestTreatment[];

    // ─────────────────────────────────────────────────────────────────────────
    // Timestamps
    // ─────────────────────────────────────────────────────────────────────────

    @CreateDateColumn({ name: "created_at", type: "timestamptz" })
    createdAt!: Date;

    @UpdateDateColumn({ name: "updated_at", type: "timestamptz" })
    updatedAt!: Date;
}
