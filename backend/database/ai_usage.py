"""AI 建议用量与缓存持久化模块。

复用 backend/database/scans.db，使用 Python 标准库 sqlite3。
新增 ai_usage 与 ai_suggestion_cache 两张表，启动时自动创建。
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DATABASE_DIRECTORY = Path(__file__).resolve().parent
DATABASE_PATH = DATABASE_DIRECTORY / "scans.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS ai_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id TEXT NOT NULL,
    request_hash TEXT NOT NULL,
    model TEXT NOT NULL,
    prompt_tokens INTEGER NOT NULL DEFAULT 0,
    completion_tokens INTEGER NOT NULL DEFAULT 0,
    cost_usd REAL NOT NULL DEFAULT 0,
    cached INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ai_suggestion_cache (
    request_hash TEXT PRIMARY KEY,
    model TEXT NOT NULL,
    response_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def _connect() -> sqlite3.Connection:
    """打开数据库连接，确保目录与数据表存在。"""
    DATABASE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(DATABASE_PATH))
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    connection.commit()
    return connection



def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_cached_suggestion(request_hash: str) -> dict | None:
    """按 request_hash 返回缓存建议；不存在时返回 None。"""
    connection = _connect()
    try:
        row = connection.execute(
            """
            SELECT request_hash, model, response_json, created_at
            FROM ai_suggestion_cache
            WHERE request_hash = ?
            """,
            (request_hash,),
        ).fetchone()
        return dict(row) if row is not None else None
    finally:
        connection.close()


def save_cached_suggestion(request_hash: str, model: str, response_json: str) -> None:
    """保存一条 AI 建议缓存。"""
    connection = _connect()
    try:
        connection.execute(
            """
            INSERT OR REPLACE INTO ai_suggestion_cache (
                request_hash, model, response_json, created_at
            ) VALUES (?, ?, ?, ?)
            """,
            (request_hash, model, response_json, _now()),
        )
        connection.commit()
    finally:
        connection.close()


def record_usage(
    *,
    client_id: str,
    request_hash: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    cost_usd: float,
    cached: bool,
    status: str,
) -> int:
    """记录一次 AI 调用用量，返回新记录 id。"""
    connection = _connect()
    try:
        cursor = connection.execute(
            """
            INSERT INTO ai_usage (
                client_id, request_hash, model, prompt_tokens,
                completion_tokens, cost_usd, cached, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                client_id,
                request_hash,
                model,
                prompt_tokens,
                completion_tokens,
                cost_usd,
                1 if cached else 0,
                status,
                _now(),
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)
    finally:
        connection.close()


def count_non_cached_today(client_id: str) -> int:
    """统计某 client_id 当天非缓存调用次数。"""
    today = datetime.now().strftime("%Y-%m-%d")
    connection = _connect()
    try:
        row = connection.execute(
            """
            SELECT COUNT(*) AS cnt
            FROM ai_usage
            WHERE client_id = ? AND cached = 0 AND created_at LIKE ?
            """,
            (client_id, f"{today}%"),
        ).fetchone()
        return int(row["cnt"]) if row is not None else 0
    finally:
        connection.close()


def sum_cost_today(client_id: str) -> float:
    """统计某 client_id 当天累计花费（美元）。"""
    today = datetime.now().strftime("%Y-%m-%d")
    connection = _connect()
    try:
        row = connection.execute(
            """
            SELECT COALESCE(SUM(cost_usd), 0) AS total
            FROM ai_usage
            WHERE client_id = ? AND created_at LIKE ?
            """,
            (client_id, f"{today}%"),
        ).fetchone()
        return float(row["total"]) if row is not None else 0.0
    finally:
        connection.close()
