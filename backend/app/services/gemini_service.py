import logging

from google import genai
from google.genai import types

from app.schemas import LlmBaselineResult

logger = logging.getLogger(__name__)


def generate_llm_baseline(
    *,
    problem_title: str,
    problem_statement: str,
    source_code: str,
    language: str,
    gemini_api_key: str,
    gemini_model: str,
) -> LlmBaselineResult:
    if not gemini_api_key:
        return LlmBaselineResult(
            analysis="Không thể chạy baseline LLM vì thiếu GEMINI_API_KEY.",
            suggested_fixes=["Thiết lập GEMINI_API_KEY trong backend/.env để bật so sánh với baseline."],
            confidence="low",
        )

    prompt = f"""
Bạn là reviewer code cho sinh viên nhập môn lập trình.
Hãy đọc đề bài, mã nguồn và trả lời theo định dạng thuần văn bản:
1) Tóm tắt lỗi logic/thuật toán quan trọng
2) 3-5 gợi ý sửa lỗi ngắn gọn
3) Mức tự tin: high/medium/low

Đề bài: {problem_title}
Mô tả: {problem_statement}
Ngôn ngữ: {language}
Mã nguồn:
{source_code}
"""
    client = genai.Client(api_key=gemini_api_key)
    try:
        response = client.models.generate_content(
            model=gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
            ),
        )
    except Exception as e:
        logger.exception("gemini baseline failed")
        return LlmBaselineResult(
            analysis=f"Baseline LLM gặp lỗi khi gọi Gemini: {e!s}",
            suggested_fixes=["Thử lại sau hoặc kiểm tra quota/API key."],
            confidence="low",
        )

    raw = (getattr(response, "text", None) or "").strip()
    if not raw:
        return LlmBaselineResult(
            analysis="Baseline LLM không trả về nội dung.",
            suggested_fixes=["Thử model khác hoặc giảm độ dài mã nguồn đầu vào."],
            confidence="low",
        )

    lines = [line.strip("- ").strip() for line in raw.splitlines() if line.strip()]
    fixes = [line for line in lines if any(token in line.lower() for token in ("sửa", "fix", "đổi", "thêm"))]
    if not fixes:
        fixes = lines[1:5] if len(lines) > 1 else [raw]

    confidence = "medium"
    text_lower = raw.lower()
    if "mức tự tin: high" in text_lower or "confidence: high" in text_lower:
        confidence = "high"
    elif "mức tự tin: low" in text_lower or "confidence: low" in text_lower:
        confidence = "low"

    return LlmBaselineResult(
        analysis=raw[:1200],
        suggested_fixes=fixes[:5],
        confidence=confidence,
    )
