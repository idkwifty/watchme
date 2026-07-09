
import json

from typing import Any

import psycopg2
import psycopg2.extras

from config import DATABASE_URL


def _connect():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    return conn


def init_db() -> None:
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    language TEXT DEFAULT 'uk',
                    quiz_step TEXT DEFAULT '',
                    quiz_data TEXT DEFAULT '{}',
                    shown_ids TEXT DEFAULT '[]'
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS favorites (
                    user_id BIGINT,
                    item_id TEXT,
                    item_data TEXT,
                    PRIMARY KEY (user_id, item_id)
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS watched (
                    user_id BIGINT,
                    item_id TEXT,
                    item_data TEXT DEFAULT '{}',
                    PRIMARY KEY (user_id, item_id)
                )
                """
            )
            cur.execute(
                "ALTER TABLE watched ADD COLUMN IF NOT EXISTS item_data TEXT DEFAULT '{}'"
            )
            conn.commit()


def get_user(user_id: int) -> dict[str, Any]:
    """Отримати дані користувача або створити нового."""
    with _connect() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            row = cur.fetchone()

            if row is None:
                cur.execute("INSERT INTO users (user_id) VALUES (%s)", (user_id,))
                conn.commit()
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
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET language = %s WHERE user_id = %s",
                (language, user_id),
            )
        conn.commit()


def set_quiz_step(user_id: int, step: str) -> None:
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET quiz_step = %s WHERE user_id = %s",
                (step, user_id),
            )
        conn.commit()


def update_quiz_data(user_id: int, data: dict[str, Any]) -> None:
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET quiz_data = %s WHERE user_id = %s",
                (json.dumps(data, ensure_ascii=False), user_id),
            )
        conn.commit()


def add_shown_ids(user_id: int, ids: list) -> None:
    user = get_user(user_id)
    shown = user["shown_ids"] + ids
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET shown_ids = %s WHERE user_id = %s",
                (json.dumps(shown), user_id),
            )
        conn.commit()


def reset_quiz(user_id: int) -> None:
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE users
                SET quiz_step = '', quiz_data = '{}', shown_ids = '[]'
                WHERE user_id = %s
                """,
                (user_id,),
            )
        conn.commit()


def add_favorite(user_id: int, item: dict) -> None:
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO favorites (user_id, item_id, item_data)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, item_id) DO UPDATE
                SET item_data = EXCLUDED.item_data
                """,
                (user_id, str(item["id"]), json.dumps(item, ensure_ascii=False)),
            )
        conn.commit()


def get_favorites(user_id: int) -> list[dict]:
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT item_data FROM favorites WHERE user_id = %s", (user_id,)
            )
            rows = cur.fetchall()
            return [json.loads(r[0]) for r in rows]


def remove_favorite(user_id: int, item_id: str) -> None:
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM favorites WHERE user_id = %s AND item_id = %s",
                (user_id, item_id),
            )
        conn.commit()
        
def add_watched(user_id: int, item: dict) -> None:
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO watched (user_id, item_id, item_data)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, item_id) DO NOTHING
                """,
                (user_id, str(item["id"]), json.dumps(item, ensure_ascii=False)),
            )
        conn.commit()


def get_watched_ids(user_id: int) -> list[str]:
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT item_id FROM watched WHERE user_id = %s", (user_id,))
            rows = cur.fetchall()
            return [r[0] for r in rows]


def get_watched(user_id: int) -> list[dict]:
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT item_data FROM watched WHERE user_id = %s", (user_id,))
            rows = cur.fetchall()
            return [json.loads(r[0]) for r in rows]