import {
    Entity,
    PrimaryGeneratedColumn,
    Column,
    CreateDateColumn,
    Index,
    ManyToOne,
    JoinColumn
} from "typeorm";
import { Field } from "./Field";

/**
 * Field Boundary History Entity
 *
 * Tracks all boundary changes for audit and rollback purposes
 * Each change is stored with the user who made it and reason
 */
@Entity("field_boundary_history")
export class FieldBoundaryHistory {

    @PrimaryGeneratedColumn("uuid")
    id!: string;

    @Column({ name: "field_id" })
    @Index()
    fieldId!: string;

    @ManyToOne(() => Field, { onDelete: "CASCADE" })
    @JoinColumn({ name: "field_id" })
    field!: Field;

    /**
     * Version number at time of change
     */
    @Column({ name: "version_at_change" })
    versionAtChange!: number;

    /**
     * Previous boundary (before change)
     */
    @Column({
        type: "geometry",
        spatialFeatureType: "Polygon",
        srid: 4326,
        nullable: true,
        name: "previous_boundary"
    })
    previousBoundary?: object;

    /**
     * New boundary (after change)
     */
    @Column({
        type: "geometry",
        spatialFeatureType: "Polygon",
        srid: 4326,
        nullable: true,
        name: "new_boundary"
    })
    newBoundary?: object;

    /**
     * Area change in hectares (positive = increase, negative = decrease)
     */
    @Column({ name: "area_change_hectares", type: "decimal", precision: 10, scale: 4, default: 0 })
    areaChangeHectares!: number;

    /**
     * User who made the change
     */
    @Column({ name: "changed_by", nullable: true })
    changedBy?: string;

    /**
     * Change reason/description
     */
    @Column({ name: "change_reason", length: 500, nullable: true })
    changeReason?: string;

    /**
     * Source of the change (mobile, web, api, system)
     */
    @Column({ name: "change_source", length: 50, default: "api" })
    changeSource!: string;

    /**
     * Device ID for mobile changes
     */
    @Column({ name: "device_id", nullable: true })
    deviceId?: string;

    @Index("idx_history_created_at")
    @CreateDateColumn({ name: "created_at" })
    createdAt!: Date;
}
