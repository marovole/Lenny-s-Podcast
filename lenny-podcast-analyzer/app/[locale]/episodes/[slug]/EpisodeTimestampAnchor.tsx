"use client";

import { useEffect } from "react";

/** Seek episode audio to #t={seconds} when the page loads with a time hash. */
export function EpisodeTimestampAnchor() {
  useEffect(() => {
    const seekFromHash = () => {
      const match = window.location.hash.match(/^#t=(\d+)$/);
      if (!match) return;

      const seconds = parseInt(match[1], 10);
      if (Number.isNaN(seconds)) return;

      const audio = document.getElementById("main-episode-player") as HTMLAudioElement | null;
      if (!audio) return;

      const seek = () => {
        audio.currentTime = seconds;
      };

      if (audio.readyState >= 1) {
        seek();
      } else {
        audio.addEventListener("loadedmetadata", seek, { once: true });
      }
    };

    seekFromHash();
    window.addEventListener("hashchange", seekFromHash);
    return () => window.removeEventListener("hashchange", seekFromHash);
  }, []);

  return null;
}
