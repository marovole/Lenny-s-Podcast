/**
 * Chat API Route Handler
 *
 * POST /api/chat
 * Handles RAG-based chat with streaming responses.
 */

import { NextRequest } from 'next/server';
import { getRequestContext } from '@cloudflare/next-on-pages';
import type { ChatRequest, Citation, StreamEvent } from '../../../lib/rag/types';
import { createQueryEmbedding, queryVectorize } from '../../../lib/rag/vectorize';
import { buildPrompt } from '../../../lib/rag/prompt';
import { checkRateLimit, getClientIp } from '../../../lib/rag/rate-limit';

export const runtime = 'edge';

// Support both OpenRouter (recommended, free) and OpenAI
const OPENROUTER_CHAT_URL = 'https://openrouter.ai/api/v1/chat/completions';
const OPENAI_CHAT_URL = 'https://api.openai.com/v1/chat/completions';
const OPENROUTER_EMBEDDING_URL = 'https://openrouter.ai/api/v1/embeddings';
const OPENAI_EMBEDDING_URL = 'https://api.openai.com/v1/embeddings';

// Type for Cloudflare env (using local interfaces to avoid strict type conflicts)
interface KVNamespaceLike {
  get(key: string, type: 'json'): Promise<unknown>;
  put(key: string, value: string, options?: { expirationTtl?: number }): Promise<void>;
}

interface CloudflareEnv {
  VECTORIZE_INDEX: {
    query(vector: number[], options: { topK: number; returnMetadata?: boolean; filter?: Record<string, string> }): Promise<{ matches: Array<{ id: string; score: number; metadata: Record<string, unknown> }> }>;
  };
  R2_SEGMENTS: {
    get(key: string): Promise<{ text(): Promise<string> } | null>;
  };
  RATE_LIMIT_KV: KVNamespaceLike;
  OPENROUTER_API_KEY?: string; // Recommended (free tier)
  OPENAI_API_KEY?: string; // Alternative
  OPENAI_CHAT_MODEL: string;
  OPENAI_EMBEDDING_MODEL: string;
  OLLAMA_HOST?: string; // Optional: for local embeddings
  OLLAMA_MODEL?: string; // Optional: Ollama model name
  RATE_LIMIT_WINDOW_SECONDS: string;
  RATE_LIMIT_MAX: string;
}

export async function POST(request: NextRequest) {
  try {
    const ctx = getRequestContext();
    const env = ctx.env as unknown as CloudflareEnv;

    // Parse request body
    let body: ChatRequest;
    try {
      body = await request.json();
    } catch {
      return errorResponse('Invalid JSON body', 400);
    }

    // Validate request
    if (!body.messages || !Array.isArray(body.messages) || body.messages.length === 0) {
      return errorResponse('messages array is required', 400);
    }

    // Rate limiting
    const clientIp = getClientIp(request);
    const windowSeconds = parseInt(env.RATE_LIMIT_WINDOW_SECONDS || '60', 10);
    const maxRequests = parseInt(env.RATE_LIMIT_MAX || '30', 10);

    const rateLimit = await checkRateLimit(env.RATE_LIMIT_KV, clientIp, windowSeconds, maxRequests);
    if (!rateLimit.allowed) {
      return errorResponse('Rate limit exceeded', 429, {
        'Retry-After': String(rateLimit.resetAt - Math.floor(Date.now() / 1000)),
        'X-RateLimit-Remaining': '0',
      });
    }

    // Extract the last user message for embedding
    const lastUserMessage = body.messages
      .filter((m) => m.role === 'user')
      .pop();

    if (!lastUserMessage) {
      return errorResponse('No user message found', 400);
    }

    // Determine API provider (prefer OpenRouter for free tier)
    const useOpenRouter = !!env.OPENROUTER_API_KEY;
    const apiKey = useOpenRouter ? env.OPENROUTER_API_KEY : env.OPENAI_API_KEY;

    if (!apiKey) {
      return errorResponse('No API key configured', 500);
    }

    // Check if Ollama is configured for local embeddings
    const useOllama = !!env.OLLAMA_HOST;
    
    // Create query embedding
    let embedding: number[];
    try {
      if (useOllama) {
        // Use Ollama for local embeddings
        embedding = await createQueryEmbedding(
          lastUserMessage.content,
          '', // No API key needed for Ollama
          env.OLLAMA_MODEL || 'nomic-embed-text',
          'ollama'
        );
      } else {
        // Use OpenRouter or OpenAI
        embedding = await createQueryEmbedding(
          lastUserMessage.content,
          apiKey,
          env.OPENAI_EMBEDDING_MODEL,
          useOpenRouter ? 'openrouter' : 'openai'
        );
      }
    } catch (error) {
      console.error('Embedding error:', error);
      return errorResponse('Failed to create query embedding', 500);
    }

    // Query Vectorize
    const topK = Math.min(body.top_k ?? 8, 20);
    const matches = await queryVectorize(
      env.VECTORIZE_INDEX,
      embedding,
      topK,
      body.filters
    );

    // Fetch content for citations
    const citations: Citation[] = [];
    for (const match of matches) {
      // Try to get content from R2
      let content = '';
      try {
        const obj = await env.R2_SEGMENTS.get(match.metadata.content_key);
        if (obj) {
          content = await obj.text();
        }
      } catch {
        // Fallback: content not available
      }

      citations.push({
        episode_slug: match.metadata.episode_slug,
        episode_title: match.metadata.episode_title,
        speaker: match.metadata.speaker || 'Unknown',
        timestamp: match.metadata.timestamp || '00:00:00',
        segment_index: match.metadata.segment_index,
        content,
      });
    }

    // Build prompt
    const currentContext = body.filters?.episode_slug
      ? {
          episode_slug: body.filters.episode_slug,
          episode_title: citations.find(c => c.episode_slug === body.filters?.episode_slug)?.episode_title,
        }
      : undefined;

    const messages = buildPrompt(body.messages, citations, currentContext);

    // Stream response from OpenRouter or OpenAI
    const endpoint = useOpenRouter ? OPENROUTER_CHAT_URL : OPENAI_CHAT_URL;

    const headers: Record<string, string> = {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    };

    // Add OpenRouter specific headers
    if (useOpenRouter) {
      headers['HTTP-Referer'] = 'https://lennypodcast.com';
      headers['X-Title'] = 'Lenny Podcast AI Chat';
    }

    const chatResponse = await fetch(endpoint, {
      method: 'POST',
      headers,
      signal: AbortSignal.timeout(25000), // 25s timeout before CF 30s limit
      body: JSON.stringify({
        model: env.OPENAI_CHAT_MODEL,
        messages,
        stream: true,
        max_tokens: 1024,
      }),
    });

    if (!chatResponse.ok) {
      const error = await chatResponse.text();
      console.error(`${useOpenRouter ? 'OpenRouter' : 'OpenAI'} error:`, error);
      return errorResponse('AI service error', 502);
    }

    // Create streaming response
    const encoder = new TextEncoder();
    const decoder = new TextDecoder();

    const stream = new ReadableStream({
      async start(controller) {
        const reader = chatResponse.body?.getReader();
        if (!reader) {
          controller.close();
          return;
        }

        let buffer = '';

        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            // Split on \n, handling both \n and \r\n line endings
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const rawLine of lines) {
              // Remove potential \r at end (for \r\n endings)
              const line = rawLine.replace(/\r$/, '');
              if (!line.startsWith('data: ')) continue;
              
              const data = line.slice(6).trim();
              if (data === '[DONE]') {
                  // Send citations at the end
                  const citationEvent: StreamEvent = {
                    type: 'citations',
                    citations: citations.filter(c => c.content), // Only include citations with content
                  };
                  controller.enqueue(encoder.encode(`data: ${JSON.stringify(citationEvent)}\n\n`));

                  const doneEvent: StreamEvent = { type: 'done' };
                  controller.enqueue(encoder.encode(`data: ${JSON.stringify(doneEvent)}\n\n`));
                  continue;
                }

                try {
                  const parsed = JSON.parse(data);
                  const content = parsed.choices?.[0]?.delta?.content;
                  if (content) {
                    const deltaEvent: StreamEvent = { type: 'delta', content };
                    controller.enqueue(encoder.encode(`data: ${JSON.stringify(deltaEvent)}\n\n`));
                  }
                } catch {
                  // Skip invalid JSON
                }
              }
            }
          }
        } catch (error) {
          const errorEvent: StreamEvent = {
            type: 'error',
            error: 'Stream error',
          };
          controller.enqueue(encoder.encode(`data: ${JSON.stringify(errorEvent)}\n\n`));
        } finally {
          controller.close();
        }
      },
    });

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'X-RateLimit-Remaining': String(rateLimit.remaining),
      },
    });
  } catch (error) {
    console.error('Chat API error:', error);
    // Handle timeout specifically
    if (error instanceof Error && error.name === 'TimeoutError') {
      return errorResponse('AI service timed out. Please try again.', 504, {
        'X-RateLimit-Remaining': String(rateLimit?.remaining ?? 30),
      });
    }
    return errorResponse('Internal server error', 500);
  }
}

function errorResponse(message: string, status: number, headers?: Record<string, string>) {
  return new Response(JSON.stringify({ error: message }), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
  });
}
