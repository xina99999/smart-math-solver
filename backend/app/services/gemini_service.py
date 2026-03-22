import json
import logging
import re
from pathlib import Path

from google import genai
from google.genai import types

from app.config import Settings
from app.schemas import SolveResponse

logger = logging.getLogger(__name__)


def _load_rules_text(rules_file: Path) -> str:
    if not rules_file.is_file():
        return "{}"
    return rules_file.read_text(encoding="utf-8")


def _strip_json_fence(raw: str) -> str:
    text = raw.strip()
    m = re.match(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", text, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return text


def _parse_solve_response(raw: str) -> SolveResponse:
    cleaned = _strip_json_fence(raw)
    data = json.loads(cleaned)
    return SolveResponse.model_validate(data)


def build_system_instruction(rules_json: str, grade_level: int) -> str:
    cap = "cap_1" if grade_level == 1 else "cap_2"
    return f"""Bạn là bộ suy diễn (Inference Engine) của hệ thống giải toán theo mô hình COKB.
Người dùng đang học cấp {grade_level}. Áp dụng inference_logic["{cap}"] trong file tri thức.

NỘI DUNG TRI THỨC (rules.json — chỉ được dùng các đối tượng, thuộc tính và công thức sau đây):
{rules_json}

QUY TẮC BẮT BUỘC:
1) Xác định đối tượng toán học phù hợp (Object) và các thuộc tính đã biết / cần tìm.
2) Chỉ dùng các công thức có trong rules của object đó (hoặc suy ra trực tiếp từ chúng).
3) Trình bày từng bước rõ ràng; mỗi bước có thể có công thức LaTeX trong trường "latex" (chuỗi LaTeX thuần, không bọc $).
4) Đáp án cuối ghi trong "result" (kèm đơn vị nếu đề cho đơn vị).

ĐẦU RA: CHỈ một object JSON hợp lệ, không có ký tự nào khác trước hoặc sau JSON.
Schema:
{{
  "method": "string",
  "steps": [
    {{
      "step_number": 1,
      "title": "string",
      "latex": "string hoặc null",
      "explanation": "string"
    }}
  ],
  "result": "string"
}}
"""


def _gemini_failure_detail(response: types.GenerateContentResponse) -> str | None:
    """Trả về chuỗi mô tả ngắn nếu không có nội dung hợp lệ để parse."""
    if getattr(response, "prompt_feedback", None) is not None:
        pf = response.prompt_feedback
        br = getattr(pf, "block_reason", None)
        if br is not None and str(br) not in ("BlockReason.BLOCK_REASON_UNSPECIFIED", "BLOCK_REASON_UNSPECIFIED"):
            return f"Prompt bị chặn: block_reason={br}"
    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        return "Không có candidates trong phản hồi (có thể do chính sách an toàn hoặc lỗi model)."
    c0 = candidates[0]
    fr = getattr(c0, "finish_reason", None)
    if fr is not None:
        fr_str = str(fr)
        if "SAFETY" in fr_str or "RECITATION" in fr_str:
            return f"Kết thúc bất thường: finish_reason={fr_str}"
    return None


def _extract_text(response: types.GenerateContentResponse) -> str:
    detail = _gemini_failure_detail(response)
    try:
        raw = response.text
    except Exception as e:
        if detail:
            raise RuntimeError(detail) from e
        raise RuntimeError(f"Không đọc được nội dung phản hồi: {e!s}") from e
    if raw and str(raw).strip():
        return str(raw).strip()
    if detail:
        raise RuntimeError(detail)
    raise RuntimeError("Gemini trả về nội dung rỗng (response.text).")


def solve_with_gemini(
    *,
    settings: Settings,
    rules_file: Path,
    problem: str,
    grade_level: int,
) -> SolveResponse:
    if not settings.gemini_api_key:
        raise RuntimeError("Thiếu GEMINI_API_KEY (đặt biến môi trường hoặc file backend/.env).")

    rules_text = _load_rules_text(rules_file)
    system_instruction = build_system_instruction(rules_text, grade_level)

    user_text = f"""---
YÊU CẦU BÀI TOÁN:
Đề bài (tiếng Việt): {problem}
Cấp độ học: {grade_level}

HÃY TRẢ LỜI CHỈ BẰNG JSON HỢP LỆ."""

    client = genai.Client(api_key=settings.gemini_api_key)
    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=user_text,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.1,
                response_mime_type="application/json",
            ),
        )
    except Exception as e:
        logger.exception("gemini generate_content failed")
        msg = str(e)
        if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
            raise RuntimeError(
                "Hết quota / throttling Gemini (429). Thử lại sau hoặc kiểm tra billing / API key."
            ) from e
        raise RuntimeError(f"Lỗi khi gọi Gemini API: {msg}") from e

    try:
        raw = _extract_text(response)
        return _parse_solve_response(raw)
    except Exception as e:
        logger.exception("parse Gemini JSON failed; raw=%s", getattr(response, "text", None))
        raise RuntimeError(
            f"Không parse được JSON từ Gemini: {e!s}. "
            f"Đảm bảo model hỗ trợ response_mime_type=application/json."
        ) from e
