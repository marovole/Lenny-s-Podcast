import Link from "next/link";
import { getFailurePatterns } from "../../../lib/site-data";

export default function FailurePage({ params }: { params: { locale: string } }) {
  const patterns = getFailurePatterns(params.locale);

  return (
    <section>
      <h2>Failure Patterns</h2>
      <ul>
        {patterns.map((pattern) => (
          <li key={pattern.id}>
            <Link href={`/${params.locale}/failure/${pattern.id}`}>
              {pattern.name}
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
