# Smart Math Solver (COKB)

Ứng dụng giải toán cấp 1–2: **tri thức** trong `backend/rules.json` (mô hình đối tượng–thuộc tính–luật), **orchestrator** FastAPI, **bộ suy diễn** Google Gemini. Frontend React hiển thị các bước và công thức bằng KaTeX.

## Cấu trúc

- `backend/` — FastAPI, đọc `rules.json`, gọi Gemini, trả JSON chuẩn (`method`, `steps`, `result`).
- `frontend/` — Vite + React + KaTeX, proxy `/api` → backend khi chạy dev.

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

- `POST /api/solve` — Body JSON: `{ "problem": "...", "grade_level": 1 | 2 }`
- `GET /health` — Kiểm tra dịch vụ
- `GET /api/rules` — Đường dẫn file `rules.json` (debug)

## Mở rộng tri thức

Chỉnh `backend/rules.json`: thêm `objects`, `attributes`, `rules` và cập nhật `inference_logic` nếu cần phong cách suy diễn khác nhau theo cấp.
