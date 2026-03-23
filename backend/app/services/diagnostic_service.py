import json
import re
from pathlib import Path
from typing import Any

from app.schemas import (
    ComparisonResult,
    DiagnoseRequest,
    DiagnoseResponse,
    DiagnosticItem,
    LlmBaselineResult,
    RuleBasedResult,
    StepExplanation,
)
from app.services.gemini_service import generate_llm_baseline


def _load_knowledge(rules_file: Path) -> dict[str, Any]:
    return json.loads(rules_file.read_text(encoding="utf-8"))


def _match_rule(source_code: str, rule: dict[str, Any]) -> tuple[bool, str]:
    """Match source code against rule patterns with enhanced detection."""
    for pattern_item in rule.get("detection_patterns", []):
        regex = pattern_item.get("regex", "")
        evidence_template = pattern_item.get("evidence", "")
        if not regex:
            continue
        try:
            match = re.search(regex, source_code, flags=re.MULTILINE | re.DOTALL)
            if match:
                evidence = evidence_template.format(match=match.group(0)) if evidence_template else match.group(0)
                return True, evidence
        except re.error:
            continue
    
    # Enhanced heuristics for common errors
    if rule["id"] == "R_OFF_BY_ONE_ARRAY":
        # Check for array access patterns that might indicate off-by-one
        if re.search(r"a\[\s*[ni]\s*\]", source_code, re.IGNORECASE) and "for" in source_code:
            if re.search(r"<=\s*n", source_code):
                return True, "Mảng truy cập a[n] với điều kiện <= n phát hiện"
    
    if rule["id"] == "R_UNINITIALIZED_ARRAY_ACCESS":
        # Check for array initialization without null check
        if re.search(r"int\s+\w+\s*=\s*a\[\s*0\s*\]", source_code):
            if not re.search(r"if\s*\(\s*n\s*>\s*0\s*\)", source_code):
                return True, "Khởi tạo từ a[0] mà không kiểm tra n > 0"
    
    return False, ""


def _build_steps(rule: dict[str, Any], source_code: str) -> list[StepExplanation]:
    steps: list[StepExplanation] = []
    for index, step in enumerate(rule.get("guided_fix_steps", []), start=1):
        suggested = step.get("suggested_code")
        if suggested and "{code}" in suggested:
            suggested = suggested.replace("{code}", source_code)
        steps.append(
            StepExplanation(
                step_number=index,
                title=step.get("title", f"Step {index}"),
                explanation=step.get("explanation", ""),
                suggested_code=suggested,
            )
        )
    return steps


def run_diagnosis(
    *,
    rules_file: Path,
    body: DiagnoseRequest,
    gemini_api_key: str,
    gemini_model: str,
) -> DiagnoseResponse:
    knowledge = _load_knowledge(rules_file)
    rule_set = knowledge.get("diagnostic_rules", [])
    topic_map = knowledge.get("topic_keywords", {})

    lowered = f"{body.problem_title}\n{body.problem_statement}\n{body.source_code}".lower()
    detected_topics = [topic for topic, keywords in topic_map.items() if any(k.lower() in lowered for k in keywords)]

    diagnostics: list[DiagnosticItem] = []
    for rule in rule_set:
        matched, evidence = _match_rule(body.source_code, rule)
        if not matched:
            continue
        diagnostics.append(
            DiagnosticItem(
                rule_id=rule["id"],
                error_type=rule["error_type"],
                severity=rule["severity"],
                why_it_happens=rule["why_it_happens"],
                evidence=evidence,
                fix_summary=rule["fix_summary"],
                step_explanations=_build_steps(rule, body.source_code),
            )
        )

    if not diagnostics:
        diagnostics.append(
            DiagnosticItem(
                rule_id="NO_RULE_TRIGGERED",
                error_type="Chưa phát hiện lỗi logic theo tập luật hiện tại",
                severity="low",
                why_it_happens="Mã nguồn có thể đúng hoặc lỗi nằm ngoài tập lỗi đã mô hình hóa.",
                evidence="Không có biểu thức nào khớp mẫu trong diagnostic_rules.",
                fix_summary="Chạy thêm test biên, test ngẫu nhiên, và kiểm tra lại điều kiện dừng.",
                step_explanations=[
                    StepExplanation(
                        step_number=1,
                        title="Tạo bộ test biên",
                        explanation="Thêm test cho n=0, n=1, và giá trị cực đại theo đề bài để phát hiện lỗi tiềm ẩn.",
                    ),
                    StepExplanation(
                        step_number=2,
                        title="Đối chiếu với thuật toán chuẩn",
                        explanation="So sánh từng bước chạy giữa code hiện tại và pseudo-code chuẩn để định vị sai lệch logic.",
                    ),
                ],
            )
        )

    rule_based = RuleBasedResult(
        method="Rule-Based Reasoning + Pattern Matching",
        detected_topics=detected_topics,
        diagnostics=diagnostics,
        next_learning_steps=knowledge.get("recommended_learning_path", []),
    )

    llm_baseline: LlmBaselineResult | None = None
    comparison: ComparisonResult | None = None
    if body.compare_with_llm:
        llm_baseline = generate_llm_baseline(
            problem_title=body.problem_title,
            problem_statement=body.problem_statement,
            source_code=body.source_code,
            language=body.language,
            gemini_api_key=gemini_api_key,
            gemini_model=gemini_model,
        )
        comparison = ComparisonResult(
            coverage_note=(
                "Hệ thống luật tập trung vào lỗi đã mô hình hóa nên ổn định hơn ở lỗi điển hình; "
                "LLM baseline có thể bao phủ rộng hơn nhưng không luôn nhất quán."
            ),
            interpretability_note=(
                "Kết quả rule-based nêu rõ Rule_Triggered và evidence cụ thể, "
                "giúp giảng viên/sinh viên truy vết dễ hơn."
            ),
            actionability_note=(
                "Rule-based cung cấp step_explanations có trình tự sửa lỗi; "
                "LLM baseline hữu ích để gợi ý bổ sung các hướng cải tiến."
            ),
        )

    return DiagnoseResponse(
        knowledge_model=knowledge.get("knowledge_model", "Problem <-> Algorithm <-> Data Structure <-> Error <-> Fix"),
        code_pattern_flow=[
            "Code",
            "Pattern Matching",
            "Rule Triggered",
            "Step Explanation",
        ],
        rule_based=rule_based,
        llm_baseline=llm_baseline,
        comparison=comparison,
    )
