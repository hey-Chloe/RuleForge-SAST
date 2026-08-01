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
)
from services.ai_explainer import AIInputError, explain_vulnerability
from services.deepseek_client import AIConfigurationError, AIUpstreamError


app = FastAPI()
BACKEND_DIRECTORY = Path(__file__).resolve().parent
DEFAULT_SCAN_RULE_ID = "php-dangerous-unserialize"


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
):
    selected_rule_id = rule_id.strip() if isinstance(rule_id, str) and rule_id.strip() else DEFAULT_SCAN_RULE_ID

    try:
        selected_rule, rule_path = resolve_rule_for_language(selected_rule_id, "php")
    except RuleSelectionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
    except RuleCatalogError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to select local scan rule: {exc}",
        ) from None

    upload_path = BACKEND_DIRECTORY / "temp.php"
    try:
        with upload_path.open("wb") as destination:
            shutil.copyfileobj(file.file, destination)

        result = scan(str(upload_path), str(rule_path))
    except Exception:
        raise HTTPException(status_code=500, detail="Semgrep scan failed") from None
    finally:
        if upload_path.exists():
            upload_path.unlink()

    for vulnerability in result.get("vulnerabilities", []):
        vulnerability["id"] = selected_rule["id"]
        vulnerability["rule"] = selected_rule["id"]

    result["scan"] = {
        "rule_id": selected_rule["id"],
        "source_file": selected_rule["source_file"],
    }
    return result
