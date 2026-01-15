import SearchClient from "./search-client";

export default function SearchPage({ params }: { params: { locale: string } }) {
  return (
    <section className="page-section">
      <h2 className="section-title">Search</h2>
      <div className="search-shell">
        <SearchClient locale={params.locale} />
      </div>
    </section>
  );
}
