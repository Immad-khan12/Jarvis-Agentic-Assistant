import sqlite3

DB_PATH = "jarvis_memory.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            key TEXT,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_memory(user_id: str, key: str, value: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO memories (user_id, key, value) VALUES (?, ?, ?)", (user_id, key, value))
    conn.commit()
    conn.close()

def get_memories(user_id: str) -> str:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM memories WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return "No past memories recorded yet."
    return "\n".join([f"- {row[0]}: {row[1]}" for row in rows])

init_db()