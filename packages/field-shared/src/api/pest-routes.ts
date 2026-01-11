/**
 * SAHOOL Pest Management API Routes
 * Provides REST endpoints for pest incident and treatment management
 */

import { Router, Request, Response } from "express";
import { AppDataSource } from "../data-source";
import { PestIncident, PestType, IncidentStatus } from "../entity/PestIncident";
import { PestTreatment } from "../entity/PestTreatment";

export const pestRoutes = Router();

// ═════════════════════════════════════════════════════════════════════════════
// PEST INCIDENT ENDPOINTS
// ═════════════════════════════════════════════════════════════════════════════

/**
 * GET /api/v1/pests/incidents
 * List all pest incidents with optional filtering
 */
pestRoutes.get("/incidents", async (req: Request, res: Response) => {
    try {
        const incidentRepo = AppDataSource.getRepository(PestIncident);
        const {
            tenantId,
            fieldId,
            cropSeasonId,
            status,
            pestType,
            limit = 100,
            offset = 0
        } = req.query;

        const queryBuilder = incidentRepo.createQueryBuilder("incident");

        if (tenantId) {
            queryBuilder.andWhere("incident.tenantId = :tenantId", { tenantId });
        }
        if (fieldId) {
            queryBuilder.andWhere("incident.fieldId = :fieldId", { fieldId });
        }
        if (cropSeasonId) {
            queryBuilder.andWhere("incident.cropSeasonId = :cropSeasonId", { cropSeasonId });
        }
        if (status) {
            queryBuilder.andWhere("incident.status = :status", { status });
        }
        if (pestType) {
            queryBuilder.andWhere("incident.pestType = :pestType", { pestType });
        }

        const [incidents, total] = await queryBuilder
            .orderBy("incident.detectedAt", "DESC")
            .skip(Number(offset))
            .take(Number(limit))
            .getManyAndCount();

        res.json({
            success: true,
            data: incidents,
            pagination: {
                total,
                limit: Number(limit),
                offset: Number(offset)
            }
        });
    } catch (error) {
        console.error("Error fetching pest incidents:", error);
        res.status(500).json({
            success: false,
            error: "Failed to fetch pest incidents",
            error_ar: "فشل في جلب حوادث الآفات"
        });
    }
});

/**
 * GET /api/v1/pests/incidents/:id
 * Get a single pest incident by ID with treatments
 */
pestRoutes.get("/incidents/:id", async (req: Request, res: Response) => {
    try {
        const id = Array.isArray(req.params.id) ? req.params.id[0] : req.params.id;
        const incidentRepo = AppDataSource.getRepository(PestIncident);
        const incident = await incidentRepo.findOne({
            where: { id },
            relations: ["treatments"]
        });

        if (!incident) {
            return res.status(404).json({
                success: false,
                error: "Pest incident not found",
                error_ar: "حادثة الآفة غير موجودة"
            });
        }

        res.json({
            success: true,
            data: incident
        });
    } catch (error) {
        console.error("Error fetching pest incident:", error);
        res.status(500).json({
            success: false,
            error: "Failed to fetch pest incident",
            error_ar: "فشل في جلب حادثة الآفة"
        });
    }
});

/**
 * POST /api/v1/pests/incidents
 * Report a new pest incident
 */
pestRoutes.post("/incidents", async (req: Request, res: Response) => {
    try {
        const incidentRepo = AppDataSource.getRepository(PestIncident);
        const {
            fieldId,
            cropSeasonId,
            tenantId,
            pestType,
            pestName,
            severityLevel,
            affectedArea,
            detectedAt,
            reportedBy,
            location,
            photos,
            notes,
            status
        } = req.body;

        // Validate required fields
        if (!fieldId || !tenantId || !pestType || !pestName || !severityLevel || !affectedArea || !detectedAt || !reportedBy) {
            return res.status(400).json({
                success: false,
                error: "Missing required fields: fieldId, tenantId, pestType, pestName, severityLevel, affectedArea, detectedAt, reportedBy",
                error_ar: "حقول مطلوبة مفقودة"
            });
        }

        // Validate severity level (1-5)
        if (severityLevel < 1 || severityLevel > 5) {
            return res.status(400).json({
                success: false,
                error: "Severity level must be between 1 and 5",
                error_ar: "يجب أن يكون مستوى الخطورة بين 1 و 5"
            });
        }

        // Validate pest type
        if (!Object.values(PestType).includes(pestType)) {
            return res.status(400).json({
                success: false,
                error: `Invalid pest type. Must be one of: ${Object.values(PestType).join(", ")}`,
                error_ar: "نوع الآفة غير صالح"
            });
        }

        // Validate status if provided
        if (status && !Object.values(IncidentStatus).includes(status)) {
            return res.status(400).json({
                success: false,
                error: `Invalid status. Must be one of: ${Object.values(IncidentStatus).join(", ")}`,
                error_ar: "الحالة غير صالحة"
            });
        }

        // Create pest incident
        const newIncident = incidentRepo.create({
            fieldId,
            cropSeasonId,
            tenantId,
            pestType,
            pestName,
            severityLevel,
            affectedArea,
            detectedAt: new Date(detectedAt),
            reportedBy,
            location,
            photos,
            notes,
            status: status || IncidentStatus.DETECTED
        });

        const savedIncident = await incidentRepo.save(newIncident);

        res.status(201).json({
            success: true,
            data: savedIncident,
            message: "Pest incident reported successfully",
            message_ar: "تم الإبلاغ عن حادثة الآفة بنجاح"
        });
    } catch (error) {
        console.error("Error creating pest incident:", error);
        res.status(500).json({
            success: false,
            error: "Failed to create pest incident",
            error_ar: "فشل في إنشاء حادثة الآفة"
        });
    }
});

/**
 * PUT /api/v1/pests/incidents/:id
 * Update a pest incident
 */
pestRoutes.put("/incidents/:id", async (req: Request, res: Response) => {
    try {
        const id = Array.isArray(req.params.id) ? req.params.id[0] : req.params.id;
        const incidentRepo = AppDataSource.getRepository(PestIncident);
        const incident = await incidentRepo.findOne({
            where: { id }
        });

        if (!incident) {
            return res.status(404).json({
                success: false,
                error: "Pest incident not found",
                error_ar: "حادثة الآفة غير موجودة"
            });
        }

        const {
            pestType,
            pestName,
            severityLevel,
            affectedArea,
            status,
            location,
            photos,
            notes
        } = req.body;

        // Validate severity level if provided
        if (severityLevel !== undefined && (severityLevel < 1 || severityLevel > 5)) {
            return res.status(400).json({
                success: false,
                error: "Severity level must be between 1 and 5",
                error_ar: "يجب أن يكون مستوى الخطورة بين 1 و 5"
            });
        }

        // Validate pest type if provided
        if (pestType && !Object.values(PestType).includes(pestType)) {
            return res.status(400).json({
                success: false,
                error: `Invalid pest type. Must be one of: ${Object.values(PestType).join(", ")}`,
                error_ar: "نوع الآفة غير صالح"
            });
        }

        // Validate status if provided
        if (status && !Object.values(IncidentStatus).includes(status)) {
            return res.status(400).json({
                success: false,
                error: `Invalid status. Must be one of: ${Object.values(IncidentStatus).join(", ")}`,
                error_ar: "الحالة غير صالحة"
            });
        }

        // Update fields
        if (pestType !== undefined) incident.pestType = pestType;
        if (pestName !== undefined) incident.pestName = pestName;
        if (severityLevel !== undefined) incident.severityLevel = severityLevel;
        if (affectedArea !== undefined) incident.affectedArea = affectedArea;
        if (status !== undefined) incident.status = status;
        if (location !== undefined) incident.location = location;
        if (photos !== undefined) incident.photos = photos;
        if (notes !== undefined) incident.notes = notes;

        const updatedIncident = await incidentRepo.save(incident);

        res.json({
            success: true,
            data: updatedIncident,
            message: "Pest incident updated successfully",
            message_ar: "تم تحديث حادثة الآفة بنجاح"
        });
    } catch (error) {
        console.error("Error updating pest incident:", error);
        res.status(500).json({
            success: false,
            error: "Failed to update pest incident",
            error_ar: "فشل في تحديث حادثة الآفة"
        });
    }
});

/**
 * PATCH /api/v1/pests/incidents/:id/status
 * Update pest incident status only
 */
pestRoutes.patch("/incidents/:id/status", async (req: Request, res: Response) => {
    try {
        const id = Array.isArray(req.params.id) ? req.params.id[0] : req.params.id;
        const incidentRepo = AppDataSource.getRepository(PestIncident);
        const incident = await incidentRepo.findOne({
            where: { id }
        });

        if (!incident) {
            return res.status(404).json({
                success: false,
                error: "Pest incident not found",
                error_ar: "حادثة الآفة غير موجودة"
            });
        }

        const { status } = req.body;

        if (!status || !Object.values(IncidentStatus).includes(status)) {
            return res.status(400).json({
                success: false,
                error: `Invalid status. Must be one of: ${Object.values(IncidentStatus).join(", ")}`,
                error_ar: "الحالة غير صالحة"
            });
        }

        incident.status = status;
        const updatedIncident = await incidentRepo.save(incident);

        res.json({
            success: true,
            data: updatedIncident,
            message: "Pest incident status updated successfully",
            message_ar: "تم تحديث حالة حادثة الآفة بنجاح"
        });
    } catch (error) {
        console.error("Error updating pest incident status:", error);
        res.status(500).json({
            success: false,
            error: "Failed to update pest incident status",
            error_ar: "فشل في تحديث حالة حادثة الآفة"
        });
    }
});

/**
 * DELETE /api/v1/pests/incidents/:id
 * Delete a pest incident
 */
pestRoutes.delete("/incidents/:id", async (req: Request, res: Response) => {
    try {
        const id = Array.isArray(req.params.id) ? req.params.id[0] : req.params.id;
        const incidentRepo = AppDataSource.getRepository(PestIncident);
        const incident = await incidentRepo.findOne({
            where: { id }
        });

        if (!incident) {
            return res.status(404).json({
                success: false,
                error: "Pest incident not found",
                error_ar: "حادثة الآفة غير موجودة"
            });
        }

        await incidentRepo.remove(incident);

        res.json({
            success: true,
            message: "Pest incident deleted successfully",
            message_ar: "تم حذف حادثة الآفة بنجاح"
        });
    } catch (error) {
        console.error("Error deleting pest incident:", error);
        res.status(500).json({
            success: false,
            error: "Failed to delete pest incident",
            error_ar: "فشل في حذف حادثة الآفة"
        });
    }
});

// ═════════════════════════════════════════════════════════════════════════════
// PEST TREATMENT ENDPOINTS
// ═════════════════════════════════════════════════════════════════════════════

/**
 * GET /api/v1/pests/treatments
 * List all pest treatments with optional filtering
 */
pestRoutes.get("/treatments", async (req: Request, res: Response) => {
    try {
        const treatmentRepo = AppDataSource.getRepository(PestTreatment);
        const {
            tenantId,
            incidentId,
            limit = 100,
            offset = 0
        } = req.query;

        const queryBuilder = treatmentRepo.createQueryBuilder("treatment");

        if (tenantId) {
            queryBuilder.andWhere("treatment.tenantId = :tenantId", { tenantId });
        }
        if (incidentId) {
            queryBuilder.andWhere("treatment.incidentId = :incidentId", { incidentId });
        }

        const [treatments, total] = await queryBuilder
            .leftJoinAndSelect("treatment.incident", "incident")
            .orderBy("treatment.treatmentDate", "DESC")
            .skip(Number(offset))
            .take(Number(limit))
            .getManyAndCount();

        res.json({
            success: true,
            data: treatments,
            pagination: {
                total,
                limit: Number(limit),
                offset: Number(offset)
            }
        });
    } catch (error) {
        console.error("Error fetching pest treatments:", error);
        res.status(500).json({
            success: false,
            error: "Failed to fetch pest treatments",
            error_ar: "فشل في جلب علاجات الآفات"
        });
    }
});

/**
 * GET /api/v1/pests/treatments/:id
 * Get a single pest treatment by ID
 */
pestRoutes.get("/treatments/:id", async (req: Request, res: Response) => {
    try {
        const id = Array.isArray(req.params.id) ? req.params.id[0] : req.params.id;
        const treatmentRepo = AppDataSource.getRepository(PestTreatment);
        const treatment = await treatmentRepo.findOne({
            where: { id },
            relations: ["incident"]
        });

        if (!treatment) {
            return res.status(404).json({
                success: false,
                error: "Pest treatment not found",
                error_ar: "علاج الآفة غير موجود"
            });
        }

        res.json({
            success: true,
            data: treatment
        });
    } catch (error) {
        console.error("Error fetching pest treatment:", error);
        res.status(500).json({
            success: false,
            error: "Failed to fetch pest treatment",
            error_ar: "فشل في جلب علاج الآفة"
        });
    }
});

/**
 * POST /api/v1/pests/treatments
 * Record a new pest treatment
 */
pestRoutes.post("/treatments", async (req: Request, res: Response) => {
    try {
        const treatmentRepo = AppDataSource.getRepository(PestTreatment);
        const incidentRepo = AppDataSource.getRepository(PestIncident);
        const {
            incidentId,
            tenantId,
            treatmentDate,
            method,
            productUsed,
            productId,
            quantity,
            unit,
            appliedBy,
            effectiveness,
            cost,
            notes
        } = req.body;

        // Validate required fields
        if (!incidentId || !tenantId || !treatmentDate || !method || !productUsed || !quantity || !unit || !appliedBy) {
            return res.status(400).json({
                success: false,
                error: "Missing required fields: incidentId, tenantId, treatmentDate, method, productUsed, quantity, unit, appliedBy",
                error_ar: "حقول مطلوبة مفقودة"
            });
        }

        // Verify incident exists
        const incident = await incidentRepo.findOne({
            where: { id: incidentId }
        });

        if (!incident) {
            return res.status(404).json({
                success: false,
                error: "Pest incident not found",
                error_ar: "حادثة الآفة غير موجودة"
            });
        }

        // Validate effectiveness if provided (1-5)
        if (effectiveness !== undefined && (effectiveness < 1 || effectiveness > 5)) {
            return res.status(400).json({
                success: false,
                error: "Effectiveness must be between 1 and 5",
                error_ar: "يجب أن تكون الفعالية بين 1 و 5"
            });
        }

        // Create pest treatment
        const newTreatment = treatmentRepo.create({
            incidentId,
            tenantId,
            treatmentDate: new Date(treatmentDate),
            method,
            productUsed,
            productId,
            quantity,
            unit,
            appliedBy,
            effectiveness,
            cost,
            notes
        });

        const savedTreatment = await treatmentRepo.save(newTreatment);

        // If treatment is applied, update incident status to TREATING
        if (incident.status === IncidentStatus.DETECTED) {
            incident.status = IncidentStatus.TREATING;
            await incidentRepo.save(incident);
        }

        res.status(201).json({
            success: true,
            data: savedTreatment,
            message: "Pest treatment recorded successfully",
            message_ar: "تم تسجيل علاج الآفة بنجاح"
        });
    } catch (error) {
        console.error("Error creating pest treatment:", error);
        res.status(500).json({
            success: false,
            error: "Failed to create pest treatment",
            error_ar: "فشل في إنشاء علاج الآفة"
        });
    }
});

/**
 * PUT /api/v1/pests/treatments/:id
 * Update a pest treatment
 */
pestRoutes.put("/treatments/:id", async (req: Request, res: Response) => {
    try {
        const id = Array.isArray(req.params.id) ? req.params.id[0] : req.params.id;
        const treatmentRepo = AppDataSource.getRepository(PestTreatment);
        const treatment = await treatmentRepo.findOne({
            where: { id }
        });

        if (!treatment) {
            return res.status(404).json({
                success: false,
                error: "Pest treatment not found",
                error_ar: "علاج الآفة غير موجود"
            });
        }

        const {
            treatmentDate,
            method,
            productUsed,
            productId,
            quantity,
            unit,
            appliedBy,
            effectiveness,
            cost,
            notes
        } = req.body;

        // Validate effectiveness if provided
        if (effectiveness !== undefined && (effectiveness < 1 || effectiveness > 5)) {
            return res.status(400).json({
                success: false,
                error: "Effectiveness must be between 1 and 5",
                error_ar: "يجب أن تكون الفعالية بين 1 و 5"
            });
        }

        // Update fields
        if (treatmentDate !== undefined) treatment.treatmentDate = new Date(treatmentDate);
        if (method !== undefined) treatment.method = method;
        if (productUsed !== undefined) treatment.productUsed = productUsed;
        if (productId !== undefined) treatment.productId = productId;
        if (quantity !== undefined) treatment.quantity = quantity;
        if (unit !== undefined) treatment.unit = unit;
        if (appliedBy !== undefined) treatment.appliedBy = appliedBy;
        if (effectiveness !== undefined) treatment.effectiveness = effectiveness;
        if (cost !== undefined) treatment.cost = cost;
        if (notes !== undefined) treatment.notes = notes;

        const updatedTreatment = await treatmentRepo.save(treatment);

        res.json({
            success: true,
            data: updatedTreatment,
            message: "Pest treatment updated successfully",
            message_ar: "تم تحديث علاج الآفة بنجاح"
        });
    } catch (error) {
        console.error("Error updating pest treatment:", error);
        res.status(500).json({
            success: false,
            error: "Failed to update pest treatment",
            error_ar: "فشل في تحديث علاج الآفة"
        });
    }
});

/**
 * DELETE /api/v1/pests/treatments/:id
 * Delete a pest treatment
 */
pestRoutes.delete("/treatments/:id", async (req: Request, res: Response) => {
    try {
        const id = Array.isArray(req.params.id) ? req.params.id[0] : req.params.id;
        const treatmentRepo = AppDataSource.getRepository(PestTreatment);
        const treatment = await treatmentRepo.findOne({
            where: { id }
        });

        if (!treatment) {
            return res.status(404).json({
                success: false,
                error: "Pest treatment not found",
                error_ar: "علاج الآفة غير موجود"
            });
        }

        await treatmentRepo.remove(treatment);

        res.json({
            success: true,
            message: "Pest treatment deleted successfully",
            message_ar: "تم حذف علاج الآفة بنجاح"
        });
    } catch (error) {
        console.error("Error deleting pest treatment:", error);
        res.status(500).json({
            success: false,
            error: "Failed to delete pest treatment",
            error_ar: "فشل في حذف علاج الآفة"
        });
    }
});

/**
 * GET /api/v1/pests/incidents/:incidentId/treatments
 * Get all treatments for a specific incident
 */
pestRoutes.get("/incidents/:incidentId/treatments", async (req: Request, res: Response) => {
    try {
        const incidentId = Array.isArray(req.params.incidentId) ? req.params.incidentId[0] : req.params.incidentId;
        const treatmentRepo = AppDataSource.getRepository(PestTreatment);

        const treatments = await treatmentRepo.find({
            where: { incidentId },
            order: { treatmentDate: "DESC" }
        });

        res.json({
            success: true,
            data: treatments,
            count: treatments.length
        });
    } catch (error) {
        console.error("Error fetching incident treatments:", error);
        res.status(500).json({
            success: false,
            error: "Failed to fetch incident treatments",
            error_ar: "فشل في جلب علاجات الحادثة"
        });
    }
});
