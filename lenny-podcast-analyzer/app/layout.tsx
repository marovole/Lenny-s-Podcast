import "./globals.css";
import type { ReactNode } from "react";
import { ChatProvider } from "../components/ai/ChatProvider";
import { ChatWidget } from "../components/ai/ChatWidget";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="site-body">
        <ChatProvider>
          <div className="site-root">{children}</div>
          <ChatWidget />
        </ChatProvider>
      </body>
    </html>
  );
}
