"""Simple backend for mini-game-platform coursework."""

import os

from flask import Flask, jsonify, request
from sqlalchemy.exc import OperationalError
from sqlalchemy import select

from database import Base, create_session_local, create_sqlite_engine
from models import Game, Score
from routes.games import register_game_routes
from routes.scores import register_score_routes

DEFAULT_GAMES = [
    ("brick_breaker", "Brick Breaker game"),
    ("caro", "Caro / Tic Tac Toe game"),
    ("flappy", "Flappy Bird game"),
    ("snake", "Snake game"),
    ("tetris", "Tetris game"),
]


def _seed_score_for_game(game_name: str, idx: int, duration_seconds: int) -> int:
    if game_name == "caro":
        # Keep seeded scores aligned with API validation: -1 (loss), 0 (draw), 1 (win).
        return [-1, 0, 1, -1, 1][idx % 5]
    if game_name == "snake":
        # Snake score must not exceed duration // 2.
        return min((idx + 1) * 10, duration_seconds // 2)
    return (idx + 1) * 10


def _score_is_seed_valid(game_name: str, score: int, duration_seconds: int) -> bool:
    if game_name == "caro":
        return score in {-1, 0, 1}
    if game_name == "snake":
        return 0 <= score <= (duration_seconds // 2)
    return True


def seed_data(session_local) -> None:
    with session_local() as db:
        existing_games = {game.name for game in db.execute(select(Game)).scalars().all()}
        for game_name, description in DEFAULT_GAMES:
            if game_name not in existing_games:
                db.add(Game(name=game_name, description=description))
        db.commit()

    with session_local() as db:
        for game_name, _description in DEFAULT_GAMES:
            existing_scores = db.execute(select(Score).where(Score.game_name == game_name)).scalars().all()

            for idx, score_row in enumerate(existing_scores):
                if _score_is_seed_valid(game_name, score_row.score, score_row.duration_seconds):
                    continue
                score_row.score = _seed_score_for_game(game_name, idx, score_row.duration_seconds)

            if len(existing_scores) >= 5:
                continue
            missing = 5 - len(existing_scores)
            for idx in range(missing):
                duration_seconds = 30 + idx * 10
                db.add(
                    Score(
                        game_name=game_name,
                        player_name=f"Player_{game_name}_{idx + 1}",
                        score=_seed_score_for_game(game_name, idx, duration_seconds),
                        level=1 + (idx // 2),
                        duration_seconds=duration_seconds,
                    )
                )
        db.commit()


def create_app(database_url: str = "sqlite:///./games.db", seed: bool = True) -> Flask:
    app = Flask(__name__)
    engine = create_sqlite_engine(database_url)
    session_local = create_session_local(engine)
    Base.metadata.create_all(bind=engine)

    app.config["SessionLocal"] = session_local

    if seed:
        try:
            seed_data(session_local)
        except OperationalError as e:
            # Trường hợp games.db cũ có schema khác (vd: thiếu cột games.name).
            # Drop/recreate schema để chạy lại local dev được ngay.
            msg = str(e).lower()
            if "no such column" in msg and "games." in msg:
                Base.metadata.drop_all(bind=engine)
                Base.metadata.create_all(bind=engine)
                seed_data(session_local)
            else:
                raise

    register_game_routes(app)
    register_score_routes(app)

    @app.before_request
    def handle_preflight():
        if request.method != "OPTIONS":
            return None
        response = app.make_default_options_response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    @app.errorhandler(400)
    def handle_bad_request(_error):
        return jsonify({"success": False, "data": {}, "message": "Bad request"}), 400

    @app.errorhandler(404)
    def handle_not_found(_error):
        return jsonify({"success": False, "data": {}, "message": "Not found"}), 404

    @app.errorhandler(500)
    def handle_server_error(_error):
        return jsonify({"success": False, "data": {}, "message": "Server error"}), 500

    return app


app = None if os.getenv("SKIP_APP_AUTOCREATE") == "1" else create_app()


if __name__ == "__main__":
    runtime_app = create_app()
    runtime_app.run(host="0.0.0.0", port=5000, debug=True)
