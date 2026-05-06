"""Game routes."""

from flask import jsonify
from sqlalchemy import select

from models import Game


def register_game_routes(app):
    @app.get("/api/games")
    def list_games():
        session_local = app.config["SessionLocal"]
        with session_local() as db:
            games = db.execute(select(Game).order_by(Game.name.asc())).scalars().all()
            data = [{"id": game.id, "name": game.name, "description": game.description} for game in games]
            return jsonify({"success": True, "data": data, "message": "Games fetched"})

    @app.get("/api/games/<string:game_name>")
    def game_detail(game_name: str):
        session_local = app.config["SessionLocal"]
        with session_local() as db:
            game = db.execute(select(Game).where(Game.name == game_name)).scalar_one_or_none()
            if not game:
                return jsonify({"success": False, "data": {}, "message": "Game not found"}), 404
            return jsonify(
                {
                    "success": True,
                    "data": {"id": game.id, "name": game.name, "description": game.description},
                    "message": "Game fetched",
                }
            )
