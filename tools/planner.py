"""Local-first calendar events and reminders for Jarvis."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
import threading
import time
import uuid

DB_PATH = Path(__file__).resolve().parents[1] / "jarvis_memory.db"
CALENDAR_DIR = Path.home() / "Documents" / "Jarvis Calendar"


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS planner_items (
            id TEXT PRIMARY KEY,
            kind TEXT NOT NULL,
            title TEXT NOT NULL,
            due_at TEXT NOT NULL,
            details TEXT NOT NULL DEFAULT '',
            completed INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    return conn


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.now().astimezone().tzinfo)
    return parsed.astimezone(timezone.utc)


def _format_ics_datetime(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def create_calendar_event(title: str, start_time: str, duration_minutes: int = 60, details: str = "") -> str:
    if not title.strip():
        return "❌ Calendar event ka title required hai."
    if duration_minutes < 1 or duration_minutes > 1440:
        return "❌ Duration 1 se 1440 minutes ke darmiyan honi chahiye."

    try:
        start = _parse_datetime(start_time)
    except ValueError:
        return "❌ Start time ISO format mein dein, example: 2026-10-01T15:00:00."

    event_id = uuid.uuid4().hex
    end = start + timedelta(minutes=duration_minutes)
    CALENDAR_DIR.mkdir(parents=True, exist_ok=True)
    ics_path = CALENDAR_DIR / f"{event_id}.ics"
    ics_content = "\r\n".join([
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Jarvis//Calendar//EN",
        "BEGIN:VEVENT",
        f"UID:{event_id}@jarvis",
        f"DTSTAMP:{_format_ics_datetime(datetime.now(timezone.utc))}",
        f"DTSTART:{_format_ics_datetime(start)}",
        f"DTEND:{_format_ics_datetime(end)}",
        f"SUMMARY:{title.replace(chr(10), ' ')}",
        f"DESCRIPTION:{details.replace(chr(10), ' ')}",
        "END:VEVENT",
        "END:VCALENDAR",
        "",
    ])
    ics_path.write_text(ics_content, encoding="utf-8")

    with _connect() as conn:
        conn.execute(
            "INSERT INTO planner_items (id, kind, title, due_at, details) VALUES (?, ?, ?, ?, ?)",
            (event_id, "event", title.strip(), start.isoformat(), details.strip()),
        )
    return f"✅ Calendar event '{title}' save ho gaya. File: {ics_path.name}"


def create_reminder(title: str, remind_at: str, details: str = "") -> str:
    if not title.strip():
        return "❌ Reminder ka title required hai."
    try:
        due = _parse_datetime(remind_at)
    except ValueError:
        return "❌ Reminder time ISO format mein dein, example: 2026-10-01T15:00:00."

    reminder_id = uuid.uuid4().hex
    with _connect() as conn:
        conn.execute(
            "INSERT INTO planner_items (id, kind, title, due_at, details) VALUES (?, ?, ?, ?, ?)",
            (reminder_id, "reminder", title.strip(), due.isoformat(), details.strip()),
        )
    return f"✅ Reminder set ho gaya: '{title}' at {due.astimezone().strftime('%Y-%m-%d %H:%M')}"


def list_planner_items(kind: str = "all") -> str:
    allowed_kinds = {"all", "event", "reminder"}
    if kind not in allowed_kinds:
        return "❌ Kind all, event, ya reminder hona chahiye."
    with _connect() as conn:
        if kind == "all":
            rows = conn.execute(
                "SELECT id, kind, title, due_at FROM planner_items WHERE completed = 0 ORDER BY due_at LIMIT 50"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, kind, title, due_at FROM planner_items WHERE completed = 0 AND kind = ? ORDER BY due_at LIMIT 50",
                (kind,),
            ).fetchall()
    if not rows:
        return "📅 Koi pending calendar item nahi hai."
    return "\n".join(f"- ID {item_id}: {item_kind}: {title} at {due_at}" for item_id, item_kind, title, due_at in rows)


def cancel_planner_item(item_id: str) -> str:
    with _connect() as conn:
        row = conn.execute("SELECT kind, title FROM planner_items WHERE id = ? AND completed = 0", (item_id.strip(),)).fetchone()
        if not row:
            return "❌ Calendar item nahi mila."
        conn.execute("UPDATE planner_items SET completed = 1 WHERE id = ?", (item_id.strip(),))
    return f"✅ {row[0].capitalize()} '{row[1]}' cancel kar diya."


def get_due_reminders(now: datetime | None = None) -> list[str]:
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, title FROM planner_items WHERE kind = 'reminder' AND completed = 0 AND due_at <= ? ORDER BY due_at",
            (current.isoformat(),),
        ).fetchall()
        conn.executemany("UPDATE planner_items SET completed = 1 WHERE id = ?", [(row[0],) for row in rows])
    return [row[1] for row in rows]


def start_reminder_scheduler(callback) -> threading.Thread:
    def run():
        while True:
            for title in get_due_reminders():
                try:
                    callback(f"🔔 Reminder: {title}")
                except Exception:
                    pass
            time.sleep(15)

    worker = threading.Thread(target=run, name="jarvis-reminders", daemon=True)
    worker.start()
    return worker
