#!/usr/bin/env python3
"""
Feedback and Learning System for EFFICODE-ACRR
"""

import json
import sqlite3
import time
from typing import Dict, List
from datetime import datetime

class FeedbackSystem:
    def __init__(self, db_path: str = "efficode_feedback.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize feedback database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                original_code TEXT NOT NULL,
                predicted_technique TEXT NOT NULL,
                confidence REAL NOT NULL,
                user_feedback TEXT NOT NULL,
                user_rating INTEGER,
                session_id TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def collect_feedback(self, optimization_result: Dict, user_feedback: Dict) -> str:
        """Collect user feedback"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feedback (
                timestamp, original_code, predicted_technique, confidence,
                user_feedback, user_rating, session_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            optimization_result.get('original_code', ''),
            optimization_result.get('ml_analysis', {}).get('predicted_technique', ''),
            optimization_result.get('ml_analysis', {}).get('confidence', 0.0),
            user_feedback.get('feedback_type', 'unknown'),
            user_feedback.get('rating', 0),
            user_feedback.get('session_id', '')
        ))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return str(feedback_id)
    
    def get_statistics(self) -> Dict:
        """Get feedback statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM feedback")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(user_rating) FROM feedback WHERE user_rating > 0")
        avg_rating = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT user_feedback, COUNT(*) FROM feedback GROUP BY user_feedback")
        feedback_types = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_feedback': total,
            'average_rating': round(avg_rating, 2),
            'feedback_types': feedback_types
        }

def test_feedback_system():
    """Test feedback system"""
    feedback_system = FeedbackSystem()
    
    # Test data
    optimization_result = {
        'original_code': 'def test(): pass',
        'ml_analysis': {
            'predicted_technique': 'hash_map',
            'confidence': 0.85
        }
    }
    
    user_feedback = {
        'feedback_type': 'accepted',
        'rating': 5,
        'session_id': 'test_session'
    }
    
    # Collect feedback
    feedback_id = feedback_system.collect_feedback(optimization_result, user_feedback)
    print(f"Feedback collected with ID: {feedback_id}")
    
    # Get statistics
    stats = feedback_system.get_statistics()
    print(f"Statistics: {stats}")

if __name__ == "__main__":
    test_feedback_system()