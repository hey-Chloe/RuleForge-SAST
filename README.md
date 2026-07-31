# RuleForge-SAST

## 基于 Semgrep 的轻量级静态应用安全测试平台（SAST）

RuleForge-SAST 是一个面向代码安全审计场景的静态分析工具。

通过 Semgrep 规则引擎实现漏洞检测，并结合 Git Diff 分析和 Patch Verification（修复验证）流程，实现漏洞发现、代码修改分析以及修复效果自动验证闭环。

目前支持 PHP 安全漏洞检测，并提供结构化漏洞结果输出。

---

# 项目介绍

在实际软件开发过程中，漏洞通常隐藏在代码提交和迭代过程中。

传统人工代码审计存在：

- 审计效率低
- 容易遗漏漏洞
- 难以持续验证修复效果

因此，本项目尝试构建一个轻量级 SAST 工具，实现：

```
源码
 |
 ↓
安全规则检测
 |
 ↓
漏洞结果输出
 |
 ↓
Git Diff分析
 |
 ↓
Patch修复验证
 |
 ↓
漏洞修复确认
```

---

# Features

- [x] 基于 Semgrep 自定义漏洞检测规则
- [x] PHP 安全漏洞静态扫描
- [x] JSON 格式漏洞结果输出
- [x] Git Commit Diff 分析
- [x] Patch 自动化修复验证
- [ ] Web 可视化扫描界面（开发中）
- [ ] AI 漏洞分析与修复建议（规划中）

---

# 项目架构

```
                 User Code
                     |
                     |
              RuleForge-SAST
                     |
        ----------------------------
        |                          |
 Semgrep Detection Engine      Git Analyzer
        |                          |
   Rule YAML Files          Patch Verification
        |
        |
 Vulnerability Report(JSON)
```

---

# 项目结构

```
RuleForge-SAST

├── backend
│   ├── engine
│   │   └── semgrep_runner.py
│   │
│   ├── analyzer
│   │   ├── git_diff.py
│   │   ├── evaluator.py
│   │   └── patch_verify.py
│   │
│   └── main.py
│
├── rules
│   └── php-unserialize.yaml
│
├── testcase
│   └── test.php
│
├── reports
│   └── result.json
│
├── requirements.txt
│
└── README.md
```

---

# 核心功能

## 1. 自定义漏洞规则检测

基于 Semgrep YAML Rule 实现漏洞检测。

例如 PHP 反序列化漏洞：

危险代码：

```php
<?php

unserialize($_GET["cmd"]);

?>
```

检测规则：

```yaml
rules:
  - id: php-dangerous-unserialize
    languages:
      - php
    message: Dangerous unserialize usage
    severity: ERROR
```

检测结果：

```
Rule:
php-dangerous-unserialize

File:
test.php

Line:
3
```

---

## 2. 降低误报检测

针对安全写法进行排除。

例如：

```php
unserialize(
    $data,
    [
        "allowed_classes" => false
    ]
);
```

通过：

```yaml
pattern-not
```

排除安全场景。

减少静态扫描误报。

---

## 3. JSON漏洞结果输出

扫描结果结构化输出：

```json
{
    "vulnerabilities": [
        {
            "rule": "rules.php-dangerous-unserialize",
            "file": "test.php",
            "line": 3
        }
    ]
}
```

方便后续接入：

- Web管理平台
- 漏洞报告系统
- AI分析模块

---

## 4. Git Diff 分析

针对代码提交变化进行分析。

示例：

修改前：

```php
unserialize($_GET["cmd"]);
```

修改后：

```php
unserialize(
    $_GET["cmd"],
    [
        "allowed_classes"=>false
    ]
);
```

通过 Git Diff 获取：

```diff
- unserialize($_GET["cmd"]);

+ unserialize(
+ $_GET["cmd"],
+ ["allowed_classes"=>false]
+ );
```

---

## 5. Patch 修复验证

自动判断漏洞是否修复。

流程：

```
旧版本代码

      |
      ↓

Semgrep扫描

      |
      ↓

代码修复

      |
      ↓

再次扫描

      |
      ↓

结果对比
```

示例：

修复前：

```
Findings: 1
```

修复后：

```
Findings: 0
```

结果：

```
FIXED
```

---

# Supported Vulnerabilities

|漏洞类型|语言|检测方式|
|-|-|-|
|PHP Unsafe Deserialization|PHP|Semgrep AST Rule|

---

# Roadmap

未来计划：

- [ ] 增加 SQL Injection 检测规则
- [ ] 增加 Command Injection 检测规则
- [ ] 增加文件上传漏洞检测
- [ ] 增加 SSRF 检测
- [ ] 增加 Web 可视化管理界面
- [ ] 接入 LLM 自动漏洞分析
- [ ] 自动生成漏洞修复建议

---

# Installation

## 1. Clone项目

```bash
git clone https://github.com/hey-Chloe/RuleForge-SAST.git

cd RuleForge-SAST
```

---

## 2. 安装Python依赖

```bash
pip install -r requirements.txt
```

安装 Semgrep：

```bash
pip install semgrep
```

检查：

```bash
semgrep --version
```

---

# Usage

## 1. Semgrep扫描

```bash
semgrep scan \
--config rules/php-unserialize.yaml \
testcase
```

---

## 2. RuleForge扫描

```bash
python backend/main.py scan testcase
```

输出：

```
RuleForge-SAST

开始扫描...

发现漏洞:

规则:
php-dangerous-unserialize

文件:
test.php

行号:
3
```

---

## 3. 查看JSON报告

扫描完成后：

```
reports/result.json
```

示例：

```json
{
    "rule":"php-dangerous-unserialize",
    "file":"test.php",
    "line":3
}
```

---

# Demo

## 扫描结果

放置截图：

```
docs/
├── scan.png
├── result.png
└── architecture.png
```

展示：

![scan](docs/scan.png)

![result](docs/result.png)

---

# Tech Stack

## Backend

- Python
- FastAPI
- Semgrep
- GitPython

## Security

- SAST
- AST Pattern Matching
- Vulnerability Detection
- Patch Verification

## Frontend（规划）

- Vue3
- Vite
- Axios

---

# Project Goals

通过 RuleForge-SAST 学习并实践：

- 静态应用安全测试（SAST）
- 安全规则编写
- 自动化漏洞检测
- Git代码审计流程
- 漏洞修复验证

---

# Author

hey-Chloe

Security Engineering Learning Project
