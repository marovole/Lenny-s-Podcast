import { describe, it, expect } from 'vitest';
import { getClientIp } from '../rate-limit';

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
