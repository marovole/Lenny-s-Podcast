## Context
We have processed transcript JSONs and a requirement to publish a public, SEO-friendly, multi-language site with audio playback and original podcast links. Updates are quarterly.

## Goals / Non-Goals
- Goals: Fast static site, full 8-language content, SEO baseline, low maintenance.
- Non-Goals: Real-time updates, server-side rendering, per-user personalization.

## Decisions
- Decision: Use Next.js App Router + static generation (SSG).
- Alternatives considered: Streamlit (not SEO friendly), SSR (heavier ops).
- Decision: Persist translations to static JSON; no runtime translation.
- Decision: Use RSS feed for audio_url and episode_url mapping.

## Risks / Trade-offs
- Full translation cost/time → mitigated by batch processing and caching.
- RSS title mismatch → mitigated with manual overrides file.

## Migration Plan
1. Generate base dataset from processed transcripts
2. Enrich with RSS audio + links
3. Translate to 8 locales
4. Build static site
5. Deploy to Cloudflare Pages

## Open Questions
- None (requirements confirmed)
