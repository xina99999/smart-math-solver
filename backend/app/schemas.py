from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class StepExplanation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    step_number: int = Field(ge=1)
    title: str = Field(min_length=1)
    explanation: str = Field(min_length=1)
    suggested_code: Optional[str] = None


class DiagnosticItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    rule_id: str = Field(min_length=1)
    error_type: str = Field(min_length=1)
    severity: Literal["low", "medium", "high", "critical"]
    why_it_happens: str = Field(min_length=1)
    evidence: str = Field(min_length=1)
    fix_summary: str = Field(min_length=1)
    step_explanations: list[StepExplanation]


class RuleBasedResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    method: str = Field(min_length=1)
    detected_topics: list[str]
    diagnostics: list[DiagnosticItem]
    next_learning_steps: list[str]


class LlmBaselineResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    analysis: str = Field(min_length=1)
    suggested_fixes: list[str]
    confidence: str = Field(min_length=1)


class ComparisonResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    coverage_note: str = Field(min_length=1)
    interpretability_note: str = Field(min_length=1)
    actionability_note: str = Field(min_length=1)


class DiagnoseRequest(BaseModel):
    problem_title: str = Field(min_length=1, description="Tên bài tập lập trình")
    problem_statement: str = Field(min_length=1, description="Mô tả đề bài")
    source_code: str = Field(min_length=1, description="Mã nguồn sinh viên")
    language: Literal["c", "cpp"] = "cpp"
    compare_with_llm: bool = True


class DiagnoseResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    knowledge_model: str = Field(min_length=1)
    code_pattern_flow: list[str]
    rule_based: RuleBasedResult
    llm_baseline: Optional[LlmBaselineResult] = None
    comparison: Optional[ComparisonResult] = None
