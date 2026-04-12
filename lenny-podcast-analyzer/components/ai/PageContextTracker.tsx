/**
 * Page Context Tracker - Sets the current page context for chat
 */

'use client';

import { useEffect } from 'react';
import { useChat } from './ChatProvider';

interface PageContextTrackerProps {
  slug: string;
  title: string;
}

export function PageContextTracker({ slug, title }: PageContextTrackerProps) {
  const { setContext } = useChat();

  useEffect(() => {
    setContext({ type: 'episode', slug, title });
    return () => setContext(null);
  }, [slug, title, setContext]);

  return null;
}
