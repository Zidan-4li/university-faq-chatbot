import sqlite3
import os
from datetime import datetime

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(_PROJECT_ROOT, "models", "chat_history.db")


def init_db():
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
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE chat_history SET feedback = ? WHERE id = ?", (feedback, row_id))
    conn.commit()
    conn.close()


def get_all_interactions():
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
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM chat_history")
    count = cursor.fetchone()[0]
    conn.close()
    return count
