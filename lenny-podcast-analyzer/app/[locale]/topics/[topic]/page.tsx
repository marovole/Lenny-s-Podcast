import Link from "next/link";
import { getEpisodes, getTopics } from "../../../../lib/site-data";
import { LOCALE_CODES } from "../../../../lib/locales";

export function generateStaticParams() {
  const params: { locale: string; topic: string }[] = [];
  for (const locale of LOCALE_CODES) {
    for (const topic of getTopics(locale)) {
      params.push({ locale, topic: topic.id });
    }
  }
  return params;
}

export default function TopicDetail({
  params
}: {
  params: { locale: string; topic: string };
}) {
  const topics = getTopics(params.locale);
  const topic = topics.find((item) => item.id === params.topic);
  const episodes = getEpisodes(params.locale).filter((episode) =>
    episode.topics.includes(params.topic)
  );

  if (!topic) {
    return <p>Topic not found.</p>;
  }

  return (
    <section>
      <h2>{topic.name}</h2>
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
