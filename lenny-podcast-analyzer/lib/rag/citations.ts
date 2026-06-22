/**
 * Citation URL and timestamp helpers.
 * Links always point to on-site episode pages with a time anchor.
 */

import { DEFAULT_LOCALE } from '../locales';

/** Parse HH:MM:SS (or MM:SS) timestamp text to seconds. Strips trailing junk like ")". */
export function parseTimestampToSeconds(timestamp: string): number {
  const cleaned = timestamp.replace(/\)$/, '').trim();
  if (!cleaned) return 0;

  const parts = cleaned.split(':').map((p) => parseFloat(p));
  if (parts.some((n) => Number.isNaN(n))) return 0;

  if (parts.length === 3) {
    return Math.floor(parts[0] * 3600 + parts[1] * 60 + parts[2]);
  }
  if (parts.length === 2) {
    return Math.floor(parts[0] * 60 + parts[1]);
  }
  return Math.floor(parts[0]);
}

/** Format seconds as HH:MM:SS for display. */
export function formatTimestampSeconds(seconds: number): string {
  const total = Math.max(0, Math.floor(seconds));
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  return [h, m, s].map((n) => String(n).padStart(2, '0')).join(':');
}

/** Resolve timestamp_seconds from vector metadata, falling back to parsing timestamp text. */
export function resolveTimestampSeconds(metadata: {
  timestamp_seconds?: number | string;
  timestamp?: string;
}): number {
  const raw = metadata.timestamp_seconds;
  if (raw !== undefined && raw !== null && raw !== '') {
    const n = typeof raw === 'number' ? raw : parseFloat(String(raw));
    if (!Number.isNaN(n) && n >= 0) return Math.floor(n);
  }
  return parseTimestampToSeconds(metadata.timestamp || '00:00:00');
}

/** Build on-site episode citation URL: /{locale}/episodes/{slug}#t={seconds} */
export function buildEpisodeCitationUrl(
  locale: string,
  episodeSlug: string,
  timestampSeconds: number
): string {
  const loc = locale || DEFAULT_LOCALE;
  return `/${loc}/episodes/${episodeSlug}#t=${Math.max(0, Math.floor(timestampSeconds))}`;
}

/** Display label: [Speaker · Episode Title @ HH:MM:SS] */
export function formatCitationLabel(
  speaker: string,
  episodeTitle: string,
  timestampSeconds: number
): string {
  const time = formatTimestampSeconds(timestampSeconds);
  return `[${speaker} · ${episodeTitle} @ ${time}]`;
}
