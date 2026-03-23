# 🤖 Models & APIs sử dụng trong dự án

## 📊 Tổng quan

Dự án này **chỉ dùng 1 model/API ngoài**: **Google Gemini AI**

---

## 1️⃣ Google Gemini AI (Chính)

### 📌 Thông tin cơ bản
- **Service**: Google Gemini API
- **Model mặc định**: `gemini-2.0-flash`
- **Phiên bản library**: `google-genai >= 1.0.0`
- **Vị trí sử dụng**: [backend/app/services/gemini_service.py](backend/app/services/gemini_service.py)
- **Vai trò**: Baseline so sánh cho hệ thống rule-based

### 🔧 Cấu hình
```python
# File: backend/app/config.py
gemini_api_key: str = ""           # Từ biến môi trường GEMINI_API_KEY
gemini_model: str = "gemini-2.0-flash"
```

### 📝 Chi tiết sử dụng

**File**: [backend/app/services/gemini_service.py](backend/app/services/gemini_service.py)

```python
from google import genai
from google.genai import types

def generate_llm_baseline(
    problem_title: str,
    problem_statement: str,
    source_code: str,
    language: str,
    gemini_api_key: str,
    gemini_model: str,
) -> LlmBaselineResult:
    """Gọi Gemini API để phân tích code"""
    
    client = genai.Client(api_key=gemini_api_key)
    response = client.models.generate_content(
        model=gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,  # Giảm ngẫu nhiên để kết quả nhất quán
        ),
    )
```

### 📤 Input cho Gemini
```
Prompt template:
- Đề bài (problem_title)
- Mô tả bài (problem_statement)
- Mã nguồn (source_code)
- Ngôn ngữ (language: c hoặc cpp)

Yêu cầu:
1) Tóm tắt lỗi logic/thuật toán
2) 3-5 gợi ý sửa lỗi
3) Mức tự tin: high/medium/low
```

### 📥 Output từ Gemini
```python
LlmBaselineResult(
    analysis: str           # Phân tích từ Gemini (max 1200 ký tự)
    suggested_fixes: list   # 3-5 gợi ý sửa lỗi
    confidence: str         # "high" / "medium" / "low"
)
```

### 🔄 Quy trình gọi
1. **Frontend** gửi code + bài tập → **Backend API** (`POST /api/diagnose`)
2. **Backend** chạy rule-based diagnosis
3. Nếu `compare_with_llm=true` → **Gọi Gemini API**
4. Parse response từ Gemini → trả về LlmBaselineResult
5. **Frontend** hiển thị cả rule-based + LLM baseline để so sánh

### ⚙️ Cấu hình trong .env
```bash
# backend/.env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash  # (optional, default)
```

### 🚨 Xử lý lỗi
```python
if not gemini_api_key:
    # Trả về thông báo "Cần GEMINI_API_KEY"
    return LlmBaselineResult(confidence="low", ...)

try:
    response = client.models.generate_content(...)
except Exception as e:
    # Ghi log & trả về lỗi graceful
    logger.exception("gemini baseline failed")
    return LlmBaselineResult(confidence="low", ...)
```

---

## 📦 Dependencies liên quan

### [backend/requirements.txt](backend/requirements.txt)
```
google-genai>=1.0.0  ← Chỉ có Google Gemini
```

### Các lib khác (không phải AI models)
- `fastapi==0.115.6` - Web framework
- `uvicorn[standard]==0.32.1` - ASGI server
- `pydantic==2.10.3` - Data validation
- `pydantic-settings==2.6.1` - Environment config
- `python-dotenv==1.0.1` - Load .env file

---

## 🎯 Có những model nào khác KHÔNG?

❌ **OpenAI API** - Không sử dụng
❌ **Anthropic Claude** - Không sử dụng  
❌ **Hugging Face** - Không sử dụng
❌ **Local LLMs** (Ollama, LLaMA, v.v.) - Không sử dụng
❌ **Replicate** - Không sử dụng
❌ **Cohere** - Không sử dụng

---

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────────────────────────┐
│         Frontend (React)             │
│  - Input: Problem + Code             │
│  - Display: Rule-based + LLM compare │
└─────────────┬───────────────────────┘
              │
              ↓
┌─────────────────────────────────────┐
│    Backend API (FastAPI)            │
│  POST /api/diagnose                 │
└─────────────┬───────────────────────┘
              │
              ├─────────────────────────────────┐
              ↓                                 ↓
    ┌──────────────────┐          ┌─────────────────────┐
    │ Rule-Based Engine│          │  Google Gemini API  │
    │ (Pattern Match)  │          │  (LLM Baseline)     │
    │ - R_OFF_BY_ONE   │          │                     │
    │ - R_INFINITE_... │          │  Temperature: 0.2   │
    │ - R_RECURSION... │          │  Model: gemini-...  │
    └──────────────────┘          └─────────────────────┘
              │                                 │
              └─────────────────────────────────┘
                            ↓
            ┌─────────────────────────────────┐
            │  Response (DiagnoseResponse)    │
            │  - rule_based results           │
            │  - llm_baseline results         │
            │  - comparison notes             │
            └─────────────────────────────────┘
                            ↓
                      ┌──────────┐
                      │ Frontend │
                      │ Display  │
                      └──────────┘
```

---

## 💡 Nếu muốn thêm model khác

### Cách 1: Thêm OpenAI (để so sánh)
```python
# backend/app/services/openai_service.py
import openai

def generate_openai_baseline(...):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return LlmBaselineResult(...)
```

### Cách 2: Thêm Anthropic Claude
```python
# backend/app/services/claude_service.py
import anthropic

def generate_claude_baseline(...):
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        messages=[{"role": "user", "content": prompt}]
    )
    return LlmBaselineResult(...)
```

### Cách 3: Thêm Local LLM (Ollama)
```python
# backend/app/services/ollama_service.py
import requests

def generate_ollama_baseline(...):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama2", "prompt": prompt}
    )
    return LlmBaselineResult(...)
```

---

## 📊 So sánh các model hiện có vs có thể thêm

| Model | Loại | Tốc độ | Chi phí | Chất lượng | Trạng thái |
|-------|------|--------|---------|-----------|-----------|
| **Gemini 2.0 Flash** | Cloud API | ⚡⚡⚡ Nhanh | 💰 Rẻ | ⭐⭐⭐⭐ | ✅ Đang dùng |
| GPT-4 | Cloud API | ⚡⚡ Trung bình | 💰💰💰 Đắt | ⭐⭐⭐⭐⭐ | ❌ Không dùng |
| Claude 3 | Cloud API | ⚡⚡ Trung bình | 💰💰 Trung | ⭐⭐⭐⭐⭐ | ❌ Không dùng |
| Llama 2 Local | Local | ⚡ Chậm | 💰 Miễn phí | ⭐⭐⭐ | ❌ Không dùng |
| Ollama | Local | ⚡ Chậm | 💰 Miễn phí | ⭐⭐⭐ | ❌ Không dùng |

---

## 🔐 API Keys & Configuration

### Hiện tại
```bash
# backend/.env
GEMINI_API_KEY=sk_your_gemini_key
```

### Nếu muốn thêm nhiều model
```bash
# backend/.env
# Google Gemini
GEMINI_API_KEY=sk_google_...
GEMINI_MODEL=gemini-2.0-flash

# OpenAI (nếu thêm)
OPENAI_API_KEY=sk_openai_...
OPENAI_MODEL=gpt-4

# Anthropic (nếu thêm)
ANTHROPIC_API_KEY=sk_anthropic_...
ANTHROPIC_MODEL=claude-3-sonnet

# Ollama Local (nếu thêm)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

---

## 📝 Kết luận

**Hiện tại:**
- ✅ 1 model chính: **Google Gemini 2.0 Flash**
- ✅ Được sử dụng cho LLM baseline comparison
- ✅ Dễ dàng mở rộng thêm model khác

**Lý do chọn Gemini:**
- 💨 Nhanh (flash model)
- 💰 Rẻ & free tier hấp dẫn
- 📊 Chất lượng tốt cho task phân tích code
- 🔧 API đơn giản, dễ tích hợp

