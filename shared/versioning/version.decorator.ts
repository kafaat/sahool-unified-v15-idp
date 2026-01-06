/**
 * API Version Decorators
 * Decorators for version-specific controllers and methods
 */

import { applyDecorators, SetMetadata } from '@nestjs/common';
import { ApiHeader, ApiTags } from '@nestjs/swagger';

/**
 * API Version enum
 */
export enum ApiVersion {
  V1 = '1',
  V2 = '2',
}

/**
 * Decorator for v1 controllers
 * Adds tags and metadata for deprecated endpoints
 */
export function ApiV1(resourceName: string) {
  return applyDecorators(
    ApiTags(`${resourceName} (v1 - Deprecated)`),
    ApiHeader({
      name: 'X-API-Version',
      description: 'API Version (optional, defaults to URI version)',
      required: false,
      example: '1',
    }),
    SetMetadata('api-version', ApiVersion.V1),
    SetMetadata('api-deprecated', true),
  );
}

/**
 * Decorator for v2 controllers
 * Adds tags and metadata for current endpoints
 */
export function ApiV2(resourceName: string) {
  return applyDecorators(
    ApiTags(`${resourceName} (v2)`),
    ApiHeader({
      name: 'X-API-Version',
      description: 'API Version (optional, defaults to URI version)',
      required: false,
      example: '2',
    }),
    SetMetadata('api-version', ApiVersion.V2),
  );
}

/**
 * Decorator to mark individual methods as deprecated
 */
export function ApiDeprecated(reason?: string, alternativeEndpoint?: string) {
  const description = [
    '⚠️ DEPRECATED',
    reason && `Reason: ${reason}`,
    alternativeEndpoint && `Use instead: ${alternativeEndpoint}`,
  ]
    .filter(Boolean)
    .join(' | ');

  return applyDecorators(
    SetMetadata('method-deprecated', true),
    SetMetadata('deprecation-info', { reason, alternativeEndpoint }),
  );
}
