import { LOCALE_CODES } from "../../lib/locales";
import { getEpisodes } from "../../lib/site-data";

const SITE_URL = process.env.SITE_URL ?? "https://example.com";

export const dynamic = "force-static";

function buildUrlset(): string {
  const urls: string[] = [];

  for (const locale of LOCALE_CODES) {
    urls.push(`${SITE_URL}/${locale}/`);
    urls.push(`${SITE_URL}/${locale}/search/`);
    urls.push(`${SITE_URL}/${locale}/episodes/`);
    urls.push(`${SITE_URL}/${locale}/guests/`);
    urls.push(`${SITE_URL}/${locale}/topics/`);
    urls.push(`${SITE_URL}/${locale}/frameworks/`);
    urls.push(`${SITE_URL}/${locale}/failure/`);
    urls.push(`${SITE_URL}/${locale}/interviews/`);

    for (const episode of getEpisodes(locale)) {
      urls.push(`${SITE_URL}/${locale}/episodes/${episode.slug}/`);
    }
  }

  const items = urls
    .map((url) => `<url><loc>${url}</loc></url>`)
    .join("");

  return `<?xml version="1.0" encoding="UTF-8"?>` +
    `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${items}</urlset>`;
}

export async function GET() {
  const xml = buildUrlset();
  return new Response(xml, {
    headers: {
      "Content-Type": "application/xml"
    }
  });
}
