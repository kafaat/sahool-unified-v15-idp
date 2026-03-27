/**
 * SAHOOL Fields Query Keys
 * مفاتيح الاستعلام للحقول
 */

import type { FieldFilters } from '../types';

/**
 * Centralized query keys for fields feature
 * Ensures consistency across all hooks
 */
export const fieldKeys = {
  all: ['fields'] as const,
  lists: () => [...fieldKeys.all, 'list'] as const,
  list: (filters?: FieldFilters) => [...fieldKeys.lists(), filters] as const,
  detail: (id: string) => [...fieldKeys.all, 'detail', id] as const,
  stats: (farmId?: string) => [...fieldKeys.all, 'stats', farmId] as const,
};
