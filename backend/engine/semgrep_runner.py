import subprocess
import json
import os


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

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8"
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

        vulnerabilities.append({

            # 规则名称
            "rule": item["check_id"],

            # 文件名
            "file": os.path.basename(item["path"]),

            # 漏洞代码行
            "line": item["start"]["line"],

            # 漏洞信息
            "message": item.get("extra", {}).get("message", "")
        })


    return {
        "vulnerabilities": vulnerabilities
    }



# 给 patch_verify.py 使用
def run_semgrep(code_path, rule_path):

    return scan(
        code_path,
        rule_path
    )