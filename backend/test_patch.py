import sys
from pathlib import Path


SCRIPT_FILE = Path(__file__).resolve()
BACKEND_DIR = SCRIPT_FILE.parent
PROJECT_ROOT = BACKEND_DIR.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from analyzer.patch_verify import verify_patch


REPO_PATH = BACKEND_DIR / "target_repo"
TARGET_PATH = REPO_PATH / "testcase"
RULE_PATH = PROJECT_ROOT / "rules" / "php-unserialize.yaml"


result = verify_patch(

    str(REPO_PATH),

    "5c2ef4e",

    "f565423",

    str(TARGET_PATH),

    str(RULE_PATH)

)


print(result)
