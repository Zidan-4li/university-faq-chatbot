"""
Simple script to view everything logged in the chat_history database.
Run with: python view_history.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from database import get_all_interactions, get_interaction_count

count = get_interaction_count()
print(f"Total interactions logged: {count}\n")
print("=" * 70)

for row in get_all_interactions():
    row_id, question, answer, sources, timestamp, feedback = row
    print(f"\n[#{row_id}] {timestamp}")
    print(f"Q: {question}")
    print(f"A: {answer}")
    print(f"Feedback: {feedback if feedback else '(none given)'}")
    print("-" * 70)
