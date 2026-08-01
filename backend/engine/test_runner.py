import sys
from pathlib import Path


SCRIPT_FILE = Path(__file__).resolve()
PROJECT_ROOT = SCRIPT_FILE.parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.engine.semgrep_runner import scan


TARGET_PATH = PROJECT_ROOT / "testcase" / "test.php"
RULE_PATH = PROJECT_ROOT / "rules" / "php-unserialize.yaml"


result = scan(
    str(TARGET_PATH),
    str(RULE_PATH)
)

print(result)
