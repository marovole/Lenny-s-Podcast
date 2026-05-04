## ADDED Requirements

### Requirement: Multi-Language Static Site Generation
The system SHALL generate a static, SEO-friendly website for Lenny's Podcast transcripts supporting 8 languages: English (en), Spanish (es), French (fr), German (de), Japanese (ja), Korean (ko), Portuguese (pt-br), and Chinese Simplified (zh-cn).

#### Scenario: Site loads in any supported locale
- **WHEN** a user visits any page with a supported locale path
- **THEN** the page renders correctly with all content in that locale

### Requirement: Static Site Architecture
The system SHALL use Next.js App Router with static generation (SSG) for all pages, ensuring fast page loads and minimal server infrastructure requirements.

#### Scenario: Home page loads for default locale
- **WHEN** a user visits the root URL
- **THEN** the site redirects to the default locale (en) landing page

#### Scenario: Locale-specific page generation
- **WHEN** the build process runs
- **THEN** pages are pre-rendered for all 8 supported locales

### Requirement: Episode Pages
The system SHALL display individual podcast episode pages containing transcript content, guest information, episode metadata, and links to original podcast audio.

#### Scenario: Episode page displays transcript
- **WHEN** a user navigates to an episode page
- **THEN** the page displays the episode title, guest name, episode date, transcript content, and a link to the original podcast

#### Scenario: Episode page audio playback link
- **WHEN** an episode page is rendered
- **THEN** an audio_url from RSS mapping is included linking to the original podcast episode

### Requirement: Multi-Language Content
The system SHALL persist translations for all content in static JSON files, with translations generated via batch processing and cached for performance.

#### Scenario: Locale-specific content loads
- **WHEN** a user visits a page with a locale path (e.g., /de/episodes/...)
- **THEN** the German (de) translated content is displayed

#### Scenario: Fallback to English for missing translation
- **WHEN** a translation key is missing for a non-default locale
- **THEN** the system falls back to the English content

### Requirement: Search Functionality
The system SHALL provide client-side search across all episode transcripts using a pre-built search index.

#### Scenario: Search returns relevant episodes
- **WHEN** a user enters a search query
- **THEN** matching episodes are returned with highlighted snippets

#### Scenario: Search index size is capped
- **WHEN** the search index is generated for Cloudflare Pages deployment
- **THEN** the index size is limited to meet deployment constraints

### Requirement: Browse Pages
The system SHALL provide browsable index pages for guests, topics, frameworks, failure cases, and interview questions.

#### Scenario: Topic index page
- **WHEN** a user navigates to /topics
- **THEN** a list of all available topics is displayed

#### Scenario: Guest index page
- **WHEN** a user navigates to /guests
- **THEN** a list of all podcast guests is displayed

### Requirement: SEO Assets
The system SHALL generate SEO assets including sitemap.xml, hreflang tags, and schema.org structured data.

#### Scenario: Sitemap generation
- **WHEN** the build process completes
- **THEN** a sitemap.xml file is generated containing all locale-prefixed URLs

#### Scenario: Hreflang tags for internationalization
- **WHEN** a page is rendered
- **THEN** hreflang tags are included referencing all locale variants of that page

#### Scenario: Schema.org structured data
- **WHEN** an episode page is rendered
- **THEN** JSON-LD schema.org data is included for the podcast episode

### Requirement: Cloudflare Pages Deployment
The system SHALL be deployable to Cloudflare Pages using Wrangler with a build adapter that generates static output.

#### Scenario: Build produces static output
- **WHEN** `npm run build` is executed
- **THEN** a static `out/` directory is generated with all locale variants

#### Scenario: Pages deployment with no-bundle option
- **WHEN** deploying to Cloudflare Pages
- **THEN** the no-bundle Pages deploy command can be used for static-only hosting

### Requirement: RSS Integration
The system SHALL map processed transcripts to RSS feed data for audio_url and episode_url enrichment.

#### Scenario: RSS metadata enrichment
- **WHEN** episode data is processed
- **THEN** audio_url and episode_url are populated from RSS feed mapping

#### Scenario: Manual override for RSS mismatch
- **WHEN** RSS title does not match transcript title
- **THEN** a manual overrides file is consulted for corrections

### Requirement: Navigation Structure
The system SHALL provide a consistent navigation structure with locale-aware routing.

#### Scenario: Language switcher on landing page
- **WHEN** a user visits the landing page
- **THEN** a language selector is displayed showing all 8 supported locales

#### Scenario: Breadcrumb navigation on episode pages
- **WHEN** a user views an episode page
- **THEN** breadcrumb navigation shows: Home > Locale > Episodes > Episode Title
