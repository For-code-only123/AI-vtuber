import sqlite3
import yaml
from datetime import datetime

def get_db_path():
    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config["sqlite"]["path"]

def init_db():
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        display_name TEXT,
        nickname TEXT,
        first_seen DATETIME,
        last_seen DATETIME,
        affinity_score REAL DEFAULT 0,
        notes TEXT
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS user_facts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        fact TEXT,
        category TEXT,
        confidence REAL,
        importance REAL,
        source TEXT,
        created_at DATETIME,
        updated_at DATETIME,
        is_active INTEGER DEFAULT 1
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS episodes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stream_id TEXT,
        summary TEXT,
        participants TEXT,
        importance REAL,
        created_at DATETIME
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS safety_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        content TEXT,
        reason TEXT,
        created_at DATETIME
    )""")

    conn.commit()
    conn.close()
    print("数据库初始化完成")

def upsert_user(user_id: str, display_name: str):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    now = datetime.now().isoformat()

    c.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if c.fetchone():
        c.execute("UPDATE users SET last_seen=?, display_name=? WHERE user_id=?",
                  (now, display_name, user_id))
    else:
        c.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?)",
                  (user_id, display_name, None, now, now, 0.0, None))

    conn.commit()
    conn.close()

def add_user_fact(user_id: str, fact: str, category: str,
                  confidence: float = 0.8, importance: float = 0.5, source: str = "danmu"):
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    now = datetime.now().isoformat()

    c.execute("""
    INSERT INTO user_facts (user_id, fact, category, confidence, importance, source, created_at, updated_at)
    VALUES (?,?,?,?,?,?,?,?)
    """, (user_id, fact, category, confidence, importance, source, now, now))

    conn.commit()
    conn.close()

def get_user_facts(user_id: str, limit: int = 5) -> list:
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()

    c.execute("""
    SELECT fact, category FROM user_facts
    WHERE user_id=? AND is_active=1
    ORDER BY importance DESC, updated_at DESC
    LIMIT ?
    """, (user_id, limit))

    rows = c.fetchall()
    conn.close()
    return rows

def get_user_profile(user_id: str) -> dict:
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return {}
    return {
        "user_id": row[0],
        "display_name": row[1],
        "nickname": row[2],
        "first_seen": row[3],
        "last_seen": row[4],
        "affinity_score": row[5],
    }

if __name__ == "__main__":
    init_db()