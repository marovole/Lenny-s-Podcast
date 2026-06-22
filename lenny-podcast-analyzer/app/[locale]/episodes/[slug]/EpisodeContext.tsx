"use client";

import { PageContextTracker } from "../../../../components/ai/PageContextTracker";

interface EpisodeContextProps {
  slug: string;
  title: string;
  locale: string;
}

export function EpisodeContext({ slug, title, locale }: EpisodeContextProps) {
  return <PageContextTracker slug={slug} title={title} locale={locale} />;
}
