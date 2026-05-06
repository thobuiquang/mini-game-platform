"""Simple backend for mini-game-platform coursework."""

import os

from flask import Flask, jsonify
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


def seed_data(session_local) -> None:
    with session_local() as db:
        existing_games = {game.name for game in db.execute(select(Game)).scalars().all()}
        for game_name, description in DEFAULT_GAMES:
            if game_name not in existing_games:
                db.add(Game(name=game_name, description=description))
        db.commit()

    with session_local() as db:
        for game_name, _description in DEFAULT_GAMES:
            count = db.execute(select(Score).where(Score.game_name == game_name)).scalars().all()
            if len(count) >= 5:
                continue
            missing = 5 - len(count)
            for idx in range(missing):
                db.add(
                    Score(
                        game_name=game_name,
                        player_name=f"Player_{game_name}_{idx + 1}",
                        score=(idx + 1) * 10,
                        level=1 + (idx // 2),
                        duration_seconds=30 + idx * 10,
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
        seed_data(session_local)

    register_game_routes(app)
    register_score_routes(app)

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
