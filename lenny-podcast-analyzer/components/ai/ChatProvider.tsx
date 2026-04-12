/**
 * Chat store using vanilla React state (no Zustand to avoid extra dependency).
 * Can be upgraded to Zustand if needed.
 */

'use client';

import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  isStreaming?: boolean;
  citations?: Citation[];
}

export interface Citation {
  episode_slug: string;
  episode_title: string;
  speaker: string;
  timestamp: string;
  content: string;
}

export interface PageContext {
  type: 'episode' | 'page';
  slug?: string;
  title?: string;
}

interface ChatState {
  isOpen: boolean;
  messages: ChatMessage[];
  isLoading: boolean;
  currentContext: PageContext | null;
  toggleOpen: () => void;
  setContext: (ctx: PageContext | null) => void;
  addMessage: (msg: ChatMessage) => void;
  updateLastMessage: (content: string, citations?: Citation[]) => void;
  setIsLoading: (loading: boolean) => void;
  clearMessages: () => void;
}

const ChatContext = createContext<ChatState | null>(null);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: "Hi! I'm Lenny's AI assistant. Ask me anything about the podcast episodes - insights from guests, frameworks, career advice, and more.",
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentContext, setCurrentContext] = useState<PageContext | null>(null);

  const toggleOpen = useCallback(() => setIsOpen((prev) => !prev), []);

  const setContext = useCallback((ctx: PageContext | null) => {
    setCurrentContext(ctx);
  }, []);

  const addMessage = useCallback((msg: ChatMessage) => {
    setMessages((prev) => [...prev, msg]);
  }, []);

  const updateLastMessage = useCallback((content: string, citations?: Citation[]) => {
    setMessages((prev) => {
      if (prev.length === 0) return prev;
      const updated = [...prev];
      const last = { ...updated[updated.length - 1] };
      last.content = content;
      if (citations) last.citations = citations;
      last.isStreaming = false;
      updated[updated.length - 1] = last;
      return updated;
    });
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([
      {
        id: 'welcome',
        role: 'assistant',
        content: "Hi! I'm Lenny's AI assistant. Ask me anything about the podcast episodes.",
      },
    ]);
  }, []);

  return (
    <ChatContext.Provider
      value={{
        isOpen,
        messages,
        isLoading,
        currentContext,
        toggleOpen,
        setContext,
        addMessage,
        updateLastMessage,
        setIsLoading,
        clearMessages,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  const context = useContext(ChatContext);
  if (!context) {
    // During SSR/SSG, return a no-op context to prevent errors
    return {
      isOpen: false,
      messages: [],
      isLoading: false,
      currentContext: null,
      toggleOpen: () => {},
      setContext: () => {},
      addMessage: () => {},
      updateLastMessage: () => {},
      setIsLoading: () => {},
      clearMessages: () => {},
    } as ChatState;
  }
  return context;
}
