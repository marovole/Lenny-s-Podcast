/**
 * RAG system type definitions.
 */

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ChatRequest {
  messages: ChatMessage[];
  filters?: {
    episode_slug?: string;
    speaker?: string;
  };
  top_k?: number;
  stream?: boolean;
}

export interface Citation {
  episode_slug: string;
  episode_title: string;
  speaker: string;
  timestamp: string;
  timestamp_seconds: number;
  content: string;
  segment_index: number;
}

export interface VectorMatch {
  id: string;
  score: number;
  metadata: {
    episode_slug: string;
    episode_title: string;
    speaker: string;
    timestamp: string;
    timestamp_seconds?: number | string;
    segment_index: number;
    content_key: string;
  };
}

export interface StreamEvent {
  type: 'delta' | 'citations' | 'error' | 'done';
  content?: string;
  citations?: Citation[];
  error?: string;
}

// Note: Cloudflare environment bindings are defined locally in route.ts
// to avoid type conflicts with @cloudflare/next-on-pages runtime types.
// See app/api/chat/route.ts for CloudflareEnv interface definition.

// Cloudflare Vectorize types (simplified)
export interface VectorizeIndex {
  query(
    vector: number[],
    options: {
      topK: number;
      returnMetadata?: boolean;
      filter?: Record<string, string>;
    }
  ): Promise<{ matches: VectorMatch[] }>;
}
