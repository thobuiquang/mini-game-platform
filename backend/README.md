# Mini Game Platform Backend (Simple)

Backend don gian cho du an mon hoc, dung Flask + SQLAlchemy + SQLite.

## Yeu cau

- Python 3.11+
- uv

## Cai dat

```bash
cd backend
uv sync
```

## Chay server

```bash
cd backend
uv run python app.py
```

Server chay tai: `http://localhost:5000`

## API Endpoints

### Games

- `GET /api/games`
- `GET /api/games/<game_name>`

### Scores

- `POST /api/scores`
- `GET /api/scores/<game_name>`
- `GET /api/scores/<game_name>/top10`

## Response format

Tat ca endpoint tra ve:

```json
{
  "success": true,
  "data": {},
  "message": "Optional message"
}
```

## Seed data

Khi chay `app.py`, he thong tu dong:

- Tao bang `games`, `scores`
- Seed 5 game: `brick_breaker`, `caro`, `flappy`, `snake`, `tetris`
- Seed it nhat 5 diem cho moi game

## Chay test

```bash
cd backend
uv run pytest
```
