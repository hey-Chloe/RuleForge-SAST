## RuleForge-SAST：基于 Semgrep 与大语言模型的多语言静态应用安全分析平台。

RuleForge-SAST 支持 PHP、Python 和 Java 源码扫描，能够自动识别代码语言、执行匹配的安全规则、展示漏洞详情，并结合 AI 生成修复建议，再通过 Semgrep 对修改后的代码进行二次验证。

## 核心功能
多语言代码扫描：支持 PHP、Python 和 Java，自动识别文件语言并匹配对应的 Semgrep 规则，可进行全规则或指定规则扫描。
漏洞结果分析：展示漏洞等级、CWE、文件位置、相关代码片段、风险说明和修复建议。
扫描历史管理：保存真实扫描记录，便于回顾扫描结果和问题变化。
AI 辅助修复：对扫描结果进行通俗解释，并生成针对性的代码修复建议。
修复效果验证：重新扫描修复后的代码，对比修复前后结果，判断漏洞是否已经消除。

## 快速开始

### 1. 环境要求

请先安装：

- Python 3.10+
- Node.js 18+
- Git

检查版本：

```bash
python --version
node --version
npm --version
git --version
```

### 2. 克隆项目

```bash
git clone https://github.com/hey-Chloe/RuleForge-SAST.git
cd RuleForge-SAST
```

### 3. 安装后端依赖

#### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install semgrep
```

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install semgrep
```

确认 Semgrep 可用：

```bash
semgrep --version
```

### 4. 启动项目

项目需要同时运行后端和前端，请打开两个终端。

#### 终端一：启动后端

```bash
cd backend
python -m uvicorn api:app --reload --port 8000
```

#### 终端二：启动前端

```bash
cd backend/frontend
npm install
npm run dev
```

前端启动后，在浏览器中打开终端显示的地址，通常为：

```text
http://localhost:5173
```

> macOS / Linux 如果没有 `python` 命令，请将命令替换为 `python3`。
## AI 配置

AI 修复建议功能使用 OpenRouter API。未配置 API Key 时，代码扫描、漏洞详情和扫描历史仍可正常使用。

复制环境变量模板：

```powershell
Copy-Item .env.example .env
```

macOS / Linux：

```bash
cp .env.example .env
```

编辑 `.env`：

```env
OPENROUTER_API_KEY=
AI_MODEL=deepseek/deepseek-v4-flash
AI_DAILY_REQUEST_LIMIT=3
AI_DAILY_BUDGET_USD=0.03
AI_MAX_OUTPUT_TOKENS=1000
AI_MAX_CODE_CHARS=4000
AI_REQUEST_TIMEOUT_SECONDS=30
```


---
## 在线演示

🎬 [点击观看 RuleForge-SAST 一分钟项目演示](https://www.bilibili.com/video/BV1YC3Z6EEJC/)

视频展示：

- PHP、Python、Java 自动识别
- Semgrep 全规则扫描
- 漏洞详情与代码片段
- AI 漏洞解释与修复建议
- Patch 修复验证
- 真实扫描历史

## 项目截图

### 多语言代码扫描

<img width="2582" height="1224" alt="image" src="https://github.com/user-attachments/assets/fafe9000-ea7e-494a-883d-27e7e55e91fd" />


### 漏洞详情

<img width="2590" height="1236" alt="image" src="https://github.com/user-attachments/assets/fb71e2e5-4e6e-4f2a-9215-30f774a5cd5f" />

### AI 修复建议

<img width="862" height="722" alt="image" src="https://github.com/user-attachments/assets/11929f30-7bad-40f5-a2db-f01c9484589b" />




---
## 演示流程

推荐使用测试文件：

```text
testcase/VulnerableController.java
```

1. 上传源码，系统自动识别语言并加载对应规则。
2. 使用全部适用规则进行 Semgrep 扫描。
3. 查看漏洞等级、CWE、命中代码和修复建议。
4. 生成 AI 漏洞解释与修复代码。
5. 将修复代码交给 Patch Verify，查看验证结果和扫描历史。

```text
上传源码
→ 自动识别语言
→ Semgrep 扫描
→ 漏洞详情
→ AI 修复建议
→ Patch 二次验证
→ 保存扫描历史
```

---

## Patch 验证状态

| 状态 | 含义 |
|---|---|
| `FIXED` | 修复后当前规则不再检测到漏洞 |
| `NOT_FIXED` | 修复后仍能检测到漏洞 |
| `NO_VULNERABILITY` | 修复前未检测到对应漏洞 |

> AI 建议仅供参考，只有经过 Semgrep 二次扫描后才会生成验证状态。
## 常见问题

### PowerShell 禁止运行激活脚本

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 无法识别 Semgrep

先确认虚拟环境已经激活，然后重新安装：

```bash
python -m pip install --upgrade semgrep
semgrep --version
```

仍无法使用时，可以通过 pipx 安装：

```bash
python -m pip install --user pipx
python -m pipx ensurepath
pipx install semgrep
```

### FastAPI 接口文档

后端启动后可访问：

```text
http://127.0.0.1:8000/docs
```
---

## 安全说明

- AI 修复建议仅供参考，不代表漏洞已经修复。
- Patch 验证结果由当前 Semgrep 规则判断。
- 未被规则检测到不代表代码绝对安全。
- 上传文件仅用于临时扫描。
- 临时文件使用唯一文件名并保留原始扩展名。
- 扫描结束或发生异常后，临时文件会自动删除。
- AI 功能只发送当前漏洞的代码片段，不发送完整项目。
- API Key 仅从后端环境变量读取。
- 前端不会保存、显示或返回 API Key。
- AI 请求带有缓存、每日次数限制和预算限制。
- SQLite 数据库文件不会提交到 Git 仓库。

---



## 免责声明

本项目主要用于安全学习、静态代码分析研究和授权环境中的漏洞检测。

请勿将本项目用于未经授权的系统或代码分析。使用者应自行承担因错误使用而产生的责任。

---
