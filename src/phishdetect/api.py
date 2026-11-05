"""REST API (FastAPI) + a lightweight web page served at '/'.

Run:  uvicorn phishdetect.api:app --app-dir src --port 8000
Then open http://127.0.0.1:8000
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from . import __version__
from .audit import AuditLog
from .pipeline import Detector, InputError

STATIC = Path(__file__).parent / "static"

app = FastAPI(title="AI Phishing & Scam Detector", version=__version__,
              description="CSIT305 research prototype - decision support, not a guarantee of safety.")
detector = Detector()
audit = AuditLog(os.environ.get("PHISHDETECT_AUDIT_DB", AuditLog().path))


class AnalyzeRequest(BaseModel):
    type: Literal["email", "sms", "url"]
    text: str = Field(..., max_length=100_000)
    consent: bool = Field(..., description="User agrees to have this input analysed")
    allow_logging: bool = Field(False, description="Store a de-identified record (no text) for evaluation")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": __version__,
            "models": {f: a["version"] for f, a in detector.art.items()}}


@app.post("/analyze")
def analyze(req: AnalyzeRequest) -> dict:
    if not req.consent:  # workflow step 1: no consent, no analysis
        raise HTTPException(status_code=403, detail="Consent is required before analysis.")
    try:
        result = detector.analyze(req.type, req.text)
    except InputError as e:
        raise HTTPException(status_code=422, detail=str(e))
    if req.allow_logging:
        audit.write(req.type, result)
    result["logged"] = req.allow_logging
    return result


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")
