# Web Game Backend

Backend API cho nền tảng game HTML5 sử dụng FastAPI + SQLite + SQLAlchemy.

## 1) Cài đặt

**Cách A — `uv` (khuyến nghị, Python 3.11+):**

```bash
cd backend
uv sync
```

**Cách B — pip:**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Đổ dữ liệu game từ thư mục `games/`

```bash
cd backend
uv run python seed_database.py
```

Script sẽ: tạo bảng (nếu thiếu), gọi **`seed_default_categories`** (action, casual, puzzle, …), rồi **`scan_games_folder`** để đồng bộ từ `STATIC_PATH`.

## Cấu trúc `app/` (theo PROMPT_AGENT_BACKEND_GAME_WITH_UV)

- `app/models/base.py` — `Base` ORM
- `app/middleware/cors.py` — đăng ký CORS
- `app/routes/games.py` — list / detail / play
- `app/routes/search.py` — `GET .../games/search`
- `app/routes/health.py` — `GET /health` và `GET /api/v1/health`
- `app/schemas/base.py` — schema dùng chung
- `app/utils/validators.py`, `app/utils/helpers.py` — tiện ích nhỏ
- `tests/test_routes_games.py`, `test_routes_categories.py`, `test_api_functional.py`, `test_api_boundary.py`, `test_static_files.py`, `test_schemas.py`, `test_utils.py`

## 2) Chạy server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Với **uv** (khuyến nghị):

```bash
cd backend
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend + Backend cùng lúc (thử trên máy)

1. Chạy lệnh `uvicorn` ở trên từ thư mục `backend` (để SQLite và `games/` đúng đường dẫn).
2. Mở trình duyệt:
   - **Giao diện:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/) → tự chuyển sang `/ui/` (danh sách game lấy từ API).
   - **Swagger:** [http://localhost:8000/docs](http://localhost:8000/docs)
   - **OpenAPI JSON:** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

Nếu CSDL chưa có game: dùng Swagger hoặc gọi scanner (Python) để đồng bộ từ `backend/games/*/game.json`.

Thư mục frontend mặc định là `../frontend` (cùng repo). Đổi bằng biến môi trường `FRONTEND_PATH` nếu cần.

## 3) API chính

- `GET /api/v1/games`: danh sách game (paging/filter/sort)
- `GET /api/v1/games/{game_id}`: chi tiết game
- `GET /api/v1/games/search?q=...`: tìm kiếm game
- `POST /api/v1/games/{game_id}/play`: cập nhật lượt chơi
- `GET /api/v1/categories`: danh sách category
- `GET /api/v1/health`: health check (có `timestamp`)
- `GET /health`: health check ở root (có `timestamp`, không phụ thuộc version API)

Error format thống nhất:

```json
{
  "success": false,
  "error": "..."
}
```

## 4) Migration

SQL migration file: `migrations/001_create_tables.sql`

## 5) Games static

- Thư mục game: `games/`
- URL public: `/static/games/...`
- Ví dụ: `/static/games/game1/index.html`

## 6) Scan games folder

Hàm tiện ích: `app/utils/game_scanner.py`

- Đọc metadata từ `game.json`
- Tự động insert/update/delete game trong DB
- Trả về tổng kết `{added, updated, deleted}`

## 7) Chạy test + coverage

```bash
pytest --cov=app --cov-report=html --cov-report=term
```

Coverage report HTML: `htmlcov/index.html`
