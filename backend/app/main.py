from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import Settings, rules_path
from app.schemas import SolveRequest, SolveResponse
from app.services.gemini_service import solve_with_gemini

settings = Settings()
app = FastAPI(title="Smart Math Solver (COKB)", version="1.0.0")

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


@app.post("/api/solve", response_model=SolveResponse)
def solve(body: SolveRequest) -> SolveResponse:
    rules_file: Path = rules_path()
    if not rules_file.is_file():
        raise HTTPException(status_code=500, detail=f"Không tìm thấy rules.json tại {rules_file}")
    try:
        return solve_with_gemini(
            settings=settings,
            rules_file=rules_file,
            problem=body.problem.strip(),
            grade_level=body.grade_level,
        )
    except RuntimeError as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower() or "throttling" in error_msg.lower():
            raise HTTPException(
                status_code=429,
                detail="Đã vượt quá giới hạn sử dụng Gemini API. Vui lòng thử lại sau hoặc kiểm tra billing.",
            )
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Lỗi suy diễn: {e!s}") from e
