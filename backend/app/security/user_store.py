import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from app.security.passwords import hash_password, verify_password


@dataclass(frozen=True)
class StoredUser:
    user_id: str
    username: str
    password_hash: str
    is_active: bool


def _get_db_path() -> Path:
    configured_path = os.getenv(
        "CHAT_AUTH_DB_PATH",
        "data/chat_auth.db",
    )

    db_path = Path(configured_path)

    if not db_path.is_absolute():
        backend_root = Path(__file__).resolve().parents[2]
        db_path = backend_root / db_path

    db_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    return db_path


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(
        _get_db_path()
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


def initialize_user_store() -> None:
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS user_companies (
                user_id TEXT NOT NULL,
                company_name TEXT NOT NULL,

                PRIMARY KEY (
                    user_id,
                    company_name
                ),

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
            """
        )


def create_user(
    *,
    user_id: str,
    username: str,
    password: str,
    companies: list[str],
) -> None:
    clean_user_id = user_id.strip()
    clean_username = username.strip()

    if not clean_user_id:
        raise ValueError("user_id is required")

    if not clean_username:
        raise ValueError("username is required")

    if len(password) < 8:
        raise ValueError(
            "password must be at least 8 characters"
        )

    clean_companies = sorted(
        {
            company.strip()
            for company in companies
            if company.strip()
        }
    )

    if not clean_companies:
        raise ValueError(
            "at least one company is required"
        )

    password_hash = hash_password(password)

    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO users (
                user_id,
                username,
                password_hash,
                is_active
            )
            VALUES (?, ?, ?, 1)
            """,
            (
                clean_user_id,
                clean_username,
                password_hash,
            ),
        )

        connection.executemany(
            """
            INSERT INTO user_companies (
                user_id,
                company_name
            )
            VALUES (?, ?)
            """,
            [
                (
                    clean_user_id,
                    company_name,
                )
                for company_name
                in clean_companies
            ],
        )


def get_user_by_username(
    username: str,
) -> StoredUser | None:
    clean_username = username.strip()

    if not clean_username:
        return None

    with _connect() as connection:
        row = connection.execute(
            """
            SELECT
                user_id,
                username,
                password_hash,
                is_active
            FROM users
            WHERE username = ?
            """,
            (clean_username,),
        ).fetchone()

    if row is None:
        return None

    return StoredUser(
        user_id=row["user_id"],
        username=row["username"],
        password_hash=row["password_hash"],
        is_active=bool(row["is_active"]),
    )


def get_user_companies(
    user_id: str,
) -> tuple[str, ...]:
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT company_name
            FROM user_companies
            WHERE user_id = ?
            ORDER BY company_name
            """,
            (user_id,),
        ).fetchall()

    return tuple(
        row["company_name"]
        for row in rows
    )


def authenticate_user(
    username: str,
    password: str,
) -> tuple[StoredUser, tuple[str, ...]] | None:
    user = get_user_by_username(username)

    if user is None:
        return None

    if not user.is_active:
        return None

    if not verify_password(
        password,
        user.password_hash,
    ):
        return None

    companies = get_user_companies(
        user.user_id
    )

    return user, companies