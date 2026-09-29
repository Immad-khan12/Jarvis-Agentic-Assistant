from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().parents[1] / "jarvis_memory.db"


def init_db():
	with sqlite3.connect(DB_PATH) as conn:
		conn.execute(
			"""
			CREATE TABLE IF NOT EXISTS memories (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				user_id TEXT NOT NULL,
				key TEXT NOT NULL,
				value TEXT NOT NULL
			)
			"""
		)


def save_memory(user_id: str, key: str, value: str):
	with sqlite3.connect(DB_PATH) as conn:
		conn.execute(
			"INSERT INTO memories (user_id, key, value) VALUES (?, ?, ?)",
			(user_id, key, value),
		)


def get_memories(user_id: str) -> str:
	with sqlite3.connect(DB_PATH) as conn:
		rows = conn.execute(
			"SELECT key, value FROM memories WHERE user_id = ?",
			(user_id,),
		).fetchall()

	if not rows:
		return "No past memories recorded yet."
	return "\n".join(f"- {key}: {value}" for key, value in rows)


init_db()
