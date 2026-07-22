import subprocess
import json
import os


def scan(code_path, rule_path):

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


    for item in data["results"]:

        vulnerabilities.append({
            "rule": item["check_id"],
            "file": os.path.basename(item["path"]),
            "line": item["start"]["line"]
        })


    return {
        "vulnerabilities": vulnerabilities
    }



# 给 Patch Verification 使用
def run_semgrep(code_path, rule_path):

    return scan(
        code_path,
        rule_path
    )