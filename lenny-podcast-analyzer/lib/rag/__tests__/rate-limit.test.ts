import { describe, it, expect, vi } from 'vitest';
import { checkRateLimit, getClientIp } from '../rate-limit';

describe('getClientIp', () => {
  it('returns cf-connecting-ip when present', () => {
    const req = new Request('https://example.com', {
      headers: { 'cf-connecting-ip': '1.2.3.4' },
    });
    expect(getClientIp(req)).toBe('1.2.3.4');
  });

  it('falls back to x-forwarded-for when cf-connecting-ip is missing', () => {
    const req = new Request('https://example.com', {
      headers: { 'x-forwarded-for': '5.6.7.8, 9.10.11.12' },
    });
    expect(getClientIp(req)).toBe('5.6.7.8');
  });

  it('falls back to x-real-ip', () => {
    const req = new Request('https://example.com', {
      headers: { 'x-real-ip': '10.0.0.1' },
    });
    expect(getClientIp(req)).toBe('10.0.0.1');
  });

  it('returns "unknown" when no IP headers present', () => {
    const req = new Request('https://example.com');
    expect(getClientIp(req)).toBe('unknown');
  });

  it('prioritizes cf-connecting-ip over all others', () => {
    const req = new Request('https://example.com', {
      headers: {
        'cf-connecting-ip': '1.2.3.4',
        'x-forwarded-for': '5.6.7.8',
        'x-real-ip': '10.0.0.1',
      },
    });
    expect(getClientIp(req)).toBe('1.2.3.4');
  });
});

// Mock KV store for checkRateLimit tests
function createMockKV(initialData?: number[]): any {
  let store: string | null = initialData
    ? JSON.stringify({ requests: initialData })
    : null;

  return {
    get: vi.fn().mockImplementation((_key: string, _type: string) => {
      return store ? JSON.parse(store) : null;
    }),
    put: vi.fn().mockImplementation((_key: string, value: string) => {
      store = value;
    }),
  };
}

describe('checkRateLimit', () => {
  const WINDOW = 60;
  const MAX = 5;

  it('allows first request', async () => {
    const kv = createMockKV();
    const result = await checkRateLimit(kv, '127.0.0.1', WINDOW, MAX);
    expect(result.allowed).toBe(true);
    expect(result.remaining).toBe(4);
  });

  it('allows requests under limit', async () => {
    const kv = createMockKV([Math.floor(Date.now() / 1000) - 30]);
    const result = await checkRateLimit(kv, '127.0.0.1', WINDOW, MAX);
    expect(result.allowed).toBe(true);
    expect(result.remaining).toBe(3);
  });

  it('blocks requests at limit', async () => {
    const now = Math.floor(Date.now() / 1000);
    const requests = [now - 10, now - 20, now - 30, now - 40, now - 50];
    const kv = createMockKV(requests);
    const result = await checkRateLimit(kv, '127.0.0.1', WINDOW, MAX);
    expect(result.allowed).toBe(false);
    expect(result.remaining).toBe(0);
  });

  it('allows requests after old ones expire', async () => {
    const now = Math.floor(Date.now() / 1000);
    const requests = [now - 10, now - 20, now - 30, now - 100, now - 200];
    const kv = createMockKV(requests);
    const result = await checkRateLimit(kv, '127.0.0.1', WINDOW, MAX);
    expect(result.allowed).toBe(true);
    expect(result.remaining).toBe(1);
  });

  it('returns resetAt in the future when allowed', async () => {
    const kv = createMockKV();
    const now = Math.floor(Date.now() / 1000);
    const result = await checkRateLimit(kv, '127.0.0.1', WINDOW, MAX);
    expect(result.allowed).toBe(true);
    expect(result.resetAt).toBeGreaterThanOrEqual(now + WINDOW - 1);
    expect(result.resetAt).toBeLessThanOrEqual(now + WINDOW + 1);
  });

  it('returns correct resetAt when blocked', async () => {
    const now = Math.floor(Date.now() / 1000);
    const requests = [now - 10, now - 20, now - 30, now - 40, now - 50];
    const kv = createMockKV(requests);
    const result = await checkRateLimit(kv, '127.0.0.1', WINDOW, MAX);
    expect(result.allowed).toBe(false);
    expect(result.resetAt).toBe(now - 50 + WINDOW);
  });
});
