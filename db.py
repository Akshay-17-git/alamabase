import sqlite3
import hashlib
import os

DB_PATH = "database.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    """Initialize the database with required tables."""
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS questionnaires (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            filename TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            questionnaire_id INTEGER,
            question_number INTEGER,
            question_text TEXT,
            generated_answer TEXT,
            edited_answer TEXT,
            citation TEXT,
            confidence_score REAL,
            evidence_snippet TEXT,
            FOREIGN KEY (questionnaire_id) REFERENCES questionnaires(id)
        );
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(email, password):
    """Create a new user account."""
    conn = get_conn()
    try:
        conn.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)",
                     (email, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(email, password):
    """Verify user credentials and return user_id if valid."""
    conn = get_conn()
    row = conn.execute("SELECT id FROM users WHERE email=? AND password_hash=?",
                       (email, hash_password(password))).fetchone()
    conn.close()
    return row[0] if row else None

def get_user_by_email(email):
    """Get user by email address."""
    conn = get_conn()
    row = conn.execute("SELECT id, email, created_at FROM users WHERE email=?", 
                       (email,)).fetchone()
    conn.close()
    return row

def save_questionnaire(user_id, filename):
    """Save questionnaire metadata and return questionnaire_id."""
    conn = get_conn()
    c = conn.execute("INSERT INTO questionnaires (user_id, filename) VALUES (?, ?)",
                     (user_id, filename))
    conn.commit()
    qid = c.lastrowid
    conn.close()
    return qid

def save_answers(questionnaire_id, answers):
    """Save or update answers for a questionnaire."""
    conn = get_conn()
    conn.execute("DELETE FROM answers WHERE questionnaire_id=?", (questionnaire_id,))
    for a in answers:
        conn.execute("""
            INSERT INTO answers 
            (questionnaire_id, question_number, question_text, generated_answer,
             edited_answer, citation, confidence_score, evidence_snippet)
            VALUES (?,?,?,?,?,?,?,?)
        """, (questionnaire_id, a["number"], a["question"], a["answer"],
              a["answer"], a["citation"], a["confidence"], a["snippet"]))
    conn.commit()
    conn.close()

def get_answers(questionnaire_id):
    """Get all answers for a questionnaire."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM answers WHERE questionnaire_id=? ORDER BY question_number",
        (questionnaire_id,)).fetchall()
    conn.close()
    return rows

def get_questionnaire_by_id(questionnaire_id):
    """Get questionnaire metadata by ID."""
    conn = get_conn()
    row = conn.execute(
        "SELECT id, user_id, filename, uploaded_at FROM questionnaires WHERE id=?",
        (questionnaire_id,)).fetchone()
    conn.close()
    return row

def get_user_questionnaires(user_id):
    """Get all questionnaires for a specific user."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, filename, uploaded_at FROM questionnaires WHERE user_id=? ORDER BY uploaded_at DESC",
        (user_id,)).fetchall()
    conn.close()
    return rows

def update_edited_answer(answer_id, edited_text):
    """Update the edited answer for a specific answer."""
    conn = get_conn()
    conn.execute("UPDATE answers SET edited_answer=? WHERE id=?", (edited_text, answer_id))
    conn.commit()
    conn.close()

def delete_questionnaire(questionnaire_id):
    """Delete a questionnaire and its answers."""
    conn = get_conn()
    conn.execute("DELETE FROM answers WHERE questionnaire_id=?", (questionnaire_id,))
    conn.execute("DELETE FROM questionnaires WHERE id=?", (questionnaire_id,))
    conn.commit()
    conn.close()
