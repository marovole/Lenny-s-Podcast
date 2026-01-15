import Link from "next/link";
import { getInterviewCategories } from "../../../lib/site-data";

export default function InterviewsPage({ params }: { params: { locale: string } }) {
  const categories = getInterviewCategories(params.locale);

  return (
    <section>
      <h2>Interview Questions</h2>
      <ul>
        {categories.map((category) => (
          <li key={category.id}>
            <Link href={`/${params.locale}/interviews/${category.id}`}>
              {category.name}
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}
