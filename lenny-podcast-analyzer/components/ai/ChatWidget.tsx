/**
 * Main Chat Widget - Container component
 * Note: ChatProvider is provided at layout level
 */

'use client';

import { useChat } from './ChatProvider';
import { ChatTrigger } from './ChatTrigger';
import { ChatWindow } from './ChatWindow';
import './ai.css';

export function ChatWidget() {
  const { isOpen } = useChat();

  return (
    <div className="ai-widget-root">
      {isOpen ? <ChatWindow /> : null}
      <ChatTrigger />
    </div>
  );
}
