import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Resume table to store results
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            job_role TEXT,
            match_score REAL NOT NULL,
            skills_found TEXT,
            missing_skills TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Users table for recruiters
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'recruiter'
        )
    ''')
    
    # Insert a default recruiter for testing
    try:
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", ('admin@example.com', 'password123'))
    except sqlite3.IntegrityError:
        pass # Already exists
        
    conn.commit()
    conn.close()

def insert_candidate(name, match_score, skills_found, missing_skills, job_role="N/A"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if job_role column exists (for fallback)
    cursor.execute("PRAGMA table_info(candidates)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'job_role' not in columns:
        cursor.execute("ALTER TABLE candidates ADD COLUMN job_role TEXT")
    
    cursor.execute('''
        INSERT INTO candidates (name, match_score, skills_found, missing_skills, job_role)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, match_score, skills_found, missing_skills, job_role))
    conn.commit()
    conn.close()

def get_all_candidates():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Explicitly select columns to ensure the template indices match
    cursor.execute("SELECT id, name, job_role, match_score, skills_found, missing_skills, timestamp FROM candidates ORDER BY timestamp DESC")
    candidates = cursor.fetchall()
    conn.close()
    return candidates

def verify_user(email, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
    user = cursor.fetchone()
    conn.close()
    return user

def register_user(email, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        conn.close()
        return True
    except:
        return False

init_db()
