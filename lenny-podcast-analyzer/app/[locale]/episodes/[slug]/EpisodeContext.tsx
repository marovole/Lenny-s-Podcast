"use client";

import { PageContextTracker } from "../../../../components/ai/PageContextTracker";

interface EpisodeContextProps {
  slug: string;
  title: string;
}

export function EpisodeContext({ slug, title }: EpisodeContextProps) {
  return <PageContextTracker slug={slug} title={title} />;
}
