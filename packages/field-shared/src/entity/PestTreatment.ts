import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  CreateDateColumn,
  UpdateDateColumn,
  Index,
  ManyToOne,
  JoinColumn,
} from "typeorm";
import { PestIncident } from "./PestIncident";

/**
 * Pest Treatment Entity - علاجات الآفات
 *
 * Records treatment actions taken for pest incidents
 * Tracks application details, effectiveness, and costs
 */
@Entity("pest_treatments")
@Index("idx_pest_treatment_incident", ["incidentId"])
@Index("idx_pest_treatment_tenant", ["tenantId"])
@Index("idx_pest_treatment_date", ["treatmentDate"])
export class PestTreatment {
  @PrimaryGeneratedColumn("uuid")
  id!: string;

  // ─────────────────────────────────────────────────────────────────────────
  // References
  // ─────────────────────────────────────────────────────────────────────────

  @Column({ name: "incident_id", type: "uuid" })
  incidentId!: string;

  @Column({ name: "tenant_id", length: 100 })
  tenantId!: string;

  // ─────────────────────────────────────────────────────────────────────────
  // Treatment Details
  // ─────────────────────────────────────────────────────────────────────────

  @Column({ name: "treatment_date", type: "timestamptz" })
  treatmentDate!: Date;

  @Column({ length: 255 })
  method!: string;

  @Column({ name: "product_used", length: 255 })
  productUsed!: string;

  @Column({ name: "product_id", type: "uuid", nullable: true })
  productId?: string;

  // ─────────────────────────────────────────────────────────────────────────
  // Application Details
  // ─────────────────────────────────────────────────────────────────────────

  @Column({ type: "decimal", precision: 10, scale: 3 })
  quantity!: number;

  @Column({ length: 50 })
  unit!: string;

  @Column({ name: "applied_by", length: 255 })
  appliedBy!: string;

  // ─────────────────────────────────────────────────────────────────────────
  // Results
  // ─────────────────────────────────────────────────────────────────────────

  @Column({ type: "smallint", nullable: true })
  effectiveness?: number; // 1-5 scale

  @Column({ type: "decimal", precision: 10, scale: 2, nullable: true })
  cost?: number;

  @Column({ type: "text", nullable: true })
  notes?: string;

  // ─────────────────────────────────────────────────────────────────────────
  // Relations
  // ─────────────────────────────────────────────────────────────────────────

  @ManyToOne(() => PestIncident, (incident) => incident.treatments, {
    onDelete: "CASCADE",
  })
  @JoinColumn({ name: "incident_id" })
  incident?: PestIncident;

  // ─────────────────────────────────────────────────────────────────────────
  // Timestamps
  // ─────────────────────────────────────────────────────────────────────────

  @CreateDateColumn({ name: "created_at", type: "timestamptz" })
  createdAt!: Date;

  @UpdateDateColumn({ name: "updated_at", type: "timestamptz" })
  updatedAt!: Date;
}
