/**
 * Page Context Tracker - Sets the current page context for chat
 */

'use client';

import { useEffect } from 'react';
import { useChat } from './ChatProvider';

interface PageContextTrackerProps {
  slug: string;
  title: string;
  locale?: string;
}

export function PageContextTracker({ slug, title, locale }: PageContextTrackerProps) {
  const { setContext } = useChat();

  useEffect(() => {
    setContext({ type: 'episode', slug, title, locale });
    return () => setContext(null);
  }, [slug, title, locale, setContext]);

  return null;
}
