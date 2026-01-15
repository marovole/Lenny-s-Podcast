"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

type SearchDoc = {
  slug: string;
  title: string;
  speaker: string;
  timestamp: string;
  content: string;
  search_text: string;
};

type SearchIndex = {
  documents: SearchDoc[];
};

export default function SearchClient({ locale }: { locale: string }) {
  const [query, setQuery] = useState("");
  const [index, setIndex] = useState<SearchIndex | null>(null);

  useEffect(() => {
    fetch(`/data/${locale}/search.json`)
      .then((res) => res.json())
      .then((data) => setIndex(data))
      .catch(() => setIndex({ documents: [] }));
  }, [locale]);

  const results = useMemo(() => {
    if (!index || !query.trim()) {
      return [] as SearchDoc[];
    }
    const tokens = query.toLowerCase().split(/\s+/).filter(Boolean);
    return index.documents
      .map((doc) => {
        const score = tokens.reduce((acc, token) => {
          if (doc.search_text.includes(token)) {
            return acc + 1;
          }
          return acc;
        }, 0);
        return { ...doc, score };
      })
      .filter((doc) => doc.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 20);
  }, [index, query]);

  return (
    <section>
      <label htmlFor="search-input">Search transcripts</label>
      <input
        id="search-input"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="Search for topics, speakers, or ideas"
      />
      <ul>
        {results.map((doc, index) => (
          <li key={`${doc.slug}-${doc.timestamp}-${index}`}>
            <Link href={`/${locale}/episodes/${doc.slug}`}>
              {doc.title}
            </Link>
            <div>
              <strong>{doc.speaker}</strong> [{doc.timestamp}]
            </div>
            <p>{doc.content}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
