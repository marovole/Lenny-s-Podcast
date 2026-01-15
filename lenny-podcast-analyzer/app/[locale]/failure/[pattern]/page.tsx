import Link from "next/link";
import { getEpisodes, getFailurePatterns } from "../../../../lib/site-data";
import { LOCALE_CODES } from "../../../../lib/locales";

export function generateStaticParams() {
  const params: { locale: string; pattern: string }[] = [];
  for (const locale of LOCALE_CODES) {
    for (const pattern of getFailurePatterns(locale)) {
      params.push({ locale, pattern: pattern.id });
    }
  }
  return params;
}

export default function FailureDetail({
  params
}: {
  params: { locale: string; pattern: string };
}) {
  const patterns = getFailurePatterns(params.locale);
  const pattern = patterns.find((item) => item.id === params.pattern);
  const episodes = getEpisodes(params.locale).filter((episode) =>
    episode.failure_patterns.includes(params.pattern)
  );

  if (!pattern) {
    return <p>Pattern not found.</p>;
  }

  return (
    <section>
      <h2>{pattern.name}</h2>
      <ul>
        {pattern.examples.map((example) => (
          <li key={example}>{example}</li>
        ))}
      </ul>
      <h3>Episodes</h3>
      <ul>
        {episodes.map((episode) => (
          <li key={episode.slug}>
            <Link href={`/${params.locale}/episodes/${episode.slug}`}>
              {episode.title}
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
