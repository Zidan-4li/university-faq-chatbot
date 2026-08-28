"""
Database module for the University FAQ Chatbot.
Uses SQLite (a lightweight, file-based database built into Python)
to log every question asked and answer given, along with basic
metadata. This provides a persistent record of chatbot usage and
supports the evaluation/testing process.

Database Schema (see docs/database_erd.png for the visual ERD):

Table: chat_history
------------------------------------------------------
| Column       | Type      | Description              |
------------------------------------------------------
| id           | INTEGER   | Primary key (auto)       |
| question     | TEXT      | The user's question      |
| answer       | TEXT      | The generated answer     |
| sources      | TEXT      | Retrieved source chunks  |
|              |           | (joined as one string)   |
| timestamp    | TEXT      | When the interaction     |
|              |           | happened                 |
| feedback     | TEXT      | Optional user feedback   |
|              |           | ('helpful'/'not_helpful')|
------------------------------------------------------
"""

import sqlite3
import os
from datetime import datetime

_PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_PROJECT_ROOT)  # go up from src/ to project root
DB_PATH = os.path.join(_PROJECT_ROOT, "models", "chat_history.db")


def init_db():
    """Creates the chat_history table if it doesn't already exist.
    Safe to call every time the app starts."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            sources TEXT,
            timestamp TEXT NOT NULL,
            feedback TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_interaction(question, answer, sources):
    """Saves one question-answer interaction to the database.
    Returns the id of the newly inserted row (used later to attach
    feedback to this specific interaction)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    sources_text = "\n---\n".join(sources)
    timestamp = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO chat_history (question, answer, sources, timestamp, feedback)
        VALUES (?, ?, ?, ?, NULL)
    """, (question, answer, sources_text, timestamp))
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def update_feedback(row_id, feedback):
    """Updates the feedback field for a specific interaction.
    feedback should be 'helpful' or 'not_helpful'."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE chat_history SET feedback = ? WHERE id = ?
    """, (feedback, row_id))
    conn.commit()
    conn.close()


def get_all_interactions():
    """Retrieves all logged interactions, most recent first.
    Useful for reviewing chat history or exporting evaluation data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, question, answer, sources, timestamp, feedback
        FROM chat_history
        ORDER BY timestamp DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_interaction_count():
    """Returns the total number of logged interactions."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM chat_history")
    count = cursor.fetchone()[0]
    conn.close()
    return count
