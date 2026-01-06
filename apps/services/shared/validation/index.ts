/**
 * Shared Validation Module
 * وحدة التحقق المشتركة
 *
 * @module shared/validation
 * @description Central module for all validation utilities in SAHOOL platform
 */

// Export custom validators
export * from './custom-validators';

// Export sanitization utilities
export * from './sanitization';

// Export file upload utilities
export * from './file-upload';

// Export Prisma middleware
export * from './prisma-middleware';

// Export validation error responses
export * from './validation-errors';

/**
 * Quick Reference Guide
 * دليل المرجع السريع
 *
 * ## Custom Validators (class-validator decorators)
 *
 * ### Yemen-Specific:
 * - @IsYemeniPhone() - Validates Yemen phone numbers
 * - @IsWithinYemen() - Validates coordinates within Yemen
 *
 * ### Arabic Text:
 * - @ContainsArabic() - Must contain Arabic characters
 * - @IsArabicOnly() - Only Arabic characters allowed
 *
 * ### Business Logic:
 * - @IsAfterDate(startDateField) - End date must be after start date
 * - @IsFutureDate() - Date must be in the future
 * - @IsStrongPassword(minLength) - Password complexity validation
 *
 * ### Geospatial:
 * - @IsGeoJSONPolygon() - Validates GeoJSON polygon structure
 * - @IsValidFieldArea(min, max) - Validates field area in hectares
 *
 * ### Financial:
 * - @IsMoneyValue() - Validates monetary values (positive, 2 decimals)
 * - @IsCreditCard() - Validates credit card using Luhn algorithm
 *
 * ### Other:
 * - @IsEAN13() - Validates EAN-13 barcodes
 *
 * ## Sanitization (Transform decorators)
 *
 * ### Text Sanitization:
 * - @SanitizeHtml(options) - Sanitize HTML (prevent XSS)
 * - @SanitizePlainText() - Strip all HTML, normalize whitespace
 * - @SanitizeRichText() - Allow safe HTML tags only
 *
 * ### Security:
 * - @SanitizeFilePath() - Prevent path traversal
 * - @SanitizePrompt() - Prevent prompt injection in AI inputs
 *
 * ## File Upload Validation
 *
 * ### Constants:
 * - ALLOWED_FILE_TYPES.IMAGES - ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']
 * - ALLOWED_FILE_TYPES.DOCUMENTS - ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'csv']
 * - FILE_SIZE_LIMITS.IMAGE - 10 MB
 * - FILE_SIZE_LIMITS.DOCUMENT - 50 MB
 *
 * ### Functions:
 * - validateFileUpload(file, options) - Comprehensive file validation
 * - generateSafeFilename(filename, prefix) - Create safe filenames
 * - calculateFileHash(buffer) - SHA-256 hash for duplicate detection
 *
 * ### Multer Filters:
 * - imageFileFilter - Filter for images only
 * - documentFileFilter - Filter for documents only
 * - createFileFilter(allowedExtensions) - Custom filter
 *
 * ## Prisma Middleware
 *
 * ### Validation:
 * - createValidationMiddleware(rules) - Runtime validation at DB level
 * - USER_VALIDATION_RULES - Common user validation rules
 * - PRODUCT_VALIDATION_RULES - Common product validation rules
 * - FIELD_VALIDATION_RULES - Common field validation rules
 *
 * ### Other Middleware:
 * - createAuditLoggingMiddleware(logger) - Log all mutations
 * - createSoftDeleteMiddleware() - Soft delete support
 * - createTimestampMiddleware() - Auto createdAt/updatedAt
 *
 * ## Usage Examples
 *
 * ### Example 1: DTO with Custom Validators
 * ```typescript
 * import { IsYemeniPhone, IsStrongPassword, SanitizePlainText } from '@shared/validation';
 *
 * export class CreateUserDto {
 *   @IsEmail()
 *   email: string;
 *
 *   @IsYemeniPhone()
 *   phone: string;
 *
 *   @IsStrongPassword(8)
 *   password: string;
 *
 *   @IsString()
 *   @SanitizePlainText()
 *   firstName: string;
 * }
 * ```
 *
 * ### Example 2: File Upload in Controller
 * ```typescript
 * import { validateFileUpload, ALLOWED_FILE_TYPES, FILE_SIZE_LIMITS } from '@shared/validation';
 *
 * @Post('upload')
 * @UseInterceptors(FileInterceptor('file'))
 * async uploadFile(@UploadedFile() file: Express.Multer.File) {
 *   validateFileUpload(file, {
 *     allowedExtensions: ALLOWED_FILE_TYPES.IMAGES,
 *     maxSize: FILE_SIZE_LIMITS.IMAGE,
 *   });
 *
 *   return { message: 'File uploaded successfully' };
 * }
 * ```
 *
 * ### Example 3: Prisma Middleware Setup
 * ```typescript
 * import { createValidationMiddleware, USER_VALIDATION_RULES } from '@shared/validation';
 *
 * const prisma = new PrismaClient();
 *
 * prisma.$use(
 *   createValidationMiddleware({
 *     User: { fields: USER_VALIDATION_RULES },
 *   })
 * );
 * ```
 *
 * ### Example 4: Cross-Field Validation
 * ```typescript
 * import { IsAfterDate, IsFutureDate } from '@shared/validation';
 *
 * export class CreateExperimentDto {
 *   @IsDateString()
 *   @IsFutureDate()
 *   startDate: string;
 *
 *   @IsDateString()
 *   @IsAfterDate('startDate')
 *   endDate: string;
 * }
 * ```
 *
 * ### Example 5: Yemen-Specific Validation
 * ```typescript
 * import { IsWithinYemen, IsYemeniPhone } from '@shared/validation';
 *
 * export class CreateFieldDto {
 *   @IsYemeniPhone()
 *   ownerPhone: string;
 *
 *   @ValidateNested()
 *   @IsWithinYemen()
 *   location: {
 *     lat: number;
 *     lng: number;
 *   };
 * }
 * ```
 */
