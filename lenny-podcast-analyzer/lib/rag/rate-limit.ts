/**
 * Rate limiting using Cloudflare KV.
 */

// Generic KV interface to avoid strict Cloudflare type conflicts
interface KVNamespaceLike {
  get(key: string, type: 'json'): Promise<unknown>;
  put(key: string, value: string, options?: { expirationTtl?: number }): Promise<void>;
}

interface RateLimitResult {
  allowed: boolean;
  remaining: number;
  resetAt: number;
}

/**
 * Check and update rate limit for a client IP.
 * Uses a sliding window counter approach.
 */
export async function checkRateLimit(
  kv: KVNamespaceLike,
  clientIp: string,
  windowSeconds: number,
  maxRequests: number
): Promise<RateLimitResult> {
  const now = Math.floor(Date.now() / 1000);
  const windowStart = now - windowSeconds;
  const key = `rate:${clientIp}`;

  // Get current state
  const stored = await kv.get(key, 'json') as {
    requests: number[];
  } | null;

  let requests = stored?.requests || [];

  // Filter to only requests within the window
  requests = requests.filter((ts) => ts > windowStart);

  // Check if limit exceeded
  if (requests.length >= maxRequests) {
    const oldestInWindow = Math.min(...requests);
    const resetAt = oldestInWindow + windowSeconds;

    return {
      allowed: false,
      remaining: 0,
      resetAt,
    };
  }

  // Add current request
  requests.push(now);

  // Store updated state
  await kv.put(key, JSON.stringify({ requests }), {
    expirationTtl: windowSeconds * 2, // Double window for safety
  });

  return {
    allowed: true,
    remaining: maxRequests - requests.length,
    resetAt: now + windowSeconds,
  };
}

/**
 * Get client IP from request headers.
 */
export function getClientIp(request: Request): string {
  return (
    request.headers.get('cf-connecting-ip') ||
    request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() ||
    request.headers.get('x-real-ip') ||
    'unknown'
  );
}
