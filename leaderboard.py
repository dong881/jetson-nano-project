"""
Leaderboard system for tracking top scores
"""
import json
import os
from datetime import datetime

LEADERBOARD_FILE = 'leaderboard.json'

class Leaderboard:
    """Manages the leaderboard for high scores"""
    
    def __init__(self, max_entries=10):
        self.max_entries = max_entries
        self.entries = []
        self.load()
    
    def load(self):
        """Load leaderboard from file"""
        if os.path.exists(LEADERBOARD_FILE):
            try:
                with open(LEADERBOARD_FILE, 'r') as f:
                    data = json.load(f)
                    self.entries = data.get('entries', [])
            except Exception as e:
                print(f"Error loading leaderboard: {e}")
                self.entries = []
        else:
            self.entries = []
    
    def save(self):
        """Save leaderboard to file"""
        try:
            with open(LEADERBOARD_FILE, 'w') as f:
                json.dump({'entries': self.entries}, f, indent=2)
        except Exception as e:
            print(f"Error saving leaderboard: {e}")
    
    def add_score(self, score, mode='human', difficulty='medium'):
        """Add a new score to the leaderboard"""
        if score <= 0:
            return False
        
        entry = {
            'score': score,
            'mode': mode,
            'difficulty': difficulty,
            'timestamp': datetime.now().isoformat()
        }
        
        self.entries.append(entry)
        self.entries.sort(key=lambda x: x['score'], reverse=True)
        self.entries = self.entries[:self.max_entries]
        self.save()
        return True
    
    def get_top_scores(self, n=10, mode=None, difficulty=None):
        """Get top N scores, optionally filtered by mode and difficulty"""
        filtered = self.entries
        
        if mode:
            filtered = [e for e in filtered if e.get('mode') == mode]
        
        if difficulty:
            filtered = [e for e in filtered if e.get('difficulty') == difficulty]
        
        return filtered[:n]
    
    def is_high_score(self, score, mode=None, difficulty=None):
        """Check if score qualifies for leaderboard"""
        top_scores = self.get_top_scores(self.max_entries, mode, difficulty)
        
        if len(top_scores) < self.max_entries:
            return True
        
        return score > top_scores[-1]['score']
    
    def get_rank(self, score, mode=None, difficulty=None):
        """Get rank for a given score"""
        top_scores = self.get_top_scores(self.max_entries, mode, difficulty)
        
        for i, entry in enumerate(top_scores):
            if score > entry['score']:
                return i + 1
        
        if len(top_scores) < self.max_entries:
            return len(top_scores) + 1
        
        return None  # Not in leaderboard
