import { getFrameworks } from "../../../lib/site-data";

export default function FrameworksPage({ params }: { params: { locale: string } }) {
  const frameworks = getFrameworks(params.locale);

  return (
    <section>
      <h2>Frameworks</h2>
      <ul>
        {frameworks.map((framework) => (
          <li key={framework.id}>
            <h3>{framework.name}</h3>
            <p>{framework.description}</p>
            <p>Source: {framework.source}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
