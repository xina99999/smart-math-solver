from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SolveStep(BaseModel):
    model_config = ConfigDict(extra="ignore")
    step_number: int = Field(ge=1)
    title: str = Field(min_length=1)
    latex: Optional[str] = None
    explanation: str = Field(min_length=1)


class SolveResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    method: str = Field(min_length=1, description="Tên phương pháp / định luật / object COKB")
    steps: list[SolveStep]
    result: str = Field(min_length=1, description="Đáp số cuối (có đơn vị nếu có)")


class SolveRequest(BaseModel):
    problem: str = Field(min_length=1, description="Bài toán hoặc phép tính (tiếng Việt)")
    grade_level: int = Field(ge=1, le=2, description="1 = cấp 1, 2 = cấp 2")
