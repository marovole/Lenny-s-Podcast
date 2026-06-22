/**
 * Citation Card - Shows source reference with guest attribution and on-site link.
 */

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useChat, type Citation } from './ChatProvider';
import {
  buildEpisodeCitationUrl,
  formatCitationLabel,
} from '../../lib/rag/citations';
import { DEFAULT_LOCALE, LOCALE_CODES } from '../../lib/locales';

interface CitationCardProps {
  citation: Citation;
}

function useLocaleFromPath(): string {
  const pathname = usePathname();
  const segment = pathname?.split('/')[1];
  return segment && LOCALE_CODES.includes(segment) ? segment : DEFAULT_LOCALE;
}

export function CitationCard({ citation }: CitationCardProps) {
  const { currentContext } = useChat();
  const pathLocale = useLocaleFromPath();
  const locale = currentContext?.locale ?? pathLocale;
  const isCurrentEpisode = currentContext?.slug === citation.episode_slug;
  const timestampSeconds = citation.timestamp_seconds ?? 0;
  const label = formatCitationLabel(
    citation.speaker,
    citation.episode_title,
    timestampSeconds
  );
  const episodeUrl = buildEpisodeCitationUrl(
    locale,
    citation.episode_slug,
    timestampSeconds
  );

  const handleJumpToTimestamp = () => {
    const audio = document.getElementById('main-episode-player') as HTMLAudioElement;
    if (audio) {
      audio.currentTime = timestampSeconds;
      audio.play().catch(() => {
        // Autoplay may be blocked
      });
    }
  };

  return (
    <div className="ai-citation-card">
      <div className="ai-citation-header">
        <span className="ai-citation-speaker">{citation.speaker}</span>
        <span className="ai-citation-time">{citation.timestamp}</span>
      </div>
      <div className="ai-citation-title">{citation.episode_title}</div>
      {isCurrentEpisode ? (
        <button
          type="button"
          className="ai-citation-action"
          onClick={handleJumpToTimestamp}
        >
          {label}
        </button>
      ) : (
        <Link href={episodeUrl} className="ai-citation-action">
          {label}
        </Link>
      )}
    </div>
  );
}
