import Link from "next/link";
import type { Metadata } from "next";
import type { ReactNode } from "react";
import { LOCALES, LOCALE_CODES } from "../../lib/locales";

const SITE_URL = process.env.SITE_URL ?? "https://example.com";

export function generateStaticParams() {
  return LOCALE_CODES.map((locale) => ({ locale }));
}

export function generateMetadata({ params }: { params: { locale: string } }): Metadata {
  const languages: Record<string, string> = {};
  for (const locale of LOCALES) {
    languages[locale.code] = `${SITE_URL}/${locale.code}/`;
  }

  return {
    alternates: {
      canonical: `${SITE_URL}/${params.locale}/`,
      languages
    }
  };
}

export default function LocaleLayout({
  children,
  params
}: {
  children: ReactNode;
  params: { locale: string };
}) {
  const currentLocale = params.locale;
  return (
    <section className="page-shell">
      <header className="site-header">
        <h1 className="site-title">
          <Link href={`/${currentLocale}`} className="site-title-link">
            Lenny&apos;s Podcast Transcripts
          </Link>
        </h1>
        <nav className="site-nav">
          <ul className="site-nav-list">
            <li className="site-nav-item">
              <Link href={`/${currentLocale}/search`} className="site-nav-link">
                Search
              </Link>
            </li>
            <li className="site-nav-item">
              <Link href={`/${currentLocale}/episodes/`} className="site-nav-link">
                Episodes
              </Link>
            </li>
            <li className="site-nav-item">
              <Link href={`/${currentLocale}/guests`} className="site-nav-link">
                Guests
              </Link>
            </li>
            <li className="site-nav-item">
              <Link href={`/${currentLocale}/topics`} className="site-nav-link">
                Topics
              </Link>
            </li>
            <li className="site-nav-item">
              <Link href={`/${currentLocale}/frameworks`} className="site-nav-link">
                Frameworks
              </Link>
            </li>
            <li className="site-nav-item">
              <Link href={`/${currentLocale}/failure`} className="site-nav-link">
                Failure
              </Link>
            </li>
            <li className="site-nav-item">
              <Link href={`/${currentLocale}/interviews`} className="site-nav-link">
                Interviews
              </Link>
            </li>
          </ul>
        </nav>
        <section className="locale-switcher">
          <span className="locale-label">Language:</span>
          <ul className="locale-list">
            {LOCALES.map((locale) => (
              <li key={locale.code} className="locale-item">
                <Link href={`/${locale.code}`} className="locale-link">
                  {locale.label}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      </header>
      <main className="site-main">{children}</main>
    </section>
  );
}
