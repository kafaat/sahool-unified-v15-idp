/**
 * Client IP Resolution Utility
 * أداة تحديد عنوان IP للعميل
 *
 * Safely resolves a client's IP address from HTTP headers while guarding
 * against spoofing via untrusted proxies. This module is edge-runtime
 * compatible and avoids any Node.js-only APIs.
 *
 * Resolution order:
 *   1. If the `CF-Connecting-IP` header is present (Cloudflare), use it.
 *   2. If the direct socket peer is in `TRUSTED_PROXIES`, parse
 *      `X-Forwarded-For` and return the first non-private IP.
 *   3. Otherwise return `"unknown"` — never trust XFF from unknown peers.
 */

/**
 * Minimal shape of a request-like object exposing the headers we need.
 * Accepts both the standard `Request` (Fetch API) and Next.js `NextRequest`
 * without introducing a hard dependency on `next/server`, so this module
 * stays edge-runtime friendly and easy to unit test.
 */
interface RequestLike {
  headers: {
    get(name: string): string | null;
  };
  // NextRequest exposes `ip` directly; plain `Request` does not.
  ip?: string;
}

/**
 * RFC1918 / RFC4193 / loopback / link-local ranges we treat as "private".
 * These should never be surfaced as a client IP when a trusted proxy is
 * in front of us — the proxy's own internal address often leaks into XFF.
 */
const PRIVATE_IPV4_PATTERNS: RegExp[] = [
  /^10\./, // 10.0.0.0/8
  /^127\./, // 127.0.0.0/8 loopback
  /^169\.254\./, // 169.254.0.0/16 link-local
  /^192\.168\./, // 192.168.0.0/16
  /^172\.(1[6-9]|2\d|3[0-1])\./, // 172.16.0.0/12
  /^0\./, // 0.0.0.0/8
];

function isPrivateIPv4(ip: string): boolean {
  return PRIVATE_IPV4_PATTERNS.some((re) => re.test(ip));
}

function isPrivateIPv6(ip: string): boolean {
  const lower = ip.toLowerCase();
  if (lower === '::1') return true; // loopback
  if (lower === '::') return true;
  if (lower.startsWith('fe80:')) return true; // link-local
  if (lower.startsWith('fc') || lower.startsWith('fd')) return true; // unique local (fc00::/7)
  // IPv4-mapped IPv6 (e.g. ::ffff:10.0.0.1)
  if (lower.startsWith('::ffff:')) {
    const v4 = lower.slice('::ffff:'.length);
    return isPrivateIPv4(v4);
  }
  return false;
}

function isPrivateIP(ip: string): boolean {
  if (!ip) return true;
  if (ip.includes(':')) return isPrivateIPv6(ip);
  return isPrivateIPv4(ip);
}

/**
 * Parse the `TRUSTED_PROXIES` environment variable into a set of addresses.
 * The variable is a comma-separated list of socket addresses that are
 * allowed to set `X-Forwarded-For` on our behalf (e.g. load balancers).
 */
function getTrustedProxies(): Set<string> {
  const raw = process.env.TRUSTED_PROXIES;
  if (!raw) return new Set<string>();
  return new Set(
    raw
      .split(',')
      .map((entry) => entry.trim())
      .filter((entry) => entry.length > 0)
  );
}

/**
 * Extract the direct socket peer address from request metadata.
 * In edge runtimes we cannot read the TCP socket directly, so we rely
 * on either `NextRequest.ip` or the `X-Real-IP` header which upstream
 * infrastructure conventionally sets to the immediate peer.
 */
function getDirectPeer(request: RequestLike): string | null {
  if (typeof request.ip === 'string' && request.ip.length > 0) {
    return request.ip;
  }
  const realIp = request.headers.get('x-real-ip');
  if (realIp && realIp.trim().length > 0) {
    return realIp.trim();
  }
  return null;
}

/**
 * Return the first non-private IP from an `X-Forwarded-For` header value.
 * XFF is a comma-separated list in client → proxy order, so we iterate
 * left-to-right and return the first public address we encounter.
 */
function firstPublicFromXFF(xff: string): string | null {
  const parts = xff
    .split(',')
    .map((part) => part.trim())
    .filter((part) => part.length > 0);
  for (const candidate of parts) {
    if (!isPrivateIP(candidate)) {
      return candidate;
    }
  }
  return null;
}

/**
 * Resolve the client IP for a request.
 *
 * @param request - Fetch `Request` or Next.js `NextRequest` instance
 * @returns The resolved client IP, or `"unknown"` if it cannot be
 *   determined safely.
 */
export function getClientIP(request: Request | RequestLike): string {
  const req = request as RequestLike;

  // 1. Cloudflare's CF-Connecting-IP is authoritative when present.
  const cfIp = req.headers.get('cf-connecting-ip');
  if (cfIp && cfIp.trim().length > 0) {
    return cfIp.trim();
  }

  // 2. Only honour X-Forwarded-For if the direct peer is a trusted proxy.
  const trustedProxies = getTrustedProxies();
  if (trustedProxies.size > 0) {
    const peer = getDirectPeer(req);
    if (peer && trustedProxies.has(peer)) {
      const xff = req.headers.get('x-forwarded-for');
      if (xff) {
        const candidate = firstPublicFromXFF(xff);
        if (candidate) {
          return candidate;
        }
      }
    }
  }

  // 3. Untrusted peer — do not leak a spoofable value.
  return 'unknown';
}
