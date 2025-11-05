import sqlite3
import json
import hashlib
import datetime
from pathlib import Path


class CacheManager:
    def __init__(self, db_path="data/cache.sqlite"):
        """Ensure DB exists and create tables if missing."""
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = lambda cursor, row: row  # simple row factory
        self.create_tables()

    def create_tables(self):
        """Initialize cache tables for API and LLM results."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                response_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            );
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS llm_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                prompt_hash TEXT NOT NULL UNIQUE,
                response_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            );
        """)
        self.conn.commit()

    # -----------------------
    # APIキャッシュ関連
    # -----------------------
    def get_api_cache(self, query):
        now = datetime.datetime.now().isoformat()
        row = self.conn.execute(
            "SELECT response_json FROM cache WHERE query = ? AND (expires_at IS NULL OR expires_at > ?)",
            (query, now)
        ).fetchone()
        return json.loads(row[0]) if row else None

    def set_api_cache(self, query, response, ttl_hours=24):
        expires = (datetime.datetime.now() + datetime.timedelta(hours=ttl_hours)).isoformat()
        self.conn.execute(
            "INSERT INTO cache (query, response_json, expires_at) VALUES (?, ?, ?)",
            (query, json.dumps(response), expires)
        )
        self.conn.commit()

    # -----------------------
    # LLMキャッシュ関連
    # -----------------------
    def get_llm_cache(self, model_name, prompt_hash):
        now = datetime.datetime.now().isoformat()
        row = self.conn.execute(
            "SELECT response_text FROM llm_cache WHERE model_name = ? AND prompt_hash = ? AND (expires_at IS NULL OR expires_at > ?)",
            (model_name, prompt_hash, now)
        ).fetchone()
        return row[0] if row else None

    def set_llm_cache(self, model_name, prompt_hash, response_text, ttl_hours=24):
        expires = (datetime.datetime.now() + datetime.timedelta(hours=ttl_hours)).isoformat()
        try:
            # INSERT or fallback to UPDATE if unique constraint hit
            self.conn.execute(
                "INSERT INTO llm_cache (model_name, prompt_hash, response_text, expires_at) VALUES (?, ?, ?, ?)",
                (model_name, prompt_hash, response_text, expires)
            )
        except sqlite3.IntegrityError:
            self.conn.execute(
                "UPDATE llm_cache SET response_text = ?, expires_at = ? WHERE model_name = ? AND prompt_hash = ?",
                (response_text, expires, model_name, prompt_hash)
            )
        self.conn.commit()
