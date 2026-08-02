import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

import shutil

from engine.semgrep_runner import scan
from services.rule_catalog import (
    RuleCatalogError,
    RuleSelectionError,
    load_rule_catalog,
    resolve_rule_for_language,
    resolve_rules_for_language,
)

from services.ai_explainer import AIInputError, explain_vulnerability
from services.deepseek_client import AIConfigurationError, AIUpstreamError

from database.scan_history import list_scan_history, save_scan_record



app = FastAPI()
BACKEND_DIRECTORY = Path(__file__).resolve().parent
DEFAULT_SCAN_RULE_ID = "php-dangerous-unserialize"

# 扩展名 -> Semgrep 语言。仅包含规则目录中真实存在的语言。
EXTENSION_LANGUAGE_MAP = {
    ".php": "php",
    ".py": "python",
    ".java": "java",
}



@app.get("/rules")
def get_rules():
    try:
        return {"rules": load_rule_catalog()}
    except RuleCatalogError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to load local rule catalog: {exc}",
        ) from None


@app.post("/ai/explain")
async def explain_vulnerability_with_ai(payload: dict[str, object]):
    try:
        return await explain_vulnerability(payload)
    except AIInputError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
    except AIConfigurationError:
        raise HTTPException(
            status_code=503,
            detail="AI explanation service is not configured",
        ) from None
    except AIUpstreamError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from None



# 解决 Vue(localhost:5173)
# 请求 FastAPI(127.0.0.1:8000) 的跨域问题

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173"
    ],

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ],
)



@app.post("/scan")
async def scan_code(
    file: UploadFile = File(...),
    rule_id: str | None = Form(None),
    scan_mode: str | None = Form(None),
):
    # 扫描模式：all（默认，使用该语言全部规则）或 single（指定单条规则）。
    mode = (scan_mode or "all").strip().lower()
    if mode not in {"all", "single"}:
        raise HTTPException(status_code=400, detail="scan_mode 仅支持 all 或 single")

    # 后端根据上传文件原始文件名的扩展名重新识别语言，不信任前端。
    original_name = file.filename or ""
    extension = Path(original_name).suffix.lower()
    language = EXTENSION_LANGUAGE_MAP.get(extension)
    if language is None:
        supported = "、".join(sorted(EXTENSION_LANGUAGE_MAP))
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型：{extension or '(无扩展名)'}。当前仅支持 {supported} 文件。",
        )

    # 根据后端识别的语言解析规则，不信任前端传入的规则数量或语言。
    try:
        if mode == "all":
            resolved_rules = resolve_rules_for_language(language)
            rule_paths = [str(path) for _, path in resolved_rules]
        else:
            selected_rule_id = rule_id.strip() if isinstance(rule_id, str) and rule_id.strip() else DEFAULT_SCAN_RULE_ID
            selected_rule, rule_path = resolve_rule_for_language(selected_rule_id, language)
            resolved_rules = [(selected_rule, rule_path)]
            rule_paths = [str(rule_path)]
    except RuleSelectionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
    except RuleCatalogError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to select local scan rule: {exc}",
        ) from None

    # 使用唯一临时文件并保留原始后缀，确保 Semgrep 按正确语言解析。
    upload_path = None
    try:
        fd, upload_path = tempfile.mkstemp(
            suffix=extension,
            prefix="scan_",
            dir=BACKEND_DIRECTORY,
        )
        os.close(fd)
        with open(upload_path, "wb") as destination:
            shutil.copyfileobj(file.file, destination)

        result = scan(str(upload_path), rule_paths)
    except Exception:
        raise HTTPException(status_code=500, detail="Semgrep scan failed") from None
    finally:
        if upload_path is not None and Path(upload_path).exists():
            Path(upload_path).unlink()

    # 每条漏洞保留对应的 rule id、severity、CWE、category、description 和 fix，
    # 并将 file 字段替换为用户上传的原始文件名，避免暴露 scan_xxx 临时文件名。
    rule_by_id = {rule["id"]: rule for rule, _ in resolved_rules}
    for vulnerability in result.get("vulnerabilities", []):
        vuln_rule = vulnerability.get("rule") or ""
        rule = rule_by_id.get(vuln_rule)
        if rule is None:
            # Semgrep 的 check_id 通常是完整路径，需按规则 id 后缀匹配。
            rule = next(
                (
                    item[0]
                    for item in resolved_rules
                    if vuln_rule.endswith(item[0]["id"])
                ),
                None,
            )
        if rule is not None:
            vulnerability["id"] = rule["id"]
            vulnerability["rule"] = rule["id"]
            vulnerability["severity"] = rule["severity"]
            vulnerability["cwe"] = rule["cwe"]
            vulnerability["category"] = rule["category"]
            vulnerability["description"] = rule["description"]
            vulnerability["fix"] = rule["fix"]
        vulnerability["file"] = original_name

    # 全部规则模式运行了多个规则，不返回单个 source_file/rule_id；
    # 指定单条规则模式仍返回该规则对应的 source_file。
    if mode == "all":
        result["scan"] = {
            "mode": mode,
            "language": language,
            "rule_count": len(resolved_rules),
        }
    else:
        result["scan"] = {
            "mode": mode,
            "language": language,
            "rule_count": len(resolved_rules),
            "rule_id": resolved_rules[0][0]["id"] if resolved_rules else "",
            "source_file": resolved_rules[0][0]["source_file"] if resolved_rules else "",
        }

    # 扫描成功后保存一条真实历史记录。即使 finding_count 为 0 也会保存。
    # 仅记录元数据，不保存上传文件内容、临时文件路径或 scan_xxx 临时文件名。
    selected_rule_id = (
        resolved_rules[0][0]["id"] if mode == "single" and resolved_rules else None
    )
    save_scan_record(
        filename=original_name,
        language=language,
        scan_mode=mode,
        rule_id=selected_rule_id,
        rule_count=len(resolved_rules),
        finding_count=len(result.get("vulnerabilities", [])),
        status="success",
    )
    return result


@app.get("/history")
def get_scan_history():
    """按时间倒序返回真实扫描历史记录。"""
    return {"history": list_scan_history()}




