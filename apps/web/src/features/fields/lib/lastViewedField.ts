/**
 * Last-Viewed Field Storage
 * تخزين آخر حقل تمت مشاهدته
 *
 * SSR-safe, tenant-namespaced helpers for persisting the last field
 * the user opened, so the fields list can restore selection on re-entry.
 *
 * The key is namespaced per tenant to avoid leakage across tenant
 * switches. When `tenantId` is undefined we still persist under a
 * `default` namespace so anonymous/local sessions still work.
 */

const STORAGE_KEY_PREFIX = 'sahool:lastViewedFieldId';

/**
 * Build the tenant-namespaced storage key.
 */
export function lastViewedFieldKey(tenantId?: string | null): string {
  const ns = tenantId && tenantId.length > 0 ? tenantId : 'default';
  return `${STORAGE_KEY_PREFIX}:${ns}`;
}

/**
 * Detect whether `localStorage` is usable in the current environment.
 * Guards against SSR and against environments where storage access throws
 * (private mode in some browsers, sandboxed iframes, etc.).
 */
function getStorage(): Storage | null {
  if (typeof window === 'undefined') {
    return null;
  }
  try {
    return window.localStorage;
  } catch {
    return null;
  }
}

/**
 * Persist the id of the field the user just opened.
 * No-op on SSR or when storage is unavailable; never throws.
 */
export function saveLastViewedField(
  tenantId: string | null | undefined,
  fieldId: string,
): void {
  const storage = getStorage();
  if (!storage || !fieldId) {
    return;
  }
  try {
    storage.setItem(lastViewedFieldKey(tenantId), fieldId);
  } catch {
    // Quota exceeded / storage disabled — nothing actionable here.
  }
}

/**
 * Read the last-viewed field id for the given tenant.
 * Returns `null` on SSR, when nothing is stored, or on read failure.
 */
export function getLastViewedField(
  tenantId: string | null | undefined,
): string | null {
  const storage = getStorage();
  if (!storage) {
    return null;
  }
  try {
    const value = storage.getItem(lastViewedFieldKey(tenantId));
    return value && value.length > 0 ? value : null;
  } catch {
    return null;
  }
}

/**
 * Remove the stored last-viewed field id for the given tenant.
 * No-op on SSR or when storage is unavailable; never throws.
 */
export function clearLastViewedField(
  tenantId: string | null | undefined,
): void {
  const storage = getStorage();
  if (!storage) {
    return;
  }
  try {
    storage.removeItem(lastViewedFieldKey(tenantId));
  } catch {
    // Ignore — best-effort cleanup.
  }
}
