import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

BACKEND_DIRECTORY = Path(__file__).resolve().parent
if str(BACKEND_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIRECTORY))

import database.scan_history as scan_history


class ScanHistoryDatabaseTests(unittest.TestCase):
    """验证 scan_history 表的创建、写入与倒序读取。"""

    def setUp(self):
        # 使用临时数据库文件，避免污染真实 scans.db。
        self.temp_dir = tempfile.TemporaryDirectory()
        temp_db = Path(self.temp_dir.name) / "scans.db"
        self._db_path_patch = patch.object(
            scan_history, "DATABASE_PATH", temp_db
        )
        self._db_path_patch.start()
        self.addCleanup(self._db_path_patch.stop)
        self.addCleanup(self.temp_dir.cleanup)

    def test_schema_creates_table_and_directory(self):
        connection = scan_history._connect()
        try:
            tables = connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='scan_history'"
            ).fetchall()
        finally:
            connection.close()
        self.assertEqual(len(tables), 1)
        self.assertTrue(scan_history.DATABASE_PATH.exists())

    def test_save_and_list_roundtrip(self):
        record_id = scan_history.save_scan_record(
            filename="vuln.php",
            language="php",
            scan_mode="single",
            rule_id="php-dangerous-unserialize",
            rule_count=1,
            finding_count=2,
            status="success",
        )
        self.assertIsInstance(record_id, int)
        self.assertGreater(record_id, 0)

        history = scan_history.list_scan_history()
        self.assertEqual(len(history), 1)
        record = history[0]
        self.assertEqual(record["filename"], "vuln.php")
        self.assertEqual(record["language"], "php")
        self.assertEqual(record["scan_mode"], "single")
        self.assertEqual(record["rule_id"], "php-dangerous-unserialize")
        self.assertEqual(record["rule_count"], 1)
        self.assertEqual(record["finding_count"], 2)
        self.assertEqual(record["status"], "success")
        self.assertTrue(record["created_at"])

    def test_zero_findings_record_is_saved(self):
        scan_history.save_scan_record(
            filename="clean.py",
            language="python",
            scan_mode="all",
            rule_id=None,
            rule_count=3,
            finding_count=0,
            status="success",
        )
        history = scan_history.list_scan_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["finding_count"], 0)
        self.assertIsNone(history[0]["rule_id"])

    def test_list_returns_newest_first(self):
        first = scan_history.save_scan_record(
            filename="a.php",
            language="php",
            scan_mode="all",
            rule_id=None,
            rule_count=1,
            finding_count=0,
            status="success",
        )
        second = scan_history.save_scan_record(
            filename="b.php",
            language="php",
            scan_mode="all",
            rule_id=None,
            rule_count=1,
            finding_count=0,
            status="success",
        )
        history = scan_history.list_scan_history()
        self.assertEqual([row["id"] for row in history], [second, first])


if __name__ == "__main__":
    unittest.main()
