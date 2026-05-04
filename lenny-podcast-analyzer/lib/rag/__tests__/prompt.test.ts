import { describe, it, expect } from 'vitest';
import { buildContextSection, buildPrompt } from '../prompt';
import type { Citation, ChatMessage } from '../types';

const sampleCitations: Citation[] = [
  {
    episode_slug: 'brian-chesky',
    episode_title: 'Brian Chesky on Airbnb',
    speaker: 'Brian Chesky',
    timestamp: '00:12:34',
    content: 'The best way to scale is...',
    segment_index: 0,
  },
  {
    episode_slug: 'marty-cagan',
    episode_title: 'Marty Cagan on Product',
    speaker: 'Marty Cagan',
    timestamp: '00:45:00',
    content: 'Product teams need empowered leaders.',
    segment_index: 0,
  },
];

describe('buildContextSection', () => {
  it('returns fallback for empty citations', () => {
    const result = buildContextSection([]);
    expect(result).toBe('No relevant context found.');
  });

  it('formats citations with header', () => {
    const result = buildContextSection(sampleCitations);
    expect(result).toContain('RELEVANT PODCAST SEGMENTS:');
    expect(result).toContain('[1] Episode: "Brian Chesky on Airbnb"');
    expect(result).toContain('[2] Episode: "Marty Cagan on Product"');
    expect(result).toContain('Speaker: Brian Chesky');
    expect(result).toContain('Speaker: Marty Cagan');
  });

  it('includes timestamp and content for each citation', () => {
    const result = buildContextSection(sampleCitations);
    expect(result).toContain('Time: 00:12:34');
    expect(result).toContain('Content: The best way to scale is...');
  });
});

describe('buildPrompt', () => {
  const userMessages: ChatMessage[] = [
    { role: 'user', content: 'How do I scale my startup?' },
  ];

  it('returns messages array with system prompt first', () => {
    const result = buildPrompt(userMessages, sampleCitations);
    expect(result.length).toBeGreaterThan(0);
    expect(result[0].role).toBe('system');
    expect(result[0].content).toContain("You are Lenny's AI assistant");
  });

  it('includes context in system prompt', () => {
    const result = buildPrompt(userMessages, sampleCitations);
    const systemContent = result[0].content;
    expect(systemContent).toContain('RELEVANT PODCAST SEGMENTS:');
    expect(systemContent).toContain('Brian Chesky on Airbnb');
  });

  it('appends user messages after system', () => {
    const result = buildPrompt(userMessages, sampleCitations);
    expect(result[result.length - 1]).toEqual(userMessages[0]);
  });

  it('includes current page context when provided', () => {
    const result = buildPrompt(userMessages, sampleCitations, {
      episode_slug: 'brian-chesky',
      episode_title: 'Brian Chesky on Airbnb',
    });
    const systemContent = result[0].content;
    expect(systemContent).toContain('currently reading the episode');
    expect(systemContent).toContain('Brian Chesky on Airbnb');
    expect(systemContent).toContain('Prioritize information from this episode');
  });

  it('truncates citations when token budget is exceeded', () => {
    // Use 100 citations with long content to ensure truncation fires
    const manyCitations: Citation[] = Array.from({ length: 100 }, (_, i) => ({
      episode_slug: `ep-${i}`,
      episode_title: `Episode ${i}: A very long title that takes up tokens in the context window`,
      speaker: `Speaker ${i}`,
      timestamp: '00:00:00',
      content: 'x'.repeat(300),
      segment_index: i,
    }));

    const result = buildPrompt(userMessages, manyCitations);
    const systemContent = result[0].content;
    expect(systemContent).toContain('omitted due to length');
    const citationCount = (systemContent.match(/\[\d+\] Episode:/g) || []).length;
    expect(citationCount).toBeLessThan(100);
  });

  it('handles empty citations gracefully', () => {
    const result = buildPrompt(userMessages, []);
    const systemContent = result[0].content;
    expect(systemContent).toContain('No relevant context found.');
  });
});
