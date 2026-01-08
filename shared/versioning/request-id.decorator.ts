/**
 * Request ID Decorator
 * Extracts request ID from headers or generates a new one
 */

import { createParamDecorator, ExecutionContext } from '@nestjs/common';
import { v4 as uuidv4 } from 'uuid';

/**
 * Decorator to extract or generate request ID
 * Checks for X-Request-ID header, or generates a new UUID
 */
export const RequestId = createParamDecorator(
  (data: unknown, ctx: ExecutionContext): string => {
    const request = ctx.switchToHttp().getRequest();

    // Check for existing request ID in headers
    const existingRequestId =
      request.headers['x-request-id'] ||
      request.headers['x-correlation-id'] ||
      request.headers['request-id'];

    if (existingRequestId) {
      return existingRequestId;
    }

    // Generate new request ID
    const newRequestId = uuidv4();

    // Store in request for later use
    request.requestId = newRequestId;

    return newRequestId;
  },
);
