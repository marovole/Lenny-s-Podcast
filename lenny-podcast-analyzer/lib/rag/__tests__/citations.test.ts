import { describe, it, expect } from 'vitest';
import {
  parseTimestampToSeconds,
  formatTimestampSeconds,
  resolveTimestampSeconds,
  buildEpisodeCitationUrl,
  formatCitationLabel,
} from '../citations';

describe('parseTimestampToSeconds', () => {
  it('parses HH:MM:SS', () => {
    expect(parseTimestampToSeconds('01:02:03')).toBe(3723);
  });

  it('parses MM:SS', () => {
    expect(parseTimestampToSeconds('12:34')).toBe(754);
  });

  it('strips trailing parenthesis from dirty timestamps', () => {
    expect(parseTimestampToSeconds('00:41)')).toBe(41);
  });
});

describe('formatTimestampSeconds', () => {
  it('formats seconds as HH:MM:SS', () => {
    expect(formatTimestampSeconds(3723)).toBe('01:02:03');
    expect(formatTimestampSeconds(754)).toBe('00:12:34');
  });
});

describe('resolveTimestampSeconds', () => {
  it('prefers timestamp_seconds metadata', () => {
    expect(resolveTimestampSeconds({ timestamp_seconds: 120, timestamp: '00:00:41)' })).toBe(120);
  });

  it('falls back to parsing timestamp text', () => {
    expect(resolveTimestampSeconds({ timestamp: '00:12:34' })).toBe(754);
  });
});

describe('buildEpisodeCitationUrl', () => {
  it('builds on-site episode URL with time anchor', () => {
    expect(buildEpisodeCitationUrl('en', 'marty-cagan', 754)).toBe(
      '/en/episodes/marty-cagan#t=754'
    );
  });
});

describe('formatCitationLabel', () => {
  it('formats guest attribution label', () => {
    expect(formatCitationLabel('Marty Cagan', 'Marty Cagan on Product', 754)).toBe(
      '[Marty Cagan · Marty Cagan on Product @ 00:12:34]'
    );
  });
});
