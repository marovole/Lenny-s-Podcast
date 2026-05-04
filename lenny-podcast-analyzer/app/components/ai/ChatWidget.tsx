"use client";

import { useChat } from "./ChatProvider";

function ChatTrigger() {
  const { toggleOpen, isOpen } = useChat();

  return (
    <button
      onClick={toggleOpen}
      className={`ai-chat-trigger ${isOpen ? "open" : ""}`}
      aria-label={isOpen ? "Close chat" : "Open chat"}
    >
      <svg
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M12 2C17.5228 2 22 6.47715 22 12C22 17.5228 17.5228 22 12 22H2L12 2Z"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <path
          d="M8 12H16M12 8V16"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </button>
  );
}

function ChatWindow() {
  const { messages, isLoading, sendMessage, clearMessages } = useChat();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const input = form.elements.namedItem("message") as HTMLInputElement;

    if (!input.value.trim() || isLoading) return;

    const message = input.value;
    input.value = "";

    await sendMessage(message);
  };

  return (
    <div className="ai-chat-window">
      <div className="ai-chat-header">
        <div className="ai-chat-header-info">
          <h3>Lenny's AI Assistant</h3>
          <p>Ask me about podcast episodes</p>
        </div>
        <button
          onClick={clearMessages}
          className="ai-chat-clear"
          aria-label="Clear conversation"
          title="Clear conversation"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 16 16"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M2 4H14M6 4V2.5C6 2.22386 5.77614 2 5.5 2H10.5C10.2239 2 10 2.22386 10 2.5V4M8.5 7.5V11.5M7.5 9.5H9.5M6 4H10"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>

      <div className="ai-chat-messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`ai-chat-message ${message.role}`}
          >
            <div className="ai-chat-message-content">
              {message.content}
            </div>
            {message.citations && message.citations.length > 0 && (
              <div className="ai-chat-citations">
                <h4>Sources:</h4>
                {message.citations.map((citation, idx) => (
                  <div key={idx} className="ai-chat-citation">
                    <strong>{citation.episodeTitle}</strong>
                    <span className="timestamp">{citation.timestamp}</span>
                    <p>{citation.segmentText}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="ai-chat-message assistant">
            <div className="ai-chat-message-content ai-chat-typing">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="ai-chat-input">
        <input
          type="text"
          name="message"
          placeholder="Ask about episodes, insights, frameworks..."
          disabled={isLoading}
          autoComplete="off"
        />
        <button type="submit" disabled={isLoading}>
          <svg
            width="20"
            height="20"
            viewBox="0 0 20 20"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M2.5 2.5L17.5 10L2.5 17.5V2.5Z"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </form>
    </div>
  );
}

export function ChatWidget() {
  return (
    <div className="ai-widget-root">
      <ChatWindow />
      <ChatTrigger />
    </div>
  );
}
