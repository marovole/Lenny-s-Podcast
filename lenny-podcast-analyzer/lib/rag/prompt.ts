/**
 * Prompt templates for RAG.
 */

import type { Citation, ChatMessage } from './types';

const SYSTEM_PROMPT = `You are Lenny's AI assistant, helping users explore insights from Lenny's Podcast episodes.

IMPORTANT RULES:
1. Only answer based on the provided podcast context. If the answer is not in the context, say "I don't have information about that in the podcast episodes I've reviewed."
2. Always cite your sources using the episode title and timestamp.
3. Be conversational and helpful, as if you're Lenny himself sharing insights.
4. When quoting, use the speaker's name (e.g., "As Brian Chesky mentioned...").
5. Keep responses concise but informative.

FORMAT FOR CITATIONS:
When referencing information, include inline citations like: "According to [Episode Title] (timestamp)..."`;

/**
 * Build the context section from retrieved segments.
 */
export function buildContextSection(citations: Citation[]): string {
  if (citations.length === 0) {
    return 'No relevant context found.';
  }

  const sections = citations.map((c, i) => {
    return `[${i + 1}] Episode: "${c.episode_title}" | Speaker: ${c.speaker} | Time: ${c.timestamp}
Content: ${c.content}`;
  });

  return `RELEVANT PODCAST SEGMENTS:\n\n${sections.join('\n\n')}`;
}

/**
 * Build the full prompt for OpenAI.
 */
export function buildPrompt(
  userMessages: ChatMessage[],
  citations: Citation[],
  currentContext?: { episode_slug?: string; episode_title?: string }
): ChatMessage[] {
  const contextSection = buildContextSection(citations);

  let systemContent = SYSTEM_PROMPT;

  // Add current page context if available
  if (currentContext?.episode_title) {
    systemContent += `\n\nThe user is currently reading the episode: "${currentContext.episode_title}". Prioritize information from this episode when relevant.`;
  }

  systemContent += `\n\n${contextSection}`;

  return [
    { role: 'system', content: systemContent },
    ...userMessages,
  ];
}

/**
 * Format citations for output.
 */
export function formatCitationsForOutput(citations: Citation[]): string {
  if (citations.length === 0) return '';

  const formatted = citations.map((c, i) => {
    return `[${i + 1}] ${c.episode_title} (${c.timestamp}) - ${c.speaker}`;
  });

  return `\n\nSources:\n${formatted.join('\n')}`;
}
