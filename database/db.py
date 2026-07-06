
import json
import sqlite3
from typing import Any

from config import DATABASE_PATH


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                language TEXT DEFAULT 'uk',
                quiz_step TEXT DEFAULT '',
                quiz_data TEXT DEFAULT '{}',
                shown_ids TEXT DEFAULT '[]'
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS favorites (
                user_id INTEGER,
                item_id TEXT,
                item_data TEXT,
                PRIMARY KEY (user_id, item_id)
            )
            """
        )
        db.commit()


def get_user(user_id: int) -> dict[str, Any]:
    """Отримати дані користувача або створити нового."""
    with _connect() as db:
        row = db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()

        if row is None:
            db.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
            db.commit()
            return {
                "user_id": user_id,
                "language": "uk",
                "quiz_step": "",
                "quiz_data": {},
                "shown_ids": [],
            }

        return {
            "user_id": row["user_id"],
            "language": row["language"],
            "quiz_step": row["quiz_step"],
            "quiz_data": json.loads(row["quiz_data"]),
            "shown_ids": json.loads(row["shown_ids"]),
        }


def set_language(user_id: int, language: str) -> None:
    with _connect() as db:
        db.execute(
            "UPDATE users SET language = ? WHERE user_id = ?",
            (language, user_id),
        )
        db.commit()


def set_quiz_step(user_id: int, step: str) -> None:
    with _connect() as db:
        db.execute(
            "UPDATE users SET quiz_step = ? WHERE user_id = ?",
            (step, user_id),
        )
        db.commit()


def update_quiz_data(user_id: int, data: dict[str, Any]) -> None:
    with _connect() as db:
        db.execute(
            "UPDATE users SET quiz_data = ? WHERE user_id = ?",
            (json.dumps(data, ensure_ascii=False), user_id),
        )
        db.commit()


def add_shown_ids(user_id: int, ids: list) -> None:
    user = get_user(user_id)
    shown = user["shown_ids"] + ids
    with _connect() as db:
        db.execute(
            "UPDATE users SET shown_ids = ? WHERE user_id = ?",
            (json.dumps(shown), user_id),
        )
        db.commit()


def reset_quiz(user_id: int) -> None:
    with _connect() as db:
        db.execute(
            """
            UPDATE users
            SET quiz_step = '', quiz_data = '{}', shown_ids = '[]'
            WHERE user_id = ?
            """,
            (user_id,),
        )
        db.commit()
def add_favorite(user_id: int, item: dict) -> None:
    with _connect() as db:
        db.execute(
            "INSERT OR REPLACE INTO favorites (user_id, item_id, item_data) VALUES (?, ?, ?)",
            (user_id, str(item["id"]), json.dumps(item, ensure_ascii=False)),
        )
        db.commit()


def get_favorites(user_id: int) -> list[dict]:
    with _connect() as db:
        rows = db.execute(
            "SELECT item_data FROM favorites WHERE user_id = ?", (user_id,)
        ).fetchall()
        return [json.loads(r["item_data"]) for r in rows]


def remove_favorite(user_id: int, item_id: str) -> None:
    with _connect() as db:
        db.execute(
            "DELETE FROM favorites WHERE user_id = ? AND item_id = ?",
            (user_id, item_id),
        )
        db.commit()