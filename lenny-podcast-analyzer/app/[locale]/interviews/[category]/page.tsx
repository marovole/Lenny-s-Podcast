import { getInterviewCategories } from "../../../../lib/site-data";
import { LOCALE_CODES } from "../../../../lib/locales";

export function generateStaticParams() {
  const params: { locale: string; category: string }[] = [];
  for (const locale of LOCALE_CODES) {
    for (const category of getInterviewCategories(locale)) {
      params.push({ locale, category: category.id });
    }
  }
  return params;
}

export default function InterviewCategoryPage({
  params
}: {
  params: { locale: string; category: string };
}) {
  const categories = getInterviewCategories(params.locale);
  const category = categories.find((item) => item.id === params.category);

  if (!category) {
    return <p>Category not found.</p>;
  }

  return (
    <section>
      <h2>{category.name}</h2>
      <ul>
        {category.questions.map((question) => (
          <li key={question}>{question}</li>
        ))}
      </ul>
    </section>
  );
}
