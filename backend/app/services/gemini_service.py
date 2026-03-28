import logging
import re

from google import genai
from google.genai import types

from app.schemas import LlmBaselineResult

logger = logging.getLogger(__name__)


def _parse_llm_response(raw_text: str) -> tuple[str, list[str], str]:
    """
    Parse Gemini response into structured parts.
    
    Expected format:
    1) Tóm tắt lỗi...
    2) Ai gợi ý...
    3) Mức tự tin: high/medium/low
    
    Returns: (analysis, suggested_fixes, confidence)
    """
    analysis = ""
    fixes = []
    confidence = "medium"
    
    # Extract sections using regex
    sections = re.split(r'^\s*\d+\)\s*', raw_text, flags=re.MULTILINE)
    
    for section in sections[1:]:  # Skip first empty element
        section = section.strip()
        if not section:
            continue
            
        # Detect section type by keywords
        lower_sec = section.lower()
        
        if any(k in lower_sec for k in ["tóm tắt", "lỗi", "logic", "thuật toán"]):
            # Extract analysis (first 2-3 sentences or paragraphs)
            analysis = section.split("\n")[0]  # First paragraph
            # Get more detail if available
            para = section.split("\n\n")[0] if "\n\n" in section else section
            analysis = para[:1000]  # Limit to 1000 chars
            
        elif any(k in lower_sec for k in ["gợi ý", "sửa", "fix", "cải thiện"]):
            # Extract fixes - parse bullets or numbered items
            fix_lines = section.split("\n")
            for line in fix_lines:
                line = line.strip()
                if not line or line.startswith("Mức tự tin"):
                    continue
                # Remove bullet points and numbers
                clean_line = re.sub(r'^[\*\-\•\d\.]+\s*', '', line).strip()
                if clean_line and len(clean_line) > 10:  # Filter out very short lines
                    fixes.append(clean_line)
        
        # Check for confidence level
        if "mức tự tin" in lower_sec or "confidence" in lower_sec:
            if "high" in lower_sec or "cao" in lower_sec:
                confidence = "high"
            elif "low" in lower_sec or "thấp" in lower_sec:
                confidence = "low"
            else:
                confidence = "medium"
    
    # Fallback: if no analysis extracted, use first 500 chars
    if not analysis:
        analysis = raw_text[:500]
    
    # Fallback: if no fixes extracted, split by lines with keywords
    if not fixes:
        for line in raw_text.split("\n"):
            line = line.strip()
            if any(k in line.lower() for k in ["sửa", "fix", "thay", "thêm", "đổi"]):
                clean = re.sub(r'^[\*\-\•\d\.]+\s*', '', line).strip()
                if len(clean) > 10:
                    fixes.append(clean)
    
    # Limit fixes to 5
    fixes = fixes[:5]
    
    # If still no fixes, use first few lines
    if not fixes:
        fixes = [line.strip() for line in raw_text.split("\n") 
                if line.strip() and len(line.strip()) > 15][:4]
    
    return analysis, fixes, confidence


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

    prompt = f"""Bạn là reviewer code cho sinh viên nhập môn lập trình C/C++.
Hãy đọc đề bài, mã nguồn và phân tích theo đúng định dạng dưới đây:

1) Tóm tắt lỗi logic/thuật toán quan trọng
Viết 1-2 câu ngắn gọn về lỗi chính, ví dụ: "Lỗi off-by-one trong điều kiện vòng lặp"

2) Ai gợi ý sửa lỗi
Liệt kê dưới dạng:
* Gợi ý 1: ...
* Gợi ý 2: ...
(Mỗi gợi ý nên ngắn gọn 1 dòng, bắt đầu bằng "Sửa", "Thêm", "Đổi", "Kiểm tra")

3) Mức tự tin: high

---
Đề bài: {problem_title}
Mô tả: {problem_statement}
Ngôn ngữ: {language}

Mã nguồn:
```cpp
{source_code}
```

Hãy phân tích ngay bây giờ:"""

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

    # Parse response using new parser
    analysis, fixes, confidence = _parse_llm_response(raw)

    return LlmBaselineResult(
        analysis=analysis,
        suggested_fixes=fixes,
        confidence=confidence,
    )
