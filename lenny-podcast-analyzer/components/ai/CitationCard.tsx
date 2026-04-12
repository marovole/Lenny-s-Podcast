/**
 * Citation Card - Shows source reference
 */

'use client';

import Link from 'next/link';
import { useChat, type Citation } from './ChatProvider';

interface CitationCardProps {
  citation: Citation;
}

export function CitationCard({ citation }: CitationCardProps) {
  const { currentContext } = useChat();
  const isCurrentEpisode = currentContext?.slug === citation.episode_slug;

  const handleJumpToTimestamp = () => {
    // Parse timestamp to seconds
    const parts = citation.timestamp.split(':').map(Number);
    let seconds = 0;
    if (parts.length === 3) {
      seconds = parts[0] * 3600 + parts[1] * 60 + parts[2];
    } else if (parts.length === 2) {
      seconds = parts[0] * 60 + parts[1];
    }

    // Find and control the audio element
    const audio = document.getElementById('main-episode-player') as HTMLAudioElement;
    if (audio) {
      audio.currentTime = seconds;
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
          Jump to {citation.timestamp}
        </button>
      ) : (
        <Link
          href={`/en/episodes/${citation.episode_slug}`}
          className="ai-citation-action"
        >
          View Episode
        </Link>
      )}
    </div>
  );
}
