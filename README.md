# Smart Programming Diagnosis Tutor

Hệ thống hỗ trợ giải bài tập lập trình có hướng dẫn từng bước cho sinh viên C/C++:

- Chẩn đoán lỗi logic/thuật toán bằng **Rule-Based Reasoning**.
- Tạo **Context-Aware Explanations** theo cấu trúc:
  `Code -> Pattern Matching -> Rule Triggered -> Step Explanation`.
- So sánh hiệu quả giữa:
  - Hệ thống tri thức + luật chẩn đoán.
  - Baseline chỉ dùng LLM (Gemini).

## Cấu trúc

- `backend/` — FastAPI + tri thức lỗi (`rules.json`) + bộ suy luận theo luật + baseline LLM.
- `frontend/` — Vite + React, giao diện nhập bài + mã nguồn và hiển thị từng bước sửa lỗi.

## Chuẩn bị

1. **Python 3.10+**
2. **Node.js 18+**
3. **API key Gemini**: [Google AI Studio](https://aistudio.google.com/apikey)

## Docker

```bash
export GEMINI_API_KEY=...   # bắt buộc
# tùy chọn: export GEMINI_MODEL=gemini-2.0-flash
docker compose build --no-cache
docker compose up -d
```

Frontend (preview) gọi API tại `VITE_API_BASE` (mặc định `http://localhost:8000`). Nếu deploy khác host, build lại frontend với `docker compose build --build-arg VITE_API_BASE=https://api.example.com`.

**Bảo mật:** không commit API key; nếu từng dán key vào mã nguồn, hãy **xoá và tạo lại key** trên Google AI Studio.

**Lỗi 404 `models/... is not found`:** tên model cũ (ví dụ `gemini-1.5-flash`) có thể không còn với API bạn đang dùng. Đặt `GEMINI_MODEL=gemini-2.0-flash` (hoặc model mới trong Google AI Studio → *List models*), rồi `docker compose up -d --force-recreate` backend.

## Chạy backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Sửa .env: gán GEMINI_API_KEY và tùy chọn GEMINI_MODEL (mặc định gemini-2.0-flash)

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Chạy frontend

```bash
cd frontend
npm install
npm run dev
```

Mở trình duyệt tại `http://127.0.0.1:5173`. Đảm bảo backend đang chạy ở cổng 8000 để proxy `/api` hoạt động.

## API

- `POST /api/diagnose`
  - Body JSON:
    - `problem_title`: tên bài
    - `problem_statement`: mô tả đề bài
    - `source_code`: mã nguồn C/C++
    - `language`: `c` hoặc `cpp`
    - `compare_with_llm`: `true|false`
- `POST /api/solve`: alias tương thích ngược với payload như trên
- `GET /health` — Kiểm tra dịch vụ
- `GET /api/rules` — Đường dẫn file `rules.json` (debug)

## CSDL tri thức lỗi

`backend/rules.json` gồm:

- `knowledge_model`: mô hình quan hệ Bài toán-Thuật toán-Cấu trúc dữ liệu-Lỗi-Hướng sửa.
- `topic_keywords`: ánh xạ đề bài/code sang chủ đề.
- `diagnostic_rules`: tập luật chẩn đoán lỗi phổ biến:
  - lỗi vòng lặp vô hạn
  - lỗi điều kiện biên sai
  - lỗi đệ quy thiếu base case
  - lỗi quản lý bộ nhớ
- `recommended_learning_path`: gợi ý học tập tiếp theo.
