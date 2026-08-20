import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

import numpy as np

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "inbox.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL CHECK (source_type IN ('note', 'url')),
    raw_content TEXT NOT NULL,
    source_url TEXT,
    title TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding BLOB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_chunks_item_id ON chunks(item_id);
"""


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA)


def insert_item(source_type: str, raw_content: str, source_url: str | None, title: str | None) -> int:
    created_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO items (source_type, raw_content, source_url, title, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (source_type, raw_content, source_url, title, created_at),
        )
        return cur.lastrowid


def insert_chunks(item_id: int, chunks: list[str], embeddings: list[list[float]]) -> None:
    with get_connection() as conn:
        conn.executemany(
            "INSERT INTO chunks (item_id, chunk_index, chunk_text, embedding) VALUES (?, ?, ?, ?)",
            [
                (item_id, idx, text, np.asarray(vec, dtype=np.float32).tobytes())
                for idx, (text, vec) in enumerate(zip(chunks, embeddings))
            ],
        )


def list_items() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, source_type, title, source_url, created_at FROM items ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def get_all_chunks_with_items() -> list[dict]:
    """Every chunk joined with its parent item's citation fields, for brute-force retrieval."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT c.id, c.item_id, c.chunk_text, c.embedding,
                   i.title, i.source_type
            FROM chunks c
            JOIN items i ON i.id = c.item_id
            """
        ).fetchall()
        return [
            {
                "id": row["id"],
                "item_id": row["item_id"],
                "chunk_text": row["chunk_text"],
                "embedding": np.frombuffer(row["embedding"], dtype=np.float32),
                "title": row["title"],
                "source_type": row["source_type"],
            }
            for row in rows
        ]
