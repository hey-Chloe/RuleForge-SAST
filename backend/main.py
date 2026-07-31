import sys
import json
import os

from engine.semgrep_runner import scan


def main():

    print("====================")
    print(" RuleForge-SAST ")
    print("====================")


    if len(sys.argv) < 3:
        print(
            "使用方法:\n"
            "python main.py scan <目录>"
        )
        return


    command = sys.argv[1]
    target = sys.argv[2]


    if command == "scan":

        print("\n开始扫描...\n")


        result = scan(
            target,
            "../rules/php-unserialize.yaml"
        )


        # 生成 JSON 报告
        os.makedirs(
            "../reports",
            exist_ok=True
        )


        with open(
            "../reports/result.json",
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                result,
                f,
                indent=4,
                ensure_ascii=False
            )


        print("发现漏洞:")


        for item in result["vulnerabilities"]:

            print("----------------")

            print(
                "规则:",
                item["rule"]
            )

            print(
                "文件:",
                item["file"]
            )

            print(
                "行号:",
                item["line"]
            )


        print("\n报告已生成:")
        print("../reports/result.json")


if __name__ == "__main__":
    main()