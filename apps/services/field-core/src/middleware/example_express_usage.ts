/**
 * Example Express Service with Error Localization
 * مثال على خدمة Express مع توطين الأخطاء
 *
 * This demonstrates how to use the error localization system in an Express service.
 */

import express, { Request, Response } from "express";
import {
    languageParser,
    errorHandler,
    notFoundHandler,
    asyncHandler,
    NotFoundError,
    ValidationError,
    AuthenticationError,
    ConflictError,
    AppError,
    LocalizedRequest,
} from "./errorLocalization";

const app = express();

// ════════════════════════════════════════════════════════════════════════
// MIDDLEWARE SETUP
// ════════════════════════════════════════════════════════════════════════

app.use(express.json());

// IMPORTANT: Apply language parser middleware early (before routes)
app.use(languageParser());

// ════════════════════════════════════════════════════════════════════════
// MOCK DATABASE
// ════════════════════════════════════════════════════════════════════════

interface Field {
    id: string;
    name: string;
    cropType: string;
    areaHectares: number;
    tenantId: string;
}

const FIELDS_DB: Record<string, Field> = {
    "field-123": {
        id: "field-123",
        name: "North Field",
        cropType: "Wheat",
        areaHectares: 50.5,
        tenantId: "tenant-1",
    },
};

// ════════════════════════════════════════════════════════════════════════
// EXAMPLE 1: NOT FOUND ERROR
// ════════════════════════════════════════════════════════════════════════

app.get("/api/v1/fields/:id", asyncHandler(async (req: Request, res: Response) => {
    /**
     * Get a field by ID.
     *
     * Example requests:
     * - English: GET /api/v1/fields/invalid-id
     * - Arabic: GET /api/v1/fields/invalid-id -H "Accept-Language: ar"
     *
     * Error response:
     * {
     *     "success": false,
     *     "error": {
     *         "code": "NOT_FOUND",
     *         "message": "Field not found.",
     *         "message_ar": "الحقل غير موجود.",
     *         "error": "الحقل غير موجود.",  // Matches Accept-Language
     *         "error_id": "A3F2D891"
     *     }
     * }
     */
    const field = FIELDS_DB[req.params.id];

    if (!field) {
        // Throws 404 with bilingual message
        // The error handler will automatically use Accept-Language header
        throw new NotFoundError("Field", "الحقل");
    }

    res.json({ success: true, data: field });
}));

// ════════════════════════════════════════════════════════════════════════
// EXAMPLE 2: CONFLICT ERROR
// ════════════════════════════════════════════════════════════════════════

app.post("/api/v1/fields", asyncHandler(async (req: Request, res: Response) => {
    /**
     * Create a new field.
     *
     * Example request:
     * POST /api/v1/fields
     * {
     *     "name": "North Field",  // Already exists!
     *     "cropType": "Wheat",
     *     "areaHectares": 50.5,
     *     "tenantId": "tenant-1"
     * }
     *
     * Error response (409 Conflict):
     * {
     *     "success": false,
     *     "error": {
     *         "code": "CONFLICT",
     *         "message": "A field with this name already exists",
     *         "message_ar": "حقل بهذا الاسم موجود بالفعل",
     *         "error_id": "B7E3C542",
     *         "details": {
     *             "fieldName": "North Field"
     *         }
     *     }
     * }
     */
    const { name, cropType, areaHectares, tenantId } = req.body;

    // Check if field already exists
    for (const field of Object.values(FIELDS_DB)) {
        if (field.name === name && field.tenantId === tenantId) {
            throw new ConflictError(
                "A field with this name already exists",
                "حقل بهذا الاسم موجود بالفعل",
                { fieldName: name }
            );
        }
    }

    // Create new field
    const fieldId = `field-${Object.keys(FIELDS_DB).length + 1}`;
    const newField: Field = {
        id: fieldId,
        name,
        cropType,
        areaHectares,
        tenantId,
    };
    FIELDS_DB[fieldId] = newField;

    res.status(201).json({ success: true, data: newField });
}));

// ════════════════════════════════════════════════════════════════════════
// EXAMPLE 3: VALIDATION ERROR
// ════════════════════════════════════════════════════════════════════════

app.post("/api/v1/fields/:id/validate-boundary", asyncHandler(async (req: Request, res: Response) => {
    /**
     * Validate field boundary coordinates.
     *
     * Example request with invalid data:
     * POST /api/v1/fields/field-123/validate-boundary
     * {
     *     "coordinates": [[0, 0], [0, 1]]  // Less than 3 points!
     * }
     *
     * Error response (400 Bad Request):
     * {
     *     "success": false,
     *     "error": {
     *         "code": "VALIDATION_ERROR",
     *         "message": "Field boundary must have at least 3 points",
     *         "message_ar": "حدود الحقل يجب أن تحتوي على 3 نقاط على الأقل",
     *         "error_id": "C9D4E123",
     *         "details": {
     *             "pointsProvided": 2,
     *             "minimumRequired": 3
     *         }
     *     }
     * }
     */
    const { coordinates } = req.body;

    if (!coordinates || !Array.isArray(coordinates) || coordinates.length < 3) {
        throw new ValidationError(
            "Field boundary must have at least 3 points",
            "حدود الحقل يجب أن تحتوي على 3 نقاط على الأقل",
            {
                pointsProvided: coordinates?.length || 0,
                minimumRequired: 3,
            }
        );
    }

    res.json({
        success: true,
        message: "Boundary is valid",
        message_ar: "الحدود صالحة",
    });
}));

// ════════════════════════════════════════════════════════════════════════
// EXAMPLE 4: AUTHENTICATION ERROR
// ════════════════════════════════════════════════════════════════════════

function verifyToken(req: Request): string {
    /**
     * Middleware to verify authentication token
     */
    const authorization = req.headers.authorization;

    if (!authorization) {
        throw new AuthenticationError(
            "Authentication token is required",
            "رمز المصادقة مطلوب"
        );
    }

    if (!authorization.startsWith("Bearer ")) {
        throw new AuthenticationError(
            "Invalid authentication token format",
            "تنسيق رمز المصادقة غير صالح"
        );
    }

    // Mock token validation
    const token = authorization.substring(7);
    if (token !== "valid-token") {
        throw new AuthenticationError(
            "Invalid authentication token",
            "رمز المصادقة غير صالح"
        );
    }

    return token;
}

app.get("/api/v1/fields/:id/protected", asyncHandler(async (req: Request, res: Response) => {
    /**
     * Protected endpoint requiring authentication.
     *
     * Example request without token:
     * GET /api/v1/fields/field-123/protected
     *
     * Error response (401 Unauthorized):
     * {
     *     "success": false,
     *     "error": {
     *         "code": "AUTHENTICATION_ERROR",
     *         "message": "Authentication token is required",
     *         "message_ar": "رمز المصادقة مطلوب",
     *         "error_id": "D5F6A234"
     *     }
     * }
     */
    verifyToken(req);

    const field = FIELDS_DB[req.params.id];
    if (!field) {
        throw new NotFoundError("Field", "الحقل");
    }

    res.json({
        success: true,
        data: field,
        message: "Access granted",
    });
}));

// ════════════════════════════════════════════════════════════════════════
// EXAMPLE 5: CUSTOM ERROR WITH CUSTOM CODE
// ════════════════════════════════════════════════════════════════════════

app.post("/api/v1/fields/:id/harvest", asyncHandler(async (req: Request, res: Response) => {
    /**
     * Harvest a field.
     *
     * Example with custom business logic error:
     * POST /api/v1/fields/field-123/harvest
     *
     * Error response (400 Bad Request):
     * {
     *     "success": false,
     *     "error": {
     *         "code": "CROP_NOT_READY",
     *         "message": "Crop is not ready for harvest",
     *         "message_ar": "المحصول ليس جاهزاً للحصاد",
     *         "error_id": "E7G8H345",
     *         "details": {
     *             "daysUntilReady": 30,
     *             "currentGrowthStage": "flowering"
     *         }
     *     }
     * }
     */
    const field = FIELDS_DB[req.params.id];
    if (!field) {
        throw new NotFoundError("Field", "الحقل");
    }

    // Custom business logic error
    throw new AppError(
        400,
        "CROP_NOT_READY",
        "Crop is not ready for harvest",
        "المحصول ليس جاهزاً للحصاد",
        {
            daysUntilReady: 30,
            currentGrowthStage: "flowering",
        }
    );
}));

// ════════════════════════════════════════════════════════════════════════
// EXAMPLE 6: LANGUAGE PREFERENCE IN ROUTE
// ════════════════════════════════════════════════════════════════════════

app.get("/api/v1/language-test", (req: LocalizedRequest, res: Response) => {
    /**
     * Test endpoint to see language preference.
     *
     * Example requests:
     * - curl http://localhost:3000/api/v1/language-test
     * - curl -H "Accept-Language: ar" http://localhost:3000/api/v1/language-test
     * - curl -H "Accept-Language: en-US,en;q=0.9,ar;q=0.8" http://localhost:3000/api/v1/language-test
     */
    const message = req.preferredLanguage === "ar"
        ? "مرحباً! لغتك المفضلة هي العربية"
        : "Hello! Your preferred language is English";

    res.json({
        success: true,
        preferredLanguage: req.preferredLanguage,
        message,
        headers: {
            acceptLanguage: req.headers["accept-language"],
        },
    });
});

// ════════════════════════════════════════════════════════════════════════
// ERROR HANDLERS (Must be registered last)
// ════════════════════════════════════════════════════════════════════════

// 404 handler for undefined routes
app.use(notFoundHandler);

// Global error handler (must be last)
app.use(errorHandler);

// ════════════════════════════════════════════════════════════════════════
// START SERVER
// ════════════════════════════════════════════════════════════════════════

const PORT = process.env.PORT || 3000;

if (require.main === module) {
    app.listen(PORT, () => {
        console.log("\n" + "=".repeat(70));
        console.log("SAHOOL Error Localization Example Service");
        console.log("خدمة مثال توطين الأخطاء لنظام سهول");
        console.log("=".repeat(70));
        console.log(`\nServer running at http://localhost:${PORT}`);
        console.log("\nTry these endpoints:");
        console.log("\n1. Not Found Error (English):");
        console.log(`   curl http://localhost:${PORT}/api/v1/fields/invalid-id`);
        console.log("\n2. Not Found Error (Arabic):");
        console.log(`   curl -H "Accept-Language: ar" http://localhost:${PORT}/api/v1/fields/invalid-id`);
        console.log("\n3. Conflict Error:");
        console.log(`   curl -X POST http://localhost:${PORT}/api/v1/fields \\`);
        console.log('     -H "Content-Type: application/json" \\');
        console.log('     -d \'{"name":"North Field","cropType":"Wheat","areaHectares":50,"tenantId":"tenant-1"}\'');
        console.log("\n4. Validation Error:");
        console.log(`   curl -X POST http://localhost:${PORT}/api/v1/fields/field-123/validate-boundary \\`);
        console.log('     -H "Content-Type: application/json" \\');
        console.log('     -d \'{"coordinates":[[0,0],[1,1]]}\'');
        console.log("\n5. Authentication Error:");
        console.log(`   curl http://localhost:${PORT}/api/v1/fields/field-123/protected`);
        console.log("\n6. Language Test:");
        console.log(`   curl -H "Accept-Language: ar" http://localhost:${PORT}/api/v1/language-test`);
        console.log("\n" + "=".repeat(70) + "\n");
    });
}

export default app;
