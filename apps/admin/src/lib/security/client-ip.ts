/**
 * Client IP Extraction Utility
 * أداة استخراج عنوان IP للعميل
 *
 * Edge-runtime compatible utility for safely extracting the true client IP
 * address from an incoming request. This module deliberately avoids Node-only
 * APIs (`node:net`, `dns`) so it can be used in Next.js middleware and
 * Edge runtime route handlers.
 *
 * Security model:
 * -----------------
 * The `X-Forwarded-For` header is trivially spoofable by any client that is
 * not behind a trusted reverse proxy. This utility therefore only honors
 * `X-Forwarded-For` if the direct socket peer (or the request's CF-Connecting-IP
 * hop) matches an allowlist of trusted proxies supplied via the
 * `TRUSTED_PROXIES` environment variable (comma-separated IPs and/or CIDRs).
 *
 * Resolution order:
 * 1. `CF-Connecting-IP` - always trusted (Cloudflare terminates TLS and sets it)
 * 2. `X-Forwarded-For` - only when the direct peer is an allowlisted proxy;
 *    the first non-private hop is returned
 * 3. `"unknown"` - never trust XFF from untrusted sources
 */

// ═══════════════════════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Minimal request shape that the helper requires. Both `Request` (Edge/Web
 * standard) and `NextRequest` satisfy this contract via structural typing.
 */
interface RequestLike {
  headers: {
    get(name: string): string | null;
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// IP / CIDR helpers (pure, Edge-safe)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Parse an IPv4 dotted-quad string into a 32-bit unsigned integer.
 * Returns `null` for malformed input.
 */
function ipv4ToInt(ip: string): number | null {
  const parts = ip.split('.');
  if (parts.length !== 4) return null;
  let result = 0;
  for (const part of parts) {
    if (!/^\d{1,3}$/.test(part)) return null;
    const n = Number(part);
    if (n < 0 || n > 255) return null;
    result = (result << 8) + n;
  }
  // Coerce to unsigned 32-bit
  return result >>> 0;
}

/**
 * Determine whether an IPv4 address lies within the given CIDR range.
 */
function ipv4InCidr(ip: string, cidr: string): boolean {
  const [network, bitsStr] = cidr.split('/');
  if (!network) return false;
  const bits = bitsStr === undefined ? 32 : Number(bitsStr);
  if (!Number.isInteger(bits) || bits < 0 || bits > 32) return false;

  const ipInt = ipv4ToInt(ip);
  const netInt = ipv4ToInt(network);
  if (ipInt === null || netInt === null) return false;

  if (bits === 0) return true;
  const mask = (0xffffffff << (32 - bits)) >>> 0;
  return (ipInt & mask) === (netInt & mask);
}

/**
 * Detect whether an IP belongs to a private / reserved range (RFC 1918,
 * loopback, link-local, CGNAT, unique-local IPv6, etc.). First non-private
 * hops are used when walking an `X-Forwarded-For` chain.
 */
function isPrivateIp(ip: string): boolean {
  const normalized = ip.trim().toLowerCase();
  if (!normalized) return true;

  // IPv6 loopback / unspecified / unique-local / link-local
  if (normalized === '::1' || normalized === '::') return true;
  if (normalized.startsWith('fc') || normalized.startsWith('fd')) return true;
  if (normalized.startsWith('fe80:')) return true;
  // IPv4-mapped IPv6 — strip the prefix and fall through to IPv4 checks
  const mapped = normalized.startsWith('::ffff:')
    ? normalized.slice('::ffff:'.length)
    : normalized;

  const ipInt = ipv4ToInt(mapped);
  if (ipInt === null) {
    // Unknown / non-IPv4 format — treat as non-public to be safe
    return true;
  }

  return (
    ipv4InCidr(mapped, '10.0.0.0/8') ||
    ipv4InCidr(mapped, '172.16.0.0/12') ||
    ipv4InCidr(mapped, '192.168.0.0/16') ||
    ipv4InCidr(mapped, '127.0.0.0/8') ||
    ipv4InCidr(mapped, '169.254.0.0/16') ||
    ipv4InCidr(mapped, '100.64.0.0/10') || // CGNAT
    ipv4InCidr(mapped, '0.0.0.0/8')
  );
}

/**
 * Check whether the given IP matches any entry in the configured trusted
 * proxy allowlist. Entries may be plain IPs or CIDR blocks.
 */
function isTrustedProxy(ip: string | null): boolean {
  if (!ip) return false;
  const raw = process.env.TRUSTED_PROXIES;
  if (!raw) return false;

  const candidates = raw
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);

  const normalized = ip.trim();
  if (!normalized) return false;

  for (const candidate of candidates) {
    if (candidate === normalized) return true;
    if (candidate.includes('/')) {
      if (ipv4InCidr(normalized, candidate)) return true;
    }
  }
  return false;
}

// ═══════════════════════════════════════════════════════════════════════════
// Public API
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Safely resolve the originating client IP address from a request.
 *
 * @returns the resolved client IP, or `"unknown"` when it cannot be trusted.
 *
 * @example
 * ```ts
 * import { getClientIP } from '@/lib/security/client-ip';
 *
 * export async function POST(request: NextRequest) {
 *   const ip = getClientIP(request);
 *   // ... use ip for rate limiting / audit logging
 * }
 * ```
 */
export function getClientIP(request: RequestLike): string {
  // 1. Cloudflare: always authoritative when present (CF terminates the
  //    connection and sets this header itself).
  const cfIp = request.headers.get('cf-connecting-ip');
  if (cfIp && cfIp.trim().length > 0) {
    return cfIp.trim();
  }

  // 2. Identify the direct socket peer. In Edge / Next.js there is no
  //    socket.remoteAddress, so we use `x-real-ip` as the closest proxy-
  //    injected proxy-hop identifier. A trusted proxy should always set it.
  const directPeer = request.headers.get('x-real-ip');

  // 3. Only honor `X-Forwarded-For` when the direct peer is a trusted proxy.
  if (isTrustedProxy(directPeer)) {
    const forwarded = request.headers.get('x-forwarded-for');
    if (forwarded) {
      const hops = forwarded
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean);
      for (const hop of hops) {
        if (!isPrivateIp(hop)) {
          return hop;
        }
      }
    }
    // Trusted proxy but no usable XFF — fall back to the peer itself.
    if (directPeer) return directPeer.trim();
  }

  // 4. Untrusted source — never trust XFF.
  return 'unknown';
}
