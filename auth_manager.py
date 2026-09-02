import sqlite3
import hashlib

DB_FILE = "student_portal.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT,
                    full_name TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    topic TEXT,
                    score REAL,
                    weak_areas TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
    conn.commit()
    conn.close()

def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, full_name):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?)", (username, hash_pw(password), full_name))
        conn.commit()
        return True, "Account successfully ban gaya! Ab login karein."
    except sqlite3.IntegrityError:
        return False, "Yeh username pehle se exist karta hai."
    finally:
        conn.close()

def login_user(username, password):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT full_name FROM users WHERE username = ? AND password_hash = ?", (username, hash_pw(password)))
    user = c.fetchone()
    conn.close()
    return user[0] if user else None

def save_learning_record(username, topic, score, weak_areas):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO history (username, topic, score, weak_areas) VALUES (?, ?, ?, ?)",
              (username, topic, score, str(weak_areas)))
    conn.commit()
    conn.close()
def get_user_history(username):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT topic, score, weak_areas, timestamp FROM history WHERE username = ? ORDER BY timestamp DESC", (username,))
    rows = c.fetchall()
    conn.close()
    return rows    