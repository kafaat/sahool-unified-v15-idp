/**
 * Task and Operations API Routes
 * Field operations and task management
 *
 * Migrated from field-ops Python service to TypeScript
 */

import { Router, Request, Response } from "express";
import { v4 as uuidv4 } from "uuid";

const router = Router();

// ============================================================================
// Types and Interfaces
// ============================================================================

interface OperationCreate {
  tenant_id: string;
  field_id: string;
  operation_type: string; // planting, irrigation, fertilizing, harvesting, etc.
  scheduled_date?: string;
  notes?: string;
  metadata?: Record<string, any>;
}

interface OperationResponse {
  id: string;
  field_id: string;
  tenant_id: string;
  operation_type: string;
  status: string;
  scheduled_date?: string;
  completed_date?: string;
  notes?: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// In-Memory Storage (Demo)
// ============================================================================

const _operations: Map<string, OperationResponse> = new Map();

// ============================================================================
// Operations Endpoints
// ============================================================================

/**
 * POST /operations
 * Create a field operation
 */
router.post("/operations", async (req: Request, res: Response) => {
  try {
    const op = req.body as OperationCreate;

    // Validate required fields
    if (!op.tenant_id || !op.field_id || !op.operation_type) {
      return res.status(400).json({
        success: false,
        error: "Missing required fields: tenant_id, field_id, operation_type",
      });
    }

    const opId = uuidv4();
    const now = new Date().toISOString();

    const opData: OperationResponse = {
      id: opId,
      tenant_id: op.tenant_id,
      field_id: op.field_id,
      operation_type: op.operation_type,
      status: "scheduled",
      scheduled_date: op.scheduled_date,
      completed_date: undefined,
      notes: op.notes,
      metadata: op.metadata || {},
      created_at: now,
      updated_at: now,
    };

    _operations.set(opId, opData);

    res.status(201).json({
      success: true,
      data: opData,
    });
  } catch (error) {
    console.error("Error creating operation:", error);
    res.status(500).json({
      success: false,
      error: "Failed to create operation",
    });
  }
});

/**
 * GET /operations/:id
 * Get operation by ID
 */
router.get("/operations/:id", async (req: Request, res: Response) => {
  try {
    const id = Array.isArray(req.params.id) ? req.params.id[0] : req.params.id;
    const operation = _operations.get(id);

    if (!operation) {
      return res.status(404).json({
        success: false,
        error: "Operation not found",
      });
    }

    res.json({
      success: true,
      data: operation,
    });
  } catch (error) {
    console.error("Error fetching operation:", error);
    res.status(500).json({
      success: false,
      error: "Failed to fetch operation",
    });
  }
});

/**
 * GET /operations
 * List operations for a field
 */
router.get("/operations", async (req: Request, res: Response) => {
  try {
    const { field_id, status, tenant_id, skip = 0, limit = 50 } = req.query;

    if (!field_id && !tenant_id) {
      return res.status(400).json({
        success: false,
        error: "Missing required parameter: field_id or tenant_id",
      });
    }

    let operations = Array.from(_operations.values());

    // Filter by field_id
    if (field_id) {
      operations = operations.filter((o) => o.field_id === field_id);
    }

    // Filter by tenant_id
    if (tenant_id) {
      operations = operations.filter((o) => o.tenant_id === tenant_id);
    }

    // Filter by status
    if (status) {
      operations = operations.filter((o) => o.status === status);
    }

    const total = operations.length;
    const skipNum = Number(skip);
    const limitNum = Number(limit);
    const paginatedOps = operations.slice(skipNum, skipNum + limitNum);

    res.json({
      success: true,
      data: paginatedOps,
      pagination: {
        total,
        skip: skipNum,
        limit: limitNum,
      },
    });
  } catch (error) {
    console.error("Error listing operations:", error);
    res.status(500).json({
      success: false,
      error: "Failed to list operations",
    });
  }
});

/**
 * POST /operations/:id/complete
 * Mark operation as completed
 */
router.post("/operations/:id/complete", async (req: Request, res: Response) => {
  try {
    const id = Array.isArray(req.params.id) ? req.params.id[0] : req.params.id;
    const operation = _operations.get(id);

    if (!operation) {
      return res.status(404).json({
        success: false,
        error: "Operation not found",
      });
    }

    operation.status = "completed";
    operation.completed_date = new Date().toISOString();
    operation.updated_at = new Date().toISOString();

    _operations.set(id, operation);

    res.json({
      success: true,
      data: operation,
    });
  } catch (error) {
    console.error("Error completing operation:", error);
    res.status(500).json({
      success: false,
      error: "Failed to complete operation",
    });
  }
});

/**
 * PATCH /operations/:id
 * Update operation
 */
router.patch("/operations/:id", async (req: Request, res: Response) => {
  try {
    const id = Array.isArray(req.params.id) ? req.params.id[0] : req.params.id;
    const operation = _operations.get(id);

    if (!operation) {
      return res.status(404).json({
        success: false,
        error: "Operation not found",
      });
    }

    const updates = req.body;

    // Update allowed fields
    if (updates.status !== undefined) operation.status = updates.status;
    if (updates.notes !== undefined) operation.notes = updates.notes;
    if (updates.scheduled_date !== undefined)
      operation.scheduled_date = updates.scheduled_date;
    if (updates.metadata !== undefined)
      operation.metadata = { ...operation.metadata, ...updates.metadata };

    operation.updated_at = new Date().toISOString();

    _operations.set(id, operation);

    res.json({
      success: true,
      data: operation,
    });
  } catch (error) {
    console.error("Error updating operation:", error);
    res.status(500).json({
      success: false,
      error: "Failed to update operation",
    });
  }
});

/**
 * DELETE /operations/:id
 * Delete an operation
 */
router.delete("/operations/:id", async (req: Request, res: Response) => {
  try {
    const id = Array.isArray(req.params.id) ? req.params.id[0] : req.params.id;

    if (!_operations.has(id)) {
      return res.status(404).json({
        success: false,
        error: "Operation not found",
      });
    }

    _operations.delete(id);

    res.json({
      success: true,
      message: "Operation deleted successfully",
    });
  } catch (error) {
    console.error("Error deleting operation:", error);
    res.status(500).json({
      success: false,
      error: "Failed to delete operation",
    });
  }
});

/**
 * GET /stats/tenant/:tenant_id
 * Get statistics for a tenant
 */
router.get("/stats/tenant/:tenant_id", async (req: Request, res: Response) => {
  try {
    const tenant_id = Array.isArray(req.params.tenant_id)
      ? req.params.tenant_id[0]
      : req.params.tenant_id;

    const tenantOps = Array.from(_operations.values()).filter(
      (o) => o.tenant_id === tenant_id,
    );

    const stats = {
      tenant_id,
      operations: {
        total: tenantOps.length,
        scheduled: tenantOps.filter((o) => o.status === "scheduled").length,
        completed: tenantOps.filter((o) => o.status === "completed").length,
        in_progress: tenantOps.filter((o) => o.status === "in_progress").length,
      },
      by_type: tenantOps.reduce(
        (acc, op) => {
          acc[op.operation_type] = (acc[op.operation_type] || 0) + 1;
          return acc;
        },
        {} as Record<string, number>,
      ),
    };

    res.json({
      success: true,
      data: stats,
    });
  } catch (error) {
    console.error("Error fetching tenant stats:", error);
    res.status(500).json({
      success: false,
      error: "Failed to fetch tenant statistics",
    });
  }
});

export { router as taskRoutes };
