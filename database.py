"""
database.py – SQLite persistence for investigations and EDD scores
"""
import sqlite3
from config import DB_PATH

def init_db():
    """Initializes the database schema."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS investigations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT UNIQUE,
            ground_truth_label TEXT,
            agent_decision TEXT,
            agent_reasoning TEXT,
            hallucination_score REAL,
            compliance_score REAL,
            calibration_score REAL,
            final_edd_score REAL
        )
    ''')
    conn.commit()
    conn.close()

def save_investigation(data: dict):
    """Upserts an investigation record into the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO investigations
        (transaction_id, ground_truth_label, agent_decision, agent_reasoning,
         hallucination_score, compliance_score, calibration_score, final_edd_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['transaction_id'], data['ground_truth_label'],
        data['agent_decision'], data['agent_reasoning'],
        data['hallucination_score'], data['compliance_score'],
        data['calibration_score'], data['final_edd_score']
    ))
    conn.commit()
    conn.close()