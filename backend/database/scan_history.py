"""扫描历史持久化模块。

使用 Python 标准库 sqlite3，不引入额外依赖。
数据库文件位于 backend/database/scans.db，启动时自动创建目录与数据表。
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DATABASE_DIRECTORY = Path(__file__).resolve().parent
DATABASE_PATH = DATABASE_DIRECTORY / "scans.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS scan_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    language TEXT NOT NULL,
    scan_mode TEXT NOT NULL,
    rule_id TEXT,
    rule_count INTEGER NOT NULL,
    finding_count INTEGER NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def _connect() -> sqlite3.Connection:
    """打开数据库连接，确保目录与数据表存在。"""
    DATABASE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(DATABASE_PATH))
    connection.row_factory = sqlite3.Row
    connection.execute(SCHEMA)
    connection.commit()
    return connection


def save_scan_record(
    *,
    filename: str,
    language: str,
    scan_mode: str,
    rule_id: str | None,
    rule_count: int,
    finding_count: int,
    status: str,
) -> int:
    """保存一条扫描历史记录，返回新记录的自增 id。"""
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    connection = _connect()
    try:
        cursor = connection.execute(
            """
            INSERT INTO scan_history (
                filename, language, scan_mode, rule_id, rule_count,
                finding_count, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                filename,
                language,
                scan_mode,
                rule_id,
                rule_count,
                finding_count,
                status,
                created_at,
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)
    finally:
        connection.close()


def list_scan_history() -> list[dict]:
    """按时间倒序返回全部扫描历史记录。"""
    connection = _connect()
    try:
        rows = connection.execute(
            """
            SELECT id, filename, language, scan_mode, rule_id, rule_count,
                   finding_count, status, created_at
            FROM scan_history
            ORDER BY id DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()
