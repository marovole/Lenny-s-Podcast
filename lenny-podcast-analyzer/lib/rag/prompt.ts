/**
 * Prompt templates for RAG.
 */

import type { Citation, ChatMessage } from './types';

// Token limits to prevent context overflow
const MAX_PROMPT_TOKENS = 6000;  // Conservative limit for model context window
const CHARS_PER_TOKEN = 4;        // Approximate: 4 chars ≈ 1 token for English text

const SYSTEM_PROMPT = `You are Lenny's AI assistant, helping users explore insights from Lenny's Podcast episodes.

IMPORTANT RULES:
1. Only answer based on the provided podcast context. If the answer is not in the context, say "I don't have information about that in the podcast episodes I've reviewed."
2. Attribute every insight to a specific guest by name (e.g., "Marty Cagan argues that…" or "As Shreyas Doshi noted…"). Never blend multiple guests' views without naming who said what.
3. When comparing perspectives across guests, explicitly name each guest and their position.
4. Be conversational and helpful, as if you're Lenny himself sharing insights.
5. Keep responses concise but informative.

FORMAT FOR ATTRIBUTION:
When referencing information, attribute to the guest and episode, e.g. "According to Marty Cagan on [Episode Title]…" or "Shreyas Doshi believes…"`;

/**
 * Build the context section from retrieved segments.
 */
export function buildContextSection(citations: Citation[]): string {
  if (citations.length === 0) {
    return 'No relevant context found.';
  }

  const sections = citations.map((c, i) => {
    return `[${i + 1}] [${c.speaker} | ${c.episode_title}] @ ${c.timestamp}
Content: ${c.content}`;
  });

  return `RELEVANT PODCAST SEGMENTS:\n\n${sections.join('\n\n')}`;
}

/**
 * Estimate token count from text.
 */
function estimateTokens(text: string): number {
  return Math.ceil(text.length / CHARS_PER_TOKEN);
}

/**
 * Build context section with token limit enforcement.
 * Truncates citations if needed to stay within budget.
 */
function buildContextSectionWithLimit(
  citations: Citation[],
  tokenBudget: number
): string {
  if (citations.length === 0) {
    return 'No relevant context found.';
  }

  const header = 'RELEVANT PODCAST SEGMENTS:\n\n';
  let usedTokens = estimateTokens(header);
  const sections: string[] = [];

  for (const [i, citation] of citations.entries()) {
    const section = `[${i + 1}] [${citation.speaker} | ${citation.episode_title}] @ ${citation.timestamp}
Content: ${citation.content}`;
    
    const sectionTokens = estimateTokens(section);
    
    if (usedTokens + sectionTokens > tokenBudget) {
      // Add truncated indicator if we've hit the limit
      if (sections.length > 0) {
        sections.push(`[... ${citations.length - i} more segments omitted due to length]`);
      }
      break;
    }
    
    sections.push(section);
    usedTokens += sectionTokens;
  }

  return header + sections.join('\n\n');
}

/**
 * Build the full prompt for OpenAI.
 */
export function buildPrompt(
  userMessages: ChatMessage[],
  citations: Citation[],
  currentContext?: { episode_slug?: string; episode_title?: string }
): ChatMessage[] {
  // Calculate remaining token budget for context
  const systemPromptTokens = estimateTokens(SYSTEM_PROMPT);
  const userMessagesTokens = userMessages.reduce((sum, m) => sum + estimateTokens(m.content), 0);
  const contextHeaderTokens = currentContext?.episode_title 
    ? estimateTokens(`\n\nThe user is currently reading the episode: "${currentContext.episode_title}". Prioritize information from this episode when relevant.`)
    : 0;
  
  // Reserve 1000 tokens for response
  const reservedTokens = 1000;
  const contextTokenBudget = MAX_PROMPT_TOKENS - systemPromptTokens - userMessagesTokens - contextHeaderTokens - reservedTokens;
  
  // Build context section within token budget
  const contextSection = buildContextSectionWithLimit(citations, Math.max(contextTokenBudget, 500));

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


