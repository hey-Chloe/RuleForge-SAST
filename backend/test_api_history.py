import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

BACKEND_DIRECTORY = Path(__file__).resolve().parent
if str(BACKEND_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIRECTORY))

import database.scan_history as scan_history
from api import app


class ScanHistoryApiTests(unittest.TestCase):
    """验证 /scan 保存历史记录以及 GET /history 返回真实数据。"""

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

        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()

    @patch("api.scan", return_value={"vulnerabilities": []})
    def test_scan_saves_history_record_with_zero_findings(self, scan):
        response = self.client.post(
            "/scan",
            data={"scan_mode": "all"},
            files={"file": ("clean.php", b"<?php echo 'ok';", "application/x-php")},
        )
        self.assertEqual(response.status_code, 200)

        history = scan_history.list_scan_history()
        self.assertEqual(len(history), 1)
        record = history[0]
        self.assertEqual(record["filename"], "clean.php")
        self.assertEqual(record["language"], "php")
        self.assertEqual(record["scan_mode"], "all")
        self.assertGreater(record["rule_count"], 0)
        self.assertEqual(record["finding_count"], 0)
        self.assertEqual(record["status"], "success")
        self.assertIsNone(record["rule_id"])


    @patch(
        "api.scan",
        return_value={
            "vulnerabilities": [
                {
                    "id": "php-dangerous-eval",
                    "rule": "php-dangerous-eval",
                    "file": "temp.php",
                    "line": 1,
                    "category": "code-execution",
                    "severity": "CRITICAL",
                    "cwe": "CWE-95",
                    "description": "不安全的 PHP eval 代码执行",
                    "fix": ["避免执行用户可控代码"],
                    "message": "Dangerous PHP eval usage",
                }
            ]
        },
    )
    def test_single_mode_saves_rule_id_and_finding_count(self, scan):
        response = self.client.post(
            "/scan",
            data={"rule_id": "php-dangerous-eval", "scan_mode": "single"},
            files={"file": ("vuln.php", b"<?php eval($x);", "application/x-php")},
        )
        self.assertEqual(response.status_code, 200)

        history = scan_history.list_scan_history()
        self.assertEqual(len(history), 1)
        record = history[0]
        self.assertEqual(record["filename"], "vuln.php")
        self.assertEqual(record["scan_mode"], "single")
        self.assertEqual(record["rule_id"], "php-dangerous-eval")
        self.assertEqual(record["finding_count"], 1)

    @patch("api.scan")
    def test_failed_scan_does_not_save_history(self, scan):
        scan.side_effect = Exception("boom")
        response = self.client.post(
            "/scan",
            data={"scan_mode": "all"},
            files={"file": ("bad.php", b"<?php", "application/x-php")},
        )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(scan_history.list_scan_history(), [])

    @patch("api.scan", return_value={"vulnerabilities": []})
    def test_history_endpoint_returns_records_newest_first(self, scan):
        self.client.post(
            "/scan",
            data={"scan_mode": "all"},
            files={"file": ("first.php", b"<?php", "application/x-php")},
        )
        self.client.post(
            "/scan",
            data={"scan_mode": "all"},
            files={"file": ("second.php", b"<?php", "application/x-php")},
        )

        response = self.client.get("/history")
        self.assertEqual(response.status_code, 200)
        history = response.json()["history"]
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["filename"], "second.php")
        self.assertEqual(history[1]["filename"], "first.php")

    def test_history_endpoint_empty(self):
        response = self.client.get("/history")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["history"], [])


if __name__ == "__main__":
    unittest.main()
