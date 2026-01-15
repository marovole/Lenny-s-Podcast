"""
Transcript Processor - Parse podcast transcripts from txt files.
"""
import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any


def parse_timestamp(time_str: str) -> float:
    """Convert timestamp string to seconds."""
    try:
        parts = time_str.strip().split(':')
        if len(parts) == 3:
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + float(s)
        elif len(parts) == 2:
            m, s = parts
            return int(m) * 60 + float(s)
        else:
            return float(s) if '.' in time_str else int(s)
    except:
        return 0.0


def parse_transcript(file_path: str) -> Dict[str, Any]:
    """Parse a single transcript file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    segments = []
    
    # Pattern 1: Speaker (00:00:00): Content on same line
    # Pattern 2: Speaker (00:00:00):\nContent on next line
    
    # Split by speaker pattern - find all speaker headers
    speaker_pattern = r'([A-Za-z][A-Za-z\s\.\-\'\&\+\/]+?)\s*\((\d{1,2}:\d{2}(?::\d{2})?\)):\s*'
    
    # Find all matches
    matches = list(re.finditer(speaker_pattern, content))
    
    for i, match in enumerate(matches):
        speaker = match.group(1).strip()
        timestamp = match.group(2)
        
        # Content starts after the match
        start_pos = match.end()
        
        # Content ends at the next speaker pattern or end of file
        if i + 1 < len(matches):
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(content)
        
        # Extract and clean content
        segment_content = content[start_pos:end_pos].strip()
        
        # Clean up - remove newlines and extra spaces
        segment_content = re.sub(r'\s+', ' ', segment_content)
        
        if segment_content:
            segments.append({
                'speaker': speaker,
                'timestamp': timestamp,
                'timestamp_seconds': parse_timestamp(timestamp),
                'content': segment_content
            })
    
    # Extract metadata from filename
    filename = os.path.basename(file_path)
    episode_name = filename.replace('.txt', '')
    
    # Detect companies mentioned
    company_patterns = [
        'Airbnb', 'Stripe', 'Google', 'Facebook', 'Meta', 'Apple', 'Amazon',
        'Microsoft', 'Netflix', 'Uber', 'Lyft', 'Figma', 'Linear', 'Notion',
        'Slack', 'Discord', 'Twitter', 'Instagram', 'LinkedIn', 'Pinterest',
        'DoorDash', 'Instacart', 'Coinbase', 'Robinhood', 'Square', 'Shopify',
        'Zoom', 'Dropbox', 'Box', 'Okta', 'Datadog', 'Snowflake', 'MongoDB',
        'Redis', 'Elastic', 'Confluence', 'Atlassian', 'Salesforce', 'HubSpot',
        'Intercom', 'Segment', 'Mixpanel', 'Amplitude', 'Optimizely', 'Vercel',
        'Replit', 'Bolt', ' Lovable', 'Perplexity', 'Cursor', 'OpenAI', 'Anthropic'
    ]
    
    companies = []
    for company in company_patterns:
        if company.lower() in content.lower():
            companies.append(company)
    
    companies = list(set(companies))
    
    return {
        'episode_name': episode_name,
        'filename': filename,
        'segments': segments,
        'num_segments': len(segments),
        'full_text': content,
        'companies': companies
    }


def process_all_transcripts(raw_dir: str, output_dir: str) -> List[Dict]:
    """Process all transcript files."""
    raw_path = Path(raw_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    transcripts = []
    
    for file_path in sorted(raw_path.glob('*.txt')):
        print(f"Processing: {file_path.name}")
        try:
            data = parse_transcript(str(file_path))
            transcripts.append(data)
            
            # Save individual file
            output_file = output_path / f"{data['episode_name']}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")
    
    # Save combined index
    index = {
        'total_episodes': len(transcripts),
        'episodes': [
            {
                'episode_name': t['episode_name'],
                'num_segments': t['num_segments'],
                'companies': t['companies']
            }
            for t in transcripts
        ]
    }
    
    with open(output_path / 'index.json', 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)
    
    print(f"\nProcessed {len(transcripts)} episodes")
    return transcripts


def get_all_speakers(transcripts: List[Dict]) -> Dict[str, int]:
    """Count speaker appearances across all transcripts."""
    speaker_counts = {}
    
    for transcript in transcripts:
        for segment in transcript['segments']:
            speaker = segment['speaker']
            speaker_counts[speaker] = speaker_counts.get(speaker, 0) + 1
    
    return dict(sorted(speaker_counts.items(), key=lambda x: -x[1]))


if __name__ == '__main__':
    raw_dir = 'data/raw'
    output_dir = 'data/processed'
    
    transcripts = process_all_transcripts(raw_dir, output_dir)
    
    speakers = get_all_speakers(transcripts)
    print(f"\nTop 20 Speakers:")
    for speaker, count in list(speakers.items())[:20]:
        print(f"  {speaker}: {count}")
