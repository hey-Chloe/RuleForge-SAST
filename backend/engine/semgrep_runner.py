import subprocess
import json
import os

try:
    from backend.models.vulnerability import Vulnerability
    from backend.rules.metadata_parser import parse_metadata
except ModuleNotFoundError:
    # Support the existing entry points that run with backend as the import root.
    from models.vulnerability import Vulnerability
    from rules.metadata_parser import parse_metadata


def scan(code_path, rule_path):
    """
    调用 Semgrep 扫描代码

    :param code_path: 待扫描代码路径
    :param rule_path: Semgrep规则路径
    :return: 漏洞结果JSON
    """

    command = [
        "semgrep",
        "scan",
        "--config",
        rule_path,
        code_path,
        "--json"
    ]

    environment = os.environ.copy()
    environment.setdefault("PYTHONUTF8", "1")

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=environment
    )


    if result.returncode != 0:

        print("STDOUT:")
        print(result.stdout)

        print("STDERR:")
        print(result.stderr)

        raise Exception("Semgrep scan failed")


    data = json.loads(result.stdout)


    vulnerabilities = []


    for item in data.get("results", []):

        metadata = parse_metadata(item)
        rule_id = item.get("check_id") or metadata["rule_id"]
        extra = item.get("extra", {})
        if not isinstance(extra, dict):
            extra = {}

        vulnerabilities.append(Vulnerability(

            # 规则名称
            id=rule_id,

            rule=rule_id,

            # 文件名
            file=os.path.basename(item["path"]),

            # 漏洞代码行
            line=item["start"]["line"],

            category=metadata["category"],

            severity=metadata["severity"],

            cwe=metadata["cwe"],

            description=metadata["description"],

            fix=metadata["fix"],

            # 漏洞信息
            message=extra.get("message", "")
        ))


    return {
        "vulnerabilities": vulnerabilities
    }



# 给 patch_verify.py 使用
def run_semgrep(code_path, rule_path):

    return scan(
        code_path,
        rule_path
    )
