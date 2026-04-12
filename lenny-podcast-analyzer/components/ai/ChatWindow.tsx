/**
 * Chat Window - Main chat interface
 */

'use client';

import { useRef, useEffect } from 'react';
import { useChat } from './ChatProvider';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';

export function ChatWindow() {
  const { toggleOpen, currentContext } = useChat();
  const windowRef = useRef<HTMLDivElement>(null);

  // Handle escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        toggleOpen();
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [toggleOpen]);

  // Focus trap for accessibility
  useEffect(() => {
    const firstFocusable = windowRef.current?.querySelector<HTMLElement>(
      'button, [tabindex]:not([tabindex="-1"]), input, textarea'
    );
    firstFocusable?.focus();
  }, []);

  return (
    <div
      ref={windowRef}
      className="ai-window"
      role="dialog"
      aria-label="Lenny AI Assistant"
      aria-modal="true"
    >
      <header className="ai-header">
        <div className="ai-header-content">
          <h2 className="ai-title">Lenny AI</h2>
          {currentContext?.title && (
            <span className="ai-context-badge">
              Reading: {currentContext.title}
            </span>
          )}
        </div>
        <button
          type="button"
          className="ai-close-btn"
          onClick={toggleOpen}
          aria-label="Close chat"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </header>

      <MessageList />
      <ChatInput />
    </div>
  );
}
