import Link from "next/link";
import { getTopics } from "../../../lib/site-data";

export default function TopicsPage({ params }: { params: { locale: string } }) {
  const topics = getTopics(params.locale);

  return (
    <section>
      <h2>Topics</h2>
      <ul>
        {topics.map((topic) => (
          <li key={topic.id}>
            <Link href={`/${params.locale}/topics/${topic.id}`}>
              {topic.name}
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
