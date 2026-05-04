/**
 * Message List - Displays chat messages
 */

'use client';

import { useRef, useEffect, useCallback } from 'react';
import { useChat, type ChatMessage } from './ChatProvider';
import { CitationCard } from './CitationCard';

// Distance from bottom threshold for auto-scroll (px)
const AUTO_SCROLL_THRESHOLD = 100;

export function MessageList() {
  const { messages, isLoading } = useChat();
  const listRef = useRef<HTMLDivElement>(null);
  const userScrolledUp = useRef(false);

  // Check if user is near bottom
  const isNearBottom = useCallback(() => {
    const container = listRef.current;
    if (!container) return true;
    
    const distanceFromBottom = container.scrollHeight - container.scrollTop - container.clientHeight;
    return distanceFromBottom < AUTO_SCROLL_THRESHOLD;
  }, []);

  // Handle scroll events
  const handleScroll = useCallback(() => {
    userScrolledUp.current = !isNearBottom();
  }, [isNearBottom]);

  // Smart auto-scroll: only if user is near bottom
  useEffect(() => {
    if (userScrolledUp.current) return;
    
    const container = listRef.current;
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="ai-messages" ref={listRef} onScroll={handleScroll}>
      {messages.map((message) => (
        <MessageItem key={message.id} message={message} />
      ))}
      {isLoading && (
        <div className="ai-message ai-message-assistant">
          <div className="ai-message-bubble ai-message-loading">
            <span className="ai-loading-dot" />
            <span className="ai-loading-dot" />
            <span className="ai-loading-dot" />
          </div>
        </div>
      )}
    </div>
  );
}

function MessageItem({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';

  return (
    <div className={`ai-message ai-message-${message.role}`}>
      <div className={`ai-message-bubble ${message.isStreaming ? 'ai-streaming' : ''}`}>
        {message.content}
      </div>
      {message.citations && message.citations.length > 0 && (
        <div className="ai-citations">
          {message.citations.slice(0, 3).map((citation, idx) => (
            <CitationCard key={idx} citation={citation} />
          ))}
        </div>
      )}
    </div>
  );
}
