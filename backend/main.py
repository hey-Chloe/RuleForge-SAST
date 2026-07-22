from fastapi import FastAPI
from pydantic import BaseModel

from engine.semgrep_runner import scan


app = FastAPI(
    title="RuleForge-SAST"
)


class ScanRequest(BaseModel):

    target: str

    rule: str



@app.get("/")
def index():

    return {
        "message":
        "RuleForge-SAST running"
    }



@app.post("/scan")
def scan_code(request: ScanRequest):

    result = scan(
        request.target,
        request.rule
    )

    return result