"""
LLM Insight Extraction - Extract insights from transcripts using OpenRouter.
"""
import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
except ImportError:
    print("Installing openai...")
    os.system("pip install openai -q")
    from openai import OpenAI


class InsightExtractor:
    def __init__(self, api_key: str = None, model: str = None):
        self.client = OpenAI(
            api_key=api_key or os.getenv('OPENROUTER_API_KEY'),
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = model or os.getenv('LLM_MODEL', 'deepseek/deepseek-r1:free')
    
    def extract_insights(self, transcript: Dict) -> Dict:
        """Extract structured insights from a transcript."""
        full_text = transcript['full_text'][:15000]  # Limit to avoid token limits
        
        prompt = f"""
You are analyzing a podcast transcript. Extract the following insights:

## Episode: {transcript['episode_name']}

### TL;DR Summary (100 words, Chinese):
[One sentence summary in Chinese]

### Key Frameworks/Insights (max 3):
1. [Framework name in Chinese] - [Brief description]
2. ...
3. ...

### Topics Covered (select from list):
product, growth, leadership, hiring, tech_ai, culture, finance, career, design, operations

### Failure Stories (if any):
- [Brief description of any failure stories mentioned]

### Best Quotes (max 3):
1. "..."
2. "..."
3. "..."

### Actionable Advice:
- [One actionable advice from this episode]

Please output as JSON:
{{
    "tldr": "...",
    "frameworks": [{"name": "...", "description": "..."}],
    "topics": ["...", "..."],
    "failure_stories": [{"context": "...", "lesson": "..."}],
    "quotes": ["...", "..."],
    "actionable_advice": "..."
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts insights from podcast transcripts. Always output valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # Try to parse JSON
            try:
                # Handle potential markdown code blocks
                content = content.replace('```json', '').replace('```', '')
                insights = json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from text
                start = content.find('{')
                end = content.rfind('}') + 1
                if start != -1 and end != 0:
                    insights = json.loads(content[start:end])
                else:
                    insights = {"raw_response": content}
            
            insights['episode_name'] = transcript['episode_name']
            return insights
            
        except Exception as e:
            print(f"Error extracting insights for {transcript['episode_name']}: {e}")
            return {
                "episode_name": transcript['episode_name'],
                "error": str(e)
            }
    
    def answer_question(self, question: str, context_chunks: List[Dict]) -> Dict:
        """Answer a question based on retrieved context."""
        context = "\n\n".join([
            f"[{c['episode_name']}] {c['speaker']}: {c['content'][:500]}"
            for c in context_chunks
        ])
        
        prompt = f"""
Based on the following podcast excerpts, answer the user's question.

## Question: {question}

## Relevant Excerpts:
{context}

## Answer (in Chinese):
Provide a comprehensive answer based on the excerpts. Include which episode and speaker each insight comes from.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant answering questions about podcast content. Cite sources."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return {
                "answer": response.choices[0].message.content,
                "sources": [
                    {"episode": c['episode_name'], "speaker": c['speaker']}
                    for c in context_chunks[:3]
                ]
            }
        except Exception as e:
            return {"answer": f"Error: {e}", "sources": []}


def process_all_insights(transcripts: List[Dict], output_dir: str, api_key: str = None):
    """Process all transcripts and extract insights."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    extractor = InsightExtractor(api_key=api_key)
    
    all_insights = []
    
    for i, transcript in enumerate(transcripts):
        print(f"Processing {i+1}/{len(transcripts)}: {transcript['episode_name']}")
        
        insights = extractor.extract_insights(transcript)
        
        # Save individual file
        output_file = output_path / f"{transcript['episode_name']}_insights.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False)
        
        all_insights.append(insights)
        
        # Rate limiting
        time.sleep(0.5)
    
    # Save combined index
    index = {
        'total_episodes': len(all_insights),
        'insights': [
            {
                'episode_name': i['episode_name'],
                'tldr': i.get('tldr', ''),
                'topics': i.get('topics', []),
                'frameworks': i.get('frameworks', []),
                'actionable_advice': i.get('actionable_advice', '')
            }
            for i in all_insights if 'error' not in i
        ]
    }
    
    with open(output_path / 'index.json', 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)
    
    print(f"\nExtracted insights from {len(all_insights)} episodes")
    return all_insights


if __name__ == '__main__':
    # Load processed transcripts
    with open('data/processed/index.json', 'r') as f:
        index = json.load(f)
    
    transcripts = []
    for ep in index['episodes']:
        with open(f"data/processed/{ep['episode_name']}.json", 'r') as f:
            transcripts.append(json.load(f))
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        api_key = input("Enter OpenRouter API Key: ")
    
    process_all_insights(transcripts, 'data/insights', api_key)
