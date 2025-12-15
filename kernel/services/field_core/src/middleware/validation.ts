/**
 * SAHOOL Input Validation Middleware
 * Uses Zod-like validation patterns for request validation
 */

import { Request, Response, NextFunction } from "express";

// Validation error class
export class ValidationError extends Error {
    public errors: ValidationIssue[];

    constructor(errors: ValidationIssue[]) {
        super("Validation failed");
        this.name = "ValidationError";
        this.errors = errors;
    }
}

interface ValidationIssue {
    path: string[];
    message: string;
    code: string;
    expected?: string;
    received?: string;
}

// Type definitions for schema
type SchemaType = "string" | "number" | "boolean" | "array" | "object" | "date";

interface SchemaDefinition {
    type: SchemaType;
    required?: boolean;
    min?: number;
    max?: number;
    minLength?: number;
    maxLength?: number;
    pattern?: RegExp;
    enum?: any[];
    items?: SchemaDefinition;
    properties?: Record<string, SchemaDefinition>;
    custom?: (value: any) => boolean | string;
}

// Schema builder class (Zod-like API)
export class Schema {
    private definition: SchemaDefinition;

    constructor(type: SchemaType) {
        this.definition = { type, required: true };
    }

    static string() {
        return new Schema("string");
    }

    static number() {
        return new Schema("number");
    }

    static boolean() {
        return new Schema("boolean");
    }

    static array(items?: Schema) {
        const schema = new Schema("array");
        if (items) {
            schema.definition.items = items.definition;
        }
        return schema;
    }

    static object(properties: Record<string, Schema>) {
        const schema = new Schema("object");
        schema.definition.properties = {};
        for (const [key, value] of Object.entries(properties)) {
            schema.definition.properties[key] = value.definition;
        }
        return schema;
    }

    optional() {
        this.definition.required = false;
        return this;
    }

    min(value: number) {
        this.definition.min = value;
        return this;
    }

    max(value: number) {
        this.definition.max = value;
        return this;
    }

    minLength(value: number) {
        this.definition.minLength = value;
        return this;
    }

    maxLength(value: number) {
        this.definition.maxLength = value;
        return this;
    }

    pattern(regex: RegExp) {
        this.definition.pattern = regex;
        return this;
    }

    enum(values: any[]) {
        this.definition.enum = values;
        return this;
    }

    custom(validator: (value: any) => boolean | string) {
        this.definition.custom = validator;
        return this;
    }

    // UUID validation helper
    uuid() {
        return this.pattern(/^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
    }

    // Email validation helper
    email() {
        return this.pattern(/^[^\s@]+@[^\s@]+\.[^\s@]+$/);
    }

    // Validate a value against this schema
    validate(value: any, path: string[] = []): ValidationIssue[] {
        const errors: ValidationIssue[] = [];
        const def = this.definition;

        // Check required
        if (value === undefined || value === null) {
            if (def.required) {
                errors.push({
                    path,
                    message: "Required field is missing",
                    code: "required",
                    expected: def.type,
                    received: "undefined"
                });
            }
            return errors;
        }

        // Type checking
        const actualType = Array.isArray(value) ? "array" : typeof value;
        if (def.type === "number" && actualType === "string") {
            // Allow string numbers
            if (isNaN(Number(value))) {
                errors.push({
                    path,
                    message: `Expected ${def.type}, received ${actualType}`,
                    code: "invalid_type",
                    expected: def.type,
                    received: actualType
                });
                return errors;
            }
        } else if (def.type !== actualType && !(def.type === "date" && value instanceof Date)) {
            errors.push({
                path,
                message: `Expected ${def.type}, received ${actualType}`,
                code: "invalid_type",
                expected: def.type,
                received: actualType
            });
            return errors;
        }

        // String validations
        if (def.type === "string" && typeof value === "string") {
            if (def.minLength !== undefined && value.length < def.minLength) {
                errors.push({
                    path,
                    message: `String must be at least ${def.minLength} characters`,
                    code: "too_small"
                });
            }
            if (def.maxLength !== undefined && value.length > def.maxLength) {
                errors.push({
                    path,
                    message: `String must be at most ${def.maxLength} characters`,
                    code: "too_big"
                });
            }
            if (def.pattern && !def.pattern.test(value)) {
                errors.push({
                    path,
                    message: "String does not match required pattern",
                    code: "invalid_pattern"
                });
            }
        }

        // Number validations
        if (def.type === "number") {
            const num = Number(value);
            if (def.min !== undefined && num < def.min) {
                errors.push({
                    path,
                    message: `Number must be at least ${def.min}`,
                    code: "too_small"
                });
            }
            if (def.max !== undefined && num > def.max) {
                errors.push({
                    path,
                    message: `Number must be at most ${def.max}`,
                    code: "too_big"
                });
            }
        }

        // Enum validation
        if (def.enum && !def.enum.includes(value)) {
            errors.push({
                path,
                message: `Value must be one of: ${def.enum.join(", ")}`,
                code: "invalid_enum",
                expected: def.enum.join(" | "),
                received: String(value)
            });
        }

        // Array validations
        if (def.type === "array" && Array.isArray(value)) {
            if (def.min !== undefined && value.length < def.min) {
                errors.push({
                    path,
                    message: `Array must have at least ${def.min} items`,
                    code: "too_small"
                });
            }
            if (def.max !== undefined && value.length > def.max) {
                errors.push({
                    path,
                    message: `Array must have at most ${def.max} items`,
                    code: "too_big"
                });
            }
            if (def.items) {
                const itemSchema = new Schema(def.items.type);
                Object.assign(itemSchema.definition, def.items);
                value.forEach((item, index) => {
                    errors.push(...itemSchema.validate(item, [...path, String(index)]));
                });
            }
        }

        // Object validations
        if (def.type === "object" && def.properties && typeof value === "object") {
            for (const [key, propDef] of Object.entries(def.properties)) {
                const propSchema = new Schema(propDef.type);
                Object.assign(propSchema.definition, propDef);
                errors.push(...propSchema.validate(value[key], [...path, key]));
            }
        }

        // Custom validation
        if (def.custom) {
            const result = def.custom(value);
            if (result !== true) {
                errors.push({
                    path,
                    message: typeof result === "string" ? result : "Custom validation failed",
                    code: "custom"
                });
            }
        }

        return errors;
    }

    parse(value: any): any {
        const errors = this.validate(value);
        if (errors.length > 0) {
            throw new ValidationError(errors);
        }
        return value;
    }

    safeParse(value: any): { success: true; data: any } | { success: false; errors: ValidationIssue[] } {
        const errors = this.validate(value);
        if (errors.length > 0) {
            return { success: false, errors };
        }
        return { success: true, data: value };
    }
}

// Pre-defined schemas for SAHOOL entities

export const FieldCreateSchema = Schema.object({
    name: Schema.string().minLength(1).maxLength(100),
    tenantId: Schema.string().uuid(),
    cropType: Schema.string().minLength(1).maxLength(50),
    coordinates: Schema.array(
        Schema.array(Schema.number())
    ).min(3).optional(),
    ownerId: Schema.string().uuid().optional(),
    irrigationType: Schema.string().enum(["drip", "sprinkler", "flood", "none"]).optional(),
    soilType: Schema.string().maxLength(50).optional(),
    plantingDate: Schema.string().optional(),
    expectedHarvest: Schema.string().optional(),
    metadata: Schema.object({}).optional()
});

export const FieldUpdateSchema = Schema.object({
    name: Schema.string().minLength(1).maxLength(100).optional(),
    cropType: Schema.string().minLength(1).maxLength(50).optional(),
    status: Schema.string().enum(["active", "fallow", "preparing", "harvested"]).optional(),
    irrigationType: Schema.string().enum(["drip", "sprinkler", "flood", "none"]).optional(),
    soilType: Schema.string().maxLength(50).optional(),
    plantingDate: Schema.string().optional(),
    expectedHarvest: Schema.string().optional(),
    metadata: Schema.object({}).optional()
});

export const NdviUpdateSchema = Schema.object({
    value: Schema.number().min(-1).max(1),
    source: Schema.string().maxLength(50).optional()
});

export const PaginationSchema = Schema.object({
    limit: Schema.number().min(1).max(100).optional(),
    offset: Schema.number().min(0).optional()
});

// Express middleware factory
export function validateBody(schema: Schema) {
    return (req: Request, res: Response, next: NextFunction) => {
        const result = schema.safeParse(req.body);

        if (!result.success) {
            return res.status(400).json({
                success: false,
                error: "Validation failed",
                error_ar: "فشل التحقق من البيانات",
                details: result.errors.map(e => ({
                    field: e.path.join("."),
                    message: e.message,
                    code: e.code
                }))
            });
        }

        req.body = result.data;
        next();
    };
}

export function validateQuery(schema: Schema) {
    return (req: Request, res: Response, next: NextFunction) => {
        const result = schema.safeParse(req.query);

        if (!result.success) {
            return res.status(400).json({
                success: false,
                error: "Invalid query parameters",
                error_ar: "معاملات استعلام غير صالحة",
                details: result.errors.map(e => ({
                    field: e.path.join("."),
                    message: e.message,
                    code: e.code
                }))
            });
        }

        next();
    };
}

export function validateParams(schema: Schema) {
    return (req: Request, res: Response, next: NextFunction) => {
        const result = schema.safeParse(req.params);

        if (!result.success) {
            return res.status(400).json({
                success: false,
                error: "Invalid path parameters",
                error_ar: "معاملات مسار غير صالحة",
                details: result.errors.map(e => ({
                    field: e.path.join("."),
                    message: e.message,
                    code: e.code
                }))
            });
        }

        next();
    };
}
