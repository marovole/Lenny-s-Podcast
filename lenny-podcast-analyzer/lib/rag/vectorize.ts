/**
 * Vectorize query utilities.
 * Embeddings come from OpenAI or Ollama (local) — never OpenRouter, which has
 * no embeddings endpoint. Keeping 'openrouter' out of the provider type makes
 * the "openrouter embedding failed" bug impossible to reintroduce.
 */

import type { VectorMatch, Citation } from './types';

const OPENAI_EMBEDDING_URL = 'https://api.openai.com/v1/embeddings';
const OLLAMA_EMBEDDING_URL = process.env.OLLAMA_HOST || 'http://localhost:11434';

// Generic Vectorize index interface
interface VectorizeIndexLike {
  query(
    vector: number[],
    options: {
      topK: number;
      returnMetadata?: boolean;
      filter?: Record<string, string>;
    }
  ): Promise<{ matches: Array<{ id: string; score: number; metadata: Record<string, unknown> }> }>;
}

/**
 * Create embedding for a query string.
 * Supports OpenAI and Ollama (local) APIs.
 */
export async function createQueryEmbedding(
  query: string,
  apiKey: string,
  model: string = 'text-embedding-3-small',
  provider: 'openai' | 'ollama' = 'openai'
): Promise<number[]> {
  // Ollama local embedding
  if (provider === 'ollama') {
    const ollamaModel = model || 'nomic-embed-text';
    const response = await fetch(`${OLLAMA_EMBEDDING_URL}/api/embeddings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: ollamaModel,
        prompt: query,
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Ollama embedding failed: ${error}`);
    }

    const data = await response.json() as { embedding: number[] };
    let embedding = data.embedding;
    
    // Pad to 1536 dimensions to match Vectorize index
    if (embedding.length < 1536) {
      embedding = [...embedding, ...Array(1536 - embedding.length).fill(0.0)];
    } else if (embedding.length > 1536) {
      embedding = embedding.slice(0, 1536);
    }
    
    return embedding;
  }

  // OpenAI embeddings (OpenRouter has no embeddings endpoint).
  const response = await fetch(OPENAI_EMBEDDING_URL, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model,
      input: query,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`OpenAI embedding failed: ${error}`);
  }

  const data = await response.json() as {
    data: Array<{ embedding: number[] }>;
  };

  return data.data[0].embedding;
}

/**
 * Query Vectorize for similar segments.
 */
export async function queryVectorize(
  index: VectorizeIndexLike,
  embedding: number[],
  topK: number = 8,
  filter?: { episode_slug?: string }
): Promise<VectorMatch[]> {
  const queryOptions: {
    topK: number;
    returnMetadata: boolean;
    filter?: Record<string, string>;
  } = {
    topK,
    returnMetadata: true,
  };

  // Add filter if specified
  if (filter?.episode_slug) {
    queryOptions.filter = { episode_slug: filter.episode_slug };
  }

  const result = await index.query(embedding, queryOptions);

  // Map the generic response to VectorMatch
  return result.matches.map((m) => ({
    id: m.id,
    score: m.score,
    metadata: {
      episode_slug: String(m.metadata.episode_slug || ''),
      episode_title: String(m.metadata.episode_title || ''),
      speaker: String(m.metadata.speaker || ''),
      timestamp: String(m.metadata.timestamp || ''),
      segment_index: Number(m.metadata.segment_index || 0),
      content_key: String(m.metadata.content_key || ''),
    },
  }));
}


