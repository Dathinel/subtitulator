import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

from app.config import settings


def _database_path() -> str:
    url = settings.DATABASE_URL
    if url.startswith("sqlite+aiosqlite:///"):
        raw_path = url.replace("sqlite+aiosqlite:///", "", 1)
        return unquote(raw_path)
    if url.startswith("sqlite:///"):
        raw_path = url.replace("sqlite:///", "", 1)
        return unquote(raw_path)
    return os.path.join(settings.DATA_DIR, "subtitulator.db")


DATABASE_PATH = _database_path()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def get_connection():
    Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                original_filename TEXT NOT NULL,
                input_path TEXT NOT NULL,
                output_path TEXT,
                transcript_path TEXT,
                subtitles_path TEXT,
                language TEXT,
                model TEXT NOT NULL,
                status TEXT NOT NULL,
                progress INTEGER NOT NULL DEFAULT 0,
                error_message TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
