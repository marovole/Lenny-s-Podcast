# Change: Build a public, SEO-friendly, multi-language transcript site

## Why
We need a public, fast, SEO-capable website for Lenny’s Podcast transcripts, supporting 8 languages, audio playback, and original podcast links, with low maintenance and quarterly updates.

## What Changes
- Add a Next.js App Router static site for public access.
- Add full multi-language content generation (8 locales).
- Integrate RSS metadata for audio playback and original episode links.
- Add search, guest, topic, framework, failure, and interview pages.
- Add SEO assets (sitemap, hreflang, schema.org).

## Impact
- Affected specs: new capability `public-transcript-site`
- Affected code: new Next.js app under `lenny-podcast-analyzer/` (app, lib, data, public)
