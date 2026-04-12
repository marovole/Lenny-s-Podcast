/**
 * Message List - Displays chat messages
 */

'use client';

import { useRef, useEffect } from 'react';
import { useChat, type ChatMessage } from './ChatProvider';
import { CitationCard } from './CitationCard';

export function MessageList() {
  const { messages, isLoading } = useChat();
  const listRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="ai-messages" ref={listRef}>
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
