# RuleForge-SAST

## 代码安全扫描工具

一个基于 **Semgrep** 的轻量级静态应用安全检测工具（SAST）。

RuleForge-SAST 通过自定义安全规则实现代码漏洞检测，并结合 **Git Diff 分析** 与 **Patch 修复验证流程**，对漏洞修复效果进行自动化验证。

---

# 项目背景

在实际软件开发过程中，安全漏洞往往隐藏在代码提交过程中。

传统漏洞检测工具通常只能发现问题，但无法判断：

- 漏洞是否已经修复
- 修复代码是否有效
- 修改前后漏洞数量变化

因此，本项目尝试构建一个简单的 SAST 检测闭环：

```
源代码
  ↓
安全规则匹配
  ↓
漏洞检测
  ↓
Git Diff 分析
  ↓
Patch 修复验证
  ↓
输出检测结果
```

---

# 核心功能

## 1. 自定义漏洞规则

基于 Semgrep YAML 规则实现漏洞检测。

当前支持：

- PHP 危险反序列化检测


危险代码：

```php
<?php

unserialize($_GET["cmd"]);

?>
```

检测结果：

```
Dangerous unserialize usage
```

---

## 2. 安全规则误报过滤

针对安全修复代码进行排除。

例如：

```php
unserialize(
    $_GET["cmd"],
    [
        "allowed_classes" => false
    ]
);
```

该写法不会被检测为危险反序列化。

实现：

```
pattern-not
```

用于降低安全扫描误报。

---

## 3. Semgrep 结果封装

将 Semgrep 原始 JSON 结果转换为统一格式：

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

- Web 管理页面
- 漏洞报告模块
- AI 分析模块

---

## 4. Git Diff 分析

支持分析代码提交前后的变化。


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
        "allowed_classes" => false
    ]
);
```


输出：

```
- unserialize($_GET["cmd"]);

+ allowed_classes=false
```

---

## 5. Patch 修复验证

自动验证漏洞修复是否有效。


流程：

```
旧版本代码
    ↓
Semgrep扫描
    ↓
应用Patch
    ↓
新版代码
    ↓
Semgrep扫描
    ↓
结果对比
```


示例：

漏洞数量：

```
1 → 0
```

结果：

```
FIXED
```

---

# 项目结构

```
RuleForge-SAST
│
├── backend
│   │
│   ├── engine
│   │   └── semgrep_runner.py
│   │
│   ├── analyzer
│   │   ├── git_diff.py
│   │   ├── evaluator.py
│   │   └── patch_verify.py
│   │
│   └── test_runner.py
│
├── rules
│   └── php-unserialize.yaml
│
├── testcase
│   └── test.php
│
├── requirements.txt
│
└── README.md
```

---

# 环境准备

支持：

- Windows
- Linux


Python：

```
Python >= 3.10
```


检查：

```bash
python --version
```

---

# 安装依赖

进入项目目录：

```bash
cd RuleForge-SAST
```


安装依赖：

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

# 使用方法


## 1. Semgrep 直接扫描

执行：

```bash
semgrep scan \
--config rules/php-unserialize.yaml \
testcase
```


输出：

```
1 Code Finding
```


示例：

```
testcase/test.php

Dangerous unserialize usage
```

---

## 2. 使用 RuleForge 封装扫描


执行：

```bash
python backend/engine/test_runner.py
```


输出：

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

---

# 技术栈

- Python
- Semgrep
- GitPython
- FastAPI
- YAML规则


---

# 后续计划

## 增加漏洞规则

计划支持：

- SQL注入
- 文件上传
- 命令执行
- SSRF


---

## LLM 辅助分析

结合大语言模型：

实现：

- 漏洞原因分析
- 利用方式说明
- 修复建议自动生成


---

## Web 管理平台

提供：

- 在线代码扫描
- 漏洞报告展示
- Patch 修复验证


---

# 项目定位

RuleForge-SAST 是一个面向代码安全分析的轻量级 SAST 平台。


目标：

```
代码输入
    ↓
安全规则扫描
    ↓
漏洞发现
    ↓
AI漏洞解释
    ↓
自动修复验证
```
