/**
 * Chat Input - Message input with send button
 */

'use client';

import { useState, useRef, useCallback, type KeyboardEvent, type FormEvent } from 'react';
import { useChat, type ChatMessage, type Citation } from './ChatProvider';

export function ChatInput() {
  const [input, setInput] = useState('');
  const { addMessage, updateLastMessage, setIsLoading, isLoading, currentContext, messages } = useChat();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const sendMessage = useCallback(async () => {
    const content = input.trim();
    if (!content || isLoading) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content,
    };
    addMessage(userMessage);
    setInput('');
    setIsLoading(true);

    // Add placeholder assistant message
    const assistantMessage: ChatMessage = {
      id: `assistant-${Date.now()}`,
      role: 'assistant',
      content: '',
      isStreaming: true,
    };
    addMessage(assistantMessage);

    try {
      // Build request
      const requestMessages = [...messages.filter(m => m.id !== 'welcome'), userMessage].map(m => ({
        role: m.role,
        content: m.content,
      }));

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: requestMessages,
          filters: currentContext?.slug ? { episode_slug: currentContext.slug } : undefined,
          top_k: 8,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      // Read streaming response
      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      const decoder = new TextDecoder();
      let buffer = '';
      let fullContent = '';
      let citations: Citation[] = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim();
            if (!data) continue;

            try {
              const event = JSON.parse(data);
              if (event.type === 'delta' && event.content) {
                fullContent += event.content;
                updateLastMessage(fullContent);
              } else if (event.type === 'citations' && event.citations) {
                citations = event.citations;
              } else if (event.type === 'error') {
                fullContent = 'Sorry, an error occurred. Please try again.';
                updateLastMessage(fullContent);
              }
            } catch {
              // Skip invalid JSON
            }
          }
        }
      }

      // Final update with citations
      if (citations.length > 0) {
        updateLastMessage(fullContent, citations);
      }
    } catch (error) {
      console.error('Chat error:', error);
      updateLastMessage('Sorry, I encountered an error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [input, isLoading, addMessage, updateLastMessage, setIsLoading, currentContext, messages]);

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    sendMessage();
  };

  // Auto-resize textarea
  const handleInput = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  };

  return (
    <form className="ai-input-form" onSubmit={handleSubmit}>
      <textarea
        ref={textareaRef}
        className="ai-input"
        placeholder="Ask about any episode..."
        value={input}
        onChange={(e) => {
          setInput(e.target.value);
          handleInput();
        }}
        onKeyDown={handleKeyDown}
        rows={1}
        disabled={isLoading}
        aria-label="Message Lenny AI"
      />
      <button
        type="submit"
        className="ai-send-btn"
        disabled={!input.trim() || isLoading}
        aria-label="Send message"
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
          <line x1="22" y1="2" x2="11" y2="13" />
          <polygon points="22 2 15 22 11 13 2 9 22 2" />
        </svg>
      </button>
    </form>
  );
}
