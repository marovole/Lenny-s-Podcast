import Link from "next/link";
import { DEFAULT_LOCALE, LOCALES } from "../lib/locales";

export default function RootPage() {
  return (
    <main>
      <h1>Lenny&apos;s Podcast Transcripts</h1>
      <p>Select a language to continue.</p>
      <ul>
        {LOCALES.map((locale) => (
          <li key={locale.code}>
            <Link href={`/${locale.code}`}>{locale.label}</Link>
          </li>
        ))}
      </ul>
      <p>Default locale: {DEFAULT_LOCALE}</p>
    </main>
  );
}
