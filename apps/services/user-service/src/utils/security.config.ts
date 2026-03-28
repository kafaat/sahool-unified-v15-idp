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
 * Default: 12 (OWASP recommended minimum)
 *
 * عدد جولات تشفير كلمة المرور - الحد الأدنى الموصى به من OWASP هو 12
 */
export const BCRYPT_ROUNDS = parseInt(process.env.BCRYPT_ROUNDS || '12', 10);
