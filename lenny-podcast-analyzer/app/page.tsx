import Link from "next/link";
import { DEFAULT_LOCALE, LOCALES } from "../lib/locales";

export default function RootPage() {
  return (
    <main className="landing-page">
      <section className="landing-hero" aria-labelledby="hero-title">
        <span className="landing-badge">Interactive Explorer</span>
        <h1 id="hero-title" className="landing-title">
          Lenny&apos;s Podcast <br />
          <span className="landing-title-accent">Insights</span>
        </h1>
        <p className="landing-tagline">
          Extract, organize, and visualize high-value insights from 320+ episodes.
        </p>
      </section>

      <section className="landing-description" aria-describedby="landing-desc">
        <p id="landing-desc" className="landing-summary">
          Navigate product, growth, and leadership wisdom through semantic search,
          topic browsing, and curated frameworks.
        </p>
      </section>

      <section className="landing-language" aria-labelledby="lang-title">
        <h2 id="lang-title" className="landing-section-title">
          Select Language
        </h2>
        <div className="landing-language-grid">
          {LOCALES.map((locale) => (
            <Link
              key={locale.code}
              href={`/${locale.code}`}
              className={`landing-lang-card ${
                locale.code === DEFAULT_LOCALE ? "landing-lang-default" : ""
              }`}
            >
              <span className="landing-lang-label">{locale.label}</span>
              {locale.code === DEFAULT_LOCALE && (
                <span className="landing-lang-badge">Default</span>
              )}
            </Link>
          ))}
        </div>
      </section>

      <section className="landing-features" aria-labelledby="features-title">
        <h2 id="features-title" className="landing-section-title">
          Explore
        </h2>
        <div className="landing-features-grid">
          <Link
            href={`/${DEFAULT_LOCALE}/search`}
            className="landing-feature-card"
          >
            <span className="landing-feature-icon" aria-hidden="true">
              🔍
            </span>
            <span className="landing-feature-title">Semantic Search</span>
            <span className="landing-feature-desc">
              Natural language queries across all episodes.
            </span>
          </Link>
          <Link
            href={`/${DEFAULT_LOCALE}/topics`}
            className="landing-feature-card"
          >
            <span className="landing-feature-icon" aria-hidden="true">
              📚
            </span>
            <span className="landing-feature-title">Browse Topics</span>
            <span className="landing-feature-desc">
              Product, growth, leadership, and more.
            </span>
          </Link>
          <Link
            href={`/${DEFAULT_LOCALE}/frameworks`}
            className="landing-feature-card"
          >
            <span className="landing-feature-icon" aria-hidden="true">
              🧠
            </span>
            <span className="landing-feature-title">Framework Library</span>
            <span className="landing-feature-desc">
              Expert decision-making frameworks.
            </span>
          </Link>
          <Link
            href={`/${DEFAULT_LOCALE}/failure`}
            className="landing-feature-card"
          >
            <span className="landing-feature-icon" aria-hidden="true">
              📕
            </span>
            <span className="landing-feature-title">Failure Playbook</span>
            <span className="landing-feature-desc">
              Learn from curated failure case studies.
            </span>
          </Link>
        </div>
      </section>
    </main>
  );
}
