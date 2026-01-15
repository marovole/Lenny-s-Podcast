"""
Simple Text Search for Podcast Transcripts.
Uses keyword matching and simple scoring instead of vector search.
"""
import os
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple
from dotenv import load_dotenv

load_dotenv()


class PodcastSearch:
    def __init__(self):
        self.documents = []
        self.episodes = {}  # episode_name -> segments
    
    def build_index(self, processed_dir: str, output_dir: str):
        """Build simple text index from processed transcripts."""
        processed_path = Path(processed_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print("Loading transcripts...")
        self.documents = []
        self.episodes = {}
        
        for file_path in sorted(processed_path.glob('*.json')):
            if file_path.name == 'index.json':
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            episode_name = data['episode_name']
            self.episodes[episode_name] = data
            
            for segment in data['segments']:
                # Create searchable text
                search_text = f"{segment['speaker']} {segment['content']}".lower()
                
                self.documents.append({
                    'episode_name': episode_name,
                    'speaker': segment['speaker'],
                    'timestamp': segment['timestamp'],
                    'content': segment['content'],
                    'search_text': search_text,
                    'words': set(re.findall(r'\b\w+\b', search_text))
                })
        
        print(f"Loaded {len(self.documents)} segments from {len(self.episodes)} episodes")
        
        # Save metadata
        metadata = {
            'total_segments': len(self.documents),
            'total_episodes': len(self.episodes),
            'episodes': list(self.episodes.keys())
        }
        
        with open(output_path / 'metadata.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        return self
    
    def load_index(self, index_dir: str):
        """Load pre-built index."""
        index_path = Path(index_dir)
        
        # Load all processed data
        processed_path = index_path.parent / 'processed'
        if not processed_path.exists():
            processed_path = Path('data/processed')
        
        self.build_index(str(processed_path), str(index_path))
        return self
    
    def search(self, query: str, k: int = 10) -> List[Dict]:
        """Search using simple text matching with scoring."""
        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        
        scored = []
        for doc in self.documents:
            # Calculate simple relevance score
            doc_words = doc['words']
            
            # Exact word matches
            exact_matches = len(query_words & doc_words)
            
            # Partial matches (query word in content)
            partial = sum(1 for w in query_words if w in doc['search_text'])
            
            # Phrase match
            phrase_bonus = 1 if query.lower() in doc['search_text'] else 0
            
            # Speaker match bonus
            speaker_bonus = 1 if query.lower() in doc['speaker'].lower() else 0
            
            score = exact_matches * 2 + partial * 0.5 + phrase_bonus * 3 + speaker_bonus
            
            if score > 0:
                scored.append((score, doc))
        
        # Sort by score
        scored.sort(key=lambda x: -x[0])
        
        results = []
        for i, (score, doc) in enumerate(scored[:k]):
            results.append({
                'rank': i + 1,
                'score': float(score),
                'episode_name': doc['episode_name'],
                'speaker': doc['speaker'],
                'timestamp': doc['timestamp'],
                'content': doc['content'],
                'preview': doc['content'][:300] + '...' if len(doc['content']) > 300 else doc['content']
            })
        
        return results
    
    def search_by_episode(self, episode_name: str, query: str = None, k: int = 10) -> List[Dict]:
        """Search within a specific episode."""
        if episode_name not in self.episodes:
            return []
        
        segments = self.episodes[episode_name]['segments']
        
        if not query:
            return segments[:k]
        
        # Simple text search
        query_lower = query.lower()
        matching = [s for s in segments if query_lower in s['content'].lower()]
        
        return matching[:k]
    
    def get_episode_list(self) -> List[str]:
        """Get list of all episodes."""
        return list(self.episodes.keys())
    
    def get_speaker_list(self) -> Dict[str, int]:
        """Get list of speakers with their appearance count."""
        speaker_counts = {}
        for doc in self.documents:
            speaker = doc['speaker']
            speaker_counts[speaker] = speaker_counts.get(speaker, 0) + 1
        return dict(sorted(speaker_counts.items(), key=lambda x: -x[1]))
    
    def get_episode_info(self, episode_name: str) -> Dict:
        """Get info about an episode."""
        if episode_name in self.episodes:
            return self.episodes[episode_name]
        return None
