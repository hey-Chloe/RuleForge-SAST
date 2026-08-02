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
    :param rule_path: Semgrep规则路径，可以是单个路径字符串或路径列表
    :return: 漏洞结果JSON
    """

    # 支持单个规则路径或规则路径列表，一次 Semgrep 命令加载全部规则。
    rule_paths = [rule_path] if isinstance(rule_path, (str, os.PathLike)) else list(rule_path)

    command = ["semgrep", "scan"]
    for path in rule_paths:
        command.extend(["--config", str(path)])
    command.extend([code_path, "--json"])


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

        # 优先读取 extra.lines（Semgrep 命中的代码片段），
        # 缺失时回退到 extra.fixed_lines；两者都不存在时返回空字符串。
        # 注意：不使用 extra.message，因为 message 是漏洞描述而非源代码。
        code_snippet = ""
        lines = extra.get("lines")
        if isinstance(lines, str) and lines.strip():
            code_snippet = lines.strip()
        elif isinstance(lines, list):
            code_snippet = "\n".join(
                str(line) for line in lines if isinstance(line, str) and line.strip()
            ).strip()
        if not code_snippet:
            fixed_lines = extra.get("fixed_lines")
            if isinstance(fixed_lines, str) and fixed_lines.strip():
                code_snippet = fixed_lines.strip()


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
            message=extra.get("message", ""),

            # 命中的代码片段
            code_snippet=code_snippet,
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
