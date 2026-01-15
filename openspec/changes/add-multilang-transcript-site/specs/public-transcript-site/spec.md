## ADDED Requirements

### Requirement: Public static site
The system SHALL provide a publicly accessible static website for all transcripts.

#### Scenario: Public access
- **WHEN** a user visits any valid page
- **THEN** the content renders without authentication

### Requirement: Multi-language routing
The system SHALL provide 8 locale routes using the format `/{locale}/...`.

#### Scenario: Locale route resolution
- **WHEN** a user visits `/zh-cn/episodes/{slug}`
- **THEN** the page renders in Simplified Chinese

### Requirement: Episode pages with audio and source link
Each episode page SHALL include an audio player and a link to the original podcast episode.

#### Scenario: Audio and source link
- **WHEN** a user opens an episode page
- **THEN** an audio player and original link are visible

### Requirement: RSS metadata enrichment
The system SHALL use RSS to populate `audio_url` and `episode_url`.

#### Scenario: RSS mapping success
- **WHEN** RSS data matches an episode
- **THEN** `audio_url` and `episode_url` are stored in the dataset

### Requirement: Full translation output
The system SHALL generate full translated transcripts for all supported locales.

#### Scenario: Translation availability
- **WHEN** a locale is selected
- **THEN** the entire transcript renders in that locale

### Requirement: Search capability
The system SHALL provide client-side search per locale.

#### Scenario: Localized search
- **WHEN** a user searches a query on `/en/search`
- **THEN** results are returned from the English index

### Requirement: SEO baseline
The system SHALL generate sitemap, hreflang, and PodcastEpisode structured data.

#### Scenario: SEO assets present
- **WHEN** the site is built
- **THEN** sitemap files and hreflang tags exist
