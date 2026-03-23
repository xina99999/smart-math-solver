from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import Settings, rules_path
from app.schemas import DiagnoseRequest, DiagnoseResponse
from app.services.diagnostic_service import run_diagnosis

settings = Settings()
app = FastAPI(title="Smart Programming Diagnosis System", version="2.0.0")

_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model": settings.gemini_model}


class RulesMeta(BaseModel):
    path: str


@app.get("/api/rules", response_model=RulesMeta)
def get_rules_info() -> RulesMeta:
    p = rules_path()
    return RulesMeta(path=str(p))


@app.post("/api/diagnose", response_model=DiagnoseResponse)
def diagnose(body: DiagnoseRequest) -> DiagnoseResponse:
    rules_file: Path = rules_path()
    if not rules_file.is_file():
        raise HTTPException(status_code=500, detail=f"Không tìm thấy rules.json tại {rules_file}")
    try:
        return run_diagnosis(
            rules_file=rules_file,
            body=body,
            gemini_api_key=settings.gemini_api_key,
            gemini_model=settings.gemini_model,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Lỗi suy diễn: {e!s}") from e


@app.post("/api/solve", response_model=DiagnoseResponse)
def solve_alias(body: DiagnoseRequest) -> DiagnoseResponse:
    return diagnose(body)
