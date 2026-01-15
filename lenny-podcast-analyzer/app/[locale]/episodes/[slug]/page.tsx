import Link from "next/link";
import { getEpisode, getEpisodes } from "../../../../lib/site-data";
import { LOCALE_CODES } from "../../../../lib/locales";

export function generateStaticParams() {
  const params: { locale: string; slug: string }[] = [];
  for (const locale of LOCALE_CODES) {
    for (const episode of getEpisodes(locale)) {
      params.push({ locale, slug: episode.slug });
    }
  }
  return params;
}

export default function EpisodePage({
  params
}: {
  params: { locale: string; slug: string };
}) {
  const episode = getEpisode(params.locale, params.slug);
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "PodcastEpisode",
    name: episode.title,
    url: episode.episode_url,
    associatedMedia: episode.audio_url
      ? { "@type": "MediaObject", contentUrl: episode.audio_url }
      : undefined
  };

  return (
    <article className="episode-article">
      <header className="episode-header">
        <h2 className="episode-title">{episode.title}</h2>
        <div className="episode-actions">
          {episode.episode_url ? (
            <Link
              href={episode.episode_url}
              target="_blank"
              rel="noreferrer"
              className="episode-link-out"
            >
              Original episode
            </Link>
          ) : (
            <span className="episode-link-missing">Original episode link unavailable</span>
          )}
        </div>
        <div className="episode-actions">
          {episode.audio_url ? (
            <audio controls src={episode.audio_url} className="episode-audio">
              Your browser does not support the audio element.
            </audio>
          ) : (
            <span className="episode-link-missing">Audio unavailable</span>
          )}
        </div>
      </header>
      <section className="transcript-section">
        <h3 className="section-title">Transcript</h3>
        {episode.segments.map((segment, index) => (
          <p key={`${segment.timestamp}-${index}`} className="transcript-line">
            <strong className="transcript-speaker">{segment.speaker}</strong>
            <span className="transcript-time">[{segment.timestamp}]</span>
            <span className="transcript-text">{segment.content}</span>
          </p>
        ))}
      </section>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
    </article>
  );
}
