export function nowIso(): string {
  return new Date().toISOString();
}

export function safeJsonParse<T = any>(s: string): T | null {
  try { return JSON.parse(s) as T; } catch { return null; }
}
