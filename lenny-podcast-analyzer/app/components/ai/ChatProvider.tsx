"use client";

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  ReactNode,
} from "react";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  citations?: {
    episodeId: string;
    episodeTitle: string;
    timestamp: string;
    segmentText: string;
  }[];
}

export interface ChatState {
  isOpen: boolean;
  messages: ChatMessage[];
  isLoading: boolean;
  currentContext: string | null;
  toggleOpen: () => void;
  setContext: (context: string | null) => void;
  addMessage: (message: Omit<ChatMessage, "id">) => void;
  updateLastMessage: (updates: Partial<ChatMessage>) => void;
  setIsLoading: (loading: boolean) => void;
  clearMessages: () => void;
  sendMessage: (content: string) => Promise<void>;
}

const ChatContext = createContext<ChatState | null>(null);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Hi! I'm Lenny's AI assistant. Ask me anything about the podcast episodes - insights from guests, frameworks, career advice, and more.",
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentContext, setCurrentContext] = useState<string | null>(null);

  const toggleOpen = useCallback(() => {
    setIsOpen((prev) => !prev);
  }, []);

  const setContext = useCallback((context: string | null) => {
    setCurrentContext(context);
  }, []);

  const addMessage = useCallback(
    (message: Omit<ChatMessage, "id">) => {
      const newMessage: ChatMessage = {
        ...message,
        id: Math.random().toString(36).substr(2, 9),
      };
      setMessages((prev) => [...prev, newMessage]);
    },
    []
  );

  const updateLastMessage = useCallback((updates: Partial<ChatMessage>) => {
    setMessages((prev) => {
      const newMessages = [...prev];
      const lastIndex = newMessages.length - 1;
      if (lastIndex >= 0) {
        newMessages[lastIndex] = {
          ...newMessages[lastIndex],
          ...updates,
        };
      }
      return newMessages;
    });
  }, []);

  const setIsLoadingChat = useCallback((loading: boolean) => {
    setIsLoading(loading);
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([
      {
        id: "welcome",
        role: "assistant",
        content:
          "Hi! I'm Lenny's AI assistant. Ask me anything about the podcast episodes - insights from guests, frameworks, career advice, and more.",
      },
    ]);
  }, []);

  const sendMessage = useCallback(
    async (content: string) => {
      if (isLoading) return;

      setIsLoading(true);

      // Add user message
      addMessage({
        role: "user",
        content,
      });

      try {
        // Add empty assistant message that we'll stream into
        addMessage({
          role: "assistant",
          content: "",
        });

        const response = await fetch("/api/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            messages: [
              ...messages
                .filter((m) => m.role !== "system")
                .map((m) => ({
                  role: m.role,
                  content: m.content,
                })),
              { role: "user", content },
            ],
            context: currentContext,
          }),
        });

        if (!response.ok) {
          throw new Error("Failed to send message");
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error("No response body");
        }

        const decoder = new TextDecoder();
        let accumulatedContent = "";
        let citations: ChatMessage["citations"] = [];

        while (true) {
          const { done, value } = await reader.read();

          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split("\n");

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const data = line.slice(6);

              if (data === "[DONE]") {
                break;
              }

              try {
                const parsed = JSON.parse(data);
                if (parsed.content) {
                  accumulatedContent += parsed.content;
                  updateLastMessage({
                    content: accumulatedContent,
                    citations: parsed.citations || citations,
                  });
                }
              } catch (e) {
                // Ignore parse errors for keepalive lines
              }
            }
          }
        }
      } catch (error) {
        console.error("Chat error:", error);
        updateLastMessage({
          content:
            "Sorry, I encountered an error. Please check the console for details.",
        });
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading, messages, currentContext, addMessage, updateLastMessage]
  );

  const value: ChatState = {
    isOpen,
    messages,
    isLoading,
    currentContext,
    toggleOpen,
    setContext,
    addMessage,
    updateLastMessage,
    setIsLoading: setIsLoadingChat,
    clearMessages,
    sendMessage,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChat(): ChatState {
  const context = useContext(ChatContext);

  if (!context) {
    // Return a no-op fallback for SSR
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
      sendMessage: async () => {},
    };
  }

  return context;
}
