/**
 * Error Response DTOs
 * كائنات نقل البيانات لاستجابات الأخطاء
 *
 * @module shared/errors
 * @description Standardized error response formats
 */

import { ApiProperty } from '@nestjs/swagger';
import { ErrorCode, ErrorCategory } from './error-codes';

/**
 * Field Validation Error
 * خطأ التحقق من صحة الحقل
 */
export class FieldErrorDto {
  @ApiProperty({
    description: 'Field name that failed validation',
    example: 'email',
  })
  field: string;

  @ApiProperty({
    description: 'Error message in English',
    example: 'Invalid email format',
  })
  message: string;

  @ApiProperty({
    description: 'Error message in Arabic - الرسالة بالعربية',
    example: 'تنسيق البريد الإلكتروني غير صالح',
    required: false,
  })
  messageAr?: string;

  @ApiProperty({
    description: 'Validation constraint that failed',
    example: 'isEmail',
    required: false,
  })
  constraint?: string;

  @ApiProperty({
    description: 'Invalid value that was provided',
    required: false,
  })
  value?: any;
}

/**
 * Error Details Object
 * كائن تفاصيل الخطأ
 */
export class ErrorDetailsDto {
  @ApiProperty({
    description: 'Error code',
    example: 'ERR_1001',
    enum: ErrorCode,
  })
  code: ErrorCode;

  @ApiProperty({
    description: 'Error message in English',
    example: 'Invalid input provided',
  })
  message: string;

  @ApiProperty({
    description: 'Error message in Arabic - الرسالة بالعربية',
    example: 'تم تقديم بيانات غير صالحة',
  })
  messageAr: string;

  @ApiProperty({
    description: 'Error category',
    example: 'VALIDATION',
    enum: ErrorCategory,
    required: false,
  })
  category?: ErrorCategory;

  @ApiProperty({
    description: 'Whether the operation can be retried',
    example: false,
  })
  retryable: boolean;

  @ApiProperty({
    description: 'Timestamp when error occurred',
    example: '2025-12-31T10:30:00.000Z',
  })
  timestamp: string;

  @ApiProperty({
    description: 'Request path where error occurred',
    example: '/api/v1/farms',
    required: false,
  })
  path?: string;

  @ApiProperty({
    description: 'Additional error details',
    required: false,
    type: 'object',
    example: {
      fields: [
        {
          field: 'email',
          message: 'Invalid email format',
        },
      ],
    },
  })
  details?: any;

  @ApiProperty({
    description: 'Request ID for tracking',
    example: 'req-123-456-789',
    required: false,
  })
  requestId?: string;

  @ApiProperty({
    description: 'Stack trace (only in development)',
    required: false,
  })
  stack?: string;
}

/**
 * Standard Error Response
 * استجابة الخطأ القياسية
 */
export class ErrorResponseDto {
  @ApiProperty({
    description: 'Success indicator (always false for errors)',
    example: false,
  })
  success: false;

  @ApiProperty({
    description: 'Error details',
    type: ErrorDetailsDto,
  })
  error: ErrorDetailsDto;

  constructor(
    code: ErrorCode,
    message: string,
    messageAr: string,
    retryable: boolean,
    options?: {
      category?: ErrorCategory;
      path?: string;
      details?: any;
      requestId?: string;
      stack?: string;
    },
  ) {
    this.success = false;
    this.error = {
      code,
      message,
      messageAr,
      category: options?.category,
      retryable,
      timestamp: new Date().toISOString(),
      path: options?.path,
      details: options?.details,
      requestId: options?.requestId,
      stack: options?.stack,
    };
  }
}

/**
 * Validation Error Response
 * استجابة خطأ التحقق من صحة البيانات
 */
export class ValidationErrorResponseDto extends ErrorResponseDto {
  @ApiProperty({
    description: 'Field validation errors',
    type: [FieldErrorDto],
  })
  fields?: FieldErrorDto[];

  constructor(
    message: string,
    messageAr: string,
    fields: FieldErrorDto[],
    options?: {
      path?: string;
      requestId?: string;
    },
  ) {
    super(ErrorCode.VALIDATION_ERROR, message, messageAr, false, {
      category: ErrorCategory.VALIDATION,
      path: options?.path,
      details: { fields },
      requestId: options?.requestId,
    });
    this.fields = fields;
  }
}

/**
 * Success Response (for comparison)
 * استجابة النجاح (للمقارنة)
 */
export class SuccessResponseDto<T = any> {
  @ApiProperty({
    description: 'Success indicator',
    example: true,
  })
  success: true;

  @ApiProperty({
    description: 'Response data',
  })
  data: T;

  @ApiProperty({
    description: 'Response message in English',
    required: false,
  })
  message?: string;

  @ApiProperty({
    description: 'Response message in Arabic - الرسالة بالعربية',
    required: false,
  })
  messageAr?: string;

  @ApiProperty({
    description: 'Response timestamp',
    example: '2025-12-31T10:30:00.000Z',
  })
  timestamp: string;

  constructor(data: T, message?: string, messageAr?: string) {
    this.success = true;
    this.data = data;
    this.message = message;
    this.messageAr = messageAr;
    this.timestamp = new Date().toISOString();
  }
}

/**
 * Paginated Response
 * استجابة مقسمة إلى صفحات
 */
export class PaginationMetaDto {
  @ApiProperty({
    description: 'Current page number',
    example: 1,
  })
  page: number;

  @ApiProperty({
    description: 'Items per page',
    example: 20,
  })
  limit: number;

  @ApiProperty({
    description: 'Total number of items',
    example: 100,
  })
  total: number;

  @ApiProperty({
    description: 'Total number of pages',
    example: 5,
  })
  totalPages: number;

  @ApiProperty({
    description: 'Whether there is a next page',
    example: true,
  })
  hasNextPage: boolean;

  @ApiProperty({
    description: 'Whether there is a previous page',
    example: false,
  })
  hasPreviousPage: boolean;
}

export class PaginatedResponseDto<T = any> extends SuccessResponseDto<T[]> {
  @ApiProperty({
    description: 'Pagination metadata',
    type: PaginationMetaDto,
  })
  meta: PaginationMetaDto;

  constructor(
    data: T[],
    page: number,
    limit: number,
    total: number,
    message?: string,
    messageAr?: string,
  ) {
    super(data, message, messageAr);
    this.meta = {
      page,
      limit,
      total,
      totalPages: Math.ceil(total / limit),
      hasNextPage: page * limit < total,
      hasPreviousPage: page > 1,
    };
  }
}

/**
 * Helper function to create success response
 * دالة مساعدة لإنشاء استجابة ناجحة
 */
export function createSuccessResponse<T>(
  data: T,
  message?: string,
  messageAr?: string,
): SuccessResponseDto<T> {
  return new SuccessResponseDto(data, message, messageAr);
}

/**
 * Helper function to create paginated response
 * دالة مساعدة لإنشاء استجابة مقسمة إلى صفحات
 */
export function createPaginatedResponse<T>(
  data: T[],
  page: number,
  limit: number,
  total: number,
  message?: string,
  messageAr?: string,
): PaginatedResponseDto<T> {
  return new PaginatedResponseDto(data, page, limit, total, message, messageAr);
}
