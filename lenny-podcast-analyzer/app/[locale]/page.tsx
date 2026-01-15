import Link from "next/link";
import { getEpisodes, getSiteMetadata } from "../../lib/site-data";

export default function LocaleHome({ params }: { params: { locale: string } }) {
  const episodes = getEpisodes(params.locale).slice(0, 20);
  const metadata = getSiteMetadata(params.locale);

  return (
    <section className="page-section">
      <h2 className="section-title">Latest Episodes</h2>
      <p className="section-meta">Total episodes: {metadata.total_episodes}</p>
      <ul className="episode-list">
        {episodes.map((episode) => (
          <li key={episode.slug} className="episode-item">
            <Link
              href={`/${params.locale}/episodes/${episode.slug}`}
              className="episode-link"
            >
              {episode.title}
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
