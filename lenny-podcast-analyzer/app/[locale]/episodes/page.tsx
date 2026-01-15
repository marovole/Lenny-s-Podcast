import Link from "next/link";
import { getEpisodes } from "../../../lib/site-data";

export default function EpisodeIndex({ params }: { params: { locale: string } }) {
  const episodes = getEpisodes(params.locale);

  return (
    <section className="page-section">
      <h2 className="section-title">All Episodes</h2>
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
