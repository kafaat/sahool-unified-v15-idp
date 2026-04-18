/**
 * CSV helpers — safe cell sanitization for export.
 * مساعدات CSV
 *
 * Prevents CSV formula injection (aka "CSV injection" / CVE-2014-3524-style
 * attacks) by prefixing cells whose first character could be interpreted as a
 * formula in Excel/LibreOffice/Google Sheets, and by properly quoting cells
 * that contain delimiters, quotes, or newlines.
 */

const DANGEROUS_LEADING_CHARS = new Set(['=', '+', '-', '@', '\t', '\r']);

/**
 * Sanitize a single CSV cell value. The returned string is safe to embed into
 * comma-delimited CSV output.
 */
export function sanitizeCsvCell(val: unknown): string {
  if (val === null || val === undefined) return '';
  let s = String(val).trim();

  // Prefix formula-like content with a single quote, which Excel treats as a
  // literal string marker rather than executing the cell as a formula.
  if (s.length > 0 && DANGEROUS_LEADING_CHARS.has(s[0]!)) {
    s = `'${s}`;
  }

  // Escape embedded double quotes per RFC 4180.
  const needsQuoting = /[",\r\n]/.test(s);
  const escaped = s.replace(/"/g, '""');
  return needsQuoting ? `"${escaped}"` : escaped;
}
