/**
 * Security Configuration for SAHOOL User Service
 * إعدادات الأمان لخدمة المستخدمين
 *
 * Centralized security constants including password hashing configuration.
 * OWASP recommends a minimum of 12 bcrypt rounds for password hashing.
 *
 * @see https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
 */

/**
 * Number of bcrypt salt rounds for password hashing.
 * Configurable via BCRYPT_ROUNDS environment variable.
 * Default: 12 (OWASP recommended minimum). A misconfigured value fails
 * the module load rather than silently falling back to the default —
 * silent fallback once shipped a production deployment with weakened
 * hashing that went undetected.
 *
 * عدد جولات تشفير كلمة المرور - الحد الأدنى الموصى به من OWASP هو 12
 */
function resolveBcryptRounds(): number {
  const raw = process.env.BCRYPT_ROUNDS;
  if (raw === undefined || raw === "") {
    return 12;
  }
  const parsed = Number.parseInt(raw, 10);
  if (!Number.isFinite(parsed) || parsed < 12 || parsed > 15) {
    throw new Error(
      `Invalid BCRYPT_ROUNDS=${raw}: must be an integer between 12 and 15 (OWASP recommends >=12; >15 is impractically slow).`,
    );
  }
  return parsed;
}
export const BCRYPT_ROUNDS = resolveBcryptRounds();

/**
 * Default tenant ID for users created without explicit tenant.
 * Corresponds to the sahool-demo tenant in the database.
 * معرف المستأجر الافتراضي
 */
export const DEFAULT_TENANT_ID = process.env.DEFAULT_TENANT_ID || 'a0000000-0000-0000-0000-000000000001';

/**
 * Split a full name into firstName and lastName.
 * If the name has only one part, it's used for both.
 * تقسيم الاسم الكامل إلى الاسم الأول والأخير
 */
export function splitFullName(
  name?: string,
  firstName?: string,
  lastName?: string,
): { firstName: string; lastName: string } | null {
  let first = firstName;
  let last = lastName;
  if (name && (!first || !last)) {
    const parts = name.trim().split(/\s+/);
    first = first || parts[0];
    last = last || parts.slice(1).join(' ') || parts[0];
  }
  if (!first || !last) return null;
  return { firstName: first, lastName: last };
}
