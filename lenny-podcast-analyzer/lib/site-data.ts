import fs from "fs";
import path from "path";

export type EpisodeSegment = {
  speaker: string;
  timestamp: string;
  timestamp_seconds: number;
  content: string;
};

export type EpisodeSummary = {
  slug: string;
  title: string;
  num_segments: number;
  topics: string[];
  failure_patterns: string[];
  companies: string[];
};

export type EpisodeDetail = EpisodeSummary & {
  audio_url?: string;
  episode_url?: string;
  segments: EpisodeSegment[];
  full_text: string;
};

export type SiteMetadata = {
  locale: string;
  updated_at: string;
  total_episodes: number;
  topics: { id: string; name: string }[];
  locales: { code: string; label: string }[];
};

const DATA_ROOT = path.join(process.cwd(), "data", "site");

function readJson<T>(filePath: string): T {
  const raw = fs.readFileSync(filePath, "utf-8");
  return JSON.parse(raw) as T;
}

export function getSiteMetadata(locale: string): SiteMetadata {
  return readJson<SiteMetadata>(path.join(DATA_ROOT, locale, "site.json"));
}

export function getEpisodes(locale: string): EpisodeSummary[] {
  return readJson<EpisodeSummary[]>(path.join(DATA_ROOT, locale, "episodes", "index.json"));
}

export function getEpisode(locale: string, slug: string): EpisodeDetail {
  return readJson<EpisodeDetail>(path.join(DATA_ROOT, locale, "episodes", `${slug}.json`));
}

export function getGuests(locale: string): { name: string; slug: string; episode_slug: string }[] {
  return readJson<{ name: string; slug: string; episode_slug: string }[]>(
    path.join(DATA_ROOT, locale, "guests.json")
  );
}

export function getTopics(locale: string): { id: string; name: string; episodes: string[] }[] {
  return readJson<{ id: string; name: string; episodes: string[] }[]>(
    path.join(DATA_ROOT, locale, "topics.json")
  );
}

export function getFrameworks(locale: string): {
  id: string;
  name: string;
  description: string;
  source: string;
}[] {
  return readJson(
    path.join(DATA_ROOT, locale, "frameworks.json")
  );
}

export function getFailurePatterns(locale: string): {
  id: string;
  name: string;
  examples: string[];
  episodes: string[];
}[] {
  return readJson(path.join(DATA_ROOT, locale, "failure.json"));
}

export function getInterviewCategories(locale: string): {
  id: string;
  name: string;
  questions: string[];
}[] {
  return readJson(path.join(DATA_ROOT, locale, "interviews.json"));
}
